import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbQueryPerfLikeEscapeRangeScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


_MOCK_REPAIRED_LITERAL_ROUTE = (
    "SELECT q.request_id, q.bucket_id, q.path_prefix, q.path_fragment, q.path_suffix, q.search_mode, "
    "o.path, o.object_id, o.object_size, o.payload FROM test.qp07_suffix_template AS q "
    "JOIN test.qp07_object_catalog AS o ON o.bucket_id = q.bucket_id "
    "AND o.region_code = q.contract_region AND o.storage_tier = q.contract_storage_tier "
    "AND o.lifecycle_state = q.contract_lifecycle AND o.retention_epoch >= q.contract_min_retention "
    "AND o.legal_hold = q.contract_legal_hold "
    "AND o.path >= CONCAT(q.path_prefix, q.path_fragment) "
    "AND o.path < CONCAT(q.path_prefix, q.contract_route_upper) "
    "AND o.path LIKE CONCAT(q.compiled_prefix, "
    "REPLACE(REPLACE(REPLACE(q.path_fragment, CHAR(92), CONCAT(CHAR(92), CHAR(92))), "
    "'%', CONCAT(CHAR(92), '%')), '_', CONCAT(CHAR(92), '_')), q.path_suffix) "
    "AND q.route_shape IN ('literal_directory', 'literal_object_prefix') "
    "AND q.access_lane = 'customer_live' AND q.namespace_class = 'tenant_calendar' "
    "AND q.route_contract = 'literal_route' "
    "AND q.tail_policy IN ('directory_tail', 'object_prefix_tail') "
    "AND q.fragment_class IN ('underscore_route', 'mixed_metachar_route', 'percent_route') "
    "AND q.request_lane IN ('target_lane', 'neighbor_lane', 'same_namespace_lane', 'billing_lane', 'cross_bucket_lane') "
    "AND q.contract_status = 'serving' AND q.contract_priority = q.contract_id "
    "AND q.contract_region IN ('us-east-1', 'eu-west-1', 'us-west-2') "
    "AND q.contract_storage_tier IN ('hot', 'warm', 'cold') "
    "AND q.contract_lifecycle IN ('active', 'archived') "
    "AND q.contract_min_retention BETWEEN 202000 AND 203000 "
    "AND q.contract_legal_hold IN (0, 1) "
    "AND q.contract_route_upper > q.path_fragment "
    "AND q.contract_route_upper <> q.path_fragment "
    "AND q.contract_route_upper <> '' AND q.contract_min_size <= q.min_object_size "
    "AND q.contract_max_size >= q.max_object_size "
    "AND o.object_kind = q.object_kind AND o.visibility = q.visibility "
    "AND o.object_size BETWEEN q.min_object_size AND q.max_object_size "
    "AND o.object_size BETWEEN GREATEST(q.min_object_size, q.contract_min_size) "
    "AND LEAST(q.max_object_size, q.contract_max_size) "
    "AND o.object_id > 0 AND o.object_id <= q.max_object_size * 1000000 "
    "AND CHAR_LENGTH(o.path) >= CHAR_LENGTH(q.path_prefix) AND CHAR_LENGTH(o.path) <= 255 "
    "AND LEFT(o.path, CHAR_LENGTH(q.path_prefix)) = q.path_prefix "
    "AND LOCATE('/', o.path, CHAR_LENGTH(q.path_prefix) + 1) > CHAR_LENGTH(q.path_prefix) "
    "AND LOCATE('/object-', o.path, CHAR_LENGTH(q.path_prefix)) > CHAR_LENGTH(q.path_prefix) "
    "AND SUBSTRING_INDEX(SUBSTRING_INDEX(o.path, '/', 3), '/', -1) = SUBSTRING_INDEX(q.path_fragment, '/', 1) "
    "AND o.path REGEXP '^tenant-east/2026_[0-9]{2}/.+/object-[0-9]+$' "
    "AND RIGHT(o.path, 1) <> '/' AND CHAR_LENGTH(o.payload) BETWEEN 1 AND 128 "
    "AND LEFT(o.payload, 6) IN ('target', 'live-n') "
    "AND o.payload NOT REGEXP '(deleted|tombstone|placeholder)' "
    "AND COALESCE(o.payload, '') <> '' AND LOCATE('-', o.payload) > 0 "
    "AND (q.include_deleted = 1 OR (q.include_deleted = 0 AND o.deleted = 0)) "
    "AND COALESCE(o.deleted, 0) IN (0, 1) "
    "AND CASE WHEN q.visibility = 'customer' AND q.include_deleted = 0 THEN o.deleted = 0 "
    "WHEN q.visibility = 'customer' AND q.include_deleted = 1 THEN o.deleted IN (0, 1) "
    "WHEN q.visibility = 'internal' THEN o.visibility = q.visibility ELSE o.visibility = q.visibility END "
    "AND CHAR_LENGTH(q.path_fragment) BETWEEN 1 AND 255 "
    "AND CHAR_LENGTH(q.path_suffix) BETWEEN 1 AND 255 "
    "AND RIGHT(q.path_fragment, 1) = '/' "
    "AND (q.path_suffix = '%' OR RIGHT(q.path_suffix, 1) = '%') "
    "AND CHAR_LENGTH(o.path) - CHAR_LENGTH(REPLACE(o.path, '/', '')) BETWEEN 3 AND 5 "
    "AND LEFT(q.path_prefix, 7) = 'tenant-' "
    "AND LOCATE('-', q.request_name) > 0 "
    "AND SUBSTRING_INDEX(o.path, '/', 3) = CONCAT(SUBSTRING_INDEX(q.path_prefix, '/', 2), '/', SUBSTRING_INDEX(q.path_fragment, '/', 1)) "
    "AND CHAR_LENGTH(o.payload) + CHAR_LENGTH(q.request_name) <= 224 "
    "AND COALESCE(NULLIF(TRIM(o.payload), ''), 'missing') <> 'missing' "
    "AND SUBSTRING_INDEX(o.payload, '-', 1) IN ('target', 'live') "
    "AND (q.contract_status = 'serving' OR q.contract_status = 'shadow') "
    "WHERE q.active = 1 AND q.search_mode = 'literal_prefix' "
    "AND q.min_object_size <= q.max_object_size "
    "AND EXISTS (SELECT 1 FROM test.qp07_search_requests AS policy "
    "WHERE policy.request_id = q.request_id AND policy.active = 1 "
    "AND policy.bucket_id = o.bucket_id AND policy.object_kind = o.object_kind "
    "AND policy.visibility = o.visibility AND policy.search_mode = q.search_mode "
    "AND policy.path_fragment = q.path_fragment AND policy.path_suffix = q.path_suffix "
    "AND policy.request_name = q.request_name AND policy.min_object_size <= o.object_size "
    "AND policy.max_object_size >= o.object_size) "
    "AND NOT EXISTS (SELECT 1 FROM test.qp07_search_requests AS revoked "
    "WHERE revoked.request_id = q.request_id AND revoked.active = 0 "
    "AND revoked.request_name = q.request_name)"
)


