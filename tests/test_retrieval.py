import pytest
from src.agentic_os.corpus.loader import CorpusLoader
from src.agentic_os.schemas.corpus import OutcomeCategory, SourceType
from src.agentic_os.retrieval.retriever import MarketEvidenceRetriever
from src.agentic_os.retrieval.triangulation import EvidenceTriangulator


def test_corpus_loader():
    loader = CorpusLoader()
    assert loader.count() >= 10
    categories = loader.available_categories()
    assert OutcomeCategory.WORKFLOW_AUTOMATION in categories
    assert OutcomeCategory.DATA_ETL_ANALYTICS in categories


def test_retriever_and_triangulation():
    loader = CorpusLoader()
    retriever = MarketEvidenceRetriever(loader)
    triangulator = EvidenceTriangulator()

    for cat in [OutcomeCategory.WORKFLOW_AUTOMATION, OutcomeCategory.DATA_ETL_ANALYTICS, OutcomeCategory.COMPLIANCE_SECURITY]:
        snippets = retriever.retrieve_for_category(cat)
        assert len(snippets) >= 2

        triangulated = triangulator.triangulate(cat, snippets)
        assert triangulated.source_diversity_count >= 2
        assert triangulated.triangulation_passed is True
        assert triangulated.triangulation_ratio >= 0.50
