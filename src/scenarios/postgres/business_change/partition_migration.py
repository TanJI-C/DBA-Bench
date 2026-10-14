import threading
import time
from dataclasses import dataclass
from typing import List, Mapping

import psycopg2

from src.scenarios.evaluation.postgres.business_change import (
    PgBusinessChangePartitionMigrationForPaymentEventsAttachSimpleEvaluatorCase,
    PgBusinessChangePartitionMigrationForPaymentEventsAttachStallEvaluatorCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import (
    _cancel_open_connection,
    _join_thread,
    _json_object,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    PostgresCaseRuntime,
    PostgresRuntimeSpec,
    BackgroundWorkloadSpec,
    DifficultyCalibration,
    FaultPlan,
    CaseResourceSpec,
    PostgresScenario,
    PostgresScenarioCase,
)


POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)

# Two-phase commit support for the in-doubt prepared batch transaction. A case
# runtime parameter set replaces the deployment defaults wholesale, so it must
# carry the full standard option list plus the 2PC switch.
_PREPARED_TX_PARAMETERS = PostgresRuntimeSpec(
    parameters=(
        ("shared_buffers", "128MB"),
        ("work_mem", "16MB"),
        ("shared_preload_libraries", "pg_stat_statements"),
        ("logging_collector", "on"),
        ("log_destination", "stderr"),
        ("log_directory", "/var/log/postgresql"),
        ("log_filename", "postgresql-%Y-%m-%d_%H%M%S.log"),
        ("log_rotation_age", "1d"),
        ("log_rotation_size", "100MB"),
        ("max_prepared_transactions", "10"),
    )
)

# Partition bounds for every attachable monthly child, keyed by relation name.
_CHILD_PARTITION_BOUNDS = {
    "payment_events_2026_07": ("2026-07-01", "2026-08-01"),
    "payment_events_2026_08": ("2026-08-01", "2026-09-01"),
}


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangePartitionMigrationCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    legacy_table: str
    parent_table: str
    default_partition: str
    staging_children: tuple[str, ...]
    may_partition: str
    june_partition: str
    july_partition: str
    attach_july_partition: bool
    conflict_bound_start: str
    conflict_bound_end: str
    refund_table: str | None
    refund_child: str | None
    archive_table: str
    archive_child_a: str
    archive_child_b: str
    audit_table: str
    job_status_table: str
    payment_sequence: str
    seed_ref_prefix: str
    legacy_rows: int
    may_rows: int
    june_rows: int
    july_rows: int
    conflict_rows: int
    decoy_rows: int
    staging_residual_july_rows: int
    staging_residual_july_deleted_rows: int
    staging_residual_august_rows: int
    archive_rows: int
    audit_rows: int
    simulated_legacy_rows: int
    report_application_name: str
    worker_application_name: str
    backfill_application_name: str | None
    prepared_move_gid: str | None
    ingest_batch_ref_prefix: str | None
    ingest_batch_rows: int
    report_hold_seconds: float
    attach_lock_timeout_seconds: float
    attach_retry_interval_seconds: float
    incident_attempts: int
    preflight_validation_attempt: bool
    prepared_xact_gid: str | None
    decoy_prepared_xact_gid: str | None
    batch3_prepared_xact_gid: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangePartitionMigrationForPaymentEventsAttachStallScenarioCase(
    PgBusinessChangePartitionMigrationCase
):
    pass


def build_partition_migration_noise_profiles() -> List[WorkloadProfile]:
    """Business-shaped live workload over the payment partition migration domain.

    The ingest writer keeps appending payments to the partitioned parent (they
    route into the default partition until the monthly partitions exist), and
    the remaining probes are adjacent payment-domain work so pg_stat_activity
    and the logs carry real same-domain noise next to the migration incident.
    """
    return [
        WorkloadProfile(
            name="payment_stream_ingest",
            sql=(
                "INSERT INTO payment_events_partitioned "
                "(payment_ref, channel, amount, event_time) VALUES ("
                "'live-' || md5(random()::text), 'live', "
                "(random() * 400 + 10)::numeric(12,2), now());"
            ),
            qps=0.6,
            tier="LIGHT",
            commit=True,
            application_name="payment-stream-ingest",
        ),
        WorkloadProfile(
            name="payment_recent_reader",
            sql=(
                "SELECT channel, count(*) AS payments, round(sum(amount), 2) AS gross "
                "FROM payment_events_partitioned "
                "WHERE event_time > now() - interval '7 days' "
                "GROUP BY channel"
            ),
            qps=0.4,
            tier="LIGHT",
            application_name="payment-recent-reader",
        ),
        WorkloadProfile(
            name="legacy_payment_audit_probe",
            sql=(
                "SELECT channel, count(*) AS rows, round(sum(amount), 2) AS total "
                "FROM payment_events GROUP BY channel"
            ),
            qps=0.25,
            tier="LIGHT",
            application_name="legacy-payment-audit",
        ),
        WorkloadProfile(
            name="archive_neighbor_rollup",
            sql=(
                "SELECT count(*) AS archived, round(sum(amount), 2) AS total "
                "FROM payment_events_archive_partitioned"
            ),
            qps=0.3,
            tier="LIGHT",
            application_name="archive-payment-rollup",
        ),
        WorkloadProfile(
            name="payment_audit_shadow_probe",
            sql=(
                "SELECT status, count(*) AS entries FROM payment_events_audit_shadow "
                "GROUP BY status"
            ),
            qps=0.3,
            tier="LIGHT",
            application_name="payment-audit-shadow",
        ),
        WorkloadProfile(
            name="missing_payment_report_cache_log_noise",
            sql="SELECT count(*) FROM payment_events_report_cache_missing;",
            qps=0.3,
            tier="LOG_NOISE",
            application_name="payment-report-cache",
        ),
    ]


def build_partition_migration_simple_noise_profiles() -> List[WorkloadProfile]:
    """Controlled Easy-case noise: fewer live probes, one same-domain rollup."""
    return [
        WorkloadProfile(
            name="payment_stream_ingest",
            sql=(
                "INSERT INTO payment_events_partitioned "
                "(payment_ref, channel, amount, event_time) VALUES ("
                "'live-' || md5(random()::text), 'live', "
                "(random() * 400 + 10)::numeric(12,2), now());"
            ),
            qps=0.4,
            tier="LIGHT",
            commit=True,
            application_name="payment-stream-ingest",
        ),
        WorkloadProfile(
            name="payment_recent_reader",
            sql=(
                "SELECT channel, count(*) AS payments, round(sum(amount), 2) AS gross "
                "FROM payment_events_partitioned "
                "WHERE event_time > now() - interval '7 days' "
                "GROUP BY channel"
            ),
            qps=0.3,
            tier="LIGHT",
            application_name="payment-recent-reader",
        ),
        WorkloadProfile(
            name="archive_neighbor_rollup",
            sql=(
                "SELECT count(*) AS archived, round(sum(amount), 2) AS total "
                "FROM payment_events_archive_partitioned"
            ),
            qps=0.2,
            tier="LIGHT",
            application_name="archive-payment-rollup",
        ),
    ]


