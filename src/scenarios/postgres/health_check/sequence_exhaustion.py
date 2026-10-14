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
from src.scenarios.base import DifficultyCalibration, PostgresScenario, FaultPlan, PostgresScenarioCase
from src.workloads.specs import EMPTY_BACKGROUND_WORKLOAD
from src.execution.specs import PostgresCaseRuntime, CaseResourceSpec


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
class PgHealthCheckSequenceExhaustionCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    table_name: str
    sequence_name: str
    column_name: str
    compare_table: str
    bigint_noise_table: str
    identity_noise_table: str
    unowned_sequence_name: str
    target_value: int
    int4_max_value: int
    remaining_values: int
    usage_percent: float
    noise_profile: str = "full"

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckSequenceExhaustionForBillingCanaryInt4SequenceExhaustionScenarioCase(PgHealthCheckSequenceExhaustionCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckSequenceExhaustionForBillingSequenceCapacityRiskSimpleScenarioCase(PgHealthCheckSequenceExhaustionCase):
    pass

_PGHEALTHCHECKSEQUENCEEXHAUSTIONSCENARIO_CASE = PgHealthCheckSequenceExhaustionForBillingCanaryInt4SequenceExhaustionScenarioCase(
    case_id='billing_canary_int4_sequence_exhaustion',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "invoice events int4 sequence exhausted",
                    "entity": "billing_canary_int4_sequence_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed invoice events int4 sequence exhausted"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "sequence owned by invoice events event id",
                    "entity": "billing_canary_int4_sequence_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed sequence owned by invoice events event id"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "bigint and identity sequences are safe",
                    "entity": "billing_canary_int4_sequence_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed bigint and identity sequences are safe"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "alter column and sequence to bigint",
                    "entity": "billing_canary_int4_sequence_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed alter column and sequence to bigint"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "alter table access exclusive lock risk",
                    "entity": "billing_canary_int4_sequence_exhaustion",
                    "evidence": [
                        "scripted diagnostic actions observed alter table access exclusive lock risk"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "ALTER TABLE invoice_events ALTER COLUMN event_id TYPE BIGINT; ALTER SEQUENCE invoice_events_event_id_seq AS BIGINT"
            ],
            "verification": [
                "ACCESS EXCLUSIVE risk requires a maintenance window"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgHealthCheckSequenceExhaustionForBillingCanaryInt4SequenceExhaustionEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates a noisy pre-ramp billing canary failure caused by an exhausted INT4 write-path sequence.',
    alert='[Pre-ramp Validation] Overnight billing canary writes reported a small number of insert failures while dashboards, reports, and monitor probes stayed mostly healthy. Review the database evidence, separate the current write-path issue from routine background noise, and submit a safe remediation plan.',
    initial_state={'status': 'canary_write_failures',
 'table': 'invoice_events',
 'sequence': 'invoice_events_event_id_seq',
 'last_value': 2147483647,
 'column_type': 'integer'},
    expected_target={'status': 'remediated_or_planned',
 'table': 'invoice_events',
 'sequence': 'invoice_events_event_id_seq',
 'recommendation': 'ALTER TABLE ... ALTER COLUMN ... TYPE BIGINT with lock-risk notes'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    table_name='invoice_events',
    sequence_name='invoice_events_event_id_seq',
    column_name='event_id',
    compare_table='audit_log_entries',
    bigint_noise_table='ledger_batches',
    identity_noise_table='customer_export_jobs',
    unowned_sequence_name='legacy_order_ticket_seq',
    target_value=2147483647,
    int4_max_value=2147483647,
    remaining_values=0,
    usage_percent=100.0,
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.375,
        reference_run_ids=(
            "reference-51__pg_health_check_sequence_exhaustion__"
            "billing_canary_int4_sequence_exhaustion__mock__r001",
        ),
    ),
)

_PGHEALTHCHECKSEQUENCEEXHAUSTION_SIMPLE_CASE = PgHealthCheckSequenceExhaustionForBillingSequenceCapacityRiskSimpleScenarioCase(
    case_id='billing_sequence_capacity_risk_simple', case_no=1,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "billing int4 sequence has no safe headroom",
                    "entity": "billing_sequence_capacity_risk_simple",
                    "evidence": [
                        "scripted diagnostic actions observed billing int4 sequence has no safe headroom"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "sequence belongs to the billing event id integer column",
                    "entity": "billing_sequence_capacity_risk_simple",
                    "evidence": [
                        "scripted diagnostic actions observed sequence belongs to the billing event id integer column"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "bigint sequence is not at risk",
                    "entity": "billing_sequence_capacity_risk_simple",
                    "evidence": [
                        "scripted diagnostic actions observed bigint sequence is not at risk"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "alter the column and sequence to bigint",
                    "entity": "billing_sequence_capacity_risk_simple",
                    "evidence": [
                        "scripted diagnostic actions observed alter the column and sequence to bigint"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "alter table requires a maintenance window",
                    "entity": "billing_sequence_capacity_risk_simple",
                    "evidence": [
                        "scripted diagnostic actions observed alter table requires a maintenance window"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "ALTER TABLE billing_events ALTER COLUMN event_id TYPE BIGINT; ALTER SEQUENCE billing_events_event_id_seq AS BIGINT"
            ],
            "verification": [
                "ACCESS EXCLUSIVE risk requires a maintenance window"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    evaluator=PgHealthCheckSequenceExhaustionForBillingSequenceCapacityRiskSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest', workload_tag='initialized',
    title='A billing write-path sequence at the INT4 ceiling with one high-value BIGINT comparison sequence.',
    alert='[Pre-ramp Capacity Review] A billing canary write failed while general database checks remained healthy. Identify the capacity-limited database object, bind it to its owning column, exclude the comparison object, and submit a safe migration plan.',
    initial_state={'status': 'canary_write_failures', 'table': 'billing_events', 'column_type': 'integer'},
    expected_target={'status': 'remediated_or_planned', 'recommendation': 'migrate the owning column and sequence to BIGINT'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    table_name='billing_events', sequence_name='billing_events_event_id_seq', column_name='event_id',
    compare_table='billing_audit_entries', bigint_noise_table='billing_ledger_batches',
    identity_noise_table='billing_export_jobs', unowned_sequence_name='billing_legacy_ticket_seq',
    target_value=2147483647, int4_max_value=2147483647, remaining_values=0, usage_percent=100.0,
    noise_profile='simple',
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.571429,
        reference_run_ids=('run_pg_health_check_sequence_exhaustion_billing_sequence_capacity_risk_simple_MockLLMAgent',),
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

class PgHealthCheckSequenceExhaustionInjector(BaseFaultInjector):
    """
    模拟一次被巡检噪声淹没的写入路径容量风险。
    """

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print("[FaultInjector:PgHealthCheckSequenceExhaustionInjector] Installing noisy canary-write capacity fault...")

        self._drop_objects()
        self._create_target_table()
        self._create_sequence_noise()
        if self.noise_profile == "full":
            self._create_background_noise_tables()
            self._emit_visible_log_noise(120, "before")
            self._emit_error_noise("before")
        else:
            self._emit_visible_log_noise(8, "before")
        self._trigger_canary_failure()
        if self.noise_profile == "full":
            self._emit_error_noise("after")
            self._emit_visible_log_noise(80, "after")
        else:
            self._emit_visible_log_noise(4, "after")

        self._assert_fault_observable()

        print("[FaultInjector:PgHealthCheckSequenceExhaustionInjector] Fault installation complete.")

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table_name = _validate_sql_identifier(config["table_name"], "table_name")
        self.sequence_name = _validate_sql_identifier(config["sequence_name"], "sequence_name")
        self.column_name = _validate_sql_identifier(config["column_name"], "column_name")
        self.target_value = int(config["target_value"])
        self.compare_table = _validate_sql_identifier(config["compare_table"], "compare_table")
        self.bigint_noise_table = _validate_sql_identifier(config["bigint_noise_table"], "bigint_noise_table")
        self.identity_noise_table = _validate_sql_identifier(config["identity_noise_table"], "identity_noise_table")
        self.unowned_sequence_name = _validate_sql_identifier(config["unowned_sequence_name"], "unowned_sequence_name")
        self.noise_profile = str(config.get("noise_profile", "full"))
        self.compare_sequence = f"{self.compare_table}_audit_id_seq"
        self.bigint_noise_sequence = f"{self.bigint_noise_table}_batch_id_seq"

    def _drop_objects(self):
        for table in (
            self.table_name,
            self.compare_table,
            self.bigint_noise_table,
            self.identity_noise_table,
            "report_refresh_runs",
            "monitoring_probe_samples",
            "etl_slow_sql_history",
        ):
            _require_sql_success(
                self.env.execute_sql(f"DROP TABLE IF EXISTS {table} CASCADE;"),
                f"drop sequence-exhaustion table {table}",
            )
        _require_sql_success(
            self.env.execute_sql(f"DROP SEQUENCE IF EXISTS {self.unowned_sequence_name};"),
            f"drop sequence-exhaustion unowned sequence {self.unowned_sequence_name}",
        )

    def _create_target_table(self):
        _require_sql_success(
            self.env.execute_sql(f"""
                CREATE TABLE {self.table_name} (
                    {self.column_name} SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
                INSERT INTO {self.table_name} (tenant_id, event_type, payload)
                VALUES
                    (7, 'invoice.created', 'historic invoice write'),
                    (8, 'invoice.adjusted', 'historic invoice adjustment');
                SELECT setval('{self.sequence_name}', {self.target_value}, true);
            """),
            "create target invoice event table",
        )

    def _create_sequence_noise(self):
        if self.noise_profile == "simple":
            _require_sql_success(
                self.env.execute_sql(f"""
                    CREATE TABLE {self.bigint_noise_table} (
                        batch_id BIGSERIAL PRIMARY KEY,
                        ledger_date DATE NOT NULL,
                        state TEXT NOT NULL
                    );
                    INSERT INTO {self.bigint_noise_table} (ledger_date, state)
                    VALUES (CURRENT_DATE, 'open');
                    SELECT setval('{self.bigint_noise_sequence}', 6500000000, true);
                """),
                "create simplified sequence distractor",
            )
            return
        _require_sql_success(
            self.env.execute_sql(f"""
                CREATE TABLE {self.compare_table} (
                    audit_id SERIAL PRIMARY KEY,
                    source_name TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
                INSERT INTO {self.compare_table} (source_name, detail)
                SELECT 'routine-audit', 'historical audit row ' || g
                FROM generate_series(1, 20) AS g;
                SELECT setval('{self.compare_sequence}', 1900000000, true);

                CREATE TABLE {self.bigint_noise_table} (
                    batch_id BIGSERIAL PRIMARY KEY,
                    ledger_date DATE NOT NULL,
                    state TEXT NOT NULL
                );
                INSERT INTO {self.bigint_noise_table} (ledger_date, state)
                VALUES (CURRENT_DATE - 1, 'closed'), (CURRENT_DATE, 'open');
                SELECT setval('{self.bigint_noise_sequence}', 6500000000, true);

                CREATE TABLE {self.identity_noise_table} (
                    job_id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    export_name TEXT NOT NULL,
                    status TEXT NOT NULL
                );
                INSERT INTO {self.identity_noise_table} (export_name, status)
                VALUES ('customer-daily', 'done'), ('customer-weekly', 'queued');
                SELECT setval(pg_get_serial_sequence('{self.identity_noise_table}', 'job_id')::regclass, 80000, true);

                CREATE SEQUENCE {self.unowned_sequence_name} AS integer;
                SELECT setval('{self.unowned_sequence_name}', 2147460000, true);
            """),
            "create sequence distractors",
        )

    def _create_background_noise_tables(self):
        _require_sql_success(
            self.env.execute_sql("""
                CREATE TABLE report_refresh_runs (
                    run_id BIGSERIAL PRIMARY KEY,
                    report_name TEXT NOT NULL,
                    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    duration_ms INTEGER NOT NULL
                );
                INSERT INTO report_refresh_runs (report_name, duration_ms)
                SELECT 'finance_rollup_' || (g % 9), 800 + (g % 5000)
                FROM generate_series(1, 180) AS g;

                CREATE TABLE monitoring_probe_samples (
                    sample_id INTEGER PRIMARY KEY,
                    probe_name TEXT NOT NULL,
                    ok BOOLEAN NOT NULL,
                    sampled_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
                INSERT INTO monitoring_probe_samples (sample_id, probe_name, ok)
                SELECT g, 'primary-health-' || (g % 13), (g % 17) <> 0
                FROM generate_series(1, 260) AS g;

                CREATE TABLE etl_slow_sql_history (
                    history_id BIGSERIAL PRIMARY KEY,
                    query_label TEXT NOT NULL,
                    mean_ms INTEGER NOT NULL,
                    captured_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
                INSERT INTO etl_slow_sql_history (query_label, mean_ms)
                SELECT 'nightly_etl_' || (g % 7), 1200 + (g % 9000)
                FROM generate_series(1, 120) AS g;
            """),
            "create sequence-exhaustion background noise tables",
        )

    def _emit_visible_log_noise(self, count: int, phase: str):
        _require_sql_success(
            self.env.execute_sql(f"""
                DO $$
                DECLARE
                    i integer;
                BEGIN
                    FOR i IN 1..{count} LOOP
                        RAISE WARNING 'pre-ramp {phase} log noise %: report_refresh=% monitor_probe=% checkpoint_sample=%',
                            i, i % 11, i % 17, i % 23;
                    END LOOP;
                END $$;
            """),
            f"emit {phase} warning log noise",
        )

    def _emit_error_noise(self, phase: str):
        cases = {
            "before": (
                ("report_refresh_worker", "SELECT 1 / 0;", "division by zero"),
                ("monitoring_probe", "SELECT count(*) FROM monitoring_probe_samples_202401_missing;", "does not exist"),
                ("etl_loader", "SELECT '2026-02-31'::date;", "out of range"),
            ),
            "after": (
                ("staging_dedupe", "INSERT INTO monitoring_probe_samples(sample_id, probe_name, ok) VALUES (1, 'duplicate-smoke', true);", "duplicate key"),
                ("report_timeout_probe", "SELECT pg_sleep('report-timeout');", "double precision"),
                ("json_payload_sampler", "SELECT '{broken-json'::jsonb;", "invalid input syntax"),
            ),
        }[phase]
        for app_name, sql, expected in cases:
            self._expect_sql_error(
                f"SET application_name = '{app_name}'; {sql}",
                expected,
                f"emit {phase} error noise for {app_name}",
            )

    def _trigger_canary_failure(self):
        _require_sql_success(
            self.env.execute_sql("DO $$ BEGIN RAISE WARNING 'billing canary write entering validation path'; END $$;"),
            "emit billing canary warning",
        )
        self._expect_sql_error(
            f"""
            SET application_name = 'billing_canary_pre_ramp';
            INSERT INTO {self.table_name} (tenant_id, event_type, payload)
            VALUES (42, 'invoice.canary', 'pre-ramp validation write');
            """,
            "reached maximum value of sequence",
            "trigger billing canary sequence failure",
        )

    def _expect_sql_error(self, sql: str, expected_fragment: str, context: str):
        raw = self.env.execute_sql(sql)
        payload = json.loads(raw) if isinstance(raw, str) else raw
        if payload.get("status") != "error" or expected_fragment.lower() not in str(payload).lower():
            raise RuntimeError(f"{context} did not produce expected error {expected_fragment!r}: {raw}")

    def _assert_fault_observable(self):
        raw = self.env.execute_sql(f"""
            SET statement_timeout = '5s';
            WITH sequence_inventory AS (
                SELECT
                    seq.relname AS sequence_name,
                    tbl.relname AS table_name,
                    col.attname AS column_name,
                    typ.typname AS data_type,
                    ps.last_value,
                    dep.deptype
                FROM pg_class seq
                JOIN pg_namespace ns ON ns.oid = seq.relnamespace
                JOIN pg_sequence pseq ON pseq.seqrelid = seq.oid
                JOIN pg_sequences ps
                  ON ps.schemaname = ns.nspname
                 AND ps.sequencename = seq.relname
                LEFT JOIN pg_depend dep
                  ON dep.objid = seq.oid
                 AND dep.deptype IN ('a', 'i')
                LEFT JOIN pg_class tbl ON tbl.oid = dep.refobjid
                LEFT JOIN pg_attribute col
                  ON col.attrelid = tbl.oid
                 AND col.attnum = dep.refobjsubid
                LEFT JOIN pg_type typ ON typ.oid = col.atttypid
                WHERE seq.relkind = 'S'
                  AND ns.nspname = 'public'
            )
            SELECT sequence_name, table_name, column_name, data_type, last_value, deptype
            FROM sequence_inventory
            WHERE sequence_name IN (
                '{self.sequence_name}',
                '{self.compare_sequence}',
                '{self.bigint_noise_sequence}',
                '{self.unowned_sequence_name}'
            )
            ORDER BY sequence_name;
        """)
        payload = json.loads(raw) if isinstance(raw, str) else raw
        if payload.get("status") != "success":
            raise RuntimeError(f"Could not query sequence state after injection: {raw}")
        rows = payload.get("result", [])
        by_seq = {row[0]: row for row in rows}
        target = by_seq.get(self.sequence_name)
        if not target:
            raise RuntimeError(f"Target sequence not visible after injection: {raw}")
        if target[1] != self.table_name or target[2] != self.column_name:
            raise RuntimeError(f"Target sequence ownership mismatch after injection: {raw}")
        if str(target[3]).lower() not in ("integer", "int4"):
            raise RuntimeError(f"Target sequence is not owned by an INT4 column: {raw}")
        if int(target[4] or 0) != self.target_value:
            raise RuntimeError(f"Target sequence value mismatch after injection: {raw}")
        bigint = by_seq.get(self.bigint_noise_sequence)
        if not bigint or str(bigint[3]).lower() not in ("bigint", "int8") or int(bigint[4] or 0) <= 2147483647:
            raise RuntimeError(f"BIGINT high-value distractor is not observable: {raw}")
        if self.noise_profile == "full":
            legacy = by_seq.get(self.unowned_sequence_name)
            if not legacy or legacy[1] is not None or int(legacy[4] or 0) < 2000000000:
                raise RuntimeError(f"Unowned high-value sequence distractor is not observable: {raw}")

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {}

    def quiesce(self, context: FaultLifecycleContext):
        """No background threads or runtime resources to clean up."""
        pass

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        print("[FaultInjector:PgHealthCheckSequenceExhaustionInjector] Recovering...")
        self._drop_objects()
        print("[FaultInjector:PgHealthCheckSequenceExhaustionInjector] Recovery complete.")

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._assert_fault_observable()


class PgHealthCheckSequenceExhaustionScenario(PostgresScenario):
    scenario_id = 'pg_health_check_sequence_exhaustion'
    description = 'Simulates sequence exhaustion by pushing INT4 serial sequence near its maximum value.'
    cases = (_PGHEALTHCHECKSEQUENCEEXHAUSTIONSCENARIO_CASE, _PGHEALTHCHECKSEQUENCEEXHAUSTION_SIMPLE_CASE)

    def build_fault_plan(self, case: PgHealthCheckSequenceExhaustionCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgHealthCheckSequenceExhaustionInjector,
                config={
                    'table_name': case.table_name,
                    'sequence_name': case.sequence_name,
                    'column_name': case.column_name,
                    'target_value': case.target_value,
                    'compare_table': case.compare_table,
                    'bigint_noise_table': case.bigint_noise_table,
                    'identity_noise_table': case.identity_noise_table,
                    'unowned_sequence_name': case.unowned_sequence_name,
                    'noise_profile': case.noise_profile,
                },
            ),
        )
