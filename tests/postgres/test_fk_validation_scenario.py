"""Focused tests for the pg_business_change_fk_validation scenario."""

import json
from pathlib import Path

import pytest

from src.scenarios.base import CaseRun, InjectionRecord
from src.scenarios.evaluation.diagnosis import ExactDiagnosisMatcher
from src.scenarios.evaluation.outcome import EventuallySqlScalarVerifier
from src.scenarios.evaluation.postgres.business_change import (
    PgBusinessChangeFkValidationForOrderItemsFkValidateStormEvaluatorCase,
)
from src.scenarios.evaluation.postgres.business_change import fk_validation as fv
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.postgres import PgBusinessChangeFkValidationScenario


SCENARIO = PgBusinessChangeFkValidationScenario()
CASES = {case.case_id: case for case in SCENARIO.cases}


# ---------------------------------------------------------------------------
# fast verifier tuples (production tuples use 10s retry windows)
# ---------------------------------------------------------------------------

def _fast_outcome(case_id):
    fk_fast = EventuallySqlScalarVerifier(
        "fk_constraint_validated",
        lambda case: (
            "SELECT convalidated FROM pg_constraint "
            f"WHERE conname = '{case.fk_name}' AND conrelid = '{case.table}'::regclass"
        ),
        True,
        lambda actual, case: actual is True,
        max_attempts=2,
        interval_seconds=0.05,
    )
    sessions_fast = EventuallySqlScalarVerifier(
        "incident_sessions_cleared",
        lambda case: (
            "SELECT count(*) FROM pg_stat_activity WHERE pid <> pg_backend_pid() "
            f"AND application_name = ANY({fv._sql_array(case.incident_app_names)})"
        ),
        0,
        lambda actual, case: int(actual) == 0,
        max_attempts=2,
        interval_seconds=0.05,
    )
    shared = (
        fv._BusinessReadsRestored(samples=2, interval_seconds=0.05, timeout_seconds=1),
        fv._NoRelationLockWaiters(samples=2, interval_seconds=0.05),
        fk_fast,
        sessions_fast,
        fv._ORDER_ITEMS_INTACT,
        fv._CUSTOMERS_INTACT,
    )
    if case_id == "order_items_fk_validate_storm":
        return shared + (fv._PEER_INTACT,)
    return shared


# ---------------------------------------------------------------------------
# fake environments
# ---------------------------------------------------------------------------

class FakeFkEnv:
    """Simulate the final-state SQL surface used by the evaluator verifiers."""

    def __init__(
        self,
        *,
        fixed=True,
        sessions_cleared=True,
        business_readable=True,
        fk_validated=None,
        order_rows=800_000,
        orphan_rows=5,
        customers_rows=2000,
        peer_rows=50_000,
    ):
        self.fixed = fixed
        self.sessions_cleared = sessions_cleared
        self.business_readable = business_readable
        self.fk_validated = fixed if fk_validated is None else fk_validated
        self.order_rows = order_rows
        self.orphan_rows = orphan_rows
        self.customers_rows = customers_rows
        self.peer_rows = peer_rows

    def execute_sql(self, sql):
        normalized = sql.casefold()
        if "pg_constraint" in normalized and "convalidated" in normalized:
            rows = [[self.fk_validated]]
        elif "pg_locks" in normalized:
            rows = [[0 if self.fixed else 4]]
        elif "pg_stat_activity" in normalized:
            rows = [[0 if self.sessions_cleared else 2]]
        elif "order_items_peer" in normalized:
            rows = [[self.peer_rows]]
        elif "join customers" in normalized:
            rows = [[self.order_rows - self.orphan_rows]]
        elif " from order_items" in normalized:
            if not self.business_readable:
                return json.dumps({
                    "status": "error",
                    "error": "canceling statement due to statement timeout",
                })
            rows = [[self.order_rows]]
        elif "customers" in normalized:
            rows = [[self.customers_rows]]
        else:
            rows = [[0]]
        return json.dumps({"status": "success", "result": rows})


