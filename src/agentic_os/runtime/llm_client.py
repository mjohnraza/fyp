import json
import httpx
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from src.agentic_os.optimization.model_tiering import ModelTier


class LLMDecision(BaseModel):
    thought: str
    action_type: str  # "TOOL_CALL" or "FINAL_ANSWER"
    tool_name: Optional[str] = None
    tool_args: Dict[str, Any] = {}
    final_answer: Optional[str] = None
    model_used: str = "ollama/qwen2.5:1.5b"


class OllamaLLMClient:
    """Local LLM client connecting to Ollama (/api/chat) with Model Tiering support.
    Falls back cleanly if Ollama is unavailable or disabled in fast deterministic test mode.
    """

    TIER_MODELS = {
        ModelTier.SMALL: "qwen2.5:1.5b",
        ModelTier.MID: "qwen3.5:4b",
        ModelTier.LARGE: "qwen3.5:4b",
    }

    def __init__(self, base_url: str = "http://localhost:11434", timeout_sec: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_sec = timeout_sec

    def is_available(self) -> bool:
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=1.5)
            return resp.status_code == 200
        except Exception:
            return False

    def decide_next_step(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tier: ModelTier = ModelTier.SMALL
    ) -> Optional[LLMDecision]:
        """Calls Ollama /api/chat with tool schemas and returns a structured LLMDecision.
        Returns None if Ollama is unreachable so the agent can fall back to planned tool routing.
        """
        model = self.TIER_MODELS.get(tier, "qwen2.5:1.5b")
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "tools": tools,
            "stream": False,
            "options": {"temperature": 0.1}
        }

        try:
            resp = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout_sec
            )
            if resp.status_code != 200:
                return None

            data = resp.json()
            msg = data.get("message", {})
            tool_calls = msg.get("tool_calls") or []

            if tool_calls:
                tc = tool_calls[0]
                fn = tc.get("function", {})
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {}
                return LLMDecision(
                    thought=msg.get("content", "") or f"Invoking tool {fn.get('name')}",
                    action_type="TOOL_CALL",
                    tool_name=fn.get("name"),
                    tool_args=args,
                    model_used=f"ollama/{model}"
                )

            return LLMDecision(
                thought="Goal satisfied based on gathered observations.",
                action_type="FINAL_ANSWER",
                final_answer=msg.get("content", ""),
                model_used=f"ollama/{model}"
            )
        except Exception:
            return None
