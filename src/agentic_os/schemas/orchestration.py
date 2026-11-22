from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.agentic_os.schemas.profile import DecompositionOutput, FounderProfile
from src.agentic_os.schemas.corpus import TriangulatedEvidence
from src.agentic_os.schemas.obstacle import ObstacleChain
from src.agentic_os.schemas.graph import GroundedBuyerReliefStatement, DualGraphData
from src.agentic_os.schemas.offer import ValueEquationDiagnosis, ProductSuite


class StageStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    LOOP_BACK = "LOOP_BACK"
    BLOCKED_AT_CHECKPOINT = "BLOCKED_AT_CHECKPOINT"


class ConfidenceReport(BaseModel):
    grounding_confidence: float = Field(..., ge=0.0, le=1.0, description="Based on citation density and source triangulation")
    consistency_confidence: float = Field(..., ge=0.0, le=1.0, description="Internal non-contradiction between skills and constraints")
    composite_confidence: float = Field(..., ge=0.0, le=1.0)
    requires_loop_back: bool = False
    loop_back_target: Optional[str] = None
    rationale: str


class HumanCheckpointCopy(BaseModel):
    gate_name: str
    invitation_message: str
    key_assumptions_to_verify: List[str]
    potential_regret_statement: str
    kelly_sizing_advice: str
    user_confirmed: bool = False


class FounderDecisionMemo(BaseModel):
    memo_id: str
    date: str
    founder_name: str
    primary_opportunity_title: str
    target_persona: str
    core_capability_leverage: str
    buyer_obstacle_relieved: str
    evidence_backing: List[str]
    reframe_from_labor_to_asset: str
    value_equation_score: float
    product_suite_summary: Dict[str, Any]
    first_validation_experiment: str
    regret_minimization_framing: str
    confidence_signals: Dict[str, float]
    human_checkpoint: HumanCheckpointCopy
