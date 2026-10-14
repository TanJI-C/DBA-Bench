import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import StructuredReport
from src.scenarios.tidb import TidbQueryPerfIndexOrderCorrelationScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


SCENARIO = TidbQueryPerfIndexOrderCorrelationScenario()
CASE = SCENARIO.cases[0]
REPAIRED_INDEX_SQL = (
    "ALTER TABLE test.qp01_object_catalog ADD INDEX idx_bkt_cur_del_name_ver "
    "(bucket_id, is_current, is_deleted, name, version_id)"
)
REPAIRED_POLICY_INDEX_SQL = (
    "ALTER TABLE test.qp01_bucket_policy ADD INDEX idx_policy_bucket_tenant_current "
    "(bucket_id, tenant_id, is_current, policy_version)"
)
REPAIRED_ADMIN_INDEX_SQL = (
    "ALTER TABLE test.qp01_object_catalog ADD INDEX idx_tenant_cur_del_updated "
    "(tenant_id, is_current, is_deleted, updated_at, item_id)"
)
FAULT_QUERY_SQL = CASE.fault_query_sql


FULL_PASS_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "root_cause",
                "factor": next(iter(condition.aliases)),
                "entity": CASE.table,
                "evidence": ["EXPLAIN ANALYZE, table definitions, and distribution evidence."],
            }
            for condition in CASE.evaluator.diagnosis_conditions
        ]
    },
    "outcome": {
        "changes": [
            "Added separate bucket/name and tenant/updated_at catalog paths plus a current/version policy path while keeping business rows unchanged.",
        ],
        "verification": [
            "Both recovered catalog query families scan at most 2000 rows, the versioned policy lookup scans at most 100 rows, both result truths match baseline, both table CRCs are unchanged, and the separate latency sample profile was recorded."
        ],
    },
    "summary": (
        "The customer-list, tenant-admin-list, and versioned policy paths each require their own selective prefix; the repair restores all three without changing data."
    ),
}
StructuredReport.from_mapping(FULL_PASS_REPORT)


FULL_PASS_MOCK_RESPONSES = [
    {
        "thinking": "先确认延迟是否集中在 object listing 指纹，并观察 TiDB 的查询延迟和 TopSQL。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY "
                        "FROM information_schema.cluster_statements_summary "
                        "ORDER BY SUM_LATENCY DESC LIMIT 50"
                    )
                },
            },
            {
                "api": "search_knowledge",
                "args": {
                    "query": "TiDB composite index equality predicate before range and order columns",
                    "source_scope": "all",
                    "kb_type": "performance",
                    "component": "sql",
                    "top_k": 3,
                },
            },
        ],
    },
    {
        "thinking": "先拆解长查询中的版本状态、可见性、存储状态和策略元数据点查，再对照两个表的定义与故障计划。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW CREATE TABLE test.qp01_object_catalog"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW CREATE TABLE test.qp01_bucket_policy"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": f"EXPLAIN ANALYZE {FAULT_QUERY_SQL}"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": f"EXPLAIN ANALYZE {CASE.admin_fault_query_sql}",
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT bucket_id, is_current, is_deleted, visibility, "
                        "COUNT(*) FROM test.qp01_object_catalog "
                        "GROUP BY bucket_id, is_current, is_deleted, visibility "
                        "ORDER BY bucket_id, is_current, is_deleted, visibility"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT bucket_id, tenant_id, policy_state, list_enabled, policy_version, is_current "
                        "FROM test.qp01_bucket_policy ORDER BY bucket_id, tenant_id"
                    )
                },
            },
        ],
    },
    {
        "thinking": "customer-list 的 bucket equality 必须先于 name 排序范围，tenant-admin-list 则必须先用 tenant/current/deleted 再按 updated_at；这是同一 catalog 上两个不同的真实访问前缀。",
        "action": {"api": "execute_sql", "args": {"sql_query": REPAIRED_INDEX_SQL}},
    },
    {
        "thinking": "tenant-admin-list 不能复用 bucket-first 索引，加入 tenant/current/deleted/updated_at 访问路径。",
        "action": {"api": "execute_sql", "args": {"sql_query": REPAIRED_ADMIN_INDEX_SQL}},
    },
    {
        "thinking": "policy lookup 有同 bucket 同 tenant 的历史版本；bucket_id,tenant_id 只能定位版本链，还必须把 is_current 和 policy_version 放进索引前缀。",
        "action": {"api": "execute_sql", "args": {"sql_query": REPAIRED_POLICY_INDEX_SQL}},
    },
    {
        "thinking": "刷新两张表的统计并在两个业务查询、版本化 policy lookup 和数据真值上验证三条访问路径。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {"sql_query": "ANALYZE TABLE test.qp01_object_catalog"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "ANALYZE TABLE test.qp01_bucket_policy"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": f"EXPLAIN ANALYZE {FAULT_QUERY_SQL}"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": f"EXPLAIN ANALYZE {CASE.admin_fault_query_sql}"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT 'catalog' AS source, COUNT(*), COALESCE(SUM(item_id), 0), "
                        "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', item_id, bucket_id, name, version_id, "
                        "payload, is_current, is_deleted, visibility, storage_class))), 0) "
                        "FROM test.qp01_object_catalog UNION ALL SELECT 'policy', COUNT(*), 0, "
                        "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', bucket_id, tenant_id, policy_state, list_enabled, policy_version, is_current))), 0) "
                        "FROM test.qp01_bucket_policy ORDER BY source"
                    )
                },
            },
        ],
    },
    {
        "thinking": "根因、扫描量、P95、结果集和 CRC 均已复核，提交结构化报告。",
        "action": {"api": "submit", "args": {"report": FULL_PASS_REPORT}},
    },
]


def main() -> None:
    scenario = SCENARIO
    parser = argparse.ArgumentParser(
        description="Run the TiDB QP01 composite-index order/correlation scenario."
    )
    parser.add_argument(
        "--case",
        required=True,
        choices=[case.case_id for case in scenario.cases],
    )
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--port", type=int, default=16650)
    parser.add_argument("--container-name", default="tidb-qp01-index-order")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    parser.add_argument(
        "--tool-profile",
        choices=("no_knowledge", "general_knowledge", "hierarchical_knowledge"),
        default="hierarchical_knowledge",
    )
    parser.add_argument(
        "--knowledge-backend",
        choices=("sqlite", "chroma"),
        default="sqlite",
        help="TiDB 8.1 knowledge index backend; build the selected index before a knowledge-enabled run.",
    )
    args = parser.parse_args()

    if args.mode == "llm" and not args.model:
        raise ValueError("--model is required when --mode=llm")

    os.environ["AIOPS_TIDB_KB_BACKEND"] = args.knowledge_backend

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
        agent.set_mock_responses(FULL_PASS_MOCK_RESPONSES)
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
    print(
        f"DP={result['DiagnosisPass']} OP={result['OutcomePass']} "
        f"SP={result['SafePass']}"
    )
    if args.mode == "mock":
        assert (
            result["DiagnosisPass"]
            and result["OutcomePass"]
            and result["SafePass"]
        ), json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    main()