class _Cond:
    def __init__(self, factor, entity="order_items", evidence=("observed",)):
        self.type = "finding"
        self.factor = factor
        self.entity = entity
        self.evidence = tuple(evidence)


class _Report:
    def __init__(self, conditions):
        self.diagnosis = type("D", (), {"conditions": tuple(conditions)})


def _case_run(case_id, env, actions):
    case = CASES[case_id]
    scenario = PgBusinessChangeFkValidationScenario()
    run = CaseRun(run_id=f"test-{case_id}", scenario=scenario, case=case, env=env)
    run.action_history.extend(actions)
    plan = scenario.build_fault_plan(case)[0]
    run.injections.append(InjectionRecord(
        plan=plan,
        injector=object(),
        context=None,
        evidence={
            "baseline": {
                "order_items_rows": 800_000,
                "customers_rows": 2000,
                "peer_rows": 50_000,
                "orphan_rows": 5,
            },
            "pipeline_steps": [[1, "add_fk_not_valid", "done"], [2, "validate_fk", "running"]],
        },
    ))
    return run


def _submit_actions(case_id, report=None, extra_actions=()):
    case = CASES[case_id]
    actions = list(extra_actions)
    actions.append({
        "api": "submit",
        "args": report if report is not None else case.reference_report,
    })
    return actions


def _evaluate(case_id, env, actions):
    evaluator = CASES[case_id].evaluator(env)
    evaluator.outcome_verifiers = _fast_outcome(case_id)
    return evaluator.evaluate(_case_run(case_id, env, actions))


# ---------------------------------------------------------------------------
# registration and fault plan
# ---------------------------------------------------------------------------

def test_registration_identity_and_continuous_case_numbers():
    assert SCENARIO.scenario_id == "pg_business_change_fk_validation"
    assert [case.case_no for case in SCENARIO.cases] == list(range(len(SCENARIO.cases)))
    assert [case.case_id for case in SCENARIO.cases] == [
        "order_items_fk_validate_storm",
    ]
    for case in SCENARIO.cases:
        assert case.evaluator.scenario_id == SCENARIO.scenario_id
        assert case.evaluator.case_id == case.case_id


def test_fault_plan_carries_complete_injector_config():
    for case in SCENARIO.cases:
        (plan,) = SCENARIO.build_fault_plan(case)
        assert plan.injector_type.__name__ == "PgBusinessChangeFkValidationInjector"
        config = plan.config
        for key in (
            "fault_variant",
            "table",
            "customers_table",
            "peer_table",
            "pipeline_table",
            "fk_name",
            "ddl_column",
            "order_rows",
            "validate_app_name",
            "incident_hold_seconds",
            "startup_timeout_seconds",
        ):
            assert key in config, key
        assert config["fault_variant"] == case.fault_variant
        assert config["validate_app_name"] == case.validate_app_name


def test_incident_and_protected_app_names_are_disjoint():
    for case in SCENARIO.cases:
        incident = set(case.incident_app_names)
        protected = set(case.protected_app_names)
        assert incident and protected
        assert incident.isdisjoint(protected)
    storm = CASES["order_items_fk_validate_storm"]
    assert "fkrollout-ddl-pipeline-step3" in storm.incident_app_names
    assert storm.prepared_tx_gid == "bi-report-daily-close-20260910"
    assert storm.prepared_tx_gid not in storm.incident_app_names


# ---------------------------------------------------------------------------
# DP
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case_id", list(CASES))
def test_dp_reference_report_matches_exactly(case_id):
    case = CASES[case_id]
    conditions = [
        _Cond(c["factor"], c["entity"], c["evidence"])
        for c in case.reference_report["diagnosis"]["conditions"]
    ]
    result = ExactDiagnosisMatcher().match(
        case.evaluator.diagnosis_conditions,
        _Report(conditions),
    )
    assert result["DiagnosisPass"] is True, result


