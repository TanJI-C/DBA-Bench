from __future__ import annotations

import hashlib
import json
import os
import pytest
import signal
import subprocess
import sys
import threading
import time
from collections import Counter

from src.scenarios import ALL_SCENARIOS, SCENARIO_REGISTRY, ScenarioCategory
from src.scenarios.base import CaseResourceSpec, DatabaseSystem
from src.benchmark.aggregate import aggregate
from src.benchmark.isolation import (
    HOST_EXCLUSIVE_SCENARIOS,
    allocate_workers,
    assert_fault_snapshots_exist,
    derive_worker_demand,
    expand_linux_set,
    requires_host_exclusive,
)
from src.benchmark.manifest import load_manifest
from src.benchmark.models import (
    AgentSpec,
    IsolationDemandSpec,
    IsolationPolicySpec,
    RunRecord,
    BoundedScenarioRunSpec,
    WorkerAllocation,
)
from src.benchmark.planner import plan_runs, select_specs
from src.benchmark.runner import (
    ExperimentRunner,
    _classify_process_failure,
    build_command,
    container_name,
    environment_snapshot,
    validate_execution_plan,
)
from src.benchmark.store import ExperimentStore
from src.execution.deployment import PGDockerDeployment


def test_runner_timeout_interrupts_before_escalating(monkeypatch):
    signals = []

    class Process:
        pid = 1234

        def __init__(self):
            self.wait_calls = 0

        def wait(self, timeout=None):
            self.wait_calls += 1
            if self.wait_calls == 1:
                raise subprocess.TimeoutExpired("persistent-scenario", timeout)
            return -signal.SIGTERM

    process = Process()
    monkeypatch.setattr(
        "src.benchmark.runner.os.killpg",
        lambda pid, signum: signals.append((pid, signum)),
    )

    ExperimentRunner._terminate_process_group(process, grace_seconds=1)

    assert signals == [(1234, signal.SIGINT), (1234, signal.SIGTERM)]
    assert process.wait_calls == 2


def _write_fake_topology(tmp_path):
    sys_root = tmp_path / "sys"
    cpu_layout = (
        (0, 0, 0, 0, "0,2"),
        (2, 0, 0, 0, "0,2"),
        (1, 0, 1, 0, "1,3"),
        (3, 0, 1, 0, "1,3"),
        (4, 1, 0, 1, "4,6"),
        (6, 1, 0, 1, "4,6"),
        (5, 1, 1, 1, "5,7"),
        (7, 1, 1, 1, "5,7"),
    )
    for cpu, socket, core, node, siblings in cpu_layout:
        cpu_root = sys_root / f"devices/system/cpu/cpu{cpu}"
        topology = cpu_root / "topology"
        topology.mkdir(parents=True)
        (topology / "physical_package_id").write_text(f"{socket}\n", encoding="utf-8")
        (topology / "core_id").write_text(f"{core}\n", encoding="utf-8")
        (topology / "thread_siblings_list").write_text(f"{siblings}\n", encoding="utf-8")
        (cpu_root / f"node{node}").mkdir()
    for node in (0, 1):
        node_root = sys_root / f"devices/system/node/node{node}"
        node_root.mkdir(parents=True)
        (node_root / "meminfo").write_text(
            f"Node {node} MemTotal:       8388608 kB\n"
            f"Node {node} MemFree:        2097152 kB\n"
            f"Node {node} FilePages:      2097152 kB\n"
            f"Node {node} SReclaimable:    524288 kB\n"
            f"Node {node} Shmem:            65536 kB\n",
            encoding="utf-8",
        )
    return sys_root


def _test_workers():
    return (
        WorkerAllocation(
            id="worker-01",
            physical_cores=("socket0/core0",),
            cpuset_cpus="0,2",
            cpuset_mems="0",
            cpu_capacity=1.0,
            memory_capacity_mb=512,
        ),
        WorkerAllocation(
            id="worker-02",
            physical_cores=("socket1/core0",),
            cpuset_cpus="4,6",
            cpuset_mems="1",
            cpu_capacity=1.0,
            memory_capacity_mb=512,
        ),
    )


def test_postgresql_catalog_matches_five_task_categories():
    query_perf_ids = {
        registration.scenario_id
        for registration in SCENARIO_REGISTRY
        if registration.system is DatabaseSystem.POSTGRESQL
        and registration.category is ScenarioCategory.QUERY_PERF
    }
    system_failure_ids = {
        registration.scenario_id
        for registration in SCENARIO_REGISTRY
        if registration.system is DatabaseSystem.POSTGRESQL
        and registration.category is ScenarioCategory.SYSTEM_FAILURE
    }

    assert len(query_perf_ids) == 9
    assert len(system_failure_ids) == 16
    assert {
        "pg_system_failure_lock_contention",
        "pg_system_failure_auto_analyze_storm",
    } <= system_failure_ids
    assert not {
        "pg_system_failure_lock_contention",
        "pg_system_failure_auto_analyze_storm",
    } & query_perf_ids


def test_manifest_plans_stable_run_matrix(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: pilot
benchmark:
  systems: [postgresql]
  categories: [query_perf]
  scenarios: [pg_query_perf_missing_index]
agents:
  - id: mock
    mode: mock
repetitions: 2
seeds: [11, 22]
runtime:
  port_base: 19000
""".strip(),
        encoding="utf-8",
    )

    runs = plan_runs(load_manifest(manifest_path))

    assert [run.run_id for run in runs] == [
        "pilot__pg_query_perf_missing_index__product_category_substring__mock__r001",
        "pilot__pg_query_perf_missing_index__product_category_substring__mock__r002",
        "pilot__pg_query_perf_missing_index__product_category_prefix_simple__mock__r001",
        "pilot__pg_query_perf_missing_index__product_category_prefix_simple__mock__r002",
    ]
    assert [run.case_id for run in runs] == [
        "product_category_substring",
        "product_category_substring",
        "product_category_prefix_simple",
        "product_category_prefix_simple",
    ]
    assert [run.seed for run in runs] == [11, 22, 11, 22]
    assert [run.port for run in runs] == [19000, 19001, 19002, 19003]


def test_tidb_manifest_reserves_a_port_block_per_run(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: tidb-pilot
benchmark:
  systems: [tidb]
  categories: [resource_governance]
  scenarios: [tidb_resource_governance_ru_budget_calibration]
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime:
  port_base: 19000
""".strip(),
        encoding="utf-8",
    )

    runs = plan_runs(load_manifest(manifest_path))

    assert [run.port for run in runs] == [19000, 19010]


