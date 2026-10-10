import re
import threading
import time
from contextlib import nullcontext
from dataclasses import dataclass, replace

import pymysql

from src.scenarios.evaluation.tidb.system_failure.table_cache_lease import (
    TidbSystemFailureTableCacheLeaseEvaluatorCase,
    TidbSystemFailureTableCacheLeaseFocusedEvaluatorCase,
)
from src.scenarios.evaluation.protocol import structured_reference_report
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..common import join_thread
from ..runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureTableCacheLeaseForSharedCatalogScenarioCase(TiDBScenarioCase):
    db: str
    cache_table: str
    cache_table_names: tuple[str, ...]
    pricing_table: str
    healthy_cache_table_names: tuple[str, ...]
    orders_table: str
    inventory_table: str
    catalog_row_count: int
    business_summary_sql: str
    table_integrity_sql: str
    target_profile_names: tuple[str, ...]
    recovery_lease_seconds: int
    recovery_lease_max_seconds: int


_DB = "benchops"
_CACHE_TABLE = "ma02_product_catalog"
_PRICING_TABLE = "ma02_pricing_rules"
_REFERENCE_CACHE_TABLE = "ma02_catalog_aux"
_ORDERS_TABLE = "ma02_orders"
_INVENTORY_TABLE = "ma02_inventory"
_BUSINESS_CONFLICT_BURST_ROUNDS = 32
_BUSINESS_PROBE_ORDER_IDS = (18, 19)
_BUSINESS_NOISE_ORDER_IDS = (20, 21, 22, 23)
_BUSINESS_NOISE_DURATION_SECONDS = 75
_BUSINESS_NOISE_INTERVAL_SECONDS = 0.75
_BUSINESS_INITIAL_PHASE_ROUNDS = 4
_CAUSAL_RUNTIME_MIN_ADDITIONAL_CALLS_PER_PROFILE = 1
_CAUSAL_RUNTIME_ROUNDS = 48
_CAUSAL_RUNTIME_DEADLINE_SECONDS = 900
_TABLE_CACHE_LEASE_SECONDS = 3
_TABLE_CACHE_LEASE_LEASE_EXPIRY_MARGIN_SECONDS = 0.5
_TABLE_CACHE_LEASE_CONFLICT_EVIDENCE_TOP_UP_DEADLINE_SECONDS = 90
_BUSINESS_SUMMARY_SQL = (
    "SELECT COUNT(*), COALESCE(SUM(sku_id), 0), "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', sku_id, tenant_id, category, price, stock))), 0) "
    f"FROM {_DB}.{_CACHE_TABLE}"
)
_TABLE_INTEGRITY_SQL = _BUSINESS_SUMMARY_SQL

_CATALOG_PROFILES = (
    WorkloadProfile(
        name="catalog_tenant_rollup",
        sql=(
            f"SELECT tenant_id, category, COUNT(*), AVG(price) FROM {_DB}.{_CACHE_TABLE} "
            "WHERE tenant_id IN (3, 7, 11) GROUP BY tenant_id, category ORDER BY tenant_id, category"
        ),
        qps=1.25,
        tier="OLTP_CORE",
        application_name="catalog-api",
    ),
    WorkloadProfile(
        name="catalog_sku_lookup",
        sql=(
            f"SELECT sku_id, category, price, stock FROM {_DB}.{_CACHE_TABLE} "
            "WHERE sku_id BETWEEN 17 AND 48 ORDER BY sku_id"
        ),
        qps=1.10,
        tier="OLTP_CORE",
        application_name="catalog-api",
    ),
    WorkloadProfile(
        name="catalog_category_probe",
        sql=(
            f"SELECT sku_id, price FROM {_DB}.{_CACHE_TABLE} "
            "WHERE category IN ('hardware', 'software') ORDER BY price DESC, sku_id LIMIT 40"
        ),
        qps=1.10,
        tier="OLTP_CORE",
        application_name="pricing-api",
    ),
    WorkloadProfile(
        name="catalog_stock_report",
        sql=(
            f"SELECT SUM(stock), MIN(price), MAX(price) FROM {_DB}.{_CACHE_TABLE} "
            "WHERE stock > 0"
        ),
        qps=1.00,
        tier="OLTP_CORE",
        application_name="inventory-api",
    ),
    WorkloadProfile(
        name="catalog_price_preview",
        sql=(
            f"SELECT category, COUNT(*), MIN(price), MAX(price) FROM {_DB}.{_CACHE_TABLE} "
            "GROUP BY category ORDER BY category"
        ),
        qps=0.95,
        tier="OLTP_CORE",
        application_name="merchandising-preview",
    ),
    WorkloadProfile(
        name="catalog_recent_probe",
        sql=(
            f"SELECT sku_id, updated_at FROM {_DB}.{_CACHE_TABLE} "
            "WHERE updated_at >= '2026-01-01 00:00:00' ORDER BY updated_at DESC, sku_id LIMIT 64"
        ),
        qps=0.90,
        tier="OLTP_CORE",
        application_name="catalog-cache-warmup",
    ),
)

_PRICING_PROFILES = (
    WorkloadProfile(
        name="pricing_rule_tenant_lookup",
        sql=(
            f"SELECT rule_id, tenant_id, category, discount_pct FROM {_DB}.{_PRICING_TABLE} "
            "WHERE tenant_id IN (3, 7, 11) AND active = 1 ORDER BY tenant_id, priority, rule_id"
        ),
        qps=0.85,
        tier="OLTP_CORE",
        application_name="pricing-api",
    ),
    WorkloadProfile(
        name="pricing_rule_rollup",
        sql=(
            f"SELECT category, COUNT(*), AVG(discount_pct) FROM {_DB}.{_PRICING_TABLE} "
            "WHERE active = 1 GROUP BY category ORDER BY category"
        ),
        qps=0.65,
        tier="OLAP_BURST",
        application_name="pricing-analytics",
    ),
)

_BUSINESS_PROFILES = (
    WorkloadProfile(
        name="orders_dashboard_rollup",
        sql=(
            f"SELECT tenant_id, status, COUNT(*), COALESCE(SUM(amount), 0) FROM {_DB}.{_ORDERS_TABLE} "
            "WHERE created_at >= '2026-01-01 00:00:00' GROUP BY tenant_id, status "
            "ORDER BY tenant_id, status"
        ),
        qps=0.40,
        tier="OLAP_BURST",
        application_name="orders-dashboard",
    ),
    WorkloadProfile(
        name="orders_recent_lookup",
        sql=(
            f"SELECT order_id, sku_id, amount, status FROM {_DB}.{_ORDERS_TABLE} "
            "WHERE tenant_id = 7 ORDER BY created_at DESC, order_id DESC LIMIT 30"
        ),
        qps=0.55,
        tier="OLTP_CORE",
        application_name="orders-api",
    ),
    WorkloadProfile(
        name="orders_reconciliation",
        sql=(
            f"SELECT status, COUNT(*), COALESCE(SUM(amount), 0) FROM {_DB}.{_ORDERS_TABLE} "
            "GROUP BY status ORDER BY status"
        ),
        qps=0.30,
        tier="OLAP_BURST",
        application_name="payment-reconciliation",
    ),
    WorkloadProfile(
        name="orders_tenant_export",
        sql=(
            f"SELECT tenant_id, COUNT(*), COALESCE(AVG(amount), 0) FROM {_DB}.{_ORDERS_TABLE} "
            "WHERE tenant_id BETWEEN 1 AND 32 GROUP BY tenant_id ORDER BY tenant_id"
        ),
        qps=0.28,
        tier="OLAP_BURST",
        application_name="tenant-export",
    ),
    WorkloadProfile(
        name="inventory_health_rollup",
        sql=(
            f"SELECT warehouse_id, COUNT(*), SUM(available) FROM {_DB}.{_INVENTORY_TABLE} "
            "GROUP BY warehouse_id ORDER BY warehouse_id"
        ),
        qps=0.42,
        tier="OLTP_CORE",
        application_name="inventory-monitor",
    ),
    WorkloadProfile(
        name="inventory_low_stock_probe",
        sql=(
            f"SELECT sku_id, warehouse_id, available FROM {_DB}.{_INVENTORY_TABLE} "
            "WHERE available < 20 ORDER BY available, sku_id LIMIT 50"
        ),
        qps=0.38,
        tier="OLTP_CORE",
        application_name="replenishment-worker",
    ),
    WorkloadProfile(
        name="warehouse_availability_read",
        sql=(
            f"SELECT sku_id, warehouse_id, reserved FROM {_DB}.{_INVENTORY_TABLE} "
            "WHERE sku_id BETWEEN 15 AND 80 ORDER BY sku_id, warehouse_id LIMIT 60"
        ),
        qps=0.35,
        tier="OLTP_CORE",
        application_name="warehouse-api",
    ),
    WorkloadProfile(
        name="inventory_capacity_probe",
        sql=(
            f"SELECT warehouse_id, SUM(available + reserved) FROM {_DB}.{_INVENTORY_TABLE} "
            "GROUP BY warehouse_id"
        ),
        qps=0.25,
        tier="OLAP_BURST",
        application_name="capacity-planner",
    ),
)

