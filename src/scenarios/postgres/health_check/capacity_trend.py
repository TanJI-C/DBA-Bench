from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.health_check import (
    PgHealthCheckBackupRecoverabilityForMissingWalRecoveryGapEvaluatorCase,
    PgHealthCheckCapacityTrendForSalesEventStorageGrowthEvaluatorCase,
    PgHealthCheckConfigDriftForMemoryResizeConfigDriftEvaluatorCase,
    PgHealthCheckLongRunningTxForCheckoutPoolIdleTransactionEvaluatorCase,
    PgHealthCheckSequenceExhaustionForBillingCanaryInt4SequenceExhaustionEvaluatorCase,
    PgHealthCheckTableBloatForStoreReturnsTableIndexBloatEvaluatorCase,
    PgHealthCheckUnusedIndexesForCustomerRedundantIndexesEvaluatorCase,
    PgHealthCheckBackupRecoverabilityForSingleMissingWalGapSimpleEvaluatorCase,
    PgHealthCheckCapacityTrendForArchiveGrowthForecastSimpleEvaluatorCase,
    PgHealthCheckConfigDriftForCacheBaselineDriftSimpleEvaluatorCase,
    PgHealthCheckLongRunningTxForSingleIdleTransactionCleanupSimpleEvaluatorCase,
    PgHealthCheckSequenceExhaustionForBillingSequenceCapacityRiskSimpleEvaluatorCase,
    PgHealthCheckTableBloatForStoreReturnsBloatSimpleEvaluatorCase,
    PgHealthCheckUnusedIndexesForCustomerUnusedIndexSimpleEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from ...base import (
    DifficultyCalibration,
    PostgresCaseRuntime,
    PostgresScenario,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    CaseResourceSpec,
    PostgresScenarioCase,
)


POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)

