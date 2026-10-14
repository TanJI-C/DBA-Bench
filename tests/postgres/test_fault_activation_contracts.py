import json
from types import SimpleNamespace

import pytest

from src.scenarios.postgres import (
    PgSystemFailureXidWraparoundScenario,
)
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.postgres.system_failure.connection_bloat import PgSystemFailureConnectionBloatInjector
from src.scenarios.postgres.query_perf.stale_stats_lock_contention import PgQueryPerfStaleStatsLockContentionInjector
from src.scenarios.postgres.business_change.io_saturation import PgBusinessChangeIoSaturationInjector
from src.scenarios.postgres.system_failure.xid_wraparound import PgSystemFailureXidWraparoundInjector
from src.scenarios.runtime.orchestrator import Orchestrator


def test_orchestrator_applies_xid_postgres_runtime_contract():
    scenario = PgSystemFailureXidWraparoundScenario()
    case = scenario.get_case("payment_ledger_xid_wraparound")
    deployment = PGDockerDeployment()
    orchestrator = Orchestrator.__new__(Orchestrator)
    orchestrator.scenario = scenario
    orchestrator.case = case
    orchestrator.env = PGEnv(deployment=deployment)

    orchestrator._apply_case_environment_contract()

    assert deployment.postgres_runtime_options == (
        "-c max_connections=100 -c autovacuum=off -c autovacuum_freeze_max_age=2000000000 -c shared_buffers=128MB -c work_mem=16MB "
        "-c shared_preload_libraries=pg_stat_statements"
    )


def test_xid_connection_budget_requires_case_runtime_value():
    class FakeEnv:
        def execute_sql(self, sql):
            return json.dumps({"status": "success", "result": [[22, 2]]})

    injector = PgSystemFailureXidWraparoundInjector()
    injector.env = FakeEnv()
    injector.max_connections = 100
    injector.checkout_idle_connections = 36
    injector.retry_idle_connections = 4
    injector.monitor_noise_connections = 6
    injector.connection_headroom = 8

    with pytest.raises(RuntimeError, match="expected_max_connections=100, actual_max_connections=22"):
        injector._assert_connection_budget()


def test_xid_replay_worker_budget_accounts_for_instances_and_commit_writer():
    class FakeEnv:
        def execute_sql(self, sql):
            return json.dumps({"status": "success", "result": [[100, 2]]})

    injector = PgSystemFailureXidWraparoundInjector()
    injector.env = FakeEnv()
    injector.max_connections = 100
    injector.checkout_idle_connections = 36
    injector.retry_idle_connections = 4
    injector.monitor_noise_connections = 6
    injector.connection_headroom = 8
    injector.replay_worker_instances = 2
    injector.commit_writer_enabled = True

    # 36 + 4 + 2 + 6 + 2 workers + 1 writer = 51 runtime connections;
    # remaining = 100 - 2 - 51 = 47 >= 8 headroom, so the budget holds.
    injector._assert_connection_budget()


def test_xid_control_surface_budget_accounts_for_sweep_threads():
    class FakeEnv:
        def execute_sql(self, sql):
            return json.dumps({"status": "success", "result": [[100, 2]]})

    injector = PgSystemFailureXidWraparoundInjector()
    injector.env = FakeEnv()
    injector.max_connections = 100
    injector.checkout_idle_connections = 36
    injector.retry_idle_connections = 4
    injector.monitor_noise_connections = 6
    injector.connection_headroom = 8
    injector.replay_worker_instances = 2
    injector.commit_writer_enabled = True
    injector.batch_control_table = "ops_batch_control"

    # 36 + 4 + 2 + 6 + 2 workers + 1 writer + 3 control-surface threads
    # (retry dedup sweep + nightly recon sweeper + template provisioner)
    # = 54 runtime connections; remaining = 100 - 2 - 54 = 44 >= 8 headroom,
    # so the budget holds.
    injector._assert_connection_budget()


def test_xid_control_state_reads_public_lifecycle_and_missing_row_stops_batch():
    class FakeConn:
        def __init__(self, rows):
            self.rows = rows
            self.autocommit = False

        def cursor(self):
            return self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, sql):
            self.last_sql = sql

        def fetchone(self):
            return self.rows[0] if self.rows else None

    injector = PgSystemFailureXidWraparoundInjector()
    injector.batch_control_table = "ops_batch_control"
    injector.batch_control_job = "ledger_settlement_replay"

    running = FakeConn([["running"]])
    paused = FakeConn([["paused"]])
    cancelled = FakeConn([["cancelled"]])
    removed = FakeConn([])

    assert injector._control_state(running) == "running"
    assert injector._control_state(paused) == "paused"
    assert injector._control_state(cancelled) == "cancelled"
    assert injector._control_state(removed) is None
    assert running.autocommit is True
    assert "state" in running.last_sql
    assert "ops_batch_control" in running.last_sql


