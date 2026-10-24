"""Scope, PostgreSQL units, and fresh-login regressions for the compound I/O Case."""
import json
import os
import subprocess
import threading
import time
import uuid
from contextlib import closing
from types import SimpleNamespace
from unittest.mock import MagicMock

import psycopg2
import pytest

from src.database.postgres import connect_postgres_role, postgres_work_mem_bytes
from src.execution.environments.postgres import PGEnv
from src.execution.host_ports import reserve_host_ports
from src.scenarios.evaluation.postgres.business_change import io_saturation as op
from src.scenarios.postgres.business_change.io_saturation import (
    PgBusinessChangeIoSaturationInjector,
    PgBusinessChangeIoSaturationScenario,
)


def context(env, case):
    return SimpleNamespace(case_run=SimpleNamespace(env=env, case=case))


def test_report_login_failure_fails_outcome(monkeypatch):
    case = PgBusinessChangeIoSaturationScenario().cases[1]
    env = SimpleNamespace(dbname="testdb", user="postgres")
    monkeypatch.setattr(op, "connect_postgres_role", MagicMock(side_effect=psycopg2.OperationalError("login rejected")))
    check = op._CULPRIT_ROLE_WORK_MEM_RESTORED.verify(context(env, case))
    assert not check.passed
    assert check.actual["role"] == case.report_role_name
    assert "login rejected" in check.actual["connection_error"]
    with pytest.raises(psycopg2.OperationalError, match="login rejected"):
        op._DATABASE_WORK_MEM_PRESERVED.verify(context(env, case))


def test_probe_closes_connection_on_sql_error(monkeypatch):
    case = PgBusinessChangeIoSaturationScenario().cases[1]
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value.execute.side_effect = psycopg2.ProgrammingError("broken query")
    monkeypatch.setattr(op, "connect_postgres_role", MagicMock(return_value=connection))
    with pytest.raises(psycopg2.ProgrammingError, match="broken query"):
        op._CULPRIT_ROLE_WORK_MEM_RESTORED.verify(context(SimpleNamespace(dbname="testdb"), case))
    connection.close.assert_called_once()
    connection.commit.assert_not_called()


@pytest.fixture(scope="module")
def live_env():
    if os.environ.get("DBA_BENCH_LIVE_IO_SCOPE") != "1":
        pytest.skip("set DBA_BENCH_LIVE_IO_SCOPE=1 for real PostgreSQL scope checks")
    name = "dba-io-scope-" + uuid.uuid4().hex[:8]
    with reserve_host_ports(16490, (0,), owner=name) as lease:
        subprocess.run([
            "docker", "run", "-d", "--name", name, "--cpus=1",
            "--memory=1g", "-p", f"127.0.0.1:{lease.ports[0]}:5432",
            "aiopsbench-pg-audit-initialized:pg16", "-c", "shared_buffers=128MB",
            "-c", "work_mem=16MB", "-c", "shared_preload_libraries=pg_stat_statements",
        ], check=True, capture_output=True)
        try:
            for _ in range(120):
                ready = subprocess.run(["docker", "exec", name, "pg_isready", "-h", "127.0.0.1", "-U", "postgres"],
                                       capture_output=True, timeout=5)
                if ready.returncode == 0:
                    break
                time.sleep(.5)
            else:
                raise RuntimeError(f"PostgreSQL startup timeout: container={name}")
            env = PGEnv(host="127.0.0.1", port=lease.ports[0], dbname="testdb", password="password", tool_profile="no_knowledge")
            scenario = PgBusinessChangeIoSaturationScenario()
            case = scenario.cases[1]
            injector = PgBusinessChangeIoSaturationInjector()
            injector._configure(scenario.build_fault_plan(case)[0].config, env)
            injector._setup_schema()
            yield env, case, injector
            env._conn.close()
        finally:
            subprocess.run(["docker", "rm", "-fv", name], check=True, capture_output=True)


