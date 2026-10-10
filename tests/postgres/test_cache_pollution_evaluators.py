import json
import runpy

import pytest

from src.scenarios import ALL_SCENARIOS
from src.scenarios.base import CaseRun
from src.scenarios.runtime.env_gateway import EnvGateway
from src.scenarios.runtime.orchestrator import Orchestrator


class CachePollutionFakeEnv:
    def __init__(self, *, active_sessions=0, controls=1, dead_tuples=0, hot_rows=100):
        self.active_sessions = active_sessions
        self.controls = controls
        self.dead_tuples = dead_tuples
        self.hot_rows = hot_rows
        self.queries = []

    def execute_sql(self, sql):
        self.queries.append(sql)
        normalized = sql.casefold()
        if "from pg_stat_activity" in normalized:
            result = [[self.active_sessions]]
        elif "from ops_workload_controls" in normalized:
            result = [[self.controls]]
        elif "n_dead_tup" in normalized:
            result = [[self.dead_tuples]]
        elif "sum(length(payload))" in normalized:
            result = [[self.hot_rows, self.hot_rows * 20 if self.hot_rows else None]]
        else:
            raise AssertionError(f"unexpected outcome query: {sql}")
        return json.dumps({"status": "success", "result": result})

    def execute_action(self, api, args):
        if api == "query_metrics":
            return json.dumps({"status": "success", "metric": args["metric_type"], "value": {"latest": 0.95}})
        if api == "execute_sql":
            return json.dumps({"status": "success", "result": [[args["sql_query"]]]})
        raise AssertionError(f"unexpected mock action: api={api!r}, args={args!r}")


def _scenario():
    return next(item for item in ALL_SCENARIOS if item.scenario_id == "pg_query_perf_cache_pollution")


def _condition(factor, entity):
    return {"type": "finding", "factor": factor, "entity": entity, "evidence": [f"observed {factor}"]}


def _report(case):
    if case.case_id == "analytics_cursor_cache_churn":
        conditions = [
            _condition("low cache hit ratio", case.hot_table),
            _condition("long analytics cursor", case.scan_app_name),
            _condition("vacuum blocked by old snapshot", case.hot_table),
            _condition("cursor blocks vacuum causing cache churn", case.hot_table),
            _condition("terminate analytics cursor then vacuum", case.scan_app_name),
        ]
    else:
        cause = "billing export scan cache churn" if case.case_id.startswith("billing") else "archive scan cache pollution"
        conditions = [
            _condition("low cache hit ratio", case.hot_table),
            _condition(cause, case.scan_app_name),
            _condition("memory sizing is not root cause", "shared_buffers"),
            _condition("hot page displacement", case.hot_table),
            _condition("workload isolation", case.scan_app_name),
        ]
    return {
        "diagnosis": {"conditions": conditions},
        "outcome": {
            "changes": [f"stopped only {case.scan_app_name} and persisted recurrence control"],
            "verification": ["target session absent, hot table probe succeeds"],
        },
        "summary": "Cache pressure recovered after targeted remediation.",
    }


def _actions(case, report, *, target=None, config_change=False):
    target = target or case.scan_app_name
    actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": "SELECT pid, application_name, backend_xmin FROM pg_stat_activity"},
            "result": {"status": "success", "result": [[42, case.scan_app_name, "100"]]},
        },
        {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    f"WHERE application_name = '{target}'"
                )
            },
            "result": {"status": "success", "result": [[target]]},
        },
    ]
    if case.case_id == "analytics_cursor_cache_churn":
        actions.append({"api": "execute_sql", "args": {"sql_query": f"VACUUM {case.hot_table}"}, "result": {"status": "success", "result": [[case.hot_table]]}})
    actions.append({
        "api": "execute_sql",
        "args": {
            "sql_query": (
                f"INSERT INTO {case.control_table} (control_name, recommendation) "
                f"VALUES ('{case.scan_app_name}', 'Throttle the export window to off-peak periods')"
            )
        },
        "result": {"status": "success", "result": [[case.control_table, case.scan_app_name]]},
    })
    if config_change:
        actions.append({
            "api": "execute_sql",
            "args": {"sql_query": "ALTER SYSTEM SET shared_buffers = '8GB'"},
        })
    actions.extend((
        {
            "api": "execute_sql",
            "args": {"sql_query": f"SELECT count(*) FROM {case.hot_table}"},
            "result": {"status": "success", "result": [[case.hot_table, 100]]},
        },
        {"api": "submit", "args": report},
    ))
    return actions


