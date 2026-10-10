import json
import threading
from types import SimpleNamespace

from src.scenarios.postgres.system_failure.connection_bloat import PgSystemFailureConnectionBloatInjector
from src.scenarios.postgres.query_perf.stale_stats_lock_contention import PgQueryPerfStaleStatsLockContentionInjector
from src.scenarios.postgres.health_check.table_bloat import PgHealthCheckTableBloatInjector
from src.scenarios.postgres.health_check.long_running_tx import PgHealthCheckLongRunningTxInjector
from src.scenarios.postgres.system_failure.connection_storm import PgSystemFailureConnectionStormInjector
from src.scenarios.postgres.system_failure.temp_file_explosion import PgSystemFailureTempFileExplosionInjector


class FakeConnection:
    def __init__(self, events, name, *, closed=0):
        self.events = events
        self.name = name
        self.closed = closed

    def cancel(self):
        self.events.append(f"cancel {self.name}")
        if self.closed:
            raise AssertionError(f"cancel called for closed connection {self.name}")

    def close(self):
        self.events.append(f"close {self.name}")
        self.closed = 1

    def rollback(self):
        raise AssertionError(f"rollback called for {self.name}")


class FakeThread:
    def __init__(self, events, name):
        self.events = events
        self.name = name

    def join(self, timeout):
        self.events.append(f"join {self.name}")

    def is_alive(self):
        return False


def lifecycle_context(env=None):
    return SimpleNamespace(
        env=env,
        scenario_id="scenario",
        case_id="case",
    )


def test_temp_file_cleanup_accepts_agent_terminated_culprit_connection():
    events = []
    injector = PgSystemFailureTempFileExplosionInjector()
    injector._stop_event = threading.Event()
    injector._bg_conn = FakeConnection(events, "culprit", closed=2)
    injector._thread = FakeThread(events, "culprit")

    injector._stop_runtime(lifecycle_context())

    assert events == ["join culprit", "close culprit"]
    assert injector._stop_event.is_set()
    assert injector._bg_conn is None
    assert injector._thread is None


def test_temp_file_fault_image_verification_checks_culprit_role():
    observed_sql = []

    class FakeEnv:
        def execute_sql(self, sql):
            observed_sql.append(sql)
            return json.dumps(
                {"status": "success", "result": [["report_exporter", True]]}
            )

    injector = PgSystemFailureTempFileExplosionInjector()
    injector.env = FakeEnv()
    injector.culprit_role = "report_exporter"

    injector._verify_persistent_state()

    assert len(observed_sql) == 1
    assert "FROM pg_roles" in observed_sql[0]
    assert "report_exporter" in observed_sql[0]


def test_temp_file_cleanup_cancels_before_joining_and_closing_live_connections():
    events = []
    injector = PgSystemFailureTempFileExplosionInjector()
    injector._stop_event = threading.Event()
    injector._bg_conn = FakeConnection(events, "culprit")
    injector._thread = FakeThread(events, "culprit")
    injector._noise_conns = [FakeConnection(events, "noise")]
    injector._noise_threads = [FakeThread(events, "noise")]

    injector._stop_runtime(lifecycle_context())

    assert events == [
        "cancel culprit",
        "cancel noise",
        "join noise",
        "join culprit",
        "close culprit",
        "close noise",
    ]


def test_connection_storm_cleanup_closes_agent_terminated_connections():
    events = []

    class FakeEnv:
        def execute_sql(self, sql):
            events.append("terminate residual sessions")
            return json.dumps({"status": "success", "result": []})

    injector = PgSystemFailureConnectionStormInjector()
    injector.env = FakeEnv()
    injector.app_role = "checkout_app"
    injector._short_xact_stop_event = threading.Event()
    injector._short_xact_threads = [FakeThread(events, "short transaction")]
    injector._connections = [
        FakeConnection(events, "agent terminated", closed=2),
        FakeConnection(events, "idle"),
    ]

    injector._stop_runtime(lifecycle_context(injector.env))

    assert events == [
        "join short transaction",
        "close agent terminated",
        "close idle",
        "terminate residual sessions",
    ]
    assert injector._connections == []
    assert injector._short_xact_threads == []
    assert injector._short_xact_stop_event is None


