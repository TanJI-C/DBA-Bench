import json
from pathlib import Path
from types import SimpleNamespace

from src.scenarios.evaluation.postgres.system_failure.connection_bloat import _terminate_blocker, _vacuum_target
from src.scenarios.evaluation.postgres.query_perf.stale_stats_lock_contention import _analyze_target, _terminate_holder
from src.scenarios.evaluation.postgres.system_failure.wal_checkpoint_storm import _drop_stalled_slot
from src.scenarios.evaluation.postgres.health_check.config_drift import _has_expected_drift
from src.scenarios.evaluation.outcome import (
    ActionOrderVerifier,
    EventuallySqlScalarVerifier,
    plan_nodes,
    relation_uses_index,
)
from src.scenarios.evaluation.postgres.query_perf.base import accesses_base_table, read_only_sql_statement
from src.scenarios import ALL_SCENARIOS


def _case(scenario_id):
    return next(scenario for scenario in ALL_SCENARIOS if scenario.scenario_id == scenario_id).cases[0]


def _action(sql, result=None):
    action = {"api": "execute_sql", "args": {"sql_query": sql}}
    if result is not None:
        action["result"] = result
    return action


def _order_context(case, actions):
    return SimpleNamespace(action_history=actions, case_run=SimpleNamespace(case=case))


def test_action_order_requires_successful_results():
    case = SimpleNamespace()
    verifier = ActionOrderVerifier(
        "ordered",
        lambda action, _, __: action["args"]["sql_query"] == "first",
        lambda action, _, __: action["args"]["sql_query"] == "second",
        "successful ordered events",
    )
    assert verifier.verify(_order_context(case, [_action("first"), _action("second")])).passed is False
    assert verifier.verify(_order_context(case, [
        _action("first", {"status": "error", "error": "failed"}),
        _action("second", {"status": "success", "result": []}),
    ])).passed is False
    assert verifier.verify(_order_context(case, [
        _action("first", {"status": "success", "result": []}),
        _action("second", {"status": "success", "result": []}),
    ])).passed is True


def test_eventual_scalar_verifier_waits_for_convergence_and_keeps_strict_target():
    class SequenceEnv:
        def __init__(self, values):
            self.values = iter(values)

        def execute_sql(self, sql):
            return json.dumps({"status": "success", "result": [[next(self.values)]]})

    verifier = EventuallySqlScalarVerifier(
        "workers_released",
        lambda case: "SELECT worker_count",
        0,
        lambda actual, case: int(actual) == 0,
        max_attempts=2,
        interval_seconds=0,
    )
    case = SimpleNamespace()
    converged = SimpleNamespace(case_run=SimpleNamespace(case=case, env=SequenceEnv([8, 0])))
    stuck = SimpleNamespace(case_run=SimpleNamespace(case=case, env=SequenceEnv([8, 8])))

    passed = verifier.verify(converged)
    failed = verifier.verify(stuck)

    assert passed.passed is True
    assert passed.actual == 0
    assert passed.evidence[-1] == "attempts=2"
    assert failed.passed is False
    assert failed.actual == 8
    assert failed.evidence[-1] == "attempts=2"


def test_multi_cause_order_matchers_bind_the_case_targets():
    stale = _case("pg_query_perf_stale_stats_lock_contention")
    assert _analyze_target(_action(f"ANALYZE {stale.order_table}"), stale) is True
    assert _analyze_target(_action(f"ANALYZE VERBOSE public.{stale.order_table}"), stale) is True
    assert _analyze_target(_action("ANALYZE unrelated_table"), stale) is False
    assert _terminate_holder(_action(
        f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{stale.holder_app}'"
    ), stale) is True
    assert _terminate_holder(_action(
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = 'wrong-app'"
    ), stale) is False
    observed = _action(
        f"SELECT pid, application_name FROM pg_stat_activity WHERE application_name = '{stale.holder_app}'",
        {"status": "success", "result": [[123, stale.holder_app]]},
    )
    assert _terminate_holder(_action("SELECT pg_terminate_backend(123)", {"status": "success", "result": [[True]]}), stale, (observed,)) is True
    assert _terminate_holder(_action("SELECT pg_terminate_backend(456)", {"status": "success", "result": [[True]]}), stale, (observed,)) is False

    bloat = _case("pg_system_failure_connection_bloat")
    assert _terminate_blocker(_action(
        f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{bloat.blocker_app_name}'"
    ), bloat) is True
    assert _vacuum_target(_action(f"VACUUM {bloat.table}"), bloat) is True
    assert _vacuum_target(_action(f"VACUUM (VERBOSE, ANALYZE) public.{bloat.table}"), bloat) is True
    assert _vacuum_target(_action("VACUUM unrelated_table"), bloat) is False

    wal = _case("pg_system_failure_wal_checkpoint_storm")
    assert _drop_stalled_slot(_action(f"SELECT pg_drop_replication_slot('{wal.slot_name}')"), wal) is True
    assert _drop_stalled_slot(_action(f"SELECT pg_drop_replication_slot('{wal.active_slot_name}')"), wal) is False


