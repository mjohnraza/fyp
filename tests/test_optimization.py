import pytest
import asyncio
from src.agentic_os.optimization.deterministic_first import DeterministicRuleEngine
from src.agentic_os.optimization.model_tiering import ModelTierRouter, ModelTier
from src.agentic_os.optimization.context_engineering import ContextEngineer, CompactPipelineState
from src.agentic_os.optimization.tool_optimizer import ToolCallOptimizer, ToolLoopDetectedException
from src.agentic_os.optimization.parallel_executor import ParallelPipelineExecutor
from src.agentic_os.optimization.caching_strategy import FourTierCacheManager
from src.agentic_os.optimization.guardrails import PipelineGuardrails, GuardrailBreachException
from src.agentic_os.schemas.profile import CapabilityItem, ProficiencyLevel


# 1. Layer 1: Deterministic First
def test_layer1_deterministic_first():
    engine = DeterministicRuleEngine()

    # Exact math: Hormozi Value Equation
    res_val = engine.evaluate_request(
        "CALCULATE_VALUE_EQUATION",
        {"dream_outcome": 9.0, "perceived_likelihood": 8.0, "time_delay": 2.0, "effort_sacrifice": 3.0}
    )
    assert res_val.is_deterministic is True
    assert res_val.handled is True
    assert res_val.output["computed_score"] == 12.0
    assert res_val.cost_usd == 0.0

    # Exact math: Kelly Sizing
    res_kelly = engine.evaluate_request("CALCULATE_KELLY_SIZING", {"budget_usd": 600.0})
    assert res_kelly.is_deterministic is True
    assert res_kelly.output["max_validation_spend"] == 50.0  # Capped at min(50, 600 * 0.15)

    # Probabilistic fallback
    res_prob = engine.evaluate_request("SYNTHESIZE_UNSTRUCTURED_IDEA", {"text": "hello"})
    assert res_prob.is_deterministic is False
    assert res_prob.handled is False

    stats = engine.get_stats()
    assert stats["deterministic_hits"] == 2
    assert stats["model_delegations"] == 1


# 2. Layer 2: Model Tiering
def test_layer2_model_tiering():
    router = ModelTierRouter()

    d1 = router.route_task("profile_intake")
    assert d1.assigned_tier == ModelTier.SMALL
    assert d1.estimated_cost_usd == 0.0

    d2 = router.route_task("obstacle_chain_extraction")
    assert d2.assigned_tier == ModelTier.MID

    d3 = router.route_task("ten_dimension_scorecard")
    assert d3.assigned_tier == ModelTier.LARGE

    summary = router.get_audit_summary()
    assert summary["total_calls"] == 3
    assert summary["total_cost_usd"] < (3 * 0.025)
    assert summary["estimated_savings_vs_flagship_usd"] > 0


# 3. Layer 3: Context Engineering
def test_layer3_context_engineering():
    engineer = ContextEngineer()
    state = CompactPipelineState(
        founder_id="prof-123",
        target_category="WORKFLOW_AUTOMATION",
        constraints_summary="15 hrs/wk, $500",
        last_completed_stage="profile_intake",
        immediate_preceding_output={"skills_count": 5}
    )

    ctx = engineer.compile_step_context("retrieval", state, {"extra": "data", "full_trace": "should_be_stripped"})
    assert "stage" in ctx
    assert "full_trace" not in ctx
    assert ctx["target"] == "WORKFLOW_AUTOMATION"

    metrics = engineer.get_token_savings_metrics()
    assert metrics["cumulative_tokens_trimmed"] > 0


# 4. Layer 4: Tool Call Optimization & Loop Breaker
def test_layer4_tool_optimization():
    optimizer = ToolCallOptimizer(max_allowed_duplicate_calls=2)

    args = {"query": "Zapier pain", "category": "WORKFLOW_AUTOMATION"}
    # Call 1: OK
    assert optimizer.pre_invocation_check("search_corpus", args) is True
    # Call 2: OK (duplicate threshold = 2)
    assert optimizer.pre_invocation_check("search_corpus", args) is True

    # Call 3: Loop prevention trigger
    with pytest.raises(ToolLoopDetectedException):
        optimizer.pre_invocation_check("search_corpus", args)

    metrics = optimizer.get_metrics()
    assert metrics["blocked_runaway_loops"] == 1

    # Schema output validation
    valid_cap = optimizer.validate_output(
        {"name": "Python", "category": "Engineering", "proficiency": 4, "years_experience": 2.0},
        CapabilityItem
    )
    assert valid_cap.name == "Python"


# 5. Layer 5: Async & Parallel Execution
@pytest.mark.anyio
async def test_layer5_parallel_execution():
    executor = ParallelPipelineExecutor()

    def task_a():
        return "result_a"

    def task_b():
        return "result_b"

    results = await executor.execute_concurrently([
        ("task_a", task_a),
        ("task_b", task_b)
    ])
    assert results["task_a"] == "result_a"
    assert results["task_b"] == "result_b"
    assert executor.parallel_jobs_dispatched == 2


# 6. Layer 6: Four-Tier Caching Strategy
def test_layer6_caching():
    cache = FourTierCacheManager()

    # Tier 1: Response Cache
    payload = {"founder": "Zayd", "skills": "python, n8n"}
    assert cache.get_response(payload) is None
    cache.set_response(payload, {"score": 85.0})
    cached = cache.get_response(payload)
    assert cached["score"] == 85.0

    # Tier 2: Embedding Cache
    assert cache.get_embedding("text snippet") is None
    cache.set_embedding("text snippet", [0.12, 0.45, 0.99])
    assert cache.get_embedding("text snippet") == [0.12, 0.45, 0.99]

    # Tier 3: Tool Cache
    tool_args = {"category": "WORKFLOW_AUTOMATION"}
    assert cache.get_tool_result("retrieve", tool_args) is None
    cache.set_tool_result("retrieve", tool_args, ["snip-1", "snip-2"])
    assert cache.get_tool_result("retrieve", tool_args) == ["snip-1", "snip-2"]

    # Tier 4: Reasoning Cache
    assert cache.get_reasoning("decomposition", "sig-1") is None
    cache.set_reasoning("decomposition", "sig-1", {"clusters": 3})
    assert cache.get_reasoning("decomposition", "sig-1")["clusters"] == 3

    telemetry = cache.get_telemetry()
    assert telemetry["total_hits"] >= 4
    assert telemetry["hit_ratio_pct"] > 0.0


# 7. Layer 7: Guardrails and Early Exit
def test_layer7_guardrails():
    guardrails = PipelineGuardrails(
        max_loop_iterations=2,
        max_reasoning_steps=5,
        per_step_timeout_sec=5.0,
        total_request_timeout_sec=10.0,
        early_exit_confidence_threshold=0.85
    )
    guardrails.start_request()

    # Steps tracking
    guardrails.start_step("step_1")
    guardrails.end_step("step_1")
    assert guardrails.current_step == 1

    # Loop limit
    assert guardrails.record_loop_back("retrieval") is True
    assert guardrails.record_loop_back("retrieval") is True
    with pytest.raises(GuardrailBreachException):
        guardrails.record_loop_back("retrieval")  # Exceeds max 2 loops

    # Early exit check
    res_no = guardrails.check_early_exit(0.70, "test")
    assert res_no.exited_early is False

    res_yes = guardrails.check_early_exit(0.92, "test")
    assert res_yes.exited_early is True
    assert guardrails.early_exits_triggered == 1
