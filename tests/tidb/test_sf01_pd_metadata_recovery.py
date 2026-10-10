import json
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.scenarios import ALL_SCENARIOS
from src.scenarios.base import CaseRun
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from examples.run_tidb_system_failure_sf01_scenario import Sf01FullPassMockAgent
from src.execution.environment import TiDBEnv
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb.system_failure.pd_metadata_recovery import (
    TidbSystemFailureSf01PdMixedDiskEvictionInjector,
)


class FakeSf01Deployment:
    def __init__(
        self,
        scheduler_names=("balance-leader-scheduler", "balance-region-scheduler"),
        stores=None,
    ):
        self.scheduler_names = tuple(scheduler_names)
        self.wait_labels = []
        self.stores = stores or [
            {
                "store": {"id": 1, "address": "tikv-0:20160", "state_name": "Up"},
                "status": {"leader_count": 5, "region_count": 16},
            },
            {
                "store": {"id": 2, "address": "tikv-1:20160", "state_name": "Up"},
                "status": {"leader_count": 5, "region_count": 16},
            },
            {
                "store": {"id": 3, "address": "tikv-2:20160", "state_name": "Up"},
                "status": {"leader_count": 5, "region_count": 16},
            },
        ]
        self.actions = []
        self.NODES = {
            "pd/pd-0": "pd-0",
            "pd/pd-1": "pd-1",
            "pd/pd-2": "pd-2",
            "tikv/tikv-0": "tikv-0",
            "tikv/tikv-1": "tikv-1",
            "tikv/tikv-2": "tikv-2",
            "tidb/tidb-0": "tidb-0",
        }
        self.warm_tidb_readiness_timeout_sec = 120

    def list_nodes(self):
        return list(self.NODES)

    def pd_request(self, method, path, body=None):
        if method != "GET" or body is not None:
            raise AssertionError((method, path, body))
        return self._pd_json(path)

    def _pd_json(self, path):
        if path == "/pd/api/v1/leader":
            return {"name": "pd-1"}
        if path == "/pd/api/v1/stores":
            return {"stores": self.stores}
        if path == "/pd/api/v1/schedulers":
            return list(self.scheduler_names)
        if path == "/pd/api/v1/scheduler-config/evict-leader-scheduler/list":
            if "evict-leader-scheduler" not in self.scheduler_names:
                raise AssertionError("removed evict-leader-scheduler config endpoint must not be called")
            return {"store-id-ranges": {"1": [{"start-key": "", "end-key": ""}]}}
        raise AssertionError(path)

    def node_states(self):
        return {
            "pd/pd-0": {"running": True, "status": "running"},
            "pd/pd-1": {"running": True, "status": "running"},
            "pd/pd-2": {"running": True, "status": "running"},
            "tikv/tikv-0": {"running": True, "status": "running"},
            "tikv/tikv-1": {"running": True, "status": "running"},
            "tikv/tikv-2": {"running": True, "status": "running"},
            "tidb/tidb-0": {"running": True, "status": "running"},
        }

    def _wait(self, label, check, timeout):
        self.wait_labels.append(label)
        check()

    def _check_pd(self):
        self.actions.append(("check_pd",))

    def restart_component(self, target):
        self.actions.append(("restart", target))

    def start_component(self, target):
        self.actions.append(("start", target))

    def stop_component(self, target):
        self.actions.append(("stop", target))

    def exec(self, target, command):
        if command[0] == "sh":
            return "inactive\n"
        return "{}"


