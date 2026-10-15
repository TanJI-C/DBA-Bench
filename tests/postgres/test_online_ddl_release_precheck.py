import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import psycopg2
import pytest

from src.scenarios.base import CaseRun
from src.scenarios.postgres.business_change.online_ddl import (
    PgBusinessChangeOnlineDdlInjector,
    PgBusinessChangeOnlineDdlScenario,
)


SCENARIO = PgBusinessChangeOnlineDdlScenario()


class ReleaseEnv:
    def __init__(self, column, orders):
        self.column = column
        self.orders = orders
        self.queries = []

    def execute_sql(self, sql):
        self.queries.append(sql)
        rows = self.column if "information_schema.columns" in sql else self.orders
        return json.dumps({"status": "success", "result": rows})


def evaluate(case, env, actions=()):
    run = CaseRun(
        run_id="online-ddl-test", scenario=SCENARIO, case=case,
        env=env, action_history=[*actions, {"api": "submit", "args": case.reference_report}],
    )
    return case.evaluator(env).evaluate(run)


@pytest.mark.parametrize("case", SCENARIO.cases, ids=lambda case: case.case_id)
def test_release_requirement_is_observable_from_business_request_without_alert_answer(case):
    assert case.target_column not in case.alert
    assert case.target_column not in case.alert_en
    assert "order-note-release-precheck" in case.alert
    assert "order-note-release-precheck" in case.alert_en
    precheck = case.background_workload.profiles[0]
    assert precheck.sql == case.release_precheck_sql
    assert case.target_column in precheck.sql
    assert f"public.{case.table}" in precheck.sql
    assert "ALTER" not in precheck.sql


@pytest.mark.parametrize("case", SCENARIO.cases, ids=lambda case: case.case_id)
@pytest.mark.parametrize("data_type", ["text", "character varying", "character"])
def test_business_recovery_accepts_character_types_without_action_requirements(case, data_type):
    env = ReleaseEnv([[data_type, "YES"]], [[42, None]])
    result = evaluate(case, env)
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (None, True, True)
    assert env.queries[-1] == case.release_precheck_sql
    assert any("table_schema='public'" in sql for sql in env.queries)


@pytest.mark.parametrize("column, orders", [
    ([], [[42, None]]),
    ([["integer", "YES"]], [[42, None]]),
    ([["text", "NO"]], [[42, "note"]]),
    ([["text", "YES"]], []),
])
def test_incomplete_release_fails_outcome_without_implying_unsafe_actions(column, orders):
    result = evaluate(SCENARIO.cases[1], ReleaseEnv(column, orders))
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


@pytest.mark.parametrize("case", SCENARIO.cases, ids=lambda case: case.case_id)
def test_business_probe_errors_are_not_silently_converted_to_pass(case):
    env = ReleaseEnv([["text", "YES"]], [])
    original = env.execute_sql

    def execute(sql):
        if sql == case.release_precheck_sql:
            return json.dumps({"status": "error", "error": "connection lost"})
        return original(sql)

    env.execute_sql = execute
    with pytest.raises(RuntimeError, match="connection lost"):
        evaluate(case, env)


@pytest.mark.parametrize("sql", [
    "ALTER TABLE order_line ADD COLUMN ol_gift_note text",
    "SET lock_timeout='500ms'; ALTER TABLE order_line_gift_audit_shadow ADD COLUMN unexpected text",
])
def test_recovery_does_not_override_unsafe_or_out_of_scope_actions(sql):
    case = SCENARIO.cases[1]
    action = {"api": "execute_sql", "args": {"sql_query": sql}, "result": {"status": "success"}}
    result = evaluate(case, ReleaseEnv([["text", "YES"]], [[42, None]]), [action])
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


@pytest.mark.parametrize("error", [
    None,
    psycopg2.errors.UndefinedColumn('column "ol_gift_note" does not exist'),
    psycopg2.errors.UndefinedTable('relation "order_line" does not exist'),
    psycopg2.OperationalError("connection lost"),
])
def test_setup_admits_only_the_expected_real_application_failure(error):
    case = SCENARIO.cases[1]
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value.execute.side_effect = error
    env = MagicMock()
    env.open_workload_connection.return_value = connection
    injector = PgBusinessChangeOnlineDdlInjector()
    injector.table, injector.target_column = case.table, case.target_column
    context = SimpleNamespace(env=env)

    if isinstance(error, psycopg2.errors.UndefinedColumn):
        evidence = injector.prepare_observability(context)
        assert "ol_gift_note" in evidence["release_precheck_failure"]["error"]
    else:
        with pytest.raises(RuntimeError if error is None else type(error)):
            injector.prepare_observability(context)
    connection.close.assert_called_once()
