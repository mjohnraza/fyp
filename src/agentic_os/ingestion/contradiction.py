from typing import List
from src.agentic_os.schemas.profile import FounderProfile, ContradictionFlag, DecompositionOutput
from src.agentic_os.ingestion.clusterer import ClustererAgent
from src.agentic_os.ingestion.intersection import IntersectionMinerAgent


class ContradictionCheckerAgent:
    """Agent 1d: Flags contradictions and feasibility tensions in the ingested profile."""

    def check_contradictions(self, profile: FounderProfile) -> List[ContradictionFlag]:
        flags: List[ContradictionFlag] = []

        # Check 0: Missing or unverified capabilities
        if len(profile.capabilities) == 0:
            flags.append(
                ContradictionFlag(
                    dimension="Capability Coverage",
                    severity="HIGH",
                    issue="No verifiable technical capabilities detected in profile intake.",
                    suggested_correction="Provide explicit technical skills, projects, or domain tools in the intake."
                )
            )

        # Check 1: Time availability vs ambition
        if profile.context.available_hours_per_week < 8.0:
            flags.append(
                ContradictionFlag(
                    dimension="Time Commitment",
                    severity="HIGH",
                    issue=f"Only {profile.context.available_hours_per_week} hours/week available. Developing enterprise solutions requires minimum 10-15 hours/week.",
                    suggested_correction="Focus on micro-templates or pre-built workflows requiring low initial build time."
                )
            )

        # Check 2: Financial constraints
        if profile.constraints.financial_budget_usd < 100.0:
            flags.append(
                ContradictionFlag(
                    dimension="Financial Runway",
                    severity="MEDIUM",
                    issue="Near-zero budget restricts commercial SaaS API testing and paid validation ads.",
                    suggested_correction="Rely purely on organic developer communities (GitHub, Reddit, Discord) and local open-source LLMs (Ollama)."
                )
            )

        # Check 3: Short time horizon
        if profile.constraints.time_horizon_months < 3:
            flags.append(
                ContradictionFlag(
                    dimension="Time Horizon",
                    severity="HIGH",
                    issue=f"Time horizon of {profile.constraints.time_horizon_months} months is too short for enterprise sales cycles.",
                    suggested_correction="Pivot to rapid B2B productized audits or direct freelancer upskilling assets."
                )
            )

        return flags


class DecompositionPipeline:
    """Full Stage 2 Decomposition Pipeline executing Agents 1a, 1b, 2, and 1d."""

    def __init__(self):
        self.clusterer = ClustererAgent()
        self.miner = IntersectionMinerAgent()
        self.checker = ContradictionCheckerAgent()

    def process(self, profile: FounderProfile) -> DecompositionOutput:
        clusters = self.clusterer.cluster_capabilities(profile)
        intersections = self.miner.mine_intersections(clusters)
        contradictions = self.checker.check_contradictions(profile)

        # Confidence calculation
        penalty = sum(0.35 if c.dimension == "Capability Coverage" else (0.15 if c.severity == "HIGH" else 0.05) for c in contradictions)
        confidence = max(0.25, min(1.0, 0.95 - penalty))

        return DecompositionOutput(
            profile_id=profile.id,
            clusters=clusters,
            intersections=intersections,
            contradictions=contradictions,
            confidence_score=round(confidence, 2)
        )
