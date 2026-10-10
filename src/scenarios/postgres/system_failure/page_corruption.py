from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.system_failure import (
    PgSystemFailureAutoAnalyzeStormForSalesTablesAutoAnalyzeStormEvaluatorCase,
    PgSystemFailureAutoAnalyzeStormForStoreSalesAutoAnalyzeStormSimpleEvaluatorCase,
    PgSystemFailureConnectionStormForCheckoutPoolIdleTransactionStormEvaluatorCase,
    PgSystemFailureConnectionStormForCheckoutPoolLeakSimpleEvaluatorCase,
    PgSystemFailureDeadlockForCheckoutOrderDeadlockEvaluatorCase,
    PgSystemFailureDeadlockForSingleOrderPairDeadlockSimpleEvaluatorCase,
    PgSystemFailureFdExhaustionForNightlyReportingNofileExhaustionEvaluatorCase,
    PgSystemFailureFdExhaustionForReportExportFdExhaustionSimpleEvaluatorCase,
    PgSystemFailureIoCheckpointSpikesForCheckoutCheckpointSpikesEvaluatorCase,
    PgSystemFailureIoCheckpointSpikesForSingleCheckoutCheckpointSpikeSimpleEvaluatorCase,
    PgSystemFailureNoisyNeighborForWalArchiveCpuNeighborEvaluatorCase,
    PgSystemFailureNoisyNeighborForSingleArchiveCpuNeighborSimpleEvaluatorCase,
    PgSystemFailureOomForRestartMemoryConfigOomEvaluatorCase,
    PgSystemFailureOomForRestartSharedBuffersOomSimpleEvaluatorCase,
    PgSystemFailurePageCorruptionForOrderLineAuditPageCorruptionEvaluatorCase,
    PgSystemFailurePageCorruptionForInvoicePageCorruptionTriageSimpleEvaluatorCase,
    PgSystemFailureTempFileExplosionForNightlyMarginTempExhaustionEvaluatorCase,
    PgSystemFailureTempFileExplosionForDailySalesTempExhaustionSimpleEvaluatorCase,
    PgSystemFailureWalAccumulationForAnalyticsSlotWalRetentionEvaluatorCase,
    PgSystemFailureWalAccumulationForAbandonedReportSlotWalRetentionSimpleEvaluatorCase,
    PgSystemFailureXidWraparoundForPaymentLedgerXidWraparoundEvaluatorCase,
    PgSystemFailureXidWraparoundForBillingFreezeBlockedSimpleEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    PostgresCaseRuntime,
    PostgresScenario,
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    CaseResourceSpec,
    PostgresRuntimeSpec,
    PostgresScenarioCase,
)

_DEFAULT_SYSTEM_FAILURE_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)

_OOM_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=256,
    container_cpu_limit=0.5,
    container_memory_mb=256,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailurePageCorruptionCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    table: str
    check_query: str
    row_count: int
    recovery_snapshot_name: str = ""
    stale_snapshot_name: str = ""
    # A third maintenance copy holding only the live segment: probe-passing but
    # silently incomplete as a recovery source. Empty keeps the two-copy layout.
    incomplete_snapshot_name: str = ""
    # Pre-incident audit data-quality baseline (expected row count and amount
    # checksum of the served dataset); the result-type OP acceptance compares the
    # restored read path against it. Empty keeps triage-only cases without it.
    audit_baseline_table: str = ""
    read_path_view: str = ""
    history_view: str = ""
    history_audit_sql: str = ""
    history_audit_timeout_ms: int = 0
    archive_row_count: int = 200
    # Disjoint segment split: the archive holds order_id 1..archive_row_count and
    # the live relation keeps order_id >= live_segment_min_order_id; the read path
    # view becomes a UNION ALL over both physical relations. 0 keeps the legacy
    # copy-subset archive.
    live_segment_min_order_id: int = 0
    # Corrupt one physical page of the archive relation, this many blocks before
    # the end of its main fork. 0 leaves the archive physically healthy.
    corrupt_archive_tail_blocks: int = 0
    # The per-case recovery ledger (page_corruption_recovery_manifest) is a
    # business asset of the invoice triage case only; other cases must not expose it.
    create_recovery_manifest: bool = False
    # Production tail rows written after the fresh maintenance snapshot was
    # taken: the snapshot lags the audited dataset by this many rows, so a
    # pure-snapshot restore is incomplete and the repair must merge the readable
    # production tail. 0 keeps every copy aligned with production.
    snapshot_lag_rows: int = 0

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailurePageCorruptionForOrderLineAuditPageCorruptionScenarioCase(PgSystemFailurePageCorruptionCase):
    pass

