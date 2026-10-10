import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.base import evaluation_passed
from src.scenarios.tidb import TidbQueryPerfCaseWhenInCartesianSemiJoinScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


def build_mock_responses(case):
    fixed_view_sql = (
        f"CREATE OR REPLACE VIEW {case.db}.{case.view} AS "
        f"SELECT o.id, CASE WHEN r.rule_key IS NOT NULL AND g.gate_key IS NOT NULL AND x.region_key IS NOT NULL THEN 1 "
        f"WHEN o.risk_scope IN ('scope_c', 'scope_d') AND NOT EXISTS (SELECT 1 FROM {case.db}.{case.region_table} AS xn WHERE xn.region_scope=o.risk_scope AND xn.region_key=o.lookup_key) "
        f"AND EXISTS (SELECT 1 FROM {case.db}.{case.region_table} AS xn WHERE xn.region_scope=o.risk_scope AND xn.region_key IS NULL) THEN NULL "
        "WHEN o.risk_scope IN ('scope_b', 'scope_c', 'scope_d') THEN 0 ELSE NULL END AS matched "
        f"FROM {case.db}.{case.outer_table} AS o "
        f"LEFT JOIN (SELECT DISTINCT rule_scope, rule_key FROM {case.db}.{case.rule_table} WHERE rule_key IS NOT NULL) AS r "
        "ON r.rule_scope=o.risk_scope AND r.rule_key=o.lookup_key "
        f"LEFT JOIN (SELECT DISTINCT gate_scope, gate_key FROM {case.db}.{case.gate_table} WHERE gate_key IS NOT NULL) AS g "
        "ON g.gate_scope=o.risk_scope AND g.gate_key=o.lookup_key "
        f"LEFT JOIN (SELECT DISTINCT region_scope, region_key FROM {case.db}.{case.region_table} WHERE region_key IS NOT NULL) AS x "
        "ON x.region_scope=o.risk_scope AND x.region_key=o.lookup_key"
    )
    report = case.reference_report
    return [
        {
            "thinking": "先检查报表指纹和 view 定义，再把计划证据与 nullable 子查询关联起来。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY FROM information_schema.cluster_statements_summary ORDER BY SUM_LATENCY DESC LIMIT 50"}},
                {"api": "execute_sql", "args": {"sql_query": f"SHOW CREATE VIEW {case.db}.{case.view}"}},
                {"api": "execute_sql", "args": {"sql_query": f"EXPLAIN {case.business_query}"}},
            ],
        },
        {
            "thinking": "把 scalar IN 改成带 equality correlation 的 EXISTS，并确认 endpoint 结果保持一致。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": fixed_view_sql}},
                {"api": "execute_sql", "args": {"sql_query": f"EXPLAIN {case.business_query}"}},
                {"api": "execute_sql", "args": {"sql_query": case.business_query}},
            ],
        },
        {
            "thinking": "最终计划、完整结果、命中数和 NULL 行语义均已复核，提交结构化报告。",
            "actions": [
                {"api": "submit", "args": {"report": report}},
            ],
        },
    ]


def run_mode(args, scenario, case):
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA agent.",
            use_native_tools=False,
        )
        agent.set_mock_responses(build_mock_responses(case))
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
    )
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=run_config,
    ).run()
    print(
        f"[{args.mode}] DP={result['DiagnosisPass']} "
        f"OP={result['OutcomePass']} SP={result['SafePass']}"
    )
    if args.mode == "mock":
        assert evaluation_passed(result), json.dumps(result, ensure_ascii=False, indent=2, default=str)
    return result


def main():
    scenario = TidbQueryPerfCaseWhenInCartesianSemiJoinScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB CASE IN Cartesian semi join query-performance scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--port", type=int, default=4680)
    parser.add_argument(
        "--container-name",
        default="aiopsbench-tidb-qp06-case-in-cartesian-semi-join",
    )
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    args = parser.parse_args()
    run_mode(args, scenario, scenario.get_case(args.case))


if __name__ == "__main__":
    main()
