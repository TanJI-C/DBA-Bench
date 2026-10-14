import hashlib
import shutil
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

from src.database.sql import sql_literal
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    run_sql_batches,
    validate_sql_identifier,
)

from src.scenarios.evaluation.tidb.health_check.backup_recoverability import (
    TidbHealthCheckBackupRecoverabilityForBackupChainRepairEvaluatorCase,
    TidbHealthCheckBackupRecoverabilityForSingleSegmentContinuityEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckBackupRecoverabilityCase(TiDBScenarioCase):
    db: str
    request_key: str
    backup_catalog_table: str
    log_segment_table: str
    restore_drill_table: str
    restore_check_table: str
    restore_attempt_table: str
    audit_request_table: str
    approval_table: str
    object_inventory_table: str
    monitoring_table: str
    orders_table: str
    order_lines_table: str
    payments_table: str
    inventory_table: str
    live_events_table: str
    snapshot_orders_table: str
    snapshot_order_lines_table: str
    snapshot_payments_table: str
    snapshot_inventory_table: str
    sandbox_orders_table: str
    sandbox_order_lines_table: str
    sandbox_payments_table: str
    sandbox_inventory_table: str
    selected_backup_id: str
    selected_drill_id: str
    requested_target: str
    latest_recoverable: str
    front_segment: str
    front_range_start: str
    front_range_end: str
    early_segment: str
    early_range_start: str
    early_range_end: str
    late_segment: str
    late_range_start: str
    late_range_end: str
    missing_segment: str
    missing_range_start: str
    missing_range_end: str
    secondary_segment: str
    secondary_range_start: str
    secondary_range_end: str
    continuity_segment: str
    continuity_range_start: str
    continuity_range_end: str
    source_orders: int
    source_order_lines: int
    source_payments: int
    source_inventory: int
    source_checksum: int
    rpo_target_seconds: int
    rto_target_seconds: int
    continuity_only: bool
    focused_fixture: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckBackupRecoverabilityForBackupChainRepairScenarioCase(
    TidbHealthCheckBackupRecoverabilityCase
):
    pass


HC04_DB = "benchops"
HC04_REQUEST_KEY = "hc04-weekly-recoverability-20260804"
HC04_BACKUP_TABLE = "hc04_backup_catalog"
HC04_SEGMENT_TABLE = "hc04_log_segments"
HC04_DRILL_TABLE = "hc04_restore_drills"
HC04_CHECK_TABLE = "hc04_restore_table_checks"
HC04_ATTEMPT_TABLE = "hc04_restore_attempts"
HC04_REQUEST_TABLE = "hc04_audit_requests"
HC04_APPROVAL_TABLE = "hc04_recovery_approvals"
HC04_OBJECT_TABLE = "hc04_archive_objects"
HC04_MONITOR_TABLE = "hc04_monitoring_events"
HC04_ORDERS_TABLE = "hc04_orders"
HC04_ORDER_LINES_TABLE = "hc04_order_lines"
HC04_PAYMENTS_TABLE = "hc04_payments"
HC04_INVENTORY_TABLE = "hc04_inventory"
HC04_LIVE_EVENTS_TABLE = "hc04_live_events"
HC04_SNAPSHOT_ORDERS_TABLE = "hc04_snapshot_orders"
HC04_SNAPSHOT_ORDER_LINES_TABLE = "hc04_snapshot_order_lines"
HC04_SNAPSHOT_PAYMENTS_TABLE = "hc04_snapshot_payments"
HC04_SNAPSHOT_INVENTORY_TABLE = "hc04_snapshot_inventory"
HC04_SANDBOX_ORDERS_TABLE = "hc04_restore_sandbox_orders"
HC04_SANDBOX_ORDER_LINES_TABLE = "hc04_restore_sandbox_order_lines"
HC04_SANDBOX_PAYMENTS_TABLE = "hc04_restore_sandbox_payments"
HC04_SANDBOX_INVENTORY_TABLE = "hc04_restore_sandbox_inventory"
HC04_SELECTED_BACKUP = "hc04-full-20260803-t2"
HC04_SELECTED_DRILL = "hc04-drill-20260804-selected"
HC04_REQUESTED_TARGET = "2026-08-03 01:15:00"
HC04_LATEST_RECOVERABLE = "2026-08-03 01:04:00"
HC04_FRONT_SEGMENT = "t2-00000000000000A3"
HC04_FRONT_RANGE_START = "2026-08-03 00:28:00"
HC04_FRONT_RANGE_END = "2026-08-03 00:40:00"
HC04_EARLY_SEGMENT = "t2-00000000000000A4"
HC04_EARLY_RANGE_START = "2026-08-03 00:40:00"
HC04_EARLY_RANGE_END = "2026-08-03 00:52:00"
HC04_LATE_SEGMENT = "t2-00000000000000A5"
HC04_LATE_RANGE_START = "2026-08-03 00:52:00"
HC04_LATE_RANGE_END = "2026-08-03 00:58:00"
HC04_MISSING_SEGMENT = "t2-00000000000000A7"
HC04_MISSING_RANGE_START = "2026-08-03 01:04:00"
HC04_MISSING_RANGE_END = "2026-08-03 01:10:00"
HC04_SECONDARY_SEGMENT = "t2-00000000000000A8"
HC04_SECONDARY_RANGE_START = "2026-08-03 01:10:00"
HC04_SECONDARY_RANGE_END = "2026-08-03 01:15:00"
HC04_CONTINUITY_SEGMENT = "t2-00000000000000A6"
HC04_CONTINUITY_RANGE_START = "2026-08-03 00:58:00"
HC04_CONTINUITY_RANGE_END = "2026-08-03 01:04:00"
HC04_SOURCE_ORDERS = 1800
HC04_SOURCE_ORDER_LINES = 3600
HC04_SOURCE_PAYMENTS = 1800
HC04_SOURCE_INVENTORY = 240
HC04_SOURCE_CHECKSUM = 12152520
HC04_RPO_TARGET_SECONDS = 300
HC04_RTO_TARGET_SECONDS = 120


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="hc04_checkout_order_lookup",
            sql=(
                f"SELECT order_id, tenant_id, status, amount FROM {HC04_DB}.{HC04_ORDERS_TABLE} "
                "WHERE order_id IN (17, 271, 983, 1777)"
            ),
            qps=0.85,
            tier="OLTP_READ",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="hc04_merchant_order_rollup",
            sql=(
                f"SELECT tenant_id, status, COUNT(*), SUM(amount) FROM {HC04_DB}.{HC04_ORDERS_TABLE} "
                "WHERE created_at >= '2026-08-01' GROUP BY tenant_id, status "
                "ORDER BY SUM(amount) DESC LIMIT 20"
            ),
            qps=0.34,
            tier="OLAP_ROLLUP",
            application_name="merchant-reporting",
        ),
        WorkloadProfile(
            name="hc04_order_line_reconciliation",
            sql=(
                f"SELECT order_id, COUNT(*), SUM(line_amount) FROM {HC04_DB}.{HC04_ORDER_LINES_TABLE} "
                "WHERE order_id BETWEEN 400 AND 1200 GROUP BY order_id "
                "ORDER BY SUM(line_amount) DESC LIMIT 30"
            ),
            qps=0.28,
            tier="RECONCILIATION",
            application_name="order-reconciliation",
        ),
        WorkloadProfile(
            name="hc04_payment_settlement_probe",
            sql=(
                f"SELECT payment_status, COUNT(*), SUM(amount) FROM {HC04_DB}.{HC04_PAYMENTS_TABLE} "
                "GROUP BY payment_status ORDER BY payment_status"
            ),
            qps=0.32,
            tier="PAYMENT_READ",
            application_name="settlement-worker",
        ),
        WorkloadProfile(
            name="hc04_inventory_snapshot",
            sql=(
                f"SELECT sku_id, available, reserved FROM {HC04_DB}.{HC04_INVENTORY_TABLE} "
                "WHERE sku_id IN (10017, 10171, 10983, 10271)"
            ),
            qps=0.58,
            tier="OLTP_READ",
            application_name="inventory-api",
        ),
        WorkloadProfile(
            name="hc04_backup_catalog_refresh",
            sql=(
                f"SELECT backup_kind, status, COUNT(*) FROM {HC04_DB}.{HC04_BACKUP_TABLE} "
                "GROUP BY backup_kind, status ORDER BY backup_kind, status"
            ),
            qps=0.26,
            tier="BACKUP_MONITOR",
            application_name="backup-dashboard",
        ),
        WorkloadProfile(
            name="hc04_checkpoint_window_probe",
            sql=(
                f"SELECT backup_id, MAX(checkpoint_ts), COUNT(*) FROM {HC04_DB}.{HC04_SEGMENT_TABLE} "
                "GROUP BY backup_id ORDER BY MAX(checkpoint_ts) DESC LIMIT 12"
            ),
            qps=0.24,
            tier="BACKUP_MONITOR",
            application_name="pitr-checkpoint-monitor",
        ),
        WorkloadProfile(
            name="hc04_restore_queue_probe",
            sql=(
                f"SELECT target_cluster, status, COUNT(*) FROM {HC04_DB}.{HC04_DRILL_TABLE} "
                "GROUP BY target_cluster, status ORDER BY target_cluster, status"
            ),
            qps=0.22,
            tier="DR_MONITOR",
            application_name="restore-orchestrator",
        ),
        WorkloadProfile(
            name="hc04_object_store_inventory_scan",
            sql=(
                f"SELECT region, object_status, COUNT(*) FROM {HC04_DB}.{HC04_OBJECT_TABLE} "
                "GROUP BY region, object_status ORDER BY region, object_status"
            ),
            qps=0.18,
            tier="STORAGE_MONITOR",
            application_name="object-storage-audit",
        ),
        WorkloadProfile(
            name="hc04_restore_attempt_poll",
            sql=(
                f"SELECT attempt_id, status, checkpoint_status, checksum_status "
                f"FROM {HC04_DB}.{HC04_ATTEMPT_TABLE} ORDER BY attempt_id DESC LIMIT 8"
            ),
            qps=0.36,
            tier="OPS_PROBE",
            application_name="ops-health-probe",
        ),
        WorkloadProfile(
            name="hc04_live_checkout_event_writer",
            sql=(
                f"INSERT INTO {HC04_DB}.{HC04_LIVE_EVENTS_TABLE} "
                "(event_type, order_id, observed_at, payload) "
                "SELECT 'checkout_retry', 17, NOW(), 'background-runner' "
                "FROM information_schema.tables LIMIT 1"
            ),
            qps=0.42,
            tier="OLTP_WRITE",
            commit=True,
            application_name="checkout-event-writer",
        ),
        WorkloadProfile(
            name="hc04_business_checksum_probe",
            sql=(
                f"SELECT COUNT(*), SUM(order_id) FROM {HC04_DB}.{HC04_ORDERS_TABLE}"
            ),
            qps=0.16,
            tier="AUDIT",
            application_name="business-integrity-audit",
        ),
        WorkloadProfile(
            name="hc04_statement_summary_refresh",
            sql=(
                "SELECT digest, digest_text, exec_count, avg_latency "
                "FROM information_schema.cluster_statements_summary "
                "ORDER BY sum_latency DESC LIMIT 20"
            ),
            qps=0.18,
            tier="MONITORING",
            application_name="topsql-refresh",
        ),
        WorkloadProfile(
            name="hc04_archive_inventory_refresh",
            sql="SELECT object_status, COUNT(*) FROM benchops.hc04_archive_objects GROUP BY object_status",
            qps=0.20,
            tier="STORAGE_MONITOR",
            application_name="archive-cache-refresh",
        ),
        WorkloadProfile(
            name="hc04_restore_dashboard_refresh",
            sql="SELECT source_role, status, COUNT(*) FROM benchops.hc04_restore_drills GROUP BY source_role, status",
            qps=0.16,
            tier="DR_MONITOR",
            application_name="restore-dashboard-refresh",
        ),
    ),
    worker_count=8,
    seed=0x0C04,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=18,
)


