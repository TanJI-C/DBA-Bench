"""Configuration contract for the V-ExpeL Persistent Scenario baseline."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.agents.context_compaction import ContextCompactionConfig


@dataclass(frozen=True, slots=True)
class VExpeLConfig:
    retrieval_top_k: int = 5
    context_compaction: ContextCompactionConfig = ContextCompactionConfig()

    def __post_init__(self) -> None:
        if isinstance(self.retrieval_top_k, bool) or not isinstance(self.retrieval_top_k, int) or self.retrieval_top_k < 1:
            raise ValueError(
                "V-ExpeL retrieval_top_k must be a positive integer: "
                f"value={self.retrieval_top_k!r}"
            )

    @classmethod
    def from_settings(cls, settings: Mapping[str, Any]) -> "VExpeLConfig":
        if not isinstance(settings, Mapping):
            raise ValueError(f"V-ExpeL settings must be a mapping: value={settings!r}")
        allowed = {"retrieval_top_k", "context_compaction"}
        unknown = set(settings) - allowed
        if unknown:
            raise ValueError(f"V-ExpeL settings contain unknown fields: fields={sorted(unknown)}")
        retrieval_top_k = settings.get("retrieval_top_k", 5)
        compaction_settings = {}
        if "context_compaction" in settings:
            compaction_settings = {"context_compaction": settings["context_compaction"]}
        return cls(
            retrieval_top_k=retrieval_top_k,
            context_compaction=ContextCompactionConfig.from_settings(compaction_settings),
        )