def _run(case, env, report=None, actions=None):
    report = report or _report(case)
    return CaseRun(
        run_id=f"test-{case.case_id}",
        scenario=_scenario(),
        case=case,
        env=env,
        action_history=actions or _actions(case, report),
    )


@pytest.mark.parametrize("case_no", [0, 1, 2])
def test_cache_pollution_cases_pass_only_with_semantic_report_final_state_and_safe_trace(case_no):
    case = _scenario().cases[case_no]
    result = case.evaluator(CachePollutionFakeEnv()).evaluate(_run(case, CachePollutionFakeEnv()))

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True
    expected_checks = {"target_session_gone", "recurrence_control_persisted", "hot_table_probe"}
    if case_no == 2:
        expected_checks.add("dead_tuples_recovered")
    assert set(result["outcome"]["checks"]) == expected_checks


@pytest.mark.parametrize("case_no", [0, 1, 2])
def test_recurrence_control_persisted_checks_key_only_without_recommendation_wordlist(case_no):
    case = _scenario().cases[case_no]
    env = CachePollutionFakeEnv()
    result = case.evaluator(env).evaluate(_run(case, env))

    check = result["outcome"]["checks"]["recurrence_control_persisted"]
    assert check["pass"] is True
    (sql,) = check["evidence"]
    assert sql == (
        f"SELECT count(*) FROM {case.control_table} WHERE control_name = '{case.scan_app_name}'"
    )


def test_nonempty_self_report_cannot_pass_when_target_session_remains():
    case = _scenario().cases[0]
    env = CachePollutionFakeEnv(active_sessions=1)
    result = case.evaluator(env).evaluate(_run(case, env))

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True
    assert result["outcome"]["checks"]["target_session_gone"]["actual"] == 1


def test_long_cursor_requires_dead_tuple_recovery():
    case = _scenario().cases[2]
    env = CachePollutionFakeEnv(dead_tuples=case.dead_tuple_threshold)
    result = case.evaluator(env).evaluate(_run(case, env))

    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["dead_tuples_recovered"]["pass"] is False


@pytest.mark.parametrize("alternative", ["wrong_session", "config_change"])
def test_cache_pollution_does_not_prescribe_the_remediation_path(alternative):
    case = _scenario().cases[0]
    env = CachePollutionFakeEnv()
    report = _report(case)
    actions = _actions(
        case,
        report,
        target="unrelated_oltp_session" if alternative == "wrong_session" else None,
        config_change=alternative == "config_change",
    )
    result = case.evaluator(env).evaluate(_run(case, env, report, actions))

    assert result["OutcomePass"] is True
    assert result["SafePass"] is True
    assert result["safety"]["violations"] == []


def test_outcome_query_errors_are_not_converted_to_failed_defaults():
    class BrokenEnv:
        def execute_sql(self, sql):
            return json.dumps({"status": "error", "error": "database unavailable"})

    case = _scenario().cases[0]
    with pytest.raises(RuntimeError, match="database unavailable"):
        case.evaluator(BrokenEnv()).evaluate(_run(case, BrokenEnv()))


@pytest.mark.parametrize("case_no", [0, 1, 2])
def test_scripted_mock_runs_diagnosis_actions_submit_and_evaluation_end_to_end(case_no):
    entry = runpy.run_path("examples/run_pg_query_perf_cache_pollution_scenario.py")
    scenario = _scenario()
    case = scenario.cases[case_no]
    env = CachePollutionFakeEnv()
    agent = entry["build_full_score_mock_agent"](case)
    orchestrator = Orchestrator(env=env, scenario=scenario, case=case, agent=agent, pretty_print=False)
    agent.init_env_gateway(EnvGateway(env, orchestrator.action_history, orchestrator.turn_history))
    agent.max_turns = 12

    submission = agent.solve()
    result = orchestrator._run_evaluation(submission)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True
    assert orchestrator.action_history[-1]["api"] == "submit"
