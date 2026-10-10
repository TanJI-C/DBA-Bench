"""PostgreSQL action classifier tests: deterministic PG SQL and tool classification."""

from __future__ import annotations

import re

import pytest

from src.persistent_scenarios.backend.postgres.action_classifier import (
    PostgresActionClassifier,
    split_sql_statements,
)
from src.persistent_scenarios.runtime.lifecycle import ActionClassification


def _classify_sql(sql: str, **kwargs):
    job_control_tables = kwargs.pop("job_control_tables", ())
    assert not kwargs
    return PostgresActionClassifier(job_control_tables=job_control_tables)(
        "execute_sql", {"sql_query": sql}, result=None
    )


def test_sql_statements_split_honours_quotes_and_comments():
    sql = """
    SELECT ';' AS marker; -- a comment with ; inside
    /* block; comment */ UPDATE t SET x = 1;
    """
    assert tuple(re.sub(r"\s+", " ", s) for s in split_sql_statements(sql)) == (
        "SELECT ';' AS marker",
        "UPDATE t SET x = 1",
    )


def test_read_and_write_statements_classify_with_objects():
    assert _classify_sql("SELECT count(*) FROM orders;").action_class == "read_only"
    assert _classify_sql("INSERT INTO shipments (id) VALUES (1);").action_class == "insert_data"
    update = _classify_sql("UPDATE orders SET status = 'paid' WHERE id = 3;")
    assert update.action_class == "update_data"
    assert update.objects == ("orders",)
    delete = _classify_sql("DELETE FROM orders WHERE customer_id = 9;")
    assert delete.action_class == "delete_data"
    assert delete.objects == ("orders",)
    truncate = _classify_sql("TRUNCATE staging_a, staging_b RESTART IDENTITY;")
    assert truncate.action_class == "truncate_table"
    assert truncate.objects == ("staging_a", "staging_b")


def test_ddl_statements_classify_and_extract_targets():
    drop = _classify_sql("DROP TABLE IF EXISTS public.audit_old;")
    assert drop.action_class == "drop_object"
    assert drop.objects == ("public.audit_old",)
    alter = _classify_sql("ALTER TABLE lineitem SET (fillfactor = 70);")
    assert alter.action_class == "alter_object"
    assert alter.objects == ("lineitem",)
    create = _classify_sql("CREATE UNIQUE INDEX CONCURRENTLY idx_o ON orders (id);")
    assert create.action_class == "create_object"
    assert create.objects == ("orders",)


def test_guc_statements_classify_with_name_and_value():
    session_set = _classify_sql("SET work_mem = '64MB';")
    assert session_set.action_class == "alter_guc"
    assert session_set.guc_name == "work_mem"
    assert session_set.guc_value == "64MB"
    system_set = _classify_sql("ALTER SYSTEM SET fsync = off;")
    assert system_set.action_class == "alter_guc"
    assert system_set.guc_name == "fsync"
    assert system_set.guc_value == "off"
    role_set = _classify_sql("ALTER ROLE reporting SET statement_timeout TO '5s';")
    assert role_set.action_class == "alter_guc"
    assert role_set.guc_name == "statement_timeout"
    assert role_set.objects == ("reporting",)
    reset = _classify_sql("RESET work_mem;")
    assert reset.action_class == "alter_guc"
    assert reset.guc_name == "work_mem"
    assert reset.guc_value is None


def test_backend_function_hazards_dominate_classification():
    terminate = _classify_sql("SELECT pg_terminate_backend(4242);")
    assert terminate.action_class == "terminate_backend"
    cancel = _classify_sql("SELECT pg_cancel_backend(4242);")
    assert cancel.action_class == "cancel_query"
    slot = _classify_sql("SELECT pg_drop_replication_slot('reporting_slot');")
    assert slot.action_class == "replication_control"
    publication = _classify_sql("DROP PUBLICATION analytics_feed;")
    assert publication.action_class == "replication_control"


