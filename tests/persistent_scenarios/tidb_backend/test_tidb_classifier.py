"""TiDB action classifier vocabulary tests."""

import pytest

from src.persistent_scenarios.backend.tidb.classifier import (
    ACTION_CLASS_ADMIN,
    ACTION_CLASS_BACKUP_RESTORE,
    ACTION_CLASS_COMPONENT_CONFIG,
    ACTION_CLASS_DDL,
    ACTION_CLASS_DML_WRITE,
    ACTION_CLASS_INSTANCE_MANAGE,
    ACTION_CLASS_KILL_SESSION,
    ACTION_CLASS_LOG_READ,
    ACTION_CLASS_METRIC_READ,
    ACTION_CLASS_READ_ONLY,
    ACTION_CLASS_TRANSACTION_CONTROL,
    ACTION_CLASS_UNKNOWN,
    ACTION_CLASS_VARIABLE_SET,
    TiDBActionClassifier,
)


CLASSIFIER = TiDBActionClassifier()


def classify_sql(sql: str):
    return CLASSIFIER("execute_sql", {"sql_query": sql}, {"status": "success"})


def test_read_only_sql():
    for sql in (
        "SELECT * FROM orders WHERE id = 1",
        "SHOW VARIABLES LIKE 'max_execution_time'",
        "EXPLAIN ANALYZE SELECT COUNT(*) FROM t",
        "DESC information_schema.cluster_statements_summary",
        "SELECT * FROM information_schema.cluster_processlist",
        "USE test",
    ):
        classification = classify_sql(sql)
        assert classification.action_class == ACTION_CLASS_READ_ONLY, sql
    assert "orders" in classify_sql("SELECT * FROM orders").objects


def test_with_select_is_read_only_and_with_dml_is_write():
    assert classify_sql("WITH c AS (SELECT 1) SELECT * FROM c").action_class == ACTION_CLASS_READ_ONLY
    assert classify_sql("WITH c AS (SELECT 1) UPDATE t SET a = 1 WHERE id IN (SELECT * FROM c)").action_class == ACTION_CLASS_DML_WRITE


def test_variable_set_scopes():
    classification = classify_sql("SET GLOBAL max_execution_time = 60000")
    assert classification.action_class == ACTION_CLASS_VARIABLE_SET
    assert classification.guc_name == "max_execution_time"
    assert classification.guc_value == "60000"
    assert classification.details["scope"] == "global"

    assert classify_sql("SET SESSION tidb_broadcast_join_threshold_size = 100").details["scope"] == "session"
    assert classify_sql("SET tidb_retry_limit = 3").details["scope"] == "session"
    assert classify_sql("SET @@global.tidb_enable_async_commit = ON").details["scope"] == "global"
    assert classify_sql("SET @@session.tidb_enable_async_commit = OFF").details["scope"] == "session"


def test_component_config():
    classification = classify_sql("SET CONFIG tikv 1.1.1.1:20160 log.level = \"warn\"")
    assert classification.action_class == ACTION_CLASS_COMPONENT_CONFIG
    assert "tikv" in classification.details["target"]


def test_dml_and_ddl():
    assert classify_sql("INSERT INTO orders (id) VALUES (1)").action_class == ACTION_CLASS_DML_WRITE
    assert classify_sql("UPDATE inventory SET qty = qty - 1 WHERE sku = 'a'").action_class == ACTION_CLASS_DML_WRITE
    assert classify_sql("DELETE FROM stale_rows").action_class == ACTION_CLASS_DML_WRITE
    assert classify_sql("CREATE TABLE t (id INT PRIMARY KEY)").action_class == ACTION_CLASS_DDL
    assert classify_sql("ALTER TABLE t ADD COLUMN c INT").action_class == ACTION_CLASS_DDL
    assert classify_sql("TRUNCATE TABLE t").action_class == ACTION_CLASS_DDL
    assert classify_sql("ANALYZE TABLE orders").action_class == ACTION_CLASS_DDL


