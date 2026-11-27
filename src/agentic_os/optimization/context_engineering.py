import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class CompactPipelineState(BaseModel):
    """Clean, structured state object carrying only essential signals."""
    founder_id: str
    target_category: str
    constraints_summary: str
    last_completed_stage: str
    immediate_preceding_output: Dict[str, Any]
    active_hypotheses: List[str] = Field(default_factory=list)


class ContextEngineer:
    """Layer 3: Context Engineering.
    Measures actual character/token reduction when compiling compact step state
    vs passing full raw upstream payloads.
    """

    def __init__(self):
        self.raw_tokens_observed = 0
        self.compiled_tokens_emitted = 0
        self.tokens_trimmed = 0

    def compile_step_context(
        self,
        current_stage: str,
        state: CompactPipelineState,
        additional_signal: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Assembles a minimal, signal-dense context payload."""
        raw_serialized = json.dumps(
            {
                "state": state.model_dump(),
                "additional_signal": additional_signal or {},
            },
            default=str,
        )
        raw_tokens = max(1, len(raw_serialized) // 4)

        payload: Dict[str, Any] = {
            "stage": current_stage,
            "target": state.target_category,
            "constraints": state.constraints_summary,
            "inputs_from_preceding_stage": state.immediate_preceding_output,
        }

        if additional_signal:
            for k, v in additional_signal.items():
                if k not in ("raw_dump", "full_trace", "debug_log"):
                    payload[k] = v

        compiled_tokens = max(1, len(json.dumps(payload, default=str)) // 4)
        trimmed = max(0, raw_tokens - compiled_tokens)

        self.raw_tokens_observed += raw_tokens
        self.compiled_tokens_emitted += compiled_tokens
        self.tokens_trimmed += trimmed

        return payload

    def get_token_savings_metrics(self) -> Dict[str, Any]:
        pct = (
            round((self.tokens_trimmed / self.raw_tokens_observed) * 100.0, 1)
            if self.raw_tokens_observed > 0
            else 0.0
        )
        return {
            "raw_tokens_observed": self.raw_tokens_observed,
            "compiled_tokens_emitted": self.compiled_tokens_emitted,
            "cumulative_tokens_trimmed": self.tokens_trimmed,
            "measured_context_reduction_pct": pct,
        }