_INVENTORY_PROFILES = _BUSINESS_PROFILES[4:]
_BUSINESS_PROFILES = _BUSINESS_PROFILES[:4]
_TARGET_PROFILES = tuple(
    replace(profile, target="tidb/tidb-0")
    for index, profile in enumerate((*_CATALOG_PROFILES, *_PRICING_PROFILES, *_INVENTORY_PROFILES))
)

_HEALTHY_CACHE_PROFILES = (
    WorkloadProfile(
        name="lookup_variant_a",
        sql=(
            f"SELECT sku_id, category, price, stock FROM {_DB}.{_REFERENCE_CACHE_TABLE} "
            "WHERE sku_id BETWEEN 10017 AND 10048 ORDER BY sku_id"
        ),
        qps=0.80,
        tier="OLTP_CORE",
        application_name="commerce-reader-a",
        target="tidb/tidb-0",
    ),
    WorkloadProfile(
        name="rollup_variant_b",
        sql=(
            f"SELECT category, COUNT(*), AVG(price) FROM {_DB}.{_REFERENCE_CACHE_TABLE} "
            "GROUP BY category ORDER BY category"
        ),
        qps=0.45,
        tier="OLAP_BURST",
        application_name="commerce-reader-b",
        target="tidb/tidb-0",
    ),
)

_RECOVERY_PROFILE_NAMES = (
    *(profile.name for profile in _TARGET_PROFILES),
)

_OBSERVATION_PROFILES = (
    WorkloadProfile(
        name="schema_table_status",
        sql=f"SHOW TABLE STATUS FROM {_DB} LIKE '{_CACHE_TABLE}'",
        qps=0.32,
        tier="OPS_MAINTENANCE",
        application_name="schema-observer",
    ),
    WorkloadProfile(
        name="schema_inventory_status",
        sql=f"SHOW TABLE STATUS FROM {_DB} LIKE '{_INVENTORY_TABLE}'",
        qps=0.28,
        tier="OPS_MAINTENANCE",
        application_name="schema-observer",
    ),
    WorkloadProfile(
        name="schema_pricing_status",
        sql=f"SHOW TABLE STATUS FROM {_DB} LIKE '{_PRICING_TABLE}'",
        qps=0.24,
        tier="OPS_MAINTENANCE",
        application_name="schema-observer",
    ),
    WorkloadProfile(
        name="schema_columns_probe",
        sql=(
            "SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM information_schema.columns "
            f"WHERE TABLE_SCHEMA = '{_DB}' AND TABLE_NAME IN "
            f"('{_CACHE_TABLE}', '{_ORDERS_TABLE}', '{_INVENTORY_TABLE}', '{_PRICING_TABLE}', '{_REFERENCE_CACHE_TABLE}') "
            "ORDER BY TABLE_NAME, ORDINAL_POSITION"
        ),
        qps=0.25,
        tier="OPS_MAINTENANCE",
        application_name="schema-observer",
    ),
    WorkloadProfile(
        name="cluster_tso_probe",
        sql="SELECT @@tidb_current_ts",
        qps=0.50,
        tier="OPS_MAINTENANCE",
        application_name="transaction-monitor",
    ),
    WorkloadProfile(
        name="cluster_variable_probe",
        sql="SHOW GLOBAL VARIABLES LIKE 'tidb_%lease%'",
        qps=0.18,
        tier="OPS_MAINTENANCE",
        application_name="configuration-observer",
    ),
)

_ROLLBACK_PROFILES = (
    WorkloadProfile(
        name="order_status_touch",
        sql=f"UPDATE {_DB}.{_ORDERS_TABLE} SET status = status WHERE order_id = 17",
        qps=0.42,
        tier="OLTP_BACKGROUND",
        application_name="orders-api-live-touch",
    ),
    WorkloadProfile(
        name="inventory_reservation_touch",
        sql=f"UPDATE {_DB}.{_INVENTORY_TABLE} SET reserved = reserved WHERE sku_id = 17",
        qps=0.38,
        tier="OLTP_BACKGROUND",
        application_name="inventory-api-live-touch",
    ),
    WorkloadProfile(
        name="order_insert_preview",
        sql=(
            f"INSERT INTO {_DB}.{_ORDERS_TABLE} (order_id, tenant_id, sku_id, amount, status, created_at) "
            "VALUES (9999991, 7, 17, 19.99, 'preview', '2026-01-31 12:00:00')"
        ),
        qps=0.18,
        tier="OLTP_BACKGROUND",
        application_name="order-preview",
    ),
    WorkloadProfile(
        name="inventory_reservation_preview",
        sql=(
            f"UPDATE {_DB}.{_INVENTORY_TABLE} SET reserved = reserved + 1 "
            "WHERE sku_id = 23 AND warehouse_id = 2"
        ),
        qps=0.22,
        tier="OLTP_BACKGROUND",
        application_name="reservation-preview",
    ),
)

_LOG_NOISE_PROFILES = (
    WorkloadProfile(
        name="order_status_check",
        sql=(
            f"SELECT status, COUNT(*) FROM {_DB}.{_ORDERS_TABLE} "
            "WHERE status IN ('paid', 'pending', 'shipped', 'cancelled') GROUP BY status"
        ),
        qps=0.08,
        tier="INTEGRATION_BACKGROUND",
        application_name="report-cache-refresher",
    ),
    WorkloadProfile(
        name="pricing_active_check",
        sql=(
            f"SELECT COUNT(*) FROM {_DB}.{_PRICING_TABLE} "
            "WHERE active = 1 AND discount_pct >= 0"
        ),
        qps=0.07,
        tier="INTEGRATION_BACKGROUND",
        application_name="pricing-validation-worker",
    ),
    WorkloadProfile(
        name="export_batch_check",
        sql=(
            f"SELECT COUNT(*) FROM {_DB}.{_ORDERS_TABLE} "
            "WHERE created_at >= '2026-01-01 00:00:00'"
        ),
        qps=0.06,
        tier="INTEGRATION_BACKGROUND",
        application_name="export-worker",
    ),
    WorkloadProfile(
        name="inventory_reporting_check",
        sql=(
            f"SELECT warehouse_id, COUNT(*) FROM {_DB}.{_INVENTORY_TABLE} "
            "GROUP BY warehouse_id"
        ),
        qps=0.05,
        tier="INTEGRATION_BACKGROUND",
        application_name="inventory-reporting",
    ),
)

_TABLE_CACHE_LEASE_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        *_TARGET_PROFILES,
        *_HEALTHY_CACHE_PROFILES,
        *_BUSINESS_PROFILES,
        *_OBSERVATION_PROFILES,
        *_ROLLBACK_PROFILES,
        *_LOG_NOISE_PROFILES,
    ),
    worker_count=12,
    seed=20260803,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=28,
)


