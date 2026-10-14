import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgQueryPerfImplicitTypeConversionScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSXWorkload



# 讲解主线：完整 tpcdsx 订单排查 SQL 在 branch_order_line receipt membership 谓词上用整数 key
# 对比支持请求表里的 numeric[] receipt watchlist，导致普通整数索引失效。fixed SQL 只恢复类型一致比较。
def reference_report_for_case(case):
    if case.case_id == "branch_order_implicit_cast_simple":
        return {
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "order exception triage query",
                        "entity": "branch_order_implicit_cast_simple",
                        "evidence": [
                            "scripted diagnostic actions observed order exception triage query"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": "request values have wrong type",
                        "entity": "branch_order_implicit_cast_simple",
                        "evidence": [
                            "scripted diagnostic actions observed request values have wrong type"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": "implicit cast bypasses integer index",
                        "entity": "branch_order_implicit_cast_simple",
                        "evidence": [
                            "scripted diagnostic actions observed implicit cast bypasses integer index"
                        ],
                    },
                ]
            },
            "outcome": {
                "changes": ["cast request values to integer before comparison"],
                "verification": ["typed request query was verified"],
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification.",
        }
    return case.reference_report


def build_full_score_mock_responses(case):
    fault_explain_sql = (
        f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {case.fault_fingerprint_sql.rstrip(';')};"
    )
    index_sql = (
        "SELECT indexname, indexdef FROM pg_indexes "
        f"WHERE tablename = '{case.table}' "
        f"AND indexdef ILIKE '%{case.column}%';"
    )
    type_stats_sql = (
        "SELECT a.attname, pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type, "
        "s.n_distinct, s.correlation "
        "FROM pg_attribute a "
        f"LEFT JOIN pg_stats s ON s.tablename = '{case.table}' AND s.attname = a.attname "
        f"WHERE a.attrelid = '{case.table}'::regclass "
        f"AND a.attname IN ('{case.column}', 'bol_product_sk');\n"
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name = 'support_triage_request' "
        "AND column_name IN ('receipt_watchlist');"
    )
    return [
    {
        "thinking": "先看 topsql 和慢查询，确认真正慢的是完整订单排查 SQL，而不是随便挑一条短 probe。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {"api": "query_metrics", "args": {"metric_type": "slow_queries"}},
        ],
    },
    {
        "thinking": "对完整故障 SQL 做 EXPLAIN ANALYZE；SQL 文本没有 ::/CAST，真正线索要从计划里看 branch_order_line 上是否出现 Seq Scan、扫描放大和 membership 谓词异常。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": fault_explain_sql},
        },
    },
    {
        "thinking": "执行计划显示 bol_receipt_number 在 ANY 过滤里被隐式转成 numeric，需要检查目标列索引、列类型、请求上下文表参数类型和统计信息，排除缺索引/统计陈旧干扰。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": index_sql + "\n" + type_stats_sql},
        },
    },
    {
        "thinking": "索引存在且 bol_receipt_number 是 integer，请求上下文表 receipt watchlist 是 numeric[]，且可能混有小数噪声；修复是在 request_context 中保留整数值后规整为 integer[]，再实际执行完整 fixed 业务 SQL。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": case.fixed_fingerprint_sql},
        },
    },
    {
        "thinking": "完整 fixed SQL 已走整数索引路径且运行时间下降，提交结果。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {"api": "submit", "args": {"report": reference_report_for_case(case)}},
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
    # TPCDSXWorkload 负责基础 schema/data；injector 只准备本场景索引状态和 fault fingerprint。
    workload = TPCDSXWorkload(scale=case.dataset_scale)
    deployment = PGDockerDeployment(
        container_name=container_name,
        postgres_user="postgres",
        postgres_password="password",
        postgres_db="testdb",
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
    print("AiOpsBench PostgreSQL - Implicit Type Conversion Full-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfImplicitTypeConversionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=6)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Implicit Type Conversion Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfImplicitTypeConversionScenario()
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
            max_turns: int = 20, run_config: OrchestratorRunConfig = None,
            agent_name: str = "llm",
            dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
            dbot_tool_profile: str = "general_knowledge") -> float:
    print("=" * 60)
    print(f"AiOpsBench PostgreSQL - Implicit Type Conversion {agent_name.upper()}Agent Path")
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

    scenario = PgQueryPerfImplicitTypeConversionScenario()
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
    parser = argparse.ArgumentParser(description="Run the PG implicit type conversion query performance scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15448)
    parser.add_argument("--container-name", default="aiopsbench-pg-queryperf-05")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--llm-config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot. Default: general_knowledge.")
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgQueryPerfImplicitTypeConversionScenario()
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
        run_mock_zero(args.case, args.port, args.container_name, run_config)
    if args.mode in ("llm", "all"):
        run_llm(args.case,
            args.port,
            args.container_name,
            args.model,
            args.llm_config,
            args.max_turns,
            run_config,
            agent_name=args.agent,
            dbaiops_graph=args.dbaiops_graph,
            dbot_tool_profile=args.dbot_tool_profile,
        )


if __name__ == "__main__":
    main()
