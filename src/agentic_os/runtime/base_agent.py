import time
import json
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field

from src.agentic_os.runtime.skill_loader import SkillLoader
from src.agentic_os.runtime.tool_registry import ToolRegistry
from src.agentic_os.runtime.llm_client import OllamaLLMClient, LLMDecision
from src.agentic_os.optimization.model_tiering import ModelTier, ModelTierRouter
from src.agentic_os.optimization.context_engineering import ContextEngineer, CompactPipelineState
from src.agentic_os.optimization.tool_optimizer import ToolCallOptimizer, ToolLoopDetectedException
from src.agentic_os.optimization.caching_strategy import FourTierCacheManager
from src.agentic_os.optimization.guardrails import PipelineGuardrails, GuardrailBreachException


class AgentStepTrace(BaseModel):
    iteration: int
    thought: str
    action_type: str  # "TOOL_CALL" or "FINAL_ANSWER" or "EARLY_EXIT"
    tool_name: Optional[str] = None
    tool_source: Optional[str] = None
    tool_args: Dict[str, Any] = Field(default_factory=dict)
    observation_summary: Optional[str] = None
    cache_hit: bool = False
    latency_ms: float = 0.0


class AgentExecutionResult(BaseModel):
    agent_name: str
    skills_loaded: List[str]
    status: str  # "COMPLETED", "EARLY_EXIT", "GUARDRAIL_HALTED"
    iterations_used: int
    traces: List[AgentStepTrace]
    collected_outputs: Dict[str, Any]
    final_summary: str