def test_heavy_offset_accepts_any_read_only_business_query_but_rejects_non_queries():
    case = _case("pg_query_perf_heavy_offset_pagination")
    ordinary_limit = f"SELECT {case.order_column} FROM {case.table} LIMIT 1"
    statement = read_only_sql_statement(ordinary_limit)

    assert statement is not None
    assert accesses_base_table(statement, case.table) is True
    assert read_only_sql_statement(f"EXPLAIN {ordinary_limit}") is None
    assert read_only_sql_statement(f"SELECT 1; SELECT 2") is None
    assert read_only_sql_statement(f"WITH {case.table} AS (VALUES (1)) SELECT * FROM {case.table}") is not None
    cte_statement = read_only_sql_statement(f"WITH {case.table} AS (VALUES (1)) SELECT * FROM {case.table}")
    assert accesses_base_table(cte_statement, case.table) is False


def test_plan_access_is_correlated_with_the_target_relation():
    rows = [[{"Plan": {
        "Node Type": "Nested Loop",
        "Plans": [
            {"Node Type": "Seq Scan", "Relation Name": "product"},
            {"Node Type": "Index Scan", "Relation Name": "calendar_day", "Index Name": "calendar_day_pkey"},
        ],
    }}]]
    assert relation_uses_index(rows, "product") is False
    assert relation_uses_index(rows, "calendar_day", "calendar_day_pkey") is True

    mixed_target = [[{"Plan": {
        "Node Type": "Append",
        "Plans": [
            {"Node Type": "Index Scan", "Relation Name": "product", "Index Name": "product_idx"},
            {"Node Type": "Seq Scan", "Relation Name": "product"},
        ],
    }}]]
    assert relation_uses_index(mixed_target, "product") is False

def test_plan_verifier_rejects_garbage_and_unrelated_indexes():
    assert plan_nodes([[{"garbage": "not a plan"}]]) == ()

    rows = [[{"Plan": {
        "Node Type": "Index Scan",
        "Relation Name": "product",
        "Index Name": "product_pkey",
    }}]]
    assert relation_uses_index(rows, "product", "idx_product_pr_category_func") is False


def test_config_drift_requires_new_capacity_and_old_target_settings():
    case = _case("pg_health_check_config_drift")
    old_rows = [
        [name, case.old_baseline_params[name], "configuration file", False, case.memory_limit_mb]
        for name in ("shared_buffers", "effective_cache_size", "maintenance_work_mem", "work_mem")
    ]
    assert _has_expected_drift(old_rows, case) is True

    old_capacity = [row[:4] + [8192] for row in old_rows]
    assert _has_expected_drift(old_capacity, case) is False

    recommended = [list(row) for row in old_rows]
    recommended[0][1] = "8GB"
    recommended[1][1] = "48GB"
    recommended[2][1] = "1GB"
    assert _has_expected_drift(recommended, case) is False


def test_visualization_renders_diagnosis_none_as_na():
    root = Path(__file__).parents[2] / "src" / "visualization" / "static"
    for name in ("experiments.js", "raw-traces.js"):
        source = (root / name).read_text(encoding="utf-8")
        assert "passMark" in source
        assert '"N/A"' in source