_MOCK_LITERAL_ROUTE_SPECS = (
    ("bucket01", "tenant-east/2026_08/", "exports_2026/", "%"),
    ("bucket01", "tenant-east/2026_07/", "exports_2026/", "%"),
    ("bucket01", "tenant-east/2026_09/", "exports_2026/", "%"),
    ("bucket01", "tenant-east/2026_08/", "ingest_2026/", "%"),
    ("bucket01", "tenant-east/2026_08/", "reports_2026/", "%"),
    ("bucket01", "tenant-east/2026_08/", "exports_2026/", "object-00%"),
    ("bucket01", "tenant-east/2026_08/", "snapshots_2026/", "%"),
    ("bucket01", "tenant-east/2026_08/", "manifests_2026/", "%"),
    ("bucket01", "tenant-east/2026_08/", "archive_2026/", "%"),
    ("bucket02", "tenant-east/2026_08/", "exports_2026/", "%"),
    ("bucket01", "tenant-east/2026_08/", "exports_2026/", "object-000%"),
    ("bucket01", "tenant-east/2026_08/", "staging_2026/", "%"),
    ("bucket01", "tenant-east/2026_08/", "analytics_2026/", "%"),
    ("bucket01", "tenant-east/2026_08/", "exports_2026_archive/", "%"),
    ("bucket01", "tenant-east/2026_08/", "billing%_2026/", "%"),
)


def _next_ascii_prefix(value):
    last = ord(value[-1])
    if last >= 127:
        raise ValueError(f"QP07 mock route upper bound requires an ASCII terminal character: value={value!r}")
    return value[:-1] + chr(last + 1)


def _sql_literal(value):
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def _mock_compiled_literal_routes():
    branches = []
    for bucket_id, path_prefix, path_fragment, path_suffix in _MOCK_LITERAL_ROUTE_SPECS:
        lower_key = path_prefix + path_fragment
        upper_key = _next_ascii_prefix(lower_key)
        branches.append(
            _MOCK_REPAIRED_LITERAL_ROUTE.replace(
                "AND o.path >= CONCAT(q.path_prefix, q.path_fragment) "
                "AND o.path < CONCAT(q.path_prefix, q.contract_route_upper) ",
                "AND o.path >= " + _sql_literal(lower_key) + " "
                "AND o.path < " + _sql_literal(upper_key) + " "
                "AND q.bucket_id = " + _sql_literal(bucket_id) + " "
                "AND q.path_prefix = " + _sql_literal(path_prefix) + " "
                "AND q.path_fragment = " + _sql_literal(path_fragment) + " "
                "AND q.path_suffix = " + _sql_literal(path_suffix) + " ",
            )
        )
    return "\nUNION ALL\n".join(branches)