def test_manifest_accepts_postgres_cold_start_timeout(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: pg-timeout
benchmark: {systems: [postgresql], categories: [health_check], scenarios: [pg_health_check_autovacuum_sustainability]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime:
  postgres_cold_start_timeout_sec: 777
""".strip(),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)

    assert manifest.runtime.postgres_cold_start_timeout_sec == 777


def test_manifest_and_runner_expose_semantic_diagnosis_configuration(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: pg-semantic-dp
benchmark: {systems: [postgresql], categories: [health_check], scenarios: [pg_health_check_autovacuum_sustainability]}
agents: [{id: agent-a, mode: llm, model: test-model-a}]
repetitions: 1
seeds: [11]
runtime:
  diagnosis_match_mode: semantic
  diagnosis_semantic_model: test-model-a
  llm_config: config/llm_config.json
""".strip(),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)
    run = plan_runs(manifest)[0]
    command = build_command(run, manifest)

    assert manifest.runtime.diagnosis_match_mode == "semantic"
    assert command[command.index("--diagnosis-match-mode") + 1] == "semantic"
    assert command[command.index("--diagnosis-semantic-model") + 1] == "test-model-a"


def test_serial_io_context_run_uses_its_reserved_port_range(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: pg-io-port
benchmark: {systems: [postgresql], categories: [resource_governance], scenarios: [pg_resource_governance_io_context_workload]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime: {port_base: 41000, fault_snapshot: "off"}
""".strip(),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)
    command = build_command(plan_runs(manifest)[0], manifest)

    assert command[command.index("--port") + 1] == "15871"
    assert command[command.index("--monitoring-port") + 1] == "15872"


def test_tidb_manifest_allocates_non_overlapping_port_blocks(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: tidb-port-blocks
benchmark:
  systems: [tidb]
  categories: [business_change]
  scenarios:
    - tidb_business_change_rolling_upgrade
    - tidb_business_change_cdc_dc_migration
agents: [{id: mock, mode: mock}]
exclude_cells:
  - {scenario: tidb_business_change_rolling_upgrade, case: rolling_upgrade_6_5_to_7_5, agent: mock}
  - {scenario: tidb_business_change_cdc_dc_migration, case: cdc_dc_migration_reverse_cutover, agent: mock}
repetitions: 1
seeds: [11]
runtime: {port_base: 20000, fault_snapshot: "off"}
""".strip(),
        encoding="utf-8",
    )

    runs = plan_runs(load_manifest(manifest_path))

    ports_by_case = {run.case_id: run.port for run in runs}
    assert ports_by_case == {
        "cdc_dc_migration_reverse_direction": 20000,
        "rolling_upgrade_7_5_to_8_1": 20010,
    }


def test_manifest_excludes_one_exact_cell(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: main
benchmark:
  systems: [postgresql]
  categories: [query_perf]
  scenarios: [pg_query_perf_missing_index]
agents:
  - {id: pilot, mode: mock}
  - {id: other, mode: mock}
exclude_cells:
  - scenario: pg_query_perf_missing_index
    case: product_category_substring
    agent: pilot
repetitions: 1
seeds: [11]
""".strip(),
        encoding="utf-8",
    )

    runs = plan_runs(load_manifest(manifest_path))

    assert [(run.agent.id, run.scenario_id, run.case_id) for run in runs] == [
        ("other", "pg_query_perf_missing_index", "product_category_substring"),
        ("pilot", "pg_query_perf_missing_index", "product_category_prefix_simple"),
        ("other", "pg_query_perf_missing_index", "product_category_prefix_simple"),
    ]


def test_manifest_rejects_unmatched_excluded_cell(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: main
benchmark: {systems: [postgresql], categories: [query_perf], scenarios: [pg_query_perf_missing_index]}
agents: [{id: mock, mode: mock}]
exclude_cells:
  - scenario: pg_query_perf_missing_index
    case: wrong_case
    agent: mock
repetitions: 1
seeds: [11]
""".strip(),
        encoding="utf-8",
    )

    try:
        plan_runs(load_manifest(manifest_path))
    except ValueError as exc:
        assert "wrong_case" in str(exc)
    else:
        raise AssertionError("unmatched excluded cells must fail planning")


def test_manifest_rejects_legacy_agent_scenario_filter(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: invalid
benchmark: {systems: [postgresql], categories: [query_perf], scenarios: [pg_query_perf_missing_index]}
agents:
  - id: mock
    mode: mock
    scenarios: [pg_query_perf_missing_index]
""".strip(),
        encoding="utf-8",
    )

    try:
        load_manifest(manifest_path)
    except ValueError as exc:
        assert "unknown fields" in str(exc)
        assert "scenarios" in str(exc)
    else:
        raise AssertionError("legacy agent scenario filters must fail explicitly")


def test_select_specs_keeps_only_requested_run_ids(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: exact-rerun
benchmark: {systems: [postgresql], categories: [query_perf], scenarios: [pg_query_perf_missing_index]}
agents:
  - {id: first, mode: mock}
  - {id: second, mode: mock}
repetitions: 1
seeds: [11]
""".strip(),
        encoding="utf-8",
    )
    specs = plan_runs(load_manifest(manifest_path))

    selected = select_specs(specs, [specs[1].run_id])

    assert selected == [specs[1]]
    for run_ids, expected in ((["missing-run"], "missing-run"), ([specs[0].run_id] * 2, "Duplicate")):
        try:
            select_specs(specs, run_ids)
        except ValueError as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(f"invalid exact rerun ids must fail: {run_ids}")


def test_manifest_rejects_seed_count_mismatch(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: invalid
benchmark: {systems: [postgresql], categories: [query_perf], scenarios: all}
agents: [{id: mock, mode: mock}]
repetitions: 2
seeds: [11]
""".strip(),
        encoding="utf-8",
    )

    try:
        load_manifest(manifest_path)
    except ValueError as exc:
        assert "exactly 2" in str(exc)
    else:
        raise AssertionError("seed count mismatch must fail")


def test_runner_passes_planned_case_to_scenario_entrypoint(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: smoke
benchmark: {systems: [postgresql], categories: [system_failure], scenarios: [pg_system_failure_deadlock]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime: {fault_snapshot: use}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    spec = plan_runs(manifest)[0]

    command = build_command(spec, manifest)

    case_index = command.index("--case")
    assert command[case_index + 1] == "checkout_order_deadlock"


def test_runner_maps_backup_entrypoint_to_primary_and_restore_ports(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: backup-ports
benchmark: {systems: [postgresql], categories: [health_check], scenarios: [pg_health_check_backup_rpo_certification]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime: {port_base: 19000, fault_snapshot: "off"}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    command = build_command(plan_runs(manifest)[0], manifest)

    assert command[command.index("--primary-port") + 1] == "19000"
    assert command[command.index("--restore-port") + 1] == "19001"
    assert "--port" not in command


def test_runner_honors_explicit_postgres_port_base_for_isolated_worktree(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: isolated-checkpoint-archive
benchmark: {systems: [postgresql], categories: [system_failure], scenarios: [pg_system_failure_checkpoint_archive]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime: {port_base: 29641, fault_snapshot: "off"}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    command = build_command(plan_runs(manifest)[0], manifest)

    assert command[command.index("--port") + 1] == "29641"
    assert "--primary-port" not in command


def test_runner_uses_reserved_scenario_ports_and_optional_arguments(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: reserved-ports
benchmark: {systems: [postgresql], categories: [resource_governance], scenarios: [pg_resource_governance_container_cpu_budget]}
agents: [{id: mock, mode: mock}]
exclude_cells:
  - {scenario: pg_resource_governance_container_cpu_budget, case: db_quota_throttle, agent: mock}
repetitions: 1
seeds: [11]
runtime: {port_base: 24000, fault_snapshot: "off"}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    spec = plan_runs(manifest)[0]
    command = build_command(spec, manifest)

    assert command[command.index("--port") + 1] == "24000"
    assert command[command.index("--aux-port") + 1] == "24001"
    assert command[command.index("--seed") + 1] == "11"
    container_index = command.index("--container-name")
    assert command[container_index + 1] == container_name(manifest.runtime.container_prefix, spec.run_id)


def test_runner_isolates_container_names_between_attempts(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: attempt-container
benchmark: {systems: [postgresql], categories: [system_failure], scenarios: [pg_system_failure_checkpoint_archive]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime: {fault_snapshot: "off"}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    spec = plan_runs(manifest)[0]

    first = build_command(spec, manifest, attempt=1)
    second = build_command(spec, manifest, attempt=2)

    first_name = first[first.index("--container-name") + 1]
    second_name = second[second.index("--container-name") + 1]
    assert first_name != second_name


def test_runner_preflight_uses_case_metric_catalog_extensions(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: checkpoint-archive-frozen-history-preflight
benchmark:
  systems: [postgresql]
  categories: [system_failure]
  scenarios: [pg_system_failure_checkpoint_archive]
agents: [{id: agent-a, mode: llm, model: test-model-a, max_turns: 30}]
repetitions: 1
seeds: [20260819]
runtime:
  timeout_seconds: 3600
  fault_snapshot: "off"
  llm_config: config/llm_config.json
""".strip(),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)
    specs = plan_runs(manifest)

    assert validate_execution_plan(manifest, specs) == ()


def test_runner_maps_baseline_agent_mode_to_real_llm_entrypoint(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: dbot-pilot
benchmark: {systems: [postgresql], categories: [query_perf], scenarios: [pg_query_perf_missing_index]}
agents:
  - id: dbot-agent-a
    mode: dbot
    model: test-model-a
    settings: {frozen: true}
repetitions: 1
seeds: [20260718]
runtime: {fault_snapshot: use}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    spec = plan_runs(manifest)[0]

    command = build_command(spec, manifest)

    assert command[command.index("--mode") + 1] == "llm"
    assert command[command.index("--model") + 1] == "test-model-a"
    assert spec.agent.mode == "dbot"
    assert spec.agent.settings == {"frozen": True}


def test_runner_uses_image_group_mode_for_qp07_entrypoint(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: qp07-persistent
benchmark:
  systems: [tidb]
  categories: [query_perf]
  scenarios: [tidb_query_perf_like_escape_range]
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime:
  fault_snapshot: auto
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    command = build_command(plan_runs(manifest)[0], manifest)

    assert command[command.index("--fault-snapshot-mode") + 1] == "auto"
    assert "--storage-key" not in command
    assert "--storage-root" not in command


def test_runner_scopes_tidb_persistent_storage_to_rolling_upgrade(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: storage-scope
benchmark:
  systems: [tidb]
  categories: [business_change]
  scenarios:
    - tidb_business_change_rolling_upgrade
    - tidb_business_change_large_table_batch_dml
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime:
  fault_snapshot: "off"
  tidb_storage_key: storage-scope
  tidb_storage_root: /tmp/aiopsbench-storage
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    specs = plan_runs(manifest)
    commands = {spec.case_id: build_command(spec, manifest) for spec in specs}

    rolling = commands["rolling_upgrade_6_5_to_7_5"]
    large_table = commands["large_table_batch_update_and_index"]
    assert rolling[rolling.index("--storage-key") + 1] == "storage-scope"
    assert rolling[rolling.index("--storage-root") + 1] == "/tmp/aiopsbench-storage"
    assert "--storage-key" not in large_table
    assert "--storage-root" not in large_table


def test_runner_passes_agent_output_token_limit_to_scenario_entrypoint(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: output-limit
benchmark: {systems: [tidb], categories: [system_failure], scenarios: [tidb_system_failure_br_permission]}
agents:
  - id: test-agent
    mode: llm
    model: test-model-b
    max_turns: 30
    max_output_tokens: 2048
repetitions: 1
seeds: [20260802]
runtime: {port_base: 14700, fault_snapshot: "off", llm_config: config/llm_config.json}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    command = build_command(plan_runs(manifest)[0], manifest)

    index = command.index("--max-output-tokens")
    assert command[index + 1] == "2048"


def test_frozen_history_plan_accepts_scenario_owned_metric_catalog(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: rg2-frozen-history
benchmark:
  systems: [postgresql]
  categories: [resource_governance]
  scenarios: [pg_resource_governance_container_cpu_budget]
agents: [{id: mock, mode: mock}]
exclude_cells:
  - {scenario: pg_resource_governance_container_cpu_budget, case: db_quota_throttle, agent: mock}
repetitions: 1
seeds: [20260819]
runtime: {fault_snapshot: "off"}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    specs = plan_runs(manifest)

    assert validate_execution_plan(manifest, specs) == ()
    command = build_command(specs[0], manifest)
    seed_index = command.index("--seed")
    assert command[seed_index + 1] == "20260819"


def test_rg2_llm_command_pins_model_xhigh(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: rg2-agent-a
benchmark:
  systems: [postgresql]
  categories: [resource_governance]
  scenarios: [pg_resource_governance_container_cpu_budget]
agents: [{id: agent-a, mode: llm, model: test-model-a}]
repetitions: 1
seeds: [20260819]
runtime: {fault_snapshot: "off"}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    command = build_command(plan_runs(manifest)[0], manifest)

    model_index = command.index("--model")
    reasoning_index = command.index("--reasoning-effort")
    assert command[model_index + 1] == "test-model-a"
    assert command[reasoning_index + 1] == "xhigh"


def test_bounded_llm_command_honors_explicit_reasoning_effort(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: explicit-medium
benchmark:
  systems: [postgresql]
  categories: [health_check]
  scenarios: [pg_health_check_autovacuum_sustainability]
agents:
  - id: sol
    mode: llm
    model: test-model-d
    reasoning_effort: medium
repetitions: 1
seeds: [20260904]
runtime: {fault_snapshot: "off"}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    command = build_command(plan_runs(manifest)[0], manifest)

    reasoning_index = command.index("--reasoning-effort")
    assert command[reasoning_index + 1] == "medium"


def test_pg_readiness_requires_application_database_round_trip(monkeypatch):
    deployment = PGDockerDeployment(container_name="readiness-test")
    sql_ready = iter((False, True))
    monkeypatch.setattr(deployment, "is_ready", lambda: True)
    monkeypatch.setattr(deployment, "_sql_ready", lambda: next(sql_ready))
    monkeypatch.setattr("src.execution.deployment.time.sleep", lambda _: None)

    assert deployment.wait_for_ready(timeout=1) is True


def test_pg_sql_readiness_treats_docker_timeout_as_not_ready(monkeypatch):
    deployment = PGDockerDeployment(container_name="readiness-timeout-test")

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="docker exec", timeout=10)

    monkeypatch.setattr("src.execution.deployment.subprocess.run", raise_timeout)

    assert deployment._sql_ready() is False


def test_container_name_keeps_long_run_ids_unique():
    common = "experiment__scenario__case__" + "x" * 120

    first = container_name("aiopsbench", common + "__agent_a__r001")
    second = container_name("aiopsbench", common + "__agent_b__r001")

    assert len(first) == 120
    assert len(second) == 120
    assert first != second


@pytest.mark.skipif(
    os.cpu_count() is not None and os.cpu_count() < 26,
    reason="kernel affinity fixture pins CPUs 24-25",
)
def test_bound_process_wrapper_records_kernel_affinity(tmp_path):
    audit_path = tmp_path / "process-runtime.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/exec_bound_process.py",
            "--cpuset-cpus",
            "24-25",
            "--audit-path",
            str(audit_path),
            "--",
            sys.executable,
            "-c",
            "import os; assert sorted(os.sched_getaffinity(0)) == [24, 25]",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == ""
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["affinity_matches"] is True
    assert audit["observed_affinity_cpus"] == [24, 25]


def test_environment_snapshot_preserves_external_llm_config_path(tmp_path, monkeypatch):
    config = tmp_path / "llm_config.json"
    config.write_text('{"test-model-a": {"api_key": "secret"}}', encoding="utf-8")
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        "experiment_id: snapshot\n"
        "benchmark: {systems: [postgresql], categories: [business_change], scenarios: [pg_business_change_online_ddl]}\n"
        "agents: [{id: agent-a, mode: llm, model: test-model-a}]\n"
        "repetitions: 1\nseeds: [1]\n"
        f"runtime:\n  llm_config: {config}\n",
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)

    def fake_check_output(command, **kwargs):
        if command[:2] == ["git", "diff"]:
            return b""
        if command[:2] == ["git", "status"]:
            return ""
        if command[:2] == ["git", "rev-parse"]:
            return "abc123\n"
        if command[0] == "docker":
            return "27.4.0\n"
        return "package==1.0\n"

    monkeypatch.setattr("src.benchmark.runner.subprocess.check_output", fake_check_output)
    snapshot = environment_snapshot(manifest, ())
    assert snapshot["llm_config_path"] == str(config)
    assert snapshot["llm_config_sha256"] == hashlib.sha256(config.read_bytes()).hexdigest()


def test_parallel_manifest_requires_isolation_policy(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: invalid
benchmark: {systems: [postgresql], categories: [system_failure], scenarios: [pg_system_failure_deadlock]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime: {concurrency: 2, fault_snapshot: auto}
""".strip(),
        encoding="utf-8",
    )

    try:
        load_manifest(manifest_path)
    except ValueError as exc:
        assert "isolation NUMA policy" in str(exc)
    else:
        raise AssertionError("parallel experiments must require an isolation policy")


def test_parallel_manifest_rejects_fixed_isolation_slots(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: invalid
benchmark: {systems: [postgresql], categories: [system_failure], scenarios: [pg_system_failure_deadlock]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime:
  concurrency: 2
  fault_snapshot: use
  isolation:
    slots:
      - {id: pg-a, cpuset_cpus: "0-1", cpuset_mems: "0"}
      - {id: pg-b, cpuset_cpus: "1-2", cpuset_mems: "1"}
""".strip(),
        encoding="utf-8",
    )

    try:
        load_manifest(manifest_path)
    except ValueError as exc:
        assert "must contain exactly" in str(exc)
        assert "slots" in str(exc)
    else:
        raise AssertionError("fixed isolation slots are not part of the resource-demand schema")


def test_linux_cpu_set_parser_and_resource_policy():
    assert expand_linux_set("0-2,8", "test") == {0, 1, 2, 8}
    spec = BoundedScenarioRunSpec(
        experiment_id="pilot",
        run_id="oom",
        system=DatabaseSystem.POSTGRESQL,
        scenario_id="pg_system_failure_oom",
        script="scenario.py",
        category="system_failure",
        case_id="default",
        agent=AgentSpec(id="mock", mode="mock"),
        repetition=1,
        seed=11,
        port=19000,
    )
    assert requires_host_exclusive(spec) is True


def test_postgres_resource_contract_rejects_container_quota_above_worker_reservation():
    try:
        CaseResourceSpec(
            worker_physical_cores=1,
            worker_memory_mb=256,
            container_cpu_limit=2.0,
            container_memory_mb=512,
        )
    except ValueError as exc:
        assert "Worker CPU reservation" in str(exc)
    else:
        raise AssertionError("container quota must fit inside its worker reservation")


def test_dynamic_worker_allocator_uses_complete_cores_and_separate_numa(tmp_path):
    workers = allocate_workers(
        IsolationDemandSpec(
            physical_cores_per_worker=1,
            memory_mb_per_worker=512,
            numa_policy="separate",
        ),
        worker_count=2,
        sys_root=_write_fake_topology(tmp_path),
        allowed_cpus=set(range(8)),
    )

    assert workers == _test_workers()


def test_dynamic_worker_allocator_allows_one_worker_to_span_numa_nodes(tmp_path):
    workers = allocate_workers(
        IsolationDemandSpec(
            physical_cores_per_worker=3,
            memory_mb_per_worker=512,
            numa_policy="local",
        ),
        worker_count=1,
        sys_root=_write_fake_topology(tmp_path),
        allowed_cpus=set(range(8)),
    )

    assert len(workers[0].physical_cores) == 3
    assert workers[0].cpuset_mems == "0,1"
    assert workers[0].cpuset_cpus == "0,1,2,3,4,6"


def test_dynamic_worker_allocator_restricts_one_worker_to_explicit_cpuset(tmp_path):
    workers = allocate_workers(
        IsolationDemandSpec(
            physical_cores_per_worker=3,
            memory_mb_per_worker=512,
            numa_policy="local",
        ),
        worker_count=1,
        sys_root=_write_fake_topology(tmp_path),
        allowed_cpus=set(range(8)),
        cpuset_cpus="0,2,4,5,6,7",
    )

    assert workers[0].cpuset_cpus == "0,2,4,5,6,7"
    assert workers[0].cpuset_mems == "0,1"


def test_planner_derives_worker_capacity_from_largest_planned_case(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: mixed-resources
benchmark:
  systems: [postgresql]
  categories: [system_failure]
  scenarios:
    - pg_system_failure_lock_contention
    - pg_system_failure_oom
    - pg_system_failure_deadlock
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime:
  concurrency: 2
  fault_snapshot: use
  isolation: {numa_policy: separate}
""".strip(),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)
    specs = plan_runs(manifest)
    resources = {spec.scenario_id: spec.resources for spec in specs}
    demand = derive_worker_demand(specs, manifest.runtime.isolation)

    assert resources["pg_system_failure_oom"] == CaseResourceSpec(
        worker_physical_cores=1,
        worker_memory_mb=256,
        container_cpu_limit=0.5,
        container_memory_mb=256,
    )
    assert resources["pg_system_failure_lock_contention"] == resources[
        "pg_system_failure_oom"
    ]
    assert resources["pg_system_failure_deadlock"] == CaseResourceSpec(
        worker_physical_cores=1,
        worker_memory_mb=512,
        container_cpu_limit=1.0,
        container_memory_mb=512,
    )
    assert demand == IsolationDemandSpec(
        physical_cores_per_worker=1,
        memory_mb_per_worker=512,
        numa_policy="separate",
    )


def test_resource_governance_contracts_and_formal_matrix(tmp_path):
    scenarios = [
        "pg_resource_governance_data_archiving",
        "pg_resource_governance_resource_throttling",
        "pg_resource_governance_audit_logging",
        "pg_resource_governance_privilege_masking",
    ]
    pilot_path = tmp_path / "pilot.yaml"
    pilot_path.write_text(
        """
experiment_id: rg-pilot
benchmark:
  systems: [postgresql]
  categories: [resource_governance]
  scenarios: [pg_resource_governance_privilege_masking]
agents: [{id: agent-a, mode: llm, model: test-model-a, max_turns: 30}]
repetitions: 1
seeds: [20260716]
runtime:
  concurrency: 1
  isolation: {numa_policy: separate}
""".strip(),
        encoding="utf-8",
    )
    main_path = tmp_path / "main.yaml"
    main_path.write_text(
        f"""
experiment_id: rg-main
benchmark:
  systems: [postgresql]
  categories: [resource_governance]
  scenarios: [{', '.join(scenarios)}]
agents:
  - id: agent-a
    mode: llm
    model: test-model-a
    max_turns: 30
  - id: agent-b
    mode: llm
    model: test-model-b
    max_turns: 30
  - id: agent-c
    mode: llm
    model: test-model-c
    max_turns: 30
  - id: agent-d
    mode: llm
    model: test-model-d
    max_turns: 30
  - id: agent-e
    mode: llm
    model: test-model-e
    max_turns: 30
  - id: agent-f
    mode: llm
    model: test-model-f
    max_turns: 30
exclude_cells:
  - scenario: pg_resource_governance_privilege_masking
    case: customer_developer_masking
    agent: agent-a
  - scenario: pg_resource_governance_privilege_masking
    case: customer_support_masking_simple
    agent: agent-a
repetitions: 1
seeds: [20260716]
runtime:
  concurrency: 1
  isolation: {{numa_policy: separate}}
""".strip(),
        encoding="utf-8",
    )

    pilot = plan_runs(load_manifest(pilot_path))
    main_manifest = load_manifest(main_path)
    main = plan_runs(main_manifest)
    expected_resources = CaseResourceSpec(
        worker_physical_cores=1,
        worker_memory_mb=512,
        container_cpu_limit=1.0,
        container_memory_mb=512,
    )
    logical_key = lambda run: (
        run.agent.model,
        run.scenario_id,
        run.case_id,
        run.repetition,
        run.seed,
    )

    assert len(pilot) == 2
    assert len(main) == 46
    assert {logical_key(run) for run in pilot}.isdisjoint(
        {logical_key(run) for run in main}
    )
    assert len({logical_key(run) for run in pilot + main}) == 48
    assert {run.resources for run in pilot + main} == {expected_resources}
    assert derive_worker_demand(main, main_manifest.runtime.isolation) == IsolationDemandSpec(
        physical_cores_per_worker=1,
        memory_mb_per_worker=512,
        numa_policy="separate",
    )


def test_multi_cause_contracts_and_formal_matrix(tmp_path):
    scenarios = [
        "pg_system_failure_wal_checkpoint_storm",
        "pg_query_perf_stale_stats_lock_contention",
        "pg_system_failure_connection_bloat",
    ]
    manifest_path = tmp_path / "composite-main.yaml"
    manifest_path.write_text(
        f"""
experiment_id: composite-main
benchmark:
  systems: [postgresql]
  categories: [system_failure, query_perf]
  scenarios: [{', '.join(scenarios)}]
agents:
  - id: agent-a
    mode: llm
    model: test-model-a
    max_turns: 30
  - id: agent-b
    mode: llm
    model: test-model-b
    max_turns: 30
  - id: agent-c
    mode: llm
    model: test-model-c
    max_turns: 30
  - id: agent-d
    mode: llm
    model: test-model-d
    max_turns: 30
  - id: agent-e
    mode: llm
    model: test-model-e
    max_turns: 30
  - id: agent-f
    mode: llm
    model: test-model-f
    max_turns: 30
exclude_cells:
  - scenario: pg_query_perf_stale_stats_lock_contention
    case: checkout_stale_stats_and_lock
    agent: agent-a
repetitions: 1
seeds: [20260717]
runtime:
  concurrency: 1
  isolation: {{numa_policy: separate}}
""".strip(),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)
    specs = plan_runs(manifest)
    resources = CaseResourceSpec(
        worker_physical_cores=1,
        worker_memory_mb=512,
        container_cpu_limit=1.0,
        container_memory_mb=512,
    )

    assert len(specs) == 35
    assert {spec.resources for spec in specs} == {resources}
    assert derive_worker_demand(specs, manifest.runtime.isolation) == IsolationDemandSpec(
        physical_cores_per_worker=1,
        memory_mb_per_worker=512,
        numa_policy="separate",
    )


def test_worker_demand_rejects_planned_case_without_resource_contract():
    spec = BoundedScenarioRunSpec(
        experiment_id="pilot",
        run_id="missing-contract",
        system=DatabaseSystem.POSTGRESQL,
        scenario_id="pg_system_failure_deadlock",
        script="scenario.py",
        category="system_failure",
        case_id="checkout_order_deadlock",
        agent=AgentSpec(id="mock", mode="mock"),
        repetition=1,
        seed=11,
        port=19000,
    )

    try:
        derive_worker_demand([spec], IsolationPolicySpec(numa_policy="separate"))
    except ValueError as exc:
        assert "pg_system_failure_deadlock/checkout_order_deadlock" in str(exc)
    else:
        raise AssertionError("parallel PostgreSQL plans must define every case resource contract")


def test_dynamic_worker_allocator_rejects_insufficient_separate_numa_nodes(tmp_path):
    try:
        allocate_workers(
            IsolationDemandSpec(
                physical_cores_per_worker=1,
                memory_mb_per_worker=512,
                numa_policy="separate",
            ),
            worker_count=3,
            sys_root=_write_fake_topology(tmp_path),
            allowed_cpus=set(range(8)),
        )
    except RuntimeError as exc:
        assert "Cannot allocate benchmark worker 3/3" in str(exc)
    else:
        raise AssertionError("separate NUMA policy must allocate each worker on a distinct node")


def test_dynamic_worker_allocator_rejects_insufficient_numa_memory(tmp_path):
    sys_root = _write_fake_topology(tmp_path)
    (sys_root / "devices/system/node/node1/meminfo").write_text(
        "Node 1 MemTotal:       8388608 kB\n"
        "Node 1 MemFree:         262144 kB\n"
        "Node 1 FilePages:            0 kB\n"
        "Node 1 SReclaimable:         0 kB\n"
        "Node 1 Shmem:                 0 kB\n",
        encoding="utf-8",
    )

    try:
        allocate_workers(
            IsolationDemandSpec(
                physical_cores_per_worker=1,
                memory_mb_per_worker=512,
                numa_policy="separate",
            ),
            worker_count=2,
            sys_root=sys_root,
            allowed_cpus=set(range(8)),
        )
    except RuntimeError as exc:
        assert "Cannot allocate benchmark worker 2/2" in str(exc)
        assert "available_memory_mb': 256" in str(exc)
    else:
        raise AssertionError("worker allocation must fit the target NUMA node available memory")


def test_dynamic_worker_allocator_allows_partial_physical_cores(tmp_path):
    workers = allocate_workers(
        IsolationDemandSpec(
            physical_cores_per_worker=1,
            memory_mb_per_worker=512,
            numa_policy="local",
        ),
        worker_count=1,
        sys_root=_write_fake_topology(tmp_path),
        allowed_cpus={0, 1, 3, 4, 5, 6, 7},
    )

    assert len(workers) == 1
    assert workers[0].cpuset_cpus == "0"
    assert workers[0].cpuset_mems == "0"


def test_dynamic_worker_allocator_pins_single_worker_to_explicit_logical_band(tmp_path):
    workers = allocate_workers(
        IsolationDemandSpec(
            physical_cores_per_worker=3,
            memory_mb_per_worker=512,
            numa_policy="local",
        ),
        worker_count=1,
        sys_root=_write_fake_topology(tmp_path),
        allowed_cpus=set(range(8)),
        cpuset_cpus="0,4,6",
    )

    assert workers[0].cpuset_cpus == "0,4,6"
    assert workers[0].cpuset_mems == "0,1"


def test_dynamic_worker_allocator_rejects_logical_band_smaller_than_demand(tmp_path):
    try:
        allocate_workers(
            IsolationDemandSpec(
                physical_cores_per_worker=3,
                memory_mb_per_worker=512,
                numa_policy="local",
            ),
            worker_count=1,
            sys_root=_write_fake_topology(tmp_path),
            allowed_cpus=set(range(8)),
            cpuset_cpus="0,4",
        )
    except RuntimeError as exc:
        assert "fewer logical CPUs than the case demand" in str(exc)
    else:
        raise AssertionError("a logical band below the case demand must be rejected")


def test_store_rebuilds_jsonl_from_run_records(tmp_path):
    store = ExperimentStore(tmp_path, "pilot")
    store.initialize({"experiment_id": "pilot"}, {"git_commit": "abc"})
    spec = BoundedScenarioRunSpec(
        experiment_id="pilot", run_id="run-1", system=DatabaseSystem.POSTGRESQL,
        scenario_id="scenario", script="script.py",
        category="chapter", case_id="default", agent=AgentSpec(id="mock", mode="mock"),
        repetition=1, seed=11, port=19000,
    )
    record = RunRecord.from_spec(spec)
    store.save(record)
    record.status = "succeeded"
    record.diagnosis_pass = True
    record.outcome_pass = True
    record.safe_pass = True
    record.valid_for_aggregate = True
    store.save(record)

    lines = (store.root / "runs.jsonl").read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1
    assert json.loads(lines[0])["status"] == "succeeded"
    assert store.load("run-1").safe_pass is True
    assert (store.root / "failures.jsonl").read_text(encoding="utf-8") == ""


def test_runner_preserves_attempts_and_extracts_evaluation(tmp_path, monkeypatch):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: pilot
benchmark: {systems: [postgresql], categories: [system_failure], scenarios: [pg_system_failure_oom]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime:
  timeout_seconds: 10
  isolation: {numa_policy: local}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    spec = plan_runs(manifest)[0]
    store = ExperimentStore(tmp_path / "artifacts", manifest.experiment_id)
    store.initialize(manifest.raw, {"git_commit": "abc"})
    store.save(RunRecord.from_spec(spec))
    child = (
        "import json, os, pathlib; "
        "p=pathlib.Path(os.environ['AIOPS_TRACE_OUTPUT_DIR'])/os.environ['AIOPS_TRACE_FILENAME']; "
        "p.parent.mkdir(parents=True, exist_ok=True); "
        "p.write_text(json.dumps({'evaluation': {'DiagnosisPass': True, "
        "'OutcomePass': True, 'SafePass': True, 'evaluator': 'TestEvaluatorCase', "
        "'case_no': 0}}), encoding='utf-8')"
    )
    monkeypatch.setattr(
        "src.benchmark.runner.build_command",
        lambda run_spec, experiment: [sys.executable, "-c", child],
    )
    worker = _test_workers()[0]
    runner = ExperimentRunner(manifest, store, (worker,))
    first = runner._execute(spec, worker)
    second = runner._execute(spec, worker)

    assert second.status == "succeeded"
    assert second.diagnosis_pass is True
    assert second.outcome_pass is True
    assert second.safe_pass is True
    assert second.attempt == 2
    assert [attempt["attempt"] for attempt in second.attempts] == [1, 2]
    assert second.worker_id == "worker-01"
    assert second.physical_cores == ("socket0/core0",)
    assert second.cpuset_cpus == "0,2"
    assert second.attempts[-1]["cpuset_mems"] == "0"
    assert second.worker_cpu_capacity == 1.0
    assert second.worker_memory_capacity_mb == 512
    assert second.container_cpu_limit == 0.5
    assert second.container_memory_mb == 256
    assert second.evaluator == "TestEvaluatorCase"
    assert second.case_no == 0
    assert second.attempts[-1]["worker_memory_capacity_mb"] == 512
    assert second.attempts[-1]["container_memory_mb"] == 256
    assert store.load(spec.run_id).physical_cores == ("socket0/core0",)
    assert (store.attempt_dir(spec.run_id, 1) / "stdout.log").is_file()
    assert (store.attempt_dir(spec.run_id, 2) / "evaluator.json").is_file()
    attempt_snapshot = json.loads(store.attempt_path(spec.run_id, 1).read_text(encoding="utf-8"))
    assert attempt_snapshot["attempt"] == 1
    assert attempt_snapshot["diagnosis_pass"] is True


def test_pg_deployment_combines_worker_cpuset_with_each_run_quota(monkeypatch):
    monkeypatch.setenv("AIOPS_CPUSET_CPUS", "0,2")
    monkeypatch.setenv("AIOPS_CPUSET_MEMS", "0")
    deployment = PGDockerDeployment(
        container_name="test-resource-contract",
        resources={"cpus": 9.0, "memory_mb": 9999},
    )

    for cpu_limit, memory_mb in ((0.5, 256), (1.0, 512)):
        monkeypatch.setenv("AIOPS_CPU_LIMIT", str(cpu_limit))
        monkeypatch.setenv("AIOPS_MEMORY_MB", str(memory_mb))
        command = deployment._build_docker_run_command()

        assert command[command.index("--cpuset-cpus") + 1] == "0,2"
        assert command[command.index("--cpuset-mems") + 1] == "0"
        assert command[command.index("--cpus") + 1] == str(cpu_limit)
        assert command[command.index("--memory") + 1] == f"{memory_mb}m"
        assert command[command.index("--memory-swap") + 1] == f"{memory_mb}m"


def test_runner_parallelizes_different_scenarios_but_serializes_each_scenario(
    tmp_path,
    monkeypatch,
):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: pilot
benchmark: {systems: [postgresql], categories: [system_failure], scenarios: [pg_system_failure_deadlock]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime:
  concurrency: 2
  fault_snapshot: use
  isolation:
    numa_policy: separate
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    runner = ExperimentRunner(
        manifest,
        ExperimentStore(tmp_path / "artifacts", "pilot"),
        _test_workers(),
    )
    scenarios = (
        "pg_system_failure_deadlock",
        "pg_system_failure_connection_storm",
        "pg_system_failure_lock_contention",
    )
    specs = [
        BoundedScenarioRunSpec(
            experiment_id="pilot",
            run_id=f"{scenario}-{repetition}",
            system=DatabaseSystem.POSTGRESQL,
            scenario_id=scenario,
            script="scenario.py",
            category="query",
            case_id="default",
            agent=AgentSpec(id="mock", mode="mock"),
            repetition=repetition,
            seed=repetition,
            port=19000 + index,
        )
        for index, (scenario, repetition) in enumerate(
            (scenario, repetition)
            for scenario in scenarios
            for repetition in (1, 2)
        )
    ]
    lock = threading.Lock()
    active_by_scenario = Counter()
    started = []
    executed = []
    peak_total = 0
    peak_by_scenario = Counter()
    active_workers = set()
    worker_violations = []
    used_workers = []

    def execute(spec, worker):
        nonlocal peak_total
        with lock:
            if worker.id in active_workers:
                worker_violations.append(worker.id)
            active_workers.add(worker.id)
            used_workers.append(worker.id)
            active_by_scenario[spec.scenario_id] += 1
            started.append(spec.run_id)
            peak_total = max(peak_total, sum(active_by_scenario.values()))
            peak_by_scenario[spec.scenario_id] = max(
                peak_by_scenario[spec.scenario_id], active_by_scenario[spec.scenario_id]
            )
        time.sleep(0.02)
        with lock:
            active_workers.remove(worker.id)
            active_by_scenario[spec.scenario_id] -= 1
            executed.append(spec.run_id)
        record = RunRecord.from_spec(spec)
        record.status = "succeeded"
        return record

    runner._execute = execute

    failures = runner._run_selected(specs)

    assert failures == 0
    assert peak_total == 2
    assert worker_violations == []
    assert set(used_workers) == {"worker-01", "worker-02"}
    assert peak_by_scenario == {scenario: 1 for scenario in scenarios}
    assert Counter(executed) == Counter(spec.run_id for spec in specs)
    for scenario in scenarios:
        assert [run_id for run_id in started if run_id.startswith(scenario)] == [
            f"{scenario}-1", f"{scenario}-2"
        ]


def test_runner_executes_host_exclusive_scenarios_alone(tmp_path, monkeypatch):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: pilot
benchmark: {systems: [postgresql], categories: [system_failure], scenarios: [pg_system_failure_deadlock]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime:
  concurrency: 2
  fault_snapshot: use
  isolation:
    numa_policy: separate
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    runner = ExperimentRunner(
        manifest,
        ExperimentStore(tmp_path / "artifacts", "pilot"),
        _test_workers(),
    )
    scenario_ids = (
        "pg_system_failure_deadlock",
        "pg_system_failure_oom",
        "pg_system_failure_connection_storm",
        "pg_system_failure_lock_contention",
    )
    specs = [
        BoundedScenarioRunSpec(
            experiment_id="pilot",
            run_id=scenario_id,
            system=DatabaseSystem.POSTGRESQL,
            scenario_id=scenario_id,
            script="scenario.py",
            category="system_failure",
            case_id="default",
            agent=AgentSpec(id="mock", mode="mock"),
            repetition=1,
            seed=11,
            port=19000 + index,
        )
        for index, scenario_id in enumerate(scenario_ids)
    ]
    lock = threading.Lock()
    active: set[str] = set()
    overlap_violations = []
    peak_total = 0

    def execute(spec, worker):
        nonlocal peak_total
        with lock:
            if requires_host_exclusive(spec) and active:
                overlap_violations.append((spec.scenario_id, sorted(active)))
            if any(scenario_id == "pg_system_failure_oom" for scenario_id in active):
                overlap_violations.append((spec.scenario_id, sorted(active)))
            active.add(spec.scenario_id)
            peak_total = max(peak_total, len(active))
        time.sleep(0.02)
        with lock:
            active.remove(spec.scenario_id)
        record = RunRecord.from_spec(spec)
        record.status = "succeeded"
        return record

    runner._execute = execute

    failures = runner._run_selected(specs)

    assert failures == 0
    assert overlap_violations == []
    assert peak_total == 2


def test_build_command_passes_fault_snapshot_use(tmp_path):
    manifest_path = tmp_path / "experiment.yaml"
    manifest_path.write_text(
        """
experiment_id: pilot
benchmark: {systems: [postgresql], categories: [system_failure], scenarios: [pg_system_failure_deadlock]}
agents: [{id: mock, mode: mock}]
repetitions: 1
seeds: [11]
runtime: {fault_snapshot: use}
""".strip(),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    command = build_command(plan_runs(manifest)[0], manifest)

    index = command.index("--fault-snapshot-mode")
    assert command[index + 1] == "use"


def test_fault_snapshot_use_preflight_requires_every_image(monkeypatch):
    specs = [
        BoundedScenarioRunSpec(
            experiment_id="pilot",
            run_id="deadlock",
            system=DatabaseSystem.POSTGRESQL,
            scenario_id="pg_system_failure_deadlock",
            script="run_pg_system_failure_deadlock_scenario.py",
            category="system_failure",
            case_id="checkout_order_deadlock",
            agent=AgentSpec(id="mock", mode="mock"),
            repetition=1,
            seed=11,
            port=19000,
        )
    ]
    monkeypatch.setattr("src.execution.environment.PGEnv.snapshot_exists", lambda self, name: False)

    try:
        assert_fault_snapshots_exist(specs)
    except RuntimeError as exc:
        assert "pg_system_failure_deadlock" in str(exc)
        assert "aiopsbench-pg-fault" in str(exc)
    else:
        raise AssertionError("fault_snapshot='use' must fail before execution when an image is missing")


def test_tidb_fault_snapshot_use_preflight_checks_image_group(monkeypatch):
    specs = [
        BoundedScenarioRunSpec(
            experiment_id="pilot",
            run_id="tidb-bc02",
            system=DatabaseSystem.TIDB,
            scenario_id="tidb_business_change_cdc_dc_migration",
            script="run_tidb_business_change_cdc_dc_migration_scenario.py",
            category="business_change",
            case_id="cdc_dc_migration_reverse_cutover",
            agent=AgentSpec(id="mock", mode="mock"),
            repetition=1,
            seed=11,
            port=19020,
        )
    ]
    monkeypatch.setattr(
        "src.execution.deployment.TiDBDockerDeployment.image_group_exists",
        lambda self, name: name == self.image_group_name,
    )

    snapshots = assert_fault_snapshots_exist(specs)

    assert snapshots == {
        "tidb_business_change_cdc_dc_migration/cdc_dc_migration_reverse_cutover": (
            "aiopsbench-tidb-group-bc02-cdc-migration-98276443fb492b0dd1e17642:latest"
        )
    }


def test_pg_docker_command_applies_experiment_cpuset(monkeypatch):
    monkeypatch.setenv("AIOPS_CPUSET_CPUS", "0,2")
    monkeypatch.setenv("AIOPS_CPUSET_MEMS", "0")
    monkeypatch.setenv("AIOPS_CPU_LIMIT", "1.0")
    monkeypatch.setenv("AIOPS_MEMORY_MB", "512")
    deployment = PGDockerDeployment(container_name="isolated-pg", port=19000)

    command = deployment._build_docker_run_command(for_init=False)

    assert command[command.index("--cpuset-cpus") + 1] == "0,2"
    assert command[command.index("--cpuset-mems") + 1] == "0"
    assert command[command.index("--cpus") + 1] == "1.0"
    assert command[command.index("--memory") + 1] == "512m"


def test_aggregate_reports_pass_rates_and_infrastructure_failures():
    base = dict(
        experiment_id="pilot", system="postgresql", case_id="default",
        category="query", script="x.py",
        agent_id="agent", agent_mode="llm", model="model", repetition=1, seed=1, port=1,
    )
    records = [
        RunRecord(run_id="one", scenario_id="s1", status="succeeded",
                  diagnosis_pass=True, outcome_pass=True, safe_pass=True,
                  valid_for_aggregate=True, **base),
        RunRecord(run_id="two", scenario_id="s2", status="succeeded",
                  diagnosis_pass=True, outcome_pass=False, safe_pass=False,
                  valid_for_aggregate=True, **base),
        RunRecord(run_id="three", scenario_id="s2", status="failed", **base),
    ]

    result = aggregate(records)

    assert result["summary"]["infrastructure_failure_rate"] == 1 / 3
    assert result["agents"][0]["diagnosis_pass_rate"] == 1.0
    assert result["agents"][0]["outcome_pass_rate"] == 0.5
    assert result["agents"][0]["safe_pass_rate"] == 0.5


def test_runner_classifies_admission_blocker_from_process_log(tmp_path):
    stdout = tmp_path / "stdout.log"
    stdout.write_text(
        "RuntimeError: PG-RG-PC01 admission blocker: target storage did not produce a stable chain\n",
        encoding="utf-8",
    )

    category, error = _classify_process_failure(stdout)

    assert category == "admission"
    assert "target storage did not produce a stable chain" in error


def test_runner_classifies_rg1_replay_provider_failure_as_infrastructure(tmp_path):
    stdout = tmp_path / "stdout.log"
    stdout.write_text(
        "RuntimeError: PG-RG-MF01 replay infrastructure: checkout worker/provider error: connection refused\n",
        encoding="utf-8",
    )

    category, error = _classify_process_failure(stdout)

    assert category == "evaluator"
    assert "checkout worker/provider error" in error


def test_runner_classifies_ltx_fixture_missing_as_invalid_run(tmp_path):
    stdout = tmp_path / "stdout.log"
    stdout.write_text(
        "LongRunningTxFixtureMissingError: LTX-FIXTURE-MISSING: contract fixture session is absent "
        "at evaluation and the agent action history shows no successful "
        "pg_terminate_backend/pg_cancel_backend against it; session-count checks would carry no "
        "agent signal. role=decoy, application_name='payment-short-tx-simple', observed_count=0\n",
        encoding="utf-8",
    )

    category, error = _classify_process_failure(stdout)

    assert category == "fixture_missing"
    assert "role=decoy" in error


def test_runner_classifies_llm_provider_failure_from_process_log(tmp_path):
    stdout = tmp_path / "stdout.log"
    stdout.write_text(
        "RuntimeError: LLM API 调用失败: 413 Request Entity Too Large\n",
        encoding="utf-8",
    )

    category, error = _classify_process_failure(stdout)

    assert category == "provider"
    assert "413 Request Entity Too Large" in error


def test_runner_classifies_tpcds_bootstrap_failure_as_infrastructure(tmp_path):
    stdout = tmp_path / "stdout.log"
    stdout.write_text(
        "dsdgen not found, compiling tpcds-kit...\n"
        "Cloning tpcds-kit repository...\n"
        "fatal: unable to access https://github.com/gregrahn/tpcds-kit.git\n",
        encoding="utf-8",
    )

    category, error = _classify_process_failure(stdout)

    assert category == "workload_setup"
    assert "TPC-DS workload bootstrap failed" in error


def test_runner_classifies_dataset_hash_mismatch_as_infrastructure(tmp_path):
    stdout = tmp_path / "stdout.log"
    stdout.write_text(
        "RuntimeError: Dataset init SQL hash differs from manifest: expected='old', actual='new'\n",
        encoding="utf-8",
    )

    category, error = _classify_process_failure(stdout)

    assert category == "workload_setup"
    assert "does not match the frozen manifest" in error


def test_aggregate_keeps_safe_pass_independent_from_outcome_pass():
    base = dict(
        experiment_id="pilot", system="postgresql", case_id="default",
        category="query", script="x.py",
        agent_id="agent", agent_mode="llm", model="model", repetition=1, seed=1, port=1,
    )
    records = [
        RunRecord(run_id="safe-only", scenario_id="s1", status="succeeded",
                  diagnosis_pass=True, outcome_pass=False, safe_pass=True,
                  valid_for_aggregate=True, **base),
        RunRecord(run_id="full", scenario_id="s2", status="succeeded",
                  diagnosis_pass=True, outcome_pass=True, safe_pass=True,
                  valid_for_aggregate=True, **base),
    ]

    result = aggregate(records)["summary"]

    assert result["outcome_pass_rate"] == 0.5
    assert result["safe_pass_rate"] == 1.0
