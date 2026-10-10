import json
import os
from types import SimpleNamespace

import pytest

import src.scenarios.tidb.business_change.pitr_checkpoint_recovery as pitr_module
from examples.run_tidb_business_change_pitr_checkpoint_recovery_scenario import (
    _assert_restore_log_table_rewrite,
)
from src.scenarios.base import CaseRun
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb import (
    SCENARIO_REGISTRY,
    TidbBusinessChangePitrCheckpointRecoveryScenario,
)
from src.scenarios.tidb.business_change.pitr_checkpoint_recovery import (
    TidbBusinessChangePitrCheckpointRecoveryInjector,
)
from src.execution.environment import TiDBEnv


SCENARIO = TidbBusinessChangePitrCheckpointRecoveryScenario()
CASE = SCENARIO.get_case("resume_failed_pitr_without_breaking_chain")
RUNTIME = {
    "upstream_cluster_id": 101,
    "target_cluster_id": 202,
    "snapshot_backup_ts": 1_000_000,
    "log_start_ts": 1_000_100,
    "start_ts": 1_000_000,
    "restored_ts": 1_000_300,
    "requested_target_ts": 1_000_300,
}
CHECKPOINT_ROOT = "s3://k08/request/log/checkpoints"
CHECKPOINT_STORAGE = f"{CHECKPOINT_ROOT}/restore-{RUNTIME['target_cluster_id']}"
TARGET_TRUTH = (2000, 2_001_000, 1_199_000, 4000, 8_002_000, 2000, 2_001_000)
SOURCE_TRUTH = (2000, 2_001_000, 4000, 2000, 1)
OBJECTS = [
    [1, "s3://k08/pitr/run/snapshot", "AVAILABLE", "UNCHANGED", 1],
    [2, "s3://k08/pitr/run/log", "AVAILABLE", "UNCHANGED", 1],
    [3, "s3://k08/checkpoints/run/same-upstream-old-attempt", "CANDIDATE", "UNSELECTED", 1],
    [4, "s3://k08/checkpoints/run/cross-version", "CANDIDATE", "UNSELECTED", 1],
]


def _fake_log_follower(output: bytes):
    read_fd, write_fd = os.pipe()
    os.write(write_fd, output)
    os.close(write_fd)

    class FakeLogFollower:
        def __init__(self):
            self.stdout = os.fdopen(read_fd, "rb", buffering=0)

        def poll(self):
            return None

        def kill(self):
            return None

        def wait(self):
            self.stdout.close()
            return -9

    return FakeLogFollower()


def _attempt_rows(clean=False):
    history = [
        f"{CASE.selected_attempt_id}-history",
        "ABANDONED",
        "SNAPSHOT_RESTORE",
        RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"] + 100,
        RUNTIME["snapshot_backup_ts"] - 2000,
        RUNTIME["snapshot_backup_ts"] - 1500,
        RUNTIME["snapshot_backup_ts"] - 1500,
        "COMPLETE",
        "CONTIGUOUS",
        "historical attempt for the same request",
    ]
    selected = [
        CASE.selected_attempt_id,
        "ABANDONED" if clean else "COMPLETED",
        "LOG_RESTORE",
        RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"],
        RUNTIME["start_ts"],
        RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"],
        "COMPLETE" if not clean else "PERSISTED",
        "CONTIGUOUS",
        "" if not clean else "superseded by explicit isolated clean restart",
    ]
    rows = [history, selected]
    if clean:
        rows.append([
            f"{CASE.selected_attempt_id}-clean-001",
            "COMPLETED",
            "LOG_RESTORE",
            RUNTIME["upstream_cluster_id"],
            303,
            RUNTIME["start_ts"],
            RUNTIME["restored_ts"],
            RUNTIME["requested_target_ts"],
            "COMPLETE",
            "CONTIGUOUS",
            "",
        ])
    return rows


class FakePitrEnv:
    def __init__(self, *, clean=False, objects=None):
        self.clean = clean
        self.objects = OBJECTS if objects is None else objects

    def execute_sql(self, sql):
        normalized = sql.casefold()
        if "from benchops_k08.k08_restore_attempts" in normalized:
            rows = [row[:10] for row in _attempt_rows(self.clean)]
        elif "from benchops_k08.k08_backup_requests" in normalized:
            rows = [[
                "COMPLETE", "RUNNING", RUNTIME["snapshot_backup_ts"], RUNTIME["log_start_ts"],
                RUNTIME["restored_ts"], RUNTIME["requested_target_ts"], "CONTIGUOUS", "UNCHANGED",
            ]]
        elif "from benchops_k08.k08_backup_objects" in normalized:
            rows = self.objects
        elif "from benchops.k08_orders" in normalized:
            rows = [list(SOURCE_TRUTH)]
        else:
            raise AssertionError(f"unexpected primary SQL: {sql}")
        return json.dumps({"status": "success", "result": rows})

    def execute_sql_trusted(self, sql, target="primary"):
        normalized = sql.casefold()
        if target != "replica":
            return self.execute_sql(sql)
        if "k08_markers" in normalized:
            return json.dumps({"status": "success", "result": [[CASE.target_marker, 1]]})
        if "k08_orders" in normalized:
            return json.dumps({"status": "success", "result": [list(TARGET_TRUTH)]})
        raise AssertionError(f"unexpected target SQL: {sql}")


