import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb.health_check import TidbHealthCheckAutoAnalyzeDriftScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


def _mock_responses(case) -> list[dict]:
    return [
        {
            "thinking": "先查看组件、业务查询和 TopSQL，确认巡检窗口不是空集群。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT TYPE, INSTANCE, VERSION FROM information_schema.cluster_info ORDER BY TYPE, INSTANCE"}},
                {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY FROM information_schema.cluster_statements_summary ORDER BY SUM_LATENCY DESC LIMIT 50"}},
            ],
        },
        {
            "thinking": "核对全局维护设置、统计健康、统计锁和维护交接记录，辨别需要释放的对象。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "SHOW GLOBAL VARIABLES LIKE 'tidb_enable_auto_analyze'"},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SHOW GLOBAL VARIABLES"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "SHOW STATS_HEALTHY WHERE Db_name = 'benchops'"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "SHOW STATS_LOCKED"},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": "SHOW STATS_META WHERE Db_name = 'benchops'",
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT object_name, maintenance_kind, handoff_state, "
                            "expected_stats_mode FROM benchops.hc07_review_context "
                            "ORDER BY object_name"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT 'hc07_orders' AS table_name, COUNT(*), "
                            "COALESCE(SUM(order_id), 0), COALESCE(SUM(amount_cents), 0) "
                            "FROM benchops.hc07_orders UNION ALL "
                            "SELECT 'hc07_payments', COUNT(*), COALESCE(SUM(payment_id), 0), "
                            "COALESCE(SUM(amount_cents), 0) FROM benchops.hc07_payments UNION ALL "
                            "SELECT 'hc07_inventory', COUNT(*), COALESCE(SUM(sku_id), 0), "
                            "COALESCE(SUM(available), 0) FROM benchops.hc07_inventory UNION ALL "
                            "SELECT 'hc07_order_events', COUNT(*), COALESCE(SUM(event_id), 0), "
                            "COALESCE(SUM(order_id), 0) FROM benchops.hc07_order_events UNION ALL "
                            "SELECT 'hc07_review_context', COUNT(*), 0, 0 "
                            "FROM benchops.hc07_review_context"
                        )
                    },
                },
            ],
        },
        {
            "thinking": "恢复运行基线中的全局统计维护设置，但不改变仍在 active canary 中的支付表策略。",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": "SET GLOBAL tidb_enable_auto_analyze = ON"},
            },
        },
        {
            "thinking": "订单批量维护已完成，只释放订单表遗留的统计锁。",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": "UNLOCK STATS benchops.hc07_orders"},
            },
        },
        {
            "thinking": "对已经精确解锁的订单表重新收集统计信息。",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": "ANALYZE TABLE benchops.hc07_orders"},
            },
        },
        {
            "thinking": "验证配置、锁范围、受保护统计版本和双表业务真值。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "SHOW GLOBAL VARIABLES LIKE 'tidb_enable_auto_analyze'"},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": "SHOW STATS_HEALTHY WHERE Db_name = 'benchops'",
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "SHOW STATS_LOCKED"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "SHOW WARNINGS"},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT 'hc07_orders' AS table_name, COUNT(*), "
                            "COALESCE(SUM(order_id), 0), COALESCE(SUM(amount_cents), 0) "
                            "FROM benchops.hc07_orders UNION ALL "
                            "SELECT 'hc07_payments', COUNT(*), COALESCE(SUM(payment_id), 0), "
                            "COALESCE(SUM(amount_cents), 0) FROM benchops.hc07_payments"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SHOW STATS_META WHERE Db_name = 'benchops' "
                            "AND Table_name = 'hc07_payments'"
                        )
                    },
                },
                {"api": "execute_sql", "args": {"sql_query": "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY FROM information_schema.cluster_statements_summary ORDER BY SUM_LATENCY DESC LIMIT 50"}},
            ],
        },
        {
            "thinking": "巡检闭环已完成，提交可复核报告。",
            "action": {
                "api": "submit",
                "args": {"report": case.reference_report},
            },
        },
    ]


def main() -> None:
    scenario = TidbHealthCheckAutoAnalyzeDriftScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB HC07 automatic statistics configuration drift health check."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--container-name", default="tidb-hc07")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=16)
    parser.add_argument(
        "--tool-profile",
        choices=["no_knowledge", "general_knowledge", "hierarchical_knowledge"],
        default="no_knowledge",
    )
    parser.add_argument(
        "--fault-snapshot-mode",
        choices=["auto", "off", "save", "use"],
        default="off",
    )
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=120,
    )
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA agent.",
            use_native_tools=False,
        )
        agent.set_mock_responses(_mock_responses(case))
    else:
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    run_config = OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode)
    orchestrator = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=run_config,
    )
    result = orchestrator.run()
    if args.mode == "mock" and (
        result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]
    ) != (None, True, True):
        raise AssertionError(
            "HC07 mock path must pass with N/T/T: "
            f"evaluation={result!r}"
        )


if __name__ == "__main__":
    main()
