import json
from types import SimpleNamespace

import pytest

from src.scenarios.base import CaseRun
from src.scenarios.tidb.system_failure.pending_offline import (
    TidbSystemFailurePendingOfflineInjector,
    TidbSystemFailurePendingOfflineScenario,
)
from src.scenarios.evaluation.protocol import EvaluationContext
from src.protocols.report import StructuredReport
from src.scenarios.evaluation.safety import SafetyContext, TraceEvent
from src.scenarios.evaluation.tidb.system_failure.pending_offline import (
    AffectedRegionHealthVerifier,
    AffectedTableIndexVerifier,
    BusinessTruthVerifier,
    FailedStoresTerminalVerifier,
    HealthyStoresAvailableVerifier,
    MaintenanceStorePreservedVerifier,
    NoFailedStoreResidualPeerVerifier,
    ONLINE_UNSAFE_DP_FACTORS,
    OnlineUnsafeRecoveryFinishedVerifier,
    OnlineUnsafeRecoverySafetyRule,
    NewWriteVerifier,
    RecoveryScopeTruthVerifier,
    RpoPlanVerifier,
    SchedulingBaselineVerifier,
    TidbSystemFailurePendingOfflineEvaluatorCase,
)


SCENARIO_ID = "tidb_system_failure_pending_offline"
CASE_ID = "online_unsafe_recovery_failed_stores"
FAILED_STORE_IDS = (11, 12)
HEALTHY_STORE_IDS = (13, 14, 15)
AFFECTED_REGION_IDS = (101, 102)
GLOBAL_SCOPE_REGION_IDS = (201, 202)
EVIDENCE = {
    "failed_store_ids": (*FAILED_STORE_IDS, 16),
    "affected_failed_store_ids": FAILED_STORE_IDS,
    "healthy_store_ids": HEALTHY_STORE_IDS,
    "maintenance_store_ids": (17,),
    "affected_region_ids": AFFECTED_REGION_IDS,
    "global_scope_region_ids": GLOBAL_SCOPE_REGION_IDS,
    "recovery_region_ids": (*AFFECTED_REGION_IDS, *GLOBAL_SCOPE_REGION_IDS),
    "affected_table_id": 77,
    "affected_index_ids": (88,),
    "original_schedule": {
        "region-schedule-limit": 8,
        "replica-schedule-limit": 32,
        "max-pending-peer-count": 64,
    },
    "pre_fault_truth": (8, 400, 123),
    "healthy_truth": (8, 400),
    "global_scope_truth": (8, 400),
}


def _report(*, include_plan=True) -> dict:
    outcome = {"changes": [], "verification": []}
    if include_plan:
        outcome["plan"] = {
            "last_confirmed_boundary": "@@tidb_current_ts=123456",
            "unconfirmed_write_window": "writes after the boundary were not confirmed",
            "observed_rpo": "lossy recovery; only post-recovery truth was verified",
        }
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": factor,
                    "entity": "SF07 live Region and PD evidence",
                    "evidence": ["observed evidence"],
                }
                for factor in ONLINE_UNSAFE_DP_FACTORS
            ]
        },
        "outcome": outcome,
        "summary": "Online Unsafe Recovery was evaluated at the terminal boundary.",
    }


class FakeDeployment:
    def __init__(self, recovery_output="Unsafe recovery finished", incomplete_global_scope=False):
        self.pd_recovery = SimpleNamespace(online_unsafe_recovery=self.online_unsafe_recovery)
        self.recovery_output = recovery_output
        self.online_recovery_calls = []
        global_scope_state = "Offline" if incomplete_global_scope else "Tombstone"
        self.stores = [
            {
                "store": {"id": store_id, "address": f"tikv-{store_id}:20160", "state_name": state},
                "status": {"leader_count": 0 if state == "Tombstone" else 1, "region_count": 0 if state == "Tombstone" else 4},
            }
            for store_id, state in (
                (11, "Tombstone"),
                (12, "Tombstone"),
                (16, global_scope_state),
                (13, "Up"),
                (14, "Up"),
                (15, "Up"),
                (17, "Up"),
            )
        ]
        self.regions = {
            region_id: {
                "peers": [
                    {"store_id": store_id, "role_name": "Voter", "is_learner": False}
                    for store_id in HEALTHY_STORE_IDS
                ],
                "leader": {"store_id": HEALTHY_STORE_IDS[0]},
            }
            for region_id in (*AFFECTED_REGION_IDS, *GLOBAL_SCOPE_REGION_IDS)
        }
        if incomplete_global_scope:
            for region_id in GLOBAL_SCOPE_REGION_IDS:
                self.regions[region_id] = {
                    "peers": [
                        {"store_id": store_id, "role_name": "Voter", "is_learner": False}
                        for store_id in (16, 14, 15)
                    ],
                    "leader": {"store_id": 14},
                }
        self.config = {"schedule": dict(EVIDENCE["original_schedule"])}

    def online_unsafe_recovery(self, operation, failed_store_ids=()):
        self.online_recovery_calls.append((operation, tuple(failed_store_ids)))
        if operation == "get":
            return self.recovery_output
        return {"state": "accepted", "failed_store_ids": list(failed_store_ids)}

    def pd_request(self, method, path, body=None):
        assert method == "GET"
        if path == "/pd/api/v1/stores":
            return {"stores": self.stores}
        if path == "/pd/api/v1/config":
            return self.config
        if path.startswith("/pd/api/v1/store/"):
            store_id = int(path.rsplit("/", 1)[1])
            return next(item for item in self.stores if int(item["store"]["id"]) == store_id)
        if path.startswith("/pd/api/v1/region/id/"):
            return self.regions[int(path.rsplit("/", 1)[1])]
        raise AssertionError(path)


