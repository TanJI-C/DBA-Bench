from __future__ import annotations

import sys
from pathlib import Path

from src.scenarios import SCENARIO_REGISTRY
from src.execution.metric_catalog import metric_catalog_for_system
from src.database.system import DatabaseSystem

from ..manifest import ExperimentManifest
from ..models import BoundedScenarioRunSpec
from ..commands import container_name, script_options


SCENARIO_PORT_BASES = {
    "pg_health_check_autovacuum_sustainability": 15801,
    "pg_health_check_backup_rpo_certification": 15811,
    "pg_resource_governance_pgbouncer_connection_budget": 15821,
    "pg_resource_governance_container_cpu_budget": 15831,
    "pg_system_failure_checkpoint_archive": 15841,
    "pg_business_change_lwlock_pgbouncer_cascade": 15851,
    "pg_resource_governance_partition_cleanup": 15861,
    "pg_resource_governance_io_context_workload": 15871,
}
_TIDB_SYSTEM_FAILURE_PORT_BLOCK_SIZE = 32
_TIDB_PERSISTENT_STORAGE_SCRIPTS = frozenset({
    "run_tidb_business_change_rolling_upgrade_scenario.py",
})


FORMAL_SCENARIOS = tuple(
    registration
    for registration in SCENARIO_REGISTRY
    if registration.entrypoint is not None
)
FORMAL_SCENARIOS_BY_ID = {
    registration.scenario_id: registration
    for registration in FORMAL_SCENARIOS
}


def select_registrations(systems, categories, scenario_ids):
    requested = set(scenario_ids)
    selected = tuple(
        registration
        for registration in FORMAL_SCENARIOS
        if registration.system in systems
        and registration.category in categories
        and (not requested or registration.scenario_id in requested)
    )
    missing = requested - {registration.scenario_id for registration in selected}
    if missing:
        raise ValueError(
            "Unknown scenarios for selected systems/categories: "
            + ", ".join(sorted(missing))
        )
    if not selected:
        raise ValueError(
            "Benchmark selection contains no formal scenarios: "
            f"systems={[system.value for system in systems]}, "
            f"categories={[category.value for category in categories]}"
        )
    return selected


def _history_case_for_spec(spec: BoundedScenarioRunSpec):
    registrations = [item for item in SCENARIO_REGISTRY if item.scenario_id == spec.scenario_id]
    if len(registrations) != 1:
        raise ValueError(
            "RunSpec must resolve to exactly one registered scenario: "
            f"scenario_id={spec.scenario_id!r}, matches={len(registrations)}"
        )
    cases = [case for case in registrations[0].scenario.cases if case.case_id == spec.case_id]
    if len(cases) != 1:
        raise ValueError(
            "RunSpec must resolve to exactly one registered case: "
            f"scenario_id={spec.scenario_id!r}, case_id={spec.case_id!r}, matches={len(cases)}"
        )
    return cases[0] if getattr(cases[0], "frozen_history", None) is not None else None


def plan_bounded_scenario_runs(manifest: ExperimentManifest) -> list[BoundedScenarioRunSpec]:
    selected = select_registrations(
        manifest.benchmark.systems,
        manifest.benchmark.categories,
        manifest.benchmark.scenarios,
    )
    runs = []
    matched_exclusions = set()
    index = 0
    for registration in selected:
        if registration.system is DatabaseSystem.TIDB:
            port_stride = (
                _TIDB_SYSTEM_FAILURE_PORT_BLOCK_SIZE
                if registration.category.value == "system_failure"
                else 10
            )
        else:
            port_stride = 1
        scenario = registration.scenario
        for case in scenario.cases:
            for agent in manifest.agents:
                cell = (scenario.scenario_id, case.case_id, agent.id)
                if cell in manifest.exclude_cells:
                    matched_exclusions.add(cell)
                    continue
                for repetition, seed in enumerate(manifest.seeds, start=1):
                    run_id = "__".join((
                        manifest.experiment_id,
                        scenario.scenario_id,
                        case.case_id,
                        agent.id,
                        f"r{repetition:03d}",
                    ))
                    runs.append(BoundedScenarioRunSpec(
                        experiment_id=manifest.experiment_id,
                        run_id=run_id,
                        system=registration.system,
                        scenario_id=scenario.scenario_id,
                        script=registration.entrypoint,
                        category=registration.category.value,
                        case_id=case.case_id,
                        agent=agent,
                        repetition=repetition,
                        seed=seed,
                        port=manifest.runtime.port_base + index * port_stride,
                        resources=case.runtime.resources,
                        host_ports=case.runtime.host_ports,
                    ))
                    index += 1
    unmatched_exclusions = manifest.exclude_cells - matched_exclusions
    if unmatched_exclusions:
        details = ", ".join("/".join(cell) for cell in sorted(unmatched_exclusions))
        raise ValueError(f"manifest.exclude_cells did not match planned cells: {details}")
    if not runs:
        raise ValueError("Scenario benchmark plan contains no runs")
    return runs


