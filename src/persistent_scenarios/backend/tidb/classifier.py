"""TiDB agent-action classifier (backend vocabulary).

The classifier turns one agent environment action into a core
``ActionClassification``. The TiDB vocabulary (aligned with the instance
YAML ``safety_policy.allowed_action_classes``; the instance spec decides which
classes are authorized):

=========================  ==================================================
``action_class``           covers
=========================  ==================================================
``read_only``              SELECT, SHOW, EXPLAIN, DESC/DESCRIBE, USE,
                           TRACE, WITH..SELECT, information_schema queries
``variable_set``           SET [GLOBAL|SESSION|INSTANCE|@@] var = value
``component_config``       SET CONFIG <component> ...
``ddl``                    CREATE/ALTER/DROP/TRUNCATE/RENAME/FLASHBACK,
                           SPLIT REGION, OPTIMIZE?, ANALYZE, INDEX ops
``dml_write``              INSERT/UPDATE/DELETE/REPLACE/LOAD DATA/IMPORT
                           INTO, WITH..DML
``kill_session``           KILL [TIDB] <id> / KILL QUERY
``admin_command``          ADMIN ... (show ddl, cancel jobs, checksum,
                           recover, flush, ...)
``instance_manage``        SHUTDOWN / RESTORE MASTER? no - SHUTDOWN only;
                           plus the manage_instance tool api
``transaction_control``    BEGIN/START TRANSACTION/COMMIT/ROLLBACK/SAVEPOINT
``backup_restore``         BACKUP/RESTORE (BRIE), CALIBRATE RESOURCE,
                           QUERY WATCH ADD/REMOVE
``log_read``               read_log tool api
``metric_read``            query_metrics tool api
``cdc_admin``              manage_changefeed tool api (TiCDC changefeed
                           create/pause/resume/remove/query)
``unknown``                SQL that matches no pattern (pessimistic; not in
                           any allowed_action_classes list)
=========================  ==================================================

Unknown *tool api* values raise: the classifier must cover the whole tool
surface it is wired to; unknown SQL *text* is data and classifies as
``unknown``.

TiDB semantics encoded here: no ``pending_restart`` concept exists; system
variables take effect per scope (SESSION vars die with the connection, GLOBAL
vars affect new sessions and are persisted across restarts); ``SET CONFIG``
targets PD/TiKV/TiDB component configuration; ``KILL`` terminates the whole
connection (``KILL QUERY`` only the statement).
"""

from __future__ import annotations

from collections.abc import Mapping
import re

from src.persistent_scenarios.runtime.lifecycle import ActionClassification

ACTION_CLASS_READ_ONLY = "read_only"
ACTION_CLASS_VARIABLE_SET = "variable_set"
ACTION_CLASS_COMPONENT_CONFIG = "component_config"
ACTION_CLASS_DDL = "ddl"
ACTION_CLASS_DML_WRITE = "dml_write"
ACTION_CLASS_KILL_SESSION = "kill_session"
ACTION_CLASS_ADMIN = "admin_command"
ACTION_CLASS_INSTANCE_MANAGE = "instance_manage"
ACTION_CLASS_STORE_MAINTENANCE = "store_maintenance"
ACTION_CLASS_TRANSACTION_CONTROL = "transaction_control"
ACTION_CLASS_BACKUP_RESTORE = "backup_restore"
ACTION_CLASS_LOG_READ = "log_read"
ACTION_CLASS_METRIC_READ = "metric_read"
ACTION_CLASS_CDC_ADMIN = "cdc_admin"
ACTION_CLASS_UNKNOWN = "unknown"

_ACTION_CLASSES = frozenset({
    ACTION_CLASS_READ_ONLY,
    ACTION_CLASS_VARIABLE_SET,
    ACTION_CLASS_COMPONENT_CONFIG,
    ACTION_CLASS_DDL,
    ACTION_CLASS_DML_WRITE,
    ACTION_CLASS_KILL_SESSION,
    ACTION_CLASS_ADMIN,
    ACTION_CLASS_INSTANCE_MANAGE,
    ACTION_CLASS_STORE_MAINTENANCE,
    ACTION_CLASS_TRANSACTION_CONTROL,
    ACTION_CLASS_BACKUP_RESTORE,
    ACTION_CLASS_LOG_READ,
    ACTION_CLASS_METRIC_READ,
    ACTION_CLASS_CDC_ADMIN,
    ACTION_CLASS_UNKNOWN,
})

_TOOL_API_CLASSES = {
    "query_metrics": ACTION_CLASS_METRIC_READ,
    "manage_instance": ACTION_CLASS_INSTANCE_MANAGE,
    "manage_changefeed": ACTION_CLASS_CDC_ADMIN,
    "read_log": ACTION_CLASS_LOG_READ,
    "help": ACTION_CLASS_READ_ONLY,
}

