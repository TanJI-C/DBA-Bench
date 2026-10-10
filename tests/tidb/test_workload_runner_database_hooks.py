import threading
import time

import pytest

from src.execution.environment import TiDBEnv
from src.execution.tidb_connection_router import TiDBConnectionRouter
from src.scenarios.workloads import SessionSetupBehavior, WorkloadProfile
from src.scenarios.runtime.workload_runner import WorkloadRunner


class Cursor:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def execute(self, sql):
        pass


class Connection:
    def __init__(self):
        self.closed = False

    def cursor(self):
        return Cursor()

    def close(self):
        if self.closed:
            raise RuntimeError("connection closed twice")
        self.closed = True


class HookEnv:
    def __init__(self):
        self.connections = {}
        self.targets = []
        self.configured = 0
        self.executed = 0

    def open_workload_connection(
        self,
        application_name,
        connection_pool=None,
        *,
        target=None,
    ):
        assert application_name == WorkloadRunner.APPLICATION_NAME
        assert not (connection_pool is not None and target is not None)
        route = connection_pool if connection_pool is not None else target
        self.targets.append(target)
        return self.connections.setdefault(route, Connection())

    def configure_workload_session(self, connection, profile):
        assert connection in self.connections.values()
        self.configured += 1

    def execute_workload_profile(self, connection, profile):
        assert connection in self.connections.values()
        self.executed += 1
        return {"session_setup_statements": 0, "result_rows": 0}

    @staticmethod
    def should_recycle_workload_connection(connection):
        return False

    @staticmethod
    def close_workload_connection(connection):
        connection.close()


def test_runner_uses_environment_database_hooks_and_closes_connection():
    env = HookEnv()
    runner = WorkloadRunner(
        env,
        profiles=[WorkloadProfile(name="probe", sql="SELECT 1", qps=100)],
        worker_count=1,
    )

    runner.start()
    time.sleep(0.05)
    runner.stop()

    assert env.configured > 0
    assert env.executed > 0
    assert env.connections[None].closed


def test_runner_initializes_session_setup_without_connection_setup_statements():
    class SessionEnv(HookEnv):
        def __init__(self):
            super().__init__()
            self.initialized = []

        def initialize_workload_session(self, connection, profile):
            assert connection in self.connections.values()
            self.initialized.append(profile.name)

    env = SessionEnv()
    profile = WorkloadProfile(
        name="qp05_fp_07",
        sql="SELECT 1",
        session_setup=SessionSetupBehavior(
            config_query="SELECT 1",
            statement="SET @aiopsbench_qp05_request_fingerprint = 'qp05_fp_07'",
            statement_count=lambda _configuration, _checkout_number: 1,
        ),
    )
    runner = WorkloadRunner(env, profiles=[profile], worker_count=1)

    assert runner._ensure_connection(profile) is True
    assert env.initialized == ["qp05_fp_07"]


def test_runner_does_not_close_a_connection_recycled_by_the_environment():
    env = HookEnv()

    def execute_workload_profile(connection, profile):
        connection.close()
        return {"session_setup_statements": 0, "result_rows": 0}

    env.execute_workload_profile = execute_workload_profile
    runner = WorkloadRunner(
        env,
        profiles=[WorkloadProfile(name="probe", sql="SELECT 1", qps=100)],
        worker_count=1,
    )

    runner.start()
    time.sleep(0.05)
    runner.stop()

    assert env.connections[None].closed