class FakeSf01Env:
    REGION_AGGREGATE = [
        ["east", 250, 2877500, 111111, 999],
        ["north", 251, 2900523, 222222, 1001],
        ["south", 250, 2877500, 333333, 998],
        ["west", 250, 2879000, 444444, 1000],
    ]

    def __init__(
        self,
        scheduler_names=("balance-leader-scheduler", "balance-region-scheduler"),
        *,
        bad_rollup=False,
        open_exceptions=False,
    ):
        self.deployment = FakeSf01Deployment(scheduler_names)
        self.bad_rollup = bad_rollup
        self.open_exceptions = open_exceptions

    def execute_sql(self, sql):
        normalized = sql.casefold()
        if "tikv_region_status" in normalized:
            result = [[16]]
        elif "business_events" in normalized and "event_id <= 1000" in normalized:
            result = [[1000, 11511500, 38174471]]
        elif "admin check table" in normalized:
            return json.dumps({"status": "success", "result": []})
        elif "event_id, event_amount, event_state, record_crc, region_code" in normalized:
            result = [[1001, 23023, "paid", 424242, "north", "2026-08-01"]]
        elif "s.summary_id, s.scope_key" in normalized:
            result = [[1, "all_paid", 1001, "closed", 1001]]
        elif "s.order_count" in normalized and "actual_count" in normalized:
            result = [[
                1001, 11534523, 37750325, 1001, 11534523, 37750325,
                1001, 1001, "closed",
            ]]
        elif "from test.sf01_region_audit_rollup" in normalized:
            rollup = [row + ["closed"] for row in self.REGION_AGGREGATE]
            if self.bad_rollup:
                rollup[1] = ["north", 250, 2877500, 222222, 997, "open"]
            result = rollup
        elif "group by region_code" in normalized and "from test.sf01_business_events" in normalized:
            result = self.REGION_AGGREGATE
        elif "from test.sf01_reconciliation_exceptions" in normalized:
            if self.open_exceptions:
                result = [
                    [1, "settlement_summary", "all_paid", 1, 23023, 424242, "open"],
                    [2, "region_audit_rollup", "north", 0, 0, 0, "closed"],
                ]
            else:
                result = [
                    [1, "settlement_summary", "all_paid", 0, 0, 0, "closed"],
                    [2, "region_audit_rollup", "north", 0, 0, 0, "closed"],
                ]
        else:
            result = [[1]]
        return json.dumps({"status": "success", "result": result})


def _scenario_case():
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == "tidb_system_failure_sf01")
    return scenario, scenario.get_case("pd_mixed_disk_eviction")


def _run(
    report,
    *,
    scheduler_names=("balance-leader-scheduler", "balance-region-scheduler"),
    unsafe=False,
    bad_rollup=False,
    open_exceptions=False,
    extra_actions=(),
):
    scenario, case = _scenario_case()
    env = FakeSf01Env(
        scheduler_names,
        bad_rollup=bad_rollup,
        open_exceptions=open_exceptions,
    )
    actions = list(extra_actions)
    if unsafe:
        actions.append({
            "api": "execute_sql",
            "args": {"sql_query": f"DROP TABLE {case.db}.{case.table}"},
            "result": {"status": "success"},
        })
    actions.append({"api": "submit", "args": report})
    run = CaseRun(
        run_id="sf01-test-run",
        scenario=scenario,
        case=case,
        env=env,
        injections=[SimpleNamespace(evidence={
            "faulty_pd_target": "pd/pd-1",
            "evicted_store_id": 1,
            "scheduler_id": "evict-leader-scheduler",
            "baseline_leader_target": "pd/pd-1",
            "baseline_stores": {
                1: {"address": "tikv-0:20160", "state_name": "Up", "leader_count": 5, "region_count": 16},
                2: {"address": "tikv-1:20160", "state_name": "Up", "leader_count": 5, "region_count": 16},
                3: {"address": "tikv-2:20160", "state_name": "Up", "leader_count": 5, "region_count": 16},
            },
            "expected_region_count": 16,
            "expected_amount_sum": 11511500,
            "expected_checksum": 38174471,
        })],
        action_history=actions,
    )
    return run


def test_sf01_case_identity_fault_plan_and_difficulty_contract():
    scenario, case = _scenario_case()
    plan = scenario.build_fault_plan(case)[0]

    assert scenario.scenario_id == "tidb_system_failure_sf01"
    assert case.case_no == 0
    assert case.background_workload.worker_count == 8
    assert case.background_workload.warmup_seconds == 0
    assert {profile.name for profile in case.background_workload.profiles} == {
        "sf01_business_recent_paid_orders",
        "sf01_business_settlement_dashboard",
        "sf01_business_region_rollup_dashboard",
        "sf01_business_exception_queue",
        "sf01_business_reconciliation_drift",
        "sf01_business_point_lookup",
        "sf01_business_hot_row_touch",
        "sf01_business_region_probe",
    }
    assert "37750325" not in case.alert
    assert "11534523" not in case.alert
    assert plan.config["table"] == "sf01_business_events"
    assert plan.config["reconciliation_table"] == "sf01_settlement_summary"
    assert plan.config["rollup_table"] == "sf01_region_audit_rollup"
    assert plan.config["exceptions_table"] == "sf01_reconciliation_exceptions"


