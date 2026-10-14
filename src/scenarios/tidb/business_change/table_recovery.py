from dataclasses import dataclass, replace
from datetime import datetime

from src.workloads.specs import WorkloadProfile
from src.protocols.report import structured_reference_report
from src.scenarios.evaluation.tidb.business_change.table_recovery import (
    TidbBusinessChangeTableRecoveryEvaluatorCase,
    TidbBusinessChangeTableRecoveryForPaymentEventsEvaluatorCase,
)

from src.workloads.specs import BackgroundWorkloadSpec
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


_BC07_TIDB_RELEASE = replace(
    TIDB_V8_1_0,
    tidb_extra_args=(*TIDB_V8_1_0.tidb_extra_args, "--lease=1s"),
)


def _background_workload(
    database: str,
    service_name: str,
    environment: str,
    logical_table: str,
    missing_cache_table: str,
    table: str,
    archive_table: str,
    audit_table: str,
    release_registry_table: str,
    release_control_table: str,
    release_ledger_table: str,
    incident_context_table: str,
    release_transition_table: str,
    release_binding_table: str,
) -> BackgroundWorkloadSpec:
    profile_prefix = logical_table.removesuffix("_events")
    return BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name=f"{profile_prefix}_api_recent_lookup",
                sql=(
                    f"SELECT event_id, amount_cents FROM {database}.{table} "
                    "WHERE tenant_id BETWEEN 7 AND 12 ORDER BY event_id DESC LIMIT 50"
                ),
                qps=0.75,
                tier="LIGHT",
                application_name=service_name,
            ),
            WorkloadProfile(
                name=f"{profile_prefix}_reconciliation_rollup",
                sql=(
                    f"SELECT tenant_id, event_type, COUNT(*), SUM(amount_cents) "
                    f"FROM {database}.{table} GROUP BY tenant_id, event_type "
                    "ORDER BY tenant_id, event_type"
                ),
                qps=0.35,
                tier="MEDIUM",
                application_name="reconciliation-worker",
            ),
            WorkloadProfile(
                name="release_archive_preview",
                sql=(
                    f"SELECT event_type, COUNT(*), SUM(amount_cents) FROM {database}.{archive_table} "
                    "GROUP BY event_type ORDER BY event_type"
                ),
                qps=0.45,
                tier="LIGHT",
                application_name="release-dashboard",
            ),
            WorkloadProfile(
                name="release_audit_window",
                sql=(
                    f"SELECT audit_id, action, created_at FROM {database}.{audit_table} "
                    "WHERE created_at >= NOW() - INTERVAL 7 DAY ORDER BY audit_id DESC LIMIT 40"
                ),
                qps=0.4,
                tier="LIGHT",
                application_name="release-audit",
            ),
            WorkloadProfile(
                name="ddl_history_refresh",
                sql=(
                    "SELECT JOB_ID, DB_NAME, TABLE_NAME, JOB_TYPE, STATE "
                    "FROM information_schema.ddl_jobs ORDER BY JOB_ID DESC LIMIT 12"
                ),
                qps=0.3,
                tier="MONITOR",
                application_name="schema-registry",
            ),
            WorkloadProfile(
                name="gc_window_probe",
                sql=(
                    "SELECT VARIABLE_NAME, VARIABLE_VALUE FROM mysql.tidb "
                    "WHERE VARIABLE_NAME IN ('tikv_gc_safe_point', 'tikv_gc_last_run_time')"
                ),
                qps=0.25,
                tier="MONITOR",
                application_name="retention-monitor",
            ),
            WorkloadProfile(
                name=f"missing_{profile_prefix}_cache_refresh",
                sql=f"SELECT COUNT(*) FROM {database}.{missing_cache_table}",
                qps=0.2,
                tier="LOG_NOISE",
                application_name="cache-refresher",
            ),
            WorkloadProfile(
                name="release_control_plane_lookup",
                sql=(
                    f"SELECT c.service_name, c.environment, c.region, c.control_role, c.control_key, "
                    f"b.release_id, c.effective_at, c.status, c.traffic_percent, c.control_epoch "
                    f"FROM {database}.{release_control_table} c LEFT JOIN {database}.{release_binding_table} b "
                    f"ON b.control_key=c.control_key WHERE c.environment='{environment}' "
                    "ORDER BY c.effective_at, c.control_id"
                ),
                qps=0.35,
                tier="MONITOR",
                application_name="release-controller",
            ),
            WorkloadProfile(
                name="release_registry_snapshot",
                sql=(
                    f"SELECT release_id, table_id, lifecycle_state, generation, expected_rows, expected_crc, "
                    f"effective_at, change_ticket "
                    f"FROM {database}.{release_registry_table} ORDER BY effective_at"
                ),
                qps=0.3,
                tier="MONITOR",
                application_name="schema-registry",
            ),
            WorkloadProfile(
                name="business_release_ledger_reconcile",
                sql=(
                    f"SELECT r.release_id, r.lifecycle_state, r.expected_rows, l.order_count, "
                    f"r.expected_crc, l.crc FROM {database}.{release_registry_table} r "
                    f"JOIN {database}.{release_ledger_table} l ON l.release_id=r.release_id "
                    "ORDER BY r.effective_at"
                ),
                qps=0.3,
                tier="MEDIUM",
                application_name="ledger-reconciler",
            ),
            WorkloadProfile(
                name="release_ddl_lineage_refresh",
                sql=(
                    f"SELECT d.job_id, d.job_type, d.table_id, r.release_id, r.lifecycle_state "
                    f"FROM information_schema.ddl_jobs d LEFT JOIN {database}.{release_registry_table} r "
                    f"ON d.table_id=r.table_id WHERE d.db_name='{database}' "
                    "ORDER BY d.job_id DESC LIMIT 32"
                ),
                qps=0.28,
                tier="MONITOR",
                application_name="schema-lineage",
            ),
            WorkloadProfile(
                name="release_audit_config_window",
                sql=(
                    f"SELECT audit_id, action, config_key, previous_value, requested_value "
                    f"FROM {database}.{audit_table} WHERE config_key IS NOT NULL ORDER BY audit_id DESC"
                ),
                qps=0.25,
                tier="LIGHT",
                application_name="release-audit",
            ),
            WorkloadProfile(
                name="release_incident_boundary",
                sql=(
                    f"SELECT incident_id, service_name, environment, logical_table, incident_at, "
                    f"last_known_good_at, expected_control_epoch FROM {database}.{incident_context_table} "
                    "ORDER BY incident_id"
                ),
                qps=0.28,
                tier="MONITOR",
                application_name="incident-coordinator",
            ),
            WorkloadProfile(
                name="release_transition_timeline",
                sql=(
                    f"SELECT control_key, transition, occurred_at, traffic_percent, control_epoch, recorded_at, resulting_state, event_key, event_revision, revision_state "
                    f"FROM {database}.{release_transition_table} ORDER BY occurred_at, transition_id LIMIT 64"
                ),
                qps=0.3,
                tier="MONITOR",
                application_name="release-controller",
            ),
            WorkloadProfile(
                name="release_control_epoch_reconcile",
                sql=(
                    f"SELECT c.control_key, b.release_id, c.control_role, c.effective_at, c.status, c.traffic_percent, "
                    f"c.control_epoch, i.incident_at, i.expected_control_epoch "
                    f"FROM {database}.{release_control_table} c "
                    f"LEFT JOIN {database}.{release_binding_table} b ON b.control_key=c.control_key "
                    f"JOIN {database}.{incident_context_table} i ON i.service_name=c.service_name "
                    "AND i.environment=c.environment AND i.logical_table=c.logical_table "
                    f"WHERE c.service_name='{service_name}' AND c.environment='{environment}' "
                    "ORDER BY c.effective_at, c.control_id"
                ),
                qps=0.25,
                tier="MEDIUM",
                application_name="release-reconciler",
            ),
            WorkloadProfile(
                name="release_binding_snapshot",
                sql=(
                    f"SELECT control_key, release_id, binding_state, binding_revision, valid_from, valid_until, recorded_at, change_ticket "
                    f"FROM {database}.{release_binding_table} ORDER BY recorded_at, binding_id"
                ),
                qps=0.24,
                tier="MONITOR",
                application_name="deployment-registry",
            ),
            WorkloadProfile(
                name="release_transition_lineage_join",
                sql=(
                    f"SELECT t.control_key, t.transition, t.occurred_at, b.release_id, b.binding_revision "
                    f"FROM {database}.{release_transition_table} t "
                    f"JOIN {database}.{release_binding_table} b ON b.control_key=t.control_key "
                    "ORDER BY t.occurred_at DESC, t.transition_id DESC LIMIT 64"
                ),
                qps=0.22,
                tier="MONITOR",
                application_name="schema-lineage",
            ),
            WorkloadProfile(
                name="gc_delete_range_probe",
                sql="SELECT COUNT(*) AS pending_delete_ranges FROM mysql.gc_delete_range",
                qps=0.22,
                tier="MONITOR",
                application_name="gc-inspector",
            ),
        ),
        worker_count=8,
        seed=2707,
        warmup_seconds=8,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeTableRecoveryCase(TiDBScenarioCase):
    database: str
    service_name: str
    environment: str
    logical_table: str
    missing_cache_table: str
    table: str
    archive_table: str
    audit_table: str
    ddl_seed_table: str
    release_registry_table: str
    release_control_table: str
    release_ledger_table: str
    incident_context_table: str
    release_transition_table: str
    release_binding_table: str
    incident_at: str
    ddl_history_noise_jobs: int
    source_row_count: int
    expected_event_id_sum: int
    expected_crc: int
    candidate_row_count: int
    decoy_row_count: int
    recovery_gc_lifetime: str
    pre_release_id: str
    target_release_id: str
    canary_release_id: str
    smoke_release_id: str
    hotfix_release_id: str
    rehearsal_release_id: str
    shadow_release_id: str
    rollback_release_id: str
    reference_evidence_counts: tuple[tuple[str, int, int], ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeTableRecoveryForDroppedTableGcRecoveryScenarioCase(
    TidbBusinessChangeTableRecoveryCase
):
    pass


_CASE = TidbBusinessChangeTableRecoveryForDroppedTableGcRecoveryScenarioCase(
    case_id="dropped_table_gc_recovery",
    reference_report=structured_reference_report(
        case_id="dropped_table_gc_recovery",
        factors=(
            "the outage is the exact DROP DDL for the last-known-good serving release at the incident boundary",
            "the table remains recoverable inside the temporary GC window",
        ),
        changes=(
            "recovered the original order_events table from the matching DROP DDL job",
            "restored the GC life time to the baseline after recovery",
        ),
        verification=(
            "row count, CRC, primary/index metadata, and ADMIN CHECK TABLE matched the expected business truth",
            "current online query load recovered without rebuilding from application exports",
        ),
        summary="The reference path recovered the dropped table before GC and verified business correctness.",
    ),
    case_no=0,
    evaluator=TidbBusinessChangeTableRecoveryEvaluatorCase,
    title="Recover the original order-event table from an exact DROP DDL job before GC removes its data.",
    alert=(
        "[CRITICAL] [Order Platform] 查询 benchops.order_events 的订单检索、对账和发布审计接口同时出现 "
        "'table doesn't exist'；数据库节点仍然 Up，其他归档查询正常。请在 GC 可恢复窗口内恢复 "
        "order-api/prod 在事故发生时使用的原始业务表。保留当前在线查询负载，"
        "不要从应用导出重建数据；恢复前必须核对 DDL 历史、GC safe point 和恢复对象，"
        "恢复后必须证明业务真值、主键/索引一致性和 TiDB 表检查均通过，并撤销本次临时保留窗口。"
    ),
    initial_state={
        "status": "business_queries_fail",
        "database": "benchops",
        "table": "order_events_absent",
        "cluster": "healthy",
        "gc_window": "temporarily_extended",
    },
    expected_target={
        "status": "recovered",
        "table_rows": 2000,
        "drop_job_id": "the DROP job for the last-known-good release at the incident boundary from this run",
        "last_known_good_release": "the fully serving release at the incident boundary",
        "crc": 2393356967,
        "admin_check": "empty_success_result",
        "gc_life_time": "restored_to_baseline",
    },
    background_workload=_background_workload(
        "benchops",
        "order-api",
        "prod",
        "order_events",
        "order_cache_refresh_missing",
        "order_events",
        "order_events_archive",
        "release_audit",
        "release_registry",
        "release_control",
        "business_release_ledger",
        "incident_context",
        "release_transition_log",
        "release_binding",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=11,
        environmental_complexity=144 / 195,
        reference_run_ids=(
            "table-recovery-r7-mock-20261012__"
            "tidb_business_change_table_recovery__dropped_table_gc_recovery__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=_BC07_TIDB_RELEASE,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=180,
    ),
    database="benchops",
    service_name="order-api",
    environment="prod",
    logical_table="order_events",
    missing_cache_table="order_cache_refresh_missing",
    table="order_events",
    archive_table="order_events_archive",
    audit_table="release_audit",
    ddl_seed_table="bc07_ddl_seed",
    release_registry_table="release_registry",
    release_control_table="release_control",
    release_ledger_table="business_release_ledger",
    incident_context_table="incident_context",
    release_transition_table="release_transition_log",
    release_binding_table="release_binding",
    incident_at="2026-08-03 11:30:00",
    ddl_history_noise_jobs=24,
    source_row_count=2000,
    expected_event_id_sum=2_001_000,
    expected_crc=2_393_356_967,
    candidate_row_count=2000,
    decoy_row_count=17,
    recovery_gc_lifetime="72h",
    pre_release_id="orders_r4d9",
    target_release_id="orders_r7a2",
    canary_release_id="orders_r1f6",
    smoke_release_id="orders_r8c3",
    hotfix_release_id="orders_r2b5",
    rehearsal_release_id="orders_r6e1",
    shadow_release_id="orders_r9a4",
    rollback_release_id="orders_r3f8",
    reference_evidence_counts=(
        ('schema catalog', 0, 11),
        ('incident context', 1, 0),
        ('controller snapshots', 3, 3),
        ('historical bindings', 4, 6),
        ('controller commands', 17, 19),
        ('publisher leases', 2, 3),
        ('receiver application receipts', 19, 22),
        ('artifact registry', 1, 7),
        ('business ledger', 1, 7),
        ('native DDL history', 1, 66),
        ('native GC boundary', 2, 0),
    ),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeTableRecoveryForDroppedPaymentEventsGcRecoveryScenarioCase(
    TidbBusinessChangeTableRecoveryCase
):
    pass


_PAYMENT_CASE = TidbBusinessChangeTableRecoveryForDroppedPaymentEventsGcRecoveryScenarioCase(
    case_id="dropped_payment_events_gc_recovery",
    reference_report=structured_reference_report(
        case_id="dropped_payment_events_gc_recovery",
        factors=(
            "the payment serving table was dropped from the release serving at the incident boundary",
            "the original table remains recoverable inside the temporary GC window",
        ),
        changes=(
            "recovered the incident-boundary payment release from its matching DROP DDL job",
            "restored the GC lifetime to the baseline after recovery",
        ),
        verification=(
            "payment row count, CRC, primary/index metadata, and ADMIN CHECK TABLE matched business truth",
            "online payment reconciliation recovered without rebuilding from an export",
        ),
        summary="The reference path recovered the dropped payment-events table before GC and verified its business truth.",
    ),
    case_no=1,
    evaluator=TidbBusinessChangeTableRecoveryForPaymentEventsEvaluatorCase,
    title="Recover the incident-boundary payment-events table from the exact DROP DDL job before GC cleanup.",
    alert=(
        "[CRITICAL] [Payment Platform] 查询 benchops_bc07_payments.payment_events 的支付检索、对账和发布审计接口同时出现 "
        "'table doesn't exist'；数据库节点仍然 Up，其他归档查询正常。最近一次 payment release cleanup 可能误删了 "
        "payment_events，但同一逻辑表曾被发布流程重复创建和清理。请在 GC 可恢复窗口内恢复原始业务表，"
        "事故边界为 2026-08-10 16:30:00；请从 incident context 和 release transition history 重建该时刻 "
        "payments-api/prod 实际 serving 的 release，而不是直接采用当前 desired release。保留当前在线查询负载，"
        "不要从应用导出重建数据；恢复前必须核对 DDL 历史、GC safe point 和恢复对象，"
        "恢复后必须证明业务真值、主键/索引一致性和 TiDB 表检查均通过，并撤销本次临时保留窗口。"
    ),
    initial_state={
        "status": "business_queries_fail",
        "database": "benchops_bc07_payments",
        "table": "payment_events_absent",
        "cluster": "healthy",
        "gc_window": "temporarily_extended",
    },
    expected_target={
        "status": "recovered",
        "table_rows": 2000,
        "drop_job_id": "the DROP job for the incident-boundary payment release from this run",
        "last_known_good_release": "the fully serving payment release at the incident boundary",
        "crc": 2846650938,
        "admin_check": "empty_success_result",
        "gc_life_time": "restored_to_baseline",
    },
    background_workload=_background_workload(
        "benchops_bc07_payments",
        "payments-api",
        "prod",
        "payment_events",
        "payment_reconciliation_cache_missing",
        "payment_events",
        "payment_events_archive",
        "payment_release_audit",
        "payment_release_registry",
        "payment_release_control",
        "payment_release_ledger",
        "payment_incident_context",
        "payment_release_transition_log",
        "payment_release_binding",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=8,
        environmental_complexity=112 / 135,
        reference_run_ids=(
            "table-recovery-r2-mock-20261012__"
            "tidb_business_change_table_recovery__dropped_payment_events_gc_recovery__"
            "mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=_BC07_TIDB_RELEASE,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=180,
    ),
    database="benchops_bc07_payments",
    service_name="payments-api",
    environment="prod",
    logical_table="payment_events",
    missing_cache_table="payment_reconciliation_cache_missing",
    table="payment_events",
    archive_table="payment_events_archive",
    audit_table="payment_release_audit",
    ddl_seed_table="payment_bc07_ddl_seed",
    release_registry_table="payment_release_registry",
    release_control_table="payment_release_control",
    release_ledger_table="payment_release_ledger",
    incident_context_table="payment_incident_context",
    release_transition_table="payment_release_transition_log",
    release_binding_table="payment_release_binding",
    incident_at="2026-08-10 16:30:00",
    ddl_history_noise_jobs=24,
    source_row_count=2000,
    expected_event_id_sum=2_001_000,
    expected_crc=2_846_650_938,
    candidate_row_count=2000,
    decoy_row_count=17,
    recovery_gc_lifetime="72h",
    pre_release_id="payments_r4d9",
    target_release_id="payments_r7a2",
    canary_release_id="payments_r1f6",
    smoke_release_id="payments_r8c3",
    hotfix_release_id="payments_r2b5",
    rehearsal_release_id="payments_r6e1",
    shadow_release_id="payments_r9a4",
    rollback_release_id="payments_r3f8",
    reference_evidence_counts=(
        ('schema catalog', 0, 9),
        ('incident context', 1, 0),
        ('controller snapshots', 3, 7),
        ('historical bindings', 4, 6),
        ('controller transitions', 10, 17),
        ('artifact registry', 1, 7),
        ('business ledger', 1, 7),
        ('native DDL history', 1, 59),
        ('native GC boundary', 2, 0),
    ),
)


class TidbBusinessChangeTableRecoveryScenario(TiDBScenario):
    scenario_id = "tidb_business_change_table_recovery"
    description = "Recover an accidentally dropped TiDB business table from the exact DDL job within the GC lifetime."
    cases = (_CASE, _PAYMENT_CASE)

    def build_fault_plan(
        self,
        case: TidbBusinessChangeTableRecoveryCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangeTableRecoveryInjector,
                config={
                    "database": case.database,
                    "service_name": case.service_name,
                    "environment": case.environment,
                    "logical_table": case.logical_table,
                    "missing_cache_table": case.missing_cache_table,
                    "table": case.table,
                    "archive_table": case.archive_table,
                    "audit_table": case.audit_table,
                    "ddl_seed_table": case.ddl_seed_table,
                    "release_registry_table": case.release_registry_table,
                    "release_control_table": case.release_control_table,
                    "release_ledger_table": case.release_ledger_table,
                    "incident_context_table": case.incident_context_table,
                    "release_transition_table": case.release_transition_table,
                    "release_binding_table": case.release_binding_table,
                    "incident_at": case.incident_at,
                    "ddl_history_noise_jobs": case.ddl_history_noise_jobs,
                    "source_row_count": case.source_row_count,
                    "expected_event_id_sum": case.expected_event_id_sum,
                    "expected_crc": case.expected_crc,
                    "candidate_row_count": case.candidate_row_count,
                    "decoy_row_count": case.decoy_row_count,
                    "recovery_gc_lifetime": case.recovery_gc_lifetime,
                    "pre_release_id": case.pre_release_id,
                    "target_release_id": case.target_release_id,
                    "canary_release_id": case.canary_release_id,
                    "smoke_release_id": case.smoke_release_id,
                    "hotfix_release_id": case.hotfix_release_id,
                    "rehearsal_release_id": case.rehearsal_release_id,
                    "shadow_release_id": case.shadow_release_id,
                    "rollback_release_id": case.rollback_release_id,
                },
            ),
        )

from collections.abc import Mapping

from src.database.sql import execute_result_rows
from src.scenarios.faults import FaultLifecycleContext

from src.scenarios.tidb.common import BaseFaultInjector, require_sql_success, validate_sql_identifier


class TidbBusinessChangeTableRecoveryInjector(BaseFaultInjector):
    """Create eight real same-name release generations inside the TiDB GC window."""

    def __init__(self):
        self.database = None
        self.service_name = None
        self.environment = None
        self.logical_table = None
        self.missing_cache_table = None
        self.table = None
        self.archive_table = None
        self.audit_table = None
        self.ddl_seed_table = None
        self.release_registry_table = None
        self.release_control_table = None
        self.release_ledger_table = None
        self.incident_context_table = None
        self.release_transition_table = None
        self.release_binding_table = None
        self.incident_at = None
        self.ddl_history_noise_jobs = None
        self.source_row_count = None
        self.expected_event_id_sum = None
        self.expected_crc = None
        self.candidate_row_count = None
        self.decoy_row_count = None
        self.recovery_gc_lifetime = None
        self.pre_release_id = None
        self.target_release_id = None
        self.canary_release_id = None
        self.smoke_release_id = None
        self.hotfix_release_id = None
        self.rehearsal_release_id = None
        self.shadow_release_id = None
        self.rollback_release_id = None
        self.gc_lifetime_before = None
        self.release_drop_jobs = {}
        self.production_payload_evidence = {}
        self.target_drop_job_id = None
        self.latest_same_name_drop_job_id = None
        self.env = None

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.database = validate_sql_identifier(str(config["database"]), "database")
        self.service_name = str(config["service_name"])
        self.environment = str(config["environment"])
        self.logical_table = validate_sql_identifier(str(config["logical_table"]), "logical_table")
        self.missing_cache_table = validate_sql_identifier(
            str(config["missing_cache_table"]), "missing_cache_table"
        )
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.archive_table = validate_sql_identifier(str(config["archive_table"]), "archive_table")
        self.audit_table = validate_sql_identifier(str(config["audit_table"]), "audit_table")
        self.ddl_seed_table = validate_sql_identifier(str(config["ddl_seed_table"]), "ddl_seed_table")
        self.release_registry_table = validate_sql_identifier(
            str(config["release_registry_table"]), "release_registry_table"
        )
        self.release_control_table = validate_sql_identifier(
            str(config["release_control_table"]), "release_control_table"
        )
        self.release_ledger_table = validate_sql_identifier(
            str(config["release_ledger_table"]), "release_ledger_table"
        )
        self.incident_context_table = validate_sql_identifier(
            str(config["incident_context_table"]), "incident_context_table"
        )
        self.release_transition_table = validate_sql_identifier(
            str(config["release_transition_table"]), "release_transition_table"
        )
        self.release_binding_table = validate_sql_identifier(
            str(config["release_binding_table"]), "release_binding_table"
        )
        self.incident_at = str(config["incident_at"])
        self.ddl_history_noise_jobs = int(config["ddl_history_noise_jobs"])
        self.source_row_count = int(config["source_row_count"])
        self.expected_event_id_sum = int(config["expected_event_id_sum"])
        self.expected_crc = int(config["expected_crc"])
        self.candidate_row_count = int(config["candidate_row_count"])
        self.decoy_row_count = int(config["decoy_row_count"])
        self.recovery_gc_lifetime = str(config["recovery_gc_lifetime"])
        self.pre_release_id = str(config["pre_release_id"])
        self.target_release_id = str(config["target_release_id"])
        self.canary_release_id = str(config["canary_release_id"])
        self.smoke_release_id = str(config["smoke_release_id"])
        self.hotfix_release_id = str(config["hotfix_release_id"])
        self.rehearsal_release_id = str(config["rehearsal_release_id"])
        self.shadow_release_id = str(config["shadow_release_id"])
        self.rollback_release_id = str(config["rollback_release_id"])
        self.env = env
        if self.ddl_history_noise_jobs <= 0:
            raise ValueError(
                "BC07 requires positive DDL history noise: "
                f"ddl_history_noise_jobs={self.ddl_history_noise_jobs}"
            )
        if self.candidate_row_count != self.source_row_count:
            raise ValueError(
                "BC07 requires full-sized candidate releases: "
                f"candidate_rows={self.candidate_row_count}, source_rows={self.source_row_count}"
            )
        release_ids = (
            self.pre_release_id,
            self.target_release_id,
            self.canary_release_id,
            self.smoke_release_id,
            self.hotfix_release_id,
            self.rehearsal_release_id,
            self.shadow_release_id,
            self.rollback_release_id,
        )
        if len(set(release_ids)) != len(release_ids):
            raise ValueError(f"BC07 release IDs must be unique: release_ids={release_ids!r}")

    @property
    def _qualified_table(self) -> str:
        return f"{self.database}.{self.table}"

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        env = context.env
        with env.metrics_hidden():
            self._create_schema_and_fixture(env)
            self.gc_lifetime_before = self._gc_lifetime(env)
            require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {self.database}.{self.audit_table} "
                    "(audit_id,action,created_at,config_key,previous_value,requested_value) "
                    f"VALUES (129,'gc-lifetime-override','{self._history_time('2026-07-29 12:00:00')}',"
                    f"'tidb_gc_life_time','{self.gc_lifetime_before}',"
                    f"'{self.recovery_gc_lifetime}')"
                ),
                "record BC07 GC lifetime change in the release audit",
            )
            require_sql_success(
                env.execute_sql(f"SET GLOBAL tidb_gc_life_time='{self.recovery_gc_lifetime}'"),
                "extend TiDB GC lifetime for BC07 recovery window",
            )
            require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {self.database}.{self.audit_table} "
                    "(audit_id,action,created_at,config_key,previous_value,requested_value,event_kind) VALUES "
                    f"(130,'gc-window-plan','{self._history_time('2026-08-03 11:20:00')}','tidb_gc_life_time','24h','72h','planned'),"
                    f"(131,'gc-window-rehearsal','{self._history_time('2026-08-03 12:00:00')}','tidb_gc_life_time','72h','72h','rehearsal')"
                ),
                "record BC07 planned and rehearsal GC audit noise",
            )
            self._seed_ddl_history(env)
            self._create_release_version(
                env,
                self.pre_release_id,
                "blue",
                self.candidate_row_count,
                "2026-07-30 09:00:00",
            )
            self._create_release_version(
                env,
                self.target_release_id,
                "active",
                self.source_row_count,
                "2026-07-31 09:00:00",
            )
            self._create_release_version(
                env,
                self.canary_release_id,
                "canary",
                self.candidate_row_count,
                "2026-08-01 09:00:00",
            )
            self._create_release_version(
                env,
                self.smoke_release_id,
                "smoke",
                self.decoy_row_count,
                "2026-08-02 09:00:00",
            )
            self._create_release_version(
                env,
                self.hotfix_release_id,
                "hotfix",
                self.candidate_row_count,
                "2026-08-03 11:45:00",
            )
            self._create_release_version(
                env,
                self.rehearsal_release_id,
                "rehearsal",
                self.candidate_row_count,
                "2026-08-03 11:15:00" if self.logical_table == "order_events" else "2026-08-03 12:00:00",
            )
            self._create_release_version(
                env,
                self.shadow_release_id,
                "shadow",
                self.candidate_row_count,
                "2026-08-03 12:15:00",
            )
            self._create_release_version(
                env,
                self.rollback_release_id,
                "rollback",
                self.candidate_row_count,
                "2026-08-03 12:30:00",
            )
            self._insert_incident_and_transition_history(env)
            self._create_ddl_noise(env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        if self.gc_lifetime_before is None or self.target_drop_job_id is None:
            raise RuntimeError(
                f"BC07 activation lacks install evidence: run_id={context.run_id!r}"
            )
        if self._scalar(
            context.env,
            "SELECT COUNT(*) FROM information_schema.tables "
            f"WHERE table_schema='{self.database}' AND table_name='{self.table}'",
        ) != 0:
            raise RuntimeError(
                "BC07 activation found the target table present before Agent takeover: "
                f"run_id={context.run_id!r}, table={self._qualified_table!r}"
            )
        if self._latest_drop_job(context.env) != self.latest_same_name_drop_job_id:
            raise RuntimeError(
                "BC07 activation lost the final same-name cleanup DROP history: "
                f"run_id={context.run_id!r}, expected_latest={self.latest_same_name_drop_job_id!r}"
            )
        incident_epoch = self._scalar(
            context.env,
            f"SELECT expected_control_epoch FROM {self.database}.{self.incident_context_table} "
            f"WHERE service_name='{self.service_name}' AND environment='{self.environment}' "
            f"AND logical_table='{self.logical_table}' "
            f"AND incident_at='{self.incident_at}'",
        )
        snapshot_boundary = (
            "" if self.logical_table == "order_events" else
            "AND c.status='serving' AND c.traffic_percent=100 "
            f"AND c.effective_at <= '{self.incident_at}' "
        )
        target_candidate = self._scalar(
            context.env,
            f"SELECT COUNT(*) FROM {self.database}.{self.release_control_table} c "
            f"JOIN {self.database}.{self.release_binding_table} b ON b.control_key=c.control_key "
            f"WHERE c.service_name='{self.service_name}' AND c.environment='{self.environment}' "
            f"AND c.logical_table='{self.logical_table}' "
            f"AND c.region='global' AND c.control_role='observed' AND b.release_id='{self.target_release_id}' "
            f"AND c.control_epoch={int(incident_epoch)} {snapshot_boundary}"
            f"AND b.valid_from <= '{self.incident_at}' AND b.valid_until > '{self.incident_at}'",
        )
        if target_candidate != 1:
            raise RuntimeError(
                "BC07 activation lost the original incident-scope historical candidate: "
                f"target_release={self.target_release_id!r}, incident_epoch={incident_epoch!r}, rows={target_candidate!r}"
            )

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config, context.env)
        history = execute_result_rows(
            context.env.execute_sql,
            (
                "SELECT JOB_ID, DB_NAME, TABLE_NAME, JOB_TYPE, STATE, TABLE_ID "
                "FROM information_schema.ddl_jobs "
                f"WHERE DB_NAME='{self.database}' ORDER BY JOB_ID DESC LIMIT 96"
            ),
            "capture BC07 DDL history",
        )
        release_registry = execute_result_rows(
            context.env.execute_sql,
            f"SELECT * FROM {self.database}.{self.release_registry_table} ORDER BY registry_id",
            "capture BC07 release registry",
        )
        release_control = execute_result_rows(
            context.env.execute_sql,
            f"SELECT * FROM {self.database}.{self.release_control_table} ORDER BY control_id",
            "capture BC07 release control",
        )
        release_bindings = execute_result_rows(
            context.env.execute_sql,
            f"SELECT * FROM {self.database}.{self.release_binding_table} ORDER BY binding_id",
            "capture BC07 release binding map",
        )
        release_ledger = execute_result_rows(
            context.env.execute_sql,
            f"SELECT * FROM {self.database}.{self.release_ledger_table} ORDER BY release_id",
            "capture BC07 business release ledger",
        )
        incident_context = execute_result_rows(
            context.env.execute_sql,
            f"SELECT * FROM {self.database}.{self.incident_context_table} ORDER BY incident_id",
            "capture BC07 incident context",
        )
        release_transitions = execute_result_rows(
            context.env.execute_sql,
            f"SELECT * FROM {self.database}.{self.release_transition_table} ORDER BY occurred_at, transition_id",
            "capture BC07 release transition history",
        )
        safe_point = self._scalar(
            context.env,
            "SELECT VARIABLE_VALUE FROM mysql.tidb "
            "WHERE VARIABLE_NAME='tikv_gc_safe_point'",
        )
        target_exists = self._scalar(
            context.env,
            "SELECT COUNT(*) FROM information_schema.tables "
            f"WHERE table_schema='{self.database}' AND table_name='{self.table}'",
        )
        if target_exists != 0:
            raise RuntimeError(
                "BC07 observability requires the target table to be absent: "
                f"table={self._qualified_table!r}, target_exists={target_exists!r}"
            )
        return {
            "bc07_fixture_truth": {
                "row_count": self.source_row_count,
                "event_id_sum": self.expected_event_id_sum,
                "crc": self.expected_crc,
            },
            "bc07_drop_job_id": self.target_drop_job_id,
            "bc07_decoy_drop_job_id": self.release_drop_jobs[self.smoke_release_id],
            "bc07_same_name_drop_jobs": [
                {"release_id": release_id, "drop_job_id": job_id}
                for release_id, job_id in self.release_drop_jobs.items()
            ],
            "bc07_target_release_id": self.target_release_id,
            "bc07_release_registry": release_registry,
            "bc07_release_control": release_control,
            "bc07_release_bindings": release_bindings,
            "bc07_release_ledger": release_ledger,
            "bc07_incident_context": incident_context,
            "bc07_release_transitions": release_transitions,
            "bc07_ddl_history": history,
            **({
                "bc07_production_payload_profiles": self.production_payload_evidence,
                "bc07_public_checksum_schemas": {
                    name: execute_result_rows(
                        context.env.execute_sql,
                        f"SHOW CREATE TABLE {self.database}.{name}",
                        f"capture public Orders checksum schema {name}",
                    )
                    for name in (self.release_registry_table, self.release_ledger_table)
                },
                "bc07_current_observer_schema": execute_result_rows(
                    context.env.execute_sql,
                    f"SHOW CREATE TABLE {self.database}.{self.release_control_table}",
                    "capture public Orders current observer schema",
                ),
                "bc07_controller_leases": execute_result_rows(
                    context.env.execute_sql,
                    f"SELECT * FROM {self.database}.controller_lease_history ORDER BY lease_id",
                    "capture BC07 order publisher leases",
                ),
                "bc07_apply_receipts": execute_result_rows(
                    context.env.execute_sql,
                    f"SELECT * FROM {self.database}.controller_apply_receipts ORDER BY receipt_id",
                    "capture BC07 order raw receiver/application facts",
                ),
            } if self.logical_table == "order_events" else {}),
            "bc07_gc_window": {
                "before": self.gc_lifetime_before,
                "during": self.recovery_gc_lifetime,
                "safe_point": safe_point,
            },
            "bc07_initial_state": {
                "target_table_present": False,
                "same_name_drop_count": len(self.release_drop_jobs),
                "full_sized_candidate_count": 7,
                "target_business_queries": "expected to fail until active release recovery",
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        if self.gc_lifetime_before is None:
            raise RuntimeError(
                f"BC07 recovery lacks the original GC lifetime: run_id={context.run_id!r}"
            )
        require_sql_success(
            context.env.execute_sql(f"SET GLOBAL tidb_gc_life_time='{self.gc_lifetime_before}'"),
            "restore TiDB GC lifetime after BC07",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE {self.database}"),
            f"remove BC07 database {self.database}",
        )

    def _create_schema_and_fixture(self, env) -> None:
        inventory_comment = (
            " COMMENT 'Artifact inventory registration time; serving membership comes from scoped route application receipts'"
            if self.logical_table == "order_events" else ""
        )
        ledger_crc_comment = (
            " COMMENT 'BIT_XOR(CRC32(CONCAT_WS(0x23,event_id,tenant_id,event_type,amount_cents,payload))); payload is raw bytes, not HEX; 0x23 is the field separator'"
            if self.logical_table == "order_events" else ""
        )
        control_schema = (
            "control_role ENUM('observed','desired') NOT NULL, "
            "control_key VARCHAR(64) NOT NULL, effective_at DATETIME NOT NULL "
            "COMMENT 'Observed rows: latest actual route application time; desired rows: planned activation time', "
            "status ENUM('inactive','serving','pending') NOT NULL, traffic_percent INT NOT NULL, "
            "observed_at DATETIME NOT NULL COMMENT 'Current snapshot collection time; reconstruct incident membership from scoped application history', "
            if self.logical_table == "order_events" else
            "control_role VARCHAR(24) NOT NULL, "
            "control_key VARCHAR(64) NOT NULL, effective_at DATETIME NOT NULL, "
            "status VARCHAR(24) NOT NULL, traffic_percent INT NOT NULL, "
        )
        require_sql_success(
            env.execute_sql(f"CREATE DATABASE {self.database}"),
            f"create BC07 database {self.database}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.archive_table} ({self._event_schema()})"
            ),
            "create BC07 archive table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.audit_table} ("
                "audit_id BIGINT PRIMARY KEY, action VARCHAR(32) NOT NULL, event_kind ENUM('applied','planned','rehearsal') NOT NULL DEFAULT 'applied' COMMENT 'Only applied rows changed cluster configuration', "
                "created_at DATETIME NOT NULL, config_key VARCHAR(64), "
                "previous_value VARCHAR(64), requested_value VARCHAR(64))"
            ),
            "create BC07 release audit table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.ddl_seed_table} ("
                "seed_id BIGINT PRIMARY KEY, marker VARCHAR(64) NOT NULL)"
            ),
            "create BC07 DDL seed table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.release_registry_table} ("
                "registry_id BIGINT PRIMARY KEY, release_id VARCHAR(64) UNIQUE NOT NULL, "
                "logical_table VARCHAR(64) NOT NULL, table_id BIGINT NOT NULL, "
                "lifecycle_state VARCHAR(32) NOT NULL, generation VARCHAR(32) NOT NULL, "
                "expected_rows BIGINT NOT NULL, expected_event_id_sum BIGINT NOT NULL, "
                "expected_crc BIGINT NOT NULL COMMENT 'BIT_XOR(CRC32(CONCAT_WS(0x23,event_id,tenant_id,event_type,amount_cents,payload)))', "
                f"effective_at DATETIME NOT NULL{inventory_comment}, "
                "change_ticket VARCHAR(64) NOT NULL)"
            ),
            "create BC07 release registry",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.release_control_table} ("
                "control_id BIGINT PRIMARY KEY, service_name VARCHAR(64) NOT NULL, "
                "environment VARCHAR(32) NOT NULL, logical_table VARCHAR(64) NOT NULL, "
                f"region VARCHAR(32) NOT NULL, {control_schema}"
                "control_epoch BIGINT NOT NULL, change_ticket VARCHAR(64) NOT NULL)"
            ),
            "create BC07 release control table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.release_ledger_table} ("
                "release_id VARCHAR(64) PRIMARY KEY, order_count BIGINT NOT NULL, "
                f"event_id_sum BIGINT NOT NULL, crc BIGINT NOT NULL{ledger_crc_comment}, "
                "source_system VARCHAR(64) NOT NULL, reconciliation_state VARCHAR(24) NOT NULL, "
                "recorded_at DATETIME NOT NULL)"
            ),
            "create BC07 business release ledger",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.incident_context_table} ("
                "incident_id BIGINT PRIMARY KEY, service_name VARCHAR(64) NOT NULL, "
                "environment VARCHAR(32) NOT NULL, logical_table VARCHAR(64) NOT NULL, "
                "incident_at DATETIME NOT NULL, last_known_good_at DATETIME NOT NULL, "
                "expected_control_epoch BIGINT NOT NULL, evidence_source VARCHAR(64) NOT NULL, "
                "scope_note VARCHAR(128) NOT NULL)"
            ),
            "create BC07 incident context",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.release_transition_table} ("
                "transition_id BIGINT PRIMARY KEY, control_key VARCHAR(64) NOT NULL, "
                "service_name VARCHAR(64) NOT NULL, environment VARCHAR(32) NOT NULL, "
                "logical_table VARCHAR(64) NOT NULL, transition VARCHAR(32) NOT NULL, "
                "occurred_at DATETIME NOT NULL, traffic_percent INT NOT NULL, "
                "control_epoch BIGINT NOT NULL, change_ticket VARCHAR(64) NOT NULL, "
                "event_key VARCHAR(64) NOT NULL COMMENT 'Logical event identity within service/environment/logical_table/control_key/epoch', "
                "event_revision BIGINT NOT NULL COMMENT 'Highest revision replaces prior versions of the same logical event before applying the occurred_at boundary; recorded_at is audit arrival', "
                "revision_state ENUM('applied','retracted') NOT NULL COMMENT 'Choose highest revision, remove retracted events, then fold surviving occurred_at', "
                "actor VARCHAR(64) NOT NULL, recorded_at DATETIME NOT NULL COMMENT 'Audit ingestion time; occurred_at is business event time', "
                "resulting_state ENUM('inactive','serving') NOT NULL COMMENT 'State after this event; fold occurred_at within control_key and epoch')"
            ),
            "create BC07 release transition history",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.release_binding_table} ("
                "binding_id BIGINT PRIMARY KEY, control_key VARCHAR(64) NOT NULL, "
                "release_id VARCHAR(64) NOT NULL, binding_state ENUM('bound','revoked') NOT NULL, "
                "binding_revision BIGINT NOT NULL COMMENT 'Highest applicable revision within each control_key corrects prior binding facts', "
                "valid_from DATETIME NOT NULL COMMENT 'Inclusive business-time interval start', "
                "valid_until DATETIME COMMENT 'Exclusive business-time interval end; NULL means open', "
                "recorded_at DATETIME NOT NULL COMMENT 'Ingestion time, including late corrections; not deployment effective time', "
                "change_ticket VARCHAR(64) NOT NULL)"
            ),
            "create BC07 release binding map",
        )
        self._insert_event_rows(env, self.archive_table, 64, "archive")
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.audit_table} "
                "(audit_id,action,created_at) VALUES "
                + ",".join(
                    f"({index},'release-check',{self._audit_timestamp(index)})"
                    for index in range(1, 129)
                )
            ),
            "insert BC07 release audit rows",
        )
        self._insert_control_and_binding_history(env)

    def _history_time(self, value: str) -> str:
        offset = datetime.fromisoformat(self.incident_at) - datetime(2026, 8, 3, 11, 30)
        return (datetime.fromisoformat(value) + offset).isoformat(sep=" ")

    def _insert_control_and_binding_history(self, env) -> None:
        controls = (
            (1, self.service_name, self.environment, "global", "observed", "slot-a17", "2026-08-03 11:30:01", "inactive", 0, 41),
            (2, self.service_name, self.environment, "us-east", "observed", "slot-g53", "2026-08-03 11:29:59", "serving", 100, 41),
            (4, self.service_name, self.environment, "global", "desired", "slot-c39", "2026-08-03 11:45:00", "pending", 0, 42),
            (6, self.service_name, "staging", "global", "observed", "slot-g53", "2026-08-03 11:29:59", "serving", 100, 7),
            (9, self.service_name, self.environment, "global", "observed", "slot-g53", "2026-08-03 11:30:02", "serving", 100, 41),
            (10, self.service_name, self.environment, "global", "observed", "slot-h28", "2026-08-03 11:25:00", "inactive", 0, 41),
        ) if self.logical_table == "order_events" else (
            (1, self.service_name, self.environment, "global", "observed", "slot-a17", "2026-07-31 09:20:00", "serving", 100, 41),
            (2, self.service_name, self.environment, "us-east", "observed", "slot-a17", "2026-07-31 09:20:00", "serving", 100, 41),
            (3, self.service_name, self.environment, "eu-west", "observed", "slot-b04", "2026-08-01 09:10:00", "shadow", 0, 41),
            (4, self.service_name, self.environment, "global", "desired", "slot-c39", "2026-08-03 11:45:00", "pending", 0, 42),
            (5, self.service_name, self.environment, "global", "observed", "slot-a17", "2026-08-03 11:45:00", "serving", 100, 42),
            (6, self.service_name, "staging", "global", "observed", "slot-d82", "2026-08-01 09:10:00", "serving", 100, 7),
            (7, "release-dashboard", self.environment, "global", "observed", "slot-e11", "2026-08-03 11:50:00", "cleanup", 0, 43),
            (8, "reconciliation-worker", self.environment, "global", "observed", "slot-f62", "2026-07-30 09:00:00", "retired", 0, 40),
            (9, self.service_name, self.environment, "global", "observed", "slot-g53", "2026-08-03 11:15:00", "serving", 100, 41),
            (10, self.service_name, self.environment, "global", "observed", "slot-h28", "2026-07-31 09:31:00", "serving", 100, 41),
        )
        observation_column = ",observed_at" if self.logical_table == "order_events" else ""
        observation_value = (
            f",'{self._history_time('2026-08-03 11:44:30')}'"
            if self.logical_table == "order_events" else ""
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.release_control_table} "
                "(control_id,service_name,environment,logical_table,region,control_role,control_key,"
                f"effective_at,status,traffic_percent,control_epoch,change_ticket{observation_column}) VALUES "
                + ",".join(
                    f"({i},'{service}','{environment}','{self.logical_table}','{region}','{role}','{key}',"
                    f"'{self._history_time(at)}','{status}',{traffic},{epoch},'CHG-{i:04d}'{observation_value})"
                    for i, service, environment, region, role, key, at, status, traffic, epoch in controls
                )
            ),
            "record BC07 controller snapshots",
        )
        bindings = (
            (1, "slot-a17", self.pre_release_id, 1, "2026-07-31 09:20:00", "2026-08-03 11:45:00", "2026-07-31 09:20:01"),
            (2, "slot-b04", self.canary_release_id, 1, "2026-08-01 09:00:00", None, "2026-08-01 09:10:00"),
            (3, "slot-a17", self.hotfix_release_id, 3, "2026-08-03 11:45:00", None, "2026-08-03 11:46:00"),
            (4, "slot-d82", self.canary_release_id, 1, "2026-08-01 09:00:00", None, "2026-08-01 09:10:00"),
            (5, "slot-e11", self.smoke_release_id, 1, "2026-08-02 09:00:00", None, "2026-08-03 11:50:00"),
            (6, "slot-f62", self.pre_release_id, 1, "2026-07-30 08:00:00", None, "2026-07-30 09:00:00"),
            (7, "slot-a17-legacy", self.rollback_release_id, 1, "2026-07-31 09:21:00", None, "2026-07-31 09:21:00"),
            (8, "slot-g53", self.rehearsal_release_id, 1, "2026-08-03 11:15:00", None, "2026-08-03 11:15:00"),
            (9, "slot-h28", self.pre_release_id, 1, "2026-07-31 09:31:00", None, "2026-07-31 09:31:00"),
            (10, "slot-a17", self.target_release_id, 2, "2026-07-31 09:20:00", "2026-08-03 11:45:00", "2026-08-03 11:35:00"),
        )
        values = []
        for i, key, release, revision, start, end, recorded in bindings:
            end_sql = "NULL" if end is None else f"'{self._history_time(end)}'"
            values.append(
                f"({i},'{key}','{release}','bound',{revision},'{self._history_time(start)}',"
                f"{end_sql},'{self._history_time(recorded)}','CHG-{i:04d}')"
            )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.release_binding_table} "
                "(binding_id,control_key,release_id,binding_state,binding_revision,valid_from,valid_until,recorded_at,change_ticket) VALUES "
                + ",".join(values)
            ),
            "record BC07 business-time bindings and late registry correction",
        )

    def _insert_incident_and_transition_history(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.incident_context_table} "
                "(incident_id,service_name,environment,logical_table,incident_at,last_known_good_at,"
                "expected_control_epoch,evidence_source,scope_note) VALUES "
                f"(9001,'{self.service_name}','{self.environment}','{self.logical_table}','{self.incident_at}',"
                f"'{self._history_time('2026-08-03 11:29:59')}',41,'incident-coordinator','global serving release before cleanup')"
            ),
            "record BC07 incident boundary",
        )
        transitions = (
            (1, "slot-f62", "retired", "2026-07-30 08:55:00", 0, 40, "inactive"),
            (2, "slot-f62", "rollback_completed", "2026-07-30 09:30:00", 0, 40, "inactive"),
            (3, "slot-a17", "deploy_started", "2026-07-31 08:55:00", 0, 41, "inactive"),
            (4, "slot-a17", "traffic_shift", "2026-07-31 09:05:00", 10, 41, "inactive"),
            (5, "slot-a17", "traffic_shift", "2026-07-31 09:20:00", 100, 41, "serving"),
            (6, "slot-a17", "promoted", "2026-07-31 09:25:00", 100, 41, "serving"),
            (7, "slot-a17", "reconciled", "2026-07-31 09:30:00", 100, 41, "serving"),
            (8, "slot-b04", "shadow_started", "2026-08-01 09:00:00", 0, 41, "inactive"),
            (9, "slot-b04", "shadow_aborted", "2026-08-01 09:10:00", 0, 41, "inactive"),
            (10, "slot-e11", "cleanup_started", "2026-08-02 09:00:00", 0, 41, "inactive"),
            (11, "slot-e11", "cleanup_completed", "2026-08-02 09:02:00", 0, 41, "inactive"),
            (12, "slot-a17", "deploy_started", "2026-08-03 11:45:00", 0, 42, "inactive"),
            (13, "slot-a17", "traffic_shift", "2026-08-03 11:50:00", 100, 42, "serving"),
            (14, "slot-a17", "promoted", "2026-08-03 11:55:00", 100, 42, "serving"),
            (15, "slot-g53", "rollout_preflight" if self.logical_table == "order_events" else "rehearsal_started", "2026-08-03 12:00:00", 0, 43, "inactive"),
            (16, "slot-g53", "rollout_completed" if self.logical_table == "order_events" else "rehearsal_completed", "2026-08-03 12:04:00", 0, 43, "inactive"),
            (17, "slot-i66", "shadow_started", "2026-08-03 12:15:00", 0, 44, "inactive"),
            (18, "slot-i66", "shadow_completed", "2026-08-03 12:20:00", 0, 44, "inactive"),
            (19, "slot-j91", "rollback_candidate", "2026-08-03 12:30:00", 0, 45, "inactive"),
            (20, "slot-j91", "rollback_completed", "2026-08-03 12:35:00", 0, 45, "inactive"),
            (21, "slot-h28", "promoted", "2026-07-31 09:32:00", 100, 41, "serving"),
            (22, "slot-h28", "reconciled", "2026-07-31 09:33:00", 100, 41, "serving"),
            (23, "slot-h28", "traffic_withdrawn", "2026-08-03 11:25:00", 0, 41, "inactive"),
        )
        revisions = [
            (*event, f"event-{event[0]:04d}", 1, "applied", "2026-08-03 11:40:00" if event[0] == 23 else event[3])
            for event in transitions
        ]
        revisions.extend((
            (24, "slot-a17", "traffic_withdrawn", "2026-08-03 11:28:00", 0, 41, "inactive", "event-0024", 1, "applied", "2026-08-03 11:29:00"),
            (25, "slot-a17", "traffic_withdrawn", "2026-08-03 11:28:00", 0, 41, "inactive", "event-0024", 2, "retracted", "2026-08-03 11:42:00"),
            (26, "slot-h28", "traffic_withdrawn", "2026-08-03 11:25:00", 100, 41, "serving", "event-0023", 2, "applied", "2026-08-03 11:29:30"),
            (27, "slot-h28", "traffic_withdrawn", "2026-08-03 11:25:00", 0, 41, "inactive", "event-0023", 3, "applied", "2026-08-03 11:43:00"),
        ))
        revisions.extend({
            "order_events": (
                (28, "slot-a17", "traffic_withdrawn", "2026-08-03 11:29:00", 0, 41, "inactive", "event-0028", 1, "applied", "2026-08-03 11:29:30"),
                (29, "slot-a17", "traffic_withdrawn", "2026-08-03 11:31:00", 0, 41, "inactive", "event-0028", 2, "applied", "2026-08-03 11:44:00"),
            ),
            "payment_events": (),
        }[self.logical_table])
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.release_transition_table} "
                "(transition_id,control_key,service_name,environment,logical_table,transition,occurred_at,"
                "traffic_percent,control_epoch,change_ticket,actor,recorded_at,resulting_state,event_key,event_revision,revision_state) VALUES "
                + ",".join(
                    f"({i},'{key}','{self.service_name}','{self.environment}','{self.logical_table}',"
                    f"'{transition}','{self._history_time(at)}',{traffic},{epoch},'CHG-{i:04d}','release-controller',"
                    f"'{self._history_time(recorded)}','{state}','{event_key}',{revision},'{revision_state}')"
                    for i, key, transition, at, traffic, epoch, state, event_key, revision, revision_state, recorded in revisions
                )
            ),
            "record BC07 revised and retracted controller events",
        )
        if self.logical_table == "order_events":
            self._insert_controller_authority_history(env)
            self._insert_application_history(env)

    def _insert_controller_authority_history(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.controller_lease_history ("
                "lease_id BIGINT PRIMARY KEY, controller_id VARCHAR(64) NOT NULL, "
                "service_name VARCHAR(64) NOT NULL, environment VARCHAR(32) NOT NULL, "
                "logical_table VARCHAR(64) NOT NULL, region VARCHAR(32) NOT NULL, "
                "control_epoch BIGINT NOT NULL, "
                "valid_from DATETIME NOT NULL COMMENT 'Inclusive business time from which publisher owns this scoped controller lease', "
                "valid_until DATETIME COMMENT 'Exclusive business time of lease loss; NULL means open')"
            ),
            "create BC07 order controller lease history",
        )
        leases = (
            (1, "release-controller", self.environment, "global", 41, "2026-07-30 00:00:00", "2026-08-03 11:29:45"),
            (2, "release-controller-b", self.environment, "global", 41, "2026-08-03 11:29:45", "2026-08-03 11:45:00"),
            (3, "release-controller", self.environment, "us-east", 41, "2026-07-30 00:00:00", None),
            (4, "release-controller", "staging", "global", 7, "2026-07-30 00:00:00", None),
            (5, "release-controller-b", self.environment, "global", 42, "2026-08-03 11:45:00", None),
        )
        values = []
        for i, controller, environment, region, epoch, start, end in leases:
            end_sql = "NULL" if end is None else f"'{end}'"
            values.append(
                f"({i},'{controller}','{self.service_name}','{environment}','{self.logical_table}',"
                f"'{region}',{epoch},'{start}',{end_sql})"
            )
        require_sql_success(
            env.execute_sql(f"INSERT INTO {self.database}.controller_lease_history VALUES " + ",".join(values)),
            "record BC07 business-time controller authority",
        )
        require_sql_success(
            env.execute_sql(
                f"ALTER TABLE {self.database}.{self.release_transition_table} MODIFY actor VARCHAR(64) NOT NULL "
                "COMMENT 'Publishing controller identity; global control events require its matching scoped lease at occurred_at, not audit arrival'"
            ),
            "describe BC07 publishing identity",
        )
        events = (
            (30, "slot-a17", "reconciled", "2026-08-03 11:29:50", 100, "serving", "release-controller-b"),
            (31, "slot-a17", "traffic_withdrawn", "2026-08-03 11:29:55", 0, "inactive", "release-controller"),
            (32, "slot-h28", "promoted", "2026-08-03 11:29:56", 100, "serving", "release-controller"),
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.release_transition_table} "
                "(transition_id,control_key,service_name,environment,logical_table,transition,occurred_at,"
                "traffic_percent,control_epoch,change_ticket,actor,recorded_at,resulting_state,event_key,event_revision,revision_state) VALUES "
                + ",".join(
                    f"({i},'{key}','{self.service_name}','{self.environment}','{self.logical_table}',"
                    f"'{transition}','{at}',{traffic},41,'CHG-{i:04d}','{actor}',"
                    f"'{at}','{state}','event-{i:04d}',1,'applied')"
                    for i, key, transition, at, traffic, state, actor in events
                )
            ),
            "record BC07 controller handoff publications",
        )

    def _insert_application_history(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"ALTER TABLE {self.database}.{self.release_transition_table} "
                "ADD COLUMN region VARCHAR(32) NOT NULL DEFAULT 'global' "
                "COMMENT 'Command route scope; match the exact receipt scope', "
                "MODIFY resulting_state ENUM('inactive','serving') NOT NULL "
                "COMMENT 'Command intent; actual route changes only at matching receipt applied_at', "
                "MODIFY revision_state ENUM('applied','retracted') NOT NULL "
                "COMMENT 'Accepted historical audit revision, not receiver application; resolve revisions before joining receipts'"
            ),
            "expose BC07 command scope and receiver application semantics",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.controller_apply_receipts ("
                "receipt_id BIGINT PRIMARY KEY, service_name VARCHAR(64) NOT NULL, "
                "environment VARCHAR(32) NOT NULL, logical_table VARCHAR(64) NOT NULL, "
                "control_key VARCHAR(64) NOT NULL, region VARCHAR(32) NOT NULL, "
                "control_epoch BIGINT NOT NULL, event_key VARCHAR(64) NOT NULL, "
                "event_revision BIGINT NOT NULL COMMENT 'Audited application fact for the same scoped command revision; historical corrections supersede both command and associated receipt facts', "
                "receiver_id VARCHAR(64) NOT NULL, receiver_epoch BIGINT NOT NULL "
                "COMMENT 'Only the matching control epoch can change that route', "
                "phase ENUM('accepted','applied','rejected','cancelled') NOT NULL "
                "COMMENT 'Accepted means queued, applied means route changed; rejected/cancelled never changed it', "
                "accepted_at DATETIME, applied_at DATETIME "
                "COMMENT 'Actual route effective time; apply the incident boundary here, not to accepted_at or command occurrence', "
                "recorded_at DATETIME NOT NULL COMMENT 'Audit arrival only, including late historical corrections', "
                "resulting_state ENUM('inactive','serving') NOT NULL, traffic_percent INT NOT NULL, "
                "rejection_reason ENUM('none','publisher_fenced','stale_epoch','cancelled_command') NOT NULL)"
            ),
            "create BC07 raw controller receiver/application receipts",
        )
        authority = (
            f"EXISTS (SELECT 1 FROM {self.database}.controller_lease_history l "
            "WHERE l.controller_id=t.actor AND l.service_name=t.service_name "
            "AND l.environment=t.environment AND l.logical_table=t.logical_table "
            "AND l.region=t.region AND l.control_epoch=t.control_epoch "
            "AND l.valid_from <= t.occurred_at "
            "AND (l.valid_until IS NULL OR t.occurred_at < l.valid_until))"
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.controller_apply_receipts "
                "SELECT t.transition_id,t.service_name,t.environment,t.logical_table,t.control_key,t.region,"
                "t.control_epoch,t.event_key,t.event_revision,'global-route-applier',t.control_epoch,"
                "CASE WHEN t.revision_state='retracted' THEN 'cancelled' "
                f"WHEN {authority} THEN 'applied' ELSE 'rejected' END,"
                "t.occurred_at,CASE WHEN t.revision_state='applied' "
                f"AND {authority} THEN t.occurred_at ELSE NULL END,"
                "t.recorded_at,t.resulting_state,t.traffic_percent,"
                "CASE WHEN t.revision_state='retracted' THEN 'cancelled_command' "
                f"WHEN {authority} THEN 'none' ELSE 'publisher_fenced' END "
                f"FROM {self.database}.{self.release_transition_table} t"
            ),
            "record scoped application or cancellation for every historical command revision",
        )
        events = (
            (33, "slot-a17", self.environment, "global", "traffic_withdrawn", 41, "release-controller-b", "inactive", 0),
            (34, "slot-g53", self.environment, "global", "promoted", 41, "release-controller-b", "serving", 100),
            (35, "slot-g53", self.environment, "us-east", "promoted", 41, "release-controller", "serving", 100),
            (36, "slot-g53", "staging", "global", "promoted", 7, "release-controller", "serving", 100),
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.release_transition_table} "
                "(transition_id,control_key,service_name,environment,logical_table,transition,occurred_at,"
                "traffic_percent,control_epoch,change_ticket,actor,recorded_at,resulting_state,event_key,event_revision,revision_state,region) VALUES "
                + ",".join(
                    f"({i},'{key}','{self.service_name}','{environment}','{self.logical_table}',"
                    f"'{transition}','2026-08-03 11:29:57',{traffic},{epoch},'CHG-{i:04d}',"
                    f"'{actor}','2026-08-03 11:29:57','{state}','event-{i:04d}',1,'applied','{region}')"
                    for i, key, environment, region, transition, epoch, actor, state, traffic in events
                )
            ),
            "record global queued commands and independent regional/staging commands",
        )
        receipts = []
        for i, key, environment, region, transition, epoch, actor, state, traffic in events:
            apply_time = {33: "11:30:01", 34: "11:30:02", 35: "11:29:59", 36: "11:29:59"}[i]
            for phase_index, phase in enumerate(("accepted", "applied")):
                applied_sql = "NULL" if phase == "accepted" else f"'2026-08-03 {apply_time}'"
                recorded = "11:29:58" if phase == "accepted" else apply_time
                receipts.append(
                    f"({i * 10 + phase_index},'{self.service_name}','{environment}','{self.logical_table}',"
                    f"'{key}','{region}',{epoch},'event-{i:04d}',1,'{region}-route-applier',{epoch},"
                    f"'{phase}','2026-08-03 11:29:58',{applied_sql},'2026-08-03 {recorded}',"
                    f"'{state}',{traffic},'none')"
                )
        receipts.append(
            f"(399,'{self.service_name}','{self.environment}','{self.logical_table}',"
            "'slot-g53','global',41,'event-0034',1,'retiring-global-applier',40,"
            "'rejected','2026-08-03 11:29:58',NULL,'2026-08-03 11:29:59','serving',100,'stale_epoch')"
        )
        require_sql_success(
            env.execute_sql(f"INSERT INTO {self.database}.controller_apply_receipts VALUES " + ",".join(receipts)),
            "record acceptance, delayed global application and scoped healthy application",
        )

    @staticmethod
    def _event_schema() -> str:
        return (
            "event_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, "
            "event_type VARCHAR(32) NOT NULL, amount_cents BIGINT NOT NULL, "
            "payload VARBINARY(64) NOT NULL"
        )

    @staticmethod
    def _audit_timestamp(index: int) -> str:
        day = 1 + (index % 27)
        return f"'2026-07-{day:02d} 12:00:00'"

    def _insert_event_rows(self, env, table: str, row_count: int, generation: str) -> None:
        event_types = ("purchase", "refund", "shipment", "login", "chargeback")
        generation_shift = {
            "active": 0,
            "blue": 1,
            "canary": 2,
            "smoke": 3,
            "hotfix": 4,
            "rehearsal": 5,
            "shadow": 6,
            "rollback": 7,
            "archive": 0,
        }[generation]
        for offset in range(0, row_count, 250):
            values = []
            for event_id in range(offset + 1, min(offset + 251, row_count + 1)):
                tenant_id = event_id % 31 + 1
                event_type = event_types[(event_id + generation_shift) % len(event_types)]
                amount_cents = 1000 + event_id * 13 + generation_shift * 101
                if self.logical_table == "order_events":
                    payload = f"order-{event_id:04d}".encode()
                elif generation == "active" and event_id == self.source_row_count:
                    payload = bytes.fromhex("3a3ef539")
                elif generation in {"active", "archive"}:
                    payload = f"order-{event_id:04d}".encode()
                else:
                    payload = f"{generation}-order-{event_id:04d}".encode()
                values.append(
                    f"({event_id},{tenant_id},'{event_type}',{amount_cents},0x{payload.hex()})"
                )
            require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {self.database}.{table} "
                    "(event_id,tenant_id,event_type,amount_cents,payload) VALUES "
                    + ",".join(values)
                ),
                f"insert BC07 {generation} release rows into {self.database}.{table}",
            )

    def _seed_ddl_history(self, env) -> None:
        current = self._max_ddl_job_id(env)
        target_job = current + self.ddl_history_noise_jobs
        while current < target_job:
            next_job = current + 1
            require_sql_success(
                env.execute_sql(
                    f"ALTER TABLE {self.database}.{self.ddl_seed_table} "
                    f"COMMENT='bc07-ddl-seed-{next_job}'"
                ),
                "advance BC07 DDL history noise",
            )
            observed = self._max_ddl_job_id(env)
            if observed != next_job:
                raise RuntimeError(
                    "BC07 DDL job IDs are not contiguous while calibrating history noise: "
                    f"expected={next_job}, observed={observed}"
                )
            current = observed

    def _create_release_version(
        self,
        env,
        release_id: str,
        generation: str,
        row_count: int,
        effective_at: str,
    ) -> None:
        effective_at = self._history_time(effective_at)
        require_sql_success(
            env.execute_sql(f"CREATE TABLE {self._qualified_table} ({self._event_schema()})"),
            f"create BC07 {release_id} same-name release table",
        )
        self._insert_event_rows(env, self.table, row_count, generation)
        truth = self._truth(env)
        if self.logical_table == "order_events":
            self.production_payload_evidence[release_id] = execute_result_rows(
                env.execute_sql,
                f"SELECT COUNT(*), SUM(payload=CONCAT('order-',LPAD(event_id,4,'0'))), "
                f"MIN(LENGTH(payload)), MAX(LENGTH(payload)) FROM {self._qualified_table}",
                f"capture native production payload profile for {release_id}",
            )
        if release_id == self.target_release_id:
            expected = (self.source_row_count, self.expected_event_id_sum, self.expected_crc)
            if truth != expected:
                raise RuntimeError(
                    "BC07 active release fixture does not match the formal business truth: "
                    f"expected={expected}, actual={truth}"
                )
        table_id = int(
            self._scalar(
                env,
                "SELECT TIDB_TABLE_ID FROM information_schema.tables "
                f"WHERE TABLE_SCHEMA='{self.database}' AND TABLE_NAME='{self.table}'",
            )
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.release_registry_table} "
                "(registry_id,release_id,logical_table,table_id,lifecycle_state,generation,"
                "expected_rows,expected_event_id_sum,expected_crc,effective_at,change_ticket) VALUES "
                f"({len(self.release_drop_jobs) + 1},'{release_id}','{self.table}',{table_id},"
                f"'retained','artifact-{len(self.release_drop_jobs) + 1:02d}',{truth[0]},{truth[1]},{truth[2]},"
                f"'{effective_at}','CHG-{len(self.release_drop_jobs) + 1:04d}')"
            ),
            f"record BC07 release registry row for {release_id}",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.release_ledger_table} "
                "(release_id,order_count,event_id_sum,crc,source_system,reconciliation_state,recorded_at) VALUES "
                f"('{release_id}',{truth[0]},{truth[1]},{truth[2]},'order-ledger','reconciled','{effective_at}')"
            ),
            f"record BC07 business ledger row for {release_id}",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE {self._qualified_table}"),
            f"drop BC07 {release_id} same-name release table",
        )
        drop_job_id = self._latest_drop_job(env)
        self.release_drop_jobs[release_id] = drop_job_id
        self.latest_same_name_drop_job_id = drop_job_id
        if release_id == self.target_release_id:
            self.target_drop_job_id = drop_job_id

    def _create_ddl_noise(self, env) -> None:
        for index in range(1, 6):
            name = f"bc07_cleanup_{index}"
            require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {self.database}.{name} (id BIGINT PRIMARY KEY)"
                ),
                f"create BC07 DDL noise table {name}",
            )
            require_sql_success(
                env.execute_sql(f"DROP TABLE {self.database}.{name}"),
                f"drop BC07 DDL noise table {name}",
            )

    def _truth(self, env) -> tuple[int, int, int]:
        rows = execute_result_rows(
            env.execute_sql,
            (
                f"SELECT COUNT(*), COALESCE(SUM(event_id),0), "
                "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#',event_id,tenant_id,event_type,amount_cents,payload))),0) "
                f"FROM {self._qualified_table}"
            ),
            "read BC07 release business truth",
        )
        return tuple(int(value) for value in rows[0])

    def _max_ddl_job_id(self, env) -> int:
        return int(
            self._scalar(
                env,
                "SELECT COALESCE(MAX(JOB_ID),0) FROM information_schema.ddl_jobs",
            )
        )

    @staticmethod
    def _gc_lifetime(env) -> str:
        rows = execute_result_rows(
            env.execute_sql,
            "SHOW GLOBAL VARIABLES LIKE 'tidb_gc_life_time'",
            "read BC07 TiDB GC lifetime",
        )
        if len(rows) != 1 or len(rows[0]) < 2:
            raise ValueError(
                "BC07 GC lifetime query expected one variable row with a value: "
                f"rows={rows!r}"
            )
        return str(rows[0][1])

    def _latest_drop_job(self, env) -> int:
        rows = execute_result_rows(
            env.execute_sql,
            (
                "SELECT JOB_ID FROM information_schema.ddl_jobs "
                f"WHERE DB_NAME='{self.database}' AND TABLE_NAME='{self.table}' "
                "AND JOB_TYPE='drop table' ORDER BY JOB_ID DESC LIMIT 1"
            ),
            f"find latest BC07 DROP job for {self._qualified_table}",
        )
        if len(rows) != 1:
            raise RuntimeError(
                "BC07 expected exactly one latest same-name DROP job row: "
                f"database={self.database!r}, table={self.table!r}, rows={rows!r}"
            )
        return int(rows[0][0])

    @staticmethod
    def _scalar(env, sql: str) -> object:
        rows = execute_result_rows(env.execute_sql, sql, f"BC07 scalar query: {sql}")
        if len(rows) != 1 or len(rows[0]) != 1:
            raise ValueError(f"BC07 scalar query expected one row/column: sql={sql!r}, rows={rows!r}")
        return rows[0][0]
