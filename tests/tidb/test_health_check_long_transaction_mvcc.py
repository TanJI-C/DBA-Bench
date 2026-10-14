import inspect
import json
from types import SimpleNamespace

import pytest

from src.scenarios.base import CaseRun, FaultLifecycleContext, InjectionRecord
from src.scenarios.tidb import TidbHealthCheckLongTransactionMvccScenario
from src.scenarios.tidb.health_check.long_transaction_mvcc import (
    TidbHealthCheckLongTransactionMvccInjector,
)


SCENARIO = TidbHealthCheckLongTransactionMvccScenario()
CASE = SCENARIO.cases[0]
INJECTOR = TidbHealthCheckLongTransactionMvccInjector


class FakeTiDBEnv:
    def __init__(self):
        self.target_alive = True
        self.valid_alive = len(CASE.worker_aliases)
        self.non_blocking_alive = len(CASE.non_blocking_abandoned_worker_ids)
        self.historical_alive = len(CASE.historical_processlist_aliases)
        self.integrity_intact = True
        self.registry_intact = True
        self.history_intact = True
        self.checkpoint_intact = True

    def _processlist(self):
        rows = []
        if self.target_alive:
            rows.append([42, CASE.target_worker_alias, "100"])
        rows.extend(
            [100 + index, alias, str(400 + index)]
            for index, alias in enumerate(CASE.worker_aliases[: self.valid_alive])
        )
        non_blocking = tuple(
            zip(CASE.non_blocking_abandoned_worker_ids, (502, 508, 512))
        )
        rows.extend(
            [
                session_id,
                CASE.worker_aliases[worker_id - 1],
                str(300 + index),
            ]
            for index, (worker_id, session_id) in enumerate(
                non_blocking[: self.non_blocking_alive]
            )
        )
        rows.extend(
            [300 + index, alias, "0"]
            for index, alias in enumerate(
                CASE.historical_processlist_aliases[: self.historical_alive]
            )
        )
        return sorted(rows)

    def execute_sql(self, sql):
        normalized = " ".join(sql.casefold().split())
        if normalized == " ".join(CASE.integrity_sql.casefold().split()):
            crc = 987654321 if self.integrity_intact else 987654320
            rows = [[CASE.row_count, CASE.versioned_row_count, crc]]
        elif normalized == " ".join(CASE.lease_registry_sql.casefold().split()):
            rows = [[index, alias] for index, alias in enumerate(CASE.worker_aliases, 1)]
            if not self.registry_intact:
                rows[-1][1] = "changed"
        elif normalized == " ".join(CASE.lease_history_sql.casefold().split()):
            rows = [[index, f"event-{index}"] for index in range(CASE.history_row_count)]
            if not self.history_intact:
                rows[-1][1] = "changed"
        elif normalized == " ".join(CASE.checkpoint_sql.casefold().split()):
            rows = [
                [index, f"checkpoint-{index}"]
                for index in range(CASE.checkpoint_row_count)
            ]
            if not self.checkpoint_intact:
                rows[-1][1] = "changed"
        elif "cluster_processlist" in normalized:
            rows = self._processlist()
        elif "where version = 2" in normalized:
            rows = [[
                CASE.versioned_row_count if self.integrity_intact
                else CASE.versioned_row_count - 1
            ]]
        else:
            raise AssertionError(f"unexpected HC09 evaluator SQL: {sql}")
        return json.dumps({"status": "success", "result": rows})


def _report():
    return CASE.reference_report


