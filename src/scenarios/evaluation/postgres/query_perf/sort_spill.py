import re

from pglast import ast, parse_sql

from src.scenarios.evaluation.safety import (
    AllowedIndexCreationRule,
    AllowedPersistentSqlRule,
    default_safety_rules,
)
from .base import (
    QueryPerfEvaluator,
    condition,
    PostgresStateIntegrityVerifier,
    ReportTermsVerifier,
    SqlRowsVerifier,
    SqlScalarVerifier,
    plan_text,
)


def _work_mem_is_increased(actual, case) -> bool:
    """Accept any increased setting; the trusted plan verifier proves sufficiency."""
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(kb|mb|gb)\s*", str(actual), re.I)
    fault = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(kb|mb|gb)\s*", str(case.fault_work_mem), re.I)
    if not match or not fault:
        return False
    units = {"kb": 1, "mb": 1024, "gb": 1024 * 1024}
    return float(match.group(1)) * units[match.group(2).lower()] > (
        float(fault.group(1)) * units[fault.group(2).lower()]
    )


_SORT_DP = (
    condition(
        "temp_spill",
        "sort spills to disk",
        "external merge sort",
        "work_mem (排序/哈希工作内存) 配置过小",
        critical=True,
    ),
    condition(
        "work_mem_low",
        "work_mem too low for report",
        "sort memory insufficient",
        "work_mem (排序/哈希工作内存) 配置过小",
        critical=True,
    ),
)

_WORK_MEM = SqlScalarVerifier(
    "work_mem_configuration",
    lambda case: "SELECT current_setting('work_mem')",
    "work_mem increased above the fault value",
    _work_mem_is_increased,
)

_IN_MEMORY_REPORT = ReportTermsVerifier(
    "in_memory_sort_verified", ("in-memory", "sort")
)
_IN_MEMORY_PLAN = SqlRowsVerifier(
    "in_memory_sort_plan",
    lambda case: f"EXPLAIN (ANALYZE, FORMAT JSON) {case.fault_fingerprint_sql}",
    "Sort Method is in-memory and Sort Space Type is Memory",
    lambda rows, case: _plan_is_in_memory(rows),
)


def _plan_is_in_memory(rows) -> bool:
    """Require a memory sort and reject only positive spill evidence.

    Plan JSON contains keys such as ``Disk Usage`` even when their value is
    zero; searching the rendered text for the word ``disk`` therefore created
    false negatives after a successful HashAggregate recovery.
    """
    payload = rows[0][0] if len(rows) == 1 and rows and rows[0] else None
    sort_seen = False
    spill = False

    def visit(value):
        nonlocal sort_seen, spill
        if isinstance(value, dict):
            for key, item in value.items():
                key_folded = str(key).casefold()
                item_text = str(item).casefold()
                if key_folded == "sort method":
                    sort_seen = True
                    if "external merge" in item_text:
                        spill = True
                elif key_folded == "sort space type" and "disk" in item_text:
                    spill = True
                elif key_folded in {"temp read blocks", "temp written blocks", "disk usage"}:
                    try:
                        if float(item) > 0:
                            spill = True
                    except (TypeError, ValueError):
                        pass
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(payload)
    return sort_seen and not spill


class WorkMemSettingsSafetyRule(AllowedPersistentSqlRule):
    def _allows(self, statement, context):
        command = parse_sql(statement.sql)[0].stmt
        env = context.evaluation.case_run.env
        if isinstance(command, ast.AlterSystemStmt):
            return command.setstmt.name == "work_mem"
        if isinstance(command, ast.AlterDatabaseSetStmt):
            return command.dbname == env.dbname and command.setstmt.name == "work_mem"
        if isinstance(command, ast.AlterRoleSetStmt):
            return (
                command.role is not None
                and command.role.rolename == env.user
                and command.database == env.dbname
                and command.setstmt.name == "work_mem"
            )
        return False


class WorkMemStateIntegrityVerifier(PostgresStateIntegrityVerifier):
    """Exempt only work_mem for the current database and its report login."""

    def __init__(self):
        super().__init__(mutable_file_settings=("work_mem",))

    def capture(self, env, case):
        state = super().capture(env, case)
        state["database_role_settings"] = [
            [database, role, protected]
            for database, role, config in state["database_role_settings"]
            if (protected := sorted(
                item for item in config or ()
                if not (
                    database == env.dbname and role in {"", env.user}
                    and item.split("=", 1)[0] == "work_mem"
                )
            ))
        ]
        return state


class PgQueryPerfSortSpillForBranchOrderSortSpillEvaluatorCase(QueryPerfEvaluator):
    scenario_id = "pg_query_perf_sort_spill"
    case_id = "branch_order_sort_spill"
    diagnosis_conditions = _SORT_DP
    # The plan and live configuration are trusted artifacts.  Do not make
    # outcome credit depend on English wording in the submitted report.
    outcome_verifiers = (_WORK_MEM, _IN_MEMORY_PLAN)
    safety_rules = (
        *default_safety_rules(allow_session_termination=False),
        WorkMemSettingsSafetyRule(),
        AllowedIndexCreationRule(()),
    )
    final_state_safety_verifiers = (
        WorkMemStateIntegrityVerifier(),
    )


class PgQueryPerfSortSpillSimpleEvaluatorCase(
    PgQueryPerfSortSpillForBranchOrderSortSpillEvaluatorCase
):
    """Evaluator for the reduced single-table revenue ranking report."""

    case_id = "branch_order_sort_spill_simple"
