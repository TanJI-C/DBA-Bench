import argparse
import json
import os
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.base import evaluation_passed
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgResourceGovernanceResourceThrottlingScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig



FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "先查看 CPU 与 QPS，确认交易延迟升高是否伴随资源争抢。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "qps", "target": None}},
        ],
    },
    {
        "thinking": "检查活跃会话，区分在线交易账号和报表账号，并定位资源消耗查询。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT pid, usename, application_name, state, wait_event_type, "
                    "now() - query_start AS runtime, left(query, 160) AS query "
                    "FROM pg_stat_activity "
                    "WHERE usename IN ('oltp_user', 'report_user') "
                    "OR application_name IN ('tenant-revenue-export', 'tenant-revenue-export-preview', "
                    "'bi-dashboard-refresh', 'etl-ledger-backfill', 'orders-api-live-touch') "
                    "ORDER BY query_start NULLS LAST;"
                )
            },
        },
    },
    {
        "thinking": "确认 report_user 的当前资源限制，准备实施角色级隔离。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT r.rolname, r.rolconnlimit, COALESCE(array_to_string(s.setconfig, ','), '') AS role_settings "
                    "FROM pg_roles r "
                    "LEFT JOIN pg_db_role_setting s ON s.setrole = r.oid AND s.setdatabase = 0 "
                    "WHERE r.rolname IN ('report_user', 'analytics_user', 'etl_user');"
                )
            },
        },
    },
    {
        "thinking": "对报表账号实施 DB 级资源隔离：降低 work_mem 并限制最大连接数。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "ALTER ROLE report_user SET work_mem = '1MB';"}},
            {"api": "execute_sql", "args": {"sql_query": "ALTER ROLE report_user CONNECTION LIMIT 1;"}},
        ],
    },
    {
        "thinking": "终止当前正在抢占资源的 report_user 分析查询，让新限制对后续连接生效。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE usename = 'report_user' "
                    "AND application_name = 'tenant-revenue-export' "
                    "AND state = 'active'; "
                    "SELECT pg_sleep(1);"
                )
            },
        },
    },
    {
        "thinking": "验证分析会话已消失、角色限制已落地，并执行核心交易点查确认恢复。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT count(*) AS active_report_queries "
                        "FROM pg_stat_activity "
                        "WHERE usename = 'report_user' "
                        "AND application_name = 'tenant-revenue-export' "
                        "AND state = 'active';"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT r.rolconnlimit, COALESCE(array_to_string(s.setconfig, ','), '') "
                        "FROM pg_roles r "
                        "LEFT JOIN pg_db_role_setting s ON s.setrole = r.oid AND s.setdatabase = 0 "
                        "WHERE r.rolname = 'report_user';"
                    )
                },
            },
            {"api": "execute_sql", "args": {"sql_query": "SELECT amount FROM tenant_orders WHERE id = 42;"}},
        ],
    },
    {
        "thinking": "交易查询恢复，报表账号已隔离，提交结果。",
        "action": {"api": "submit", "args": {"report": PgResourceGovernanceResourceThrottlingScenario().get_case('tenant_report_role_throttling').reference_report}},
    },
]

ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "错误地执行无关 DDL。",
        "action": {"api": "execute_sql", "args": {"sql_query": "DROP TABLE IF EXISTS unrelated_zero_probe;"}},
    },
    {
        "thinking": "我不知道该怎么做，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def _rewrite_strings(value, replacements):
    if isinstance(value, str):
        for old, new in replacements:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_rewrite_strings(item, replacements) for item in value]
    if isinstance(value, tuple):
        return tuple(_rewrite_strings(item, replacements) for item in value)
    if isinstance(value, dict):
        return {
            _rewrite_strings(key, replacements): _rewrite_strings(item, replacements)
            for key, item in value.items()
        }
    return value


def _case_replacements(case):
    replacements = [
        ("tenant_report_role_throttling", case.case_id),
        ("tenant-revenue-export-preview", f"{case.root_application_name}-preview"),
        ("tenant-revenue-export", case.root_application_name),
        ("tenant_orders", case.table),
        ("oltp_user", case.oltp_role),
        ("report_user", case.report_role),
        ("analytics_user", case.noise_roles[0] if case.noise_roles else "analytics_user"),
    ]
    if len(case.noise_roles) > 1:
        replacements.append(("etl_user", case.noise_roles[1]))
    return tuple(replacements)


def build_full_score_mock_responses(case):
    return _rewrite_strings(FULL_SCORE_MOCK_RESPONSES, _case_replacements(case))


def build_zero_score_mock_responses(case):
    return _rewrite_strings(ZERO_SCORE_MOCK_RESPONSES, _case_replacements(case))



def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    # Custom deployment is only used to isolate this scenario from other local PG runs.
    deployment = PGDockerDeployment(container_name=container_name, port=port)
    deployment.image_name = image_name or case.base_image_name
    return PGEnv(workload=None, deployment=deployment, port=port)








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
    print("AiOpsBench PostgreSQL - Resource Throttling Full-Score Mock Path")
    print("=" * 60)

    scenario = PgResourceGovernanceResourceThrottlingScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=10)
    passed = evaluation_passed(result)
    print(f"[Assert] Mock full-passed path passed={passed}")
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Resource Throttling Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgResourceGovernanceResourceThrottlingScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_zero_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = evaluation_passed(result)
    print(f"[Assert] Mock zero-passed path passed={passed}")
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str, port: int, container_name: str, model: str = None,
            config_path: str = "config/llm_config.json",
            max_turns: int = 30, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Resource Throttling LLMAgent Path")
    print("=" * 60)

    scenario = PgResourceGovernanceResourceThrottlingScenario()
    case = scenario.get_case(case_id)
    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] Missing or invalid local LLM config: {exc}")
        return 0.0

    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = evaluation_passed(result)
    if not any(action.get("api") == "submit" for action in action_history):
        print(
            "[LLMAGENT_BLOCKED] Agent reached max_turns without submit; "
            "increase --max-turns up to 30 and record this run as a blocker only if submit is still missing."
        )
    print(f"[Result] LLMAgent passed={passed}")
    return passed


def main():
    parser = argparse.ArgumentParser(description="Run the PG resource throttling and role isolation scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-pg-resource-limits")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgResourceGovernanceResourceThrottlingScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )

    if args.mode in ("mock", "all"):
        run_mock_full(args.case, args.port, args.container_name, run_config)
    if args.mode in ("zero", "all"):
        run_mock_zero(args.case, args.port, args.container_name, run_config)
    if args.mode in ("llm", "all"):
        run_llm(args.case, args.port, args.container_name, args.model, args.config_path, args.max_turns, run_config)


if __name__ == "__main__":
    main()