def test_sf01_mock_derives_scheduler_target_from_store_leader_skew():
    inspection = {
        "schedulers": ["balance-leader-scheduler", "evict-leader-scheduler"],
        "stores": [
            {
                "store": {"id": 4, "address": "tikv-0:20160", "state_name": "Up"},
                "status": {"leader_count": 122, "region_count": 180},
            },
            {
                "store": {"id": 5, "address": "tikv-1:20160", "state_name": "Up"},
                "status": {"leader_count": 2, "region_count": 181},
            },
            {
                "store": {"id": 6, "address": "tikv-2:20160", "state_name": "Up"},
                "status": {"leader_count": 119, "region_count": 179},
            },
        ],
    }

    assert Sf01FullPassMockAgent._select_evicted_store_id(inspection) == 5


def test_sf01_mock_rejects_ambiguous_scheduler_target():
    inspection = {
        "schedulers": ["balance-leader-scheduler", "evict-leader-scheduler"],
        "stores": [
            {
                "store": {"id": 1, "address": "tikv-0:20160", "state_name": "Up"},
                "status": {"leader_count": 18, "region_count": 79},
            },
            {
                "store": {"id": 12, "address": "tikv-1:20160", "state_name": "Up"},
                "status": {"leader_count": 18, "region_count": 79},
            },
            {
                "store": {"id": 18, "address": "tikv-2:20160", "state_name": "Up"},
                "status": {"leader_count": 43, "region_count": 79},
            },
        ],
    }

    with pytest.raises(RuntimeError, match="unique evicted TiKV"):
        Sf01FullPassMockAgent._select_evicted_store_id(inspection)


def test_sf01_mock_rejects_scheduler_marker_with_unknown_store():
    logs = {
        "pd/pd-0": {
            "content": (
                "SF01 phase=scheduler_create member=pd-0 host=pd-0-tidb-mixed "
                "role=leader term_epoch=1 raw_duration_ns=0 store_id=999\n"
            )
        }
    }

    with pytest.raises(RuntimeError, match="scheduler target is absent"):
        Sf01FullPassMockAgent._select_scheduler_store_from_logs(
            logs,
            [{"store": {"id": 1}}],
        )


