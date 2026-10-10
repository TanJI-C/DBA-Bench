from __future__ import annotations

import re

from .adapters import plan_bounded_scenario_runs, plan_persistent_scenario_runs
from .manifest import ExperimentManifest
from .models import BoundedScenarioRunSpec, PersistentScenarioRunSpec, ScenarioKind

def slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()
    if not normalized:
        raise ValueError(f"Cannot create identifier from {value!r}")
    return normalized


def select_specs(
    specs: list[BoundedScenarioRunSpec | PersistentScenarioRunSpec],
    run_ids: list[str],
) -> list[BoundedScenarioRunSpec | PersistentScenarioRunSpec]:
    if not run_ids:
        return specs
    if len(set(run_ids)) != len(run_ids):
        raise ValueError(f"Duplicate run IDs: {run_ids}")
    specs_by_id = {spec.run_id: spec for spec in specs}
    missing = sorted(set(run_ids) - set(specs_by_id))
    if missing:
        raise ValueError(f"Unknown run IDs: {missing}")
    requested = set(run_ids)
    return [spec for spec in specs if spec.run_id in requested]


def plan_runs(manifest: ExperimentManifest) -> list[BoundedScenarioRunSpec | PersistentScenarioRunSpec]:
    if manifest.benchmark.scenario_kind is ScenarioKind.PERSISTENT:
        return plan_persistent_scenario_runs(manifest)
    return plan_bounded_scenario_runs(manifest)
