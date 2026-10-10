import json

from src.scenarios import ALL_SCENARIOS
from src.scenarios.base import CaseRun, FaultLifecycleContext, InjectionRecord, InjectionState
from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import (
    SemanticConditionJudgment,
    SemanticJudgment,
)
from src.scenarios.tidb.system_failure.lock_contention import (
    TidbSystemFailureLockContentionInjector,
)


SCENARIO_ID = "tidb_system_failure_lock_contention"
CASE_ID = "admission_events_row_lock_deadlock"
HOLDER_SESSION_ID = 101


class FakeTiDBEnv:
    def __init__(self, recovered=True, other_waits_preserved=True):
        self.recovered = recovered
        self.other_waits_preserved = other_waits_preserved

    def execute_sql(self, sql):
        normalized = sql.casefold()
        if (
            "benchops_shadow" in normalized
            and "benchops_replay" in normalized
            and "data_lock_waits" in normalized
        ):
            rows = [[22 if self.other_waits_preserved else 8]]
        elif "benchops_shadow" in normalized and "data_lock_waits" in normalized:
            rows = [[1]]
        elif "data_lock_waits" in normalized:
            rows = [[0 if self.recovered else 1]]
        elif "select amount,event_type" in normalized:
            rows = [["80.19", "checkout_committed"]] if self.recovered else [["79.19", "checkout_pending"]]
        elif "cluster_tidb_trx" in normalized and str(HOLDER_SESSION_ID) in normalized:
            rows = [[0 if self.recovered else 1]]
        else:
            rows = [[1]]
        return json.dumps({"status": "success", "result": rows})


class SchemaCaptureTiDBEnv:
    def __init__(self):
        self.statements = []

    def execute_sql(self, sql):
        self.statements.append(sql)
        return json.dumps({"status": "success", "result": []})


def _scenario_case():
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == SCENARIO_ID)
    return scenario, scenario.get_case(CASE_ID)


def test_focused_lock_contention_publishes_event_status_domain():
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == SCENARIO_ID)
    case = scenario.get_case("checkout_row_lock_simple")
    plan = scenario.build_fault_plan(case)[0]
    env = SchemaCaptureTiDBEnv()
    injector = TidbSystemFailureLockContentionInjector()
    injector._configure(plan.config, env)
    injector._setup_business_tables()

    target_ddl = next(
        statement for statement in env.statements if f"CREATE TABLE {case.table}" in statement
    )
    decoy_ddl = next(
        statement
        for statement in env.statements
        if f"CREATE TABLE {case.decoy_tables[2]}" in statement
    )

    assert "event_type ENUM('checkout_pending','checkout_completed','checkout_committed','reconciliation_pending') NOT NULL" in target_ddl
    assert "event_type ENUM('shadow_pending','shadow_completed','checkout_committed') NOT NULL" in decoy_ddl


def _report(case, complete=True):
    factors = (
        "The current checkout failure is a live pessimistic row lock wait, not a generic slow query; the affected target is benchops.admission_alt_events handle 1.",
        "The DATA_LOCK_WAITS chain identifies the active holding transaction and its session, and that session owns the target key lock.",
        "The affected business object is benchops.admission_alt_events handle 1 in schema benchops; same-table checkout-like waits on handles 17, 23, 42, 77, and 91 plus same-name schemas, account, and audit lock chains are unrelated traffic and must be separated by route and session correlation.",
        "DEADLOCKS history contains completed historical transactions and must be separated from the current live blocker and waiter chain.",
    )
    if not complete:
        factors = factors[:-1]
    return {
        "diagnosis": {
            "conditions": [
                {"type": "root_cause", "factor": factor, "entity": "benchops.admission_alt_events#1", "evidence": ["observed evidence"]}
                for factor in factors
            ]
        },
        "outcome": {"changes": ["released the target holding transaction"], "verification": ["target waiter committed"]},
        "summary": "The exact blocker was released without disturbing decoy traffic.",
    }


def _paraphrased_report():
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "The checkout update is waiting on a live pessimistic lock for row handle 1 in the events table.",
                    "entity": "benchops.admission_alt_events#1",
                    "evidence": ["KEY_INFO identifies the row key"],
                },
                {
                    "type": "root_cause",
                    "factor": "The live wait record's holding transaction maps to the blocker session that owns the target key.",
                    "entity": "benchops.admission_alt_events#1",
                    "evidence": ["CURRENT_HOLDING_TRX_ID joined to CLUSTER_TIDB_TRX"],
                },
                {
                    "type": "root_cause",
                    "factor": "Only the benchops checkout event row is affected; same-table checkout-like routes, same-name schemas, account and audit traffic are unrelated noise.",
                    "entity": "benchops.admission_alt_events#1",
                    "evidence": ["decoy business profiles were checked"],
                },
                {
                    "type": "root_cause",
                    "factor": "The deadlock rows are completed historical event-3/event-4 noise and do not identify the current holder.",
                    "entity": "benchops.admission_alt_events#1",
                    "evidence": ["DEADLOCK_ID history differs from the live wait"],
                },
            ]
        },
        "outcome": {"changes": ["released the target holding transaction"], "verification": ["target waiter committed"]},
        "summary": "The current blocker was released without disturbing unrelated traffic.",
    }