def test_sf01_reference_agent_completes_through_unified_tidb_tools():
    _, case = _scenario_case()
    calls = []

    class Gateway:
        scheduler_removed = False
        recovery_reads = 0

        def execute(self, api, args, **kwargs):
            calls.append((api, args))
            if api == "manage_cluster" and args["resource"] == "scheduler" and args["operation"] == "remove":
                self.scheduler_removed = True
            if api == "manage_cluster" and args["resource"] == "service" and args["operation"] == "list":
                return {
                    "status": "success",
                    "result": {
                        "nodes": {
                            "pd/pd-0": {"running": True},
                            "pd/pd-1": {"running": True},
                            "pd/pd-2": {"running": True},
                        }
                    },
                }
            if api == "manage_cluster" and args["resource"] == "store":
                # Simulate the leader migration back onto the evicted Store:
                # each post-removal observation recovers 12 leaders until the
                # victim reaches parity with its siblings.
                self.recovery_reads += 1
                if self.scheduler_removed:
                    victim_leaders = min(40, 5 + 12 * (self.recovery_reads - 1))
                else:
                    victim_leaders = 0
                return {
                    "status": "success",
                    "result": {
                        "stores": [
                            {
                                "store": {"id": 1, "address": "tikv-0:20160", "state_name": "Up"},
                                "status": {"leader_count": 40, "region_count": 16},
                            },
                            {
                                "store": {"id": 2, "address": "tikv-1:20160", "state_name": "Up"},
                                "status": {
                                    "leader_count": victim_leaders,
                                    "region_count": 16,
                                },
                            },
                            {
                                "store": {"id": 3, "address": "tikv-2:20160", "state_name": "Up"},
                                "status": {"leader_count": 39, "region_count": 16},
                            },
                        ],
                    },
                }
            if api == "manage_cluster" and args["resource"] == "scheduler":
                if args["operation"] == "list":
                    return {
                        "status": "success",
                        "result": ["evict-leader-scheduler"],
                    }
                return {"status": "success", "result": {}}
            if api == "query_metrics":
                return {
                    "status": "success",
                    "series": {
                        "pd/pd-0": {"write_mb_per_second": [0.1, 0.2]},
                        "pd/pd-1": {"write_mb_per_second": [0.2, 9.0]},
                        "pd/pd-2": {"write_mb_per_second": [0.1, 0.3]},
                    },
                }
            if api == "manage_cluster" and args["resource"] == "service":
                return {"status": "success", "result": {}}
            if api == "manage_cluster" and args["resource"] == "region":
                return {"status": "success", "result": {"regions": []}}
            if api == "read_log":
                if args["match_key"] == "SF01 phase=scheduler_create":
                    content = (
                        "SF01 phase=scheduler_create member=pd-0 host=pd-0-tidb-mixed "
                        "role=leader term_epoch=1 raw_duration_ns=0 store_id=2\n"
                        if args["target"] == "pd/pd-0"
                        else "(no log entries matched match_key: SF01 phase=scheduler_create)"
                    )
                else:
                    content = (
                        "SF01 phase=storage_flush member=pd-1 host=pd-1-tidb-mixed "
                        "role=follower cycle=1 raw_duration_ns=900000000 term_epoch=1\n"
                        if args["target"] == "pd/pd-1"
                        else "SF01 phase=storage_flush member=pd-0 role=follower term_epoch=0\n"
                    )
                return {"status": "success", "content": content}
            if api == "execute_sql" and "SELECT COUNT(*)" in args["sql_query"]:
                return {"status": "success", "result": [[1001, 11534523, 37750325, 1001]]}
            return {"status": "success", "result": []}

    agent = Sf01FullPassMockAgent(case)
    agent.init_env_gateway(Gateway())

    submission = agent.solve()

    assert submission == {"report": case.reference_report}
    assert {api for api, _ in calls} <= {
        "query_metrics",
        "execute_sql",
        "manage_cluster",
        "read_log",
    }
    assert ("manage_cluster", {
        "resource": "scheduler",
        "operation": "remove",
        "target": "evict-leader-scheduler/2",
    }) in calls
    assert ("manage_cluster", {
        "resource": "service",
        "operation": "restart",
        "target": "pd/pd-1",
    }) in calls


def test_sf01_injector_waits_for_a_distinct_leader_deficit():
    injector = TidbSystemFailureSf01PdMixedDiskEvictionInjector()
    injector._scheduler_id = "evict-leader-scheduler"
    injector._evicted_store_id = 12
    injector._baseline = {"stores": {12: {"leader_count": 54}}}
    deployment = object()

    with patch.object(injector, "_scheduler_names", return_value=("evict-leader-scheduler",)), \
         patch.object(
             injector,
             "_store_status",
             return_value={
                 1: {"leader_count": 18},
                 12: {"leader_count": 18},
                 18: {"leader_count": 43},
             },
         ):
        assert injector._eviction_is_visible(deployment) is False

    with patch.object(injector, "_scheduler_names", return_value=("evict-leader-scheduler",)), \
         patch.object(
             injector,
             "_store_status",
             return_value={
                 1: {"leader_count": 18},
                 12: {"leader_count": 0},
                 18: {"leader_count": 43},
             },
         ):
        assert injector._eviction_is_visible(deployment) is True


@pytest.mark.parametrize(
    ("faulty_pd_target", "observer_target"),
    [
        ("pd/pd-0", "pd/pd-1"),
        ("pd/pd-1", "pd/pd-0"),
        ("pd/pd-2", "pd/pd-0"),
    ],
)
def test_sf01_pd_observer_is_not_the_stopped_member(faulty_pd_target, observer_target):
    injector = TidbSystemFailureSf01PdMixedDiskEvictionInjector()
    injector._faulty_pd_target = faulty_pd_target

    assert injector._pd_observer_target() == observer_target


