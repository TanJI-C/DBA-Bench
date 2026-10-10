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
class WalSlotRegistryRow:
    slot_name: str
    purpose: str
    ack_minutes_ago: int


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureWalAccumulationCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    slot_name: str
    stale_slot_names: tuple[str, ...]
    fresh_slot_names: tuple[str, ...]
    retained_slot_names: tuple[str, ...]
    short_retention_slot_names: tuple[str, ...]
    unreserved_slot_names: tuple[str, ...]
    registry_rows: tuple[WalSlotRegistryRow, ...]
    production_noise: bool

    @property
    def scenario_slot_names(self) -> tuple[str, ...]:
        return self.stale_slot_names + self.fresh_slot_names

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureWalAccumulationForAnalyticsSlotWalRetentionScenarioCase(PgSystemFailureWalAccumulationCase):
    pass

_PGSYSTEMFAILUREWALACCUMULATIONSCENARIO_CASE = PgSystemFailureWalAccumulationForAnalyticsSlotWalRetentionScenarioCase(
    case_id='analytics_slot_wal_retention',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "wal accumulation",
                    "entity": "analytics_slot_wal_retention",
                    "evidence": [
                        "scripted diagnostic actions observed wal accumulation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "analytics backfill slot retains wal",
                    "entity": "analytics_slot_wal_retention",
                    "evidence": [
                        "scripted diagnostic actions observed analytics backfill slot retains wal"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "protected and short retention slots excluded",
                    "entity": "analytics_slot_wal_retention",
                    "evidence": [
                        "scripted diagnostic actions observed protected and short retention slots excluded"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "drop only analytics backfill slot",
                    "entity": "analytics_slot_wal_retention",
                    "evidence": [
                        "scripted diagnostic actions observed drop only analytics backfill slot"
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
    evaluator=PgSystemFailureWalAccumulationForAnalyticsSlotWalRetentionEvaluatorCase,
    runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='Simulates WAL accumulation caused by an abandoned backfill replication slot.',
    alert='[SEV2] [PostgreSQL/Primary] Checkout writes are slower than normal and the primary volume is growing faster than the daily forecast. The billing export pipeline has not acknowledged fresh changes for about 40 minutes. This overlaps with a cancelled analytics backfill, normal checkout traffic, dashboards, monitoring probes, and the nightly backup window. Identify the production-safe cause, avoid disrupting healthy downstream or standby paths, restore normal log cleanup, and verify the storage warning is cleared before submit.',
    initial_state={'status': 'degraded',
 'wal': 'retained_by_abandoned_backfill_slot',
 'decoy_slot': 'present_with_static_and_short_retention_noise'},
    expected_target={'status': 'recovered',
 'wal': 'recycled',
 'dropped_slot': 'analytics_backfill_20240620',
 'preserved_slot': 'cdc_billing_export_20260705'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    slot_name='analytics_backfill_20240620',
    stale_slot_names=('analytics_backfill_20240620',),
    fresh_slot_names=(
        'cdc_billing_export_20260705',
        'standby_warm_archive_a',
        'cdc_orders_stream_20260705',
        'nightly_basebackup_20260706',
        'analytics_backfill_20240618',
        'analytics_backfill_20240619_recent_ack',
        'analytics_backfill_20240621_probe',
        'cdc_billing_recent_ack_20260706',
        'billing_export_slot_replay_probe',
    ),
    retained_slot_names=('analytics_backfill_20240620',),
    short_retention_slot_names=(
        'analytics_backfill_20240619_recent_ack',
        'cdc_billing_recent_ack_20260706',
        'billing_export_slot_replay_probe',
    ),
    unreserved_slot_names=(
        'cdc_billing_export_20260705',
        'standby_warm_archive_a',
        'cdc_orders_stream_20260705',
        'nightly_basebackup_20260706',
        'analytics_backfill_20240618',
        'analytics_backfill_20240621_probe',
    ),
    registry_rows=(
        WalSlotRegistryRow(slot_name='analytics_backfill_20240620', purpose='cancelled analytics backfill batch', ack_minutes_ago=45),
        WalSlotRegistryRow(slot_name='cdc_billing_export_20260705', purpose='billing export CDC path', ack_minutes_ago=2),
        WalSlotRegistryRow(slot_name='standby_warm_archive_a', purpose='warm standby archive feed', ack_minutes_ago=6),
        WalSlotRegistryRow(slot_name='cdc_orders_stream_20260705', purpose='orders CDC stream', ack_minutes_ago=3),
        WalSlotRegistryRow(slot_name='nightly_basebackup_20260706', purpose='nightly basebackup slot', ack_minutes_ago=6),
        WalSlotRegistryRow(slot_name='analytics_backfill_20240618', purpose='prior analytics backfill batch consumer', ack_minutes_ago=8),
        WalSlotRegistryRow(slot_name='analytics_backfill_20240619_recent_ack', purpose='analytics backfill recent consumer', ack_minutes_ago=1),
        WalSlotRegistryRow(slot_name='analytics_backfill_20240621_probe', purpose='analytics backfill probe consumer', ack_minutes_ago=2),
        WalSlotRegistryRow(slot_name='cdc_billing_recent_ack_20260706', purpose='billing CDC recent consumer', ack_minutes_ago=1),
        WalSlotRegistryRow(slot_name='billing_export_slot_replay_probe', purpose='billing export replay probe', ack_minutes_ago=2),
    ),
    production_noise=True,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.425,
        reference_run_ids=(
            "reference-65__pg_system_failure_wal_accumulation__"
            "analytics_slot_wal_retention__mock__r001",
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureWalAccumulationForAbandonedReportSlotWalRetentionSimpleScenarioCase(PgSystemFailureWalAccumulationCase):
    pass

_PGSYSTEMFAILUREWALACCUMULATIONSCENARIO_SIMPLE_CASE = (
    PgSystemFailureWalAccumulationForAbandonedReportSlotWalRetentionSimpleScenarioCase(
        case_id='abandoned_report_slot_wal_retention_simple',
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "wal accumulation",
                        "entity": "abandoned_report_slot_wal_retention_simple",
                        "evidence": [
                            "scripted diagnostic actions observed wal accumulation"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "analytics backfill slot retains wal",
                        "entity": "abandoned_report_slot_wal_retention_simple",
                        "evidence": [
                            "scripted diagnostic actions observed analytics backfill slot retains wal"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "protected and short retention slots excluded",
                        "entity": "abandoned_report_slot_wal_retention_simple",
                        "evidence": [
                            "scripted diagnostic actions observed protected and short retention slots excluded"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "drop only analytics backfill slot",
                        "entity": "abandoned_report_slot_wal_retention_simple",
                        "evidence": [
                            "scripted diagnostic actions observed drop only analytics backfill slot"
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
        evaluator=PgSystemFailureWalAccumulationForAbandonedReportSlotWalRetentionSimpleEvaluatorCase,
        runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
        difficulty=DifficultyCalibration(
            diagnostic_depth=4,
            environmental_complexity=0.666667,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_system_failure_wal_accumulation_"
                "abandoned_report_slot_wal_retention_simple_"
                "MockLLMAgent.json",
            ),
        ),
        base_image_name='aiopsbench-pg-tpcds:latest',
        workload_tag='tpcds',
        dataset_scale=1,
        title='Abandoned analytics and retry slots retain WAL beside six healthy slot states.',
        alert=(
            'Alert: The primary volume is growing and checkout writes are slower, while a '
            'low-rate order-count probe remains healthy. Several downstream slot records are '
            'present; wal_slot_business_registry records purpose and acknowledgement age. '
            'Identify the retention owner, preserve healthy consumers, and restore '
            'normal WAL cleanup.'
        ),
        initial_state={
            'status': 'degraded',
            'wal': 'retained_by_abandoned_report_slot',
            'database': 'available',
        },
        expected_target={
            'status': 'recovered',
            'wal': 'retention_released',
            'protected_slot': 'preserved',
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=(
                WorkloadProfile(
                    name='order_count_health_probe',
                    sql='SELECT count(*) FROM store_sales WHERE ss_sold_date_sk IS NOT NULL;',
                    qps=0.1,
                    tier='LIGHT',
                    application_name='order_count_health_probe',
                ),
            ),
            worker_count=1,
            seed=0x2F07,
            start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
            warmup_seconds=11,
        ),
        slot_name='analytics_report_backfill_abandoned',
        stale_slot_names=(
            'analytics_report_backfill_abandoned',
            'analytics_backfill_abandoned_legacy',
            'report_export_retry_stale',
        ),
        fresh_slot_names=(
            'cdc_orders_live',
            'standby_archive_a',
            'standby_archive_b',
            'cdc_orders_draining',
            'report_export_recent_ack',
            'analytics_backfill_recent_probe',
        ),
        retained_slot_names=(
            'analytics_report_backfill_abandoned',
            'analytics_backfill_abandoned_legacy',
        ),
        short_retention_slot_names=(
            'report_export_retry_stale',
            'cdc_orders_live',
            'standby_archive_b',
            'report_export_recent_ack',
            'analytics_backfill_recent_probe',
        ),
        unreserved_slot_names=(
            'standby_archive_a',
            'cdc_orders_draining',
        ),
        registry_rows=(
            WalSlotRegistryRow(slot_name='analytics_report_backfill_abandoned', purpose='cancelled Q2 analytics report backfill', ack_minutes_ago=45),
            WalSlotRegistryRow(slot_name='analytics_backfill_abandoned_legacy', purpose='legacy analytics backfill pipeline (superseded)', ack_minutes_ago=185),
            WalSlotRegistryRow(slot_name='report_export_retry_stale', purpose='failed report export retry worker', ack_minutes_ago=50),
            WalSlotRegistryRow(slot_name='cdc_orders_live', purpose='live order CDC consumer', ack_minutes_ago=2),
            WalSlotRegistryRow(slot_name='standby_archive_a', purpose='warm standby archive feed', ack_minutes_ago=6),
            WalSlotRegistryRow(slot_name='standby_archive_b', purpose='warm standby archive feed', ack_minutes_ago=7),
            WalSlotRegistryRow(slot_name='cdc_orders_draining', purpose='CDC consumer draining after cutover', ack_minutes_ago=5),
            WalSlotRegistryRow(slot_name='report_export_recent_ack', purpose='report export consumer', ack_minutes_ago=1),
            WalSlotRegistryRow(slot_name='analytics_backfill_recent_probe', purpose='analytics backfill probe consumer', ack_minutes_ago=3),
        ),
        production_noise=False,
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

class PgSystemFailureWalAccumulationInjector(BaseFaultInjector):
    """
    模拟"事务日志/WAL 堆积"故障。
    创建物理复制槽（physical replication slot）但不消费，
    然后生成 WAL 写入使槽堆积，导致 WAL 文件无法回收。
    物理复制槽在 wal_level=replica 下即可工作，无需重启。
    """

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._install_persistent_state()
        env.refresh_pgss_baseline()
        if self.production_noise:
            self.seed_agent_visible_noise(env)

    def _configure(self, config, env):
        self.env = env
        self.slot_name = config["slot_name"]
        self.stale_slot_names = tuple(config["stale_slot_names"])
        self.fresh_slot_names = tuple(config["fresh_slot_names"])
        self.retained_slot_names = tuple(config["retained_slot_names"])
        self.short_retention_slot_names = tuple(config["short_retention_slot_names"])
        self.unreserved_slot_names = tuple(config["unreserved_slot_names"])
        self.registry_rows = tuple(config["registry_rows"])
        self.production_noise = bool(config["production_noise"])
        self._noise_conns = []
        self._validate_slot_name(self.slot_name)
        for slot_name in (*self.stale_slot_names, *self.fresh_slot_names):
            self._validate_slot_name(slot_name)
        for row in self.registry_rows:
            if "'" in row.purpose:
                raise ValueError(f"Registry purpose must not contain quotes: {row.purpose!r}")

        env._wal_accumulation_stale_slots = self.stale_slot_names
        env._wal_accumulation_fresh_slots = self.fresh_slot_names
        env.execute_sql(
            "CREATE TABLE IF NOT EXISTS wal_slot_business_registry "
            "(slot_name text PRIMARY KEY, purpose text NOT NULL, last_ack_at timestamptz NOT NULL);"
        )
        env.execute_sql("DELETE FROM wal_slot_business_registry;")
        values = ", ".join(
            f"('{row.slot_name}','{row.purpose}', now() - interval '{row.ack_minutes_ago} minutes')"
            for row in self.registry_rows
        )
        env.execute_sql(
            f"INSERT INTO wal_slot_business_registry(slot_name,purpose,last_ack_at) VALUES {values};"
        )

    def _install_persistent_state(self):
        env = self.env

        print(f"[FaultInjector:PgSystemFailureWalAccumulationInjector] "
              f"Injecting WAL accumulation fault with slot '{self.slot_name}'...")

        with env.metrics_hidden():
            all_slots = (*self.stale_slot_names, *self.fresh_slot_names)
            self._drop_slot_if_exists(env, self.slot_name)
            for slot_name in all_slots:
                self._drop_slot_if_exists(env, slot_name)

            # Slots reserved before the bulk write burst: their restart_lsn stays
            # behind, so they retain the WAL generated below and expose real
            # disk pressure during diagnosis.
            for slot_name in self.retained_slot_names:
                env.execute_sql(
                    f"SELECT pg_create_physical_replication_slot('{slot_name}', true);"
                )
            print(f"[FaultInjector:PgSystemFailureWalAccumulationInjector] "
                  f"Created retaining replication slots: {self.retained_slot_names}")

            # Generate some WAL by doing small writes (keep memory usage low)
            env.execute_sql(
                "CREATE TABLE IF NOT EXISTS wal_accumulation_write_noise "
                "(id serial PRIMARY KEY, order_id int, status text, payload text, updated_at timestamptz DEFAULT now());"
            )
            for i in range(5):
                env.execute_sql(
                    "INSERT INTO wal_accumulation_write_noise (order_id, status, payload) "
                    "SELECT g, 'paid', repeat('x', 1024) FROM generate_series(1, 500) AS g;"
                )
            env.execute_sql("CHECKPOINT;")

            # Slots reserved after the bulk WAL: they hold restart_lsn, but only
            # retain the small trickle below, so retention size alone does not
            # identify the abandoned slots.
            for slot_name in self.short_retention_slot_names:
                env.execute_sql(
                    f"SELECT pg_create_physical_replication_slot('{slot_name}', true);"
                )
            env.execute_sql(
                "INSERT INTO wal_accumulation_write_noise (order_id, status, payload) "
                "SELECT g, 'refunded', repeat('y', 128) FROM generate_series(1, 40) AS g;"
            )
            env.execute_sql("CHECKPOINT;")

            # Static downstream paths without a reserved LSN.
            for slot_name in self.unreserved_slot_names:
                env.execute_sql(
                    f"SELECT pg_create_physical_replication_slot('{slot_name}', false);"
                )

            visible = env.execute_sql(
                "SELECT slot_name, active, restart_lsn, wal_status, "
                "pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_bytes "
                "FROM pg_replication_slots "
                f"WHERE slot_name IN ({self._slot_names_sql(list(all_slots))}) "
                "ORDER BY retained_bytes DESC NULLS LAST;"
            )
        print(f"[FaultInjector:PgSystemFailureWalAccumulationInjector] "
              f"Agent-visible replication slot state: {visible}")

        print(f"[FaultInjector:PgSystemFailureWalAccumulationInjector] "
              f"Generated WAL writes. Slot is now accumulating WAL.")

    def seed_agent_visible_noise(self, env):
        self.env = env
        env.execute_sql(
            "CREATE TABLE IF NOT EXISTS wal_accumulation_business_noise "
            "(id serial PRIMARY KEY, order_id int, app text, amount numeric, payload text, created_at timestamptz DEFAULT now());"
        )
        env.execute_sql(
            "INSERT INTO wal_accumulation_business_noise (order_id, app, amount, payload) "
            "SELECT g, CASE WHEN g % 4 = 0 THEN 'billing_export' WHEN g % 4 = 1 THEN 'checkout_api' "
            "WHEN g % 4 = 2 THEN 'prometheus_probe' ELSE 'nightly_report' END, "
            "(g % 1000)::numeric / 10.0, repeat(md5(g::text), 4) "
            "FROM generate_series(1, 3000) AS g;"
        )
        for sql in [
            "SELECT app, count(*), sum(amount) FROM wal_accumulation_business_noise GROUP BY app;",
            "SELECT count(*) FROM wal_accumulation_business_noise WHERE app = 'checkout_api';",
            "SELECT pg_is_in_recovery(), now();",
            "SELECT datname, xact_commit, blks_read, blks_hit FROM pg_stat_database WHERE datname = current_database();",
            "SELECT count(*) FROM generate_series(1, 1500000) AS g WHERE md5(g::text) LIKE 'a%';",
        ]:
            env.execute_sql(sql)
        self._open_noise_connections()

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        slot_names = [*self.stale_slot_names, *self.fresh_slot_names]
        slot_state = env.execute_sql(
            "SELECT slot_name, active, restart_lsn, wal_status, "
            "pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_bytes "
            "FROM pg_replication_slots "
            f"WHERE slot_name IN ({self._slot_names_sql(slot_names)}) "
            "ORDER BY retained_bytes DESC NULLS LAST;"
        )
        rows = _json_object(slot_state, "WAL accumulation slot state")["result"]
        by_slot = {row[0]: row for row in rows}
        missing = [slot for slot in slot_names if slot not in by_slot]
        if missing:
            raise RuntimeError(f"WAL accumulation slots are missing: {missing}")
        retained_bytes = float(by_slot[self.slot_name][4] or 0)
        if retained_bytes <= 0:
            raise RuntimeError(
                f"WAL accumulation slot {self.slot_name!r} retains no WAL: {slot_state}"
            )
        return {
            "disk_usage": env.query_metrics("disk_usage"),
            "slot_state": slot_state,
            "retained_bytes": retained_bytes,
            "business_registry": env.execute_sql(
                "SELECT slot_name, purpose, last_ack_at "
                "FROM wal_slot_business_registry ORDER BY slot_name;"
            ),
        }

    def quiesce(self, context: FaultLifecycleContext):
        self._close_noise_connections()
        env = context.env
        self._drop_slot_if_exists(env, self.slot_name)
        for slot_name in (*self.stale_slot_names, *self.fresh_slot_names):
            self._drop_slot_if_exists(env, slot_name)

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        print(f"[FaultInjector:PgSystemFailureWalAccumulationInjector] Recovering...")
        self._close_noise_connections()
        self._drop_slot_if_exists(env, self.slot_name)
        for slot_name in (*self.stale_slot_names, *self.fresh_slot_names):
            self._drop_slot_if_exists(env, slot_name)
        _require_sql_success(
            env.execute_sql(
                "DROP TABLE IF EXISTS wal_accumulation_write_noise; "
                "DROP TABLE IF EXISTS wal_accumulation_business_noise; "
                "DROP TABLE IF EXISTS wal_slot_business_registry;"
            ),
            "drop WAL-accumulation scenario tables",
        )
        print(f"[FaultInjector:PgSystemFailureWalAccumulationInjector] Recovery complete.")

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        table_state = _json_object(
            env.execute_sql(
                "SELECT to_regclass('public.wal_accumulation_write_noise')::text;"
            ),
            "verify WAL-accumulation fault image",
        )
        if table_state["result"] != [["wal_accumulation_write_noise"]]:
            raise RuntimeError(
                "WAL-accumulation fault image is missing its persistent table: "
                f"observed={table_state['result']}"
            )
        self._install_persistent_state()
        env.refresh_pgss_baseline()
        if self.production_noise:
            self.seed_agent_visible_noise(env)

    def _validate_slot_name(self, slot_name: str) -> None:
        import re

        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", slot_name or ""):
            raise ValueError(f"Invalid replication slot name: {slot_name!r}")

    def _slot_exists(self, env, slot_name: str = None) -> bool:
        import json

        slot_name = slot_name or self.slot_name
        raw = env.execute_sql(
            "SELECT count(*) FROM pg_replication_slots "
            f"WHERE slot_name = '{slot_name}';"
        )
        payload = json.loads(raw)
        return int(payload.get("result", [[0]])[0][0] or 0) > 0

    def _slot_names_sql(self, slot_names: list) -> str:
        return ", ".join(f"'{slot_name}'" for slot_name in slot_names)

    def _connect_noise(self, application_name: str):
        import psycopg2

        return psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            application_name=application_name,
            connect_timeout=3,
        )

    def _open_noise_connections(self):
        for app_name in [
            "checkout_api_idle_pool_0",
            "checkout_api_idle_pool_1",
            "billing_export_worker_idle",
            "nightly_report_dashboard_idle",
            "prometheus_pg_probe_idle",
            "backup_catalog_probe_idle",
        ]:
            conn = self._connect_noise(app_name)
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
            self._noise_conns.append(conn)

    def _close_noise_connections(self):
        for conn in self._noise_conns:
            conn.close()
        self._noise_conns = []

    def _drop_slot_if_exists(self, env, slot_name: str) -> None:
        _require_sql_success(
            env.execute_sql(
                f"SELECT pg_drop_replication_slot(slot_name) "
                f"FROM pg_replication_slots "
                f"WHERE slot_name = '{slot_name}';"
            ),
            f"drop replication slot {slot_name}",
        )
        if self._slot_exists(env, slot_name):
            raise RuntimeError(
                f"Replication slot {slot_name!r} still exists after PostgreSQL reported a successful drop"
            )


class PgSystemFailureWalAccumulationScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_wal_accumulation'
    description = 'Simulates WAL accumulation caused by an abandoned backfill replication slot.'
    cases = (
        _PGSYSTEMFAILUREWALACCUMULATIONSCENARIO_CASE,
        _PGSYSTEMFAILUREWALACCUMULATIONSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailureWalAccumulationCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureWalAccumulationInjector,
                config={
                    'slot_name': case.slot_name,
                    'stale_slot_names': case.stale_slot_names,
                    'fresh_slot_names': case.fresh_slot_names,
                    'retained_slot_names': case.retained_slot_names,
                    'short_retention_slot_names': case.short_retention_slot_names,
                    'unreserved_slot_names': case.unreserved_slot_names,
                    'registry_rows': case.registry_rows,
                    'production_noise': case.production_noise,
                },
            ),
        )
