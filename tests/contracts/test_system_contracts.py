from pathlib import Path
from types import SimpleNamespace

import pytest

from src.scenarios import SCENARIO_REGISTRY
from src.scenarios.base import DatabaseSystem
from src.execution.environment import PGEnv, TiDBEnv
from src.benchmark.isolation import derive_worker_demand
from src.benchmark.manifest import load_manifest
from src.benchmark.planner import plan_runs


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMMON_TOOL_ALIASES = {
    "query_metrics",
    "execute_sql",
    "read_log",
    "help",
    "submit",
    "exit",
}
SYSTEM_PACKAGE_NAMES = {
    DatabaseSystem.POSTGRESQL: "postgres",
    DatabaseSystem.TIDB: "tidb",
}


def _pg_env() -> PGEnv:
    return PGEnv(deployment=SimpleNamespace(resources={}))


def _tidb_env() -> TiDBEnv:
    deployment = SimpleNamespace(
        run_id="system-contract",
        primary_tidb_endpoint=("127.0.0.1", 4000),
    )
    return TiDBEnv(deployment=deployment)


def _write_manifest(tmp_path: Path, system: str, category: str, scenario: str) -> Path:
    path = tmp_path / f"{system}.yaml"
    path.write_text(
        f"""
experiment_id: {system}-contract
benchmark:
  systems: [{system}]
  categories: [{category}]
  scenarios: [{scenario}]
agents: [{{id: mock, mode: mock}}]
repetitions: 1
seeds: [11]
""".strip(),
        encoding="utf-8",
    )
    return path


def test_registry_system_category_scenario_keys_are_unique():
    keys = [
        (registration.system, registration.category, registration.scenario_id)
        for registration in SCENARIO_REGISTRY
    ]
    assert len(keys) == len(set(keys))
    assert {registration.system for registration in SCENARIO_REGISTRY} == {
        DatabaseSystem.POSTGRESQL,
        DatabaseSystem.TIDB,
    }


def test_every_scenario_case_and_registration_agree_on_system():
    for registration in SCENARIO_REGISTRY:
        assert registration.system is registration.scenario.system
        assert all(
            case.system is registration.system
            for case in registration.scenario.cases
        )


def test_scenarios_and_evaluators_follow_system_category_module_axis():
    for registration in SCENARIO_REGISTRY:
        system_package = SYSTEM_PACKAGE_NAMES[registration.system]
        category = registration.category.value
        scenario_prefix = f"src.scenarios.{system_package}.{category}"
        assert (
            registration.scenario.__class__.__module__ == scenario_prefix
            or registration.scenario.__class__.__module__.startswith(scenario_prefix + ".")
        ), registration
        for case in registration.scenario.cases:
            evaluator_prefix = f"src.scenarios.evaluation.{system_package}.{category}"
            assert (
                case.evaluator.__module__ == evaluator_prefix
                or case.evaluator.__module__.startswith(evaluator_prefix + ".")
            ), (registration, case.evaluator)


def test_tidb_fault_injectors_are_colocated_with_their_scenario():
    for registration in SCENARIO_REGISTRY:
        if registration.system is not DatabaseSystem.TIDB:
            continue
        scenario_module = registration.scenario.__class__.__module__
        for case in registration.scenario.cases:
            assert all(
                plan.injector_type.__module__ in {scenario_module, "src.scenarios.faults"}
                for plan in registration.scenario.build_fault_plan(case)
            ), (registration, case)


@pytest.mark.parametrize(
    ("relative_root", "allowed_root_modules"),
    (
        ("src/scenarios/postgres", {"__init__.py", "common.py"}),
        ("src/scenarios/tidb", {"__init__.py", "common.py", "runtime.py"}),
        ("src/scenarios/evaluation/postgres", {"__init__.py"}),
        ("src/scenarios/evaluation/tidb", {"__init__.py", "base.py"}),
    ),
)
def test_system_packages_do_not_place_category_modules_at_the_root(
    relative_root,
    allowed_root_modules,
):
    root = PROJECT_ROOT / relative_root
    root_modules = {path.name for path in root.glob("*.py")}
    assert root_modules == allowed_root_modules


def test_environments_reject_cases_from_the_other_system():
    postgres_case = next(
        registration.scenario.cases[0]
        for registration in SCENARIO_REGISTRY
        if registration.system is DatabaseSystem.POSTGRESQL
    )
    tidb_case = next(
        registration.scenario.cases[0]
        for registration in SCENARIO_REGISTRY
        if registration.system is DatabaseSystem.TIDB
    )

    with pytest.raises(TypeError, match="Environment/case system mismatch"):
        _pg_env().configure_case(tidb_case)
    with pytest.raises(TypeError, match="Environment/case system mismatch"):
        _tidb_env().configure_case(postgres_case)


def test_every_formal_registration_has_an_existing_entrypoint():
    formal = [
        registration
        for registration in SCENARIO_REGISTRY
        if registration.entrypoint is not None
    ]
    assert formal
    for registration in formal:
        assert (PROJECT_ROOT / "examples" / registration.entrypoint).is_file(), registration


def test_postgresql_and_tidb_share_the_common_agent_tool_surface():
    for env in (_pg_env(), _tidb_env()):
        aliases = {
            schema["function"]["name"]
            for schema in env.get_tool_schemas()
        }
        assert COMMON_TOOL_ALIASES <= aliases, type(env).__name__


@pytest.mark.parametrize(
    ("system", "category", "scenario"),
    (
        ("postgresql", "query_perf", "pg_query_perf_missing_index"),
        ("tidb", "query_perf", "tidb_query_perf_index_merge_selection_failure"),
    ),
)
def test_each_system_manifest_plans_with_system_identity(
    tmp_path,
    system,
    category,
    scenario,
):
    manifest = load_manifest(_write_manifest(tmp_path, system, category, scenario))
    specs = plan_runs(manifest)

    assert specs
    assert {spec.system.value for spec in specs} == {system}
    if system == "tidb":
        assert all(spec.resources is not None for spec in specs)


def test_tidb_parallel_plan_derives_worker_demand_without_fault_snapshots(tmp_path):
    path = _write_manifest(
        tmp_path,
        "tidb",
        "query_perf",
        "tidb_query_perf_index_merge_selection_failure",
    )
    manifest_text = path.read_text(encoding="utf-8")
    path.write_text(
        manifest_text
        + "\nruntime:\n  concurrency: 2\n  isolation: {numa_policy: local}\n",
        encoding="utf-8",
    )
    manifest = load_manifest(path)
    specs = plan_runs(manifest)

    demand = derive_worker_demand(specs, manifest.runtime.isolation)

    assert manifest.runtime.fault_snapshot == "auto"
    assert demand.physical_cores_per_worker == 4
    assert demand.memory_mb_per_worker == 9216
