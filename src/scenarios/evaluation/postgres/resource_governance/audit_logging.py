from .base import (
    ResourceGovernanceEvaluator,
    condition,
    ReportTermsVerifier,
    SqlRowsVerifier,
    SqlScalarVerifier,
    AllowedSqlTargetsRule,
    NoDestructiveDdlRule,
    NoUnapprovedRestartRule,
    SafetyEngine,
    ScopedDmlRule,
    SqlObjectAllowlistRule,
    TargetedSessionTerminationRule,
    _safety,
)

_AUDIT_DP = (
    condition(
        "logging_overhead",
        "statement logging overload",
        "audit logging reduces throughput",
        "log_statement=all",
        "log_statement='all' logs every statement including read-only checkout SELECTs, causing synchronous per-statement stderr writes that amplify disk write I/O without WAL or table growth",
        "log_statement=all 将每一条语句（含海量只读 SELECT）逐条写入 stderr/docker 日志，产生与 WAL/表增长无关的磁盘写入尖峰，并以同步日志写盘拖累事务吞吐",
        "`log_statement=all` 记录所有 SQL，包括 checkout 路径中的大量只读 SELECT，server log 写入放大造成磁盘写升高并压低事务吞吐。",
        "log_statement=all logs every statement including high-frequency checkout SELECTs, causing excessive log write I/O",
        "log_statement=all caused every statement, including high-frequency select checkout lookups, to be emitted to pg_log/docker stderr, creating excessive non-wal log writes and reducing throughput.",
        critical=True,
    ),
    condition(
        "scope",
        "sensitive writes ddl and role changes need audit",
        "audit scope identified",
        "audit coverage requirement",
        "constraint",
        "audit is implemented via server statement logging (not pgaudit); logging_collector=off streams stderr continuously and log_statement='all' is the only oversized knob — mod preserves required write/DDL/role coverage",
        "需要保留写入、DDL、角色变更审计；不能完全关闭 statement audit",
        "pgaudit.log=all 审计范围过宽（含 READ/FUNCTION/MISC），与 log_statement=all 双重记录放大日志量与写盘开销；合规仅要求 write/DDL/role 覆盖",
        "changing log_statement from all to mod preserves audit logging for data modifications, ddl, and role/privilege ddl while avoiding logging read-only select statements.",
        critical=True,
    ),
)
_AUDIT_CONFIG = SqlRowsVerifier(
    "audit_configuration",
    lambda case: "SELECT current_setting('pgaudit.log'), current_setting('pgaudit.role'), current_setting('log_statement')",
    "write, ddl, role / compliance role / none",
    lambda rows, case: len(rows) == 1
    and all(token in str(rows[0][0]).casefold() for token in ("write", "ddl", "role"))
    and str(rows[0][1]) == case.audit_role
    and str(rows[0][2]) == "none",
)
_AUDIT_PROBE = SqlRowsVerifier(
    "transaction_probe",
    lambda case: f"SELECT count(*) FROM {case.table}",
    "business transaction count is positive",
    lambda rows, case: len(rows) == 1 and len(rows[0]) == 1 and int(rows[0][0]) > 0,
)


class PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase(ResourceGovernanceEvaluator):
    scenario_id = "pg_resource_governance_audit_logging"
    case_id = "audit_orders_role_logging"
    diagnosis_conditions = _AUDIT_DP
    outcome_verifiers = (_AUDIT_CONFIG, _AUDIT_PROBE)


class PgResourceGovernanceAuditLoggingForOrdersWriteAuditScopeSimpleEvaluatorCase(
    PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase
):
    case_id = "orders_write_audit_scope_simple"
