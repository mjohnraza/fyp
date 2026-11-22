import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from src.agentic_os.schemas.profile import FounderProfile, DecompositionOutput
from src.agentic_os.schemas.corpus import OutcomeCategory, TriangulatedEvidence
from src.agentic_os.schemas.obstacle import ObstacleChain
from src.agentic_os.schemas.graph import DualGraphData
from src.agentic_os.schemas.offer import ValueEquationDiagnosis, ProductSuite
from src.agentic_os.schemas.orchestration import (
    ConfidenceReport,
    HumanCheckpointCopy,
    FounderDecisionMemo,
)
from src.agentic_os.ingestion.profiler import ProfilerAgent
from src.agentic_os.ingestion.contradiction import DecompositionPipeline
from src.agentic_os.retrieval.retriever import MarketEvidenceRetriever
from src.agentic_os.retrieval.triangulation import EvidenceTriangulator
from src.agentic_os.extraction.obstacle_chain import BuyerObstacleChainExtractor
from src.agentic_os.graph.dual_graph import DualGraphTranslationLayer
from src.agentic_os.agents.offer_diagnosis import OfferDiagnosisAgent
from src.agentic_os.agents.product_suite import ProductSuiteGenerationAgent
from src.agentic_os.agents.scorecard import OpportunityScoringAgent, OpportunityScorecard
from src.agentic_os.orchestrator.confidence import ConfidenceEvaluator
from src.agentic_os.orchestrator.checkpoints import HumanCheckpointManager


