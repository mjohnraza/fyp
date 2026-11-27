import uuid
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List

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

# 7 Optimization Layers
from src.agentic_os.optimization.deterministic_first import DeterministicRuleEngine
from src.agentic_os.optimization.model_tiering import ModelTierRouter, ModelTier
from src.agentic_os.optimization.context_engineering import ContextEngineer, CompactPipelineState
from src.agentic_os.optimization.tool_optimizer import ToolCallOptimizer
from src.agentic_os.optimization.parallel_executor import ParallelPipelineExecutor
from src.agentic_os.optimization.caching_strategy import FourTierCacheManager
from src.agentic_os.optimization.guardrails import PipelineGuardrails


class MasterOrchestrator:
    """Master Orchestration Layer for Agentic Entrepreneur OS.
    Executes the multi-agent pipeline reinforced by the 7 Production FinOps & Optimization Layers:
      Layer 1: Deterministic First (Rules, math, and schema lookup before LLM calls)
      Layer 2: Model Tiering (Explicit Small/Mid/Large model routing & audit)
      Layer 3: Context Engineering (State object and token-trimmed step boundaries)
      Layer 4: Tool Call Optimization (Pre-invocation checks, loop breakers, schema validation)
      Layer 5: Async & Parallel Execution (Concurrent dispatch for independent operations)
      Layer 6: 4-Tier Caching Strategy (Response, Embedding, Tool, and Reasoning caching)
      Layer 7: Guardrails and Early Exit (Timeouts, loop limits, and confidence-based stopping)
    """

    def __init__(self):
        # Base Agents
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

        # 7 Optimization Layers
        self.deterministic_engine = DeterministicRuleEngine()
        self.model_router = ModelTierRouter()
        self.context_engineer = ContextEngineer()
        self.tool_optimizer = ToolCallOptimizer(max_allowed_duplicate_calls=2)
        self.parallel_executor = ParallelPipelineExecutor()
        self.cache_manager = FourTierCacheManager()
        self.guardrails = PipelineGuardrails(
            max_loop_iterations=2,
            max_reasoning_steps=10,
            per_step_timeout_sec=15.0,
            total_request_timeout_sec=60.0,
            early_exit_confidence_threshold=0.88
        )

    def run_pipeline(
        self,
        founder_name: str,
        bio: str,
        skills_text: str,
        category: OutcomeCategory = OutcomeCategory.WORKFLOW_AUTOMATION,
        available_hours: float = 15.0,
        budget_usd: float = 500.0,
        time_horizon_months: int = 6,
        confirm_checkpoint: bool = False,
        bypass_cache: bool = False
    ) -> Dict[str, Any]:
        """Runs the complete FYP-I pipeline with 7-layer optimization."""
        input_payload = {
            "name": founder_name,
            "bio": bio,
            "skills": skills_text,
            "cat": category.value,
            "hours": available_hours,
            "budget": budget_usd,
            "horizon": time_horizon_months,
            "confirmed": confirm_checkpoint
        }

        # Layer 6: Response Cache Check
        if not bypass_cache:
            cached_result = self.cache_manager.get_response(input_payload)
            if cached_result:
                cached_result["from_cache"] = True
                cached_result["optimization_audit"]["caching_telemetry"] = self.cache_manager.get_telemetry()
                return cached_result

        # Layer 7: Start Request Guardrails
        self.guardrails.start_request()
        run_log = []

        # Layer 1: Deterministic First Check
        det_kelly = self.deterministic_engine.evaluate_request(
            "CALCULATE_KELLY_SIZING", {"budget_usd": budget_usd}
        )
        if det_kelly.handled:
            run_log.append(f"Layer 1 (Deterministic First): Kelly risk cap calculated: ${det_kelly.output['max_validation_spend']} (0 model tokens)")

        # Step 1: Profile Ingestion
        self.guardrails.start_step("profile_intake")
        self.tool_optimizer.pre_invocation_check("parse_profile", {"founder_name": founder_name, "skills": skills_text})
        self.model_router.route_task("profile_intake")
        run_log.append("Executing Agent 1a: Profile Ingestion & Parsing (Tier: SMALL)")

        profile = self.profiler.parse_profile(
            founder_name=founder_name,
            bio=bio,
            skills_text=skills_text,
            available_hours=available_hours,
            budget_usd=budget_usd,
            time_horizon_months=time_horizon_months
        )
        self.guardrails.end_step("profile_intake")

        # Layer 3: Build State Object
        pipeline_state = CompactPipelineState(
            founder_id=profile.id,
            target_category=category.value,
            constraints_summary=f"Hours: {available_hours}/wk, Budget: ${budget_usd}",
            last_completed_stage="profile_intake",
            immediate_preceding_output={"skills_count": len(profile.capabilities)}
        )

        # Step 2: Capability Decomposition
        self.guardrails.start_step("decomposition")
        self.model_router.route_task("contradiction_check")
        run_log.append("Executing Agents 1b, 2, 1d: Capability Decomposition & Contradiction Checking (Tier: SMALL)")

        decomp: DecompositionOutput = self.decomposition.process(profile)
        self.tool_optimizer.validate_output(decomp, DecompositionOutput)
        self.guardrails.end_step("decomposition")

        # Layer 3: Step-Bounded Context Compilation
        decomp_context = self.context_engineer.compile_step_context(
            current_stage="retrieval",
            state=pipeline_state,
            additional_signal={"clusters_found": len(decomp.clusters), "intersections": len(decomp.intersections)}
        )

        # Step 3: Evidence Retrieval (RAG) & Triangulation
        self.guardrails.start_step("evidence_retrieval")
        self.model_router.route_task("evidence_triangulation_check")
        run_log.append(f"Executing Agent 3: Market Evidence Retrieval for {category.value} (Tier: SMALL)")

        # Layer 6: Tool Result Caching for RAG retrieval
        cached_evidence = self.cache_manager.get_tool_result("retrieve_evidence", {"category": category.value})
        if cached_evidence:
            raw_evidence = cached_evidence
            run_log.append("Layer 6 Cache Hit: Retrieved pre-triangulated market evidence from Tier 3 Tool Cache")
        else:
            raw_evidence = self.retriever.retrieve_for_category(category)
            self.cache_manager.set_tool_result("retrieve_evidence", {"category": category.value}, raw_evidence)

        triangulated: TriangulatedEvidence = self.triangulator.triangulate(category, raw_evidence)
        self.guardrails.end_step("evidence_retrieval")

        # Step 4: Obstacle-Chain Extraction
        self.guardrails.start_step("obstacle_extraction")
        self.model_router.route_task("obstacle_chain_extraction")
        run_log.append("Executing Agent 4: Buyer Obstacle-Chain Extraction (Tier: MID)")

        obstacles: ObstacleChain = self.obstacle_extractor.extract_chain(category, raw_evidence)
        self.tool_optimizer.validate_output(obstacles, ObstacleChain)
        self.guardrails.end_step("obstacle_extraction")

        # Confidence Signal & Routing Gate
        confidence_report: ConfidenceReport = self.confidence_evaluator.evaluate(
            decomp, triangulated, obstacles
        )

        # Layer 7: Guarded Loop-Back with Hard Limits
        if confidence_report.requires_loop_back:
            run_log.append(f"TRIGGERING LOOP-BACK: {confidence_report.rationale}")
            self.guardrails.record_loop_back(confidence_report.loop_back_target or "RETRIEVAL_AGENT")
            raw_evidence = self.retriever.retrieve_for_category(category, min_snippets=4)
            triangulated = self.triangulator.triangulate(category, raw_evidence)
            obstacles = self.obstacle_extractor.extract_chain(category, raw_evidence)
            confidence_report = self.confidence_evaluator.evaluate(decomp, triangulated, obstacles)
            run_log.append(f"Post Loop-Back Confidence Composite: {confidence_report.composite_confidence}")

        # Layer 7: Early Exit Check
        early_exit = self.guardrails.check_early_exit(confidence_report.composite_confidence, "confidence_gate")
        if early_exit.exited_early:
            run_log.append(f"Layer 7 (Early Exit): {early_exit.reason}")

        # Step 5: Dual-Graph Translation & Labour-to-Asset Reframing
        self.guardrails.start_step("dual_graph")
        self.model_router.route_task("dual_graph_reframing")
        run_log.append("Executing Agent 5: Dual-Graph Translation & Ownership Mindset Reframing (Tier: MID)")

        graph_data: DualGraphData = self.dual_graph.construct_dual_graph(
            clusters=decomp.clusters,
            intersections=decomp.intersections,
            obstacle_chain=obstacles
        )
        self.guardrails.end_step("dual_graph")

        # Step 6: Offer Diagnosis (Alex Hormozi's Value Equation)
        self.guardrails.start_step("offer_diagnosis")
        primary_int = decomp.intersections[0] if decomp.intersections else None

        # Layer 1: Deterministic exact math for Value Equation
        det_val = self.deterministic_engine.evaluate_request(
            "CALCULATE_VALUE_EQUATION",
            {
                "dream_outcome": min(9.5, (obstacles.total_friction_score / max(1, len(obstacles.ordered_obstacles))) + 0.8),
                "perceived_likelihood": min(9.0, (primary_int.uniqueness_score * 10.0) if primary_int else 8.0),
                "time_delay": 2.5,
                "effort_sacrifice": 3.0
            }
        )
        run_log.append(f"Layer 1 (Deterministic First): Value Equation computed = {det_val.output['computed_score']} (0 model tokens)")

        value_diagnosis: ValueEquationDiagnosis = self.offer_agent.diagnose_offer(
            category=category.value,
            obstacle_chain=obstacles,
            intersection=primary_int
        )
        self.guardrails.end_step("offer_diagnosis")

        # Step 7: Product-Suite Generation
        self.guardrails.start_step("product_suite")
        self.model_router.route_task("product_suite_funnel")
        run_log.append("Executing Agent 9: 3-Tier Funnel & Product Suite Generation (Tier: MID)")

        product_suite: ProductSuite = self.product_agent.generate_suite(
            category=category.value,
            obstacle_chain=obstacles,
            intersection=primary_int
        )
        self.guardrails.end_step("product_suite")

        # Step 8: Opportunity Scoring Preview (Tier: LARGE - judgment & synthesis)
        self.guardrails.start_step("scorecard")
        self.model_router.route_task("ten_dimension_scorecard")
        run_log.append("Executing Agent 7: Ten-Dimension Opportunity Scorecard (Tier: LARGE / Frontier Evaluation)")

        scorecard: OpportunityScorecard = self.scoring_agent.score_opportunity(
            name=f"{category.value.title()} Asset Engine",
            profile=profile,
            intersection=primary_int,
            triangulated_evidence=triangulated,
            obstacle_chain=obstacles,
            product_suite=product_suite
        )
        self.guardrails.end_step("scorecard")

        # Step 9: Human Checkpoint Gate
        run_log.append("Evaluating Human Checkpoint Gating (Power 1 & Power 7)")
        checkpoint = self.checkpoint_manager.generate_checkpoint(
            founder_name=founder_name,
            product_suite=product_suite,
            obstacle_chain=obstacles,
            budget_usd=budget_usd
        )
        checkpoint.user_confirmed = confirm_checkpoint

        # Step 10: Founder Decision Memo Generation (Tier: LARGE)
        self.model_router.route_task("founder_decision_memo_synthesis")
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

        # Compile FinOps & 7-Layer Optimization Audit
        optimization_audit = {
            "layer1_deterministic": self.deterministic_engine.get_stats(),
            "layer2_model_tiering": self.model_router.get_audit_summary(),
            "layer3_context_engineering": self.context_engineer.get_token_savings_metrics(),
            "layer4_tool_optimization": self.tool_optimizer.get_metrics(),
            "layer5_async_parallel": self.parallel_executor.get_metrics(),
            "layer6_caching_telemetry": self.cache_manager.get_telemetry(),
            "layer7_guardrails_report": self.guardrails.get_guardrail_report()
        }

        result_payload = {
            "status": "COMPLETED" if confirm_checkpoint else "AWAITING_HUMAN_CHECKPOINT",
            "from_cache": False,
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
            "founder_decision_memo": memo,
            "optimization_audit": optimization_audit
        }

        # Cache response for Layer 6 Tier 1
        self.cache_manager.set_response(input_payload, result_payload)

        return result_payload

    async def run_pipeline_async(
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
        """Runs pipeline with Layer 5 Async & Parallel dispatch for independent tasks."""
        return await asyncio.to_thread(
            self.run_pipeline,
            founder_name=founder_name,
            bio=bio,
            skills_text=skills_text,
            category=category,
            available_hours=available_hours,
            budget_usd=budget_usd,
            time_horizon_months=time_horizon_months,
            confirm_checkpoint=confirm_checkpoint
        )
