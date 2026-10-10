import re

from collections.abc import Mapping

from src.database.query_results import capture_query_result_truth

from src.database.sql import execute_json_payload

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext

from src.scenarios.tidb.common import validate_sql_identifier

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.resource_governance import (
    TidbResourceGovernanceSqlBindingEvaluatorCase,
    TidbResourceGovernanceSqlBindingChannelWindowEvaluatorCase,
)
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


_RG10_DB = "test"
_RG10_TABLE = "event_log"
_RG10_ORDER_TABLE = "order_activity"
_RG10_CUSTOMER_TABLE = "customer_profile"
_RG10_EXPECTED_INDEX = "idx_tenant_time"
_RG10_DECOY_INDEX = "idx_type"
_RG10_TARGET_FILTER = (
    "((tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-02 00:00:00' AND event_type = 'refund') "
    "OR (tenant_id = 7 AND event_ts >= '2026-01-02 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND event_type = 'charge'))"
)
_RG10_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE}"
    f" WHERE {_RG10_TARGET_FILTER} ORDER BY event_id"
)
_RG10_BINDING_TEMPLATE_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE ((tenant_id = 8 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-02 00:00:00' AND event_type = 'refund') "
    "OR (tenant_id = 8 AND event_ts >= '2026-01-02 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND event_type = 'charge')) ORDER BY event_id"
)
_RG10_RESULT_SUMMARY = (
    "SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_ts, "
    f"event_type, amount))), 0) FROM {_RG10_DB}.{_RG10_TABLE} WHERE {_RG10_TARGET_FILTER}"
)
_RG10_ORDER_QUERY = (
    f"SELECT order_id, tenant_id, status FROM {_RG10_DB}.{_RG10_ORDER_TABLE} "
    "WHERE tenant_id = 7 ORDER BY order_id LIMIT 50"
)
_RG10_CUSTOMER_QUERY = (
    f"SELECT customer_id, segment FROM {_RG10_DB}.{_RG10_CUSTOMER_TABLE} "
    "WHERE tenant_id IN (7, 8) LIMIT 100"
)
_RG10_CHANNEL_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND channel = 'mobile' ORDER BY event_id"
)
_RG10_CHANNEL_TARGET_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND channel = 'batch' ORDER BY event_id"
)
_RG10_CHANNEL_TARGET_SUMMARY = (
    "SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_ts, "
    f"event_type, amount))), 0) FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND channel = 'batch'"
)
_RG10_AMOUNT_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND amount BETWEEN 100.00 AND 200.00 "
    "ORDER BY event_id"
)
_RG10_LIMIT_VARIANT_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND event_type IN ('refund', 'charge') "
    "ORDER BY event_id LIMIT 100"
)
_RG10_PREDICATE_SWAP_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE ((event_type = 'refund' AND tenant_id = 8 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-02 00:00:00') "
    "OR (event_type = 'charge' AND tenant_id = 8 AND event_ts >= '2026-01-02 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00')) ORDER BY event_id"
)
_RG10_EXTRA_PREDICATE_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND event_type IN ('refund', 'charge') "
    "AND event_id > 50000 ORDER BY event_id"
)
_RG10_TENANT8_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 8 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND event_type IN ('refund', 'charge') "
    "ORDER BY event_id"
)
_RG10_REFUND_WINDOW_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE event_type = 'refund' AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND tenant_id IN (7, 8) "
    "ORDER BY event_id"
)
_RG10_TENANT_TIME_REORDER_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE event_ts >= '2026-01-01 00:00:00' AND event_ts < '2026-01-03 00:00:00' "
    "AND tenant_id = 7 AND event_type IN ('refund', 'charge') ORDER BY event_id LIMIT 200"
)
_RG10_EVENT_RANGE_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_id BETWEEN 1 AND 90000 "
    "AND event_ts < '2026-01-03 00:00:00' ORDER BY event_id"
)
_RG10_TENANT_DAY_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-02 00:00:00' ORDER BY event_id"
)
_RG10_TYPE_TENANT_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE event_type IN ('refund', 'charge') AND tenant_id = 7 "
    "AND event_ts >= '2026-01-01 00:00:00' AND event_ts < '2026-01-03 00:00:00' "
    "ORDER BY event_id LIMIT 200"
)
_RG10_WINDOW_ORDER_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND event_type IN ('refund', 'charge') "
    "ORDER BY event_ts, event_id LIMIT 200"
)
_RG10_REFUND_TENANT_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_type = 'refund' AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' ORDER BY event_id LIMIT 200"
)
_RG10_CHARGE_TENANT_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_type = 'charge' AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' ORDER BY event_id LIMIT 200"
)
_RG10_TENANT_PAIR_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id IN (7, 8) AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND event_type IN ('refund', 'charge') "
    "ORDER BY event_id LIMIT 200"
)
_RG10_WEB_CHANNEL_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND channel = 'web' "
    "ORDER BY event_id LIMIT 200"
)
_RG10_AMOUNT_CAP_QUERY = (
    f"SELECT event_id, tenant_id, event_ts, event_type, amount FROM {_RG10_DB}.{_RG10_TABLE} "
    "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
    "AND event_ts < '2026-01-03 00:00:00' AND amount < 300.00 "
    "ORDER BY event_id LIMIT 200"
)
_RG10_CHANNEL_MOBILE_IN_QUERY = _RG10_CHANNEL_QUERY.replace(
    "channel = 'mobile'", "channel IN ('mobile')"
)
_RG10_CHANNEL_WEB_IN_QUERY = _RG10_WEB_CHANNEL_QUERY.replace(
    "channel = 'web'", "channel IN ('web')"
)
_RG10_GLOBAL_NOISE_BINDINGS = (
    (_RG10_ORDER_QUERY, _RG10_ORDER_TABLE, "idx_order_tenant"),
    (_RG10_CUSTOMER_QUERY, _RG10_CUSTOMER_TABLE, "idx_customer_tenant"),
    (_RG10_CHANNEL_QUERY, _RG10_TABLE, "idx_channel_time"),
    (_RG10_AMOUNT_QUERY, _RG10_TABLE, "idx_amount_event"),
    (_RG10_LIMIT_VARIANT_QUERY, _RG10_TABLE, "idx_type"),
    (_RG10_PREDICATE_SWAP_QUERY, _RG10_TABLE, "idx_channel_time"),
    (_RG10_EXTRA_PREDICATE_QUERY, _RG10_TABLE, "idx_amount_event"),
    (_RG10_TENANT8_QUERY, _RG10_TABLE, _RG10_EXPECTED_INDEX),
    (_RG10_REFUND_WINDOW_QUERY, _RG10_TABLE, _RG10_DECOY_INDEX),
    (_RG10_TENANT_TIME_REORDER_QUERY, _RG10_TABLE, "idx_channel_time"),
    (_RG10_EVENT_RANGE_QUERY, _RG10_TABLE, "idx_amount_event"),
    (_RG10_TENANT_DAY_QUERY, _RG10_TABLE, _RG10_EXPECTED_INDEX),
    (_RG10_TYPE_TENANT_QUERY, _RG10_TABLE, _RG10_DECOY_INDEX),
    (_RG10_WINDOW_ORDER_QUERY, _RG10_TABLE, "idx_tenant_time"),
    (_RG10_REFUND_TENANT_QUERY, _RG10_TABLE, _RG10_DECOY_INDEX),
    (_RG10_CHARGE_TENANT_QUERY, _RG10_TABLE, _RG10_DECOY_INDEX),
    (_RG10_TENANT_PAIR_QUERY, _RG10_TABLE, "idx_tenant_time"),
    (_RG10_WEB_CHANNEL_QUERY, _RG10_TABLE, "idx_channel_time"),
    (_RG10_AMOUNT_CAP_QUERY, _RG10_TABLE, "idx_amount_event"),
)
_RG10_CHANNEL_GLOBAL_NOISE_BINDINGS = tuple(
    (
        (
            _RG10_CHANNEL_MOBILE_IN_QUERY
            if query == _RG10_CHANNEL_QUERY
            else _RG10_CHANNEL_WEB_IN_QUERY
            if query == _RG10_WEB_CHANNEL_QUERY
            else query
        ),
        table,
        index,
    )
    for query, table, index in _RG10_GLOBAL_NOISE_BINDINGS
)