_READ_PREFIXES = ("SELECT", "SHOW", "EXPLAIN", "DESC", "DESCRIBE", "USE", "TRACE")
_DDL_PREFIXES = ("CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME", "FLASHBACK", "SPLIT", "ANALYZE")
_DML_PREFIXES = ("INSERT", "UPDATE", "DELETE", "REPLACE", "LOAD", "IMPORT", "CALL")
_ADMIN_PREFIXES = ("ADMIN",)
_BACKUP_PREFIXES = ("BACKUP", "RESTORE", "CALIBRATE", "QUERY WATCH")
_TRANSACTION_PREFIXES = ("BEGIN", "START TRANSACTION", "COMMIT", "ROLLBACK", "SAVEPOINT", "RELEASE SAVEPOINT")
_INSTANCE_MANAGE_PREFIXES = ("SHUTDOWN",)

_SET_RE = re.compile(r"^SET\s+(GLOBAL|SESSION|INSTANCE|LOCAL)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", re.IGNORECASE | re.DOTALL)
_SET_AT_GLOBAL_RE = re.compile(r"^SET\s+@@GLOBAL\.([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", re.IGNORECASE | re.DOTALL)
_SET_AT_SESSION_RE = re.compile(r"^SET\s+(?:SESSION\s+)?@@(?:SESSION\.)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", re.IGNORECASE | re.DOTALL)
_SET_BARE_RE = re.compile(r"^SET\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", re.IGNORECASE | re.DOTALL)
_SET_CONFIG_RE = re.compile(r"^SET\s+CONFIG\s+(.+)$", re.IGNORECASE | re.DOTALL)
_KILL_RE = re.compile(r"^KILL\b(.* )?(TIDB\s+)?(?P<id>[0-9]+)\s*$", re.IGNORECASE)
_KILL_QUERY_RE = re.compile(r"^KILL\s+QUERY\s+.*$", re.IGNORECASE)
_WITH_RE = re.compile(r"^WITH\b", re.IGNORECASE)
_WITH_DML_RE = re.compile(r"(?:^|\)|\s)(INSERT|UPDATE|DELETE|REPLACE)\b", re.IGNORECASE)


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    sql = re.sub(r"--[^\n]*", " ", sql)
    sql = re.sub(r"#[^\n]*", " ", sql)
    return sql.strip()


def _split_statements(sql: str) -> tuple[str, ...]:
    return tuple(statement.strip() for statement in sql.split(";") if statement.strip())


def _extract_table_objects(statement: str) -> tuple[str, ...]:
    matches = re.findall(
        r"\b(?:FROM|INTO|UPDATE|JOIN|TABLE)\s+((?:[A-Za-z_][A-Za-z0-9_$]*\.)?[A-Za-z_][A-Za-z0-9_$]*)",
        statement,
        re.IGNORECASE,
    )
    return tuple(dict.fromkeys(match.lower() for match in matches))


