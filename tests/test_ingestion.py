import pytest
from src.agentic_os.ingestion.profiler import ProfilerAgent
from src.agentic_os.ingestion.clusterer import ClustererAgent
from src.agentic_os.ingestion.intersection import IntersectionMinerAgent
from src.agentic_os.ingestion.contradiction import ContradictionCheckerAgent, DecompositionPipeline


def test_profiler_parsing():
    profiler = ProfilerAgent()
    profile = profiler.parse_profile(
        founder_name="Taha",
        bio="Experienced software engineer with deep interest in automation and AI agents.",
        skills_text="python, fastapi, docker, postgresql, n8n, rag",
        available_hours=20.0,
        budget_usd=1000.0
    )
    assert profile.founder_name == "Taha"
    assert len(profile.capabilities) >= 5
    assert profile.context.available_hours_per_week == 20.0
    assert profile.constraints.financial_budget_usd == 1000.0


def test_clusterer_and_intersection():
    profiler = ProfilerAgent()
    clusterer = ClustererAgent()
    miner = IntersectionMinerAgent()

    profile = profiler.parse_profile(
        founder_name="Fatima",
        bio="Data scientist specializing in pipelines and machine learning.",
        skills_text="python, sql, etl, rag, llm"
    )

    clusters = clusterer.cluster_capabilities(profile)
    assert len(clusters) >= 2

    intersections = miner.mine_intersections(clusters)
    assert len(intersections) >= 1
    assert intersections[0].uniqueness_score >= 0.70


def test_contradiction_checker():
    profiler = ProfilerAgent()
    checker = ContradictionCheckerAgent()

    # Extreme constraints to trigger flags
    profile = profiler.parse_profile(
        founder_name="Ali",
        bio="Student",
        skills_text="python",
        available_hours=4.0,   # High contradiction: < 8 hrs
        budget_usd=20.0,       # High contradiction: < $100
        time_horizon_months=1  # High contradiction: < 3 months
    )

    flags = checker.check_contradictions(profile)
    assert len(flags) == 3
    assert any(f.dimension == "Time Commitment" for f in flags)
    assert any(f.dimension == "Financial Runway" for f in flags)
    assert any(f.dimension == "Time Horizon" for f in flags)


def test_full_decomposition_pipeline():
    pipeline = DecompositionPipeline()
    profiler = ProfilerAgent()
    profile = profiler.parse_profile(
        founder_name="Zubair",
        bio="Full stack dev with compliance background",
        skills_text="python, fastapi, soc2, docker",
        available_hours=15.0,
        budget_usd=500.0
    )
    output = pipeline.process(profile)
    assert output.profile_id == profile.id
    assert len(output.clusters) >= 1
    assert output.confidence_score >= 0.70
