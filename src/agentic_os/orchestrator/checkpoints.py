from typing import List
from src.agentic_os.schemas.orchestration import HumanCheckpointCopy
from src.agentic_os.schemas.offer import ProductSuite
from src.agentic_os.schemas.obstacle import ObstacleChain


class HumanCheckpointManager:
    """Manages the mandatory human-in-the-loop checkpoint before external commitment.
    Implements Power 1 (Regret Minimization) and Power 7 (Self-Permission) copy conventions.
    """

    def generate_checkpoint(
        self,
        founder_name: str,
        product_suite: ProductSuite,
        obstacle_chain: ObstacleChain,
        budget_usd: float
    ) -> HumanCheckpointCopy:
        assumptions = [
            f"Assumes target buyers ({product_suite.target_niche}) experience severe friction around '{obstacle_chain.ordered_obstacles[0].label}'.",
            f"Assumes the free lead magnet '{product_suite.lead_magnet.title}' can capture qualified emails at < $5 CAC.",
            f"Assumes the core offer priced at ${product_suite.core_offer.price_point_usd:,.0f} can convert at >= 3% from qualified leads."
        ]

        regret_statement = (
            f"Looking back 12 months from now, which would you regret more: "
            f"Spending 5 hours deploying '{product_suite.lead_magnet.title}' and getting zero replies, "
            f"or wondering whether a multi-thousand dollar recurring asset engine was within your reach?"
        )

        kelly_advice = (
            f"Per Kelly-sizing principles [13]: With a total budget of ${budget_usd:.0f}, allocate no more than "
            f"${min(50.0, budget_usd * 0.15):.0f} (or 10-15%) to this initial validation experiment. "
            f"Never bet enough capital on a single experiment to jeopardize your survival runway."
        )

        invitation = (
            f"Hello {founder_name}. The Agentic Entrepreneur OS has structured your capabilities into an "
            f"evidence-grounded opportunity. We present this checkpoint not to pressure you into immediate commitment, "
            f"but to invite you to audit the underlying assumptions before deploying real outreach or capital."
        )

        return HumanCheckpointCopy(
            gate_name="PRE_OUTREACH_VALIDATION_GATE",
            invitation_message=invitation,
            key_assumptions_to_verify=assumptions,
            potential_regret_statement=regret_statement,
            kelly_sizing_advice=kelly_advice,
            user_confirmed=False
        )
