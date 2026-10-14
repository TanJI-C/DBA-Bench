from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.query_perf.noncovering_index_tail_latency import (
    TidbQueryPerfNoncoveringIndexTailLatencyEvaluatorCase,
    TidbQueryPerfNoncoveringIndexTailLatencyReducedEvaluatorCase,
)
from src.scenarios.tidb.query_perf.noncovering_index_tail_latency_fault import (
    TidbQueryPerfNoncoveringIndexTailLatencyInjector as _TidbQueryPerfNoncoveringIndexTailLatencyInjector,
)
from src.workloads.specs import SessionSetupBehavior, WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


class TidbQueryPerfNoncoveringIndexTailLatencyInjector(
    _TidbQueryPerfNoncoveringIndexTailLatencyInjector
):
    install = _TidbQueryPerfNoncoveringIndexTailLatencyInjector.install
    activate = _TidbQueryPerfNoncoveringIndexTailLatencyInjector.activate
    prepare_observability = _TidbQueryPerfNoncoveringIndexTailLatencyInjector.prepare_observability
    quiesce = _TidbQueryPerfNoncoveringIndexTailLatencyInjector.quiesce
    recover = _TidbQueryPerfNoncoveringIndexTailLatencyInjector.recover


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfNoncoveringIndexTailLatencyForOrderHistoryScenarioCase(TiDBScenarioCase):
    db: str
    table: str
    audit_table: str
    page_context_table: str
    route_registry_table: str
    row_count: int
    query: str
    workload_query: str
    table_crc_sql: str
    page_context_truth_sql: str
    route_registry_sql: str
    route_registry_truth_sql: str
    index_catalog_sql: str
    stats_sql: str
    table_size_sql: str
    ddl_jobs_sql: str
    fault_index_names: tuple[str, ...]
    replaceable_fault_index_names: tuple[str, ...]
    route_registry_rows: tuple[tuple[object, ...], ...]
    route_registry_row_count: int
    target_workload_fingerprint: str
    expected_target_result_count: int
    fault_scan_floor: int
    recovered_scan_ceiling: int
    latency_sample_count: int
    p95_slo_ms: float
    target_qps: float
    target_traffic_share_percent: float
    read_write_ratio_percent: tuple[float, float]
    target_profile_name: str
    neighbor_profile_names: tuple[str, ...]
    decoy_profile_names: tuple[str, ...]
    write_profile_name: str
    observation_window_seconds: int
    neighbor_p95_slo_ms: float
    write_p95_slo_ms: float


