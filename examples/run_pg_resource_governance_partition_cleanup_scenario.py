"""Run PG-RG-PC01 with the shared Orchestrator path."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import uuid

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.factory import build_experiment_agent
from src.agents.agent import MockLLMAgent
from src.execution.deployment import PGDockerDeployment
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.postgres import PgResourceGovernancePartitionCleanupScenario


PARTITION_CLEANUP_SCENARIO_ID = "pg_resource_governance_partition_cleanup"
DEFAULT_AUX_PORTS = tuple(range(15862, 15870))


def build_report(case, success: bool) -> dict:
    if not success:
        return {
            "diagnosis": {"conditions": []},
            "outcome": {"changes": [], "verification": []},
            "summary": "No diagnosis or remediation was attempted.",
        }
    return copy.deepcopy(dict(case.reference_report))


def build_full_score_mock_agent(case):
    function_name = "aiopsbench_retention_worker_run"
    policy_table = getattr(case, "policy_table", None)
    mock_responses = [
        {
            "thinking": "先对齐真实 host pressure、filesystem I/O、BufferIO waiters 和数据库 query CPU，确认不是只看 CPU 关键词。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "host_pressure", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "filesystem_io", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "bufferio_waiters", "target": None}},
            ],
        },
        {
            "thinking": "查看 partition lifecycle 和 cleanup job，区分 retention cleanup 与备份、报表、host compressor 诱饵。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "partition_lifecycle", "target": None}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT * FROM {case.job_table} ORDER BY job_name; SELECT application_name, state, wait_event_type, wait_event FROM pg_stat_activity WHERE application_name LIKE 'pc-%' ORDER BY application_name;"}},
            ],
        },
        *(
            [
        {
            "thinking": "对照审批过的 legal-hold 名单检查 catalog 标记是否一致，并核对全部治理任务的 retention 是否还在业务保留边界内。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT job_name, enabled, paused, batch_size, retention_days FROM {case.job_table} ORDER BY job_name;"}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT * FROM {policy_table} ORDER BY 1; SELECT partition_name, legal_hold, state FROM {case.metadata_table} ORDER BY partition_name;"}},
            ],
        },
        {
            "thinking": "停止本场景的 retention worker，保留 pgbench/报表和 legal-hold 数据，不杀无关 query。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{case.cleanup_app_name}' AND pid <> pg_backend_pid();"}},
            ],
        },
        {
            "thinking": "用有界 batch 重放 retention cleanup，函数会真实 detach/drop 到期且非 legal-hold partition。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT {function_name}(1);"}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT {function_name}(1);"}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT {function_name}(1);"}},
            ],
        },
        {
            "thinking": "清理动作刚完成，先等待一个恢复窗口。",
            "delay_seconds": 120,
            "actions": [],
        },
            ]
            if policy_table
            else []
        ),
        {
            "thinking": "复查 catalog 与 job：治理会话可能在诊断期间又回写过配置，若 cleanup job 仍越界/被暂停，再终止配置代理会话并重新修正，然后确认无 detached 残留。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{getattr(case, 'sync_app_name', '')}';"}},
                {"api": "execute_sql", "args": {"sql_query": f"UPDATE {case.job_table} SET retention_days = 7, paused = false WHERE job_name = '{case.cleanup_job_name}' AND (retention_days < 7 OR retention_days > {case.max_retention_days} OR paused);"}},
                {"api": "execute_sql", "args": {"sql_query": f"UPDATE {case.metadata_table} SET legal_hold = false WHERE partition_name NOT IN (SELECT approved_partition_name FROM {policy_table}) AND legal_hold;"}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT partition_name, legal_hold, state FROM {case.metadata_table} ORDER BY partition_name; SELECT job_name, enabled, paused, retention_days FROM {case.job_table};"}},
            ],
        },
        {
            "thinking": "最终 SQL 校验已完成，再等待一个采样窗口后确认 pressure、filesystem I/O 和 OLTP SLO。",
            "delay_seconds": 180,
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "host_pressure", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "filesystem_io", "target": None}},
            ],
        },
        {"thinking": "cleanup replay 完成且保护边界完整，提交。", "actions": [{"api": "submit", "args": {"report": build_report(case, True)}}]},
    ]
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a PostgreSQL DBA agent.", use_native_tools=False)
    agent.set_mock_responses(mock_responses)
    return agent


def _check_ports(ports: tuple[int, ...]) -> None:
    if shutil.which("ss"):
        result = subprocess.run(["ss", "-ltnH"], capture_output=True, text=True, check=False)
        occupied = {
            int(match.group(1))
            for match in re.finditer(r":(\d+)\s+", result.stdout)
        }
        conflicts = sorted(set(ports) & occupied)
        if conflicts:
            raise RuntimeError(f"PG-RG-PC01 port preflight failed; ports already listen: {conflicts}")
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"PG-RG-PC01 port preflight failed; port is in use: {port}")


def _check_docker_names(names: tuple[str, ...]) -> None:
    if not shutil.which("docker"):
        raise RuntimeError("Docker is required for PG-RG-PC01")
    result = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}"], capture_output=True, text=True, check=False)
    existing = set(result.stdout.splitlines())
    conflicts = sorted(set(names) & existing)
    if conflicts:
        raise RuntimeError(f"PG-RG-PC01 Docker resource preflight failed; names already exist: {conflicts}")


def build_env(case, port: int, container_name: str, volume_name: str, network_name: str, image_name: str | None = None) -> PGEnv:
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=image_name or case.base_image_name,
        data_volume_name=volume_name,
        network_name=network_name,
        resources={
            "cpus": case.runtime.resources.container_cpu_limit,
            "memory_mb": case.runtime.resources.container_memory_mb,
            "shm_size": "256m",
            "disk_quota_mb": 8192,
        },
    )
    return PGEnv(workload=None, deployment=deployment, port=port)


def run_mode(args, scenario, case, mode, resource_suffix: str, run_config):
    container_name = f"{args.container_name}-{resource_suffix}".replace("_", "-")
    volume_name = f"{container_name}-data"
    network_name = f"{container_name}-network"
    env = build_env(case, args.port, container_name, volume_name, network_name, image_name=args.image)
    if mode == "mock":
        agent = build_full_score_mock_agent(case)
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a PostgreSQL DBA agent.", use_native_tools=False)
        agent.set_mock_responses([{"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": build_report(case, False)}}}])
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=10 if mode == "mock" else (3 if mode == "zero" else args.max_turns), run_config=run_config)
    return orchestrator.run()


def main() -> None:
    scenario = PgResourceGovernancePartitionCleanupScenario()
    parser = argparse.ArgumentParser(description="Run pg_resource_governance_partition_cleanup.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15861)
    parser.add_argument("--container-name", default=f"aiopsbench-{PARTITION_CLEANUP_SCENARIO_ID}")
    parser.add_argument("--image")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="off")
    parser.add_argument("--fault-snapshot-name")
    args = parser.parse_args()
    case = scenario.get_case(args.case)
    aux_ports = DEFAULT_AUX_PORTS[: case.aux_port_count]
    _check_ports((args.port, *aux_ports))
    resource_prefix = f"{PARTITION_CLEANUP_SCENARIO_ID}-{case.case_id}".replace("_", "-")
    _check_docker_names((f"aiopsbench-{resource_prefix}-mock", f"aiopsbench-{resource_prefix}-zero", f"aiopsbench-{resource_prefix}-llm"))
    os.environ.setdefault("AIOPS_PARTITION_CLEANUP_AUX_PORTS", ",".join(map(str, aux_ports)))
    run_config = OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode, fault_snapshot_name=args.fault_snapshot_name)
    modes = ("mock", "zero", "llm") if args.mode == "all" else (args.mode,)
    for mode in modes:
        result = run_mode(args, scenario, case, mode, mode, run_config)
        print(f"[{mode}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")
        if mode == "mock":
            assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True), json.dumps(result, ensure_ascii=False)
        elif mode == "zero":
            # The injector's real cleanup worker may complete the safe final state
            # before an empty submission is evaluated. Zero must lose diagnosis,
            # while OP/SP continue to reflect the observed final state.
            assert result["DiagnosisPass"] is False, json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    main()