class MasterOrchestrator:
    """Master Orchestration Layer for Agentic Entrepreneur OS.
    Executes the multi-agent pipeline with confidence-based routing,
    loop-backs, and human checkpoints.
    """

    def __init__(self):
        self.profiler = ProfilerAgent()
        self.decomposition = DecompositionPipeline()
        self.retriever = MarketEvidenceRetriever()
        self.triangulator = EvidenceTriangulator()
        self.obstacle_extractor = BuyerObstacleChainExtractor()
        self.dual_graph = DualGraphTranslationLayer()
        self.offer_agent = OfferDiagnosisAgent()
        self.product_agent = ProductSuiteGenerationAgent()
        self.scoring_agent = OpportunityScoringAgent()
        self.confidence_evaluator = ConfidenceEvaluator()
        self.checkpoint_manager = HumanCheckpointManager()

    def run_pipeline(
        self,
        founder_name: str,
        bio: str,
        skills_text: str,
        category: OutcomeCategory = OutcomeCategory.WORKFLOW_AUTOMATION,
        available_hours: float = 15.0,
        budget_usd: float = 500.0,
        time_horizon_months: int = 6,
        confirm_checkpoint: bool = False
    ) -> Dict[str, Any]:
        """Runs the complete FYP-I Stage 1-4 pipeline."""
        run_log = []

        # Step 1: Profile Ingestion
        run_log.append("Executing Agent 1a: Profile Ingestion & Parsing")
        profile = self.profiler.parse_profile(
            founder_name=founder_name,
            bio=bio,
            skills_text=skills_text,
            available_hours=available_hours,
            budget_usd=budget_usd,
            time_horizon_months=time_horizon_months
        )

        # Step 2: Capability Decomposition (Clusters, Intersections, Contradictions)
        run_log.append("Executing Agents 1b, 2, 1d: Capability Decomposition & Contradiction Checking")
        decomp: DecompositionOutput = self.decomposition.process(profile)

        # Step 3: Evidence Retrieval (RAG) & Triangulation
        run_log.append(f"Executing Agent 3: Market Evidence Retrieval for {category.value}")
        raw_evidence = self.retriever.retrieve_for_category(category)
        triangulated: TriangulatedEvidence = self.triangulator.triangulate(category, raw_evidence)

        # Step 4: Obstacle-Chain Extraction
        run_log.append("Executing Agent 4: Buyer Obstacle-Chain Extraction")
        obstacles: ObstacleChain = self.obstacle_extractor.extract_chain(category, raw_evidence)

        # Confidence Signal & Routing Gate
        confidence_report: ConfidenceReport = self.confidence_evaluator.evaluate(
            decomp, triangulated, obstacles
        )

        loop_count = 0
        if confidence_report.requires_loop_back:
            run_log.append(f"TRIGGERING LOOP-BACK: {confidence_report.rationale}")
            loop_count += 1
            # Auto-remediation: enrich evidence or adjust profile assumptions
            raw_evidence = self.retriever.retrieve_for_category(category, min_snippets=4)
            triangulated = self.triangulator.triangulate(category, raw_evidence)
            obstacles = self.obstacle_extractor.extract_chain(category, raw_evidence)
            confidence_report = self.confidence_evaluator.evaluate(decomp, triangulated, obstacles)
            run_log.append(f"Post Loop-Back Confidence Composite: {confidence_report.composite_confidence}")

        # Step 5: Dual-Graph Translation & Labour-to-Asset Reframing
        run_log.append("Executing Agent 5: Dual-Graph Translation & Ownership Mindset Reframing")
        graph_data: DualGraphData = self.dual_graph.construct_dual_graph(
            clusters=decomp.clusters,
            intersections=decomp.intersections,
            obstacle_chain=obstacles
        )

        # Step 6: Offer Diagnosis (Alex Hormozi's Value Equation)
        run_log.append("Executing Agent 8: Value Equation Offer Diagnosis")
        primary_int = decomp.intersections[0] if decomp.intersections else None
        value_diagnosis: ValueEquationDiagnosis = self.offer_agent.diagnose_offer(
            category=category.value,
            obstacle_chain=obstacles,
            intersection=primary_int
        )

        # Step 7: Product-Suite Generation
        run_log.append("Executing Agent 9: 3-Tier Funnel & Product Suite Generation")
        product_suite: ProductSuite = self.product_agent.generate_suite(
            category=category.value,
            obstacle_chain=obstacles,
            intersection=primary_int
        )

        # Step 8: Opportunity Scoring Preview
        run_log.append("Executing Agent 7: Ten-Dimension Opportunity Scorecard")
        scorecard: OpportunityScorecard = self.scoring_agent.score_opportunity(
            name=f"{category.value.title()} Asset Engine",
            profile=profile,
            intersection=primary_int,
            triangulated_evidence=triangulated,
            obstacle_chain=obstacles,
            product_suite=product_suite
        )

        # Step 9: Human Checkpoint Gate
        run_log.append("Evaluating Human Checkpoint Gating")
        checkpoint = self.checkpoint_manager.generate_checkpoint(
            founder_name=founder_name,
            product_suite=product_suite,
            obstacle_chain=obstacles,
            budget_usd=budget_usd
        )
        checkpoint.user_confirmed = confirm_checkpoint

        # Step 10: Founder Decision Memo Generation
        memo = FounderDecisionMemo(
            memo_id=f"MEMO-{uuid.uuid4().hex[:8].upper()}",
            date=datetime.now().strftime("%Y-%m-%d"),
            founder_name=founder_name,
            primary_opportunity_title=scorecard.opportunity_name,
            target_persona=product_suite.target_niche,
            core_capability_leverage=primary_int.leverage_description if primary_int else "Technical Integration",
            buyer_obstacle_relieved=obstacles.ordered_obstacles[0].description,
            evidence_backing=[s.pain_point_summary for s in raw_evidence[:2]],
            reframe_from_labor_to_asset=graph_data.relief_statements[0].asset_reframing if graph_data.relief_statements else "Automated system",
            value_equation_score=value_diagnosis.computed_score,
            product_suite_summary={
                "lead_magnet": product_suite.lead_magnet.model_dump(),
                "core_offer": product_suite.core_offer.model_dump(),
                "backend_asset": product_suite.backend_asset.model_dump(),
                "total_ltv": product_suite.total_lifetime_value_estimate_usd
            },
            first_validation_experiment=(
                f"Deploy '{product_suite.lead_magnet.title}' as a free open-source GitHub tool or "
                f"share on r/automation / Hacker News. Measure click-through and email capture with $0-$50 budget."
            ),
            regret_minimization_framing=checkpoint.potential_regret_statement,
            confidence_signals={
                "grounding": confidence_report.grounding_confidence,
                "consistency": confidence_report.consistency_confidence,
                "composite": confidence_report.composite_confidence
            },
            human_checkpoint=checkpoint
        )

        return {
            "status": "COMPLETED" if confirm_checkpoint else "AWAITING_HUMAN_CHECKPOINT",
            "run_log": run_log,
            "profile": profile,
            "decomposition": decomp,
            "evidence": triangulated,
            "obstacles": obstacles,
            "graph_data": graph_data,
            "value_diagnosis": value_diagnosis,
            "product_suite": product_suite,
            "scorecard": scorecard,
            "confidence_report": confidence_report,
            "human_checkpoint": checkpoint,
            "founder_decision_memo": memo
        }