def execute(env, sql):
    result = json.loads(env.execute_sql(sql))
    assert result["status"] == "success", result
    return result


@pytest.fixture
def live_case(live_env):
    env, case, injector = live_env
    execute(env, f"""
        ALTER ROLE {case.report_role_name} LOGIN;
        ALTER ROLE {case.report_role_name} RESET work_mem;
        ALTER ROLE {case.report_role_name} IN DATABASE testdb SET work_mem='64kB';
        ALTER ROLE {case.report_role_name} IN DATABASE postgres RESET work_mem;
        ALTER ROLE {case.bi_role_name} SET work_mem='32MB';
        ALTER ROLE {case.bi_role_name} IN DATABASE testdb RESET work_mem;
        ALTER ROLE {case.bi_role_name} IN DATABASE postgres RESET work_mem;
        ALTER DATABASE testdb SET work_mem='64MB';
        UPDATE {case.schedule_table} SET last_heartbeat_at=now();
    """)
    try:
        yield env, case, injector
    finally:
        execute(env, "ROLLBACK; RESET work_mem")


@pytest.mark.parametrize("repair,passed", [
    ("reset", True), ("local_floor", True), ("bare_numeric", True),
    ("local_over_bad_role", True), ("other_database", True),
    ("below_floor", False), ("good_role_shadowed", False),
    ("wrong_database", False), ("database_only", False),
    ("agent_session", False), ("uncommitted", False), ("no_login", False),
])
def test_live_report_login_scope(live_case, repair, passed):
    env, case, injector = live_case
    role = case.report_role_name
    repairs = {
        "reset": f"ALTER ROLE {role} IN DATABASE testdb RESET work_mem",
        "local_floor": f"ALTER ROLE {role} IN DATABASE testdb SET work_mem='8MB'",
        "bare_numeric": f"ALTER ROLE {role} IN DATABASE testdb SET work_mem='8192'",
        "local_over_bad_role": f"ALTER ROLE {role} SET work_mem='64kB'; ALTER ROLE {role} IN DATABASE testdb SET work_mem='8MB'",
        "other_database": f"ALTER ROLE {role} IN DATABASE testdb RESET work_mem; ALTER ROLE {role} IN DATABASE postgres SET work_mem='64kB'",
        "below_floor": f"ALTER ROLE {role} IN DATABASE testdb SET work_mem='8191'",
        "good_role_shadowed": f"ALTER ROLE {role} SET work_mem='64MB'",
        "wrong_database": f"ALTER ROLE {role} IN DATABASE postgres SET work_mem='64MB'",
        "database_only": "ALTER DATABASE testdb SET work_mem='128MB'",
        "agent_session": "SET work_mem='128MB'",
        "uncommitted": f"BEGIN; ALTER ROLE {role} IN DATABASE testdb SET work_mem='64MB'",
        "no_login": f"ALTER ROLE {role} IN DATABASE testdb RESET work_mem; ALTER ROLE {role} NOLOGIN",
    }
    execute(env, repairs[repair])
    result = case.evaluator(env).OutcomePassFunc(context(env, case))
    assert result["OutcomePass"] is passed, result
    assert result["checks"]["culprit_role_work_mem_restored"]["pass"] is passed
    if repair not in ("uncommitted", "no_login"):
        # The runtime gate must reach the same scope/unit verdict as OP.
        with closing(connect_postgres_role(env, env.user, "gate-test")) as conn:
            with conn.cursor() as cur:
                assert injector._maintenance_pressure_active(cur) is not passed


