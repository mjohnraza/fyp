from typing import Dict, Any, Optional, List
from src.agentic_os.schemas.offer import ValueEquationDiagnosis
from src.agentic_os.schemas.obstacle import ObstacleChain, ObstaclePhase
from src.agentic_os.schemas.profile import CapabilityIntersection


class OfferDiagnosisAgent:
    """Agent 8: Formalizes Alex Hormozi's Value Equation [8]:
    Value = (Dream Outcome * Perceived Likelihood) / (Time Delay * Effort/Sacrifice).
    """

    def diagnose_offer(
        self,
        category: str,
        obstacle_chain: ObstacleChain,
        intersection: Optional[CapabilityIntersection] = None
    ) -> ValueEquationDiagnosis:
        # 1. Dream Outcome (0-10): Severity of pain relieved directly reflects value of dream outcome
        avg_severity = obstacle_chain.total_friction_score / max(1, len(obstacle_chain.ordered_obstacles))
        dream_outcome = round(min(9.5, max(4.0, avg_severity + 0.6)), 1)

        # 2. Perceived Likelihood of Achievement (0-10): Grounded by intersection uniqueness & citation coverage
        uniqueness = intersection.uniqueness_score if intersection else 0.55
        perceived_likelihood = round(min(9.5, max(3.5, (uniqueness * 8.5) + (obstacle_chain.coverage_ratio * 1.5))), 1)

        # 3. Time Delay (0.1 - 10.0): Estimated from execution-phase friction & intersection readiness
        exec_obs = [o for o in obstacle_chain.ordered_obstacles if o.phase == ObstaclePhase.DURING_EXECUTION]
        exec_severity = (sum(o.severity for o in exec_obs) / len(exec_obs)) if exec_obs else avg_severity
        readiness_discount = 0.8 if intersection else 0.0
        time_delay = round(min(9.0, max(1.5, (exec_severity * 0.38) - readiness_discount)), 1)

        # 4. Effort & Sacrifice (0.1 - 10.0): Estimated from after-completion maintenance debt & before-attempt friction
        post_obs = [o for o in obstacle_chain.ordered_obstacles if o.phase == ObstaclePhase.AFTER_COMPLETION]
        post_severity = (sum(o.severity for o in post_obs) / len(post_obs)) if post_obs else avg_severity
        effort_sacrifice = round(min(9.0, max(1.8, (post_severity * 0.40) - (0.5 if intersection else 0.0))), 1)

        # Compute Value Equation Score
        numerator = dream_outcome * perceived_likelihood
        denominator = time_delay * effort_sacrifice
        computed_score = round(numerator / denominator, 2)

        # Identify bottleneck
        dimensions = {
            "Time Delay": time_delay,
            "Effort & Sacrifice": effort_sacrifice,
            "Perceived Likelihood": 10.0 - perceived_likelihood,
            "Dream Outcome": 10.0 - dream_outcome,
        }
        bottleneck = max(dimensions, key=dimensions.get)

        recommendations = {
            "Time Delay": "Implement a 24-hour rapid setup template or instant docker compose script to slash time-to-first-value.",
            "Effort & Sacrifice": "Package the service as 'Done-For-You' configuration with automated self-healing so the buyer does zero maintenance.",
            "Perceived Likelihood": "Provide a concrete 14-day money-back guarantee and published case studies with code audits.",
            "Dream Outcome": "Tie the guarantee directly to revenue protection (e.g. 'protects 100% of pipeline leads from silent drop').",
        }

        assumptions: List[str] = [
            f"Dream Outcome ({dream_outcome}) estimated from mean obstacle severity ({avg_severity:.1f}/10).",
            f"Perceived Likelihood ({perceived_likelihood}) estimated from intersection uniqueness ({uniqueness:.2f}) and citation coverage ({obstacle_chain.coverage_ratio:.2f}).",
            f"Time Delay ({time_delay}) estimated from DURING_EXECUTION severity ({exec_severity:.1f}/10); empirical validation required in FYP-II.",
            f"Effort & Sacrifice ({effort_sacrifice}) estimated from AFTER_COMPLETION maintenance severity ({post_severity:.1f}/10); empirical validation required in FYP-II."
        ]

        return ValueEquationDiagnosis(
            dream_outcome=dream_outcome,
            perceived_likelihood=perceived_likelihood,
            time_delay=time_delay,
            effort_sacrifice=effort_sacrifice,
            computed_score=computed_score,
            bottleneck_dimension=bottleneck,
            remediation_recommendation=recommendations[bottleneck],
            assumptions=assumptions
        )
