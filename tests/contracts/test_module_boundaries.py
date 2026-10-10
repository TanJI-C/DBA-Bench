from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src.project_paths import REPOSITORY_ROOT, SOURCE_ROOT

PROJECT_ROOT = SOURCE_ROOT
SRC_ROOT = PROJECT_ROOT / "src"


def _absolute_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module)
    return modules


def test_migrated_persistent_scenario_and_benchmark_namespaces_are_unique():
    for relative in (
        "src/orchestration",
        "src/evaluation",
        "src/evaluation/experiment",
        "src/experiment",
    ):
        assert not (PROJECT_ROOT / relative).exists(), relative
    for relative in (
        "src/persistent_scenarios/model",
        "src/persistent_scenarios/runtime",
        "src/persistent_scenarios/evaluation",
        "src/persistent_scenarios/backend",
        "src/scenarios/runtime",
        "src/scenarios/evaluation",
        "src/benchmark",
    ):
        assert (PROJECT_ROOT / relative).is_dir(), relative


def test_production_code_does_not_import_removed_scenario_namespaces():
    violations = []
    for path in SRC_ROOT.rglob("*.py"):
        for module in _absolute_imports(path):
            if module == "src.evaluation" or module.startswith("src.evaluation."):
                violations.append((path, module))
            if module == "src.orchestration" or module.startswith("src.orchestration."):
                violations.append((path, module))
    assert violations == []


def test_persistent_scenario_model_does_not_import_runtime_evaluation_or_backend():
    forbidden = (
        "src.persistent_scenarios.runtime",
        "src.persistent_scenarios.evaluation",
        "src.persistent_scenarios.backend",
        "src.benchmark",
    )
    violations = []
    for path in (SRC_ROOT / "persistent_scenarios/model").rglob("*.py"):
        for module in _absolute_imports(path):
            if module == forbidden[0] or module.startswith(forbidden[0] + "."):
                violations.append((path, module))
            if module == forbidden[1] or module.startswith(forbidden[1] + "."):
                violations.append((path, module))
            if module == forbidden[2] or module.startswith(forbidden[2] + "."):
                violations.append((path, module))
            if module == forbidden[3] or module.startswith(forbidden[3] + "."):
                violations.append((path, module))
    assert violations == []


def test_persistent_scenario_runtime_and_evaluation_do_not_import_concrete_backend():
    violations = []
    for relative in ("src/persistent_scenarios/runtime", "src/persistent_scenarios/evaluation"):
        for path in (PROJECT_ROOT / relative).rglob("*.py"):
            for module in _absolute_imports(path):
                if module.startswith("src.persistent_scenarios.backend.postgres"):
                    violations.append((path, module))
    assert violations == []


def test_benchmark_core_does_not_import_concrete_persistent_scenario_backend():
    violations = []
    for name in ("planner.py", "runner.py", "store.py", "aggregate.py"):
        path = SRC_ROOT / "benchmark" / name
        for module in _absolute_imports(path):
            if module.startswith("src.persistent_scenarios.backend"):
                violations.append((path, module))
    assert violations == []


def test_postgres_backend_is_composition_and_registry_is_explicit():
    backend_source = (SRC_ROOT / "persistent_scenarios/backend/postgres/backend.py").read_text(encoding="utf-8")
    assert "SELECT " not in backend_source
    assert "alert_text" not in backend_source
    assert "SCENARIOS_BY_ID" not in backend_source
    assert "PostgresEventCapabilityRegistry" in backend_source

    from src.persistent_scenarios.backend.contracts import EventCapabilityRegistry, PersistentScenarioEventCapability
    from src.persistent_scenarios.backend.postgres.registry import PostgresEventCapabilityRegistry

    registry = PostgresEventCapabilityRegistry(())
    assert isinstance(registry, EventCapabilityRegistry)
    assert registry.capability_ids() == ()
    with pytest.raises(ValueError, match="capability_id"):
        registry.capability("missing")


def test_postgres_capabilities_speak_the_core_protocol_only():
    from src.persistent_scenarios.backend.contracts import PersistentScenarioEventCapability
    from src.persistent_scenarios.backend.postgres.instance_adapter import InstanceCapabilityAdapter

    required = {"declaration", "activate", "alert", "cleanup", "assert_clean"}
    assert required <= set(dir(PersistentScenarioEventCapability))
    adapter_methods = set(dir(InstanceCapabilityAdapter))
    assert required <= adapter_methods
    retired = {"evaluate_diagnosis", "evaluate_outcome", "reference_actions", "safety_scope", "match_inspection_finding"}
    assert not retired & adapter_methods


def test_project_root_is_independent_of_benchmark_module_depth():
    assert SOURCE_ROOT == PROJECT_ROOT
    assert (SRC_ROOT / "persistent_scenarios" / "postgres").is_dir()
    assert (REPOSITORY_ROOT / "examples").is_dir()


def test_public_package_smoke_imports_have_no_runtime_side_effects():
    if not (REPOSITORY_ROOT / "data" / "workloads" / "tpcds" / "queries" / "query_0.sql").is_file():
        pytest.skip(
            "TPC-DS query text is not present; fetch it per docs/getting-started.md"
        )
    import src.benchmark.api
    import src.cli
    import src.persistent_scenarios.api
    import src.scenarios
