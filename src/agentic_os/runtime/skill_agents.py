from typing import Dict, Any, Optional

from src.agentic_os.runtime.base_agent import BaseReActAgent, AgentExecutionResult
from src.agentic_os.runtime.tool_registry import ToolRegistry
from src.agentic_os.runtime.skill_loader import SkillLoader
from src.agentic_os.optimization.model_tiering import ModelTier


class ObstacleExtractionAgent(BaseReActAgent):
    """Skill-driven agent loading .agents/skills/obstacle-chain-extractor/SKILL.md.
    Loops over retrieve_evidence -> extract_obstacle_chain until triangulation & coverage pass.
    """

    def __init__(self, tool_registry: Optional[ToolRegistry] = None, use_llm: bool = False):
        super().__init__(
            name="ObstacleExtractionAgent",
            skill_names=["obstacle-chain-extractor"],
            allowed_tools=["retrieve_evidence", "extract_obstacle_chain"],
            tool_registry=tool_registry,
            max_iterations=5,
            model_tier=ModelTier.MID,
            use_llm=use_llm
        )

    def run(self, category: str = "WORKFLOW_AUTOMATION") -> AgentExecutionResult:
        plan = [
            {
                "thought": "Skill Rule: Triangulate at least 2 distinct source types before extracting obstacles.",
                "tool_name": "retrieve_evidence",
                "tool_args": {"category": category}
            },
            {
                "thought": "Skill Rule: Sequence obstacles chronologically (BEFORE_ATTEMPT -> DURING_EXECUTION -> AFTER_COMPLETION).",
                "tool_name": "extract_obstacle_chain",
                "tool_args": {"category": category}
            }
        ]
        return self.run_loop(
            goal=f"Retrieve triangulated buyer evidence and extract an ordered obstacle chain for {category}.",
            initial_context={"category": category},
            planned_sequence=plan,
            goal_satisfied_fn=lambda outs: (
                "retrieve_evidence" in outs
                and "extract_obstacle_chain" in outs
                and outs["retrieve_evidence"].get("triangulation_passed", False)
                and outs["extract_obstacle_chain"].get("coverage_ratio", 0.0) >= 0.65
            )
        )


class OfferDiagnosticianAgent(BaseReActAgent):
    """Skill-driven agent loading .agents/skills/offer-diagnostician/SKILL.md.
    Loops over diagnose_offer_value -> generate_product_suite.
    """

    def __init__(self, tool_registry: Optional[ToolRegistry] = None, use_llm: bool = False):
        super().__init__(
            name="OfferDiagnosticianAgent",
            skill_names=["offer-diagnostician"],
            allowed_tools=["diagnose_offer_value", "generate_product_suite"],
            tool_registry=tool_registry,
            max_iterations=5,
            model_tier=ModelTier.MID,
            use_llm=use_llm
        )

    def run(self, category: str = "WORKFLOW_AUTOMATION", skills_text: str = "python, fastapi, n8n") -> AgentExecutionResult:
        plan = [
            {
                "thought": "Skill Rule: Formalize Hormozi's Value Equation and detect primary bottleneck.",
                "tool_name": "diagnose_offer_value",
                "tool_args": {"category": category, "skills_text": skills_text}
            },
            {
                "thought": "Skill Rule: Build 3-tier funnel (Lead Magnet, Core Offer, Compounding Backend).",
                "tool_name": "generate_product_suite",
                "tool_args": {"category": category, "skills_text": skills_text}
            }
        ]
        return self.run_loop(
            goal=f"Diagnose offer value equation and design a 3-tier compounding asset funnel for {category}.",
            initial_context={"category": category, "skills_text": skills_text},
            planned_sequence=plan,
            goal_satisfied_fn=lambda outs: "diagnose_offer_value" in outs and "generate_product_suite" in outs
        )


class OpportunityCoordinatorAgent(BaseReActAgent):
    """Master Coordinator Agent loading .agents/skills/agentic-entrepreneur-os/SKILL.md
    and executing tools over live MCP (agentic-os-engine) in an agentic loop.
    """

    def __init__(self, attach_mcp: bool = True, use_llm: bool = False):
        registry = ToolRegistry(attach_mcp=attach_mcp)
        super().__init__(
            name="OpportunityCoordinatorAgent",
            skill_names=[
                "agentic-entrepreneur-os",
                "obstacle-chain-extractor",
                "offer-diagnostician"
            ],
            allowed_tools=[
                "ingest_profile",
                "decompose_capabilities",
                "retrieve_evidence",
                "extract_obstacle_chain",
                "diagnose_offer_value",
                "generate_founder_decision_memo"
            ],
            tool_registry=registry,
            max_iterations=8,
            model_tier=ModelTier.MID,
            use_llm=use_llm
        )

    def run(
        self,
        founder_name: str,
        skills_text: str,
        category: str = "WORKFLOW_AUTOMATION",
        available_hours: float = 15.0,
        budget_usd: float = 500.0
    ) -> AgentExecutionResult:
        plan = [
            {
                "thought": "Step 1: Ingest raw founder capabilities and constraints via MCP.",
                "tool_name": "ingest_profile",
                "tool_args": {
                    "founder_name": founder_name,
                    "skills_text": skills_text,
                    "available_hours": available_hours,
                    "budget_usd": budget_usd
                }
            },
            {
                "thought": "Step 2: Decompose capabilities into clusters and cross-cluster intersections.",
                "tool_name": "decompose_capabilities",
                "tool_args": {"founder_name": founder_name, "skills_text": skills_text}
            },
            {
                "thought": "Step 3: Retrieve triangulated buyer evidence from corpus.",
                "tool_name": "retrieve_evidence",
                "tool_args": {"category": category}
            },
            {
                "thought": "Step 4: Extract ordered buyer obstacle chain.",
                "tool_name": "extract_obstacle_chain",
                "tool_args": {"category": category}
            },
            {
                "thought": "Step 5: Diagnose Hormozi Value Equation bottleneck.",
                "tool_name": "diagnose_offer_value",
                "tool_args": {"category": category}
            },
            {
                "thought": "Step 6: Synthesize final Founder Decision Memo with Kelly sizing & human checkpoint.",
                "tool_name": "generate_founder_decision_memo",
                "tool_args": {
                    "founder_name": founder_name,
                    "skills_text": skills_text,
                    "category": category,
                    "available_hours": available_hours,
                    "budget_usd": budget_usd
                }
            }
        ]
        try:
            return self.run_loop(
                goal=f"Turn {founder_name}'s skills ({skills_text}) into a grounded Founder Decision Memo for {category}.",
                initial_context={
                    "founder_name": founder_name,
                    "skills_text": skills_text,
                    "category": category,
                    "available_hours": available_hours,
                    "budget_usd": budget_usd
                },
                planned_sequence=plan,
                goal_satisfied_fn=lambda outs: "generate_founder_decision_memo" in outs
            )
        finally:
            self.tool_registry.close()
