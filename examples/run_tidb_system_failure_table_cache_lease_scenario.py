import argparse
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.tidb import TidbSystemFailureTableCacheLeaseScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


PASS_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "root_cause",
                "factor": (
                    "the 2PC and Prewrite failures are lease-renewal write conflicts on mysql.table_cache_meta "
                    "for the cached tables rather than business-row conflicts"
                ),
                "entity": "the cached tables' lease metadata rows are the conflicting transaction keys",
                "evidence": ["TiDB logs contain kv:9007 for table_cache_meta and the cached-table tids"],
            },
            {
                "type": "mechanism",
                "factor": (
                    "TiDB internal cached-table reads renew the lease through lock cached table for read "
                    "and collide while updating the metadata row"
                ),
                "entity": "TiDB renews cached-table lease metadata while serving internal cached-table reads.",
                "evidence": ["the TiDB log source is lock cached table for read"],
            },
            {
                "type": "scope",
                "factor": (
                    "multiple TiDB instances concurrently access the three causal cached business tables and therefore contend on their shared leases"
                ),
                "entity": "Two TiDB instances concurrently read the three causal cached business tables and contend on their shared lease metadata rows.",
                "evidence": ["cluster_info shows tidb-0 and tidb-1; the three causal SHOW CREATE results contain CACHED ON"],
            },
            {
                "type": "necessary_exclusion",
                "factor": (
                    "the ordinary business tables and TiKV stores are not the root cause of the observed 9007 failures"
                ),
                "entity": "Ordinary business-row conflicts and TiKV capacity pressure are excluded as the cause of the 9007 failures.",
                "evidence": ["the conflict key is mysql.table_cache_meta and the business table truth is unchanged"],
            },
            {
                "type": "necessary_exclusion",
                "factor": (
                    "the healthy cached reference table is not implicated by the conflict keys or target workload and must remain cached"
                ),
                "entity": "The unrelated healthy cached reference table is outside the conflicting keys and target workload and must remain cached.",
                "evidence": ["ma02_catalog_aux is cached, is read through tidb-0 only, and has no conflict handle"],
            },
        ]
    },
    "outcome": {
            "changes": [
                "removed the cached-table attribute from benchops.ma02_product_catalog",
                "removed the cached-table attribute from benchops.ma02_inventory",
                "removed the cached-table attribute from benchops.ma02_pricing_rules",
            ],
            "verification": [
                "verified all three causal cache markers are removed, the healthy reference cache remains enabled, and TiDB 8.1 may retain stale table_cache_meta rows",
                "verified business truth, five-table schema presence, TSO and every causal workload profile",
            ],
        },
    "summary": "The QPS cliff was caused by lease metadata contention for three causal cached business tables across two TiDB instances; disabling only those cache markers preserved the healthy reference cache and business data.",
}
StructuredReport.from_mapping(PASS_REPORT)


MOCK_SCENARIO = TidbSystemFailureTableCacheLeaseScenario()
MOCK_CASE = MOCK_SCENARIO.get_case("table_cache_lease_write_conflict")