_CASE = TidbHealthCheckBackupRecoverabilityForBackupChainRepairScenarioCase(
    case_id="backup_chain_repair_and_restore",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "repaired the selected primary archive object from its authorized immutable replica",
                "reran the approved isolated restore",
            ],
            "verification": [
                "the latest isolated restore reached the requested checkpoint and all four sandbox checks matched",
                "production business truth remained unchanged",
            ],
        },
        "summary": "The approved archive chain was repaired and the isolated recovery contract passed.",
    },
    case_no=0,
    evaluator=TidbHealthCheckBackupRecoverabilityForBackupChainRepairEvaluatorCase,
    title=(
        "Repair a corrupted TiDB backup-chain object and prove the approved isolated restore "
        "reaches the requested checkpoint rather than trusting a green backup job."
    ),
    alert=(
        "[Data Protection Recovery Alert] The approved weekly restore validation for the regional "
        "commerce cluster did not reach its requested checkpoint. The scheduler still reports a "
        "green backup. Determine why the approved restore did not reach its requested checkpoint. Use the "
        "available recovery records and live traffic to identify the affected validation, apply a safe correction "
        "in the isolated validation environment, and verify the four critical business tables. Never restore over production, mutate the "
        "production business tables, or restart a healthy TiDB/TiKV/PD component."
    ),
    initial_state={
        "status": "restore_validation_failed",
        "backup_jobs": "green",
        "business_window": "checkout/payments/inventory/reporting/audit",
        "request_key": HC04_REQUEST_KEY,
    },
    expected_target={
        "restore_status": "success",
        "selected_chain": HC04_SELECTED_BACKUP,
        "restore_sample": HC04_SELECTED_DRILL,
        "checkpoint": "requested checkpoint is complete",
        "critical_tables": "all four isolated restore checks match",
        "safety": "no production restore or business-table mutation",
    },
    background_workload=_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=120,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=10,
        environmental_complexity=0.858231,
        reference_run_ids=(
            "reference-84__tidb_health_check_backup_recoverability__backup_chain_repair_and_restore__mock__r001",
        ),
    ),
    db=HC04_DB,
    request_key=HC04_REQUEST_KEY,
    backup_catalog_table=HC04_BACKUP_TABLE,
    log_segment_table=HC04_SEGMENT_TABLE,
    restore_drill_table=HC04_DRILL_TABLE,
    restore_check_table=HC04_CHECK_TABLE,
    restore_attempt_table=HC04_ATTEMPT_TABLE,
    audit_request_table=HC04_REQUEST_TABLE,
    approval_table=HC04_APPROVAL_TABLE,
    object_inventory_table=HC04_OBJECT_TABLE,
    monitoring_table=HC04_MONITOR_TABLE,
    orders_table=HC04_ORDERS_TABLE,
    order_lines_table=HC04_ORDER_LINES_TABLE,
    payments_table=HC04_PAYMENTS_TABLE,
    inventory_table=HC04_INVENTORY_TABLE,
    live_events_table=HC04_LIVE_EVENTS_TABLE,
    snapshot_orders_table=HC04_SNAPSHOT_ORDERS_TABLE,
    snapshot_order_lines_table=HC04_SNAPSHOT_ORDER_LINES_TABLE,
    snapshot_payments_table=HC04_SNAPSHOT_PAYMENTS_TABLE,
    snapshot_inventory_table=HC04_SNAPSHOT_INVENTORY_TABLE,
    sandbox_orders_table=HC04_SANDBOX_ORDERS_TABLE,
    sandbox_order_lines_table=HC04_SANDBOX_ORDER_LINES_TABLE,
    sandbox_payments_table=HC04_SANDBOX_PAYMENTS_TABLE,
    sandbox_inventory_table=HC04_SANDBOX_INVENTORY_TABLE,
    selected_backup_id=HC04_SELECTED_BACKUP,
    selected_drill_id=HC04_SELECTED_DRILL,
    requested_target=HC04_REQUESTED_TARGET,
    latest_recoverable=HC04_LATEST_RECOVERABLE,
    front_segment=HC04_FRONT_SEGMENT,
    front_range_start=HC04_FRONT_RANGE_START,
    front_range_end=HC04_FRONT_RANGE_END,
    early_segment=HC04_EARLY_SEGMENT,
    early_range_start=HC04_EARLY_RANGE_START,
    early_range_end=HC04_EARLY_RANGE_END,
    late_segment=HC04_LATE_SEGMENT,
    late_range_start=HC04_LATE_RANGE_START,
    late_range_end=HC04_LATE_RANGE_END,
    missing_segment=HC04_MISSING_SEGMENT,
    missing_range_start=HC04_MISSING_RANGE_START,
    missing_range_end=HC04_MISSING_RANGE_END,
    secondary_segment=HC04_SECONDARY_SEGMENT,
    secondary_range_start=HC04_SECONDARY_RANGE_START,
    secondary_range_end=HC04_SECONDARY_RANGE_END,
    continuity_segment=HC04_CONTINUITY_SEGMENT,
    continuity_range_start=HC04_CONTINUITY_RANGE_START,
    continuity_range_end=HC04_CONTINUITY_RANGE_END,
    source_orders=HC04_SOURCE_ORDERS,
    source_order_lines=HC04_SOURCE_ORDER_LINES,
    source_payments=HC04_SOURCE_PAYMENTS,
    source_inventory=HC04_SOURCE_INVENTORY,
    source_checksum=HC04_SOURCE_CHECKSUM,
    rpo_target_seconds=HC04_RPO_TARGET_SECONDS,
    rto_target_seconds=HC04_RTO_TARGET_SECONDS,
    continuity_only=False,
)


