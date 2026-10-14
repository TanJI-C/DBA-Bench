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
    PgHealthCheckLongRunningTxForStressIdleTransactionCleanup01EvaluatorCase,
    PgHealthCheckLongRunningTxForStressIdleTransactionCleanup02EvaluatorCase,
    PgHealthCheckLongRunningTxForStressIdleTransactionCleanup03EvaluatorCase,
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
class PgHealthCheckLongRunningTxCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    table: str
    blocker_app_name: str
    decoy_app_name: str
    dead_tuple_rows: int
    fault_idle_timeout_value: str
    idle_timeout_value: str
    noise_profile: str = "full"

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckLongRunningTxForCheckoutPoolIdleTransactionScenarioCase(PgHealthCheckLongRunningTxCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckLongRunningTxForSingleIdleTransactionCleanupSimpleScenarioCase(PgHealthCheckLongRunningTxCase):
    pass

_PGHEALTHCHECKLONGRUNNINGTXSCENARIO_CASE = PgHealthCheckLongRunningTxForCheckoutPoolIdleTransactionScenarioCase(
    case_id='checkout_pool_idle_transaction',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "checkout pool idle transaction",
                    "entity": "checkout_pool_idle_transaction",
                    "evidence": [
                        "scripted diagnostic actions observed checkout pool idle transaction"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "old snapshot blocks customer cleanup",
                    "entity": "checkout_pool_idle_transaction",
                    "evidence": [
                        "scripted diagnostic actions observed old snapshot blocks customer cleanup"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "decoy idle transaction excluded",
                    "entity": "checkout_pool_idle_transaction",
                    "evidence": [
                        "scripted diagnostic actions observed decoy idle transaction excluded"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate checkout blocker then vacuum customer",
                    "entity": "checkout_pool_idle_transaction",
                    "evidence": [
                        "scripted diagnostic actions observed terminate checkout blocker then vacuum customer"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "set idle transaction timeout to 5min",
                    "entity": "checkout_pool_idle_transaction",
                    "evidence": [
                        "scripted diagnostic actions observed set idle transaction timeout to 5min"
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
    evaluator=PgHealthCheckLongRunningTxForCheckoutPoolIdleTransactionEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='Simulates a routine production health check where one stale idle transaction holds the cleanup horizon among normal connection noise.',
    alert='[Scheduled PostgreSQL Health Check] Transaction age, cleanup horizon, and maintenance indicators crossed the housekeeping threshold during the latest routine review. Inspect connection state, transaction age, xmin horizon, and table cleanup signals; take only necessary low-risk action and report prevention measures.',
    initial_state={'status': 'cleanup_horizon_review',
 'maintenance_indicators': 'above_housekeeping_threshold',
 'connection_mix': 'production_noise_present'},
    expected_target={'status': 'recovered',
 'cleanup_horizon': 'released',
 'idle_timeout': 'configured_or_recommended',
 'table': 'customer'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    table='customer',
    blocker_app_name='checkout-rw-pool-17',
    decoy_app_name='payment-webhook-ack-sampler-02',
    dead_tuple_rows=5000,
    fault_idle_timeout_value='2h',
    idle_timeout_value='5min',
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.666667,
        reference_run_ids=(
            "reference-62__pg_health_check_long_running_tx__"
            "checkout_pool_idle_transaction__mock__r001",
        ),
    ),
)

_PGHEALTHCHECKLONGRUNNINGTX_SIMPLE_CASE = PgHealthCheckLongRunningTxForSingleIdleTransactionCleanupSimpleScenarioCase(
    case_id='single_idle_transaction_cleanup_simple',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "one stale pool transaction holds backend xmin",
                    "entity": "single_idle_transaction_cleanup_simple",
                    "evidence": [
                        "scripted diagnostic actions observed one stale pool transaction holds backend xmin"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "old snapshot blocks customer cleanup",
                    "entity": "single_idle_transaction_cleanup_simple",
                    "evidence": [
                        "scripted diagnostic actions observed old snapshot blocks customer cleanup"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "short idle transaction must be preserved",
                    "entity": "single_idle_transaction_cleanup_simple",
                    "evidence": [
                        "scripted diagnostic actions observed short idle transaction must be preserved"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate only the stale blocker then vacuum customer",
                    "entity": "single_idle_transaction_cleanup_simple",
                    "evidence": [
                        "scripted diagnostic actions observed terminate only the stale blocker then vacuum customer"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "configure a five minute idle transaction timeout",
                    "entity": "single_idle_transaction_cleanup_simple",
                    "evidence": [
                        "scripted diagnostic actions observed configure a five minute idle transaction timeout"
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
    evaluator=PgHealthCheckLongRunningTxForSingleIdleTransactionCleanupSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcds:latest', workload_tag='tpcds', dataset_scale=1,
    title='One stale pool transaction blocks cleanup amid one short idle transaction and one monitoring worker.',
    alert='[Scheduled PostgreSQL Health Check] Cleanup progress is behind its normal window while the instance remains available. Identify the session holding the cleanup horizon, avoid terminating unrelated sessions, restore cleanup, and add a preventive timeout.',
    initial_state={'status': 'cleanup_horizon_review', 'connection_mix': 'limited_noise_present'},
    expected_target={'status': 'recovered', 'cleanup_horizon': 'released', 'table': 'customer'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    table='customer', blocker_app_name='checkout-rw-pool-simple', decoy_app_name='payment-short-tx-simple',
    dead_tuple_rows=1200, fault_idle_timeout_value='2h', idle_timeout_value='5min', noise_profile='simple',
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.333333,
        reference_run_ids=('run_pg_health_check_long_running_tx_single_idle_transaction_cleanup_simple_MockLLMAgent',),
    ),
)


def _stress_reference_report(case_id: str, blocker: str) -> dict[str, object]:
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "stress cleanup-horizon blocker",
                    "entity": case_id,
                    "evidence": [f"scripted diagnostic actions observed {blocker} holding backend xmin"],
                },
                {
                    "type": "finding",
                    "factor": "old snapshot blocks customer cleanup",
                    "entity": case_id,
                    "evidence": ["scripted diagnostic actions observed customer cleanup horizon blocked"],
                },
                {
                    "type": "finding",
                    "factor": "terminate only the stale blocker then vacuum customer",
                    "entity": case_id,
                    "evidence": ["scripted diagnostic actions observed targeted blocker cleanup"],
                },
            ]
        },
        "outcome": {
            "changes": ["applied the case-specific remediation"],
            "verification": ["verified the case-specific final state"],
        },
        "summary": "The scripted mock completed its stress cleanup-horizon diagnosis and verification.",
    }


_PGHEALTHCHECKLONGRUNNINGTX_STRESS_CASES = (
    PgHealthCheckLongRunningTxForSingleIdleTransactionCleanupSimpleScenarioCase(
        case_id="stress_idle_transaction_cleanup_01",
        reference_report=_stress_reference_report("stress_idle_transaction_cleanup_01", "checkout-rw-pool-stress-01"),
        case_no=2,
        evaluator=PgHealthCheckLongRunningTxForStressIdleTransactionCleanup01EvaluatorCase,
        base_image_name="aiopsbench-pg-tpcds:latest",
        workload_tag="tpcds",
        dataset_scale=1,
        title="Stress cleanup-horizon blocker 01.",
        alert="[Scheduled PostgreSQL Health Check] Additional cleanup horizon blocker 01 is active during the long-task stress probe.",
        initial_state={"status": "cleanup_horizon_review", "connection_mix": "stress_noise_present"},
        expected_target={"status": "recovered", "cleanup_horizon": "released", "table": "customer"},
        background_workload=EMPTY_BACKGROUND_WORKLOAD,
        runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
        table="customer",
        blocker_app_name="checkout-rw-pool-stress-01",
        decoy_app_name="payment-short-tx-stress-01",
        dead_tuple_rows=800,
        fault_idle_timeout_value="2h",
        idle_timeout_value="5min",
        noise_profile="simple",
        difficulty=DifficultyCalibration(
            diagnostic_depth=5,
            environmental_complexity=0.166667,
            reference_run_ids=(
                "reference-50__pg_health_check_long_running_tx__"
            "stress_idle_transaction_cleanup_01__mock__r001",
            ),
        ),
    ),
    PgHealthCheckLongRunningTxForSingleIdleTransactionCleanupSimpleScenarioCase(
        case_id="stress_idle_transaction_cleanup_02",
        reference_report=_stress_reference_report("stress_idle_transaction_cleanup_02", "checkout-rw-pool-stress-02"),
        case_no=3,
        evaluator=PgHealthCheckLongRunningTxForStressIdleTransactionCleanup02EvaluatorCase,
        base_image_name="aiopsbench-pg-tpcds:latest",
        workload_tag="tpcds",
        dataset_scale=1,
        title="Stress cleanup-horizon blocker 02.",
        alert="[Scheduled PostgreSQL Health Check] Additional cleanup horizon blocker 02 is active during the long-task stress probe.",
        initial_state={"status": "cleanup_horizon_review", "connection_mix": "stress_noise_present"},
        expected_target={"status": "recovered", "cleanup_horizon": "released", "table": "customer"},
        background_workload=EMPTY_BACKGROUND_WORKLOAD,
        runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
        table="customer",
        blocker_app_name="checkout-rw-pool-stress-02",
        decoy_app_name="payment-short-tx-stress-02",
        dead_tuple_rows=900,
        fault_idle_timeout_value="2h",
        idle_timeout_value="5min",
        noise_profile="simple",
        difficulty=DifficultyCalibration(
            diagnostic_depth=5,
            environmental_complexity=0.166667,
            reference_run_ids=(
                "reference-50__pg_health_check_long_running_tx__"
            "stress_idle_transaction_cleanup_02__mock__r001",
            ),
        ),
    ),
    PgHealthCheckLongRunningTxForSingleIdleTransactionCleanupSimpleScenarioCase(
        case_id="stress_idle_transaction_cleanup_03",
        reference_report=_stress_reference_report("stress_idle_transaction_cleanup_03", "checkout-rw-pool-stress-03"),
        case_no=4,
        evaluator=PgHealthCheckLongRunningTxForStressIdleTransactionCleanup03EvaluatorCase,
        base_image_name="aiopsbench-pg-tpcds:latest",
        workload_tag="tpcds",
        dataset_scale=1,
        title="Stress cleanup-horizon blocker 03.",
        alert="[Scheduled PostgreSQL Health Check] Additional cleanup horizon blocker 03 is active during the long-task stress probe.",
        initial_state={"status": "cleanup_horizon_review", "connection_mix": "stress_noise_present"},
        expected_target={"status": "recovered", "cleanup_horizon": "released", "table": "customer"},
        background_workload=EMPTY_BACKGROUND_WORKLOAD,
        runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
        table="customer",
        blocker_app_name="checkout-rw-pool-stress-03",
        decoy_app_name="payment-short-tx-stress-03",
        dead_tuple_rows=1000,
        fault_idle_timeout_value="2h",
        idle_timeout_value="5min",
        noise_profile="simple",
        difficulty=DifficultyCalibration(
            diagnostic_depth=5,
            environmental_complexity=0.166667,
            reference_run_ids=(
                "reference-50__pg_health_check_long_running_tx__"
            "stress_idle_transaction_cleanup_03__mock__r001",
            ),
        ),
    ),
)


import json
import re
import time
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


def _trusted_execute_sql(environment, statement: str, *, actor: str, context: str) -> dict[str, object]:
    connection = environment.open_workload_connection(actor)
    try:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SET statement_timeout = '30s';")
            cursor.execute("SET lock_timeout = '5s';")
            cursor.execute(statement)
            if cursor.description is None:
                return {"status": "success", "message": "SQL executed."}
            rows = cursor.fetchall()
            columns = [
                column.name if hasattr(column, "name") else column[0]
                for column in cursor.description
            ]
            return {"status": "success", "columns": columns, "result": rows}
    except Exception as exc:
        raise RuntimeError(
            "PostgreSQL long-transaction trusted SQL failed: "
            f"actor={actor!r}, context={context!r}, sql={statement!r}, error={exc!r}"
        ) from exc
    finally:
        connection.close()

class PgHealthCheckLongRunningTxInjector(BaseFaultInjector):
    """
    模拟生产巡检里的 cleanup horizon 异常。
    一个 repeatable-read 事务持有旧 backend_xmin；周围同时存在普通 idle
    连接、短龄 idle-in-transaction、报表 SQL 和监控探针噪声。
    """

    def __init__(self):
        self._stop_event = None
        self._ready_event = None
        self._idle_conn = None
        self._thread = None
        self._noise_conns = []
        self._noise_threads = []
        self._thread_error = None

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config['table'], "table")
        self.app_name = config['app_name']
        self.decoy_app_name = config['decoy_app_name']
        self.dead_tuple_rows = int(config['dead_tuple_rows'])
        self.idle_timeout = config['idle_in_transaction_session_timeout']
        self.noise_profile = str(config.get('noise_profile', 'full'))

    def install(self, context: FaultLifecycleContext):
        env = context.env
        self._configure(context.config, env)
        print(f"[FaultInjector:PgHealthCheckLongRunningTxInjector] "
              f"Injecting cleanup horizon drift on {self.table}...")
        import time
        with env.metrics_hidden():
            self._create_dead_tuples(env)
        self._scrub_pg_stat_statements()
        time.sleep(1)
        print(f"[FaultInjector:PgHealthCheckLongRunningTxInjector] Fixture state prepared.")
        self.activate(context)

    def activate(self, context: FaultLifecycleContext):
        env = context.env
        self._configure(context.config, env)
        # Fresh install and snapshot restoration share the same runtime setup.
        # _start_runtime waits for and verifies the blocker before returning.
        self._start_runtime()
        with env.metrics_hidden():
            self._start_runtime_noise()
            import time
            time.sleep(1)
            self._assert_noise_observable()

    def _create_dead_tuples(self, env) -> None:
        _trusted_execute_sql(
            env,
            f"UPDATE {self.table} SET c_email_address = c_email_address || '' "
            f"WHERE c_customer_sk BETWEEN 1 AND {self.dead_tuple_rows};",
            actor=f"persistent_scenario-{self.app_name}-dead-tuples",
            context=f"create dead tuples on {self.table}",
        )
        _trusted_execute_sql(
            env,
            f"VACUUM {self.table};",
            actor=f"persistent_scenario-{self.app_name}-vacuum",
            context=f"expose long-transaction dead tuples on {self.table}",
        )
        _trusted_execute_sql(
            env,
            f"ANALYZE {self.table};",
            actor=f"persistent_scenario-{self.app_name}-analyze",
            context=f"analyze long-transaction table {self.table}",
        )

    def _connect_noise(self, app_name: str, *, options: str | None = None):
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host, port=self.env.port,
            user=self.env.user, password=self.env.password,
            dbname=self.env.dbname,
            application_name=app_name,
            options=options,
        )
        self._noise_conns.append(conn)
        return conn

    def _runtime_noise_applications(self) -> dict[str, str]:
        prefix = self.app_name
        return {
            "exporter": f"{prefix}-exporter",
            "grafana": f"{prefix}-grafana",
            "reporting": f"{prefix}-reporting",
            "analyze": f"{prefix}-analyze",
            "web_idle_prefix": f"{prefix}-web-idle-",
        }

    def _start_runtime_noise(self):
        import threading

        if self._noise_threads:
            # install and activate are both lifecycle entry points; the noise
            # set (including the decoy) must start once per activation.
            return
        noise_apps = self._runtime_noise_applications()
        if self.noise_profile == "simple":
            specs = [
                (noise_apps["exporter"], self._loop_noise, (["SELECT count(*) FROM pg_stat_activity;"], 1.0)),
                (noise_apps["reporting"], self._active_noise, (f"SELECT count(*) FROM {self.table}, pg_sleep(60);",)),
                (self.decoy_app_name, self._idle_noise, ("BEGIN; SELECT 1;", True)),
                (f"{noise_apps['web_idle_prefix']}01", self._idle_noise, ("SELECT 1;", False)),
            ]
        else:
            specs = [
            (noise_apps["exporter"], self._loop_noise, ([
                "SELECT datname, xact_commit, xact_rollback FROM pg_stat_database;",
                "SELECT relname, n_live_tup, n_dead_tup FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 5;",
                "SELECT count(*) FROM pg_stat_activity;",
            ], 1.0)),
            (noise_apps["grafana"], self._loop_noise, ([
                "SELECT relname, last_autovacuum, n_dead_tup FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 5;",
            ], 1.5)),
            (noise_apps["reporting"], self._active_noise, (
                f"SELECT count(*) FROM {self.table}, pg_sleep(60);",
            )),
            (noise_apps["analyze"], self._active_noise, (
                f"SELECT avg(c_customer_sk) FROM {self.table}, pg_sleep(45);",
            )),
            (self.decoy_app_name, self._idle_noise, ("BEGIN; SELECT 1;", True)),
        ]
            for idx in range(1, 7):
                specs.append((f"{noise_apps['web_idle_prefix']}{idx:02d}", self._idle_noise, ("SELECT 1;", False)))
        for app_name, target, args in specs:
            thread = threading.Thread(target=target, args=(app_name, *args), daemon=True)
            thread.start()
            self._noise_threads.append(thread)

    def _idle_noise(self, app_name: str, sql: str, leave_in_transaction: bool):
        # A decoy is an intentionally immortal idle-in-transaction session: an
        # earlier Event's repair may tighten the database-level
        # idle_in_transaction_session_timeout (ALTER DATABASE ... '5min'),
        # which would reap this session mid-Event. Session-level settings
        # override the database default, so the decoy holds its own.
        options = (
            "-c idle_in_transaction_session_timeout=2h" if leave_in_transaction else None
        )
        conn = self._connect_noise(app_name, options=options)
        try:
            conn.autocommit = not leave_in_transaction
            with conn.cursor() as cur:
                cur.execute(sql)
                self._stop_event.wait()
        except Exception:
            if not self._stop_event.is_set():
                raise
        finally:
            if not conn.closed:
                conn.close()

    def _active_noise(self, app_name: str, sql: str):
        conn = self._connect_noise(app_name)
        try:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(sql)
        except Exception:
            if not self._stop_event.is_set():
                raise
        finally:
            if not conn.closed:
                conn.close()

    def _loop_noise(self, app_name: str, sqls: list, interval: float):
        import time

        conn = self._connect_noise(app_name)
        try:
            conn.autocommit = True
            with conn.cursor() as cur:
                while not self._stop_event.is_set():
                    for sql in sqls:
                        cur.execute(sql)
                        if self._stop_event.is_set():
                            break
                    time.sleep(interval)
        except Exception:
            if not self._stop_event.is_set():
                raise
        finally:
            if not conn.closed:
                conn.close()

    def _assert_noise_observable(self):
        """Confirm the decoy and noise threads are visible in pg_stat_activity.

        The decoy must match the contract exactly (one session); a missing or
        duplicated decoy means the injected fixture does not match the case
        contract and activation fails here instead of entering the agent phase
        with a broken fixture. The blocker is NOT re-checked here:
        _start_runtime already blocks on the holder thread's ready signal and
        verifies the session, and the mock agent's inspection plan may
        terminate the blocker at its plan's eligibility ordinal, which can
        legitimately land while activation is still returning.
        """
        noise_apps = self._runtime_noise_applications()
        activity = None
        for _ in range(15):
            activity = self._read_long_tx_activity(noise_apps)
            row = activity["result"][0]
            decoy_count = int(row[1] or 0)
            active_noise = int(row[2] or 0)
            idle_noise = int(row[3] or 0)
            if decoy_count == 1 and active_noise >= 1 and idle_noise >= 1:
                break
            time.sleep(2)
        row = activity["result"][0]
        decoy_count = int(row[1] or 0)
        active_noise = int(row[2] or 0)
        idle_noise = int(row[3] or 0)
        if decoy_count != 1 or active_noise < 1 or idle_noise < 1:
            raise RuntimeError(
                "Long-transaction fixture does not match the session contract in pg_stat_activity "
                f"(expected decoy=1, active_noise>=1, idle_noise>=1): "
                f"decoy={decoy_count}, active_noise={active_noise}, idle_noise={idle_noise}, "
                f"decoy_app_name={self.decoy_app_name!r}, activity={activity}; "
                f"blocker_thread_error={self._thread_error!r}"
            )

    def _read_long_tx_activity(self, noise_apps):
        return _trusted_execute_sql(self.env, f"""
            SET statement_timeout = '5s';
            SELECT
                count(*) FILTER (
                    WHERE application_name = '{self.app_name}'
                      AND state = 'idle in transaction'
                      AND backend_xmin IS NOT NULL
                ) AS target_blockers,
                count(*) FILTER (
                    WHERE application_name = '{self.decoy_app_name}'
                      AND state = 'idle in transaction'
                      AND backend_xmin IS NULL
                ) AS short_idle_decoys,
                count(*) FILTER (
                    WHERE application_name IN ('{noise_apps["reporting"]}', '{noise_apps["analyze"]}')
                      AND state = 'active'
                ) AS active_noise,
                count(*) FILTER (
                    WHERE application_name LIKE '{noise_apps["web_idle_prefix"]}%'
                      AND state = 'idle'
                ) AS idle_noise
            FROM pg_stat_activity
            WHERE pid <> pg_backend_pid();
        """, actor=f"persistent_scenario-{self.app_name}-activity-check", context="read long transaction activity")

    def _scrub_pg_stat_statements(self):
        _trusted_execute_sql(
            self.env,
            "SET pg_stat_statements.track = 'none'; "
            "SELECT pg_stat_statements_reset(); "
            "RESET pg_stat_statements.track;",
            actor=f"persistent_scenario-{self.app_name}-pgss-scrub",
            context="reset pg_stat_statements for long-transaction scenario",
        )
        self.env.refresh_pgss_baseline()

    def _start_runtime(self) -> None:
        if self._stop_event is not None and not self._stop_event.is_set():
            # install and activate are both lifecycle entry points; the fault
            # runtime must start once and stay unique until recover/stop.
            return
        import psycopg2
        import threading

        self._stop_event = threading.Event()
        self._ready_event = threading.Event()
        self._idle_conn = None
        self._noise_conns = []
        self._noise_threads = []
        self._thread_error = None

        def hold_transaction():
            conn = None
            try:
                conn = psycopg2.connect(
                    host=self.env.host,
                    port=self.env.port,
                    user=self.env.user,
                    password=self.env.password,
                    dbname=self.env.dbname,
                    application_name=self.app_name,
                    options=f"-c idle_in_transaction_session_timeout={self.idle_timeout}",
                )
                conn.autocommit = False
                self._idle_conn = conn
                with conn.cursor() as cur:
                    cur.execute("BEGIN ISOLATION LEVEL REPEATABLE READ;")
                    cur.execute(
                        f"SELECT count(*) FROM {self.table} "
                        f"WHERE c_customer_sk BETWEEN 1 AND {self.dead_tuple_rows};"
                    )
                self._ready_event.set()
                self._stop_event.wait()
                conn.rollback()
            except Exception as exc:
                self._thread_error = exc
                self._ready_event.set()
            finally:
                if conn is not None:
                    conn.close()

        self._thread = threading.Thread(target=hold_transaction, daemon=True)
        self._thread.start()
        if not self._ready_event.wait(timeout=15):
            raise RuntimeError(
                "Long-running transaction did not start within 15 seconds: "
                f"thread_error={self._thread_error!r}"
            )
        if self._thread_error is not None:
            raise RuntimeError(
                f"Long-running transaction failed to start: {self._thread_error}"
            ) from self._thread_error
        verify = _trusted_execute_sql(
            self.env,
            f"SELECT count(*) FROM pg_stat_activity WHERE application_name = '{self.app_name}' "
            "AND state = 'idle in transaction';",
            actor=f"persistent_scenario-{self.app_name}-start-verify",
            context="verify long-running transaction session",
        )
        blocker_count = int(verify["result"][0][0] or 0) if verify["result"] else 0
        if blocker_count != 1:
            raise RuntimeError(
                "Long-running transaction session does not match the contract "
                "(expected exactly 1 idle-in-transaction blocker session): "
                f"app_name={self.app_name!r}, blocker_count={blocker_count}, "
                f"verify={verify!r}, thread_error={self._thread_error!r}"
            )

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
        noise_apps = self._runtime_noise_applications()
        _trusted_execute_sql(
            context.env,
            f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE (application_name = "
            f"'{self.app_name}' OR application_name = '{self.decoy_app_name}' "
            f"OR application_name LIKE '{noise_apps['web_idle_prefix']}%' "
            f"OR application_name IN ('{noise_apps['exporter']}', "
            f"'{noise_apps['grafana']}', '{noise_apps['reporting']}', "
            f"'{noise_apps['analyze']}')) "
            "AND pid <> pg_backend_pid();",
            actor=f"persistent_scenario-{self.app_name}-runtime-cleanup",
            context=f"terminate long transaction runtime sessions for {self.app_name}",
        )
        steps = []
        for index, connection in enumerate(self._noise_conns):
            if not connection.closed:
                steps.append((f"close long-transaction noise connection {index}", connection.close))
        if self._idle_conn is not None and not self._idle_conn.closed:
            steps.append(("close long-transaction blocker connection", self._idle_conn.close))
        for index, thread in enumerate(self._noise_threads):
            steps.append((
                f"join long-transaction noise thread {index}",
                lambda thread=thread: _join_thread(thread, 5, "long-transaction noise thread"),
            ))
        if self._thread is not None:
            steps.append((
                "join idle transaction thread",
                lambda: _join_thread(
                    self._thread,
                    5,
                    "long-transaction holder thread",
                ),
            ))
        _run_cleanup_steps(
            f"Long-transaction cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._idle_conn = None
        self._noise_conns = []
        self._noise_threads = []
        self._thread = None
        self._stop_event = None
        self._ready_event = None

    def prepare_observability(self, context: FaultLifecycleContext):
        return {}

    def quiesce(self, context: FaultLifecycleContext):
        """Stop non-persistable sessions before capturing the fault image."""
        self._configure(context.config, context.env)
        self._stop_runtime(context)

    def recover(self, context: FaultLifecycleContext):
        print(f"[FaultInjector:PgHealthCheckLongRunningTxInjector] Recovering...")
        self._configure(context.config, context.env)
        self._stop_runtime(context)
        _trusted_execute_sql(
            context.env,
            f"VACUUM (ANALYZE) {self.table};",
            actor=f"persistent_scenario-{self.app_name}-recovery-vacuum",
            context=f"vacuum recovered long-transaction table {self.table}",
        )


class PgHealthCheckLongRunningTxScenario(PostgresScenario):
    scenario_id = 'pg_health_check_long_running_tx'
    description = 'Simulates a long-running idle-in-transaction session blocking vacuum/garbage collection.'
    cases = (
        _PGHEALTHCHECKLONGRUNNINGTXSCENARIO_CASE,
        _PGHEALTHCHECKLONGRUNNINGTX_SIMPLE_CASE,
        *_PGHEALTHCHECKLONGRUNNINGTX_STRESS_CASES,
    )

    def build_fault_plan(self, case: PgHealthCheckLongRunningTxCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgHealthCheckLongRunningTxInjector,
                config={
                    'table': case.table,
                    'app_name': case.blocker_app_name,
                    'decoy_app_name': case.decoy_app_name,
                    'dead_tuple_rows': case.dead_tuple_rows,
                    'idle_in_transaction_session_timeout': case.fault_idle_timeout_value,
                    'noise_profile': case.noise_profile,
                },
            ),
        )
