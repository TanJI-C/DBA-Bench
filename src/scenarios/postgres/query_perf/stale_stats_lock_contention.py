from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.query_perf import (
    PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsAndLockEvaluatorCase,
    PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsSingleWaiterSimpleEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    PostgresCaseRuntime,
    PostgresScenario,
    BackgroundWorkloadSpec,
    DifficultyCalibration,
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


@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfStaleStatsLockContentionCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    customer_table: str
    order_table: str
    lock_table: str
    holder_app: str
    waiter_app: str
    initial_orders: int
    stale_orders: int
    tables: tuple[str, ...]
    diagnostic_query: str
    lock_holder_query: str
    slow_queries: tuple[str, ...]
    waiter_count: int
    noise_profiles: tuple[object, ...]

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsAndLockScenarioCase(PgQueryPerfStaleStatsLockContentionCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsSingleWaiterSimpleScenarioCase(PgQueryPerfStaleStatsLockContentionCase):
    pass

_PGQUERYPERFSTALESTATSLOCKCONTENTIONSCENARIO_CASE = PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsAndLockScenarioCase(
    case_id='checkout_stale_stats_and_lock',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "lock waits and slow queries",
                    "entity": "checkout_order_event",
                    "evidence": [
                        "observed lock waits and slow queries"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "active slow query holds locks",
                    "entity": "checkout_order_event",
                    "evidence": [
                        "observed active slow query holds locks"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "stale optimizer statistics",
                    "entity": "checkout_order_event",
                    "evidence": [
                        "observed stale optimizer statistics"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "stale plan prolongs locks",
                    "entity": "checkout_order_event",
                    "evidence": [
                        "observed stale plan prolongs locks"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "analyze target table",
                    "entity": "checkout_order_event",
                    "evidence": [
                        "observed analyze target table"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "analyzed checkout_order_event"
            ],
            "verification": [
                "statistics are fresh and lock waiters cleared"
            ]
        },
        "summary": "Stale statistics prolonged an active lock holder."
    },
    case_no=0,
    evaluator=PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsAndLockEvaluatorCase,
    base_image_name='aiopsbench-pg-default:latest',
    workload_tag='default',
    title='Simulates stale statistics causing slow active lock holders and downstream lock contention.',
    alert='Alert: order-service write requests are intermittently timing out and p95 latency is above SLO. Write throughput is below the normal baseline. Investigate and restore service health.',
    initial_state={'status': 'degraded',
 'statistics': 'stale',
 'lock_holder_state': 'active slow query',
 'lock_waiters': 'present'},
    expected_target={'status': 'recovered',
 'statistics': 'fresh',
 'lock_holder_state': 'fast',
 'lock_waiters': 'cleared',
 'required_fix': 'ANALYZE checkout_order_event'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    customer_table='checkout_customer_profile',
    order_table='checkout_order_event',
    lock_table='checkout_session_state',
    holder_app='order-api',
    waiter_app='checkout-worker',
    initial_orders=300000,
    stale_orders=1200000,
    tables=('checkout_customer_profile', 'checkout_order_event', 'checkout_session_state'),
    diagnostic_query=('SELECT count(*) AS matching_orders FROM checkout_customer_profile c JOIN checkout_order_event e '
 'ON e.customer_id = c.customer_id WHERE c.customer_id = 42 AND e.status IN (1, 2, 3);'),
    lock_holder_query=('WITH session_touch AS MATERIALIZED (UPDATE checkout_session_state SET revision = revision + 1, '
 'last_write_at = clock_timestamp() WHERE session_id = 1 RETURNING session_id), candidate_events '
 'AS MATERIALIZED (SELECT e.order_id, e.customer_id, e.status, e.amount FROM '
 'checkout_customer_profile c JOIN checkout_order_event e ON e.customer_id = c.customer_id WHERE '
 'c.customer_id = 42 AND e.status IN (1, 2, 3)) SELECT st.session_id, count(*) AS pending_events, '
 'coalesce(sum(ev.amount), 0) AS pending_amount FROM session_touch st JOIN candidate_events ev ON '
 'true GROUP BY st.session_id;'),
    slow_queries=('WITH session_touch AS MATERIALIZED (UPDATE checkout_session_state SET revision = revision + 1, '
 'last_write_at = clock_timestamp() WHERE session_id = 1 RETURNING session_id), candidate_events '
 'AS MATERIALIZED (SELECT e.order_id, e.customer_id, e.status, e.amount FROM '
 'checkout_customer_profile c JOIN checkout_order_event e ON e.customer_id = c.customer_id WHERE '
 'c.customer_id = 42 AND e.status IN (1, 2, 3)) SELECT st.session_id, count(*) AS pending_events, '
 'coalesce(sum(ev.amount), 0) AS pending_amount FROM session_touch st JOIN candidate_events ev ON '
 'true GROUP BY st.session_id;',),
    waiter_count=3,
    noise_profiles=(WorkloadProfile(name='order_summary_rollup',
                 sql='SELECT e.status, count(*) AS order_count, coalesce(sum(e.amount), 0) AS '
                     'gross_amount FROM checkout_order_event e WHERE e.customer_id BETWEEN 10 AND '
                     '90 GROUP BY e.status ORDER BY gross_amount DESC',
                 qps=0.25,
                 tier='MEDIUM',
                 commit=False,
                 application_name=None),
 WorkloadProfile(name='customer_dashboard_refresh',
                 sql='SELECT c.region, c.tier, count(*) AS events_seen, coalesce(avg(e.amount), 0) '
                     'AS avg_amount FROM checkout_customer_profile c JOIN checkout_order_event e '
                     'ON e.customer_id = c.customer_id WHERE c.tier IN (1, 2, 3) GROUP BY '
                     'c.region, c.tier ORDER BY events_seen DESC, c.region LIMIT 25',
                 qps=0.2,
                 tier='MEDIUM',
                 commit=False,
                 application_name=None),
 WorkloadProfile(name='checkout_status_touch',
                 sql='UPDATE checkout_session_state SET revision = revision + 1, last_write_at = '
                     'clock_timestamp() WHERE session_id = 2',
                 qps=0.35,
                 tier='LIGHT',
                 commit=False,
                 application_name=None),
 WorkloadProfile(name='billing_retry_worker',
                 sql='SELECT pg_sleep(0.6), count(*) AS retry_candidates FROM checkout_order_event '
                     'WHERE status = 2 AND customer_id BETWEEN 20 AND 80',
                 qps=0.2,
                 tier='LIGHT',
                 commit=False,
                 application_name=None)),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.472222,
        reference_run_ids=(
            "reference-64__pg_stale_stats_lock_contention__"
            "checkout_stale_stats_and_lock__mock__r001",
        ),
    ),
)

_PGQUERYPERFSTALESTATSLOCKCONTENTION_SIMPLE_CASE = PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsSingleWaiterSimpleScenarioCase(
    case_id='checkout_stale_stats_single_waiter_simple',
    case_no=1,
    evaluator=PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsSingleWaiterSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-default:latest',
    workload_tag='default',
    title='A focused stale-statistics lock contention case with one slow active holder and one waiter.',
    alert='Alert: checkout writes are timing out and one worker queue is waiting on a lock while a related query is slow. Identify the blocker and restore throughput.',
    initial_state={'status': 'degraded', 'statistics': 'stale', 'lock_holder_state': 'active slow query', 'lock_waiters': 'present'},
    expected_target={'status': 'recovered', 'statistics': 'fresh', 'lock_holder_state': 'fast', 'lock_waiters': 'cleared', 'required_fix': 'ANALYZE checkout_order_event_simple'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    customer_table='checkout_customer_profile_simple',
    order_table='checkout_order_event_simple',
    lock_table='checkout_session_state_simple',
    holder_app='order-api-simple',
    waiter_app='checkout-worker-simple',
    initial_orders=60000,
    stale_orders=180000,
    tables=('checkout_customer_profile_simple', 'checkout_order_event_simple', 'checkout_session_state_simple'),
    diagnostic_query="SELECT count(*) AS matching_orders FROM checkout_customer_profile_simple c JOIN checkout_order_event_simple e ON e.customer_id = c.customer_id WHERE c.customer_id = 42 AND e.status IN (1, 2, 3);",
    lock_holder_query="WITH session_touch AS MATERIALIZED (UPDATE checkout_session_state_simple SET revision = revision + 1, last_write_at = clock_timestamp() WHERE session_id = 1 RETURNING session_id), candidate_events AS MATERIALIZED (SELECT e.order_id, e.customer_id, e.status, e.amount FROM checkout_customer_profile_simple c JOIN checkout_order_event_simple e ON e.customer_id = c.customer_id WHERE c.customer_id = 42 AND e.status IN (1, 2, 3)) SELECT st.session_id, count(*) AS pending_events, coalesce(sum(ev.amount), 0) AS pending_amount FROM session_touch st JOIN candidate_events ev ON true GROUP BY st.session_id;",
    slow_queries=("WITH session_touch AS MATERIALIZED (UPDATE checkout_session_state_simple SET revision = revision + 1, last_write_at = clock_timestamp() WHERE session_id = 1 RETURNING session_id), candidate_events AS MATERIALIZED (SELECT e.order_id, e.customer_id, e.status, e.amount FROM checkout_customer_profile_simple c JOIN checkout_order_event_simple e ON e.customer_id = c.customer_id WHERE c.customer_id = 42 AND e.status IN (1, 2, 3)) SELECT st.session_id, count(*) AS pending_events, coalesce(sum(ev.amount), 0) AS pending_amount FROM session_touch st JOIN candidate_events ev ON true GROUP BY st.session_id;",),
    waiter_count=1,
    noise_profiles=(WorkloadProfile(name='simple_order_summary_rollup', sql='SELECT status, count(*) FROM checkout_order_event_simple WHERE customer_id BETWEEN 10 AND 90 GROUP BY status', qps=0.2, tier='LIGHT', commit=False, application_name=None),),
    reference_report=_PGQUERYPERFSTALESTATSLOCKCONTENTIONSCENARIO_CASE.reference_report,
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.25,
        reference_run_ids=('run_pg_query_perf_stale_stats_lock_contention_checkout_stale_stats_single_waiter_simple_MockLLMAgent',),
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

class PgQueryPerfStaleStatsLockContentionInjector(BaseFaultInjector):
    """
    构造统计信息过期引发的 active 慢查询持锁场景。
    后台 holder 会话执行一个先 UPDATE 热点行、再跑慢聚合的语句；
    waiter 会话持续尝试更新同一热点行，从 pg_locks 和 pg_stat_activity
    中能同时看到慢查询与锁等待。
    """

    HOLDER_APP = "order-api"
    WAITER_APP = "checkout-worker"

    def __init__(self):
        self._stop_event = None
        self._threads = []
        self._noise_runner = None

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self.env = env
        self._apply_config(config)
        self._stop_runtime_workers(context)

        print("[FaultInjector:PgQueryPerfStaleStatsLockContentionInjector] Preparing stale-stats lock contention fault...")
        with env.metrics_hidden():
            self._terminate_background_backends()
            self._drop_objects()
            self._create_objects()
            self._load_baseline_data()
            self._make_statistics_stale()

        self._start_runtime_workers(context)

        with env.metrics_hidden():
            self._wait_until_observable(timeout=45)
        print("[FaultInjector:PgQueryPerfStaleStatsLockContentionInjector] Fault injected.")

    def _apply_config(self, config: dict):
        self.customer_table = _validate_sql_identifier(config['customer_table'], "customer_table")
        self.order_table = _validate_sql_identifier(config['order_table'], "order_table")
        self.lock_table = _validate_sql_identifier(config['lock_table'], "lock_table")
        self.holder_app = config['holder_app']
        self.waiter_app = config['waiter_app']
        self.lock_holder_query = config["lock_holder_query"]
        self.diagnostic_query = config["diagnostic_query"]
        self.initial_orders = int(config['initial_orders'])
        self.stale_orders = int(config['stale_orders'])
        self.waiter_count = int(config['waiter_count'])
        self.noise_profiles = list(config['noise_profiles'])

    def _stop_runtime_workers(self, context: FaultLifecycleContext):
        if self._stop_event is not None:
            self._stop_event.set()
        steps = [
            (
                f"join runtime thread {index}",
                lambda thread=thread, index=index: _join_thread(
                    thread,
                    3,
                    f"stale-stats/lock thread {index}",
                ),
            )
            for index, thread in enumerate(self._threads)
        ]
        if self._noise_runner is not None:
            steps.append(("stop noise runner", self._noise_runner.stop))
        _run_cleanup_steps(
            f"Stale-stats/lock cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._threads = []
        self._stop_event = None
        self._noise_runner = None

    def _start_runtime_workers(self, context: FaultLifecycleContext):
        import threading
        import time

        self._stop_runtime_workers(context)
        self._start_noise_runner()
        self._stop_event = threading.Event()
        self._threads = []
        holder = threading.Thread(target=self._run_holder_loop, daemon=True)
        holder.start()
        self._threads.append(holder)
        time.sleep(1.0)

        for idx in range(self.waiter_count):
            waiter = threading.Thread(target=self._run_waiter_loop, args=(idx,), daemon=True)
            waiter.start()
            self._threads.append(waiter)

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {
            "active_connections": env.query_metrics("active_connections"),
            "slow_queries": env.query_metrics("slow_queries"),
            "statistics": env.execute_sql(
                "SELECT relname, n_live_tup, n_mod_since_analyze, last_analyze "
                f"FROM pg_stat_user_tables WHERE relname = '{self.order_table}';"
            ),
        }

    def quiesce(self, context: FaultLifecycleContext):
        self._terminate_background_backends()
        self._stop_runtime_workers(context)

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self.env = env
        self._apply_config(config)
        with env.metrics_hidden():
            self._verify_persistent_state()
            self._terminate_background_backends()
        self._start_runtime_workers(context)
        with env.metrics_hidden():
            self._wait_until_observable(timeout=45)

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{self.customer_table}')::text, "
                f"to_regclass('public.{self.order_table}')::text, "
                f"to_regclass('public.{self.lock_table}')::text, "
                f"(SELECT count(*) FROM {self.order_table}), "
                f"(SELECT reltuples::bigint FROM pg_class "
                f" WHERE oid = '{self.order_table}'::regclass), "
                f"(SELECT n_mod_since_analyze FROM pg_stat_user_tables "
                f" WHERE relname = '{self.order_table}'), "
                f"(SELECT reloptions @> ARRAY['autovacuum_enabled=false'] "
                f" FROM pg_class WHERE oid = '{self.order_table}'::regclass), "
                f"to_regclass('public.idx_{self.order_table}_customer_status') IS NOT NULL;"
            ),
            "verify stale-stats/lock fault image",
        )
        (
            customer,
            orders,
            locks,
            order_count,
            estimated_rows,
            modifications_since_analyze,
            autovacuum_disabled,
            index_exists,
        ) = payload["result"][0]
        if (
            customer != self.customer_table
            or orders != self.order_table
            or locks != self.lock_table
            or int(order_count) < self.initial_orders + self.stale_orders
            or int(estimated_rows) > self.initial_orders * 2
            or int(modifications_since_analyze) < self.stale_orders
            or autovacuum_disabled is not True
            or index_exists is not True
        ):
            raise RuntimeError(
                f"Stale-stats/lock fault image does not match the Case: "
                f"objects={(customer, orders, locks)}, order_count={order_count}, "
                f"required={self.initial_orders + self.stale_orders}, "
                f"estimated_rows={estimated_rows}, expected_at_most={self.initial_orders * 2}, "
                f"modifications_since_analyze={modifications_since_analyze}, "
                f"required_modifications={self.stale_orders}, "
                f"autovacuum_disabled={autovacuum_disabled}, index_exists={index_exists}"
            )

    def _create_objects(self):
        statements = [
            f"""
            CREATE TABLE IF NOT EXISTS {self.customer_table} (
                customer_id integer PRIMARY KEY,
                tier integer NOT NULL,
                region integer NOT NULL,
                pad text NOT NULL
            );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {self.order_table} (
                order_id integer PRIMARY KEY,
                customer_id integer NOT NULL,
                status integer NOT NULL,
                amount numeric(12, 2) NOT NULL,
                pad text NOT NULL
            );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {self.lock_table} (
                session_id integer PRIMARY KEY,
                status integer NOT NULL DEFAULT 0,
                revision integer NOT NULL DEFAULT 0,
                last_write_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
            """,
            f"CREATE INDEX IF NOT EXISTS idx_{self.order_table}_customer_status ON {self.order_table}(customer_id, status);",
            f"CREATE INDEX IF NOT EXISTS idx_{self.customer_table}_tier ON {self.customer_table}(tier);",
        ]
        for sql in statements:
            self.env.execute_sql(sql)

    def _load_baseline_data(self):
        print("[FaultInjector:PgQueryPerfStaleStatsLockContentionInjector] Loading baseline rows...")
        self.env.execute_sql(
            f"""
            INSERT INTO {self.customer_table}(customer_id, tier, region, pad)
            SELECT g, g % 10, g % 20, repeat('customer-', 8)
            FROM generate_series(1, 1000) AS g;
            """
        )
        self.env.execute_sql(
            f"""
            INSERT INTO {self.order_table}(order_id, customer_id, status, amount, pad)
            SELECT g, (g % 1000) + 1, (g % 3) + 1, (g % 1000)::numeric / 10.0,
                   repeat('order-baseline-', 5)
            FROM generate_series(1, {self.initial_orders}) AS g;
            """
        )
        self.env.execute_sql(
            f"""
            INSERT INTO {self.lock_table}(session_id, status)
            SELECT g, 0 FROM generate_series(1, 3) AS g;
            """
        )
        for table in (self.customer_table, self.order_table, self.lock_table):
            self.env.execute_sql(f"ALTER TABLE {table} SET (autovacuum_enabled = false);")
            self.env.execute_sql(f"ANALYZE {table};")

    def _make_statistics_stale(self):
        print("[FaultInjector:PgQueryPerfStaleStatsLockContentionInjector] Creating stale statistics...")
        start_id = self.initial_orders + 1
        end_id = self.initial_orders + self.stale_orders
        self.env.execute_sql("SET statement_timeout = '0';")
        self.env.execute_sql(
            f"""
            INSERT INTO {self.order_table}(order_id, customer_id, status, amount, pad)
            SELECT g, 42, (g % 3) + 1, (g % 1000)::numeric / 10.0,
                   repeat('order-after-analyze-', 5)
            FROM generate_series({start_id}, {end_id}) AS g;
            """
        )

    def _start_noise_runner(self):
        if not self.noise_profiles:
            return
        runner = self.create_workload_runner(self.env, self.noise_profiles, 3)
        runner.start()
        self._noise_runner = runner

    def _connect(self, application_name):
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

    def _run_holder_loop(self):
        import time

        while self._stop_event is not None and not self._stop_event.is_set():
            conn = None
            try:
                conn = self._connect(self.holder_app)
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute("SET statement_timeout = '90s';")
                    while self._stop_event is not None and not self._stop_event.is_set():
                        cur.execute(self.lock_holder_query)
                        time.sleep(0.05)
            except Exception as exc:
                if self._stop_event is not None and not self._stop_event.is_set():
                    print(f"[FaultInjector:PgQueryPerfStaleStatsLockContentionInjector] Holder loop error: {exc}")
                    time.sleep(0.5)
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass

    def _run_waiter_loop(self, idx):
        import time

        app_name = f"{self.waiter_app}-{idx}"
        update_sql = (
            f"UPDATE {self.lock_table} "
            "SET status = status + 1, revision = revision + 1, "
            "last_write_at = clock_timestamp() "
            "WHERE session_id = 1;"
        )
        while self._stop_event is not None and not self._stop_event.is_set():
            conn = None
            try:
                conn = self._connect(app_name)
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute("SET statement_timeout = '90s';")
                    cur.execute(update_sql)
            except Exception as exc:
                if self._stop_event is not None and not self._stop_event.is_set():
                    print(f"[FaultInjector:PgQueryPerfStaleStatsLockContentionInjector] Waiter {idx} error: {exc}")
                    time.sleep(0.2)
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
            time.sleep(0.05)

    def _wait_until_observable(self, timeout):
        import time

        deadline = time.time() + timeout
        last_observed = None
        while time.time() < deadline:
            res = self.env.execute_sql(
                f"""
                SELECT
                    count(*) FILTER (WHERE a.application_name = '{self.holder_app}'
                                      AND a.state = 'active'
                                      AND a.query LIKE '%candidate_events%') AS active_holders,
                    count(*) FILTER (WHERE NOT l.granted
                                      AND a.application_name LIKE '{self.waiter_app}%') AS waiting_locks,
                    (SELECT reltuples::bigint FROM pg_class
                     WHERE oid = '{self.order_table}'::regclass) AS estimated_rows,
                    (SELECT n_mod_since_analyze FROM pg_stat_user_tables
                     WHERE relname = '{self.order_table}') AS modifications_since_analyze
                FROM pg_stat_activity a
                LEFT JOIN pg_locks l ON l.pid = a.pid
                WHERE a.application_name = '{self.holder_app}'
                   OR a.application_name LIKE '{self.waiter_app}%';
                """
            )
            rows = _json_object(
                res,
                "read stale-stats/lock visibility",
            )["result"]
            if len(rows) != 1 or len(rows[0]) != 4:
                raise RuntimeError(
                    f"Stale-stats/lock visibility returned invalid rows: {rows}"
                )
            active_holders, waiting_locks, estimated_rows, modifications = (
                int(value or 0) for value in rows[0]
            )
            last_observed = {
                "active_holders": active_holders,
                "waiting_locks": waiting_locks,
                "estimated_rows": estimated_rows,
                "modifications_since_analyze": modifications,
            }
            if (
                active_holders >= 1
                and waiting_locks >= 1
                and estimated_rows <= self.initial_orders * 2
                and modifications >= self.stale_orders
            ):
                return
            time.sleep(0.5)
        raise RuntimeError(
            f"Stale-stats/lock fault did not become observable within {timeout} seconds: "
            f"last_observed={last_observed}"
        )

    def _terminate_background_backends(self):
        _require_sql_success(
            self.env.execute_sql(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE (
                    application_name LIKE 'aiopsbench_order_writer_%'
                    OR application_name LIKE 'aiopsbench_stale_stats_lock_%'
                    OR application_name = 'order-api'
                    OR application_name LIKE 'checkout-worker%'
                  )
                  AND pid <> pg_backend_pid();
                """
            ),
            "terminate stale-stats/lock background sessions",
        )

    def _drop_objects(self):
        for sql in (
            f"DROP TABLE IF EXISTS {self.order_table} CASCADE;",
            f"DROP TABLE IF EXISTS {self.customer_table} CASCADE;",
            f"DROP TABLE IF EXISTS {self.lock_table} CASCADE;",
            "DROP FUNCTION IF EXISTS aiops_stale_stats_delay();",
        ):
            _require_sql_success(
                self.env.execute_sql(sql),
                "drop stale-stats/lock object",
            )

    def recover(self, context: FaultLifecycleContext):
        self.env = context.env
        self._apply_config(context.config)
        print("[FaultInjector:PgQueryPerfStaleStatsLockContentionInjector] Recovering...")
        self._terminate_background_backends()
        self._stop_runtime_workers(context)
        for table in (self.customer_table, self.order_table, self.lock_table):
            _require_sql_success(
                self.env.execute_sql(
                    f"ALTER TABLE IF EXISTS {table} RESET (autovacuum_enabled);"
                ),
                f"restore autovacuum for target table {table}",
            )
        self._drop_objects()
        print("[FaultInjector:PgQueryPerfStaleStatsLockContentionInjector] Recovery complete.")


class PgQueryPerfStaleStatsLockContentionScenario(PostgresScenario):
    scenario_id = 'pg_query_perf_stale_stats_lock_contention'
    description = 'Simulates stale statistics causing slow active lock holders and downstream lock contention.'
    cases = (_PGQUERYPERFSTALESTATSLOCKCONTENTIONSCENARIO_CASE, _PGQUERYPERFSTALESTATSLOCKCONTENTION_SIMPLE_CASE)

    def build_fault_plan(self, case: PgQueryPerfStaleStatsLockContentionCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgQueryPerfStaleStatsLockContentionInjector,
                config={
                    'customer_table': case.customer_table,
                    'order_table': case.order_table,
                    'lock_table': case.lock_table,
                    'holder_app': case.holder_app,
                    'waiter_app': case.waiter_app,
                    'lock_holder_query': case.lock_holder_query,
                    'diagnostic_query': case.diagnostic_query,
                    'initial_orders': case.initial_orders,
                    'stale_orders': case.stale_orders,
                    'waiter_count': case.waiter_count,
                    'noise_profiles': case.noise_profiles,
                },
            ),
        )
