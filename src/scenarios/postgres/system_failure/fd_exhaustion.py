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

from src.workloads.tpcds import default_mix

from ...base import (
    PostgresCaseRuntime,
    PostgresScenario,
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    EMPTY_BACKGROUND_WORKLOAD,
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
class PgSystemFailureFdExhaustionCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    schema_name: str
    table_prefix: str
    table_count: int
    low_nofile_limit: int
    safe_nofile_limit: int
    background_connections: int
    app_role: str
    app_password: str
    app_name_prefix: str
    noisy_sources: tuple[str, ...]
    validation_sql: str
    failure_probe_timeout_seconds: int
    recovery_probe_timeout_seconds: int
    slow_queries: tuple[str, ...]
    noisy_sources_2: tuple[str, ...]
    production_noise: bool
    # Extended fault fields (report_export_fd_exhaustion_simple only; the nightly case keeps defaults
    # so its fault image, evaluator identity, and difficulty behavior stay unchanged).
    control_schema: str = ""
    stuck_job_run_id: str = ""
    stuck_job_run_id_2: str = ""
    protected_job_run_id: str = ""
    stuck_job_family: str = ""
    healthy_job_family: str = ""
    stuck_job_notes: str = ""
    persistent_sessions: tuple[str, ...] = ()
    refresh_result_rows: tuple[tuple[int, int], ...] = ()
    noise_log_lines: tuple[str, ...] = ()

    @property
    def refresh_result_totals(self) -> tuple[int, int, int]:
        return (
            len(self.refresh_result_rows),
            sum(row_count for row_count, _ in self.refresh_result_rows),
            sum(checksum for _, checksum in self.refresh_result_rows),
        )

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureFdExhaustionForNightlyReportingNofileExhaustionScenarioCase(PgSystemFailureFdExhaustionCase):
    pass

_PGSYSTEMFAILUREFDEXHAUSTIONSCENARIO_CASE = PgSystemFailureFdExhaustionForNightlyReportingNofileExhaustionScenarioCase(
    case_id='nightly_reporting_nofile_exhaustion',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "too many open files",
                    "entity": "nightly_reporting_nofile_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed too many open files"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "postmaster nofile limit too low",
                    "entity": "nightly_reporting_nofile_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed postmaster nofile limit too low"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "report archive probe fanout consumes descriptors",
                    "entity": "nightly_reporting_nofile_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed report archive probe fanout consumes descriptors"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "raise nofile to 4096 and restart",
                    "entity": "nightly_reporting_nofile_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed raise nofile to 4096 and restart"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "raise persistent nofile and bound report/archive fan-out"
            ],
            "verification": [
                "nofile and validation query were rechecked"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgSystemFailureFdExhaustionForNightlyReportingNofileExhaustionEvaluatorCase,
    runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='Simulates mixed production query and connection failures caused by an exhausted OS file descriptor limit.',
    alert='P1 Alert: checkout and reporting APIs are intermittently failing during the nightly revenue export window. Dashboards show a mix of slow statements, checkpoint write spikes, connection-pool retry storms, archive/COPY warnings, and monitoring probe errors. A DBA administrative path to the PostgreSQL instance still works. Find the real rejecting layer, separate it from the noisy symptoms, restore service, and submit evidence plus a temporary and permanent remediation plan.',
    initial_state={'status': 'mixed_query_and_connection_failures',
 'database_logs': 'redacted application errors plus PostgreSQL resource errors',
 'root_cause_layer': 'os_process_limit',
 'red_herrings': ('slow_queries', 'checkpoint_io', 'connection_pool', 'archive_job')},
    expected_target={'status': 'recovered',
 'nofile_limit': '>=4096',
 'postgresql_restarted': True,
 'validation_query': 'succeeds',
 'leak_source': 'reporting/archive/probe fan-out bounded'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(default_mix()),
        worker_count=6,
        seed=0,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    ),
    schema_name='ops_reporting',
    table_prefix='batch_slice',
    table_count=96,
    low_nofile_limit=8,
    safe_nofile_limit=4096,
    background_connections=80,
    app_role='order_app',
    app_password='order_app_pwd',
    app_name_prefix='checkout_pool',
    noisy_sources=('checkout_pool', 'archive_copy_worker', 'prometheus_probe', 'daily_revenue_report'),
    validation_sql=("SELECT sum(c) AS total_rows FROM (SELECT count(*) AS c FROM "
 'ops_reporting.batch_slice_000 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_001 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_002 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_003 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_004 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_005 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_006 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_007 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_008 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_009 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_010 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_011 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_012 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_013 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_014 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_015 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_016 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_017 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_018 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_019 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_020 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_021 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_022 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_023 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_024 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_025 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_026 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_027 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_028 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_029 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_030 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_031 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_032 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_033 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_034 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_035 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_036 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_037 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_038 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_039 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_040 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_041 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_042 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_043 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_044 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_045 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_046 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_047 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_048 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_049 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_050 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_051 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_052 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_053 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_054 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_055 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_056 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_057 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_058 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_059 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_060 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_061 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_062 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_063 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_064 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_065 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_066 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_067 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_068 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_069 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_070 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_071 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_072 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_073 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_074 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_075 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_076 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_077 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_078 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_079 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_080 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_081 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_082 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_083 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_084 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_085 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_086 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_087 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_088 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_089 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_090 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_091 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_092 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_093 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_094 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_095) AS daily_rollup;'),
    failure_probe_timeout_seconds=8,
    recovery_probe_timeout_seconds=30,
    slow_queries=("SET statement_timeout = '8s'; SELECT sum(c) AS total_rows FROM (SELECT count(*) AS c FROM "
 'ops_reporting.batch_slice_000 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_001 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_002 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_003 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_004 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_005 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_006 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_007 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_008 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_009 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_010 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_011 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_012 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_013 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_014 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_015 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_016 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_017 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_018 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_019 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_020 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_021 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_022 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_023 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_024 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_025 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_026 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_027 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_028 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_029 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_030 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_031 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_032 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_033 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_034 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_035 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_036 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_037 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_038 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_039 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_040 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_041 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_042 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_043 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_044 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_045 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_046 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_047 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_048 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_049 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_050 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_051 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_052 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_053 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_054 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_055 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_056 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_057 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_058 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_059 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_060 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_061 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_062 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_063 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_064 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_065 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_066 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_067 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_068 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_069 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_070 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_071 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_072 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_073 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_074 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_075 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_076 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_077 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_078 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_079 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_080 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_081 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_082 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_083 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_084 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_085 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_086 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_087 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_088 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_089 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_090 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_091 UNION ALL SELECT count(*) AS c FROM '
 'ops_reporting.batch_slice_092 UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_093 '
 'UNION ALL SELECT count(*) AS c FROM ops_reporting.batch_slice_094 UNION ALL SELECT count(*) AS c '
 'FROM ops_reporting.batch_slice_095) AS daily_rollup;',),
    noisy_sources_2=('checkout_pool', 'archive_copy_worker', 'prometheus_probe', 'daily_revenue_report'),
    production_noise=True,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.458333,
        reference_run_ids=(
            "reference-46__pg_system_failure_fd_exhaustion__"
            "nightly_reporting_nofile_exhaustion__mock__r001",
        ),
    ),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureFdExhaustionForReportExportFdExhaustionSimpleScenarioCase(
    PgSystemFailureFdExhaustionCase
):
    pass


def _fd_validation_sql(schema: str, prefix: str, table_count: int) -> str:
    selects = " UNION ALL ".join(
        f"SELECT count(*) AS c FROM {schema}.{prefix}_{index:03d}"
        for index in range(table_count)
    )
    return f"SELECT sum(c) AS total_rows FROM ({selects}) AS daily_rollup;"


_PGSYSTEMFAILUREFDEXHAUSTIONSCENARIO_SIMPLE_CASE = (
    PgSystemFailureFdExhaustionForReportExportFdExhaustionSimpleScenarioCase(
        case_id='report_export_fd_exhaustion_simple',
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "too many open files",
                        "entity": "report_export_fd_exhaustion_simple",
                        "evidence": [
                            "scripted diagnostic actions observed too many open files"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "postmaster nofile limit too low",
                        "entity": "report_export_fd_exhaustion_simple",
                        "evidence": [
                            "scripted diagnostic actions observed postmaster nofile limit too low"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "report archive probe fanout consumes descriptors",
                        "entity": "report_export_fd_exhaustion_simple",
                        "evidence": [
                            "scripted diagnostic actions observed report archive probe fanout consumes descriptors"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "stuck ledger export run left running",
                        "entity": (
                            "report_export_control.export_job_run/"
                            "ledger_sync_full_20260913b + ledger_sync_delta_20260913c "
                            "(expired leases); summary_refresh_backfill_20260913 protected"
                        ),
                        "evidence": [
                            "scripted diagnostic actions observed both orphaned ledger export runs "
                            "with expired leases left RUNNING while the leased backfill run stayed alive"
                        ]
                    }
                ]
            },
            "outcome": {
                "changes": [
                    "raise persistent nofile, restart PostgreSQL, close both orphaned ledger export runs, "
                    "and keep the leased backfill running"
                ],
                "verification": [
                    "nofile, validation query, orphan run statuses, protected backfill status, and "
                    "refresh results were rechecked"
                ]
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification."
        },
        case_no=1,
        evaluator=PgSystemFailureFdExhaustionForReportExportFdExhaustionSimpleEvaluatorCase,
        runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
        difficulty=DifficultyCalibration(
            diagnostic_depth=5,
            environmental_complexity=0.5495,
            reference_run_ids=(
                'reference-264__pg_system_failure_fd_exhaustion',
                'logs/traces/run_pg_system_failure_fd_exhaustion_report_export_fd_exhaustion_simple_'
                'MockLLMAgent',
            ),
        ),
        base_image_name='aiopsbench-pg-tpcds:latest',
        workload_tag='tpcds',
        dataset_scale=1,
        title=(
            'A single reporting export fan-out exhausts the PostgreSQL process file limit, '
            'leaving a stuck ledger export run that must be closed out.'
        ),
        alert=(
            'Alert: a scheduled report export intermittently fails while PostgreSQL remains '
            'reachable through the DBA path. A low-rate date health probe is also active. '
            'The export platform records job runs in a control schema inside this database '
            'and resumes or abandons runs based on those records. Identify the rejecting '
            'resource layer and the export pattern that consumes it, restore the export '
            'safely, leave the export platform job records in a consistent state, and '
            'provide a durable prevention plan.'
        ),
        initial_state={
            'status': 'report_export_failing',
            'database': 'administrative_path_available',
            'health_probe': 'low_rate',
        },
        expected_target={
            'status': 'recovered',
            'nofile_limit': '>=4096',
            'postgresql_restarted': True,
            'export_fanout': 'bounded',
            'stuck_job_run': 'both orphaned runs closed (FAILED or CANCELLED)',
            'protected_job_run': 'leased backfill still RUNNING',
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=(
                WorkloadProfile(
                    name='date_health_probe',
                    sql='SELECT count(*) FROM date_dim WHERE d_year = 2001;',
                    qps=0.1,
                    tier='LIGHT',
                    application_name='date_health_probe',
                ),
            ),
            worker_count=1,
            seed=0x2F09,
            start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
            warmup_seconds=5,
        ),
        schema_name='report_export_simple',
        table_prefix='export_slice',
        table_count=24,
        low_nofile_limit=8,
        safe_nofile_limit=4096,
        background_connections=12,
        app_role='report_export_app',
        app_password='report_export_pwd',
        app_name_prefix='report_export',
        noisy_sources=('report_export',),
        validation_sql=_fd_validation_sql('report_export_simple', 'export_slice', 24),
        failure_probe_timeout_seconds=8,
        recovery_probe_timeout_seconds=8,
        slow_queries=(),
        noisy_sources_2=('report_export',),
        production_noise=False,
        control_schema='report_export_control',
        stuck_job_run_id='ledger_sync_full_20260913b',
        stuck_job_run_id_2='ledger_sync_delta_20260913c',
        protected_job_run_id='summary_refresh_backfill_20260913',
        stuck_job_family='ledger_sync',
        healthy_job_family='summary_refresh',
        stuck_job_notes=(
            'full ledger export over 24 export_slice relations; lease_until is the scheduler '
            'lease: an expired lease means no worker owns this run; the scheduler resumes '
            'RUNNING runs and each retry doubles the slice fan-out; close orphaned runs '
            '(FAILED/CANCELLED) to stop the reschedule'
        ),
        persistent_sessions=(
            'ledger_sync_export_00',
            'summary_refresh_00',
            'summary_refresh_01',
            'summary_refresh_02',
        ),
        refresh_result_rows=(
            (120, 4801),
            (118, 4711),
            (124, 4957),
            (117, 4680),
            (121, 4839),
            (119, 4756),
        ),
        noise_log_lines=(
            "2026-07-01 00:00:06.010 UTC [601] LOG:  connection authorized: user=report_export_app database=testdb application_name=summary_refresh_03",
            "2026-07-01 00:00:06.020 UTC [602] LOG:  disconnection: session time: 0:00:31.220 user=report_export_app database=testdb application_name=summary_refresh_02 host=172.17.0.1",
            "2026-07-01 00:00:06.030 UTC [603] WARNING:  remaining connection slots are reserved for roles with privileges of the pg_use_reserved_connections role",
            "2026-07-01 00:00:06.040 UTC [604] LOG:  checkpoint starting: time",
            "2026-07-01 00:00:06.050 UTC [605] LOG:  checkpoint complete: wrote 1612 buffers (9.8%); sync files=38, longest=219.443 ms",
            "2026-07-01 00:00:06.060 UTC [606] WARNING:  checkpoint sync time exceeded SLO while reports were failing",
            "2026-07-01 00:00:06.070 UTC [607] LOG:  temporary file: path \"base/pgsql_tmp/pgsql_tmp614.0\", size 58720256 /* ledger_sync_delta */",
            "2026-07-01 00:00:06.080 UTC [608] LOG:  duration: 1848.220 ms  execute <unnamed>: SELECT refresh_summary_metrics($1) /* application_name=summary_refresh_00 */",
            "2026-07-01 00:00:06.090 UTC [609] WARNING:  canceling statement due to statement timeout in summary refresh",
            "2026-07-01 00:00:06.100 UTC [610] LOG:  automatic analyze of table \"public.store_sales\" system usage: CPU 0.42s/1.71u sec elapsed 6.88 sec",
            "2026-07-01 00:00:06.110 UTC [611] WARNING:  date_health_probe database ping timeout after retry",
            "2026-07-01 00:00:06.120 UTC [612] WARNING:  summary_refresh_01 retrying after SQLSTATE 08006",
            "2026-07-01 00:00:06.130 UTC [613] LOG:  duration: 2311.904 ms  statement: SELECT build_customer_activity_rollup(20260701) /* application_name=summary_refresh_02 */",
            "2026-07-01 00:00:06.140 UTC [614] LOG:  background worker \"parallel worker\" exited with exit code 1",
            "2026-07-01 00:00:06.150 UTC [615] LOG:  connection authorized: user=report_export_app database=testdb application_name=date_health_probe",
            "2026-07-01 00:00:06.160 UTC [616] WARNING:  could not serialize access due to concurrent update in summary refresh",
            "2026-07-01 00:00:06.170 UTC [617] LOG:  duration: 944.337 ms  parse <unnamed>: SELECT * FROM catalog_sales WHERE cs_sold_date_sk = $1",
            "2026-07-01 00:00:06.180 UTC [618] WARNING:  ledger_sync_delta retry 8 reported slow slice batch; scheduler backoff active",
            "2026-07-01 00:00:06.190 UTC [619] LOG:  automatic vacuum of table \"public.inventory\": index scans: 1",
            "2026-07-01 00:00:06.200 UTC [620] LOG:  checkpoint complete: wrote 842 buffers (5.1%); sync files=21, longest=141.208 ms",
            "2026-07-01 00:00:06.210 UTC [621] LOG:  duration: 1287.552 ms  execute <unnamed>: SELECT refresh_summary_metrics($1) /* application_name=summary_refresh_01 */",
            "2026-07-01 00:00:06.220 UTC [622] LOG:  temporary file: path \"base/pgsql_tmp/pgsql_tmp620.0\", size 33554432 /* summary_refresh_01 */",
            "2026-07-01 00:00:06.230 UTC [623] LOG:  duration: 471.204 ms  statement: SELECT count(*) FROM date_dim WHERE d_year = 2001;",
            "2026-07-01 00:00:06.240 UTC [624] WARNING:  summary_refresh_00 retry limit backoff: next attempt in 30s",
            "2026-07-01 00:00:06.250 UTC [625] LOG:  disconnection: session time: 0:00:12.004 user=report_export_app database=testdb application_name=summary_refresh_03 host=172.17.0.1",
            "2026-07-01 00:00:06.260 UTC [626] LOG:  automatic analyze of table \"public.catalog_returns\" system usage: CPU 0.18s/0.66u sec elapsed 3.02 sec",
            "2026-07-01 00:00:06.270 UTC [627] WARNING:  archive of daily revenue CSV skipped: upstream export not ready",
            "2026-07-01 00:00:06.280 UTC [628] LOG:  duration: 2077.881 ms  statement: SELECT build_customer_activity_rollup(20260630) /* application_name=summary_refresh_01 */",
            "2026-07-01 00:00:06.290 UTC [629] LOG:  checkpoint starting: time",
            "2026-07-01 00:00:06.300 UTC [630] WARNING:  pg_stat_statements query text truncated for 3 slow reporting statements",
        ),
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

class PgSystemFailureFdExhaustionInjector(BaseFaultInjector):
    """
    Simulate OS file descriptor exhaustion by lowering PostgreSQL's nofile soft
    limit and running a relation fan-out query that requires many file opens.
    """

    def __init__(self):
        self._connections = []

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print("[FaultInjector:FdExhaustion] Preparing relation fan-out workload...")
        self._restore_safe_limit()
        self._cleanup_leftovers()
        self._ensure_app_role()
        self._create_relation_fanout()
        self._open_persistent_sessions()
        self._create_control_state()
        if self.production_noise:
            self._emit_business_noise_logs()
        self._activate_runtime()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.schema_name = _validate_sql_identifier(config["schema_name"], "schema_name")
        self.table_prefix = _validate_sql_identifier(config["table_prefix"], "table_prefix")
        self.table_count = int(config['table_count'])
        self.low_nofile_limit = int(config['low_nofile_limit'])
        self.safe_nofile_limit = int(config['safe_nofile_limit'])
        self.background_connections = int(config['background_connections'])
        self.app_role = _validate_sql_identifier(config['app_role'], "app_role")
        self.app_password = config['app_password']
        self.app_name_prefix = config['app_name_prefix']
        self.noisy_sources = list(config['noisy_sources'])
        self.validation_sql = config['validation_sql']
        self.failure_probe_timeout_seconds = int(config['failure_probe_timeout_seconds'])
        self.production_noise = bool(config['production_noise'])
        # Extended fault knobs; empty defaults keep the nightly case behavior identical.
        self.control_schema = str(config.get('control_schema', '') or '')
        self.stuck_job_run_id = str(config.get('stuck_job_run_id', '') or '')
        self.stuck_job_run_id_2 = str(config.get('stuck_job_run_id_2', '') or '')
        self.protected_job_run_id = str(config.get('protected_job_run_id', '') or '')
        self.stuck_job_family = str(config.get('stuck_job_family', '') or '')
        self.healthy_job_family = str(config.get('healthy_job_family', '') or '')
        self.stuck_job_notes = str(config.get('stuck_job_notes', '') or '')
        self.persistent_sessions = tuple(config.get('persistent_sessions', ()) or ())
        self.refresh_result_rows = tuple(config.get('refresh_result_rows', ()) or ())
        self.noise_log_lines = tuple(config.get('noise_log_lines', ()) or ())
        self._connections = []
        self._persistent_connections = []
        self._persistent_session_pids = {}
        self._failure_error = ""
        self._log_excerpt = ""

    def _activate_runtime(self) -> None:
        import time

        if not self.production_noise:
            self.env._reset_pg_log_visibility()
        print(
            "[FaultInjector:FdExhaustion] Lowering running PostgreSQL nofile soft limit "
            f"to {self.low_nofile_limit}..."
        )
        set_result = self.env.manage_instance("set_config", "nofile", str(self.low_nofile_limit))
        _require_sql_success(set_result, "set low PostgreSQL nofile limit")
        if not self.env.deployment.apply_pg_nofile_limit_runtime(self.low_nofile_limit):
            raise RuntimeError("Failed to apply low nofile limit to running postmaster")
        time.sleep(1)

        self._open_background_connections()
        self._failure_error = self._run_failure_probe()
        self._emit_case_noise_logs()
        if self.production_noise:
            self._emit_post_failure_noise_logs()
        # 必须立刻关 background conn，否则 agent 后续 execute_sql / read_log
        # 也吃 fd，PG postmaster nofile 太低时一直被占，agent 永远连不上 PG → 0 分。
        # 关完之后 PG 还保有低 nofile，应用新连接仍然 reject（"too many open files"），
        # 这正是该场景指定故障的 fingerprint。
        self._close_background_connections()
        self._log_excerpt = self._read_recent_pg_log()
        evidence_text = f"{self._failure_error}\n{self._log_excerpt}".lower()
        if "too many open files" not in evidence_text:
            raise RuntimeError(
                "FD exhaustion probe did not produce 'Too many open files'; "
                f"probe_result={self._failure_error[:300]}"
            )
        print("[FaultInjector:FdExhaustion] Fault injection complete; pg_log contains 'Too many open files'.")

    def _build_validation_sql(self) -> str:
        parts = [
            f"SELECT count(*) AS c FROM {self.schema_name}.{self.table_prefix}_{idx:03d}"
            for idx in range(self.table_count)
        ]
        return (
            "SELECT sum(c) AS total_rows FROM ("
            + " UNION ALL ".join(parts)
            + ") AS daily_rollup;"
        )

    def _ensure_app_role(self):
        self.env.execute_sql(f"DROP ROLE IF EXISTS {self.app_role};")
        self.env.execute_sql(f"CREATE ROLE {self.app_role} LOGIN PASSWORD '{self.app_password}';")

    def _create_relation_fanout(self):
        self.env.execute_sql(f"DROP SCHEMA IF EXISTS {self.schema_name} CASCADE;")
        self.env.execute_sql(f"CREATE SCHEMA {self.schema_name};")
        for start in range(0, self.table_count, 16):
            statements = []
            for idx in range(start, min(start + 16, self.table_count)):
                table = f"{self.schema_name}.{self.table_prefix}_{idx:03d}"
                statements.append(
                    f"CREATE TABLE {table} (id integer PRIMARY KEY, amount integer NOT NULL); "
                    f"INSERT INTO {table} VALUES (1, {idx}); "
                    f"GRANT SELECT ON {table} TO {self.app_role};"
                )
            raw = self.env.execute_sql("\n".join(statements))
            if '"status": "success"' not in raw:
                raise RuntimeError(f"Failed to create fan-out tables: {raw}")

    def _open_persistent_sessions(self):
        """Open pre-fault sessions (stuck coordinator + healthy neighbors) at the safe limit.

        They must be opened before the nofile soft limit drops: new post-prlimit connections
        are rejected, which is exactly the fault fingerprint. The sessions then stay visible
        in pg_stat_activity for the whole episode.
        """
        import psycopg2

        for app_name in self.persistent_sessions:
            try:
                conn = psycopg2.connect(
                    host=self.env.host,
                    port=self.env.port,
                    user=self.app_role,
                    password=self.app_password,
                    dbname=self.env.dbname,
                    connect_timeout=3,
                    application_name=app_name,
                )
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_backend_pid();")
                    pid = cur.fetchone()[0]
                self._persistent_connections.append(conn)
                self._persistent_session_pids[app_name] = int(pid)
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to open persistent FD-exhaustion session {app_name}: {exc}"
                ) from exc

    def _create_control_state(self):
        """Create the export platform control schema with stuck runs and healthy truth."""
        if not self.control_schema:
            return
        schema = _validate_sql_identifier(self.control_schema, "control_schema")
        stuck_pid = self._persistent_session_pids.get('ledger_sync_export_00')
        healthy_pid = self._persistent_session_pids.get('summary_refresh_00')
        protected_pid = healthy_pid if healthy_pid is not None else 101
        statements = [
            f"DROP SCHEMA IF EXISTS {schema} CASCADE;",
            f"CREATE SCHEMA {schema};",
            (
                f"CREATE TABLE {schema}.export_job_run ("
                "job_run_id text PRIMARY KEY, "
                "job_family text NOT NULL, "
                "status text NOT NULL CHECK (status IN ('PENDING','RUNNING','SUCCEEDED','FAILED','CANCELLED')), "
                "slice_count integer NOT NULL, "
                "retry_count integer NOT NULL DEFAULT 0, "
                "started_at timestamptz NOT NULL, "
                "updated_at timestamptz NOT NULL, "
                "lease_until timestamptz, "
                "backend_pid integer, "
                "last_error text, "
                "notes text NOT NULL DEFAULT '');"
            ),
            (
                f"CREATE TABLE {schema}.refresh_result ("
                "result_id integer PRIMARY KEY, "
                "job_run_id text NOT NULL, "
                "row_count integer NOT NULL, "
                "checksum integer NOT NULL, "
                "produced_at timestamptz NOT NULL);"
            ),
            # history: closed successful runs (relative timestamps keep lease semantics live)
            (
                f"INSERT INTO {schema}.export_job_run (job_run_id, job_family, status, slice_count, "
                "retry_count, started_at, updated_at, lease_until, backend_pid, last_error, notes) VALUES "
                "('ledger_sync_full_20260912', 'ledger_sync', 'SUCCEEDED', 24, 0, "
                "now() - interval '25 hours', now() - interval '24 hours 42 minutes', NULL, NULL, NULL, "
                "'routine nightly full export'), "
                "('ledger_sync_delta_20260913a', 'ledger_sync', 'SUCCEEDED', 8, 0, "
                "now() - interval '13 hours', now() - interval '12 hours 56 minutes', NULL, NULL, NULL, "
                "'routine delta export');"
            ),
            # stuck run 1: fd errors + expired lease + dead coordinator pid
            (
                f"INSERT INTO {schema}.export_job_run (job_run_id, job_family, status, slice_count, "
                "retry_count, started_at, updated_at, lease_until, backend_pid, last_error, notes) VALUES "
                f"('{self.stuck_job_run_id}', 'ledger_sync', 'RUNNING', 24, 9, "
                "now() - interval '100 minutes', now() - interval '25 minutes', "
                f"now() - interval '20 minutes', {stuck_pid if stuck_pid is not None else 'NULL'}, "
                f"'retry 9 failed: too many open files', '{self.stuck_job_notes}');"
            ),
            # stuck run 2: no error string, expired lease, pid that owns no live session
            (
                f"INSERT INTO {schema}.export_job_run (job_run_id, job_family, status, slice_count, "
                "retry_count, started_at, updated_at, lease_until, backend_pid, last_error, notes) VALUES "
                f"('{self.stuck_job_run_id_2}', 'ledger_sync', 'RUNNING', 8, 0, "
                "now() - interval '50 minutes', now() - interval '26 minutes', "
                "now() - interval '26 minutes', 999999, "
                "NULL, 'delta export; lease_until is the scheduler lease: an expired lease means no "
                "worker owns this run; the scheduler resumes RUNNING runs and each retry doubles the "
                "slice fan-out');"
            ),
            # protected healthy backfill: valid lease + live session pid
            (
                f"INSERT INTO {schema}.export_job_run (job_run_id, job_family, status, slice_count, "
                "retry_count, started_at, updated_at, lease_until, backend_pid, last_error, notes) VALUES "
                f"('{self.protected_job_run_id}', 'summary_refresh', 'RUNNING', 1, 0, "
                "now() - interval '30 minutes', now() - interval '1 minute', "
                f"now() + interval '90 minutes', {protected_pid}, "
                "NULL, 'sanctioned two-hour backfill window; the worker renews the lease each minute "
                "while it runs; do not cancel or close this run');"
            ),
        ]
        for index, (row_count, checksum) in enumerate(self.refresh_result_rows, start=1):
            statements.append(
                f"INSERT INTO {schema}.refresh_result (result_id, job_run_id, row_count, checksum, produced_at) "
                f"VALUES ({index}, 'summary_refresh_20260913_{index:02d}', {row_count}, {checksum}, "
                f"now() - interval '{(len(self.refresh_result_rows) - index) * 5 + 10} minutes');"
            )
        for index in range(1, len(self.refresh_result_rows) + 1):
            statements.append(
                f"INSERT INTO {schema}.export_job_run (job_run_id, job_family, status, slice_count, "
                f"retry_count, started_at, updated_at, lease_until, backend_pid, last_error, notes) VALUES "
                f"('summary_refresh_20260913_{index:02d}', 'summary_refresh', 'SUCCEEDED', 1, 0, "
                f"now() - interval '{(len(self.refresh_result_rows) - index) * 5 + 15} minutes', "
                f"now() - interval '{(len(self.refresh_result_rows) - index) * 5 + 10} minutes', "
                f"NULL, NULL, NULL, 'healthy single-table refresh');"
            )
        raw = self.env.execute_sql("\n".join(statements))
        if '"status": "success"' not in raw:
            raise RuntimeError(f"Failed to create FD exhaustion control state: {raw}")

    def _emit_case_noise_logs(self):
        """Append bounded same-window business noise to the PostgreSQL log."""
        import shlex
        import subprocess

        if not self.noise_log_lines:
            return
        payload = "\n".join(self.noise_log_lines) + "\n"
        subprocess.run(
            [
                "docker", "exec", self.env.deployment.container_name, "sh", "-c",
                f"printf %s {shlex.quote(payload)} >> /var/log/postgresql/postgresql.log",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def _close_persistent_connections(self):
        for conn in list(getattr(self, "_persistent_connections", [])):
            try:
                conn.close()
            except Exception:
                pass
        self._persistent_connections = []

    def _open_background_connections(self):
        import psycopg2

        for idx in range(self.background_connections):
            app_name = self._app_name_for_connection(idx)
            try:
                conn = psycopg2.connect(
                    host=self.env.host,
                    port=self.env.port,
                    user=self.app_role,
                    password=self.app_password,
                    dbname=self.env.dbname,
                    connect_timeout=3,
                    application_name=app_name,
                )
                conn.autocommit = True
                self._connections.append(conn)
            except Exception as exc:
                self._failure_error += f"\nbackground connection {idx} failed: {exc}"
                break

    def _app_name_for_connection(self, idx: int) -> str:
        sources = self.noisy_sources or [self.app_name_prefix]
        return f"{sources[idx % len(sources)]}_{idx}"

    def _close_background_connections(self):
        for conn in list(getattr(self, "_connections", [])):
            try:
                conn.close()
            except Exception:
                pass
        self._connections = []

    def _run_failure_probe(self) -> str:
        raw = self.env.execute_sql(
            f"SET statement_timeout = '{self.failure_probe_timeout_seconds}s'; "
            f"{self.validation_sql}"
        )
        payload = _json_response(raw, "run FD exhaustion failure probe")
        if payload.get("status") == "success":
            return str(raw)
        if payload.get("status") != "error":
            raise RuntimeError(
                f"FD exhaustion probe returned an unknown status: result={raw}"
            )
        return str(payload["error"])

    def _read_recent_pg_log(self) -> str:
        import subprocess

        result = subprocess.run(
            [
                "docker", "exec", self.env.deployment.container_name, "sh", "-c",
                "found=0; "
                "for log_file in /var/log/postgresql/*.log; do "
                "  [ -f \"$log_file\" ] || continue; "
                "  found=1; "
                "  printf '%s\\n' \"--- $log_file\"; "
                "  tail -c 65536 \"$log_file\"; "
                "done; "
                "test \"$found\" -eq 1",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to read PostgreSQL log for FD exhaustion: "
                f"{(result.stderr or result.stdout).strip()}"
            )
        return result.stdout.strip()

    def _emit_business_noise_logs(self):
        # 直接写 PG log 文件，避免用 SQL RAISE LOG 扰动 postmaster FD 状态。
        import shlex
        import subprocess

        log_messages = [
            "duration: 1848.220 ms  execute <unnamed>: SELECT refresh_order_dashboard($1) /* application_name=checkout_pool */",
            "duration: 2311.904 ms  statement: SELECT build_customer_activity_rollup(20260701) /* application_name=daily_revenue_report */",
            "checkpoint starting: time",
            "checkpoint complete: wrote 1612 buffers (9.8%); sync files=38, longest=219.443 ms",
            "temporary file: path \"base/pgsql_tmp/pgsql_tmp614.0\", size 58720256 /* daily_revenue_report */",
            "automatic analyze of table \"public.store_sales\" system usage: CPU 0.42s/1.71u sec elapsed 6.88 sec",
            "connection authorized: user=order_app database=testdb application_name=checkout_pool_17",
            "connection authorized: user=order_app database=testdb application_name=archive_copy_worker_18",
            "connection authorized: user=order_app database=testdb application_name=prometheus_probe_19",
            "disconnection: session time: 0:00:04.812 user=order_app database=testdb host=172.17.0.1",
            "duration: 944.337 ms  parse <unnamed>: SELECT * FROM catalog_sales WHERE cs_sold_date_sk = $1",
            "background worker \"parallel worker\" exited with exit code 1",
        ]
        warning_messages = [
            "canceling statement due to statement timeout in order reporting refresh",
            "remaining connection slots are reserved for roles with privileges of the pg_use_reserved_connections role",
            "connection pool retry storm: checkout-api observed SQLSTATE 08006 from checkout_pool",
            "application warning: order service retried after client disconnect",
            "analytics_worker blocked by process 77 while reading catalog_sales",
            "archive_copy_worker COPY to object storage failed after client disconnect",
            "prometheus_probe reported database ping timeout after retry",
            "autovacuum worker skipped relation public.store_sales due to conflicting lock",
            "could not serialize access due to concurrent update in reporting refresh",
            "replication apply lag exceeded 20s on reporting subscriber",
        ]
        lines = []
        for _ in range(8):
            lines.extend(f"2026-07-01 00:00:00.000 UTC [417] LOG:  {msg}" for msg in log_messages)
            lines.extend(f"2026-07-01 00:00:00.000 UTC [418] WARNING:  {msg}" for msg in warning_messages)
        payload = "\n".join(lines) + "\n"
        subprocess.run(
            [
                "docker", "exec", self.env.deployment.container_name, "sh", "-c",
                f"printf %s {shlex.quote(payload)} >> /var/log/postgresql/postgresql.log",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def _emit_post_failure_noise_logs(self):
        import shlex
        import subprocess

        payload = "\n".join([
            "2026-07-01 00:00:06.000 UTC [512] WARNING: checkpoint sync time exceeded SLO while reports were failing",
            "2026-07-01 00:00:06.100 UTC [513] WARNING: daily_revenue_report retrying after SQLSTATE 08006",
            "2026-07-01 00:00:06.200 UTC [514] WARNING: archive_copy_worker saw short write during COPY export",
            "2026-07-01 00:00:06.300 UTC [515] WARNING: prometheus_probe database ping failed during retry storm",
        ]) + "\n"
        subprocess.run(
            [
                "docker", "exec", self.env.deployment.container_name, "sh", "-c",
                f"printf %s {shlex.quote(payload)} >> /var/log/postgresql/postgresql.log",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def _restore_safe_limit(self):
        _require_sql_success(
            self.env.manage_instance("set_config", "nofile", str(self.safe_nofile_limit)),
            "restore safe PostgreSQL nofile limit",
        )
        restart_result = self.env.manage_instance("restart", "postgres")
        restart_payload = _json_response(
            restart_result,
            "restart PostgreSQL after restoring nofile limit",
        )
        if restart_payload.get("status") != "success":
            restart_result = self.env.manage_instance("start", "postgres")
        _require_sql_success(restart_result, "restart PostgreSQL after restoring nofile limit")
        self.env.reconnect()

    def _cleanup_leftovers(self):
        _require_sql_success(
            self.env.execute_sql(f"DROP SCHEMA IF EXISTS {self.schema_name} CASCADE;"),
            f"drop FD exhaustion schema {self.schema_name}",
        )
        if self.control_schema:
            _require_sql_success(
                self.env.execute_sql(f"DROP SCHEMA IF EXISTS {self.control_schema} CASCADE;"),
                f"drop FD exhaustion control schema {self.control_schema}",
            )
        _require_sql_success(
            self.env.execute_sql(f"DROP ROLE IF EXISTS {self.app_role};"),
            f"drop FD exhaustion role {self.app_role}",
        )

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                "SELECT count(*), "
                f"EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{self.app_role}') "
                "FROM information_schema.tables "
                f"WHERE table_schema = '{self.schema_name}' "
                f"AND table_name LIKE '{self.table_prefix}\\_%' ESCAPE '\\';"
            ),
            "verify FD exhaustion fault image",
        )
        expected = [[self.table_count, True]]
        if payload["result"] != expected:
            raise RuntimeError(
                f"FD exhaustion fault image does not match the Case: "
                f"expected={expected}, observed={payload['result']}"
            )
        if self.control_schema:
            stuck_payload = _json_object(
                self.env.execute_sql(
                    "SELECT job_run_id, status FROM "
                    f"{self.control_schema}.export_job_run "
                    f"WHERE job_run_id IN ('{self.stuck_job_run_id}', '{self.stuck_job_run_id_2}') "
                    "ORDER BY job_run_id;"
                ),
                "verify FD exhaustion stuck control runs",
            )
            expected_stuck = sorted(
                [[run_id, "RUNNING"] for run_id in (self.stuck_job_run_id, self.stuck_job_run_id_2)]
            )
            observed = sorted([list(row) for row in stuck_payload["result"]])
            if observed != expected_stuck:
                raise RuntimeError(
                    "FD exhaustion stuck control runs are missing or mutated: "
                    f"expected={expected_stuck}, observed={observed}"
                )

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        nofile_config = env.manage_instance("get_config", "nofile")
        evidence_text = f"{self._failure_error}\n{self._log_excerpt}".lower()
        if "too many open files" not in evidence_text:
            raise RuntimeError(
                "FD exhaustion evidence is missing 'too many open files': "
                f"probe={self._failure_error!r}, log={self._log_excerpt[:500]!r}"
            )
        if str(self.low_nofile_limit) not in str(nofile_config):
            raise RuntimeError(
                f"FD soft limit {self.low_nofile_limit} is not visible: {nofile_config}"
            )
        return {
            "nofile_config": nofile_config,
            "failure_error": self._failure_error,
            "log_excerpt": self._log_excerpt,
        }

    def quiesce(self, context: FaultLifecycleContext):
        """Close runtime connections and restore the snapshot-safe FD limit."""
        print("[FaultInjector:FdExhaustion] quiesce...")
        _run_cleanup_steps(
            f"FD-exhaustion connection cleanup for {context.scenario_id}/{context.case_id}",
            (
                (f"close background connection {index}", conn.close)
                for index, conn in enumerate(self._connections)
            ),
        )
        self._connections = []
        _run_cleanup_steps(
            f"FD-exhaustion persistent session cleanup for {context.scenario_id}/{context.case_id}",
            (
                (f"close persistent session {index}", conn.close)
                for index, conn in enumerate(self._persistent_connections)
            ),
        )
        self._persistent_connections = []
        self._restore_safe_limit()

    def recover(self, context: FaultLifecycleContext):
        print("[FaultInjector:FdExhaustion] Recovering...")
        _run_cleanup_steps(
            f"FD-exhaustion connection cleanup for {context.scenario_id}/{context.case_id}",
            (
                (f"close background connection {index}", conn.close)
                for index, conn in enumerate(self._connections)
            ),
        )
        self._connections = []
        _run_cleanup_steps(
            f"FD-exhaustion persistent session cleanup for {context.scenario_id}/{context.case_id}",
            (
                (f"close persistent session {index}", conn.close)
                for index, conn in enumerate(self._persistent_connections)
            ),
        )
        self._persistent_connections = []
        self.env = context.env
        self._restore_safe_limit()
        self._cleanup_leftovers()
        print("[FaultInjector:FdExhaustion] Recovery complete.")

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._verify_persistent_state()
        self._activate_runtime()
        print("[FaultInjector:FdExhaustion] FD exhaustion fault re-activated.")


class PgSystemFailureFdExhaustionScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_fd_exhaustion'
    description = 'Simulates mixed production query and connection failures caused by an exhausted OS file descriptor limit.'
    cases = (
        _PGSYSTEMFAILUREFDEXHAUSTIONSCENARIO_CASE,
        _PGSYSTEMFAILUREFDEXHAUSTIONSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailureFdExhaustionCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureFdExhaustionInjector,
                config={
                    'schema_name': case.schema_name,
                    'table_prefix': case.table_prefix,
                    'table_count': case.table_count,
                    'low_nofile_limit': case.low_nofile_limit,
                    'safe_nofile_limit': case.safe_nofile_limit,
                    'background_connections': case.background_connections,
                    'app_role': case.app_role,
                    'app_password': case.app_password,
                    'app_name_prefix': case.app_name_prefix,
                    'noisy_sources': case.noisy_sources_2,
                    'validation_sql': case.validation_sql,
                    'failure_probe_timeout_seconds': case.failure_probe_timeout_seconds,
                    'production_noise': case.production_noise,
                    'control_schema': case.control_schema,
                    'stuck_job_run_id': case.stuck_job_run_id,
                    'stuck_job_run_id_2': case.stuck_job_run_id_2,
                    'protected_job_run_id': case.protected_job_run_id,
                    'stuck_job_family': case.stuck_job_family,
                    'healthy_job_family': case.healthy_job_family,
                    'stuck_job_notes': case.stuck_job_notes,
                    'persistent_sessions': case.persistent_sessions,
                    'refresh_result_rows': case.refresh_result_rows,
                    'noise_log_lines': case.noise_log_lines,
                },
            ),
        )
