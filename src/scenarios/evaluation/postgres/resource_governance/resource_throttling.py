import re

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


def _work_mem_mb(setting):
    match = re.search(r"work_mem\s*=\s*'?([0-9]+(?:\.[0-9]+)?)\s*(kb|mb|gb)'?", str(setting), re.I)
    if match is None:
        return None
    amount = float(match.group(1))
    unit = match.group(2).casefold()
    if unit == "kb":
        return amount / 1024
    if unit == "gb":
        return amount * 1024
    return amount


_THROTTLE_DP = (
    condition(
        "tenant_impact",
        "report tenant degrades oltp latency",
        "mixed tenant resource contention",
        "resource_contention",
        "workload_impact",
        "Unbounded reporting-export query saturating CPU and starving OLTP point reads",
        "报表导出查询在 OLTP 实例上长时间运行并放大扫描/计算，消耗 I/O/CPU 资源",
        "报表查询榨干 CPU，挤压 OLTP checkout/dashboard 流量，checkpoint 与读路径延迟上升",
        "Runaway analytical export query consuming CPU via parallel execution, starving OLTP reads on the shared instance",
        "长运行报表 SQL 消耗共享数据库资源，影响 checkout/OLTP 读性能",
        # Evidence-backed aliases: semantically
        # complete reports phrased the OLTP impact in these forms.
        "cpu saturation slowed shared instance checkout point reads and grew the active session count",
        "checkout point reads",
        "oltp point reads",
        "starving the oltp checkout point reads",
        critical=True,
    ),
    condition(
        "culprit_role",
        "report user export is culprit",
        "tenant revenue export identified",
        "runaway_query",
        "role:report_simple_user / pid 96",
        "report_simple_user / pid 95",
        "report_simple_user 角色在 testdb 上以应用 tenant-simple-export 并发运行两个笛卡尔积式报表查询（tenant_orders_simple 自连接 × generate_series(1,250)），EXPLAIN 预估 290 亿行、成本 3.38 亿，长时间占用 CPU 导致实例饱和、OLTP checkpoint/读路径变慢",
        "report_simple_user / pid 95 (leader) + pid 96 (parallel worker)",
        "report_simple_user active reporting export",
        # Evidence-backed aliases: any correct diagnosis names the culprit role
        # or its application; single-condition attribution stays required.
        "report_simple_user",
        "tenant-simple-export",
        "tenant simple export",
        critical=True,
    ),
    condition(
        "role_guardrail_gap",
        "report role has no resource guardrails",
        "report role lacks resource isolation",
        "misconfiguration",
        "config_gap",
        "insufficient_isolation",
        "Reporting role had no resource guardrails (no statement_timeout / parallelism / work_mem / idle timeout), unlike the OLTP role",
        "statement_timeout 仅配置给 postgres 角色（pg_db_role_setting setrole=10），report_simple_user 无角色级配置，实际 statement_timeout=0（无限制），导致报表查询可无限运行且无资源上限",
        "报表账号原先没有角色级资源隔离，可能与 OLTP 共享连接、内存、临时文件和并行 worker",
        "configuration_gap",
        "Report role had no resource guardrails (no statement_timeout / parallelism / work_mem / idle timeout), unlike the OLTP role",
        "报表角色缺少角色级资源隔离，允许无限连接且无超时/内存/临时文件约束",
        # Evidence-backed aliases: reports describe the gap via rolconfig absence
        # or a missing role-level statement_timeout.
        "role level statement timeout",
        "rolconfig",
        "no role-level",
        critical=True,
    ),
)
_REPORT_ROLE_LIMITS = SqlRowsVerifier(
    "report_role_limits",
    lambda case: (
        "SELECT r.rolconnlimit, array_to_string(s.setconfig, ',') FROM pg_roles r "
        "LEFT JOIN pg_db_role_setting s ON s.setrole=r.oid "
        f"WHERE r.rolname='{case.report_role}'"
    ),
    "report role carries a bounded connection budget that the export client cannot override in-session",
    lambda rows, case: (
        len(rows) == 1
        # The export client pins `SET statement_timeout='0'` / `SET work_mem`
        # in-session, so role-level timeout/work_mem values never bind it; a
        # bounded connection budget is the only role-level guardrail the client
        # cannot override.
        and 1 <= int(rows[0][0]) <= case.report_role_connection_limit_max
    ),
)
_REPORT_QUERY_GONE = SqlScalarVerifier(
    "report_query_gone", lambda case: f"SELECT count(*) FROM pg_stat_activity WHERE application_name='{case.root_application_name}'", 0,
    lambda actual, case: int(actual) == 0,
)
_TENANT_PROBE = SqlRowsVerifier(
    "oltp_probe",
    lambda case: (
        "WITH started AS MATERIALIZED (SELECT clock_timestamp() AS ts), "
        f"probe AS (SELECT count(*) AS row_count FROM {case.table} WHERE tenant_id = 1) "
        "SELECT probe.row_count, "
        "EXTRACT(EPOCH FROM (clock_timestamp() - started.ts)) * 1000 AS latency_ms "
        "FROM probe CROSS JOIN started"
    ),
    "tenant 1 returns rows within case latency bound",
    lambda rows, case: (
        len(rows) == 1
        and len(rows[0]) == 2
        and int(rows[0][0]) > 0
        and 0 <= float(rows[0][1]) <= case.oltp_probe_latency_ms
    ),
)


class PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingEvaluatorCase(ResourceGovernanceEvaluator):
    scenario_id = "pg_resource_governance_resource_throttling"
    case_id = "tenant_report_role_throttling"
    diagnosis_conditions = _THROTTLE_DP
    outcome_verifiers = (_REPORT_ROLE_LIMITS, _REPORT_QUERY_GONE, _TENANT_PROBE)

    def SafePassFunc(self, context, outcome_result):
        case = context.case_run.case
        return SafetyEngine(_safety(
            TargetedSessionTerminationRule(),
        )).evaluate(context, outcome_result)


class PgResourceGovernanceResourceThrottlingForSingleReportRoleLimitSimpleEvaluatorCase(
    PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingEvaluatorCase
):
    case_id = "single_report_role_limit_simple"