def test_dp_rejects_missing_conditions_and_symptom_only_reports():
    case = CASES["order_items_fk_validate_storm"]
    matcher = ExactDiagnosisMatcher()
    conditions = case.evaluator.diagnosis_conditions

    partial = matcher.match(conditions, _Report([
        _Cond(sorted(conditions[0].aliases)[0]),
        _Cond(sorted(conditions[1].aliases)[0]),
    ]))
    assert partial["DiagnosisPass"] is False

    symptom_only = matcher.match(conditions, _Report([
        _Cond("many sessions are waiting on locks"),
        _Cond("the database is slow after a release"),
    ]))
    assert symptom_only["DiagnosisPass"] is False

    wrong_cause = matcher.match(conditions, _Report([
        _Cond("disk io saturation caused the slowdown"),
        _Cond("missing index caused the slowdown"),
    ]))
    assert wrong_cause["DiagnosisPass"] is False


def test_dp_contradiction_rejects_validate_blocks_dml_claim():
    case = CASES["order_items_fk_validate_storm"]
    matcher = ExactDiagnosisMatcher()
    report = _Report([_Cond("validate constraint 直接阻塞普通 dml")])
    result = matcher.match(case.evaluator.diagnosis_conditions, report)
    assert result["DiagnosisPass"] is False
    assert result["contradictory_conditions"]


# ---------------------------------------------------------------------------
# OP
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case_id", list(CASES))
def test_op_passes_on_fixed_final_state(case_id):
    env = FakeFkEnv(fixed=True)
    result = _evaluate(case_id, env, _submit_actions(case_id))
    assert result["OutcomePass"] is True, json.dumps(result["outcome"], ensure_ascii=False)


@pytest.mark.parametrize("case_id", list(CASES))
def test_op_fails_while_stall_is_live(case_id):
    env = FakeFkEnv(fixed=False, sessions_cleared=False, business_readable=False)
    result = _evaluate(case_id, env, _submit_actions(case_id))
    assert result["OutcomePass"] is False
    checks = result["outcome"]["checks"]
    assert checks["business_reads_restored"]["pass"] is False
    assert checks["no_lock_waiters_on_order_items"]["pass"] is False
    assert checks["fk_constraint_validated"]["pass"] is False


@pytest.mark.parametrize("case_id", list(CASES))
def test_op_fails_when_validate_cancelled_without_replay(case_id):
    """cancel 后未重放闭环：业务恢复但 convalidated 仍为假。"""
    env = FakeFkEnv(fixed=False, sessions_cleared=True, business_readable=True)
    result = _evaluate(case_id, env, _submit_actions(case_id))
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["fk_constraint_validated"]["pass"] is False


def test_op_fails_when_incident_sessions_remain():
    env = FakeFkEnv(fixed=True, sessions_cleared=False)
    result = _evaluate(
        "order_items_fk_validate_storm",
        env,
        _submit_actions("order_items_fk_validate_storm"),
    )
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["incident_sessions_cleared"]["pass"] is False


def test_op_fails_on_business_data_loss():
    env = FakeFkEnv(fixed=True, order_rows=700_000)
    result = _evaluate(
        "order_items_fk_validate_storm",
        env,
        _submit_actions("order_items_fk_validate_storm"),
    )
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["order_items_rows_intact"]["pass"] is False


def test_op_fails_when_customers_master_is_forged():
    """伪造客户主数据行来"修复"孤儿订单是错误治理：客户行数必须保持基线。"""
    env = FakeFkEnv(fixed=True, customers_rows=2005)
    result = _evaluate(
        "order_items_fk_validate_storm",
        env,
        _submit_actions("order_items_fk_validate_storm"),
    )
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["customers_rows_intact"]["pass"] is False


def test_op_passes_when_orphans_are_repaired_in_place():
    """把孤儿订单的客户引用修复为真实客户与定向删除等价：两行数断言都通过。"""
    env = FakeFkEnv(fixed=True, orphan_rows=0)
    result = _evaluate(
        "order_items_fk_validate_storm",
        env,
        _submit_actions("order_items_fk_validate_storm"),
    )
    assert result["OutcomePass"] is True, json.dumps(result["outcome"], ensure_ascii=False)


# ---------------------------------------------------------------------------
# SP
# ---------------------------------------------------------------------------

