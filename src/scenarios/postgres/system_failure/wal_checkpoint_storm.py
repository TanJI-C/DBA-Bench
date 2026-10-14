from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.system_failure import (
    PgSystemFailureWalCheckpointStormForBillingSlotCheckpointStormEvaluatorCase,
    PgSystemFailureWalCheckpointStormForBillingSlotCheckpointBurstSimpleEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.workloads.tpcds import default_mix
from src.scenarios.postgres.common import (
    build_checkpoint_log_noise_profiles,
    build_checkpoint_temp_spill_profiles,
)

from src.execution.specs import PostgresCaseRuntime, CaseResourceSpec
from src.scenarios.base import PostgresScenario, DifficultyCalibration, FaultPlan, PostgresScenarioCase
from src.workloads.specs import BackgroundWorkloadSpec, EMPTY_BACKGROUND_WORKLOAD


POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureWalCheckpointStormCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    slot_name: str
    active_slot_name: str
    checkpoint_timeout_fault: str
    max_wal_size_fault: str
    checkpoint_completion_target_fault: str
    checkpoint_timeout_target: str
    max_wal_size_target: str
    checkpoint_completion_target_target: str
    slow_queries: tuple[str, ...]
    protected_slot_name: str | None = None
    protected_slot_job_id: str | None = None
    retired_slot_job_id: str | None = None
    slot_registry_table: str | None = None
    export_batches_table: str | None = None
    protected_slot_period_seconds: float = 12.0
    protected_slot_active_seconds: float = 3.0
    retired_slot_idle_days: int = 45

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureWalCheckpointStormForBillingSlotCheckpointStormScenarioCase(PgSystemFailureWalCheckpointStormCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureWalCheckpointStormForBillingSlotCheckpointBurstSimpleScenarioCase(PgSystemFailureWalCheckpointStormCase):
    pass

_PGSYSTEMFAILUREWALCHECKPOINTSTORMSCENARIO_CASE = PgSystemFailureWalCheckpointStormForBillingSlotCheckpointStormScenarioCase(
    case_id='billing_slot_checkpoint_storm',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "wal disk growth and checkpoint latency",
                    "entity": "billing_migration_archive",
                    "evidence": [
                        "observed wal disk growth and checkpoint latency"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "inactive slot retains wal",
                    "entity": "billing_migration_archive",
                    "evidence": [
                        "observed inactive slot retains wal"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "checkpoint storm",
                    "entity": "billing_migration_archive",
                    "evidence": [
                        "observed checkpoint storm"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "wal retention and checkpoint storm are independent roots",
                    "entity": "billing_migration_archive",
                    "evidence": [
                        "observed wal retention and checkpoint storm are independent roots"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "release wal then tune checkpoint",
                    "entity": "billing_migration_archive",
                    "evidence": [
                        "observed release wal then tune checkpoint"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "dropped stalled slot and restored checkpoint settings"
            ],
            "verification": [
                "slot absence and all three settings verified"
            ]
        },
        "summary": "WAL retention and checkpoint pressure were independent root causes."
    },
    case_no=0,
    evaluator=PgSystemFailureWalCheckpointStormForBillingSlotCheckpointStormEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='Simulates WAL accumulation plus frequent checkpoint storms.',
    alert='[CRITICAL] [PostgreSQL/Primary] Disk capacity and write-latency SLOs are breaching. Available disk space is declining, and storage I/O is intermittently near saturation. Triage the incident and restore database stability.',
    initial_state={'status': 'degraded',
 'wal': 'retained_by_unused_slot',
 'checkpoint': 'too_frequent',
 'priority': 'release_wal_first'},
    expected_target={'status': 'recovered',
 'wal': 'slot_dropped_and_recyclable',
 'checkpoint': 'parameters_tuned',
 'verification': 'both_roots_resolved'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(default_mix()) + tuple(build_checkpoint_log_noise_profiles()) + tuple(build_checkpoint_temp_spill_profiles()),
        worker_count=6,
        seed=0xA10B,
    ),
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    slot_name='billing_migration_archive',
    active_slot_name='orders_reporting_replica',
    checkpoint_timeout_fault='30s',
    max_wal_size_fault='32MB',
    checkpoint_completion_target_fault='0.1',
    checkpoint_timeout_target='5min',
    max_wal_size_target='1GB',
    checkpoint_completion_target_target='0.9',
    slow_queries=("INSERT INTO order_write_events (payload) SELECT repeat('x', 1000) FROM generate_series(1, "
 '1000);',),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.266667,
        reference_run_ids=(
            "reference-64__pg_wal_checkpoint_storm__"
            "billing_slot_checkpoint_storm__mock__r001",
        ),
    ),
)

_PGSYSTEMFAILUREWALCHECKPOINTSTORM_SIMPLE_CASE = PgSystemFailureWalCheckpointStormForBillingSlotCheckpointBurstSimpleScenarioCase(
    case_id='billing_slot_checkpoint_burst_simple',
    case_no=1,
    evaluator=PgSystemFailureWalCheckpointStormForBillingSlotCheckpointBurstSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='A focused WAL retention plus checkpoint burst case with a stalled slot, a protected export slot, and light write noise.',
    alert='[SEV2] [PostgreSQL/Primary] Disk free space keeps dropping and write latency shows short recurring spikes. Scheduled billing exports and healthy replication must not be interrupted. Diagnose the database causes and restore disk headroom and stable write latency.',
    initial_state={'status': 'degraded', 'wal': 'retained_by_unused_slot', 'checkpoint': 'too_frequent', 'priority': 'release_wal_first'},
    expected_target={'status': 'recovered', 'wal': 'slot_dropped_and_recyclable', 'checkpoint': 'parameters_tuned', 'verification': 'both_roots_resolved'},
    protected_slot_name='billing_export_wal_archive',
    protected_slot_job_id='billing_hourly_export',
    retired_slot_job_id='billing_migration_2026q2',
    slot_registry_table='billing_export_job_registry',
    export_batches_table='billing_export_batches',
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_checkpoint_log_noise_profiles()[:1]),
        worker_count=1,
        seed=0x6103,
    ),
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    slot_name='billing_simple_archive',
    active_slot_name='orders_simple_reporting_replica',
    checkpoint_timeout_fault='45s',
    max_wal_size_fault='64MB',
    checkpoint_completion_target_fault='0.2',
    checkpoint_timeout_target='5min',
    max_wal_size_target='1GB',
    checkpoint_completion_target_target='0.9',
    slow_queries=("INSERT INTO order_write_events (payload) SELECT repeat('x', 500) FROM generate_series(1, 250);",),
    reference_report=_PGSYSTEMFAILUREWALCHECKPOINTSTORMSCENARIO_CASE.reference_report,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.133333,
        reference_run_ids=(
            'reference-247__pg_system_failure_wal_checkpoint_storm__'
            'billing_slot_checkpoint_burst_simple__mock__r001',
        ),
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

class PgSystemFailureWalCheckpointStormInjector(BaseFaultInjector):
    """
    模拟 WAL 堆积 + Checkpoint 风暴复合故障。
    复制槽负责制造 WAL 保留，过小 checkpoint_timeout/max_wal_size 与过低
    checkpoint_completion_target 负责制造频繁且尖锐的 checkpoint I/O 压力。
    """

    def __init__(self):
        self.env = None
        self.slot_name = "billing_migration_archive"
        self.active_slot_name = "orders_reporting_replica"
        self.checkpoint_timeout = "30s"
        self.max_wal_size = "32MB"
        self.checkpoint_completion_target = "0.1"
        self.protected_slot_name = None
        self.protected_slot_job_id = None
        self.retired_slot_job_id = None
        self.slot_registry_table = None
        self.export_batches_table = None
        self.protected_slot_period_seconds = 12.0
        self.protected_slot_active_seconds = 3.0
        self.retired_slot_idle_days = 45
        self._stop_event = None
        self._writer_thread = None
        self._writer_conn = None
        self._active_slot_stop_event = None
        self._active_slot_thread = None
        self._active_slot_conn = None
        self._active_slot_start_lsn = 0
        self._export_stop_event = None
        self._export_thread = None
        self._export_conn = None

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self.env = env
        self._apply_config(config)
        self._validate_config()
        self.pre_activation_checkpoint_config = env.execute_sql(
            "SELECT name, setting, unit FROM pg_settings "
            "WHERE name IN ('checkpoint_timeout', 'max_wal_size', "
            "'checkpoint_completion_target') ORDER BY name;"
        )

        print(f"[FaultInjector:PgSystemFailureWalCheckpointStormInjector] "
              f"Injecting WAL retention + checkpoint storm...")

        self.recover(context)

        with env.metrics_hidden():
            env.execute_sql(
                f"SELECT pg_create_physical_replication_slot('{self.slot_name}', true);"
            )

            env.execute_sql(
                f"ALTER SYSTEM SET checkpoint_timeout = '{self.checkpoint_timeout}';"
            )
            env.execute_sql(
                f"ALTER SYSTEM SET max_wal_size = '{self.max_wal_size}';"
            )
            env.execute_sql(
                "ALTER SYSTEM SET checkpoint_completion_target = "
                f"'{self.checkpoint_completion_target}';"
            )
            env.execute_sql("SELECT pg_reload_conf();")

            env.execute_sql(
                "CREATE TABLE IF NOT EXISTS order_write_events "
                "(id bigserial PRIMARY KEY, payload text, created_at timestamptz DEFAULT now());"
            )
            for _ in range(6):
                env.execute_sql(
                    "INSERT INTO order_write_events (payload) "
                    "SELECT repeat(md5(random()::text), 64) "
                    "FROM generate_series(1, 4000);"
                )
            if self._protected_enabled():
                self._create_export_business_state()
                self._prepare_protected_slot()
            self._start_active_slot_consumer()
            if self._protected_enabled():
                self._start_export_worker()

        self._start_writer()
        env.reconnect()

        print(f"[FaultInjector:PgSystemFailureWalCheckpointStormInjector] "
              f"Created inactive slot '{self.slot_name}' and set "
              f"checkpoint_timeout={self.checkpoint_timeout}, "
              f"max_wal_size={self.max_wal_size}, "
              f"checkpoint_completion_target={self.checkpoint_completion_target}.")

    def _protected_enabled(self) -> bool:
        return self.protected_slot_name is not None

    def _apply_config(self, config: dict):
        self.slot_name = config['slot_name']
        self.active_slot_name = config['active_slot_name']
        self.checkpoint_timeout = config['checkpoint_timeout']
        self.max_wal_size = config['max_wal_size']
        self.checkpoint_completion_target = config['checkpoint_completion_target']
        self.protected_slot_name = config.get('protected_slot_name')
        self.protected_slot_job_id = config.get('protected_slot_job_id')
        self.retired_slot_job_id = config.get('retired_slot_job_id')
        self.slot_registry_table = config.get('slot_registry_table')
        self.export_batches_table = config.get('export_batches_table')
        self.protected_slot_period_seconds = float(config.get('protected_slot_period_seconds', 12.0))
        self.protected_slot_active_seconds = float(config.get('protected_slot_active_seconds', 3.0))
        self.retired_slot_idle_days = int(config.get('retired_slot_idle_days', 45))

    def _validate_config(self):
        import re

        if not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", self.slot_name):
            raise ValueError("slot_name must be a simple replication slot identifier")
        if not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", self.active_slot_name):
            raise ValueError("active_slot_name must be a simple replication slot identifier")
        if self.slot_name == self.active_slot_name:
            raise ValueError("slot_name and active_slot_name must be different")
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
        if self._protected_enabled():
            for name, value in (
                ("protected_slot_name", self.protected_slot_name),
                ("slot_registry_table", self.slot_registry_table),
                ("export_batches_table", self.export_batches_table),
            ):
                if not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", str(value)):
                    raise ValueError(f"{name} must be a simple identifier, got {value!r}")
            if self.protected_slot_name in (self.slot_name, self.active_slot_name):
                raise ValueError("protected_slot_name must differ from the fault and active slots")
            for field in ("protected_slot_job_id", "retired_slot_job_id"):
                if not getattr(self, field):
                    raise ValueError(f"{field} is required when protected_slot_name is set")
            if not 0 < self.protected_slot_active_seconds < self.protected_slot_period_seconds:
                raise ValueError(
                    "protected slot consumer window must be inside its period: "
                    f"active={self.protected_slot_active_seconds}s, period={self.protected_slot_period_seconds}s"
                )
            if self.retired_slot_idle_days <= 0:
                raise ValueError(f"retired_slot_idle_days must be positive, got {self.retired_slot_idle_days}")

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
        self._writer_conn = conn
        return conn

    def _wal_checkpoint_writer_loop(self):
        import time

        conn = None
        try:
            conn = self._connect("order_write_worker")
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                while self._stop_event is not None and not self._stop_event.is_set():
                    cur.execute(
                        "INSERT INTO order_write_events (payload) "
                        "SELECT repeat(md5(random()::text), 64) "
                        "FROM generate_series(1, 2000);"
                    )
                    time.sleep(1.0)
        except Exception as exc:
            print(f"[FaultInjector:PgSystemFailureWalCheckpointStormInjector] "
                  f"Background WAL/checkpoint writer stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _active_slot_consumer_loop(self):
        import select
        import time

        import psycopg2
        import psycopg2.errors
        import psycopg2.extras

        conn = None
        try:
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.dbname,
                connect_timeout=5,
                application_name=self.active_slot_name,
                connection_factory=psycopg2.extras.PhysicalReplicationConnection,
            )
            self._active_slot_conn = conn
            cur = conn.cursor()
            cur.start_replication(
                slot_name=self.active_slot_name,
                slot_type=psycopg2.extras.REPLICATION_PHYSICAL,
                start_lsn=self._active_slot_start_lsn,
                decode=False,
                status_interval=1,
            )
            while (
                self._active_slot_stop_event is not None
                and not self._active_slot_stop_event.is_set()
            ):
                msg = cur.read_message()
                if msg is not None:
                    msg.cursor.send_feedback(flush_lsn=msg.data_start, reply=True)
                    continue
                select.select([cur], [], [], 1.0)
        except Exception as exc:
            print(f"[FaultInjector:PgSystemFailureWalCheckpointStormInjector] "
                  f"Active replication slot consumer stopped: {exc}")
            time.sleep(0.2)
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            self._active_slot_conn = None

    @staticmethod
    def _lsn_to_int(lsn: str) -> int:
        upper, lower = str(lsn).split("/")
        return (int(upper, 16) << 32) + int(lower, 16)

    def _prepare_active_replication_slot(self):
        import json

        self.env.execute_sql(
            f"SELECT pg_create_physical_replication_slot('{self.active_slot_name}', true) "
            f"WHERE NOT EXISTS ("
            f"SELECT 1 FROM pg_replication_slots WHERE slot_name = '{self.active_slot_name}'"
            f");"
        )
        res = self.env.execute_sql("SELECT pg_current_wal_lsn();")
        try:
            data = json.loads(res) if isinstance(res, str) else res
            rows = data.get("result") or []
            if rows and rows[0] and rows[0][0]:
                self._active_slot_start_lsn = self._lsn_to_int(rows[0][0])
        except Exception:
            self._active_slot_start_lsn = 0

    def _ensure_replication_hba(self):
        import subprocess

        container_name = self.env.deployment.container_name
        pgdata = getattr(self.env.deployment, "pgdata", "/var/lib/postgresql/data_fat")
        rule = "host replication postgres 172.16.0.0/12 scram-sha-256"
        marker = "# aiopsbench normal replication client access"
        script = (
            f"set -e; HBA='{pgdata}/pg_hba.conf'; "
            f"grep -F {rule!r} \"$HBA\" >/dev/null 2>&1 || "
            f"printf '\\n%s\\n%s\\n' {marker!r} {rule!r} >> \"$HBA\"; "
            "PG_BIN=$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1); "
            f"su - postgres -c \"$PG_BIN/pg_ctl reload -D {pgdata}\" >/dev/null"
        )
        result = subprocess.run(
            ["docker", "exec", container_name, "bash", "-lc", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Could not enable replication HBA rule: {result.stderr.strip()}"
            )

    def _wait_for_active_slot(self, timeout_sec: float = 5.0):
        import json
        import time

        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            res = self.env.execute_sql(
                "SELECT active FROM pg_replication_slots "
                f"WHERE slot_name = '{self.active_slot_name}';"
            )
            try:
                data = json.loads(res) if isinstance(res, str) else res
                rows = data.get("result") or []
                if rows and rows[0] and rows[0][0] is True:
                    return True
            except Exception:
                pass
            time.sleep(0.2)
        return False

    def _start_active_slot_consumer(self):
        import threading

        self._stop_active_slot_consumer()
        self._prepare_active_replication_slot()
        self._ensure_replication_hba()
        self._active_slot_stop_event = threading.Event()
        self._active_slot_thread = threading.Thread(
            target=self._active_slot_consumer_loop,
            daemon=True,
        )
        self._active_slot_thread.start()
        if not self._wait_for_active_slot():
            raise RuntimeError(
                f"Active slot {self.active_slot_name!r} did not become active before timeout"
            )

    def _connect_export(self):
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name="billing_export_worker",
        )
        conn.autocommit = True
        self._export_conn = conn
        return conn

    def _advance_protected_slot_window(self):
        import select
        import time

        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name=self.protected_slot_name,
            connection_factory=psycopg2.extras.PhysicalReplicationConnection,
        )
        try:
            cur = conn.cursor()
            cur.start_replication(
                slot_name=self.protected_slot_name,
                slot_type=psycopg2.extras.REPLICATION_PHYSICAL,
                decode=False,
                status_interval=1,
            )
            deadline = time.time() + self.protected_slot_active_seconds
            while time.time() < deadline:
                msg = cur.read_message()
                if msg is not None:
                    msg.cursor.send_feedback(flush_lsn=msg.data_start, reply=True)
                    continue
                select.select([cur], [], [], 0.5)
        finally:
            conn.close()

    def _billing_export_worker_loop(self):
        import time

        batch_no = 0
        conn = None
        try:
            conn = self._connect_export()
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                while self._export_stop_event is not None and not self._export_stop_event.is_set():
                    batch_no += 1
                    cur.execute(
                        f"INSERT INTO {self.export_batches_table} (batch_no, payload) "
                        "SELECT %s, repeat(md5(random()::text), 48) "
                        "FROM generate_series(1, 400);",
                        (batch_no,),
                    )
                    cur.execute("SELECT count(*) FROM store_sales WHERE ss_net_paid > 20;")
                    cur.execute(
                        f"UPDATE {self.slot_registry_table} "
                        "SET last_run_at = clock_timestamp() "
                        f"WHERE job_id = '{self.protected_slot_job_id}';"
                    )
                    self._advance_protected_slot_window()
                    time.sleep(
                        max(self.protected_slot_period_seconds - self.protected_slot_active_seconds, 0.5)
                    )
        except Exception as exc:
            print(f"[FaultInjector:PgSystemFailureWalCheckpointStormInjector] "
                  f"Billing export worker stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            self._export_conn = None

    def _prepare_protected_slot(self):
        import json

        self.env.execute_sql(
            f"SELECT pg_create_physical_replication_slot('{self.protected_slot_name}', true) "
            f"WHERE NOT EXISTS ("
            f"SELECT 1 FROM pg_replication_slots WHERE slot_name = '{self.protected_slot_name}'"
            f");"
        )
        payload = _json_object(
            self.env.execute_sql(
                "SELECT count(*) FROM pg_replication_slots "
                f"WHERE slot_name = '{self.protected_slot_name}';"
            ),
            "verify protected export slot creation",
        )
        if payload["result"] != [[1]]:
            raise RuntimeError(
                f"Protected export slot {self.protected_slot_name!r} was not created"
            )

    def _create_export_business_state(self):
        self.env.execute_sql(
            f"CREATE TABLE IF NOT EXISTS {self.slot_registry_table} ("
            "job_id text PRIMARY KEY, "
            "slot_name text UNIQUE NOT NULL, "
            "status text NOT NULL, "
            "schedule text, "
            "last_run_at timestamptz);"
        )
        self.env.execute_sql(
            f"CREATE TABLE IF NOT EXISTS {self.export_batches_table} ("
            "id bigserial PRIMARY KEY, "
            "batch_no int NOT NULL, "
            "payload text, "
            "created_at timestamptz DEFAULT now());"
        )
        self.env.execute_sql(
            f"INSERT INTO {self.slot_registry_table} (job_id, slot_name, status, schedule, last_run_at) "
            f"VALUES ('{self.retired_slot_job_id}', '{self.slot_name}', 'finished', NULL, "
            f"now() - interval '{self.retired_slot_idle_days} days') "
            "ON CONFLICT (job_id) DO UPDATE SET "
            "slot_name = EXCLUDED.slot_name, status = EXCLUDED.status, "
            "schedule = EXCLUDED.schedule, last_run_at = EXCLUDED.last_run_at;"
        )
        self.env.execute_sql(
            f"INSERT INTO {self.slot_registry_table} (job_id, slot_name, status, schedule, last_run_at) "
            f"VALUES ('{self.protected_slot_job_id}', '{self.protected_slot_name}', 'running', "
            f"'continuous ({int(self.protected_slot_period_seconds)}s cycle)', now()) "
            "ON CONFLICT (job_id) DO UPDATE SET "
            "slot_name = EXCLUDED.slot_name, status = EXCLUDED.status, "
            "schedule = EXCLUDED.schedule;"
        )

    def _drop_export_business_state(self):
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.export_batches_table};")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.slot_registry_table};")

    def _wait_for_export_worker(self, timeout_sec: float = 20.0):
        import json
        import time

        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            payload = _json_object(
                self.env.execute_sql(f"SELECT count(*) FROM {self.export_batches_table};"),
                "verify billing export batch evidence",
            )
            if payload["result"] and payload["result"][0][0] >= 1:
                return True
            time.sleep(0.2)
        return False

    def _start_export_worker(self):
        import threading

        self._stop_export_worker()
        self._create_export_business_state()
        self._prepare_protected_slot()
        self._export_stop_event = threading.Event()
        self._export_thread = threading.Thread(
            target=self._billing_export_worker_loop,
            daemon=True,
        )
        self._export_thread.start()
        if not self._wait_for_export_worker():
            raise RuntimeError(
                f"Billing export worker produced no batch evidence within timeout "
                f"(table={self.export_batches_table!r})"
            )

    def _terminate_export_sessions(self):
        if not self.env:
            return
        self.env.execute_sql(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE application_name IN ('billing_export_worker', "
            f"'{self.protected_slot_name}') AND pid <> pg_backend_pid();"
        )

    def _stop_export_worker(self):
        if self._export_stop_event is not None:
            self._export_stop_event.set()
        if self._export_thread is not None and self._export_thread.is_alive():
            self._export_thread.join(timeout=3)
        if self._export_thread is not None and self._export_thread.is_alive():
            self._terminate_export_sessions()
            self._export_thread.join(timeout=2)
        self._export_thread = None
        self._export_conn = None
        self._export_stop_event = None

    def _verify_persistent_state(self) -> None:
        protected_columns = ""
        if self._protected_enabled():
            protected_columns = (
                f"to_regclass('public.{self.slot_registry_table}')::text, "
                f"to_regclass('public.{self.export_batches_table}')::text, "
                f"EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = '{self.protected_slot_name}'), "
            )
            expected = [[
                "order_write_events",
                self.slot_registry_table,
                self.export_batches_table,
                False,
                False,
                False,
                True,
                True,
                True,
            ]]
        else:
            expected = [["order_write_events", False, False, True, True, True]]
        payload = _json_object(
            self.env.execute_sql(
                "SELECT to_regclass('public.order_write_events')::text, "
                + protected_columns
                + f"EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = '{self.slot_name}'), "
                f"EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = '{self.active_slot_name}'), "
                f"current_setting('checkpoint_timeout')::interval = '{self.checkpoint_timeout}'::interval, "
                f"pg_size_bytes(current_setting('max_wal_size')) = pg_size_bytes('{self.max_wal_size}'), "
                "current_setting('checkpoint_completion_target')::numeric = "
                f"{float(self.checkpoint_completion_target)}::numeric;"
            ),
            "verify WAL/checkpoint fault image",
        )
        if payload["result"] != expected:
            raise RuntimeError(
                f"WAL/checkpoint fault image does not match the Case: "
                f"expected={expected}, observed={payload['result']}"
            )

    def _terminate_active_slot_backend(self):
        if not self.env:
            return
        self.env.execute_sql(
            "SELECT pg_terminate_backend(active_pid) "
            "FROM pg_replication_slots "
            f"WHERE slot_name = '{self.active_slot_name}' "
            "AND active_pid IS NOT NULL;"
        )

    def _stop_active_slot_consumer(self):
        if self._active_slot_stop_event is not None:
            self._active_slot_stop_event.set()
        if self._active_slot_conn is not None:
            try:
                self._active_slot_conn.close()
            except Exception:
                pass
        if self._active_slot_thread is not None and self._active_slot_thread.is_alive():
            self._active_slot_thread.join(timeout=3)
        if self._active_slot_thread is not None and self._active_slot_thread.is_alive():
            self._terminate_active_slot_backend()
            self._active_slot_thread.join(timeout=2)
        self._active_slot_thread = None
        self._active_slot_conn = None
        self._active_slot_stop_event = None

    def _terminate_leftover_sessions(self):
        if not self.env:
            return
        self.env.execute_sql("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE application_name = 'order_write_worker'
              AND pid <> pg_backend_pid();
        """)

    def _stop_writer(self):
        if self._stop_event is not None:
            self._stop_event.set()
        if self._writer_thread is not None and self._writer_thread.is_alive():
            self._writer_thread.join(timeout=3)
        if self._writer_thread is not None and self._writer_thread.is_alive():
            self._terminate_leftover_sessions()
            self._writer_thread.join(timeout=2)
        if self._writer_conn is not None:
            try:
                self._writer_conn.close()
            except Exception:
                pass
        self._writer_thread = None
        self._writer_conn = None
        self._stop_event = None

    def _start_writer(self):
        import threading
        import time

        self._stop_writer()
        self._stop_event = threading.Event()
        self._writer_thread = threading.Thread(
            target=self._wal_checkpoint_writer_loop,
            daemon=True,
        )
        self._writer_thread.start()
        time.sleep(1.0)

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        slot_names = (self.slot_name, self.active_slot_name)
        if self._protected_enabled():
            slot_names = slot_names + (self.protected_slot_name,)
        observability = {
            "pre_activation_checkpoint_config": self.pre_activation_checkpoint_config,
            "replication_slots": env.execute_sql(
                "SELECT slot_name, active, restart_lsn, wal_status "
                "FROM pg_replication_slots "
                f"WHERE slot_name IN ({', '.join(repr(name) for name in slot_names)}) "
                "ORDER BY slot_name;"
            ),
            "checkpoint_config": env.execute_sql(
                "SELECT name, setting, unit FROM pg_settings "
                "WHERE name IN ('checkpoint_timeout', 'max_wal_size', "
                "'checkpoint_completion_target') ORDER BY name;"
            ),
            "bgwriter": env.execute_sql(
                "SELECT checkpoints_timed, checkpoints_req, buffers_checkpoint "
                "FROM pg_stat_bgwriter;"
            ),
        }
        if self._protected_enabled():
            observability["slot_registry"] = env.execute_sql(
                f"SELECT job_id, slot_name, status, schedule, last_run_at "
                f"FROM {self.slot_registry_table} ORDER BY job_id;"
            )
        return observability

    def quiesce(self, context: FaultLifecycleContext):
        self._terminate_leftover_sessions()
        self._stop_writer()
        if self._protected_enabled():
            self._stop_export_worker()
        self._stop_active_slot_consumer()
        self._drop_runtime_slots()

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self.env = env
        self._apply_config(config)
        self._validate_config()
        self.pre_activation_checkpoint_config = env.execute_sql(
            "SELECT name, setting, unit FROM pg_settings "
            "WHERE name IN ('checkpoint_timeout', 'max_wal_size', "
            "'checkpoint_completion_target') ORDER BY name;"
        )
        with env.metrics_hidden():
            self._verify_persistent_state()
            _require_sql_success(
                env.execute_sql(
                    f"SELECT pg_create_physical_replication_slot('{self.slot_name}', true);"
                ),
                f"create runtime WAL-retention slot {self.slot_name}",
            )
            self._start_active_slot_consumer()
            if self._protected_enabled():
                self._start_export_worker()
        self._start_writer()
        env.reconnect()

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        self.env = env
        self._apply_config(context.config)
        self._validate_config()
        print(f"[FaultInjector:PgSystemFailureWalCheckpointStormInjector] Recovering...")
        self._stop_writer()
        if self._protected_enabled():
            self._stop_export_worker()
        self._stop_active_slot_consumer()
        if not env.reconnect():
            raise RuntimeError(
                f"WAL/checkpoint recovery could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )

        self._drop_runtime_slots()
        for setting in (
            "checkpoint_timeout",
            "max_wal_size",
            "checkpoint_completion_target",
        ):
            _require_sql_success(
                env.execute_sql(f"ALTER SYSTEM RESET {setting};"),
                f"reset WAL/checkpoint setting {setting}",
            )
        _require_sql_success(
            env.execute_sql("SELECT pg_reload_conf();"),
            "reload WAL/checkpoint settings",
        )
        _require_sql_success(
            env.execute_sql("DROP TABLE IF EXISTS order_write_events;"),
            "drop WAL/checkpoint table",
        )
        if self._protected_enabled():
            self._drop_export_business_state()
        print(f"[FaultInjector:PgSystemFailureWalCheckpointStormInjector] Recovery complete.")

    def _drop_runtime_slots(self) -> None:
        runtime_slots = (self.slot_name, self.active_slot_name)
        if self._protected_enabled():
            runtime_slots = runtime_slots + (self.protected_slot_name,)
        for slot_name in runtime_slots:
            _require_sql_success(
                self.env.execute_sql(
                    f"SELECT pg_drop_replication_slot(slot_name) "
                    f"FROM pg_replication_slots WHERE slot_name = '{slot_name}';"
                ),
                f"drop runtime replication slot {slot_name}",
            )
            remaining = _json_object(
                self.env.execute_sql(
                    "SELECT count(*) FROM pg_replication_slots "
                    f"WHERE slot_name = '{slot_name}';"
                ),
                f"verify removal of replication slot {slot_name}",
            )
            if remaining["result"] != [[0]]:
                raise RuntimeError(
                    f"Replication slot {slot_name!r} still exists after PostgreSQL reported a successful drop"
                )


class PgSystemFailureWalCheckpointStormScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_wal_checkpoint_storm'
    description = 'Simulates WAL accumulation plus frequent checkpoint storms.'
    cases = (_PGSYSTEMFAILUREWALCHECKPOINTSTORMSCENARIO_CASE, _PGSYSTEMFAILUREWALCHECKPOINTSTORM_SIMPLE_CASE)

    def build_fault_plan(self, case: PgSystemFailureWalCheckpointStormCase) -> tuple[FaultPlan, ...]:
        config = {
            'slot_name': case.slot_name,
            'active_slot_name': case.active_slot_name,
            'checkpoint_timeout': case.checkpoint_timeout_fault,
            'max_wal_size': case.max_wal_size_fault,
            'checkpoint_completion_target': case.checkpoint_completion_target_fault,
        }
        if case.protected_slot_name is not None:
            config.update({
                'protected_slot_name': case.protected_slot_name,
                'protected_slot_job_id': case.protected_slot_job_id,
                'retired_slot_job_id': case.retired_slot_job_id,
                'slot_registry_table': case.slot_registry_table,
                'export_batches_table': case.export_batches_table,
                'protected_slot_period_seconds': case.protected_slot_period_seconds,
                'protected_slot_active_seconds': case.protected_slot_active_seconds,
                'retired_slot_idle_days': case.retired_slot_idle_days,
            })
        return (
            FaultPlan(
                injector_type=PgSystemFailureWalCheckpointStormInjector,
                config=config,
            ),
        )