def _profile(name: str, sql: str, qps: float, tier: str, application_name: str) -> WorkloadProfile:
    return WorkloadProfile(
        name=name,
        sql=sql,
        qps=qps,
        tier=tier,
        application_name=application_name,
    )


_RG10_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        _profile(
            "wrk_03",
            f"SELECT COUNT(*), COALESCE(SUM(event_id), 0) FROM {_RG10_DB}.{_RG10_TABLE} "
            "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
            "AND event_ts < '2026-01-02 00:00:00'",
            0.20,
            "SEARCH_READ",
            "search-api",
        ),
        _profile(
            "wrk_04",
            f"SELECT COUNT(*), COALESCE(SUM(event_id), 0) FROM {_RG10_DB}.{_RG10_TABLE} "
            "WHERE tenant_id = 7 AND event_ts >= '2026-01-02 00:00:00' "
            "AND event_ts < '2026-01-03 00:00:00'",
            0.20,
            "SEARCH_READ",
            "search-api",
        ),
        _profile(
            "wrk_05",
            f"SELECT COUNT(*) FROM {_RG10_DB}.{_RG10_TABLE} "
            "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
            "AND event_ts < '2026-01-03 00:00:00' AND event_type IN ('refund', 'charge')",
            0.18,
            "SEARCH_READ",
            "search-api",
        ),
        _profile("wrk_06", _RG10_LIMIT_VARIANT_QUERY, 0.15, "SEARCH_READ", "search-api"),
        _profile(
            "wrk_07",
            f"SELECT COUNT(*), MIN(event_id), MAX(event_id) FROM {_RG10_DB}.{_RG10_TABLE} "
            "WHERE tenant_id = 7 AND event_ts >= '2026-01-01 00:00:00' "
            "AND event_ts < '2026-01-03 00:00:00'",
            0.20,
            "SEARCH_READ",
            "search-api",
        ),
        _profile(
            "wrk_08",
            f"SELECT COUNT(*), COALESCE(SUM(event_id), 0) FROM {_RG10_DB}.{_RG10_TABLE} "
            "WHERE tenant_id = 8 AND event_ts >= '2026-01-01 00:00:00' "
            "AND event_ts < '2026-01-03 00:00:00'",
            0.22,
            "SEARCH_READ",
            "search-api",
        ),
        _profile(
            "wrk_09",
            f"SELECT COUNT(*), COALESCE(SUM(event_id), 0) FROM {_RG10_DB}.{_RG10_TABLE} "
            "WHERE event_type = 'refund' AND event_ts >= '2026-01-01 00:00:00' "
            "AND event_ts < '2026-01-03 00:00:00'",
            0.22,
            "SEARCH_READ",
            "search-api",
        ),
        _profile(
            "wrk_10",
            f"SELECT COUNT(*), COALESCE(SUM(event_id), 0) FROM {_RG10_DB}.{_RG10_TABLE} "
            "WHERE event_type = 'charge' AND event_ts >= '2026-01-01 00:00:00' "
            "AND event_ts < '2026-01-03 00:00:00'",
            0.22,
            "SEARCH_READ",
            "search-api",
        ),
        _profile(
            "wrk_11",
            _RG10_CHANNEL_QUERY,
            0.22,
            "SEARCH_READ",
            "search-api",
        ),
        _profile(
            "wrk_12",
            _RG10_AMOUNT_QUERY,
            0.18,
            "SEARCH_READ",
            "search-api",
        ),
        _profile("wrk_29", _RG10_LIMIT_VARIANT_QUERY, 0.16, "SEARCH_READ", "search-api"),
        _profile("wrk_30", _RG10_PREDICATE_SWAP_QUERY, 0.16, "SEARCH_READ", "search-api"),
        _profile("wrk_31", _RG10_EXTRA_PREDICATE_QUERY, 0.16, "SEARCH_READ", "search-api"),
        _profile("wrk_32", _RG10_TENANT8_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile("wrk_33", _RG10_REFUND_WINDOW_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile("wrk_34", _RG10_TENANT_TIME_REORDER_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile("wrk_35", _RG10_EVENT_RANGE_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile("wrk_36", _RG10_TENANT_DAY_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile("wrk_37", _RG10_TYPE_TENANT_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile("wrk_38", _RG10_WINDOW_ORDER_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile("wrk_39", _RG10_REFUND_TENANT_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile("wrk_40", _RG10_CHARGE_TENANT_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile("wrk_41", _RG10_TENANT_PAIR_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile("wrk_42", _RG10_WEB_CHANNEL_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile("wrk_43", _RG10_AMOUNT_CAP_QUERY, 0.08, "SEARCH_READ", "search-api"),
        _profile(
            "wrk_13",
            f"SELECT event_type, COUNT(*) FROM {_RG10_DB}.{_RG10_TABLE} "
            "WHERE tenant_id = 7 GROUP BY event_type",
            0.20,
            "BUSINESS_READ",
            "search-analytics",
        ),
        _profile(
            "wrk_14",
            _RG10_ORDER_QUERY,
            0.30,
            "BUSINESS_READ",
            "checkout-api",
        ),
        _profile(
            "wrk_15",
            f"SELECT status, COUNT(*) FROM {_RG10_DB}.{_RG10_ORDER_TABLE} GROUP BY status",
            0.25,
            "BUSINESS_READ",
            "checkout-api",
        ),
        _profile(
            "wrk_16",
            _RG10_CUSTOMER_QUERY,
            0.25,
            "BUSINESS_READ",
            "customer-api",
        ),
        _profile("wrk_17", f"SHOW CREATE TABLE {_RG10_DB}.{_RG10_TABLE}", 0.12, "METADATA", "schema-observer"),
        _profile("wrk_18", f"SHOW INDEX FROM {_RG10_DB}.{_RG10_TABLE}", 0.12, "METADATA", "schema-observer"),
        _profile(
            "wrk_19",
            "SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME, CARDINALITY "
            f"FROM information_schema.statistics WHERE TABLE_SCHEMA = '{_RG10_DB}' "
            f"AND TABLE_NAME = '{_RG10_TABLE}'",
            0.12,
            "METADATA",
            "schema-observer",
        ),
        _profile(
            "wrk_20",
            "SHOW VARIABLES LIKE 'tidb_use_plan_baselines'",
            0.12,
            "METADATA",
            "session-inspector",
        ),
        _profile(
            "wrk_21",
            "SHOW GLOBAL BINDINGS",
            0.12,
            "METADATA",
            "plan-governance",
        ),
        _profile(
            "wrk_22",
            "SELECT DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY "
            "FROM information_schema.cluster_statements_summary "
            "ORDER BY SUM_LATENCY DESC LIMIT 20",
            0.16,
            "METADATA",
            "top-sql-exporter",
        ),
        _profile("wrk_23", f"SELECT COUNT(*) FROM {_RG10_DB}.rg10_search_cache_missing", 0.12, "AUXILIARY", "search-cache-refresher"),
        _profile("wrk_24", f"SELECT COUNT(*) FROM {_RG10_DB}.rg10_event_rollup_missing", 0.12, "AUXILIARY", "event-rollup-worker"),
        _profile("wrk_25", f"SELECT COUNT(*) FROM {_RG10_DB}.rg10_binding_audit_missing", 0.10, "AUXILIARY", "plan-audit-worker"),
        _profile(
            "wrk_26",
            f"SELECT COUNT(*), COALESCE(SUM(event_id), 0) FROM {_RG10_DB}.{_RG10_TABLE} "
            "WHERE event_id BETWEEN 20000 AND 80000",
            0.16,
            "BUSINESS_READ",
            "event-replay-worker",
        ),
        _profile(
            "wrk_27",
            f"SELECT COUNT(*), COALESCE(SUM(event_id), 0) FROM {_RG10_DB}.{_RG10_TABLE} "
            "WHERE amount BETWEEN 100.00 AND 200.00",
            0.16,
            "BUSINESS_READ",
            "risk-scoring-worker",
        ),
        _profile("wrk_28", "SELECT 1", 0.30, "AUXILIARY", "cluster-health-check"),
    ),
    worker_count=6,
    seed=20260802,
    start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
    warmup_seconds=15,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceSqlBindingForDeterministicOrBindingApprovalScenarioCase(
    TiDBScenarioCase
):
    db: str
    table: str
    row_count: int
    expected_result_count: int
    expected_index: str
    decoy_index: str
    business_query: str
    binding_template_query: str
    result_summary_sql: str
    noise_tables: tuple[str, ...]
    global_noise_bindings: tuple[tuple[str, str, str], ...]


_RG10_CASE = TidbResourceGovernanceSqlBindingForDeterministicOrBindingApprovalScenarioCase(
    case_id="deterministic_or_binding_approval",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "Created a session-local binding for the exact observed search query and selected the existing tenant/time access path."
            ],
            "verification": [
                "The session binding is enabled, EXPLAIN contains the tenant/time index, @@last_plan_from_binding is 1, the result truth is unchanged, and the protected table is unchanged."
            ]
        },
        "summary": "The noisy workload contained a global decoy policy; the current session now has a validated local binding without changing global state, schema, or business data."
    },
    case_no=0,
    evaluator=TidbResourceGovernanceSqlBindingEvaluatorCase,
    title="Approve one currently served customer read path with a session-local plan policy.",
    alert=(
        "[RESOURCE GOVERNANCE] 一个 customer-facing read path 需要批准稳定的 session-local 执行计划。"
        "当前 workload 同时包含相邻业务读取、历史 plan policy、schema/统计探针和可失败的辅助探针；"
        "请从未过滤的 workload/TopSQL 与当前 plan policy 证据中识别准确的业务请求，"
        "在当前 session 选择已有的匹配访问路径，保护全局 policy、全局 TiDB 变量、schema 和业务数据。"
        "当前业务真值摘要必须保持为 782 行、event id sum=39092962、CRC=1892534002；"
        "提交时保留启用的 session binding，并验证最终计划由该 binding 控制、业务结果与表真值未变；"
        "harness 会在 teardown 清理 session binding。"
    ),
    initial_state={
        "status": "plan_approval_pending",
        "session_binding": "absent",
        "global_binding": "present_decoy",
        "approved_access_path": "existing_matching_path",
    },
    expected_target={
        "status": "plan_approved",
        "session_binding": "enabled",
        "plan_contains": _RG10_EXPECTED_INDEX,
        "last_plan_from_binding": 1,
        "result_count": 782,
        "cleanup": "no target binding after teardown",
    },
    background_workload=_RG10_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=180,
        image_group_key=None,
        bootstrap_cache_enabled=False,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.925532,
        reference_run_ids=(
            "reference-131__tidb_resource_governance_sql_binding__deterministic_or_binding_approval__mock__r001",
        ),
    ),
    db=_RG10_DB,
    table=_RG10_TABLE,
    row_count=100000,
    expected_result_count=782,
    expected_index=_RG10_EXPECTED_INDEX,
    decoy_index=_RG10_DECOY_INDEX,
    business_query=_RG10_QUERY,
    binding_template_query=_RG10_BINDING_TEMPLATE_QUERY,
    result_summary_sql=_RG10_RESULT_SUMMARY,
    noise_tables=(_RG10_ORDER_TABLE, _RG10_CUSTOMER_TABLE),
    global_noise_bindings=_RG10_GLOBAL_NOISE_BINDINGS,
)

_RG10_CHANNEL_CASE = replace(
    _RG10_CASE,
    case_id="channel_window_binding_approval",
    case_no=1,
    evaluator=TidbResourceGovernanceSqlBindingChannelWindowEvaluatorCase,
    title="Approve the batch-channel search window with a session-local plan policy.",
    reference_report={
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": [
                "Created a session-local binding for the exact batch-channel search window and selected the existing channel/time access path.",
            ],
            "verification": [
                "The session binding is enabled, EXPLAIN contains the channel/time index, @@last_plan_from_binding is 1, the result truth is unchanged, and the protected table is unchanged.",
            ],
        },
        "summary": "The noisy workload contained neighboring channel and tenant policies; the current session now has a validated local binding without changing global state, schema, or business data.",
    },
    alert=(
        "[RESOURCE GOVERNANCE] A customer-facing channel search window needs a session-local plan approval. "
        "The workload contains neighboring tenant/time and channel searches, historical plan policies, "
        "schema probes, and auxiliary checks. Identify the exact batch-channel request from live evidence, "
        "choose an existing matching access path in the current session, and preserve global policy, global "
        "TiDB variables, schema, and business data. The published result summary must remain unchanged; "
        "the harness removes the target session binding during teardown."
    ),
    initial_state={
        "status": "plan_approval_pending",
        "session_binding": "absent",
        "global_binding": "present_decoy",
        "approved_access_path": "existing_channel_time_path",
    },
    expected_target={
        "status": "plan_approved",
        "session_binding": "enabled",
        "plan_contains": "idx_channel_time",
        "last_plan_from_binding": 1,
        "result_count": 260,
        "cleanup": "no target binding after teardown",
    },
    expected_result_count=260,
    expected_index="idx_channel_time",
    business_query=_RG10_CHANNEL_TARGET_QUERY,
    binding_template_query=_RG10_CHANNEL_TARGET_QUERY,
    result_summary_sql=_RG10_CHANNEL_TARGET_SUMMARY,
    global_noise_bindings=_RG10_CHANNEL_GLOBAL_NOISE_BINDINGS,
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.255319,
        reference_run_ids=(
            "tidb-reference-14__tidb_resource_governance_sql_binding__"
            "channel_window_binding_approval__mock__r001",
        ),
    ),
)


class TidbResourceGovernanceSqlBindingInjector(BaseFaultInjector):
    """Create the RG10 binding-approval fixture and its noisy business workload."""

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._disable_statement_summary(context.env)
        self._create_target_table(context.env)
        self._load_target_rows(context.env)
        self._create_noise_tables(context.env)
        self._load_noise_rows(context.env)
        self._create_global_decoy_binding(context.env)
        self._verify_initial_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._disable_statement_summary(context.env)
        self._verify_initial_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_initial_state(context.env)
        summary = self._execute(
            context.env,
            self.result_summary_sql,
            "capture RG10 business result truth",
        )
        evidence = {
            "business_result_truth": capture_query_result_truth(summary, ordered=True),
            "business_result_count": int(summary["result"][0][0]),
            "table_integrity": self._table_integrity(context.env),
            "index_catalog": self._execute(
                context.env,
                f"SHOW INDEX FROM {self.db}.{self.table}",
                "capture RG10 index catalog",
            ),
            "global_binding_catalog": self._execute(
                context.env,
                "SHOW GLOBAL BINDINGS",
                "capture RG10 global binding catalog",
            ),
            "session_binding_catalog": self._execute(
                context.env,
                "SHOW SESSION BINDINGS",
                "capture RG10 session binding catalog",
            ),
            "fault_plan": self._execute(
                context.env,
                f"EXPLAIN {self.business_query}",
                "capture RG10 decoy plan",
            ),
        }
        self._enable_statement_summary(context.env)
        return evidence

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        session_bindings = self._execute(
            context.env,
            "SHOW SESSION BINDINGS",
            "inspect RG10 session bindings for cleanup",
        )
        for row in self._binding_rows(session_bindings):
            if self.table.casefold() not in " ".join(str(value) for value in row).casefold():
                continue
            digest = str(row[9])
            self._execute(
                context.env,
                f"DROP SESSION BINDING FOR SQL DIGEST '{digest}'",
                f"remove RG10 session binding digest={digest!r}",
            )
        session_bindings = self._execute(
            context.env,
            "SHOW SESSION BINDINGS",
            "verify RG10 session binding cleanup",
        )
        self._assert_no_table_binding(session_bindings, self.table, "session")
        bindings_to_remove = (
            (self.binding_template_query, self.table, self.decoy_index),
            *self.global_noise_bindings,
        )
        for query, table, index in bindings_to_remove:
            self._execute(
                context.env,
                f"DROP GLOBAL BINDING FOR {query}",
                f"remove RG10 global binding for {table}.{index}",
            )
        global_bindings = self._execute(
            context.env,
            "SHOW GLOBAL BINDINGS",
            "verify RG10 global binding cleanup",
        )
        for table in dict.fromkeys(item[1] for item in bindings_to_remove):
            self._assert_no_table_binding(global_bindings, table, "global")
        for table in (*self.noise_tables, self.table):
            self._execute(
                context.env,
                f"DROP TABLE {self.db}.{table}",
                f"drop RG10 fixture table {self.db}.{table}",
            )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.row_count = int(config["row_count"])
        self.expected_result_count = int(config["expected_result_count"])
        self.expected_index = validate_sql_identifier(
            str(config["expected_index"]), "expected index"
        )
        self.decoy_index = validate_sql_identifier(
            str(config["decoy_index"]), "decoy index"
        )
        self.business_query = str(config["business_query"])
        self.binding_template_query = str(config["binding_template_query"])
        self.result_summary_sql = str(config["result_summary_sql"])
        self.noise_tables = tuple(
            validate_sql_identifier(str(table), "noise table")
            for table in config["noise_tables"]
        )
        if len(self.noise_tables) != 2:
            raise ValueError(f"RG10 requires exactly two noise tables, got {self.noise_tables!r}")
        self.global_noise_bindings = tuple(
            (
                str(query),
                validate_sql_identifier(str(table), "global binding table"),
                validate_sql_identifier(str(index), "global binding index"),
            )
            for query, table, index in config["global_noise_bindings"]
        )

    @staticmethod
    def _execute(env, sql: str, context: str) -> dict:
        return execute_json_payload(env.execute_sql, sql, context)

    def _disable_statement_summary(self, env) -> None:
        self._execute(
            env,
            "SET GLOBAL tidb_enable_stmt_summary = 0",
            "disable RG10 statement summary during scenario setup",
        )

    def _enable_statement_summary(self, env) -> None:
        self._execute(
            env,
            "SET GLOBAL tidb_enable_stmt_summary = 1",
            "enable RG10 statement summary before agent handoff",
        )

    def _create_target_table(self, env) -> None:
        index_columns = {
            "idx_tenant_time": "tenant_id, event_ts",
            "idx_channel_time": "channel, event_ts",
        }
        indexes = []
        for index_name in ("idx_tenant_time", "idx_channel_time", self.decoy_index):
            if index_name in {name for name, _ in indexes}:
                continue
            columns = index_columns.get(index_name, "event_type")
            indexes.append((index_name, columns))
        index_definitions = ", ".join(
            f"KEY {index_name} ({columns})" for index_name, columns in indexes
        )
        self._execute(
            env,
            (
                f"CREATE TABLE {self.db}.{self.table} ("
                "event_id BIGINT NOT NULL, tenant_id INT NOT NULL, "
                "event_ts DATETIME NOT NULL, event_type VARCHAR(16) NOT NULL, "
                "channel VARCHAR(16) NOT NULL, amount DECIMAL(12,2) NOT NULL, "
                "payload VARCHAR(128) NOT NULL, PRIMARY KEY (event_id), "
                f"{index_definitions}, "
                "KEY idx_amount_event (amount, event_id)) "
                "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin"
            ),
            f"create RG10 target table {self.db}.{self.table}",
        )

    def _load_target_rows(self, env) -> None:
        batch_size = 1000
        for start in range(0, self.row_count, batch_size):
            size = min(batch_size, self.row_count - start)
            expression = start + 1
            self._execute(
                env,
                (
                    f"INSERT INTO {self.db}.{self.table} "
                    "(event_id, tenant_id, event_ts, event_type, channel, amount, payload) "
                    f"SELECT {start} + n, MOD({start} + n, 128), "
                    f"TIMESTAMPADD(SECOND, {start} + n, TIMESTAMP'2026-01-01 00:00:00'), "
                    f"CASE WHEN MOD({start} + n, 128) = 7 THEN "
                    f"CASE WHEN {start} + n < 86401 THEN 'refund' ELSE 'charge' END "
                    f"ELSE ELT(MOD({start} + n, 4) + 1, 'create', 'update', 'charge', 'close') END, "
                    f"ELT(MOD({start} + n, 3) + 1, 'mobile', 'web', 'batch'), "
                    f"CAST(MOD(({start} + n) * 7919, 100000) / 100 AS DECIMAL(12,2)), "
                    f"RPAD(CONCAT('event-', {start} + n), 64, 'x') "
                    "FROM (SELECT ROW_NUMBER() OVER "
                    "(ORDER BY table_schema, table_name, column_name) AS n "
                    f"FROM information_schema.columns LIMIT {size}) AS source"
                ),
                f"load RG10 target rows starting at {expression}",
            )

    def _create_noise_tables(self, env) -> None:
        order_table, customer_table = self.noise_tables
        self._execute(
            env,
            (
                f"CREATE TABLE {self.db}.{order_table} ("
                "order_id BIGINT NOT NULL, tenant_id INT NOT NULL, "
                "status VARCHAR(16) NOT NULL, created_at DATETIME NOT NULL, "
                "PRIMARY KEY (order_id), KEY idx_order_tenant (tenant_id)) "
                "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            ),
            f"create RG10 order noise table {self.db}.{order_table}",
        )
        self._execute(
            env,
            (
                f"CREATE TABLE {self.db}.{customer_table} ("
                "customer_id BIGINT NOT NULL, tenant_id INT NOT NULL, "
                "segment VARCHAR(16) NOT NULL, PRIMARY KEY (customer_id), "
                "KEY idx_customer_tenant (tenant_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            ),
            f"create RG10 customer noise table {self.db}.{customer_table}",
        )

    def _load_noise_rows(self, env) -> None:
        order_table, customer_table = self.noise_tables
        self._execute(
            env,
            (
                f"INSERT INTO {self.db}.{order_table} "
                "(order_id, tenant_id, status, created_at) "
                "SELECT n, MOD(n, 128), "
                "ELT(MOD(n, 4) + 1, 'paid', 'packed', 'shipped', 'returned'), "
                "TIMESTAMPADD(MINUTE, n, TIMESTAMP'2026-01-01 00:00:00') "
                "FROM (SELECT ROW_NUMBER() OVER "
                "(ORDER BY table_schema, table_name, column_name) AS n "
                "FROM information_schema.columns LIMIT 5000) AS source"
            ),
            f"load RG10 order noise table {self.db}.{order_table}",
        )
        self._execute(
            env,
            (
                f"INSERT INTO {self.db}.{customer_table} "
                "(customer_id, tenant_id, segment) SELECT n, MOD(n, 128), "
                "ELT(MOD(n, 3) + 1, 'new', 'growth', 'enterprise') "
                "FROM (SELECT ROW_NUMBER() OVER "
                "(ORDER BY table_schema, table_name, column_name) AS n "
                "FROM information_schema.columns LIMIT 3000) AS source"
            ),
            f"load RG10 customer noise table {self.db}.{customer_table}",
        )

    def _create_global_decoy_binding(self, env) -> None:
        for query, table, index in (
            (self.binding_template_query, self.table, self.decoy_index),
            *self.global_noise_bindings,
        ):
            self._execute(
                env,
                f"CREATE GLOBAL BINDING FOR {query} USING {self._bound_query(query, table, index)}",
                f"create RG10 global binding for {table}.{index}",
            )

    @staticmethod
    def _bound_query(query: str, table: str, index: str) -> str:
        prefix, remainder = query.split(" ", 1)
        return f"{prefix} /*+ USE_INDEX({table}, {index}) */ {remainder}"

    def _verify_initial_state(self, env) -> None:
        integrity = self._table_integrity(env)
        observed_count = int(integrity[0])
        if observed_count != self.row_count:
            raise RuntimeError(
                f"RG10 target row count mismatch before agent handoff: table={self.table!r}, "
                f"expected={self.row_count}, observed={integrity!r}"
            )
        summary = self._execute(
            env,
            self.result_summary_sql,
            "verify RG10 business result summary",
        )
        result_count = int(summary["result"][0][0])
        if result_count != self.expected_result_count:
            raise RuntimeError(
                f"RG10 target result count mismatch before agent handoff: "
                f"expected={self.expected_result_count}, observed={result_count}, "
                f"sql={self.business_query!r}"
            )
        self._assert_no_table_binding(
            self._execute(env, "SHOW SESSION BINDINGS", "verify RG10 session binding absence"),
            self.table,
            "session",
        )
        global_rows = self._binding_rows(
            self._execute(env, "SHOW GLOBAL BINDINGS", "verify RG10 global decoy binding")
        )
        self._require_one_binding(
            global_rows,
            self.binding_template_query,
            self.table,
            self.decoy_index,
            "global template decoy",
        )
        for query, table, index in self.global_noise_bindings:
            self._require_one_binding(global_rows, query, table, index, "global noise")
        plan = self._execute(
            env,
            f"EXPLAIN {self.business_query}",
            "verify RG10 decoy plan",
        )["result"]
        rendered = "\n".join(" | ".join(str(value) for value in row) for row in plan).casefold()
        if self.decoy_index.casefold() not in rendered:
            raise RuntimeError(
                f"RG10 global decoy binding did not control the initial plan: "
                f"index={self.decoy_index!r}, plan={plan!r}"
            )

    def _require_one_binding(
        self,
        rows: tuple[tuple[object, ...], ...],
        query: str,
        table: str,
        index: str,
        label: str,
    ) -> None:
        matching = [row for row in rows if self._binding_matches(row, query, table, index)]
        if len(matching) != 1:
            raise RuntimeError(
                f"RG10 expected exactly one {label} binding: query={query!r}, "
                f"table={table!r}, index={index!r}, "
                f"matches={matching!r}, rows={rows!r}"
            )

    def _assert_no_table_binding(
        self,
        payload: Mapping[str, object],
        table: str,
        scope: str,
    ) -> None:
        rows = self._binding_rows(payload)
        matches = [
            row
            for row in rows
            if table.casefold() in " ".join(str(value) for value in row).casefold()
        ]
        if matches:
            raise RuntimeError(
                f"RG10 {scope} binding cleanup left rows for table={table!r}: "
                f"rows={matches!r}"
            )

    @staticmethod
    def _binding_matches(row: tuple[object, ...], query: str, table: str, index: str) -> bool:
        rendered = " ".join(str(value) for value in row).casefold()
        return (
            table.casefold() in rendered
            and index.casefold() in rendered
            and TidbResourceGovernanceSqlBindingInjector._normalize_binding_sql(str(row[0]))
            == TidbResourceGovernanceSqlBindingInjector._normalize_binding_sql(query)
        )

    @staticmethod
    def _normalize_binding_sql(sql: str) -> str:
        normalized = sql.casefold().replace("`", "")
        normalized = re.sub(r"'(?:''|[^'])*'", "?", normalized)
        normalized = re.sub(r"\b\d+(?:\.\d+)?\b", "?", normalized)
        normalized = re.sub(r"\bin\s*\([^)]*\)", "in(?)", normalized)
        normalized = normalized.replace("...", "?")
        normalized = re.sub(r"\s*(>=|<=|<>|!=|=|<|>|\(|\)|,|\.)\s*", r"\1", normalized)
        return re.sub(r"\s+", " ", normalized).strip()

    @staticmethod
    def _binding_rows(payload: Mapping[str, object]) -> tuple[tuple[object, ...], ...]:
        columns = payload["columns"]
        rows = payload["result"]
        if len(columns) != 11:
            raise RuntimeError(
                f"RG10 expected 11 SHOW BINDINGS columns, observed={columns!r}"
            )
        return tuple(tuple(row) for row in rows)

    def _table_integrity(self, env) -> tuple[object, ...]:
        sql = (
            "SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_ts, "
            f"event_type, amount, payload))), 0) FROM {self.db}.{self.table}"
        )
        return tuple(
            self._execute(env, sql, f"RG10 table integrity query: sql={sql!r}")["result"][0]
        )


class TidbResourceGovernanceSqlBindingScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_sql_binding"
    description = "Approve one currently served customer read path with a session-local TiDB SQL binding in a noisy workload."
    cases = (_RG10_CASE, _RG10_CHANNEL_CASE)

    def build_fault_plan(
        self,
        case: TidbResourceGovernanceSqlBindingForDeterministicOrBindingApprovalScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernanceSqlBindingInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "row_count": case.row_count,
                    "expected_result_count": case.expected_result_count,
                    "expected_index": case.expected_index,
                    "decoy_index": case.decoy_index,
                    "business_query": case.business_query,
                    "binding_template_query": case.binding_template_query,
                    "result_summary_sql": case.result_summary_sql,
                    "noise_tables": case.noise_tables,
                    "global_noise_bindings": case.global_noise_bindings,
                },
            ),
        )