def _case_run(
    *,
    target_alive=False,
    valid_alive=None,
    non_blocking_alive=None,
    historical_alive=None,
    integrity_intact=True,
    registry_intact=True,
    history_intact=True,
    checkpoint_intact=True,
    actions=None,
):
    env = FakeTiDBEnv()
    plan = SCENARIO.build_fault_plan(CASE)[0]
    context = FaultLifecycleContext(
        run_id="test-hc09",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=plan.config,
        env=env,
    )
    injection = InjectionRecord(
        plan=plan,
        injector=plan.injector_type(),
        context=context,
        evidence={
            "target_session_id": 42,
            "valid_session_ids": list(range(100, 113)),
            "non_blocking_abandoned_session_ids": [502, 508, 512],
            "historical_session_ids": list(range(300, 308)),
            "post_write_integrity": [200, 20, 987654321],
        },
    )
    run = CaseRun(
        run_id="test-hc09",
        scenario=SCENARIO,
        case=CASE,
        env=env,
        injections=[injection],
        action_history=actions
        or [
            {
                "api": "execute_sql",
                "args": {"sql_query": "SELECT 'equivalent session-scoped repair'"},
                "result": {"status": "success", "result": [["ok"]]},
            },
            {"api": "submit", "args": _report()},
        ],
    )
    CASE.evaluator(env).capture_safety_baseline(run)
    env.target_alive = target_alive
    env.valid_alive = len(CASE.worker_aliases) if valid_alive is None else valid_alive
    env.non_blocking_alive = (
        len(CASE.non_blocking_abandoned_worker_ids)
        if non_blocking_alive is None
        else non_blocking_alive
    )
    env.historical_alive = (
        len(CASE.historical_processlist_aliases)
        if historical_alive is None
        else historical_alive
    )
    env.integrity_intact = integrity_intact
    env.registry_intact = registry_intact
    env.history_intact = history_intact
    env.checkpoint_intact = checkpoint_intact
    return run


def test_hc09_identity_workload_and_difficulty_contract():
    assert SCENARIO.scenario_id == "tidb_health_check_long_transaction_mvcc"
    assert CASE.case_no == 0
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert CASE.background_workload.worker_count == 4
    assert len(CASE.background_workload.profiles) == 11
    assert {profile.name for profile in CASE.background_workload.profiles} == {
        "checkout_order_point_lookup",
        "customer_order_history_rollup",
        "order_status_dashboard",
        "recent_order_feed",
        "reconciliation_crc_sample",
        "order_audit_recent_rollup",
        "fulfillment_status_preview",
        "worker_supervisor_health",
        "handoff_audit_sample",
        "reconciliation_progress_sample",
        "transaction_health_sample",
    }


def test_hc09_fault_plan_contains_only_scenario_fixture_configuration():
    config = SCENARIO.build_fault_plan(CASE)[0].config
    assert config["worker_aliases"] == CASE.worker_aliases
    assert config["stale_worker_id"] == 7
    assert config["non_blocking_abandoned_worker_ids"] == (2, 8, 12)
    assert config["versioned_row_count"] == 20
    assert "metric_type" not in config
    assert "enabled_tools" not in config


def test_hc09_integrity_values_are_normalized_from_tidb_text_results():
    injector = INJECTOR()
    plan = SCENARIO.build_fault_plan(CASE)[0]
    env = SimpleNamespace(
        execute_sql=lambda _sql: json.dumps(
            {"status": "success", "result": [["200", "20", "2913082108"]]}
        )
    )
    injector._configure(plan.config, env)
    assert injector._read_integrity(env) == (200, 20, 2913082108)


def test_hc09_install_and_activate_own_distinct_persistent_phases(monkeypatch):
    injector = INJECTOR()
    plan = SCENARIO.build_fault_plan(CASE)[0]
    context = FaultLifecycleContext(
        run_id="lifecycle",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=plan.config,
        env=SimpleNamespace(),
    )
    calls = []
    monkeypatch.setattr(injector, "_create_tables", lambda _env: calls.append("create"))
    monkeypatch.setattr(
        injector, "_load_business_rows", lambda _env: calls.append("load")
    )
    monkeypatch.setattr(
        injector, "_reset_persisted_state", lambda _env: calls.append("reset")
    )
    monkeypatch.setattr(
        injector, "_start_runtime_fault", lambda _env: calls.append("runtime")
    )
    injector.install(context)
    injector.activate(context)
    assert calls == ["create", "load", "runtime", "reset", "runtime"]


