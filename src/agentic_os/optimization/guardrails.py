import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class GuardrailBreachException(Exception):
    """Raised when an execution boundary or timeout threshold is violated."""
    pass


class EarlyExitResult(BaseModel):
    exited_early: bool
    step_reached: int
    confidence_score: float
    reason: str


class PipelineGuardrails:
    """Layer 7: Guardrails and Early Exit.
    Enforces non-negotiable operational safety limits in orchestration:
    1. Maximum iteration depth (halts infinite loop-backs)
    2. Per-step & total request timeouts
    3. Confidence-based early exit (exits when satisfaction threshold is met)
    4. Escalation to human checkpoint on boundary exhaustion
    """

    def __init__(
        self,
        max_loop_iterations: int = 2,
        max_reasoning_steps: int = 8,
        per_step_timeout_sec: float = 10.0,
        total_request_timeout_sec: float = 45.0,
        early_exit_confidence_threshold: float = 0.85
    ):
        self.max_loops = max_loop_iterations
        self.max_steps = max_reasoning_steps
        self.per_step_timeout = per_step_timeout_sec
        self.total_timeout = total_request_timeout_sec
        self.early_exit_threshold = early_exit_confidence_threshold

        self.current_step = 0
        self.current_loops = 0
        self.start_time: Optional[float] = None
        self.step_start_time: Optional[float] = None
        self.early_exits_triggered = 0

    def start_request(self) -> None:
        self.start_time = time.time()
        self.current_step = 0
        self.current_loops = 0

    def start_step(self, step_name: str) -> None:
        if self.start_time is None:
            self.start_request()

        # Check total timeout
        elapsed_total = time.time() - self.start_time
        if elapsed_total > self.total_timeout:
            raise GuardrailBreachException(
                f"Total request timeout exceeded ({elapsed_total:.2f}s > {self.total_timeout}s). Escalating to human checkpoint."
            )

        self.current_step += 1
        if self.current_step > self.max_steps:
            raise GuardrailBreachException(
                f"Maximum reasoning step limit reached ({self.current_step} > {self.max_steps}). Forcing early termination."
            )

        self.step_start_time = time.time()

    def end_step(self, step_name: str) -> None:
        if self.step_start_time:
            step_duration = time.time() - self.step_start_time
            if step_duration > self.per_step_timeout:
                raise GuardrailBreachException(
                    f"Per-step timeout exceeded in '{step_name}' ({step_duration:.2f}s > {self.per_step_timeout}s)."
                )

    def record_loop_back(self, source_stage: str) -> bool:
        """Enforces hard limits on loop-backs."""
        self.current_loops += 1
        if self.current_loops > self.max_loops:
            raise GuardrailBreachException(
                f"Maximum loop-back depth ({self.current_loops} > {self.max_loops}) reached. "
                f"Halting retry cycle to prevent runaway budget leakage; escalating to Human Checkpoint."
            )
        return True

    def check_early_exit(self, confidence_score: float, current_stage: str) -> EarlyExitResult:
        """Exits early when output quality/confidence is already decisively satisfied."""
        if confidence_score >= self.early_exit_threshold:
            self.early_exits_triggered += 1
            return EarlyExitResult(
                exited_early=True,
                step_reached=self.current_step,
                confidence_score=confidence_score,
                reason=f"Early exit triggered at '{current_stage}': Confidence {confidence_score:.2f} satisfies threshold ({self.early_exit_threshold}). Bypassing redundant refinement cycles."
            )
        return EarlyExitResult(
            exited_early=False,
            step_reached=self.current_step,
            confidence_score=confidence_score,
            reason="Confidence below early exit threshold; proceeding with standard pipeline pass."
        )

    def get_guardrail_report(self) -> Dict[str, Any]:
        elapsed = (time.time() - self.start_time) if self.start_time else 0.0
        return {
            "total_elapsed_sec": round(elapsed, 2),
            "steps_executed": self.current_step,
            "loop_backs_incurred": self.current_loops,
            "max_loops_allowed": self.max_loops,
            "early_exits_triggered": self.early_exits_triggered,
            "within_safety_bounds": elapsed <= self.total_timeout and self.current_loops <= self.max_loops
        }