_DB = "benchops"
_TABLE = "qp05_order_events"
_AUDIT_TABLE = "qp05_order_event_audit"
_PAGE_CONTEXT_TABLE = "qp05_page_context"
_ROUTE_REGISTRY_TABLE = "qp05_route_registry"
_ROW_COUNT = 1_000_000
_SESSION_FINGERPRINT = "@aiopsbench_qp05_request_fingerprint"
_ROUTE_REGISTRY_ROWS = (
    ("qp05_fp_01", "merchant-settlement-page", 4, 1, "settlement", "aggregate", 450),
    ("qp05_fp_01", "merchant-settlement-page", 3, 0, "settlement", "aggregate", 450),
    ("qp05_fp_02", "checkout-history-export", 7, 1, "export", "page_projection", 300),
    ("qp05_fp_02", "checkout-history-export", 6, 0, "export", "full_projection", 900),
    ("qp05_fp_03", "checkout-history-replay", 5, 1, "replay", "page_projection", 300),
    ("qp05_fp_03", "checkout-history-replay", 4, 0, "replay", "page_projection", 300),
    ("qp05_fp_04", "checkout-history-ops", 8, 1, "operations", "page_projection", 300),
    ("qp05_fp_04", "checkout-history-ops", 7, 0, "operations", "page_projection", 300),
    ("qp05_fp_05", "checkout-history-export", 7, 1, "export", "full_projection", 900),
    ("qp05_fp_05", "checkout-history-export", 6, 0, "export", "full_projection", 900),
    ("qp05_fp_06", "warehouse-replay-page", 3, 1, "warehouse", "wide_range", 600),
    ("qp05_fp_06", "warehouse-replay-page", 2, 0, "warehouse", "wide_range", 600),
    ("qp05_fp_07", "checkout-history-page", 9, 1, "page", "page_projection", 300),
    ("qp05_fp_07", "checkout-history-page", 8, 0, "page", "page_projection", 300),
    ("qp05_fp_08", "customer-support-page", 4, 1, "support", "aggregate", 500),
    ("qp05_fp_08", "customer-support-page", 3, 0, "support", "aggregate", 500),
    ("qp05_fp_09", "fraud-review-page", 6, 1, "fraud", "aggregate", 500),
    ("qp05_fp_09", "fraud-review-page", 5, 0, "fraud", "aggregate", 500),
    ("qp05_fp_10", "checkout-history-page-mobile", 2, 1, "page", "page_projection", 120),
    ("qp05_fp_10", "checkout-history-page-mobile", 1, 0, "page", "page_projection", 120),
    ("qp05_fp_11", "checkout-history-page", 9, 1, "schema", "catalog", 1000),
    ("qp05_fp_11", "checkout-history-page", 8, 0, "schema", "catalog", 1000),
    ("qp05_fp_12", "checkout-history-page", 9, 1, "schema", "catalog", 1000),
    ("qp05_fp_12", "checkout-history-page", 8, 0, "schema", "catalog", 1000),
    ("qp05_fp_13", "checkout-history-page", 9, 1, "audit", "aggregate", 1000),
    ("qp05_fp_13", "checkout-history-page", 8, 0, "audit", "aggregate", 1000),
    ("qp05_fp_14", "checkout-history-page", 9, 1, "point_read", "point", 1000),
    ("qp05_fp_14", "checkout-history-page", 8, 0, "point_read", "point", 1000),
    ("qp05_fp_15", "checkout-history-page", 9, 1, "writer", "update", 1000),
    ("qp05_fp_15", "checkout-history-page", 8, 0, "writer", "update", 1000),
    ("qp05_fp_16", "merchant-settlement-page", 4, 1, "merchant", "wide_range", 600),
    ("qp05_fp_16", "merchant-settlement-page", 3, 0, "merchant", "wide_range", 600),
    ("qp05_fp_17", "customer-support-page", 4, 1, "customer", "wide_range", 600),
    ("qp05_fp_17", "customer-support-page", 3, 0, "customer", "wide_range", 600),
    ("qp05_fp_18", "warehouse-replay-page", 3, 1, "tenant_range", "wide_range", 600),
    ("qp05_fp_18", "warehouse-replay-page", 2, 0, "tenant_range", "wide_range", 600),
)


def _route_query(scope_expression: str) -> str:
    return (
        "WITH page_scope AS ("
        f"SELECT c.tenant_id, c.order_state, c.window_start, c.window_end "
        f"FROM {_DB}.{_ROUTE_REGISTRY_TABLE} AS r "
        f"JOIN {_DB}.{_PAGE_CONTEXT_TABLE} AS c ON c.route_key = r.route_key "
        f"WHERE r.fingerprint = {scope_expression} AND r.is_current = 1"
        ") "
        "SELECT e.event_id, e.tenant_id, e.event_time, e.order_state, "
        "e.order_total, e.currency, e.fulfillment_zone "
        f"FROM {_DB}.{_TABLE} AS e "
        "JOIN page_scope AS s "
        "ON e.tenant_id = s.tenant_id AND e.order_state = s.order_state "
        "WHERE e.event_time >= s.window_start "
        "AND e.event_time < s.window_end "
        "ORDER BY e.event_time, e.event_id LIMIT 100"
    )