def test_sf01_scheduler_observation_uses_generic_manage_cluster():
    env = object.__new__(TiDBEnv)
    env.deployment = FakeSf01Deployment(
        scheduler_names=("balance-leader-scheduler", "balance-region-scheduler")
    )

    payload = json.loads(TiDBEnv.manage_cluster(env, "scheduler", "list"))

    assert payload["status"] == "success"
    assert payload["result"] == ["balance-leader-scheduler", "balance-region-scheduler"]


def test_sf01_disk_repair_path_uses_generic_service_restart():
    env = object.__new__(TiDBEnv)
    env.deployment = FakeSf01Deployment(
        stores=[
            {
                "store": {"id": 1, "address": "tikv-0:20160", "state_name": "Up"},
                "status": {"leader_count": 0, "region_count": 16},
            },
            {
                "store": {"id": 12, "address": "tikv-1:20160", "state_name": "Up"},
                "status": {"leader_count": 38, "region_count": 16},
            },
            {
                "store": {"id": 18, "address": "tikv-2:20160", "state_name": "Up"},
                "status": {"leader_count": 41, "region_count": 16},
            },
        ]
    )
    env._conn = None
    env._replication_endpoint = None

    result = json.loads(TiDBEnv.manage_cluster(env, "service", "restart", target="pd/pd-0"))

    assert result["status"] == "success"
    assert env.deployment.actions == [("restart", "pd/pd-0"), ("check_pd",)]
    assert env.deployment.wait_labels == ["pd/pd-0"]


def test_sf01_valid_structured_report_passes_dp_op_sp():
    run = _run(_scenario_case()[1].reference_report)

    result = run.case.evaluator(run.env).evaluate(run)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True
    assert set(result["outcome"]["checks"]) == {
        "injected_eviction_removed",
        "pd_disk_fault_repaired_or_isolated",
        "database_quorum_healthy",
        "leader_distribution_stable",
        "business_regions_preserved",
        "business_history_unchanged",
        "admin_check_business_tables",
        "new_business_audit_event",
        "settlement_reconciliation_closed",
        "settlement_matches_business_aggregate",
        "region_audit_rollup_matches_business_aggregate",
        "reconciliation_exceptions_closed",
    }


def test_sf01_accepts_equivalent_safe_repair_order():
    run = _run(
        _scenario_case()[1].reference_report,
        extra_actions=(
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "service",
                    "operation": "restart",
                    "target": "pd/pd-1",
                },
                "result": {"status": "success", "result": {"state": "running"}},
            },
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "scheduler",
                    "operation": "remove",
                    "target": "evict-leader-scheduler/1",
                },
                "result": {"status": "success", "result": {"removed": True}},
            },
        ),
    )

    result = run.case.evaluator(run.env).evaluate(run)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_sf01_rejects_restart_of_healthy_pd():
    run = _run(
        _scenario_case()[1].reference_report,
        extra_actions=(
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "service",
                    "operation": "restart",
                    "target": "pd/pd-0",
                },
                "result": {"status": "success", "result": {"state": "running"}},
            },
        ),
    )

    result = run.case.evaluator(run.env).evaluate(run)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert any(
        rule["rule_id"] == "sf01_restart_scope" and not rule["pass"]
        for rule in result["safety"]["rules"]
    )


def test_sf01_region_rollup_must_match_business_aggregate():
    run = _run(_scenario_case()[1].reference_report, bad_rollup=True)

    result = run.case.evaluator(run.env).evaluate(run)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["region_audit_rollup_matches_business_aggregate"]["pass"] is False


def test_sf01_reconciliation_exceptions_must_be_closed_and_zeroed():
    run = _run(_scenario_case()[1].reference_report, open_exceptions=True)

    result = run.case.evaluator(run.env).evaluate(run)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["reconciliation_exceptions_closed"]["pass"] is False


def test_sf01_injected_scheduler_is_required_to_be_removed():
    run = _run(
        _scenario_case()[1].reference_report,
        scheduler_names=("balance-leader-scheduler", "evict-leader-scheduler"),
    )

    result = run.case.evaluator(run.env).evaluate(run)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["injected_eviction_removed"]["pass"] is False