_MOCK_REPAIRED_LITERAL_ROUTE = _mock_compiled_literal_routes()


_MOCK_WILDCARD_ROUTE = (
    "SELECT q.request_id, q.bucket_id, q.path_prefix, q.path_fragment, q.path_suffix, q.search_mode, "
    "o.path, o.object_id, o.object_size, o.payload FROM test.qp07_suffix_template AS q "
    "JOIN test.qp07_object_catalog AS o ON o.bucket_id = q.bucket_id "
    "AND o.region_code = q.contract_region AND o.storage_tier = q.contract_storage_tier "
    "AND o.lifecycle_state = q.contract_lifecycle AND o.retention_epoch >= q.contract_min_retention "
    "AND o.legal_hold = q.contract_legal_hold "
    "AND o.path LIKE CONCAT(q.path_prefix, q.path_fragment, q.path_suffix) "
        "AND q.route_shape = 'wildcard_pattern' AND q.access_lane = 'customer_live' "
        "AND q.namespace_class = 'tenant_calendar' "
    "AND q.route_contract = 'pattern_route' AND q.tail_policy = 'pattern_tail' "
    "AND q.fragment_class = 'pattern_route' AND q.request_lane = 'pattern_lane' "
    "AND q.contract_status = 'serving' AND q.contract_priority = q.contract_id "
    "AND q.contract_region IN ('us-east-1', 'eu-west-1', 'us-west-2') "
    "AND q.contract_storage_tier IN ('hot', 'warm', 'cold') "
    "AND q.contract_lifecycle IN ('active', 'archived') "
    "AND q.contract_min_retention BETWEEN 202000 AND 203000 "
    "AND q.contract_legal_hold IN (0, 1) "
    "AND o.object_kind = q.object_kind AND o.visibility = q.visibility "
    "AND o.object_size BETWEEN q.min_object_size AND q.max_object_size AND o.object_id > 0 "
    "AND o.object_id <= q.max_object_size * 1000000 "
    "AND CHAR_LENGTH(o.path) >= CHAR_LENGTH(q.path_prefix) "
    "AND CHAR_LENGTH(o.path) <= 255 "
    "AND LOCATE('/', o.path, CHAR_LENGTH(q.path_prefix) + 1) > CHAR_LENGTH(q.path_prefix) "
    "AND LOCATE('/object-', o.path) > 0 "
    "AND o.path REGEXP '^tenant-east/2026_[0-9]{2}/.+/object-[0-9]+$' "
    "AND RIGHT(o.path, 1) <> '/' "
    "AND CHAR_LENGTH(o.payload) BETWEEN 1 AND 128 AND COALESCE(o.payload, '') <> '' "
    "AND LEFT(o.payload, 6) IN ('target', 'live-n') "
    "AND o.payload NOT REGEXP '(deleted|tombstone|placeholder)' "
    "AND (q.include_deleted = 1 OR (q.include_deleted = 0 AND o.deleted = 0)) "
    "AND COALESCE(o.deleted, 0) IN (0, 1) "
    "AND CASE WHEN q.visibility = 'customer' AND q.include_deleted = 0 THEN o.deleted = 0 "
    "WHEN q.visibility = 'customer' AND q.include_deleted = 1 THEN o.deleted IN (0, 1) "
    "WHEN q.visibility = 'internal' THEN o.visibility = q.visibility ELSE o.visibility = q.visibility END "
    "WHERE q.active = 1 AND q.search_mode = 'like_pattern' AND q.min_object_size <= q.max_object_size "
    "AND EXISTS (SELECT 1 FROM test.qp07_search_requests AS policy "
    "WHERE policy.request_id = q.request_id AND policy.active = 1 "
    "AND policy.bucket_id = o.bucket_id AND policy.object_kind = o.object_kind AND policy.visibility = o.visibility "
    "AND policy.search_mode = q.search_mode AND policy.path_fragment = q.path_fragment "
    "AND policy.path_suffix = q.path_suffix AND policy.request_name = q.request_name "
    "AND policy.min_object_size <= o.object_size AND policy.max_object_size >= o.object_size) "
    "AND NOT EXISTS (SELECT 1 FROM test.qp07_search_requests AS revoked "
    "WHERE revoked.request_id = q.request_id AND revoked.active = 0 AND revoked.request_name = q.request_name)"
)


