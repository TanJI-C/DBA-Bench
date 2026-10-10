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
from src.scenarios.postgres import PgSystemFailureTempFileExplosionScenario
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload



# 模拟模式仍然使用真实 PostgreSQL，只是把智能体的动作固定下来。
# 下面这组响应表示一条预期满分的诊断与恢复路径。
FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "先确认磁盘和慢查询视角，避免被普通连接、BI 历史 SQL 或监控探针误导。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "disk_usage"}},
            {"api": "query_metrics", "args": {"metric_type": "slow_queries", "threshold_ms": 500}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT a.pid, a.usename, a.application_name, a.state, a.wait_event, "
                        "now() - a.query_start AS runtime, left(a.query, 240) AS query_text, "
                        "t.name AS temp_file, t.size "
                        "FROM pg_stat_activity a "
                        "JOIN pg_ls_tmpdir() t ON t.name LIKE 'pgsql_tmp' || a.pid || '.%' "
                        "WHERE a.pid <> pg_backend_pid() "
                        "AND a.state = 'active' "
                        "ORDER BY t.size DESC;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT r.rolname, d.datname, q.query, q.calls, q.total_exec_time, "
                        "q.temp_blks_read, q.temp_blks_written, "
                        "(SELECT setting FROM pg_settings WHERE name = 'work_mem') AS work_mem, "
                        "(SELECT setting FROM pg_settings WHERE name = 'temp_file_limit') AS temp_file_limit "
                        "FROM pg_stat_statements q "
                        "JOIN pg_roles r ON r.oid = q.userid "
                        "JOIN pg_database d ON d.oid = q.dbid "
                        "WHERE q.temp_blks_written > 0 "
                        "ORDER BY q.temp_blks_written DESC "
                        "LIMIT 10;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "临时文件名中的 PID 关联到 report_batch 的 nightly_margin_rollup，终止这个批处理并给该角色加临时文件上限。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT pg_terminate_backend(pid) "
                        "FROM pg_stat_activity "
                        "WHERE pid <> pg_backend_pid() "
                        "AND state = 'active' "
                        "AND usename = 'report_batch' "
                        "AND application_name = 'batch_rollup_scheduler' "
                        "AND query ILIKE '%nightly_margin_rollup%';"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER ROLE report_batch SET temp_file_limit = '64MB';"},
            },
        ],
    },
    {
        "thinking": "复查 pgsql_tmp 已释放、问题批处理消失、角色级 guard 生效，然后提交。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(1);"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT COALESCE(SUM(size), 0) FROM pg_ls_tmpdir();"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT "
                        "(SELECT count(*) FROM pg_stat_activity "
                        " WHERE pid <> pg_backend_pid() "
                        " AND state = 'active' "
                        " AND usename = 'report_batch' "
                        " AND application_name = 'batch_rollup_scheduler') AS active_batch_backends, "
                        "EXISTS ("
                        " SELECT 1 FROM pg_db_role_setting s "
                        " JOIN pg_roles r ON r.oid = s.setrole "
                        " CROSS JOIN LATERAL unnest(s.setconfig) cfg "
                        " WHERE r.rolname = 'report_batch' "
                        " AND lower(cfg) = 'temp_file_limit=64mb'"
                        ") AS role_guard;"
                    )
                },
            },
            {"api": "submit", "args": {"report": PgSystemFailureTempFileExplosionScenario().get_case('nightly_margin_temp_exhaustion').reference_report}},
        ],
    },
]


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "不做诊断和修复，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]

def build_simple_full_score_mock_responses(case) -> list:
    return [
        {
            "thinking": "先确认 temp 存储异常，并检查低频 date probe 是否只是正常背景。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "disk_usage"}},
                {"api": "query_metrics", "args": {"metric_type": "workload_activity"}},
            ],
        },
        {
            "thinking": "把 pgsql_tmp 文件 PID 关联到活动会话、角色、应用和 batch job。",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT a.pid, a.usename, a.application_name, a.state, "
                        "left(a.query, 240), t.name, t.size "
                        "FROM pg_stat_activity a "
                        "JOIN pg_ls_tmpdir() t ON t.name LIKE 'pgsql_tmp' || a.pid || '.%' "
                        "WHERE a.pid <> pg_backend_pid() ORDER BY t.size DESC;"
                    )
                },
            },
        },
        {
            "thinking": "仅终止 report batch 的 spill 会话，并给该角色设置 48MB temp guard。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                            f"WHERE usename = '{case.culprit_role}' "
                            f"AND application_name = '{case.culprit_application}' "
                            f"AND query ILIKE '%job={case.culprit_job} %';"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"ALTER ROLE {case.culprit_role} SET temp_file_limit = '48MB';"
                        )
                    },
                },
            ],
        },
        {
            "thinking": "等待临时文件释放，验证 batch 消失和 role guard 生效后提交。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(1);"}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT COALESCE(SUM(size), 0) FROM pg_ls_tmpdir();"}},
                {
                    "api": "submit",
                    "args": {"report": case.reference_report},
                },
            ],
        },
    ]


HARD_TIMEOUT_SEC = 420


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    workload = TPCDSWorkload(scale=case.dataset_scale)
    env = PGEnv(workload=workload, port=port)
    # 只在本场景首次 docker run 时挂载 pgsql_tmp 的 tmpfs。
    # injector 只负责制造数据库压力，不再负责重建容器。
    env.deployment.resources["tmpfs_mounts"] = [
        f"{case.pgdata}/base/pgsql_tmp:size={case.tmpfs_size_mb}m"
    ]
    env.deployment.container_name = container_name
    env.deployment.image_name = image_name or case.base_image_name
    return env



















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
    print("AiOpsBench PostgreSQL - Temp File Explosion Full-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureTempFileExplosionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(
        build_simple_full_score_mock_responses(case)
        if case.case_id == "daily_sales_temp_exhaustion_simple"
        else FULL_SCORE_MOCK_RESPONSES
    )
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=8)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Temp File Explosion Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureTempFileExplosionScenario()
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
            max_turns: int = 20, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Temp File Explosion LLMAgent Path")
    print("=" * 60)

    max_turns = min(max_turns, 30)
    try:
        agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)
    except Exception as exc:
        print(f"[LLMAGENT_BLOCKED] {exc}")
        return 0.0

    scenario = PgSystemFailureTempFileExplosionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
            print(
                "[LLMAGENT_BLOCKED] Agent reached max_turns without submit; "
                "increase --max-turns up to 30 and record the trace as a blocker only if submit is still missing."
            )
    print_evaluation_basis("llm", result)
    print(f"[Result] LLMAgent passed={passed}")
    return passed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["mock", "zero", "llm"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-pg-system-failure-temp-file-explosion")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgSystemFailureTempFileExplosionScenario()
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
        passed = run_mock_full(args.case, args.port, args.container_name, run_config=run_config)
    elif args.mode == "zero":
        passed = run_mock_zero(args.case, args.port, f"{args.container_name}-zero", run_config=run_config)
    else:
        passed = run_llm(args.case, args.port, args.container_name, model=args.model,
                        config_path=args.config, max_turns=args.max_turns, run_config=run_config)
    print(f"[Result] mode={args.mode}, passed={passed}")


if __name__ == "__main__":
    main()
