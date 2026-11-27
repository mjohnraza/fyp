from typing import Dict, Any, Optional
from src.agentic_os.schemas.offer import ValueEquationDiagnosis
from src.agentic_os.schemas.obstacle import ObstacleChain
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
        dream_outcome = round(min(9.5, max(5.0, avg_severity + 0.8)), 1)

        # 2. Perceived Likelihood of Achievement (0-10): Grounded by intersection uniqueness & proof
        uniqueness = intersection.uniqueness_score if intersection else 0.80
        perceived_likelihood = round(min(9.0, max(5.0, uniqueness * 10.0)), 1)

        # 3. Time Delay (0.1 - 10.0): Lower is better (faster time to value)
        # Software/automation assets deliver value rapidly (< 7 days) compared to 6-month consulting
        time_delay = 2.5

        # 4. Effort & Sacrifice (0.1 - 10.0): Lower is better
        # Pre-configured deployable asset minimizes buyer effort
        effort_sacrifice = 3.0

        # Compute Value Equation Score
        numerator = dream_outcome * perceived_likelihood
        denominator = time_delay * effort_sacrifice
        computed_score = round(numerator / denominator, 2)

        # Identify bottleneck
        # If time or effort are high, or likelihood is low
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

        return ValueEquationDiagnosis(
            dream_outcome=dream_outcome,
            perceived_likelihood=perceived_likelihood,
            time_delay=time_delay,
            effort_sacrifice=effort_sacrifice,
            computed_score=computed_score,
            bottleneck_dimension=bottleneck,
            remediation_recommendation=recommendations[bottleneck]
        )
