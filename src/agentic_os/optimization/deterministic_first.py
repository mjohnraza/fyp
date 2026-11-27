import math
from typing import Dict, Any, Optional, Tuple, Callable
from pydantic import BaseModel, Field


class DeterministicResult(BaseModel):
    is_deterministic: bool
    handled: bool
    action_type: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    explanation: str


class DeterministicRuleEngine:
    """Layer 1: Deterministic First.
    Asks: 'Does this request have a single, known correct answer?'
    If yes, resolves via rules, lookups, and exact math instead of sending
    deterministic queries to probabilistic models.
    """

    EXACT_LOOKUPS = {
        "categories": ["WORKFLOW_AUTOMATION", "DATA_ETL_ANALYTICS", "KNOWLEDGE_ONBOARDING", "COMPLIANCE_SECURITY", "DEVELOPER_TOOLING"],
        "default_budget": 500.0,
        "default_hours": 15.0,
        "default_horizon": 6,
    }

    def __init__(self):
        self.deterministic_hits = 0
        self.model_delegations = 0

    def evaluate_request(self, request_type: str, data: Dict[str, Any]) -> DeterministicResult:
        """Determines if a task can be solved deterministically with 0 token spend."""

        # 1. Math computation: Hormozi Value Equation
        if request_type == "CALCULATE_VALUE_EQUATION":
            dream = float(data.get("dream_outcome", 8.0))
            likelihood = float(data.get("perceived_likelihood", 8.0))
            time_delay = max(0.1, float(data.get("time_delay", 2.5)))
            effort = max(0.1, float(data.get("effort_sacrifice", 3.0)))
            computed = round((dream * likelihood) / (time_delay * effort), 2)
            self.deterministic_hits += 1
            return DeterministicResult(
                is_deterministic=True,
                handled=True,
                action_type="EXACT_MATH",
                output={"computed_score": computed, "formula": "(Dream * Likelihood) / (Time * Effort)"},
                cost_usd=0.0,
                latency_ms=0.1,
                explanation="Resolved mathematically via deterministic formula without LLM call."
            )

        # 2. Math computation: Kelly Criterion capital sizing
        if request_type == "CALCULATE_KELLY_SIZING":
            budget = float(data.get("budget_usd", 500.0))
            max_risk = round(min(50.0, budget * 0.15), 2)
            self.deterministic_hits += 1
            return DeterministicResult(
                is_deterministic=True,
                handled=True,
                action_type="EXACT_MATH",
                output={"budget_usd": budget, "max_validation_spend": max_risk, "risk_percentage": "10-15%"},
                cost_usd=0.0,
                latency_ms=0.1,
                explanation="Resolved via deterministic Kelly risk cap rule."
            )

        # 3. Known Category / Schema Lookup
        if request_type == "LIST_CATEGORIES":
            self.deterministic_hits += 1
            return DeterministicResult(
                is_deterministic=True,
                handled=True,
                action_type="TABLE_LOOKUP",
                output={"categories": self.EXACT_LOOKUPS["categories"]},
                cost_usd=0.0,
                latency_ms=0.05,
                explanation="Resolved via direct table lookup."
            )

        # 4. Keyword to skill category mapping
        if request_type == "CLASSIFY_SKILL_KEYWORD":
            keyword = str(data.get("keyword", "")).lower()
            mapping = {
                "python": "Engineering",
                "fastapi": "Engineering",
                "docker": "DevOps",
                "sql": "Data",
                "postgresql": "Data",
                "rag": "AI/NLP",
                "llm": "AI/NLP",
                "n8n": "Automation",
                "zapier": "Automation",
                "soc2": "Security/Compliance",
                "iso": "Security/Compliance"
            }
            if keyword in mapping:
                self.deterministic_hits += 1
                return DeterministicResult(
                    is_deterministic=True,
                    handled=True,
                    action_type="KEYWORD_MAP",
                    output={"keyword": keyword, "category": mapping[keyword]},
                    cost_usd=0.0,
                    latency_ms=0.05,
                    explanation="Direct regex/keyword deterministic mapping."
                )

        # Not deterministic -> Must pass to probabilistic model layers
        self.model_delegations += 1
        return DeterministicResult(
            is_deterministic=False,
            handled=False,
            explanation="Requires natural language reasoning, synthesis, or qualitative evaluation."
        )

    def get_stats(self) -> Dict[str, Any]:
        total = self.deterministic_hits + self.model_delegations
        hit_rate = (self.deterministic_hits / total * 100) if total > 0 else 0.0
        return {
            "deterministic_hits": self.deterministic_hits,
            "model_delegations": self.model_delegations,
            "hit_rate_pct": round(hit_rate, 1),
            "estimated_cost_saved_usd": round(self.deterministic_hits * 0.015, 3)
        }