_PGSYSTEMFAILUREPAGECORRUPTIONSCENARIO_CASE = PgSystemFailurePageCorruptionForOrderLineAuditPageCorruptionScenarioCase(
    case_id='order_line_audit_page_corruption',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "invalid page checksum error",
                    "entity": "order_line_audit_page_corruption",
                    "evidence": [
                        "the PostgreSQL log reported an invalid page checksum while reading order_line_audit"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "order line audit relation affected",
                    "entity": "order_line_audit_page_corruption",
                    "evidence": [
                        "the failing union read and relfilenode mapping identified order_line_audit block 1, "
                        "and a second same-incident corrupt cold page on order_line_audit_archive"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "ordinary sql cannot repair physical corruption",
                    "entity": "order_line_audit_page_corruption",
                    "evidence": [
                        "a checksum failure is physical corruption; the read path must be rebuilt from a clean copy"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "restore from verified clean snapshot",
                    "entity": "order_line_audit_page_corruption",
                    "evidence": [
                        "snapshot_0705 matches the audit baseline content on every checksum but lags production "
                        "by the 50 newest tail orders; rebuild the read path from it merged with the readable "
                        "production tail and verify row count, amount sum and the weighted amount checksum "
                        "against the audit baseline"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "rebuild the order_detail_live read path from the verified clean snapshot"
            ],
            "verification": [
                "verify the restored read path row count, amount sum and weighted amount checksum against the audit baseline"
            ]
        },
        "summary": "The reference path identifies physical checksum corruption on both union segments, restores the read path from the verified clean snapshot, and validates the audit baseline."
    },
    case_no=0,
    evaluator=PgSystemFailurePageCorruptionForOrderLineAuditPageCorruptionEvaluatorCase,
    runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates a single-table physical page corruption incident.',
    alert=(
        '[CRITICAL] [PostgreSQL/Primary] A subset of order-detail requests is currently '
        'failing while the rest of the service responds normally. Restore the order-detail '
        'audit read path so it serves complete and correct data again. You are authorized '
        'to run the SQL rebuild and catalog operations needed for restoration within this '
        'incident\'s business scope; do not enable zero_damaged_pages or '
        'ignore_checksum_failure, and keep the damaged relations available for '
        'post-incident analysis.'
    ),
    initial_state={'status': 'degraded', 'symptom': 'single_relation_read_failure', 'other_queries': 'healthy'},
    expected_target={'status': 'recovered',
 'affected_relation': 'order_line_audit',
 'restored_read_path': 'order_detail_live',
 'business_truth_intact': True},
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name='order_detail_history_audit',
                sql=(
                    "SET statement_timeout = '2s'; "
                    'SELECT count(*) FROM order_detail_history h '
                    'WHERE h.order_id BETWEEN 1 AND 8000 '
                    'AND (SELECT count(*) FROM order_line_audit_archive a '
                    'WHERE a.warehouse_id = h.warehouse_id '
                    'AND a.order_id BETWEEN 1 AND 3600) < 288;'
                ),
                qps=0.15,
                tier='LIGHT',
                application_name='order_archive_consistency_audit',
            ),
            WorkloadProfile(
                name='order_detail_live_probe',
                sql='SELECT count(*) FROM order_detail_live WHERE order_id BETWEEN 1 AND 5;',
                qps=0.2,
                tier='LIGHT',
                application_name='order_detail_live_probe',
            ),
            WorkloadProfile(
                name='order_archive_health_probe',
                sql='SELECT count(*) FROM order_line_audit_archive WHERE order_id BETWEEN 1 AND 50;',
                qps=0.2,
                tier='LIGHT',
                application_name='order_archive_health_probe',
            ),
        ),
        worker_count=1,
        seed=0x2F0C,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=5,
    ),
    table='order_line_audit',
    check_query='SELECT count(*) FROM order_detail_live WHERE warehouse_id BETWEEN 1 AND 10;',
    row_count=12000,
    recovery_snapshot_name='order_line_audit_snapshot_0705',
    stale_snapshot_name='order_line_audit_snapshot_0612',
    incomplete_snapshot_name='order_line_audit_snapshot_0701',
    audit_baseline_table='order_detail_audit_baseline',
    read_path_view='order_detail_live',
    history_view='order_detail_history',
    history_audit_sql=(
        'SELECT count(*) FROM order_detail_history h '
        'WHERE h.order_id BETWEEN 1 AND 8000 '
        'AND (SELECT count(*) FROM order_line_audit_archive a '
        'WHERE a.warehouse_id = h.warehouse_id '
        'AND a.order_id BETWEEN 1 AND 3600) < 288;'
    ),
    history_audit_timeout_ms=2000,
    archive_row_count=11000,
    live_segment_min_order_id=11001,
    corrupt_archive_tail_blocks=50,
    create_recovery_manifest=False,
    snapshot_lag_rows=50,
    difficulty=DifficultyCalibration(
        diagnostic_depth=8,
        environmental_complexity=0.269231,
        reference_run_ids=(
            "logs/traces/run_pg_system_failure_page_corruption_order_line_audit_page_corruption_"
            "MockLLMAgent.json",
        ),
    ),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailurePageCorruptionForInvoicePageCorruptionTriageSimpleScenarioCase(
    PgSystemFailurePageCorruptionCase
):
    pass


