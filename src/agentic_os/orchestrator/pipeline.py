import uuid
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

from src.agentic_os.optimization.deterministic_first import DeterministicRuleEngine
from src.agentic_os.optimization.model_tiering import ModelTierRouter
from src.agentic_os.optimization.context_engineering import ContextEngineer, CompactPipelineState
from src.agentic_os.optimization.tool_optimizer import ToolCallOptimizer
from src.agentic_os.optimization.parallel_executor import ParallelPipelineExecutor
from src.agentic_os.optimization.caching_strategy import FourTierCacheManager
from src.agentic_os.optimization.guardrails import PipelineGuardrails


class MasterOrchestrator:
    """Master Orchestration Layer for Agentic Entrepreneur OS.
    Executes the multi-agent pipeline with:
      - Target-aware confidence loop-back routing (PROFILER_AGENT vs RETRIEVAL_AGENT)
      - Mandatory human-in-the-loop checkpoint gating before memo commitment
      - Genuine early-exit short-circuiting when requested and confidence is high
      - 7 Production FinOps & Optimization Layers
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

        self.deterministic_engine = DeterministicRuleEngine()
        self.model_router = ModelTierRouter()
        self.context_engineer = ContextEngineer()
        self.tool_optimizer = ToolCallOptimizer(max_allowed_duplicate_calls=5)
        self.parallel_executor = ParallelPipelineExecutor()
        self.cache_manager = FourTierCacheManager()
        self.guardrails = PipelineGuardrails(
            max_loop_iterations=2,
            max_reasoning_steps=12,
            per_step_timeout_sec=15.0,
            total_request_timeout_sec=60.0,
            early_exit_confidence_threshold=0.88
        )

    def _run_profiler_recovery(
        self,
        founder_name: str,
        bio: str,
        skills_text: str,
        available_hours: float,
        budget_usd: float,
        time_horizon_months: int,
        run_log: List[str]
    ) -> tuple[FounderProfile, DecompositionOutput]:
        """QA-001: Dedicated PROFILER_AGENT recovery path when consistency confidence is low."""
        run_log.append("Executing PROFILER_AGENT recovery: adjusting constraints & re-parsing profile")
        adjusted_hours = max(available_hours, 8.0) if available_hours < 8.0 else available_hours
        adjusted_horizon = max(time_horizon_months, 3) if time_horizon_months < 3 else time_horizon_months
        adjusted_budget = max(budget_usd, 100.0) if budget_usd < 100.0 else budget_usd

        refined_profile = self.profiler.parse_profile(
            founder_name=founder_name,
            bio=bio,
            skills_text=skills_text,
            available_hours=adjusted_hours,
            budget_usd=adjusted_budget,
            time_horizon_months=adjusted_horizon
        )
        refined_decomp = self.decomposition.process(refined_profile)
        return refined_profile, refined_decomp

    def _build_optimization_audit(self) -> Dict[str, Any]:
        return {
            "layer1_deterministic": self.deterministic_engine.get_stats(),
            "layer2_model_tiering": self.model_router.get_audit_summary(),
            "layer3_context_engineering": self.context_engineer.get_token_savings_metrics(),
            "layer4_tool_optimization": self.tool_optimizer.get_metrics(),
            "layer5_async_parallel": self.parallel_executor.get_metrics(),
            "layer6_caching_telemetry": self.cache_manager.get_telemetry(),
            "layer7_guardrails_report": self.guardrails.get_guardrail_report(),
        }

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
        bypass_cache: bool = False,
        stop_on_early_exit: bool = False
    ) -> Dict[str, Any]:
        """Runs the complete FYP-I pipeline with QA-verified routing, gating, and short-circuiting."""
        input_payload = {
            "name": founder_name,
            "bio": bio,
            "skills": skills_text,
            "cat": category.value,
            "hours": available_hours,
            "budget": budget_usd,
            "horizon": time_horizon_months,
            "confirmed": confirm_checkpoint,
            "stop_on_early_exit": stop_on_early_exit,
        }

        if not bypass_cache:
            cached_result = self.cache_manager.get_response(input_payload)
            if cached_result:
                cached_result["from_cache"] = True
                cached_result["optimization_audit"]["layer6_caching_telemetry"] = self.cache_manager.get_telemetry()
                return cached_result

        self.guardrails.start_request()
        run_log: List[str] = []

        # Layer 1: Deterministic First Check
        det_kelly = self.deterministic_engine.evaluate_request(
            "CALCULATE_KELLY_SIZING", {"budget_usd": budget_usd}
        )
        if det_kelly.handled:
            run_log.append(
                f"Layer 1 (Deterministic First): Kelly risk cap calculated: "
                f"${det_kelly.output['max_validation_spend']} (0 model tokens)"
            )

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

        pipeline_state = CompactPipelineState(
            founder_id=profile.id,
            target_category=category.value,
            constraints_summary=f"Hours: {available_hours}/wk, Budget: ${budget_usd}",
            last_completed_stage="profile_intake",
            immediate_preceding_output={"skills_count": len(profile.capabilities)}
        )

        # Step 2: Capability Decomposition (with Layer 6 Reasoning Cache)
        self.guardrails.start_step("decomposition")
        self.model_router.route_task("contradiction_check")
        run_log.append("Executing Agents 1b, 2, 1d: Capability Decomposition & Contradiction Checking (Tier: SMALL)")

        decomp_sig = {"skills": [c.name for c in profile.capabilities], "hours": available_hours, "budget": budget_usd, "horizon": time_horizon_months}
        decomp: Optional[DecompositionOutput] = self.cache_manager.get_reasoning("decomposition", decomp_sig)
        if decomp is None:
            decomp = self.decomposition.process(profile)
            self.cache_manager.set_reasoning("decomposition", decomp_sig, decomp)
        self.tool_optimizer.validate_output(decomp, DecompositionOutput)
        self.guardrails.end_step("decomposition")

        decomp_context = self.context_engineer.compile_step_context(
            current_stage="retrieval",
            state=pipeline_state,
            additional_signal={"clusters_found": len(decomp.clusters), "intersections": len(decomp.intersections)}
        )

        # Step 3: Evidence Retrieval (RAG) & Triangulation
        self.guardrails.start_step("evidence_retrieval")
        self.model_router.route_task("evidence_triangulation_check")
        run_log.append(f"Executing Agent 3: Market Evidence Retrieval for {category.value} (Tier: SMALL)")

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

        # Confidence Signal & Target-Aware Routing Gate (QA-001)
        confidence_report: ConfidenceReport = self.confidence_evaluator.evaluate(
            decomp, triangulated, obstacles
        )

        if confidence_report.requires_loop_back:
            target = confidence_report.loop_back_target or "RETRIEVAL_AGENT"
            run_log.append(f"TRIGGERING LOOP-BACK -> {target}: {confidence_report.rationale}")
            self.guardrails.record_loop_back(target)

            if target == "PROFILER_AGENT":
                profile, decomp = self._run_profiler_recovery(
                    founder_name, bio, skills_text,
                    available_hours, budget_usd, time_horizon_months, run_log
                )
            else:
                raw_evidence = self.retriever.retrieve_for_category(category, min_snippets=4)
                triangulated = self.triangulator.triangulate(category, raw_evidence)
                obstacles = self.obstacle_extractor.extract_chain(category, raw_evidence)

            confidence_report = self.confidence_evaluator.evaluate(decomp, triangulated, obstacles)
            run_log.append(f"Post Loop-Back Confidence Composite: {confidence_report.composite_confidence}")

        # Low-confidence persistence guard: do not silently proceed as normal if recovery still failed
        if confidence_report.requires_loop_back:
            run_log.append(f"ESCALATION: Low confidence persists after recovery ({confidence_report.composite_confidence}). Halting before downstream offer/memo generation.")
            return {
                "status": "LOW_CONFIDENCE_ESCALATED",
                "from_cache": False,
                "run_log": run_log,
                "profile": profile,
                "decomposition": decomp,
                "evidence": triangulated,
                "obstacles": obstacles,
                "graph_data": None,
                "value_diagnosis": None,
                "product_suite": None,
                "scorecard": None,
                "confidence_report": confidence_report,
                "human_checkpoint": None,
                "founder_decision_memo": None,
                "optimization_audit": self._build_optimization_audit(),
            }

        # QA-003: Genuine Early Exit Short-Circuit
        early_exit = self.guardrails.check_early_exit(confidence_report.composite_confidence, "confidence_gate")
        if early_exit.exited_early and stop_on_early_exit:
            run_log.append(f"Layer 7 (Early Exit Short-Circuit): {early_exit.reason}")
            return {
                "status": "EARLY_EXIT_PARTIAL",
                "from_cache": False,
                "run_log": run_log,
                "profile": profile,
                "decomposition": decomp,
                "evidence": triangulated,
                "obstacles": obstacles,
                "graph_data": None,
                "value_diagnosis": None,
                "product_suite": None,
                "scorecard": None,
                "confidence_report": confidence_report,
                "human_checkpoint": None,
                "founder_decision_memo": None,
                "optimization_audit": self._build_optimization_audit(),
            }

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

        value_diagnosis: ValueEquationDiagnosis = self.offer_agent.diagnose_offer(
            category=category.value,
            obstacle_chain=obstacles,
            intersection=primary_int
        )
        det_val = self.deterministic_engine.evaluate_request(
            "CALCULATE_VALUE_EQUATION",
            {
                "dream_outcome": value_diagnosis.dream_outcome,
                "perceived_likelihood": value_diagnosis.perceived_likelihood,
                "time_delay": value_diagnosis.time_delay,
                "effort_sacrifice": value_diagnosis.effort_sacrifice,
            }
        )
        run_log.append(f"Layer 1 (Deterministic First): Value Equation computed = {det_val.output['computed_score']} (0 model tokens)")
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

        # Step 8: Opportunity Scoring Preview (Tier: LARGE)
        self.guardrails.start_step("scorecard")
        self.model_router.route_task("ten_dimension_scorecard")
        run_log.append("Executing Agent 7: Ten-Dimension Opportunity Scorecard (Tier: LARGE / Frontier Evaluation)")

        scorecard: OpportunityScorecard = self.scoring_agent.score_opportunity(
            name=f"{category.value.replace('_', ' ').title()} Asset Engine",
            profile=profile,
            intersection=primary_int,
            triangulated_evidence=triangulated,
            obstacle_chain=obstacles,
            product_suite=product_suite
        )
        self.guardrails.end_step("scorecard")

        # Step 9: Human Checkpoint Gate (QA-002)
        run_log.append("Evaluating Human Checkpoint Gating (Power 1 & Power 7)")
        checkpoint = self.checkpoint_manager.generate_checkpoint(
            founder_name=founder_name,
            product_suite=product_suite,
            obstacle_chain=obstacles,
            budget_usd=budget_usd
        )
        checkpoint.user_confirmed = confirm_checkpoint

        # QA-002: Gate Founder Decision Memo behind explicit human confirmation
        memo: Optional[FounderDecisionMemo] = None
        if confirm_checkpoint:
            self.model_router.route_task("founder_decision_memo_synthesis")
            memo = FounderDecisionMemo(
                memo_id=f"MEMO-{uuid.uuid4().hex[:8].upper()}",
                date=datetime.now().strftime("%Y-%m-%d"),
                founder_name=founder_name,
                primary_opportunity_title=scorecard.opportunity_name,
                target_persona=product_suite.target_niche,
                core_capability_leverage=primary_int.leverage_description if primary_int else "Single-cluster technical execution",
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
            status = "COMPLETED"
        else:
            run_log.append("CHECKPOINT GATE ACTIVE: Founder Decision Memo blocked pending explicit human approval.")
            status = "AWAITING_HUMAN_CHECKPOINT"

        result_payload = {
            "status": status,
            "from_cache": False,
            "run_log": run_log,
            "context_snapshot": decomp_context,
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
            "optimization_audit": self._build_optimization_audit()
        }

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
        """Layer 5: Dispatches independent ingestion/decomposition and evidence retrieval concurrently."""
        profile = self.profiler.parse_profile(
            founder_name=founder_name,
            bio=bio,
            skills_text=skills_text,
            available_hours=available_hours,
            budget_usd=budget_usd,
            time_horizon_months=time_horizon_months
        )

        # Run decomposition and evidence retrieval concurrently
        concurrent_results = await self.parallel_executor.execute_concurrently([
            ("decomposition", lambda: self.decomposition.process(profile)),
            ("raw_evidence", lambda: self.retriever.retrieve_for_category(category)),
        ])

        decomp = concurrent_results["decomposition"]
        raw_evidence = concurrent_results["raw_evidence"]
        self.cache_manager.set_tool_result("retrieve_evidence", {"category": category.value}, raw_evidence)

        return await asyncio.to_thread(
            self.run_pipeline,
            founder_name=founder_name,
            bio=bio,
            skills_text=skills_text,
            category=category,
            available_hours=available_hours,
            budget_usd=budget_usd,
            time_horizon_months=time_horizon_months,
            confirm_checkpoint=confirm_checkpoint,
            bypass_cache=True
        )