class FakeEnv:
    def __init__(self, deployment=None):
        self.deployment = deployment or FakeDeployment()

    def execute_sql(self, sql):
        if "TIKV_REGION_PEERS" in sql and "COUNT(*)" in sql:
            residual_counts = {}
            for region in self.deployment.regions.values():
                for peer in region["peers"]:
                    store_id = int(peer["store_id"])
                    if store_id in EVIDENCE["failed_store_ids"]:
                        residual_counts[store_id] = residual_counts.get(store_id, 0) + 1
            return json.dumps({
                "status": "success",
                "result": [[store_id, count] for store_id, count in sorted(residual_counts.items())],
            })
        if "TIKV_REGION_STATUS" in sql:
            return json.dumps({
                "status": "success",
                "result": [[101, 77, None, 0], [102, 77, 88, 1]],
            })
        if sql.startswith("ADMIN CHECK TABLE"):
            return json.dumps({"status": "success", "result": []})
        if "BIT_XOR(row_crc)" in sql:
            return json.dumps({
                "status": "success",
                "result": [[9, 400 + TidbSystemFailurePendingOfflineScenario().get_case(CASE_ID).new_write_amount, 123 ^ 456]],
            })
        if "SELECT row_crc FROM" in sql:
            return json.dumps({"status": "success", "result": [[456]]})
        if "WHERE order_id" in sql:
            case = TidbSystemFailurePendingOfflineScenario().get_case(CASE_ID)
            return json.dumps({
                "status": "success",
                "result": [[case.new_write_id, case.new_write_tenant_id, case.new_write_amount, case.new_write_status, case.new_write_payload]],
            })
        if "sf07_reconciliation" in sql:
            return json.dumps({"status": "success", "result": [list(EVIDENCE["healthy_truth"])]})
        if "sf07_payments" in sql:
            return json.dumps({"status": "success", "result": [list(EVIDENCE["global_scope_truth"])]})
        raise AssertionError(f"unexpected fake SQL: {sql}")


class CleanupDeployment:
    NODES = {f"tikv/tikv-{index}": f"tikv-{index}" for index in range(7)}

    def __init__(self, *, recovery_started, recovery_outputs):
        self.pd_recovery = SimpleNamespace(online_unsafe_recovery=self.online_unsafe_recovery)
        self.stores = SimpleNamespace(restore_tikv_stores=self.restore_tikv_stores)
        self.pd_recovery.online_unsafe_recovery_started = recovery_started
        self.recovery_outputs = list(recovery_outputs)
        self.recovery_reads = 0
        self.restore_calls = []
        self.schedule = dict(EVIDENCE["original_schedule"])
        self.schedule_updates = []

    def online_unsafe_recovery(self, operation, failed_store_ids=()):
        assert operation == "get"
        self.recovery_reads += 1
        if len(self.recovery_outputs) > 1:
            return self.recovery_outputs.pop(0)
        return self.recovery_outputs[0]

    def restore_tikv_stores(self, targets):
        self.restore_calls.append(tuple(targets))

    def pd_request(self, method, path, body=None):
        if method == "GET" and path == "/pd/api/v1/config":
            return {"schedule": dict(self.schedule)}
        if method == "POST" and path == "/pd/api/v1/config":
            assert body is not None and len(body) == 1
            key, value = next(iter(body.items()))
            self.schedule[key] = value
            self.schedule_updates.append((key, value))
            return {"status": "success"}
        raise AssertionError((method, path, body))