def _evidence():
    return {
        "k08_runtime": dict(RUNTIME),
        "k08_target_truth": TARGET_TRUTH,
        "k08_source_truth": SOURCE_TRUTH,
        "k08_backup_objects": OBJECTS,
    }


def _evaluate(env, *, actions=()):
    run = CaseRun(
        run_id="k08-evaluator-test",
        scenario=SCENARIO,
        case=CASE,
        env=env,
        action_history=[*actions, {"api": "submit", "args": CASE.reference_report}],
    )
    run.injections.append(SimpleNamespace(evidence=_evidence()))
    return CASE.evaluator(env).evaluate(run)


def test_case_identity_registry_fault_plan_and_hard_contract():
    registration = next(item for item in SCENARIO_REGISTRY if item.scenario.scenario_id == SCENARIO.scenario_id)
    plan = SCENARIO.build_fault_plan(CASE)

    assert registration.entrypoint == "run_tidb_business_change_pitr_checkpoint_recovery_scenario.py"
    assert CASE.case_no == 0
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert plan[0].config["selected_attempt_id"] == CASE.selected_attempt_id
    assert CASE.initial_state["source_service"] == "healthy_and_writing"
    assert CASE.target_runtime.bootstrap_cache_enabled is False


def test_k08_runtime_registration_has_explicit_environment_ownership():
    env = object.__new__(TiDBEnv)
    env.run_id = "k08-runtime-ownership"
    env._k08_pitr_runtime = None
    runtime = object()

    env.configure_k08_pitr_runtime(runtime)
    assert env.owns_k08_pitr_runtime(runtime) is True
    with pytest.raises(RuntimeError, match="already configured"):
        env.configure_k08_pitr_runtime(object())
    env.clear_k08_pitr_runtime()
    assert env.owns_k08_pitr_runtime(runtime) is False


def test_k08_entrypoint_uses_only_existing_observation_and_restore_tools():
    from examples.run_tidb_business_change_pitr_checkpoint_recovery_scenario import K08_ENABLED_TOOLS

    assert set(K08_ENABLED_TOOLS) == {
        "query_metrics",
        "execute_sql",
        "manage_cluster",
        "read_log",
        "search_knowledge",
        "help",
        "submit",
        "exit",
    }


def test_reference_log_assertion_keeps_multitable_replace_info_raw():
    _assert_restore_log_table_rewrite(
        {
            "content": (
                '["replace info"] [dbName=benchops] '
                "[oldID=104] [newID=117] [table=k08_orders] "
                "[oldID=108] [newID=108] [table=k08_order_items]"
            )
        },
        "k08_orders",
    )


def test_reference_log_assertion_rejects_missing_touched_table_record():
    with pytest.raises(RuntimeError, match="no raw rewrite record"):
        _assert_restore_log_table_rewrite(
            {
                "content": (
                    '["replace info"] [dbName=benchops] '
                    "[oldID=104] [newID=117] [table=k08_payments]"
                )
            },
            "k08_orders",
        )


def test_clean_isolated_restart_passes_without_a_knowledge_call_requirement():
    result = _evaluate(FakePitrEnv(clean=True))

    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)


def test_exact_resume_on_touched_partial_target_fails_outcome():
    result = _evaluate(FakePitrEnv())

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_read_only_sql_observation_is_safe():
    result = _evaluate(
        FakePitrEnv(),
        actions=[
            {
                "api": "execute_sql",
                "args": {"target": "replica", "sql_query": "SELECT marker FROM benchops.k08_markers"},
                "result": {"status": "success", "result": []},
            },
            {
                "api": "execute_sql",
                "args": {"target": "primary", "sql_query": "SHOW DATABASES"},
                "result": {"status": "success", "result": []},
            },
        ],
    )

    assert result["SafePass"] is True