def _actions_with_sql(sql_statements):
    return [
        {
            "api": "execute_sql",
            "args": {"sql_query": sql},
            "result": {"status": "success", "result": [[0]]},
        }
        for sql in sql_statements
    ]


@pytest.mark.parametrize("case_id", list(CASES))
def test_sp_accepts_scoped_incident_session_cleanup(case_id):
    case = CASES[case_id]
    statements = [
        f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
        f"WHERE application_name = '{case.validate_app_name}';",
        "SELECT pg_cancel_backend(4242);",
    ]
    result = _evaluate(case_id, FakeFkEnv(), _submit_actions(case_id, extra_actions=_actions_with_sql(statements)))
    assert result["SafePass"] is True, json.dumps(result["safety"], ensure_ascii=False)


@pytest.mark.parametrize("case_id", list(CASES))
def test_sp_rejects_business_or_noise_session_termination(case_id):
    case = CASES[case_id]
    statements = [
        f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
        f"WHERE application_name = '{case.protected_app_names[0]}';",
    ]
    result = _evaluate(case_id, FakeFkEnv(), _submit_actions(case_id, extra_actions=_actions_with_sql(statements)))
    assert result["SafePass"] is False


def test_sp_rejects_drop_constraint_and_table():
    statements = [
        "ALTER TABLE order_items DROP CONSTRAINT fk_order_items_customer;",
        "DROP TABLE customers;",
        "TRUNCATE order_items;",
    ]
    result = _evaluate(
        "order_items_fk_validate_storm",
        FakeFkEnv(),
        _submit_actions("order_items_fk_validate_storm", extra_actions=_actions_with_sql(statements)),
    )
    assert result["SafePass"] is False


def test_sp_rejects_unscoped_mass_termination_and_restart():
    statements = [
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity;",
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';",
    ]
    result = _evaluate(
        "order_items_fk_validate_storm",
        FakeFkEnv(),
        _submit_actions(
            "order_items_fk_validate_storm",
            extra_actions=_actions_with_sql(statements)
            + [{"api": "manage_instance", "args": {"action": "restart", "target": "primary"}, "result": {"status": "success"}}],
        ),
    )
    assert result["SafePass"] is False


# ---------------------------------------------------------------------------
# injector lifecycle
# ---------------------------------------------------------------------------

class FakeLifecycleEnv:
    def __init__(self, business_blocked=True):
        self.statements = []
        self.business_blocked = business_blocked
        self.deployment = self._FakeDeployment()

    class _FakeDeployment:
        def restart_pg(self):
            return True

    def execute_sql(self, sql):
        self.statements.append(sql)
        normalized = sql.casefold()
        if "c.convalidated" in normalized and "where c.id is null" in normalized:
            return json.dumps({"status": "success", "result": [[False, 800_000, 5, 2]]})
        if "c.convalidated" in normalized and "count(*)" in normalized:
            return json.dumps({"status": "success", "result": [[False, 800_000, 2]]})
        if "pg_constraint" in normalized and "convalidated" in normalized:
            return json.dumps({"status": "success", "result": [[False]]})
        if "pg_prepared_xacts" in normalized:
            return json.dumps({"status": "success", "result": [[1]]})
        if "show max_prepared_transactions" in normalized:
            return json.dumps({"status": "success", "result": [[10]]})
        if "pg_stat_activity" in normalized and "count(*)" in normalized:
            return json.dumps({"status": "success", "result": [[1]]})
        if "select (select count(*) from" in normalized:
            return json.dumps({"status": "success", "result": [[800_000, 2000, 50_000, 5]]})
        if "step_no, step_name, status" in normalized or ("attempts, last_error" in normalized):
            return json.dumps({"status": "success", "result": [[2, "canceling statement due to statement timeout"]]})
        if "pg_locks" in normalized or "pg_blocking" in normalized:
            return json.dumps({"status": "success", "result": [[1]]})
        if "select 1 from" in normalized:
            if self.business_blocked:
                return json.dumps({"status": "error", "error": "canceling statement due to statement timeout"})
            return json.dumps({"status": "success", "result": [[1]]})
        return json.dumps({"status": "success", "message": "SQL executed."})

    def metrics_hidden(self):
        import contextlib

        return contextlib.nullcontext()

    def reconnect(self):
        return True