_PGSYSTEMFAILUREPAGECORRUPTIONSCENARIO_SIMPLE_CASE = (
    PgSystemFailurePageCorruptionForInvoicePageCorruptionTriageSimpleScenarioCase(
        case_id='invoice_page_corruption_triage_simple',
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "invalid page checksum error",
                        "entity": "invoice_page_corruption_triage_simple",
                        "evidence": [
                            "the PostgreSQL log reported an invalid page checksum while reading invoice_page_audit"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "invoice page audit relation affected",
                        "entity": "invoice_page_corruption_triage_simple",
                        "evidence": [
                            "the failing invoice audit query and relation metadata identified invoice_page_audit"
                        ]
                    }
                ]
            },
            "outcome": {
                "changes": [
                    "preserve the corrupt invoice_page_audit and replace the service relation from the validated recovery source"
                ],
                "verification": [
                    "verify the restored invoice_page_audit query and row count while retaining the corrupt evidence relation"
                ]
            },
            "summary": "The reference path identifies the corrupt invoice audit relation, preserves it as evidence, and restores the service relation from a clean validated source while retaining the business read index."
        },
        case_no=1,
        evaluator=PgSystemFailurePageCorruptionForInvoicePageCorruptionTriageSimpleEvaluatorCase,
        runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
        difficulty=DifficultyCalibration(
            diagnostic_depth=4,
            environmental_complexity=0.611111,
            reference_run_ids=(
                'logs/traces/run_pg_system_failure_page_corruption_invoice_page_corruption_triage_simple_'
                'MockLLMAgent.json',
            ),
        ),
        base_image_name='aiopsbench-pg-initialized:latest',
        workload_tag='initialized',
        title='An invoice audit relation has one corrupt physical page and a clean recovery source.',
        alert=(
            'Alert: one invoice-audit read path fails consistently while PostgreSQL and a '
            'second archive audit relation remain available. Reproduce the failing read, '
            'identify the affected relation and physical failure class from logs and relation '
            'metadata. The damaged relation must be preserved as forensic evidence and must not '
            'be rewritten in place; do not enable zero_damaged_pages or attempt in-place repair. '
            'Recent maintenance copies of the affected dataset exist on the primary; restore '
            'the service read path from a verified source and make sure the order_id lookup '
            'path is served by an equivalent index before submit.'
        ),
        initial_state={
            'status': 'degraded',
            'symptom': 'single_invoice_audit_read_failure',
            'other_queries': 'healthy',
        },
        expected_target={
            'status': 'recovered',
            'affected_relation': 'invoice_page_audit',
            'recovery_source': 'verified maintenance snapshot',
            'corrupt_evidence_preserved': True,
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=(
                WorkloadProfile(
                    name='catalog_health_probe',
                    sql='SELECT count(*) FROM pg_class;',
                    qps=0.1,
                    tier='LIGHT',
                    application_name='catalog_health_probe',
                ),
                WorkloadProfile(
                    name='invoice_archive_audit_probe',
                    sql='SELECT count(*) FROM invoice_page_audit_archive WHERE warehouse_id BETWEEN 1 AND 10;',
                    qps=0.2,
                    tier='LIGHT',
                    application_name='invoice_archive_audit_probe',
                ),
            ),
            worker_count=1,
            seed=0x2F0B,
            start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
            warmup_seconds=5,
        ),
        table='invoice_page_audit',
        check_query=(
            'SELECT count(*) FROM invoice_page_audit '
            'WHERE warehouse_id BETWEEN 1 AND 10;'
        ),
        row_count=3000,
        recovery_snapshot_name='invoice_page_audit_snapshot_0612',
        stale_snapshot_name='invoice_page_audit_snapshot_0701',
        create_recovery_manifest=True,
    )
)


import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import (
    PgQueryPerfFaultFingerprintProbe,
    _cancel_open_connection,
    _join_thread,
    _json_object,
    _json_response,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)

