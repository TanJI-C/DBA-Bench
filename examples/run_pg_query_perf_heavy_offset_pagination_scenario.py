import argparse
import json
import os
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgQueryPerfHeavyOffsetPaginationScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSXWorkload



# 讲解主线：完整 tpcdsx 查询用 row_number() 取审计导出深段；
# 慢不是缺索引/统计/work_mem，而是必须跳过大量已排序前序行。
ANCHOR_SQL = """
WITH candidate_events AS MATERIALIZED (
    SELECT
        bol.bol_sold_date_sk AS event_day_sk,
        bol.bol_receipt_number AS receipt_number,
        bol.bol_product_sk AS product_sk
    FROM branch_order_line bol
    WHERE bol.bol_sold_date_sk BETWEEN 2450815 AND 2452640
      AND bol.bol_receipt_number IS NOT NULL
      AND bol.bol_product_sk IS NOT NULL
)
SELECT event_day_sk, receipt_number, product_sk
FROM candidate_events
ORDER BY event_day_sk, receipt_number, product_sk
LIMIT 1 OFFSET 999999;
"""


KEYSET_REWRITE_SQL = """
WITH candidate_events AS MATERIALIZED (
    SELECT
        cal.cal_date AS event_ts,
        bol.bol_sold_date_sk AS event_day_sk,
        bol.bol_receipt_number AS receipt_number,
        bol.bol_product_sk AS product_sk,
        bol.bol_account_sk AS account_sk,
        bol.bol_branch_sk AS branch_sk,
        bol.bol_quantity AS quantity,
        bol.bol_net_paid AS net_paid,
        bol.bol_net_profit AS net_profit,
        prod.pr_category,
        prod.pr_brand
    FROM branch_order_line bol
    JOIN calendar_day cal ON cal.cal_day_sk = bol.bol_sold_date_sk
    JOIN product prod ON prod.pr_product_sk = bol.bol_product_sk
    WHERE bol.bol_sold_date_sk BETWEEN 2450815 AND 2452640
      AND (bol.bol_sold_date_sk, bol.bol_receipt_number, bol.bol_product_sk) > (2451513, 155272, 10411)
),
export_total AS MATERIALIZED (
    SELECT COUNT(*) AS export_total
    FROM branch_order_line bol
    WHERE bol.bol_sold_date_sk BETWEEN 2450815 AND 2452640
      AND bol.bol_receipt_number IS NOT NULL
      AND bol.bol_product_sk IS NOT NULL
)
SELECT
    ce.event_ts,
    ce.event_day_sk,
    ce.receipt_number,
    ce.product_sk,
    ce.account_sk,
    ce.branch_sk,
    ce.quantity,
    ce.net_paid,
    ce.net_profit,
    ce.pr_category,
    ce.pr_brand,
    et.export_total
FROM candidate_events ce
JOIN export_total et ON TRUE
ORDER BY ce.event_day_sk, ce.receipt_number, ce.product_sk
LIMIT 10;
"""

# The shallow reference anchor is the cursor returned by the preceding anchor
# query for the frozen TPC-DSX dataset. Keeping it literal makes the candidate
# a real keyset seek instead of charging the anchor OFFSET to the repair query.
SHALLOW_KEYSET_BOUNDARY = (2450827, 24902, 10216)


def anchor_sql(case) -> str:
    if case.case_id == "branch_order_deep_offset":
        return ANCHOR_SQL
    if case.case_id == "branch_order_shallow_offset":
        return f"""
SELECT {case.order_column}, bol_receipt_number, bol_product_sk
FROM {case.table}
WHERE {case.order_column} BETWEEN 2450815 AND 2452640
ORDER BY {case.order_column}, bol_receipt_number, bol_product_sk
LIMIT 1 OFFSET {case.offset_value - 1};
"""
    raise ValueError(f"Unsupported heavy-offset mock Case: {case.case_id!r}")


def keyset_rewrite_sql(case) -> str:
    if case.case_id == "branch_order_deep_offset":
        return KEYSET_REWRITE_SQL
    if case.case_id == "branch_order_shallow_offset":
        return f"""
SELECT bol.{case.order_column}, bol.bol_receipt_number, bol.bol_product_sk
FROM {case.table} bol
WHERE bol.{case.order_column} BETWEEN 2450815 AND 2452640
  AND (bol.{case.order_column}, bol.bol_receipt_number, bol.bol_product_sk)
      > {SHALLOW_KEYSET_BOUNDARY}
ORDER BY bol.{case.order_column}, bol.bol_receipt_number, bol.bol_product_sk
LIMIT 10;
"""
    raise ValueError(f"Unsupported heavy-offset mock Case: {case.case_id!r}")


