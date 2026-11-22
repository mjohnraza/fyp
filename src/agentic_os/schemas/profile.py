from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProficiencyLevel(int, Enum):
    NOVICE = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    WORLD_CLASS = 5


class CapabilityItem(BaseModel):
    name: str = Field(..., description="Name of the skill or technical capability")
    category: str = Field("Engineering", description="Category: Engineering, Data, Sales, Domain, Operations")
    proficiency: ProficiencyLevel = Field(ProficiencyLevel.ADVANCED, description="1-5 skill level")
    proof: Optional[str] = Field(None, description="Verifiable proof or past project/repo")
    years_experience: float = Field(1.0, ge=0.0)


class ContextItem(BaseModel):
    current_role: str = "Freelancer / Engineer"
    primary_industry: str = "Software & Technology"
    network_reach: str = "Modest (0-500 professional contacts)"
    available_hours_per_week: float = Field(15.0, ge=1.0, le=100.0)
    risk_tolerance: str = "Medium"


class ConstraintItem(BaseModel):
    financial_budget_usd: float = Field(500.0, ge=0.0)
    time_horizon_months: int = Field(6, ge=1, le=60)
    hard_restrictions: List[str] = Field(default_factory=list, description="e.g. no full-time relocation, ethical AI limits")


class FounderProfile(BaseModel):
    id: str
    founder_name: str
    bio: str
    capabilities: List[CapabilityItem]
    context: ContextItem = Field(default_factory=ContextItem)
    constraints: ConstraintItem = Field(default_factory=ConstraintItem)
    raw_text: Optional[str] = None


class CapabilityCluster(BaseModel):
    cluster_id: str
    name: str
    description: str
    capabilities: List[str]
    cohesion_score: float = Field(0.8, ge=0.0, le=1.0)


class CapabilityIntersection(BaseModel):
    intersection_id: str
    cluster_names: List[str]
    combined_capabilities: List[str]
    uniqueness_score: float = Field(0.85, ge=0.0, le=1.0)
    leverage_description: str
    defensibility_hypothesis: str


class ContradictionFlag(BaseModel):
    dimension: str
    severity: str = "HIGH"  # LOW, MEDIUM, HIGH
    issue: str
    suggested_correction: str


class DecompositionOutput(BaseModel):
    profile_id: str
    clusters: List[CapabilityCluster]
    intersections: List[CapabilityIntersection]
    contradictions: List[ContradictionFlag] = Field(default_factory=list)
    confidence_score: float = Field(0.9, ge=0.0, le=1.0)
