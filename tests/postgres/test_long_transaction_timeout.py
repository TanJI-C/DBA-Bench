"""Fresh-login timeout checks, precedence, and complete OP for all five LTX Cases."""
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
from src.protocols.report import StructuredReport
from src.scenarios.base import CaseRun
from src.scenarios.evaluation.protocol import EvaluationContext
from src.scenarios.evaluation.postgres.health_check import long_running_tx as op
from src.scenarios.postgres.health_check.long_running_tx import PgHealthCheckLongRunningTxScenario


SCENARIO = PgHealthCheckLongRunningTxScenario()


@pytest.mark.parametrize("timeout_ms,passed", [
    (0, False), (29999, False), (30000, True), (300000, True),
    (900000, True), (900001, False), (7200000, False),
])
def test_timeout_reads_new_business_connection_and_preserves_interval(timeout_ms, passed):
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value.fetchone.return_value = timeout_ms, "database user"
    env = SimpleNamespace(user="business_login", dbname="business_db", open_workload_connection=MagicMock(return_value=conn))
    result = op.IdleTransactionTimeoutVerifier().verify(SimpleNamespace(case_run=SimpleNamespace(env=env)))
    assert result.passed is passed
    assert result.actual == {"timeout_ms": timeout_ms, "source": "database user", "role": "business_login", "database": "business_db"}
    env.open_workload_connection.assert_called_once_with("evaluator-idle-transaction-timeout")
    conn.close.assert_called_once()


def test_business_login_failure_is_failed_outcome():
    env = SimpleNamespace(user="business_login", dbname="business_db",
                          open_workload_connection=MagicMock(side_effect=psycopg2.OperationalError("login rejected")))
    result = op.IdleTransactionTimeoutVerifier().verify(SimpleNamespace(case_run=SimpleNamespace(env=env)))
    assert not result.passed
    assert "login rejected" in result.actual["connection_error"]
    assert "role=business_login, database=business_db" in result.evidence[0]


def test_query_error_propagates_and_closes_connection():
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value.execute.side_effect = psycopg2.ProgrammingError("query failed")
    env = SimpleNamespace(open_workload_connection=MagicMock(return_value=conn))
    with pytest.raises(psycopg2.ProgrammingError, match="query failed"):
        op.IdleTransactionTimeoutVerifier().verify(SimpleNamespace(case_run=SimpleNamespace(env=env)))
    conn.close.assert_called_once()


def execute(env, sql):
    result = json.loads(env.execute_sql(sql))
    assert result["status"] == "success", result
    return result


@pytest.fixture(scope="module")
def live_env():
    if os.environ.get("DBA_BENCH_LIVE_LTX_TIMEOUT") != "1":
        pytest.skip("set DBA_BENCH_LIVE_LTX_TIMEOUT=1 for real PostgreSQL scope checks")
    name = "dba-ltx-timeout-" + uuid.uuid4().hex[:8]
    with reserve_host_ports(16480, (0,), owner=name) as lease:
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
            execute(env, "CREATE TABLE customer(id integer); CREATE ROLE unrelated_ltx_role")
            yield env
            env._conn.close()
        finally:
            subprocess.run(["docker", "rm", "-f", name], check=True, capture_output=True)


