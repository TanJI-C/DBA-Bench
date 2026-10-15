"""Role/database precedence and login-boundary regressions for temp-file OP."""
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
from src.scenarios.evaluation.postgres.system_failure import temp_file_explosion as op
from src.scenarios.postgres.system_failure.temp_file_explosion import PgSystemFailureTempFileExplosionScenario


@pytest.mark.parametrize("limit_kb,source,passed", [
    (32768, "user", True), (65536, "database user", True),
    (32767, "user", False), (65537, "database user", False),
    (-1, "default", False), (65536, "database", False),
    (65536, "configuration file", False), (65536, "session", False),
])
def test_effective_limit_uses_fresh_report_login(monkeypatch, limit_kb, source, passed):
    env = SimpleNamespace(host="db", port=5433, dbname="business")
    case = PgSystemFailureTempFileExplosionScenario().cases[0]
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value.fetchone.return_value = limit_kb, source
    connect = MagicMock(return_value=connection)
    monkeypatch.setattr(op.psycopg2, "connect", connect)
    result = op.TempFileLimitVerifier().verify(SimpleNamespace(case_run=SimpleNamespace(env=env, case=case)))
    assert result.passed is passed
    connect.assert_called_once_with(
        host="db", port=5433, dbname="business", user=case.culprit_role,
        password=case.culprit_password, application_name="evaluator-temp-file-limit", connect_timeout=3,
    )
    assert result.actual["limit_kb"] == limit_kb
    connection.close.assert_called_once()


def test_report_login_failure_is_failed_outcome(monkeypatch):
    monkeypatch.setattr(op.psycopg2, "connect", MagicMock(side_effect=psycopg2.OperationalError("login rejected")))
    case = PgSystemFailureTempFileExplosionScenario().cases[0]
    env = SimpleNamespace(host="db", port=5432, dbname="business")
    result = op.TempFileLimitVerifier().verify(SimpleNamespace(case_run=SimpleNamespace(env=env, case=case)))
    assert not result.passed
    assert "login rejected" in result.actual["connection_error"]


@pytest.fixture(scope="module")
def live_env():
    if os.environ.get("DBA_BENCH_LIVE_TEMP_LIMIT") != "1":
        pytest.skip("set DBA_BENCH_LIVE_TEMP_LIMIT=1 for real PostgreSQL scope checks")
    name = "dba-temp-limit-" + uuid.uuid4().hex[:8]
    with reserve_host_ports(16460, (0,), owner=name) as lease:
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


def execute(env, sql):
    result = json.loads(env.execute_sql(sql))
    assert result["status"] == "success", result
    return result


@pytest.fixture(params=(0, 1))
def live_case(live_env, request):
    case = PgSystemFailureTempFileExplosionScenario().cases[request.param]
    execute(live_env, f"DROP ROLE IF EXISTS {case.culprit_role}; CREATE ROLE {case.culprit_role} LOGIN PASSWORD '{case.culprit_password}'")
    return case


@pytest.mark.parametrize("repair,passed", [
    ("role", True), ("role_database", True), ("both_scopes", True),
    ("target_overrides_bad_default", True), ("unrelated_bad_database", True),
    ("minimum", True), ("maximum", True),
    ("below_minimum", False), ("above_maximum", False),
    ("wrong_database", False), ("wrong_role", False),
    ("looser_target_override", False), ("unlimited_target_override", False),
    ("agent_session", False), ("database_wide_only", False),
    ("uncommitted", False), ("no_login", False),
])
def test_live_full_op_scope(live_env, live_case, repair, passed):
    case = live_case
    role = case.culprit_role
    execute(live_env, 'RESET temp_file_limit; ALTER DATABASE testdb RESET temp_file_limit; CREATE ROLE unrelated_temp_role')
    commands = {
        "role": f"ALTER ROLE {role} SET temp_file_limit='48MB'",
        "role_database": f"ALTER ROLE {role} IN DATABASE testdb SET temp_file_limit='48MB'",
        "both_scopes": f"ALTER ROLE {role} SET temp_file_limit='64MB'; ALTER ROLE {role} IN DATABASE testdb SET temp_file_limit='64MB'",
        "target_overrides_bad_default": f"ALTER ROLE {role} SET temp_file_limit='1GB'; ALTER ROLE {role} IN DATABASE testdb SET temp_file_limit='48MB'",
        "unrelated_bad_database": f"ALTER ROLE {role} SET temp_file_limit='48MB'; ALTER ROLE {role} IN DATABASE postgres SET temp_file_limit='1GB'",
        "minimum": f"ALTER ROLE {role} SET temp_file_limit='32MB'",
        "maximum": f"ALTER ROLE {role} SET temp_file_limit='64MB'",
        "below_minimum": f"ALTER ROLE {role} SET temp_file_limit='32767kB'",
        "above_maximum": f"ALTER ROLE {role} SET temp_file_limit='65537kB'",
        "wrong_database": f"ALTER ROLE {role} IN DATABASE postgres SET temp_file_limit='64MB'",
        "wrong_role": "ALTER ROLE unrelated_temp_role SET temp_file_limit='64MB'",
        "looser_target_override": f"ALTER ROLE {role} SET temp_file_limit='64MB'; ALTER ROLE {role} IN DATABASE testdb SET temp_file_limit='1GB'",
        "unlimited_target_override": f"ALTER ROLE {role} SET temp_file_limit='64MB'; ALTER ROLE {role} IN DATABASE testdb SET temp_file_limit='-1'",
        "agent_session": "SET temp_file_limit='64MB'",
        "database_wide_only": "ALTER DATABASE testdb SET temp_file_limit='64MB'",
        "uncommitted": f"BEGIN; ALTER ROLE {role} SET temp_file_limit='64MB'",
        "no_login": f"ALTER ROLE {role} SET temp_file_limit='64MB'; ALTER ROLE {role} NOLOGIN",
    }
    try:
        execute(live_env, commands[repair])
        context = SimpleNamespace(case_run=SimpleNamespace(env=live_env, case=case))
        result = case.evaluator(live_env).OutcomePassFunc(context)
        assert result["OutcomePass"] is passed, result
        assert result["checks"]["culprit_temp_file_limit"]["pass"] is passed
    finally:
        execute(live_env, 'ROLLBACK; RESET temp_file_limit; ALTER DATABASE testdb RESET temp_file_limit; DROP ROLE unrelated_temp_role')


def test_live_role_limit_actually_stops_temp_spill(live_env, live_case):
    case = live_case
    execute(live_env, f"ALTER ROLE {case.culprit_role} SET temp_file_limit='32MB'")
    with closing(psycopg2.connect(host=live_env.host, port=live_env.port, dbname=live_env.dbname,
                                  user=case.culprit_role, password=case.culprit_password,
                                  options="-c statement_timeout=10000")) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
            assert cur.fetchone() == (1,)
            cur.execute("SET work_mem='64kB'")
            with pytest.raises(psycopg2.errors.ConfigurationLimitExceeded, match="temporary file size exceeds temp_file_limit"):
                cur.execute("SELECT count(*) FROM (SELECT repeat(md5(i::text),32) AS v FROM generate_series(1,100000) i ORDER BY v) s")
            cur.execute('SELECT 1')
            assert cur.fetchone() == (1,)