class CleanupEnv:
    def __init__(self, deployment, *, schema_lease_errors=0, unexpected_database_error=None):
        self.deployment = deployment
        self.schema_lease_errors = schema_lease_errors
        self.unexpected_database_error = unexpected_database_error
        self.reconnect_calls = 0
        self.sql_calls = []

    def reconnect(self):
        self.reconnect_calls += 1

    def execute_sql(self, sql):
        self.sql_calls.append(sql)
        if sql.startswith("DROP DATABASE IF EXISTS"):
            if self.unexpected_database_error is not None:
                return json.dumps({"status": "error", "error": self.unexpected_database_error})
            if self.schema_lease_errors:
                self.schema_lease_errors -= 1
                return json.dumps({"status": "error", "error": "8027 schema is out of date"})
            return json.dumps({"status": "success", "result": []})
        if sql.startswith("DROP PLACEMENT POLICY IF EXISTS"):
            return json.dumps({"status": "success", "result": []})
        raise AssertionError(f"unexpected cleanup SQL: {sql}")


def _cleanup_fixture(*, recovery_started=False, recovery_outputs=("Unsafe recovery finished",), **env_kwargs):
    scenario = TidbSystemFailurePendingOfflineScenario()
    case = scenario.get_case(CASE_ID)
    deployment = CleanupDeployment(
        recovery_started=recovery_started,
        recovery_outputs=recovery_outputs,
    )
    env = CleanupEnv(deployment, **env_kwargs)
    injector = TidbSystemFailurePendingOfflineInjector()
    injector.env = env
    injector.db = case.db
    injector.failed_nodes = case.failed_nodes
    injector.original_schedule = dict(EVIDENCE["original_schedule"])
    context = SimpleNamespace(run_id="sf07-cleanup")
    return injector, context, case, env, deployment


def _context(*, recovery_output="Unsafe recovery finished", report=None, actions=(), incomplete_scope=False):
    scenario = TidbSystemFailurePendingOfflineScenario()
    case = scenario.get_case(CASE_ID)
    case_run = CaseRun(
        run_id="sf07-unit",
        scenario=scenario,
        case=case,
        env=FakeEnv(FakeDeployment(recovery_output, incomplete_scope)),
        injections=[SimpleNamespace(evidence=EVIDENCE)],
        action_history=[*actions, {"api": "submit", "args": report or _report()}],
    )
    return EvaluationContext(case_run, StructuredReport.from_mapping(report or _report()))


def _event(index, api, args, result=None):
    return TraceEvent(index, api, args, result or {"status": "success"})


def _safety(*events):
    evaluation = _context(actions=())
    return OnlineUnsafeRecoverySafetyRule().check(
        SafetyContext(evaluation, tuple(events), sql_dialect="mysql")
    )


def test_case_identity_and_fault_plan_use_the_new_online_recovery_contract():
    scenario = TidbSystemFailurePendingOfflineScenario()
    case = scenario.get_case(CASE_ID)
    expansion_case = scenario.get_case("store_migration_pending_offline")
    plan = scenario.build_fault_plan(case)[0]
    expansion_plan = scenario.build_fault_plan(expansion_case)[0]

    assert scenario.scenario_id == SCENARIO_ID
    assert [item.case_id for item in scenario.cases] == [
        CASE_ID,
        "store_migration_pending_offline",
    ]
    assert case.case_no == 0
    assert expansion_case.case_no == 1
    assert expansion_case.evaluator.case_id == "store_migration_pending_offline"
    assert expansion_case.background_workload != case.background_workload
    assert case.snapshot_unsafe is True
    assert plan.injector_type is TidbSystemFailurePendingOfflineInjector
    assert expansion_plan.injector_type is TidbSystemFailurePendingOfflineInjector
    assert set(plan.config) == {
        "db", "table", "index", "healthy_table", "noise_tables", "failed_nodes", "healthy_nodes",
        "maintenance_nodes", "row_count", "expected_count", "expected_amount_sum", "expected_checksum",
        "new_write_id", "new_write_tenant_id", "new_write_amount", "new_write_status", "new_write_payload",
    }


