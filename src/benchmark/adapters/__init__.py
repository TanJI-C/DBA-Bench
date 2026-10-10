"""Explicit bounded and Persistent Scenario benchmark target adapters."""

from __future__ import annotations

from ..models import ScenarioKind
from .persistent_scenario import (
    build_persistent_scenario_command,
    plan_persistent_scenario_runs,
    validate_persistent_scenario_target,
)
from .scenario import build_scenario_command, plan_bounded_scenario_runs, select_registrations


ADAPTER_TYPES = frozenset(kind.value for kind in ScenarioKind)


def require_scenario_kind(scenario_kind: str) -> str:
    if scenario_kind not in ADAPTER_TYPES:
        raise ValueError(f"Unsupported Scenario kind: scenario_kind={scenario_kind!r}")
    return scenario_kind


__all__ = (
    "ADAPTER_TYPES",
    "build_persistent_scenario_command",
    "build_scenario_command",
    "plan_bounded_scenario_runs",
    "plan_persistent_scenario_runs",
    "require_scenario_kind",
    "select_registrations",
    "validate_persistent_scenario_target",
)
