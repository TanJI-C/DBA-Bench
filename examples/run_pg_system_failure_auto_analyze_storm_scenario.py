import argparse
import copy
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.scenarios.postgres import PgSystemFailureAutoAnalyzeStormScenario
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload



# 讲解主线：本入口脚本调低 autovacuum analyze 阈值并更新大表，
# 让后台 autovacuum ANALYZE worker 周期性抢 I/O。Agent 需要从 disk_io、
# pg_stat_activity 和 pg_settings 关联出后台维护任务，而不是只盯业务 SQL。
ANALYZE_ACTIVITY_SQL = (
    "SELECT pid, backend_type, state, wait_event_type, wait_event, query "
    "FROM pg_stat_activity "
    "WHERE pid <> pg_backend_pid() "
    "AND (backend_type = 'autovacuum worker' "
    "     OR query ILIKE '%ANALYZE%' "
    "     OR query ILIKE '%autovacuum%') "
    "ORDER BY query_start NULLS LAST;"
)

CONFIG_SQL = (
    "SELECT name, setting, unit, source "
    "FROM pg_settings "
    "WHERE name IN ('autovacuum_analyze_scale_factor', "
    "'autovacuum_analyze_threshold', 'autovacuum_naptime', "
    "'autovacuum_max_workers') "
    "ORDER BY name;"
)

TABLE_STATS_SQL = (
    "SELECT relname, n_mod_since_analyze, last_autoanalyze, last_analyze "
    "FROM pg_stat_user_tables "
    "WHERE relname IN ('customer', 'store_sales', 'inventory', 'web_sales', 'catalog_sales', "
    "'store_returns', 'customer_demographics') "
    "ORDER BY relname;"
)

RELOPTIONS_SQL = (
    "SELECT relname, reloptions, reltuples::bigint FROM pg_class "
    "WHERE oid IN ('web_sales'::regclass, 'inventory'::regclass, "
    "'store_returns'::regclass, 'customer_demographics'::regclass) "
    "ORDER BY relname;"
)


FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Start from the reported periodic I/O spikes and inspect disk I/O metrics.",
        "action": {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
    },
    {
        "thinking": "Check normal workload activity so report queries and background DML are treated as context, not the root cause.",
        "action": {"api": "query_metrics", "args": {"metric_type": "workload_activity", "target": None}},
    },
    {
        "thinking": "The I/O bursts need to be correlated with active database work. Check for maintenance/analyze workers.",
        "action": {"api": "execute_sql", "args": {"sql_query": ANALYZE_ACTIVITY_SQL}},
    },
    {
        "thinking": "Differentiate target-table analyze triggers from non-target table and workload noise by checking table modification counters.",
        "action": {"api": "execute_sql", "args": {"sql_query": TABLE_STATS_SQL}},
    },
    {
        "thinking": "Maintenance workers are running during the spikes, so inspect analyze scale factor, threshold, and naptime.",
        "action": {"api": "execute_sql", "args": {"sql_query": CONFIG_SQL}},
    },
    {
        "thinking": "Per-table reloptions override the global GUCs, so compare every override row via reltuples arithmetic: only a trigger far below the recurring-storm band is a fault candidate, healthy tuning stays above it.",
        "action": {"api": "execute_sql", "args": {"sql_query": RELOPTIONS_SQL}},
    },
    {
        "thinking": "The analyze threshold and naptime are too aggressive, and only web_sales keeps a storm-level per-table override while inventory, store_returns, and customer_demographics hold healthy above-band tuning that must survive. Restore the global settings and clear only the web_sales override.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER SYSTEM SET autovacuum_analyze_scale_factor = '0.1';"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER SYSTEM SET autovacuum_analyze_threshold = '50';"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER SYSTEM RESET autovacuum_naptime;"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "ALTER TABLE web_sales RESET "
                        "(autovacuum_analyze_scale_factor, autovacuum_analyze_threshold);"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SELECT pg_reload_conf();"},
            },
        ],
    },
    {
        "thinking": "The unsafe analyze settings have been restored; submit the diagnosis and repair summary.",
        "action": {"api": "submit", "args": {"report": PgSystemFailureAutoAnalyzeStormScenario().get_case('sales_tables_auto_analyze_storm').reference_report}},
    },
]


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Do not inspect or repair anything; submit immediately.",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]

SIMPLE_TABLE_STATS_SQL = (
    "SELECT relname, n_mod_since_analyze, last_autoanalyze, last_analyze, autoanalyze_count "
    "FROM pg_stat_user_tables "
    "WHERE relname IN ('store_sales', 'store_returns') "
    "ORDER BY relname;"
)