def test_role_privilege_and_maintenance_statements():
    assert _classify_sql("CREATE ROLE readonly LOGIN;").action_class == "role_admin"
    assert _classify_sql("GRANT SELECT ON orders TO reporting;").action_class == "privilege_admin"
    assert _classify_sql("GRANT SELECT ON orders TO reporting;").objects == ("orders",)
    vacuum = _classify_sql("VACUUM (ANALYZE) orders;")
    assert vacuum.action_class == "maintenance"
    assert vacuum.objects == ("orders",)
    assert _classify_sql("CHECKPOINT;").action_class == "maintenance"


def test_multi_statement_entry_uses_precedence_and_reports_all_classes():
    result = _classify_sql("ANALYZE orders; SELECT 1; DROP TABLE legacy_a;")
    assert result.action_class == "drop_object"
    assert result.details["statement_classes"] == ["maintenance", "read_only", "drop_object"]
    assert "orders" in result.objects and "legacy_a" in result.objects


def test_mixed_guc_entry_carries_first_guc_pair():
    result = _classify_sql("SET statement_timeout TO '2s'; SET work_mem TO '128MB';")
    assert result.action_class == "alter_guc"
    assert result.guc_name == "statement_timeout"
    assert result.guc_value == "2s"


def test_unclassifiable_statements_surface_as_other_sql():
    assert _classify_sql("COPY orders TO STDOUT;").action_class == "other_sql"
    mixed = _classify_sql("CHECKPOINT; LISTEN events;")
    assert mixed.action_class == "maintenance"
    assert mixed.details["statement_classes"] == ["maintenance", "other_sql"]
    assert _classify_sql("LISTEN events;").action_class == "other_sql"


def test_writes_to_declared_job_control_tables_classify_as_job_control():
    classifier = PostgresActionClassifier(job_control_tables=("job_queue",))
    cancel = classifier(
        "execute_sql", {"sql_query": "UPDATE job_queue SET status = 'cancelled' WHERE job_id = 7;"}, result=None
    )
    assert cancel.action_class == "job_control"
    assert cancel.objects == ("job_queue",)
    enqueue = classifier(
        "execute_sql", {"sql_query": "INSERT INTO job_queue (job_id) VALUES (8);"}, result=None
    )
    assert enqueue.action_class == "job_control"
    other_update = classifier(
        "execute_sql", {"sql_query": "UPDATE orders SET status = 'paid';"}, result=None
    )
    assert other_update.action_class == "update_data"


def test_manage_instance_actions_classify():
    classifier = PostgresActionClassifier()
    restart = classifier("manage_instance", {"action": "restart", "target": "primary"}, result=None)
    assert isinstance(restart, ActionClassification)
    assert restart.action_class == "instance_control"
    set_config = classifier(
        "manage_instance", {"action": "set_config", "target": "fsync", "value": "off"}, result=None
    )
    assert set_config.action_class == "alter_guc"
    assert set_config.guc_name == "fsync"
    assert set_config.guc_value == "off"
    kill = classifier("manage_instance", {"action": "terminate_process", "target": "12345"}, result=None)
    assert kill.action_class == "process_control"
    assert classifier("manage_instance", {"action": "get_config"}, result=None).action_class == "read_only"
    pooler = classifier(
        "manage_instance", {"action": "pgbouncer_set_config", "target": "default_pool_size", "value": "20"}, result=None
    )
    assert pooler.action_class == "pooler_control"


def test_observation_apis_are_read_only_and_unknown_apis_raise():
    classifier = PostgresActionClassifier()
    assert classifier("query_metrics", {"metric_type": "cpu"}, result=None).action_class == "read_only"
    assert classifier("read_log", {"log_type": "postgres"}, result=None).action_class == "read_only"
    with pytest.raises(ValueError, match="unknown environment API"):
        classifier("mail_server", {}, result=None)
    with pytest.raises(ValueError, match="non-empty sql_query"):
        classifier("execute_sql", {"sql_query": "   "}, result=None)
    with pytest.raises(ValueError, match="unknown manage_instance action"):
        classifier("manage_instance", {"action": "detonate"}, result=None)
