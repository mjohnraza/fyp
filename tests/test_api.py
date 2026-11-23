import pytest
from fastapi.testclient import TestClient
from src.agentic_os.api.app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "FAST NUCES" in data["institution"]


def test_corpus_categories_endpoint():
    response = client.get("/api/v1/corpus/categories")
    assert response.status_code == 200
    cats = response.json()
    assert "WORKFLOW_AUTOMATION" in cats
    assert "DATA_ETL_ANALYTICS" in cats


def test_frontend_static_serving():
    response = client.get("/")
    assert response.status_code == 200
    assert "Agentic Entrepreneur OS" in response.text
    assert "Fraunces" in response.text


def test_learning_module_serving():
    response = client.get("/learning/")
    assert response.status_code == 200
    assert "Building Businesses Around Fundamental Human Needs" in response.text
    assert "Maslow" in response.text


def test_pipeline_run_api():
    payload = {
        "founder_name": "Tariq",
        "bio": "Automation engineer with FastAPI background",
        "skills_text": "python, fastapi, n8n, docker",
        "category": "WORKFLOW_AUTOMATION",
        "available_hours": 15.0,
        "budget_usd": 500.0,
        "time_horizon_months": 6,
        "confirm_checkpoint": True
    }
    response = client.post("/api/v1/pipeline/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert "scorecard" in data
    assert "founder_decision_memo" in data