_TARGET_QUERY = _route_query("'qp05_fp_07'")
_WORKLOAD_QUERY = _route_query(_SESSION_FINGERPRINT)
_TABLE_CRC_SQL = (
    "SELECT COUNT(*), SUM(event_id), "
    "BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_time, order_state, "
    "order_total, currency, fulfillment_zone, merchant_id, customer_ref, last_modified))) "
    f"FROM {_DB}.{_TABLE}"
)
_PAGE_CONTEXT_TRUTH_SQL = (
    "SELECT route_key, tenant_id, order_state, window_start, window_end "
    f"FROM {_DB}.{_PAGE_CONTEXT_TABLE} ORDER BY route_key"
)
_ROUTE_REGISTRY_SQL = (
    "SELECT fingerprint, route_key, route_version, is_current, surface, projection_class, slo_ms "
    f"FROM {_DB}.{_ROUTE_REGISTRY_TABLE} ORDER BY fingerprint, route_version DESC"
)
_ROUTE_REGISTRY_TRUTH_SQL = _ROUTE_REGISTRY_SQL
_INDEX_CATALOG_SQL = f"SHOW INDEX FROM {_DB}.{_TABLE}"
_STATS_SQL = (
    f"SHOW STATS_META WHERE Db_name = '{_DB}' AND Table_name = '{_TABLE}'"
)
_TABLE_SIZE_SQL = (
    "SELECT TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH "
    "FROM information_schema.tables "
    f"WHERE TABLE_SCHEMA = '{_DB}' AND TABLE_NAME = '{_TABLE}'"
)
_DDL_JOBS_SQL = "ADMIN SHOW DDL JOBS 20"
_FAULT_INDEX_NAMES = (
    "qp05_event_time_state_tenant_id",
    "qp05_state_time_tenant_id",
    "qp05_history_projection_v2",
    "qp05_event_time_state_tenant_id_v2",
    "qp05_state_time_tenant_id_v2",
    "qp05_history_full_replay_v3",
    "qp05_history_state_replay_v4",
    "qp05_history_zone_replay_v4",
)
_REPLACEABLE_FAULT_INDEX_NAMES = _FAULT_INDEX_NAMES


def _session_context(fingerprint: str) -> str:
    return f"SET {_SESSION_FINGERPRINT} = '{fingerprint}'"


def _session_setup_behavior(fingerprint: str) -> SessionSetupBehavior:
    return SessionSetupBehavior(
        config_query="SELECT 1",
        statement=_session_context(fingerprint),
        statement_count=lambda _configuration, _checkout_number: 1,
    )