_TABLE_CACHE_LEASE_CASE = TidbSystemFailureTableCacheLeaseForSharedCatalogScenarioCase(
    case_id="table_cache_lease_write_conflict",
    reference_report=structured_reference_report(
        case_id="table_cache_lease_write_conflict",
        factors=(
            "2PC and prewrite failures are caused by table cache lease contention on cached business tables",
            "the same-domain cached auxiliary table and TiKV capacity are not the primary causes",
        ),
        changes=("removed table-cache contention from every causal cached business table while preserving the healthy cache",),
        verification=(
            "QPS, error rate, schema validity, and TSO advancement recovered",
            "business truth stayed unchanged and the cached auxiliary table remained cached",
        ),
        summary="The reference path removed causal table-cache lease contention and verified service recovery.",
    ),
    case_no=0,
    evaluator=TidbSystemFailureTableCacheLeaseEvaluatorCase,
    title="Diagnose a misleading 2PC alert amid mixed commerce reads, writes, and component activity.",
    alert=(
        "[CRITICAL] [Commerce transaction path] 最近观测窗口内，多个业务入口均出现间歇性事务提交失败；"
        "多个业务读取路径的成功率与集群 QPS 同时波动，TiDB 侧出现 2PC/Prewrite 错误，"
        "TiKV 写流量也有所上升。请定位造成当前业务退化的主要原因，在不改变业务数据语义且不扩大影响范围的前提下恢复服务，"
        "并验证错误率、吞吐、Schema 与 TSO。"
    ),
    initial_state={
        "status": "degraded",
        "symptoms": ("2PC/Prewrite failures", "QPS cliff", "intermittent business errors"),
        "tidb_instances": 2,
    },
    expected_target={
        "status": "recovered",
        "cache_contention": "removed from every causal cached business table",
        "healthy_cache": "same-domain cached auxiliary table preserved",
        "business_truth": "unchanged",
        "schema": "valid",
        "tso": "advancing",
    },
    background_workload=_TABLE_CACHE_LEASE_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=2,
        sql_timeout_seconds=120,
        image_group_key="table-cache-lease-v5",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.856319,
        reference_run_ids=(
            "reference-170__tidb_table_cache_lease__"
            "table_cache_lease_write_conflict__mock__r001",
        ),
    ),
    db=_DB,
    cache_table=_CACHE_TABLE,
    pricing_table=_PRICING_TABLE,
    healthy_cache_table_names=(_REFERENCE_CACHE_TABLE,),
    orders_table=_ORDERS_TABLE,
    inventory_table=_INVENTORY_TABLE,
    catalog_row_count=256,
    business_summary_sql=_BUSINESS_SUMMARY_SQL,
    table_integrity_sql=_TABLE_INTEGRITY_SQL,
    target_profile_names=_RECOVERY_PROFILE_NAMES,
    cache_table_names=(_CACHE_TABLE, _INVENTORY_TABLE, _PRICING_TABLE),
    recovery_lease_seconds=6,
    recovery_lease_max_seconds=30,
)

_TABLE_CACHE_LEASE_FOCUSED_CASE = replace(
    _TABLE_CACHE_LEASE_CASE,
    case_id="table_cache_lease_single_table_focus",
    case_no=1,
    evaluator=TidbSystemFailureTableCacheLeaseFocusedEvaluatorCase,
    reference_report=structured_reference_report(
        case_id="table_cache_lease_single_table_focus",
        factors=(
            "the 2PC and Prewrite failures are lease-renewal write conflicts on mysql.table_cache_meta for one cached business table: TiDB internal cached-table reads renew the lease through lock cached table for read and collide while updating the metadata row, and two TiDB instances concurrently read that causal cached business table and contend on its shared lease",
            "the ordinary business tables and TiKV stores are not the root cause of the observed 9007 failures, and the healthy cached reference table is not implicated by the conflict keys or target workload and must remain cached",
        ),
        changes=("removed table-cache contention from the causal cached business table while preserving the healthy cache",),
        verification=(
            "QPS, error rate, schema validity, and TSO advancement recovered",
            "business truth stayed unchanged and the cached auxiliary table remained cached",
        ),
        summary="The focused reference path isolates one causal cached table while preserving the same lease-contention mechanism and safety boundary.",
    ),
    title="Diagnose a focused misleading 2PC alert from one cached commerce table.",
    alert=(
        "[CRITICAL] 订单入口间歇性出现 2PC/Prewrite 失败，集群 QPS 与成功率波动，"
        "TiKV 写流量也有所上升。请在不改变业务数据语义、不修改健康缓存表的前提下定位并恢复服务，"
        "验证错误率、吞吐、Schema 与 TSO。"
    ),
    initial_state={
        "status": "degraded",
        "symptoms": ("2PC/Prewrite failures", "QPS cliff", "intermittent business errors"),
        "tidb_instances": 2,
        "causal_cached_tables": 1,
    },
    expected_target={
        "status": "recovered",
        "cache_contention": "removed from the causal cached business table",
        "healthy_cache": "same-domain cached auxiliary table preserved",
        "business_truth": "unchanged",
        "schema": "valid",
        "tso": "advancing",
    },
    cache_table_names=(_CACHE_TABLE,),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.942414,
        reference_run_ids=(
            "tidb-reference-8__tidb_system_failure_table_cache_lease__"
            "table_cache_lease_single_table_focus__mock__r001",
        ),
    ),
)


class TidbSystemFailureTableCacheLeaseScenario(TiDBScenario):
    scenario_id = "tidb_system_failure_table_cache_lease"
    description = "Diagnose intermittent TiDB commerce transaction failures across two SQL entrances under mixed read and write load."
    cases = (_TABLE_CACHE_LEASE_CASE, _TABLE_CACHE_LEASE_FOCUSED_CASE)

    def build_fault_plan(
        self,
        case: TidbSystemFailureTableCacheLeaseForSharedCatalogScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureTableCacheLeaseInjector,
                config={
                    "db": case.db,
                    "cache_table": case.cache_table,
                    "cache_table_names": case.cache_table_names,
                    "pricing_table": case.pricing_table,
                    "healthy_cache_table_names": case.healthy_cache_table_names,
                    "orders_table": case.orders_table,
                    "inventory_table": case.inventory_table,
                    "catalog_row_count": case.catalog_row_count,
                    "business_summary_sql": case.business_summary_sql,
                    "table_integrity_sql": case.table_integrity_sql,
                    "target_profile_names": case.target_profile_names,
                },
            ),
        )

from collections.abc import Mapping