def build_scenario_command(
    spec: BoundedScenarioRunSpec,
    manifest: ExperimentManifest,
    project_root: Path,
    *,
    attempt: int | None = None,
):
    script_path = project_root / "examples" / spec.script
    options = script_options(script_path)
    command = [sys.executable, str(script_path)]
    relayed = spec.agent.mode in {"human", "remote"}
    execution_mode = (
        "llm" if relayed or spec.agent.mode in {"dbot", "dbaiops"} else spec.agent.mode
    )
    if "--mode" in options:
        command.extend(["--mode", execution_mode])
    elif "--agent" in options:
        command.extend(["--agent", execution_mode if relayed else spec.agent.mode])
    else:
        raise ValueError(
            f"Scenario script {spec.script} must expose --mode or --agent for benchmark execution"
        )
    runtime_data = manifest.raw.get("runtime")
    has_explicit_port_base = isinstance(runtime_data, dict) and "port_base" in runtime_data
    # PG-RG-IO01 validates a fixed port range internally.  It therefore owns
    # that range for serial execution even when a manifest has a generic base.
    if spec.scenario_id == "pg_resource_governance_io_context_workload" and manifest.runtime.concurrency == 1:
        port = SCENARIO_PORT_BASES[spec.scenario_id]
    else:
        port = spec.port if has_explicit_port_base else SCENARIO_PORT_BASES.get(spec.scenario_id, spec.port)
    if "--port" in options:
        command.extend(["--port", str(port)])
        if "--pgbouncer-port" in options:
            # RG1 keeps the shared PostgreSQL endpoint fixed but must isolate
            # the externally published PgBouncer endpoint across worktrees.
            command.extend(["--pgbouncer-port", str(spec.port + 1)])
        if "--aux-port" in options:
            command.extend(["--aux-port", str(port + 1)])
        if "--monitoring-port" in options:
            command.extend(["--monitoring-port", str(port + 1)])
    elif "--primary-port" in options:
        command.extend(["--primary-port", str(port)])
        if "--restore-port" in options:
            command.extend(["--restore-port", str(port + 1)])
    else:
        raise ValueError(
            f"Scenario script {spec.script} must expose --port or "
            "the --primary-port/--restore-port pair"
        )
    if "--container-name" in options:
        container_run_id = spec.run_id
        if attempt is not None:
            container_run_id = f"{container_run_id}-a{attempt:03d}"
        command.extend([
            "--container-name",
            container_name(manifest.runtime.container_prefix, container_run_id),
        ])
    if "--case" not in options:
        raise ValueError(f"Scenario script {spec.script} must expose --case")
    command.extend(["--case", spec.case_id])
    history_case = _history_case_for_spec(spec)
    if history_case is not None:
        if "--seed" not in options:
            raise ValueError(
                f"Frozen history scenario script {spec.script} must expose explicit --seed"
            )
        command.extend(["--seed", str(spec.seed)])
    if spec.agent.mode in {"human", "remote", "llm", "dbot", "dbaiops"}:
        # Relayed agents never resolve an LLM config; --model only labels the run.
        if spec.agent.mode == "human":
            command.extend(["--model", "human"])
        elif spec.agent.mode == "remote":
            command.extend(["--model", spec.agent.model or "remote"])
        elif spec.agent.model:
            command.extend(["--model", spec.agent.model])
        config_option = next(
            (option for option in ("--llm-config", "--config-path", "--config") if option in options),
            None,
        )
        if config_option:
            command.extend([config_option, manifest.runtime.llm_config])
        if "--max-turns" in options and spec.agent.mode != "human":
            command.extend(["--max-turns", str(spec.agent.max_turns)])
        if "--reasoning-effort" in options and not relayed:
            command.extend(["--reasoning-effort", spec.agent.reasoning_effort or "xhigh"])
        if spec.agent.max_output_tokens is not None:
            if "--max-output-tokens" not in options:
                raise ValueError(
                    f"Scenario script {spec.script} must expose --max-output-tokens "
                    "when the manifest sets agent.max_output_tokens"
                )
            command.extend(["--max-output-tokens", str(spec.agent.max_output_tokens)])
    if "--fault-snapshot-mode" in options:
        command.extend(["--fault-snapshot-mode", manifest.runtime.fault_snapshot])
    elif manifest.runtime.fault_snapshot in {"save", "use"}:
        raise ValueError(
            f"Scenario script {spec.script} must expose --fault-snapshot-mode for "
            f"fault_snapshot={manifest.runtime.fault_snapshot!r}"
        )
    persistent_storage_enabled = spec.script in _TIDB_PERSISTENT_STORAGE_SCRIPTS
    if persistent_storage_enabled and manifest.runtime.tidb_storage_key is not None and "--storage-key" in options:
        command.extend(["--storage-key", manifest.runtime.tidb_storage_key])
    if persistent_storage_enabled and manifest.runtime.tidb_storage_root is not None and "--storage-root" in options:
        command.extend(["--storage-root", manifest.runtime.tidb_storage_root])
    if "--cold-start-timeout" in options:
        cold_start_timeout = (
            manifest.runtime.tidb_cold_start_timeout_sec
            if spec.system is DatabaseSystem.TIDB
            else manifest.runtime.postgres_cold_start_timeout_sec
        )
        command.extend(["--cold-start-timeout", str(cold_start_timeout)])
    if "--diagnosis-match-mode" in options:
        command.extend(["--diagnosis-match-mode", manifest.runtime.diagnosis_match_mode])
        if manifest.runtime.diagnosis_match_mode == "semantic":
            command.extend([
                "--diagnosis-semantic-model",
                manifest.runtime.diagnosis_semantic_model,
                "--diagnosis-semantic-config",
                manifest.runtime.llm_config,
            ])
    if "--warm-start-timeout" in options:
        command.extend(["--warm-start-timeout", str(manifest.runtime.tidb_warm_start_timeout_sec)])
    return command


