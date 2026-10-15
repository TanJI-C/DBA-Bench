"""Fresh checkout-login and configuration-precedence regressions for both storm Cases."""
import json
import os
import subprocess
import time
import uuid
from contextlib import closing
from types import SimpleNamespace
from unittest.mock import MagicMock

import psycopg2
import pytest

from src.execution.environments.postgres import PGEnv
from src.execution.host_ports import reserve_host_ports
from src.scenarios.evaluation.postgres.system_failure import connection_storm as op
from src.scenarios.postgres.system_failure.connection_storm import PgSystemFailureConnectionStormScenario


CASES = PgSystemFailureConnectionStormScenario().cases


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
@pytest.mark.parametrize("timeout_ms,source,passed", [
    (30000, "user", True), (30000, "database user", True),
    (30000, "database", True), (30000, "configuration file", True),
    (1, "user", True), (0, "database user", False), (0, "default", False),
])
def test_timeout_uses_fresh_checkout_login(monkeypatch, case, timeout_ms, source, passed):
    env = SimpleNamespace(host="db", port=5433, dbname="business")
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value.fetchone.return_value = timeout_ms, source
    connect = MagicMock(return_value=connection)
    monkeypatch.setattr(op.psycopg2, "connect", connect)
    result = op.PoolTimeoutGuardVerifier().verify(SimpleNamespace(case_run=SimpleNamespace(env=env, case=case)))
    assert result.passed is passed
    connect.assert_called_once_with(
        host="db", port=5433, dbname="business", user=case.app_role,
        password=case.app_password, application_name="evaluator-pool-timeout", connect_timeout=3,
    )
    assert result.actual == {"timeout_ms": timeout_ms, "source": source, "role": case.app_role, "database": "business"}
    connection.close.assert_called_once()


def test_checkout_login_failure_is_failed_outcome(monkeypatch):
    monkeypatch.setattr(op.psycopg2, "connect", MagicMock(side_effect=psycopg2.OperationalError("login rejected")))
    env = SimpleNamespace(host="db", port=5432, dbname="business")
    result = op.PoolTimeoutGuardVerifier().verify(SimpleNamespace(case_run=SimpleNamespace(env=env, case=CASES[0])))
    assert not result.passed
    assert "login rejected" in result.actual["connection_error"]
    assert "database=business" in result.evidence[0]


def test_probe_sql_error_propagates_and_closes_connection(monkeypatch):
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value.execute.side_effect = psycopg2.ProgrammingError("bad query")
    monkeypatch.setattr(op.psycopg2, "connect", MagicMock(return_value=connection))
    env = SimpleNamespace(host="db", port=5432, dbname="business")
    with pytest.raises(psycopg2.ProgrammingError, match="bad query"):
        op.PoolTimeoutGuardVerifier().verify(SimpleNamespace(case_run=SimpleNamespace(env=env, case=CASES[0])))
    connection.close.assert_called_once()


def execute(env, sql):
    result = json.loads(env.execute_sql(sql))
    assert result["status"] == "success", result
    return result


@pytest.fixture(scope="module")
def live_env():
    if os.environ.get("DBA_BENCH_LIVE_STORM_TIMEOUT") != "1":
        pytest.skip("set DBA_BENCH_LIVE_STORM_TIMEOUT=1 for real PostgreSQL scope checks")
    name = "dba-storm-timeout-" + uuid.uuid4().hex[:8]
    with reserve_host_ports(16470, (0,), owner=name) as lease:
        port = lease.ports[0]
        subprocess.run([
            "docker", "run", "-d", "--name", name, "--cpus=1", "--memory=512m",
            "-e", "POSTGRES_PASSWORD=password", "-e", "POSTGRES_DB=testdb",
            "-p", f"127.0.0.1:{port}:5432", "postgres:16",
        ], check=True, capture_output=True)
        try:
            for _ in range(360):
                ready = subprocess.run(["docker", "exec", name, "pg_isready", "-h", "127.0.0.1", "-U", "postgres"],
                                       capture_output=True, timeout=5)
                if ready.returncode == 0:
                    break
                time.sleep(.5)
            else:
                raise RuntimeError(f"PostgreSQL startup timeout: container={name}")
            env = PGEnv(host="127.0.0.1", port=port, dbname="testdb", password="password", tool_profile="no_knowledge")
            yield env
            env._conn.close()
        finally:
            subprocess.run(["docker", "rm", "-f", name], check=True, capture_output=True)


@pytest.fixture(params=CASES, ids=lambda case: case.case_id)
def live_case(live_env, request):
    case = request.param
    execute(live_env, f"DROP ROLE IF EXISTS {case.app_role}; CREATE ROLE {case.app_role} LOGIN PASSWORD '{case.app_password}'")
    connections = []
    try:
        for app in case.preserved_bystander_apps:
            conn = psycopg2.connect(host=live_env.host, port=live_env.port, dbname=live_env.dbname,
                                    user="postgres", password="password", application_name=app)
            connections.append(conn)
        yield case
    finally:
        for conn in connections:
            conn.close()