_NEW_CASE = replace(
    _CASE,
    case_id="single_segment_continuity_repair",
    case_no=1,
    evaluator=TidbHealthCheckBackupRecoverabilityForSingleSegmentContinuityEvaluatorCase,
    title="Repair one readable but unreplicated TiDB backup segment and prove isolated restore continuity.",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "a single archive continuity gap blocks the requested restore even though the segment bytes are readable",
                    "entity": "single_segment_continuity_repair",
                    "evidence": ["present=0, replica_status=NOT_REPLICATED, and usable_for_restore=0"],
                }
            ]
        },
        "outcome": {
            "changes": ["copied the approved archive source for the continuity segment into the isolated target"],
            "verification": ["the isolated restore and all four sandbox business checks matched without changing production"],
        },
        "summary": "The single archive continuity gap was repaired from its authorized source and the isolated restore passed.",
    },
    alert=(
        "数据保护例行恢复抽样发现当前 restore chain 没有跨过请求 checkpoint。请把当前请求、批准的 archive source、"
        "segment continuity 和 isolated restore 记录关联起来。区分 readable-but-unreplicated 与 checksum failure，"
        "只在隔离目标修复单个 continuity gap，禁止覆盖生产表或修改业务数据。"
    ),
    initial_state={
        "status": "restore_validation_failed",
        "request_key": "hc04-weekly-recoverability-20260804",
        "fault_shape": "one readable but unreplicated segment",
    },
    expected_target={
        "restore_status": "success",
        "continuity_segment": "replicated_and_usable",
        "critical_tables": "all four isolated restore checks match",
        "production": "unchanged",
    },
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.222222,
        reference_run_ids=(
            "tidb-reference-12__"
            "tidb_health_check_backup_recoverability__"
            "single_segment_continuity_repair__mock__r001",
        ),
    ),
    continuity_only=True,
    focused_fixture=True,
)


class TidbHealthCheckBackupRecoverabilityScenario(TiDBScenario):
    scenario_id = "tidb_health_check_backup_recoverability"
    description = (
        "Routine TiDB backup recoverability health check with isolated restore evidence, "
        "checkpoint validation, and noisy commerce workload."
    )
    cases = (_CASE, _NEW_CASE)

    def build_fault_plan(
        self,
        case: TidbHealthCheckBackupRecoverabilityCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbHealthCheckBackupRecoverabilityInjector,
                config={
                    "db": case.db,
                    "request_key": case.request_key,
                    "backup_catalog_table": case.backup_catalog_table,
                    "log_segment_table": case.log_segment_table,
                    "restore_drill_table": case.restore_drill_table,
                    "restore_check_table": case.restore_check_table,
                    "restore_attempt_table": case.restore_attempt_table,
                    "audit_request_table": case.audit_request_table,
                    "approval_table": case.approval_table,
                    "object_inventory_table": case.object_inventory_table,
                    "monitoring_table": case.monitoring_table,
                    "orders_table": case.orders_table,
                    "order_lines_table": case.order_lines_table,
                    "payments_table": case.payments_table,
                    "inventory_table": case.inventory_table,
                    "live_events_table": case.live_events_table,
                    "snapshot_orders_table": case.snapshot_orders_table,
                    "snapshot_order_lines_table": case.snapshot_order_lines_table,
                    "snapshot_payments_table": case.snapshot_payments_table,
                    "snapshot_inventory_table": case.snapshot_inventory_table,
                    "sandbox_orders_table": case.sandbox_orders_table,
                    "sandbox_order_lines_table": case.sandbox_order_lines_table,
                    "sandbox_payments_table": case.sandbox_payments_table,
                    "sandbox_inventory_table": case.sandbox_inventory_table,
                    "selected_backup_id": case.selected_backup_id,
                    "selected_drill_id": case.selected_drill_id,
                    "requested_target": case.requested_target,
                    "latest_recoverable": case.latest_recoverable,
                    "front_segment": case.front_segment,
                    "front_range_start": case.front_range_start,
                    "front_range_end": case.front_range_end,
                    "early_segment": case.early_segment,
                    "early_range_start": case.early_range_start,
                    "early_range_end": case.early_range_end,
                    "late_segment": case.late_segment,
                    "late_range_start": case.late_range_start,
                    "late_range_end": case.late_range_end,
                    "missing_segment": case.missing_segment,
                    "missing_range_start": case.missing_range_start,
                    "missing_range_end": case.missing_range_end,
                    "secondary_segment": case.secondary_segment,
                    "secondary_range_start": case.secondary_range_start,
                    "secondary_range_end": case.secondary_range_end,
                    "continuity_segment": case.continuity_segment,
                    "continuity_range_start": case.continuity_range_start,
                    "continuity_range_end": case.continuity_range_end,
                    "source_orders": case.source_orders,
                    "source_order_lines": case.source_order_lines,
                    "source_payments": case.source_payments,
                    "source_inventory": case.source_inventory,
                    "source_checksum": case.source_checksum,
                    "rpo_target_seconds": case.rpo_target_seconds,
                    "rto_target_seconds": case.rto_target_seconds,
                    "continuity_only": case.continuity_only,
                    "focused_fixture": case.focused_fixture,
                },
            ),
        )



_HC04_TARGETED_NOISE_ROWS = 96
_HC04_APPROVAL_ORDER_STEP = 37


