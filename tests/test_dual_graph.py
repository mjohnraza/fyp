import pytest
from src.agentic_os.schemas.corpus import OutcomeCategory
from src.agentic_os.ingestion.profiler import ProfilerAgent
from src.agentic_os.ingestion.contradiction import DecompositionPipeline
from src.agentic_os.retrieval.retriever import MarketEvidenceRetriever
from src.agentic_os.extraction.obstacle_chain import BuyerObstacleChainExtractor
from src.agentic_os.graph.dual_graph import DualGraphTranslationLayer
from src.agentic_os.graph.reframing import OwnershipMindsetReframer


def test_dual_graph_construction():
    profiler = ProfilerAgent()
    decomp_pipe = DecompositionPipeline()
    retriever = MarketEvidenceRetriever()
    extractor = BuyerObstacleChainExtractor()
    dual_graph = DualGraphTranslationLayer()

    profile = profiler.parse_profile(
        founder_name="Usman",
        bio="Senior automation engineer",
        skills_text="python, fastapi, n8n, docker"
    )
    decomp = decomp_pipe.process(profile)

    category = OutcomeCategory.WORKFLOW_AUTOMATION
    snippets = retriever.retrieve_for_category(category)
    chain = extractor.extract_chain(category, snippets)

    graph_data = dual_graph.construct_dual_graph(
        clusters=decomp.clusters,
        intersections=decomp.intersections,
        obstacle_chain=chain
    )

    assert len(graph_data.capability_nodes) > 0
    assert len(graph_data.buyer_nodes) > 0
    assert len(graph_data.edges) > 0
    assert len(graph_data.relief_statements) == len(chain.ordered_obstacles)

    # Validate ownership mindset reframing
    statement = graph_data.relief_statements[0]
    assert statement.multiplicative_leverage_ratio > 1.0
    assert "hourly" not in statement.asset_reframing.lower()