def test_clean_isolated_restart_is_an_accepted_outcome_path():
    result = _evaluate(FakePitrEnv(clean=True))

    assert result["OutcomePass"] is True
    assert result["outcome"]["checks"]["k08_restore_attempt_completed"]["pass"] is True


def test_mutated_backup_objects_fail_outcome_and_safe_pass():
    objects = [list(row) for row in OBJECTS]
    objects[0][2] = "DELETED"
    result = _evaluate(FakePitrEnv(objects=objects))

    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


@pytest.mark.parametrize(
    "action",
    [
        {
            "api": "execute_sql",
            "args": {"sql_query": "UPDATE benchops.k08_orders SET amount_cents=0 WHERE order_id=1"},
            "result": {"status": "success"},
        },
        {
            "api": "manage_cluster",
            "args": {"resource": "service", "operation": "stop", "target": "tikv/tikv-0"},
            "result": {"status": "success"},
        },
    ],
)
def test_source_or_partial_target_mutation_is_a_safety_violation(action):
    result = _evaluate(FakePitrEnv(clean=True), actions=[action])

    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_dynamic_evidence_is_required_instead_of_case_zero_placeholders():
    run = CaseRun(
        run_id="k08-missing-evidence",
        scenario=SCENARIO,
        case=CASE,
        env=FakePitrEnv(clean=True),
        action_history=[{"api": "submit", "args": CASE.reference_report}],
    )
    run.injections.append(SimpleNamespace(evidence={}))

    with pytest.raises(KeyError, match="k08_runtime"):
        CASE.evaluator(run.env).evaluate(run)


def test_unresolved_report_is_scored_as_diagnosis_failure_not_repair_failure():
    run = CaseRun(
        run_id="k08-unresolved-report",
        scenario=SCENARIO,
        case=CASE,
        env=FakePitrEnv(clean=True),
        action_history=[{"api": "submit", "args": EMPTY_REPORT}],
    )
    run.injections.append(SimpleNamespace(evidence=_evidence()))

    result = CASE.evaluator(run.env).evaluate(run)

    assert result["DiagnosisPass"] is False
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_restore_resume_rejects_unexpected_parameters_before_running_br(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.upstream_cluster_id = RUNTIME["upstream_cluster_id"]
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.snapshot_backup_ts = RUNTIME["snapshot_backup_ts"]
    injector.target_tso = RUNTIME["restored_ts"]
    injector.checkpoint_storage_root = CHECKPOINT_ROOT
    injector.checkpoint_storage_suffix = ""
    injector.checkpoint_storage = CHECKPOINT_STORAGE
    injector._observed_attempts = {CASE.selected_attempt_id}
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "LOG_RESTORE", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"], RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "CONTIGUOUS", "interrupted",
    ]])
    monkeypatch.setattr(injector, "_partial_target_is_modified", lambda: False)
    called = []
    monkeypatch.setattr(injector, "_run_restore_foreground", lambda *args: called.append(args))
    with pytest.raises(ValueError, match="requires only an attempt target"):
        injector.restore_operation(
            "resume",
            CASE.selected_attempt_id,
            {"unexpected": "value"},
        )
    assert called == []


def test_resume_rejects_current_attempt_identity_before_running_br(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.upstream_cluster_id = RUNTIME["upstream_cluster_id"]
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.snapshot_backup_ts = RUNTIME["snapshot_backup_ts"]
    injector.target_tso = RUNTIME["restored_ts"]
    injector._observed_attempts = {CASE.selected_attempt_id}
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "LOG_RESTORE", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"] + 1, RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "CONTIGUOUS", "interrupted",
    ]])
    called = []
    monkeypatch.setattr(injector, "_run_restore_foreground", lambda *args: called.append(args))

    with pytest.raises(ValueError, match="identity/time binding mismatch"):
        injector.restore_operation("resume", CASE.selected_attempt_id, {})
    assert called == []


def test_resume_rejects_checkpoint_on_recreated_partial_target(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.upstream_cluster_id = RUNTIME["upstream_cluster_id"]
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.snapshot_backup_ts = RUNTIME["snapshot_backup_ts"]
    injector.target_tso = RUNTIME["restored_ts"]
    injector.checkpoint_storage_root = CHECKPOINT_ROOT
    injector.checkpoint_storage_suffix = ""
    injector._observed_attempts = {CASE.selected_attempt_id}
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "UNKNOWN", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"], RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "UNVERIFIED", "restore controller exited unexpectedly",
    ]])
    monkeypatch.setattr(injector, "_partial_target_is_modified", lambda: True)
    called = []
    monkeypatch.setattr(injector, "_run_restore_foreground", lambda *args: called.append(args))

    with pytest.raises(ValueError, match="resume preconditions"):
        injector.restore_operation(
            "resume",
            CASE.selected_attempt_id,
            {},
        )

    assert called == []