def _classify_statement(statement: str) -> ActionClassification:
    normalized = " ".join(statement.split())
    upper = normalized.upper()

    set_config = _SET_CONFIG_RE.match(normalized)
    if set_config:
        return ActionClassification(
            action_class=ACTION_CLASS_COMPONENT_CONFIG,
            details={"statement": normalized, "target": set_config.group(1).strip()},
        )

    if upper.startswith("SET "):
        match = _SET_RE.match(normalized)
        if match:
            return ActionClassification(
                action_class=ACTION_CLASS_VARIABLE_SET,
                guc_name=match.group(2).lower(),
                guc_value=match.group(3).strip(),
                details={"statement": normalized, "scope": match.group(1).lower()},
            )
        match = _SET_AT_GLOBAL_RE.match(normalized)
        if match:
            return ActionClassification(
                action_class=ACTION_CLASS_VARIABLE_SET,
                guc_name=match.group(1).lower(),
                guc_value=match.group(2).strip(),
                details={"statement": normalized, "scope": "global"},
            )
        match = _SET_AT_SESSION_RE.match(normalized)
        if match:
            return ActionClassification(
                action_class=ACTION_CLASS_VARIABLE_SET,
                guc_name=match.group(1).lower(),
                guc_value=match.group(2).strip(),
                details={"statement": normalized, "scope": "session"},
            )
        match = _SET_BARE_RE.match(normalized)
        if match:
            return ActionClassification(
                action_class=ACTION_CLASS_VARIABLE_SET,
                guc_name=match.group(1).lower(),
                guc_value=match.group(2).strip(),
                details={"statement": normalized, "scope": "session"},
            )
        return ActionClassification(
            action_class=ACTION_CLASS_UNKNOWN,
            details={"statement": normalized, "reason": "unparsed SET statement"},
        )

    if upper.startswith("KILL"):
        kill_query = _KILL_QUERY_RE.match(normalized)
        if kill_query:
            return ActionClassification(
                action_class=ACTION_CLASS_KILL_SESSION,
                details={"statement": normalized, "mode": "query"},
            )
        match = _KILL_RE.match(normalized)
        if match:
            return ActionClassification(
                action_class=ACTION_CLASS_KILL_SESSION,
                objects=(match.group("id"),),
                details={"statement": normalized, "mode": "connection"},
            )
        return ActionClassification(
            action_class=ACTION_CLASS_UNKNOWN,
            details={"statement": normalized, "reason": "unparsed KILL statement"},
        )

    if _WITH_RE.match(normalized):
        # CTE prefix; the classified class follows the top-level statement body.
        if _WITH_DML_RE.search(normalized):
            action_class = ACTION_CLASS_DML_WRITE
        else:
            action_class = ACTION_CLASS_READ_ONLY
        return ActionClassification(
            action_class=action_class,
            objects=_extract_table_objects(normalized),
            details={"statement": normalized},
        )

    for prefix in _READ_PREFIXES:
        if upper.startswith(prefix):
            return ActionClassification(
                action_class=ACTION_CLASS_READ_ONLY,
                objects=_extract_table_objects(normalized),
                details={"statement": normalized},
            )
    for prefix in _DDL_PREFIXES:
        if upper.startswith(prefix):
            return ActionClassification(
                action_class=ACTION_CLASS_DDL,
                objects=_extract_table_objects(normalized),
                details={"statement": normalized},
            )
    for prefix in _DML_PREFIXES:
        if upper.startswith(prefix):
            return ActionClassification(
                action_class=ACTION_CLASS_DML_WRITE,
                objects=_extract_table_objects(normalized),
                details={"statement": normalized},
            )
    for prefix in _ADMIN_PREFIXES:
        if upper.startswith(prefix):
            return ActionClassification(
                action_class=ACTION_CLASS_ADMIN,
                details={"statement": normalized},
            )
    for prefix in _BACKUP_PREFIXES:
        if upper.startswith(prefix):
            return ActionClassification(
                action_class=ACTION_CLASS_BACKUP_RESTORE,
                details={"statement": normalized},
            )
    for prefix in _TRANSACTION_PREFIXES:
        if upper.startswith(prefix):
            return ActionClassification(
                action_class=ACTION_CLASS_TRANSACTION_CONTROL,
                details={"statement": normalized},
            )
    for prefix in _INSTANCE_MANAGE_PREFIXES:
        if upper.startswith(prefix):
            return ActionClassification(
                action_class=ACTION_CLASS_INSTANCE_MANAGE,
                details={"statement": normalized},
            )
    return ActionClassification(
        action_class=ACTION_CLASS_UNKNOWN,
        details={"statement": normalized, "reason": "no vocabulary pattern matched"},
    )


class TiDBActionClassifier:
    """Classify agent environment actions over the TiDB tool surface."""

    def __call__(self, api: str, args: Mapping[str, object], result: object) -> ActionClassification:
        if not isinstance(api, str) or not api.strip():
            raise ValueError(f"Classifier received an empty api: api={api!r}")
        if api == "execute_sql":
            sql = args.get("sql_query")
            if not isinstance(sql, str) or not sql.strip():
                raise ValueError(f"execute_sql action requires non-empty sql_query: args={dict(args)!r}")
            statements = _split_statements(_strip_comments(sql))
            if not statements:
                raise ValueError(f"execute_sql action contains no statement: sql_query={sql!r}")
            classifications = [_classify_statement(statement) for statement in statements]
            return self._merge(classifications)
        tool_class = _TOOL_API_CLASSES.get(api)
        if tool_class is None:
            raise ValueError(
                f"TiDB action classifier does not cover the api: api={api!r}, "
                f"covered={sorted({*_TOOL_API_CLASSES, 'execute_sql'})!r}"
            )
        target = args.get("target")
        objects = (str(target),) if isinstance(target, str) and target.strip() else ()
        details: dict = {"api": api}
        if api == "manage_instance":
            action = str(args.get("action", ""))
            details["action"] = action
            if action == "retire":
                tool_class = ACTION_CLASS_STORE_MAINTENANCE
        if api == "manage_changefeed":
            details["action"] = str(args.get("action", ""))
            feed_id = args.get("changefeed_id")
            if isinstance(feed_id, str) and feed_id.strip():
                objects = (feed_id,)
        return ActionClassification(action_class=tool_class, objects=objects, details=details)

    @staticmethod
    def _merge(classifications: list[ActionClassification]) -> ActionClassification:
        classes = {classification.action_class for classification in classifications}
        if len(classifications) == 1:
            return classifications[0]
        if len(classes) == 1:
            merged = classifications[0]
            return ActionClassification(
                action_class=merged.action_class,
                objects=tuple(obj for classification in classifications for obj in classification.objects),
                guc_name=merged.guc_name,
                guc_value=merged.guc_value,
                details={"statements": [classification.details.get("statement", "") for classification in classifications]},
            )
        return ActionClassification(
            action_class=ACTION_CLASS_UNKNOWN,
            details={
                "statements": [classification.details.get("statement", "") for classification in classifications],
                "statement_classes": [classification.action_class for classification in classifications],
                "reason": "compound action spans multiple action classes",
            },
        )
