import pytest
from fastapi.testclient import TestClient

from src.agentic_os.api.app import app
from src.agentic_os.runtime.skill_loader import SkillLoader
from src.agentic_os.runtime.mcp_client import MCPStdioClient
from src.agentic_os.runtime.tool_registry import ToolRegistry
from src.agentic_os.runtime.base_agent import BaseReActAgent
from src.agentic_os.runtime.skill_agents import (
    ObstacleExtractionAgent,
    OfferDiagnosticianAgent,
    OpportunityCoordinatorAgent,
)


def test_skill_loader_discovers_all_skills():
    loader = SkillLoader()
    skills = loader.list_skills()
    names = {s.name for s in skills}
    assert "agentic-entrepreneur-os" in names
    assert "obstacle-chain-extractor" in names
    assert "offer-diagnostician" in names

    prompt = loader.render_system_prompt(["obstacle-chain-extractor", "offer-diagnostician"])
    assert "Active Skill: obstacle-chain-extractor" in prompt
    assert "Active Skill: offer-diagnostician" in prompt
    assert "Value Equation" in prompt


def test_mcp_stdio_client_live_handshake_and_call():
    with MCPStdioClient(server_name="agentic-os-engine") as client:
        tools = client.list_tools()
        tool_names = {t["name"] for t in tools}
        assert "ingest_profile" in tool_names
        assert "retrieve_evidence" in tool_names
        assert "generate_founder_decision_memo" in tool_names

        evidence = client.call_tool("retrieve_evidence", {"category": "WORKFLOW_AUTOMATION"})
        assert evidence["triangulation_passed"] is True
        assert evidence["source_diversity_count"] >= 2


def test_tool_registry_attaches_mcp_tools():
    registry = ToolRegistry(attach_mcp=True)
    try:
        mcp_tool = registry.get_tool("generate_founder_decision_memo")
        assert mcp_tool is not None
        assert mcp_tool.source == "mcp:agentic-os-engine"

        schemas = registry.get_ollama_tool_schemas(["retrieve_evidence"])
        assert len(schemas) == 1
        assert schemas[0]["function"]["name"] == "retrieve_evidence"
    finally:
        registry.close()


def test_obstacle_extraction_agent_loop():
    agent = ObstacleExtractionAgent(use_llm=False)
    result = agent.run(category="DATA_ETL_ANALYTICS")

    assert result.status in ("COMPLETED", "EARLY_EXIT")
    assert "obstacle-chain-extractor" in result.skills_loaded
    assert "retrieve_evidence" in result.collected_outputs
    assert "extract_obstacle_chain" in result.collected_outputs
    assert result.collected_outputs["extract_obstacle_chain"]["coverage_ratio"] >= 0.65


def test_offer_diagnostician_agent_loop():
    agent = OfferDiagnosticianAgent(use_llm=False)
    result = agent.run(category="WORKFLOW_AUTOMATION", skills_text="python, fastapi, n8n")

    assert result.status in ("COMPLETED", "EARLY_EXIT")
    assert "offer-diagnostician" in result.skills_loaded
    assert result.collected_outputs["diagnose_offer_value"]["computed_score"] > 0
    assert result.collected_outputs["generate_product_suite"]["backend_asset"]["is_recurring"] is True


def test_opportunity_coordinator_agent_with_live_mcp_loop():
    coordinator = OpportunityCoordinatorAgent(attach_mcp=True, use_llm=False)
    result = coordinator.run(
        founder_name="Zayd",
        skills_text="python, fastapi, n8n, docker",
        category="WORKFLOW_AUTOMATION",
        available_hours=15.0,
        budget_usd=500.0,
        confirm_checkpoint=True
    )

    assert result.status in ("COMPLETED", "EARLY_EXIT")
    assert len(result.skills_loaded) == 3
    assert result.iterations_used >= 6
    assert "generate_founder_decision_memo" in result.collected_outputs
    memo = result.collected_outputs["generate_founder_decision_memo"]["founder_decision_memo"]
    assert memo["memo_id"].startswith("MEMO-")
    # Verify tools were executed via live MCP server
    mcp_traces = [t for t in result.traces if t.tool_source == "mcp:agentic-os-engine"]
    assert len(mcp_traces) >= 5


def test_react_agent_loop_prevention_guardrail():
    agent = BaseReActAgent(
        name="LoopTestAgent",
        skill_names=["obstacle-chain-extractor"],
        allowed_tools=["retrieve_evidence"],
        max_iterations=6,
        use_llm=False
    )
    # Intentionally repeat the exact same tool+args 3 times (max_allowed_duplicate_calls=2)
    repetitive_plan = [
        {"thought": "Call 1", "tool_name": "retrieve_evidence", "tool_args": {"category": "WORKFLOW_AUTOMATION"}},
        {"thought": "Call 2", "tool_name": "retrieve_evidence", "tool_args": {"category": "WORKFLOW_AUTOMATION"}},
        {"thought": "Call 3 (should halt)", "tool_name": "retrieve_evidence", "tool_args": {"category": "WORKFLOW_AUTOMATION"}},
    ]
    result = agent.run_loop(
        goal="Test loop breaker",
        initial_context={"category": "WORKFLOW_AUTOMATION"},
        planned_sequence=repetitive_plan
    )
    assert result.status == "GUARDRAIL_HALTED"
    assert "Loop prevention triggered" in result.final_summary


def test_agent_api_endpoints():
    client = TestClient(app)

    r_skills = client.get("/api/v1/agent/skills")
    assert r_skills.status_code == 200
    assert len(r_skills.json()) >= 3

    r_tools = client.get("/api/v1/agent/tools")
    assert r_tools.status_code == 200
    assert len(r_tools.json()) >= 7

    r_run = client.post(
        "/api/v1/agent/run?use_llm=false&attach_mcp=true",
        json={
            "founder_name": "Ayesha",
            "bio": "Data Engineer",
            "skills_text": "python, sql, etl, docker",
            "category": "DATA_ETL_ANALYTICS",
            "available_hours": 15.0,
            "budget_usd": 500.0,
            "confirm_checkpoint": True
        }
    )
    assert r_run.status_code == 200
    data = r_run.json()
    assert data["status"] in ("COMPLETED", "EARLY_EXIT")
    assert "generate_founder_decision_memo" in data["collected_outputs"]