def test_runner_keeps_independent_connections_for_independent_pools_and_targets():
    class MultiPoolEnv:
        def __init__(self):
            self.connections = {}

        def open_workload_connection(
            self,
            application_name,
            connection_pool=None,
            *,
            target=None,
        ):
            assert application_name in {"checkout-api", "order-dashboard"}
            assert not (connection_pool is not None and target is not None)
            route = (
                ("pool", connection_pool)
                if connection_pool is not None
                else ("target", target)
            )
            return self.connections.setdefault(route, Connection())

        def configure_workload_session(self, connection, profile):
            assert connection in self.connections.values()

        def execute_workload_profile(self, connection, profile):
            assert connection in self.connections.values()
            return {"session_setup_statements": 0, "result_rows": 0}

        @staticmethod
        def should_recycle_workload_connection(connection):
            return False

        @staticmethod
        def close_workload_connection(connection):
            connection.close()

    env = MultiPoolEnv()
    runner = WorkloadRunner(
        env,
        profiles=[
            WorkloadProfile(
                name="checkout",
                sql="SELECT 1",
                qps=100,
                application_name="checkout-api",
                connection_pool="checkout-router",
            ),
            WorkloadProfile(
                name="dashboard",
                sql="SELECT 1",
                qps=100,
                application_name="order-dashboard",
                connection_pool="reporting-router",
            ),
        ],
        worker_count=1,
    )

    runner.start()
    time.sleep(0.05)
    runner.stop()

    assert set(env.connections) == {
        ("pool", "checkout-router"),
        ("pool", "reporting-router"),
    }
    assert all(connection.closed for connection in env.connections.values())


def test_runner_routes_targeted_profiles_to_distinct_connections():
    env = HookEnv()
    runner = WorkloadRunner(
        env,
        profiles=[
            WorkloadProfile(name="primary", sql="SELECT 1", qps=100),
            WorkloadProfile(
                name="affected",
                sql="SELECT 1",
                qps=100,
                target="tidb/tidb-1",
            ),
        ],
        worker_count=1,
    )

    runner.start()
    time.sleep(0.05)
    runner.stop()

    assert None in env.targets
    assert "tidb/tidb-1" in env.targets
    assert env.connections[None] is not env.connections["tidb/tidb-1"]
    assert all(connection.closed for connection in env.connections.values())


def test_runner_activity_preserves_session_setup_counts():
    runner = WorkloadRunner(
        HookEnv(),
        profiles=[WorkloadProfile(name="probe", sql="SELECT 1", qps=1)],
        worker_count=1,
    )
    runner._recent.extend((
        {
            "profile": "probe",
            "tier": "OLTP_CORE",
            "exec_ms": 10.0,
            "ok": True,
            "error": None,
            "session_setup_statements": 5,
        },
        {
            "profile": "probe",
            "tier": "OLTP_CORE",
            "exec_ms": 12.0,
            "ok": True,
            "error": None,
            "session_setup_statements": 5,
        },
    ))

    profile = runner.get_activity(limit=1)["value"][0]

    assert profile["session_setup_statements"] == 10
    assert profile["last_session_setup_statements"] == 5


def test_observation_window_quiesces_in_flight_execution_before_reset_callback():
    class BlockingEnv(HookEnv):
        def __init__(self):
            super().__init__()
            self.started = threading.Event()
            self.release = threading.Event()
            self.in_flight = 0
            self.reset_snapshots = []

        def execute_workload_profile(self, connection, profile):
            self.in_flight += 1
            self.started.set()
            if not self.release.wait(2):
                raise RuntimeError("blocking workload test did not receive release")
            self.in_flight -= 1
            return {"session_setup_statements": 7}

    env = BlockingEnv()
    runner = WorkloadRunner(
        env,
        profiles=[WorkloadProfile(name="probe", sql="SELECT 1", qps=100)],
        worker_count=1,
    )
    runner.start()
    assert env.started.wait(2)

    release = threading.Timer(0.05, env.release.set)
    release.start()
    runner.begin_observation_window(
        before_reset=lambda: (
            env.reset_snapshots.append((env.in_flight, runner._stats["probe"]["attempts"])),
        )
    )
    runner.stop()

    assert env.reset_snapshots == [(0, 1)]


