import hashlib
import json
from typing import Dict, Any, List, Set, Optional, Callable
from pydantic import BaseModel, ValidationError


class ToolLoopDetectedException(Exception):
    """Raised when an agent attempts to execute an identical tool call in a loop."""
    pass


class ToolCallOptimizer:
    """Layer 4: Tool Call Optimization.
    Compounds 3 critical practices:
    1. Pre-invocation check (input schema validation & duplication check)
    2. Output validation (strict Pydantic model conformance)
    3. Loop prevention (track tool+args fingerprint; halt repeats)
    """

    def __init__(self, max_allowed_duplicate_calls: int = 1):
        self.max_duplicates = max_allowed_duplicate_calls
        self.call_history: List[str] = []
        self.fingerprint_counts: Dict[str, int] = {}
        self.blocked_loops_count = 0
        self.validation_errors_caught = 0

    def compute_fingerprint(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        serialized = json.dumps({"tool": tool_name, "args": arguments}, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

    def pre_invocation_check(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        required_keys: Optional[List[str]] = None
    ) -> bool:
        """1. Validates inputs & detects repeated loop execution."""
        # Validate required parameters
        if required_keys:
            for k in required_keys:
                if k not in arguments or arguments[k] is None:
                    raise ValueError(f"Pre-invocation failed: Missing mandatory parameter '{k}' for tool '{tool_name}'.")

        # Loop prevention: fingerprint tracking
        fp = self.compute_fingerprint(tool_name, arguments)
        self.fingerprint_counts[fp] = self.fingerprint_counts.get(fp, 0) + 1

        if self.fingerprint_counts[fp] > self.max_duplicates:
            self.blocked_loops_count += 1
            raise ToolLoopDetectedException(
                f"Loop prevention triggered: Tool '{tool_name}' invoked with identical arguments {self.fingerprint_counts[fp]} times. "
                f"Halting execution to prevent runaway costs."
            )

        self.call_history.append(fp)
        return True

    def validate_output(
        self,
        output_data: Any,
        schema_cls: type[BaseModel]
    ) -> BaseModel:
        """2. Output validation: Enforce schema before downstream passing."""
        try:
            if isinstance(output_data, dict):
                return schema_cls(**output_data)
            elif isinstance(output_data, schema_cls):
                return output_data
            else:
                return schema_cls.model_validate(output_data)
        except ValidationError as e:
            self.validation_errors_caught += 1
            raise ValueError(f"Output validation failed for {schema_cls.__name__}: {str(e)}")

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "total_tool_calls_monitored": len(self.call_history),
            "blocked_runaway_loops": self.blocked_loops_count,
            "validation_errors_prevented": self.validation_errors_caught
        }