class BaseReActAgent:
    """True Agentic Loop (Think -> Act -> Observe) powered by:
    - SKILL.md instructions (SkillLoader)
    - Native & MCP Tools (ToolRegistry)
    - Local Ollama LLM with planned fallback (OllamaLLMClient)
    - 7 Optimization Layers (Tool loop breaker, 4-tier cache, context trimming, guardrails)
    """

    def __init__(
        self,
        name: str,
        skill_names: List[str],
        allowed_tools: List[str],
        tool_registry: Optional[ToolRegistry] = None,
        skill_loader: Optional[SkillLoader] = None,
        llm_client: Optional[OllamaLLMClient] = None,
        max_iterations: int = 6,
        model_tier: ModelTier = ModelTier.SMALL,
        use_llm: bool = False
    ):
        self.name = name
        self.skill_names = skill_names
        self.allowed_tools = allowed_tools
        self.skill_loader = skill_loader or SkillLoader()
        self.tool_registry = tool_registry or ToolRegistry(attach_mcp=False)
        self.llm_client = llm_client or OllamaLLMClient()
        self.model_tier = model_tier
        self.use_llm = use_llm

        # Optimization Layers
        self.tool_optimizer = ToolCallOptimizer(max_allowed_duplicate_calls=2)
        self.cache_manager = FourTierCacheManager()
        self.context_engineer = ContextEngineer()
        self.model_router = ModelTierRouter()
        self.guardrails = PipelineGuardrails(
            max_loop_iterations=2,
            max_reasoning_steps=max_iterations,
            per_step_timeout_sec=15.0,
            total_request_timeout_sec=60.0
        )

        # Load SKILL.md instructions
        self.system_prompt = self.skill_loader.render_system_prompt(self.skill_names)

    def run_loop(
        self,
        goal: str,
        initial_context: Dict[str, Any],
        planned_sequence: Optional[List[Dict[str, Any]]] = None,
        goal_satisfied_fn: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> AgentExecutionResult:
        """Executes the Think -> Act -> Observe agent loop."""
        self.guardrails.start_request()
        traces: List[AgentStepTrace] = []
        collected_outputs: Dict[str, Any] = {}
        step_idx = 0

        state = CompactPipelineState(
            founder_id=str(initial_context.get("founder_name", "founder")),
            target_category=str(initial_context.get("category", "WORKFLOW_AUTOMATION")),
            constraints_summary=json.dumps({k: v for k, v in initial_context.items() if k in ["available_hours", "budget_usd"]}),
            last_completed_stage="init",
            immediate_preceding_output=initial_context
        )

        tool_schemas = self.tool_registry.get_ollama_tool_schemas(self.allowed_tools)
        plan_cursor = 0

        while True:
            step_idx += 1
            step_start = time.perf_counter()

            # Layer 7: Guardrails check (max steps & total timeout)
            try:
                self.guardrails.start_step(f"{self.name}_iter_{step_idx}")
            except GuardrailBreachException as e:
                traces.append(AgentStepTrace(
                    iteration=step_idx,
                    thought=str(e),
                    action_type="GUARDRAIL_HALTED",
                    latency_ms=round((time.perf_counter() - step_start) * 1000, 2)
                ))
                return AgentExecutionResult(
                    agent_name=self.name,
                    skills_loaded=self.skill_names,
                    status="GUARDRAIL_HALTED",
                    iterations_used=step_idx - 1,
                    traces=traces,
                    collected_outputs=collected_outputs,
                    final_summary=str(e)
                )

            # Layer 7: Confidence / Goal satisfaction early exit
            if goal_satisfied_fn and goal_satisfied_fn(collected_outputs):
                traces.append(AgentStepTrace(
                    iteration=step_idx,
                    thought="Goal satisfaction criteria verified. Triggering early exit.",
                    action_type="EARLY_EXIT",
                    latency_ms=round((time.perf_counter() - step_start) * 1000, 2)
                ))
                return AgentExecutionResult(
                    agent_name=self.name,
                    skills_loaded=self.skill_names,
                    status="EARLY_EXIT",
                    iterations_used=step_idx,
                    traces=traces,
                    collected_outputs=collected_outputs,
                    final_summary=f"{self.name} completed via early exit after {len(collected_outputs)} tool observations."
                )

            # Layer 3: Compile bounded step context
            compact_ctx = self.context_engineer.compile_step_context(
                current_stage=f"iteration_{step_idx}",
                state=state
            )

            # Think: Decide next action via Ollama LLM or deterministic skill plan
            decision: Optional[LLMDecision] = None
            if self.use_llm and self.llm_client.is_available():
                self.model_router.route_task(self.name, complexity_override=self.model_tier)
                prompt_msg = [{"role": "user", "content": f"Goal: {goal}\nCompact State: {json.dumps(compact_ctx)}"}]
                decision = self.llm_client.decide_next_step(
                    system_prompt=self.system_prompt,
                    messages=prompt_msg,
                    tools=tool_schemas,
                    tier=self.model_tier
                )

            if decision is None:
                # Planned SKILL.md execution fallback when LLM is disabled/offline
                if plan_cursor < len(planned_sequence or []):
                    planned = planned_sequence[plan_cursor]
                    plan_cursor += 1
                    decision = LLMDecision(
                        thought=planned.get("thought", f"Executing skill step {plan_cursor}"),
                        action_type="TOOL_CALL",
                        tool_name=planned["tool_name"],
                        tool_args=planned.get("tool_args", {}),
                        model_used="skill-plan-router"
                    )
                else:
                    decision = LLMDecision(
                        thought="All skill steps completed.",
                        action_type="FINAL_ANSWER",
                        final_answer=f"Completed {len(collected_outputs)} skill steps.",
                        model_used="skill-plan-router"
                    )

            if decision.action_type == "FINAL_ANSWER":
                self.guardrails.end_step(f"{self.name}_iter_{step_idx}")
                traces.append(AgentStepTrace(
                    iteration=step_idx,
                    thought=decision.thought,
                    action_type="FINAL_ANSWER",
                    observation_summary=decision.final_answer,
                    latency_ms=round((time.perf_counter() - step_start) * 1000, 2)
                ))
                return AgentExecutionResult(
                    agent_name=self.name,
                    skills_loaded=self.skill_names,
                    status="COMPLETED",
                    iterations_used=step_idx,
                    traces=traces,
                    collected_outputs=collected_outputs,
                    final_summary=decision.final_answer or "Completed"
                )

            # Act: Execute Tool Call with Layer 4 (Optimizer) & Layer 6 (Cache)
            tool_name = decision.tool_name or ""
            tool_args = decision.tool_args

            if tool_name not in self.allowed_tools:
                traces.append(AgentStepTrace(
                    iteration=step_idx,
                    thought=f"Tool '{tool_name}' not permitted for agent '{self.name}'.",
                    action_type="TOOL_CALL",
                    tool_name=tool_name,
                    observation_summary="Blocked: tool not in allowed_tools",
                    latency_ms=round((time.perf_counter() - step_start) * 1000, 2)
                ))
                continue

            # Layer 4: Pre-invocation & loop prevention check
            try:
                self.tool_optimizer.pre_invocation_check(tool_name, tool_args)
            except ToolLoopDetectedException as e:
                traces.append(AgentStepTrace(
                    iteration=step_idx,
                    thought=decision.thought,
                    action_type="GUARDRAIL_HALTED",
                    tool_name=tool_name,
                    tool_args=tool_args,
                    observation_summary=str(e),
                    latency_ms=round((time.perf_counter() - step_start) * 1000, 2)
                ))
                return AgentExecutionResult(
                    agent_name=self.name,
                    skills_loaded=self.skill_names,
                    status="GUARDRAIL_HALTED",
                    iterations_used=step_idx,
                    traces=traces,
                    collected_outputs=collected_outputs,
                    final_summary=str(e)
                )

            # Layer 6: Tool Result Cache Check
            cached = self.cache_manager.get_tool_result(tool_name, tool_args)
            cache_hit = False
            if cached is not None:
                obs = cached
                cache_hit = True
            else:
                obs = self.tool_registry.execute(tool_name, tool_args)
                self.cache_manager.set_tool_result(tool_name, tool_args, obs)

            collected_outputs[tool_name] = obs
            tool_meta = self.tool_registry.get_tool(tool_name)

            # Update compact state with ONLY immediate preceding output (Layer 3)
            state.last_completed_stage = tool_name
            state.immediate_preceding_output = {"tool": tool_name, "keys": list(obs.keys()) if isinstance(obs, dict) else "raw"}

            self.guardrails.end_step(f"{self.name}_iter_{step_idx}")

            traces.append(AgentStepTrace(
                iteration=step_idx,
                thought=decision.thought,
                action_type="TOOL_CALL",
                tool_name=tool_name,
                tool_source=tool_meta.source if tool_meta else "unknown",
                tool_args=tool_args,
                observation_summary=f"Returned {len(obs) if isinstance(obs, (dict, list)) else 1} fields",
                cache_hit=cache_hit,
                latency_ms=round((time.perf_counter() - step_start) * 1000, 2)
            ))
