"""诊断死循环止血：基于轮次签名多样性的及时终止。

数据依据（全量 trace 标定）：病理 run 94 轮仅 11 种不同工具调用签名
（多样比 0.12），周期性循环（A→B→C→…→A）不含
相邻重复；健康 run（含成功 run）签名多样比全部 ≥ 0.5，轮内相邻重复至多 2 次。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

TOOL_LOOP_ABORT_MARKER = "MODEL-LOOP-ABORT"


@dataclass(frozen=True, slots=True)
class LoopGuardConfig:
    enabled: bool = True
    # 连续 N 轮完全相同的调用（含参数）
    consecutive_limit: int = 3
    # 轮数达到 min_ratio_rounds 后，distinct/turns 低于该比值视为僵化循环
    min_ratio_rounds: int = 12
    min_distinct_ratio: float = 0.5

    @classmethod
    def from_settings(cls, raw: Mapping[str, Any] | None) -> "LoopGuardConfig":
        if raw is None:
            return cls()
        if not isinstance(raw, Mapping):
            raise ValueError(
                f"loop_guard settings must be a mapping: got {type(raw).__name__!r}"
            )
        allowed = {"enabled", "consecutive_limit", "min_ratio_rounds", "min_distinct_ratio"}
        unexpected = set(raw) - allowed
        if unexpected:
            raise ValueError(
                f"loop_guard settings has unknown keys: {sorted(unexpected)}"
            )
        config = cls(**raw)
        if not isinstance(config.enabled, bool):
            raise ValueError(
                f"loop_guard.enabled must be bool: got {config.enabled!r}"
            )
        for name in ("consecutive_limit", "min_ratio_rounds"):
            value = getattr(config, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError(
                    f"loop_guard.{name} must be a positive integer: got {value!r}"
                )
        ratio = config.min_distinct_ratio
        if not isinstance(ratio, (int, float)) or isinstance(ratio, bool) or not 0 < ratio <= 1:
            raise ValueError(
                f"loop_guard.min_distinct_ratio must be in (0, 1]: got {ratio!r}"
            )
        return config


def round_signature(actions: Sequence[Mapping[str, Any]]) -> str:
    """一轮诊断的工具调用签名：同名同参视为相同。"""
    return json.dumps(
        [
            {"api": action.get("api"), "args": action.get("args")}
            for action in actions
        ],
        ensure_ascii=False,
        sort_keys=True,
    )


def check_loop(
    signatures: Sequence[str],
    config: LoopGuardConfig,
) -> str | None:
    """返回止血原因；无异常返回 None。signatures 为含当轮在内的全部历史签名。"""
    if not config.enabled or not signatures:
        return None
    latest = signatures[-1]
    if (
        config.consecutive_limit <= len(signatures)
        and all(sig == latest for sig in signatures[-config.consecutive_limit:])
    ):
        return f"连续 {config.consecutive_limit} 轮重复完全相同的工具调用"
    if len(signatures) >= config.min_ratio_rounds:
        distinct = len(set(signatures))
        ratio = distinct / len(signatures)
        if ratio < config.min_distinct_ratio:
            return (
                f"诊断僵化：{len(signatures)} 轮中仅 {distinct} 种不同工具调用"
                f"（占比 {ratio:.2f} < {config.min_distinct_ratio}）"
            )
    return None
