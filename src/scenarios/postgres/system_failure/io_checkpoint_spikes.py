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
from src.scenarios.postgres.common import (
    build_checkpoint_log_noise_profiles,
    build_checkpoint_temp_spill_profiles,
)

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
class PgSystemFailureIoCheckpointSpikesCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    table: str
    checkpoint_timeout_fault: str
    max_wal_size_fault: str
    checkpoint_completion_target_fault: str
    checkpoint_timeout_target: str
    max_wal_size_target: str
    checkpoint_completion_target_target: str

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureIoCheckpointSpikesForCheckoutCheckpointSpikesScenarioCase(PgSystemFailureIoCheckpointSpikesCase):
    pass

_PGSYSTEMFAILUREIOCHECKPOINTSPIKESSCENARIO_CASE = PgSystemFailureIoCheckpointSpikesForCheckoutCheckpointSpikesScenarioCase(
    case_id='checkout_checkpoint_spikes',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "periodic checkpoint latency spikes",
                    "entity": "checkout_checkpoint_spikes",
                    "evidence": [
                        "scripted diagnostic actions observed periodic checkpoint latency spikes"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "checkpoint settings too aggressive",
                    "entity": "checkout_checkpoint_spikes",
                    "evidence": [
                        "scripted diagnostic actions observed checkpoint settings too aggressive"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "bgwriter checkpoint deltas",
                    "entity": "checkout_checkpoint_spikes",
                    "evidence": [
                        "scripted diagnostic actions observed bgwriter checkpoint deltas"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "tune checkpoint settings and reload",
                    "entity": "checkout_checkpoint_spikes",
                    "evidence": [
                        "scripted diagnostic actions observed tune checkpoint settings and reload"
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
    evaluator=PgSystemFailureIoCheckpointSpikesForCheckoutCheckpointSpikesEvaluatorCase,
    runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='Simulates periodic disk I/O spikes caused by overly aggressive checkpoint settings.',
    alert='[CRITICAL] Order-write path latency has been showing periodic spikes every few dozen seconds; some orders take >5s to ack. Correlate the write stalls with database state, restore safe settings, and verify the reproducibility of the fix, and then submit.',
    initial_state={'status': 'degraded', 'symptom': 'periodic_write_io_spikes', 'checkpoint': 'too_frequent'},
    expected_target={'status': 'recovered',
 'checkpoint': 'parameters_tuned_and_reloaded',
 'verification': 'settings_and_bgwriter_checked'},
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            tuple(default_mix())
            + tuple(build_checkpoint_log_noise_profiles())
            + tuple(build_checkpoint_temp_spill_profiles())
        ),
        worker_count=6,
        seed=0,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    ),
    table='checkout_order_events',
    checkpoint_timeout_fault='90s',
    max_wal_size_fault='64MB',
    checkpoint_completion_target_fault='0.3',
    checkpoint_timeout_target='5min',
    max_wal_size_target='1GB',
    checkpoint_completion_target_target='0.9',
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.45,
        reference_run_ids=(
            "reference-50__pg_system_failure_io_checkpoint_spikes__"
            "checkout_checkpoint_spikes__mock__r001",
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureIoCheckpointSpikesForSingleCheckoutCheckpointSpikeSimpleScenarioCase(PgSystemFailureIoCheckpointSpikesCase):
    pass

_PGSYSTEMFAILUREIOCHECKPOINTSPIKESSCENARIO_SIMPLE_CASE = (
    PgSystemFailureIoCheckpointSpikesForSingleCheckoutCheckpointSpikeSimpleScenarioCase(
        case_id='single_checkout_checkpoint_spike_simple',
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "periodic checkpoint latency spikes",
                        "entity": "single_checkout_checkpoint_spike_simple",
                        "evidence": [
                            "scripted diagnostic actions observed periodic checkpoint latency spikes"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "checkpoint settings too aggressive",
                        "entity": "single_checkout_checkpoint_spike_simple",
                        "evidence": [
                            "scripted diagnostic actions observed checkpoint settings too aggressive"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "bgwriter checkpoint deltas",
                        "entity": "single_checkout_checkpoint_spike_simple",
                        "evidence": [
                            "scripted diagnostic actions observed bgwriter checkpoint deltas"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "tune checkpoint settings and reload",
                        "entity": "single_checkout_checkpoint_spike_simple",
                        "evidence": [
                            "scripted diagnostic actions observed tune checkpoint settings and reload"
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
        evaluator=PgSystemFailureIoCheckpointSpikesForSingleCheckoutCheckpointSpikeSimpleEvaluatorCase,
        runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
        difficulty=DifficultyCalibration(
            diagnostic_depth=3,
            environmental_complexity=0.25,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_system_failure_io_checkpoint_spikes_"
                "single_checkout_checkpoint_spike_simple_"
                "MockLLMAgent.json",
            ),
        ),
        base_image_name='aiopsbench-pg-tpcds:latest',
        workload_tag='tpcds',
        dataset_scale=1,
        title='One checkout write stream exposes checkpoint I/O spikes from unsafe checkpoint settings.',
        alert=(
            'Alert: Checkout writes show repeated short latency spikes while PostgreSQL stays '
            'available. A low-rate calendar lookup is also active. Correlate the write stalls '
            'with database state, restore safe settings, and verify the change.'
        ),
        initial_state={
            'status': 'degraded',
            'symptom': 'periodic_checkout_write_stalls',
            'database': 'available',
        },
        expected_target={
            'status': 'recovered',
            'checkpoint': 'parameters_tuned_and_reloaded',
            'database_probe': 'healthy',
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=(
                WorkloadProfile(
                    name='checkout_calendar_lookup',
                    sql='SELECT count(*) FROM date_dim WHERE d_year = 2001;',
                    qps=0.1,
                    tier='LIGHT',
                    application_name='checkout_calendar_lookup',
                ),
            ),
            worker_count=1,
            seed=0x2F06,
            start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
            warmup_seconds=11,
        ),
        table='checkout_order_events_simple',
        checkpoint_timeout_fault='90s',
        max_wal_size_fault='64MB',
        checkpoint_completion_target_fault='0.3',
        checkpoint_timeout_target='5min',
        max_wal_size_target='1GB',
        checkpoint_completion_target_target='0.9',
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

class PgSystemFailureIoCheckpointSpikesInjector(BaseFaultInjector):
    """
    模拟"存储 I/O 饱和与 Checkpoint 抖动"故障。
    通过过小 checkpoint 参数叠加持续订单写入，让 requested checkpoint
    明显增加，并在 cgroup disk_io 指标中暴露写入压力。
    """

    def __init__(self):
        self.env = None
        self.table = "checkout_order_events"
        self.checkpoint_timeout = "90s"
        self.max_wal_size = "64MB"
        self.checkpoint_completion_target = "0.3"
        self._stop_event = None
        self._writer_thread = None
        self._writer_conn = None
        self.baseline_bgwriter = {}
        self.fault_bgwriter = {}
        self.fault_checkpoint_req_delta = 0

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print("[FaultInjector:PgSystemFailureIoCheckpointSpikesInjector] "
              "Injecting checkpoint-driven I/O spike fault...")
        with env.metrics_hidden():
            for setting, value in (
                ("checkpoint_timeout", self.checkpoint_timeout),
                ("max_wal_size", self.max_wal_size),
                ("checkpoint_completion_target", self.checkpoint_completion_target),
            ):
                _require_sql_success(
                    env.execute_sql(f"ALTER SYSTEM SET {setting} = '{value}';"),
                    f"install checkpoint-spike setting {setting}={value}",
                )
            _require_sql_success(
                env.execute_sql("SELECT pg_reload_conf();"),
                "reload checkpoint-spike settings",
            )
            self._ensure_write_table(env)
        # The mock/periodic inspection may run the repair (settings reset) while
        # this install is still waiting for checkpoint pressure; re-apply the
        # fault image so activation hands over an actually-faulting state.
        self._apply_fault_settings(env)
        self._activate_runtime()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(
            config['table'], "table")
        self.checkpoint_timeout = config['checkpoint_timeout']
        self.max_wal_size = config['max_wal_size']
        self.checkpoint_completion_target = config['checkpoint_completion_target']
        self._validate_config()

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{self.table}')::text, "
                f"current_setting('checkpoint_timeout')::interval = '{self.checkpoint_timeout}'::interval, "
                f"pg_size_bytes(current_setting('max_wal_size')) = pg_size_bytes('{self.max_wal_size}'), "
                "current_setting('checkpoint_completion_target')::numeric = "
                f"{float(self.checkpoint_completion_target)}::numeric;"
            ),
            "verify checkpoint-spike fault image",
        )
        expected = [[self.table, True, True, True]]
        if payload["result"] != expected:
            raise RuntimeError(
                f"Checkpoint-spike fault image does not match the Case: "
                f"expected={expected}, observed={payload['result']}"
            )

    def _activate_runtime(self) -> None:
        import threading

        _require_sql_success(
            self.env.execute_sql("SELECT pg_stat_reset_shared('bgwriter');"),
            "reset checkpoint-spike bgwriter statistics",
        )
        self.baseline_bgwriter = self._bgwriter_snapshot()
        self._generate_wal_burst(self.env, rounds=8)
        self._stop_event = threading.Event()
        self._writer_thread = threading.Thread(
            target=self._write_load_loop,
            daemon=True,
        )
        self._writer_thread.start()
        self._wait_for_checkpoint_pressure(timeout_seconds=120)
        self.env.reconnect()

        print("[FaultInjector:PgSystemFailureIoCheckpointSpikesInjector] "
              f"Fault active: checkpoint_timeout={self.checkpoint_timeout}, "
              f"max_wal_size={self.max_wal_size}, "
              f"checkpoint_completion_target={self.checkpoint_completion_target}, "
              f"checkpoints_req_delta={self.fault_checkpoint_req_delta}.")

    def _validate_config(self):
        if not re.fullmatch(r"\d+(s|min|h|d)", str(self.checkpoint_timeout)):
            raise ValueError("checkpoint_timeout must be a PostgreSQL duration")
        if not re.fullmatch(r"\d+(MB|GB)", str(self.max_wal_size)):
            raise ValueError("max_wal_size must be an MB or GB value")
        try:
            target = float(self.checkpoint_completion_target)
        except (TypeError, ValueError) as exc:
            raise ValueError("checkpoint_completion_target must be numeric") from exc
        if target <= 0.0 or target > 1.0:
            raise ValueError("checkpoint_completion_target must be in (0, 1]")

    def _ensure_write_table(self, env):
        env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id bigserial PRIMARY KEY,
                warehouse_id integer NOT NULL,
                district_id integer NOT NULL,
                customer_id integer NOT NULL,
                status text NOT NULL DEFAULT 'PENDING',
                amount numeric(12, 2) NOT NULL,
                payload text NOT NULL,
                created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
                updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
        """)
        env.execute_sql(f"TRUNCATE TABLE {self.table};")
        env.execute_sql(f"""
            INSERT INTO {self.table} (
                warehouse_id, district_id, customer_id, status, amount, payload
            )
            SELECT
                (random() * 10)::int + 1,
                (random() * 10)::int + 1,
                (random() * 100000)::int + 1,
                CASE WHEN random() < 0.75 THEN 'PENDING' ELSE 'SETTLED' END,
                round((random() * 1000)::numeric, 2),
                repeat(md5(random()::text), 48)
            FROM generate_series(1, 24000);
        """)
        env.execute_sql(f"""
            UPDATE {self.table}
            SET status = CASE WHEN status = 'PENDING' THEN 'RETRY' ELSE 'PENDING' END,
                amount = amount + 0.01,
                payload = overlay(payload placing md5(random()::text) from 1 for 32)
            WHERE id % 2 = 0;
        """)
        env.execute_sql(f"DELETE FROM {self.table} WHERE id % 11 = 0;")
        env.execute_sql(f"""
            ALTER TABLE {self.table} SET (
                autovacuum_vacuum_scale_factor = 0.01,
                autovacuum_analyze_scale_factor = 0.01,
                autovacuum_vacuum_threshold = 50,
                autovacuum_analyze_threshold = 50
            );
        """)
        env.execute_sql(f"ANALYZE {self.table};")

    def _generate_wal_burst(self, env, rounds: int = 1):
        for _ in range(rounds):
            env.execute_sql(f"""
                INSERT INTO {self.table} (
                    warehouse_id, district_id, customer_id, status, amount, payload
                )
                SELECT
                    (random() * 10)::int + 1,
                    (random() * 10)::int + 1,
                    (random() * 100000)::int + 1,
                    CASE WHEN random() < 0.8 THEN 'PENDING' ELSE 'RETRY' END,
                    round((random() * 1000)::numeric, 2),
                    repeat(md5(random()::text), 64)
                FROM generate_series(1, 4000);
            """)
            env.execute_sql(f"""
                UPDATE {self.table}
                SET amount = amount + 1,
                    updated_at = clock_timestamp(),
                    status = CASE WHEN status = 'PENDING' THEN 'RETRY' ELSE 'PENDING' END,
                    payload = overlay(payload placing md5(random()::text) from 1 for 32)
                WHERE id IN (
                    SELECT id FROM {self.table}
                    WHERE status IN ('PENDING', 'RETRY')
                      AND warehouse_id BETWEEN 1 AND 8
                    ORDER BY random()
                    LIMIT 5000
                );
            """)

    def _bgwriter_snapshot(self) -> dict:
        payload = _json_object(
            self.env.execute_sql(
                "SELECT checkpoints_timed, checkpoints_req, buffers_checkpoint, "
                "checkpoint_write_time, checkpoint_sync_time FROM pg_stat_bgwriter;"
            ),
            "read checkpoint-spike bgwriter statistics",
        )
        row = payload["result"][0]
        return {
            "checkpoints_timed": int(row[0]),
            "checkpoints_req": int(row[1]),
            "buffers_checkpoint": int(row[2]),
            "checkpoint_write_time": float(row[3]),
            "checkpoint_sync_time": float(row[4]),
        }

    def _wait_for_checkpoint_pressure(self, timeout_seconds: int):
        import time

        base_req = int(self.baseline_bgwriter.get("checkpoints_req", 0))
        base_buffers = int(self.baseline_bgwriter.get("buffers_checkpoint", 0))
        deadline = time.time() + timeout_seconds
        burst_count = 0
        while time.time() < deadline:
            snap = self._bgwriter_snapshot()
            req_delta = int(snap.get("checkpoints_req", 0)) - base_req
            buffers_delta = int(snap.get("buffers_checkpoint", 0)) - base_buffers
            self.fault_bgwriter = snap
            self.fault_checkpoint_req_delta = max(0, req_delta)
            # requested checkpoint 和实际刷脏页都出现后，Agent 查询能看到稳定证据。
            if req_delta >= 2 or (req_delta >= 1 and buffers_delta > 0):
                return
            if burst_count < 40:
                self._generate_wal_burst(self.env, rounds=1)
                burst_count += 1
            time.sleep(1.0)
        raise RuntimeError(
            f"Checkpoint-spike pressure did not become observable: "
            f"baseline={self.baseline_bgwriter}, latest={self.fault_bgwriter}"
        )

    def _connect(self, application_name: str):
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name=application_name,
        )
        conn.autocommit = True
        if application_name == "checkout_write_load":
            self._writer_conn = conn
        return conn

    def _write_load_loop(self):
        import time

        conn = None
        try:
            conn = self._connect("checkout_write_load")
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                cur.execute("SET synchronous_commit = off;")
                while self._stop_event is not None and not self._stop_event.is_set():
                    cur.execute(f"""
                        INSERT INTO {self.table} (
                            warehouse_id, district_id, customer_id, status, amount, payload
                        )
                        SELECT
                            (random() * 10)::int + 1,
                            (random() * 10)::int + 1,
                            (random() * 100000)::int + 1,
                            CASE WHEN random() < 0.8 THEN 'PENDING' ELSE 'RETRY' END,
                            round((random() * 1000)::numeric, 2),
                            repeat(md5(random()::text), 64)
                        FROM generate_series(1, 1800);
                    """)
                    cur.execute(f"""
                        UPDATE {self.table}
                        SET amount = amount + 1,
                            updated_at = clock_timestamp(),
                            status = CASE WHEN status = 'PENDING' THEN 'RETRY' ELSE 'PENDING' END,
                            payload = overlay(payload placing md5(random()::text) from 1 for 32)
                        WHERE id IN (
                            SELECT id FROM {self.table}
                            WHERE status IN ('PENDING', 'RETRY')
                              AND warehouse_id BETWEEN 1 AND 8
                            ORDER BY random()
                            LIMIT 3500
                        );
                    """)
                    time.sleep(0.35)
        except Exception as exc:
            print("[FaultInjector:PgSystemFailureIoCheckpointSpikesInjector] "
                  f"Background write load stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _terminate_leftover_sessions(self):
        if not self.env:
            return
        self.env.execute_sql("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE application_name = 'checkout_write_load'
              AND pid <> pg_backend_pid();
        """)

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {
            "disk_io": env.query_metrics("disk_io"),
            "checkpoint_config": env.execute_sql(
                "SELECT name, setting, unit FROM pg_settings "
                "WHERE name IN ('checkpoint_timeout', 'max_wal_size', "
                "'checkpoint_completion_target') ORDER BY name;"
            ),
            "bgwriter": env.execute_sql(
                "SELECT checkpoints_timed, checkpoints_req, buffers_checkpoint, "
                "checkpoint_write_time, checkpoint_sync_time FROM pg_stat_bgwriter;"
            ),
            "fault_checkpoint_req_delta": self.fault_checkpoint_req_delta,
        }

    def quiesce(self, context: FaultLifecycleContext):
        """Clean up background write load thread for teardown."""
        print("[FaultInjector:PgSystemFailureIoCheckpointSpikesInjector] quiesce...")
        if self._stop_event is not None:
            self._stop_event.set()
        steps = []
        if self._writer_conn is not None:
            steps.append(("close checkpoint writer connection", self._writer_conn.close))
        if self._writer_thread is not None:
            steps.append((
                "join checkpoint writer thread",
                lambda: _join_thread(
                    self._writer_thread,
                    3,
                    "checkpoint-spike writer thread",
                ),
            ))
        _run_cleanup_steps(
            f"Checkpoint-spike cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._writer_thread = None
        self._writer_conn = None

    def recover(self, context: FaultLifecycleContext):
        print("[FaultInjector:PgSystemFailureIoCheckpointSpikesInjector] Recovering...")
        self.quiesce(context)
        self.env.reconnect()
        for setting in (
            "checkpoint_timeout",
            "max_wal_size",
            "checkpoint_completion_target",
        ):
            _require_sql_success(
                self.env.execute_sql(f"ALTER SYSTEM RESET {setting};"),
                f"recover checkpoint-spike setting {setting}",
            )
        _require_sql_success(
            self.env.execute_sql("SELECT pg_reload_conf();"),
            "reload recovered checkpoint-spike settings",
        )
        _require_sql_success(
            self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table};"),
            f"drop checkpoint-spike table {self.table}",
        )
        print("[FaultInjector:PgSystemFailureIoCheckpointSpikesInjector] Recovery complete.")

    def _apply_fault_settings(self, env):
        for setting, value in (
            ("checkpoint_timeout", self.checkpoint_timeout),
            ("max_wal_size", self.max_wal_size),
            ("checkpoint_completion_target", self.checkpoint_completion_target),
        ):
            _require_sql_success(
                env.execute_sql(f"ALTER SYSTEM SET {setting} = '{value}';"),
                f"apply checkpoint-spike setting {setting}={value}",
            )
        _require_sql_success(
            env.execute_sql("SELECT pg_reload_conf();"),
            "reload checkpoint-spike settings",
        )
        import time

        time.sleep(1)

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        # A periodic inspection may fire its repair between our fault re-apply
        # and the state verification; re-apply and re-verify until the fault
        # image survives a verification pass.
        last_error: RuntimeError | None = None
        for attempt in range(5):
            self._apply_fault_settings(env)
            try:
                self._verify_persistent_state()
                last_error = None
                break
            except RuntimeError as exc:
                last_error = exc
                import time

                time.sleep(2)
        if last_error is not None:
            raise last_error
        self._activate_runtime()
        print("[FaultInjector:PgSystemFailureIoCheckpointSpikesInjector] Write load re-activated.")


class PgSystemFailureIoCheckpointSpikesScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_io_checkpoint_spikes'
    description = 'Simulates periodic disk I/O spikes caused by overly aggressive checkpoint settings.'
    cases = (
        _PGSYSTEMFAILUREIOCHECKPOINTSPIKESSCENARIO_CASE,
        _PGSYSTEMFAILUREIOCHECKPOINTSPIKESSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailureIoCheckpointSpikesCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureIoCheckpointSpikesInjector,
                config={
                    'table': case.table,
                    'checkpoint_timeout': case.checkpoint_timeout_fault,
                    'max_wal_size': case.max_wal_size_fault,
                    'checkpoint_completion_target': case.checkpoint_completion_target_fault,
                },
            ),
        )
