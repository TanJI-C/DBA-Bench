import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgSystemFailureFdExhaustionScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload


def build_env(case, port: int, container_name: str, image_name: str, tool_profile: str = None) -> PGEnv:
    resources = PGDockerDeployment.DEFAULT_RESOURCES.copy()
    # Runtime prlimit is required to lower postmaster's nofile limit after PG is healthy.
    resources["cap_add"] = ["SYS_RESOURCE"]
    # 用 aiopsbench-pg-tpcds:latest 作 base image（已含 TPC-DS schema + data），
    # 无需 mount init.sql / workload_data。workload=TPCDSWorkload 让 env.deploy()
    # 调 workload.prepare() 时检测 init.sql/data 已存在就 skip，避免 dsdgen 重新生成。
    workload = TPCDSWorkload(scale=case.dataset_scale)
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        resources=resources,
        image_name=image_name or case.base_image_name,
    )
    return PGEnv(
        workload=workload,
        deployment=deployment,
        port=port,
        tool_profile=tool_profile or "general_knowledge",
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )


PG_STAT_ACTIVE_SQL = """
SELECT application_name, state, wait_event_type, wait_event, count(*) AS sessions,
       min(now() - state_change) AS oldest_state_age
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY application_name, state, wait_event_type, wait_event
ORDER BY sessions DESC, application_name;
"""

def build_full_score_mock_responses(scenario: PgSystemFailureFdExhaustionScenario) -> list:
    if scenario.case_id == "report_export_fd_exhaustion_simple":
        return [
            {
                "thinking": (
                    "Step 1: inspect the database log for the rejecting resource and compare "
                    "the one low-rate workload session with the failing report export."
                ),
                "actions": [
                    {
                        "api": "read_log",
                        "args": {
                            "log_type": "pg_log",
                            "lines": 5,
                        },
                    },
                    {"api": "query_metrics", "args": {"metric_type": "workload_activity"}},
                ],
            },
            {
                "thinking": (
                    "Step 2: Too many open files plus the relation fan-out statement points "
                    "to the postmaster process limit, so verify the running nofile limit."
                ),
                "actions": [
                    {"api": "manage_instance", "args": {"action": "get_config", "target": "nofile"}},
                    {
                        "api": "execute_sql",
                        "args": {
                            "sql_query": (
                                "SELECT calls, left(query, 160) FROM pg_stat_statements "
                                "WHERE query ILIKE '%report_export_simple%' "
                                "ORDER BY calls DESC LIMIT 1;"
                            )
                        },
                    },
                ],
            },
            {
                "thinking": (
                    "Raise the durable nofile baseline and restart PostgreSQL to apply it."
                ),
                "actions": [
                    {
                        "api": "manage_instance",
                        "args": {
                            "action": "set_config",
                            "target": "nofile",
                            "value": str(scenario.safe_nofile_limit),
                        },
                    },
                    {"api": "manage_instance", "args": {"action": "restart", "target": "postgres"}},
                ],
            },
            {
                "thinking": (
                    "Close out both orphaned ledger export runs (expired leases) in the control "
                    "schema so the scheduler does not resume or re-fan-out them, keeping the "
                    "leased backfill run and healthy runs untouched."
                ),
                "actions": [
                    {
                        "api": "execute_sql",
                        "args": {
                            "sql_query": (
                                "UPDATE report_export_control.export_job_run "
                                "SET status = 'CANCELLED', updated_at = now() "
                                f"WHERE job_run_id IN ('{scenario.stuck_job_run_id}', "
                                f"'{scenario.stuck_job_run_id_2}') "
                                "AND status = 'RUNNING';"
                            )
                        },
                    },
                    {
                        "api": "execute_sql",
                        "args": {
                            "sql_query": (
                                "SELECT job_run_id, job_family, status, lease_until FROM "
                                "report_export_control.export_job_run ORDER BY job_run_id;"
                            )
                        },
                    },
                ],
            },
            {
                "thinking": (
                    "Verify the running limit, replay the report fan-out query, and confirm "
                    "the orphan runs are closed while the leased backfill and protected "
                    "refresh results are intact."
                ),
                "actions": [
                    {"api": "manage_instance", "args": {"action": "get_config", "target": "nofile"}},
                    {"api": "execute_sql", "args": {"sql_query": scenario.validation_sql}},
                    {
                        "api": "execute_sql",
                        "args": {
                            "sql_query": (
                                "SELECT count(*), sum(row_count), sum(checksum) FROM "
                                "report_export_control.refresh_result;"
                            )
                        },
                    },
                    {
                        "api": "execute_sql",
                        "args": {
                            "sql_query": (
                                "SELECT status FROM report_export_control.export_job_run "
                                f"WHERE job_run_id = '{scenario.protected_job_run_id}';"
                            )
                        },
                    },
                ],
            },
            {
                "thinking": "The FD rejection is cleared and the health probe was unrelated.",
                "action": {
                    "api": "submit",
                    "args": {"report": scenario.reference_report},
                },
            },
        ]
    return [
        {
            "thinking": (
                "Step 1: 先采集表象噪声：慢查询、连接池活动和磁盘/检查点压力都可能是红鲱鱼，"
                "但不能直接按 max_connections 或 IO 事故处理。"
            ),
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None, "threshold_ms": 500}},
                {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
            ],
        },
        {
            "thinking": (
                "Step 2: 翻 PostgreSQL 日志，在慢 SQL、checkpoint、COPY/归档、probe 告警之间找真正拒绝新连接的错误。"
            ),
            "action": {"api": "read_log", "args": {"log_type": "pg_log", "lines": 260, "end_line": -1}},
        },
        {
            "thinking": (
                "Step 3: 日志里有 FD 错误后，读 OS/container nofile 限制，并排除 PG 内部文件限制和连接数上限。"
            ),
            "actions": [
                {"api": "manage_instance", "args": {"action": "get_config", "target": "nofile"}},
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SET statement_timeout = '3s'; "
                            "SELECT name, setting, unit, source "
                            "FROM pg_settings "
	                            "WHERE name IN ('max_files_per_process', 'max_connections', "
	                            "'superuser_reserved_connections');"
                        )
                    },
                },
                {"api": "execute_sql", "args": {"sql_query": PG_STAT_ACTIVE_SQL}},
            ],
        },
        {
            "thinking": (
                "Step 4: 根因是进程级 FD soft limit 过低；先止血提高 nofile，重启 PostgreSQL 让运行时限制生效。"
            ),
            "actions": [
                {
                    "api": "manage_instance",
                    "args": {
                        "action": "set_config",
                        "target": "nofile",
                        "value": str(scenario.safe_nofile_limit),
                    },
                },
                {"api": "manage_instance", "args": {"action": "restart", "target": "postgres"}},
            ],
        },
        {
            "thinking": (
                "Step 5: 修复后复查 nofile、跑失败的报表 fan-out SQL，并确认日志不再继续出现新的 FD 错误。"
            ),
            "actions": [
                {"api": "manage_instance", "args": {"action": "get_config", "target": "nofile"}},
                {"api": "execute_sql", "args": {"sql_query": scenario.validation_sql}},
                {"api": "read_log", "args": {"log_type": "pg_log", "lines": 80, "end_line": -1}},
            ],
        },
        {
            "thinking": "Step 6: 证据链闭合：FD 错误 + nofile 低 + 误导信号已排除 + 修复验证通过，提交结果。",
            "actions": [{
                "api": "submit",
                "args": {"report": scenario.reference_report},
            }],
        },
    ]









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
    print("AiOpsBench PostgreSQL - FD Exhaustion Full-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureFdExhaustionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=8)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - FD Exhaustion Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureFdExhaustionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, None)
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
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str,
    port: int,
    container_name: str = None,
    model: str = None,
    config_path: str = None,
    max_turns: int = 30,
    agent_name: str = "llm",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
    dbot_tool_profile: str = "general_knowledge",
    run_config: OrchestratorRunConfig = None,
    max_output_tokens: int = None,
    ) -> float:
    print("=" * 60)
    print(f"AiOpsBench PostgreSQL - FD Exhaustion {agent_name.upper()}Agent Path")
    print("=" * 60)

    max_turns = min(max_turns, 30)
    try:
        agent = build_agent(
            agent_name=agent_name,
            model=model,
            config_path=config_path or "config/llm_config.json",
            dbaiops_graph=dbaiops_graph,
            max_output_tokens=max_output_tokens,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"[{agent_name.upper()}AGENT_BLOCKED] {exc}")
        return 0.0

    # D-Bot 依赖 PGEnv 的 tool_profile；其他 agent 走默认 profile 即可。
    tool_profile = dbot_tool_profile if agent_name == "dbot" else None

    scenario = PgSystemFailureFdExhaustionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(
        case,
        port,
        container_name,
        None,
        tool_profile=tool_profile,
    )
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
                print(
                    f"[{agent_name.upper()}AGENT_BLOCKED] Agent reached max_turns without submit; "
                    "increase --max-turns up to 30 and record this run as a blocker only if submit is still missing."
                )
    print(f"[Result] {agent_name.upper()}Agent passed={passed}")
    return passed


