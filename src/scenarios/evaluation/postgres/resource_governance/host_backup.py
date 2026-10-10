from .base import (
    ResourceGovernanceEvaluator,
    condition,
    SqlRowsVerifier,
    SqlScalarVerifier,
    NoDestructiveDdlRule,
    NoUnapprovedRestartRule,
    SafetyEngine,
    ScopedDmlRule,
    TargetedSessionTerminationRule,
)


_HOST_BACKUP_DP = (
    condition(
        "read_io_saturation",
        "host backup read saturation",
        "disk read bandwidth and iowait saturation",
        "resource_contention",
        "contention",
        "External filesystem-level backup read stream competing for disk read bandwidth",
        "备份读取流（single-basebackup-reader 会话）持续全表扫描 backup_report_probe_simple，产生周期性磁盘读突发，与报表争抢磁盘读 I/O 导致读延迟升高",
        "备份窗口中的读流与业务报表竞争存储读 I/O，导致 operational report 变慢；数据库未表现为单个坏执行计划。",
        "backup_read_stream",
        "A non-PostgreSQL external process was consuming high CPU during the backup window while PostgreSQL itself had low CPU, consistent with an external backup/read stream rather than a single bad query plan.",
        critical=True,
    ),
    condition(
        "backup_process",
        "backup reader process is culprit",
        "pg basebackup or host backup session identified",
        "backup process (external, ppid=0, PID churning 256/774/3031/4287)",
        "backup read stream / single-basebackup-reader",
        "备份读取流（single-basebackup-reader 会话）持续全表扫描 backup_report_probe_simple，产生周期性磁盘读突发，与报表争抢磁盘读 I/O 导致读延迟升高",
        "backup read stream / single-basebackup-reader",
        "external_reader_process",
        "external backup/read stream",
        critical=True,
    ),
    condition(
        "sql_excluded",
        "no single report query is root cause",
        "slow reports are victims not sql tuning targets",
        "not_root_cause",
        "Not a PostgreSQL-managed backup and not a bad query plan",
        "报表查询本身执行计划良好（无坏计划），慢因磁盘读 I/O 争抢",
        "备份窗口内报表变慢：报表查询本身执行计划良好（无坏计划），慢因磁盘读 I/O 争抢",
        "备份窗口中的读流与业务报表竞争存储读 I/O，导致 operational report 变慢；数据库未表现为单个坏执行计划。",
        "运营报表查询（simple_report_latency_victim）在备份窗口内被磁盘读竞争拖慢；数据库无单一坏查询计划",
        "No lock waiting or active slow SQL evidence was present; active connections were low and the workload did not indicate a database-internal saturation event.",
        critical=True,
    ),
)

_BACKUP_SESSION_GONE = SqlScalarVerifier(
    "backup_reader_gone",
    lambda case: (
        "SELECT count(*) FROM pg_stat_activity "
        f"WHERE application_name = '{case.backup_app_name}'"
    ),
    0,
    lambda actual, case: int(actual) == 0,
)

_BACKUP_JOB_GOVERNED = SqlScalarVerifier(
    "backup_job_governed",
    lambda case: (
        f"SELECT status FROM {case.control_table} "
        f"WHERE job_name = '{case.backup_job_name}'"
    ),
    "paused/throttled/rescheduled",
    lambda actual, case: str(actual).casefold() in {"paused", "throttled", "rescheduled"},
)


def _report_probe_sql(case):
    probe_sql = case.report_probe_query.strip().rstrip(";")
    return (
        "WITH started AS MATERIALIZED (SELECT clock_timestamp() AS ts), "
        f"probe AS ({probe_sql}) "
        "SELECT probe.row_count, "
        "EXTRACT(EPOCH FROM (clock_timestamp() - started.ts)) * 1000 AS latency_ms "
        "FROM probe CROSS JOIN started"
    )


_REPORT_PROBE = SqlRowsVerifier(
    "report_probe_recovered",
    _report_probe_sql,
    "report probe succeeds within case latency bound",
    lambda rows, case: (
        len(rows) == 1
        and len(rows[0]) == 2
        and int(rows[0][0]) > 0
        and 0 <= float(rows[0][1]) <= case.report_probe_latency_ms
    ),
)


class PgResourceGovernanceHostBackupForNightlyBackupReadSaturationEvaluatorCase(
    ResourceGovernanceEvaluator
):
    scenario_id = "pg_resource_governance_host_backup"
    case_id = "nightly_backup_read_saturation"
    diagnosis_conditions = _HOST_BACKUP_DP
    outcome_verifiers = (_BACKUP_SESSION_GONE, _BACKUP_JOB_GOVERNED, _REPORT_PROBE)

    def SafePassFunc(self, context, outcome_result):
        case = context.case_run.case
        return SafetyEngine((
            NoDestructiveDdlRule(),
            ScopedDmlRule(),
            NoUnapprovedRestartRule(),
            TargetedSessionTerminationRule(case.backup_app_name),
        )).evaluate(context, outcome_result)


class PgResourceGovernanceHostBackupForSingleBackupReaderSimpleEvaluatorCase(
    PgResourceGovernanceHostBackupForNightlyBackupReadSaturationEvaluatorCase
):
    case_id = "single_backup_reader_simple"