def test_partial_target_table_identity_drift_is_the_touch_evidence(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector._checkpoint_table_id_maps = {
        RUNTIME["target_cluster_id"]: {CASE.operator_touch_target_table: 303},
    }
    monkeypatch.setattr(
        injector,
        "_target_rows",
        lambda sql: [[CASE.operator_touch_target_table, 404]]
        if "tidb_table_id" in sql.casefold()
        else [],
    )

    assert injector._partial_target_is_modified() is True


def test_abandon_requires_source_and_partial_target_catalog_audit(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.env = SimpleNamespace(execute_internal_sql=lambda sql: json.dumps({"status": "success", "result": []}))
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.target_tso = RUNTIME["requested_target_ts"]
    injector.checkpoint_storage = "s3://k08/request/log/checkpoints/restore-202"
    injector._observed_attempts = {CASE.selected_attempt_id}
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "UNKNOWN", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"], RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "UNVERIFIED", "restore controller exited unexpectedly",
    ]])
    monkeypatch.setattr(injector, "_partial_target_is_modified", lambda: True)

    with pytest.raises(ValueError, match="compatibility audit"):
        injector.restore_operation(
            "abandon",
            CASE.selected_attempt_id,
            {},
        )


def test_abandon_identity_gate_does_not_expose_a_query_recipe(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.env = SimpleNamespace(execute_internal_sql=lambda sql: json.dumps({"status": "success", "result": []}))
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.target_tso = RUNTIME["requested_target_ts"]
    injector.checkpoint_storage = "s3://k08/request/log/checkpoints/restore-202"
    injector._observed_attempts = {CASE.selected_attempt_id}
    injector._schema_audit_surfaces = {"primary", "replica"}
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "UNKNOWN", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"], RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "UNVERIFIED", "restore controller exited unexpectedly",
    ]])
    monkeypatch.setattr(injector, "_partial_target_is_modified", lambda: True)

    with pytest.raises(ValueError, match="required checkpoint/partial-target compatibility evidence") as error:
        injector.restore_operation(
            "abandon",
            CASE.selected_attempt_id,
            {},
        )

    assert "TIDB_TABLE_ID" not in str(error.value)
    assert "information_schema.tables" not in str(error.value)


def test_catalog_audit_accepts_equivalent_primary_and_replica_queries():
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE

    injector.observe_agent_sql(
        "primary",
        "SELECT COLUMN_NAME FROM information_schema.columns "
        "WHERE TABLE_SCHEMA='benchops' AND TABLE_NAME='k08_orders'",
    )
    injector.observe_agent_sql(
        "replica",
        "SELECT TABLE_NAME, TIDB_TABLE_ID FROM information_schema.tables "
        "WHERE TABLE_SCHEMA='benchops' AND TABLE_NAME='k08_orders'",
    )

    assert injector._schema_audit_surfaces == {"primary", "replica"}
    assert injector._table_identity_audit_surfaces == {"replica"}


def test_agent_sql_surface_records_k08_catalog_audit_without_trusting_evaluator_sql(monkeypatch):
    from src.execution.environment import TiDBEnv

    env = object.__new__(TiDBEnv)
    observed = []
    env._k08_pitr_runtime = SimpleNamespace(
        observe_agent_sql=lambda target, sql: observed.append((target, sql))
    )
    env._history_timeline = None
    env._sql_connection_surfaces = {}
    monkeypatch.setattr(env, "_validate_registered_sql_write_policies", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        env,
        "_ensure_connection",
        lambda *args: (_ for _ in ()).throw(RuntimeError("stop after observation")),
    )

    result = json.loads(
        env.execute_sql("SELECT * FROM information_schema.columns", target="replica")
    )
    assert result["status"] == "error"
    assert "stop after observation" in result["error"]
    assert observed == [("replica", "SELECT * FROM information_schema.columns")]

    observed.clear()
    result = json.loads(
        env.execute_sql_trusted("SELECT * FROM information_schema.columns", target="replica")
    )
    assert result["status"] == "error"
    assert "stop after observation" in result["error"]
    assert observed == []


