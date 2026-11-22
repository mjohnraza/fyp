from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ObstaclePhase(str, Enum):
    BEFORE_ATTEMPT = "BEFORE_ATTEMPT"       # Friction in evaluating, choosing, or initiating
    DURING_EXECUTION = "DURING_EXECUTION"   # Technical bugs, configuration errors, setup friction
    AFTER_COMPLETION = "AFTER_COMPLETION"   # Maintenance debt, ongoing cost, brittle sync, lack of audits


class ObstacleNode(BaseModel):
    obstacle_id: str
    phase: ObstaclePhase
    label: str = Field(..., description="Normalized short label")
    description: str = Field(..., description="Detailed description of buyer pain point")
    severity: int = Field(5, ge=1, le=10, description="Pain intensity")
    citations: List[str] = Field(default_factory=list, description="IDs of backing evidence snippets")
    failure_mode: str = Field(..., description="What happens if this obstacle is not cleared")
    underlying_buyer_emotion: Optional[str] = "Overwhelmed / Frustrated"


class ObstacleChain(BaseModel):
    chain_id: str
    target_category: str
    ordered_obstacles: List[ObstacleNode]
    total_friction_score: float = 0.0
    coverage_ratio: float = Field(1.0, ge=0.0, le=1.0, description="Percentage of obstacles with >=1 citation")