def _background_workload() -> BackgroundWorkloadSpec:
    return BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="qp05_fp_07",
                sql=_WORKLOAD_QUERY,
                qps=4.0,
                tier="HEAVY",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
                session_setup=_session_setup_behavior("qp05_fp_07"),
            ),
            WorkloadProfile(
                name="qp05_fp_02",
                sql=_WORKLOAD_QUERY,
                qps=0.05,
                tier="MEDIUM",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
                session_setup=_session_setup_behavior("qp05_fp_02"),
            ),
            WorkloadProfile(
                name="qp05_fp_03",
                sql=_WORKLOAD_QUERY,
                qps=0.05,
                tier="MEDIUM",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
                session_setup=_session_setup_behavior("qp05_fp_03"),
            ),
            WorkloadProfile(
                name="qp05_fp_04",
                sql=_WORKLOAD_QUERY,
                qps=0.05,
                tier="MEDIUM",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
                session_setup=_session_setup_behavior("qp05_fp_04"),
            ),
            WorkloadProfile(
                name="qp05_fp_05",
                sql=(
                    f"SELECT event_id, tenant_id, event_time, order_state, order_total, currency, "
                    f"fulfillment_zone, merchant_id, customer_ref, last_modified, event_note "
                    f"FROM {_DB}.{_TABLE} WHERE tenant_id = 42 "
                    "AND event_time >= '2024-07-01' AND event_time < '2025-07-01' "
                    "ORDER BY event_time DESC, event_id DESC LIMIT 160"
                ),
                # Keep the full-projection neighbor visible without letting its
                # wide range scan starve the canonical page under the 100 ms SLO.
                qps=0.2,
                tier="HEAVY",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
            ),
            WorkloadProfile(
                name="qp05_fp_06",
                sql=(
                    f"SELECT event_id, event_time, order_state, merchant_id, customer_ref "
                    f"FROM {_DB}.{_TABLE} WHERE tenant_id BETWEEN 100 AND 260 "
                    "AND event_time >= '2024-07-01' AND event_time < '2025-07-01' "
                    "ORDER BY event_time DESC, event_id DESC LIMIT 240"
                ),
                qps=0.02,
                tier="HEAVY",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
            ),
            WorkloadProfile(
                name="qp05_fp_01",
                sql=(
                    f"SELECT tenant_id, order_state, COUNT(*), SUM(order_total) FROM {_DB}.{_TABLE} "
                    "WHERE tenant_id BETWEEN 100 AND 260 "
                    "AND event_time >= '2024-07-01' AND event_time < '2025-07-01' "
                    "GROUP BY tenant_id, order_state"
                ),
                qps=0.1,
                tier="HEAVY",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
            ),
            WorkloadProfile(
                name="qp05_fp_08",
                sql=(
                    f"SELECT tenant_id, order_state, COUNT(*) FROM {_DB}.{_TABLE} "
                    "WHERE tenant_id BETWEEN 100 AND 260 GROUP BY tenant_id, order_state"
                ),
                qps=0.2,
                tier="MEDIUM",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
            ),
            WorkloadProfile(
                name="qp05_fp_09",
                sql=(
                    f"SELECT merchant_id, order_state, COUNT(*), MAX(last_modified) "
                    f"FROM {_DB}.{_TABLE} WHERE merchant_id BETWEEN 1000 AND 1040 "
                    "GROUP BY merchant_id, order_state"
                ),
                qps=0.02,
                tier="MEDIUM",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
            ),
            WorkloadProfile(
                name="qp05_fp_10",
                sql=_WORKLOAD_QUERY,
                qps=0.05,
                tier="MEDIUM",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
                session_setup=_session_setup_behavior("qp05_fp_10"),
            ),
            WorkloadProfile(
                name="qp05_fp_11",
                sql=(
                    "SELECT TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME "
                    "FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = 'benchops' "
                    "ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX"
                ),
                qps=0.4,
                tier="LIGHT",
                application_name="schema-observer",
                connection_pool="checkout-history-admin",
            ),
            WorkloadProfile(
                name="qp05_fp_12",
                sql=(
                    "SELECT TABLE_NAME, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH "
                    "FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'benchops' "
                    "ORDER BY TABLE_NAME"
                ),
                qps=0.4,
                tier="LIGHT",
                application_name="schema-observer",
                connection_pool="checkout-history-admin",
            ),
            WorkloadProfile(
                name="qp05_fp_13",
                sql=(
                    f"SELECT operation, COUNT(*) FROM {_DB}.{_AUDIT_TABLE} "
                    "GROUP BY operation ORDER BY operation"
                ),
                qps=0.5,
                tier="LIGHT",
                application_name="order-audit-monitor",
                connection_pool="checkout-history-admin",
            ),
            WorkloadProfile(
                name="qp05_fp_14",
                sql=(
                    f"SELECT event_id, order_state, order_total FROM {_DB}.{_TABLE} "
                    "WHERE event_id = MOD(CAST(UNIX_TIMESTAMP(NOW(6)) * 1000 AS UNSIGNED), 1000000) + 1"
                ),
                qps=0.8,
                tier="LIGHT",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
            ),
            WorkloadProfile(
                name="qp05_fp_15",
                sql=(
                    f"UPDATE {_DB}.{_TABLE} SET order_total = order_total + 0.01, "
                    "event_note = CONCAT('checkout-event-', event_id), "
                    "last_modified = last_modified + INTERVAL 1 SECOND, "
                    "merchant_id = merchant_id + 1, "
                    "customer_ref = LPAD(CAST(MOD(CAST(customer_ref AS UNSIGNED) + 1, 100000) AS CHAR), 10, '0') "
                    "WHERE event_id BETWEEN "
                    "MOD(CAST(UNIX_TIMESTAMP(NOW(6)) * 1000 AS UNSIGNED), 1000000) + 1 "
                    "AND MOD(CAST(UNIX_TIMESTAMP(NOW(6)) * 1000 AS UNSIGNED), 1000000) + 312"
                ),
                qps=1.3575,
                tier="WRITE",
                commit=False,
                application_name="checkout-history-writer",
                connection_pool="checkout-history-write",
            ),
            WorkloadProfile(
                name="qp05_fp_16",
                sql=(
                    f"SELECT event_id, tenant_id, event_time, order_state, order_total, currency, fulfillment_zone "
                    f"FROM {_DB}.{_TABLE} WHERE merchant_id BETWEEN 1000 AND 1120 "
                    "AND event_time >= '2025-01-01' AND event_time < '2025-07-01' "
                    "ORDER BY event_time, event_id LIMIT 240"
                ),
                qps=0.02,
                tier="HEAVY",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
            ),
            WorkloadProfile(
                name="qp05_fp_17",
                sql=(
                    f"SELECT event_id, tenant_id, event_time, order_state, order_total, currency, fulfillment_zone "
                    f"FROM {_DB}.{_TABLE} WHERE customer_ref BETWEEN '0000000000' AND '0000500000' "
                    "AND event_time >= '2025-01-01' AND event_time < '2025-07-01' "
                    "ORDER BY event_time, event_id LIMIT 240"
                ),
                qps=0.02,
                tier="HEAVY",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
            ),
            WorkloadProfile(
                name="qp05_fp_18",
                sql=(
                    f"SELECT event_id, tenant_id, event_time, order_state, order_total, currency, fulfillment_zone "
                    f"FROM {_DB}.{_TABLE} WHERE tenant_id BETWEEN 100 AND 260 "
                    "AND event_time >= '2025-01-01' AND event_time < '2025-07-01' "
                    "ORDER BY event_time, event_id LIMIT 240"
                ),
                qps=0.02,
                tier="HEAVY",
                application_name="checkout-history-api",
                connection_pool="checkout-history-ro",
            ),
        ),
        worker_count=8,
        seed=20260806,
        # Capture the broad fault plan before the full mixed replay starts. The
        # workload is still active for the complete agent loop and final SLO.
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=10,
    )


_REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "root_cause",
                "factor": (
                    "the target order-history query uses an access path whose event_time range is evaluated "
                    "before tenant_id and order_state equality, so TiKV scans a broad time slice before the "
                    "page predicates can narrow it"
                ),
                "entity": "benchops.qp05_order_events",
                "evidence": ["EXPLAIN ANALYZE shows the range-leading composite index and broad TiKV scan"],
            },
            {
                "type": "root_cause",
                "factor": (
                    "the existing candidates split range selectivity and projection coverage: the range-leading "
                    "paths do not cover the page projection, while the equality-leading near paths do not put "
                    "both equality predicates before the event_time range in one complete covering path"
                ),
                "entity": "benchops.qp05_order_events",
                "evidence": ["EXPLAIN ANALYZE shows back-to-table reads and SHOW INDEX exposes candidate column orders"],
            },
            {
                "type": "necessary_exclusion",
                "factor": (
                    "the p95 tail is caused by TiKV coprocessor scan amplification "
                    "while PD, TiDB, and TiKV node health remain normal, so this is not a cluster node failure"
                ),
                "entity": "PD, TiDB, and TiKV components",
                "evidence": ["node health and logs show the distributed components are healthy"],
            },
        ]
    },
    "outcome": {
        "changes": ["created one equivalent composite covering access path with equality columns before the time range"],
        "verification": [
            "EXPLAIN ANALYZE is an IndexReader without IndexLookUp/TableRowIDScan",
            "scan volume and target p95 recovered while business truth and ADMIN CHECK TABLE remained valid",
        ],
    },
    "summary": "The report identifies the range-leading and non-covering access path, excludes a component outage, and uses a replacement path that preserves the writer budget.",
}

