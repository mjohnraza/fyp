from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
import uvicorn

from src.agentic_os.schemas.profile import FounderProfile, DecompositionOutput
from src.agentic_os.schemas.corpus import OutcomeCategory, TriangulatedEvidence
from src.agentic_os.schemas.obstacle import ObstacleChain
from src.agentic_os.schemas.offer import ValueEquationDiagnosis, ProductSuite
from src.agentic_os.schemas.orchestration import FounderDecisionMemo
from src.agentic_os.orchestrator.pipeline import MasterOrchestrator

app = FastAPI(
    title="Agentic Entrepreneur OS API",
    description="REST API for FAST NUCES FYP-I: Opportunity Discovery Pipeline",
    version="1.0.0"
)

orchestrator = MasterOrchestrator()


class PipelineRunRequest(BaseModel):
    founder_name: str = "Ahmed"
    bio: str = "Senior Python engineer with experience in FastAPI and automation"
    skills_text: str = "python, fastapi, n8n, docker, postgresql, rag"
    category: OutcomeCategory = OutcomeCategory.WORKFLOW_AUTOMATION
    available_hours: float = 15.0
    budget_usd: float = 500.0
    time_horizon_months: int = 6
    confirm_checkpoint: bool = True


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Agentic Entrepreneur OS",
        "version": "1.0.0",
        "institution": "FAST NUCES Karachi"
    }


@app.get("/api/v1/corpus/categories")
def get_categories():
    return [c.value for c in OutcomeCategory]


@app.post("/api/v1/pipeline/run")
def run_full_pipeline(req: PipelineRunRequest):
    try:
        result = orchestrator.run_pipeline(
            founder_name=req.founder_name,
            bio=req.bio,
            skills_text=req.skills_text,
            category=req.category,
            available_hours=req.available_hours,
            budget_usd=req.budget_usd,
            time_horizon_months=req.time_horizon_months,
            confirm_checkpoint=req.confirm_checkpoint
        )
        return {
            "status": result["status"],
            "run_log": result["run_log"],
            "profile": result["profile"].model_dump(),
            "decomposition": result["decomposition"].model_dump(),
            "scorecard": result["scorecard"].model_dump(),
            "value_diagnosis": result["value_diagnosis"].model_dump(),
            "product_suite": result["product_suite"].model_dump(),
            "founder_decision_memo": result["founder_decision_memo"].model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
LEARNING_DIR = ROOT_DIR / "learning_module"

if LEARNING_DIR.exists():
    learning_index = LEARNING_DIR / "index.html"

    @app.get("/learning")
    @app.get("/learning/")
    @app.get("/learning-module")
    @app.get("/learning_module")
    @app.get("/learning_module/index.html")
    def serve_learning_module():
        return FileResponse(learning_index)

    app.mount("/learning", StaticFiles(directory=str(LEARNING_DIR), html=True), name="learning")
    app.mount("/learning_module", StaticFiles(directory=str(LEARNING_DIR), html=True), name="learning_module_static")

if FRONTEND_DIR.exists():
    frontend_index = FRONTEND_DIR / "index.html"

    @app.get("/")
    @app.get("/index.html")
    @app.get("/frontend")
    @app.get("/frontend/index.html")
    def serve_frontend_root():
        return FileResponse(frontend_index)

    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


def start():
    uvicorn.run("src.agentic_os.api.app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    start()
