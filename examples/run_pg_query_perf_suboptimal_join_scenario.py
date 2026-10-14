import argparse
import json
import os
import re
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgQueryPerfSuboptimalJoinScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSXWorkload



# 讲解主线：健康基线来自 DBA session；故障来自报表应用角色的 role-level
# planner 配置漂移。普通 SHOW 参数不会直接泄底，Agent 需要从 topsql 追到角色设置。
DBA_SESSION_SETTINGS_SQL = (
    "SELECT name, setting, source "
    "FROM pg_settings "
    "WHERE name IN ('enable_hashjoin', 'enable_mergejoin') "
    "ORDER BY name;"
)
FAULT_CONTEXT_SQLS = (
    "SET enable_hashjoin = off;",
    "SET enable_mergejoin = off;",
)
RESET_CONTEXT_SQLS = (
    "RESET enable_hashjoin;",
    "RESET enable_mergejoin;",
)
REFRESH_APP_CONNECTION_SQL = (
    "SELECT pg_terminate_backend(pid) "
    "FROM pg_stat_activity "
    "WHERE application_name = 'aiopsbench_fp_suboptimal_join' "
    "AND pid <> pg_backend_pid();"
)


def build_full_score_mock_responses(case):
    target_explain_sql = (
        "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
        f"{case.fault_fingerprint_sql.rstrip(';')};"
    )
    role_settings_sql = (
        "SELECT r.rolname, d.datname, s.setconfig "
        "FROM pg_db_role_setting s "
        "JOIN pg_roles r ON r.oid = s.setrole "
        "LEFT JOIN pg_database d ON d.oid = s.setdatabase "
        f"WHERE r.rolname = '{case.app_role}' "
        "ORDER BY r.rolname, d.datname;"
    )
    topsql_role_sql = (
        "SELECT r.rolname, s.queryid, round(s.mean_exec_time::numeric, 2) AS mean_ms, s.calls, s.query "
        "FROM pg_stat_statements s "
        "JOIN pg_roles r ON r.oid = s.userid "
        f"WHERE r.rolname = '{case.app_role}' "
        "ORDER BY s.total_exec_time DESC LIMIT 5;"
    )
    reset_role_sqls = (
        f"ALTER ROLE {case.app_role} RESET enable_hashjoin;",
        f"ALTER ROLE {case.app_role} RESET enable_mergejoin;",
    )
    return [
    {
        "thinking": "先看 topsql 找出完整慢报表，再把 pg_stat_statements.userid 关联到执行它的应用角色。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "slow_queries"}},
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {"api": "execute_sql", "args": {"sql_query": topsql_role_sql}},
        ],
    },
    {
        "thinking": "DBA session 的 planner 参数正常，继续查报表角色的 role-level setting；这比直接 SHOW 当前参数更接近生产漂移。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": DBA_SESSION_SETTINGS_SQL}},
            {"api": "execute_sql", "args": {"sql_query": role_settings_sql}},
        ],
    },
    {
        "thinking": "按报表角色设置复现同一条完整 SQL 的执行计划，确认退化来自 Join 顺序/方法而不是简化 probe。",
        "actions": [
            *[{"api": "execute_sql", "args": {"sql_query": sql}} for sql in FAULT_CONTEXT_SQLS],
            {"api": "execute_sql", "args": {"sql_query": target_explain_sql}},
            *[{"api": "execute_sql", "args": {"sql_query": sql}} for sql in RESET_CONTEXT_SQLS],
        ],
    },
    {
        "thinking": "根因是报表角色级 planner 配置漂移，重置该角色的配置并刷新正在跑旧配置的报表连接。",
        "actions": [
            *[{"api": "execute_sql", "args": {"sql_query": sql}} for sql in reset_role_sqls],
            {"api": "execute_sql", "args": {"sql_query": REFRESH_APP_CONNECTION_SQL}},
        ],
    },
    {
        "thinking": "重新执行同一条原始复杂 SQL，验证默认 planner 下恢复 Hash/Merge Join 或显著减少 Nested Loop 探测。",
        "action": {"api": "execute_sql", "args": {"sql_query": target_explain_sql}},
    },
    {
        "thinking": "参数和计划已恢复，再次查看 topsql 确认 mean_exec_time 下降，提交诊断结果。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {"api": "submit", "args": {"report": PgQueryPerfSuboptimalJoinScenario().get_case('sales_report_role_planner_drift').reference_report}},
        ],
    },
    ]


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "不做诊断和修复，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def build_env(case, port: int, container_name: str, image_name: str = None, tool_profile: str = None) -> PGEnv:
    workload = TPCDSXWorkload(scale=case.dataset_scale)
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=workload.data_dir,
        dataset_manifest_path=workload.manifest_path,
        image_name=image_name or case.base_image_name,
        resources={
            "cpus": case.deployment_cpus,
            "memory_mb": case.deployment_memory_mb,
            "shm_size": case.deployment_shm_size,
            "disk_quota_mb": workload.disk_quota_mb,
        },
    )
    env_kwargs = {"workload": workload, "deployment": deployment, "port": port}
    if tool_profile:
        env_kwargs["tool_profile"] = tool_profile
    return PGEnv(**env_kwargs)













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
    print("AiOpsBench PostgreSQL - Suboptimal Join Full-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfSuboptimalJoinScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=9)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Suboptimal Join Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfSuboptimalJoinScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(ZERO_SCORE_MOCK_RESPONSES)
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str, port: int, container_name: str, model: str = None,
            config_path: str = "config/llm_config.json",
            max_turns: int = 20,
            run_config: OrchestratorRunConfig = None,
            agent_name: str = "llm",
            dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
            dbot_tool_profile: str = "general_knowledge") -> float:
    print("=" * 60)
    print(f"AiOpsBench PostgreSQL - Suboptimal Join {agent_name.upper()}Agent Path")
    print("=" * 60)

    max_turns = min(max_turns, 30)
    try:
        agent = build_agent(
            agent_name=agent_name,
            model=model,
            config_path=config_path,
            dbaiops_graph=dbaiops_graph,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"[{agent_name.upper()}AGENT_BLOCKED] {exc}")
        return 0.0

    tool_profile = dbot_tool_profile if agent_name == "dbot" else None

    scenario = PgQueryPerfSuboptimalJoinScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case,
        port,
        container_name,
        image_name=None,
        tool_profile=tool_profile,
    )
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
                print(
                    f"[{agent_name.upper()}AGENT_BLOCKED] Agent reached max_turns without submit; "
                    "this is recorded as an execution blocker, not a scenario setup failure."
                )
    print_evaluation_basis(agent_name, result)
    print(f"[Result] {agent_name.upper()}Agent passed={passed}")
    return passed


def build_agent(
    agent_name: str,
    model: str = None,
    config_path: str = "config/llm_config.json",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
):
    return build_experiment_agent(
        model=model,
        config_path=config_path,
        use_native_tools=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Run the PG suboptimal join query performance scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15458)
    parser.add_argument("--container-name", default="aiopsbench-pg")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--llm-config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot. Default: general_knowledge.")
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgQueryPerfSuboptimalJoinScenario()
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
        run_mock_full(args.case, args.port, args.container_name, run_config=run_config)
    if args.mode in ("zero", "all"):
        run_mock_zero(args.case, args.port, args.container_name, run_config=run_config)
    if args.mode in ("llm", "all"):
        run_llm(args.case,
            args.port,
            args.container_name,
            args.model,
            args.llm_config,
            args.max_turns,
            run_config=run_config,
            agent_name=args.agent,
            dbaiops_graph=args.dbaiops_graph,
            dbot_tool_profile=args.dbot_tool_profile,
        )


if __name__ == "__main__":
    main()