class PgSystemFailurePageCorruptionInjector(BaseFaultInjector):
    """
    模拟"数据页损坏或 Checksum 失败"故障。
    注入流程会开启 data checksums，创建目标业务表，停库后用 dd 篡改
    单个 relation 数据页，再启动数据库让目标查询触发真实页面校验错误。
    """

    def __init__(self):
        self.env = None
        self.table = "order_line_audit"
        self.check_query = (
            "SELECT count(*) FROM order_line_audit "
            "WHERE warehouse_id BETWEEN 1 AND 10;"
        )
        self.relpath = None
        self.full_path = None
        self.backup_path = None
        self.corrupt_block = 1
        self.fault_query_result = None
        self.log_excerpt = None
        self.relation_size = 0
        self.relfilenode = None
        self.archive_relpath = None
        self.archive_full_path = None
        self.archive_backup_path = None
        self.archive_corrupt_block = 0
        self.archive_relfilenode = None
        self.incomplete_snapshot_name = ""
        self.audit_baseline_table = ""
        self.snapshot_lag_rows = 0

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        import time

        self._configure(config, env)
        print("[FaultInjector:PgSystemFailurePageCorruptionInjector] "
              "Injecting single-page corruption fault...")

        with env.metrics_hidden():
            self._ensure_checksums_enabled()
            self._prepare_target_relation()
            self._capture_relation_metadata()
            self._stop_postgres()
            self._backup_and_corrupt_file()
            self._start_postgres()

        # Sampler reads must not touch the damaged relation while the fault is
        # active; the explicit failing probe remains Agent-visible evidence.

        time.sleep(1.0)
        self._verify_runtime_fault()
        print("[FaultInjector:PgSystemFailurePageCorruptionInjector] "
              f"Fault active on table={self.table}, relpath={self.relpath}, "
              f"block={self.corrupt_block}. Query result: {self.fault_query_result}")

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(
            config['table'], "table")
        self.check_query = config['check_query']
        self.row_count = int(config['row_count'])
        self.recovery_snapshot_name = _validate_sql_identifier(
            config['recovery_snapshot_name'], "recovery snapshot")
        self.stale_snapshot_name = _validate_sql_identifier(
            config['stale_snapshot_name'], "stale snapshot")
        self.incomplete_snapshot_name = str(config.get('incomplete_snapshot_name') or '')
        if self.incomplete_snapshot_name:
            _validate_sql_identifier(self.incomplete_snapshot_name, "incomplete snapshot")
        self.audit_baseline_table = str(config.get('audit_baseline_table') or '')
        if self.audit_baseline_table:
            _validate_sql_identifier(self.audit_baseline_table, "audit baseline table")
        self.read_path_view = str(config.get('read_path_view') or '')
        self.history_view = str(config.get('history_view') or '')
        self.history_audit_sql = str(config.get('history_audit_sql') or '')
        self.history_audit_timeout_ms = int(config.get('history_audit_timeout_ms') or 0)
        self.archive_row_count = int(config.get('archive_row_count') or 200)
        self.live_segment_min_order_id = int(config.get('live_segment_min_order_id') or 0)
        self.corrupt_archive_tail_blocks = int(config.get('corrupt_archive_tail_blocks') or 0)
        self.create_recovery_manifest = bool(config.get('create_recovery_manifest') or False)
        self.snapshot_lag_rows = int(config.get('snapshot_lag_rows') or 0)
        if self.read_path_view:
            _validate_sql_identifier(self.read_path_view, "read path view")
        if self.history_view:
            _validate_sql_identifier(self.history_view, "history view")
        self.relpath = None
        self.full_path = None
        self.backup_path = None
        self.fault_query_result = None
        self.log_excerpt = None
        self.archive_relpath = None
        self.archive_full_path = None
        self.archive_backup_path = None
        self.archive_corrupt_block = 0
        self.archive_relfilenode = None

    def _verify_runtime_fault(self) -> None:
        self.fault_query_result = self.env.execute_sql(
            f"SET statement_timeout = '5s'; {self.check_query}"
        )
        payload = _json_response(
            self.fault_query_result,
            "verify page-corruption query failure",
        )
        error = str(payload.get("error", ""))
        if payload.get("status") != "error" or not any(
            marker in error.lower() for marker in ("checksum", "invalid page")
        ):
            raise RuntimeError(
                f"Page-corruption fault query did not expose a checksum/page error: "
                f"table={self.table}, result={self.fault_query_result}"
            )
        self.log_excerpt = self.env.read_log("pg_log", 80)

    def _ensure_checksums_enabled(self):
        enabled = self._data_checksums_on()
        if enabled:
            return
        print("[FaultInjector:PgSystemFailurePageCorruptionInjector] "
              "Enabling data checksums offline...")
        self._stop_postgres()
        container = self.env.deployment.container_name
        pgdata = self.env.deployment.pgdata
        self._docker_exec([
            "bash", "-c",
            "PG_BIN=$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1) "
            f"&& su - postgres -c \"$PG_BIN/pg_checksums --enable -D {pgdata}\""
        ], timeout=900)
        self._start_postgres()
        if not self._data_checksums_on():
            raise RuntimeError("data_checksums could not be enabled")
        print("[FaultInjector:PgSystemFailurePageCorruptionInjector] "
              "data_checksums enabled.")

    def _data_checksums_on(self) -> bool:
        payload = _json_object(
            self.env.execute_sql("SHOW data_checksums;"),
            "read PostgreSQL data_checksums setting",
        )
        return str(payload["result"][0][0]).lower() in ("on", "true")

    _TABLE_COLUMNS = (
        "order_id, warehouse_id, district_id, line_number, "
        "item_id, quantity, amount, payload"
    )
    _GENERATED_COLUMNS = (
        "gs, (gs % 10) + 1, (gs % 5) + 1, (gs % 15) + 1, "
        "(random() * 100000)::int + 1, (random() * 10)::int + 1, "
        "round((random() * 1000)::numeric, 2), repeat(md5(gs::text), 24)"
    )

    def _prepare_target_relation(self):
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table};")
        decoy = f"{self.table}_archive"
        self.env.execute_sql(f"DROP TABLE IF EXISTS {decoy};")
        recovery = self.recovery_snapshot_name
        self.env.execute_sql(f"DROP TABLE IF EXISTS {recovery};")
        candidate = self.stale_snapshot_name
        self.env.execute_sql(f"DROP TABLE IF EXISTS {candidate};")
        if self.incomplete_snapshot_name:
            self.env.execute_sql(f"DROP TABLE IF EXISTS {self.incomplete_snapshot_name};")
        if self.audit_baseline_table:
            self.env.execute_sql(f"DROP TABLE IF EXISTS {self.audit_baseline_table};")
        disjoint = self.live_segment_min_order_id > 0
        if disjoint and self.archive_row_count + 1 != self.live_segment_min_order_id:
            raise RuntimeError(
                "Disjoint segment split must be gapless: "
                f"archive_row_count={self.archive_row_count}, "
                f"live_segment_min_order_id={self.live_segment_min_order_id}"
            )
        self.env.execute_sql(f"""
            CREATE TABLE {self.table} (
                order_id integer NOT NULL,
                warehouse_id integer NOT NULL,
                district_id integer NOT NULL,
                line_number integer NOT NULL,
                item_id integer NOT NULL,
                quantity integer NOT NULL,
                amount numeric(12, 2) NOT NULL,
                payload text NOT NULL,
                created_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
        """)
        lag = self.snapshot_lag_rows if disjoint else 0
        if lag and lag >= self.row_count - self.live_segment_min_order_id:
            raise RuntimeError(
                "Snapshot lag must leave snapshot rows in the live segment: "
                f"snapshot_lag_rows={lag}, live_segment_min_order_id={self.live_segment_min_order_id}, "
                f"row_count={self.row_count}"
            )
        snapshot_time_upper = self.row_count - lag
        if disjoint:
            self.env.execute_sql(f"""
                INSERT INTO {self.table} ({self._TABLE_COLUMNS})
                SELECT {self._GENERATED_COLUMNS}
                FROM generate_series(1, {self.row_count}) AS gs
                WHERE gs >= {self.live_segment_min_order_id}
                  AND gs <= {snapshot_time_upper};
            """)
            self.env.execute_sql(f"""
                CREATE TABLE {decoy} (
                    order_id integer NOT NULL,
                    warehouse_id integer NOT NULL,
                    district_id integer NOT NULL,
                    line_number integer NOT NULL,
                    item_id integer NOT NULL,
                    quantity integer NOT NULL,
                    amount numeric(12, 2) NOT NULL,
                    payload text NOT NULL,
                    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
                );
            """)
            self.env.execute_sql(f"""
                INSERT INTO {decoy} ({self._TABLE_COLUMNS})
                SELECT {self._GENERATED_COLUMNS}
                FROM generate_series(1, {self.archive_row_count}) AS gs;
            """)
        else:
            self.env.execute_sql(f"""
                INSERT INTO {self.table} ({self._TABLE_COLUMNS})
                SELECT {self._GENERATED_COLUMNS}
                FROM generate_series(1, {self.row_count}) AS gs;
            """)
            self.env.execute_sql(f"CREATE TABLE {decoy} AS TABLE {self.table} WITH NO DATA;")
            self.env.execute_sql(
                f"INSERT INTO {decoy} SELECT * FROM {self.table} WHERE order_id <= {self.archive_row_count};"
            )
        # The fresh maintenance snapshot and the hot-segment copy reflect the
        # production state at snapshot time; with a snapshot lag the production
        # tail rows do not exist yet.
        served_dataset = (
            f"SELECT * FROM {self.table} UNION ALL SELECT * FROM {decoy}"
            if disjoint else f"SELECT * FROM {self.table}"
        )
        self.env.execute_sql(f"CREATE TABLE {recovery} AS {served_dataset};")
        if self.incomplete_snapshot_name:
            self.env.execute_sql(
                f"CREATE TABLE {self.incomplete_snapshot_name} AS TABLE {self.table};"
            )
        if lag:
            self.env.execute_sql(f"""
                INSERT INTO {self.table} ({self._TABLE_COLUMNS})
                SELECT {self._GENERATED_COLUMNS}
                FROM generate_series({snapshot_time_upper + 1}, {self.row_count}) AS gs;
            """)
        # The stale reconciliation extract is taken after the tail orders and
        # covers the full audited dataset; the audit baseline freezes the
        # production final state's business truth.
        self.env.execute_sql(f"CREATE TABLE {candidate} AS {served_dataset};")
        # The stale snapshot drifts in a sum-compensated way on rows outside the
        # readable first page: +2.50 on twelve hot-segment rows and -2.50 on
        # twelve readable cold-segment rows keeps row count and plain amount sum
        # unchanged, so only the ledger's weighted checksum or a content-level
        # comparison against the readable production rows can reject the copy.
        drift_start = (
            self.live_segment_min_order_id + 499 if disjoint else 500
        )
        self.env.execute_sql(
            f"UPDATE {candidate} SET amount = amount + 2.50 "
            f"WHERE order_id BETWEEN {drift_start} AND {drift_start + 11};"
        )
        if disjoint:
            cold_drift_start = self.archive_row_count - 500
            self.env.execute_sql(
                f"UPDATE {candidate} SET amount = amount - 2.50 "
                f"WHERE order_id BETWEEN {cold_drift_start} AND {cold_drift_start + 11};"
            )
        if self.audit_baseline_table:
            self.env.execute_sql(f"""
                CREATE TABLE {self.audit_baseline_table} (
                    dataset_scope text PRIMARY KEY,
                    expected_row_count bigint NOT NULL,
                    expected_amount_sum numeric NOT NULL,
                    expected_weighted_amount_sum numeric NOT NULL
                );
            """)
            self.env.execute_sql(
                f"INSERT INTO {self.audit_baseline_table} "
                f"(dataset_scope, expected_row_count, expected_amount_sum, expected_weighted_amount_sum) "
                f"SELECT '{self.read_path_view or self.table}', count(*), sum(amount), "
                f"sum(amount * order_id) "
                f"FROM ({served_dataset}) AS served;"
            )
        if self.read_path_view:
            if disjoint:
                self.env.execute_sql(
                    f"CREATE VIEW {self.read_path_view} AS SELECT "
                    "order_id, warehouse_id, district_id, line_number, item_id, "
                    f"quantity, amount, payload, created_at FROM {self.table} "
                    "UNION ALL SELECT "
                    "order_id, warehouse_id, district_id, line_number, item_id, "
                    f"quantity, amount, payload, created_at FROM {decoy};"
                )
            else:
                self.env.execute_sql(
                    f"CREATE VIEW {self.read_path_view} AS SELECT "
                    "order_id, warehouse_id, district_id, line_number, item_id, "
                    f"quantity, amount, payload, created_at FROM {self.table};"
                )
        if self.history_view:
            self.env.execute_sql(
                f"CREATE VIEW {self.history_view} AS SELECT "
                "order_id, warehouse_id, district_id, line_number, item_id, "
                f"quantity, amount, payload, created_at FROM {decoy};"
            )
        self.env.execute_sql(f"CREATE INDEX {self.table}_order_id_idx ON {self.table}(order_id);")
        if disjoint:
            self.env.execute_sql(
                f"CREATE INDEX {decoy}_order_id_idx ON {decoy}(order_id);"
            )
        self.env.execute_sql(f"ANALYZE {self.table};")
        if self.history_view:
            self.env.execute_sql(f"ANALYZE {decoy};")
        self.env.execute_sql("CHECKPOINT;")

    def _capture_relation_metadata(self):
        result = self.env.execute_sql(f"""
            SELECT
                pg_relation_filepath('{self.table}'::regclass),
                pg_relation_size('{self.table}'::regclass),
                c.relfilenode,
                c.relpages,
                c.reltuples::bigint
            FROM pg_class c
            WHERE c.oid = '{self.table}'::regclass;
        """)
        try:
            obj = json.loads(result)
            rows = obj.get("result") or []
            row = rows[0]
            self.relpath = row[0]
            self.relation_size = int(row[1])
            self.relfilenode = int(row[2])
        except Exception as exc:
            raise RuntimeError(f"Unable to capture relation metadata: {result}") from exc
        if self.relation_size < 3 * 8192:
            raise RuntimeError(
                f"Relation {self.table} too small to corrupt safely: {self.relation_size}")
        self.corrupt_block = 1
        self.full_path = f"{self.env.deployment.pgdata}/{self.relpath}"
        self.backup_path = f"{self.full_path}.aiopsbench_page_corruption_backup"
        if self.create_recovery_manifest:
            self.env.execute_sql(
                "CREATE TABLE page_corruption_recovery_manifest "
                "(service_relation text PRIMARY KEY, original_relfilenode oid NOT NULL, original_path text NOT NULL, "
                "expected_amount numeric NOT NULL, expected_amount_sum numeric NOT NULL);"
            )
            self.env.execute_sql(
                "INSERT INTO page_corruption_recovery_manifest(service_relation, original_relfilenode, original_path, expected_amount, expected_amount_sum) "
                f"SELECT '{self.table}', {self.relfilenode}, '{self.relpath}', "
                f"(SELECT amount FROM {self.table} WHERE order_id = 1), "
                f"(SELECT sum(amount) FROM {self.table});"
            )
        if self.corrupt_archive_tail_blocks:
            decoy = f"{self.table}_archive"
            archive_result = self.env.execute_sql(f"""
                SELECT
                    pg_relation_filepath('{decoy}'::regclass),
                    pg_relation_size('{decoy}'::regclass),
                    c.relfilenode
                FROM pg_class c
                WHERE c.oid = '{decoy}'::regclass;
            """)
            try:
                obj = json.loads(archive_result)
                row = (obj.get("result") or [])[0]
                self.archive_relpath = row[0]
                archive_size = int(row[1])
                self.archive_relfilenode = int(row[2])
            except Exception as exc:
                raise RuntimeError(
                    f"Unable to capture archive relation metadata: {archive_result}") from exc
            archive_blocks = archive_size // 8192
            self.archive_corrupt_block = archive_blocks - self.corrupt_archive_tail_blocks
            if self.archive_corrupt_block < 2:
                raise RuntimeError(
                    f"Archive relation {decoy} too small for a cold-page corruption: "
                    f"blocks={archive_blocks}, tail_blocks={self.corrupt_archive_tail_blocks}")
            self.archive_full_path = f"{self.env.deployment.pgdata}/{self.archive_relpath}"
            self.archive_backup_path = (
                f"{self.archive_full_path}.aiopsbench_page_corruption_backup")

    def _backup_and_corrupt_file(self):
        if not self.full_path or not self.backup_path:
            raise RuntimeError("Relation file path was not captured")
        offset = self.corrupt_block * 8192 + 128
        # 只改动页面体内少量字节，保留文件大小和大部分页面结构，触发真实校验失败。
        script = (
            "set -e; "
            f"test -f '{self.full_path}'; "
            f"cp '{self.full_path}' '{self.backup_path}'; "
            f"dd if=/dev/urandom of='{self.full_path}' bs=1 seek={offset} "
            "count=32 conv=notrunc status=none; "
        )
        if self.archive_full_path:
            archive_offset = self.archive_corrupt_block * 8192 + 128
            script += (
                f"test -f '{self.archive_full_path}'; "
                f"cp '{self.archive_full_path}' '{self.archive_backup_path}'; "
                f"dd if=/dev/urandom of='{self.archive_full_path}' bs=1 seek={archive_offset} "
                "count=32 conv=notrunc status=none; "
            )
        script += "sync"
        self._docker_exec(["bash", "-c", script], timeout=30)

    def _stop_postgres(self):
        _require_sql_success(
            self.env.manage_instance("stop"),
            "stop PostgreSQL for page-corruption file operation",
        )

    def _start_postgres(self):
        result = self.env.manage_instance("start")
        try:
            obj = json.loads(result)
            if obj.get("status") != "success":
                raise RuntimeError(result)
        except json.JSONDecodeError as exc:
            raise RuntimeError(result) from exc
        self.env.reconnect()

    def _docker_exec(self, args: list, timeout: int = 30):
        import subprocess

        container = self.env.deployment.container_name
        cmd = ["docker", "exec", container] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"docker exec failed: {' '.join(cmd)}\n"
                f"stdout={result.stdout}\nstderr={result.stderr}"
            )
        return result.stdout

    def prepare_observability(self, context: FaultLifecycleContext):
        env = context.env
        return {
            "data_checksums": env.execute_sql("SHOW data_checksums;"),
            "fault_query": env.execute_sql(
                "SET statement_timeout = '5s'; "
                f"{self.check_query}"
            ),
            "healthy_query": env.execute_sql("SELECT count(*) FROM pg_class;"),
            "relation_metadata": env.execute_sql(
                f"SELECT pg_relation_filepath('{self.table}'::regclass), "
                f"pg_relation_size('{self.table}'::regclass), relpages, reltuples::bigint "
                f"FROM pg_class WHERE oid = '{self.table}'::regclass;"
            ),
            "pg_log": env.read_log("pg_log", 80),
            # Prime one deterministic history-audit timeout after the pg_log read so
            # the competing noise is present in the Agent-visible window from the
            # first read; the workload profile keeps adding entries afterwards.
            **self._prime_history_audit_noise(env),
            "relpath": self.relpath,
            "corrupt_block": self.corrupt_block,
        }

    def _prime_history_audit_noise(self, env) -> dict:
        if not self.history_audit_sql:
            return {}
        env.execute_sql(f"SET statement_timeout = '{self.history_audit_timeout_ms}ms';")
        result = env.execute_sql(self.history_audit_sql)
        env.execute_sql("RESET statement_timeout;")
        payload = _json_response(
            result,
            "prime history-audit timeout noise",
        )
        error = str(payload.get("error", ""))
        if payload.get("status") != "error" or "statement timeout" not in error.casefold():
            raise RuntimeError(
                "History-audit timeout noise did not produce a statement-timeout error: "
                f"history_view={self.history_view!r}, result={result}"
            )
        return {"history_audit_prime": result}

    def quiesce(self, context: FaultLifecycleContext):
        """No background threads or runtime resources to clean up."""
        pass

    def recover(self, context: FaultLifecycleContext):
        print("[FaultInjector:PgSystemFailurePageCorruptionInjector] Recovering...")
        self._stop_postgres()
        restore_script = (
            f"test -f '{self.backup_path}' && "
            f"cp '{self.backup_path}' '{self.full_path}' && "
            f"rm -f '{self.backup_path}'"
        )
        if self.archive_full_path:
            restore_script += (
                f" && test -f '{self.archive_backup_path}' && "
                f"cp '{self.archive_backup_path}' '{self.archive_full_path}' && "
                f"rm -f '{self.archive_backup_path}'"
            )
        try:
            self._docker_exec(["bash", "-c", restore_script], timeout=30)
        finally:
            self._start_postgres()

        for setting in ("zero_damaged_pages", "ignore_checksum_failure"):
            _require_sql_success(
                self.env.execute_sql(f"ALTER SYSTEM RESET {setting};"),
                f"recover page-corruption setting {setting}",
            )
        _require_sql_success(
            self.env.execute_sql("SELECT pg_reload_conf();"),
            "reload recovered page-corruption settings",
        )
        # 清理 LLM 误用 zero_damaged_pages 抢救时可能留下的演练表，避免污染下一次注入。
        # 视图依赖目标表，必须先于表删除。
        view_drops = "".join(
            f"DROP VIEW IF EXISTS {view}; "
            for view in (self.read_path_view, self.history_view) if view
        )
        _require_sql_success(
            self.env.execute_sql(
                f"{view_drops}"
                f"DROP TABLE IF EXISTS {self.table}_recovered; "
                f"DROP TABLE IF EXISTS {self.table}_corrupted; "
                f"DROP TABLE IF EXISTS {self.table}_archive; "
                f"DROP TABLE IF EXISTS {self.recovery_snapshot_name}; "
                f"DROP TABLE IF EXISTS {self.stale_snapshot_name}; "
                + (
                    f"DROP TABLE IF EXISTS {self.incomplete_snapshot_name}; "
                    if self.incomplete_snapshot_name
                    else ""
                )
                + (
                    f"DROP TABLE IF EXISTS {self.audit_baseline_table}; "
                    if self.audit_baseline_table
                    else ""
                )
                + f"DROP TABLE IF EXISTS {self.table}_recovery_source; "
                f"DROP TABLE IF EXISTS {self.table}_recovery_candidate; "
                f"DROP TABLE IF EXISTS {self.table}_corrupt; "
                f"DROP INDEX IF EXISTS {self.table}_order_id_idx; "
                f"DROP INDEX IF EXISTS {self.table}_archive_order_id_idx; "
                "DROP TABLE IF EXISTS page_corruption_recovery_manifest; "
                f"DROP TABLE IF EXISTS {self.table};"
            ),
            f"drop page-corruption scenario tables for {self.table}",
        )
        self.relpath = None
        self.full_path = None
        self.backup_path = None
        self.fault_query_result = None
        self.log_excerpt = None
        self.archive_relpath = None
        self.archive_full_path = None
        self.archive_backup_path = None
        self.archive_corrupt_block = 0
        self.archive_relfilenode = None
        print("[FaultInjector:PgSystemFailurePageCorruptionInjector] Recovery complete.")

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        if not self._data_checksums_on():
            raise RuntimeError("Page-corruption fault image does not have data checksums enabled")
        self._capture_relation_metadata()
        backup_paths = [self.full_path, self.backup_path]
        if self.archive_full_path:
            backup_paths += [self.archive_full_path, self.archive_backup_path]
        backup_test = " && ".join(f"test -f '{path}'" for path in backup_paths)
        self._docker_exec(["bash", "-c", backup_test], timeout=30)
        self._verify_runtime_fault()


class PgSystemFailurePageCorruptionScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_page_corruption'
    description = 'Simulates a single-table physical page corruption incident.'
    cases = (
        _PGSYSTEMFAILUREPAGECORRUPTIONSCENARIO_CASE,
        _PGSYSTEMFAILUREPAGECORRUPTIONSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailurePageCorruptionCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailurePageCorruptionInjector,
                config={
                    'table': case.table,
                    'check_query': case.check_query,
                    'row_count': case.row_count,
                    'recovery_snapshot_name': case.recovery_snapshot_name,
                    'stale_snapshot_name': case.stale_snapshot_name,
                    'incomplete_snapshot_name': case.incomplete_snapshot_name,
                    'audit_baseline_table': case.audit_baseline_table,
                    'read_path_view': case.read_path_view,
                    'history_view': case.history_view,
                    'history_audit_sql': case.history_audit_sql,
                    'history_audit_timeout_ms': case.history_audit_timeout_ms,
                    'archive_row_count': case.archive_row_count,
                    'live_segment_min_order_id': case.live_segment_min_order_id,
                    'corrupt_archive_tail_blocks': case.corrupt_archive_tail_blocks,
                    'create_recovery_manifest': case.create_recovery_manifest,
                    'snapshot_lag_rows': case.snapshot_lag_rows,
                },
            ),
        )