from src.database.query_results import capture_query_result_truth
from src.database.tidb import execute_integrity_tuple, table_cache_lease_integrity_sql
from src.database.sql import (
    execute_json_payload,
    execute_result_rows,
    parse_json_object,
    require_one_result_row,
    require_success_payload,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext

from src.scenarios.tidb.common import validate_sql_identifier


class TidbSystemFailureTableCacheLeaseInjector(BaseFaultInjector):
    """Create a real multi-TiDB cached-table lease contention window."""

    def __init__(self) -> None:
        self._business_noise_stop = threading.Event()
        self._business_noise_thread: threading.Thread | None = None
        self._business_noise_failure: BaseException | None = None
        self._causal_runtime_stop = threading.Event()
        self._causal_runtime_thread: threading.Thread | None = None
        self._causal_runtime_failure: BaseException | None = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        # Schema/data seeding and cache enabling are injector provenance, not incident evidence.
        # Keep the standard SQL/log state available for later queries while excluding those setup
        # statements from the Agent-visible post-fault window.
        with self._hide_setup_observability(context.env):
            self._create_schema(context.env)
            self._load_catalog(context.env)
            self._load_orders(context.env)
            self._load_inventory(context.env)
            self._load_pricing(context.env)
            self._load_reference_catalog(context.env)
            for table in self.all_business_table_names:
                self._execute(
                    context.env,
                    f"ANALYZE TABLE {self.db}.{table}",
                    f"analyze table-cache-lease table: table={table}",
                )
            for table in self.all_cache_table_names:
                self._execute(
                    context.env,
                    f"ALTER TABLE {self.db}.{table} CACHE",
                    f"enable table-cache-lease cached table: table={table}",
                )
            self._verify_fault_state(context.env)
            with self._hide_setup_observability(context.env):
                self._settle_setup_observability(context.env)

    @staticmethod
    def _hide_setup_observability(env: object):
        hidden = getattr(env, "metrics_hidden", None)
        return hidden() if callable(hidden) else nullcontext()

    @staticmethod
    def _settle_setup_observability(env: object) -> None:
        """Wait for asynchronous DDL log delivery before closing visibility."""
        deployment = getattr(env, "deployment", None)
        read_logs = getattr(deployment, "read_logs", None)
        list_nodes = getattr(deployment, "list_nodes", None)
        if not callable(read_logs) or not callable(list_nodes):
            return
        previous = None
        for _ in range(24):
            current = tuple(
                len(read_logs(target, lines=10000).splitlines())
                for target in list_nodes()
            )
            if current and current == previous:
                return
            previous = current
            threading.Event().wait(0.25)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_fault_state(context.env)
        env = context.env
        targets = tuple(env.deployment.tidb_endpoints)
        cached_table_ids = {table: self._table_id(env, table) for table in self.all_cache_table_names}
        orders_table_id = self._table_id(env, self.orders_table)
        with self._hide_setup_observability(env):
            maintenance_burst = self._run_maintenance_burst(env, targets[0])
            interleaved_conflict, evidence_windows = self._run_interleaved_conflict_burst(
                env,
                targets,
                cached_table_ids,
                orders_table_id,
            )
            conflict_logs = self._capture_logs(
                env,
                targets,
                "capture table-cache-lease hidden combined conflict evidence",
                match_key="Write conflict",
            )
            read_path_logs = self._capture_logs(
                env,
                targets,
                "capture table-cache-lease hidden cached-table read-path evidence",
                match_key="lock cached table for read",
            )
            hidden_fault_logs = self._combine_log_windows(
                conflict_logs,
                read_path_logs,
                *evidence_windows.values(),
            )
            self._verify_combined_conflict_logs(hidden_fault_logs, cached_table_ids, orders_table_id)

        initial_business_phase = self._run_initial_business_phase(env, targets, orders_table_id)
        initial_fault_logs = self._capture_initial_business_logs(env, targets, orders_table_id)
        self._verify_initial_business_logs(initial_fault_logs, orders_table_id)
        causal_runtime_baseline = self._workload_profile_calls(env)
        business_payload = execute_json_payload(
            env.execute_sql,
            self.business_summary_sql,
            "capture table-cache-lease business result truth",
        )
        cached_table_states = {}
        cached_table_integrity = {}
        for table in self.all_cache_table_names:
            table_id = self._table_id(env, table)
            cache_meta_sql = (
                "SELECT tid, lock_type, lease, oldReadLease FROM mysql.table_cache_meta "
                f"WHERE tid = {table_id}"
            )
            cached_table_states[table] = {
                "table_id": table_id,
                "definition": execute_json_payload(
                    env.execute_sql,
                    f"SHOW CREATE TABLE {self.db}.{table}",
                    f"capture table-cache-lease cached table definition: table={table}",
                ),
                "cache_meta": execute_json_payload(
                    env.execute_sql,
                    cache_meta_sql,
                    f"capture table-cache-lease table cache metadata: table={table}",
                ),
            }
            cached_table_integrity[table] = self._integrity(env, table)
        lease_variable = execute_json_payload(
            env.execute_sql,
            "SHOW GLOBAL VARIABLES LIKE 'tidb_table_cache_lease'",
            "capture table-cache-lease table cache lease variable",
        )
        self._start_business_conflict_noise(env, targets, orders_table_id)
        self._start_causal_runtime(env, targets, causal_runtime_baseline)
        statement_summary = self._statement_summary(env)
        tso_sample = execute_json_payload(
            env.execute_sql,
            "BEGIN; SELECT @ma02_tso := TIDB_CURRENT_TSO(); ROLLBACK; SELECT @ma02_tso",
            "capture table-cache-lease TSO sample",
        )
        qps_series = parse_json_object(env.query_metrics("qps"), "capture table-cache-lease QPS series")
        query_latency_series = parse_json_object(
            env.query_metrics("query_latency"),
            "capture table-cache-lease query latency series",
        )
        return {
            "ma02_table_ids": {table: state["table_id"] for table, state in cached_table_states.items()},
            "ma02_orders_table_id": orders_table_id,
            "ma02_maintenance_burst": maintenance_burst,
            "ma02_interleaved_conflict_probe": interleaved_conflict,
            "ma02_initial_business_phase": initial_business_phase,
            "ma02_cached_table_states": cached_table_states,
            "ma02_lease_variable": lease_variable,
            "ma02_statement_summary": statement_summary,
            "business_result_truth": capture_query_result_truth(business_payload, ordered=True),
            "ma02_cached_table_integrity": cached_table_integrity,
            "ma02_tso_sample": tso_sample,
            "ma02_hidden_fault_logs": hidden_fault_logs,
            "ma02_initial_fault_logs": initial_fault_logs,
            "ma02_qps_series": qps_series,
            "ma02_query_latency_series": query_latency_series,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_business_conflict_noise()
        self._stop_causal_runtime()

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        env = context.env
        stopped_targets = self._stopped_tidb_targets(env)
        self._stop_business_conflict_noise(expected_stopped_targets=stopped_targets)
        self._stop_causal_runtime(expected_stopped_targets=stopped_targets)
        self._restart_stopped_tidb_targets(env, stopped_targets)
        for table in self.all_cache_table_names:
            self._execute(env, f"ALTER TABLE {self.db}.{table} NOCACHE", f"disable table-cache-lease cached table: table={table}")
        self._execute(env, "SET GLOBAL tidb_table_cache_lease = 3", "restore table-cache-lease table cache lease")
        for table in self.all_business_table_names:
            self._execute(env, f"DROP TABLE IF EXISTS {self.db}.{table}", f"drop table-cache-lease table: table={table}")

    @staticmethod
    def _line_payloads(logs: Mapping[str, object]) -> dict[str, str]:
        return {
            target: str(payload.get("content", ""))
            for target, payload in logs.items()
            if isinstance(payload, Mapping)
        }

    @staticmethod
    def _cache_conflict_handles(logs: Mapping[str, object]) -> set[int]:
        handles = set()
        for content in TidbSystemFailureTableCacheLeaseInjector._line_payloads(logs).values():
            for line in content.splitlines():
                folded = line.casefold()
                if "9007" not in folded or "table_cache_meta" not in folded:
                    continue
                for match in re.finditer(r"(?:handle|tid)\s*[=:]\s*(\d+)", line, flags=re.IGNORECASE):
                    handles.add(int(match.group(1)))
        return handles

    @staticmethod
    def _business_conflict_seen(logs: Mapping[str, object], orders_table_id: int) -> bool:
        table_markers = (
            f"handle={orders_table_id}",
            f"handle:{orders_table_id}",
            f"tid={orders_table_id}",
            f"tid:{orders_table_id}",
            "ma02_orders",
        )
        for content in TidbSystemFailureTableCacheLeaseInjector._line_payloads(logs).values():
            for line in content.splitlines():
                folded = line.casefold()
                if "9007" in folded and any(marker in folded for marker in table_markers):
                    return True
        return False

    def _capture_logs(
        self,
        env: object,
        targets: tuple[str, ...],
        context: str,
        *,
        match_key: str | None = None,
    ) -> dict[str, object]:
        return {
            target: require_success_payload(
                env.read_log(
                    target,
                    lines=200,
                    **({"match_key": match_key} if match_key is not None else {}),
                ),
                f"{context}: target={target!r}",
            )
            for target in targets
        }

    @staticmethod
    def _combine_log_windows(*windows: Mapping[str, object]) -> dict[str, object]:
        if not windows:
            raise ValueError("table-cache-lease log window combination requires at least one window")
        targets = tuple(windows[0])
        if any(tuple(window) != targets for window in windows[1:]):
            raise RuntimeError(
                "table-cache-lease log windows returned different target sets: "
                f"target_sets={tuple(tuple(window) for window in windows)!r}"
            )
        combined = {}
        for target in targets:
            first = dict(windows[0][target])
            first["content"] = "\n".join(
                window[target]["content"]
                for window in windows
            )
            first["match_key"] = tuple(
                window[target].get("match_key")
                for window in windows
                if window[target].get("match_key") is not None
            )
            combined[target] = first
        return combined

    def _verify_combined_conflict_logs(
        self,
        logs: Mapping[str, object],
        cached_table_ids: Mapping[str, int],
        orders_table_id: int,
    ) -> None:
        causal_ids = {cached_table_ids[table] for table in self.cache_table_names}
        healthy_ids = {cached_table_ids[table] for table in self.healthy_cache_table_names}
        rendered = "\n".join(self._line_payloads(logs).values()).casefold()
        observed_handles = self._cache_conflict_handles(logs)
        metadata_targets = {
            target
            for target, content in self._line_payloads(logs).items()
            if "9007" in content.casefold() and "table_cache_meta" in content.casefold()
        }
        missing_markers = [
            marker
            for marker in ("9007", "table_cache_meta", "lock cached table for read")
            if marker not in rendered
        ]
        missing_causal = causal_ids - observed_handles
        healthy_conflicts = healthy_ids & observed_handles
        if (
            missing_markers
            or missing_causal
            or healthy_conflicts
            or not metadata_targets
            or not self._business_conflict_seen(logs, orders_table_id)
        ):
            raise RuntimeError(
                "table-cache-lease combined conflict evidence is incomplete after the interleaved probes: "
                f"cached_table_ids={dict(cached_table_ids)!r}, orders_table_id={orders_table_id}, "
                f"observed_cache_handles={sorted(observed_handles)!r}, "
                f"business_conflict_seen={self._business_conflict_seen(logs, orders_table_id)!r}, "
                f"metadata_targets={sorted(metadata_targets)!r}, logs={logs!r}"
            )

    def _run_initial_business_phase(
        self,
        env: object,
        targets: tuple[str, ...],
        orders_table_id: int,
    ) -> dict[str, object]:
        if len(targets) < 2:
            raise RuntimeError(f"table-cache-lease initial business phase requires two TiDB endpoints: targets={targets!r}")
        probe_evidence = tuple(
            self._run_business_conflict_probe(
                env,
                targets,
                orders_table_id,
                order_id=order_id,
            )
            for order_id in _BUSINESS_NOISE_ORDER_IDS[:_BUSINESS_INITIAL_PHASE_ROUNDS]
        )
        if any(
            evidence["conflicts"] < 1 or evidence["retry_successes"] < 1
            for evidence in probe_evidence
        ):
            raise RuntimeError(
                "table-cache-lease initial business phase did not produce retryable business-row conflicts: "
                f"targets={targets!r}, orders_table_id={orders_table_id}, evidence={probe_evidence!r}"
            )
        return {
            "targets": targets[:2],
            "orders_table_id": orders_table_id,
            "rounds": len(probe_evidence),
            "order_ids": tuple(evidence["order_id"] for evidence in probe_evidence),
            "conflicts": sum(int(evidence["conflicts"]) for evidence in probe_evidence),
            "retry_successes": sum(int(evidence["retry_successes"]) for evidence in probe_evidence),
            "commits": sum(int(evidence["commits"]) for evidence in probe_evidence),
        }

    def _verify_initial_business_logs(
        self,
        logs: Mapping[str, object],
        orders_table_id: int,
    ) -> None:
        rendered = "\n".join(self._line_payloads(logs).values()).casefold()
        if not self._business_conflict_seen(logs, orders_table_id):
            raise RuntimeError(
                "table-cache-lease initial business log window did not contain the required orders conflict: "
                f"orders_table_id={orders_table_id}, logs={logs!r}"
            )
        if "table_cache_meta" in rendered or "lock cached table for read" in rendered:
            raise RuntimeError(
                "table-cache-lease initial business log window leaked cached-table conflict evidence before the runtime phase: "
                f"orders_table_id={orders_table_id}, logs={logs!r}"
            )

    def _capture_initial_business_logs(
        self,
        env: object,
        targets: tuple[str, ...],
        orders_table_id: int,
    ) -> dict[str, object]:
        deadline = time.monotonic() + 30
        logs: dict[str, object] = {}
        while time.monotonic() < deadline:
            logs = self._capture_logs(
                env,
                targets,
                "capture table-cache-lease initial business conflict evidence",
                match_key=f"UPDATE {self.db}.{self.orders_table}",
            )
            if self._business_conflict_seen(logs, orders_table_id):
                return logs
            time.sleep(0.25)
        raise RuntimeError(
            "table-cache-lease initial business conflict did not become visible before the bounded log deadline: "
            f"orders_table_id={orders_table_id}, logs={logs!r}"
        )

    def _start_causal_runtime(
        self,
        env: object,
        targets: tuple[str, ...],
        baseline_calls: Mapping[str, int],
    ) -> None:
        if self._causal_runtime_thread is not None:
            raise RuntimeError("table-cache-lease causal runtime is already running")
        if len(targets) < 2:
            raise RuntimeError(f"table-cache-lease causal runtime requires two TiDB endpoints: targets={targets!r}")
        self._causal_runtime_stop.clear()
        self._causal_runtime_failure = None

        def run() -> None:
            deadline = time.monotonic() + _CAUSAL_RUNTIME_DEADLINE_SECONDS
            try:
                self._wait_for_workload_phase(env, deadline, baseline_calls)
                for round_no in range(1, _CAUSAL_RUNTIME_ROUNDS + 1):
                    if self._causal_runtime_stop.is_set():
                        return
                    table = self.cache_table_names[(round_no - 1) % len(self.cache_table_names)]
                    self._run_dual_cache_read(env, targets[:2], table, round_no)
                    self._run_healthy_cache_read(
                        env,
                        targets[0],
                        self.healthy_cache_table_names[0],
                        round_no,
                    )
            except BaseException as exc:
                self._causal_runtime_failure = exc

        self._causal_runtime_thread = threading.Thread(
            target=run,
            name="causal-cache-runtime",
            daemon=True,
        )
        self._causal_runtime_thread.start()

    def _workload_profile_calls(self, env: object) -> dict[str, int]:
        payload = parse_json_object(
            env.observe_metric("workload_activity"),
            "capture table-cache-lease workload phase",
        )
        return {
            str(item["fingerprint"]): int(item["ok_calls"])
            for item in payload["snapshot"]["profiles"]
            if isinstance(item, Mapping) and "fingerprint" in item and "ok_calls" in item
        }

    def _wait_for_workload_phase(
        self,
        env: object,
        deadline: float,
        baseline_calls: Mapping[str, int],
    ) -> None:
        while time.monotonic() < deadline and not self._causal_runtime_stop.is_set():
            current_calls = self._workload_profile_calls(env)
            gate_profile = self.target_profile_names[0]
            if (
                gate_profile in baseline_calls
                and gate_profile in current_calls
                and current_calls[gate_profile]
                >= baseline_calls[gate_profile] + _CAUSAL_RUNTIME_MIN_ADDITIONAL_CALLS_PER_PROFILE
            ):
                return
            if self._causal_runtime_stop.wait(0.25):
                return
        raise RuntimeError(
            "table-cache-lease causal runtime did not reach the workload phase deadline: "
            f"target_profiles={self.target_profile_names!r}, "
            f"minimum_additional_calls={_CAUSAL_RUNTIME_MIN_ADDITIONAL_CALLS_PER_PROFILE}"
        )

    @staticmethod
    def _connection_loss(exc: BaseException) -> bool:
        current: BaseException | None = exc
        while current is not None:
            if isinstance(current, pymysql.MySQLError):
                code = current.args[0] if current.args else None
                if code in {2003, 2013, 2055}:
                    return True
            if isinstance(current, (BrokenPipeError, ConnectionError)):
                return True
            current = current.__cause__ or current.__context__
        return False

    @staticmethod
    def _stopped_tidb_targets(env: object) -> tuple[str, ...]:
        deployment = env.deployment
        states = deployment.node_states()
        return tuple(
            target
            for target in deployment.tidb_endpoints
            if not states[target]["running"]
        )

    @staticmethod
    def _restart_stopped_tidb_targets(env: object, targets: tuple[str, ...]) -> None:
        deployment = env.deployment
        for target in targets:
            deployment.start_component(target)
            deployment.wait_for_target(target, deployment.warm_tidb_readiness_timeout_sec)

    def _stop_causal_runtime(
        self,
        *,
        expected_stopped_targets: tuple[str, ...] = (),
    ) -> None:
        thread = self._causal_runtime_thread
        if thread is None:
            return
        self._causal_runtime_stop.set()
        join_thread(thread, 60, "table-cache-lease causal cache runtime")
        self._causal_runtime_thread = None
        if self._causal_runtime_failure is not None:
            if expected_stopped_targets and self._connection_loss(self._causal_runtime_failure):
                return
            raise RuntimeError(
                "table-cache-lease causal cache runtime failed: "
                f"error={self._causal_runtime_failure!r}"
            ) from self._causal_runtime_failure

    def _run_interleaved_conflict_burst(
        self,
        env: object,
        targets: tuple[str, ...],
        cached_table_ids: Mapping[str, int],
        orders_table_id: int,
    ) -> tuple[dict[str, object], dict[str, dict[str, object]]]:
        if len(targets) < 2:
            raise RuntimeError(f"table-cache-lease interleaved conflict burst requires two TiDB endpoints: targets={targets!r}")
        selected_targets = targets[:2]
        healthy_table = self.healthy_cache_table_names[0]
        healthy_target = selected_targets[0]
        per_round: list[dict[str, object]] = []
        evidence_windows: dict[str, dict[str, object]] = {}
        causal_last_probe: dict[str, float] = {}
        totals = {"commits": 0, "conflicts": 0, "retry_successes": 0}
        for round_no in range(1, _BUSINESS_CONFLICT_BURST_ROUNDS + 1):
            causal_table = self.cache_table_names[(round_no - 1) % len(self.cache_table_names)]
            try:
                business_evidence = tuple(
                    self._run_business_conflict_probe(
                        env,
                        selected_targets,
                        orders_table_id,
                        order_id=order_id,
                    )
                    for order_id in _BUSINESS_PROBE_ORDER_IDS
                )
                self._run_dual_cache_read(env, selected_targets, causal_table, round_no)
                causal_last_probe[causal_table] = time.monotonic()
                self._accumulate_conflict_evidence(
                    env,
                    selected_targets,
                    causal_table,
                    cached_table_ids,
                    evidence_windows,
                )
                self._run_healthy_cache_read(env, healthy_target, healthy_table, round_no)
            except BaseException as exc:
                raise RuntimeError(
                    "table-cache-lease interleaved conflict burst failed during a bounded round: "
                    f"round={round_no}, causal_table={causal_table!r}, healthy_table={healthy_table!r}, "
                    f"targets={selected_targets!r}, cached_table_ids={dict(cached_table_ids)!r}, "
                    f"orders_table_id={orders_table_id}, completed_rounds={len(per_round)}"
                ) from exc
            if any(
                evidence["conflicts"] < 1 or evidence["retry_successes"] < 1
                for evidence in business_evidence
            ):
                raise RuntimeError(
                    "table-cache-lease interleaved round did not produce two real business conflicts and retry successes: "
                    f"round={round_no}, causal_table={causal_table!r}, targets={selected_targets!r}, "
                    f"orders_table_id={orders_table_id}, evidence={business_evidence!r}"
                )
            round_evidence = {
                "round": round_no,
                "causal_table": causal_table,
                "causal_table_id": cached_table_ids[causal_table],
                "healthy_table": healthy_table,
                "healthy_target": healthy_target,
                "business_probes": business_evidence,
                "commits": sum(int(evidence["commits"]) for evidence in business_evidence),
                "conflicts": sum(int(evidence["conflicts"]) for evidence in business_evidence),
                "retry_successes": sum(int(evidence["retry_successes"]) for evidence in business_evidence),
            }
            per_round.append(round_evidence)
            totals["commits"] += int(round_evidence["commits"])
            totals["conflicts"] += int(round_evidence["conflicts"])
            totals["retry_successes"] += int(round_evidence["retry_successes"])
        self._top_up_conflict_evidence(
            env,
            selected_targets,
            cached_table_ids,
            evidence_windows,
            causal_last_probe,
        )
        summary = {
            "orders_table_id": orders_table_id,
            "targets": selected_targets,
            "rounds": _BUSINESS_CONFLICT_BURST_ROUNDS,
            "business_probes_per_round": 2,
            "healthy_table": healthy_table,
            "healthy_target": healthy_target,
            "causal_rounds": {
                table: sum(round_evidence["causal_table"] == table for round_evidence in per_round)
                for table in self.cache_table_names
            },
            "healthy_reads": len(per_round),
            "evidence_tables": tuple(table for table in self.cache_table_names if table in evidence_windows),
            **totals,
            "per_round": tuple(per_round),
        }
        return summary, evidence_windows

    @staticmethod
    def _meta_conflict_match_key(table_id: int) -> str:
        return f"table_cache_meta, handle={table_id}"

    def _accumulate_conflict_evidence(
        self,
        env: object,
        targets: tuple[str, ...],
        table: str,
        cached_table_ids: Mapping[str, int],
        evidence_windows: dict[str, dict[str, object]],
    ) -> None:
        """Capture a per-table meta-conflict window that cannot be flooded out by
        business "Write conflict" matches or lost to log-window pagination."""
        if table in evidence_windows:
            return
        table_id = cached_table_ids[table]
        window = self._capture_logs(
            env,
            targets,
            f"capture table-cache-lease hidden meta-conflict evidence: table={table!r}",
            match_key=self._meta_conflict_match_key(table_id),
        )
        if table_id in self._cache_conflict_handles(window):
            evidence_windows[table] = window

    def _top_up_conflict_evidence(
        self,
        env: object,
        targets: tuple[str, ...],
        cached_table_ids: Mapping[str, int],
        evidence_windows: dict[str, dict[str, object]],
        causal_last_probe: Mapping[str, float],
    ) -> None:
        """Re-probe causal tables whose cached-table reads never collided: the
        meta write conflict only fires once the shared read lease expired, so
        wait past the lease before each retry and require evidence per table."""
        pending = tuple(table for table in self.cache_table_names if table not in evidence_windows)
        attempt = 0
        deadline = time.monotonic() + _TABLE_CACHE_LEASE_CONFLICT_EVIDENCE_TOP_UP_DEADLINE_SECONDS
        while pending:
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "table-cache-lease interleaved conflict burst did not produce mysql.table_cache_meta write-conflict "
                    f"evidence for every causal table before the bounded top-up deadline: "
                    f"pending_tables={pending!r}, cached_table_ids={dict(cached_table_ids)!r}, "
                    f"evidence_tables={sorted(evidence_windows)!r}, targets={targets!r}"
                )
            for table in pending:
                expiry_wait = (
                    _TABLE_CACHE_LEASE_SECONDS
                    + _TABLE_CACHE_LEASE_LEASE_EXPIRY_MARGIN_SECONDS
                    - (time.monotonic() - causal_last_probe.get(table, 0.0))
                )
                if expiry_wait > 0:
                    time.sleep(expiry_wait)
                attempt += 1
                self._run_dual_cache_read(env, targets, table, attempt)
                causal_last_probe[table] = time.monotonic()
                self._accumulate_conflict_evidence(
                    env,
                    targets,
                    table,
                    cached_table_ids,
                    evidence_windows,
                )
            pending = tuple(table for table in self.cache_table_names if table not in evidence_windows)

    def _run_dual_cache_read(self, env: object, targets: tuple[str, ...], table: str, attempt: int) -> None:
        barrier = threading.Barrier(2, timeout=20)
        failures: list[BaseException] = []
        lock = threading.Lock()

        def worker(target: str) -> None:
            conn = env.open_workload_connection(f"cache-read-{table}-{target.rsplit('/', 1)[1]}", target=target)
            try:
                with conn.cursor() as cur:
                    barrier.wait()
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM {self.db}.{table}")
                        cur.fetchall()
                        conn.rollback()
                    except pymysql.MySQLError as exc:
                        code = exc.args[0] if exc.args else None
                        conn.rollback()
                        if code != 9007:
                            raise RuntimeError(
                                "table-cache-lease cache read probe returned an unexpected SQL error: "
                                f"table={table!r}, target={target!r}, attempt={attempt}, code={code!r}, error={exc}"
                            ) from exc
            except BaseException as exc:
                with lock:
                    failures.append(exc)
                barrier.abort()
            finally:
                conn.close()

        threads = tuple(
            threading.Thread(target=worker, args=(target,), name=f"cache-read-{table}-{target}", daemon=True)
            for target in targets
        )
        for thread in threads:
            thread.start()
        for thread in threads:
            join_thread(thread, 30, f"table-cache-lease cache read probe {thread.name}")
        if failures:
            raise RuntimeError(f"table-cache-lease cache read probe failed: table={table!r}, failures={failures!r}") from failures[0]

    def _run_healthy_cache_read(self, env: object, target: str, table: str, round_no: int) -> None:
        conn = env.open_workload_connection("cache-companion-read", target=target)
        try:
            with conn.cursor() as cur:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {self.db}.{table}")
                    cur.fetchall()
                    conn.rollback()
                except pymysql.MySQLError as exc:
                    code = exc.args[0] if exc.args else None
                    conn.rollback()
                    raise RuntimeError(
                        "table-cache-lease healthy cached companion read failed: "
                        f"round={round_no}, table={table!r}, target={target!r}, code={code!r}, error={exc}"
                    ) from exc
        finally:
            conn.close()

    def _run_business_conflict_probe(
        self,
        env: object,
        targets: tuple[str, ...],
        orders_table_id: int,
        *,
        order_id: int = 17,
    ) -> dict[str, object]:
        if len(targets) < 2:
            raise RuntimeError(f"table-cache-lease business conflict probe requires two TiDB endpoints: targets={targets!r}")
        selected_targets = targets[:2]
        barrier = threading.Barrier(2, timeout=20)
        failures: list[BaseException] = []
        errors: list[str] = []
        counts = {"commits": 0, "conflicts": 0, "retries": 0}
        lock = threading.Lock()
        original_attempts = self._read_business_attempts(
            env,
            selected_targets[0],
            "capture table-cache-lease business conflict probe baseline",
            order_id=order_id,
        )
        write_barrier = threading.Barrier(2, timeout=20)
        first_commit = threading.Event()

        def worker(worker_id: int, target: str) -> None:
            conn = env.open_workload_connection(f"checkout-retry-worker-{worker_id}", target=target)
            try:
                with conn.cursor() as cur:
                    cur.execute("SET SESSION tidb_txn_mode = 'OPTIMISTIC'")
                    cur.execute("START TRANSACTION")
                    cur.execute(
                        f"SELECT write_attempts FROM {self.db}.{self.orders_table} WHERE order_id = {order_id}"
                    )
                    barrier.wait()
                    try:
                        cur.execute(
                            f"UPDATE {self.db}.{self.orders_table} "
                            f"SET write_attempts = write_attempts + 1 WHERE order_id = {order_id}"
                        )
                        write_barrier.wait()
                        if worker_id == 1:
                            if not first_commit.wait(20):
                                raise RuntimeError(
                                    "table-cache-lease business conflict probe timed out waiting for the first commit: "
                                    f"worker={worker_id}, target={target!r}"
                                )
                        conn.commit()
                    except pymysql.MySQLError as exc:
                        code = exc.args[0] if exc.args else None
                        if code != 9007:
                            raise RuntimeError(
                                "table-cache-lease business conflict probe returned an unexpected SQL error: "
                                f"worker={worker_id}, target={target!r}, code={code!r}, error={exc}"
                            ) from exc
                        conn.rollback()
                        with lock:
                            counts["conflicts"] += 1
                            errors.append(str(exc))
                        cur.execute("START TRANSACTION")
                        cur.execute(
                            f"UPDATE {self.db}.{self.orders_table} "
                            f"SET write_attempts = write_attempts + 1 WHERE order_id = {order_id}"
                        )
                        conn.commit()
                        with lock:
                            counts["retries"] += 1
                    else:
                        with lock:
                            counts["commits"] += 1
                    finally:
                        if worker_id == 0:
                            first_commit.set()
            except BaseException as exc:
                with lock:
                    failures.append(exc)
                barrier.abort()
                write_barrier.abort()
            finally:
                conn.close()

        try:
            threads = tuple(
                threading.Thread(
                    target=worker,
                    args=(worker_id, target),
                    name=f"business-row-conflict-{worker_id}",
                    daemon=True,
                )
                for worker_id, target in enumerate(selected_targets)
            )
            for thread in threads:
                thread.start()
            for thread in threads:
                join_thread(thread, 30, f"table-cache-lease business conflict probe {thread.name}")
            if failures:
                raise RuntimeError(f"table-cache-lease business conflict probe failed: failures={failures!r}") from failures[0]
            if counts["conflicts"] < 1 or counts["retries"] < 1:
                raise RuntimeError(
                    "table-cache-lease business conflict probe did not produce a retryable business-row 9007: "
                    f"targets={selected_targets!r}, orders_table_id={orders_table_id}, order_id={order_id}, "
                    f"counts={counts!r}, errors={errors!r}"
                )
            return {
                "orders_table_id": orders_table_id,
                "order_id": order_id,
                "targets": selected_targets,
                "commits": counts["commits"],
                "conflicts": counts["conflicts"],
                "retry_successes": counts["retries"],
                "errors": tuple(errors),
            }
        finally:
            self._restore_business_attempts(
                env,
                selected_targets[0],
                original_attempts,
                "restore table-cache-lease business conflict probe baseline",
                order_id=order_id,
            )

    def _read_business_attempts(self, env: object, target: str, context: str, *, order_id: int) -> int:
        conn = env.open_workload_connection("business-probe-baseline", target=target)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT write_attempts FROM {self.db}.{self.orders_table} WHERE order_id = {order_id}"
                )
                rows = cur.fetchall()
            conn.rollback()
        finally:
            conn.close()
        return int(
            require_one_result_row(
                rows,
                context,
            )[0]
        )

    def _restore_business_attempts(
        self,
        env: object,
        target: str,
        original_attempts: int,
        context: str,
        *,
        order_id: int,
    ) -> None:
        conn = env.open_workload_connection("business-probe-restore", target=target)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {self.db}.{self.orders_table} "
                    f"SET write_attempts = {original_attempts} WHERE order_id = {order_id}"
                )
            conn.commit()
        finally:
            conn.close()

    def _run_maintenance_burst(self, env: object, target: str) -> dict[str, object]:
        tables = (self.orders_table, self.inventory_table)
        for table in tables:
            self._execute(
                env,
                f"ANALYZE TABLE {self.db}.{table}",
                f"run table-cache-lease bounded maintenance burst: table={table}",
                target=target,
            )
        return {
            "target": target,
            "tables": tables,
            "completed": True,
        }

    def _start_business_conflict_noise(
        self,
        env: object,
        targets: tuple[str, ...],
        orders_table_id: int,
    ) -> None:
        if self._business_noise_thread is not None:
            raise RuntimeError("table-cache-lease business conflict noise is already running")
        self._business_noise_stop.clear()
        self._business_noise_failure = None

        def run() -> None:
            deadline = time.monotonic() + _BUSINESS_NOISE_DURATION_SECONDS
            noise_round = 0
            try:
                while time.monotonic() < deadline and not self._business_noise_stop.is_set():
                    order_id = _BUSINESS_NOISE_ORDER_IDS[noise_round % len(_BUSINESS_NOISE_ORDER_IDS)]
                    self._run_business_conflict_probe(env, targets, orders_table_id, order_id=order_id)
                    noise_round += 1
                    if self._business_noise_stop.wait(_BUSINESS_NOISE_INTERVAL_SECONDS):
                        return
            except BaseException as exc:
                self._business_noise_failure = exc

        self._business_noise_thread = threading.Thread(
            target=run,
            name="business-conflict-noise",
            daemon=True,
        )
        self._business_noise_thread.start()

    def _stop_business_conflict_noise(
        self,
        *,
        expected_stopped_targets: tuple[str, ...] = (),
    ) -> None:
        thread = self._business_noise_thread
        if thread is None:
            return
        self._business_noise_stop.set()
        join_thread(thread, 60, "table-cache-lease business conflict noise")
        self._business_noise_thread = None
        if self._business_noise_failure is not None:
            if expected_stopped_targets and self._connection_loss(self._business_noise_failure):
                return
            raise RuntimeError(
                "table-cache-lease business conflict noise failed: "
                f"error={self._business_noise_failure!r}"
            ) from self._business_noise_failure

    def _statement_summary(self, env: object) -> dict[str, object]:
        return execute_json_payload(
            env.execute_sql,
            "SELECT INSTANCE, DIGEST_TEXT, EXEC_COUNT, SUMMARY_BEGIN_TIME, SUMMARY_END_TIME "
            "FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY "
            f"WHERE DIGEST_TEXT LIKE '%{self.db}%' OR DIGEST_TEXT LIKE '%ma02_%' "
            "ORDER BY EXEC_COUNT DESC LIMIT 80",
            "capture table-cache-lease statement summary",
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.cache_table = validate_sql_identifier(str(config["cache_table"]), "cache table")
        self.cache_table_names = tuple(
            validate_sql_identifier(str(table), "cached table") for table in config["cache_table_names"]
        )
        self.pricing_table = validate_sql_identifier(str(config["pricing_table"]), "pricing table")
        self.healthy_cache_table_names = tuple(
            validate_sql_identifier(str(table), "healthy cached table")
            for table in config["healthy_cache_table_names"]
        )
        self.orders_table = validate_sql_identifier(str(config["orders_table"]), "orders table")
        self.inventory_table = validate_sql_identifier(str(config["inventory_table"]), "inventory table")
        self.all_cache_table_names = self.cache_table_names + self.healthy_cache_table_names
        self.all_business_table_names = (
            self.cache_table,
            self.orders_table,
            self.inventory_table,
            self.pricing_table,
            *self.healthy_cache_table_names,
        )
        self.catalog_row_count = int(config["catalog_row_count"])
        self.business_summary_sql = str(config["business_summary_sql"])
        self.table_integrity_sql = str(config["table_integrity_sql"])
        self.target_profile_names = tuple(
            validate_sql_identifier(str(profile), "target workload profile")
            for profile in config["target_profile_names"]
        )

    @staticmethod
    def _execute(env: object, sql: str, context: str, *, target: str | None = None) -> dict:
        result = env.execute_sql(sql) if target is None else env.execute_sql(sql, target=target)
        return require_success_payload(result, f"{context}: sql={sql!r}")

    def _create_schema(self, env: object) -> None:
        self._execute(env, f"CREATE DATABASE IF NOT EXISTS {self.db}", "create table-cache-lease database")
        for table in self.all_business_table_names:
            self._execute(env, f"DROP TABLE IF EXISTS {self.db}.{table}", f"clear table-cache-lease table: table={table}")
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.cache_table} ("
            "sku_id BIGINT NOT NULL, "
            "tenant_id INT NOT NULL, "
            "category VARCHAR(32) NOT NULL, "
            "price DECIMAL(12,2) NOT NULL, "
            "stock INT NOT NULL, "
            "updated_at DATETIME NOT NULL, "
            "PRIMARY KEY (sku_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            "create table-cache-lease cache table",
        )
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.orders_table} ("
            "order_id BIGINT NOT NULL, "
            "tenant_id INT NOT NULL, "
            "sku_id BIGINT NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, "
            "status VARCHAR(16) NOT NULL, "
            "write_attempts INT NOT NULL DEFAULT 0, "
            "created_at DATETIME NOT NULL, "
            "PRIMARY KEY (order_id), KEY idx_orders_tenant (tenant_id, created_at), KEY idx_orders_sku (sku_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            "create table-cache-lease orders table",
        )
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.inventory_table} ("
            "sku_id BIGINT NOT NULL, "
            "warehouse_id INT NOT NULL, "
            "available INT NOT NULL, "
            "reserved INT NOT NULL, "
            "PRIMARY KEY (sku_id, warehouse_id), KEY idx_inventory_warehouse (warehouse_id, sku_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            "create table-cache-lease inventory table",
        )
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.pricing_table} ("
            "rule_id BIGINT NOT NULL, "
            "tenant_id INT NOT NULL, "
            "category VARCHAR(32) NOT NULL, "
            "discount_pct DECIMAL(5,2) NOT NULL, "
            "priority INT NOT NULL, "
            "active TINYINT NOT NULL, "
            "PRIMARY KEY (rule_id), KEY idx_rules_tenant (tenant_id, active, priority)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            "create table-cache-lease pricing rules table",
        )
        for table in self.healthy_cache_table_names:
            self._execute(
                env,
                f"CREATE TABLE {self.db}.{table} ("
                "sku_id BIGINT NOT NULL, "
                "tenant_id INT NOT NULL, "
                "category VARCHAR(32) NOT NULL, "
                "price DECIMAL(12,2) NOT NULL, "
                "stock INT NOT NULL, "
                "updated_at DATETIME NOT NULL, "
                "PRIMARY KEY (sku_id)"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
                f"create table-cache-lease healthy cached table: table={table}",
            )

    def _load_catalog(self, env: object) -> None:
        self._execute(
            env,
            f"INSERT INTO {self.db}.{self.cache_table} "
            "(sku_id, tenant_id, category, price, stock, updated_at) "
            "SELECT n, MOD(n, 32) + 1, ELT(MOD(n, 4) + 1, 'hardware', 'software', 'service', 'accessory'), "
            "CAST(MOD(n * 7919, 100000) / 100 AS DECIMAL(12,2)), MOD(n * 13, 400), "
            "TIMESTAMPADD(DAY, MOD(n, 365), '2026-01-01 00:00:00') "
            "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) AS n "
            f"FROM information_schema.columns LIMIT {self.catalog_row_count}) AS source",
            "load table-cache-lease cache table",
        )

    def _load_orders(self, env: object) -> None:
        self._execute(
            env,
            f"INSERT INTO {self.db}.{self.orders_table} "
            "(order_id, tenant_id, sku_id, amount, status, created_at) "
            "SELECT a.n * 32 + b.n + 1, MOD(a.n, 32) + 1, MOD(a.n * 7 + b.n, 256), "
            "CAST(MOD((a.n * 32 + b.n) * 313, 100000) / 100 AS DECIMAL(12,2)), "
            "ELT(MOD(a.n + b.n, 4) + 1, 'paid', 'pending', 'shipped', 'cancelled'), "
            "TIMESTAMPADD(MINUTE, a.n * 32 + b.n, '2026-01-01 00:00:00') "
            "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) - 1 AS n "
            "FROM information_schema.columns LIMIT 64) AS a "
            "CROSS JOIN (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) - 1 AS n "
            "FROM information_schema.columns LIMIT 32) AS b",
            "load table-cache-lease orders table",
        )

    def _load_inventory(self, env: object) -> None:
        self._execute(
            env,
            f"INSERT INTO {self.db}.{self.inventory_table} "
            "(sku_id, warehouse_id, available, reserved) "
            "SELECT a.n + 1, b.n + 1, MOD(a.n * 17 + b.n * 11, 400), MOD(a.n + b.n, 40) "
            "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) - 1 AS n "
            "FROM information_schema.columns LIMIT 256) AS a "
            "CROSS JOIN (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) - 1 AS n "
            "FROM information_schema.columns LIMIT 4) AS b",
            "load table-cache-lease inventory table",
        )

    def _load_pricing(self, env: object) -> None:
        self._execute(
            env,
            f"INSERT INTO {self.db}.{self.pricing_table} "
            "(rule_id, tenant_id, category, discount_pct, priority, active) "
            "SELECT n, MOD(n, 32) + 1, ELT(MOD(n, 4) + 1, 'hardware', 'software', 'service', 'accessory'), "
            "CAST(MOD(n * 17, 2500) / 100 AS DECIMAL(5,2)), MOD(n, 5) + 1, IF(MOD(n, 3) = 0, 0, 1) "
            "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) AS n "
            "FROM information_schema.columns LIMIT 128) AS source",
            "load table-cache-lease pricing rules table",
        )

    def _load_reference_catalog(self, env: object) -> None:
        for table in self.healthy_cache_table_names:
            self._execute(
                env,
                f"INSERT INTO {self.db}.{table} "
                "(sku_id, tenant_id, category, price, stock, updated_at) "
                "SELECT n + 10000, MOD(n, 32) + 1, ELT(MOD(n, 4) + 1, 'hardware', 'software', 'service', 'accessory'), "
                "CAST(MOD(n * 6151, 100000) / 100 AS DECIMAL(12,2)), MOD(n * 7, 400), "
                "TIMESTAMPADD(DAY, MOD(n, 365), '2026-01-01 00:00:00') "
                "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) - 1 AS n "
                "FROM information_schema.columns LIMIT 64) AS source",
                f"load table-cache-lease healthy cached table: table={table}",
            )

    def _table_id(self, env: object, table: str) -> int:
        rows = execute_result_rows(
            env.execute_sql,
            "SELECT TIDB_TABLE_ID FROM information_schema.tables "
            f"WHERE TABLE_SCHEMA = '{self.db}' AND TABLE_NAME = '{table}'",
            f"read table-cache-lease cached table ID: table={table}",
        )
        row = require_one_result_row(rows, f"read table-cache-lease cached table ID: table={table}")
        if len(row) != 1:
            raise ValueError(f"table-cache-lease cached table ID query returned an unexpected row: table={table!r}, row={row!r}")
        return int(row[0])

    def _integrity(self, env: object, table: str) -> tuple[int, int, int]:
        sql = table_cache_lease_integrity_sql(
            self.db,
            table,
            cache_table=self.cache_table,
            cache_integrity_sql=self.table_integrity_sql,
            orders_table=self.orders_table,
            inventory_table=self.inventory_table,
            pricing_table=self.pricing_table,
            healthy_cache_table_names=self.healthy_cache_table_names,
        )
        return execute_integrity_tuple(env.execute_sql, sql, f"capture table-cache-lease {table} integrity")

    def _verify_fault_state(self, env: object) -> None:
        lease_rows = execute_result_rows(
            env.execute_sql,
            "SHOW GLOBAL VARIABLES LIKE 'tidb_table_cache_lease'",
            "verify table-cache-lease table cache lease",
        )
        if len(lease_rows) != 1 or int(lease_rows[0][1]) != 3:
            raise RuntimeError(f"table-cache-lease requires the fixed TiDB v8.1 default lease of 3 seconds: observed={lease_rows!r}")
        for table in self.all_cache_table_names:
            definition = execute_json_payload(
                env.execute_sql,
                f"SHOW CREATE TABLE {self.db}.{table}",
                f"verify table-cache-lease cached table definition: table={table}",
            )
            rendered_definition = "\n".join(str(value) for row in definition["result"] for value in row).casefold()
            if "cached on" not in rendered_definition:
                raise RuntimeError(
                    f"table-cache-lease cache table is not cached: table={self.db}.{table}, definition={definition!r}"
                )
            table_id = self._table_id(env, table)
            meta = execute_result_rows(
                env.execute_sql,
                "SELECT tid, lock_type, lease, oldReadLease FROM mysql.table_cache_meta "
                f"WHERE tid = {table_id}",
                f"verify table-cache-lease table cache metadata: table={table}",
            )
            if len(meta) != 1 or int(meta[0][0]) != table_id:
                raise RuntimeError(
                    f"table-cache-lease cached table metadata row is missing: table={table!r}, table_id={table_id}, observed={meta!r}"
                )
        summary = execute_result_rows(env.execute_sql, self.business_summary_sql, "verify table-cache-lease business truth")
        if len(summary) != 1 or len(summary[0]) != 3:
            raise RuntimeError(f"table-cache-lease business summary is malformed: observed={summary!r}")
        tso = execute_result_rows(
            env.execute_sql,
            "BEGIN; SELECT @ma02_tso := TIDB_CURRENT_TSO(); ROLLBACK; SELECT @ma02_tso",
            "verify table-cache-lease TSO",
        )
        if len(tso) != 1 or int(tso[0][0]) <= 0:
            raise RuntimeError(f"table-cache-lease TSO is not advancing: observed={tso!r}")