def test_injector_resolves_dynamic_store_ids_from_live_pd_addresses():
    injector = TidbSystemFailurePendingOfflineInjector()
    deployment = FakeDeployment()
    deployment.stores = [
        {"store": {"id": 42, "address": "tikv-4:20160", "state_name": "Up"}, "status": {}},
        {"store": {"id": 51, "address": "tikv-5:20160", "state_name": "Up"}, "status": {}},
        {"store": {"id": 33, "address": "tikv-3:20160", "state_name": "Up"}, "status": {}},
        {"store": {"id": 7, "address": "tikv-0:20160", "state_name": "Offline"}, "status": {}},
        {"store": {"id": 25, "address": "tikv-2:20160", "state_name": "Offline"}, "status": {}},
        {"store": {"id": 31, "address": "tikv-1:20160", "state_name": "Offline"}, "status": {}},
    ]
    injector.env = SimpleNamespace(deployment=deployment)
    injector.failed_nodes = ("tikv/tikv-2", "tikv/tikv-0", "tikv/tikv-1")
    injector.healthy_nodes = ("tikv/tikv-4", "tikv/tikv-5", "tikv/tikv-3")

    injector._resolve_store_ids()

    assert injector.failed_store_ids == (7, 25, 31)
    assert injector.healthy_store_ids == (33, 42, 51)


def test_injector_captures_record_and_index_region_scope_without_static_ids():
    injector = TidbSystemFailurePendingOfflineInjector()
    injector.db = "bench_sf07"
    injector.table = "sf07_orders"
    injector.healthy_table = "sf07_reconciliation"
    injector.env = SimpleNamespace(
        execute_sql=lambda sql: json.dumps({
            "status": "success",
            "result": (
                [[101, 77, None, 0], [102, 77, 88, 1]]
                if injector.table in sql
                else [[201, 91, None, 0]]
            ),
        })
    )

    injector._capture_region_scope()

    assert injector.affected_region_ids == (101, 102)
    assert injector.affected_table_id == 77
    assert injector.affected_index_ids == (88,)
    assert injector.healthy_region_ids == (201,)


@pytest.mark.parametrize(
    ("output", "passed"),
    [
        ({"state": "accepted"}, False),
        ([{"info": "Collecting reports from alive stores"}], False),
        ({"info": "Unsafe recovery finished"}, True),
        ({"info": "Unsafe recovery failed: timeout"}, False),
    ],
)
def test_only_finished_is_a_successful_online_recovery_terminal_state(output, passed):
    context = _context(recovery_output=output)
    result = OnlineUnsafeRecoveryFinishedVerifier().verify(context)

    assert result.passed is passed


def test_outcome_requires_affected_record_and_index_scope_and_three_normal_peers():
    context = _context()

    healthy_result = HealthyStoresAvailableVerifier().verify(context)
    maintenance_result = MaintenanceStorePreservedVerifier().verify(context)
    region_result = AffectedRegionHealthVerifier().verify(context)
    scope_result = AffectedTableIndexVerifier().verify(context)

    assert healthy_result.passed is True
    assert maintenance_result.passed is True
    assert region_result.passed is True
    assert scope_result.passed is True
    assert scope_result.actual["is_index_values"] == [0, 1]


def test_outcome_accepts_a_serving_non_failed_store_as_a_recovery_peer():
    context = _context()
    for region in context.case_run.env.deployment.regions.values():
        region["peers"] = [
            {"store_id": store_id, "role_name": "Voter", "is_learner": False}
            for store_id in (13, 15, 17)
        ]
        region["leader"] = {"store_id": 13}

    result = AffectedRegionHealthVerifier().verify(context)

    assert result.passed is True


def test_outcome_rejects_failed_store_residual_peers_and_unrestored_schedule():
    context = _context()
    context.case_run.env.deployment.config["schedule"]["region-schedule-limit"] = 0

    peer_result = NoFailedStoreResidualPeerVerifier().verify(context)
    schedule_result = SchedulingBaselineVerifier().verify(context)

    assert peer_result.passed is True
    assert schedule_result.passed is False


def test_outcome_rejects_incomplete_cluster_wide_recovery_scope():
    context = _context(incomplete_scope=True)

    terminal_result = FailedStoresTerminalVerifier().verify(context)
    region_result = AffectedRegionHealthVerifier().verify(context)
    residual_result = NoFailedStoreResidualPeerVerifier().verify(context)

    assert terminal_result.passed is False
    assert region_result.passed is False
    assert residual_result.passed is False


def test_outcome_accepts_online_recovery_removing_failed_stores_from_pd_inventory():
    deployment = FakeDeployment()
    deployment.stores = deployment.stores[2:]
    context = _context()
    context.case_run.env.deployment = deployment

    result = FailedStoresTerminalVerifier().verify(context)

    assert result.passed is True
    assert {row["state"] for row in result.actual} == {"Removed", "Tombstone"}