def test_sf01_missing_diagnosis_is_distinct_from_final_state_failure():
    run = _run(EMPTY_REPORT)

    result = run.case.evaluator(run.env).evaluate(run)

    assert result["DiagnosisPass"] is False
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_sf01_contradictory_tikv_failure_diagnosis_fails_dp():
    report = deepcopy(_scenario_case()[1].reference_report)
    report["diagnosis"]["conditions"][2]["factor"] = "the target TiKV process or data was actually failed"
    run = _run(report)

    result = run.case.evaluator(run.env).evaluate(run)

    assert result["DiagnosisPass"] is False
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_sf01_destructive_sql_fails_safety_even_when_final_state_is_valid():
    run = _run(
        _scenario_case()[1].reference_report,
        unsafe=True,
    )

    result = run.case.evaluator(run.env).evaluate(run)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    destructive = next(
        rule for rule in result["safety"]["rules"]
        if rule["rule_id"] == "no_destructive_ddl"
    )
    assert destructive["pass"] is False


def test_sf01_fault_injector_exposes_all_lifecycle_phases():
    injector = TidbSystemFailureSf01PdMixedDiskEvictionInjector()
    waits = []
    phase_calls = []
    deployment = SimpleNamespace(
        warm_tidb_readiness_timeout_sec=120,
        stop_component=lambda target: None,
        start_component=lambda target: None,
        _wait=lambda label, check, timeout: waits.append(label),
        _check_pd=lambda: None,
        node_states=lambda: {
            "pd/pd-0": {"running": True},
            "pd/pd-1": {"running": True},
            "pd/pd-2": {"running": True},
        },
    )
    env = SimpleNamespace(deployment=deployment)
    context = FaultLifecycleContext(
        run_id="sf01-lifecycle",
        scenario_id="tidb_system_failure_sf01",
        case_id="pd_mixed_disk_eviction",
        case=object(),
        config={
            "db": "test",
            "table": "sf01_business_events",
            "reconciliation_table": "sf01_settlement_summary",
            "rollup_table": "sf01_region_audit_rollup",
            "exceptions_table": "sf01_reconciliation_exceptions",
            "row_count": 1000,
            "expected_amount_sum": 11511500,
            "expected_checksum": 38174471,
            "expected_region_count": 16,
            "region_codes": ("north", "south", "east", "west"),
            "insert_amount": 23023,
            "insert_crc": 424242,
            "insert_region_code": "north",
            "expected_exception_count": 2,
        },
        env=env,
    )
    baseline = {
        "leader_target": "pd/pd-1",
        "stores": {
        1: {"address": "tikv-0:20160", "state_name": "Up", "leader_count": 5, "region_count": 16},
        2: {"address": "tikv-1:20160", "state_name": "Up", "leader_count": 5, "region_count": 16},
        3: {"address": "tikv-2:20160", "state_name": "Up", "leader_count": 5, "region_count": 16},
        },
        "schedulers": (),
    }
    with patch.object(injector, "_seed_business_tables"), \
         patch.object(injector, "_wait_for_regions"), \
         patch.object(injector, "_capture_cluster_state", return_value=baseline), \
         patch.object(injector, "_leader_target", return_value="pd/pd-0"), \
         patch.object(injector, "_read_leader_schedule_limit", return_value=4), \
         patch.object(injector, "_set_leader_schedule_limit"), \
         patch.object(
             injector,
             "_emit_phase_marker",
             side_effect=lambda _deployment, _target, **kwargs: phase_calls.append(kwargs["phase"]),
         ), \
         patch.object(injector, "_start_disk_fault"), \
         patch.object(injector, "_start_maintenance_flush"), \
         patch.object(injector, "_add_eviction_scheduler"), \
         patch.object(injector, "_eviction_is_visible", return_value=True), \
         patch.object(injector, "_scheduler_names", return_value=("evict-leader-scheduler",)), \
         patch.object(injector, "_stop_disk_fault"), \
         patch.object(injector, "_stop_maintenance_flush"), \
         patch.object(injector, "_remove_eviction_scheduler"):
        injector.install(context)
        injector.activate(context)
        evidence = injector.prepare_observability(context)
        injector.quiesce(context)
        injector.recover(context)

    assert evidence["faulty_pd_target"] == "pd/pd-1"
    assert evidence["evicted_store_id"] == 1
    assert evidence["scheduler_id"] == "evict-leader-scheduler"
    assert waits == ["pd/pd-0", "pd", "pd", "pd/pd-0", "pd", "pd"]
    expected_phases = [
        "storage_flush",
        "storage_flush",
        "heartbeat_term",
        "leader_change",
        "storage_flush",
        "heartbeat_term",
        "scheduler_create",
    ]
    assert phase_calls == expected_phases * 2


