"""Run PG-RG-IO01 with isolated PostgreSQL, monitoring and Docker resources."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.execution.specs import HostPortLayout
from src.scenarios.evaluation.config import add_diagnosis_arguments
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.postgres import PgResourceGovernanceIoContextWorkloadScenario
from src.workloads.tpcds import TPCDSWorkload


def _resource_names(case, mode: str, container_name: str) -> tuple[str, str]:
    suffix = hashlib.sha256(container_name.encode("utf-8")).hexdigest()[:12]
    base = f"aiopsbench-pg-{case.evaluator.scenario_id}-{case.case_id}-{mode}".replace("_", "-")
    return f"{base}-{suffix}-network", f"{base}-{suffix}-volume"


class IoContextDeployment(PGDockerDeployment):
    """Attach only this task's named network/volume and remove only owned resources."""

    DATASET_INIT_TIMEOUT_SECONDS = 1800

    def __init__(self, *, network_name: str, volume_name: str, **kwargs):
        super().__init__(**kwargs)
        self.network_name = network_name
        self.volume_name = volume_name
        self._created_network = False
        self._created_volume = False

    def _ensure_named_resources(self):
        network = subprocess.run(["docker", "network", "inspect", self.network_name], capture_output=True, text=True)
        if network.returncode != 0:
            subprocess.run(
                [
                    "docker", "network", "create",
                    "--label", "aiopsbench.owner=pg-hc-mf01",
                    self.network_name,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self._created_network = True
        volume = subprocess.run(["docker", "volume", "inspect", self.volume_name], capture_output=True, text=True)
        if volume.returncode != 0:
            subprocess.run(
                [
                    "docker", "volume", "create",
                    "--label", "aiopsbench.owner=pg-hc-mf01",
                    self.volume_name,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self._created_volume = True

    def _build_docker_run_command(self, for_init: bool = False) -> list:
        command = super()._build_docker_run_command(for_init=for_init)
        if for_init:
            command.extend([
                "-c", "fsync=off",
                "-c", "synchronous_commit=off",
                "-c", "full_page_writes=off",
            ])
        image_index = max(index for index, value in enumerate(command) if value in {"postgres:16", self.image_name})
        command[image_index:image_index] = [
            "-v", f"{self.volume_name}:/var/lib/aiopsbench/io-context",
        ]
        return command

    def deploy(self):
        self._ensure_named_resources()
        super().deploy()

    def teardown(self):
        # PGDockerDeployment owns the explicitly named resources after
        # _ensure_owned_resources() and removes them as part of teardown.
        # Removing them again here made otherwise valid runs fail with
        # "network/volume not found" after the parent had already cleaned up.
        super().teardown()


def _ensure_port_range(port: int, monitoring_port: int) -> None:
    # Ports come from the experiment runner (rebased to a free pair); only
    # distinctness and the unprivileged range are contract requirements.
    if not 1024 <= port <= 65535 or not 1024 <= monitoring_port <= 65535:
        raise ValueError(f"PG-RG-IO01 ports must be unprivileged: postgres={port}, monitoring={monitoring_port}")
    if port == monitoring_port:
        raise ValueError("PostgreSQL and monitoring ports must be distinct")
    # Docker's userland proxy can retain a just-removed published port while
    # the previous scenario process is already gone. Give the owner a bounded
    # grace period before reporting a real conflict.
    deadline = time.monotonic() + 90
    while True:
        ss = subprocess.run(["ss", "-ltn"], capture_output=True, text=True, check=False)
        listening = [
            line.strip()
            for line in ss.stdout.splitlines()
            if any(f":{candidate} " in line or f":{candidate}\n" in line for candidate in (port, monitoring_port))
        ]
        unavailable = None
        for candidate in (port, monitoring_port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.bind(("127.0.0.1", candidate))
                except OSError:
                    unavailable = candidate
                    break
        if unavailable is None and not listening:
            return
        if time.monotonic() >= deadline:
            detail = listening[0] if listening else f"bind failed for {unavailable}"
            raise RuntimeError(f"Requested PG-RG-IO01 port is unavailable: {detail}")
        time.sleep(0.25)


def _ensure_docker_name_free(container_name: str, network_name: str, volume_name: str) -> None:
    checks = (("container", ["docker", "container", "inspect", container_name]), ("network", ["docker", "network", "inspect", network_name]), ("volume", ["docker", "volume", "inspect", volume_name]))
    for kind, command in checks:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            raise RuntimeError(f"PG-RG-IO01 {kind} already exists; choose a new --container-name or mode")


def build_report(case, success: bool) -> dict:
    if not success:
        return {
            "diagnosis": {"conditions": []},
            "outcome": {"changes": [], "verification": []},
            "summary": "No diagnosis or remediation was attempted.",
        }
    conditions = [
        ("bulkread context pressure", case.report_app_name, "pg_stat_io context and device queue were elevated"),
        ("report workload causes the OLTP SLO violation", case.report_app_name, "the causal workload bucket preceded the OLTP p99 violation"),
        ("read count alone is a decoy", "same-domain windows", "a larger read-count window had no business impact"),
        ("OLTP p99 violation follows report I/O pressure", "pgbench-oltp", "the independent history preserved pressure before impact"),
    ]
    return {
        "diagnosis": {"conditions": [{"type": "finding", "factor": factor, "entity": entity, "evidence": [evidence]} for factor, entity, evidence in conditions]},
        "outcome": {
            "changes": [f"controlled only {case.report_app_name} with a bounded workload policy"],
            "verification": ["OLTP SLO, target workload, required-job deadlines and checksums were rechecked"],
        },
        "summary": "The causal workload I/O context caused the OLTP impact; read count and cache-hit were not sufficient evidence.",
    }


def build_mock_agent(case):
    control_sql = (
        f"INSERT INTO {case.control_table}(control_name, requested_mode, target_application) "
        f"VALUES ('workload_policy', 'throttle', '{case.report_app_name}') "
        "ON CONFLICT (control_name) DO UPDATE SET requested_mode = EXCLUDED.requested_mode, "
        "target_application = EXCLUDED.target_application, requested_at = clock_timestamp();"
    )
    inspect_sql = (
        "SELECT backend_type, object, context, reads, read_time, hits, evictions, reuses "
        "FROM pg_stat_io ORDER BY context, backend_type; "
        f"SELECT window_name, bucket_application, bucket_queryid, query_shared_blks_read_delta, "
        f"query_exec_ms_delta, oltp_p99_ms, oltp_slo_violations "
        f"FROM {case.observations_table} ORDER BY observed_at DESC LIMIT 30; "
        f"SELECT window_name, context_reads_delta, context_read_time_ms_delta, context_hits_delta, "
        f"device_io_in_progress, device_weighted_io_ms_delta "
        f"FROM {case.context_observations_table} ORDER BY observed_at DESC LIMIT 30;"
        f" SELECT phase_started_at, phase_finished_at, window_name, bucket_application, bucket_queryid, "
        f"scan_count, query_calls_delta, query_shared_blks_read_delta, query_exec_ms_delta, "
        f"context_reads_delta, context_read_time_ms_delta, context_hits_delta, device_io_in_progress, "
        f"device_weighted_io_ms_delta FROM {case.phase_observations_table} ORDER BY phase_started_at; "
        f"SELECT application_name, queryid, anchor_date, window_days, duration_ms, call_role "
        f"FROM {case.call_history_table} ORDER BY phase_started_at;"
    )
    verify_sql = (
        "DO $$ DECLARE ready boolean; BEGIN "
        "FOR i IN 1..300 LOOP "
        f"SELECT target_workload_controlled AND report_pressure_recovered AND oltp_slo_pass "
        f"AND required_jobs_completed AND required_jobs_checksum_ok AND required_jobs_deadline_ok "
        f"AND target_job_status = 'completed' INTO ready FROM {case.outcome_table}; "
        "EXIT WHEN coalesce(ready, false); PERFORM pg_sleep(2); END LOOP; END $$; "
        f"SELECT target_workload_controlled, report_pressure_recovered, oltp_slo_pass, "
        f"required_jobs_completed, required_jobs_checksum_ok, required_jobs_deadline_ok, "
        f"target_job_status, worst_oltp_p99_ms FROM {case.outcome_table};"
    )
    responses = [
        {"thinking": "先确认 cache-hit/read-count 只是表象，读取 PG16 I/O context 和历史 bucket。", "action": {"api": "query_metrics", "args": {"metric_type": "cache_hit_ratio", "target": None}}},
        {"thinking": "pg_stat_io 只能提供 context aggregate；把 bulkread time、device queue、query/application bucket 与 OLTP p99 的时间关系放在一起。", "action": {"api": "execute_sql", "args": {"sql_query": inspect_sql}}},
        {"thinking": "因果 workload 的 bulkread pressure 先于 OLTP 违约，最大 read count 的其他窗口没有同样业务影响；保留 required jobs。", "action": {"api": "execute_sql", "args": {"sql_query": control_sql}}},
        {"thinking": "复查真实 replay 的 SLO、报告控制、required job deadline 和 checksum。", "action": {"api": "execute_sql", "args": {"sql_query": verify_sql}}},
        {"thinking": "提交诊断与结果。", "action": {"api": "submit", "args": {"report": build_report(case, True)}}},
    ]
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a PostgreSQL DBA agent.", use_native_tools=False)
    agent.set_mock_responses(responses)
    return agent


def build_zero_agent():
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a PostgreSQL DBA agent.", use_native_tools=False)
    agent.set_mock_responses([
        {"thinking": "Take an unsafe shortcut without diagnosing the actual workload.", "action": {"api": "execute_sql", "args": {"sql_query": "ALTER SYSTEM SET shared_buffers = '8GB';"}}},
        {"thinking": "Submit without checking the database.", "action": {"api": "submit", "args": {"report": build_report(None, False)}}},
    ])
    return agent


def build_env(case, port: int, monitoring_port: int, container_name: str, mode: str):
    workload = TPCDSWorkload(scale=1)
    # The init SQL is bind-mounted into the postgres init container and must be
    # readable by the container's postgres user after workload generation.
    os.chmod(workload.get_init_sql_path(), 0o644)
    scenario_id = case.evaluator.scenario_id
    network_name, volume_name = _resource_names(case, mode, container_name)
    deployment = IoContextDeployment(
        container_name=container_name,
        port=port,
        image_name=case.base_image_name,
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=os.path.dirname(
            os.path.realpath(os.path.join(workload.data_dir, "store_sales.dat"))
        ),
        network_name=network_name,
        volume_name=volume_name,
        postgres_runtime_options=case.runtime.parameters.as_command_line(),
        resources={
            "cpus": case.runtime.resources.container_cpu_limit,
            "memory_mb": case.runtime.resources.container_memory_mb,
            "shm_size": "256m",
            "disk_quota_mb": 8192,
        },
    )
    # This scenario's causal I/O evidence comes from its own 1-second observer.
    # Keep the generic catalog sampler lightweight and tolerant of short host
    # scheduling gaps so unrelated host load cannot invalidate the run.
    env = PGEnv(
        workload=workload,
        deployment=deployment,
        port=port,
        sample_interval_sec=10,
        allow_sampler_jitter=True,
    )
    # The dedicated image is initialized from the shared TPC-DS dataset, so use
    # its existing 1CPU/512MB baseline rather than creating a generated artifact.
    env.baseline_image_name = "aiopsbench-pg-tpcds:latest"
    case = dataclasses.replace(case, monitoring_port=monitoring_port,
        runtime=dataclasses.replace(case.runtime,
            host_ports=HostPortLayout(offsets=(0, monitoring_port - port))))
    return env, case, network_name, volume_name


def run_one(scenario, case, mode: str, port: int, monitoring_port: int, container_name: str, args) -> dict:
    _ensure_port_range(port, monitoring_port)
    scenario_id = case.evaluator.scenario_id
    network_name, volume_name = _resource_names(case, mode, container_name)
    _ensure_docker_name_free(container_name, network_name, volume_name)
    env, case, _, _ = build_env(case, port, monitoring_port, container_name, mode)
    agent = build_mock_agent(case) if mode == "mock" else build_zero_agent() if mode == "zero" else build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        max_turns=10 if mode == "mock" else 3 if mode == "zero" else args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
            fault_snapshot_name=args.fault_snapshot_name,
            diagnosis_match_mode=args.diagnosis_match_mode,
            diagnosis_semantic_model=args.diagnosis_semantic_model,
            diagnosis_semantic_config_path=args.diagnosis_semantic_config_path,
        ),
    )
    result = orchestrator.run()
    print(f"[{mode}] postgres_port={port} monitoring_port={monitoring_port} DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")
    expected = (True, True, True) if mode == "mock" else (False, False, False) if mode == "zero" else None
    actual = (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"])
    if expected is not None and actual != expected:
        print(f"[{mode}] calibration expectation mismatch; preserving evaluator result: {json.dumps(result, ensure_ascii=False)}")
    return result


def main() -> None:
    scenario = PgResourceGovernanceIoContextWorkloadScenario()
    parser = argparse.ArgumentParser(description="Run PG-RG-IO01 I/O context workload scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "flash", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15871)
    parser.add_argument("--monitoring-port", type=int)
    parser.add_argument("--container-name", default="aiopsbench-pg-io-context")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--fault-snapshot-mode", "--fault-image-mode", dest="fault_snapshot_mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name", "--fault-image-name", dest="fault_snapshot_name")
    add_diagnosis_arguments(parser)
    args = parser.parse_args()
    case = scenario.get_case(args.case)
    monitoring_port = args.monitoring_port or case.monitoring_port
    if args.monitoring_port is None and monitoring_port == args.port:
        monitoring_port = args.port + 1
    if not 1 <= monitoring_port <= 65535:
        raise ValueError(f"--monitoring-port must be a valid TCP port: {monitoring_port}")
    if args.mode == "all":
        modes = ("mock", "zero", "flash")
    else:
        modes = ("flash" if args.mode == "llm" else args.mode,)
    for offset, mode in enumerate(modes):
        run_one(
            scenario,
            case,
            mode,
            args.port + offset * 3,
            monitoring_port + offset * 3,
            f"{args.container_name}-{case.case_id}-{mode}".replace("_", "-"),
            args,
        )


if __name__ == "__main__":
    main()