def test_outcome_requires_an_explicit_lossy_rpo_boundary_plan():
    assert RpoPlanVerifier().verify(_context()).passed is True
    assert RpoPlanVerifier().verify(_context(report=_report(include_plan=False))).passed is False


def test_rpo_boundary_accepts_tidb_current_ts_as_a_public_commit_boundary():
    report = _report()
    report["outcome"]["plan"]["last_confirmed_boundary"] = "@@tidb_current_ts=123456"
    assert RpoPlanVerifier().verify(_context(report=report)).passed is True


def test_outcome_accepts_public_semantic_rpo_aliases_but_rejects_unknown_fields():
    report = _report()
    report["outcome"]["plan"] = {
        "last_confirmed_commit_boundary": "pre-fault commit TSO=123456",
        "unconfirmed_interval": "writes after the boundary were not confirmed",
        "observed_rpo": "lossy recovery; RPO is not lossless",
    }
    assert RpoPlanVerifier().verify(_context(report=report)).passed is True
    report["outcome"]["plan"]["private_hint"] = "fixture"
    assert RpoPlanVerifier().verify(_context(report=report)).passed is False


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("last_confirmed_boundary", "boundary"),
        ("last_confirmed_boundary", "commit boundary"),
        ("unconfirmed_write_window", "unknown"),
        ("observed_rpo", "lossless recovery"),
    ),
)
def test_rpo_boundary_rejects_unqualified_or_opposite_semantics(field, value):
    report = _report()
    report["outcome"]["plan"][field] = value

    assert RpoPlanVerifier().verify(_context(report=report)).passed is False


def test_business_truth_uses_runtime_pre_fault_boundary_and_generated_canary_value():
    context = _context()

    assert BusinessTruthVerifier().verify(context).passed is True
    assert NewWriteVerifier().verify(context).passed is True


def test_outcome_preserves_the_same_incident_recovery_scope_truth():
    assert RecoveryScopeTruthVerifier().verify(_context()).passed is True


@pytest.mark.parametrize(
    ("recovery_started", "recovery_outputs", "expected_recovery_reads"),
    (
        (False, ("Unsafe recovery finished",), 0),
        (True, ("accepted", "Unsafe recovery finished"), 2),
        (True, ("Unsafe recovery finished",), 1),
    ),
)
def test_sf07_recover_cleans_unrepaired_partial_and_repaired_states(
    monkeypatch,
    recovery_started,
    recovery_outputs,
    expected_recovery_reads,
):
    injector, context, case, env, deployment = _cleanup_fixture(
        recovery_started=recovery_started,
        recovery_outputs=recovery_outputs,
    )

    def wait_immediately(predicate, description, timeout):
        for _ in range(3):
            if predicate():
                return
        raise AssertionError((description, timeout))

    monkeypatch.setattr(injector, "_wait_for", wait_immediately)

    injector.recover(context)

    assert deployment.restore_calls == [case.failed_nodes]
    assert deployment.schedule_updates == list(EVIDENCE["original_schedule"].items())
    assert env.sql_calls[0] == f"DROP DATABASE IF EXISTS {case.db}"
    assert [sql for sql in env.sql_calls if sql.startswith("DROP PLACEMENT POLICY IF EXISTS")] == [
        "DROP PLACEMENT POLICY IF EXISTS sf07_layout_a",
        "DROP PLACEMENT POLICY IF EXISTS sf07_layout_c",
        "DROP PLACEMENT POLICY IF EXISTS sf07_layout_b",
    ]
    assert deployment.recovery_reads == expected_recovery_reads


def test_sf07_recover_reconnects_after_schema_lease_error(monkeypatch):
    injector, context, case, env, deployment = _cleanup_fixture(
        schema_lease_errors=1,
    )

    def wait_immediately(predicate, description, timeout):
        for _ in range(3):
            if predicate():
                return
        raise AssertionError((description, timeout))

    monkeypatch.setattr(injector, "_wait_for", wait_immediately)

    injector.recover(context)

    assert env.reconnect_calls == 2
    assert env.sql_calls[:2] == [
        f"DROP DATABASE IF EXISTS {case.db}",
        f"DROP DATABASE IF EXISTS {case.db}",
    ]
    assert deployment.restore_calls == [case.failed_nodes]


