import pytest
from fastapi.testclient import TestClient

from src.agentic_os.api.app import app
from src.agentic_os.ingestion.profiler import ProfilerAgent
from src.agentic_os.ingestion.contradiction import DecompositionPipeline
from src.agentic_os.retrieval.retriever import MarketEvidenceRetriever
from src.agentic_os.retrieval.triangulation import EvidenceTriangulator
from src.agentic_os.extraction.obstacle_chain import BuyerObstacleChainExtractor
from src.agentic_os.graph.dual_graph import DualGraphTranslationLayer
from src.agentic_os.agents.scorecard import OpportunityScoringAgent
from src.agentic_os.agents.product_suite import ProductSuiteGenerationAgent
from src.agentic_os.orchestrator.pipeline import MasterOrchestrator
from src.agentic_os.optimization.caching_strategy import FourTierCacheManager
from src.agentic_os.runtime.mcp_client import MCPStdioClient
from src.agentic_os.schemas.corpus import OutcomeCategory, EvidenceSnippet, SourceType
from src.agentic_os.schemas.profile import ProficiencyLevel


def test_profiler_unknown_skills():
    """QA-008: Unknown skills must NOT fabricate 'General Python Engineering'."""
    profiler = ProfilerAgent()
    prof = profiler.parse_profile(
        founder_name="TestUser",
        bio="No technical background",
        skills_text="gardening, cooking, painting"
    )
    assert prof.capabilities == []


def test_profiler_proficiency_validation():
    """QA-008: Mentioning a skill does not imply ADVANCED proficiency or 2.5 years."""
    profiler = ProfilerAgent()
    prof = profiler.parse_profile(
        founder_name="BeginnerUser",
        bio="Exploring software tools",
        skills_text="python, docker"
    )
    assert len(prof.capabilities) == 2
    for cap in prof.capabilities:
        assert cap.proficiency == ProficiencyLevel.INTERMEDIATE
        assert cap.years_experience == 0.0


def test_empty_intersections():
    """QA-007: Pipeline & scorecard handle zero intersections without crashing."""
    profiler = ProfilerAgent()
    decomp = DecompositionPipeline().process(
        profiler.parse_profile("SoloSkill", "Developer", "python")  # 1 cluster -> 0 intersections
    )
    assert len(decomp.intersections) == 0

    orch = MasterOrchestrator()
    res = orch.run_pipeline(
        founder_name="SoloSkill",
        bio="Developer",
        skills_text="python",
        category=OutcomeCategory.WORKFLOW_AUTOMATION,
        available_hours=15.0,
        budget_usd=500.0,
        confirm_checkpoint=True
    )
    assert res["status"] == "COMPLETED"
    assert res["scorecard"].defensibility == 4.0
    assert "INSUFFICIENT INTERSECTION" in res["scorecard"].recommendation


def test_profiler_loopback():
    """QA-001: Profiler recovery path is actually invoked when consistency is low."""
    orch = MasterOrchestrator()
    res = orch.run_pipeline(
        founder_name="ConstrainedUser",
        bio="Busy dev",
        skills_text="python, fastapi, n8n",
        category=OutcomeCategory.WORKFLOW_AUTOMATION,
        available_hours=4.0,   # Triggers Time Commitment HIGH contradiction
        budget_usd=20.0,       # Triggers Financial Runway MEDIUM contradiction
        time_horizon_months=1, # Triggers Time Horizon HIGH contradiction
        confirm_checkpoint=False
    )
    assert any("PROFILER_AGENT recovery" in entry for entry in res["run_log"])


def test_low_confidence_persists():
    """QA-001: If low confidence persists after recovery, pipeline escalates instead of silently continuing."""
    orch = MasterOrchestrator()
    res = orch.run_pipeline(
        founder_name="NoSkillsUser",
        bio="No relevant background",
        skills_text="unknown_xyz_skill",
        category=OutcomeCategory.WORKFLOW_AUTOMATION,
        available_hours=4.0,
        budget_usd=20.0,
        time_horizon_months=1,
        confirm_checkpoint=False
    )
    assert res["status"] == "LOW_CONFIDENCE_ESCALATED"
    assert res["founder_decision_memo"] is None
    assert res["scorecard"] is None