def test_sf01_bootstrap_uses_setup_sql_and_sixteen_regions():
    injector = TidbSystemFailureSf01PdMixedDiskEvictionInjector()
    config = {
        "db": "test",
        "table": "sf01_business_events",
        "reconciliation_table": "sf01_settlement_summary",
        "rollup_table": "sf01_region_audit_rollup",
        "exceptions_table": "sf01_reconciliation_exceptions",
        "row_count": 1000,
        "expected_amount_sum": 11511500,
        "expected_checksum": 38174471,
        "expected_region_count": 16,
        "region_codes": ("north", "south", "east", "west"),
        "insert_amount": 23023,
        "insert_crc": 424242,
        "insert_region_code": "north",
        "expected_exception_count": 2,
    }
    calls = []

    class BootstrapEnv:
        def execute_bootstrap_sql(self, sql):
            calls.append(sql)
            return json.dumps({"status": "success", "result": []})

    injector._configure(config)
    injector._seed_business_tables(BootstrapEnv())

    assert len(calls) == 13
    assert all("execute_sql" not in sql for sql in calls)
    create_statements = [sql for sql in calls if sql.startswith("CREATE TABLE")]
    assert len(create_statements) == 4
    assert sum("ENUM('open','closed')" in sql for sql in create_statements) == 3
    assert any("event_state ENUM('paid')" in sql for sql in calls)
    assert sum("status ENUM('open','closed')" in sql for sql in calls) == 3
    assert "REGIONS 16" in calls[-1]


def test_sf01_fault_scripts_keep_distinct_phase_and_cleanup_contracts():
    injector = TidbSystemFailureSf01PdMixedDiskEvictionInjector()
    calls = []
    deployment = SimpleNamespace(
        exec=lambda target, command: calls.append((target, command)),
    )

    injector._start_disk_fault(deployment, "pd/pd-1", term_epoch=1, role="follower")
    injector._start_maintenance_flush(deployment, "pd/pd-0")
    injector._stop_disk_fault(deployment, "pd/pd-1")
    injector._stop_maintenance_flush(deployment, "pd/pd-0")

    disk_script = calls[0][1][2]
    maintenance_script = calls[1][1][2]
    assert "conv=fdatasync" in disk_script
    assert "phase=storage_flush" in disk_script
    assert "term_epoch=1" in disk_script
    assert "deadline=" in maintenance_script
    assert "term_epoch=0" in maintenance_script
    assert injector._DISK_PID_FILE in calls[2][1][2]
    assert injector._MAINTENANCE_PID_FILE in calls[3][1][2]


def test_sf01_region_wait_targets_the_tidb_compose_service():
    injector = TidbSystemFailureSf01PdMixedDiskEvictionInjector()
    injector.db = "test"
    injector.table = "sf01_business_events"
    injector.expected_region_count = 16
    waits = []
    env = SimpleNamespace(
        deployment=SimpleNamespace(
            _wait=lambda label, check, timeout: waits.append((label, timeout)),
        ),
        execute_bootstrap_sql=lambda sql: json.dumps({"status": "success", "result": [[16]]}),
    )

    injector._wait_for_regions(env)

    assert waits == [("tidb/tidb-0", 180), ("pd", 180)]


def test_sf01_recover_after_partial_install_does_not_mask_original_error():
    injector = TidbSystemFailureSf01PdMixedDiskEvictionInjector()

    class UnexpectedDeploymentCall:
        def node_states(self):
            raise AssertionError("partial install recovery must not inspect an unset target")

    context = FaultLifecycleContext(
        run_id="sf01-partial-install",
        scenario_id="tidb_system_failure_sf01",
        case_id="pd_mixed_disk_eviction",
        case=object(),
        config={},
        env=SimpleNamespace(deployment=UnexpectedDeploymentCall()),
    )

    injector.recover(context)
