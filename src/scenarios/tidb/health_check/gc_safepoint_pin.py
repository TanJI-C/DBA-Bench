import json
import time
from collections.abc import Mapping
from dataclasses import dataclass, replace

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)

from src.scenarios.evaluation.tidb.health_check.gc_safepoint_pin import (
    TidbHealthCheckGcSafepointPinForAbandonedChangefeedEvaluatorCase,
    TidbHealthCheckGcSafepointPinForOrphanedBackupRestoreEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


def _background_profiles(target_service_id: str = "svc-7f2a") -> tuple[WorkloadProfile, ...]:
    return (
        WorkloadProfile(
            name="order_status_dashboard",
            sql=(
                "SELECT tenant_id, status, COUNT(*) AS orders, SUM(amount_cents) AS cents "
                "FROM benchops.order_events WHERE updated_at > NOW() - INTERVAL 2 DAY "
                "GROUP BY tenant_id, status ORDER BY cents DESC LIMIT 20"
            ),
            qps=0.7,
            tier="OLTP_READ",
            application_name="checkout-dashboard",
        ),
        WorkloadProfile(
            name="customer_activity_probe",
            sql=(
                "SELECT customer_id, COUNT(*) AS events, MAX(updated_at) AS newest_event "
                "FROM benchops.order_events WHERE tenant_id IN (2, 5, 8) "
                "GROUP BY customer_id ORDER BY events DESC LIMIT 40"
            ),
            qps=0.5,
            tier="OLTP_READ",
            application_name="customer-activity-api",
        ),
        WorkloadProfile(
            name="revenue_window_rollup",
            sql=(
                "SELECT region_id, SUM(amount_cents) AS cents, COUNT(*) AS orders "
                "FROM benchops.order_events WHERE created_at > NOW() - INTERVAL 7 DAY "
                "GROUP BY region_id ORDER BY cents DESC"
            ),
            qps=0.35,
            tier="OLAP_BURST",
            application_name="finance-rollup",
        ),
        WorkloadProfile(
            name="order_touch_writer",
            sql=(
                "UPDATE benchops.order_events SET amount_cents = amount_cents + 1, updated_at = NOW() "
                "WHERE order_id BETWEEN 101 AND 180"
            ),
            qps=0.25,
            tier="OLTP_WRITE",
            commit=True,
            application_name="checkout-writer",
        ),
        WorkloadProfile(
            name="capacity_audit_writer",
            sql=(
                "INSERT INTO benchops.order_event_log (event_type, tenant_id, payload, created_at) "
                "SELECT 'capacity_probe', tenant_id, CONCAT('audit-', order_id), NOW() "
                "FROM benchops.order_events WHERE order_id BETWEEN 1 AND 20"
            ),
            qps=0.18,
            tier="DDL_MAINTENANCE",
            commit=True,
            application_name="capacity-audit-job",
        ),
        WorkloadProfile(
            name="replication_status_rollup",
            sql=(
                "SELECT state, owner_status, lifecycle_stage, COUNT(*) AS feeds, "
                "MAX(checkpoint_lag_seconds) AS max_lag "
                "FROM benchops.replication_checkpoints GROUP BY state, owner_status, lifecycle_stage "
                "ORDER BY max_lag DESC"
            ),
            qps=0.45,
            tier="BACKUP_MIGRATION",
            application_name="replication-inventory",
        ),
        WorkloadProfile(
            name="capacity_trend_review",
            sql=(
                "SELECT sample_name, MAX(observed_mb) AS newest_mb, "
                "MAX(growth_mb_per_day) AS growth_mb_per_day "
                "FROM benchops.capacity_samples GROUP BY sample_name "
                "ORDER BY growth_mb_per_day DESC LIMIT 40"
            ),
            qps=0.45,
            tier="HOST_NOISE",
            application_name="capacity-forecast",
        ),
        WorkloadProfile(
            name="owner_lineage_scan",
            sql=(
                "SELECT owner_type, registration_state, COUNT(*) AS owners, "
                "MIN(safe_point_time) AS oldest "
                "FROM benchops.owner_lineage_matrix GROUP BY owner_type, registration_state "
                "ORDER BY oldest"
            ),
            qps=0.35,
            tier="BACKUP_MIGRATION",
            application_name="retention-owner-review",
        ),
        WorkloadProfile(
            name="retention_history_rollup",
            sql=(
                "SELECT source, MIN(safe_point_age_hours), MAX(safe_point_age_hours), "
                "MAX(retained_versions_estimate), MAX(tikv_disk_used_mb) "
                "FROM benchops.retention_history GROUP BY source ORDER BY MAX(tikv_disk_used_mb) DESC"
            ),
            qps=0.3,
            tier="HOST_NOISE",
            application_name="retention-dashboard",
        ),
        WorkloadProfile(
            name="review_queue_triage",
            sql=(
                "SELECT category, status, severity, COUNT(*) AS tickets "
                "FROM benchops.review_queue GROUP BY category, status, severity "
                "ORDER BY tickets DESC"
            ),
            qps=0.35,
            tier="MONITOR",
            application_name="ops-ticket-review",
        ),
        WorkloadProfile(
            name="account_balance_reconciliation",
            sql=(
                "SELECT a.region_code, COUNT(*) AS accounts, SUM(a.balance_cents) AS balance "
                "FROM benchops.account_balances a GROUP BY a.region_code ORDER BY balance DESC"
            ),
            qps=0.25,
            tier="OLTP_READ",
            application_name="finance-reconciliation",
        ),
        WorkloadProfile(
            name="daily_order_summary",
            sql=(
                "SELECT DATE(created_at) AS order_day, status, COUNT(*) AS orders, SUM(amount_cents) AS cents "
                "FROM benchops.order_events GROUP BY DATE(created_at), status ORDER BY order_day DESC, status"
            ),
            qps=0.25,
            tier="OLAP_BURST",
            application_name="daily-summary-job",
        ),
        WorkloadProfile(
            name="checkpoint_window_probe",
            sql=(
                "SELECT changefeed_id, checkpoint_time, last_heartbeat_at, checkpoint_lag_seconds "
                "FROM benchops.replication_checkpoints "
                "WHERE checkpoint_time > NOW() - INTERVAL 2 DAY ORDER BY checkpoint_lag_seconds DESC"
            ),
            qps=0.4,
            tier="MONITOR",
            application_name="replication-slo-probe",
        ),
        WorkloadProfile(
            name="recent_event_log_probe",
            sql=(
                "SELECT event_type, tenant_id, COUNT(*) AS events "
                "FROM benchops.order_event_log "
                "WHERE created_at > NOW() - INTERVAL 1 DAY "
                "GROUP BY event_type, tenant_id ORDER BY events DESC LIMIT 30"
            ),
            qps=0.3,
            tier="OLTP_READ",
            application_name="audit-dashboard",
        ),
        WorkloadProfile(
            name="exception_register_scan",
            sql=(
                "SELECT exception_state, COUNT(*) AS exceptions, MAX(hold_until) AS latest_hold "
                "FROM benchops.retention_exceptions GROUP BY exception_state ORDER BY latest_hold DESC"
            ),
            qps=0.28,
            tier="BACKUP_MIGRATION",
            application_name="retention-exception-review",
        ),
        WorkloadProfile(
            name="tenant_order_heatmap",
            sql=(
                "SELECT tenant_id, region_id, COUNT(*) AS orders, SUM(amount_cents) AS cents "
                "FROM benchops.order_events WHERE created_at >= NOW() - INTERVAL 30 DAY "
                "GROUP BY tenant_id, region_id ORDER BY cents DESC LIMIT 50"
            ),
            qps=0.32,
            tier="OLAP_BURST",
            application_name="tenant-heatmap",
        ),
        WorkloadProfile(
            name="owner_checkpoint_join_probe",
            sql=(
                "SELECT l.owner_type, c.state, c.owner_status, COUNT(*) AS rows_seen "
                "FROM benchops.retention_owner_ledger l "
                "LEFT JOIN benchops.replication_checkpoints c ON c.service_id = l.service_id "
                "GROUP BY l.owner_type, c.state, c.owner_status ORDER BY rows_seen DESC"
            ),
            qps=0.3,
            tier="MONITOR",
            application_name="continuity-audit",
        ),
        WorkloadProfile(
            name="order_event_recent_volume",
            sql=(
                "SELECT DATE(created_at) AS event_day, event_type, COUNT(*) AS events "
                "FROM benchops.order_event_log WHERE created_at >= NOW() - INTERVAL 7 DAY "
                "GROUP BY DATE(created_at), event_type ORDER BY event_day DESC, events DESC"
            ),
            qps=0.26,
            tier="OLTP_READ",
            application_name="event-volume-dashboard",
        ),
        WorkloadProfile(
            name="service_window_distribution",
            sql=(
                "SELECT retention_class, registration_state, COUNT(*) AS owners, "
                "MIN(safe_point_time) AS oldest_window, MAX(last_heartbeat_at) AS newest_heartbeat "
                "FROM benchops.retention_owner_ledger GROUP BY retention_class, registration_state"
            ),
            qps=0.24,
            tier="MONITOR",
            application_name="service-window-dashboard",
        ),
        WorkloadProfile(
            name="account_region_snapshot",
            sql=(
                "SELECT region_code, MIN(balance_cents), MAX(balance_cents), AVG(balance_cents) "
                "FROM benchops.account_balances GROUP BY region_code ORDER BY region_code"
            ),
            qps=0.22,
            tier="OLTP_READ",
            application_name="account-region-report",
        ),
        WorkloadProfile(
            name="capacity_source_crosscheck",
            sql=(
                "SELECT source, COUNT(*) AS samples, SUM(observed_mb) AS observed_total, "
                "AVG(growth_mb_per_day) AS avg_growth "
                "FROM benchops.capacity_samples GROUP BY source ORDER BY avg_growth DESC"
            ),
            qps=0.2,
            tier="HOST_NOISE",
            application_name="capacity-source-crosscheck",
        ),
        WorkloadProfile(
            name="review_status_digest",
            sql=(
                "SELECT status, category, COUNT(*) AS tickets, MIN(opened_at) AS oldest_ticket "
                "FROM benchops.review_queue GROUP BY status, category ORDER BY oldest_ticket"
            ),
            qps=0.2,
            tier="MONITOR",
            application_name="review-status-digest",
        ),
        WorkloadProfile(
            name="retention_coordinator_reconcile",
            sql=(
                "UPDATE benchops.retention_reconciliation "
                "SET stable_at = IF(observation_count + 1 >= required_observations, COALESCE(stable_at, NOW()), stable_at), "
                "reconciliation_state = IF(observation_count + 1 >= required_observations, 'stable', 'pending'), "
                "observation_count = observation_count + 1, "
                "last_observed_at = NOW() "
                f"WHERE service_id = '{target_service_id}' "
                "AND reconciliation_state = 'pending' "
                f"AND (SELECT active FROM benchops.retention_owner_ledger WHERE service_id = '{target_service_id}') = 0"
            ),
            qps=0.5,
            tier="CONTROL_PLANE",
            commit=True,
            application_name="gc-retention-coordinator",
        ),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckGcSafepointPinCase(TiDBScenarioCase):
    db: str
    target_service_id: str
    target_changefeed_id: str
    target_owner_type: str
    protected_service_ids: tuple[str, ...]
    protected_account_count: int
    protected_account_balance_cents: int
    max_effective_safepoint_age_hours: int
    closeout_required_observations: int
    focused_fixture: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckGcSafepointPinForAbandonedChangefeedScenarioCase(TidbHealthCheckGcSafepointPinCase):
    pass


_TARGET_SERVICE_ID = "svc-7f2a"
_PROTECTED_SERVICE_IDS = (
    "ticdc-default-ledger-live-v2",
    "ticdc-default-warehouse-hourly",
    "br-nightly-full-20260801",
    "ticdc-default-analytics-pause-2026w31",
    "dm-default-region-mirror",
    "ticdc-default-orders-replay",
    "br-weekly-restore-validation",
    "ticdc-default-compliance-export",
    "ticdc-default-warehouse-backfill",
    "dm-default-cold-archive",
    "ticdc-default-inventory-delta",
    "ticdc-default-batch-export",
    "ticdc-default-feature-sandbox",
    "ticdc-default-legacy-report-2025",
    "dm-default-delivery-replay",
    "br-default-cold-restore",
    "br-default-legal-hold-2025",
    "svc-3b18",
    "svc-4c91",
    "svc-5d27",
    "svc-6e44",
    "svc-7a83",
)


_CASE = TidbHealthCheckGcSafepointPinForAbandonedChangefeedScenarioCase(
    case_id="abandoned_changefeed_gc_safepoint_pin",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "a stopped or missing TiCDC changefeed has no live owner but still pins the oldest active service GC safepoint",
                    "entity": "abandoned_changefeed_gc_safepoint_pin",
                    "evidence": ["owner lineage and replication checkpoint evidence"],
                },
                {
                    "type": "finding",
                    "factor": "the stale service safepoint prevents TiDB GC from advancing and retains old MVCC versions",
                    "entity": "abandoned_changefeed_gc_safepoint_pin",
                    "evidence": ["effective retention window and retention history"],
                },
                {
                    "type": "finding",
                    "factor": "active ledger warehouse and backup safepoint owners are healthy and must be preserved",
                    "entity": "abandoned_changefeed_gc_safepoint_pin",
                    "evidence": ["protected owner and exception registers"],
                },
            ]
        },
        "outcome": {
            "changes": ["applied the case-specific remediation"],
            "verification": ["verified the case-specific final state"],
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification.",
    },
    case_no=0,
    evaluator=TidbHealthCheckGcSafepointPinForAbandonedChangefeedEvaluatorCase,
    title="Routine TiDB retention review where an orphaned changefeed keeps the oldest service GC safepoint.",
    alert=(
        "日常数据服务与容量巡检：近期报表里历史版本清理窗口、异步处理时间跨度和多个存储来源的变化需要复核，"
        "但核心交易延迟、业务读写和节点存活都没有事故告警。请按常规 DBA 流程核对各类保留责任、"
        "处理进度、业务活动与容量时间序列，判断是否有已经结束却仍影响在线系统的流程；只有证据能排除"
        "当前业务、备份、恢复和合规保留后，才允许做最小范围的状态收口。报告中说明风险、影响范围、"
        "保留的例外和已排除的其它链路，并给出最终复核结果。"
    ),
    initial_state={
        "status": "routine_health_check",
        "incident": "none",
        "retention_window": "older_than_expected",
        "business_traffic": "active",
    },
    expected_target={
        "status": "retention_owner_cleaned",
        "target_service_id_removed": _TARGET_SERVICE_ID,
        "healthy_owners_preserved": True,
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_background_profiles(),
        worker_count=8,
        seed=0x0C01,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=12.0,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=8,
        environmental_complexity=0.994412,
        reference_run_ids=(
            "reference-193__tidb_health_check_gc_safepoint_pin__"
            "abandoned_changefeed_gc_safepoint_pin__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        bootstrap_cache_enabled=False,
    ),
    db="benchops",
    target_service_id=_TARGET_SERVICE_ID,
    target_changefeed_id="cf-7f2a",
    target_owner_type="ticdc",
    protected_service_ids=_PROTECTED_SERVICE_IDS,
    protected_account_count=64,
    protected_account_balance_cents=6435360,
    max_effective_safepoint_age_hours=24,
    closeout_required_observations=3,
)


