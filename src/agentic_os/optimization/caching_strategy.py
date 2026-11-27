import time
import hashlib
import json
from typing import Dict, Any, Optional, Tuple


class CacheEntry:
    def __init__(self, value: Any, ttl_seconds: float = 3600.0):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl_seconds

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl


class FourTierCacheManager:
    """Layer 6: 4-Tier Caching Strategy.
    Spans 4 distinct caching surfaces:
    1. Response Caching: Exact hash of pipeline run inputs
    2. Embedding Caching: Cached vector representations of evidence snippets
    3. Tool Result Caching: Cached RAG corpus lookups with TTL
    4. Intermediate Reasoning Caching: Cached capability intersections & obstacle chains
    """

    def __init__(self):
        # 4 distinct cache stores
        self._response_cache: Dict[str, CacheEntry] = {}
        self._embedding_cache: Dict[str, CacheEntry] = {}
        self._tool_cache: Dict[str, CacheEntry] = {}
        self._reasoning_cache: Dict[str, CacheEntry] = {}

        self.hits = {"response": 0, "embedding": 0, "tool": 0, "reasoning": 0}
        self.misses = {"response": 0, "embedding": 0, "tool": 0, "reasoning": 0}

    def _hash_key(self, key_data: Any) -> str:
        serialized = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    # Tier 1: Response Cache
    def get_response(self, input_payload: Dict[str, Any]) -> Optional[Any]:
        key = self._hash_key(input_payload)
        entry = self._response_cache.get(key)
        if entry and not entry.is_expired():
            self.hits["response"] += 1
            return entry.value
        self.misses["response"] += 1
        return None

    def set_response(self, input_payload: Dict[str, Any], result: Any, ttl: float = 1800.0) -> None:
        key = self._hash_key(input_payload)
        self._response_cache[key] = CacheEntry(result, ttl)

    # Tier 2: Embedding Cache
    def get_embedding(self, text: str) -> Optional[Any]:
        key = hashlib.md5(text.encode("utf-8")).hexdigest()
        entry = self._embedding_cache.get(key)
        if entry and not entry.is_expired():
            self.hits["embedding"] += 1
            return entry.value
        self.misses["embedding"] += 1
        return None

    def set_embedding(self, text: str, embedding_vector: Any, ttl: float = 86400.0) -> None:
        key = hashlib.md5(text.encode("utf-8")).hexdigest()
        self._embedding_cache[key] = CacheEntry(embedding_vector, ttl)

    # Tier 3: Tool Result Cache
    def get_tool_result(self, tool_name: str, args: Dict[str, Any]) -> Optional[Any]:
        key = self._hash_key({"tool": tool_name, "args": args})
        entry = self._tool_cache.get(key)
        if entry and not entry.is_expired():
            self.hits["tool"] += 1
            return entry.value
        self.misses["tool"] += 1
        return None

    def set_tool_result(self, tool_name: str, args: Dict[str, Any], result: Any, ttl: float = 3600.0) -> None:
        key = self._hash_key({"tool": tool_name, "args": args})
        self._tool_cache[key] = CacheEntry(result, ttl)

    # Tier 4: Intermediate Reasoning Cache
    def get_reasoning(self, stage_name: str, input_signature: Any) -> Optional[Any]:
        key = self._hash_key({"stage": stage_name, "sig": input_signature})
        entry = self._reasoning_cache.get(key)
        if entry and not entry.is_expired():
            self.hits["reasoning"] += 1
            return entry.value
        self.misses["reasoning"] += 1
        return None

    def set_reasoning(self, stage_name: str, input_signature: Any, reasoning_output: Any, ttl: float = 3600.0) -> None:
        key = self._hash_key({"stage": stage_name, "sig": input_signature})
        self._reasoning_cache[key] = CacheEntry(reasoning_output, ttl)

    def invalidate_response(self, input_payload: Dict[str, Any]) -> bool:
        key = self._hash_key(input_payload)
        return self._response_cache.pop(key, None) is not None

    def invalidate_all(self) -> None:
        self._response_cache.clear()
        self._embedding_cache.clear()
        self._tool_cache.clear()
        self._reasoning_cache.clear()

    def get_telemetry(self) -> Dict[str, Any]:
        total_hits = sum(self.hits.values())
        total_misses = sum(self.misses.values())
        total_queries = total_hits + total_misses
        ratio = (total_hits / total_queries * 100) if total_queries > 0 else 0.0

        return {
            "total_queries": total_queries,
            "total_hits": total_hits,
            "hit_ratio_pct": round(ratio, 1),
            "hits_breakdown": dict(self.hits),
            "estimated_dollars_saved_usd": round(total_hits * 0.012, 3)
        }