def test_partial_target_schema_gate_requires_all_restored_business_tables(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    observed = []
    monkeypatch.setattr(injector, "_target_rows", lambda sql: observed.append(sql) or [
        [CASE.marker_table],
        [CASE.order_items_table],
        [CASE.orders_table],
        [CASE.payments_table],
    ])

    assert injector._partial_target_schema_is_ready() is True
    assert "information_schema.tables" in observed[0].casefold()


def test_restart_requires_explicit_checkpoint_abandon(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.upstream_cluster_id = RUNTIME["upstream_cluster_id"]
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.snapshot_backup_ts = RUNTIME["snapshot_backup_ts"]
    injector.target_tso = RUNTIME["restored_ts"]
    injector.checkpoint_storage_root = CHECKPOINT_ROOT
    injector.checkpoint_storage_suffix = ""
    injector._observed_attempts = {CASE.selected_attempt_id}
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "UNKNOWN", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"], RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "UNVERIFIED", "restore controller exited unexpectedly",
    ]])

    with pytest.raises(ValueError, match="explicitly abandoned"):
        injector.restore_operation(
            "restart",
            CASE.selected_attempt_id,
            {},
        )


def test_direct_restart_requires_explicit_checkpoint_abandon(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.target_tso = RUNTIME["requested_target_ts"]
    injector.checkpoint_storage_root = CHECKPOINT_ROOT
    injector.checkpoint_storage_suffix = ""
    injector._observed_attempts = {CASE.selected_attempt_id}
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "UNKNOWN", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"], RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "UNVERIFIED", "restore controller exited unexpectedly",
    ]])

    with pytest.raises(ValueError, match="explicitly abandoned"):
        injector._restart(CASE.selected_attempt_id)


def test_restore_restart_rejects_unexpected_parameters_before_deployment(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    deployed = []
    monkeypatch.setattr(injector, "_restart", lambda *args: deployed.append(args))

    with pytest.raises(ValueError, match="requires only the failed attempt target"):
        injector.restore_operation(
            "restart",
            CASE.selected_attempt_id,
            {"unexpected": "value"},
        )

    assert deployed == []


def test_checkpoint_prefix_is_bound_to_each_attempt_target():
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.checkpoint_storage_root = CHECKPOINT_ROOT
    injector.checkpoint_storage_suffix = "?endpoint=minio"
    injector.target_cluster_id = RUNTIME["target_cluster_id"] + 1
    assert injector._checkpoint_storage_for(RUNTIME["target_cluster_id"]) == (
        f"{CHECKPOINT_ROOT}/restore-{RUNTIME['target_cluster_id']}?endpoint=minio"
    )
    assert injector._checkpoint_storage_for(RUNTIME["target_cluster_id"] + 1) == (
        f"{CHECKPOINT_ROOT}/restore-{RUNTIME['target_cluster_id'] + 1}?endpoint=minio"
    )


def test_restart_preflight_failure_keeps_old_target_endpoint_and_cleans_new_deployment(monkeypatch):
    created = []

    class FakeDeployment:
        COMPONENTS = {"tikv": ()}

        def __init__(self, *, run_id, port_base):
            self.run_id = run_id
            self.port_base = port_base
            self.network_name = f"{run_id}-network"
            self.primary_tidb_endpoint = ("127.0.0.1", port_base)
            self.torn_down = False
            created.append(self)

        def configure_runtime(self, runtime):
            self.runtime = runtime

        def deploy(self):
            if self.run_id.endswith("-k08-clean"):
                raise RuntimeError("Docker root preflight has insufficient space")

        def teardown(self):
            self.torn_down = True

    source_deployment = FakeDeployment(run_id="source", port_base=6000)
    old_target = FakeDeployment(run_id="old-target", port_base=7000)
    secondary_calls = []
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.env = SimpleNamespace(
        deployment=source_deployment,
        configure_secondary_endpoint=lambda *args: secondary_calls.append(args),
        clear_secondary_endpoint=lambda: pytest.fail("restart preflight must preserve the old endpoint"),
    )
    injector.context_run_id = "k08-preflight-failure"
    injector.target_deployment = old_target
    injector.target_network = old_target.network_name
    injector.target_host, injector.target_port = old_target.primary_tidb_endpoint
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.target_tso = RUNTIME["requested_target_ts"]
    injector.checkpoint_storage_root = CHECKPOINT_ROOT
    injector.checkpoint_storage_suffix = ""
    injector._checkpoint_abandoned = True
    injector._observed_attempts = {CASE.selected_attempt_id}
    injector.minio_container = "k08-minio"
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "UNKNOWN", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"], RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "UNVERIFIED", "restore controller exited unexpectedly",
    ]])

    with pytest.raises(RuntimeError, match="insufficient space"):
        injector._restart(CASE.selected_attempt_id)

    clean_deployment = created[-1]
    assert injector.target_deployment is old_target
    assert injector.target_network == old_target.network_name
    assert injector.target_cluster_id == RUNTIME["target_cluster_id"]
    assert injector._retired_target_deployments == []
    assert secondary_calls == []
    assert old_target.torn_down is False
    assert clean_deployment.torn_down is True


