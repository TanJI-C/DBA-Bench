import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbQueryPerfStatisticsDriftScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


def build_mock_responses(case):
    return [
        {
            "thinking": "First separate the degraded fingerprint from the healthy comparison workload and inspect both plans before changing state.",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {"sql_query": f"EXPLAIN ANALYZE {case.business_query}"},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": f"EXPLAIN ANALYZE {case.control_query}",
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "EXPLAIN ANALYZE SELECT COUNT(*) AS matched_rows, "
                            "CAST(SUM(amount) AS DECIMAL(18,2)) AS total_amount "
                            "FROM ("
                            f"SELECT id, {case.target_column}, {case.status_column}, amount FROM {case.db}.{case.noise_table} "
                            "UNION ALL "
                            f"SELECT id, {case.target_column}, {case.status_column}, amount FROM {case.db}.{case.noise_partner_table}"
                            f") AS archive_shards WHERE {case.target_column}='{case.target_value}' OR {case.status_column}='{case.status_value}'"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"SHOW STATS_META WHERE Db_name='{case.db}' "
                            "AND Table_name LIKE 'qp04_order_event%'"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": f"SHOW INDEX FROM {case.db}.{case.table}"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": f"SHOW INDEX FROM {case.db}.{case.partner_table}"},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": "SHOW VARIABLES LIKE 'tidb_enable_index_merge'",
                    },
                },
                {
                    "api": "query_metrics",
                    "args": {"sql_query": "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY FROM information_schema.cluster_statements_summary ORDER BY SUM_LATENCY DESC LIMIT 50"},
                },
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "query_latency", "target": None},
                },
            ],
        },
        {
            "thinking": "Both physical target shards changed after statistics collection, and the diagnostic session also has IndexMerge disabled for the OR predicate. Refresh both target shard statistics, enable IndexMerge for this session, and verify the recovered plan.",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"SELECT {case.target_column}, COUNT(*) AS cnt "
                            f"FROM {case.db}.{case.table} GROUP BY {case.target_column} "
                            "ORDER BY cnt DESC"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": f"ANALYZE TABLE {case.db}.{case.table}"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": f"ANALYZE TABLE {case.db}.{case.partner_table}"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "SET SESSION tidb_enable_index_merge=ON"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": f"EXPLAIN ANALYZE {case.business_query}"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.business_query},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": f"EXPLAIN ANALYZE {case.control_query}"},
                },
                {
                    "api": "submit",
                    "args": {
                        "report": case.reference_report
                    },
                },
            ],
        },
    ]


def main():
    scenario = TidbQueryPerfStatisticsDriftScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB QP04 stale-statistics distribution-shift scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--container-name", default="tidb-qp04-statistics-drift")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=300,
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

    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
        ),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (True, True, True):
            raise RuntimeError(
                f"QP04 mock must pass DP/OP/SP, observed={observed!r}, result={result!r}"
            )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
