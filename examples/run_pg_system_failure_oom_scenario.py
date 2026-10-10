import argparse
import json
import os
import signal
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.runtime.config import required_run_timeout_seconds
from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.scenarios.postgres import PgSystemFailureOomScenario
from src.execution.deployment import PGDockerDeployment
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload


FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "数据库实例不可用，先确认连接状态并读取数据库日志判断进程退出原因。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
            {"api": "read_log", "args": {"log_type": "pg_log", "lines": 120}},
        ],
    },
    {
        "thinking": "日志指向内存分配失败；继续读取持久化配置来源和值，确认不是普通连接池或 checkpoint 噪声。",
        "actions": [
            {"api": "manage_instance", "args": {"action": "get_config", "target": "shared_buffers"}},
            {"api": "manage_instance", "args": {"action": "get_config", "target": "work_mem"}},
        ],
    },
    {
        "thinking": "auto.conf 中持久化内存配置超过当前 256MB cgroup 承载能力，清除危险配置后重启实例以脱离 crash recovery。",
        "actions": [
            {"api": "manage_instance", "args": {"action": "reset_config", "target": "shared_buffers"}},
            {"api": "manage_instance", "args": {"action": "reset_config", "target": "work_mem"}},
            {"api": "manage_instance", "args": {"action": "reboot", "target": "postgres"}},
        ],
    },
    {
        "thinking": "数据库已恢复，执行简单查询确认服务可用后提交。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT 1;"}},
            {"api": "submit", "args": {"report": PgSystemFailureOomScenario().get_case('restart_memory_config_oom').reference_report}},
        ],
    },
]


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "不做诊断和修复，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def build_full_score_mock_responses(case) -> list:
    if case.case_id != "restart_shared_buffers_oom_simple":
        return FULL_SCORE_MOCK_RESPONSES
    return [
        {
            "thinking": "Read the verified process-exit evidence and the one pre-restart probe.",
            "actions": [
                {
                    "api": "read_log",
                    "args": {
                        "log_type": "pg_log",
                        "lines": 5,
                        "match_key": "oom_kill",
                    },
                },
                {"api": "query_metrics", "args": {"metric_type": "workload_activity"}},
            ],
        },
        {
            "thinking": "Inspect the persistent memory settings against the 256MB cgroup.",
            "actions": [
                {"api": "manage_instance", "args": {"action": "get_config", "target": "shared_buffers"}},
                {"api": "manage_instance", "args": {"action": "get_config", "target": "work_mem"}},
            ],
        },
        {
            "thinking": "Clear only the unsafe shared_buffers override and reboot PostgreSQL.",
            "actions": [
                {"api": "manage_instance", "args": {"action": "reset_config", "target": "shared_buffers"}},
                {"api": "manage_instance", "args": {"action": "reboot", "target": "postgres"}},
            ],
        },
        {
            "thinking": "Verify safe settings and the calendar probe query.",
            "actions": [
                {"api": "manage_instance", "args": {"action": "get_config", "target": "shared_buffers"}},
                {"api": "manage_instance", "args": {"action": "get_config", "target": "work_mem"}},
                {"api": "execute_sql", "args": {"sql_query": case.tpcds_memory_safety_probe_sql}},
            ],
        },
        {
            "thinking": "The OOM restart loop is cleared without unrelated changes.",
            "action": {
                "api": "submit",
                "args": {"report": case.reference_report},
            },
        },
    ]


HARD_TIMEOUT_SEC = 900


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    workload = TPCDSWorkload(scale=case.dataset_scale)
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=workload.data_dir,
        image_name=image_name or case.base_image_name,
        # OOM 场景必须显式保留 256MB cgroup 限制，同时放大 /dev/shm，
        # 避免故障退化成纯 shm 配额不足而不是内存配置导致的进程退出。
        resources={
            "memory_mb": 256,
            "shm_size": "512m", # 与默认配置的 128m 不同，做了修改。
            "disk_quota_mb": workload.disk_quota_mb,
            "pg_ctl_start_timeout_sec": 180,
            "pg_ctl_restart_timeout_sec": 180,
            "pg_ctl_recovery_wait_sec": 15,
            "reboot_ready_timeout_sec": 360,
        },
        # 默认 entrypoint 会用命令行 -c 固定 shared_buffers/work_mem；
        # 本场景必须让 ALTER SYSTEM 写入的危险内存配置真实参与下次启动。
        postgres_runtime_options="-c shared_preload_libraries=pg_stat_statements",
    )
    return PGEnv(
        workload=workload,
        deployment=deployment,
        port=port,
        # OOM intentionally restarts PostgreSQL; keep the generic sampler
        # alive across that expected connection reset.
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )


def run_with_orchestrator(
    env, scenario, case, agent, run_config, max_turns: int,
):
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        max_turns=max_turns,
        run_config=run_config,
    )
    result = orchestrator.run()
    return result, orchestrator.action_history


def print_evaluation_basis(label: str, result: dict):
    print(f"[Evaluation:{label}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")

def run_mock_full(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - OOM Full-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureOomScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=8)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - OOM Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureOomScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses([
        {
            "thinking": "不做诊断和修复，直接提交。",
            "action": {
                "api": "submit",
                "args": {"report": EMPTY_REPORT},
            },
        }
    ])
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str, port: int, container_name: str, model: str = None,
            config_path: str = "config/llm_config.json",
            max_turns: int = 20,
            run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - OOM LLMAgent Path")
    print("=" * 60)

    max_turns = min(max_turns, 30)
    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] {exc}")
        return 0.0

    scenario = PgSystemFailureOomScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
            print(
                "[LLMAGENT_BLOCKED] Agent reached max_turns without submit; "
                "this is recorded as an LLM execution blocker, not a scenario setup failure."
            )
    print_evaluation_basis("llm", result)
    print(f"[Result] LLMAgent passed={passed}")
    return passed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["mock", "zero", "llm"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-pg-system-failure-oom")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgSystemFailureOomScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )

    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(required_run_timeout_seconds())

    if args.mode == "mock":
        passed = run_mock_full(args.case, args.port, args.container_name, run_config)
    elif args.mode == "zero":
        passed = run_mock_zero(args.case, args.port, f"{args.container_name}-zero", run_config)
    else:
        passed = run_llm(args.case, args.port, args.container_name, model=args.model,
                        config_path=args.config, max_turns=args.max_turns,
                        run_config=run_config)
    print(f"[Result] mode={args.mode}, passed={passed}")


if __name__ == "__main__":
    main()
