from typing import Dict, Any
from pydantic import BaseModel, Field
from src.agentic_os.schemas.profile import FounderProfile, CapabilityIntersection
from src.agentic_os.schemas.corpus import TriangulatedEvidence
from src.agentic_os.schemas.obstacle import ObstacleChain
from src.agentic_os.schemas.offer import ProductSuite


class OpportunityScorecard(BaseModel):
    opportunity_name: str
    buyer_pain: float = Field(..., ge=0.0, le=10.0)
    evidence_strength: float = Field(..., ge=0.0, le=10.0)
    capability_fit: float = Field(..., ge=0.0, le=10.0)
    multiplicative_potential: float = Field(..., ge=0.0, le=10.0)
    opportunity_surface_area: float = Field(..., ge=0.0, le=10.0)
    defensibility: float = Field(..., ge=0.0, le=10.0)
    ai_leverage: float = Field(..., ge=0.0, le=10.0)
    recurring_revenue_potential: float = Field(..., ge=0.0, le=10.0)
    asset_accumulation_potential: float = Field(..., ge=0.0, le=10.0)
    risk_validation_cost: float = Field(..., ge=0.0, le=10.0)  # Lower risk = higher score (10 = low risk, fast validation)
    composite_score: float = Field(..., ge=0.0, le=100.0)
    recommendation: str


class OpportunityScoringAgent:
    """Agent 7: Evaluates opportunities across the Ten-Dimension Scorecard
    grounded in Section 4.d and Table III of the FYP proposal.
    """

    def score_opportunity(
        self,
        name: str,
        profile: FounderProfile,
        intersection: CapabilityIntersection,
        triangulated_evidence: TriangulatedEvidence,
        obstacle_chain: ObstacleChain,
        product_suite: ProductSuite
    ) -> OpportunityScorecard:
        # 1. Buyer Pain: Average severity of obstacle chain
        buyer_pain = round(min(10.0, obstacle_chain.total_friction_score / max(1, len(obstacle_chain.ordered_obstacles))), 1)

        # 2. Evidence Strength: Diversity and citation coverage
        ev_strength = round(min(10.0, (triangulated_evidence.source_diversity_count * 2.5) * obstacle_chain.coverage_ratio), 1)

        # 3. Capability Fit: Founder's available hours and relevant experience
        cap_fit = round(min(10.0, 7.0 + min(3.0, profile.context.available_hours_per_week / 10.0)), 1)

        # 4. Multiplicative Potential: Bouchaud & Mézard [11] - asset vs labor ratio
        mult_pot = 8.5 if product_suite.backend_asset.is_recurring else 5.0

        # 5. Opportunity Surface Area: Pluchino et al. [12] - distribution & lead magnet reach
        surf_area = 8.0 if product_suite.lead_magnet.price_point_usd == 0 else 6.0

        # 6. Defensibility: Barney (RBV) [15] - proprietary code and data
        defense = round(min(10.0, intersection.uniqueness_score * 10.0), 1)

        # 7. AI Leverage: Maresca [14] - degree to which LLMs accelerate delivery
        ai_lev = 9.0

        # 8. Recurring Revenue Potential: Monthly MRR component
        recurring = 9.0 if product_suite.backend_asset.is_recurring else 4.0

        # 9. Asset Accumulation Potential: Penrose [16] - reusable codebase / dataset
        asset_accum = 8.5

        # 10. Risk / Validation Cost: Kelly [13] - feasibility of rapid test with low downside
        # 10 = minimal capital risk (< $100) and short cycle
        risk_val = 8.5 if profile.constraints.financial_budget_usd >= 100 else 6.5

        scores = [
            buyer_pain, ev_strength, cap_fit, mult_pot, surf_area,
            defense, ai_lev, recurring, asset_accum, risk_val
        ]
        composite = round(sum(scores), 1)

        recommendation = "STRONG PURSUE - Asset formation profile highly viable." if composite >= 75.0 else "CONDITIONAL PURSUE - Strengthen evidence."

        return OpportunityScorecard(
            opportunity_name=name,
            buyer_pain=buyer_pain,
            evidence_strength=ev_strength,
            capability_fit=cap_fit,
            multiplicative_potential=mult_pot,
            opportunity_surface_area=surf_area,
            defensibility=defense,
            ai_leverage=ai_lev,
            recurring_revenue_potential=recurring,
            asset_accumulation_potential=asset_accum,
            risk_validation_cost=risk_val,
            composite_score=composite,
            recommendation=recommendation
        )