@pytest.mark.parametrize("repair,passed", [
    ("none", False), ("role", True), ("role_database", True), ("both_scopes", True),
    ("target_overrides_zero_default", True), ("unrelated_zero_database", True),
    ("database_wide", True), ("instance_wide", True),
    ("wrong_database", False), ("wrong_role", False), ("zero_target_override", False),
    ("role_overrides_database", False), ("agent_session", False),
    ("agent_session_and_wrong_database", False), ("uncommitted", False),
    ("no_login", False), ("connection_limit_zero", False),
])
def test_live_full_op_scope(live_env, live_case, repair, passed):
    case = live_case
    role = case.app_role
    execute(live_env, 'RESET idle_in_transaction_session_timeout; CREATE ROLE unrelated_storm_role')
    commands = {
        "none": "SELECT 1",
        "role": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'",
        "role_database": f"ALTER ROLE {role} IN DATABASE testdb SET idle_in_transaction_session_timeout='5min'",
        "both_scopes": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} IN DATABASE testdb SET idle_in_transaction_session_timeout='5min'",
        "target_overrides_zero_default": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout=0; ALTER ROLE {role} IN DATABASE testdb SET idle_in_transaction_session_timeout='5min'",
        "unrelated_zero_database": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} IN DATABASE postgres SET idle_in_transaction_session_timeout=0",
        "database_wide": "ALTER DATABASE testdb SET idle_in_transaction_session_timeout='5min'",
        "instance_wide": "ALTER SYSTEM SET idle_in_transaction_session_timeout='5min'",
        "wrong_database": f"ALTER ROLE {role} IN DATABASE postgres SET idle_in_transaction_session_timeout='5min'",
        "wrong_role": "ALTER ROLE unrelated_storm_role SET idle_in_transaction_session_timeout='5min'",
        "zero_target_override": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} IN DATABASE testdb SET idle_in_transaction_session_timeout=0",
        "role_overrides_database": f"ALTER DATABASE testdb SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} SET idle_in_transaction_session_timeout=0",
        "agent_session": "SET idle_in_transaction_session_timeout='5min'",
        "agent_session_and_wrong_database": f"SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} IN DATABASE postgres SET idle_in_transaction_session_timeout='5min'",
        "uncommitted": f"BEGIN; ALTER ROLE {role} IN DATABASE testdb SET idle_in_transaction_session_timeout='5min'",
        "no_login": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} NOLOGIN",
        "connection_limit_zero": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} CONNECTION LIMIT 0",
    }
    try:
        execute(live_env, commands[repair])
        if repair == "instance_wide":
            reload_timeout(live_env, 300000)
        context = SimpleNamespace(case_run=SimpleNamespace(env=live_env, case=case))
        started = time.monotonic()
        result = case.evaluator(live_env).OutcomePassFunc(context)
        elapsed = time.monotonic() - started
        assert result["OutcomePass"] is passed, result
        assert result["checks"]["pool_timeout_guard"]["pass"] is passed
        assert elapsed < 120, f"OP took {elapsed:.3f}s: {repair}"
        print(f"{case.case_id} {repair}: OP={result['OutcomePass']}, {elapsed:.3f}s")
    finally:
        execute(live_env, 'ROLLBACK; RESET idle_in_transaction_session_timeout; ALTER DATABASE testdb RESET idle_in_transaction_session_timeout; DROP ROLE unrelated_storm_role')
        if repair == "instance_wide":
            execute(live_env, "ALTER SYSTEM RESET idle_in_transaction_session_timeout")
            reload_timeout(live_env, 0)


def reload_timeout(env, expected_ms):
    execute(env, "SELECT pg_reload_conf()")
    for _ in range(50):
        result = execute(env, "SELECT setting::bigint FROM pg_settings WHERE name='idle_in_transaction_session_timeout'")
        if result["result"] == [[expected_ms]]:
            return
        time.sleep(.1)
    raise AssertionError(f"configuration reload did not apply timeout_ms={expected_ms}: {result}")


def test_live_timeout_actually_disconnects_idle_transaction(live_env, live_case):
    case = live_case
    execute(live_env, f"ALTER ROLE {case.app_role} IN DATABASE testdb SET idle_in_transaction_session_timeout='100ms'")
    with closing(psycopg2.connect(host=live_env.host, port=live_env.port, dbname=live_env.dbname,
                                  user=case.app_role, password=case.app_password)) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
            assert cur.fetchone() == (1,)
            time.sleep(.3)
            with pytest.raises(psycopg2.OperationalError):
                cur.execute('SELECT 1')
