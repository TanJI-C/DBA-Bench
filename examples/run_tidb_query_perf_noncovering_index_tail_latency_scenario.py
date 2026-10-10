import argparse
import json
import os
import sys
from dataclasses import replace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.tidb import TidbQueryPerfNoncoveringIndexTailLatencyScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


def build_pass_report(case):
    report = {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "在 benchops.qp05_order_events 上，event_time 范围列先于 tenant_id 或 order_state 等值列，导致订单历史查询宽范围扫描后再过滤",
                    "entity": f"{case.db}.{case.table}",
                    "evidence": [
                        "EXPLAIN ANALYZE shows the range-leading composite index and broad TiKV scan across the page scope",
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": "现有候选索引没有同时满足等值列在前、时间范围列在后且覆盖目标投影的单一路径",
                    "entity": f"{case.db}.{case.table}",
                    "evidence": [
                        "SHOW INDEX 和 EXPLAIN ANALYZE 显示候选路径把选择性与覆盖能力分散在不同索引上",
                    ],
                },
                {
                    "type": "necessary_exclusion",
                    "factor": "排除基础设施/组件健康故障",
                    "entity": "TiDB/TiKV cluster",
                    "evidence": [
                        "service status shows PD, TiDB, and TiKV are normal"
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "replaced injector-owned stale candidates with a safe composite covering access path with tenant and state equality columns before the time range"
            ],
            "verification": [
                "EXPLAIN ANALYZE shows IndexReader, a narrow scan, and no IndexLookUp/TableRowIDScan",
                "target p95 is within the declared SLO and target result, page context, table CRC, and ADMIN CHECK TABLE match baseline",
            ],
        },
        "summary": (
            "The target path was repaired by replacing injector-owned stale candidates with one "
            "equivalent safe covering composite access path; business rows and healthy indexes were preserved."
        ),
    }
    StructuredReport.from_mapping(report)
    return report


def build_mock_responses(case):
    return [
        {
            "thinking": "First correlate application_name, workload activity, TopSQL, query latency, and SQL fingerprints to identify the canonical checkout page route, read the page context, then rule out a component outage.",
            "actions": [
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "qps", "target": "tidb/tidb-0"},
                },
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "query_latency", "target": "tidb/tidb-0"},
                },
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "active_connections", "target": "tidb/tidb-0"},
                },
                {
                    "api": "manage_cluster",
                    "args": {"resource": "service", "operation": "list"},
                },
                {
                    "api": "read_log",
                    "args": {
                        "target": "tikv/tikv-0",
                        "lines": 200,
                    },
                },
                {
                    "api": "read_log",
                    "args": {
                        "target": "tidb/tidb-0",
                        "lines": 200,
                    },
                },
            ],
        },
        {
            "thinking": "Map the opaque shared-digest fingerprint through the current route registry and page context before comparing the canonical EXPLAIN ANALYZE plan. Use the full index catalog to compare equality-leading and range-leading candidates, then check statistics and DDL state.",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {"sql_query": f"EXPLAIN ANALYZE {case.query}"},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, "
                            "SUM_LATENCY, AVG_TOTAL_KEYS, AVG_PROCESSED_KEYS, AVG_MEM, MAX_MEM, "
                            "AVG_DISK, MAX_DISK FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY "
                            "ORDER BY SUM_LATENCY DESC LIMIT 50"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT TIME, INSTANCE, DIGEST, QUERY, QUERY_TIME, PROCESS_TIME, "
                            "WAIT_TIME, BACKOFF_TIME, TOTAL_KEYS, PROCESS_KEYS, MEM_MAX, DISK_MAX "
                            "FROM INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY ORDER BY TIME DESC LIMIT 50"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.route_registry_sql},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.index_catalog_sql},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.stats_sql},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.page_context_truth_sql},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.table_size_sql},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.ddl_jobs_sql},
                },
            ],
        },
        {
            "thinking": "Replace the injector-owned stale candidates with one narrow equality-leading covering access path that puts tenant_id and order_state before event_time, refresh statistics, and verify plan, workload costs, DDL state, and invariants.",
            "actions": [
                *[
                    {
                        "api": "execute_sql",
                        "args": {
                            "sql_query": f"DROP INDEX {index_name} ON {case.db}.{case.table}"
                        },
                    }
                    for index_name in case.replaceable_fault_index_names
                ],
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"CREATE INDEX qp05_covering_history_v1 ON {case.db}.{case.table} "
                            "(tenant_id, order_state, event_time, event_id, order_total, currency, fulfillment_zone)"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": f"ANALYZE TABLE {case.db}.{case.table}"
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": f"EXPLAIN ANALYZE {case.query}"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.table_size_sql},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.ddl_jobs_sql},
                },
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "query_latency", "target": "tidb/tidb-0"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.route_registry_truth_sql},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.query},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.table_crc_sql},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.page_context_truth_sql},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": f"ADMIN CHECK TABLE {case.db}.{case.table}"
                    },
                },
            ],
        },
        {
            "thinking": "The canonical final plan, scan volume, p95, business result, CRC, and table check are all verified; submit the structured report.",
            "action": {
                "api": "submit",
                "args": {"report": build_pass_report(case)},
            },
        },
    ]


def main() -> None:
    scenario = TidbQueryPerfNoncoveringIndexTailLatencyScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB QP05 composite non-covering-index scenario."
    )
    parser.add_argument(
        "--case",
        required=True,
        choices=[case.case_id for case in scenario.cases],
    )
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--port", type=int, default=6500)
    parser.add_argument("--container-name", default="tidb-qp05-composite")
    parser.add_argument(
        "--fault-snapshot-mode",
        choices=("auto", "off", "save", "use"),
        default="auto",
    )
    parser.add_argument("--cold-start-timeout", type=int, default=1800)
    parser.add_argument("--warm-start-timeout", type=int, default=300)
    parser.add_argument("--storage-key")
    parser.add_argument("--storage-root")
    args = parser.parse_args()

    if args.mode == "llm" and not args.model:
        raise ValueError("--model is required when --mode=llm")
    if (args.storage_key is None) != (args.storage_root is None):
        raise ValueError("--storage-key and --storage-root must be provided together")

    case = scenario.get_case(args.case)
    if args.storage_key is not None:
        case = replace(
            case,
            runtime=replace(case.runtime, image_group_key=None),
        )
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        tidb_readiness_timeout_sec=args.cold_start_timeout,
        warm_tidb_readiness_timeout_sec=args.warm_start_timeout,
        return_window_seconds=300,
        storage_key=args.storage_key,
        storage_root=args.storage_root,
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
                "QP05 mock must pass DP/OP/SP: "
                f"observed={observed!r}, result={json.dumps(result, ensure_ascii=False, default=str)}"
            )
    print(f"Final result: {json.dumps(result, ensure_ascii=False, default=str)}")


if __name__ == "__main__":
    main()