_CASE = TidbQueryPerfNoncoveringIndexTailLatencyForOrderHistoryScenarioCase(
    case_id="noncovering_index_tail_latency",
    case_no=0,
    evaluator=TidbQueryPerfNoncoveringIndexTailLatencyEvaluatorCase,
    title=(
        "Checkout order-history page p95 regresses in a multi-tenant traffic mix."
    ),
    alert=(
        "[CRITICAL] the checkout order-history page is above its 100 ms database p95 budget "
        "while returned order rows remain correct. Restore target p95 to <=100 ms, keep "
        "same-domain neighbor reads <=360 ms p95 and the order-event writer <=350 ms p95, "
        "leave the canonical plan at <=10,000 process keys with IndexReader and no "
        "IndexLookUp/TableRowIDScan, leave schema DDL fully public/synced with visible "
        "stats, preserve healthy neighbor indexes, and do not change order-event records, "
        "route registry, or page context."
    ),
    initial_state={
        "status": "degraded",
        "table_rows": _ROW_COUNT,
        "page_route": "checkout-history-page",
        "workload": "checkout-history API traffic with nearby export, replay, reporting and write activity",
    },
    expected_target={
        "status": "recovered",
        "p95_slo_ms": 100.0,
        "neighbor_p95_slo_ms": 360.0,
        "write_p95_slo_ms": 350.0,
        "table_rows": _ROW_COUNT,
    },
    reference_report=_REFERENCE_REPORT,
    background_workload=_background_workload(),
    difficulty=DifficultyCalibration(
        diagnostic_depth=10,
        environmental_complexity=0.790131,
        reference_run_ids=(
            "reference-108__tidb_query_perf_noncovering_index_tail_latency__noncovering_index_tail_latency__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=3,
        tidb_count=1,
        # The 1M-row mixed replay can briefly exceed 4 GiB during wide scans;
        # keep the workload contract stable without turning cgroup OOM into an invalid run.
        tikv_memory_mb=6144,
        tidb_memory_mb=4096,
        sql_timeout_seconds=600,
        image_group_key="qp05-composite-noncovering-index-tail-latency-v3",
    ),
    db=_DB,
    table=_TABLE,
    audit_table=_AUDIT_TABLE,
    page_context_table=_PAGE_CONTEXT_TABLE,
    route_registry_table=_ROUTE_REGISTRY_TABLE,
    row_count=_ROW_COUNT,
    query=_TARGET_QUERY,
    workload_query=_WORKLOAD_QUERY,
    table_crc_sql=_TABLE_CRC_SQL,
    page_context_truth_sql=_PAGE_CONTEXT_TRUTH_SQL,
    route_registry_sql=_ROUTE_REGISTRY_SQL,
    route_registry_truth_sql=_ROUTE_REGISTRY_TRUTH_SQL,
    index_catalog_sql=_INDEX_CATALOG_SQL,
    stats_sql=_STATS_SQL,
    table_size_sql=_TABLE_SIZE_SQL,
    ddl_jobs_sql=_DDL_JOBS_SQL,
    fault_index_names=_FAULT_INDEX_NAMES,
    replaceable_fault_index_names=_REPLACEABLE_FAULT_INDEX_NAMES,
    route_registry_rows=_ROUTE_REGISTRY_ROWS,
    route_registry_row_count=len(_ROUTE_REGISTRY_ROWS),
    target_workload_fingerprint="qp05_fp_07",
    expected_target_result_count=100,
    fault_scan_floor=12_000,
    recovered_scan_ceiling=10_000,
    latency_sample_count=7,
    p95_slo_ms=100.0,
    target_qps=4.0,
    target_traffic_share_percent=48.44,
    read_write_ratio_percent=(83.56, 16.44),
    target_profile_name="qp05_fp_07",
    neighbor_profile_names=(
        "qp05_fp_02",
        "qp05_fp_03",
        "qp05_fp_04",
        "qp05_fp_10",
        "qp05_fp_11",
        "qp05_fp_12",
        "qp05_fp_13",
        "qp05_fp_14",
    ),
    decoy_profile_names=(
        "qp05_fp_01",
        "qp05_fp_05",
        "qp05_fp_06",
        "qp05_fp_08",
        "qp05_fp_09",
        "qp05_fp_16",
        "qp05_fp_17",
        "qp05_fp_18",
    ),
    write_profile_name="qp05_fp_15",
    observation_window_seconds=60,
    neighbor_p95_slo_ms=360.0,
    # Keep the rollback writer observable without letting host I/O contention
    # turn the replacement reference into a writer-only failure.
    write_p95_slo_ms=350.0,
)

_CASE_REDUCED = replace(
    _CASE,
    case_id="noncovering_index_tail_latency_reduced",
    case_no=1,
    evaluator=TidbQueryPerfNoncoveringIndexTailLatencyReducedEvaluatorCase,
    title="Checkout order-history page p95 regresses in a multi-tenant traffic mix.",
    row_count=500_000,
    fault_scan_floor=6_000,
    difficulty=DifficultyCalibration(
        diagnostic_depth=10,
        environmental_complexity=0.621538,
        reference_run_ids=(
            "reference-271__tidb_query_perf_noncovering_index_tail_latency__noncovering_index_tail_latency_reduced__mock__r001",
        ),
    ),
)


class TidbQueryPerfNoncoveringIndexTailLatencyScenario(TiDBScenario):
    scenario_id = "tidb_query_perf_noncovering_index_tail_latency"
    description = (
        "A production-shaped TiDB checkout order-history API regresses inside a mixed, "
        "multi-tenant workload and must be restored without changing business truth."
    )
    cases = (_CASE, _CASE_REDUCED)

    def build_fault_plan(
        self,
        case: TidbQueryPerfNoncoveringIndexTailLatencyForOrderHistoryScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbQueryPerfNoncoveringIndexTailLatencyInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "audit_table": case.audit_table,
                    "page_context_table": case.page_context_table,
                    "route_registry_table": case.route_registry_table,
                    "row_count": case.row_count,
                    "query": case.query,
                    "workload_query": case.workload_query,
                    "table_crc_sql": case.table_crc_sql,
                    "page_context_truth_sql": case.page_context_truth_sql,
                    "route_registry_sql": case.route_registry_sql,
                    "route_registry_truth_sql": case.route_registry_truth_sql,
                    "index_catalog_sql": case.index_catalog_sql,
                    "stats_sql": case.stats_sql,
                    "table_size_sql": case.table_size_sql,
                    "ddl_jobs_sql": case.ddl_jobs_sql,
                    "fault_index_names": case.fault_index_names,
                    "replaceable_fault_index_names": case.replaceable_fault_index_names,
                    "route_registry_rows": case.route_registry_rows,
                    "route_registry_row_count": case.route_registry_row_count,
                    "target_workload_fingerprint": case.target_workload_fingerprint,
                    "fault_scan_floor": case.fault_scan_floor,
                    "p95_slo_ms": case.p95_slo_ms,
                    "latency_sample_count": case.latency_sample_count,
                    "target_profile_name": case.target_profile_name,
                    "neighbor_profile_names": case.neighbor_profile_names,
                    "write_profile_name": case.write_profile_name,
                    "observation_window_seconds": case.observation_window_seconds,
                    "neighbor_p95_slo_ms": case.neighbor_p95_slo_ms,
                    "write_p95_slo_ms": case.write_p95_slo_ms,
                },
            ),
        )
