import json
from types import SimpleNamespace

import pytest

from src.execution.environment import PGEnv
from src.execution.postgres_history import reject_postgres_public_historical_sql


def test_postgres_sql_guard_rejects_relations_functions_ctes_and_multistatements():
    rejected = (
        "SELECT * FROM pg_stat_statements",
        "SELECT * FROM pg_stat_statements_info",
        "SELECT pg_stat_statements_reset()",
        "SELECT pg_read_file('postgresql.conf')",
        "SELECT pg_read_binary_file('postgresql.conf')",
        "SELECT * FROM pg_ls_logdir()",
        "WITH rows AS (SELECT * FROM public.pg_stat_statements) SELECT * FROM rows",
        "SELECT 1; SELECT * FROM pg_stat_statements",
    )
    for query in rejected:
        try:
            reject_postgres_public_historical_sql(query)
        except ValueError as exc:
            assert "physical historical telemetry" in str(exc)
        else:
            raise AssertionError(f"PostgreSQL history guard allowed a forbidden query: {query!r}")
    with pytest.raises(ValueError, match="Cannot parse SQL"):
        reject_postgres_public_historical_sql("SELECT (")


def test_postgres_sql_guard_rejects_environment_declared_protected_relations():
    with pytest.raises(ValueError, match="protected runtime relation"):
        reject_postgres_public_historical_sql(
            "SELECT marker_id FROM aiopsbench_rpo.business_markers",
            protected_relation_names=("aiopsbench_rpo.business_markers",),
        )


def test_postgres_sql_guard_rejects_uninspectable_dynamic_commands():
    for query in (
        "DO $$ BEGIN EXECUTE 'CREATE TEMP TABLE leaked AS SELECT * FROM pg_stat_statements'; END $$",
        "PREPARE history_stmt AS SELECT * FROM pg_stat_statements",
    ):
        with pytest.raises(ValueError, match="uninspectable SQL commands"):
            reject_postgres_public_historical_sql(query)


def test_postgres_sql_guard_allows_bounded_role_connection_limit_commands():
    for query in (
        "ALTER ROLE checkout_user CONNECTION LIMIT 6",
        "alter user checkout_user connection limit -1;",
    ):
        reject_postgres_public_historical_sql(query)


def test_postgres_sql_guard_rejects_unbounded_role_commands_and_command_injection():
    rejected = (
        "ALTER ROLE checkout_user SET work_mem = '1MB'",
        "ALTER ROLE checkout_user CONNECTION LIMIT 6; SELECT 1",
        "ALTER ROLE checkout_user CONNECTION LIMIT 6; DROP TABLE orders",
        "ALTER ROLE checkout_user CONNECTION LIMIT 6 -- bypass\n; SELECT 1",
        "ALTER ROLE checkout-user CONNECTION LIMIT 6",
    )
    for query in rejected:
        with pytest.raises(ValueError):
            reject_postgres_public_historical_sql(query)


def test_postgres_sql_guard_allows_current_state_and_business_relations():
    for query in (
        "SELECT * FROM pg_stat_activity",
        "SELECT * FROM pg_locks",
        "SELECT * FROM pg_stat_database",
        "SELECT * FROM pg_stat_user_tables",
        "SELECT * FROM public.orders",
        "SELECT name, setting FROM pg_settings",
        "ALTER SYSTEM SET checkpoint_timeout = '5min'",
        "ALTER SYSTEM RESET checkpoint_timeout",
    ):
        reject_postgres_public_historical_sql(query)


def test_postgres_sql_guard_rejects_case_owned_staging_relations_only_when_protected():
    query = "SELECT * FROM public.hc_mf01_observation_history"
    reject_postgres_public_historical_sql(query)
    with pytest.raises(ValueError, match="physical historical telemetry"):
        reject_postgres_public_historical_sql(
            query,
            protected_relations=frozenset({"hc_mf01_observation_history"}),
        )
    with pytest.raises(ValueError, match="physical historical telemetry"):
        reject_postgres_public_historical_sql(
            "WITH rows AS (SELECT * FROM hc_mf01_observation_history) SELECT * FROM rows",
            protected_relations=frozenset({"hc_mf01_observation_history"}),
        )


class FakeCursor:
    description = (SimpleNamespace(name="value"),)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql):
        self.sql = sql

    def fetchall(self):
        return [(1,)]


class FakeConnection:
    def cursor(self):
        return FakeCursor()

    def commit(self):
        pass


def test_environment_separates_public_frozen_sql_from_trusted_live_sql():
    env = PGEnv(deployment=SimpleNamespace(container_name="pg", resources={}))
    env._conn = FakeConnection()
    env._ensure_connection = lambda: True
    env._history_timeline = object()

    public = json.loads(env.execute_sql("SELECT * FROM pg_stat_statements"))
    assert public["status"] == "error"
    assert "execute_sql(target='history')" in public["error"]

    trusted = json.loads(env.execute_sql_trusted("SELECT * FROM pg_stat_statements"))
    assert trusted == {"status": "success", "columns": ["value"], "result": [[1]]}

    env._history_timeline = None
    ordinary = json.loads(env.execute_sql("SELECT * FROM pg_stat_statements"))
    assert ordinary["status"] == "success"


def test_trusted_sql_boundary_allows_internal_postgres_reset_ddl():
    env = PGEnv(deployment=SimpleNamespace(container_name="pg", resources={}))
    env._conn = FakeConnection()
    env._ensure_connection = lambda: True
    env._history_timeline = object()

    public = json.loads(env.execute_sql("ALTER TABLE hc_mf01_target RESET (autovacuum_enabled)"))
    assert public["status"] == "error"
    assert "uninspectable SQL commands" in public["error"]

    trusted = json.loads(env.execute_sql_trusted("ALTER TABLE hc_mf01_target RESET (autovacuum_enabled)"))
    assert trusted["status"] == "success"