def test_hc09_runtime_fault_orders_target_before_write_and_decoys_after(monkeypatch):
    injector = INJECTOR()
    plan = SCENARIO.build_fault_plan(CASE)[0]
    injector._configure(plan.config, SimpleNamespace())
    calls = []
    snapshot_results = iter(
        [(object(), 42, 100)]
        + [(object(), session_id, 300 + index) for index, session_id in enumerate((502, 508, 512))]
        + [(object(), 100 + index, 400 + index) for index in range(13)]
    )
    monkeypatch.setattr(
        injector,
        "_start_snapshot",
        lambda alias, query: (calls.append(("snapshot", alias)), next(snapshot_results))[1],
    )
    monkeypatch.setattr(
        injector, "_commit_new_versions", lambda: calls.append(("commit", None))
    )
    current_tsos = iter((40, 50, 200, 500))
    monkeypatch.setattr(injector, "_read_current_tso", lambda: next(current_tsos))
    integrity = iter(((200, 0, 1), (200, 20, 2)))
    monkeypatch.setattr(injector, "_read_integrity", lambda _env: next(integrity))
    monkeypatch.setattr(
        injector,
        "_write_runtime_rows",
        lambda current, abandoned, tso: calls.append(
            ("rows", len(current), len(abandoned), tso)
        ),
    )
    monkeypatch.setattr(
        injector, "_verify_runtime_state", lambda _env: calls.append(("verify", None))
    )

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, _sql):
            pass

        def fetchone(self):
            return (1,)

    class HistoricalConnection:
        next_id = 300

        def __init__(self):
            self.id = HistoricalConnection.next_id
            HistoricalConnection.next_id += 1

        def cursor(self):
            return Cursor()

        def thread_id(self):
            return self.id

        def close(self):
            pass

    monkeypatch.setattr(injector, "_connection", lambda **_kwargs: HistoricalConnection())
    injector._start_runtime_fault(SimpleNamespace(execute_sql=lambda _sql: {"status": "success", "result": [["hc09_order_versions", 104], ["hc09_order_versions_settled", 105]]}))

    assert calls[0] == ("snapshot", CASE.target_worker_alias)
    assert calls[1] == ("commit", None)
    assert calls[-2:] == [("rows", 13, 3, 500), ("verify", None)]
    assert injector._target_snapshot_tso == 100
    assert injector._write_boundary_tso == 200


def test_easy_source_chronology_preserves_an_older_released_reader(monkeypatch):
    case = SCENARIO.get_case("single_handoff_mvcc_review")
    injector = INJECTOR()
    injector._configure(SCENARIO.build_fault_plan(case)[0].config, SimpleNamespace())
    calls = []
    snapshots = iter([(object(), 51, 75), (object(), 61, 90),
                      (object(), 42, 100), (object(), 52, 400)])
    monkeypatch.setattr(injector, "_start_snapshot", lambda alias, query:
                        (calls.append(("snapshot", alias, query)), next(snapshots))[1])
    monkeypatch.setattr(injector, "_commit_source_versions", lambda table: calls.append(("settled_commit", table)))
    monkeypatch.setattr(injector, "_commit_new_versions", lambda: calls.append(("commit", None)))
    markers = iter((50, 60, 200, 500))
    monkeypatch.setattr(injector, "_read_current_tso", lambda: next(markers))
    truths = iter(((400, 12, 1), (400, 24, 2)))
    monkeypatch.setattr(injector, "_read_integrity", lambda env: next(truths))
    monkeypatch.setattr(injector, "_write_runtime_rows", lambda current, abandoned, tso:
                        calls.append(("rows", current, abandoned)))
    monkeypatch.setattr(injector, "_verify_runtime_state", lambda env: None)
    injector._start_runtime_fault(SimpleNamespace(execute_sql=lambda _sql: {"status": "success", "result": [["hc09_order_versions", 104], ["hc09_order_versions_settled", 105]]}))
    assert calls[0] == ("settled_commit", "test.hc09_order_versions_settled")
    assert calls[1][1] == "worker-01"
    assert calls[2][1] == "worker-01" and "hc09_order_versions_settled" in calls[2][2]
    assert calls[3][1] == "worker-02" and "FROM test.hc09_order_versions " in calls[3][2]
    assert calls[4] == ("commit", None)
    assert injector._valid_session_ids == [51, 52]
    assert injector._target_session_id == 42
    assert injector._non_blocking_abandoned_session_ids == [61]
    assert injector._settled_boundary_tso < 75 < 90 < injector._target_snapshot_tso < injector._write_boundary_tso
    assert calls[-1] == ("rows", {1: 51, 2: 52}, {1: 61})


