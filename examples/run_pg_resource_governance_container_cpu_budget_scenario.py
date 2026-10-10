"""Run PG-RG-MF02 with mock, zero or LLM agents."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.base import evaluation_passed
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.execution.deployment import PGDockerDeployment
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.postgres.resource_governance.container_cpu_budget import (
    CpuBudgetPGEnv,
    PgResourceGovernanceContainerCpuBudgetScenario,
)


DEFAULT_PG_PORT = 15831
DEFAULT_AUX_PORT = 15832
def _assert_port_range(port: int, aux_port: int, run_count: int) -> None:
    if port == aux_port:
        raise ValueError("PostgreSQL and auxiliary ports must be distinct")


def _mock_submit(case):
    return {"action": {"api": "submit", "args": {"report": case.reference_report}}}


def build_full_score_mock_responses(case):
    frozen_history = case.frozen_history is not None
    # The target bundle is placed by the public frozen history contract,
    # not at the live wall-clock tail. The response script is created before
    # the real capture/setup delay, so use the public maximum bounded history
    # window. It covers the aged target after setup without issuing an
    # unbounded query or relying on private timeline state.
    history_end = datetime.now(timezone.utc)
    history_spec = case.frozen_history
    history_query_start = history_end - timedelta(
        seconds=(history_spec.max_history_query_seconds if history_spec else 900)
    )
    history_query_end = history_end
    history_window = {
        "start_timestamp": history_query_start.strftime("%Y-%m-%d %H:%M:%S"),
        "end_timestamp": history_query_end.strftime("%Y-%m-%d %H:%M:%S"),
    }
    sibling_actions = [
        {
                "api": "manage_instance",
                "args": {
                "action": "set_peer_limit",
                "target": job.job_id,
                "value": str(quota),
            },
        }
        for job, quota in zip(case.sibling_jobs, case.reference_sibling_quota_cores)
    ]
    policy_binding_actions = (
        [{
            "api": "manage_instance",
            "args": {
                "action": "set_scheduling_weight",
                "target": "postgres",
                "value": str(case.initial_db_weight),
            },
        }]
        if case.fault_db_weight != case.initial_db_weight else []
    )
    first_observations = (
        [
            {"api": "query_metrics", "args": {"metric_type": "host_cpu", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "host_cpu_pressure", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "cgroup_cpu_usage", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "cgroup_cpu_throttle", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "process_cpu", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "service_slo", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "job_progress", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "workload_activity", "limit": 20}},
            {"api": "read_log", "args": {"log_type": "operation_event", **history_window, "target": "postgres", "filters": {"event_type": "quota_revision"}, "lines": 100}},
        ]
        if frozen_history else [
            {"api": "query_metrics", "args": {"metric_type": "resource_history", "target": None}},
        ]
    )
    final_observations = (
        [
            {"api": "query_metrics", "args": {"metric_type": "cgroup_cpu_usage", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "cgroup_cpu_throttle", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "service_slo", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "job_progress", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "workload_activity", "limit": 20}},
        ]
        if frozen_history else [
            {"api": "query_metrics", "args": {"metric_type": "resource_history", "target": None}},
        ]
    )
    return [
        {
            "thinking": "先读取跨层 CPU、quota、throttle、PSI 和业务历史，确认 host 仍有 headroom，不能只看 PostgreSQL CPU 百分比。",
            "actions": first_observations,
        },
        {
            "thinking": "先恢复数据库正确的 workload-class 策略绑定，阻止协调器继续回写低 quota；再在保留必要 sibling job 的前提下完成有界预算重分配。",
            "actions": [
                *sibling_actions,
                *policy_binding_actions,
                {"api": "manage_instance", "args": {"action": "set_resource_limit", "target": "postgres", "value": str(case.reference_db_quota_cores)}},
            ],
        },
        {
            "thinking": "重读 cgroup 和 workload replay，确认 OLTP p99、report throughput、job progress、host headroom 和 pressure 都满足目标。",
            "actions": final_observations,
        },
        _mock_submit(case),
    ]


def build_zero_score_mock_responses(case):
    if case.case_id == "db_quota_throttle":
        return [{"action": {"api": "submit", "args": {"report": EMPTY_REPORT}}}]
    first_job = case.sibling_jobs[0].job_id
    return [
        {
            "thinking": "错误地把资源治理当作无限扩容和停止必要备份。",
            "actions": [
                {"api": "manage_instance", "args": {"action": "set_resource_limit", "target": "postgres", "value": "max"}},
                {"api": "manage_instance", "args": {"action": "stop_sibling", "target": first_job, "value": "stop"}},
            ],
        },
        {
            "thinking": "不验证业务结果，直接提交空报告。",
            "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
        },
    ]


def build_equivalent_score_mock_responses(case):
    """Exercise a safe equivalent policy path beyond the quota-only reference."""
    responses = build_full_score_mock_responses(case)
    responses[1]["actions"].insert(0, {
        "api": "manage_instance",
        "args": {
            "action": "set_scheduling_weight",
            "target": "postgres",
            "value": "100",
        },
    })
    return responses


def build_env(case, port: int, container_name: str) -> CpuBudgetPGEnv:
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=case.base_image_name,
        resources={
            "cpus": case.runtime.resources.container_cpu_limit,
            "memory_mb": case.runtime.resources.container_memory_mb,
            "shm_size": "256m",
            "disk_quota_mb": 8192,
        },
    )
    return CpuBudgetPGEnv(workload=None, deployment=deployment, port=port)


def run_mode(case, mode: str, port: int, aux_port: int, model: str, reasoning_effort: str, config_path: str, max_turns: int, run_config, container_name: str | None = None):
    scenario = PgResourceGovernanceContainerCpuBudgetScenario()
    env = build_env(
        case,
        port,
        container_name or f"aiopsbench-pg-{scenario.scenario_id}-{case.case_id}-{mode}",
    )
    print(json.dumps({"scenario": scenario.scenario_id, "case": case.case_id, "ports": {"postgres": port, "auxiliary_reserved": aux_port}}, ensure_ascii=False))
    if mode in {"mock", "mock-equivalent"}:
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        responses = (
            build_equivalent_score_mock_responses(case)
            if mode == "mock-equivalent"
            else build_full_score_mock_responses(case)
        )
        agent.set_mock_responses(responses)
        turns = 12
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(build_zero_score_mock_responses(case))
        turns = 4
    else:
        agent = build_experiment_agent(
            model=model,
            config_path=config_path,
            use_native_tools=True,
            reasoning_effort=reasoning_effort if os.environ.get("AIOPS_AGENT_MODE") in {"llm", "v-expel"} else None,
        )
        turns = min(max_turns, 30)
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        max_turns=turns,
        run_config=run_config,
    )
    result = orchestrator.run()
    passed = evaluation_passed(result)
    print(f"[{mode}] case={case.case_id} DiagnosisPass={result['DiagnosisPass']} OutcomePass={result['OutcomePass']} SafePass={result['SafePass']} passed={passed}")
    if mode in {"mock", "mock-equivalent"}:
        expected_diagnosis = True if case.evaluator.diagnosis_applicable else None
        assert result["DiagnosisPass"] is expected_diagnosis and result["OutcomePass"] is True and result["SafePass"] is True, json.dumps(result, ensure_ascii=False)
    if mode == "zero":
        expected_diagnosis = False if case.evaluator.diagnosis_applicable else None
        assert result["DiagnosisPass"] is expected_diagnosis and result["OutcomePass"] is False and result["SafePass"] is False, json.dumps(result, ensure_ascii=False)
    return result


def main() -> None:
    scenario = PgResourceGovernanceContainerCpuBudgetScenario()
    parser = argparse.ArgumentParser(description="Run PG-RG-MF02 PostgreSQL container CPU budget governance.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "mock-equivalent", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=DEFAULT_PG_PORT)
    parser.add_argument("--aux-port", type=int, default=DEFAULT_AUX_PORT)
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high", "xhigh"], default="xhigh")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--container-name")
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="off")
    parser.add_argument("--fault-snapshot-name")
    args = parser.parse_args()
    modes = ("mock", "zero", "llm") if args.mode == "all" else (args.mode,)
    _assert_port_range(args.port, args.aux_port, len(modes))
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
        history_seed=args.seed,
    )
    for index, mode in enumerate(modes):
        run_mode(
            scenario.get_case(args.case),
            mode,
            args.port + index,
            args.aux_port + index,
            args.model,
            args.reasoning_effort,
            args.config_path,
            args.max_turns,
            run_config,
            args.container_name,
        )


if __name__ == "__main__":
    main()
