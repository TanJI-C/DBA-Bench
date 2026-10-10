"""Narrow target adapter boundary for benchmark planning and execution."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .manifest import ExperimentManifest
    from .models import BoundedScenarioRunSpec, PersistentScenarioRunSpec


class BenchmarkTargetAdapter(Protocol):
    scenario_kind: str

    def plan(self, manifest: ExperimentManifest) -> list[BoundedScenarioRunSpec | PersistentScenarioRunSpec]: ...

    def build_command(
        self,
        spec: BoundedScenarioRunSpec | PersistentScenarioRunSpec,
        manifest: ExperimentManifest,
        project_root: Path,
    ) -> list[str]: ...