def test_observation_window_closes_idle_connections_before_reset_callback():
    env = HookEnv()
    runner = WorkloadRunner(
        env,
        profiles=[WorkloadProfile(name="probe", sql="SELECT 1", qps=1)],
        worker_count=1,
    )
    runner._threads = [threading.current_thread()]
    thread = runner._threads[0]
    connection = Connection()
    key = runner._connection_key(runner.profiles[0])
    thread._runner_connections = {key: connection}
    thread._runner_connection_started_at = {key: time.monotonic()}
    runner._worker_connections[(thread, key)] = connection

    snapshots = []
    runner.begin_observation_window(
        before_reset=lambda: snapshots.append((connection.closed, dict(runner._worker_connections)))
    )

    assert snapshots == [(True, {})]
    assert thread._runner_connections == {}
    assert thread._runner_connection_started_at == {}


def test_runner_reopens_a_connection_invalidated_by_the_environment():
    class RecyclingEnv(HookEnv):
        def __init__(self):
            super().__init__()
            self.opened = []
            self.recycle = False

        def open_workload_connection(self, application_name, connection_pool=None, *, target=None):
            connection = Connection()
            self.opened.append(connection)
            return connection

        def should_recycle_workload_connection(self, connection):
            return self.recycle

    env = RecyclingEnv()
    profile = WorkloadProfile(name="probe", sql="SELECT 1")
    runner = WorkloadRunner(env, profiles=[profile], worker_count=1)

    assert runner._ensure_connection(profile) is True
    first = env.opened[0]
    env.recycle = True
    assert runner._ensure_connection(profile) is True

    assert first.closed is True
    assert len(env.opened) == 2


def test_router_generation_marks_existing_connections_for_recycle():
    router = TiDBConnectionRouter({"tidb/tidb-0": ("127.0.0.1", 4000)}, "tidb/tidb-0")
    connection = Connection()
    router.register_connection(connection, "tidb/tidb-0")

    assert router.should_recycle(connection) is False
    router.invalidate_connections()
    assert router.should_recycle(connection) is True
    router.release_connection(connection)


def test_tidb_control_table_dml_invalidates_registered_routers():
    class Router:
        def __init__(self):
            self.invalidations = 0

        def invalidate_connections(self):
            self.invalidations += 1

    env = object.__new__(TiDBEnv)
    router = Router()
    env._connection_routers = {"router": router}
    env._workload_connection_invalidation_generation = 0
    env._connection_router_invalidation_rules = {
        "set-autocommit": (frozenset({"benchops.runtime_assignments"}), ("router",)),
    }

    env._invalidate_connection_routers_for_sql(
        "UPDATE benchops.runtime_assignments SET connector_revision='r1' WHERE cohort_id='cohort-04'"
    )
    env._invalidate_connection_routers_for_sql(
        "SELECT * FROM benchops.runtime_assignments"
    )

    assert router.invalidations == 1


def test_tidb_close_workload_connection_releases_router_without_double_close():
    class Router:
        def __init__(self):
            self.released = []

        def release_connection(self, connection):
            self.released.append(connection)

    class ClosedConnection:
        open = False

        def close(self):
            raise AssertionError("already-closed connection must not be closed twice")

    env = object.__new__(TiDBEnv)
    connection = ClosedConnection()
    router = Router()
    env._workload_session_setups = {id(connection): ("profile",)}
    env._connection_router_connections = {id(connection): "router"}
    env._connection_routers = {"router": router}

    env.close_workload_connection(connection)

    assert router.released == [connection]
    assert id(connection) not in env._workload_session_setups
    assert id(connection) not in env._connection_router_connections


@pytest.mark.parametrize("route", ["connection_pool", "target"])
def test_workload_profile_rejects_both_route_fields(route):
    kwargs = {"connection_pool": "checkout-router", "target": "tidb/tidb-1"}

    with pytest.raises(ValueError, match="either connection_pool or target"):
        WorkloadProfile(name=f"invalid-{route}", sql="SELECT 1", **kwargs)