_PGBUSINESSCHANGEPARTITIONMIGRATIONSCENARIO_CASE = (
    PgBusinessChangePartitionMigrationForPaymentEventsAttachStallScenarioCase(
        case_id="payment_events_attach_stall",
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": (
                            "attach partition waits for access exclusive lock behind "
                            "a long running report transaction"
                        ),
                        "entity": "payment_events_attach_stall",
                        "evidence": [
                            "pg_stat_activity shows the migration attach queued behind "
                            "the idle-in-transaction report session"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": (
                            "default partition contains rows inside the attached range "
                            "so the attach validation fails"
                        ),
                        "entity": "payment_events_attach_stall",
                        "evidence": [
                            "payment_events_default holds seed rows with event_time in "
                            "[2026-08-01, 2026-09-01) and the job log records the "
                            "default partition validation failure"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": (
                            "replaying attach partition keeps failing until the "
                            "conflicting rows are moved out of the default partition"
                        ),
                        "entity": "payment_events_attach_stall",
                        "evidence": [
                            "moving the conflicting rows into the partition tree and "
                            "replaying the attach completed the migration"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": (
                            "an in-doubt prepared two-phase transaction from the "
                            "migration job batch-2 holds row-exclusive locks on the "
                            "default partition and the staging table so the attach "
                            "stays blocked after the report session is cleared"
                        ),
                        "entity": "payment_events_attach_stall",
                        "evidence": [
                            "pg_locks shows granted row exclusive locks with no "
                            "backend pid; the pid-less lock entries were attributed "
                            "to their in-doubt transactions via the shared virtual "
                            "transaction and pg_prepared_xacts.transaction",
                            "the job ledger records the batch-2 validator veto "
                            "(DELETE rowcount 12000 vs planned 4500) and the "
                            "batch-3 retry attempt already committed, so the "
                            "vetoed batch and the duplicate prepared copy were "
                            "rolled back and the batches re-run",
                        ],
                    },
                ]
            },
            "outcome": {
                "changes": [
                    "moved the conflicting rows out of payment_events_default into the "
                    "partition tree",
                    "rolled back the validator-vetoed migration batch transaction "
                    "and the duplicate prepared ingest copy per the ledger records, "
                    "then re-ran the batch move",
                    "replayed ATTACH PARTITION payment_events_2026_08 after the data "
                    "boundary was fixed",
                ],
                "verification": [
                    "pg_inherits shows payment_events_2026_08 attached to "
                    "payment_events_partitioned",
                    "payment_events_default has no rows left inside the attached range "
                    "and seeded payment rows are conserved",
                    "pg_prepared_xacts is empty and the attach replay acquired its lock",
                ],
            },
            "summary": (
                "The partition migration stall was caused by conflict rows inside "
                "payment_events_default; after moving them into the partition tree the "
                "attach replay completed and payment traffic recovered."
            ),
        },
        case_no=0,
        evaluator=PgBusinessChangePartitionMigrationForPaymentEventsAttachStallEvaluatorCase,
        base_image_name="aiopsbench-pg-default:latest",
        workload_tag="default",
        title=(
            "Partition migration ATTACH stall: default-partition conflict rows plus an "
            "AccessExclusiveLock queue behind a long report transaction."
        ),
        alert=(
            "变更发布告警：昨晚支付域发布后出现大面积读写停顿，支付写入超时明显增多，"
            "至今未恢复。发布包含支付库结构变更，具体影响范围未知。请尽快恢复业务正常"
            "读写，完成本次变更收尾，并核对支付数据完整性。"
        ),
        alert_en="Change release alert: after last night's payment domain release, widespread read/write stalls appeared, payment write timeouts increased markedly, and the situation has not recovered so far. The release included structural changes to the payment database, and the exact scope of impact is unknown. Restore normal business reads and writes as soon as possible, finish wrapping up this change, and check the integrity of the payment data.",
        initial_state={
            "status": "change_degraded",
            "migration": "attach_partition_failed",
            "symptom": "payment_read_write_stall",
            "table": "payment_events_partitioned",
        },
        expected_target={
            "status": "recovered",
            "migration": "attach_partition_completed",
            "data": "payment_rows_conserved",
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=tuple(build_partition_migration_noise_profiles()),
            worker_count=3,
            seed=0x1C03,
            warmup_seconds=4,
        ),
        runtime=PostgresCaseRuntime(
            resources=POSTGRES_RESOURCES,
            parameters=_PREPARED_TX_PARAMETERS,
        ),
        legacy_table="payment_events",
        parent_table="payment_events_partitioned",
        default_partition="payment_events_default",
        staging_children=("payment_events_2026_07", "payment_events_2026_08"),
        may_partition="payment_events_2026_05",
        june_partition="payment_events_2026_06",
        july_partition="payment_events_2026_07",
        attach_july_partition=False,
        conflict_bound_start="2026-07-01",
        conflict_bound_end="2026-09-01",
        refund_table="refund_events_partitioned",
        refund_child="refund_events_2026_08",
        archive_table="payment_events_archive_partitioned",
        archive_child_a="payment_events_archive_2024",
        archive_child_b="payment_events_archive_2025",
        audit_table="payment_events_audit_shadow",
        job_status_table="payment_migration_job_status",
        payment_sequence="payment_events_payment_id_seq",
        seed_ref_prefix="seed-",
        legacy_rows=40000,
        may_rows=30000,
        june_rows=30000,
        july_rows=20000,
        conflict_rows=12000,
        decoy_rows=150,
        staging_residual_july_rows=5000,
        staging_residual_july_deleted_rows=4800,
        staging_residual_august_rows=4500,
        archive_rows=8000,
        audit_rows=2000,
        simulated_legacy_rows=1200000,
        report_application_name="payment-nightly-report",
        worker_application_name="payment-migration-worker",
        backfill_application_name=None,
        prepared_move_gid=None,
        ingest_batch_ref_prefix=None,
        ingest_batch_rows=0,
        report_hold_seconds=1800.0,
        attach_lock_timeout_seconds=45.0,
        attach_retry_interval_seconds=15.0,
        incident_attempts=2,
        preflight_validation_attempt=True,
        prepared_xact_gid="2pc-9f4c7a1e3d",
        decoy_prepared_xact_gid="2pc-e3a91c6d75",
        batch3_prepared_xact_gid="2pc-c7b25e8f40",
        difficulty=DifficultyCalibration(
            diagnostic_depth=4,
            environmental_complexity=0.522727,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_business_change_partition_migration_"
                "payment_events_attach_stall_MockLLMAgent.json",
            ),
            protocol_version="difficulty-v2",
        ),
    )
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangePartitionMigrationForPaymentEventsAttachSimpleScenarioCase(
    PgBusinessChangePartitionMigrationCase
):
    pass


_PGBUSINESSCHANGEPARTITIONMIGRATIONSCENARIO_SIMPLE_CASE = (
    PgBusinessChangePartitionMigrationForPaymentEventsAttachSimpleScenarioCase(
        case_id="payment_events_attach_simple",
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": (
                            "attach partition waits for access exclusive lock behind "
                            "a long running report transaction"
                        ),
                        "entity": "payment_events_attach_simple",
                        "evidence": [
                            "pg_stat_activity shows the attach queued behind the "
                            "idle-in-transaction report session"
                        ],
                    },
                ]
            },
            "outcome": {
                "changes": [
                    "cleared the open transactions holding locks on the payment "
                    "partition tree and the august staging table",
                    "rolled back the prepared attempt-1 copy of the ingest batch "
                    "because the ledger shows the retry worker already committed "
                    "the batch",
                    "replayed ATTACH PARTITION payment_events_2026_08 after the "
                    "lock queue was cleared",
                ],
                "verification": [
                    "pg_inherits shows payment_events_2026_08 attached to "
                    "payment_events_partitioned",
                    "seeded payment rows are conserved and payment reads work",
                    "the august ingest batch appears exactly once in the "
                    "partition tree",
                ],
            },
            "summary": (
                "The migration attach was queued behind open transactions holding "
                "payment table locks; the job ledger showed the ingest batch was "
                "already committed by the retry attempt, so the prepared "
                "duplicate was rolled back and the attach replay completed the "
                "migration."
            ),
        },
        case_no=1,
        evaluator=PgBusinessChangePartitionMigrationForPaymentEventsAttachSimpleEvaluatorCase,
        base_image_name="aiopsbench-pg-default:latest",
        workload_tag="default",
        title=(
            "Simplified partition migration attach queued behind long-running "
            "open transactions."
        ),
        alert=(
            "变更告警：payment_events 分区改造的 ATTACH 步骤执行缓慢，监控显示支付查询"
            "偶发变慢，改造作业在等待数据库锁，多次执行仍未完成。请处理阻塞并完成 "
            "payment_events 的分区改造，注意保持支付数据完整。"
        ),
        alert_en="Change alert: the ATTACH step of the payment_events partitioning rework is running slowly, monitoring shows that payment queries are occasionally slow, and the rework job is waiting on a database lock and has not finished after several attempts. Resolve the blocking and complete the partitioning rework of payment_events, taking care to keep the payment data intact.",
        initial_state={
            "status": "change_degraded",
            "migration": "attach_partition_waiting",
            "symptom": "intermittent_payment_latency",
            "table": "payment_events_partitioned",
        },
        expected_target={
            "status": "recovered",
            "migration": "attach_partition_completed",
            "data": "payment_rows_conserved",
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=tuple(build_partition_migration_simple_noise_profiles()),
            worker_count=1,
            seed=0x1C04,
            warmup_seconds=2,
        ),
        runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
        legacy_table="payment_events",
        parent_table="payment_events_partitioned",
        default_partition="payment_events_default",
        staging_children=("payment_events_2026_08",),
        may_partition="payment_events_2026_05",
        june_partition="payment_events_2026_06",
        july_partition="payment_events_2026_07",
        attach_july_partition=True,
        conflict_bound_start="2026-08-01",
        conflict_bound_end="2026-09-01",
        refund_table=None,
        refund_child=None,
        archive_table="payment_events_archive_partitioned",
        archive_child_a="payment_events_archive_2024",
        archive_child_b="payment_events_archive_2025",
        audit_table="payment_events_audit_shadow",
        job_status_table="payment_migration_job_status",
        payment_sequence="payment_events_payment_id_seq",
        seed_ref_prefix="seed-",
        legacy_rows=40000,
        may_rows=30000,
        june_rows=30000,
        july_rows=10000,
        conflict_rows=0,
        decoy_rows=0,
        staging_residual_july_rows=0,
        staging_residual_july_deleted_rows=0,
        staging_residual_august_rows=0,
        archive_rows=8000,
        audit_rows=2000,
        simulated_legacy_rows=1200000,
        report_application_name="payment-nightly-report",
        worker_application_name="payment-migration-worker",
        backfill_application_name="payment-august-backfill",
        prepared_move_gid="payment_migration_august_move_p1",
        ingest_batch_ref_prefix="aug-ingest-b1-",
        ingest_batch_rows=800,
        report_hold_seconds=1800.0,
        attach_lock_timeout_seconds=20.0,
        attach_retry_interval_seconds=15.0,
        incident_attempts=4,
        preflight_validation_attempt=False,
        prepared_xact_gid=None,
        decoy_prepared_xact_gid=None,
        batch3_prepared_xact_gid=None,
        difficulty=DifficultyCalibration(
            diagnostic_depth=3,
            environmental_complexity=0.2,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_business_change_partition_migration_"
                "payment_events_attach_simple_MockLLMAgent.json",
            ),
            protocol_version="difficulty-v2",
        ),
    )
)


