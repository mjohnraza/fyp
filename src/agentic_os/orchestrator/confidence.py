from typing import List, Optional
from src.agentic_os.schemas.orchestration import ConfidenceReport
from src.agentic_os.schemas.profile import DecompositionOutput
from src.agentic_os.schemas.corpus import TriangulatedEvidence
from src.agentic_os.schemas.obstacle import ObstacleChain


class ConfidenceEvaluator:
    """Evaluates grounding and consistency signals rather than relying on
    self-reported LLM confidence (Section 6.f of Proposal).
    """

    GROUNDING_THRESHOLD = 0.65
    CONSISTENCY_THRESHOLD = 0.70

    def evaluate(
        self,
        decomposition: DecompositionOutput,
        triangulated_evidence: TriangulatedEvidence,
        obstacle_chain: ObstacleChain
    ) -> ConfidenceReport:
        # Grounding Confidence: Based on source diversity and obstacle citation coverage
        source_factor = triangulated_evidence.triangulation_ratio
        coverage_factor = obstacle_chain.coverage_ratio
        grounding_score = round((source_factor * 0.5) + (coverage_factor * 0.5), 2)

        # Consistency Confidence: Internal non-contradiction
        consistency_score = round(decomposition.confidence_score, 2)

        # Composite score
        composite = round((grounding_score * 0.5) + (consistency_score * 0.5), 2)

        requires_loop = False
        loop_target: Optional[str] = None
        rationale = "Grounding and consistency metrics meet target thresholds."

        if grounding_score < self.GROUNDING_THRESHOLD:
            requires_loop = True
            loop_target = "RETRIEVAL_AGENT"
            rationale = (
                f"Weak grounding detected (score: {grounding_score} < {self.GROUNDING_THRESHOLD}). "
                f"Requires loop-back to Market Evidence Retrieval to expand source triangulation."
            )
        elif consistency_score < self.CONSISTENCY_THRESHOLD:
            requires_loop = True
            loop_target = "PROFILER_AGENT"
            rationale = (
                f"Low consistency detected (score: {consistency_score} < {self.CONSISTENCY_THRESHOLD}). "
                f"Contradictions between constraints and capability ambition require profile refinement."
            )

        return ConfidenceReport(
            grounding_confidence=grounding_score,
            consistency_confidence=consistency_score,
            composite_confidence=composite,
            requires_loop_back=requires_loop,
            loop_back_target=loop_target,
            rationale=rationale
        )
