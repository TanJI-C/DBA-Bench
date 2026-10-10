"""LLM prompt-cache circuit breaker.

连续多次诊断调用 cache_read=0（prompt cache 持续不命中/未被注入）达到阈值即
熔断：终止当前对话，runner 按场景进程崩溃的既有语义放弃同一 chunk 的后续
case，并在 attempt 目录落一份 JSON 报告。

默认开启、默认连续 5 轮判定；可在 llm_config.json 的模型条目里覆盖：

    "<model-name>": {
        "url": "...",
        "cache_circuit_breaker": {"enabled": true, "consecutive_misses": 3}
    }

首调冷启动（cache 写入）不会误触发：健康会话 call2 起必然 read>0，连续
不命中只出现在缓存注入消失的会话里。非诊断调用（summary/auxiliary 前缀
不同）不计入也不重置。
"""

import json
import os
from typing import Any, Dict, List, Optional

DEFAULT_CONSECUTIVE_MISSES = 5
REPORT_FILENAME = "cache_circuit_breaker_report.json"


class CacheCircuitBreakerError(RuntimeError):
    """缓存熔断触发：当前对话的 prompt cache 连续不命中。"""


class CacheBreakerConfig:
    def __init__(self, enabled: bool = True, consecutive_misses: int = DEFAULT_CONSECUTIVE_MISSES):
        self.enabled = enabled
        self.consecutive_misses = consecutive_misses

    @classmethod
    def from_entry(cls, entry: Any) -> "CacheBreakerConfig":
        block = entry.get("cache_circuit_breaker") if isinstance(entry, dict) else None
        if not isinstance(block, dict):
            return cls()
        enabled = block.get("enabled", True)
        misses = block.get("consecutive_misses", DEFAULT_CONSECUTIVE_MISSES)
        if not isinstance(enabled, bool):
            raise ValueError(
                f"cache_circuit_breaker.enabled must be a bool: {enabled!r}"
            )
        if not isinstance(misses, int) or isinstance(misses, bool) or misses < 1:
            raise ValueError(
                f"cache_circuit_breaker.consecutive_misses must be an int >= 1: {misses!r}"
            )
        return cls(enabled=enabled, consecutive_misses=misses)


class CacheCircuitBreaker:
    """统计诊断调用的连续 cache miss，达到阈值即熔断。"""

    def __init__(self, config: CacheBreakerConfig, model: str):
        self.config = config
        self.model = model
        self.miss_streak = 0
        self.miss_events: List[Dict[str, Any]] = []

    @property
    def tripped(self) -> bool:
        return self.config.enabled and self.miss_streak >= self.config.consecutive_misses

    def record(self, cached_input_tokens: int, purpose: str = "diagnostic", call_id: str = "") -> None:
        if not self.config.enabled or purpose != "diagnostic":
            return
        if cached_input_tokens > 0:
            self.miss_streak = 0
            return
        self.miss_streak += 1
        self.miss_events.append({"call_id": call_id, "cached_input_tokens": cached_input_tokens})

    def report(self, output_dir: Optional[str]) -> Optional[str]:
        """熔断报告落盘到 attempt 目录；目录未知时返回 None。"""
        payload = {
            "schema": "aiopsbench_cache_circuit_breaker_v1",
            "model": self.model,
            "consecutive_misses": self.miss_streak,
            "threshold": self.config.consecutive_misses,
            "miss_events": self.miss_events,
        }
        if not output_dir:
            return None
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, REPORT_FILENAME)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        return path

    def error_message(self) -> str:
        return (
            f"cache circuit breaker tripped: model={self.model!r}, "
            f"consecutive cache-miss calls={self.miss_streak} "
            f">= threshold={self.config.consecutive_misses} "
            f"(calls={self.miss_events!r})"
        )
