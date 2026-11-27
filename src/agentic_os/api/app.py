import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
import uvicorn

from src.agentic_os.schemas.corpus import OutcomeCategory
from src.agentic_os.orchestrator.pipeline import MasterOrchestrator
from src.agentic_os.runtime.skill_loader import SkillLoader
from src.agentic_os.runtime.tool_registry import ToolRegistry
from src.agentic_os.runtime.skill_agents import OpportunityCoordinatorAgent

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic Entrepreneur OS API",
    description="REST API for FAST NUCES FYP-I: Opportunity Discovery Pipeline",
    version="1.0.0"
)

orchestrator = MasterOrchestrator()


class PipelineRunRequest(BaseModel):
    founder_name: str = Field("Ahmed", min_length=1, max_length=100)
    bio: str = Field("Senior Python engineer with experience in FastAPI and automation", min_length=1)
    skills_text: str = Field("python, fastapi, n8n, docker, postgresql, rag", min_length=1)
    category: OutcomeCategory = OutcomeCategory.WORKFLOW_AUTOMATION
    available_hours: float = Field(15.0, ge=1.0, le=100.0)
    budget_usd: float = Field(500.0, ge=0.0)
    time_horizon_months: int = Field(6, ge=1, le=60)
    confirm_checkpoint: bool = Field(False, description="Must be explicitly True to unlock Founder Decision Memo")
    stop_on_early_exit: bool = False


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
            confirm_checkpoint=req.confirm_checkpoint,
            stop_on_early_exit=req.stop_on_early_exit
        )
        memo_obj = result.get("founder_decision_memo")
        return {
            "status": result["status"],
            "run_log": result["run_log"],
            "profile": result["profile"].model_dump(),
            "decomposition": result["decomposition"].model_dump(),
            "scorecard": result["scorecard"].model_dump() if result.get("scorecard") else None,
            "value_diagnosis": result["value_diagnosis"].model_dump() if result.get("value_diagnosis") else None,
            "product_suite": result["product_suite"].model_dump() if result.get("product_suite") else None,
            "human_checkpoint": result["human_checkpoint"].model_dump() if result.get("human_checkpoint") else None,
            "founder_decision_memo": memo_obj.model_dump() if memo_obj else None,
            "optimization_audit": result.get("optimization_audit", {}),
            "from_cache": result.get("from_cache", False)
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail="Invalid pipeline input parameters.") from e
    except Exception:
        logger.exception("Unhandled error during pipeline execution")
        raise HTTPException(status_code=500, detail="Internal pipeline error. Check server logs.")


@app.get("/api/v1/agent/skills")
def list_loaded_skills():
    loader = SkillLoader()
    return [s.model_dump() for s in loader.list_skills()]


@app.get("/api/v1/agent/tools")
def list_available_tools(attach_mcp: bool = False):
    registry = ToolRegistry(attach_mcp=attach_mcp)
    try:
        return [t.model_dump() for t in registry.list_tools()]
    finally:
        registry.close()


@app.post("/api/v1/agent/run")
def run_skill_mcp_agent_loop(req: PipelineRunRequest, use_llm: bool = False, attach_mcp: bool = True):
    try:
        coordinator = OpportunityCoordinatorAgent(attach_mcp=attach_mcp, use_llm=use_llm)
        exec_result = coordinator.run(
            founder_name=req.founder_name,
            skills_text=req.skills_text,
            category=req.category.value,
            available_hours=req.available_hours,
            budget_usd=req.budget_usd
        )
        return exec_result.model_dump()
    except Exception:
        logger.exception("Unhandled error during agent loop execution")
        raise HTTPException(status_code=500, detail="Internal agent execution error. Check server logs.")


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