SIMPLE_RELOPTIONS_SQL = (
    "SELECT relname, reloptions FROM pg_class "
    "WHERE oid = 'store_returns'::regclass;"
)

SIMPLE_FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "先检查 analyze 触发参数，确认是否存在会造成重复维护的全局配置。",
        "action": {"api": "execute_sql", "args": {"sql_query": CONFIG_SQL}},
    },
    {
        "thinking": "检查目标 sales 表和同级 returns 表的修改量与最新 autoanalyze 时间，识别持续风暴的表。",
        "action": {"api": "execute_sql", "args": {"sql_query": SIMPLE_TABLE_STATS_SQL}},
    },
    {
        "thinking": "检查真实低频工作负载，排除 calendar health probe 是周期 I/O 根因。",
        "action": {"api": "query_metrics", "args": {"metric_type": "workload_activity", "target": None}},
    },
    {
        "thinking": "store_returns 在修改量极小的情况下仍被高频 autoanalyze，检查它是否带表级 reloptions 覆盖。",
        "action": {"api": "execute_sql", "args": {"sql_query": SIMPLE_RELOPTIONS_SQL}},
    },
    {
        "thinking": "恢复全局安全 analyze 阈值和 naptime，并清除 store_returns 的表级风暴覆盖，最后 reload 配置。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER SYSTEM SET autovacuum_analyze_scale_factor = '0.1';"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER SYSTEM SET autovacuum_analyze_threshold = '50';"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER SYSTEM RESET autovacuum_naptime;"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "ALTER TABLE store_returns RESET "
                        "(autovacuum_analyze_scale_factor, autovacuum_analyze_threshold);"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SELECT pg_reload_conf();"},
            },
        ],
    },
    {
        "thinking": "给 SIGHUP reload 一个确定的短等待窗口。",
        "action": {"api": "execute_sql", "args": {"sql_query": "SELECT pg_sleep(1);"}},
    },
    {
        "thinking": "复查三项 analyze 配置已恢复安全值，store_returns 风暴应停止。",
        "action": {"api": "execute_sql", "args": {"sql_query": CONFIG_SQL}},
    },
    {
        "thinking": "安全配置已生效，提交目标表 auto-analyze 风暴诊断。",
        "action": {
            "api": "submit",
            "args": {
                "report": PgSystemFailureAutoAnalyzeStormScenario().get_case('store_sales_auto_analyze_storm_simple').reference_report
            },
        },
    },
]


def build_env(case, port: int, container_name: str, image_name: str = None, tool_profile: str = None) -> PGEnv:
    # 使用默认 TPC-DS 部署即可；本场景的资源压力来自 autovacuum analyze 配置和表更新。
    workload = TPCDSWorkload(scale=case.dataset_scale)
    env_kwargs = {"workload": workload, "port": port}
    if tool_profile:
        env_kwargs["tool_profile"] = tool_profile
    env = PGEnv(**env_kwargs)
    # 共享宿主机磁盘争抢会让 TPC-DS COPY 装载超过默认 600s 初始化窗口，放宽到 40 分钟。
    env.deployment.initialization_timeout_seconds = 2400
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
    print("AiOpsBench PostgreSQL - Auto-Analyze Storm Full-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureAutoAnalyzeStormScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    template = (
        SIMPLE_FULL_SCORE_MOCK_RESPONSES
        if case.case_id == "store_sales_auto_analyze_storm_simple"
        else FULL_SCORE_MOCK_RESPONSES
    )
    responses = copy.deepcopy(template)
    responses[-1]["action"]["args"]["report"] = case.reference_report
    agent.set_mock_responses(responses)
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=8)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Auto-Analyze Storm Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureAutoAnalyzeStormScenario()
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
            max_turns: int = 20,
            run_config: OrchestratorRunConfig = None,
            agent_name: str = "llm",
            dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
            dbot_tool_profile: str = "general_knowledge") -> float:
    print("=" * 60)
    print(f"AiOpsBench PostgreSQL - Auto-Analyze Storm {agent_name.upper()}Agent Path")
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

    scenario = PgSystemFailureAutoAnalyzeStormScenario()
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
    parser = argparse.ArgumentParser(description="Run the PG auto-analyze storm query performance scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15459)
    parser.add_argument("--container-name", default="aiopsbench-pg-queryperf-09")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--llm-config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot. Default: general_knowledge.")
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgSystemFailureAutoAnalyzeStormScenario()
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
