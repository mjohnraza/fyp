import pytest
from src.agentic_os.schemas.corpus import OutcomeCategory
from src.agentic_os.retrieval.retriever import MarketEvidenceRetriever
from src.agentic_os.extraction.obstacle_chain import BuyerObstacleChainExtractor
from src.agentic_os.schemas.profile import CapabilityIntersection
from src.agentic_os.agents.offer_diagnosis import OfferDiagnosisAgent
from src.agentic_os.agents.product_suite import ProductSuiteGenerationAgent
from src.agentic_os.schemas.offer import ProductTierType


def test_offer_diagnosis_value_equation():
    retriever = MarketEvidenceRetriever()
    extractor = BuyerObstacleChainExtractor()
    offer_agent = OfferDiagnosisAgent()

    category = OutcomeCategory.WORKFLOW_AUTOMATION
    snippets = retriever.retrieve_for_category(category)
    chain = extractor.extract_chain(category, snippets)

    intersection = CapabilityIntersection(
        intersection_id="INT-TEST",
        cluster_names=["Engineering", "Automation"],
        combined_capabilities=["Python", "n8n"],
        uniqueness_score=0.85,
        leverage_description="Workflow orchestration",
        defensibility_hypothesis="Code resilience"
    )

    diagnosis = offer_agent.diagnose_offer(category.value, chain, intersection)

    assert diagnosis.dream_outcome > 0
    assert diagnosis.perceived_likelihood > 0
    assert diagnosis.time_delay > 0
    assert diagnosis.effort_sacrifice > 0
    assert diagnosis.computed_score > 0
    assert diagnosis.bottleneck_dimension in ["Time Delay", "Effort & Sacrifice", "Perceived Likelihood", "Dream Outcome"]
    assert len(diagnosis.remediation_recommendation) > 10


def test_product_suite_generation():
    retriever = MarketEvidenceRetriever()
    extractor = BuyerObstacleChainExtractor()
    product_agent = ProductSuiteGenerationAgent()

    category = OutcomeCategory.WORKFLOW_AUTOMATION
    snippets = retriever.retrieve_for_category(category)
    chain = extractor.extract_chain(category, snippets)
    intersection = CapabilityIntersection(
        intersection_id="INT-TEST",
        cluster_names=["Engineering", "Automation"],
        combined_capabilities=["Python", "n8n"],
        uniqueness_score=0.85,
        leverage_description="Workflow orchestration",
        defensibility_hypothesis="Code resilience"
    )

    suite = product_agent.generate_suite(category.value, chain, intersection)

    assert suite.lead_magnet.tier == ProductTierType.LEAD_MAGNET
    assert suite.lead_magnet.price_point_usd == 0.0
    assert suite.core_offer.tier == ProductTierType.CORE_OFFER
    assert suite.core_offer.price_point_usd > 500.0
    assert suite.backend_asset.tier == ProductTierType.COMPOUNDING_BACKEND
    assert suite.backend_asset.is_recurring is True
    assert suite.total_lifetime_value_estimate_usd > suite.core_offer.price_point_usd