def test_xid_replay_worker_parks_on_stopped_states_and_rearms_on_running():
    """'running' is the only state that runs a hold cycle.
    paused (sweeper observation hold) and cancelled/missing (pending
    re-provisioning) both drain the worker into the supervisor standby park;
    the worker re-arms when the row reads running again (sweeper resume or
    provisioner restore) and exits only with the injector shutdown. The
    standby polls under the supervisor identity, never the worker identity."""

    class FakeCursor:
        def __init__(self, worker):
            self.worker = worker

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, sql, args=None):
            self.worker.executed.append(sql)

        def fetchone(self):
            return (123,)

    class FakeConn:
        def __init__(self, worker, app_name):
            self.worker = worker
            self.app_name = app_name
            self.autocommit = False
            self.closed = False

        def cursor(self):
            return FakeCursor(self.worker)

        def close(self):
            self.closed = True

    class WorkerInjector(PgSystemFailureXidWraparoundInjector):
        def __init__(self, states):
            super().__init__()
            self.states = list(states)
            self.executed = []
            self.connect_identities = []

        def _connect_noise(self, app_name):
            self.connect_identities.append(app_name)
            return FakeConn(self, app_name)

        def _control_state(self, conn):
            self.executed.append("state")
            if not self.states:
                return "cancelled"
            return self.states.pop(0)

    import threading
    import time

    injector = WorkerInjector(["running", "paused", "cancelled", "running", "running"])
    stop_event = threading.Event()
    injector._stop_event = stop_event
    injector.table = "payment_ledger"
    injector.blocker_app_name = "settlement_replay_worker"
    injector._worker_supervisor_app_name = "settlement_replay_worker_supervisor"
    injector.batch_control_table = "ops_batch_control"
    injector.batch_control_job = "ledger_settlement_replay"
    injector._worker_hold_seconds = 0.01
    injector._worker_gap_seconds = 0.01
    injector._worker_reconnect_backoff_seconds = 0.01

    ready = threading.Event()
    thread = threading.Thread(target=injector._run_replay_worker, args=(ready, 0), daemon=True)
    thread.start()

    deadline = time.time() + 5
    while time.time() < deadline:
        locks = [sql for sql in injector.executed if "LOCK TABLE" in sql]
        if len(locks) >= 2:
            break
        time.sleep(0.01)
    # The worker ran its initial hold, parked through paused and cancelled,
    # then re-armed for a second hold once the row read running again.
    locks = [sql for sql in injector.executed if "LOCK TABLE" in sql]
    assert len(locks) == 2, injector.executed
    assert injector.states == []
    assert any(
        app_name == "settlement_replay_worker_supervisor"
        for app_name in injector.connect_identities
    )
    stop_event.set()
    thread.join(timeout=10)
    assert not thread.is_alive()


def test_xid_provisioner_restores_cancelled_rows_and_stops_when_retired():
    """The provisioner replays enabled templates - a control
    row that is missing or left cancelled comes back as running with its
    provisioned_from template binding - and exits permanently once its own
    control row leaves the running state (cancelling the provisioner row is
    an accepted way to stop provisioning)."""

    class FakeCursor:
        def __init__(self, provisioner):
            self.provisioner = provisioner

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, sql, args=None):
            self.last_sql = sql
            self.provisioner.executed_sql.append(sql)

        def fetchone(self):
            if "to_regclass" in self.last_sql:
                return ("public.ops_batch_control_template",)
            states = self.provisioner.provisioner_row_states
            state = states.pop(0) if states else "cancelled"
            return (state,)

        def fetchall(self):
            if "INSERT INTO" in self.last_sql:
                return [("ledger_settlement_replay",)]
            return []

    class FakeConn:
        def __init__(self, provisioner):
            self.provisioner = provisioner
            self.autocommit = False

        def cursor(self):
            return FakeCursor(self.provisioner)

        def close(self):
            pass

    import threading

    class ProvisionerInjector(PgSystemFailureXidWraparoundInjector):
        def __init__(self, provisioner_row_states):
            super().__init__()
            self.provisioner_row_states = list(provisioner_row_states)
            self.executed_sql = []

        def _connect_noise(self, app_name):
            assert app_name == self._provisioner_app_name
            return FakeConn(self)

    injector = ProvisionerInjector(["running", "cancelled"])
    injector.batch_control_table = "ops_batch_control"
    injector.batch_control_template_table = "ops_batch_control_template"
    injector._stop_event = threading.Event()
    injector._provisioner_interval_seconds = 0.01
    injector._worker_reconnect_backoff_seconds = 0.01

    thread = threading.Thread(target=injector._run_control_provisioner, daemon=True)
    thread.start()
    thread.join(timeout=10)
    assert not thread.is_alive()

    inserts = [sql for sql in injector.executed_sql if "INSERT INTO" in sql]
    assert len(inserts) == 1
    assert "ops_batch_control_template" in inserts[0]
    assert "c.state <> 'cancelled'" in inserts[0]
    assert "provisioned_from" in inserts[0]
    logs = [sql for sql in injector.executed_sql if "RAISE LOG" in sql]
    assert len(logs) == 1
    assert "restored control rows: ledger_settlement_replay" in logs[0]