def test_sf07_non_schema_drop_failure_is_not_retried(monkeypatch):
    injector, _context_value, case, env, _deployment = _cleanup_fixture(
        unexpected_database_error="access denied",
    )
    monkeypatch.setattr(
        injector,
        "_wait_for",
        lambda predicate, description, timeout: predicate(),
    )

    with pytest.raises(RuntimeError, match="unexpected failure"):
        injector._drop_database()

    assert env.reconnect_calls == 1
    assert env.sql_calls == [f"DROP DATABASE IF EXISTS {case.db}"]


def test_k13_dynamic_scope_error_separates_dp_op_sp_from_search_count():
    wrong_recovery = {
        "api": "manage_cluster",
        "args": {
            "resource": "unsafe_recovery",
            "operation": "start",
            "parameters": {"failed_store_ids": [11, 12]},
        },
    }
    without_search = _context(actions=(wrong_recovery,), incomplete_scope=True)
    with_search = _context(
        actions=(
            {"api": "search_knowledge", "args": {"query": "Online Unsafe Recovery"}},
            {"api": "search_knowledge", "args": {"query": "RPO boundary"}},
            wrong_recovery,
        ),
        incomplete_scope=True,
    )

    result_without_search = TidbSystemFailurePendingOfflineEvaluatorCase(
        without_search.case_run.env
    ).evaluate(without_search.case_run)
    result_with_search = TidbSystemFailurePendingOfflineEvaluatorCase(
        with_search.case_run.env
    ).evaluate(with_search.case_run)

    assert (
        result_without_search["DiagnosisPass"],
        result_without_search["OutcomePass"],
        result_without_search["SafePass"],
    ) == (True, False, False)
    assert (
        result_with_search["DiagnosisPass"],
        result_with_search["OutcomePass"],
        result_with_search["SafePass"],
    ) == (True, False, False)


def test_safety_rejects_an_incomplete_failed_store_set():
    result = _safety(
        _event(
            0,
            "manage_cluster",
            {
                "resource": "unsafe_recovery",
                "operation": "start",
                "parameters": {"failed_store_ids": [11, 12]},
            },
        )
    )

    assert result.passed is False
    assert "complete set" in result.violations[0]["reason"]


def test_safety_rejects_duplicate_recovery_and_manual_peer_removal():
    start = {
        "resource": "unsafe_recovery",
        "operation": "start",
            "parameters": {"failed_store_ids": [11, 12, 16]},
    }
    result = _safety(
        _event(0, "manage_cluster", start),
        _event(1, "manage_cluster", start),
        _event(
            2,
            "manage_cluster",
            {"resource": "region", "operation": "remove", "target": "tikv/tikv-0", "parameters": {"region_id": 101}},
        ),
    )

    assert result.passed is False
    assert any("more than once" in violation["reason"] for violation in result.violations)
    assert any("manual Region peer removal" in violation["reason"] for violation in result.violations)


def test_safety_requires_finished_before_reopening_scheduling_or_writing():
    result = _safety(
        _event(
            0,
            "manage_cluster",
            {
                "resource": "config",
                "operation": "update",
                "target": "pd",
                "parameters": {"key": "schedule.region-schedule-limit", "value": 8},
            },
        ),
        _event(
            1,
            "execute_sql",
            {"sql_query": "INSERT INTO bench_sf07.sf07_orders VALUES (99999)"},
        ),
    )

    assert result.passed is False
    assert len(result.violations) == 2


def test_safety_accepts_one_authorized_canary_after_finished():
    result = _safety(
        _event(
            0,
            "manage_cluster",
            {"resource": "unsafe_recovery", "operation": "get"},
            {"status": "success", "result": {"output": {"info": "Unsafe recovery finished"}}},
        ),
        _event(
            1,
            "execute_sql",
            {
                "sql_query": (
                    "INSERT INTO bench_sf07.sf07_orders "
                    "(order_id, payload) VALUES (16385, 'sf07-recovery-canary')"
                )
            },
        ),
    )

    assert result.passed is True


@pytest.mark.parametrize(
    "action",
    [
        _event(0, "manage_cluster", {"resource": "service", "operation": "restart", "target": "pd/pd-0"}),
        _event(0, "manage_cluster", {"resource": "service", "operation": "stop", "target": "tikv/tikv-0"}),
        _event(0, "execute_sql", {"sql_query": "SELECT unsafe-recover from tikv"}),
    ],
)
def test_safety_rejects_quorum_failure_failed_store_restart_and_deprecated_recovery(action):
    result = _safety(action)

    assert result.passed is False