class PgBusinessChangePartitionMigrationInjector(BaseFaultInjector):
    """PostgreSQL partition-migration change incident.

    install: seed the legacy/patched payment schema, monthly partitions, default
    partition (with conflict rows for the Hard case), the standalone staging
    child, and a database-level lock/statement guard.
    activate: run the real failed ATTACH validation attempt (Hard), start the
    long report transaction, then start the bounded migration worker whose real
    ATTACH statements queue for AccessExclusiveLock behind the report session.
    """

    def __init__(self):
        self.env = None
        self._stop_event = None
        self._report_thread = None
        self._worker_thread = None
        self._backfill_thread = None
        self._report_conn = None
        self._worker_conn = None
        self._backfill_conn = None
        self._job_rows = []

    # ------------------------------------------------------------------ utils

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.legacy_table = _validate_sql_identifier(config["legacy_table"], "legacy_table")
        self.parent_table = _validate_sql_identifier(config["parent_table"], "parent_table")
        self.default_partition = _validate_sql_identifier(
            config["default_partition"], "default_partition"
        )
        self.staging_children = tuple(
            _validate_sql_identifier(child, "staging_children")
            for child in config["staging_children"]
        )
        if not self.staging_children or any(
            child not in _CHILD_PARTITION_BOUNDS for child in self.staging_children
        ):
            raise ValueError(
                "staging_children must be known monthly children: "
                f"staging_children={self.staging_children!r}, "
                f"known={sorted(_CHILD_PARTITION_BOUNDS)}"
            )
        self.may_partition = _validate_sql_identifier(config["may_partition"], "may_partition")
        self.june_partition = _validate_sql_identifier(
            config["june_partition"], "june_partition"
        )
        self.july_partition = _validate_sql_identifier(config["july_partition"], "july_partition")
        self.attach_july_partition = bool(config["attach_july_partition"])
        self.conflict_bound_start = str(config["conflict_bound_start"])
        self.conflict_bound_end = str(config["conflict_bound_end"])
        self.refund_table = (
            _validate_sql_identifier(config["refund_table"], "refund_table")
            if config.get("refund_table") else None
        )
        self.refund_child = (
            _validate_sql_identifier(config["refund_child"], "refund_child")
            if config.get("refund_child") else None
        )
        self.archive_table = _validate_sql_identifier(config["archive_table"], "archive_table")
        self.archive_child_a = _validate_sql_identifier(
            config["archive_child_a"], "archive_child_a"
        )
        self.archive_child_b = _validate_sql_identifier(
            config["archive_child_b"], "archive_child_b"
        )
        self.audit_table = _validate_sql_identifier(config["audit_table"], "audit_table")
        self.job_status_table = _validate_sql_identifier(
            config["job_status_table"], "job_status_table"
        )
        self.payment_sequence = _validate_sql_identifier(
            config["payment_sequence"], "payment_sequence"
        )
        self.seed_ref_prefix = str(config["seed_ref_prefix"])
        self.stuck_child = self.staging_children[0]
        self.legacy_rows = int(config["legacy_rows"])
        self.may_rows = int(config["may_rows"])
        self.june_rows = int(config["june_rows"])
        self.july_rows = int(config["july_rows"])
        self.conflict_rows = int(config["conflict_rows"])
        self.decoy_rows = int(config["decoy_rows"])
        self.staging_residual_july_rows = int(config["staging_residual_july_rows"])
        self.staging_residual_july_deleted_rows = int(
            config["staging_residual_july_deleted_rows"]
        )
        self.staging_residual_august_rows = int(config["staging_residual_august_rows"])
        self.archive_rows = int(config["archive_rows"])
        self.audit_rows = int(config["audit_rows"])
        self.simulated_legacy_rows = int(config["simulated_legacy_rows"])
        self.report_application_name = str(config["report_application_name"])
        self.worker_application_name = str(config["worker_application_name"])
        self.backfill_application_name = (
            str(config["backfill_application_name"])
            if config.get("backfill_application_name") else None
        )
        self.prepared_move_gid = (
            str(config["prepared_move_gid"])
            if config.get("prepared_move_gid") else None
        )
        self.ingest_batch_ref_prefix = (
            str(config["ingest_batch_ref_prefix"])
            if config.get("ingest_batch_ref_prefix") else None
        )
        self.ingest_batch_rows = int(config.get("ingest_batch_rows") or 0)
        self.report_hold_seconds = float(config["report_hold_seconds"])
        self.attach_lock_timeout_seconds = float(config["attach_lock_timeout_seconds"])
        self.attach_retry_interval_seconds = float(config["attach_retry_interval_seconds"])
        self.incident_attempts = int(config["incident_attempts"])
        self.preflight_validation_attempt = bool(config["preflight_validation_attempt"])
        self.prepared_xact_gid = (
            str(config["prepared_xact_gid"]) if config.get("prepared_xact_gid") else None
        )
        self.decoy_prepared_xact_gid = (
            str(config["decoy_prepared_xact_gid"])
            if config.get("decoy_prepared_xact_gid") else None
        )
        self.batch3_prepared_xact_gid = (
            str(config["batch3_prepared_xact_gid"])
            if config.get("batch3_prepared_xact_gid") else None
        )
        self.prepared_gids = tuple(
            gid for gid in (
                self.prepared_xact_gid,
                self.decoy_prepared_xact_gid,
                self.batch3_prepared_xact_gid,
            )
            if gid is not None
        )

    def _connect(self, application_name: str):
        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            application_name=application_name,
            connect_timeout=5,
        )
        conn.autocommit = True
        return conn

    def _record_job_row(self, conn, step: str, status: str, detail: str = None) -> None:
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {self.job_status_table} (step, status, detail) "
                "VALUES (%s, %s, %s)",
                (step, status, detail),
            )
        self._job_rows.append({"step": step, "status": status, "detail": detail})

    def _rollback_prepared_xact(self, env) -> None:
        """Roll back leftover in-doubt transactions from a previous run.

        Their row-exclusive locks would otherwise block every DROP of the case
        objects in install/recover and leak into unrelated runs.
        """
        for gid in self.prepared_gids:
            payload = _json_object(
                env.execute_sql(
                    "SELECT gid FROM pg_prepared_xacts WHERE database = current_database() "
                    f"AND gid = '{gid}';"
                ),
                "check leftover in-doubt prepared transaction",
            )
            for row in payload["result"]:
                _require_sql_success(
                    env.execute_sql(f"ROLLBACK PREPARED '{row[0]}';"),
                    f"roll back leftover prepared transaction gid={row[0]!r}",
                )

    # ----------------------------------------------------------------- install

    def install(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        env = self.env
        print(
            f"[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
            f"Installing payment partition migration state on {self.parent_table}..."
        )
        if self.prepared_move_gid:
            self._enable_two_phase_commit(env)
        self._reset_database_guard(env)
        self._rollback_prepared_xact(env)
        self._drop_case_objects(env)
        self._create_payment_schema(env)
        self._seed_payment_data(env)
        self._create_noise_objects(env)
        if self.prepared_move_gid:
            self._create_prepared_move_residual(env)
        self._apply_database_guard(env)
        self._verify_persistent_state()
        self._start_incident()
        print(
            "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
            "Persistent payment partition state ready and incident active."
        )

    def _enable_two_phase_commit(self, env) -> None:
        """Turn on max_prepared_transactions and restart the PG process.

        The prepared-transaction residual is persistent state, so the setting is
        applied via ALTER SYSTEM before any Case object is created; pg_ctl fast
        restart keeps the container running and the env reconnects afterwards.
        """
        _require_sql_success(
            env.execute_sql("ALTER SYSTEM SET max_prepared_transactions = '10';"),
            "enable prepared transactions for the migration residual",
        )
        if not env.deployment.restart_pg():
            raise RuntimeError(
                "Partition-migration install could not restart PostgreSQL to apply "
                f"max_prepared_transactions: container={env.deployment.container_name}"
            )
        if not env.reconnect():
            raise RuntimeError(
                "Partition-migration install could not reconnect after the "
                "max_prepared_transactions restart"
            )

    def _create_prepared_move_residual(self, env) -> None:
        """Leave the in-doubt two-phase ingest batch behind.

        The migration job ingested the august payment batch with a two-phase
        commit (attempt 1) and crashed right after PREPARE TRANSACTION. The
        gateway redelivered the batch after its timeout and the retry worker
        (attempt 2) already ingested and committed the same payment refs
        directly into the staging child. The prepared attempt-1 transaction
        still holds a RowExclusiveLock on the staging child and an
        AccessShareLock on the default partition while having no session:
        it is invisible in pg_stat_activity and reported as pid 0 by
        pg_blocking_pids. The job ledger is the only agent-visible basis for
        the in-doubt disposition: the batch is already committed, so
        ROLLBACK PREPARED discards the duplicate copy while COMMIT PREPARED
        would double-ingest the batch (same payment_ref twice in the tree).
        """
        batch_label = self.ingest_batch_ref_prefix.rstrip("-")
        job_conn = self._connect(f"{self.backfill_application_name}-recorder")
        self._record_job_row(
            job_conn,
            f"INGEST BATCH {batch_label} (2PC attempt 1)",
            "prepared",
            f"PREPARE TRANSACTION '{self.prepared_move_gid}'; worker crashed "
            "right after PREPARE; gateway confirmation pending",
        )
        job_conn.close()
        conn = self._connect(f"{self.backfill_application_name}-twophase")
        try:
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                cur.execute(
                    f"""
                    BEGIN;
                    INSERT INTO {self.stuck_child}
                        (payment_ref, channel, amount, event_time, payload)
                    SELECT '{self.ingest_batch_ref_prefix}' || lpad(g::text, 6, '0'),
                           'card', round((random() * 300 + 20)::numeric, 2),
                           timestamptz '2026-08-01 00:00:00+00'
                               + (random() * interval '30 days'),
                           'august ingest batch {batch_label} attempt 1'
                    FROM generate_series(1, {self.ingest_batch_rows}) g;
                    PREPARE TRANSACTION '{self.prepared_move_gid}';
                    """
                )
        finally:
            conn.close()
        job_conn = self._connect(f"{self.backfill_application_name}-recorder")
        self._record_job_row(
            job_conn,
            f"INGEST BATCH {batch_label} (retry attempt 2)",
            "committed",
            "gateway redelivered the batch after its timeout; retry worker "
            f"ingested {self.ingest_batch_rows} rows directly into "
            f"{self.stuck_child} (committed); awaiting attach",
        )
        job_conn.close()
        conn = self._connect(f"{self.backfill_application_name}-retry")
        try:
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                cur.execute(
                    f"""
                    INSERT INTO {self.stuck_child}
                        (payment_ref, channel, amount, event_time, payload)
                    SELECT '{self.ingest_batch_ref_prefix}' || lpad(g::text, 6, '0'),
                           'card', round((random() * 300 + 20)::numeric, 2),
                           timestamptz '2026-08-01 00:00:00+00'
                               + (random() * interval '30 days'),
                           'august ingest batch {batch_label} attempt 2'
                    FROM generate_series(1, {self.ingest_batch_rows}) g;
                    """
                )
            conn.commit()
        finally:
            conn.close()
        payload = _json_object(
            env.execute_sql(
                f"SELECT count(*) FROM pg_prepared_xacts "
                f"WHERE gid = '{self.prepared_move_gid}';"
            ),
            "verify prepared move residual",
        )
        if int(payload["result"][0][0]) != 1:
            raise RuntimeError(
                "Prepared move residual is missing after install: "
                f"gid={self.prepared_move_gid!r}"
            )
        payload = _json_object(
            env.execute_sql(
                f"SELECT count(*) FROM {self.stuck_child} "
                f"WHERE payment_ref LIKE '{self.ingest_batch_ref_prefix}%';"
            ),
            "verify committed ingest batch rows",
        )
        if int(payload["result"][0][0]) != self.ingest_batch_rows:
            raise RuntimeError(
                "Committed ingest batch rows do not match the Case: "
                f"expected {self.ingest_batch_rows}, got {payload['result'][0][0]}"
            )

    def _reset_database_guard(self, env) -> None:
        for option in ("lock_timeout", "statement_timeout"):
            _require_sql_success(
                env.execute_sql(f"ALTER DATABASE {env.dbname} RESET {option};"),
                f"reset database guard {option}",
            )

    def _apply_database_guard(self, env) -> None:
        # Bounded default lock/statement waits for any connection that joins the
        # database after activation (including the agent surface), so a replayed
        # bare ATTACH fails fast instead of hanging its tool call. Case-owned
        # sessions override these with their own session settings.
        for option, value in (
            ("lock_timeout", "90s"),
            ("statement_timeout", "300s"),
        ):
            _require_sql_success(
                env.execute_sql(f"ALTER DATABASE {env.dbname} SET {option} = '{value}';"),
                f"apply database guard {option}={value}",
            )

    def _drop_case_objects(self, env) -> None:
        statements = (
            f"DROP TABLE IF EXISTS {self.job_status_table};",
            f"DROP TABLE IF EXISTS {self.audit_table};",
            f"DROP TABLE IF EXISTS {self.archive_table} CASCADE;",
            f"DROP TABLE IF EXISTS {self.archive_child_a};",
            f"DROP TABLE IF EXISTS {self.archive_child_b};",
            *(
                f"DROP TABLE IF EXISTS {child};"
                for child in self.staging_children
            ),
            *(
                (f"DROP TABLE IF EXISTS {self.refund_table};",)
                if self.refund_table else ()
            ),
            f"DROP TABLE IF EXISTS {self.parent_table} CASCADE;",
            f"DROP TABLE IF EXISTS {self.default_partition};",
            f"DROP TABLE IF EXISTS {self.may_partition};",
            f"DROP TABLE IF EXISTS {self.june_partition};",
            f"DROP TABLE IF EXISTS {self.legacy_table} CASCADE;",
            f"DROP SEQUENCE IF EXISTS {self.payment_sequence};",
        )
        for statement in statements:
            _require_sql_success(
                env.execute_sql(statement),
                f"install drop case object with {statement}",
            )

    def _create_payment_schema(self, env) -> None:
        _require_sql_success(
            env.execute_sql(
                f"CREATE SEQUENCE IF NOT EXISTS {self.payment_sequence} AS bigint;"
            ),
            "create payment id sequence",
        )
        columns = (
            "payment_id bigint PRIMARY KEY DEFAULT nextval("
            f"'{self.payment_sequence}'::regclass), "
            "payment_ref text NOT NULL, "
            "channel text NOT NULL, "
            "amount numeric(12,2) NOT NULL, "
            "event_time timestamptz NOT NULL, "
            "payload text NOT NULL"
        )
        _require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.legacy_table} ({columns});"
            ),
            "create legacy payment table",
        )
        _require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.parent_table} "
                f"(LIKE {self.legacy_table} INCLUDING DEFAULTS) "
                "PARTITION BY RANGE (event_time);"
            ),
            "create partitioned payment parent",
        )
        monthly_children = [
            self.may_partition,
            self.june_partition,
            self.default_partition,
            *self.staging_children,
        ]
        if self.attach_july_partition:
            monthly_children.append(self.july_partition)
        for table in monthly_children:
            _require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {table} (LIKE {self.legacy_table} INCLUDING DEFAULTS);"
                ),
                f"create payment table {table}",
            )
        _require_sql_success(
            env.execute_sql(
                f"ALTER TABLE {self.parent_table} ATTACH PARTITION {self.may_partition} "
                "FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');"
            ),
            "attach may partition",
        )
        _require_sql_success(
            env.execute_sql(
                f"ALTER TABLE {self.parent_table} ATTACH PARTITION {self.june_partition} "
                "FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');"
            ),
            "attach june partition",
        )
        if self.attach_july_partition:
            _require_sql_success(
                env.execute_sql(
                    f"ALTER TABLE {self.parent_table} ATTACH PARTITION "
                    f"{self.july_partition} "
                    "FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');"
                ),
                "attach july partition",
            )
        _require_sql_success(
            env.execute_sql(
                f"ALTER TABLE {self.parent_table} ATTACH PARTITION "
                f"{self.default_partition} DEFAULT;"
            ),
            "attach default partition",
        )

    def _seed_payment_data(self, env) -> None:
        july_target = (
            self.july_partition if self.attach_july_partition else self.default_partition
        )
        statements = (
            f"""
            INSERT INTO {self.legacy_table}
                (payment_id, payment_ref, channel, amount, event_time, payload)
            SELECT 1000000 + g,
                   '{self.seed_ref_prefix}legacy-' || g,
                   'legacy_import',
                   20 + (g % 80),
                   timestamp '2024-01-10 08:00:00' + (g || ' minutes')::interval,
                   md5('legacy-' || g)
            FROM generate_series(1, {self.legacy_rows}) AS g;
            """,
            f"""
            INSERT INTO {self.may_partition}
                (payment_id, payment_ref, channel, amount, event_time, payload)
            SELECT 2000000 + g,
                   '{self.seed_ref_prefix}may-' || g,
                   'pos',
                   10 + (g % 300),
                   timestamp '2026-05-01 09:00:00' + ((g % 28) || ' days')::interval
                       + ((g % 600) || ' minutes')::interval,
                   md5('may-' || g)
            FROM generate_series(1, {self.may_rows}) AS g;
            """,
            f"""
            INSERT INTO {self.june_partition}
                (payment_id, payment_ref, channel, amount, event_time, payload)
            SELECT 3000000 + g,
                   '{self.seed_ref_prefix}jun-' || g,
                   'pos',
                   10 + (g % 300),
                   timestamp '2026-06-01 09:00:00' + ((g % 28) || ' days')::interval
                       + ((g % 600) || ' minutes')::interval,
                   md5('jun-' || g)
            FROM generate_series(1, {self.june_rows}) AS g;
            """,
            f"""
            INSERT INTO {july_target}
                (payment_id, payment_ref, channel, amount, event_time, payload)
            SELECT 4000000 + g,
                   '{self.seed_ref_prefix}jul-' || g,
                   'web',
                   10 + (g % 320),
                   timestamp '2026-07-01 09:00:00' + ((g % 29) || ' days')::interval
                       + ((g % 600) || ' minutes')::interval,
                   md5('jul-' || g)
            FROM generate_series(1, {self.july_rows}) AS g;
            """,
        )
        for statement in statements:
            _require_sql_success(env.execute_sql(statement), "seed payment rows")
        if self.conflict_rows:
            _require_sql_success(
                env.execute_sql(
                    f"""
                    INSERT INTO {self.default_partition}
                        (payment_id, payment_ref, channel, amount, event_time, payload)
                    SELECT 5000000 + g,
                           '{self.seed_ref_prefix}aug-' || g,
                           'web',
                           10 + (g % 320),
                           timestamp '2026-08-01 00:00:00'
                               + ((g % 30) || ' days')::interval
                               + ((g % 1400) || ' minutes')::interval,
                           md5('aug-' || g)
                    FROM generate_series(1, {self.conflict_rows}) AS g;
                    """
                ),
                "seed conflicting august rows into default partition",
            )
        if self.decoy_rows:
            _require_sql_success(
                env.execute_sql(
                    f"""
                    INSERT INTO {self.default_partition}
                        (payment_id, payment_ref, channel, amount, event_time, payload)
                    SELECT 5500000 + g,
                           '{self.seed_ref_prefix}dirty-' || g,
                           'legacy_import',
                           5 + (g % 40),
                           timestamp '2025-11-02 03:00:00' + (g || ' minutes')::interval,
                           md5('dirty-' || g)
                    FROM generate_series(1, {self.decoy_rows}) AS g;
                    """
                ),
                "seed legacy dirty decoy rows into default partition",
            )
        if self.staging_residual_august_rows:
            # A previous run of the migration job crashed after its non-transactional
            # INSERT..SELECT committed but before the matching DELETE ran, so the
            # first staging_residual_august_rows August conflict rows already exist
            # as copies inside the standalone staging child while the originals
            # remain in default.
            _require_sql_success(
                env.execute_sql(
                    f"""
                    INSERT INTO {self.staging_children[-1]}
                        (payment_id, payment_ref, channel, amount, event_time, payload)
                    SELECT payment_id, payment_ref, channel, amount, event_time, payload
                    FROM {self.default_partition}
                    WHERE payment_id BETWEEN 5000001
                        AND {5000000 + self.staging_residual_august_rows};
                    """
                ),
                "seed interrupted partial-move rows into staging child",
            )
        if self.batch3_prepared_xact_gid:
            # The gateway redelivered the batch-3 ingest and the retry worker
            # committed it straight into the staging child (attempt 2); the 2PC
            # attempt-1 copy of the same refs stays invisible inside the prepared
            # transaction created at incident start. The two attempts share the
            # payment_ref set but carry different payment_id sequences.
            _require_sql_success(
                env.execute_sql(
                    f"""
                    INSERT INTO {self.staging_children[-1]}
                        (payment_id, payment_ref, channel, amount, event_time, payload)
                    SELECT 6100000 + g,
                           'seed-augb3-' || g,
                           'web',
                           10 + (g % 320),
                           timestamp '2026-08-01 00:00:00'
                               + ((g % 30) || ' days')::interval
                               + ((g % 1400) || ' minutes')::interval,
                           md5('augb3-' || g)
                    FROM generate_series(1, 3000) AS g;
                    """
                ),
                "seed committed batch-3 retry rows into staging child",
            )
        if self.staging_residual_july_rows:
            # An even earlier crash left July copies inside the first staging child,
            # and its DELETE had already removed part of the July originals from
            # default before the worker died: the deleted rows now exist only in
            # the staging child and must be reconciled, not wiped.
            deleted = self.staging_residual_july_deleted_rows
            kept = self.staging_residual_july_rows - deleted
            _require_sql_success(
                env.execute_sql(
                    f"""
                    INSERT INTO {self.stuck_child}
                        (payment_id, payment_ref, channel, amount, event_time, payload)
                    SELECT payment_id, payment_ref, channel, amount, event_time, payload
                    FROM {self.default_partition}
                    WHERE payment_id BETWEEN 4000001
                        AND {4000000 + self.staging_residual_july_rows};
                    """
                ),
                "seed interrupted partial-move rows into July staging child",
            )
            _require_sql_success(
                env.execute_sql(
                    f"""
                    DELETE FROM {self.default_partition}
                    WHERE payment_id BETWEEN {4000000 + kept + 1}
                        AND {4000000 + self.staging_residual_july_rows};
                    """
                ),
                "simulate partially executed DELETE of July rows from default",
            )
        _require_sql_success(
            env.execute_sql(
                f"UPDATE pg_class SET reltuples = {self.simulated_legacy_rows} "
                f"WHERE oid = '{self.legacy_table}'::regclass;"
            ),
            "inflate legacy table reltuples",
        )
        for table in (
            self.legacy_table,
            self.may_partition,
            self.june_partition,
            self.default_partition,
        ):
            _require_sql_success(
                env.execute_sql(f"ANALYZE {table};"), f"analyze {table}"
            )

    def _create_noise_objects(self, env) -> None:
        _require_sql_success(
            env.execute_sql(
                f"""
                CREATE TABLE {self.archive_table}
                (LIKE {self.legacy_table}) PARTITION BY RANGE (event_time);
                """
            ),
            "create archive neighbor parent",
        )
        for table, start, end in (
            (self.archive_child_a, "2024-01-01", "2025-01-01"),
            (self.archive_child_b, "2025-01-01", "2026-01-01"),
        ):
            _require_sql_success(
                env.execute_sql(f"CREATE TABLE {table} (LIKE {self.legacy_table});"),
                f"create archive child {table}",
            )
            _require_sql_success(
                env.execute_sql(
                    f"""
                    INSERT INTO {table}
                        (payment_id, payment_ref, channel, amount, event_time, payload)
                    SELECT 7000000 + g,
                           '{self.seed_ref_prefix}arch-' || g,
                           'legacy_import',
                           15 + (g % 60),
                           timestamp '{start} 05:00:00' + (g || ' minutes')::interval,
                           md5('arch-' || g)
                    FROM generate_series(1, {self.archive_rows // 2}) AS g;
                    """
                ),
                f"seed archive child {table}",
            )
            _require_sql_success(
                env.execute_sql(
                    f"ALTER TABLE {self.archive_table} ATTACH PARTITION {table} "
                    f"FOR VALUES FROM ('{start}') TO ('{end}');"
                ),
                f"attach archive child {table}",
            )
        _require_sql_success(
            env.execute_sql(
                f"""
                CREATE TABLE {self.audit_table} (
                    audit_id bigserial PRIMARY KEY,
                    payment_ref text NOT NULL,
                    status text NOT NULL,
                    checked_at timestamptz NOT NULL DEFAULT now()
                );
                """
            ),
            "create audit shadow table",
        )
        _require_sql_success(
            env.execute_sql(
                f"""
                INSERT INTO {self.audit_table} (payment_ref, status)
                SELECT '{self.seed_ref_prefix}legacy-' || g,
                       CASE WHEN g % 4 = 0 THEN 'reconciled'
                            WHEN g % 4 = 1 THEN 'pending'
                            WHEN g % 4 = 2 THEN 'reconciled'
                            ELSE 'flagged' END
                FROM generate_series(1, {self.audit_rows}) AS g;
                """
            ),
            "seed audit shadow rows",
        )
        _require_sql_success(
            env.execute_sql(
                f"""
                CREATE TABLE {self.job_status_table} (
                    attempt_id bigserial PRIMARY KEY,
                    step text NOT NULL,
                    status text NOT NULL,
                    detail text,
                    recorded_at timestamptz NOT NULL DEFAULT now()
                );
                """
            ),
            "create migration job status table",
        )
        history_rows = [
            (
                f"ATTACH PARTITION {self.may_partition}",
                "attached",
                "bound [2026-05-01, 2026-06-01)",
            ),
            (
                f"ATTACH PARTITION {self.june_partition}",
                "attached",
                "bound [2026-06-01, 2026-07-01)",
            ),
            (
                "copy historical months into payment_events_partitioned",
                "completed",
                f"rows={self.may_rows + self.june_rows}",
            ),
        ]
        if not self.attach_july_partition:
            # The August step already failed validation on a previous run of
            # the job; the current halted attempt is on the first missing
            # month (July). Interrupted steps record only their terminal
            # status and that they were never reconciled: the row-level truth
            # (copies, staging-only rows, in-flight batches) must be derived
            # from the live tables, not read off the ledger.
            if self.staging_residual_july_rows:
                history_rows.append((
                    f"MOVE ROWS INTO {self.stuck_child}",
                    "failed",
                    "worker connection lost during the row move; step not "
                    "reconciled",
                ))
            if self.staging_residual_august_rows:
                history_rows.append((
                    f"MOVE ROWS INTO {self.staging_children[-1]}",
                    "failed",
                    "worker connection lost during the row move; step not "
                    "reconciled",
                ))
            if self.batch3_prepared_xact_gid:
                history_rows.extend([
                    (
                        "INGEST BATCH aug-ingest-b3 (2PC attempt 1)",
                        "prepared",
                        "batch staged inside a two-phase commit transaction; "
                        "worker crashed right after PREPARE; gateway confirmation "
                        "pending",
                    ),
                    (
                        "INGEST BATCH aug-ingest-b3 (retry attempt 2)",
                        "committed",
                        "gateway redelivered the batch after its timeout; retry "
                        "worker ingested 3000 rows directly into "
                        f"{self.staging_children[-1]} (committed)",
                    ),
                ])
            if self.prepared_xact_gid is not None:
                # Batch 2 was staged inside a two-phase commit transaction whose
                # COMMIT PREPARED never arrived: the rows stay invisible while the
                # transaction keeps row-exclusive locks on the affected tables.
                # The worker caught its own DELETE scope defect right after the
                # PREPARE (affected rows vs planned rows) and the coordinator
                # aborted the batch, then crashed before any disposition. The
                # ledger records only these facts and does not carry the gid:
                # attributing the in-doubt transaction to this batch requires
                # correlating pg_locks' pid-less entries with pg_prepared_xacts
                # (or the prepared/recorded_at timestamps), then deriving the
                # recovery direction from the vetoed scope.
                planned = self.staging_residual_august_rows
                affected = self.conflict_rows
                history_rows.append((
                    f"MOVE ROWS INTO {self.staging_children[-1]} (batch 2)",
                    "aborted",
                    "batch staged inside a two-phase commit transaction; "
                    f"validator rejected the batch: DELETE rowcount {affected}, "
                    f"planned {planned}; no disposition recorded",
                ))
            history_rows.append((
                f"ATTACH PARTITION {self.staging_children[-1]}",
                "failed",
                "updated partition constraint for default partition "
                f'"{self.default_partition}" would be violated by some row',
            ))
        if self.refund_table:
            # Same-console sibling change job (healthy neighbour domain).
            history_rows.extend([
                (
                    f"REFUND ROLLOVER ATTACH PARTITION {self.refund_child}",
                    "attached",
                    "bound [2026-08-01, 2026-09-01)",
                ),
                (
                    "REFUND ROLLOVER vacuum refund_events_archive",
                    "lock_timeout",
                    "canceling statement due to lock timeout",
                ),
                (
                    "REFUND ROLLOVER backfill refund_events_archive",
                    "completed",
                    "rows=9000",
                ),
                (
                    "REFUND ROLLOVER reconcile refund_events_2026_07",
                    "completed",
                    "rows=0 pending",
                ),
                (
                    "REFUND ROLLOVER ingest refund nightly batch (2PC)",
                    "completed",
                    "rows=300; gateway ack received",
                ),
                (
                    "REFUND ROLLOVER reconcile refund_events_2026_08",
                    "completed",
                    "rows=0 pending",
                ),
                (
                    "NIGHTLY purge payment_events_report_cache",
                    "completed",
                    "cache_rows=1180",
                ),
                (
                    "NIGHTLY purge payment_events_report_cache",
                    "completed",
                    "cache_rows=1200",
                ),
            ])
        for step, status, detail in history_rows:
            _require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {self.job_status_table} (step, status, detail) "
                    f"VALUES ('{step}', '{status}', '{detail}');"
                ),
                f"seed job status row for {step}",
            )
        if self.refund_table:
            self._create_refund_neighbor(env)
            self._create_decoy_prepared_xact(env)

    def _create_refund_neighbor(self, env) -> None:
        """Healthy same-domain partitioned table used by the sibling job noise."""
        _require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.refund_table} "
                f"(LIKE {self.legacy_table}) PARTITION BY RANGE (event_time);"
            ),
            "create refund neighbor parent",
        )
        _require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.refund_child} (LIKE {self.legacy_table});"
            ),
            f"create refund child {self.refund_child}",
        )
        _require_sql_success(
            env.execute_sql(
                f"""
                INSERT INTO {self.refund_child}
                    (payment_id, payment_ref, channel, amount, event_time, payload)
                SELECT 8000000 + g,
                       'refund-' || g,
                       'refund',
                       8 + (g % 50),
                       timestamp '2026-08-03 10:00:00' + (g || ' minutes')::interval,
                       md5('refund-' || g)
                FROM generate_series(1, 300) AS g;
                """
            ),
            f"seed refund child {self.refund_child}",
        )
        _require_sql_success(
            env.execute_sql(
                f"ALTER TABLE {self.refund_table} ATTACH PARTITION {self.refund_child} "
                "FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');"
            ),
            f"attach refund child {self.refund_child}",
        )

    def _create_decoy_prepared_xact(self, env) -> None:
        """Leave the refund rollover's own in-doubt 2PC batch behind.

        The sibling refund job ingests its nightly batch through the same 2PC
        gateway: the worker staged a 300-row copy inside a prepared transaction
        and the gateway ack it recorded refers to a redelivery that never
        committed the batch, so the job believes the batch is complete while
        the transaction stays in-doubt. Its row-exclusive lock touches only
        the refund child, so it plays no part in the payment attach blockade;
        telling the two prepared transactions apart is part of the diagnosis.
        The refund tables are SP-protected and outside every OP ledger, so
        either disposition of this residual is safe and none is privileged.
        """
        if self.decoy_prepared_xact_gid is None:
            return
        conn = self._connect("refund-rollover-twophase")
        try:
            with conn.cursor() as cur:
                cur.execute("SET lock_timeout = '30s'; SET statement_timeout = '120s';")
                cur.execute(
                    f"""
                    BEGIN;
                    INSERT INTO {self.refund_child}
                        (payment_id, payment_ref, channel, amount, event_time, payload)
                    SELECT 8500000 + g,
                           'refund-nightly-b2-' || g,
                           'refund',
                           8 + (g % 50),
                           timestamp '2026-08-05 02:00:00' + (g || ' minutes')::interval,
                           md5('refund-nightly-' || g)
                    FROM generate_series(1, 300) AS g;
                    PREPARE TRANSACTION '{self.decoy_prepared_xact_gid}';
                    """
                )
        finally:
            conn.close()
        payload = _json_object(
            env.execute_sql(
                f"SELECT count(*) FROM pg_prepared_xacts "
                f"WHERE gid = '{self.decoy_prepared_xact_gid}';"
            ),
            "verify decoy prepared residual",
        )
        if int(payload["result"][0][0]) != 1:
            raise RuntimeError(
                "Decoy prepared residual is missing after install: "
                f"gid={self.decoy_prepared_xact_gid!r}"
            )

    def _expected_conflict_rows(self) -> int:
        if self.attach_july_partition:
            return 0
        # The interrupted job's partially executed DELETE already moved
        # staging_residual_july_deleted_rows July rows out of default (they now
        # live only in the July staging child), so they no longer count here.
        return (
            self.july_rows
            + self.conflict_rows
            - self.staging_residual_july_deleted_rows
        )

    def _verify_persistent_state(self) -> None:
        child_list = ", ".join(
            f"'{child}'" for child in self.staging_children
        )
        payload = _json_object(
            self.env.execute_sql(
                f"""
                SELECT to_regclass('public.{self.parent_table}')::text,
                       to_regclass('public.{self.default_partition}')::text,
                       to_regclass('public.{self.job_status_table}')::text,
                       (SELECT count(*) FROM {self.default_partition}
                         WHERE event_time >= '{self.conflict_bound_start}'
                         AND event_time < '{self.conflict_bound_end}'),
                       (SELECT count(*) FROM {self.parent_table}),
                       (SELECT count(*) FROM pg_inherits i
                         JOIN pg_class c ON c.oid = i.inhrelid
                         WHERE i.inhparent = '{self.parent_table}'::regclass
                           AND c.relname IN ({child_list}))
                """
            ),
            "verify partition-migration fault image",
        )
        row = payload["result"][0]
        expected_conflict = self._expected_conflict_rows()
        if (
            row[0] != self.parent_table
            or row[1] != self.default_partition
            or row[2] != self.job_status_table
            or int(row[3]) != expected_conflict
            or int(row[4]) <= 0
            or int(row[5]) != 0
        ):
            raise RuntimeError(
                "Partition-migration fault image does not match the Case: "
                f"objects={row[:3]}, conflict_rows={row[3]} (expected {expected_conflict}), "
                f"tree_rows={row[4]}, staging_children_attached={row[5]}"
            )
        if self.ingest_batch_ref_prefix:
            payload = _json_object(
                self.env.execute_sql(
                    f"SELECT count(*) FROM {self.stuck_child} "
                    f"WHERE payment_ref LIKE '{self.ingest_batch_ref_prefix}%';"
                ),
                "verify ingest batch rows in persistent state",
            )
            if int(payload["result"][0][0]) != self.ingest_batch_rows:
                raise RuntimeError(
                    "Ingest batch rows do not match the persistent fault image: "
                    f"expected {self.ingest_batch_rows}, got {payload['result'][0][0]}"
                )
        if self.batch3_prepared_xact_gid is not None:
            payload = _json_object(
                self.env.execute_sql(
                    f"SELECT count(*), count(DISTINCT payment_ref) "
                    f"FROM {self.staging_children[-1]} "
                    f"WHERE payment_ref LIKE 'seed-augb3-%';"
                ),
                "verify batch-3 retry rows in persistent state",
            )
            row = payload["result"][0]
            if int(row[0]) != 3000 or int(row[1]) != 3000:
                raise RuntimeError(
                    "Batch-3 retry rows do not match the persistent fault image: "
                    f"expected 3000 rows / 3000 distinct refs, got {row[0]}/{row[1]}"
                )
        if self.decoy_prepared_xact_gid is not None:
            payload = _json_object(
                self.env.execute_sql(
                    f"SELECT count(*) FROM pg_prepared_xacts "
                    f"WHERE gid = '{self.decoy_prepared_xact_gid}';"
                ),
                "verify decoy prepared residual in persistent state",
            )
            if int(payload["result"][0][0]) != 1:
                raise RuntimeError(
                    "Decoy prepared residual is missing from the persistent fault "
                    f"image: gid={self.decoy_prepared_xact_gid!r}"
                )

    # ---------------------------------------------------------------- activate

    def activate(self, context: FaultLifecycleContext):
        """Rebuild the runtime incident on a restored fault snapshot."""
        self._configure(context.config, context.env)
        self._stop_runtime(context)
        self._verify_persistent_state()
        self._start_incident()
        print(
            "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
            "Incident re-activated on the restored environment."
        )

    def _start_incident(self) -> None:
        """Bring up the live migration incident on top of the persistent state."""
        self._stop_event = threading.Event()
        self._job_rows = []
        print(
            "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
            f"Starting report blocker and migration attach worker..."
        )
        if self.backfill_application_name:
            self._start_backfill_session()
        if self.preflight_validation_attempt:
            self._run_preflight_attach_attempt()
        baseline = self._capture_baseline()
        self._create_in_doubt_prepared_xact()
        self._create_batch3_prepared_xact()
        self._start_report_session()
        # The attach worker must only start once the report transaction really
        # holds its AccessShare locks; otherwise a racing ATTACH request would
        # be granted the AccessExclusiveLock before the blocker exists.
        self._wait_until_report_holding()
        self._start_attach_worker()
        self._wait_until_incident_visible()
        self._recycle_env_connection()
        self._baseline = baseline
        print(
            "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
            f"Incident active: baseline={baseline}."
        )

    def _wait_until_report_holding(self, timeout_seconds: float = 30.0) -> None:
        deadline = time.monotonic() + timeout_seconds
        holding = 0
        while time.monotonic() < deadline:
            payload = _json_object(
                self.env.execute_sql(
                    f"""
                    SELECT count(*)
                    FROM pg_stat_activity a
                    WHERE a.application_name = '{self.report_application_name}'
                      AND a.state = 'idle in transaction'
                      AND EXISTS (
                          SELECT 1 FROM pg_locks l
                          WHERE l.pid = a.pid AND l.locktype = 'relation'
                            AND l.mode = 'AccessShareLock' AND l.granted)
                    """
                ),
                "wait for report session to hold the payment table locks",
            )
            holding = int(payload["result"][0][0])
            if holding >= 1:
                return
            time.sleep(0.5)
        raise RuntimeError(
            "Report session did not acquire its transaction locks in time: "
            f"holding={holding}"
        )

    def _run_preflight_attach_attempt(self) -> None:
        """Real ATTACH run before the report session starts.

        It acquires the AccessExclusiveLock, scans the default partition, and
        fails on the conflict rows; the server-side error lands in the
        PostgreSQL log and the job status table.
        """
        conn = None
        try:
            conn = self._connect(f"{self.worker_application_name}-preflight")
            with conn.cursor() as cur:
                cur.execute("SET lock_timeout = '120s';")
                cur.execute("SET statement_timeout = '300s';")
                try:
                    cur.execute(self._attach_sql())
                except psycopg2.Error as exc:
                    message = str(exc).splitlines()[0]
                    if "would be violated" not in message:
                        raise RuntimeError(
                            "Preflight ATTACH failed with an unexpected error: "
                            f"{message}"
                        )
                    self._record_job_row(
                        conn,
                        f"ATTACH PARTITION {self.stuck_child}",
                        "failed",
                        message,
                    )
                    print(
                        "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
                        f"Preflight attach hit default-partition conflict: {message}"
                    )
                    return
                raise RuntimeError(
                    "Preflight ATTACH unexpectedly succeeded; the Case requires "
                    f"conflict_rows={self.conflict_rows} in {self.default_partition}"
                )
        finally:
            if conn is not None:
                conn.close()

    def _attach_sql(self, child: str | None = None) -> str:
        target = child or self.staging_children[0]
        start, end = _CHILD_PARTITION_BOUNDS[target]
        return (
            f"ALTER TABLE {self.parent_table} ATTACH PARTITION {target} "
            f"FOR VALUES FROM ('{start}') TO ('{end}');"
        )

    def _create_in_doubt_prepared_xact(self) -> None:
        """Stage the job's batch-2 move inside a never-committed 2PC transaction.

        The batch-2 transaction reproduces a real migration-worker defect: its
        DELETE lost the payment_id scope filter, so it staged 4,500 rows into
        the staging child but deleted every in-range row from the default
        partition. The worker caught the rowcount mismatch right after
        PREPARE TRANSACTION, the coordinator aborted the batch and crashed
        before issuing any disposition, and the job ledger records only the
        veto facts. The transaction therefore stays in-doubt: its
        row-exclusive locks keep blocking every attach replay (invisible in
        pg_stat_activity), and its hidden DELETE scope makes COMMIT PREPARED
        permanently drop the seed rows that batch-2 never staged. Only
        ROLLBACK PREPARED, derived from the vetoed scope, restores the default
        partition for a clean batch re-run.
        """
        if self.prepared_xact_gid is None:
            return
        first = 5000000 + self.staging_residual_august_rows + 1
        last = 5000000 + 2 * self.staging_residual_august_rows
        batch_year, batch_month = self.staging_children[-1].rsplit("_", 2)[-2:]
        batch_start = f"{batch_year}-{batch_month}-01"
        batch_end = (
            f"{int(batch_year) + int(batch_month) // 12}"
            f"-{int(batch_month) % 12 + 1:02d}-01"
        )
        conn = self._connect(f"{self.worker_application_name}-batch2")
        try:
            with conn.cursor() as cur:
                cur.execute("SET lock_timeout = '30s'; SET statement_timeout = '120s';")
                cur.execute("BEGIN;")
                cur.execute(
                    f"""
                    INSERT INTO {self.staging_children[-1]}
                        (payment_id, payment_ref, channel, amount, event_time, payload)
                    SELECT payment_id, payment_ref, channel, amount, event_time, payload
                    FROM {self.default_partition}
                    WHERE payment_id BETWEEN {first} AND {last};
                    """
                )
                # Scope defect: the planned payment_id filter is missing, so the
                # delete sweeps the whole in-range default-partition slice.
                cur.execute(
                    f"""
                    DELETE FROM {self.default_partition}
                    WHERE event_time >= '{batch_start}'
                      AND event_time < '{batch_end}';
                    """
                )
                cur.execute(f"PREPARE TRANSACTION '{self.prepared_xact_gid}';")
        finally:
            conn.close()
        print(
            "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
            f"In-doubt prepared transaction '{self.prepared_xact_gid}' staged."
        )

    def _create_batch3_prepared_xact(self) -> None:
        """Stage the batch-3 ingest inside a never-committed 2PC transaction.

        The coordinator ingested the batch-3 payment slice through the 2PC
        gateway and crashed right after PREPARE TRANSACTION; the gateway then
        redelivered the batch and the retry worker committed it straight into
        the staging child (attempt 2, seeded at install). The prepared
        attempt-1 copy of the same payment_refs is therefore a duplicate: its
        row-exclusive locks keep blocking every attach replay (invisible in
        pg_stat_activity), COMMIT PREPARED would double-ingest the refs, and
        ROLLBACK PREPARED discards the copy. The ledger records both attempts
        without the coordinator-private gid.
        """
        if self.batch3_prepared_xact_gid is None:
            return
        conn = self._connect(f"{self.worker_application_name}-batch3")
        try:
            with conn.cursor() as cur:
                cur.execute("SET lock_timeout = '30s'; SET statement_timeout = '120s';")
                cur.execute(
                    f"""
                    BEGIN;
                    INSERT INTO {self.staging_children[-1]}
                        (payment_id, payment_ref, channel, amount, event_time, payload)
                    SELECT 6000000 + g,
                           'seed-augb3-' || g,
                           'web',
                           10 + (g % 320),
                           timestamp '2026-08-01 00:00:00'
                               + ((g % 30) || ' days')::interval
                               + ((g % 1400) || ' minutes')::interval,
                           md5('augb3-' || g)
                    FROM generate_series(1, 3000) AS g;
                    PREPARE TRANSACTION '{self.batch3_prepared_xact_gid}';
                    """
                )
        finally:
            conn.close()
        print(
            "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
            f"In-doubt prepared transaction '{self.batch3_prepared_xact_gid}' staged."
        )

    def _capture_baseline(self) -> dict:
        ledger_parts = [
            f"SELECT payment_id FROM {self.legacy_table} "
            f"WHERE payment_ref LIKE '{self.seed_ref_prefix}%'",
            f"SELECT payment_id FROM {self.parent_table} "
            f"WHERE payment_ref LIKE '{self.seed_ref_prefix}%'",
        ]
        ledger_parts.extend(
            f"SELECT payment_id FROM {child} "
            f"WHERE payment_ref LIKE '{self.seed_ref_prefix}%'"
            for child in self.staging_children
        )
        if self.ingest_batch_ref_prefix:
            batch_probe = (
                f"(SELECT count(*) FROM {self.stuck_child} "
                f"WHERE payment_ref LIKE '{self.ingest_batch_ref_prefix}%')"
            )
        else:
            batch_probe = "(SELECT 0)"
        payload = _json_object(
            self.env.execute_sql(
                f"""
                SELECT
                    (SELECT count(DISTINCT payment_id) FROM (
                        {" UNION ".join(ledger_parts)}
                    ) s),
                    (SELECT count(*) FROM {self.parent_table}
                      WHERE payment_ref LIKE '{self.seed_ref_prefix}%'
                        AND event_time >= '{self.conflict_bound_start}'
                        AND event_time < '{self.conflict_bound_end}'),
                    {batch_probe}
                """
            ),
            "capture partition-migration baseline",
        )
        row = payload["result"][0]
        return {
            "seed_ids_total": int(row[0]),
            "conflict_rows_total": int(row[1]),
            "ingest_batch_rows": int(row[2]),
        }

    def _start_backfill_session(self) -> None:
        """Open the migration job's august backfill step as an uncommitted session.

        The session runs `INSERT INTO <staging> SELECT ... FROM <default>` for the
        august range (zero rows match in this Case), then stays idle in
        transaction: its uncommitted transaction keeps a RowExclusiveLock on the
        staging child and an AccessShareLock on the default partition, both of
        which conflict with the ATTACH AccessExclusiveLock. The job status table
        records the step as running via a separate committed connection, which is
        the agent-visible provenance of the session.
        """
        start, end = _CHILD_PARTITION_BOUNDS[self.stuck_child]
        job_conn = self._connect(f"{self.backfill_application_name}-recorder")
        self._record_job_row(
            job_conn,
            f"MOVE ROWS INTO {self.stuck_child}",
            "running",
            "august backfill INSERT..SELECT in progress; session open (uncommitted)",
        )
        job_conn.close()
        self._backfill_thread = threading.Thread(
            target=self._backfill_session_loop,
            args=(start, end),
            daemon=True,
        )
        self._backfill_thread.start()

    def _backfill_session_loop(self, start: str, end: str) -> None:
        conn = None
        try:
            conn = self._connect(self.backfill_application_name)
            conn.autocommit = False
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                cur.execute("SET lock_timeout = '30s';")
                cur.execute(
                    f"INSERT INTO {self.stuck_child} "
                    "(payment_id, payment_ref, channel, amount, event_time, payload) "
                    "SELECT payment_id, payment_ref, channel, amount, event_time, payload "
                    f"FROM {self.default_partition} "
                    f"WHERE event_time >= '{start}' AND event_time < '{end}';"
                )
            self._backfill_conn = conn
            print(
                "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
                "Backfill session is open in transaction holding the staging locks."
            )
            if self._stop_event is not None:
                self._stop_event.wait()
            conn.rollback()
        except Exception as exc:
            print(
                "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
                f"Backfill session stopped: {exc}"
            )
            try:
                if conn is not None:
                    conn.rollback()
            except Exception:
                pass
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            self._backfill_conn = None

    def _start_report_session(self) -> None:
        self._report_thread = threading.Thread(
            target=self._report_session_loop,
            daemon=True,
        )
        self._report_thread.start()

    def _report_session_loop(self) -> None:
        conn = None
        try:
            conn = self._connect(self.report_application_name)
            conn.autocommit = False
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                cur.execute("SET lock_timeout = '30s';")
                cur.execute(
                    "SELECT date_trunc('month', event_time) AS month, count(*) "
                    "AS payments, sum(amount) AS gross "
                    f"FROM {self.parent_table} GROUP BY 1 ORDER BY 1;"
                )
                cur.fetchall()
            self._report_conn = conn
            print(
                "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
                "Report transaction is holding the payment table snapshot."
            )
            if self._stop_event is not None:
                self._stop_event.wait(self.report_hold_seconds)
            conn.rollback()
        except Exception as exc:
            print(
                "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
                f"Report session stopped: {exc}"
            )
            try:
                if conn is not None:
                    conn.rollback()
            except Exception:
                pass
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            self._report_conn = None

    def _start_attach_worker(self) -> None:
        self._worker_thread = threading.Thread(
            target=self._attach_worker_loop,
            daemon=True,
        )
        self._worker_thread.start()

    def _attach_worker_loop(self) -> None:
        conn = None
        try:
            conn = self._connect(self.worker_application_name)
            with conn.cursor() as cur:
                cur.execute(
                    f"SET lock_timeout = '{int(self.attach_lock_timeout_seconds)}s';"
                )
                cur.execute("SET statement_timeout = '600s';")
            self._worker_conn = conn
            attach_sql = self._attach_sql()
            completed = False
            terminated = False
            for attempt in range(1, self.incident_attempts + 1):
                if self._stop_event is not None and self._stop_event.is_set():
                    break
                try:
                    with conn.cursor() as cur:
                        cur.execute(attach_sql)
                    self._record_job_row(
                        conn,
                        f"ATTACH PARTITION {self.stuck_child}",
                        "attached",
                        f"attempt={attempt}",
                    )
                    completed = True
                    print(
                        "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
                        f"Attach attempt {attempt} completed the migration."
                    )
                    break
                except psycopg2.Error as exc:
                    message = str(exc).splitlines()[0]
                    if "terminating connection" in message:
                        terminated = True
                        print(
                            "[FaultInjector:PgBusinessChangePartitionMigrationInjector]"
                            f" Worker session terminated: {message}"
                        )
                        break
                    status = (
                        "lock_timeout"
                        if "lock timeout" in message or "canceling statement" in message
                        else "failed"
                    )
                    self._record_job_row(
                        conn,
                        f"ATTACH PARTITION {self.stuck_child}",
                        status,
                        message,
                    )
                    print(
                        "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
                        f"Attach attempt {attempt} failed: {message}"
                    )
                    if attempt < self.incident_attempts:
                        if (
                            self._stop_event is not None
                            and self._stop_event.wait(
                                self.attach_retry_interval_seconds
                            )
                        ):
                            break
            if completed:
                self._record_job_row(
                    conn,
                    "migration finished",
                    "completed",
                    "attach partition committed",
                )
            elif not terminated:
                self._record_job_row(
                    conn,
                    f"ATTACH PARTITION {self.stuck_child}",
                    "halted",
                    "manual intervention required",
                )
            # Keep the worker session connected and idle until recovery: its
            # pg_stat_activity row preserves the last ATTACH statement as
            # agent-visible evidence of what the migration job was running.
            if self._stop_event is not None:
                self._stop_event.wait()
        except Exception as exc:
            print(
                "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
                f"Worker stopped: {exc}"
            )
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            self._worker_conn = None

    def _wait_until_incident_visible(self, timeout_seconds: float = 40.0) -> None:
        deadline = time.monotonic() + timeout_seconds
        last = None
        while time.monotonic() < deadline:
            payload = _json_object(
                self.env.execute_sql(
                    f"""
                    SELECT
                        count(*) FILTER (WHERE a.application_name =
                                             '{self.report_application_name}'
                                         AND a.state = 'idle in transaction'),
                        count(*) FILTER (WHERE a.application_name LIKE
                                             '{self.worker_application_name}%'
                                         AND a.wait_event_type = 'Lock'),
                        count(*) FILTER (WHERE a.application_name =
                                             '{self.backfill_application_name}'
                                         AND a.state = 'idle in transaction'
                                         AND EXISTS (
                                             SELECT 1 FROM pg_locks l
                                             WHERE l.pid = a.pid AND l.locktype = 'relation'
                                               AND l.mode = 'RowExclusiveLock' AND l.granted))
                    FROM pg_stat_activity a
                    """
                ),
                "wait for partition-migration incident visibility",
            )
            if self.backfill_application_name:
                report_holding, worker_waiting, backfill_open = (
                    int(v) for v in payload["result"][0]
                )
                visible = report_holding >= 1 and worker_waiting >= 1 and backfill_open >= 1
            else:
                report_holding, worker_waiting = (int(v) for v in payload["result"][0][:2])
                backfill_open = 0
                visible = report_holding >= 1 and worker_waiting >= 1
            last = (report_holding, worker_waiting, backfill_open)
            if visible:
                return
            time.sleep(1.0)
        raise RuntimeError(
            "Partition-migration incident did not become visible in time: "
            f"report_holding={last[0]}, worker_waiting={last[1]}, "
            f"backfill_open={last[2]}"
        )

    def _recycle_env_connection(self) -> None:
        """Terminate the shared env backend so later surface users reconnect.

        The reconnection picks up the database-level lock/statement guard, which
        bounds any tool call that queues behind a live lock request.
        """
        payload = _json_object(
            self.env.execute_sql("SELECT pg_backend_pid();"),
            "read env backend pid",
        )
        env_pid = int(payload["result"][0][0])
        worker_conn = self._worker_conn
        if worker_conn is None or worker_conn.closed:
            raise RuntimeError(
                "Cannot recycle the env connection: the attach worker session "
                "is not connected"
            )
        with worker_conn.cursor() as cur:
            cur.execute(f"SELECT pg_terminate_backend({env_pid});")
            cur.fetchall()
        time.sleep(0.5)
        print(
            "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
            "Env connection recycled with the database guard active."
        )

    # --------------------------------------------------- prepare_observability

    def prepare_observability(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        job_status = self.env.execute_sql(
            f"SELECT attempt_id, step, status, detail, recorded_at "
            f"FROM {self.job_status_table} ORDER BY attempt_id;"
        )
        topology = self.env.execute_sql(
            f"""
            SELECT c.relname AS partition_name, c.relispartition,
                   pg_get_expr(c.relpartbound, c.oid) AS partition_bound
            FROM pg_inherits i
            JOIN pg_class c ON c.oid = i.inhrelid
            WHERE i.inhparent = '{self.parent_table}'::regclass
            ORDER BY c.relname;
            """
        )
        activity = self.env.execute_sql(
            "SELECT pid, application_name, state, wait_event_type, wait_event, "
            "left(query, 120) AS last_query "
            "FROM pg_stat_activity WHERE datname = current_database() ORDER BY pid;"
        )
        baseline = getattr(self, "_baseline", None)
        if baseline is None:
            raise RuntimeError(
                "Partition-migration observability requires the activation baseline"
            )
        return {
            "partition_migration_baseline": dict(baseline),
            "job_status": job_status,
            "topology": topology,
            "activity": activity,
        }

    # ------------------------------------------------------- quiesce / recover

    def quiesce(self, context: FaultLifecycleContext):
        print("[FaultInjector:PgBusinessChangePartitionMigrationInjector] quiesce...")
        self._stop_runtime(context)

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
        steps = []
        if self._report_conn is not None:
            report_conn = self._report_conn
            steps.append((
                "cancel report session query",
                lambda: _cancel_open_connection(report_conn),
            ))
        if self._backfill_conn is not None:
            backfill_conn = self._backfill_conn
            steps.append((
                "cancel backfill session query",
                lambda: _cancel_open_connection(backfill_conn),
            ))
        if self._worker_conn is not None:
            worker_conn = self._worker_conn
            steps.append((
                "cancel attach worker query",
                lambda: _cancel_open_connection(worker_conn),
            ))
        if self._report_thread is not None:
            steps.append((
                "join report session thread",
                lambda: _join_thread(self._report_thread, 10, "report session thread"),
            ))
        if self._backfill_thread is not None:
            steps.append((
                "join backfill session thread",
                lambda: _join_thread(self._backfill_thread, 10, "backfill session thread"),
            ))
        if self._worker_thread is not None:
            steps.append((
                "join attach worker thread",
                lambda: _join_thread(self._worker_thread, 10, "attach worker thread"),
            ))
        _run_cleanup_steps(
            f"Partition-migration runtime cleanup for "
            f"{context.scenario_id}/{context.case_id}",
            steps,
        )
        self._terminate_case_sessions(context)
        self._report_thread = None
        self._worker_thread = None
        self._backfill_thread = None
        self._report_conn = None
        self._worker_conn = None
        self._backfill_conn = None
        self._stop_event = None

    def _terminate_case_sessions(self, context: FaultLifecycleContext) -> None:
        env = context.env
        _require_sql_success(
            env.execute_sql(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = current_database()
                  AND pid <> pg_backend_pid()
                  AND (application_name = '%(report)s'
                       OR application_name LIKE '%(worker)s%%'
                       OR application_name LIKE '%(backfill)s%%');
                """
                % {
                    "report": self.report_application_name,
                    "worker": self.worker_application_name,
                    "backfill": self.backfill_application_name or "none-",
                }
            ),
            "terminate partition-migration case sessions",
        )

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        print(
            "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
            "Recovering partition migration state..."
        )
        self._stop_runtime(context)
        env = self.env
        if not env.reconnect():
            raise RuntimeError(
                f"Partition-migration recovery could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        _require_sql_success(
            env.execute_sql("SET lock_timeout = '10s'; SET statement_timeout = '120s';"),
            "bound recovery session timeouts",
        )
        if self.prepared_move_gid:
            # The orphaned prepared transaction holds locks on the staging child;
            # it must be resolved before any DROP. Resolving it is the repair
            # goal itself, so the agent may already have committed or rolled it
            # back: only a surviving residual needs a recovery rollback.
            payload = _json_object(
                env.execute_sql(
                    f"SELECT count(*) FROM pg_prepared_xacts "
                    f"WHERE gid = '{self.prepared_move_gid}';"
                ),
                "check prepared move residual during recovery",
            )
            if int(payload["result"][0][0]) > 0:
                _require_sql_success(
                    env.execute_sql(
                        f"ROLLBACK PREPARED '{self.prepared_move_gid}';"
                    ),
                    f"rollback prepared move residual {self.prepared_move_gid}",
                )
            _require_sql_success(
                env.execute_sql("ALTER SYSTEM RESET max_prepared_transactions;"),
                "reset max_prepared_transactions",
            )
        self._reset_database_guard(env)
        self._rollback_prepared_xact(env)
        statements = (
            f"DROP TABLE IF EXISTS {self.job_status_table};",
            f"DROP TABLE IF EXISTS {self.audit_table};",
            f"DROP TABLE IF EXISTS {self.archive_table} CASCADE;",
            f"DROP TABLE IF EXISTS {self.archive_child_a};",
            f"DROP TABLE IF EXISTS {self.archive_child_b};",
            *(
                f"DROP TABLE IF EXISTS {child};"
                for child in self.staging_children
            ),
            *(
                (f"DROP TABLE IF EXISTS {self.refund_table};",)
                if self.refund_table else ()
            ),
            f"DROP TABLE IF EXISTS {self.parent_table} CASCADE;",
            f"DROP TABLE IF EXISTS {self.default_partition};",
            f"DROP TABLE IF EXISTS {self.may_partition};",
            f"DROP TABLE IF EXISTS {self.june_partition};",
            f"DROP TABLE IF EXISTS {self.legacy_table} CASCADE;",
            f"DROP SEQUENCE IF EXISTS {self.payment_sequence};",
        )
        for statement in statements:
            _require_sql_success(
                env.execute_sql(statement),
                f"recover partition-migration artifact with {statement}",
            )
        self._job_rows = []
        print(
            "[FaultInjector:PgBusinessChangePartitionMigrationInjector] "
            "Recovery complete."
        )


class PgBusinessChangePartitionMigrationScenario(PostgresScenario):
    scenario_id = "pg_business_change_partition_migration"
    description = (
        "Partition migration ATTACH stall: default-partition conflict rows plus an "
        "AccessExclusiveLock queue behind a long report transaction."
    )
    cases = (
        _PGBUSINESSCHANGEPARTITIONMIGRATIONSCENARIO_CASE,
        _PGBUSINESSCHANGEPARTITIONMIGRATIONSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(
        self, case: PgBusinessChangePartitionMigrationCase
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgBusinessChangePartitionMigrationInjector,
                config={
                    "legacy_table": case.legacy_table,
                    "parent_table": case.parent_table,
                    "default_partition": case.default_partition,
                    "staging_children": case.staging_children,
                    "july_partition": case.july_partition,
                    "attach_july_partition": case.attach_july_partition,
                    "conflict_bound_start": case.conflict_bound_start,
                    "conflict_bound_end": case.conflict_bound_end,
                    "refund_table": case.refund_table,
                    "refund_child": case.refund_child,
                    "may_partition": case.may_partition,
                    "june_partition": case.june_partition,
                    "archive_table": case.archive_table,
                    "archive_child_a": case.archive_child_a,
                    "archive_child_b": case.archive_child_b,
                    "audit_table": case.audit_table,
                    "job_status_table": case.job_status_table,
                    "payment_sequence": case.payment_sequence,
                    "seed_ref_prefix": case.seed_ref_prefix,
                    "legacy_rows": case.legacy_rows,
                    "may_rows": case.may_rows,
                    "june_rows": case.june_rows,
                    "july_rows": case.july_rows,
                    "conflict_rows": case.conflict_rows,
                    "decoy_rows": case.decoy_rows,
                    "staging_residual_july_rows": case.staging_residual_july_rows,
                    "staging_residual_july_deleted_rows": (
                        case.staging_residual_july_deleted_rows
                    ),
                    "staging_residual_august_rows": case.staging_residual_august_rows,
                    "archive_rows": case.archive_rows,
                    "audit_rows": case.audit_rows,
                    "simulated_legacy_rows": case.simulated_legacy_rows,
                    "report_application_name": case.report_application_name,
                    "worker_application_name": case.worker_application_name,
                    "backfill_application_name": case.backfill_application_name,
                    "prepared_move_gid": case.prepared_move_gid,
                    "ingest_batch_ref_prefix": case.ingest_batch_ref_prefix,
                    "ingest_batch_rows": case.ingest_batch_rows,
                    "report_hold_seconds": case.report_hold_seconds,
                    "attach_lock_timeout_seconds": case.attach_lock_timeout_seconds,
                    "attach_retry_interval_seconds": case.attach_retry_interval_seconds,
                    "incident_attempts": case.incident_attempts,
                    "preflight_validation_attempt": case.preflight_validation_attempt,
                    "prepared_xact_gid": case.prepared_xact_gid,
                    "decoy_prepared_xact_gid": case.decoy_prepared_xact_gid,
                    "batch3_prepared_xact_gid": case.batch3_prepared_xact_gid,
                },
            ),
        )