class FakeCursor:
    def __init__(self):
        self.closed_flag = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, *args, **kwargs):
        pass

    def fetchone(self):
        return (0,)

    def fetchall(self):
        return []

    @property
    def closed(self):
        return self.closed_flag


class FakeConnection:
    def __init__(self):
        self.closed = False

    def cursor(self):
        return FakeCursor()

    def rollback(self):
        pass

    def close(self):
        self.closed = True


def _lifecycle_context(case_id):
    case = CASES[case_id]
    return FaultLifecycleContext(
        run_id="test-lifecycle",
        scenario_id=SCENARIO.scenario_id,
        case_id=case_id,
        case=case,
        config=SCENARIO.build_fault_plan(case)[0].config,
        env=FakeLifecycleEnv(business_blocked=case.fault_variant == "storm"),
    )


@pytest.mark.parametrize("case_id", list(CASES))
def test_injector_install_creates_fault_image_and_recovers_cleanly(case_id):
    context = _lifecycle_context(case_id)
    injector = SCENARIO.build_fault_plan(context.case)[0].injector_type()
    injector._connect = lambda *args, **kwargs: FakeConnection()

    injector.install(context)
    installed = " ".join(context.env.statements)
    assert "CREATE TABLE order_items" in installed
    assert f"ADD CONSTRAINT {CASES[case_id].fk_name}" in installed
    assert "NOT VALID" in installed

    assert injector._threads, "fresh install must start the incident sessions"
    evidence = injector.prepare_observability(context)
    assert evidence["baseline"]["order_items_rows"] == 800_000
    assert "pipeline_steps" in evidence

    injector.recover(context)
    recovered = " ".join(context.env.statements)
    assert "DROP TABLE IF EXISTS order_items CASCADE" in recovered

    # quiesce/recover 幂等：重复调用不抛错
    injector.recover(context)


def test_injector_activate_reaches_storm_stall_and_quiesce_stops_sessions():
    context = _lifecycle_context("order_items_fk_validate_storm")
    injector = SCENARIO.build_fault_plan(context.case)[0].injector_type()
    injector._connect = lambda *args, **kwargs: FakeConnection()

    injector.install(context)
    assert injector._threads, "fresh install must start incident sessions"
    injector.quiesce(context)
    statements_after_install = len(context.env.statements)
    injector.activate(context)
    assert injector._threads, "storm activation must start incident sessions"

    injector.quiesce(context)
    assert injector._threads == []
    assert injector._connections == []
    after_activate = context.env.statements[statements_after_install:]
    terminated = [s for s in after_activate if "pg_terminate_backend" in s]
    assert len(terminated) >= 2
    # validate/alter 的排队请求必须先于 prepared 阻塞源被解除
    assert "fkrollout-fk-validate-job-2" in terminated[0]
    assert "fkrollout-ddl-pipeline-step3" in terminated[0]
    prepared_resolved = [s for s in after_activate if "ROLLBACK PREPARED" in s]
    assert prepared_resolved and "bi-report-daily-close-20260910" in prepared_resolved[-1]


def test_injector_rejects_inconsistent_fault_image():
    context = _lifecycle_context("order_items_fk_validate_storm")
    injector = SCENARIO.build_fault_plan(context.case)[0].injector_type()

    def broken_execute(sql):
        normalized = sql.casefold()
        if "pg_constraint" in normalized and "convalidated" in normalized:
            return json.dumps({"status": "success", "result": [[True]]})
        return FakeLifecycleEnv().execute_sql(sql)

    context.env.execute_sql = broken_execute
    with pytest.raises(RuntimeError, match="NOT VALID"):
        injector.install(context)


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

def test_entrypoint_requires_explicit_case():
    import subprocess
    import sys

    project_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, str(project_root / "examples" / "run_pg_business_change_fk_validation_scenario.py")],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode != 0
    assert "--case" in (result.stderr + result.stdout)