CONFIG_DRIFT_POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=65536,
    container_cpu_limit=1.0,
    container_memory_mb=65536,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckCapacityTrendCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    sample_table: str
    review_table: str
    target_table: str
    review_key: str
    total_mb: float
    daily_growth_mb: float
    expected_days_to_full: float
    history_days: int = 30
    finding_ids: tuple[str, ...] = ()
    target_rows: int = 5000

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckCapacityTrendForSalesEventStorageGrowthScenarioCase(PgHealthCheckCapacityTrendCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckCapacityTrendForArchiveGrowthForecastSimpleScenarioCase(PgHealthCheckCapacityTrendCase):
    pass

_PGHEALTHCHECKCAPACITYTRENDSCENARIO_CASE = PgHealthCheckCapacityTrendForSalesEventStorageGrowthScenarioCase(
    case_id='sales_event_storage_growth',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "storage growth is 26mb per day",
                    "entity": "sales_event_storage_growth",
                    "evidence": [
                        "scripted diagnostic actions observed storage growth is 26mb per day"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "sales event history is primary growth source",
                    "entity": "sales_event_storage_growth",
                    "evidence": [
                        "scripted diagnostic actions observed sales event history is primary growth source"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "about 8 days to full",
                    "entity": "sales_event_storage_growth",
                    "evidence": [
                        "scripted diagnostic actions observed about 8 days to full"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "expand capacity and archive partitioned history",
                    "entity": "sales_event_storage_growth",
                    "evidence": [
                        "scripted diagnostic actions observed expand capacity and archive partitioned history"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "applied the case-specific remediation"
            ],
            "verification": [
                "verified the case-specific final state"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgHealthCheckCapacityTrendForSalesEventStorageGrowthEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates a routine capacity-planning health check using one month of disk usage snapshots.',
    alert="[INFO] [PostgreSQL/Primary] Scheduled weekly health-check completed for the primary database. One item remains open in the routine review queue; current live metrics alone are not enough for sign-off. Use the job's stored records and close the row in place if follow-up action is required before the next planning window.",
    initial_state={'status': 'capacity_risk',
 'history_window_days': 30,
 'disk_growth': 'mixed_long_term_trend_with_transient_spikes',
 'review': 'open'},
    expected_target={'status': 'reported',
 'days_to_full': 'about 8.0',
 'primary_growth_source': 'sales_event_history',
 'recommendation': 'expand capacity and archive partitioned sales event history after separating transient noise'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    sample_table='ops_job_samples',
    review_table='ops_review_queue',
    target_table='sales_event_history',
    review_key='primary-weekly-2026w28',
    total_mb=2048.0,
    daily_growth_mb=26.0,
    expected_days_to_full=8.0,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.366667,
        reference_run_ids=(
            "reference-62__pg_health_check_capacity_trend__"
            "sales_event_storage_growth__mock__r001",
        ),
    ),
)

_PGHEALTHCHECKCAPACITYTREND_SIMPLE_CASE = PgHealthCheckCapacityTrendForArchiveGrowthForecastSimpleScenarioCase(
    case_id='archive_growth_forecast_simple',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "persistent storage growth measured",
                    "entity": "archive_growth_forecast_simple",
                    "evidence": [
                        "scripted diagnostic actions observed persistent storage growth measured"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "archive event history is primary growth source",
                    "entity": "archive_growth_forecast_simple",
                    "evidence": [
                        "scripted diagnostic actions observed archive event history is primary growth source"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "capacity exhaustion window forecast",
                    "entity": "archive_growth_forecast_simple",
                    "evidence": [
                        "scripted diagnostic actions observed capacity exhaustion window forecast"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "expand capacity and archive old event partitions",
                    "entity": "archive_growth_forecast_simple",
                    "evidence": [
                        "scripted diagnostic actions observed expand capacity and archive old event partitions"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "applied the case-specific remediation"
            ],
            "verification": [
                "verified the case-specific final state"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=1,
    evaluator=PgHealthCheckCapacityTrendForArchiveGrowthForecastSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='A two-week capacity review with one persistent archive source and two deterministic comparison findings.',
    alert='[Weekly Capacity Review] A storage follow-up remains open. Use the stored review samples to distinguish persistent growth from short-lived activity, forecast the remaining window, and close the review with a safe capacity and retention plan.',
    initial_state={'status': 'capacity_risk', 'history_window_days': 14, 'review': 'open'},
    expected_target={'status': 'reported', 'primary_growth_source': 'archive_event_history', 'recommendation': 'expand capacity and archive old partitions'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    sample_table='ops_archive_samples',
    review_table='ops_archive_review',
    target_table='archive_event_history',
    review_key='archive-weekly-2026w30',
    total_mb=1024.0,
    daily_growth_mb=20.0,
    expected_days_to_full=10.4,
    history_days=14,
    finding_ids=('rel_sales_event_history', 'idx_sales_event_history', 'probe_prometheus_pg_exporter'),
    target_rows=1200,
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.5,
        reference_run_ids=('run_pg_health_check_capacity_trend_archive_growth_forecast_simple_MockLLMAgent',),
    ),
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

class PgHealthCheckCapacityTrendInjector(BaseFaultInjector):
    """
    模拟容量趋势巡检场景。
    创建真实数据库表保存一个月巡检记录和待关闭复核项，要求 Agent 基于记录
    做趋势预测后写回复核队列。
    """

    def __init__(self):
        self.env = None
        self.sample_table = "ops_job_samples"
        self.review_table = "ops_review_queue"
        self.target_table = "sales_event_history"
        self.review_key = "primary-weekly-2026w28"
        self.total_mb = 2048.0
        self.daily_growth_mb = 26.0

    def install(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        print("[FaultInjector:PgHealthCheckCapacityTrendInjector] "
              "Injecting noisy production capacity samples...")
        with self.env.metrics_hidden():
            self.recover(context)
            self._create_space_consumer_table()
            self._create_sample_and_review_tables()
            self._seed_capacity_history()
            self.env.execute_sql(f"ANALYZE {self.sample_table};")
            self.env.execute_sql(f"ANALYZE {self.target_table};")
        self._verify_persistent_state()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.sample_table = _validate_sql_identifier(config['sample_table'], "sample_table")
        self.review_table = _validate_sql_identifier(config['review_table'], "review_table")
        self.target_table = _validate_sql_identifier(config['target_table'], "target_table")
        self.review_key = str(config['review_key'])
        self.total_mb = float(config['total_mb'])
        self.daily_growth_mb = float(config['daily_growth_mb'])
        self.history_days = int(config.get('history_days', 30))
        self.finding_ids = tuple(config.get('finding_ids', ()))
        self.target_rows = int(config.get('target_rows', 5000))

    def _review_key_sql(self) -> str:
        return self.review_key.replace("'", "''")

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT "
                f"(SELECT count(*) FROM {self.sample_table} WHERE record_type = 'storage_sample'), "
                f"(SELECT count(*) FROM {self.sample_table} WHERE record_type <> 'storage_sample'), "
                f"(SELECT count(*) FROM {self.review_table} WHERE check_key = '{self._review_key_sql()}' AND status = 'open'), "
                f"(SELECT count(*) FROM {self.target_table}), "
                f"(SELECT min(total_mb) FROM {self.sample_table} WHERE record_type = 'storage_sample'), "
                f"(SELECT max(total_mb) FROM {self.sample_table} WHERE record_type = 'storage_sample');"
            ),
            "verify capacity-trend fault image",
        )
        samples, findings, open_reviews, target_rows, min_total, max_total = payload["result"][0]
        if (
            int(samples) != self.history_days
            or int(findings) != (len(self.finding_ids) if self.finding_ids else 8)
            or int(open_reviews) != 1
            or int(target_rows) != self.target_rows
            or float(min_total) != self.total_mb
            or float(max_total) != self.total_mb
        ):
            raise RuntimeError(
                f"Capacity-trend fault image does not match the Case: "
                f"samples={samples}, findings={findings}, open_reviews={open_reviews}, "
                f"target_rows={target_rows}, total_range=({min_total}, {max_total}), "
                f"expected_total={self.total_mb}"
            )

    def _create_space_consumer_table(self):
        self.env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {self.target_table} (
                id bigint PRIMARY KEY,
                created_at timestamptz NOT NULL,
                payload text NOT NULL
            );
        """)
        self.env.execute_sql(f"TRUNCATE {self.target_table};")
        self.env.execute_sql(f"""
            INSERT INTO {self.target_table} (id, created_at, payload)
            SELECT gs,
                   NOW() - (gs % 45) * INTERVAL '1 day',
                   repeat(md5(gs::text), 8)
            FROM generate_series(1, {self.target_rows}) AS gs;
        """)

    def _create_sample_and_review_tables(self):
        self.env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {self.sample_table} (
                record_id text PRIMARY KEY,
                check_key text NOT NULL,
                record_type text NOT NULL,
                observed_at timestamptz NOT NULL,
                subject text NOT NULL,
                used_mb numeric(12, 2),
                total_mb numeric(12, 2),
                persistent_mb numeric(12, 2),
                database_mb numeric(12, 2),
                index_mb numeric(12, 2),
                archive_mb numeric(12, 2),
                pg_wal_mb numeric(12, 2),
                temp_mb numeric(12, 2),
                reporting_batch_mb numeric(12, 2),
                backup_residue_mb numeric(12, 2),
                maintenance_reclaimed_mb numeric(12, 2),
                current_mb numeric(12, 2),
                thirty_day_growth_mb numeric(12, 2),
                trend_mb_per_day numeric(12, 2),
                reclaimable_mb numeric(12, 2),
                persistent_capacity_risk boolean,
                note text NOT NULL
            );
        """)
        self.env.execute_sql(f"TRUNCATE {self.sample_table};")
        self.env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {self.review_table} (
                check_key text PRIMARY KEY CHECK (check_key = '{self._review_key_sql()}'),
                status text NOT NULL CHECK (status IN ('open', 'closed')),
                opened_at timestamptz NOT NULL DEFAULT NOW(),
                closed_at timestamptz,
                measured_change_mb_per_day numeric(12, 2) NOT NULL,
                risk_window_days numeric(12, 2) NOT NULL,
                confidence_score numeric(8, 4) NOT NULL,
                risk_source text NOT NULL,
                dismissed_signals text NOT NULL,
                action_plan text NOT NULL
            );
        """)
        self.env.execute_sql(f"TRUNCATE {self.review_table};")
        self.env.execute_sql(f"""
            INSERT INTO {self.review_table}
                (check_key, status, measured_change_mb_per_day, risk_window_days,
                 confidence_score, risk_source, dismissed_signals, action_plan)
            VALUES ('{self._review_key_sql()}', 'open', 0, 0, 0, '', '', '');
        """)

    def _seed_capacity_history(self):
        last_day = self.history_days - 1
        start_mb = self.total_mb - (self.daily_growth_mb * last_day) - 208.0
        self.env.execute_sql(f"""
            INSERT INTO {self.sample_table}
                (record_id, check_key, record_type, observed_at, subject,
                 used_mb, total_mb, persistent_mb, database_mb, index_mb,
                 archive_mb, pg_wal_mb, temp_mb, reporting_batch_mb,
                 backup_residue_mb, maintenance_reclaimed_mb, note)
            WITH samples AS (
                SELECT
                    day_no,
                    ({start_mb} + day_no * {self.daily_growth_mb})::numeric AS persistent_mb,
                    CASE WHEN day_no IN (8, 16, 24) THEN 110 ELSE 12 + (day_no % 3) * 3 END AS temp_mb,
                    CASE WHEN day_no IN (7, 8, 9, 21, 22) THEN 95 ELSE 0 END AS reporting_batch_mb,
                    CASE WHEN day_no BETWEEN 18 AND 23 THEN 170 WHEN day_no = 24 THEN 55 ELSE 18 END AS backup_residue_mb,
                    CASE WHEN day_no IN (12, 13) THEN 135 ELSE 62 + (day_no % 4) * 2 END AS pg_wal_mb,
                    CASE WHEN day_no = 24 THEN 115 ELSE 0 END AS maintenance_reclaimed_mb
                FROM generate_series(0, {last_day}) AS day_no
            )
            SELECT
                'sample_' || lpad(day_no::text, 2, '0'),
                '{self._review_key_sql()}',
                'storage_sample',
                (CURRENT_DATE - ({last_day} - day_no) * INTERVAL '1 day')::timestamptz,
                'primary-db',
                round((persistent_mb + temp_mb + reporting_batch_mb + backup_residue_mb
                       + greatest(pg_wal_mb - 70, 0) - maintenance_reclaimed_mb)::numeric, 2),
                {self.total_mb}::numeric,
                round(persistent_mb, 2),
                round((620 + day_no * 19)::numeric, 2),
                round((142 + day_no * 2)::numeric, 2),
                round((260 + day_no * 5)::numeric, 2),
                round(pg_wal_mb::numeric, 2),
                round(temp_mb::numeric, 2),
                round(reporting_batch_mb::numeric, 2),
                round(backup_residue_mb::numeric, 2),
                round(maintenance_reclaimed_mb::numeric, 2),
                CASE
                    WHEN day_no IN (8, 16, 24) THEN 'reporting temp-file peak'
                    WHEN day_no BETWEEN 18 AND 23 THEN 'validated backup residue awaiting cleanup'
                    WHEN day_no IN (12, 13) THEN 'WAL/checkpoint burst'
                    WHEN day_no = 24 THEN 'routine archive cleanup reclaimed space'
                    ELSE 'normal monitor sample'
                END
            FROM samples;
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.sample_table}
                (record_id, check_key, record_type, observed_at, subject, current_mb,
                 thirty_day_growth_mb, trend_mb_per_day, reclaimable_mb,
                 persistent_capacity_risk, note)
            VALUES
                ('rel_sales_event_history', '{self._review_key_sql()}', 'relation_growth', NOW() - INTERVAL '1 day',
                 '{self.target_table}', 1171, 551, 19, 430, true,
                 'older event partitions are archive candidates'),
                ('rel_customer_audit_events', '{self._review_key_sql()}', 'relation_growth', NOW() - INTERVAL '1 day',
                 'customer_audit_events', 454, 174, 6, 35, true,
                 'regulated audit data grows steadily with limited short-term reclaim'),
                ('idx_sales_event_history', '{self._review_key_sql()}', 'index_growth', NOW() - INTERVAL '1 day',
                 'sales_event_history_idx', 200, 58, 2, 20, true,
                 'index growth follows sales_event_history'),
                ('batch_regional_sales', '{self._review_key_sql()}', 'batch_activity', NOW() - INTERVAL '21 days',
                 'regional_sales_report', 24, 0, 0, 0, false,
                 'temporary files and reporting batch samples clear after completion'),
                ('sql_monthly_revenue_rollup', '{self._review_key_sql()}', 'historical_sql', NOW() - INTERVAL '18 days',
                 'monthly_revenue_rollup', 0, 0, 0, 0, false,
                 'slow SQL in history; no sustained relation growth after completion'),
                ('probe_prometheus_pg_exporter', '{self._review_key_sql()}', 'monitoring_probe', NOW() - INTERVAL '7 days',
                 'prometheus_pg_exporter', 0, 0, 0, 0, false,
                 'regular metadata probes and short connections'),
                ('backup_verify_residue', '{self._review_key_sql()}', 'backup_residue', NOW() - INTERVAL '5 days',
                 'pgbackrest_verify', 55, 0, 0, 55, false,
                 'validated backup residue appears then is reclaimed by routine cleanup'),
                ('wal_checkpoint_burst', '{self._review_key_sql()}', 'wal_burst', NOW() - INTERVAL '16 days',
                 'pg_wal', 68, 0, 0, 0, false,
                 'short WAL/checkpoint burst, not a month-long trend');
        """)
        if self.finding_ids:
            keep = ", ".join("'" + item.replace("'", "''") + "'" for item in self.finding_ids)
            self.env.execute_sql(
                f"DELETE FROM {self.sample_table} WHERE record_type <> 'storage_sample' "
                f"AND record_id NOT IN ({keep});"
            )

    def prepare_observability(self, context: FaultLifecycleContext):
        return {}

    def quiesce(self, context: FaultLifecycleContext):
        """No background threads or runtime resources to clean up."""
        pass

    def recover(self, context: FaultLifecycleContext):
        print("[FaultInjector:PgHealthCheckCapacityTrendInjector] Recovering...")
        self._configure(context.config, context.env)
        self.env.reconnect()
        for table in (self.review_table, self.sample_table, self.target_table):
            _require_sql_success(
                self.env.execute_sql(f"DROP TABLE IF EXISTS {table};"),
                f"drop capacity-trend table {table}",
            )
        print("[FaultInjector:PgHealthCheckCapacityTrendInjector] Recovery complete.")

    def activate(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        self._verify_persistent_state()


class PgHealthCheckCapacityTrendScenario(PostgresScenario):
    scenario_id = 'pg_health_check_capacity_trend'
    description = 'Simulates a routine capacity-planning health check using one month of disk usage snapshots.'
    cases = (_PGHEALTHCHECKCAPACITYTRENDSCENARIO_CASE, _PGHEALTHCHECKCAPACITYTREND_SIMPLE_CASE)

    def build_fault_plan(self, case: PgHealthCheckCapacityTrendCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgHealthCheckCapacityTrendInjector,
                config={
                    'sample_table': case.sample_table,
                    'review_table': case.review_table,
                    'target_table': case.target_table,
                    'review_key': case.review_key,
                    'total_mb': case.total_mb,
                    'daily_growth_mb': case.daily_growth_mb,
                    'history_days': case.history_days,
                    'finding_ids': case.finding_ids,
                    'target_rows': case.target_rows,
                },
            ),
        )
