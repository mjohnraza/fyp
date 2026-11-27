from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ModelTier(str, Enum):
    SMALL = "SMALL"      # e.g., Ollama / vLLM + Qwen 1.5B/7B (~70% of calls, $0.00)
    MID = "MID"          # e.g., Gemini 1.5 Flash / Qwen 14B (~25% of calls, $0.001-$0.01)
    LARGE = "LARGE"      # e.g., Gemini Pro / Claude 3.5 Sonnet / GPT-4o (~5% of calls, $0.03-$0.10)


class TierRoutingDecision(BaseModel):
    task_name: str
    assigned_tier: ModelTier
    model_name: str
    estimated_cost_usd: float
    expected_latency_sec: float
    routing_rationale: str


class ModelTierRouter:
    """Layer 2: Model Tiering.
    Avoids routing everything through a flagship model when a lighter one suffices.
    Explicitly logs and audits model tiering per task (Table V in FYP proposal).
    """

    TIER_CONFIG = {
        ModelTier.SMALL: {
            "model_identifier": "ollama/qwen2.5:1.5b",
            "cost_per_call": 0.000,
            "typical_latency_sec": 0.25,
            "capabilities": ["classification", "intent_detection", "simple_extraction", "schema_validation"]
        },
        ModelTier.MID: {
            "model_identifier": "gemini-flash-1.5",
            "cost_per_call": 0.002,
            "typical_latency_sec": 0.85,
            "capabilities": ["summarization", "structured_generation", "rag_synthesis", "obstacle_extraction"]
        },
        ModelTier.LARGE: {
            "model_identifier": "gemini-pro-1.5 / frontier",
            "cost_per_call": 0.025,
            "typical_latency_sec": 2.20,
            "capabilities": ["multi_step_reasoning", "cross_source_synthesis", "10_dimension_scoring", "executive_memo"]
        }
    }

    # Explicit routing matrix
    TASK_ROUTING_MAP = {
        "profile_intake": ModelTier.SMALL,
        "contradiction_check": ModelTier.SMALL,
        "evidence_triangulation_check": ModelTier.SMALL,
        "obstacle_chain_extraction": ModelTier.MID,
        "dual_graph_reframing": ModelTier.MID,
        "product_suite_funnel": ModelTier.MID,
        "ten_dimension_scorecard": ModelTier.LARGE,
        "founder_decision_memo_synthesis": ModelTier.LARGE,
    }

    def __init__(self):
        self.routing_history: List[TierRoutingDecision] = []

    def route_task(self, task_name: str, complexity_override: Optional[ModelTier] = None) -> TierRoutingDecision:
        tier = complexity_override or self.TASK_ROUTING_MAP.get(task_name, ModelTier.MID)
        cfg = self.TIER_CONFIG[tier]

        decision = TierRoutingDecision(
            task_name=task_name,
            assigned_tier=tier,
            model_name=cfg["model_identifier"],
            estimated_cost_usd=cfg["cost_per_call"],
            expected_latency_sec=cfg["typical_latency_sec"],
            routing_rationale=f"Task '{task_name}' matched to {tier.value} tier for optimal cost/capability balance."
        )
        self.routing_history.append(decision)
        return decision

    def get_audit_summary(self) -> Dict[str, Any]:
        total_calls = len(self.routing_history)
        if total_calls == 0:
            return {"total_calls": 0, "total_cost_usd": 0.0, "tier_distribution": {}}

        small_count = sum(1 for d in self.routing_history if d.assigned_tier == ModelTier.SMALL)
        mid_count = sum(1 for d in self.routing_history if d.assigned_tier == ModelTier.MID)
        large_count = sum(1 for d in self.routing_history if d.assigned_tier == ModelTier.LARGE)
        total_cost = sum(d.estimated_cost_usd for d in self.routing_history)

        # Baseline cost if all calls were routed to flagship Large model
        flagship_cost = total_calls * self.TIER_CONFIG[ModelTier.LARGE]["cost_per_call"]
        savings_usd = max(0.0, flagship_cost - total_cost)

        return {
            "total_calls": total_calls,
            "total_cost_usd": round(total_cost, 4),
            "tier_distribution": {
                "small_pct": round(small_count / total_calls * 100, 1),
                "mid_pct": round(mid_count / total_calls * 100, 1),
                "large_pct": round(large_count / total_calls * 100, 1)
            },
            "estimated_savings_vs_flagship_usd": round(savings_usd, 4),
            "savings_percentage": round((savings_usd / flagship_cost * 100) if flagship_cost > 0 else 0, 1)
        }
