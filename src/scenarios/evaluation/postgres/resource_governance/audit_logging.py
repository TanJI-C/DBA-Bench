import csv
from contextlib import closing
import time
from uuid import uuid4

from src.execution.postgres_history import parse_postgres_log_records
from src.scenarios.evaluation.outcome import (
    OutcomeCheck,
    OutcomeVerifier,
    SqlRowsVerifier,
)
from .base import ResourceGovernanceEvaluator, condition

_AUDIT_DP = (
    condition(
        "logging_overhead",
        "statement logging overload",
        "audit logging reduces throughput",
        "log_statement=all",
        "log_statement=all and pgaudit.log=all duplicate read-only checkout logging; the audit role's SELECT privilege also enables pgAudit object READ audit",
        "log_statement=all 将每一条语句（含海量只读 SELECT）逐条写入 stderr/docker 日志，产生与 WAL/表增长无关的磁盘写入尖峰，并以同步日志写盘拖累事务吞吐",
        "`log_statement=all` 记录所有 SQL，包括 checkout 路径中的大量只读 SELECT，server log 写入放大造成磁盘写升高并压低事务吞吐。",
        "log_statement=all logs every statement including high-frequency checkout SELECTs, causing excessive log write I/O",
        "log_statement=all caused every statement, including high-frequency select checkout lookups, to be emitted to pg_log/docker stderr, creating excessive non-wal log writes and reducing throughput.",
        "原生 log_statement=all 与 pgAudit 全量 session/object READ 审计记录大量只读查询，放大非 WAL 日志写入",
        critical=True,
    ),
    condition(
        "scope",
        "sensitive writes ddl and role changes need audit",
        "audit scope identified",
        "audit coverage requirement",
        "constraint",
        "retain real write, ddl and role audit coverage while eliminating high-frequency checkout read logging",
        "保留真实写入、DDL、角色变更审计，消除高频 checkout 读查询的日志放大",
        critical=True,
    ),
)


def _audit_probe(context):
    """Exercise the final state without committing probe objects or business writes."""
    case = context.case_run.case
    marker = f"audit_op_{uuid4().hex}"
    log_path = "/var/log/postgresql/postgresql.log"
    read_sql = f"SELECT amount FROM public.{case.table} WHERE id = 42"
    insert_id = -int(marker[-7:], 16) - 1
    env = context.case_run.env
    # Read raw logs through the observer connection: Agent SQL responses bound
    # long text cells and would truncate audit evidence.
    with closing(env.open_workload_connection("audit-outcome-log-observer")) as observer:
        observer.autocommit = True
        with observer.cursor() as log_cur:
            log_cur.execute("SELECT (pg_stat_file(%s)).size", (log_path,))
            offset = log_cur.fetchone()[0]
            with closing(env.open_workload_connection(marker)) as conn:
                pid = conn.get_backend_pid()
                with conn.cursor() as cur:
                    try:
                        cur.execute(read_sql)
                        read_rows = cur.fetchall()
                        cur.execute(
                            f"UPDATE public.{case.table} SET amount = amount + 1 "
                            "WHERE id = 42 RETURNING id"
                        )
                        write_rows = cur.fetchall()
                        cur.execute(
                            f"INSERT INTO public.{case.table} (id, customer_id, amount, status) "
                            f"VALUES ({insert_id}, 43, 1, 'PAID')"
                        )
                        cur.execute(f"DELETE FROM public.{case.table} WHERE id = {insert_id}")
                        cur.execute(f"CREATE TEMP TABLE {marker} (id integer)")
                        cur.execute(f"CREATE ROLE {marker}")
                    finally:
                        conn.rollback()
                    conn.autocommit = True
                    cur.execute(f"DO $$ BEGIN RAISE LOG '{marker}'; END $$")

            # The same backend's final LOG confirms preceding records arrived.
            for attempt in range(20):
                log_cur.execute(
                    "SELECT pg_read_file(%s, %s, (pg_stat_file(%s)).size - %s)",
                    (log_path, offset, log_path, offset),
                )
                raw = log_cur.fetchone()[0]
                records = tuple(
                    record.payload for record in parse_postgres_log_records(raw, 0, 2**63 - 1)
                    if record.payload["pid"] == pid
                )
                if any(record["message"].strip() == marker for record in records):
                    return read_sql, read_rows, write_rows, records
                if attempt < 19:
                    time.sleep(0.1)
    raise RuntimeError(f"Audit probe log collection did not reach completion: pid={pid}, marker={marker}, records={records!r}")


class AuditBehaviorVerifier(OutcomeVerifier):
    check_id = "audit_behavior"

    def verify(self, context):
        read_sql, read_rows, write_rows, records = _audit_probe(context)
        audited_commands = set()
        read_logs = []
        ddl_object_identified = False
        for record in records:
            message = record["message"].strip()
            if message.startswith("AUDIT: "):
                fields = next(csv.reader([message.removeprefix("AUDIT: ")]))
                audited_commands.add((fields[3], fields[4]))
                if fields[3:5] == ["DDL", "CREATE TABLE"]:
                    ddl_object_identified = fields[5] == "TABLE" and bool(fields[6])
                if fields[3] == "READ":
                    read_logs.append(message)
            elif read_sql.casefold() in " ".join(message.split()).casefold():
                read_logs.append(message)
        required = {
            ("WRITE", "INSERT"), ("WRITE", "UPDATE"), ("WRITE", "DELETE"),
            ("DDL", "CREATE TABLE"), ("ROLE", "CREATE ROLE"),
        }
        actual = {
            "audited_commands": sorted(audited_commands),
            "checkout_read_log_count": len(read_logs),
            "checkout_read_succeeded": len(read_rows) == 1 and read_rows[0][0] is not None,
            "checkout_write_succeeded": write_rows == [(42,)],
            "ddl_object_identified": ddl_object_identified,
        }
        return OutcomeCheck(
            check_id=self.check_id,
            passed=required <= audited_commands
            and not read_logs
            and actual["checkout_read_succeeded"]
            and actual["checkout_write_succeeded"]
            and ddl_object_identified,
            expected="real WRITE/DDL/ROLE audit records, zero ordinary checkout READ logs, successful business read/write",
            actual=actual,
            evidence=tuple(record["message"] for record in records),
        )


_AUDIT_BEHAVIOR = AuditBehaviorVerifier()
_AUDIT_PROBE = SqlRowsVerifier(
    "transaction_probe",
    lambda case: f"SELECT count(*) FROM {case.table}",
    "business row count is positive",
    lambda rows, case: len(rows) == 1 and len(rows[0]) == 1 and int(rows[0][0]) > 0,
)


class PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase(ResourceGovernanceEvaluator):
    scenario_id = "pg_resource_governance_audit_logging"
    case_id = "audit_orders_role_logging"
    diagnosis_conditions = _AUDIT_DP
    outcome_verifiers = (_AUDIT_BEHAVIOR, _AUDIT_PROBE)


class PgResourceGovernanceAuditLoggingForOrdersWriteAuditScopeSimpleEvaluatorCase(
    PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase
):
    case_id = "orders_write_audit_scope_simple"
