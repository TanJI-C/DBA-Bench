import json
import threading
from types import SimpleNamespace

import psycopg2
import pytest

from src.execution.environments.postgres import PGEnv


class FakeSamplerConn:
    def close(self):
        pass


def _deployment(*, start_result=True, ready=True, restart_pg=None):
    return SimpleNamespace(
        restart_pg=restart_pg or (lambda: start_result),
        start_pg=lambda: start_result,
        stop_pg=lambda: True,
        reboot_machine=lambda: True,
        wait_for_ready=lambda timeout: ready,
        resources={"reboot_ready_timeout_sec": 5},
    )


def _env(deployment, allow_sampler_reconnect=True):
    env = PGEnv(
        deployment=deployment,
        allow_sampler_reconnect=allow_sampler_reconnect,
    )
    env._ensure_connection = lambda: True
    return env


def _start_stub_sampler(env):
    def stub_loop():
        env._sampler_stop.wait(timeout=5)

    env._resource_sampler_loop = stub_loop
    env._start_sampler()
    assert env._sampler_thread.is_alive()


def _kill_sampler(env, error="PostgreSQL sampler could not reconnect within the allowed restart windows"):
    env._sampler_stop.set()
    thread = threading.Thread(target=lambda: None)
    thread.start()
    thread.join()
    env._sampler_thread = thread
    env._sampler_failure = RuntimeError(error)


def test_accept_expected_sampler_failure_requires_pending_failure():
    env = _env(_deployment())
    env._expected_sampler_disconnect_reason = "manage_instance('start')"
    assert env._accept_expected_sampler_failure() is False
    assert env._expected_sampler_disconnect_reason == "manage_instance('start')"


def test_accept_expected_sampler_failure_swallows_pending_failure_once():
    env = _env(_deployment())
    env._sampler_failure = RuntimeError("connection refused")
    env._expected_sampler_disconnect_reason = "manage_instance('start')"
    assert env._accept_expected_sampler_failure() is True
    assert env._sampler_failure is None
    assert env._expected_sampler_disconnect_reason is None
    assert env._expected_sampler_disconnect_evidence is None


def test_raise_sampler_failure_without_expected_reason_still_raises():
    env = _env(_deployment())
    env._sampler_failure = RuntimeError("cpu counter moved backwards")
    with pytest.raises(RuntimeError, match="cpu counter moved backwards"):
        env._raise_sampler_failure()


def test_stop_sampler_accepts_stale_failure_when_disconnect_is_expected():
    env = _env(_deployment())
    _kill_sampler(env)
    env._expected_sampler_disconnect_reason = "manage_instance('restart')"
    env._stop_sampler()
    assert env._sampler_failure is None
    assert env._sampler_thread is None


def test_sampler_ensure_conn_recovers_in_a_later_reconnect_round(monkeypatch):
    env = _env(_deployment())
    env.SAMPLER_RECONNECT_TIMEOUT_SEC = 0.05
    attempts = {"count": 0}

    def fake_connect(**kwargs):
        attempts["count"] += 1
        if attempts["count"] <= 3:
            raise RuntimeError(f"connect refused {attempts['count']}")
        return FakeSamplerConn()

    monkeypatch.setattr(psycopg2, "connect", fake_connect)
    conn = env._sampler_ensure_conn()
    assert isinstance(conn, FakeSamplerConn)
    # Three refused attempts cannot fit into the first 180s-style window alone,
    # so recovery happened only because a fresh window was opened.
    assert attempts["count"] >= 3


def test_sampler_ensure_conn_raises_after_all_reconnect_rounds_exhausted(monkeypatch):
    env = _env(_deployment())
    env.SAMPLER_RECONNECT_TIMEOUT_SEC = 0.02
    env.SAMPLER_RECONNECT_MAX_ROUNDS = 2
    attempts = {"count": 0}

    def fake_connect(**kwargs):
        attempts["count"] += 1
        raise RuntimeError(f"connect refused {attempts['count']}")

    monkeypatch.setattr(psycopg2, "connect", fake_connect)
    with pytest.raises(RuntimeError, match="rounds=2"):
        env._sampler_ensure_conn()
    assert attempts["count"] >= 4


def test_sampler_ensure_conn_without_reconnect_dies_on_first_failure(monkeypatch):
    env = _env(_deployment(), allow_sampler_reconnect=False)
    attempts = {"count": 0}

    def fake_connect(**kwargs):
        attempts["count"] += 1
        raise RuntimeError("connect refused once")

    monkeypatch.setattr(psycopg2, "connect", fake_connect)
    with pytest.raises(RuntimeError, match="connect refused once"):
        env._sampler_ensure_conn()
    assert attempts["count"] == 1


def test_manage_instance_start_revives_dead_sampler_and_clears_stale_failure():
    env = _env(_deployment())
    _kill_sampler(env)
    try:
        result = json.loads(env.manage_instance("start"))
        assert result == {"status": "success", "action": "start"}
        assert env._sampler_failure is None
        assert env._expected_sampler_disconnect_reason is None
        assert env._sampler_thread is not None and env._sampler_thread.is_alive()
    finally:
        env._stop_sampler()