def build_agent(
    agent_name: str,
    model: str = None,
    config_path: str = "config/llm_config.json",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
    max_output_tokens: int = None,
):
    return build_experiment_agent(
        model=model,
        config_path=config_path,
        use_native_tools=True,
        max_output_tokens=max_output_tokens,
    )


def main():
    parser = argparse.ArgumentParser(description="Run the PG file descriptor exhaustion scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15709)
    parser.add_argument("--container-name", default="aiopsbench-pg-system-09")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot. Default: general_knowledge "
                             "(better RCA on PG scenarios). Pass db_gpt for the DB-GPT semantic tool set.")
    scenario_definition = PgSystemFailureFdExhaustionScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )

    if args.max_turns > 30:
        raise ValueError("--max-turns must be <= 30")
    if args.mode in ("mock", "all"):
        run_mock_full(args.case, args.port, args.container_name, run_config)
    if args.mode in ("zero", "all"):
        run_mock_zero(args.case, args.port, f"{args.container_name}-zero", run_config)
    if args.mode in ("llm", "all"):
        run_llm(args.case,
            args.port,
            args.container_name,
            args.model,
            args.config_path,
            args.max_turns,
            agent_name=args.agent,
            dbaiops_graph=args.dbaiops_graph,
            dbot_tool_profile=args.dbot_tool_profile,
            run_config=run_config,
            max_output_tokens=args.max_output_tokens,
        )


if __name__ == "__main__":
    main()
