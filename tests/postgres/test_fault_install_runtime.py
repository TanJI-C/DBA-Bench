from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.postgres.health_check.long_running_tx import PgHealthCheckLongRunningTxScenario
from src.scenarios.postgres.business_change.fk_validation import PgBusinessChangeFkValidationScenario
from src.scenarios.postgres.system_failure.lock_contention import PgSystemFailureLockContentionScenario


@pytest.mark.parametrize("scenario_type", [
    PgHealthCheckLongRunningTxScenario,
    PgBusinessChangeFkValidationScenario,
    PgSystemFailureLockContentionScenario,
])
def test_fresh_install_starts_runtime_and_snapshot_restore_rebuilds_it(monkeypatch, scenario_type):
    scenario = scenario_type()
    case = scenario.cases[0]
    plan = scenario.build_fault_plan(case)[0]
    injector = plan.injector_type()
    env = SimpleNamespace(
        metrics_hidden=lambda: nullcontext(),
        execute_sql=lambda sql: {"status": "success", "result": [[False]]},
    )
    context = FaultLifecycleContext(
        run_id="install-runtime-test", scenario_id=scenario.scenario_id,
        case_id=case.case_id, case=case, config=plan.config, env=env,
    )
    active = []

    def start_runtime():
        assert not active, "runtime must not be started twice"
        active.append("blocker")

    monkeypatch.setattr("time.sleep", lambda seconds: None)
    if isinstance(scenario, PgHealthCheckLongRunningTxScenario):
        monkeypatch.setattr(injector, "_create_dead_tuples", lambda env: None)
        monkeypatch.setattr(injector, "_scrub_pg_stat_statements", lambda: None)
        monkeypatch.setattr(injector, "_start_runtime", start_runtime)
        monkeypatch.setattr(injector, "_start_runtime_noise", lambda: None)
        monkeypatch.setattr(injector, "_assert_noise_observable", lambda: None)
    elif isinstance(scenario, PgBusinessChangeFkValidationScenario):
        for method in ("_enable_prepared_transactions", "_drop_case_objects", "_setup_schema", "_verify_persistent_state"):
            monkeypatch.setattr(injector, method, lambda: None)
        monkeypatch.setattr(injector, "_terminate_sessions", lambda apps: None)
        monkeypatch.setattr(injector, "_capture_baseline", lambda: {"rows": 1})
        monkeypatch.setattr(injector, "_start_incident", start_runtime)
    else:
        monkeypatch.setattr(injector, "_install_persistent_state", lambda: None)
        monkeypatch.setattr(injector, "_verify_persistent_state", lambda: None)
        monkeypatch.setattr(injector, "_start_runtime", start_runtime)
    monkeypatch.setattr(injector, "quiesce", lambda context: active.clear())

    # fault_snapshot=off only calls install, so it must already be observable.
    injector.install(context)
    assert active == ["blocker"]
    # save stops sessions before capturing the image; use rebuilds them once.
    injector.quiesce(context)
    assert active == []
    injector.activate(context)
    assert active == ["blocker"]
    injector.quiesce(context)
    assert active == []


def test_long_transaction_quiesce_releases_runtime_for_snapshot(monkeypatch):
    scenario = PgHealthCheckLongRunningTxScenario()
    case = scenario.cases[0]
    plan = scenario.build_fault_plan(case)[0]
    injector = plan.injector_type()
    context = FaultLifecycleContext(
        run_id="snapshot-cleanup-test", scenario_id=scenario.scenario_id,
        case_id=case.case_id, case=case, config=plan.config, env=object(),
    )
    stopped = []
    monkeypatch.setattr(injector, "_stop_runtime", lambda context: stopped.append(context))
    injector.quiesce(context)
    assert stopped == [context]