@pytest.mark.parametrize("configuration,passed", [
    ("database_bare_floor", True), ("database_below_floor", False), ("database_removed", False),
    ("healthy_bare_floor", True), ("healthy_below_floor", False), ("healthy_removed", False),
    ("healthy_two_good_rows", True), ("healthy_low_override", False),
    ("healthy_other_database_low", True), ("healthy_bad_default_good_override", False),
])
def test_live_healthy_configuration_invariants(live_case, configuration, passed):
    env, case, _ = live_case
    execute(env, f"ALTER ROLE {case.report_role_name} IN DATABASE testdb RESET work_mem")
    role = case.bi_role_name
    commands = {
        "database_bare_floor": "ALTER DATABASE testdb SET work_mem='32768'",
        "database_below_floor": "ALTER DATABASE testdb SET work_mem='32767'",
        "database_removed": "ALTER DATABASE testdb RESET work_mem",
        "healthy_bare_floor": f"ALTER ROLE {role} SET work_mem='16384'",
        "healthy_below_floor": f"ALTER ROLE {role} SET work_mem='16383'",
        "healthy_removed": f"ALTER ROLE {role} RESET work_mem",
        "healthy_two_good_rows": f"ALTER ROLE {role} IN DATABASE testdb SET work_mem='64MB'",
        "healthy_low_override": f"ALTER ROLE {role} IN DATABASE testdb SET work_mem='64kB'",
        "healthy_other_database_low": f"ALTER ROLE {role} IN DATABASE postgres SET work_mem='64kB'",
        "healthy_bad_default_good_override": f"ALTER ROLE {role} SET work_mem='64kB'; ALTER ROLE {role} IN DATABASE testdb SET work_mem='64MB'",
    }
    execute(env, commands[configuration])
    # Evaluator normalization uses private rollback-only sessions, never the Agent session.
    before = execute(env, "SELECT current_setting('work_mem')")["result"]
    result = case.evaluator(env).OutcomePassFunc(context(env, case))
    assert result["OutcomePass"] is passed, result
    assert execute(env, "SELECT current_setting('work_mem')")["result"] == before
    invariant = "database_work_mem_preserved" if configuration.startswith("database_") else "healthy_role_setting_preserved"
    assert result["checks"][invariant]["pass"] is passed
    with closing(connect_postgres_role(env, env.user, "normalization-cleanup-test")) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_setting('work_mem')")
            expected = {"database_bare_floor": "32MB", "database_below_floor": "32767kB", "database_removed": "16MB"}
            expected = expected[configuration] if configuration.startswith("database_") else "64MB"
            assert cur.fetchone()[0] == expected
    assert execute(env, f"SELECT rolcanlogin FROM pg_roles WHERE rolname='{role}'")["result"] == [[False]]


def test_live_victim_exits_after_persistent_repair_with_stale_session(live_case):
    env, case, injector = live_case
    with closing(connect_postgres_role(env, case.report_role_name, "old-report-login")) as old:
        with old.cursor() as cur:
            assert postgres_work_mem_bytes(cur) == 64 * 1024
            execute(env, f"ALTER ROLE {case.report_role_name} IN DATABASE testdb SET work_mem='8192'; "
                         f"ALTER ROLE {case.report_role_name} IN DATABASE postgres SET work_mem='64kB'")
            assert postgres_work_mem_bytes(cur) == 64 * 1024
            assert not injector._maintenance_pressure_active(cur)

    execute(env, f"ALTER ROLE {case.report_role_name} IN DATABASE testdb SET work_mem='64kB'")
    worker = threading.Thread(target=injector._run_maintenance_slow_query, args=(0, case.slow_queries[0]))
    worker.start()
    try:
        deadline = time.monotonic() + 5
        while not injector._slow_query_connections and time.monotonic() < deadline:
            time.sleep(.05)
        assert injector._slow_query_connections
        assert worker.is_alive()
        execute(env, f"ALTER ROLE {case.report_role_name} IN DATABASE testdb SET work_mem='8192'")
        worker.join(timeout=5)
        assert not worker.is_alive(), "victim loop ignored the scoped repair"
        assert all(conn.closed for conn in injector._slow_query_connections)
    finally:
        injector._close_slow_query_connections()
        worker.join(timeout=5)