_NEW_CASE = replace(
    _CASE,
    case_id="orphaned_backup_restore_gc_safepoint",
    case_no=1,
    evaluator=TidbHealthCheckGcSafepointPinForOrphanedBackupRestoreEvaluatorCase,
    title="Routine TiDB retention review where an orphaned backup/restore coordinator keeps the oldest service GC safepoint.",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "a decommissioned backup or restore coordinator has no live runtime but still pins the oldest active service GC safepoint",
                    "entity": "orphaned_backup_restore_gc_safepoint",
                    "evidence": ["owner lineage, restore checkpoint, and closeout evidence"],
                },
                {
                    "type": "finding",
                    "factor": "the stale service safepoint prevents TiDB GC from advancing and retains old MVCC versions",
                    "entity": "orphaned_backup_restore_gc_safepoint",
                    "evidence": ["effective retention window and protected owner register"],
                },
                {
                    "type": "finding",
                    "factor": "active ledger warehouse and compliance owners are healthy and must be preserved",
                    "entity": "orphaned_backup_restore_gc_safepoint",
                    "evidence": ["protected owner and exception registers"],
                },
            ]
        },
        "outcome": {
            "changes": ["closed only the orphaned backup/restore owner after controller convergence"],
            "verification": ["verified the effective safepoint advanced and protected accounts stayed unchanged"],
        },
        "summary": "The backup/restore closeout was reconciled and the targeted retention owner was released.",
    },
    alert=(
        "日常保留窗口复核：备份恢复值班记录与在线复制、合规保留记录混在同一批容量证据中。"
        "请关联当前请求、恢复 checkpoint、owner 心跳和 effective safepoint，确认已经退役的流程是否仍在占用"
        "保留窗口。只允许收口已证明完成的 backup/restore owner，必须保留仍有业务或合规依据的其它 owner，"
        "并在 controller 观察收敛后复核结果。"
    ),
    expected_target={
        "status": "retention_owner_cleaned",
        "target_service_id_removed": "svc-br-2c41",
        "healthy_owners_preserved": True,
        "owner_type": "backup_restore",
    },
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.0,
        reference_run_ids=(
            "tidb-reference-12__"
            "tidb_health_check_gc_safepoint_pin__"
            "orphaned_backup_restore_gc_safepoint__mock__r001",
        ),
    ),
    target_service_id="svc-br-2c41",
    target_changefeed_id="br-restore-2c41",
    target_owner_type="br",
    protected_service_ids=(
        "ticdc-default-ledger-live-v2",
        "ticdc-default-warehouse-hourly",
        "br-nightly-full-20260801",
        "br-default-legal-hold-2025",
    ),
    closeout_required_observations=2,
    focused_fixture=True,
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(
            profile
            for profile in _background_profiles("svc-br-2c41")
            if profile.name
            in {
                "order_status_dashboard",
                "order_touch_writer",
                "replication_status_rollup",
                "owner_lineage_scan",
                "checkpoint_window_probe",
                "retention_coordinator_reconcile",
            }
        ),
        worker_count=5,
        seed=0x0C11,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=10.0,
    ),
)