class TidbHealthCheckBackupRecoverabilityInjector(BaseFaultInjector):
    """Build a stateful archive repair and isolated restore validation surface."""

    def __init__(self):
        self._artifact_root: Path | None = None
        self._runtime_registered = False
        self._archive_hashes: dict[int, str] = {}

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.run_id)
        env = context.env
        require_sql_success(env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"), "clear HC04 schema")
        require_sql_success(env.execute_sql(f"CREATE DATABASE {self.db}"), "create HC04 schema")
        self._create_business_tables(env)
        self._load_business_rows(env)
        self._create_audit_tables(env)
        self._create_restore_snapshots(env)
        self._create_archive_artifacts()
        self._load_backup_catalog(env)
        self._load_log_segments(env)
        self._load_restore_drills(env)
        self._load_restore_table_checks(env)
        self._load_operational_noise(env)
        self._configure_environment_runtime(env)
        self._verify_persistent_state(env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.run_id)
        self._configure_environment_runtime(context.env)
        self._verify_persistent_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config, context.run_id)
        self._verify_persistent_state(context.env)
        return {
            "hc04_selected_backup_id": self.selected_backup_id,
            "hc04_selected_drill_id": self.selected_drill_id,
            "hc04_business_source_checksum": self.source_checksum,
            "hc04_archive_faults": (
                self.front_segment,
                self.early_segment,
                self.late_segment,
                self.continuity_segment,
                self.missing_segment,
                self.secondary_segment,
            ),
            "hc04_reference_evidence_units": {
                "audit_request_join": {"causal": 6, "noise": 192},
                "backup_catalog": {"causal": 1, "noise": 7},
                "log_segments": {"causal": 6, "noise": 97},
                "restore_drills": {"causal": 1, "noise": 15},
                "archive_objects": {"causal": 12, "noise": 106},
                "monitoring_events": {"causal": 4, "noise": 76},
                "business_workload_profiles": {"causal": 6, "noise": 9},
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        return None

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.run_id)
        if self._runtime_registered:
            context.env.clear_hc04_restore_runtime()
            self._runtime_registered = False
        require_sql_success(context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"), "drop HC04 schema")
        if self._artifact_root is not None and self._artifact_root.exists():
            shutil.rmtree(self._artifact_root)
        self._artifact_root = None

    def _configure(self, config: Mapping[str, object], run_id: str) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.request_key = str(config["request_key"])
        self.backup_catalog_table = validate_sql_identifier(str(config["backup_catalog_table"]), "backup_catalog_table")
        self.log_segment_table = validate_sql_identifier(str(config["log_segment_table"]), "log_segment_table")
        self.restore_drill_table = validate_sql_identifier(str(config["restore_drill_table"]), "restore_drill_table")
        self.restore_check_table = validate_sql_identifier(str(config["restore_check_table"]), "restore_check_table")
        self.restore_attempt_table = validate_sql_identifier(str(config["restore_attempt_table"]), "restore_attempt_table")
        self.audit_request_table = validate_sql_identifier(str(config["audit_request_table"]), "audit_request_table")
        self.approval_table = validate_sql_identifier(str(config["approval_table"]), "approval_table")
        self.object_inventory_table = validate_sql_identifier(str(config["object_inventory_table"]), "object_inventory_table")
        self.monitoring_table = validate_sql_identifier(str(config["monitoring_table"]), "monitoring_table")
        self.orders_table = validate_sql_identifier(str(config["orders_table"]), "orders_table")
        self.order_lines_table = validate_sql_identifier(str(config["order_lines_table"]), "order_lines_table")
        self.payments_table = validate_sql_identifier(str(config["payments_table"]), "payments_table")
        self.inventory_table = validate_sql_identifier(str(config["inventory_table"]), "inventory_table")
        self.live_events_table = validate_sql_identifier(str(config["live_events_table"]), "live_events_table")
        self.snapshot_orders_table = validate_sql_identifier(str(config["snapshot_orders_table"]), "snapshot_orders_table")
        self.snapshot_order_lines_table = validate_sql_identifier(str(config["snapshot_order_lines_table"]), "snapshot_order_lines_table")
        self.snapshot_payments_table = validate_sql_identifier(str(config["snapshot_payments_table"]), "snapshot_payments_table")
        self.snapshot_inventory_table = validate_sql_identifier(str(config["snapshot_inventory_table"]), "snapshot_inventory_table")
        self.sandbox_orders_table = validate_sql_identifier(str(config["sandbox_orders_table"]), "sandbox_orders_table")
        self.sandbox_order_lines_table = validate_sql_identifier(str(config["sandbox_order_lines_table"]), "sandbox_order_lines_table")
        self.sandbox_payments_table = validate_sql_identifier(str(config["sandbox_payments_table"]), "sandbox_payments_table")
        self.sandbox_inventory_table = validate_sql_identifier(str(config["sandbox_inventory_table"]), "sandbox_inventory_table")
        self.selected_backup_id = str(config["selected_backup_id"])
        self.selected_drill_id = str(config["selected_drill_id"])
        self.requested_target = str(config["requested_target"])
        self.latest_recoverable = str(config["latest_recoverable"])
        self.front_segment = str(config["front_segment"])
        self.front_range_start = str(config["front_range_start"])
        self.front_range_end = str(config["front_range_end"])
        self.early_segment = str(config["early_segment"])
        self.early_range_start = str(config["early_range_start"])
        self.early_range_end = str(config["early_range_end"])
        self.late_segment = str(config["late_segment"])
        self.late_range_start = str(config["late_range_start"])
        self.late_range_end = str(config["late_range_end"])
        self.missing_segment = str(config["missing_segment"])
        self.missing_range_start = str(config["missing_range_start"])
        self.missing_range_end = str(config["missing_range_end"])
        self.secondary_segment = str(config["secondary_segment"])
        self.secondary_range_start = str(config["secondary_range_start"])
        self.secondary_range_end = str(config["secondary_range_end"])
        self.continuity_segment = str(config["continuity_segment"])
        self.continuity_range_start = str(config["continuity_range_start"])
        self.continuity_range_end = str(config["continuity_range_end"])
        self.source_orders = int(config["source_orders"])
        self.source_order_lines = int(config["source_order_lines"])
        self.source_payments = int(config["source_payments"])
        self.source_inventory = int(config["source_inventory"])
        self.source_checksum = int(config["source_checksum"])
        self.rpo_target_seconds = int(config["rpo_target_seconds"])
        self.rto_target_seconds = int(config["rto_target_seconds"])
        self.continuity_only = bool(config["continuity_only"])
        self.focused_fixture = bool(config["focused_fixture"])
        self.targeted_noise_rows = 4 if self.focused_fixture else _HC04_TARGETED_NOISE_ROWS
        artifact_id = hashlib.sha256(run_id.encode()).hexdigest()[:16]
        self._artifact_root = Path(tempfile.gettempdir()) / f"aiopsbench-hc04-{artifact_id}"

    def _create_business_tables(self, env) -> None:
        statements = (
            f"CREATE TABLE {self.db}.{self.orders_table} ("
            "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, status VARCHAR(20) NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, created_at DATETIME NOT NULL, payload VARCHAR(96) NOT NULL, "
            "KEY idx_tenant_status (tenant_id, status), KEY idx_created_at (created_at)"
            ")",
            f"CREATE TABLE {self.db}.{self.order_lines_table} ("
            "line_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, sku_id BIGINT NOT NULL, "
            "quantity INT NOT NULL, line_amount DECIMAL(12,2) NOT NULL, created_at DATETIME NOT NULL, "
            "KEY idx_order (order_id), KEY idx_sku (sku_id)"
            ")",
            f"CREATE TABLE {self.db}.{self.payments_table} ("
            "payment_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, amount DECIMAL(12,2) NOT NULL, "
            "payment_status VARCHAR(20) NOT NULL, paid_at DATETIME NOT NULL, KEY idx_order (order_id)"
            ")",
            f"CREATE TABLE {self.db}.{self.inventory_table} ("
            "sku_id BIGINT PRIMARY KEY, available INT NOT NULL, reserved INT NOT NULL, "
            "warehouse_id INT NOT NULL, updated_at DATETIME NOT NULL"
            ")",
            f"CREATE TABLE {self.db}.{self.live_events_table} ("
            "event_id BIGINT AUTO_INCREMENT PRIMARY KEY, event_type VARCHAR(32) NOT NULL, "
            "order_id BIGINT NOT NULL, observed_at DATETIME NOT NULL, payload VARCHAR(64) NOT NULL"
            ")",
        )
        for statement in statements:
            require_sql_success(env.execute_sql(statement), "create HC04 business table")

    def _insert_rows(self, env, table: str, columns: tuple[str, ...], rows: list[tuple]) -> None:
        values = (
            "(" + ",".join(sql_literal(value) for value in row) + ")"
            for row in rows
        )
        run_sql_batches(
            env.execute_sql,
            f"INSERT INTO {self.db}.{table} ({','.join(columns)}) VALUES ",
            values,
            180,
            f"load HC04 rows into {table}",
        )

    def _load_business_rows(self, env) -> None:
        orders = [
            (
                order_id,
                order_id % 37,
                ("paid", "packed", "shipped", "pending")[order_id % 4],
                f"{100 + order_id % 991}.00",
                f"2026-08-{1 + order_id % 3:02d} 00:00:00",
                f"order-payload-{order_id:05d}",
            )
            for order_id in range(1, self.source_orders + 1)
        ]
        order_lines = [
            (
                line_id,
                1 + (line_id - 1) % self.source_orders,
                10000 + line_id % 241,
                1 + line_id % 4,
                f"{25 + line_id % 300}.00",
                f"2026-08-{1 + line_id % 3:02d} 00:00:00",
            )
            for line_id in range(1, self.source_order_lines + 1)
        ]
        payments = [
            (
                payment_id,
                payment_id,
                f"{100 + payment_id % 991}.00",
                ("authorized", "captured", "settled")[payment_id % 3],
                f"2026-08-{1 + payment_id % 3:02d} 00:00:00",
            )
            for payment_id in range(1, self.source_payments + 1)
        ]
        inventory = [
            (10000 + sku, 100 + sku % 700, sku % 23, 1 + sku % 8, "2026-08-03 00:00:00")
            for sku in range(1, self.source_inventory + 1)
        ]
        self._insert_rows(
            env,
            self.orders_table,
            ("order_id", "tenant_id", "status", "amount", "created_at", "payload"),
            orders,
        )
        self._insert_rows(
            env,
            self.order_lines_table,
            ("line_id", "order_id", "sku_id", "quantity", "line_amount", "created_at"),
            order_lines,
        )
        self._insert_rows(
            env,
            self.payments_table,
            ("payment_id", "order_id", "amount", "payment_status", "paid_at"),
            payments,
        )
        self._insert_rows(
            env,
            self.inventory_table,
            ("sku_id", "available", "reserved", "warehouse_id", "updated_at"),
            inventory,
        )
        self._insert_rows(
            env,
            self.live_events_table,
            ("event_type", "order_id", "observed_at", "payload"),
            [("seed", 17, "2026-08-03 00:00:00", "seed-event")],
        )

    def _create_audit_tables(self, env) -> None:
        definitions = (
            f"CREATE TABLE {self.db}.{self.backup_catalog_table} ("
            "backup_id VARCHAR(96) PRIMARY KEY, backup_kind VARCHAR(24), source_role VARCHAR(32), "
            "status VARCHAR(32), metadata_status VARCHAR(32), storage_uri VARCHAR(255), timeline INT, "
            "backup_end_ts DATETIME, checkpoint_ts DATETIME, requested_target_ts DATETIME, "
            "latest_recoverable_ts DATETIME, rpo_target_seconds INT, rto_target_seconds INT, "
            "restore_duration_seconds INT, metadata_checksum VARCHAR(96), business_checksum BIGINT, note VARCHAR(512)"
            ")",
            f"CREATE TABLE {self.db}.{self.log_segment_table} ("
            "segment_id BIGINT PRIMARY KEY, backup_id VARCHAR(96), timeline INT, segment_name VARCHAR(96), "
            "segment_start_ts DATETIME, segment_end_ts DATETIME, checkpoint_ts DATETIME, present TINYINT, "
            "checksum_status VARCHAR(32), object_status VARCHAR(48), replica_status VARCHAR(48), "
            "usable_for_restore TINYINT, note VARCHAR(512)"
            ")",
            f"CREATE TABLE {self.db}.{self.restore_drill_table} ("
            "drill_id VARCHAR(96) PRIMARY KEY, backup_id VARCHAR(96), target_cluster VARCHAR(64), "
            "source_role VARCHAR(32), target_ts DATETIME, status VARCHAR(32), isolated TINYINT, "
            "metadata_status VARCHAR(32), checkpoint_status VARCHAR(32), checksum_status VARCHAR(32), "
            "restore_duration_seconds INT, business_crc_status VARCHAR(32), source_rows INT, restored_rows INT, "
            "failure_class VARCHAR(96), log_excerpt VARCHAR(512)"
            ")",
            f"CREATE TABLE {self.db}.{self.restore_check_table} ("
            "drill_id VARCHAR(96), table_name VARCHAR(96), source_rows INT, restored_rows INT, "
            "source_checksum BIGINT, restored_checksum BIGINT, checksum_status VARCHAR(32), critical TINYINT, "
            "PRIMARY KEY (drill_id, table_name)"
            ")",
            f"CREATE TABLE {self.db}.{self.restore_attempt_table} ("
            "attempt_id VARCHAR(128) PRIMARY KEY, drill_id VARCHAR(96), backup_id VARCHAR(96), "
            "status VARCHAR(32), isolated TINYINT, checkpoint_status VARCHAR(32), checksum_status VARCHAR(32), "
            "observed_rpo_seconds INT, observed_rto_seconds INT, restore_duration_seconds INT, "
            "failure_class VARCHAR(128), log_excerpt VARCHAR(768), attempted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
            ")",
            f"CREATE TABLE {self.db}.{self.audit_request_table} ("
            "request_key VARCHAR(96) PRIMARY KEY, business_service VARCHAR(64), selected_backup_id VARCHAR(96), "
            "selected_drill_id VARCHAR(96), target_ts DATETIME, rpo_target_seconds INT, rto_target_seconds INT, "
            "authorized_source_role VARCHAR(32), request_reason VARCHAR(512)"
            ")",
            f"CREATE TABLE {self.db}.{self.approval_table} ("
            "approval_id BIGINT PRIMARY KEY, request_key VARCHAR(96), selected_backup_id VARCHAR(96), "
            "source_object_id BIGINT, source_segment VARCHAR(96), source_role VARCHAR(32), restore_mode VARCHAR(32), approval_state VARCHAR(32), approved_at DATETIME, "
            "approved_by VARCHAR(64), approval_notes VARCHAR(512)"
            ")",
            f"CREATE TABLE {self.db}.{self.object_inventory_table} ("
            "object_id BIGINT PRIMARY KEY, backup_id VARCHAR(96), segment_name VARCHAR(96), region VARCHAR(32), "
            "object_status VARCHAR(48), readable TINYINT, replicated TINYINT, legal_hold TINYINT, "
            "checksum VARCHAR(96), note VARCHAR(512)"
            ")",
            f"CREATE TABLE {self.db}.{self.monitoring_table} ("
            "event_id BIGINT PRIMARY KEY, event_time DATETIME, severity VARCHAR(16), source VARCHAR(32), "
            "related_backup_id VARCHAR(96), message VARCHAR(512)"
            ")",
        )
        for statement in definitions:
            require_sql_success(env.execute_sql(statement), "create HC04 audit table")

    def _create_restore_snapshots(self, env) -> None:
        tables = (
            (self.orders_table, self.snapshot_orders_table, self.sandbox_orders_table),
            (self.order_lines_table, self.snapshot_order_lines_table, self.sandbox_order_lines_table),
            (self.payments_table, self.snapshot_payments_table, self.sandbox_payments_table),
            (self.inventory_table, self.snapshot_inventory_table, self.sandbox_inventory_table),
        )
        for source_table, snapshot_table, sandbox_table in tables:
            require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {self.db}.{snapshot_table} LIKE {self.db}.{source_table}"
                ),
                f"create HC04 immutable snapshot {snapshot_table}",
            )
            require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {self.db}.{snapshot_table} SELECT * FROM {self.db}.{source_table}"
                ),
                f"populate HC04 immutable snapshot {snapshot_table}",
            )
            require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {self.db}.{sandbox_table} LIKE {self.db}.{source_table}"
                ),
                f"create HC04 isolated restore sandbox {sandbox_table}",
            )

    def _create_archive_artifacts(self) -> None:
        if self._artifact_root is None:
            raise RuntimeError("HC04 archive artifact root is not configured")
        if self._artifact_root.exists():
            shutil.rmtree(self._artifact_root)
        object_paths = {
            object_id: self._artifact_root / f"object-{object_id}"
            for object_id in range(1, 23)
        }
        for path in object_paths.values():
            path.mkdir(parents=True)
        self._object_segments = {
            1: self.missing_segment,
            2: self.missing_segment,
            3: self.missing_segment,
            4: self.missing_segment,
            5: self.secondary_segment,
            6: self.secondary_segment,
            7: self.secondary_segment,
            8: self.secondary_segment,
            9: self.continuity_segment,
            10: self.continuity_segment,
            11: self.early_segment,
            12: self.early_segment,
            13: self.early_segment,
            14: self.early_segment,
            15: self.late_segment,
            16: self.late_segment,
            17: self.late_segment,
            18: self.late_segment,
            19: self.front_segment,
            20: self.front_segment,
            21: self.front_segment,
            22: self.front_segment,
        }
        payloads = {
            self.front_segment: (
                f"backup={self.selected_backup_id}\n"
                f"segment={self.front_segment}\n"
                f"range={self.front_range_start}/{self.front_range_end}\n"
                "checkpoint=complete\n"
            ).encode(),
            self.early_segment: (
                f"backup={self.selected_backup_id}\n"
                f"segment={self.early_segment}\n"
                f"range={self.early_range_start}/{self.early_range_end}\n"
                "checkpoint=complete\n"
            ).encode(),
            self.late_segment: (
                f"backup={self.selected_backup_id}\n"
                f"segment={self.late_segment}\n"
                f"range={self.late_range_start}/{self.late_range_end}\n"
                "checkpoint=complete\n"
            ).encode(),
            self.missing_segment: (
                f"backup={self.selected_backup_id}\n"
                f"segment={self.missing_segment}\n"
                f"range={self.missing_range_start}/{self.missing_range_end}\n"
                "checkpoint=complete\n"
            ).encode(),
            self.secondary_segment: (
                f"backup={self.selected_backup_id}\n"
                f"segment={self.secondary_segment}\n"
                f"range={self.secondary_range_start}/{self.secondary_range_end}\n"
                "checkpoint=complete\n"
            ).encode(),
            self.continuity_segment: (
                f"backup={self.selected_backup_id}\n"
                f"segment={self.continuity_segment}\n"
                f"range={self.continuity_range_start}/{self.continuity_range_end}\n"
                "checkpoint=complete\n"
            ).encode(),
        }
        paths = {
            object_id: object_paths[object_id] / segment
            for object_id, segment in self._object_segments.items()
        }
        corrupt_objects = set() if self.continuity_only else {1, 5, 13, 15, 19}
        reporting_objects = {3, 7, 11, 16, 20}
        for object_id, path in paths.items():
            payload = payloads[self._object_segments[object_id]]
            if object_id in corrupt_objects:
                payload = payload.replace(b"checkpoint=complete", b"checkpoint=corrupt")
            elif object_id in reporting_objects:
                payload = payload.replace(b"checkpoint=complete", b"checkpoint=reporting")
            path.write_bytes(payload)
        self._archive_hashes = {
            object_id: hashlib.sha256(path.read_bytes()).hexdigest()
            for object_id, path in paths.items()
        }

    def _configure_environment_runtime(self, env) -> None:
        if self._artifact_root is None:
            raise RuntimeError("HC04 archive artifact root is not configured")
        if self._runtime_registered:
            return
        paths = {
            object_id: self._artifact_root / f"object-{object_id}" / self._object_segments[object_id]
            for object_id in self._object_segments
        }
        if not all(path.is_file() for path in paths.values()):
            raise RuntimeError(
                "HC04 archive artifacts are incomplete: "
                f"root={str(self._artifact_root)!r}, paths={[str(path) for path in paths.values()]!r}"
            )
        self._archive_hashes = {
            object_id: hashlib.sha256(path.read_bytes()).hexdigest()
            for object_id, path in paths.items()
        }
        env.configure_hc04_restore_runtime({
            "db": self.db,
            "request_key": self.request_key,
            "backup_catalog_table": self.backup_catalog_table,
            "log_segment_table": self.log_segment_table,
            "restore_drill_table": self.restore_drill_table,
            "restore_check_table": self.restore_check_table,
            "restore_attempt_table": self.restore_attempt_table,
            "approval_table": self.approval_table,
            "object_inventory_table": self.object_inventory_table,
            "orders_table": self.orders_table,
            "order_lines_table": self.order_lines_table,
            "payments_table": self.payments_table,
            "inventory_table": self.inventory_table,
            "snapshot_orders_table": self.snapshot_orders_table,
            "snapshot_order_lines_table": self.snapshot_order_lines_table,
            "snapshot_payments_table": self.snapshot_payments_table,
            "snapshot_inventory_table": self.snapshot_inventory_table,
            "sandbox_orders_table": self.sandbox_orders_table,
            "sandbox_order_lines_table": self.sandbox_order_lines_table,
            "sandbox_payments_table": self.sandbox_payments_table,
            "sandbox_inventory_table": self.sandbox_inventory_table,
            "selected_backup_id": self.selected_backup_id,
            "selected_drill_id": self.selected_drill_id,
            "fault_segments": (
                self.front_segment,
                self.early_segment,
                self.late_segment,
                self.continuity_segment,
                self.missing_segment,
                self.secondary_segment,
            ),
            "requested_target": self.requested_target,
            "rpo_target_seconds": self.rpo_target_seconds,
            "rto_target_seconds": self.rto_target_seconds,
            "primary_object_paths": {
                self.front_segment: str(paths[19]),
                self.early_segment: str(paths[13]),
                self.late_segment: str(paths[15]),
                self.missing_segment: str(paths[1]),
                self.secondary_segment: str(paths[5]),
                self.continuity_segment: str(paths[9]),
            },
            "primary_object_ids": {
                self.front_segment: 19,
                self.early_segment: 13,
                self.late_segment: 15,
                self.missing_segment: 1,
                self.secondary_segment: 5,
                self.continuity_segment: 9,
            },
            "object_files": {object_id: str(path) for object_id, path in paths.items()},
        })
        self._runtime_registered = True

    def _load_backup_catalog(self, env) -> None:
        rows = [
            ("hc04-full-20260801-t1", "full", "primary", "SUCCESS", "COMPLETE", "s3://prod/t1/full-0801", 1, "2026-08-01 01:02:00", "2026-08-01 01:02:00", "2026-08-01 01:15:00", "2026-08-01 01:15:00", 300, 120, 88, "meta-t1-ok", self.source_checksum, "prior successful full backup"),
            ("hc04-full-20260802-t1", "full", "primary", "SUCCESS", "COMPLETE", "s3://prod/t1/full-0802", 1, "2026-08-02 01:03:00", "2026-08-02 01:03:00", "2026-08-02 01:15:00", "2026-08-02 01:15:00", 300, 120, 94, "meta-t1-healthy", self.source_checksum, "retention comparison"),
            (self.selected_backup_id, "full", "primary", "SUCCESS", "COMPLETE", "s3://prod/t2/full-0803", 2, "2026-08-03 01:01:00", self.latest_recoverable, self.requested_target, self.latest_recoverable, 300, 120, 142, "meta-t2-green", self.source_checksum, "green scheduler result; restore proof is separate"),
            ("hc04-full-20260803-t2-standby", "full", "standby_seed", "SUCCESS", "COMPLETE", "s3://standby/t2/full-0803", 2, "2026-08-03 01:02:00", self.requested_target, self.requested_target, self.requested_target, 300, 120, 101, "meta-standby-ok", self.source_checksum, "same-day smoke-only standby seed"),
            ("hc04-full-20260803-t2-reporting", "full", "reporting_clone", "SUCCESS", "COMPLETE", "s3://reporting/t2/full-0803", 2, "2026-08-03 01:03:00", self.requested_target, self.requested_target, self.requested_target, 300, 120, 110, "meta-reporting-ok", self.source_checksum - 17, "reporting clone is not an approved source"),
            ("hc04-incremental-20260803-t2", "incremental", "primary", "SUCCESS", "COMPLETE", "s3://prod/t2/inc-0803", 2, "2026-08-03 03:00:00", "2026-08-03 03:00:00", "2026-08-03 03:10:00", "2026-08-03 03:00:00", 300, 120, 43, "meta-inc-ok", self.source_checksum, "later increment outside requested window"),
            ("hc04-full-20260725-t1", "full", "primary", "SUCCESS", "COMPLETE", "s3://prod/t1/full-0725", 1, "2026-07-25 01:02:00", "2026-07-25 01:02:00", "2026-07-25 01:15:00", "2026-07-25 01:15:00", 300, 120, 98, "meta-old-ok", self.source_checksum, "historical successful drill"),
            ("hc04-full-20260803-t2-corrupt", "full", "primary", "SUCCESS", "CHECKSUM_WARN", "s3://prod/t2/full-0803-retry", 2, "2026-08-03 01:05:00", "2026-08-03 01:05:00", self.requested_target, "2026-08-03 01:05:00", 300, 120, 155, "meta-retry-warn", self.source_checksum - 3, "failed retry artifact"),
        ]
        if self.focused_fixture:
            rows = [
                row for row in rows
                if row[0] in {
                    self.selected_backup_id,
                    "hc04-full-20260803-t2-standby",
                    "hc04-full-20260803-t2-reporting",
                    "hc04-incremental-20260803-t2",
                    "hc04-full-20260803-t2-corrupt",
                }
            ]
        self._insert_rows(
            env,
            self.backup_catalog_table,
            ("backup_id", "backup_kind", "source_role", "status", "metadata_status", "storage_uri", "timeline", "backup_end_ts", "checkpoint_ts", "requested_target_ts", "latest_recoverable_ts", "rpo_target_seconds", "rto_target_seconds", "restore_duration_seconds", "metadata_checksum", "business_checksum", "note"),
            rows,
        )
        self._insert_rows(
            env,
            self.audit_request_table,
            ("request_key", "business_service", "selected_backup_id", "selected_drill_id", "target_ts", "rpo_target_seconds", "rto_target_seconds", "authorized_source_role", "request_reason"),
            [(self.request_key, "checkout-payments-inventory", self.selected_backup_id, self.selected_drill_id, self.requested_target, 300, 120, "primary", "weekly isolated restore sample for the checkout, payments, and inventory service")],
        )

    def _load_log_segments(self, env) -> None:
        rows = []
        segment_id = 1
        for index in range(1, self.targeted_noise_rows + 1):
            hour = index % 24
            rows.append((
                segment_id,
                self.selected_backup_id,
                2,
                f"t2-00000000000000B{index:02X}",
                f"2026-08-03 {hour:02d}:00:00",
                f"2026-08-03 {hour:02d}:05:00",
                f"2026-08-03 {hour:02d}:05:00",
                1,
                "OK",
                "READABLE",
                "REPLICATED",
                1,
                "selected segment inventory row",
            ))
            segment_id += 1
        peer_state = ("OK", "READABLE", "REPLICATED", 1) if self.continuity_only else (
            "CORRUPT", "READABLE_BUT_INVALID", "REPLICATED", 0
        )
        target_specs = (
            (*((self.front_segment, self.front_range_start, self.front_range_end, self.front_range_end, 1) + peer_state), "healthy selected peer" if self.continuity_only else "selected segment requires archive validation"),
            (*((self.early_segment, self.early_range_start, self.early_range_end, self.early_range_end, 1) + peer_state), "healthy selected peer" if self.continuity_only else "selected segment requires archive validation"),
            (*((self.late_segment, self.late_range_start, self.late_range_end, self.late_range_end, 1) + peer_state), "healthy selected peer" if self.continuity_only else "selected segment requires archive validation"),
            (self.continuity_segment, self.continuity_range_start, self.continuity_range_end, self.continuity_range_start, 0, "OK", "READABLE", "NOT_REPLICATED", 0, "selected continuity gap"),
            (*((self.missing_segment, self.missing_range_start, self.missing_range_end, self.latest_recoverable, 1) + peer_state), "healthy selected peer" if self.continuity_only else "selected segment requires archive validation"),
            (*((self.secondary_segment, self.secondary_range_start, self.secondary_range_end, self.latest_recoverable, 1) + peer_state), "healthy selected peer" if self.continuity_only else "selected segment requires archive validation"),
            ("t2-00000000000000A9", "2026-08-03 01:15:00", "2026-08-03 01:30:00", "2026-08-03 01:30:00", 1, "OK", "READABLE", "REPLICATED", 1, "segment outside requested restore window"),
        )
        for name, start, end, checkpoint, present, checksum, object_status, replica, usable, note in target_specs:
            rows.append((segment_id, self.selected_backup_id, 2, name, start, end, checkpoint, present, checksum, object_status, replica, usable, note))
            segment_id += 1
        if not self.focused_fixture:
            for index in range(1, 173):
                backup_id = ("hc04-full-20260801-t1", "hc04-full-20260802-t1", "hc04-full-20260725-t1", "hc04-full-20260803-t2-standby")[index % 4]
                name = f"{'t2' if 't2' in backup_id else 't1'}-00000000000000B{index:02X}"
                hour = 2 + index % 12
                rows.append((segment_id, backup_id, 1 if "t1" in backup_id else 2, name, f"2026-08-{1 + index % 3:02d} {hour:02d}:00:00", f"2026-08-{1 + index % 3:02d} {hour:02d}:05:00", f"2026-08-{1 + index % 3:02d} {hour:02d}:05:00", 1, "OK", "READABLE", "REPLICATED", 1, "archive segment inventory row"))
                segment_id += 1
        self._insert_rows(
            env,
            self.log_segment_table,
            ("segment_id", "backup_id", "timeline", "segment_name", "segment_start_ts", "segment_end_ts", "checkpoint_ts", "present", "checksum_status", "object_status", "replica_status", "usable_for_restore", "note"),
            rows,
        )

    def _load_restore_drills(self, env) -> None:
        rows = [
            (self.selected_drill_id, self.selected_backup_id, "restore-sandbox-hc04", "primary", self.requested_target, "NOT_RUN", 1, "COMPLETE", "NOT_RUN", "NOT_RUN", 0, "NOT_VERIFIED", 0, 0, "NOT_RUN", "the selected isolated restore must be executed by the agent"),
            ("hc04-drill-standby-smoke", "hc04-full-20260803-t2-standby", "restore-sandbox-standby", "standby_seed", self.requested_target, "SUCCESS", 1, "COMPLETE", "COMPLETE", "MATCH", 101, "MATCH", self.source_orders + self.source_order_lines + self.source_payments + self.source_inventory, self.source_orders + self.source_order_lines + self.source_payments + self.source_inventory, "NONE", "smoke-only recovery; not approved for checkout business service"),
            ("hc04-drill-history-ok", "hc04-full-20260725-t1", "restore-sandbox-history", "primary", "2026-07-25 01:15:00", "SUCCESS", 1, "COMPLETE", "COMPLETE", "MATCH", 98, "MATCH", self.source_orders + self.source_order_lines + self.source_payments + self.source_inventory, self.source_orders + self.source_order_lines + self.source_payments + self.source_inventory, "NONE", "previous successful drill outside current window"),
            ("hc04-drill-reporting-failed", "hc04-full-20260803-t2-reporting", "restore-sandbox-reporting", "reporting_clone", self.requested_target, "FAILED", 1, "COMPLETE", "COMPLETE", "MISMATCH", 110, "MISMATCH", 5000, 4983, "SOURCE_CRC_MISMATCH", "reporting clone data is stale and not an approved production source"),
        ]
        if self.focused_fixture:
            rows = [row for row in rows if row[0] != "hc04-drill-history-ok"]
        else:
            for index in range(1, 13):
                rows.append((f"hc04-drill-20260802-{index:02d}", "hc04-full-20260802-t1", f"restore-sandbox-20260802-{index:02d}", "primary", f"2026-08-02 01:{index:02d}:00", "SUCCESS", 1, "COMPLETE", "COMPLETE", "MATCH", 80 + index, "MATCH", 1000, 1000, "NONE", "scheduled validation record"))
        self._insert_rows(
            env,
            self.restore_drill_table,
            ("drill_id", "backup_id", "target_cluster", "source_role", "target_ts", "status", "isolated", "metadata_status", "checkpoint_status", "checksum_status", "restore_duration_seconds", "business_crc_status", "source_rows", "restored_rows", "failure_class", "log_excerpt"),
            rows,
        )

    def _load_restore_table_checks(self, env) -> None:
        rows = []
        if not self.focused_fixture:
            for index in range(1, 49):
                rows.append(("hc04-drill-20260802-01", f"archive_table_{index:02d}", 100 + index, 100 + index, index * 101, index * 101, "MATCH", 0))
        self._insert_rows(
            env,
            self.restore_check_table,
            ("drill_id", "table_name", "source_rows", "restored_rows", "source_checksum", "restored_checksum", "checksum_status", "critical"),
            rows,
        )

    def _load_operational_noise(self, env) -> None:
        rejected_sources = (
            (20, self.front_segment),
            (11, self.early_segment),
            (16, self.late_segment),
            (10, self.continuity_segment),
            (2, self.missing_segment),
            (6, self.secondary_segment),
        )
        decoy_sources = (
            (20, self.front_segment, "primary", "online"),
            (21, self.front_segment, "standby_seed", "isolated"),
            (11, self.early_segment, "primary", "online"),
            (12, self.early_segment, "standby_seed", "isolated"),
            (16, self.late_segment, "primary", "online"),
            (17, self.late_segment, "standby_seed", "isolated"),
            (9, self.continuity_segment, "primary", "online"),
            (10, self.continuity_segment, "standby_seed", "isolated"),
            (2, self.missing_segment, "primary", "online"),
            (3, self.missing_segment, "reporting_clone", "isolated"),
            (6, self.secondary_segment, "primary", "online"),
            (7, self.secondary_segment, "reporting_clone", "isolated"),
        )
        if self.focused_fixture:
            decoy_sources = tuple(
                row for row in decoy_sources if row[1] == self.continuity_segment
            )
        approvals = [
            (
                3000 + index,
                self.request_key,
                self.selected_backup_id,
                source_object_id,
                segment,
                source_role,
                restore_mode,
                "APPROVED",
                f"2026-08-04 08:{index:02d}:00",
                "dr-owner",
                "regional recovery approval record",
            )
            for index, (source_object_id, segment, source_role, restore_mode) in enumerate(decoy_sources, start=1)
        ]
        if not self.focused_fixture:
            approvals.extend(
                (
                    2000 + index,
                    self.request_key,
                    self.selected_backup_id,
                    rejected_sources[index % len(rejected_sources)][0],
                    rejected_sources[index % len(rejected_sources)][1],
                    "primary",
                    "isolated",
                    "APPROVED",
                    f"2026-08-04 09:{index % 60:02d}:00",
                    "automation",
                    "automated validation approval record",
                )
                for index in range(1, self.targeted_noise_rows - len(decoy_sources) + 1)
            )
            approvals.extend(
                (
                    index,
                    f"hc04-weekly-recoverability-20260802-{index:02d}",
                    "hc04-full-20260802-t1",
                    0,
                    f"t1-00000000000000B{index:02X}",
                    "primary",
                    "isolated",
                    "APPROVED",
                    "2026-08-02 08:00:00",
                    "automation",
                    "archival request record",
                )
                for index in range(97, 110)
            )
            preview_sources = (
                (20, self.front_segment),
                (21, self.front_segment),
                (2, self.missing_segment),
                (3, self.missing_segment),
                (6, self.secondary_segment),
                (7, self.secondary_segment),
                (11, self.early_segment),
                (12, self.early_segment),
                (16, self.late_segment),
                (17, self.late_segment),
            )
            approvals.extend(
                (
                    900 + index,
                    self.request_key,
                    self.selected_backup_id,
                    source_object_id,
                    segment,
                    "primary",
                    "isolated",
                    "APPROVED",
                    f"2026-08-04 10:{index % 60:02d}:00",
                    "automation",
                    "automated validation approval record",
                )
                for index, (source_object_id, segment) in enumerate(
                    (preview_sources[index % len(preview_sources)] for index in range(self.targeted_noise_rows)),
                    start=1,
                )
            )
        approvals.extend([
            (1001, self.request_key, self.selected_backup_id, 4, self.missing_segment, "primary", "isolated", "APPROVED", "2026-08-04 08:00:00", "dr-owner", "recovery approval record"),
            (1002, self.request_key, self.selected_backup_id, 8, self.secondary_segment, "primary", "isolated", "APPROVED", "2026-08-04 08:00:30", "dr-owner", "recovery approval record"),
            (1003, self.request_key, self.selected_backup_id, 10, self.continuity_segment, "primary", "isolated", "APPROVED", "2026-08-04 08:01:00", "dr-owner", "recovery approval record"),
            (1004, self.request_key, "hc04-full-20260803-t2-standby", 2, self.missing_segment, "standby_seed", "isolated", "SMOKE_ONLY", "2026-08-04 08:01:30", "dr-owner", "standby approval record"),
            (1005, self.request_key, self.selected_backup_id, 14, self.early_segment, "primary", "isolated", "APPROVED", "2026-08-04 08:01:30", "dr-owner", "recovery approval record"),
            (1006, self.request_key, self.selected_backup_id, 18, self.late_segment, "primary", "isolated", "APPROVED", "2026-08-04 08:02:00", "dr-owner", "recovery approval record"),
            (1007, self.request_key, self.selected_backup_id, 22, self.front_segment, "primary", "isolated", "APPROVED", "2026-08-04 08:02:30", "dr-owner", "recovery approval record"),
        ])
        approval_count = len(approvals)
        approval_order = tuple(
            (index * _HC04_APPROVAL_ORDER_STEP) % approval_count
            for index in range(approval_count)
        )
        approvals = [
            (
                10000 + output_index,
                *approvals[source_index][1:8],
                f"2026-08-04 {8 + output_index // 60:02d}:{output_index % 60:02d}:00",
                approvals[source_index][9],
                approvals[source_index][10],
            )
            for output_index, source_index in enumerate(approval_order, start=1)
        ]
        self._insert_rows(
            env,
            self.approval_table,
            ("approval_id", "request_key", "selected_backup_id", "source_object_id", "source_segment", "source_role", "restore_mode", "approval_state", "approved_at", "approved_by", "approval_notes"),
            approvals,
        )
        objects = [
            (1, self.selected_backup_id, self.missing_segment, "us-east-1", "CORRUPT" if not self.continuity_only else "AVAILABLE", 1, 0 if not self.continuity_only else 1, 0, self._archive_hashes[1], "archive inventory row"),
            (2, self.selected_backup_id, self.missing_segment, "us-west-2", "AVAILABLE", 1, 1, 0, self._archive_hashes[2], "archive inventory row"),
            (3, self.selected_backup_id, self.missing_segment, "us-east-1", "AVAILABLE", 1, 1, 0, self._archive_hashes[3], "archive inventory row"),
            (4, self.selected_backup_id, self.missing_segment, "us-west-2", "AVAILABLE", 1, 1, 0, self._archive_hashes[4], "archive inventory row"),
            (5, self.selected_backup_id, self.secondary_segment, "us-east-1", "CORRUPT" if not self.continuity_only else "AVAILABLE", 1, 0 if not self.continuity_only else 1, 0, self._archive_hashes[5], "archive inventory row"),
            (6, self.selected_backup_id, self.secondary_segment, "us-west-2", "AVAILABLE", 1, 1, 0, self._archive_hashes[6], "archive inventory row"),
            (7, self.selected_backup_id, self.secondary_segment, "us-east-1", "AVAILABLE", 1, 1, 0, self._archive_hashes[7], "archive inventory row"),
            (8, self.selected_backup_id, self.secondary_segment, "us-west-2", "AVAILABLE", 1, 1, 0, self._archive_hashes[8], "archive inventory row"),
            (9, self.selected_backup_id, self.continuity_segment, "us-east-1", "AVAILABLE", 1, 0, 0, self._archive_hashes[9], "archive inventory row"),
            (10, self.selected_backup_id, self.continuity_segment, "us-west-2", "AVAILABLE", 1, 1, 0, self._archive_hashes[10], "archive inventory row"),
        ]
        for index, segment in (
            (11, self.early_segment),
            (12, self.early_segment),
            (13, self.early_segment),
            (14, self.early_segment),
            (15, self.late_segment),
            (16, self.late_segment),
            (17, self.late_segment),
            (18, self.late_segment),
            (19, self.front_segment),
            (20, self.front_segment),
            (21, self.front_segment),
            (22, self.front_segment),
        ):
            primary = (index in {13, 15, 19}) and not self.continuity_only
            objects.append(
                (
                    index,
                    self.selected_backup_id,
                    segment,
                    ("us-east-1", "us-west-2", "eu-west-1")[index % 3],
                    "CORRUPT" if primary else "AVAILABLE",
                    1,
                    0 if primary else 1,
                    0,
                    self._archive_hashes[index],
                    "archive inventory row",
                )
            )
        for index in range(23, 23 + self.targeted_noise_rows):
            segment = f"t2-00000000000000B{index - 22:02X}"
            objects.append((index, self.selected_backup_id, segment, ("us-east-1", "us-west-2", "eu-west-1")[index % 3], "AVAILABLE", 1, 1, int(index % 11 == 0), hashlib.sha256(f"{self.selected_backup_id}/{segment}".encode()).hexdigest(), "archive inventory row"))
        if not self.focused_fixture:
            for index in range(23 + self.targeted_noise_rows, 23 + self.targeted_noise_rows + 38):
                segment = f"t1-00000000000000B{index - 118:02X}"
                objects.append((index, "hc04-full-20260802-t1", segment, ("us-east-1", "us-west-2", "eu-west-1")[index % 3], "AVAILABLE", 1, 1, int(index % 11 == 0), hashlib.sha256(f"hc04-full-20260802-t1/{segment}".encode()).hexdigest(), "archive inventory row"))
        self._insert_rows(
            env,
            self.object_inventory_table,
            ("object_id", "backup_id", "segment_name", "region", "object_status", "readable", "replicated", "legal_hold", "checksum", "note"),
            objects,
        )
        events = [
            (1, "2026-08-04 07:45:00", "WARN", "restore", self.selected_backup_id, "isolated restore sample completed with a non-zero log restore result"),
            (2, "2026-08-04 07:46:00", "WARN", "checkpoint", self.selected_backup_id, "checkpoint did not advance through the selected recovery target"),
            (3, "2026-08-04 07:47:00", "INFO", "backup", self.selected_backup_id, "scheduled full backup job reported success"),
            (4, "2026-08-04 07:48:00", "INFO", "business", self.selected_backup_id, "checkout traffic remained within normal band"),
        ]
        routine_event_count = 8 if self.focused_fixture else 76
        sources = ("backup", "restore", "monitoring", "reporting", "storage", "scheduler", "tikv", "tidb")
        for index in range(5, 5 + routine_event_count):
            events.append((index, f"2026-08-{1 + index % 4:02d} {index % 24:02d}:{index % 60:02d}:00", ("INFO", "INFO", "WARN", "DEBUG")[index % 4], sources[index % len(sources)], "hc04-full-20260802-t1", f"routine operational event {index}; no direct recovery conclusion"))
        self._insert_rows(
            env,
            self.monitoring_table,
            ("event_id", "event_time", "severity", "source", "related_backup_id", "message"),
            events,
        )

    def _verify_persistent_state(self, env) -> None:
        payload = json_object(
            env.execute_sql(
                f"SELECT COUNT(*), COALESCE(SUM(order_id), 0) FROM {self.db}.{self.orders_table}"
            ),
            "verify HC04 source orders",
        )
        rows = payload["result"]
        if len(rows) != 1 or int(rows[0][0]) != self.source_orders:
            raise RuntimeError(
                f"HC04 source order state is invalid: expected_rows={self.source_orders}, observed={rows!r}"
            )
        selected = json_object(
            env.execute_sql(
                f"SELECT COUNT(*) FROM {self.db}.{self.log_segment_table} "
                f"WHERE backup_id = {sql_literal(self.selected_backup_id)} AND usable_for_restore = 0"
            ),
            "verify HC04 selected missing segment",
        )
        expected_unusable = 1 if self.continuity_only else 6
        if int(selected["result"][0][0]) != expected_unusable:
            raise RuntimeError(
                "HC04 selected chain has an unexpected unusable-segment count: "
                f"expected={expected_unusable}, rows={selected['result']!r}"
            )
        object_state = json_object(
            env.execute_sql(
                f"SELECT object_status, readable, replicated FROM {self.db}.{self.object_inventory_table} "
                f"WHERE object_id IN (1, 5, 9, 13, 15, 19) ORDER BY object_id"
            ),
            "verify HC04 corrupt primary archive object",
        )
        expected_object_state = [
            ["CORRUPT", 1, 0],
            ["CORRUPT", 1, 0],
            ["AVAILABLE", 1, 0],
            ["CORRUPT", 1, 0],
            ["CORRUPT", 1, 0],
            ["CORRUPT", 1, 0],
        ]
        if self.continuity_only:
            expected_object_state = [
                ["AVAILABLE", 1, 1],
                ["AVAILABLE", 1, 1],
                ["AVAILABLE", 1, 0],
                ["AVAILABLE", 1, 1],
                ["AVAILABLE", 1, 1],
                ["AVAILABLE", 1, 1],
            ]
        if object_state["result"] != expected_object_state:
            raise RuntimeError(
                "HC04 primary archive fault is not installed: "
                f"expected six primary archive states, observed={object_state['result']!r}"
            )
        attempts = json_object(
            env.execute_sql(
                f"SELECT COUNT(*) FROM {self.db}.{self.restore_attempt_table} "
                f"WHERE drill_id = {sql_literal(self.selected_drill_id)}"
            ),
            "verify HC04 restore attempt baseline",
        )
        if int(attempts["result"][0][0]) != 0:
            raise RuntimeError(
                "HC04 restore attempt table must be empty before the agent run: "
                f"rows={attempts['result']!r}"
            )
