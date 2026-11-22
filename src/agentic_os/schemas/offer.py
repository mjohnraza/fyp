from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ValueEquationDiagnosis(BaseModel):
    dream_outcome: float = Field(..., ge=0.0, le=10.0, description="Perceived value of destination")
    perceived_likelihood: float = Field(..., ge=0.0, le=10.0, description="Confidence in achieving result")
    time_delay: float = Field(..., ge=0.1, le=10.0, description="Time taken to realize first value (lower is better)")
    effort_sacrifice: float = Field(..., ge=0.1, le=10.0, description="Labor or friction demanded from buyer (lower is better)")
    computed_score: float = Field(..., description="V = (Dream * Likelihood) / (Time * Effort)")
    bottleneck_dimension: str = Field(..., description="The parameter hurting the offer most")
    remediation_recommendation: str = Field(..., description="Actionable fix to maximize value equation")


class ProductTierType(str, Enum):
    LEAD_MAGNET = "LEAD_MAGNET"                     # Free or $9 audit/template for rapid trust
    CORE_OFFER = "CORE_OFFER"                       # High-ticket, productized asset deployment ($497-$2500)
    COMPOUNDING_BACKEND = "COMPOUNDING_BACKEND"     # Recurring retainer/SaaS maintenance ($99-$499/mo)


class ProductTier(BaseModel):
    tier: ProductTierType
    title: str
    tagline: str
    target_delivery_hours: float
    price_point_usd: float
    is_recurring: bool = False
    deliverables: List[str]
    scalability_mechanic: str


class ProductSuite(BaseModel):
    suite_id: str
    target_niche: str
    lead_magnet: ProductTier
    core_offer: ProductTier
    backend_asset: ProductTier
    total_lifetime_value_estimate_usd: float
    funnel_conversion_thesis: str