@pytest.fixture(params=SCENARIO.cases, ids=lambda case: case.case_id)
def live_context(live_env, request):
    case = request.param
    with closing(psycopg2.connect(host=live_env.host, port=live_env.port, dbname=live_env.dbname,
                                  user=live_env.user, password=live_env.password,
                                  application_name=case.decoy_app_name,
                                  options="-c idle_in_transaction_session_timeout=2h")):
        action = {"api": "execute_sql", "args": {"sql_query":
                  f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name='{case.blocker_app_name}'"},
                  "result": {"status": "success"}}
        run = CaseRun(run_id=f"scope-{case.case_id}", scenario=SCENARIO, case=case, env=live_env, action_history=[action])
        yield EvaluationContext(run, StructuredReport.from_mapping(case.reference_report))


@pytest.mark.parametrize("repair,passed", [
    ("none", False), ("agent_session", False), ("wrong_database", False), ("wrong_role", False),
    ("role", True), ("role_database", True), ("database", True), ("instance", True),
    ("both_scopes", True), ("target_overrides_bad_default", True), ("unrelated_bad_database", True),
    ("zero_target_override", False), ("long_target_override", False), ("role_overrides_database", False),
    ("minimum", True), ("maximum", True), ("below_minimum", False), ("above_maximum", False),
    ("uncommitted", False), ("no_login", False),
])
def test_live_full_op_scope(live_env, live_context, repair, passed):
    role = live_env.user
    commands = {
        "none": "SELECT 1",
        "agent_session": "SET idle_in_transaction_session_timeout='5min'",
        "wrong_database": f"ALTER ROLE {role} IN DATABASE postgres SET idle_in_transaction_session_timeout='5min'",
        "wrong_role": "ALTER ROLE unrelated_ltx_role SET idle_in_transaction_session_timeout='5min'",
        "role": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'",
        "role_database": f"ALTER ROLE {role} IN DATABASE testdb SET idle_in_transaction_session_timeout='5min'",
        "database": "ALTER DATABASE testdb SET idle_in_transaction_session_timeout='5min'",
        "instance": "ALTER SYSTEM SET idle_in_transaction_session_timeout='5min'",
        "both_scopes": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} IN DATABASE testdb SET idle_in_transaction_session_timeout='5min'",
        "target_overrides_bad_default": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='2h'; ALTER ROLE {role} IN DATABASE testdb SET idle_in_transaction_session_timeout='5min'",
        "unrelated_bad_database": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} IN DATABASE postgres SET idle_in_transaction_session_timeout='2h'",
        "zero_target_override": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} IN DATABASE testdb SET idle_in_transaction_session_timeout=0",
        "long_target_override": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} IN DATABASE testdb SET idle_in_transaction_session_timeout='2h'",
        "role_overrides_database": f"ALTER DATABASE testdb SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} SET idle_in_transaction_session_timeout=0",
        "minimum": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='30s'",
        "maximum": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='15min'",
        "below_minimum": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='29999ms'",
        "above_maximum": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='900001ms'",
        "uncommitted": f"BEGIN; ALTER ROLE {role} IN DATABASE testdb SET idle_in_transaction_session_timeout='5min'",
        "no_login": f"ALTER ROLE {role} SET idle_in_transaction_session_timeout='5min'; ALTER ROLE {role} NOLOGIN",
    }
    try:
        execute(live_env, commands[repair])
        if repair == "instance":
            reload_timeout(live_env, 300000)
        started = time.monotonic()
        result = live_context.case_run.case.evaluator(live_env).OutcomePassFunc(live_context)
        elapsed = time.monotonic() - started
        assert result["OutcomePass"] is passed, result
        assert result["checks"]["idle_transaction_timeout"]["pass"] is passed
        assert elapsed < 120, f"OP took {elapsed:.3f}s: {repair}"
        print(f"{live_context.case_id} {repair}: OP={result['OutcomePass']}, {elapsed:.3f}s")
    finally:
        execute(live_env, f"ROLLBACK; RESET idle_in_transaction_session_timeout; ALTER ROLE {role} LOGIN; "
                f"ALTER ROLE {role} RESET idle_in_transaction_session_timeout; "
                f"ALTER ROLE {role} IN DATABASE testdb RESET idle_in_transaction_session_timeout; "
                f"ALTER ROLE {role} IN DATABASE postgres RESET idle_in_transaction_session_timeout; "
                "ALTER DATABASE testdb RESET idle_in_transaction_session_timeout; "
                "ALTER ROLE unrelated_ltx_role RESET idle_in_transaction_session_timeout")
        if repair == "instance":
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


def test_live_uses_environment_login_without_fault_startup_override(live_env):
    execute(live_env, "CREATE ROLE ltx_business_login LOGIN PASSWORD 'ltx_test_password'; "
            "ALTER ROLE ltx_business_login IN DATABASE testdb SET idle_in_transaction_session_timeout='5min'")
    env = PGEnv(host=live_env.host, port=live_env.port, dbname=live_env.dbname,
                user="ltx_business_login", password="ltx_test_password", tool_profile="no_knowledge")
    result = op.IdleTransactionTimeoutVerifier().verify(SimpleNamespace(case_run=SimpleNamespace(env=env)))
    assert result.passed
    assert result.actual["role"] == "ltx_business_login"
    assert result.actual["timeout_ms"] == 300000
    assert result.actual["source"] == "database user"
    with closing(psycopg2.connect(host=env.host, port=env.port, dbname=env.dbname,
                                  user=env.user, password=env.password,
                                  options="-c idle_in_transaction_session_timeout=2h")) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT setting::bigint FROM pg_settings WHERE name='idle_in_transaction_session_timeout'")
            assert cur.fetchone() == (7200000,)