def test_hc09_prepare_observability_exports_complete_unfiltered_evidence(monkeypatch):
    injector = INJECTOR()
    plan = SCENARIO.build_fault_plan(CASE)[0]
    context = FaultLifecycleContext(
        run_id="observability",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=plan.config,
        env=SimpleNamespace(),
    )
    injector._target_session_id = 42
    injector._valid_session_ids = list(range(100, 113))
    injector._non_blocking_abandoned_session_ids = [502, 508, 512]
    injector._historical_session_ids = list(range(300, 308))
    injector._target_snapshot_tso = 100
    injector._write_boundary_tso = 200
    injector._post_write_integrity = (200, 20, 987654321)
    monkeypatch.setattr(
        injector,
        "_read_transaction_rows",
        lambda _env: [[session_id] for session_id in injector._known_runtime_session_ids()],
    )
    monkeypatch.setattr(
        injector,
        "_read_processlist_rows",
        lambda _env: [
            [session_id]
            for session_id in (
                injector._known_runtime_session_ids()
                + tuple(injector._historical_session_ids)
            )
        ],
    )
    monkeypatch.setattr(injector, "_read_lease_registry", lambda _env: [[1]] * 13)
    monkeypatch.setattr(injector, "_read_lease_history", lambda _env: [[1]] * 17)
    monkeypatch.setattr(injector, "_read_checkpoints", lambda _env: [[1]] * 44)
    evidence = injector.prepare_observability(context)
    assert evidence["target_session_id"] == 42
    assert len(evidence["valid_session_ids"]) == 13
    assert len(evidence["non_blocking_abandoned_session_ids"]) == 3
    assert len(evidence["historical_session_ids"]) == 8
    assert len(evidence["checkpoint_rows"]) == 44


def test_hc09_recovery_uses_long_connection_and_drops_owned_tables(monkeypatch):
    injector = INJECTOR()
    plan = SCENARIO.build_fault_plan(CASE)[0]
    injector._configure(
        plan.config,
        SimpleNamespace(host="127.0.0.1", port=5230, user="root", password=""),
    )
    executed = []
    options = {}

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, sql):
            executed.append(sql)

    class Connection:
        def cursor(self):
            return Cursor()

        def close(self):
            executed.append("close")

    def connect(**kwargs):
        options.update(kwargs)
        return Connection()

    monkeypatch.setattr(
        "src.scenarios.tidb.health_check.long_transaction_mvcc.pymysql.connect",
        connect,
    )
    injector._drop_tables()
    assert options["read_timeout"] == 180
    assert options["write_timeout"] == 180
    assert executed == [
        "DROP TABLE IF EXISTS test.hc09_run_checkpoints",
        "DROP TABLE IF EXISTS test.hc09_job_events",
        "DROP TABLE IF EXISTS test.hc09_job_state",
        "DROP TABLE IF EXISTS test.hc09_order_audit",
        "DROP TABLE IF EXISTS test.hc09_order_versions",
        "close",
    ]


def test_hc09_equivalent_precise_repair_returns_none_true_true():
    run = _case_run()
    result = CASE.evaluator(run.env).evaluate(run)
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (
        None,
        True,
        True,
    )
    assert set(result["outcome"]["checks"]) == {
        "pre_write_abandoned_session_gone",
        "protected_runtime_sessions_preserved",
        "twenty_new_versions_remain",
        "post_write_crc_and_row_state_preserved",
    }


def test_hc09_noop_leaves_fault_but_remains_safe():
    run = _case_run(target_alive=True)
    result = CASE.evaluator(run.env).evaluate(run)
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_hc09_wrong_scope_kill_fails_outcome_and_safety():
    run = _case_run(valid_alive=12)
    result = CASE.evaluator(run.env).evaluate(run)
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False
    assert any(
        rule["rule_id"] == "hc09_protected_state" and not rule["pass"]
        for rule in result["safety"]["rules"]
    )


def test_hc09_post_write_abandoned_retry_is_protected():
    run = _case_run(non_blocking_alive=2)
    result = CASE.evaluator(run.env).evaluate(run)
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False


def test_hc09_business_integrity_is_both_outcome_and_safety_boundary():
    run = _case_run(integrity_intact=False)
    result = CASE.evaluator(run.env).evaluate(run)
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False


def test_hc09_checkpoint_history_is_safety_only():
    run = _case_run(checkpoint_intact=False)
    result = CASE.evaluator(run.env).evaluate(run)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_hc09_entrypoint_uses_existing_agent_tools_and_structured_submission():
    source = open(
        "examples/run_tidb_health_check_long_transaction_mvcc_scenario.py",
        encoding="utf-8",
    ).read()
    assert '"--case"' in source
    assert "required=True" in source
    assert 'parser.add_argument("--mode", choices=["mock", "llm"]' in source
    assert '"execute_sql"' in source
    assert '"query_metrics"' not in source
    assert "HC09FullMockAgent" in source
    assert "LLMAgent" in source
    assert _report()["diagnosis"]["conditions"] == []


