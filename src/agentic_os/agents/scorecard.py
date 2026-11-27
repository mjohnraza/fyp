from typing import Dict, Any, Optional, List
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
    risk_validation_cost: float = Field(..., ge=0.0, le=10.0)  # 10 = low risk, fast validation
    composite_score: float = Field(..., ge=0.0, le=100.0)
    recommendation: str
    score_provenance: Dict[str, str] = Field(default_factory=dict)


class OpportunityScoringAgent:
    """Agent 7: Evaluates opportunities across the Ten-Dimension Scorecard
    grounded in Section 4.d and Table III of the FYP proposal.
    """

    def score_opportunity(
        self,
        name: str,
        profile: FounderProfile,
        intersection: Optional[CapabilityIntersection],
        triangulated_evidence: TriangulatedEvidence,
        obstacle_chain: ObstacleChain,
        product_suite: ProductSuite
    ) -> OpportunityScorecard:
        # 1. Buyer Pain: Average severity of obstacle chain
        avg_sev = obstacle_chain.total_friction_score / max(1, len(obstacle_chain.ordered_obstacles))
        buyer_pain = round(min(10.0, avg_sev), 1)

        # 2. Evidence Strength: Diversity and citation coverage
        ev_strength = round(min(10.0, (triangulated_evidence.source_diversity_count * 2.5) * obstacle_chain.coverage_ratio), 1)

        # 3. Capability Fit: Verified capabilities count + available weekly hours
        cap_count = len(profile.capabilities)
        cap_fit = round(min(10.0, (min(cap_count, 5) * 1.2) + min(4.0, profile.context.available_hours_per_week / 5.0)), 1)

        # 4. Multiplicative Potential: Bouchaud & Mézard [11] - LTV-to-delivery-hour ratio
        ltv = product_suite.total_lifetime_value_estimate_usd
        core_hours = max(1.0, product_suite.core_offer.target_delivery_hours)
        mult_pot = round(min(10.0, max(3.0, (ltv / (core_hours * 100.0)) + (2.0 if product_suite.backend_asset.is_recurring else 0.0))), 1)

        # 5. Opportunity Surface Area: Pluchino et al. [12] - free lead magnet + snippet frequency weights
        avg_freq = sum(s.frequency_weight for s in triangulated_evidence.snippets) / max(1, len(triangulated_evidence.snippets))
        surf_area = round(min(10.0, (5.0 if product_suite.lead_magnet.price_point_usd == 0 else 3.0) + min(5.0, avg_freq * 1.8)), 1)

        # 6. Defensibility: Barney (RBV) [15] - cross-cluster intersection uniqueness (fallback 4.0 if None)
        if intersection is not None:
            defense = round(min(10.0, intersection.uniqueness_score * 10.0), 1)
            def_prov = f"Derived from intersection {intersection.intersection_id} uniqueness ({intersection.uniqueness_score})."
        else:
            defense = 4.0
            def_prov = "No cross-cluster intersection detected; assigned single-cluster baseline (4.0)."

        # 7. AI Leverage: Maresca [14] - fraction of founder capabilities in AI/NLP or Automation
        ai_auto_caps = sum(1 for c in profile.capabilities if c.category in ("AI/NLP", "Automation"))
        ai_lev = round(min(10.0, 4.5 + (ai_auto_caps * 1.5)), 1)

        # 8. Recurring Revenue Potential: Monthly MRR share of total LTV
        annual_mrr = product_suite.backend_asset.price_point_usd * 12.0 if product_suite.backend_asset.is_recurring else 0.0
        mrr_share = (annual_mrr / max(1.0, ltv))
        recurring = round(min(10.0, 2.0 + (mrr_share * 8.0)), 1)

        # 9. Asset Accumulation Potential: Penrose [16] - reusable deliverables count & intersection depth
        deliv_count = len(product_suite.core_offer.deliverables) + len(product_suite.lead_magnet.deliverables)
        asset_accum = round(min(10.0, 4.0 + (deliv_count * 0.8) + (1.0 if intersection else 0.0)), 1)

        # 10. Risk / Validation Cost: Kelly [13] - runway adequacy & low lead-magnet delivery hours
        lead_hours = product_suite.lead_magnet.target_delivery_hours
        budget_score = 4.5 if profile.constraints.financial_budget_usd >= 200 else 2.5
        time_score = max(1.0, 5.5 - lead_hours)
        risk_val = round(min(10.0, budget_score + time_score), 1)

        scores = [
            buyer_pain, ev_strength, cap_fit, mult_pot, surf_area,
            defense, ai_lev, recurring, asset_accum, risk_val
        ]
        composite = round(sum(scores), 1)

        if intersection is None:
            recommendation = "INSUFFICIENT INTERSECTION - Expand skills or target a multi-cluster niche."
        elif composite >= 72.0:
            recommendation = "STRONG PURSUE - Asset formation profile highly viable."
        else:
            recommendation = "CONDITIONAL PURSUE - Strengthen evidence or offer leverage."

        provenance = {
            "buyer_pain": f"Mean severity across {len(obstacle_chain.ordered_obstacles)} obstacles ({avg_sev:.1f}/10).",
            "evidence_strength": f"{triangulated_evidence.source_diversity_count} distinct source types * {obstacle_chain.coverage_ratio:.2f} coverage.",
            "capability_fit": f"{cap_count} matched capabilities and {profile.context.available_hours_per_week} hrs/wk availability.",
            "multiplicative_potential": f"Estimated LTV (${ltv:,.0f}) relative to {core_hours}h core delivery.",
            "opportunity_surface_area": f"Lead magnet price (${product_suite.lead_magnet.price_point_usd}) + mean snippet frequency ({avg_freq:.1f}).",
            "defensibility": def_prov,
            "ai_leverage": f"{ai_auto_caps} AI/NLP or Automation capabilities detected in founder profile.",
            "recurring_revenue_potential": f"Recurring backend accounts for {mrr_share*100:.0f}% of 12-month LTV.",
            "asset_accumulation_potential": f"{deliv_count} reusable productized deliverables across tiers.",
            "risk_validation_cost": f"Budget ${profile.constraints.financial_budget_usd} and {lead_hours}h lead-magnet build."
        }

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
            recommendation=recommendation,
            score_provenance=provenance
        )