def validate_scenario_target(spec: BoundedScenarioRunSpec, manifest: ExperimentManifest) -> None:
    case = _history_case_for_spec(spec)
    if case is not None:
        if manifest.runtime.fault_snapshot != "off":
            raise ValueError(
                "Frozen-history history Cases require manifest.runtime.fault_snapshot='off': "
                f"scenario={spec.scenario_id!r}, case={spec.case_id!r}, "
                f"fault_snapshot={manifest.runtime.fault_snapshot!r}"
            )
        history = case.frozen_history
        catalog = metric_catalog_for_system(spec.system)
        # Scenario-owned catalogs are validated by the environment;
        # runner preflight only needs lookbacks known to the shared catalog.
        known_lookbacks = [
            float(catalog.definition(metric).lookback_seconds)
            for metric in history.required_metrics
            if metric in catalog.metric_names
        ]
        warmup = max(
            float(case.background_workload.warmup_seconds),
            max(known_lookbacks, default=0.0),
        )
        startup_budget = (
            manifest.runtime.tidb_cold_start_timeout_sec
            if spec.system is DatabaseSystem.TIDB
            else manifest.runtime.postgres_cold_start_timeout_sec
        )
        minimum_timeout = int(
            startup_budget
            + warmup
            + history.normal_capture_seconds
            + history.fault_capture_seconds
            + 120
        )
        if manifest.runtime.timeout_seconds < minimum_timeout:
            raise ValueError(
                "Experiment timeout does not cover frozen-history deployment, captures, and Agent execution: "
                f"scenario={spec.scenario_id!r}, case={spec.case_id!r}, "
                f"timeout_seconds={manifest.runtime.timeout_seconds}, minimum_timeout_seconds={minimum_timeout}"
            )


def assert_fault_snapshots_exist(specs: list[BoundedScenarioRunSpec]) -> dict[str, str]:
    from src.database.system import DatabaseSystem
    from src.scenarios import SCENARIOS_BY_ID
    from src.execution.environments.postgres import PGEnv
    from src.execution.environments.tidb import TiDBEnv

    snapshots = {}
    snapshot_environments = {}
    for scenario_id, case_id in sorted({
        (spec.scenario_id, spec.case_id)
        for spec in specs
    }):
        registration = SCENARIOS_BY_ID[scenario_id]
        scenario = registration.scenario
        case = scenario.get_case(case_id)
        if registration.system is DatabaseSystem.POSTGRESQL:
            env = PGEnv()
        elif registration.system is DatabaseSystem.TIDB:
            image_group_key = case.runtime.image_group_key
            if image_group_key is None:
                raise ValueError(
                    f"TiDB fault snapshot requires an image_group_key: "
                    f"scenario={scenario_id!r}, case={case_id!r}"
                )
            env = TiDBEnv(
                run_id=f"snapshot-check-{scenario_id}-{case_id}",
                image_group_key=image_group_key,
            )
            env.configure_case(case)
        else:
            raise ValueError(
                f"Fault snapshots are unavailable for system={registration.system.value!r}, "
                f"scenario={scenario_id!r}, case={case_id!r}"
            )
        snapshot_name = env.snapshot_name(scenario_id, case)
        if snapshot_name is None:
            raise ValueError(
                f"Fault snapshot identity is unavailable: scenario={scenario_id!r}, case={case_id!r}"
            )
        key = f"{scenario_id}/{case_id}"
        snapshots[key] = snapshot_name
        snapshot_environments[key] = env
    missing = {
        scenario_id: snapshot_name
        for scenario_id, snapshot_name in snapshots.items()
        if not snapshot_environments[scenario_id].snapshot_exists(snapshot_name)
    }
    if missing:
        details = ", ".join(
            f"{scenario_id}={snapshot_name}"
            for scenario_id, snapshot_name in missing.items()
        )
        raise RuntimeError(
            "fault_snapshot='use' requires every fault snapshot to exist before execution; "
            f"missing: {details}"
        )
    return snapshots