def reference_report(case) -> dict:
    if case.case_id == "branch_order_deep_offset":
        return case.reference_report
    if case.case_id == "branch_order_shallow_offset":
        return {
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "late page export query",
                        "entity": case.table,
                        "evidence": [
                            "late pages of the branch order export degrade while early pages stay fast"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": "row_number window over the full ordered result",
                        "entity": case.table,
                        "evidence": [
                            "the export numbers every preceding row before returning the late page"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": "scans and discards preceding rows",
                        "entity": case.table,
                        "evidence": [
                            "pagination cost grows with page depth because the ordered prefix is rescanned"
                        ],
                    },
                ]
            },
            "outcome": {
                "changes": [
                    "replace OFFSET with keyset pagination on bol_sold_date_sk"
                ],
                "verification": ["keyset boundary query was verified"],
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification.",
        }
    raise ValueError(f"Unsupported heavy-offset mock Case: {case.case_id!r}")


def keyset_remediation_sql(case) -> str:
    return keyset_rewrite_sql(case)


PG_STAT_SQL = """
SELECT query, calls, mean_exec_time, rows
FROM pg_stat_statements
WHERE query ILIKE '%branch_order_line%'
  AND query ILIKE '%row_number%'
ORDER BY total_exec_time DESC
LIMIT 10;
"""


def build_full_score_mock_responses(case):
    target_explain_sql = (
        "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
        f"{case.fault_fingerprint_sql.rstrip(';')};"
    )
    return [
    {
        "thinking": "先看 topsql 找出 pg_stat_statements 里 mean_exec_time 最高的完整审计导出 SQL，再做诊断。",
        "action": {"api": "query_metrics", "args": {"metric_type": "topsql"}},
    },
    {
        "thinking": "先查看最耗时 SQL，确认是否存在分页相关的业务查询。",
        "action": {"api": "query_metrics", "args": {"metric_type": "topsql"}},
    },
    {
        "thinking": "继续直接检查 pg_stat_statements 中完整 row_number 批次导出 SQL 的文本和耗时。",
        "action": {"api": "execute_sql", "args": {"sql_query": PG_STAT_SQL}},
    },
    {
        "thinking": "对完整故障 SQL 执行 EXPLAIN ANALYZE，确认 WindowAgg/row_number 必须给大量前序行编号后才返回 10 行。",
        "action": {"api": "execute_sql", "args": {"sql_query": target_explain_sql}},
    },
        {
            "thinking": "定位一个业务 cursor/anchor；这一步用于把深段批次改成稳定 seek 条件。",
            "action": {"api": "execute_sql", "args": {"sql_query": anchor_sql(case)}},
        },
        {
            "thinking": "用同一业务结果的 seek 查询替换深分页，并实际执行候选业务查询。",
            "action": {"api": "execute_sql", "args": {"sql_query": keyset_rewrite_sql(case)}},
    },
    {
        "thinking": "执行一次不带 EXPLAIN 的 keyset 业务查询，确认修复路径实际可执行并返回结果。",
        "action": {"api": "execute_sql", "args": {"sql_query": keyset_remediation_sql(case)}},
    },
    {
        "thinking": "执行计划和改写验证说明这是高位 row_number/深分页反模式，应改为 keyset/cursor pagination。",
        "action": {
            "api": "submit",
            "args": {"report": reference_report(case)},
        },
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
        postgres_user="postgres",
        postgres_password="password",
        postgres_db="testdb",
        port=port,
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=workload.data_dir,
        dataset_manifest_path=workload.manifest_path,
        image_name=image_name or case.base_image_name,
    )
    env_kwargs = {"workload": workload, "deployment": deployment, "port": port}
    if tool_profile:
        env_kwargs["tool_profile"] = tool_profile
    env_kwargs.update({
        "allow_sampler_jitter": True,
        "allow_sampler_reconnect": True,
    })
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

def build_scenario() -> PgQueryPerfHeavyOffsetPaginationScenario:
    return PgQueryPerfHeavyOffsetPaginationScenario()


def run_mock_full(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - High-Rank Pagination Full-Score Mock Path")
    print("=" * 60)

    scenario = build_scenario()
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
    print("AiOpsBench PostgreSQL - High-Rank Pagination Zero-Score Mock Path")
    print("=" * 60)

    scenario = build_scenario()
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


def run_llm(case_id: str, port: int, container_name: str, model: str = None, config_path: str = "config/llm_config.json", max_turns: int = 20, run_config: OrchestratorRunConfig = None,
            agent_name: str = "llm", dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
            dbot_tool_profile: str = "general_knowledge") -> float:
    print("=" * 60)
    print(f"AiOpsBench PostgreSQL - High-Rank Pagination {agent_name.upper()}Agent Path")
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

    scenario = build_scenario()
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
    parser = argparse.ArgumentParser(description="Run pg_query_perf_heavy_offset_pagination scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15456)
    parser.add_argument("--container-name", default="aiopsbench-pg-queryperf-06")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--llm-config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot. Default: general_knowledge.")
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgQueryPerfHeavyOffsetPaginationScenario()
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
            model=args.model,
            config_path=args.llm_config,
            max_turns=args.max_turns,
            run_config=run_config,
            agent_name=args.agent,
            dbaiops_graph=args.dbaiops_graph,
            dbot_tool_profile=args.dbot_tool_profile,
        )


if __name__ == "__main__":
    main()
