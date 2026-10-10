"""Pins the ops_workload_controls key-disclosure contract for cache_pollution.

The recurrence_control_persisted OP check matches control_name exactly against
the case scan_app_name, so the legal key domain must be visible in the schema:
the CREATE TABLE DDL carries a CHECK constraint covering every case key, the
constraint is discoverable through information_schema, and non-case keys are
rejected by the database itself.
"""

import json
import re
import shutil
import subprocess
import time
import uuid
from unittest.mock import MagicMock

import pytest

from src.scenarios.postgres.query_perf.cache_pollution import (
    PgQueryPerfCachePollutionInjector,
    PgQueryPerfCachePollutionScenario,
)


CASE_CONTROL_KEYS = ("svc_audit_rollup", "billing_export_scan", "analytics-cursor-snapshot-11")


def _control_table_ddl(case_no):
    scenario = PgQueryPerfCachePollutionScenario()
    case = scenario.cases[case_no]
    injector = PgQueryPerfCachePollutionInjector()
    env = MagicMock()
    env.execute_sql.return_value = json.dumps({"status": "success", "result": []})
    injector._configure(scenario.build_fault_plan(case)[0].config, env)
    injector._setup_schema()
    executed_sql = "\n".join(str(call.args[0]) for call in env.execute_sql.call_args_list)
    match = re.search(rf"CREATE TABLE {case.control_table} \(.*?\);", executed_sql, re.DOTALL)
    assert match, executed_sql
    return case, match.group(0)


@pytest.mark.parametrize("case_no", [0, 1, 2])
def test_control_table_ddl_declares_check_over_all_case_keys(case_no):
    case, ddl = _control_table_ddl(case_no)
    assert "CHECK (control_name IN (" in ddl
    for key in CASE_CONTROL_KEYS:
        assert f"'{key}'" in ddl
    assert f"'{case.scan_app_name}'" in ddl


def _pg_config():
    import psycopg2

    if shutil.which("docker") is None:
        pytest.skip("docker is not available")
    container = f"aiopsbench-cache-pollution-ddl-{uuid.uuid4().hex[:8]}"
    subprocess.run(["docker", "rm", "-f", container], capture_output=True)
    subprocess.run(
        [
            "docker", "run", "-d", "--rm", "-P",
            "-e", "POSTGRES_PASSWORD=test", "-e", "POSTGRES_DB=testdb",
            "--name", container, "postgres:15",
        ],
        check=True, capture_output=True,
    )
    try:
        port_out = subprocess.run(
            ["docker", "port", container, "5432"], check=True, capture_output=True, text=True
        ).stdout
        config = {
            "host": "127.0.0.1",
            "port": int(port_out.strip().split(":")[-1]),
            "user": "postgres",
            "password": "test",
            "dbname": "testdb",
        }
        # pg_isready inside the container already reports ready for the throwaway
        # initdb bootstrap server, so readiness is probed with a real TCP login:
        # the mapped port only accepts queries once the final server is up.
        deadline = time.time() + 180
        while True:
            try:
                conn = psycopg2.connect(**config, connect_timeout=3)
            except psycopg2.OperationalError:
                if time.time() > deadline:
                    raise RuntimeError(
                        f"postgres test container {container} did not become ready: "
                        f"config={config}"
                    )
                time.sleep(2)
                continue
            conn.close()
            break
        yield config
    finally:
        subprocess.run(["docker", "rm", "-f", container], capture_output=True)


@pytest.fixture(scope="module")
def pg_server():
    yield from _pg_config()


def _connect(pg_server):
    import psycopg2

    return psycopg2.connect(**pg_server)


def test_check_constraint_is_visible_through_information_schema(pg_server):
    import psycopg2

    _, ddl = _control_table_ddl(0)
    with _connect(pg_server) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS ops_workload_controls")
            cur.execute(ddl)
            cur.execute(
                """
                SELECT c.check_clause
                FROM information_schema.check_constraints AS c
                JOIN information_schema.constraint_column_usage AS u
                  USING (constraint_schema, constraint_name)
                WHERE u.table_name = 'ops_workload_controls'
                  AND u.column_name = 'control_name'
                """
            )
            rows = cur.fetchall()
    assert len(rows) == 1
    check_clause = rows[0][0]
    for key in CASE_CONTROL_KEYS:
        assert key in check_clause


def test_plain_recommendation_with_case_key_passes_and_foreign_key_is_rejected(pg_server):
    import psycopg2

    _, ddl = _control_table_ddl(1)
    with _connect(pg_server) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS ops_workload_controls")
            cur.execute(ddl)
            cur.execute(
                "INSERT INTO ops_workload_controls (control_name, recommendation) "
                "VALUES ('billing_export_scan', 'Throttle the export window to off-peak periods')"
            )
            cur.execute(
                "SELECT count(*) FROM ops_workload_controls "
                "WHERE control_name = 'billing_export_scan'"
            )
            assert cur.fetchone()[0] == 1
            with pytest.raises(psycopg2.errors.CheckViolation):
                cur.execute(
                    "INSERT INTO ops_workload_controls (control_name, recommendation) "
                    "VALUES ('ad_hoc_reporting_job', 'isolate and limit')"
                )
