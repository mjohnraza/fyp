from typing import List, Dict, Optional
from src.agentic_os.schemas.corpus import EvidenceSnippet, OutcomeCategory, SourceType
from src.agentic_os.corpus.loader import CorpusLoader


class MarketEvidenceRetriever:
    """Agent 3: Market Evidence Retrieval (RAG)."""

    def __init__(self, loader: Optional[CorpusLoader] = None):
        self.loader = loader or CorpusLoader()

    def retrieve_for_category(
        self,
        category: OutcomeCategory,
        min_snippets: int = 2
    ) -> List[EvidenceSnippet]:
        snippets = self.loader.get_by_category(category)
        return snippets[:max(len(snippets), min_snippets)]

    def search_by_keywords(self, keywords: List[str]) -> List[EvidenceSnippet]:
        all_snippets = self.loader.get_all()
        matched: List[tuple[int, EvidenceSnippet]] = []

        kw_lower = [k.lower() for k in keywords]
        for s in all_snippets:
            text = f"{s.source_title} {s.raw_quote} {s.pain_point_summary}".lower()
            match_score = sum(1 for kw in kw_lower if kw in text)
            if match_score > 0:
                matched.append((match_score, s))

        matched.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in matched]