def test_manage_instance_start_failure_still_resumes_sampler():
    env = _env(_deployment(start_result=True, ready=False))
    _kill_sampler(env)
    try:
        result = json.loads(env.manage_instance("start"))
        assert result == {"status": "error", "error": "PG not ready after start"}
        # The stale reconnect failure from the instance downtime is accepted and
        # sampling resumes: the instance may still finish crash recovery later.
        assert env._sampler_failure is None
        assert env._sampler_thread is not None and env._sampler_thread.is_alive()
    finally:
        env._stop_sampler()


def test_manage_instance_restart_stops_sampler_during_action_and_resumes():
    observed = {}
    deployment = _deployment()

    def restart_pg():
        observed["sampler_during_restart"] = env._sampler_thread
        return True

    deployment.restart_pg = restart_pg
    env = _env(deployment)
    _start_stub_sampler(env)
    try:
        result = json.loads(env.manage_instance("restart"))
        assert result == {"status": "success", "action": "restart"}
        assert observed["sampler_during_restart"] is None
        assert env._sampler_thread is not None and env._sampler_thread.is_alive()
        assert env._expected_sampler_disconnect_reason is None
    finally:
        env._stop_sampler()


def test_manage_instance_lifecycle_leaves_provider_managed_sampler_alone():
    env = _env(_deployment())
    env._scenario_metric_provider = object()
    result = json.loads(env.manage_instance("start"))
    assert result == {"status": "success", "action": "start"}
    assert env._sampler_thread is None


def test_manage_instance_stop_keeps_failure_semantics_unchanged():
    env = _env(_deployment())
    result = json.loads(env.manage_instance("stop"))
    assert result == {"status": "success", "action": "stop"}
    assert env._sampler_thread is None


def test_sampler_lag_strike_counts_only_over_tolerance_ticks():
    env = _env(_deployment())
    env._sampler_record_tick_lag(6.0)
    assert env._sampler_lag_strikes == 0
    env._sampler_record_tick_lag(6.1)
    assert env._sampler_lag_strikes == 1


def test_sampler_lag_strike_raises_after_limit_consecutive_strikes():
    env = _env(_deployment())
    for _ in range(4):
        env._sampler_record_tick_lag(7.0)
    assert env._sampler_lag_strikes == 4
    with pytest.raises(RuntimeError, match="strikes=5"):
        env._sampler_record_tick_lag(7.0)


def test_sampler_lag_strike_decays_on_in_tolerance_tick_with_zero_floor():
    env = _env(_deployment())
    env._sampler_record_tick_lag(7.0)
    env._sampler_record_tick_lag(7.0)
    env._sampler_record_tick_lag(1.0)
    assert env._sampler_lag_strikes == 1
    for _ in range(5):
        env._sampler_record_tick_lag(1.0)
    assert env._sampler_lag_strikes == 0


def test_sampler_lag_strike_decay_prevents_error_after_transient_stall():
    env = _env(_deployment())
    env._sampler_record_tick_lag(30.0)
    env._sampler_record_tick_lag(0.1)
    assert env._sampler_lag_strikes == 0
    for _ in range(4):
        env._sampler_record_tick_lag(7.0)
    with pytest.raises(RuntimeError, match="strikes=5"):
        env._sampler_record_tick_lag(7.0)


def test_start_sampler_resets_lag_strike_count():
    env = _env(_deployment())
    env._sampler_lag_strikes = 4
    try:
        _start_stub_sampler(env)
        assert env._sampler_lag_strikes == 0
    finally:
        env._stop_sampler()


def test_save_snapshot_pauses_sampler_across_postgres_restart(monkeypatch):
    # 快照保存会 stop/start PostgreSQL；sampler 必须在停机窗口内暂停并在
    # 完成后恢复，否则停机会被记成 sampler 故障并在 teardown 使整个 run 失败。
    observed = {}
    deployment = _deployment()

    def stop_pg():
        observed["sampler_during_stop"] = env._sampler_thread
        return True

    deployment.stop_pg = stop_pg

    env = _env(deployment)
    env.execute_sql = lambda sql: json.dumps({"status": "success"})
    env.reconnect = lambda: True
    env.refresh_pgss_baseline = lambda: None

    env.deployment = deployment
    deployment.is_container_running = lambda: True
    deployment.container_name = "fake-container"

    def _fake_docker_commit(command, capture_output, text):
        assert command[:1] == ["docker"] and command[1] == "commit"

        class _Result:
            returncode = 0
            stdout = snapshot_name_holder["name"]
            stderr = ""

        return _Result()

    snapshot_name_holder = {"name": "fake:snapshot"}
    monkeypatch.setattr("subprocess.run", _fake_docker_commit)

    _start_stub_sampler(env)
    try:
        env.save_snapshot(snapshot_name_holder["name"], {"aiopsbench.image_kind": "fault"})
        assert observed["sampler_during_stop"] is None
        assert env._sampler_thread is not None and env._sampler_thread.is_alive()
        assert env._sampler_failure is None
    finally:
        env._stop_sampler()


def test_save_snapshot_resumes_sampler_after_checkpoint_failure():
    # 即使 CHECKPOINT 失败提前抛错，sampler 也必须在 finally 中恢复。
    env = _env(_deployment())

    def _fail(sql):
        return json.dumps({"status": "error", "error": "checkpoint failed"})

    env.execute_sql = _fail
    _start_stub_sampler(env)
    try:
        with pytest.raises(RuntimeError, match="checkpoint failed before snapshot"):
            env.save_snapshot("fake:snapshot", {})
        assert env._sampler_thread is not None and env._sampler_thread.is_alive()
    finally:
        env._stop_sampler()