_MOCK_REPAIRED_SEARCH_SQL = (
    "CREATE OR REPLACE VIEW test.qp07_search AS SELECT DISTINCT matched.request_id, matched.bucket_id, "
    "matched.path_prefix, matched.path_fragment, matched.path_suffix, matched.search_mode, matched.path, "
    "matched.object_id, matched.object_size, matched.payload FROM ("
    + _MOCK_REPAIRED_LITERAL_ROUTE + " UNION ALL " + _MOCK_WILDCARD_ROUTE
    + ") AS matched"
)


MOCK_RESPONSES = [
    {
        "thinking": "Correlate the object-search fingerprint with the query-latency series and statement-summary records before changing state.",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT digest_text, exec_count, avg_latency "
                        "FROM information_schema.statements_summary "
                        "WHERE digest_text LIKE '%qp07_search%' "
                        "ORDER BY exec_count DESC LIMIT 20"
                    )
                },
            },
        ],
    },
    {
        "thinking": "Inspect the mixed request inventory, the shared builder, the suffix template, and the target plan.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT request_id, bucket_id, path_prefix, path_fragment, path_suffix, search_mode, "
                        "object_kind, visibility, min_object_size, max_object_size, include_deleted, request_name "
                        "FROM test.qp07_search_requests ORDER BY request_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW CREATE VIEW test.qp07_query_builder"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW CREATE VIEW test.qp07_request_route"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT request_id, bucket_id, compiled_prefix, lower_key, upper_key, bind_status "
                        "FROM test.qp07_path_bindings ORDER BY request_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW CREATE VIEW test.qp07_suffix_template"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW CREATE VIEW test.qp07_search"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "EXPLAIN ANALYZE SELECT path, object_id, object_size, payload FROM test.qp07_search "
                        "WHERE request_id = 7001 ORDER BY path, object_id LIMIT 40"
                    )
                },
            },
        ],
    },
    {
        "thinking": "The builder already supplies the literal binding. Repair the shared route compiler for every literal route by joining a route specification that preserves the wildcard tail, escaping only route-name metacharacters, deriving a route-specific range, and leaving the wildcard branch parameterized; preserve every eligibility predicate and policy semi-join.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": _MOCK_REPAIRED_SEARCH_SQL
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "EXPLAIN ANALYZE SELECT path, object_id, object_size, payload FROM test.qp07_search "
                        "WHERE request_id = 7001 ORDER BY path, object_id LIMIT 40"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT path, object_id, object_size, payload FROM test.qp07_search "
                        "WHERE request_id = 7001 ORDER BY path, object_id LIMIT 40"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT COUNT(*), COALESCE(SUM(object_id), 0), "
                        "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', path, object_id, object_size, payload))), 0) "
                        "FROM test.qp07_search WHERE request_id = 7002"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT r.request_id, COUNT(v.object_id), COALESCE(SUM(v.object_id), 0), "
                        "COALESCE(BIT_XOR(CASE WHEN v.object_id IS NULL THEN NULL ELSE "
                        "CRC32(CONCAT_WS('#', v.path, v.object_id, v.object_size, v.payload)) END), 0) "
                        "FROM test.qp07_search_requests AS r "
                        "LEFT JOIN test.qp07_search AS v "
                        "ON v.request_id = r.request_id AND v.search_mode = 'literal_prefix' "
                        "WHERE r.active = 1 AND r.search_mode = 'literal_prefix' "
                        "GROUP BY r.request_id ORDER BY r.request_id"
                    )
                },
            },
            {
                "api": "submit",
                "args": {
                    "report": TidbQueryPerfLikeEscapeRangeScenario()
                    .get_case("literal_underscore_like_range")
                    .reference_report
                },
            },
        ],
    },
]


def main() -> None:
    scenario = TidbQueryPerfLikeEscapeRangeScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB QP07 object-prefix query-template scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--port", type=int, default=58500)
    parser.add_argument("--container-name", default="tidb-qp07-literal-prefix-suffix-template")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
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
        agent.set_mock_responses(MOCK_RESPONSES)
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)

    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode),
    ).run()
    print(
        "QP07 result: "
        f"DiagnosisPass={result['DiagnosisPass']} "
        f"OutcomePass={result['OutcomePass']} "
        f"SafePass={result['SafePass']}"
    )
    if args.mode == "mock" and (
        result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]
    ) != (True, True, True):
        raise AssertionError(f"QP07 mock path did not fully pass: {result!r}")


if __name__ == "__main__":
    main()
