import argparse
import copy
import json
import os
import signal
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.runtime.config import required_run_timeout_seconds
from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgSystemFailureConnectionStormScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "先看连接数监控，再按应用名和状态拆分，避免被支付/库存重试噪声带偏。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT query, calls, total_exec_time "
                        "FROM pg_stat_statements "
                        "ORDER BY total_exec_time DESC LIMIT 10;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT application_name, state, count(*) "
                        "FROM pg_stat_activity "
                        "WHERE backend_type = 'client backend' "
                        "GROUP BY application_name, state "
                        "ORDER BY count(*) DESC, application_name;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "连接槽接近上限，慢报表和探针是背景噪声；同一批 checkout-web-rw 会话 idle in transaction 成批堆积，需要看事务年龄和查询来源。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT pid, usename, application_name, state, wait_event_type, "
                    "now() - xact_start AS xact_age, now() - state_change AS state_age, "
                    "left(query, 120) AS query "
                    "FROM pg_stat_activity "
                    "WHERE backend_type = 'client backend' "
                    "AND pid <> pg_backend_pid() "
                    "ORDER BY application_name, state_change NULLS LAST;"
                )
            },
        },
    },
    {
        "thinking": "只清理 checkout-web-rw 的陈旧 idle in transaction 后端，不杀 payment/reporting/monitoring 噪声连接。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE pid <> pg_backend_pid() "
                    "AND application_name LIKE 'checkout-web-rw%' "
                    "AND state = 'idle in transaction';"
                )
            },
        },
    },
    {
        "thinking": "复查 pooler 泄漏已释放，并提交长期修复建议：修连接池事务归还逻辑和超时，不靠重启。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "ALTER ROLE checkout_app "
                        "SET idle_in_transaction_session_timeout = '30s';"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT application_name, state, count(*) "
                        "FROM pg_stat_activity "
                        "WHERE backend_type = 'client backend' "
                        "GROUP BY application_name, state; "
                        "SHOW max_connections;"
                    )
                },
            },
            {
                "api": "submit",
                "args": {"report": PgSystemFailureConnectionStormScenario().get_case('checkout_pool_idle_transaction_storm').reference_report},
            },
        ],
    },
]


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "不做诊断和修复，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]

SIMPLE_FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "先用一行聚合确认普通连接槽、目标 pool 泄漏量和无关会话量。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT current_setting('max_connections')::int AS max_connections, "
                    "count(*) FILTER (WHERE backend_type = 'client backend') AS client_connections, "
                    "count(*) FILTER (WHERE application_name LIKE 'checkout-web-rw%' "
                    "AND state = 'idle in transaction') AS leaked_pool_sessions, "
                    "count(*) FILTER (WHERE application_name LIKE 'payment-callback%' "
                    "OR application_name LIKE 'reporting-dashboard%') AS unrelated_sessions "
                    "FROM pg_stat_activity;"
                )
            },
        },
    },
    {
        "thinking": "列出目标 pool 后端并保留一个支付会话作对照，确认只清理泄漏事务。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT pid, application_name, state, now() - xact_start AS xact_age "
                    "FROM pg_stat_activity "
                    "WHERE (application_name LIKE 'checkout-web-rw%' "
                    "AND state = 'idle in transaction') "
                    "OR application_name = 'payment-callback-dispatcher-02' "
                    "ORDER BY application_name;"
                )
            },
        },
    },
    {
        "thinking": "仅终止 checkout-web-rw 的 idle in transaction 后端。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE pid <> pg_backend_pid() "
                    "AND application_name LIKE 'checkout-web-rw%' "
                    "AND state = 'idle in transaction';"
                )
            },
        },
    },
    {
        "thinking": "给 checkout 角色加非零 idle transaction timeout，避免相同 pool 泄漏再次占满连接槽。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "ALTER ROLE checkout_app "
                    "SET idle_in_transaction_session_timeout = '30s';"
                )
            },
        },
    },
    {
        "thinking": "复查泄漏连接已释放、连接数恢复余量且角色 guard 生效，再提交。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT count(*) FILTER (WHERE application_name LIKE 'checkout-web-rw%' "
                        "AND state = 'idle in transaction') AS leaked_pool_sessions, "
                        "count(*) FILTER (WHERE backend_type = 'client backend') AS client_connections, "
                        "count(*) FILTER (WHERE cfg LIKE "
                        "'idle_in_transaction_session_timeout=%') AS timeout_guards "
                        "FROM pg_stat_activity "
                        "CROSS JOIN LATERAL ("
                        "SELECT unnest(setconfig) AS cfg FROM pg_db_role_setting s "
                        "JOIN pg_roles r ON r.oid = s.setrole "
                        "WHERE r.rolname = 'checkout_app'"
                        ") AS role_guard;"
                    )
                },
            },
            {
                "api": "submit",
                "args": {"report": PgSystemFailureConnectionStormScenario().get_case('checkout_pool_leak_simple').reference_report},
            },
        ],
    },
]


HARD_TIMEOUT_SEC = 360


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    # 本场景必须降低连接上限并保留超管连接槽，才能真实复现普通业务新连接失败。
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=image_name or case.base_image_name,
        postgres_runtime_options=case.runtime.parameters.as_command_line(),
    )
    return PGEnv(workload=None, deployment=deployment, port=port)






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
    print("AiOpsBench PostgreSQL - Connection Storm Full-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureConnectionStormScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    template = (
        SIMPLE_FULL_SCORE_MOCK_RESPONSES
        if case.case_id == "checkout_pool_leak_simple"
        else FULL_SCORE_MOCK_RESPONSES
    )
    responses = copy.deepcopy(template)
    responses[-1]["actions"][-1]["args"]["report"] = case.reference_report
    agent.set_mock_responses(responses)
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=8)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Connection Storm Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureConnectionStormScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    responses = copy.deepcopy(ZERO_SCORE_MOCK_RESPONSES)
    responses[0]["action"]["args"]["report"] = EMPTY_REPORT
    agent.set_mock_responses(responses)
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
    print("AiOpsBench PostgreSQL - Connection Storm LLMAgent Path")
    print("=" * 60)

    max_turns = min(max_turns, 30)
    try:
        agent = build_experiment_agent(
            model=model,
            config_path=config_path,
            use_native_tools=True,
            max_output_tokens=max_output_tokens,
        )
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    scenario = PgSystemFailureConnectionStormScenario()
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
    parser = argparse.ArgumentParser(description="Run the PG connection storm and pool exhaustion scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15695)
    parser.add_argument("--container-name", default="aiopsbench-pg-system-05")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgSystemFailureConnectionStormScenario()
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
            run_llm(
                args.case,
                args.port,
                args.container_name,
                args.model,
                args.config_path,
                args.max_turns,
                run_config=run_config,
                max_output_tokens=args.max_output_tokens,
            )
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