def test_early_exit_short_circuits():
    """QA-003: Genuine early exit skips downstream stages when stop_on_early_exit=True."""
    orch = MasterOrchestrator()
    res = orch.run_pipeline(
        founder_name="HighConfUser",
        bio="Senior engineer",
        skills_text="python, fastapi, n8n, docker",
        category=OutcomeCategory.WORKFLOW_AUTOMATION,
        available_hours=15.0,
        budget_usd=500.0,
        stop_on_early_exit=True
    )
    assert res["status"] == "EARLY_EXIT_PARTIAL"
    assert res["scorecard"] is None
    assert res["value_diagnosis"] is None
    assert res["founder_decision_memo"] is None


def test_checkpoint_blocks_memo():
    """QA-002: Unconfirmed checkpoint must block Founder Decision Memo generation."""
    orch = MasterOrchestrator()
    res = orch.run_pipeline(
        founder_name="GatedUser",
        bio="Senior engineer",
        skills_text="python, fastapi, n8n",
        category=OutcomeCategory.WORKFLOW_AUTOMATION,
        confirm_checkpoint=False
    )
    assert res["status"] == "AWAITING_HUMAN_CHECKPOINT"
    assert res["human_checkpoint"].user_confirmed is False
    assert res["founder_decision_memo"] is None


def test_mcp_checkpoint_default():
    """QA-002: MCP generate_founder_decision_memo defaults confirm_checkpoint to False."""
    with MCPStdioClient(server_name="agentic-os-engine") as client:
        out = client.call_tool("generate_founder_decision_memo", {
            "founder_name": "MCPUser",
            "skills_text": "python, fastapi, n8n",
            "category": "WORKFLOW_AUTOMATION"
        })
        assert out["status"] == "AWAITING_HUMAN_CHECKPOINT"
        assert out["founder_decision_memo"] is None
        assert out["human_checkpoint"]["user_confirmed"] is False


def test_wrong_category_evidence():
    """QA-011: Triangulator rejects snippets from a mismatched category."""
    triangulator = EvidenceTriangulator()
    wrong_snippet = EvidenceSnippet(
        snippet_id="SNIP-WRONG-01",
        category=OutcomeCategory.COMPLIANCE_SECURITY,
        source_type=SourceType.FORUM,
        source_title="Wrong cat",
        source_url_or_ref="https://example.com",
        raw_quote="Compliance pain",
        pain_point_summary="Compliance pain"
    )
    with pytest.raises(ValueError, match="Mismatched evidence category"):
        triangulator.triangulate(OutcomeCategory.WORKFLOW_AUTOMATION, [wrong_snippet])


def test_graph_multiple_clusters():
    """QA-004: All relevant clusters receive causal relationships in the dual graph."""
    profiler = ProfilerAgent()
    prof = profiler.parse_profile("MultiCluster", "Engineer", "python, fastapi, n8n, sql")
    decomp = DecompositionPipeline().process(prof)
    assert len(decomp.clusters) >= 3

    cat = OutcomeCategory.WORKFLOW_AUTOMATION
    snippets = MarketEvidenceRetriever().retrieve_for_category(cat)
    chain = BuyerObstacleChainExtractor().extract_chain(cat, snippets)
    graph = DualGraphTranslationLayer().construct_dual_graph(decomp.clusters, decomp.intersections, chain)

    causal_sources = {e.source for e in graph.edges if e.relation == "CAUSAL_MECHANISM"}
    assert len(causal_sources) >= 2


def test_cache_invalidation():
    """QA-015: Stale cached results are not reused after invalidation."""
    cache = FourTierCacheManager()
    payload = {"name": "CacheTest", "cat": "WORKFLOW_AUTOMATION"}
    cache.set_response(payload, {"version": 1})
    assert cache.get_response(payload)["version"] == 1

    assert cache.invalidate_response(payload) is True
    assert cache.get_response(payload) is None

    cache.set_response(payload, {"version": 2})
    cache.invalidate_all()
    assert cache.get_response(payload) is None


def test_api_invalid_constraints():
    """QA-013: Invalid numeric constraints return HTTP 422 instead of HTTP 500."""
    client = TestClient(app)
    token = client.post(
        "/api/v1/auth/token",
        data={"username": "ahmed@nu.edu.pk", "password": "founder123"},
    ).json()["access_token"]
    resp = client.post(
        "/api/v1/pipeline/run",
        json={
            "founder_name": "BadInput",
            "bio": "Dev",
            "skills_text": "python",
            "available_hours": -5.0,  # Invalid: must be >= 1.0
            "budget_usd": -100.0      # Invalid: must be >= 0.0
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 422
