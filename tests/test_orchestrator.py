import pytest
from src.agentic_os.schemas.corpus import OutcomeCategory
from src.agentic_os.orchestrator.pipeline import MasterOrchestrator


def test_master_orchestrator_full_run():
    orchestrator = MasterOrchestrator()

    result = orchestrator.run_pipeline(
        founder_name="Hamza",
        bio="Full-stack engineer building AI systems and ETL pipelines",
        skills_text="python, fastapi, docker, postgresql, n8n, rag",
        category=OutcomeCategory.WORKFLOW_AUTOMATION,
        available_hours=15.0,
        budget_usd=500.0,
        confirm_checkpoint=True
    )

    assert result["status"] == "COMPLETED"
    assert len(result["run_log"]) >= 8
    assert result["confidence_report"].composite_confidence >= 0.70
    assert result["scorecard"].composite_score >= 70.0
    assert result["founder_decision_memo"].memo_id.startswith("MEMO-")
    assert result["human_checkpoint"].user_confirmed is True


def test_checkpoint_gating():
    orchestrator = MasterOrchestrator()

    # Run without confirming checkpoint
    result = orchestrator.run_pipeline(
        founder_name="Sara",
        bio="Data Analyst transitioning to automation",
        skills_text="python, sql, etl",
        category=OutcomeCategory.DATA_ETL_ANALYTICS,
        available_hours=12.0,
        budget_usd=300.0,
        confirm_checkpoint=False
    )

    assert result["status"] == "AWAITING_HUMAN_CHECKPOINT"
    assert result["human_checkpoint"].user_confirmed is False
    assert len(result["human_checkpoint"].key_assumptions_to_verify) == 3