def test_kill_session_semantics():
    classification = classify_sql("KILL 421")
    assert classification.action_class == ACTION_CLASS_KILL_SESSION
    assert classification.objects == ("421",)
    assert classification.details["mode"] == "connection"
    assert classify_sql("KILL TIDB 421").action_class == ACTION_CLASS_KILL_SESSION
    assert classify_sql("KILL QUERY 421").details["mode"] == "query"


def test_admin_and_brie_and_shutdown():
    assert classify_sql("ADMIN SHOW DDL JOBS").action_class == ACTION_CLASS_ADMIN
    assert classify_sql("ADMIN CANCEL DDL JOBS 7").action_class == ACTION_CLASS_ADMIN
    assert classify_sql("BACKUP DATABASE test TO 'local:///backup'").action_class == ACTION_CLASS_BACKUP_RESTORE
    assert classify_sql("RESTORE DATABASE test FROM 'local:///backup'").action_class == ACTION_CLASS_BACKUP_RESTORE
    assert classify_sql("SHUTDOWN").action_class == ACTION_CLASS_INSTANCE_MANAGE
    assert classify_sql("BEGIN").action_class == ACTION_CLASS_TRANSACTION_CONTROL
    assert classify_sql("COMMIT").action_class == ACTION_CLASS_TRANSACTION_CONTROL


def test_unknown_sql_is_explicit_class():
    classification = classify_sql("FLUSH PRIVILEGES")
    assert classification.action_class == ACTION_CLASS_UNKNOWN
    assert classification.details["statement"] == "FLUSH PRIVILEGES"


def test_compound_statement_with_conflicting_classes_is_unknown():
    classification = classify_sql("SELECT 1; DROP TABLE orders")
    assert classification.action_class == ACTION_CLASS_UNKNOWN
    assert classification.details["statement_classes"] == [ACTION_CLASS_READ_ONLY, ACTION_CLASS_DDL]


def test_compound_statement_same_class_merges_objects():
    classification = classify_sql("SELECT * FROM orders; SELECT * FROM inventory")
    assert classification.action_class == ACTION_CLASS_READ_ONLY
    assert set(classification.objects) == {"orders", "inventory"}


def test_comments_are_stripped():
    classification = classify_sql("/* admin hint */ SELECT 1 -- drop table orders")
    assert classification.action_class == ACTION_CLASS_READ_ONLY


def test_tool_apis_and_unknown_api():
    assert CLASSIFIER("query_metrics", {"metric_type": "cpu"}, None).action_class == ACTION_CLASS_METRIC_READ
    assert CLASSIFIER("read_log", {"log_type": "tidb"}, None).action_class == ACTION_CLASS_LOG_READ
    manage = CLASSIFIER("manage_instance", {"action": "restart", "target": "tidb-0"}, None)
    assert manage.action_class == ACTION_CLASS_INSTANCE_MANAGE
    assert manage.objects == ("tidb-0",)
    assert manage.details["action"] == "restart"
    with pytest.raises(ValueError, match="api"):
        CLASSIFIER("mailbox", {"operation": "read"}, None)


def test_manage_instance_retire_is_store_maintenance():
    from src.persistent_scenarios.backend.tidb.classifier import ACTION_CLASS_STORE_MAINTENANCE

    retire = CLASSIFIER("manage_instance", {"action": "retire", "target": "tikv-2"}, None)
    assert retire.action_class == ACTION_CLASS_STORE_MAINTENANCE
    assert retire.objects == ("tikv-2",)
    assert retire.details["action"] == "retire"
    # Lifecycle verbs keep the instance-manage class.
    stop = CLASSIFIER("manage_instance", {"action": "stop", "target": "tidb-1"}, None)
    assert stop.action_class == ACTION_CLASS_INSTANCE_MANAGE


def test_execute_sql_requires_non_empty_sql():
    with pytest.raises(ValueError, match="sql_query"):
        CLASSIFIER("execute_sql", {"sql_query": "   "}, None)