def test_connection_bloat_cleanup_closes_transactions_before_terminating_residual_sessions():
    events = []

    class FakeEnv:
        def execute_sql(self, sql):
            events.append("terminate residual sessions")
            assert events[:2] == ["close blocker", "close distractor"]
            return json.dumps({"status": "success", "result": []})

    injector = PgSystemFailureConnectionBloatInjector()
    injector._stop_event = threading.Event()
    injector.worker_app_prefix = "order_api_worker"
    injector.blocker_app_name = "settlement_reporter"
    injector.distractor_app_names = ["reporting_session"]
    injector.env = FakeEnv()
    injector._blocker_conn = FakeConnection(events, "blocker", closed=2)
    injector._distractor_connections = [FakeConnection(events, "distractor")]
    injector._connections = [FakeConnection(events, "worker", closed=2)]
    injector._threads = [FakeThread(events, "worker")]

    injector._stop_runtime_sessions(lifecycle_context(injector.env))

    assert events == [
        "close blocker",
        "close distractor",
        "terminate residual sessions",
        "join worker",
        "close worker",
    ]
    assert injector._stop_event is None
    assert injector._blocker_conn is None
    assert injector._distractor_connections == []
    assert injector._connections == []
    assert injector._threads == []


def test_stale_stats_lock_cleanup_terminates_backends_before_joining_threads():
    events = []
    injector = PgQueryPerfStaleStatsLockContentionInjector()
    injector._terminate_background_backends = lambda: events.append("terminate backends")
    injector._stop_runtime_workers = lambda context: events.append("join threads")

    injector.quiesce(lifecycle_context())

    assert events == ["terminate backends", "join threads"]


def test_long_transaction_noise_applications_are_event_scoped():
    first = PgHealthCheckLongRunningTxInjector()
    first.app_name = "checkout-rw-pool-stress-01"
    second = PgHealthCheckLongRunningTxInjector()
    second.app_name = "checkout-rw-pool-stress-02"

    first_names = first._runtime_noise_applications()
    second_names = second._runtime_noise_applications()

    assert first_names != second_names
    assert set(first_names.values()).isdisjoint(second_names.values())
    assert first_names["exporter"] == "checkout-rw-pool-stress-01-exporter"
    assert first_names["web_idle_prefix"] == "checkout-rw-pool-stress-01-web-idle-"


def test_long_transaction_cleanup_terminates_only_current_event_noise():
    statements = []

    class FakeCursor:
        description = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, sql):
            statements.append(sql)

        def fetchall(self):
            return []

    class FakeConnection:
        autocommit = False

        def cursor(self):
            return FakeCursor()

        def close(self):
            return None

    class FakeResetGuard:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    class FakeEnv:
        def open_workload_connection(self, actor):
            return FakeConnection()

        def _pgss_reset_guard(self, statement):
            return FakeResetGuard()

    injector = PgHealthCheckLongRunningTxInjector()
    injector.env = FakeEnv()
    injector.app_name = "checkout-rw-pool-stress-02"
    injector.decoy_app_name = "payment-short-tx-stress-02"
    injector._stop_event = threading.Event()

    injector._stop_runtime(lifecycle_context(injector.env))

    cleanup_sql = statements[2]
    assert "checkout-rw-pool-stress-02-exporter" in cleanup_sql
    assert "checkout-rw-pool-stress-02-reporting" in cleanup_sql
    assert "checkout-rw-pool-stress-02-web-idle-" in cleanup_sql
    assert "pg-exporter-primary-01" not in cleanup_sql
    assert "reporting-rollup-ro-11" not in cleanup_sql
    assert "web-ro-pool-idle-" not in cleanup_sql


def test_table_bloat_recovery_rebuilds_index_deleted_by_agent():
    statements = []

    class FakeEnv:
        def reconnect(self):
            return True

        def execute_sql(self, sql):
            statements.append(sql)
            return json.dumps({"status": "success", "result": []})

    context = SimpleNamespace(
        env=FakeEnv(),
        scenario_id="pg_health_check_table_bloat",
        case_id="store_returns_table_index_bloat",
        config={
            "tables": ("store_returns",),
            "target_table": "store_returns",
            "noise_tables": (),
            "update_column": "sr_return_quantity",
            "table_update_columns": {"store_returns": "sr_return_quantity"},
            "batch_size": 1,
            "rounds": 1,
            "noise_update_plan": {},
            "index_name": "idx_store_returns_sr_return_quantity_bloat_probe",
        },
    )

    PgHealthCheckTableBloatInjector().recover(context)

    assert statements[:3] == [
        "VACUUM FULL store_returns;",
        "DROP INDEX IF EXISTS idx_store_returns_sr_return_quantity_bloat_probe;",
        "CREATE INDEX idx_store_returns_sr_return_quantity_bloat_probe ON store_returns (sr_return_quantity);",
    ]
