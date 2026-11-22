import pytest
from src.agentic_os.schemas.corpus import OutcomeCategory
from src.agentic_os.retrieval.retriever import MarketEvidenceRetriever
from src.agentic_os.extraction.obstacle_chain import BuyerObstacleChainExtractor
from src.agentic_os.schemas.obstacle import ObstaclePhase


def test_obstacle_chain_extraction():
    retriever = MarketEvidenceRetriever()
    extractor = BuyerObstacleChainExtractor()

    category = OutcomeCategory.WORKFLOW_AUTOMATION
    snippets = retriever.retrieve_for_category(category)
    chain = extractor.extract_chain(category, snippets)

    assert chain.target_category == category.value
    assert len(chain.ordered_obstacles) == 3
    assert chain.ordered_obstacles[0].phase == ObstaclePhase.BEFORE_ATTEMPT
    assert chain.ordered_obstacles[1].phase == ObstaclePhase.DURING_EXECUTION
    assert chain.ordered_obstacles[2].phase == ObstaclePhase.AFTER_COMPLETION
    assert chain.coverage_ratio >= 0.65
    assert chain.total_friction_score > 0
