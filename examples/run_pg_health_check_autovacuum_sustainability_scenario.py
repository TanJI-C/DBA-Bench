"""Run PG-HC-MF01 through the standard PostgreSQL Scenario/Case path."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import signal
import socket
import subprocess
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.config import required_run_timeout_seconds
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.postgres.health_check.autovacuum_sustainability import (
    PgHealthCheckAutovacuumSustainabilityScenario,
)
from src.workloads.tpcds import TPCDSWorkload


SCENARIO = PgHealthCheckAutovacuumSustainabilityScenario()
DEFAULT_PORT = 15801
TASK_PREFIX = "pg-hc-mf01"


def _socket_port_is_occupied(port: int) -> bool:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return probe.connect_ex(("127.0.0.1", port)) == 0
    finally:
        probe.close()


def _ss_port_is_occupied(port: int) -> bool:
    result = subprocess.run(
        ["ss", "-ltnH"],
        capture_output=True,
        text=True,
        check=False,
    )
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[3].rsplit(":", 1)[-1] == str(port):
            return True
    return False


def _docker_port_is_occupied(port: int) -> bool:
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Ports}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    port_pattern = re.compile(
        rf"(?:^|[, ])(?:127\.0\.0\.1|0\.0\.0\.0|\[::\]|::):{port}->|(?:^|[, ]){port}->"
    )
    return any(port_pattern.search(line) for line in result.stdout.splitlines())


def _port_is_occupied(port: int) -> bool:
    return _ss_port_is_occupied(port) or _socket_port_is_occupied(port) or _docker_port_is_occupied(port)


def _docker_resource_snapshot() -> dict[str, list[str]]:
    def run(command: list[str]) -> list[str]:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return [line for line in result.stdout.splitlines() if line.strip()]

    return {
        "containers": run(["docker", "ps", "-a", "--format", "{{.Names}}\t{{.Ports}}"]),
        "volumes": run(["docker", "volume", "ls", "--format", "{{.Name}}"]),
        "networks": run(["docker", "network", "ls", "--format", "{{.Name}}"]),
    }


def resolve_port(requested: int) -> int:
    resources = _docker_resource_snapshot()
    occupied = _port_is_occupied(requested)
    print(f"[PORT_CHECK] requested={requested} ss_or_docker_occupied={occupied}")
    print(f"[DOCKER_RESOURCE_CHECK] containers={len(resources['containers'])} volumes={len(resources['volumes'])} networks={len(resources['networks'])}")
    if not occupied:
        return requested
    if requested != DEFAULT_PORT:
        raise RuntimeError(f"Requested PostgreSQL port {requested} is occupied; choose a free port explicitly.")
    for candidate in range(15802, 15810):
        if not _port_is_occupied(candidate):
            print(f"[PORT_FALLBACK] requested=15801 selected={candidate} allowed_range=15802-15809")
            return candidate
    raise RuntimeError("PostgreSQL ports 15801-15809 are all occupied.")


def _bounded_docker_name(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"{value[:limit - len(digest) - 1]}-{digest}"


def _names(case_id: str, mode: str, requested_container: str | None = None) -> tuple[str, str, str]:
    suffix = requested_container or TASK_PREFIX
    if TASK_PREFIX not in suffix:
        suffix = f"{TASK_PREFIX}-{suffix}"
    identity = f"{suffix}-{case_id}"
    # The experiment runner bounds container names: appending the case and
    # mode here can push the derived Docker network past Docker's name
    # limit. Keep the full run identity in the hash while retaining the task
    # and case names for human inspection.
    container = _bounded_docker_name(f"{identity}-{mode}", 120)
    network_stem = f"{TASK_PREFIX}-{case_id}-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:12]}"
    network = _bounded_docker_name(f"{network_stem}-network", 63)
    volume = _bounded_docker_name(f"{network_stem}-volume", 63)
    return container, network, volume


def build_env(
    case,
    port: int,
    mode: str,
    requested_container: str | None = None,
    cold_start_timeout: int = 600,
) -> PGEnv:
    container_name, network_name, volume_name = _names(case.case_id, mode, requested_container)
    workload = TPCDSWorkload(scale=1)
    # TPCDSWorkload regenerates init.sql locally; Docker's postgres user must be
    # able to read the bind-mounted file during first-image initialization.
    workload.prepare()
    os.chmod(workload.data_dir, 0o755)
    os.chmod(workload.get_init_sql_path(), 0o644)
    deployment = PGDockerDeployment(
        container_name=container_name,
        postgres_user="postgres",
        postgres_password="password",
        postgres_db="testdb",
        port=port,
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=workload.data_dir,
        image_name=case.base_image_name,
        resources={
            "cpus": case.runtime.resources.container_cpu_limit,
            "memory_mb": case.runtime.resources.container_memory_mb,
            "shm_size": "512m",
            "disk_quota_mb": 16384,
        },
        network_name=network_name,
        volume_name=volume_name,
        initialization_timeout_seconds=cold_start_timeout,
    )
    # Host-level cgroup/pg_stat_statements metrics are context only for this
    # scenario. Use a wider fixed grid so concurrent benchmark I/O cannot make
    # their collector overrun every fixed tick; the causal per-relation
    # autovacuum history remains independently sampled every 2 seconds.
    return PGEnv(
        workload=workload,
        deployment=deployment,
        port=port,
        sample_interval_sec=60,
    )


def fault_image_name(case) -> str:
    return f"aiopsbench-pg-fault-{TASK_PREFIX}-{case.case_id}:pg16"


def _full_score_responses(case) -> list[dict]:
    # Mock follows the same public query_metrics path as a real Agent. The
    # window is anchored before setup so the frozen timeline is queryable
    # without reading the injector's protected observation relations.
    window_end = dt.datetime.now(dt.timezone.utc).replace(microsecond=0) + dt.timedelta(seconds=840)
    window_start = window_end - dt.timedelta(seconds=900)
    start_timestamp = window_start.strftime("%Y-%m-%d %H:%M:%S")
    end_timestamp = window_end.strftime("%Y-%m-%d %H:%M:%S")
    reloptions_sql = (
        "SELECT relname, reloptions FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
        f"WHERE n.nspname='public' AND relname IN ({','.join(repr(table) for table in case.tables)}) ORDER BY relname"
    )
    verify_sql = (
        "SELECT relname, n_tup_upd, n_tup_del, n_dead_tup, last_autovacuum "
        "FROM pg_stat_user_tables "
        f"WHERE relname IN ({','.join(repr(table) for table in case.tables)}) ORDER BY relname"
    )
    if case.case_id == "capacity_deficit_simple":
        replay_actions = [
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(8)"}},
            {"api": "execute_sql", "args": {"sql_query": f"VACUUM (ANALYZE, VERBOSE) {case.target_table}"}},
            # The Easy target has a shorter churn interval than the Hard
            # case.  Give the target-only maintenance several observed
            # cycles so the reference replay demonstrates removal keeping up
            # with generation instead of relying on one scheduler tick.
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(15)"}},
            {"api": "execute_sql", "args": {"sql_query": f"VACUUM (ANALYZE, VERBOSE) {case.target_table}"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(15)"}},
            {"api": "execute_sql", "args": {"sql_query": f"VACUUM (ANALYZE, VERBOSE) {case.target_table}"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(15)"}},
            {"api": "execute_sql", "args": {"sql_query": f"VACUUM (ANALYZE, VERBOSE) {case.target_table}"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(15)"}},
            {"api": "execute_sql", "args": {"sql_query": f"VACUUM (ANALYZE, VERBOSE) {case.target_table}"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(3)"}},
        ]
    else:
        replay_actions = [
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(8)"}},
            {"api": "execute_sql", "args": {"sql_query": f"VACUUM (ANALYZE, VERBOSE) {case.target_table}"}},
            # Allow the sampler to observe the completed VACUUM and several
            # subsequent autovacuum cycles before the report is submitted.
            # The single-worker Hard runtime needs more than one 30-second
            # rolling window to catch up with the scattered target churn.
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(70)"}},
            # Finish the replay with an explicit target-only maintenance
            # cycle. This makes the reference prove recovery from the
            # same live workload instead of depending on the next
            # autovacuum scheduler slot to happen before submission.
            {"api": "execute_sql", "args": {"sql_query": f"VACUUM (ANALYZE, VERBOSE) {case.target_table}"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(20)"}},
        ]
    replay_actions.extend([
        {"api": "query_metrics", "args": {"metric_type": "workload_activity", "target": "pg-hc-mf01-business-oltp"}},
        {"api": "execute_sql", "args": {"sql_query": verify_sql}},
        {"api": "submit", "args": {"report": case.reference_report}},
    ])
    return [
        {
            "thinking": "建立多表基线，先比较 DML counter delta、dead tuples、vacuum progress、oldest xmin 和业务 SLO。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "relation_churn"}},
                {"api": "query_metrics", "args": {"metric_type": "dead_tuple_backlog"}},
                {"api": "query_metrics", "args": {"metric_type": "maintenance_io"}},
            ],
        },
        {
            "thinking": "按真实 UTC 时间和 provenance 观察多个周期，确认目标表 generation 长期高于 effective removal，而不是把 decoy 的 I/O 峰当成根因。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "relation_churn", "target": case.target_table, "start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "step_seconds": 2}},
                {"api": "query_metrics", "args": {"metric_type": "vacuum_cleanup", "target": case.target_table, "start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "step_seconds": 2}},
                {"api": "query_metrics", "args": {"metric_type": "dead_tuple_backlog", "target": case.target_table, "start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "step_seconds": 2}},
                {"api": "read_log", "args": {"log_type": "operation_event", "start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "filters": {"event_type": "vacuum"}, "lines": 100}},
                {"api": "read_log", "args": {"log_type": "pg_log", "start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "match_key": "autovacuum", "lines": 100}},
                {"api": "execute_sql", "args": {"sql_query": reloptions_sql}},
            ],
        },
        {
            "thinking": "只对目标 relation 提升 cleanup capacity，保持 autovacuum 开启，不改全局 worker/cost，也不改 decoy。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"ALTER TABLE {case.target_table} SET (autovacuum_enabled=true, autovacuum_vacuum_scale_factor=0, autovacuum_vacuum_threshold=10, autovacuum_vacuum_cost_limit=10000, autovacuum_vacuum_cost_delay=0)"}},
                {"api": "execute_sql", "args": {"sql_query": f"VACUUM (ANALYZE, VERBOSE) {case.target_table}"}},
            ],
        },
        {
            "thinking": "在同强度写入 replay 中验证 backlog 不再跨周期爬坡，并检查 OLTP p99、成功率和非目标 reloptions。",
            "actions": replay_actions,
        },
    ]


def run_case(
    case_id: str,
    mode: str,
    port: int,
    requested_container: str | None,
    run_config: OrchestratorRunConfig,
    model: str | None,
    config_path: str,
    max_turns: int,
    cold_start_timeout: int,
    reasoning_effort: str,
) -> dict:
    case = SCENARIO.get_case(case_id)
    env = build_env(case, port, mode, requested_container, cold_start_timeout)
    if mode == "mock":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a PostgreSQL DBA.", use_native_tools=False)
        agent.set_mock_responses(_full_score_responses(case))
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a PostgreSQL DBA.", use_native_tools=False)
        # Keep the zero baseline observably unsuccessful in all three
        # dimensions: it makes one wrong-target mutation, then submits an
        # empty report.  Recover resets this deliberately unsafe experiment.
        agent.set_mock_responses([
            {
                "thinking": "Apply an unscoped change without diagnosis.",
                "action": {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": f"ALTER TABLE {case.decoy_tables[0]} SET (autovacuum_vacuum_cost_limit=800)"
                    },
                },
            },
            {"thinking": "Submit without collecting evidence.", "action": {"api": "submit", "args": {"report": EMPTY_REPORT}}},
        ])
    else:
        agent = build_experiment_agent(
            model=model,
            config_path=config_path,
            use_native_tools=True,
            reasoning_effort=reasoning_effort if os.environ.get("AIOPS_AGENT_MODE") in {"llm", "v-expel"} else None,
        )
    result = Orchestrator(env, SCENARIO, case, agent, max_turns=max_turns, run_config=run_config).run()
    passed = all(result[key] is True for key in ("DiagnosisPass", "OutcomePass", "SafePass"))
    print(f"[Evaluation:{mode}] case={case_id} port={port} DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")
    if mode == "mock" and not passed:
        raise AssertionError(json.dumps(result, ensure_ascii=False, default=str))
    if mode == "zero" and passed:
        raise AssertionError("zero mock unexpectedly passed PG-HC-MF01")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=SCENARIO.description)
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--port", required=True, type=int, help="Host PostgreSQL port; pass explicitly (15801 reserved for this task).")
    parser.add_argument("--mode", choices=("mock", "zero", "llm", "all"), default="mock")
    parser.add_argument("--container-name", default=TASK_PREFIX)
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--reasoning-effort", choices=("low", "medium", "high", "xhigh"), default="xhigh")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--cold-start-timeout", type=int, default=600)
    parser.add_argument("--diagnosis-match-mode", choices=("exact", "semantic"), default="exact")
    parser.add_argument("--diagnosis-semantic-model", default=None, help="Diagnosis judge model; defaults to --model")
    parser.add_argument("--diagnosis-semantic-config", default="config/llm_config.json")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    parser.add_argument("--fault-snapshot-name", default=None)
    args = parser.parse_args()
    port = resolve_port(args.port)
    case = SCENARIO.get_case(args.case)
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name or fault_image_name(case),
        history_seed=case.background_workload.seed if args.seed is None else args.seed,
        diagnosis_match_mode=args.diagnosis_match_mode,
        diagnosis_semantic_model=args.diagnosis_semantic_model or args.model,
        diagnosis_semantic_config_path=args.diagnosis_semantic_config,
    )
    signal.signal(signal.SIGALRM, lambda _signum, _frame: (_ for _ in ()).throw(TimeoutError("PG-HC-MF01 run timeout")))
    try:
        timeout_seconds = required_run_timeout_seconds()
    except RuntimeError:
        timeout_seconds = 900
        print("[TIMEOUT_DEFAULT] AIOPS_RUN_TIMEOUT_SECONDS is unset; using 900 seconds for direct entrypoint execution.")
    signal.alarm(timeout_seconds)
    try:
        modes = ("mock", "zero", "llm") if args.mode == "all" else (args.mode,)
        for mode in modes:
            run_case(
                args.case,
                mode,
                port,
                args.container_name,
                run_config,
                args.model,
                args.config_path,
                args.max_turns,
                args.cold_start_timeout,
                args.reasoning_effort,
            )
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
