import argparse
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbHealthCheckGcSafepointPinScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator


FULL_PASS_MOCK_RESPONSES = [
    {
        "thinking": "先按日常巡检看容量、TopSQL 和业务噪声，不假设已有事故。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "disk_usage"}},
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {"api": "query_metrics", "args": {"metric_type": "workload_activity"}},
        ],
    },
    {
        "thinking": "查看 benchops 中的巡检对象，确认是否有 GC/复制保留线索。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SHOW FULL TABLES FROM benchops"}},
            {"api": "execute_sql", "args": {"sql_query": (
                "SELECT sample_name, MAX(observed_mb), MAX(growth_mb_per_day) "
                "FROM benchops.capacity_samples GROUP BY sample_name "
                "ORDER BY MAX(growth_mb_per_day) DESC"
            )}},
            {"api": "execute_sql", "args": {"sql_query": (
                "SELECT * FROM benchops.effective_retention_window"
            )}},
        ],
    },
    {
        "thinking": "把 oldest service safepoint 和 changefeed owner 状态关联起来，同时排除健康 owner。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": (
                "SELECT service_id, owner_type, owner_detail, safe_point_age_hours, active, "
                "registration_state, ticket_ref, last_heartbeat_at "
                "FROM benchops.owner_lineage_matrix ORDER BY safe_point_age_hours DESC"
            )}},
            {"api": "execute_sql", "args": {"sql_query": (
                "SELECT changefeed_id, state, owner_status, checkpoint_lag_seconds, "
                "lifecycle_stage, ticket_ref, data_class, notes "
                "FROM benchops.replication_checkpoints ORDER BY checkpoint_lag_seconds DESC"
            )}},
            {"api": "execute_sql", "args": {"sql_query": (
                "SELECT service_id, changefeed_id, reconciliation_state, observation_count, "
                "required_observations, last_observed_at, stable_at "
                "FROM benchops.retention_reconciliation"
            )}},
            {"api": "search_knowledge", "args": {
                "query": "TiCDC service GC safepoint checkpoint lag stopped changefeed",
                "source_scope": "all",
                "top_k": 3,
                "kb_type": "observability",
                "component": "ticdc",
            }},
        ],
    },
    {
            "thinking": "目标 owner 已确认退役且非保护对象，执行最小范围清理。",
            "action": {"api": "execute_sql", "args": {"sql_query": (
            "UPDATE benchops.retention_owner_ledger SET active = 0 "
            "WHERE service_id = 'svc-7f2a' "
            "AND owner_detail = 'cf-7f2a' "
            "AND registration_state = 'orphaned'"
        )}},
    },
    {
        "thinking": "owner 已释放，但先确认 controller reconciliation 已连续观察到 closeout，再验证最终 safepoint。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT * FROM benchops.effective_retention_window"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(7)"}},
            {"api": "execute_sql", "args": {"sql_query": (
                "SELECT service_id, reconciliation_state, observation_count, required_observations, stable_at "
                "FROM benchops.retention_reconciliation"
            )}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT * FROM benchops.effective_retention_window"}},
            {"api": "execute_sql", "args": {"sql_query": (
                "SELECT COUNT(*) FROM benchops.retention_owner_ledger "
                "WHERE active = 1 AND service_id IN ("
                "'ticdc-default-ledger-live-v2','ticdc-default-warehouse-hourly',"
                "'br-nightly-full-20260801','ticdc-default-analytics-pause-2026w31',"
                "'dm-default-region-mirror','ticdc-default-orders-replay',"
                "'br-weekly-restore-validation','ticdc-default-compliance-export',"
                "'ticdc-default-warehouse-backfill','dm-default-cold-archive',"
                "'ticdc-default-inventory-delta','ticdc-default-batch-export',"
                "'ticdc-default-feature-sandbox','ticdc-default-legacy-report-2025',"
                "'dm-default-delivery-replay','br-default-cold-restore',"
                "'br-default-legal-hold-2025','svc-3b18',"
                "'svc-4c91','svc-5d27',"
                "'svc-6e44','svc-7a83')"
            )}},
            {"api": "execute_sql", "args": {"sql_query": (
                "SELECT COUNT(*), SUM(balance_cents) FROM benchops.account_balances"
            )}},
            {"api": "submit", "args": {
                "report": TidbHealthCheckGcSafepointPinScenario().get_case('abandoned_changefeed_gc_safepoint_pin').reference_report
            }},
        ],
    },
]


def _mock_responses(case) -> list[dict]:
    responses = copy.deepcopy(FULL_PASS_MOCK_RESPONSES)
    if case.case_no == 1:
        replacements = {
            "svc-7f2a": case.target_service_id,
            "cf-7f2a": case.target_changefeed_id,
            "TiCDC service GC safepoint checkpoint lag stopped changefeed": "backup restore coordinator GC safepoint checkpoint closeout",
        }
        for response in responses:
            for action in response.get("actions", [response.get("action", {})]):
                sql = action.get("args", {}).get("sql_query")
                if isinstance(sql, str):
                    for old, new in replacements.items():
                        sql = sql.replace(old, new)
                    action["args"]["sql_query"] = sql
        responses[-1]["actions"][-1]["args"]["report"] = case.reference_report
    return responses


def main():
    scenario = TidbHealthCheckGcSafepointPinScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB HC01 GC safepoint pin health-check scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=18)
    parser.add_argument("--port", type=int, default=4600)
    parser.add_argument("--container-name", default="tidb-hc01-gc-pin")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
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
        agent.set_mock_responses(_mock_responses(case))
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    result = Orchestrator(env, scenario, case, agent, max_turns=args.max_turns).run()
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