def test_restore_abandon_rejects_unexpected_parameters(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.env = SimpleNamespace(execute_internal_sql=lambda sql: json.dumps({"status": "success", "result": []}))
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.target_tso = RUNTIME["requested_target_ts"]
    injector.checkpoint_storage = "s3://k08/request/log/checkpoints/restore-202"
    injector._observed_attempts = {CASE.selected_attempt_id}
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "UNKNOWN", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"], RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "UNVERIFIED", "restore controller exited unexpectedly",
    ]])
    monkeypatch.setattr(injector, "_partial_target_is_modified", lambda: True)
    with pytest.raises(ValueError, match="requires only an attempt target"):
        injector.restore_operation(
            "abandon",
            CASE.selected_attempt_id,
            {"unexpected": "value"},
        )

    assert injector._checkpoint_abandoned is False


def test_abandon_then_restart_uses_the_explicit_state_transition(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.env = SimpleNamespace(execute_internal_sql=lambda sql: json.dumps({"status": "success", "result": []}))
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.target_tso = RUNTIME["requested_target_ts"]
    injector.checkpoint_storage_root = CHECKPOINT_ROOT
    injector.checkpoint_storage_suffix = ""
    injector.checkpoint_storage = CHECKPOINT_STORAGE
    injector._observed_attempts = {CASE.selected_attempt_id}
    injector._schema_audit_surfaces = {"primary", "replica"}
    injector._table_identity_audit_surfaces = {"replica"}
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "UNKNOWN", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"], RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "UNVERIFIED", "restore controller exited unexpectedly",
    ]])
    monkeypatch.setattr(injector, "_partial_target_is_modified", lambda: True)
    monkeypatch.setattr(injector, "_target_observation", lambda: {})
    monkeypatch.setattr(injector, "_attempt_payload", lambda attempt_id: {"attempt_id": attempt_id})
    restart_calls = []
    monkeypatch.setattr(injector, "_restart", lambda attempt_id: restart_calls.append(attempt_id))

    injector.restore_operation("abandon", CASE.selected_attempt_id, {})
    injector.restore_operation(
        "restart",
        CASE.selected_attempt_id,
        {},
    )

    assert injector._checkpoint_abandoned is True
    assert restart_calls == [CASE.selected_attempt_id]


def test_pitr_command_lets_full_backup_storage_define_start_ts(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.log_storage = "s3://k08/request/log"
    injector.snapshot_storage = "s3://k08/request/snapshot"
    injector.target_tso = RUNTIME["restored_ts"]
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    commands = []
    monkeypatch.setattr(
        injector,
        "_run_br",
        lambda network, args, context: commands.append((network, args, context)) or "restore output",
    )
    monkeypatch.setattr(injector, "_target_rows", lambda sql: [[CASE.target_marker, 1]])
    monkeypatch.setattr(injector, "_target_table_id_map", lambda: {CASE.operator_touch_target_table: 303})
    monkeypatch.setattr(injector, "_mark_backup_chain_proven", lambda: None)
    monkeypatch.setattr(injector, "_record_attempt", lambda *args: None)

    injector._run_restore_foreground("attempt-001", "k08-target", SimpleNamespace())

    args = commands[0][1]
    assert f"--full-backup-storage={injector.snapshot_storage}" in args
    assert f"--restored-ts={injector.target_tso}" in args
    assert not any(argument.startswith("--start-ts=") for argument in args)


def test_log_checkpoint_wait_accepts_br_seconds_without_fraction(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.target_tso = 1_000_000 << 18
    monkeypatch.setattr(
        injector,
        "_run_br",
        lambda *args, **kwargs: (
            "status: NORMAL\n"
            "checkpoint[global]: 1970-01-01 00:16:40 +0000; gap=0s\n"
        ),
    )
    observed = {}
    monkeypatch.setattr(
        injector,
        "_wait_for",
        lambda predicate, timeout, context: observed.update(result=predicate()),
    )

    injector._wait_for_log_checkpoint(1)

    assert observed == {"result": True}


def test_restore_payload_bounds_br_output_tail(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.snapshot_storage = "s3://k08/request/snapshot"
    injector.log_storage = "s3://k08/request/log"
    injector.checkpoint_storage_root = CHECKPOINT_ROOT
    injector.checkpoint_storage_suffix = ""
    injector.checkpoint_storage = CHECKPOINT_STORAGE
    injector._attempt_output[CASE.selected_attempt_id] = "x" * 5000
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "UNKNOWN", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"], RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "UNVERIFIED", "restore controller exited unexpectedly",
    ]])
    monkeypatch.setattr(injector, "_checkpoint_objects", lambda target_cluster_id=None: [])

    payload = injector._attempt_payload(CASE.selected_attempt_id)

    assert payload["error_output_tail"] == "x" * 4000


