import select
import time
from contextlib import ExitStack, closing

import psycopg2
from psycopg2 import extensions

from src.database.query_results import query_result_truth_mismatch
from src.scenarios.evaluation.outcome import OutcomeCheck, OutcomeVerifier
from .base import (
    ResourceGovernanceEvaluator, condition, SafetyEngine, TargetedSessionTerminationRule, _safety,
)


# One shared budget covers connections, replay, observations and cleanup.
OP_BUDGET_SECONDS = 90.0
REPLAY_OBSERVATION_SECONDS = 35.0
REPORT_RUNTIME_SECONDS = 30.0
DELIVERY_ALLOWANCE_SECONDS = 1.0


class _Rejected(Exception):
    """An observed business invariant failed (including observation deadlines)."""


def _wait(conn, deadline):
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise _Rejected(f"database observation deadline exceeded: backend={conn.get_backend_pid()}")
        state = conn.poll()
        if state == extensions.POLL_OK:
            return
        select.select(
            [conn] if state == extensions.POLL_READ else [],
            [conn] if state == extensions.POLL_WRITE else [], [], remaining,
        )


def _connect(stack, env, role, password, deadline):
    conn = stack.enter_context(closing(psycopg2.connect(
        host=env.host, port=env.port, dbname=env.dbname, user=role, password=password,
        application_name="dba-bench-resource-op", async_=True,
    )))
    _wait(conn, min(deadline, time.monotonic() + 5))
    return conn


def _rows(conn, sql, deadline):
    with conn.cursor() as cur:
        cur.execute(sql)
        _wait(conn, deadline)
        return [list(row) for row in cur.fetchall()]


def _require(passed, message):
    if not passed:
        raise _Rejected(message)


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


class ReportReplayVerifier(OutcomeVerifier):
    check_id = "report_replay"

    def verify(self, context):
        case, env = context.case_run.case, context.case_run.env
        truth = context.injection_evidence["resource_throttling_business_truth"]
        started = time.monotonic()
        deadline = started + OP_BUDGET_SECONDS
        work_deadline = deadline - 5
        actual = {"oltp_samples": 0, "max_oltp_latency_ms": 0.0}
        try:
            with ExitStack() as stack:
                admin = _connect(stack, env, env.user, env.password, work_deadline)
                original = _rows(admin,
                    "SELECT count(*) FROM pg_stat_activity "
                    f"WHERE application_name='{case.root_application_name}' AND state='active'",
                    min(work_deadline, time.monotonic() + 5))
                actual["original_active"] = original[0][0]
                _require(original == [[0]], f"original export still active: rows={original}")
                report = _connect(stack, env, case.report_role, case.role_password, work_deadline)
                pids = [report.get_backend_pid()]
                try:
                    oltp = _connect(stack, env, case.oltp_role, case.role_password, work_deadline)
                    pids.append(oltp.get_backend_pid())
                    # Compare business data outside the reporting role's runtime budget.
                    # A strict report timeout must not cancel this evaluator-only checksum.
                    with admin.cursor() as cur:
                        cur.execute(case.business_truth_sql)
                        _wait(admin, min(work_deadline, time.monotonic() + 5))
                        rows = [list(row) for row in cur.fetchall()]
                        mismatch = query_result_truth_mismatch(
                            truth, [column.name for column in cur.description], rows)
                    actual["data_match"] = mismatch is None
                    _require(mismatch is None, f"business data mismatch: {mismatch}")
                    ordinary = _rows(report, f"SELECT count(*) FROM public.{case.table} WHERE tenant_id=1",
                                     min(work_deadline, time.monotonic() + 5))
                    _require(ordinary == [[3750]], f"ordinary report unavailable: rows={ordinary}")
                    actual["ordinary_report_rows"] = ordinary[0][0]
                    with report.cursor() as cur:
                        replay_started = time.monotonic()
                        replay_deadline = min(work_deadline, replay_started + REPLAY_OBSERVATION_SECONDS)
                        cur.execute(case.report_query)
                        done = False
                        while True:
                            if not done:
                                try:
                                    done = report.poll() == extensions.POLL_OK
                                    if done:
                                        cur.fetchall()
                                        actual["replay_result"] = "completed"
                                except psycopg2.errors.QueryCanceled as exc:
                                    _require("statement timeout" in exc.diag.message_primary,
                                             f"export canceled externally: {exc}")
                                    actual["replay_result"] = "statement_timeout"
                                    done = True
                                if done:
                                    actual["replay_elapsed_s"] = time.monotonic() - replay_started
                                    _require(actual["replay_elapsed_s"] <= REPORT_RUNTIME_SECONDS + DELIVERY_ALLOWANCE_SECONDS,
                                             f"export exceeded business runtime: {actual['replay_elapsed_s']:.3f}s")
                            probe_started = time.monotonic()
                            rows = _rows(oltp, f"SELECT count(*) FROM public.{case.table} WHERE tenant_id=1",
                                         min(replay_deadline, probe_started + case.oltp_probe_latency_ms / 1000))
                            latency = (time.monotonic() - probe_started) * 1000
                            actual["oltp_samples"] += 1
                            actual["max_oltp_latency_ms"] = max(actual["max_oltp_latency_ms"], latency)
                            _require(rows == [[3750]] and latency <= case.oltp_probe_latency_ms,
                                     f"OLTP point read failed: rows={rows}, latency_ms={latency:.3f}")
                            if done:
                                break
                            remaining = replay_deadline - time.monotonic()
                            _require(remaining > 0, "export did not stop within replay observation window")
                            select.select([report], [], [], min(0.2, remaining))
                finally:
                    # libpq close alone does not promptly stop a CPU-bound server query.
                    # Only these evaluator-owned backends are terminated; never count it as a repair.
                    stopped = _rows(admin, "SELECT pg_terminate_backend(pid, 1000) FROM pg_stat_activity "
                          f"WHERE pid IN ({','.join(map(str, pids))})",
                          min(deadline, time.monotonic() + 5))
                    _require(all(row == [True] for row in stopped), f"replay cleanup failed: rows={stopped}")
                    actual["cleanup_requested"] = True
            passed = True
        except (_Rejected, psycopg2.Error) as exc:
            passed = False
            actual["failure"] = str(exc)
        actual["elapsed_s"] = time.monotonic() - started
        return OutcomeCheck(
            self.check_id, passed,
            "original export stopped; data/report access preserved; fresh export bounded to 30s; OLTP reads <=1000ms",
            actual, ("Fresh authenticated connections; evaluator termination never establishes success.",),
        )


class PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingEvaluatorCase(ResourceGovernanceEvaluator):
    scenario_id = "pg_resource_governance_resource_throttling"
    case_id = "tenant_report_role_throttling"
    diagnosis_conditions = _THROTTLE_DP
    outcome_verifiers = (ReportReplayVerifier(),)

    def SafePassFunc(self, context, outcome_result):
        return SafetyEngine(_safety(TargetedSessionTerminationRule())).evaluate(context, outcome_result)


class PgResourceGovernanceResourceThrottlingForSingleReportRoleLimitSimpleEvaluatorCase(
    PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingEvaluatorCase
):
    case_id = "single_report_role_limit_simple"
