import argparse
import json
import os
import signal
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.runtime.config import required_run_timeout_seconds
from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgSystemFailureNoisyNeighborScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "不做诊断和修复，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


HARD_TIMEOUT_SEC = 420


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    deployment = PGDockerDeployment(container_name=container_name, port=port, image_name=image_name or case.base_image_name)
    return PGEnv(workload=None, deployment=deployment, port=port)


def build_full_score_mock_responses(scenario: PgSystemFailureNoisyNeighborScenario) -> list:
    if scenario.case_id == "single_archive_cpu_neighbor_simple":
        return [
            {
                "thinking": "先确认容器 CPU 压力，并检查低频数据库健康探针是否正常。",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}},
                    {"api": "query_metrics", "args": {"metric_type": "workload_activity", "target": None}},
                ],
            },
            {
                "thinking": "数据库探针正常但 CPU 仍高，查看主机进程以定位数据库外的活动资源消费者。",
                "action": {"api": "query_metrics", "args": {"metric_type": "cpu", "target": "top_processes"}},
            },
            {
                "thinking": "根因是外部 WAL 归档压缩进程抢占 CPU，不是数据库健康探针；仅终止该外部进程。",
                "action": {
                    "api": "manage_instance",
                    "args": {"action": "terminate_process", "target": scenario.external_process_name},
                },
            },
            {
                "thinking": "复查 CPU 与订单探针并提交修复结果。",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}},
                    {"api": "execute_sql", "args": {"sql_query": scenario.probe_sql}},
                    {
                        "api": "submit",
                        "args": {"report": scenario.reference_report},
                    },
                ],
            },
        ]
    activity_sql = """
        SET statement_timeout = '5s';
        SELECT application_name, state, wait_event_type, count(*)
        FROM pg_stat_activity
        WHERE datname = current_database()
          AND backend_type = 'client backend'
        GROUP BY application_name, state, wait_event_type
        ORDER BY application_name, state, wait_event_type;
    """
    locks_sql = """
        SET statement_timeout = '5s';
        SELECT count(*) AS lock_waiters
        FROM pg_stat_activity a
        JOIN pg_locks l ON l.pid = a.pid
        WHERE a.datname = current_database()
          AND NOT l.granted;
    """
    return [
        {
            "thinking": "先看系统 CPU、慢 SQL、连接和 TopSQL，区分当前资源压力与历史报表噪声。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None, "threshold_ms": 1000}},
                {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "topsql", "target": None, "limit": 10}},
            ],
        },
        {
            "thinking": "总体 CPU 高但 DB 内部信号不像根因；查看容器 top CPU 进程并继续用 SQL 排除锁等待和异常长活跃数据库会话。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "cpu", "target": "top_processes"}},
                {"api": "execute_sql", "args": {"sql_query": activity_sql}},
                {"api": "execute_sql", "args": {"sql_query": locks_sql}},
            ],
        },
        {
            "thinking": "根因是同容器外部 CPU worker 抢占配额，不是报表 SQL、连接池、锁或后台维护，终止外部压力源。",
            "action": {
                "api": "manage_instance",
                "args": {"action": "terminate_process", "target": scenario.external_process_name},
            },
        },
        {
            "thinking": "复查 CPU、慢查询、连接和业务探针，确认恢复。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(4);"}},
                {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}},
                {"api": "execute_sql", "args": {"sql_query": scenario.probe_sql}},
                {
                    "api": "submit",
                    "args": {"report": scenario.reference_report},
                },
            ],
        },
    ]


def _json_loads(raw: str) -> dict:
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _wait_for_visible_cpu_pressure(env: PGEnv, process_name: str, timeout_sec: int = 12) -> str:
    deadline = time.time() + timeout_sec
    last_cpu = ""
    while time.time() < deadline:
        last_cpu = env.query_metrics("cpu")
        if process_name in last_cpu:
            return last_cpu
        time.sleep(1.0)
    return last_cpu






def print_evaluation_basis(label: str, result: dict):
    print(f"[Evaluation:{label}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")

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



def run_mock_full(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Noisy Neighbor CPU Full-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureNoisyNeighborScenario()
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
    print("AiOpsBench PostgreSQL - Noisy Neighbor CPU Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureNoisyNeighborScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses([
        {
            "thinking": "不做诊断和修复，直接提交。",
            "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
        }
    ])
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str, port: int, container_name: str, model: str = None,
            config_path: str = "config/llm_config.json",
            max_turns: int = 20, run_config: OrchestratorRunConfig = None,
            max_output_tokens: int = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Noisy Neighbor CPU LLMAgent Path")
    print("=" * 60)

    max_turns = min(max_turns, 30)
    try:
        agent = build_experiment_agent(
            model=model, config_path=config_path, use_native_tools=True,
            max_output_tokens=max_output_tokens,
        )
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    scenario = PgSystemFailureNoisyNeighborScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
            print(
                "[LLMAGENT_BLOCKED] Agent reached max_turns without submit; "
                "increase --max-turns up to 30 and record this run as a blocker only if submit is still missing."
            )
    print_evaluation_basis("llm", result)
    print(f"[Result] LLMAgent passed={passed}")
    return passed


def main():
    parser = argparse.ArgumentParser(description="Run the PG noisy-neighbor CPU contention scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15720)
    parser.add_argument("--container-name", default="aiopsbench-pg-system-10")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgSystemFailureNoisyNeighborScenario()
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
    try:
        if args.mode in ("mock", "all"):
            run_mock_full(args.case, args.port, args.container_name, run_config)
        if args.mode in ("zero", "all"):
            run_mock_zero(args.case, args.port, args.container_name, run_config)
        if args.mode in ("llm", "all"):
            run_llm(args.case, args.port, args.container_name, args.model, args.config_path, args.max_turns,
                    run_config=run_config, max_output_tokens=args.max_output_tokens)
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