def build_mock_responses(case):
    report = copy.deepcopy(PASS_REPORT)
    if case.case_id == "table_cache_lease_single_table_focus":
        report["diagnosis"]["conditions"][0]["factor"] = (
            "the 2PC and Prewrite failures are lease-renewal write conflicts on mysql.table_cache_meta for one cached business table rather than business-row conflicts"
        )
        report["diagnosis"]["conditions"][0]["entity"] = (
            "the cached business table's lease metadata row is the conflicting transaction key"
        )
        report["diagnosis"]["conditions"][2]["factor"] = (
            "multiple TiDB instances concurrently access one causal cached business table and therefore contend on its shared lease"
        )
        report["diagnosis"]["conditions"][2]["entity"] = (
            "Two TiDB instances concurrently read one causal cached business table and contend on its shared lease metadata row."
        )
        report["diagnosis"]["conditions"][2]["evidence"] = [
            "cluster_info shows tidb-0 and tidb-1; the causal SHOW CREATE result contains CACHED ON"
        ]
        report["outcome"]["changes"] = [
            f"removed the cached-table attribute from {case.db}.{table}"
            for table in case.cache_table_names
        ]
        report["outcome"]["verification"] = [
            "verified the causal cache marker is removed, the healthy reference cache remains enabled, and TiDB 8.1 may retain stale table_cache_meta rows",
            "verified business truth, schema presence, TSO and every causal workload profile",
        ]
        report["summary"] = (
            "The QPS cliff was caused by lease metadata contention for one causal cached business table across two TiDB instances; disabling only that cache marker preserved the healthy reference cache and business data."
        )
    responses = [
    {
        "thinking": "The alert is compatible with a hot-row conflict, so first correlate QPS, latency, active profiles and the initial logs from both TiDB endpoints.",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "qps", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "query_latency", "target": None}},
            {"api": "read_log", "args": {"target": "tidb/tidb-0", "lines": 1000}},
            {"api": "read_log", "args": {"target": "tidb/tidb-1", "lines": 1000}},
        ],
    },
    {
        "thinking": "The first visible window contains a retryable business-row 9007. Map the observed table IDs and compare statement activity before concluding that this is the main cause.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": "SELECT tid, lock_type, lease, oldReadLease FROM mysql.table_cache_meta"
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT INSTANCE, DIGEST_TEXT, EXEC_COUNT, SUMMARY_BEGIN_TIME, SUMMARY_END_TIME "
                        "FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY "
                        "WHERE DIGEST_TEXT LIKE '%benchops%' OR DIGEST_TEXT LIKE '%ma02_%' "
                        "ORDER BY EXEC_COUNT DESC LIMIT 80"
                    )
                },
            },
        ],
    },
    {
        "thinking": "A later phase now shows the internal cached-table read conflict on both endpoints. Correlate the metadata rows with all cached table definitions and the shared lease before changing only the causal tables.",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "qps", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "query_latency", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": "tikv/tikv-0"}},
            {"api": "query_metrics", "args": {"metric_type": "cpu", "target": "tikv/tikv-0"}},
        ],
    },
    {
        "thinking": "The later window should now be compared with the initial business-only window. Read both endpoint logs for the internal read path, then correlate the metadata with all cached table definitions and the shared lease.",
        "actions": [
            {"api": "read_log", "args": {"target": "tidb/tidb-0", "match_key": "lock cached table for read"}},
            {"api": "read_log", "args": {"target": "tidb/tidb-1", "match_key": "lock cached table for read"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT INSTANCE, DIGEST_TEXT, EXEC_COUNT, SUMMARY_BEGIN_TIME, SUMMARY_END_TIME "
                        "FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY "
                        "WHERE DIGEST_TEXT LIKE '%benchops%' OR DIGEST_TEXT LIKE '%ma02_%' "
                        "ORDER BY EXEC_COUNT DESC LIMIT 80"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW CREATE TABLE benchops.ma02_product_catalog"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW CREATE TABLE benchops.ma02_inventory"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW CREATE TABLE benchops.ma02_pricing_rules"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW CREATE TABLE benchops.ma02_catalog_aux"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW GLOBAL VARIABLES LIKE 'tidb_table_cache_lease'"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": "SELECT TIDB_TABLE_ID FROM information_schema.tables WHERE TABLE_SCHEMA = 'benchops' AND TABLE_NAME = 'ma02_product_catalog'"
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": "SELECT TIDB_TABLE_ID FROM information_schema.tables WHERE TABLE_SCHEMA = 'benchops' AND TABLE_NAME = 'ma02_inventory'"
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": "SELECT TIDB_TABLE_ID FROM information_schema.tables WHERE TABLE_SCHEMA = 'benchops' AND TABLE_NAME = 'ma02_pricing_rules'"
                },
            },
            {"api": "manage_cluster", "args": {"resource": "service", "operation": "list"}},
        ],
    },
    {
        "thinking": "The internal metadata conflicts follow the business retry phase and the healthy companion is only read through tidb-0. Disable cache only on the three causal business tables, then verify the business truth.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER TABLE benchops.ma02_product_catalog NOCACHE"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER TABLE benchops.ma02_inventory NOCACHE"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER TABLE benchops.ma02_pricing_rules NOCACHE"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": MOCK_CASE.business_summary_sql},
            },
            {"api": "submit", "args": {"report": PASS_REPORT}},
        ],
    },
    ]
    visible_cache_tables = {
        *case.cache_table_names,
        *case.healthy_cache_table_names,
    }
    filtered = []
    for turn in responses:
        actions = []
        for action in turn.get("actions", ()):
            sql = action.get("args", {}).get("sql_query")
            if isinstance(sql, str):
                if sql.startswith("SHOW CREATE TABLE "):
                    table = sql.rsplit(".", 1)[-1]
                    if table not in visible_cache_tables:
                        continue
                if "TABLE_NAME = '" in sql and "TIDB_TABLE_ID" in sql:
                    table = sql.split("TABLE_NAME = '", 1)[1].split("'", 1)[0]
                    if table not in visible_cache_tables:
                        continue
                if sql.startswith("ALTER TABLE ") and sql.endswith(" NOCACHE"):
                    table = sql.split(".", 1)[1].split(" ", 1)[0]
                    if table not in case.cache_table_names:
                        continue
                if sql == MOCK_CASE.business_summary_sql:
                    action = {
                        **action,
                        "args": {**action["args"], "sql_query": case.business_summary_sql},
                    }
            if action.get("api") == "submit":
                action = {
                    **action,
                    "args": {"report": report},
                }
            actions.append(action)
        next_turn = {key: value for key, value in turn.items() if key != "actions"}
        if "actions" in turn:
            next_turn["actions"] = actions
        if "action" in turn and turn["action"].get("api") == "submit":
            next_turn["action"] = {
                **turn["action"],
                "args": {"report": report},
            }
        filtered.append(next_turn)
    return filtered


FULL_SCORE_MOCK_RESPONSES = build_mock_responses(MOCK_CASE)


def main() -> None:
    scenario = TidbSystemFailureTableCacheLeaseScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB table-cache-lease cached-table lease contention scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=12)
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--port", type=int, default=4300)
    parser.add_argument("--container-name", default="tidb-table-cache")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(run_id=args.container_name, port_base=args.port, return_window_seconds=300)
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
            max_output_tokens=args.max_output_tokens,
        )
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (True, True, True):
            raise RuntimeError(f"table-cache-lease mock must pass DP/OP/SP, observed={observed!r}, result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
