from typing import List
from src.agentic_os.schemas.corpus import EvidenceSnippet, OutcomeCategory, SourceType, TriangulatedEvidence


class EvidenceTriangulator:
    """Evaluates multi-source triangulation as mandated by Section 6.c."""

    MIN_SOURCES_REQUIRED = 2

    def triangulate(
        self,
        category: OutcomeCategory,
        snippets: List[EvidenceSnippet]
    ) -> TriangulatedEvidence:
        distinct_sources = list({s.source_type for s in snippets})
        diversity_count = len(distinct_sources)
        passed = diversity_count >= self.MIN_SOURCES_REQUIRED

        # Theoretical ratio based on 4 possible sources
        ratio = min(1.0, diversity_count / 4.0)

        return TriangulatedEvidence(
            category=category,
            snippets=snippets,
            source_types_represented=distinct_sources,
            source_diversity_count=diversity_count,
            triangulation_passed=passed,
            triangulation_ratio=round(ratio, 2)
        )