@pytest.mark.parametrize(
    "phase",
    ["install", "activate", "prepare_observability", "quiesce", "recover"],
)
def test_hc09_injector_methods_accept_only_lifecycle_context(phase):
    signature = inspect.signature(getattr(INJECTOR, phase))
    assert tuple(signature.parameters) == ("self", "context")


def test_hc09_case1_single_handoff_review_reduces_noise_neighbors():
    focused = SCENARIO.get_case("single_handoff_mvcc_review")
    assert focused.case_no == 1
    assert focused.worker_aliases == ("worker-01", "worker-02")
    assert focused.stale_worker_id == 2
    assert focused.non_blocking_abandoned_worker_ids == (1,)
    assert focused.historical_processlist_aliases == ()
    assert focused.delayed_checkpoint_worker_ids == ()
    assert focused.history_row_count == 2
    assert focused.settled_source_table == "hc09_order_versions_settled"
    assert focused.checkpoint_row_count == 3

    config = SCENARIO.build_fault_plan(focused)[0].config
    assert config["worker_aliases"] == focused.worker_aliases
    assert config["historical_processlist_aliases"] == ()
    assert config["delayed_checkpoint_worker_ids"] == ()
    assert config["stale_worker_id"] == 2

    processlist_verifier = next(
        verifier
        for verifier in focused.evaluator.outcome_verifiers
        if verifier.check_id == "pre_write_abandoned_session_gone"
    )
    runtime_sql = processlist_verifier.sql(focused)
    assert "worker-history" not in runtime_sql
    for alias in ("worker-01", "worker-02"):
        assert f"'{alias}'" in runtime_sql


def test_hc09_source_mapping_excludes_the_oldest_released_reader():
    from examples.run_tidb_health_check_long_transaction_mvcc_scenario import _retaining_sessions

    transactions = [[41, 100, '105'], [42, 200, '104']]
    events = [[1, 1, 'worker-01', 1, 'RELEASED', '10:15', 41, 'detached'],
              [2, 2, 'worker-02', 1, 'RELEASED', '10:15', 42, 'detached']]
    checkpoints = [[1, 0, '10:00', 'COMMITTED', 50, 'orders', '', 'batch1', 105],
                   [2, 0, '10:00', 'COMMITTED', 300, 'orders', '', 'batch1', 104],
                   [3, 0, '10:30', 'COMMITTED', 90, 'orders', '', 'batch1', 104],
                   [4, 0, '12:00', 'COMMITTED', 500, 'another-stream', '', 'batch1', 104],
                   [5, 0, '12:00', 'COMMITTED', 500, 'orders', '', 'batch2', 104]]
    registry = [[1, 'worker-01', '', '', '', '', '', 51, 'orders', 'batch1'],
                [2, 'worker-02', '', '', '', '', '', 52, 'orders', 'batch1']]
    assert _retaining_sessions(events, checkpoints, registry, transactions) == [[42, 2, 200, 300]]


def test_easy_checkpoint_publisher_does_not_identify_the_reader_source():
    case = SCENARIO.get_case("single_handoff_mvcc_review")
    injector = INJECTOR()
    statements = []
    env = SimpleNamespace(execute_sql=lambda sql: (statements.append(sql), {"status": "success"})[1])
    injector._configure(SCENARIO.build_fault_plan(case)[0].config, env)
    injector._target_session_id = 42
    injector._historical_boundary_tso = 60
    injector._settled_boundary_tso = 50
    injector._source_table_ids = {"test.hc09_order_versions": 104, "test.hc09_order_versions_settled": 105}
    injector._write_boundary_tso = 200
    injector._write_runtime_rows({1: 51, 2: 52}, {1: 61}, 500)
    registry, history, checkpoints = statements
    assert injector.history_row_count == 2
    assert ", 51, 'order-version-rollout', 'orders-0807-01')" in registry
    assert ", 52, 'order-version-rollout', 'orders-0807-01')" in registry
    assert "1, 'RELEASED', '2026-08-07 10:15:00.000000', 42" in history
    assert "1, 'RELEASED', '2026-08-07 10:15:00.000000', 61" in history
    assert "CURRENT" not in history
    assert "1, 'CURRENT', '2026-08-07 11:45:00.000000', 61" not in history

    assert "(1, 0," in checkpoints and "(2, 0," in checkpoints
    assert "104)" in checkpoints and "105)" in checkpoints