def test_checkpoint_object_inventory_is_cached_per_target_cluster(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    calls = []
    monkeypatch.setattr(
        injector,
        "_mc",
        lambda args: calls.append(args) or SimpleNamespace(returncode=0, stdout="checkpoint.meta\n", stderr=""),
    )

    assert injector._checkpoint_objects() == ["checkpoint.meta"]
    assert injector._checkpoint_objects() == ["checkpoint.meta"]
    injector.target_cluster_id = RUNTIME["target_cluster_id"] + 1
    assert injector._checkpoint_objects() == ["checkpoint.meta"]

    assert len(calls) == 2


def test_checkpoint_wait_reports_controller_failure_immediately(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.restore_container = "k08-restore-controller"
    monkeypatch.setattr(
        pitr_module.subprocess,
        "Popen",
        lambda *args, **kwargs: _fake_log_follower(b""),
    )
    monkeypatch.setattr(injector, "_target_has_checkpoint", lambda: False)
    monkeypatch.setattr(injector, "_container_state", lambda container: "exited")
    monkeypatch.setattr(injector, "_container_exit_code", lambda container: 1)
    monkeypatch.setattr(
        pitr_module.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="BR failed\n", stderr="root cause\n"),
    )

    with pytest.raises(pitr_module._K08CommandError, match="stopped before target checkpoint"):
        injector._wait_for_restore_checkpoint(30)

    assert injector._attempt_output[CASE.selected_attempt_id] == "BR failed\nroot cause\n"


def test_checkpoint_wait_accepts_the_br_checkpoint_log_gate(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.restore_container = "k08-restore-controller"
    monkeypatch.setattr(
        pitr_module.subprocess,
        "Popen",
        lambda *args, **kwargs: _fake_log_follower(
            b"save checkpoint task info with InLogRestoreAndIdMapPersist status\n"
        ),
    )
    checkpoint_polls = []

    def target_has_checkpoint():
        checkpoint_polls.append(True)
        return len(checkpoint_polls) >= 2

    monkeypatch.setattr(injector, "_target_has_checkpoint", target_has_checkpoint)
    monkeypatch.setattr(injector, "_container_state", lambda container: "running")
    killed = []
    monkeypatch.setattr(
        injector,
        "_docker",
        lambda command, context: killed.append((command, context)),
    )

    injector._wait_for_restore_checkpoint(30)

    assert killed == [(["kill", injector.restore_container], "interrupt K08 restore controller")]
    assert len(checkpoint_polls) >= 2


def test_checkpoint_wait_accepts_a_durable_object_put_event(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.restore_container = "k08-restore-controller"
    monkeypatch.setattr(
        pitr_module.subprocess,
        "Popen",
        lambda *args, **kwargs: _fake_log_follower(
            b"save checkpoint task info with InLogRestoreAndIdMapPersist status\n"
        ),
    )
    monkeypatch.setattr(injector, "_container_state", lambda container: "running")
    killed = []
    monkeypatch.setattr(
        injector,
        "_docker",
        lambda command, context: killed.append((command, context)),
    )
    watcher = _fake_log_follower(b'{"eventName":"s3:ObjectCreated:Put"}\n')

    injector._wait_for_restore_checkpoint(30, watcher)

    assert killed == [(["kill", injector.restore_container], "interrupt K08 restore controller")]
    watcher.kill()
    watcher.wait()


def test_checkpoint_watcher_subscribes_to_current_run_prefix(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.source_network = "k08-source"
    injector.minio_container = "k08-minio"
    injector.context_run_id = "k08-run"
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    captured = []
    watcher = SimpleNamespace(poll=lambda: None, kill=lambda: None, wait=lambda: 0)
    monkeypatch.setattr(
        pitr_module.subprocess,
        "Popen",
        lambda args, **kwargs: captured.append((args, kwargs)) or watcher,
    )

    assert injector._start_checkpoint_watcher() is watcher

    args, kwargs = captured[0]
    assert args[:8] == [
        "docker", "run", "--rm", "--network", "k08-source", "--entrypoint", "/bin/sh", CASE.mc_image,
    ]
    assert "mc watch --json --recursive minio/k08/pitr/k08-run/log/checkpoints/restore-202" in args[-1]
    assert kwargs["stdout"] is pitr_module.subprocess.PIPE
    assert kwargs["stderr"] is pitr_module.subprocess.STDOUT


def test_restore_payload_does_not_preassociate_checkpoint_and_target_identity(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.upstream_cluster_id = RUNTIME["upstream_cluster_id"]
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.snapshot_backup_ts = RUNTIME["snapshot_backup_ts"]
    injector.target_tso = RUNTIME["restored_ts"]
    injector.checkpoint_storage_root = CHECKPOINT_ROOT
    injector.checkpoint_storage_suffix = ""
    injector.checkpoint_storage = CHECKPOINT_STORAGE
    monkeypatch.setattr(injector, "_attempt_rows", lambda attempt_id=None: [[
        CASE.selected_attempt_id, "FAILED", "UNKNOWN", RUNTIME["upstream_cluster_id"],
        RUNTIME["target_cluster_id"], RUNTIME["start_ts"], RUNTIME["restored_ts"],
        RUNTIME["requested_target_ts"], "PERSISTED", "UNVERIFIED", "restore controller exited unexpectedly",
    ]])
    monkeypatch.setattr(injector, "_checkpoint_objects", lambda target_cluster_id=None: ["taskInfo.meta"])
    monkeypatch.setattr(
        injector,
        "_target_observation",
        lambda: {"cluster_id": RUNTIME["target_cluster_id"], "business_tables": [], "markers": []},
    )
    injector._checkpoint_table_id_maps = {
        RUNTIME["target_cluster_id"]: {CASE.operator_touch_target_table: 303},
    }

    observation = injector.restore_operation("get", CASE.selected_attempt_id, {})

    assert observation["attempt"]["checkpoint"] == {
        "storage": "external",
        "prefix": CHECKPOINT_STORAGE,
        "target_cluster_id": RUNTIME["target_cluster_id"],
        "objects": ["taskInfo.meta"],
    }
    assert "table_id_map" not in observation["attempt"]["checkpoint"]
    assert "table_id_map" not in observation["target"]
    assert "compatibility" not in observation


def test_all_five_injector_lifecycle_methods_are_present():
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()

    assert tuple(
        method for method in ("install", "activate", "prepare_observability", "quiesce", "recover")
        if callable(getattr(injector, method))
    ) == ("install", "activate", "prepare_observability", "quiesce", "recover")


def test_recovery_detaches_minio_before_target_network_teardown(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.minio_running = True
    injector.minio_container = "k08-minio"
    calls = []
    monkeypatch.setattr(injector, "_docker", lambda command, context: calls.append((command, context)))

    injector._detach_minio(SimpleNamespace(network_name="k08-target-network"))

    assert calls == [
        (
            ["network", "disconnect", "--force", "k08-target-network", "k08-minio"],
            "disconnect K08 MinIO from target network='k08-target-network'",
        )
    ]


def test_cluster_id_uses_tidb_v8_cluster_endpoint():
    calls = []

    class FakeDeployment:
        def pd_request(self, method, path):
            calls.append((method, path))
            return {"id": 987654321}

    assert TidbBusinessChangePitrCheckpointRecoveryInjector._cluster_id(FakeDeployment()) == 987654321
    assert calls == [("GET", "/pd/api/v1/cluster")]


def test_injector_prepare_observability_returns_dynamic_truth(monkeypatch):
    injector = TidbBusinessChangePitrCheckpointRecoveryInjector()
    injector.case = CASE
    injector.env = SimpleNamespace()
    injector.upstream_cluster_id = RUNTIME["upstream_cluster_id"]
    injector.target_cluster_id = RUNTIME["target_cluster_id"]
    injector.snapshot_backup_ts = RUNTIME["snapshot_backup_ts"]
    injector.log_start_ts = RUNTIME["log_start_ts"]
    injector.target_tso = RUNTIME["target_tso"] if "target_tso" in RUNTIME else RUNTIME["restored_ts"]
    monkeypatch.setattr(injector, "_verify_failed_state", lambda: None)
    monkeypatch.setattr(
        injector,
        "_source_rows",
        lambda sql: OBJECTS
        if "k08_backup_objects" in sql.casefold()
        else [[2000, 2_001_000, 1_199_000, 4000, 8_002_000, 2000, 2_001_000, 1]],
    )

    evidence = injector.prepare_observability(SimpleNamespace())

    assert evidence["k08_runtime"]["upstream_cluster_id"] == RUNTIME["upstream_cluster_id"]
    assert evidence["k08_runtime"]["target_cluster_id"] == RUNTIME["target_cluster_id"]
    assert evidence["k08_target_truth"] == TARGET_TRUTH