def test_xid_provisioner_exits_when_template_table_dropped():
    """A dropped template table removes the provisioning
    source, so the provisioner stops permanently instead of erroring in a
    reconnect loop."""

    class FakeCursor:
        def __init__(self, provisioner):
            self.provisioner = provisioner

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, sql, args=None):
            self.last_sql = sql
            self.provisioner.executed_sql.append(sql)

        def fetchone(self):
            if "to_regclass" in self.last_sql:
                return (None,)
            return ("running",)

        def fetchall(self):
            return []

    class FakeConn:
        def __init__(self, provisioner):
            self.provisioner = provisioner
            self.autocommit = False

        def cursor(self):
            return FakeCursor(self.provisioner)

        def close(self):
            pass

    import threading

    class ProvisionerInjector(PgSystemFailureXidWraparoundInjector):
        def __init__(self):
            super().__init__()
            self.executed_sql = []

        def _connect_noise(self, app_name):
            return FakeConn(self)

    injector = ProvisionerInjector()
    injector.batch_control_table = "ops_batch_control"
    injector.batch_control_template_table = "ops_batch_control_template"
    injector._stop_event = threading.Event()
    injector._provisioner_interval_seconds = 0.01
    injector._worker_reconnect_backoff_seconds = 0.01

    thread = threading.Thread(target=injector._run_control_provisioner, daemon=True)
    thread.start()
    thread.join(timeout=10)
    assert not thread.is_alive()
    assert not [sql for sql in injector.executed_sql if "INSERT INTO" in sql]


def test_xid_recon_sweeper_resumes_only_aged_paused_rows():
    """The recon sweeper resumes paused rows older than its
    hold window and exits permanently once its own control row leaves the
    running state (stopping the sweeper first is an accepted equivalent
    repair)."""

    class FakeCursor:
        def __init__(self, sweeper):
            self.sweeper = sweeper

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, sql, args=None):
            self.last_sql = sql
            self.sweeper.executed_sql.append(sql)

        def fetchone(self):
            states = self.sweeper.sweeper_row_states
            state = states.pop(0) if states else "cancelled"
            return (state,)

        def fetchall(self):
            if "UPDATE" in self.last_sql:
                return [("ledger_settlement_replay",)]
            return []

    class FakeConn:
        def __init__(self, sweeper):
            self.sweeper = sweeper
            self.autocommit = False

        def cursor(self):
            return FakeCursor(self.sweeper)

        def close(self):
            pass

    import threading

    class SweeperInjector(PgSystemFailureXidWraparoundInjector):
        def __init__(self, sweeper_row_states):
            super().__init__()
            self.sweeper_row_states = list(sweeper_row_states)
            self.executed_sql = []

        def _connect_noise(self, app_name):
            assert app_name == self._recon_sweeper_app_name
            return FakeConn(self)

    injector = SweeperInjector(["running", "cancelled"])
    injector.batch_control_table = "ops_batch_control"
    injector._stop_event = threading.Event()
    injector._recon_sweeper_interval_seconds = 0.01
    injector._worker_reconnect_backoff_seconds = 0.01

    thread = threading.Thread(target=injector._run_recon_sweeper, daemon=True)
    thread.start()
    thread.join(timeout=10)
    assert not thread.is_alive()

    updates = [sql for sql in injector.executed_sql if "UPDATE" in sql]
    assert len(updates) == 1
    assert "state = 'paused'" in updates[0]
    assert f"interval '{injector._recon_sweeper_resume_hold_seconds} seconds'" in updates[0]