class TidbHealthCheckGcSafepointPinScenario(TiDBScenario):
    scenario_id = "tidb_health_check_gc_safepoint_pin"
    description = "Routine TiDB retention review for an orphaned changefeed pinning the service GC safepoint."
    cases = (_CASE, _NEW_CASE)

    def build_fault_plan(
        self,
        case: TidbHealthCheckGcSafepointPinCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbHealthCheckGcSafepointPinInjector,
                config={
                    "db": case.db,
                    "target_service_id": case.target_service_id,
                    "target_changefeed_id": case.target_changefeed_id,
                    "target_owner_type": case.target_owner_type,
                    "protected_service_ids": case.protected_service_ids,
                    "protected_account_count": case.protected_account_count,
                    "protected_account_balance_cents": case.protected_account_balance_cents,
                    "max_effective_safepoint_age_hours": case.max_effective_safepoint_age_hours,
                    "closeout_required_observations": case.closeout_required_observations,
                    "focused_fixture": case.focused_fixture,
                },
            ),
        )



class TidbHealthCheckGcSafepointPinInjector(BaseFaultInjector):
    """Create a business-shaped retention review with one orphaned CDC owner."""

    def install(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._create_schema(context.env)
        self._load_business_tables(context.env)
        self._load_operational_tables(context.env)
        self._create_views(context.env)
        self._verify_fault_state(context.env)

    def activate(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._verify_fault_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._verify_fault_state(context.env)
        return {
            "effective_retention_window": require_sql_success(
                context.env.execute_sql(f"SELECT * FROM {self.db}.effective_retention_window"),
                "capture effective retention window",
            ),
            "owner_lineage_matrix": require_sql_success(
                context.env.execute_sql(f"SELECT * FROM {self.db}.owner_lineage_matrix"),
                "capture retention owner lineage",
            ),
            "replication_checkpoints": require_sql_success(
                context.env.execute_sql(f"SELECT * FROM {self.db}.replication_checkpoints"),
                "capture replication checkpoints",
            ),
            "retention_reconciliation": require_sql_success(
                context.env.execute_sql(f"SELECT * FROM {self.db}.retention_reconciliation"),
                "capture retention reconciliation state",
            ),
        }

    def quiesce(self, context: FaultLifecycleContext):
        return None

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config)
        query = f"DROP DATABASE IF EXISTS {self.db}"
        for attempt in range(1, 7):
            result = context.env.execute_sql(query)
            payload = json.loads(result) if isinstance(result, str) else result
            if payload.get("status") == "success":
                return
            error = str(payload.get("error", ""))
            if "no leader" not in error.casefold():
                raise RuntimeError(
                    f"drop dedicated retention-review database {self.db} failed: {result!r}"
                )
            if attempt == 6:
                raise RuntimeError(
                    f"drop dedicated retention-review database {self.db} failed after "
                    f"{attempt} attempts: {result!r}"
                )
            time.sleep(5)

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.target_service_id = str(config["target_service_id"])
        self.target_changefeed_id = str(config["target_changefeed_id"])
        self.target_owner_type = str(config["target_owner_type"])
        self.protected_service_ids = tuple(str(item) for item in config["protected_service_ids"])
        self.protected_account_count = int(config["protected_account_count"])
        self.protected_account_balance_cents = int(config["protected_account_balance_cents"])
        self.max_effective_safepoint_age_hours = int(config["max_effective_safepoint_age_hours"])
        self.closeout_required_observations = int(config["closeout_required_observations"])
        self.focused_fixture = bool(config["focused_fixture"])
        self._ledger_service_ids = {self.target_service_id, *self.protected_service_ids}

    def _create_schema(self, env) -> None:
        require_sql_success(env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {self.db}"), "create retention-review database")
        for view in ("effective_retention_window", "owner_lineage_matrix"):
            require_sql_success(env.execute_sql(f"DROP VIEW IF EXISTS {self.db}.{view}"), f"clear retention-review view {view}")
        for table in (
            "order_event_log",
            "order_events",
            "account_balances",
            "retention_owner_ledger",
            "replication_checkpoints",
            "retention_history",
            "capacity_samples",
            "review_queue",
            "retention_exceptions",
            "retention_reconciliation",
        ):
            require_sql_success(env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"), f"clear retention-review table {table}")
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.order_events ("
                "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, customer_id BIGINT NOT NULL, "
                "region_id INT NOT NULL, amount_cents BIGINT NOT NULL, status VARCHAR(24) NOT NULL, "
                "created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL, payload VARCHAR(128) NOT NULL, "
                "KEY idx_tenant_status (tenant_id, status), KEY idx_updated (updated_at))"
            ),
            "create order events",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.order_event_log ("
                "id BIGINT PRIMARY KEY AUTO_INCREMENT, event_type VARCHAR(32) NOT NULL, "
                "tenant_id INT NOT NULL, payload VARCHAR(128) NOT NULL, created_at DATETIME NOT NULL, "
                "KEY idx_created (created_at))"
            ),
            "create order event log",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.account_balances ("
                "account_id INT PRIMARY KEY, region_code VARCHAR(16) NOT NULL, balance_cents BIGINT NOT NULL)"
            ),
            "create account balances",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.retention_owner_ledger ("
                "service_id VARCHAR(96) PRIMARY KEY, owner_type VARCHAR(32) NOT NULL, "
                "owner_detail VARCHAR(96) NOT NULL, safe_point_tso BIGINT NOT NULL, "
                "safe_point_time DATETIME NOT NULL, ttl_seconds BIGINT NOT NULL, "
                "last_heartbeat_at DATETIME NOT NULL, active TINYINT NOT NULL, "
                "retention_class VARCHAR(32) NOT NULL, registration_state VARCHAR(32) NOT NULL, "
                "ticket_ref VARCHAR(32) NOT NULL, notes VARCHAR(255) NOT NULL)"
            ),
            "create retention owner ledger",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.replication_checkpoints ("
                "changefeed_id VARCHAR(96) PRIMARY KEY, service_id VARCHAR(96) NOT NULL, "
                "namespace VARCHAR(32) NOT NULL, state VARCHAR(32) NOT NULL, owner_status VARCHAR(32) NOT NULL, "
                "checkpoint_tso BIGINT NOT NULL, resolved_tso BIGINT NOT NULL, checkpoint_time DATETIME NOT NULL, "
                "last_heartbeat_at DATETIME NOT NULL, checkpoint_lag_seconds BIGINT NOT NULL, "
                "sink_uri VARCHAR(160) NOT NULL, lifecycle_stage VARCHAR(32) NOT NULL, "
                "ticket_ref VARCHAR(32) NOT NULL, data_class VARCHAR(32) NOT NULL, notes VARCHAR(255) NOT NULL)"
            ),
            "create replication checkpoints",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.retention_history ("
                "sample_no INT PRIMARY KEY, sampled_at DATETIME NOT NULL, anchor_service_id VARCHAR(96) NOT NULL, "
                "safe_point_age_hours INT NOT NULL, retained_versions_estimate BIGINT NOT NULL, "
                "tikv_disk_used_mb BIGINT NOT NULL, source VARCHAR(64) NOT NULL, notes VARCHAR(255) NOT NULL)"
            ),
            "create retention history",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.capacity_samples ("
                "sample_no INT PRIMARY KEY, sample_name VARCHAR(64) NOT NULL, sampled_at DATETIME NOT NULL, "
                "observed_mb BIGINT NOT NULL, growth_mb_per_day DECIMAL(10,2) NOT NULL, "
                "source VARCHAR(64) NOT NULL, notes VARCHAR(255) NOT NULL, KEY idx_sample_name (sample_name))"
            ),
            "create capacity samples",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.review_queue ("
                "ticket_id VARCHAR(32) PRIMARY KEY, owner_hint VARCHAR(96) NOT NULL, severity VARCHAR(16) NOT NULL, "
                "status VARCHAR(24) NOT NULL, category VARCHAR(32) NOT NULL, opened_at DATETIME NOT NULL, "
                "notes VARCHAR(255) NOT NULL)"
            ),
            "create retention review queue",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.retention_exceptions ("
                "exception_id VARCHAR(32) PRIMARY KEY, service_id VARCHAR(96) NOT NULL, "
                "exception_state VARCHAR(24) NOT NULL, hold_until DATETIME NOT NULL, "
                "approval_ref VARCHAR(32) NOT NULL, rationale VARCHAR(255) NOT NULL, "
                "KEY idx_exception_service (service_id))"
            ),
            "create retention exception register",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.retention_reconciliation ("
                "service_id VARCHAR(96) PRIMARY KEY, changefeed_id VARCHAR(96) NOT NULL, "
                "reconciliation_state VARCHAR(24) NOT NULL, observation_count INT NOT NULL, "
                "required_observations INT NOT NULL, last_observed_at DATETIME NULL, "
                "stable_at DATETIME NULL, closeout_cutoff_tso BIGINT NOT NULL, notes VARCHAR(255) NOT NULL)"
            ),
            "create retention reconciliation controller state",
        )

    def _load_business_tables(self, env) -> None:
        for start in range(1, 4001, 500):
            values = []
            for order_id in range(start, start + 500):
                tenant_id = order_id % 11 + 1
                customer_id = 100000 + order_id % 700
                region_id = order_id % 7 + 1
                amount = 1000 + order_id % 9000
                status = ("open", "paid", "shipped", "review")[order_id % 4]
                created_hours = order_id % 240
                updated_hours = order_id % 72
                values.append(
                    f"({order_id},{tenant_id},{customer_id},{region_id},{amount},"
                    f"'{status}',NOW() - INTERVAL {created_hours} HOUR,"
                    f"NOW() - INTERVAL {updated_hours} HOUR,'order-payload-{order_id % 29}')"
                )
            require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {self.db}.order_events "
                    "(order_id, tenant_id, customer_id, region_id, amount_cents, status, created_at, updated_at, payload) "
                    f"VALUES {','.join(values)}"
                ),
                f"load order batch starting {start}",
            )
        account_values = []
        for account_id in range(1, self.protected_account_count + 1):
            balance = 100000 + account_id * 17
            account_values.append(f"({account_id},'r{account_id % 8}',{balance})")
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.account_balances "
                f"(account_id, region_code, balance_cents) VALUES {','.join(account_values)}"
            ),
            "load account balances",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.order_event_log "
                "(event_type, tenant_id, payload, created_at) "
                "SELECT 'seed', tenant_id, CONCAT('seed-', order_id), created_at "
                f"FROM {self.db}.order_events WHERE order_id <= 600"
            ),
            "seed order event log",
        )

    def _load_operational_tables(self, env) -> None:
        service_rows = (
            (
                self.target_service_id, self.target_owner_type, self.target_changefeed_id, 517950000000000000,
                "NOW() - INTERVAL 27 HOUR", 86400, "NOW() - INTERVAL 26 HOUR", 1,
                "historical", "orphaned", "R-8421",
                "operator lease ended; final reconciliation is recorded in the review register",
            ),
            ("ticdc-default-ledger-live-v2", "ticdc", "ledger-live-v2", 540000000000000000,
             "NOW() - INTERVAL 2 HOUR", 86400, "NOW() - INTERVAL 1 MINUTE", 1,
             "critical", "registered", "RET-3103", "financial ledger feed is serving current traffic"),
            ("ticdc-default-warehouse-hourly", "ticdc", "warehouse-hourly", 539999999999000000,
             "NOW() - INTERVAL 3 HOUR", 86400, "NOW() - INTERVAL 2 MINUTE", 1,
             "analytics", "registered", "RET-3102", "warehouse feed is inside the normal review window"),
            ("br-nightly-full-20260801", "br", "nightly-full-backup", 539999999998000000,
             "NOW() - INTERVAL 4 HOUR", 43200, "NOW() - INTERVAL 3 MINUTE", 1,
             "backup", "registered", "RET-3104", "nightly backup owner is inside the approved window"),
            ("ticdc-default-analytics-pause-2026w31", "ticdc", "analytics-pause-2026w31", 530000000000000000,
             "NOW() - INTERVAL 9 HOUR", 86400, "NOW() - INTERVAL 4 MINUTE", 1,
             "analytics", "maintenance", "RET-3111", "scheduled analytics pause has an open change record"),
            ("dm-default-region-mirror", "dm", "region-mirror", 529000000000000000,
             "NOW() - INTERVAL 10 HOUR", 86400, "NOW() - INTERVAL 2 MINUTE", 1,
             "replication", "registered", "RET-3112", "regional mirror is current despite a longer checkpoint window"),
            ("ticdc-default-orders-replay", "ticdc", "orders-replay", 528000000000000000,
             "NOW() - INTERVAL 11 HOUR", 86400, "NOW() - INTERVAL 3 MINUTE", 1,
             "replay", "registered", "RET-3113", "replay feed is bounded by an approved backfill window"),
            ("br-weekly-restore-validation", "br", "weekly-restore-validation", 527000000000000000,
             "NOW() - INTERVAL 8 HOUR", 43200, "NOW() - INTERVAL 5 MINUTE", 1,
             "backup", "validation", "RET-3114", "restore validation is active and must retain its window"),
            ("ticdc-default-compliance-export", "ticdc", "compliance-export", 526000000000000000,
             "NOW() - INTERVAL 6 HOUR", 86400, "NOW() - INTERVAL 2 MINUTE", 1,
             "compliance", "registered", "RET-3115", "compliance export has a current downstream consumer"),
            ("ticdc-default-warehouse-backfill", "ticdc", "warehouse-backfill", 525000000000000000,
             "NOW() - INTERVAL 7 HOUR", 86400, "NOW() - INTERVAL 2 MINUTE", 1,
             "analytics", "backfill", "RET-3116", "warehouse backfill is active during the release window"),
            ("dm-default-cold-archive", "dm", "cold-archive", 524000000000000000,
             "NOW() - INTERVAL 5 HOUR", 86400, "NOW() - INTERVAL 4 MINUTE", 1,
             "archive", "registered", "RET-3117", "cold archive stream has a current sink"),
            ("ticdc-default-inventory-delta", "ticdc", "inventory-delta", 523000000000000000,
             "NOW() - INTERVAL 4 HOUR", 86400, "NOW() - INTERVAL 2 MINUTE", 1,
             "critical", "registered", "RET-3118", "inventory delta feed follows the order writer"),
            ("ticdc-default-batch-export", "ticdc", "batch-export", 522000000000000000,
             "NOW() - INTERVAL 9 HOUR", 86400, "NOW() - INTERVAL 3 MINUTE", 1,
             "analytics", "registered", "RET-3119", "batch export has a current checkpoint owner"),
            ("ticdc-default-feature-sandbox", "ticdc", "feature-sandbox", 521000000000000000,
             "NOW() - INTERVAL 12 HOUR", 86400, "NOW() - INTERVAL 5 MINUTE", 1,
             "sandbox", "paused", "RET-3120", "sandbox pause is covered by an open review"),
            ("ticdc-default-legacy-report-2025", "ticdc", "legacy-report-2025", 520000000000000000,
             "NOW() - INTERVAL 9 HOUR", 86400, "NOW() - INTERVAL 8 MINUTE", 1,
             "historical", "orphaned", "RET-3121", "legacy report migration is incomplete; owner ticket remains open"),
            ("dm-default-delivery-replay", "dm", "delivery-replay", 519000000000000000,
             "NOW() - INTERVAL 10 HOUR", 86400, "NOW() - INTERVAL 4 MINUTE", 1,
             "replay", "registered", "RET-3122", "delivery replay is retained for a current reconciliation"),
            ("br-default-cold-restore", "br", "cold-restore", 518000000000000000,
             "NOW() - INTERVAL 12 HOUR", 43200, "NOW() - INTERVAL 5 MINUTE", 1,
             "backup", "validation", "RET-3123", "cold restore validation remains inside its checkpoint window"),
            ("svc-3b18", "ticdc", "cf-3b18", 517960000000000000,
             "NOW() - INTERVAL 24 HOUR", 86400, "NOW() - INTERVAL 2 DAY", 1,
             "historical", "orphaned", "R-7314", "runtime is stopped but an approved retention exception remains active"),
            ("svc-4c91", "br", "cf-4c91", 517970000000000000,
             "NOW() - INTERVAL 23 HOUR", 43200, "NOW() - INTERVAL 3 DAY", 1,
             "backup", "orphaned", "R-7315", "recovery evidence remains inside the approved validation window"),
            ("svc-5d27", "ticdc", "cf-5d27", 517980000000000000,
             "NOW() - INTERVAL 22 HOUR", 86400, "NOW() - INTERVAL 2 DAY", 1,
             "analytics", "orphaned", "R-7316", "the migration replay still has an open change record"),
            ("svc-6e44", "dm", "cf-6e44", 517990000000000000,
             "NOW() - INTERVAL 21 HOUR", 86400, "NOW() - INTERVAL 4 DAY", 1,
             "replay", "orphaned", "R-7317", "the delivery replay remains business-authorized"),
            ("svc-7a83", "br", "cf-7a83", 518000000000000000,
             "NOW() - INTERVAL 20 HOUR", 43200, "NOW() - INTERVAL 5 DAY", 1,
             "compliance", "orphaned", "R-7318", "compliance acknowledgement is still pending"),
            ("br-default-legal-hold-2025", "br", "legal-hold-2025", 518100000000000000,
             "NOW() - INTERVAL 8 HOUR", 43200, "NOW() - INTERVAL 30 DAY", 1,
             "compliance", "orphaned", "OPS-4924", "owner heartbeat is intentionally absent while the legal hold remains active"),
            ("ticdc-default-legacy-archive", "ticdc", "legacy-archive", 410000000000000000,
             "NOW() - INTERVAL 40 DAY", 86400, "NOW() - INTERVAL 39 DAY", 0,
             "historical", "orphaned", "RET-3091", "inactive archive row retained for historical audit"),
            ("ticdc-default-migration-quarantine", "ticdc", "migration-quarantine", 420000000000000000,
             "NOW() - INTERVAL 28 DAY", 86400, "NOW() - INTERVAL 27 DAY", 0,
             "migration", "quarantined", "RET-3092", "inactive migration row awaits archive evidence"),
            ("dm-default-failed-bootstrap", "dm", "failed-bootstrap", 430000000000000000,
             "NOW() - INTERVAL 20 DAY", 86400, "NOW() - INTERVAL 19 DAY", 0,
             "migration", "quarantined", "RET-3093", "inactive bootstrap row is excluded from the active window"),
        )
        if self.focused_fixture:
            service_rows = tuple(row for row in service_rows if row[0] in self._ledger_service_ids)
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.retention_owner_ledger "
                "(service_id, owner_type, owner_detail, safe_point_tso, safe_point_time, ttl_seconds, "
                "last_heartbeat_at, active, retention_class, registration_state, ticket_ref, notes) VALUES "
                + ",".join(
                    f"('{service_id}','{owner_type}','{owner_detail}',{tso},{safe_point_time},{ttl},"
                    f"{heartbeat},{active},'{retention_class}','{registration_state}','{ticket_ref}','{notes}')"
                    for service_id, owner_type, owner_detail, tso, safe_point_time, ttl, heartbeat, active,
                    retention_class, registration_state, ticket_ref, notes in service_rows
                )
            ),
            "load retention owner ledger",
        )
        changefeed_rows = (
            (
                self.target_changefeed_id, self.target_service_id, "default", "stopped", "missing",
                517950000000000000, 517950000000100000, "NOW() - INTERVAL 27 HOUR",
                "NOW() - INTERVAL 26 HOUR", 97200, f"blackhole://{self.target_changefeed_id}", "decommissioned",
                "R-8421", "audit", "capture lease ended after the final reconciliation review",
            ),
            ("ledger-live-v2", "ticdc-default-ledger-live-v2", "default", "normal", "running",
             540000000000000000, 540000000001000000, "NOW() - INTERVAL 2 HOUR", "NOW() - INTERVAL 1 MINUTE",
             120, "mysql://ledger-downstream:4000", "active", "RET-3103", "financial", "active financial ledger replication"),
            ("warehouse-hourly", "ticdc-default-warehouse-hourly", "default", "normal", "running",
             539999999999000000, 540000000000500000, "NOW() - INTERVAL 3 HOUR", "NOW() - INTERVAL 2 MINUTE",
             180, "kafka://warehouse-hourly", "active", "RET-3102", "analytics", "active warehouse replication"),
            ("analytics-pause-2026w31", "ticdc-default-analytics-pause-2026w31", "default", "paused", "maintenance",
             530000000000000000, 530000000000500000, "NOW() - INTERVAL 9 HOUR", "NOW() - INTERVAL 4 MINUTE",
             14400, "kafka://analytics-pause", "maintenance", "RET-3111", "analytics", "planned pause with an open change record"),
            ("region-mirror", "dm-default-region-mirror", "region-a", "normal", "running",
             529000000000000000, 529000000001000000, "NOW() - INTERVAL 10 HOUR", "NOW() - INTERVAL 2 MINUTE",
             9000, "mysql://region-mirror:4000", "active", "RET-3112", "replication", "regional mirror has current owner heartbeats"),
            ("orders-replay", "ticdc-default-orders-replay", "default", "normal", "running",
             528000000000000000, 528000000001000000, "NOW() - INTERVAL 11 HOUR", "NOW() - INTERVAL 3 MINUTE",
             7200, "kafka://orders-replay", "backfill", "RET-3113", "replay", "approved order replay window"),
            ("weekly-restore-validation", "br-weekly-restore-validation", "default", "normal", "running",
             527000000000000000, 527000000001000000, "NOW() - INTERVAL 8 HOUR", "NOW() - INTERVAL 5 MINUTE",
             3600, "s3://restore-validation", "validation", "RET-3114", "backup", "backup restore validation feed"),
            ("compliance-export", "ticdc-default-compliance-export", "default", "normal", "running",
             526000000000000000, 526000000001000000, "NOW() - INTERVAL 6 HOUR", "NOW() - INTERVAL 2 MINUTE",
             1800, "s3://compliance-export", "active", "RET-3115", "compliance", "current compliance export"),
            ("warehouse-backfill", "ticdc-default-warehouse-backfill", "default", "normal", "running",
             525000000000000000, 525000000001000000, "NOW() - INTERVAL 7 HOUR", "NOW() - INTERVAL 2 MINUTE",
             3600, "kafka://warehouse-backfill", "backfill", "RET-3116", "analytics", "release backfill with active owner"),
            ("cold-archive", "dm-default-cold-archive", "archive", "normal", "running",
             524000000000000000, 524000000001000000, "NOW() - INTERVAL 5 HOUR", "NOW() - INTERVAL 4 MINUTE",
             2400, "mysql://cold-archive:4000", "active", "RET-3117", "archive", "current cold archive stream"),
            ("inventory-delta", "ticdc-default-inventory-delta", "default", "normal", "running",
             523000000000000000, 523000000001000000, "NOW() - INTERVAL 4 HOUR", "NOW() - INTERVAL 2 MINUTE",
             1800, "kafka://inventory-delta", "active", "RET-3118", "critical", "current inventory delta stream"),
            ("batch-export", "ticdc-default-batch-export", "default", "normal", "running",
             522000000000000000, 522000000001000000, "NOW() - INTERVAL 9 HOUR", "NOW() - INTERVAL 3 MINUTE",
             5400, "s3://batch-export", "active", "RET-3119", "analytics", "current batch export"),
            ("feature-sandbox", "ticdc-default-feature-sandbox", "sandbox", "stopped", "missing",
             521000000000000000, 521000000000500000, "NOW() - INTERVAL 12 HOUR", "NOW() - INTERVAL 5 MINUTE",
             14400, "blackhole://feature-sandbox", "paused", "RET-3120", "sandbox", "sandbox paused under an open review"),
            ("legacy-report-2025", "ticdc-default-legacy-report-2025", "default", "stopped", "missing",
             520000000000000000, 520000000000500000, "NOW() - INTERVAL 9 HOUR", "NOW() - INTERVAL 8 MINUTE",
             86400, "s3://legacy-report", "migration", "RET-3121", "historical", "legacy report migration is not closed"),
            ("delivery-replay", "dm-default-delivery-replay", "region-b", "normal", "running",
             519000000000000000, 519000000001000000, "NOW() - INTERVAL 10 HOUR", "NOW() - INTERVAL 4 MINUTE",
             4800, "mysql://delivery-replay:4000", "active", "RET-3122", "replay", "current delivery reconciliation"),
            ("cold-restore", "br-default-cold-restore", "default", "normal", "running",
             518000000000000000, 518000000001000000, "NOW() - INTERVAL 12 HOUR", "NOW() - INTERVAL 5 MINUTE",
             5400, "s3://cold-restore", "validation", "RET-3123", "backup", "current cold restore validation"),
            ("cf-3b18", "svc-3b18", "default", "stopped", "missing",
             517960000000000000, 517960000000500000, "NOW() - INTERVAL 24 HOUR", "NOW() - INTERVAL 2 DAY",
             90000, "s3://sink-3b18", "historical", "R-7314", "archive", "approved retention exception remains pending"),
            ("cf-4c91", "svc-4c91", "default", "stopped", "missing",
             517970000000000000, 517970000000500000, "NOW() - INTERVAL 23 HOUR", "NOW() - INTERVAL 3 DAY",
             86400, "s3://sink-4c91", "validation", "R-7315", "backup", "restore audit evidence remains required"),
            ("cf-5d27", "svc-5d27", "default", "stopped", "missing",
             517980000000000000, 517980000000500000, "NOW() - INTERVAL 22 HOUR", "NOW() - INTERVAL 2 DAY",
             82800, "kafka://sink-5d27", "migration", "R-7316", "analytics", "migration replay remains open"),
            ("cf-6e44", "svc-6e44", "region-b", "stopped", "missing",
             517990000000000000, 517990000000500000, "NOW() - INTERVAL 21 HOUR", "NOW() - INTERVAL 4 DAY",
             79200, "mysql://sink-6e44:4000", "replay", "R-7317", "replay", "delivery replay remains authorized"),
            ("cf-7a83", "svc-7a83", "default", "stopped", "missing",
             518000000000000000, 518000000000500000, "NOW() - INTERVAL 20 HOUR", "NOW() - INTERVAL 5 DAY",
             75600, "s3://sink-7a83", "compliance", "R-7318", "compliance", "acknowledgement is pending"),
            ("legal-hold-2025", "br-default-legal-hold-2025", "default", "stopped", "missing",
             518100000000000000, 518100000000500000, "NOW() - INTERVAL 8 HOUR", "NOW() - INTERVAL 30 DAY",
             28800, "s3://legal-hold-2025", "legal_hold", "OPS-4924", "compliance", "archive replay is prohibited until the legal hold release is recorded"),
        )
        if self.focused_fixture:
            changefeed_rows = tuple(row for row in changefeed_rows if row[1] in self._ledger_service_ids)
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.replication_checkpoints "
                "(changefeed_id, service_id, namespace, state, owner_status, checkpoint_tso, resolved_tso, "
                "checkpoint_time, last_heartbeat_at, checkpoint_lag_seconds, sink_uri, lifecycle_stage, "
                "ticket_ref, data_class, notes) VALUES "
                + ",".join(
                    f"('{changefeed_id}','{service_id}','{namespace}','{state}','{owner_status}',"
                    f"{checkpoint_tso},{resolved_tso},{checkpoint_time},{heartbeat},{lag},"
                    f"'{sink_uri}','{lifecycle_stage}','{ticket_ref}','{data_class}','{notes}')"
                    for changefeed_id, service_id, namespace, state, owner_status, checkpoint_tso, resolved_tso,
                    checkpoint_time, heartbeat, lag, sink_uri, lifecycle_stage, ticket_ref, data_class, notes
                    in changefeed_rows
                )
            ),
            "load replication checkpoints",
        )
        self._load_retention_history(env)
        self._load_capacity_samples(env)
        review_queue_rows = (
            "('RET-3102','warehouse-hourly','info','open','replication',NOW() - INTERVAL 3 DAY,'routine lag review for an active warehouse feed')",
            "('RET-3103','ledger-live-v2','info','open','replication',NOW() - INTERVAL 4 DAY,'financial feed is healthy but noisy in the TopSQL window')",
            "('RET-3104','nightly-full-backup','info','open','backup',NOW() - INTERVAL 5 DAY,'backup owner is inside the approved retention window')",
            "('R-8421','svc-7f2a','warning','closed','replication',NOW() - INTERVAL 9 DAY,'decommission evidence and final owner reconciliation are recorded')",
            "('RET-3111','analytics-pause-2026w31','warning','open','change',NOW() - INTERVAL 2 DAY,'planned pause awaits the next release window')",
            "('RET-3112','region-mirror','info','open','replication',NOW() - INTERVAL 6 DAY,'regional mirror checkpoint is within the review budget')",
            "('RET-3113','orders-replay','warning','open','backfill',NOW() - INTERVAL 1 DAY,'approved order replay remains in progress')",
            "('RET-3114','weekly-restore-validation','info','open','backup',NOW() - INTERVAL 8 DAY,'restore validation sample is still required')",
            "('RET-3115','compliance-export','info','open','compliance',NOW() - INTERVAL 7 DAY,'compliance downstream acknowledgement is current')",
            "('RET-3116','warehouse-backfill','warning','open','backfill',NOW() - INTERVAL 2 DAY,'release backfill is expected to retain its checkpoint')",
            "('RET-3117','cold-archive','info','open','archive',NOW() - INTERVAL 5 DAY,'cold archive reconciliation is active')",
            "('RET-3118','inventory-delta','info','open','replication',NOW() - INTERVAL 3 DAY,'inventory stream is part of current checkout traffic')",
            "('RET-3119','batch-export','info','open','analytics',NOW() - INTERVAL 4 DAY,'batch export has a current owner heartbeat')",
            "('RET-3120','feature-sandbox','warning','open','change',NOW() - INTERVAL 10 DAY,'sandbox pause has an open change record')",
            "('RET-3121','legacy-report-2025','warning','open','migration',NOW() - INTERVAL 12 DAY,'legacy migration is incomplete and must not be retired')",
            "('RET-3122','delivery-replay','info','open','replay',NOW() - INTERVAL 6 DAY,'delivery reconciliation remains active')",
            "('RET-3123','cold-restore','info','open','backup',NOW() - INTERVAL 11 DAY,'cold restore validation has not expired')",
            "('R-7314','svc-3b18','warning','open','archive',NOW() - INTERVAL 14 DAY,'approved archive replay remains pending')",
            "('R-7315','svc-4c91','info','open','backup',NOW() - INTERVAL 13 DAY,'restore audit evidence is still required')",
            "('R-7316','svc-5d27','warning','open','migration',NOW() - INTERVAL 12 DAY,'warehouse migration replay remains open')",
            "('R-7317','svc-6e44','warning','open','replay',NOW() - INTERVAL 11 DAY,'delivery replay remains business-authorized')",
            "('R-7318','svc-7a83','info','open','compliance',NOW() - INTERVAL 10 DAY,'compliance acknowledgement is pending')",
            "('RET-3099','retention-dashboard','info','open','observability',NOW() - INTERVAL 13 DAY,'dashboard sampling produces normal review noise')",
        )
        if self.focused_fixture:
            focused_tickets = ("R-8421", "RET-3102", "RET-3103", "RET-3104", "OPS-4924")
            review_queue_rows = tuple(
                row for row in review_queue_rows if row.split("'")[1] in focused_tickets
            )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.review_queue "
                "(ticket_id, owner_hint, severity, status, category, opened_at, notes) VALUES "
                + ",".join(review_queue_rows)
            ),
            "load retention review queue",
        )
        exception_rows = (
            "('EX-48291'," + repr(self.target_service_id) + ", 'released', NOW() - INTERVAL 1 HOUR, 'R-8421', 'final closeout and owner reconciliation are complete')",
            "('EX-48292','br-default-legal-hold-2025','active',NOW() + INTERVAL 14 DAY,'OPS-4924','regulatory hold blocks retirement despite an absent runtime owner')",
            "('EX-48293','ticdc-default-feature-sandbox','active',NOW() + INTERVAL 2 DAY,'RET-3120','sandbox pause remains inside an approved change window')",
            "('EX-48294','ticdc-default-legacy-report-2025','active',NOW() + INTERVAL 10 DAY,'RET-3121','migration closeout is pending')",
            "('EX-48295','br-default-cold-restore','active',NOW() + INTERVAL 1 DAY,'RET-3123','restore validation evidence is still required')",
            "('EX-48296','ticdc-default-orders-replay','active',NOW() + INTERVAL 3 DAY,'RET-3113','backfill replay remains business-authorized')",
            "('EX-48297','svc-3b18','active',NOW() + INTERVAL 3 DAY,'R-7314','approved archive replay remains pending')",
            "('EX-48298','svc-4c91','active',NOW() + INTERVAL 2 DAY,'R-7315','restore audit evidence is still required')",
            "('EX-48299','svc-5d27','active',NOW() + INTERVAL 2 DAY,'R-7316','warehouse migration replay remains open')",
            "('EX-48300','svc-6e44','active',NOW() + INTERVAL 4 DAY,'R-7317','delivery replay remains business-authorized')",
            "('EX-48301','svc-7a83','active',NOW() + INTERVAL 5 DAY,'R-7318','compliance acknowledgement is pending')",
        )
        if self.focused_fixture:
            exception_rows = tuple(
                row
                for row in exception_rows
                if any(f"'{service_id}'" in row for service_id in self._ledger_service_ids)
            )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.retention_exceptions "
                "(exception_id, service_id, exception_state, hold_until, approval_ref, rationale) VALUES "
                + ",".join(exception_rows)
            ),
            "load retention exception register",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.retention_reconciliation "
                "(service_id, changefeed_id, reconciliation_state, observation_count, required_observations, "
                "last_observed_at, stable_at, closeout_cutoff_tso, notes) VALUES "
                f"({self.target_service_id!r}, {self.target_changefeed_id!r}, 'pending', 0, "
                f"{self.closeout_required_observations}, NULL, NULL, 517950000000000000, "
                "'controller waits for repeated post-closeout observations before releasing the effective safepoint')"
            ),
            "load retention reconciliation controller state",
        )

    def _load_retention_history(self, env) -> None:
        values = []
        for sample_no in range(1, 37):
            age = 27 + (36 - sample_no)
            retained = 19000000 + sample_no * 240000
            disk = 20480 + sample_no * 52
            values.append(
                f"({sample_no},NOW() - INTERVAL {37 - sample_no} HOUR,"
                f"'{self.target_service_id}',{age},{retained},{disk},'tikv-gc',"
                "'effective retention window follows the oldest active owner')"
            )
        if not self.focused_fixture:
            for offset in range(36):
                sample_no = 37 + offset
                values.append(
                    f"({sample_no},NOW() - INTERVAL {36 - offset} HOUR,"
                    "'ticdc-default-legacy-report-2025',9,"
                    f"{8500000 + offset * 60000},{16800 + offset * 12},'tikv-compaction',"
                    "'background compaction and business writes remain in the review window')"
                )
        sample_no = 73
        decoy_services = self.protected_service_ids[-1:] if self.focused_fixture else self.protected_service_ids[-5:]
        for decoy_index, service_id in enumerate(decoy_services):
            for offset in range(36):
                age = 24 - decoy_index + (35 - offset)
                retained = 9200000 + decoy_index * 350000 + offset * 85000
                disk = 17100 + decoy_index * 180 + offset * 14
                values.append(
                    f"({sample_no},NOW() - INTERVAL {36 - offset} HOUR,"
                    f"'{service_id}',{age},{retained},{disk},'owner-history',"
                    "'stopped runtime has a valid exception or open closeout dependency')"
                )
                sample_no += 1
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.retention_history "
                "(sample_no, sampled_at, anchor_service_id, safe_point_age_hours, retained_versions_estimate, "
                f"tikv_disk_used_mb, source, notes) VALUES {','.join(values)}"
            ),
            "load retention history",
        )

    def _load_capacity_samples(self, env) -> None:
        values = []
        sample_no = 1
        sample_specs = (
            ("mvcc_version_retention", 12600, 242.4, "tikv_gc", "retained-version footprint in the historical capacity window"),
            ("snapshot_restore_staging", 11800, 318.6, "backup", "isolated restore staging grows during recovery validation"),
            ("cdc_sorter_archive", 10400, 287.2, "ticdc", "stopped-feed sorter archives remain inside a replay window"),
            ("compaction_debt_shadow", 9800, 271.4, "tikv_gc", "compaction debt follows a high-write tenant cohort"),
            ("migration_replay_staging", 11200, 259.8, "migration", "migration replay staging is bounded by an open change record"),
            ("raft_snapshot_staging", 10800, 251.7, "tikv_raft", "raft snapshots grow while a restore audit is active"),
            ("order_event_log", 8800, 98.2, "business_table", "normal audit event growth from checkout traffic"),
            ("finance_rollup_cache", 5200, 76.8, "olap_job", "report cache refresh writes temporary rows"),
            ("br_backup_staging", 4300, 44.1, "backup", "backup staging follows the nightly window"),
            ("top_sql_sampling", 2100, 18.7, "observability", "monitoring sample churn"),
            ("raft_log_retention", 7400, 61.2, "tikv_raft", "normal raft log retention during writes"),
            ("ddl_backfill_queue", 6900, 55.4, "ddl_maintenance", "release backfill produces expected files"),
            ("region_meta_snapshot", 3500, 21.6, "pd_metadata", "region metadata snapshots are periodic"),
            ("customer_activity_rollup", 6100, 47.5, "business_table", "customer activity dashboard refresh"),
            ("api_request_archive", 5700, 39.8, "business_table", "request archive follows active traffic"),
            ("inventory_delta_buffer", 4600, 32.7, "ticdc_sink", "inventory downstream buffer is bounded"),
            ("warehouse_export_staging", 6300, 51.3, "analytics", "warehouse export staging is active"),
            ("compliance_export_staging", 4100, 29.1, "compliance", "compliance export produces scheduled files"),
            ("orders_replay_buffer", 5300, 42.2, "replay", "order replay buffer follows approved backfill"),
            ("delivery_replay_buffer", 5000, 35.6, "replay", "delivery reconciliation buffer is active"),
            ("cold_archive_manifest", 3900, 24.8, "archive", "cold archive manifests are retained"),
            ("analytics_pause_window", 4500, 30.5, "analytics", "paused analytics feed has a bounded window"),
            ("restore_validation_cache", 4700, 28.6, "backup", "restore validation cache is expected"),
            ("feature_sandbox_events", 2800, 17.4, "sandbox", "sandbox event volume is low"),
            ("mysql_binlog_bridge", 3600, 26.9, "dm", "bridge checkpoint files are current"),
            ("region_mirror_staging", 4200, 31.8, "dm", "regional mirror staging follows traffic"),
            ("session_audit_archive", 5100, 33.1, "business_table", "session audit retention is scheduled"),
            ("payment_reconciliation", 4800, 37.6, "business_table", "payment reconciliation rows are current"),
            ("order_status_history", 7200, 64.2, "business_table", "order status history is a normal growth source"),
            ("daily_summary_rollup", 5600, 41.5, "olap_job", "daily summary refresh is scheduled"),
            ("object_store_manifest", 3300, 19.9, "backup", "object store manifests remain bounded"),
            ("cdc_error_archive", 3000, 16.8, "ticdc", "CDC error archive has low volume"),
            ("monitoring_snapshot", 2500, 14.7, "observability", "monitoring snapshots are normal"),
            ("query_plan_history", 2700, 13.4, "observability", "plan history sampling is normal"),
            ("tenant_quota_audit", 3100, 18.1, "governance", "tenant quota audits are periodic"),
            ("audit_event_archive", 4400, 27.3, "business_table", "audit event archive follows normal traffic"),
            ("tenant_usage_rollup", 5200, 36.4, "olap_job", "tenant usage rollup is refreshed on schedule"),
            ("session_history", 3700, 22.5, "business_table", "session history is retained for routine review"),
            ("payment_attempt_log", 4900, 34.2, "business_table", "payment attempts follow checkout volume"),
            ("fraud_feature_snapshot", 3400, 20.8, "olap_job", "fraud feature snapshots are bounded"),
            ("shipping_event_buffer", 4700, 31.4, "business_table", "shipping events remain inside normal retention"),
            ("support_case_archive", 2900, 15.9, "business_table", "support case archive has low daily growth"),
            ("webhook_delivery_log", 4100, 25.6, "business_table", "webhook delivery log follows partner traffic"),
            ("pricing_snapshot", 3600, 23.7, "business_table", "pricing snapshots are generated by the catalog job"),
            ("catalog_change_log", 3300, 18.9, "business_table", "catalog change log is a normal audit source"),
            ("user_preference_history", 2700, 13.8, "business_table", "user preference history is low volume"),
            ("merchant_payout_rollup", 5800, 43.7, "olap_job", "merchant payout rollup runs in the finance window"),
            ("tax_report_staging", 4600, 29.4, "olap_job", "tax report staging is cleared by the scheduled job"),
            ("marketing_segment_cache", 3100, 17.2, "olap_job", "marketing segment cache refresh is routine"),
            ("search_index_queue", 4300, 30.1, "business_table", "search indexing queue is bounded"),
            ("recommendation_features", 3900, 26.5, "olap_job", "recommendation feature refresh is periodic"),
            ("warehouse_slot_events", 5500, 38.2, "analytics", "warehouse slot event history is normal"),
            ("supplier_sync_staging", 3200, 19.5, "replication", "supplier synchronization staging is current"),
            ("refund_case_history", 3800, 24.3, "business_table", "refund case history tracks payment traffic"),
            ("chargeback_evidence", 3500, 21.9, "compliance", "chargeback evidence is retained for review"),
            ("risk_decision_log", 4000, 28.7, "compliance", "risk decisions are archived for audit"),
            ("invoice_export_cache", 5100, 35.1, "analytics", "invoice export cache is refreshed daily"),
            ("notification_delivery", 3000, 16.4, "business_table", "notification delivery history grows with active traffic"),
            ("partner_settlement", 5300, 40.5, "business_table", "partner settlement data is inside the ledger window"),
            ("storefront_activity", 4500, 32.8, "business_table", "storefront activity follows customer traffic"),
            ("api_latency_archive", 2800, 14.9, "observability", "API latency archive is sampled periodically"),
            ("job_execution_history", 2600, 12.6, "observability", "job execution history is low volume"),
            ("schema_change_audit", 2400, 11.8, "ddl_maintenance", "schema change audit records release activity"),
            ("region_capacity_forecast", 4800, 33.5, "capacity", "region capacity forecast is refreshed hourly"),
            ("quota_snapshot", 2300, 10.9, "governance", "quota snapshots are periodic"),
        )
        if self.focused_fixture:
            sample_specs = sample_specs[:8]
        else:
            sample_specs = sample_specs + tuple(
                (
                    f"tenant_capacity_shadow_{index:03d}",
                    1800 + (index % 23) * 137,
                    10.0 + (index % 19) * 1.7,
                    ("business_table", "olap_job", "observability", "governance")[index % 4],
                    "tenant-level capacity series from routine business and platform reporting",
                )
                for index in range(1, 451)
            )
        for name, base_mb, growth, source, notes in sample_specs:
            for offset in range(48):
                values.append(
                    f"({sample_no},'{name}',NOW() - INTERVAL {48 - offset} HOUR,"
                    f"{base_mb + offset * int(growth)},{growth},'{source}','{notes}')"
                )
                sample_no += 1
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.capacity_samples "
                "(sample_no, sample_name, sampled_at, observed_mb, growth_mb_per_day, source, notes) "
                f"VALUES {','.join(values)}"
            ),
            "load capacity samples",
        )

    def _create_views(self, env) -> None:
        pending_target = (
            f"(s.service_id = {self.target_service_id!r} AND EXISTS ("
            f"SELECT 1 FROM {self.db}.retention_reconciliation r "
            "WHERE r.service_id = s.service_id AND r.reconciliation_state <> 'stable'))"
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE VIEW {self.db}.effective_retention_window AS "
                "SELECT safe_point_tso, safe_point_time, "
                "TIMESTAMPDIFF(HOUR, safe_point_time, NOW()) AS safe_point_age_hours, "
                f"(SELECT COUNT(*) FROM {self.db}.retention_owner_ledger s "
                f"WHERE s.active = 1 OR {pending_target}) AS active_service_count "
                f"FROM {self.db}.retention_owner_ledger s "
                f"WHERE active = 1 OR {pending_target} ORDER BY safe_point_tso ASC LIMIT 1"
            ),
            "create effective retention window view",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE VIEW {self.db}.owner_lineage_matrix AS "
                "SELECT s.service_id, s.owner_type, s.owner_detail, s.safe_point_time, "
                "TIMESTAMPDIFF(HOUR, s.safe_point_time, NOW()) AS safe_point_age_hours, "
                "s.active, s.retention_class, s.registration_state, s.ticket_ref, "
                "s.last_heartbeat_at, s.notes, COALESCE(r.reconciliation_state, 'not_tracked') AS reconciliation_state "
                f"FROM {self.db}.retention_owner_ledger s "
                f"LEFT JOIN {self.db}.retention_reconciliation r ON r.service_id = s.service_id "
                f"WHERE s.active = 1 OR {pending_target} ORDER BY s.safe_point_tso ASC"
            ),
            "create owner lineage matrix view",
        )

    def _verify_fault_state(self, env) -> None:
        effective = json_object(
            env.execute_sql(
                f"SELECT service_id FROM {self.db}.retention_owner_ledger "
                "WHERE active = 1 ORDER BY safe_point_tso ASC LIMIT 1"
            ),
            "verify effective retention window",
        )
        if effective["result"] != [[self.target_service_id]]:
            raise RuntimeError(
                "effective retention window is not pinned by target owner: "
                f"target={self.target_service_id!r}, result={effective['result']!r}"
            )
        accounts = json_object(
            env.execute_sql(f"SELECT COUNT(*), SUM(balance_cents) FROM {self.db}.account_balances"),
            "verify account balance ledger",
        )
        rows = accounts["result"]
        if (
            len(rows) != 1
            or int(rows[0][0]) != self.protected_account_count
            or int(rows[0][1]) != self.protected_account_balance_cents
        ):
            raise RuntimeError(
                "account balance ledger mismatch: "
                f"expected={[self.protected_account_count, self.protected_account_balance_cents]!r}, "
                f"result={accounts['result']!r}"
            )
