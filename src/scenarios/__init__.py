"""System-neutral scenario registry."""

from src.scenarios.base import (
    BaseScenario,
    CaseRun,
    FaultPlan,
    InjectionRecord,
    PostgresScenario,
    PostgresScenarioCase,
    ScenarioCase,
    TiDBScenario,
    TiDBScenarioCase,
)
from .registry import ScenarioCategory, ScenarioRegistration


def _load_registries():
    from .postgres import SCENARIO_REGISTRY as postgres_registry
    from .tidb import SCENARIO_REGISTRY as tidb_registry

    scenario_registry = postgres_registry + tidb_registry
    scenarios_by_id = {
        registration.scenario_id: registration
        for registration in scenario_registry
    }
    if len(scenarios_by_id) != len(scenario_registry):
        raise ValueError("Scenario registry contains duplicate scenario IDs")
    return {
        "POSTGRES_SCENARIO_REGISTRY": postgres_registry,
        "TIDB_SCENARIO_REGISTRY": tidb_registry,
        "SCENARIO_REGISTRY": scenario_registry,
        "SCENARIOS_BY_ID": scenarios_by_id,
        "ALL_SCENARIOS": tuple(registration.scenario for registration in scenario_registry),
    }


def __getattr__(name: str):
    if name not in {
        "ALL_SCENARIOS",
        "POSTGRES_SCENARIO_REGISTRY",
        "SCENARIO_REGISTRY",
        "SCENARIOS_BY_ID",
        "TIDB_SCENARIO_REGISTRY",
    }:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    values = _load_registries()
    globals().update(values)
    return values[name]


__all__ = (
    "ALL_SCENARIOS",
    "BaseScenario",
    "CaseRun",
    "FaultPlan",
    "InjectionRecord",
    "PostgresScenario",
    "PostgresScenarioCase",
    "POSTGRES_SCENARIO_REGISTRY",
    "SCENARIO_REGISTRY",
    "SCENARIOS_BY_ID",
    "ScenarioCase",
    "ScenarioCategory",
    "ScenarioRegistration",
    "TiDBScenario",
    "TiDBScenarioCase",
    "TIDB_SCENARIO_REGISTRY",
)