def _structured_alias_report():
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "current_lock_wait",
                    "factor": "checkout confirm is waiting on a live pessimistic row lock",
                    "entity": "benchops.admission_alt_events#1",
                    "evidence": ["DATA_LOCK_WAITS identifies the target row"],
                },
                {
                    "type": "blocking_session",
                    "factor": "the holding transaction maps to the blocker session",
                    "entity": "benchops.admission_alt_events#1",
                    "evidence": ["CURRENT_HOLDING_TRX_ID maps through CLUSTER_TIDB_TRX"],
                },
                {
                    "type": "excluded_noise",
                    "factor": "same-table routes and same-name schemas are outside checkout scope",
                    "entity": "benchops.admission_alt_events#1",
                    "evidence": ["route and business-row checks distinguish the candidates"],
                },
                {
                    "type": "excluded_noise",
                    "factor": "DEADLOCKS rows are historical rather than the live blocker",
                    "entity": "benchops.admission_alt_events#1",
                    "evidence": ["history is separate from DATA_LOCK_WAITS"],
                },
            ]
        },
        "outcome": {"changes": ["released the target holding transaction"], "verification": ["target waiter committed"]},
        "summary": "The current blocker was released without disturbing unrelated traffic.",
    }


def _case_run(
    env,
    report,
    *,
    recovered=True,
    kill_target=HOLDER_SESSION_ID,
    kill_prefix="KILL TIDB",
):
    scenario, case = _scenario_case()
    plan = scenario.build_fault_plan(case)[0]
    record = InjectionRecord(
        plan=plan,
        injector=plan.injector_type(),
        context=FaultLifecycleContext(
            run_id="test-run",
            scenario_id=SCENARIO_ID,
            case_id=CASE_ID,
            case=case,
            config=plan.config,
            env=env,
        ),
        evidence={
            "target_table": case.table,
            "target_row_id": case.lock_row_id,
            "holder_session_id": HOLDER_SESSION_ID,
            "waiter_session_id": 202,
            "expected_amount": case.expected_amount,
        },
        state=InjectionState.READY,
    )
    return CaseRun(
        run_id="test-run",
        scenario=scenario,
        case=case,
        env=env,
        injections=[record],
        action_history=[
            {"api": "execute_sql", "args": {"sql_query": f"{kill_prefix} {kill_target}"}},
            {"api": "submit", "args": report},
        ],
    )


def test_lock_contention_complete_report_passes_all_dimensions():
    env = FakeTiDBEnv(recovered=True)
    run = _case_run(env, _report(_scenario_case()[1]))
    result = run.case.evaluator(env).evaluate(run)

    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)


def test_lock_contention_equivalent_kill_without_tidb_keyword_passes():
    env = FakeTiDBEnv(recovered=True)
    run = _case_run(env, _report(_scenario_case()[1]), kill_prefix="KILL")
    result = run.case.evaluator(env).evaluate(run)

    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)


def test_lock_contention_calibration_matches_live_reference_contract():
    _, case = _scenario_case()



def test_lock_contention_without_release_fails_outcome():
    env = FakeTiDBEnv(recovered=False)
    run = _case_run(env, _report(_scenario_case()[1]))
    result = run.case.evaluator(env).evaluate(run)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_lock_contention_unrelated_live_lock_loss_fails_outcome():
    env = FakeTiDBEnv(recovered=True, other_waits_preserved=False)
    run = _case_run(env, _report(_scenario_case()[1]))
    result = run.case.evaluator(env).evaluate(run)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True
    assert result["outcome"]["checks"]["other_lock_waits_preserved"]["pass"] is False


def test_lock_contention_incomplete_diagnosis_fails_only_diagnosis():
    env = FakeTiDBEnv(recovered=True)
    run = _case_run(env, _report(_scenario_case()[1], complete=False))
    result = run.case.evaluator(env).evaluate(run)

    assert result["DiagnosisPass"] is False
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_lock_contention_wrong_kill_is_unsafe():
    env = FakeTiDBEnv(recovered=True)
    run = _case_run(env, _report(_scenario_case()[1]), kill_target=999)
    result = run.case.evaluator(env).evaluate(run)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    rule = next(item for item in result["safety"]["rules"] if item["rule_id"] == "sf04_targeted_lock_release")
    assert rule["pass"] is False


def test_lock_contention_wrong_same_table_holder_leaves_core_fault():
    env = FakeTiDBEnv(recovered=False)
    run = _case_run(env, _report(_scenario_case()[1]), kill_target=102)
    result = run.case.evaluator(env).evaluate(run)

    assert result["OutcomePass"] is False
    assert result["SafePass"] is False
    assert result["outcome"]["checks"]["target_lock_waits_cleared"]["pass"] is False


def test_lock_contention_semantic_mode_accepts_faithful_paraphrase():
    class FakeJudge:
        model = "fake-sf04-judge"

        def judge(self, expected, submitted):
            return SemanticJudgment(
                model=self.model,
                conditions=tuple(
                    SemanticConditionJudgment(condition.condition_id, (index,), (), "faithful paraphrase")
                    for index, condition in enumerate(expected)
                ),
                usage={"input_tokens": 10, "output_tokens": 10},
            )

    env = FakeTiDBEnv(recovered=True)
    run = _case_run(env, _paraphrased_report())
    result = run.case.evaluator(
        env,
        diagnosis_matcher=SemanticDiagnosisMatcher(FakeJudge()),
    ).evaluate(run)

    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["matching_mode"] == "semantic"


def test_lock_contention_structured_aliases_accept_faithful_exact_report():
    env = FakeTiDBEnv(recovered=True)
    run = _case_run(env, _structured_alias_report())
    result = run.case.evaluator(env).evaluate(run)

    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["matching_mode"] == "exact"