def test_multi_cause_stale_lock_persistent_contract_checks_stale_statistics():
    class FakeEnv:
        def execute_sql(self, sql):
            return json.dumps({
                "status": "success",
                "result": [[
                    "checkout_customer_profile",
                    "checkout_order_event",
                    "checkout_session_state",
                    1_500_000,
                    300_000,
                    1_200_000,
                    True,
                    True,
                ]],
            })

    injector = PgQueryPerfStaleStatsLockContentionInjector()
    injector.env = FakeEnv()
    injector.customer_table = "checkout_customer_profile"
    injector.order_table = "checkout_order_event"
    injector.lock_table = "checkout_session_state"
    injector.initial_orders = 300_000
    injector.stale_orders = 1_200_000

    injector._verify_persistent_state()


def test_connection_bloat_fault_image_requires_exact_case_row_count():
    class FakeEnv:
        def execute_sql(self, sql):
            return json.dumps({
                "status": "success",
                "result": [["order_history", 31_998, True]],
            })

    injector = PgSystemFailureConnectionBloatInjector()
    injector.env = FakeEnv()
    injector.table = "order_history"
    injector.app_role = "order_app"
    injector.row_count = 24_000

    with pytest.raises(RuntimeError, match="row_count=31998, expected_rows=24000"):
        injector._verify_persistent_state()


def test_multi_cause_stale_lock_visibility_uses_causal_state_not_wall_clock():
    class FakeEnv:
        def execute_sql(self, sql):
            assert "interval '5 seconds'" not in sql
            return json.dumps({
                "status": "success",
                "result": [[1, 3, 300_000, 1_200_000]],
            })

    injector = PgQueryPerfStaleStatsLockContentionInjector()
    injector.env = FakeEnv()
    injector.holder_app = "order-api"
    injector.waiter_app = "checkout-worker"
    injector.order_table = "checkout_order_event"
    injector.initial_orders = 300_000
    injector.stale_orders = 1_200_000

    injector._wait_until_observable(timeout=1)


def _io_saturation_injector(env, fault_variant="maintenance_io_saturation"):
    injector = PgBusinessChangeIoSaturationInjector()
    injector.env = env
    injector.fault_variant = fault_variant
    injector.minimum_io_mb_per_sec = 20.0
    injector.io_observability_timeout_seconds = 1.0
    return injector


def test_io_saturation_activation_requires_evaluator_throughput():
    class FakeEnv:
        def query_metrics(self, metric_type):
            assert metric_type == "disk_io"
            return json.dumps({
                "status": "success",
                "metric": "disk_io",
                "kind": "series",
                "series": {
                    "postgres": {
                        "timestamps": ["2026-07-28 10:00:00"],
                        "read_mb_per_second": [4.0],
                        "write_mb_per_second": [21.0],
                    },
                },
            })

        def execute_sql(self, sql):
            return json.dumps({"status": "success", "result": [[0]]})

    injector = _io_saturation_injector(FakeEnv())

    injector._wait_for_io_saturation()


def test_io_saturation_activation_accepts_temp_spill_growth():
    class FakeEnv:
        def __init__(self):
            self.temp_bytes = 100

        def query_metrics(self, metric_type):
            return json.dumps({
                "status": "success",
                "metric": "disk_io",
                "kind": "series",
                "series": {
                    "postgres": {
                        "timestamps": ["2026-07-28 10:00:00"],
                        "read_mb_per_second": [1.0],
                        "write_mb_per_second": [1.0],
                    },
                },
            })

        def execute_sql(self, sql):
            self.temp_bytes += 30_000_000
            return json.dumps({"status": "success", "result": [[self.temp_bytes]]})

    injector = _io_saturation_injector(FakeEnv())

    injector._wait_for_io_saturation()


def test_io_saturation_wal_variant_ignores_temp_spill_signal():
    class FakeEnv:
        def query_metrics(self, metric_type):
            return json.dumps({
                "status": "success",
                "metric": "disk_io",
                "kind": "series",
                "series": {
                    "postgres": {
                        "timestamps": ["2026-07-28 10:00:00"],
                        "read_mb_per_second": [1.0],
                        "write_mb_per_second": [1.0],
                    },
                },
            })

        def execute_sql(self, sql):
            return json.dumps({"status": "success", "result": [[10 ** 9]]})

    injector = _io_saturation_injector(FakeEnv(), fault_variant="wal_archive_backlog")
    with pytest.raises(RuntimeError, match="throughput did not become observable"):
        injector._wait_for_io_saturation()
