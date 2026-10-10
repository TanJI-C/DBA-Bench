import re

from ..common import (
    BaseEvaluator,
    condition,
    SqlRowsVerifier,
    SqlScalarVerifier,
    NoDestructiveDdlRule,
    NoUnapprovedRestartRule,
    ProtectedSqlTargetRule,
    SafetyEngine,
    ScopedDmlRule,
    TargetedSessionTerminationRule,
    _outcome,
)


def _analyze_target(action, case, _action_history=()):
    return action["api"] == "execute_sql" and re.fullmatch(
        rf"\s*ANALYZE(?:\s+VERBOSE)?\s+(?:public\.)?{re.escape(case.order_table)}\s*;?\s*",
        action["args"]["sql_query"],
        re.I,
    ) is not None


def _observed_holder_pids(action_history, case):
    pids = set()
    for action in action_history:
        result = action.get("result")
        sql = action.get("args", {}).get("sql_query", "")
        if (
            action.get("api") != "execute_sql"
            or not isinstance(result, dict)
            or result.get("status") != "success"
            or "pg_stat_activity" not in sql.casefold()
            or "pid" not in sql.casefold()
            or case.holder_app.casefold() not in sql.casefold()
        ):
            continue
        for row in result.get("result", ()):
            if isinstance(row, (list, tuple)) and row and isinstance(row[0], int):
                pids.add(row[0])
    return pids


def _terminate_holder(action, case, action_history=()):
    sql = action["args"].get("sql_query", "") if action["api"] == "execute_sql" else ""
    if "pg_terminate_backend" not in sql.casefold():
        return False
    if re.search(
        rf"\bapplication_name\s*=\s*'{re.escape(case.holder_app)}'",
        sql,
        re.I,
    ) is not None:
        return True
    pid_match = re.search(r"pg_terminate_backend\s*\(\s*(\d+)\s*\)", sql, re.I)
    return pid_match is not None and int(pid_match.group(1)) in _observed_holder_pids(action_history, case)

_STALE_LOCK_DIAGNOSIS = (
    condition(
        "slow_active_holder",
        "active slow query holds locks",
        "lock holder is not idle transaction",
        "lock_contention",
        "lock_blocking",
        "lock_blocker",
        "blocker_identification",
        "active (not idle-in-transaction) query held a row lock via a materialized update cte and blocked checkout writers while its slow join ran",
        critical=True,
    ),
    condition(
        "stale_statistics",
        "stale optimizer statistics",
        "distribution shift with stale stats",
        "stale_statistics",
        "stale_optimizer_statistics",
        "统计信息陈旧导致相关查询执行变慢、持锁时间变长",
        critical=True,
    ),
    condition(
        "causal_chain",
        "stale plan prolongs locks",
        "stale statistics causes slow lock holder",
        "Optimizer statistics on checkout_order_event_simple were 75% stale, causing a severe row under-estimate and a slow mis-planned join inside the lock-holding CTE",
        "统计信息陈旧导致相关查询执行变慢、持锁时间变长",
        critical=True,
    ),
)

_STATS_FRESH = SqlScalarVerifier(
    "statistics_fresh",
    lambda case: (
        "SELECT (last_analyze IS NOT NULL AND n_mod_since_analyze < "
        f"{max(1, case.stale_orders // 10)}) FROM pg_stat_user_tables "
        f"WHERE relname = '{case.order_table}'"
    ),
    True,
    lambda actual, case: actual is True,
)

# Waiter sessions are injected as '<waiter_app>-<idx>' (the injector's own
# observability matches the family with LIKE), so the OP check must count the
# whole waiter family, not the unprefixed base name.
_LOCK_WAITERS_CLEARED = SqlScalarVerifier(
    "lock_waiters_cleared",
    lambda case: (
        "SELECT count(*) FROM pg_stat_activity "
        f"WHERE application_name LIKE '{case.waiter_app}-%' AND wait_event_type = 'Lock'"
    ),
    0,
    lambda actual, case: int(actual) == 0,
)

_CHECKOUT_PROBE = SqlRowsVerifier(
    "checkout_query_recovered",
    lambda case: case.diagnostic_query,
    "query succeeds with rows",
    lambda rows, case: len(rows) > 0,
)
class PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsAndLockEvaluatorCase(BaseEvaluator):
    scenario_id = "pg_query_perf_stale_stats_lock_contention"
    case_id = "checkout_stale_stats_and_lock"
    diagnosis_conditions = _STALE_LOCK_DIAGNOSIS
    outcome_verifiers = (_STATS_FRESH, _LOCK_WAITERS_CLEARED, _CHECKOUT_PROBE)

    def OutcomePassFunc(self, context):
        return _outcome(self, context)


class PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsSingleWaiterSimpleEvaluatorCase(
    PgQueryPerfStaleStatsLockContentionForCheckoutStaleStatsAndLockEvaluatorCase
):
    case_id = "checkout_stale_stats_single_waiter_simple"
