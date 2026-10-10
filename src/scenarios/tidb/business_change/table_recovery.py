from dataclasses import dataclass, replace

from src.scenarios.workloads import WorkloadProfile
from src.scenarios.evaluation.protocol import structured_reference_report
from src.scenarios.evaluation.tidb.business_change.table_recovery import (
    TidbBusinessChangeTableRecoveryEvaluatorCase,
    TidbBusinessChangeTableRecoveryForPaymentEventsEvaluatorCase,
)

from ...base import (
    BackgroundWorkloadSpec,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


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
                    f"SELECT release_id, transition, occurred_at, traffic_percent, control_epoch "
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
                    f"SELECT control_key, release_id, binding_state, bound_at, change_ticket "
                    f"FROM {database}.{release_binding_table} ORDER BY bound_at, binding_id"
                ),
                qps=0.24,
                tier="MONITOR",
                application_name="deployment-registry",
            ),
            WorkloadProfile(
                name="release_transition_lineage_join",
                sql=(
                    f"SELECT t.release_id, t.transition, t.occurred_at, r.table_id, r.lifecycle_state "
                    f"FROM {database}.{release_transition_table} t "
                    f"JOIN {database}.{release_registry_table} r ON r.release_id=t.release_id "
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
        "'table doesn't exist'；数据库节点仍然 Up，其他归档查询正常。最近一次 release cleanup 可能误删了 "
        "order_events，但同一逻辑表曾被发布流程重复创建和清理。请在 GC 可恢复窗口内恢复原始业务表，"
        "事故边界为 2026-08-03 11:30:00；请从 incident context 和 release transition history 重建该时刻 "
        "order-api/prod 实际 serving 的 release，而不是直接采用当前 desired release。保留当前在线查询负载，"
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
        "crc": 2846650938,
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
        diagnostic_depth=7,
        environmental_complexity=0.910072,
        reference_run_ids=(
            "reference-156__"
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
    expected_crc=2_846_650_938,
    candidate_row_count=2000,
    decoy_row_count=17,
    recovery_gc_lifetime="72h",
    pre_release_id="orders_blue_20260730",
    target_release_id="orders_green_20260731",
    canary_release_id="orders_canary_20260801",
    smoke_release_id="orders_smoke_20260802",
    hotfix_release_id="orders_hotfix_20260803",
    rehearsal_release_id="orders_rehearsal_20260803",
    shadow_release_id="orders_shadow_20260803",
    rollback_release_id="orders_rollback_20260803",
    reference_evidence_counts=(
        ("execute_sql", 27, 56),
        ("query_metrics", 17, 425),
        ("read_log", 1, 25),
        ("search_knowledge", 5, 0),
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
        diagnostic_depth=7,
        environmental_complexity=0.910072,
        reference_run_ids=(
            "reference-242__"
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
    pre_release_id="payments_blue_20260807",
    target_release_id="payments_green_20260808",
    canary_release_id="payments_canary_20260809",
    smoke_release_id="payments_smoke_20260810",
    hotfix_release_id="payments_hotfix_20260810",
    rehearsal_release_id="payments_rehearsal_20260810",
    shadow_release_id="payments_shadow_20260810",
    rollback_release_id="payments_rollback_20260810",
    reference_evidence_counts=(
        ("execute_sql", 27, 56),
        ("query_metrics", 17, 425),
        ("read_log", 1, 25),
        ("search_knowledge", 5, 0),
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
    """Create four real same-name release generations inside the TiDB GC window."""

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
        if self.source_row_count != 2000 or self.expected_crc != 2_846_650_938:
            raise ValueError(
                "BC07 active release fixture is fixed at 2,000 rows and CRC 2846650938: "
                f"rows={self.source_row_count}, crc={self.expected_crc}"
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
                    f"VALUES (129,'gc-lifetime-override','2026-07-29 12:00:00',"
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
                    "(audit_id,action,created_at,config_key,previous_value,requested_value) VALUES "
                    "(130,'gc-window-plan','2026-08-03 11:20:00','tidb_gc_life_time','24h','72h'),"
                    "(131,'gc-window-rehearsal','2026-08-03 12:00:00','tidb_gc_life_time','72h','72h')"
                ),
                "record BC07 planned and rehearsal GC audit noise",
            )
            self._seed_ddl_history(env)
            self._create_release_version(
                env,
                self.pre_release_id,
                "rolled_back",
                "blue",
                self.candidate_row_count,
                "2026-07-30 09:00:00",
                "REL-BLUE-0730",
            )
            self._create_release_version(
                env,
                self.target_release_id,
                "validated",
                "active",
                self.source_row_count,
                "2026-07-31 09:00:00",
                "REL-GREEN-0731",
            )
            self._create_release_version(
                env,
                self.canary_release_id,
                "cancelled_canary",
                "canary",
                self.candidate_row_count,
                "2026-08-01 09:00:00",
                "REL-CANARY-0801",
            )
            self._create_release_version(
                env,
                self.smoke_release_id,
                "cleanup_smoke",
                "smoke",
                self.decoy_row_count,
                "2026-08-02 09:00:00",
                "REL-SMOKE-0802",
            )
            self._create_release_version(
                env,
                self.hotfix_release_id,
                "validated",
                "hotfix",
                self.candidate_row_count,
                "2026-08-03 11:45:00",
                "REL-HOTFIX-0803",
            )
            self._create_release_version(
                env,
                self.rehearsal_release_id,
                "rehearsal",
                "rehearsal",
                self.candidate_row_count,
                "2026-08-03 12:00:00",
                "REL-REHEARSAL-0803",
            )
            self._create_release_version(
                env,
                self.shadow_release_id,
                "shadow",
                "shadow",
                self.candidate_row_count,
                "2026-08-03 12:15:00",
                "REL-SHADOW-0803",
            )
            self._create_release_version(
                env,
                self.rollback_release_id,
                "rolled_back",
                "rollback",
                self.candidate_row_count,
                "2026-08-03 12:30:00",
                "REL-ROLLBACK-0803",
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
        target_serving = self._scalar(
            context.env,
            f"SELECT COUNT(*) FROM {self.database}.{self.release_control_table} c "
            f"JOIN {self.database}.{self.release_binding_table} b ON b.control_key=c.control_key "
            f"WHERE c.service_name='{self.service_name}' AND c.environment='{self.environment}' "
            f"AND c.logical_table='{self.logical_table}' "
            f"AND c.region='global' AND c.control_role='observed' AND b.release_id='{self.target_release_id}' "
            "AND c.status='serving' AND c.traffic_percent=100 "
            f"AND c.control_epoch={int(incident_epoch)} AND c.effective_at <= '{self.incident_at}'",
        )
        if target_serving != 1:
            raise RuntimeError(
                "BC07 activation lost the incident-boundary serving release: "
                f"target_release={self.target_release_id!r}, incident_epoch={incident_epoch!r}, rows={target_serving!r}"
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
                "audit_id BIGINT PRIMARY KEY, action VARCHAR(32) NOT NULL, "
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
                "expected_crc BIGINT NOT NULL, effective_at DATETIME NOT NULL, "
                "change_ticket VARCHAR(64) NOT NULL)"
            ),
            "create BC07 release registry",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.release_control_table} ("
                "control_id BIGINT PRIMARY KEY, service_name VARCHAR(64) NOT NULL, "
                "environment VARCHAR(32) NOT NULL, logical_table VARCHAR(64) NOT NULL, "
                "region VARCHAR(32) NOT NULL, control_role VARCHAR(24) NOT NULL, "
                "control_key VARCHAR(64) NOT NULL, effective_at DATETIME NOT NULL, "
                "status VARCHAR(24) NOT NULL, traffic_percent INT NOT NULL, "
                "control_epoch BIGINT NOT NULL, change_ticket VARCHAR(64) NOT NULL)"
            ),
            "create BC07 release control table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.release_ledger_table} ("
                "release_id VARCHAR(64) PRIMARY KEY, order_count BIGINT NOT NULL, "
                "event_id_sum BIGINT NOT NULL, crc BIGINT NOT NULL, "
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
                "transition_id BIGINT PRIMARY KEY, release_id VARCHAR(64) NOT NULL, "
                "service_name VARCHAR(64) NOT NULL, environment VARCHAR(32) NOT NULL, "
                "logical_table VARCHAR(64) NOT NULL, transition VARCHAR(32) NOT NULL, "
                "occurred_at DATETIME NOT NULL, traffic_percent INT NOT NULL, "
                "control_epoch BIGINT NOT NULL, change_ticket VARCHAR(64) NOT NULL, "
                "actor VARCHAR(64) NOT NULL)"
            ),
            "create BC07 release transition history",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.release_binding_table} ("
                "binding_id BIGINT PRIMARY KEY, control_key VARCHAR(64) NOT NULL, "
                "release_id VARCHAR(64) NOT NULL, binding_state VARCHAR(24) NOT NULL, "
                "bound_at DATETIME NOT NULL, change_ticket VARCHAR(64) NOT NULL)"
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
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.release_control_table} "
                "(control_id,service_name,environment,logical_table,region,control_role,control_key,"
                "effective_at,status,traffic_percent,control_epoch,change_ticket) VALUES "
                f"(1,'{self.service_name}','{self.environment}','{self.logical_table}','global','observed','deploy-20260731-epoch-41',"
                "'2026-07-31 09:20:00','serving',100,41,'REL-GREEN-0731'),"
                f"(2,'{self.service_name}','{self.environment}','{self.logical_table}','us-east','observed','deploy-20260731-epoch-41',"
                "'2026-07-31 09:20:00','serving',100,41,'REL-GREEN-0731'),"
                f"(3,'{self.service_name}','{self.environment}','{self.logical_table}','eu-west','observed','deploy-20260801-canary-shadow',"
                "'2026-08-01 09:10:00','shadow',0,41,'REL-CANARY-0801'),"
                f"(4,'{self.service_name}','{self.environment}','{self.logical_table}','global','desired','deploy-20260803-epoch-42',"
                "'2026-08-03 11:45:00','pending',0,42,'REL-HOTFIX-0803'),"
                f"(5,'{self.service_name}','{self.environment}','{self.logical_table}','global','observed','deploy-20260731-epoch-41',"
                "'2026-08-03 11:45:00','serving',100,42,'REL-HOTFIX-0803'),"
                f"(6,'{self.service_name}','staging','{self.logical_table}','global','observed','deploy-20260801-canary-serving',"
                "'2026-08-01 09:10:00','serving',100,7,'REL-CANARY-0801'),"
                f"(7,'release-dashboard','prod','{self.table}','global','observed','deploy-20260802-cleanup',"
                "'2026-08-03 11:50:00','cleanup',0,43,'REL-SMOKE-0802'),"
                f"(8,'reconciliation-worker','{self.environment}','{self.logical_table}','global','observed','deploy-20260730-rollback',"
                "'2026-07-30 09:00:00','retired',0,40,'REL-BLUE-0730'),"
                f"(9,'{self.service_name}','{self.environment}','{self.logical_table}','global','observed','deploy-20260803-rehearsal-epoch-41',"
                "'2026-08-03 11:15:00','serving',100,41,'REL-REHEARSAL-ADMISSION'),"
                f"(10,'{self.service_name}','{self.environment}','{self.logical_table}','global','observed','deploy-20260731-rollback-replay',"
                "'2026-07-31 09:31:00','serving',100,41,'REL-BLUE-ROLLBACK-REPLAY')"
            ),
            "insert BC07 release control rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.release_binding_table} "
                "(binding_id,control_key,release_id,binding_state,bound_at,change_ticket) VALUES "
                f"(1,'deploy-20260731-epoch-41','{self.target_release_id}','superseded','2026-07-31 09:20:00','REL-GREEN-0731'),"
                f"(2,'deploy-20260801-canary-shadow','{self.canary_release_id}','bound','2026-08-01 09:10:00','REL-CANARY-0801'),"
                f"(3,'deploy-20260731-epoch-41','{self.hotfix_release_id}','bound','2026-08-03 11:45:00','REL-HOTFIX-0803'),"
                f"(4,'deploy-20260801-canary-serving','{self.canary_release_id}','bound','2026-08-01 09:10:00','REL-CANARY-0801'),"
                f"(5,'deploy-20260802-cleanup','{self.smoke_release_id}','bound','2026-08-03 11:50:00','REL-SMOKE-0802'),"
                f"(6,'deploy-20260730-rollback','{self.pre_release_id}','bound','2026-07-30 09:00:00','REL-BLUE-0730'),"
                f"(7,'deploy-20260731-epoch-41-legacy','{self.rollback_release_id}','stale','2026-07-31 09:21:00','REL-LEGACY-0731'),"
                f"(8,'deploy-20260803-rehearsal-epoch-41','{self.rehearsal_release_id}','bound','2026-08-03 11:15:00','REL-REHEARSAL-ADMISSION'),"
                f"(9,'deploy-20260731-rollback-replay','{self.pre_release_id}','bound','2026-07-31 09:31:00','REL-BLUE-ROLLBACK-REPLAY')"
            ),
            "insert BC07 release binding map",
        )

    def _insert_incident_and_transition_history(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.incident_context_table} "
                "(incident_id,service_name,environment,logical_table,incident_at,last_known_good_at,"
                "expected_control_epoch,evidence_source,scope_note) VALUES "
                f"(9001,'{self.service_name}','{self.environment}','{self.logical_table}','{self.incident_at}',"
                "'2026-08-03 11:29:59',41,'incident-coordinator','global serving release before cleanup')"
            ),
            "insert BC07 incident boundary",
        )
        transitions = (
            (1, self.pre_release_id, "retired", "2026-07-30 08:55:00", 0, 40, "REL-BLUE-0730", "release-bot"),
            (2, self.pre_release_id, "rollback_completed", "2026-07-30 09:30:00", 0, 40, "REL-BLUE-0730", "release-bot"),
            (3, self.target_release_id, "deploy_started", "2026-07-31 08:55:00", 0, 41, "REL-GREEN-0731", "release-bot"),
            (4, self.target_release_id, "traffic_shift", "2026-07-31 09:05:00", 10, 41, "REL-GREEN-0731", "release-bot"),
            (5, self.target_release_id, "traffic_shift", "2026-07-31 09:20:00", 100, 41, "REL-GREEN-0731", "release-bot"),
            (6, self.target_release_id, "promoted", "2026-07-31 09:25:00", 100, 41, "REL-GREEN-0731", "release-controller"),
            (7, self.target_release_id, "reconciled", "2026-07-31 09:30:00", 100, 41, "REL-GREEN-0731", "ledger-reconciler"),
            (8, self.canary_release_id, "shadow_started", "2026-08-01 09:00:00", 0, 41, "REL-CANARY-0801", "release-bot"),
            (9, self.canary_release_id, "shadow_aborted", "2026-08-01 09:10:00", 0, 41, "REL-CANARY-0801", "release-controller"),
            (10, self.smoke_release_id, "cleanup_started", "2026-08-02 09:00:00", 0, 41, "REL-SMOKE-0802", "release-cleaner"),
            (11, self.smoke_release_id, "cleanup_completed", "2026-08-02 09:02:00", 0, 41, "REL-SMOKE-0802", "release-cleaner"),
            (12, self.hotfix_release_id, "deploy_started", "2026-08-03 11:45:00", 0, 42, "REL-HOTFIX-0803", "release-bot"),
            (13, self.hotfix_release_id, "traffic_shift", "2026-08-03 11:50:00", 100, 42, "REL-HOTFIX-0803", "release-bot"),
            (14, self.hotfix_release_id, "promoted", "2026-08-03 11:55:00", 100, 42, "REL-HOTFIX-0803", "release-controller"),
            (15, self.rehearsal_release_id, "rehearsal_started", "2026-08-03 12:00:00", 0, 43, "REL-REHEARSAL-0803", "release-bot"),
            (16, self.rehearsal_release_id, "rehearsal_completed", "2026-08-03 12:04:00", 0, 43, "REL-REHEARSAL-0803", "release-bot"),
            (17, self.shadow_release_id, "shadow_started", "2026-08-03 12:15:00", 0, 44, "REL-SHADOW-0803", "release-bot"),
            (18, self.shadow_release_id, "shadow_completed", "2026-08-03 12:20:00", 0, 44, "REL-SHADOW-0803", "release-bot"),
            (19, self.rollback_release_id, "rollback_candidate", "2026-08-03 12:30:00", 0, 45, "REL-ROLLBACK-0803", "release-bot"),
            (20, self.rollback_release_id, "rollback_completed", "2026-08-03 12:35:00", 0, 45, "REL-ROLLBACK-0803", "release-controller"),
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.release_transition_table} "
                "(transition_id,release_id,service_name,environment,logical_table,transition,occurred_at,"
                "traffic_percent,control_epoch,change_ticket,actor) VALUES "
                + ",".join(
                    f"({transition_id},'{release_id}','{self.service_name}','{self.environment}',"
                    f"'{self.logical_table}','{transition}',"
                    f"'{occurred_at}',{traffic_percent},{control_epoch},'{ticket}','{actor}')"
                    for transition_id, release_id, transition, occurred_at, traffic_percent, control_epoch, ticket, actor
                    in transitions
                )
            ),
            "insert BC07 release transition history",
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
                payload = (
                    bytes.fromhex("3a3ef539")
                    if generation == "active" and event_id == self.source_row_count
                    else (
                        f"order-{event_id:04d}".encode()
                        if generation in {"active", "archive"}
                        else f"{generation}-order-{event_id:04d}".encode()
                    )
                )
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
        lifecycle_state: str,
        generation: str,
        row_count: int,
        effective_at: str,
        change_ticket: str,
    ) -> None:
        require_sql_success(
            env.execute_sql(f"CREATE TABLE {self._qualified_table} ({self._event_schema()})"),
            f"create BC07 {release_id} same-name release table",
        )
        self._insert_event_rows(env, self.table, row_count, generation)
        truth = self._truth(env)
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
                f"'{lifecycle_state}','{generation}',{truth[0]},{truth[1]},{truth[2]},"
                f"'{effective_at}','{change_ticket}')"
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
