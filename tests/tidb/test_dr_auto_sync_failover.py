from src.scenarios.evaluation.tidb.business_change.dr_auto_sync_errors import K09FinalStateUnavailable
import json
from types import SimpleNamespace
from pathlib import Path

import pytest

from src.scenarios.tidb import TidbBusinessChangeDrAutoSyncFailoverScenario
from src.scenarios.tidb.business_change.dr_auto_sync_failover import (
    TidbBusinessChangeDrAutoSyncPlannedInjector,
    TidbBusinessChangeDrAutoSyncUnplannedInjector,
)
from src.scenarios.evaluation.tidb.business_change.dr_auto_sync_failover import (
    K09RegionIntegrityVerifier,
    K09UnplannedRecoveryVerifier,
)
from src.scenarios.tidb.business_change.runtime.dr_auto_sync_control import (
    TiDBDrAutoSyncControl,
)


SCENARIO = TidbBusinessChangeDrAutoSyncFailoverScenario()


def _bundle(rules):
    return [{
        "group_id": "pd",
        "group_index": 0,
        "group_override": False,
        "rules": rules,
    }]


def _rule(rule_id, role, count, zone):
    return {
        "group_id": "pd",
        "id": rule_id,
        "start_key": "",
        "end_key": "",
        "role": role,
        "count": count,
        "label_constraints": [{"key": "zone", "op": "in", "values": [zone]}],
        "location_labels": ["zone"],
    }


class FakeDeployment:
    run_id = "k09-test"

    def __init__(self):
        self.bundle = _bundle([{"group_id": "pd", "id": "default", "role": "voter", "count": 3, "label_constraints": [], "location_labels": []}])
        self.mode = "majority"
        self.recovery = ""
        self.remove_tombstones = False
        self.services = {
            "tidb/tidb-0": {"running": True},
            "tidb/tidb-1": {"running": True},
        }
        self.stores = [
            {"id": index + 1, "address": f"tikv-{index}:20160", "state_name": "Up", "labels": [{"key": "zone", "value": zone}]}
            for index, zone in enumerate(("primary", "primary", "primary", "dr", "dr", "dr"))
        ]

    def pd_ctl_command(self, *args):
        if args == ("config", "show", "all"):
            return json.dumps({"replication": {"enable-placement-rules": "false"}, "replication-mode": "majority"})
        if args[:3] == ("config", "placement-rules", "enable"):
            return "Success!"
        if args[:3] == ("config", "placement-rules", "disable"):
            return "Success!"
        if args[:3] == ("config", "set", "replication-mode"):
            if args[3] == "majority":
                self.mode = "majority"
            else:
                self.mode = "dr-auto-sync"
            if len(args) >= 6 and args[4] == "dr-auto-sync" and args[5] == "primary":
                self.primary = args[6]
            return "Success!"
        if args[:3] == ("unsafe", "remove-failed-stores", "show"):
            return self.recovery
        if args[:2] == ("unsafe", "remove-failed-stores"):
            self.recovery = "Unsafe recovery finished"
            self.remove_tombstones = True
            for store in self.stores[:3]:
                store["state_name"] = "Tombstone"
            self.bundle = _bundle([_rule("recovered-primary-voters", "voter", 3, "dr")])
            self.mode = "dr-auto-sync"
            return "Success!"
        raise AssertionError(f"unexpected pd_ctl args={args!r}")

    def pd_ctl_command_with_json(self, args, payload, *, container_path):
        self.bundle = payload
        return "Success!"

    def exec(self, target, command):
        assert target == "pd/pd-0"
        assert command[:2] == ["sh", "-ceu"]
        return json.dumps(self.bundle)

    def pd_request(self, method, path):
        if path == "/pd/api/v1/replication_mode/status":
            return {"mode": self.mode, "dr-auto-sync": {"state": "sync"}}
        if path == "/pd/api/v1/stores":
            stores = [
                store
                for store in self.stores
                if not self.remove_tombstones or store["state_name"] != "Tombstone"
            ]
            return {"stores": [{"store": store} for store in stores]}
        if path.startswith("/pd/api/v1/store/"):
            store_id = int(path.rsplit("/", 1)[1])
            store = next(store for store in self.stores if int(store["id"]) == store_id)
            return {"store": store, "status": {"leader_count": 0, "region_count": 0}}
        raise AssertionError(f"unexpected PD path={path!r}")

    def node_states(self):
        return self.services

    def current_pd_leader(self):
        return "pd-0"


class FakeEnv:
    def __init__(self, case, deployment):
        self.case = case
        self.deployment = deployment
        self.canary_writes = 0
        self.router = {
            "policy": "round_robin",
            "draining": [],
            "active_connections": {
                case.primary_endpoint: 0,
                case.dr_endpoint: 0,
            },
        }

    def connection_router_statuses(self):
        return {"k09-business-router": self.router}

    def drain_connection_routers(self, target):
        self.router["draining"] = [target]
        return self.connection_router_statuses()

    def invalidate_workload_connections(self):
        return None

    def reset_connection_routers(self):
        self.router["draining"] = []

    def execute_sql_trusted(self, sql, target=None):
        if sql.startswith("INSERT INTO"):
            self.canary_writes += 1
            return json.dumps({"status": "success", "result": []})
        if "endpoint_fence_canaries" in sql:
            return json.dumps({"status": "success", "result": [["tidb/tidb-1", 1]]})
        if sql.startswith("ADMIN CHECK TABLE"):
            return json.dumps({"status": "success", "result": []})
        if "COUNT(*), COALESCE(SUM(amount_cents)" in sql:
            if "LIKE 'seed-%'" in sql:
                return json.dumps({"status": "success", "result": [[3, 300, 7]]})
            return json.dumps({"status": "success", "result": [[3, 300, 7, 1, 3]]})
        return json.dumps({
            "status": "success",
            "result": [["k09_dr", "ledger_markers", "INTEGRITY_OVER_LABEL", 1]],
        })


def test_k09_registers_two_cases_and_separate_injectors():
    assert [case.case_id for case in SCENARIO.cases] == [
        "planned_dual_dc_failover",
        "unplanned_dual_dc_failover",
    ]
    assert SCENARIO.build_fault_plan(SCENARIO.cases[0])[0].injector_type is TidbBusinessChangeDrAutoSyncPlannedInjector
    assert SCENARIO.build_fault_plan(SCENARIO.cases[1])[0].injector_type is TidbBusinessChangeDrAutoSyncUnplannedInjector


def test_planned_transition_requires_fence_and_waits_for_terminal_state():
    case = SCENARIO.get_case("planned_dual_dc_failover")
    deployment = FakeDeployment()
    env = FakeEnv(case, deployment)
    control = TiDBDrAutoSyncControl(env, case)
    control.install()

    with pytest.raises(RuntimeError, match="requires the current primary endpoint to be drained"):
        control.transition("planned")

    env.drain_connection_routers(case.primary_endpoint)
    accepted = control.transition("planned")
    assert accepted["status"] == "accepted"
    terminal = control.wait("planned", timeout_seconds=1)
    assert terminal["status"] == "terminal"
    assert terminal["snapshot"]["placement"][0]["rules"][0]["id"] == "primary-voters"
    assert env.canary_writes == 0


def test_region_unknown_is_not_a_terminal_replication_state():
    assert TiDBDrAutoSyncControl._region_replication_terminal(
        [["k09_dr", "ledger_markers", "INTEGRITY_OVER_LABEL", 1]]
    )
    assert TiDBDrAutoSyncControl._region_replication_terminal(
        [["k09_dr", "ledger_markers", "SIMPLE_MAJORITY", 1]]
    )
    assert not TiDBDrAutoSyncControl._region_replication_terminal(
        [["k09_dr", "ledger_markers", "UNKNOWN", 1]]
    )


def test_observability_uses_business_truth_sealed_before_fault():
    case = SCENARIO.get_case("unplanned_dual_dc_failover")
    deployment = FakeDeployment()
    env = FakeEnv(case, deployment)
    control = TiDBDrAutoSyncControl(env, case)
    control.install()
    control.seal_business_truth()
    observation = control.prepare_observability()
    assert observation["k09_initial_business"]["seed"] == {
        "count": 3,
        "amount_sum": 300,
        "crc": 7,
    }


def test_unplanned_transition_requires_exact_failed_primary_store_set():
    case = SCENARIO.get_case("unplanned_dual_dc_failover")
    deployment = FakeDeployment()
    deployment.services[case.primary_endpoint]["running"] = False
    for store in deployment.stores[:3]:
        store["state_name"] = "Down"
    env = FakeEnv(case, deployment)
    control = TiDBDrAutoSyncControl(env, case)
    control.install()
    env.drain_connection_routers(case.primary_endpoint)

    with pytest.raises(ValueError, match="exactly match all primary-AZ Stores"):
        control.transition("unplanned", failed_store_ids=[1, 2])

    accepted = control.transition("unplanned", failed_store_ids=[1, 2, 3], timeout_seconds=30)
    assert accepted["status"] == "accepted"
    terminal = control.wait("unplanned", timeout_seconds=1)
    assert terminal["status"] == "terminal"
    assert all(
        store["state_name"] == "Tombstone"
        for store in terminal["snapshot"]["stores"][:3]
    )


def test_region_endpoint_error_is_an_explicit_outcome_failure():
    case = SCENARIO.get_case("unplanned_dual_dc_failover")
    deployment = FakeDeployment()
    env = FakeEnv(case, deployment)

    def unavailable(sql, target=None):
        return json.dumps({
            "status": "error",
            "error": "TiDB SQL failed: endpoint unavailable",
        })

    env.execute_sql_trusted = unavailable
    context = SimpleNamespace(case_run=SimpleNamespace(case=case, env=env))

    check = K09RegionIntegrityVerifier().verify(context)

    assert check.passed is False
    assert check.actual["status"] == "error"
    assert "OutcomePass is false" in check.evidence[-1]


def test_unplanned_snapshot_endpoint_error_is_an_explicit_outcome_failure():
    case = SCENARIO.get_case("unplanned_dual_dc_failover")
    error = K09FinalStateUnavailable(
        "K09 Region replication status",
        {"status": "error", "error": "endpoint unavailable"},
    )

    class UnavailableControl:
        def snapshot(self):
            raise error

    class UnavailableEnv:
        def dr_replication_control(self):
            return UnavailableControl()

    context = SimpleNamespace(case_run=SimpleNamespace(case=case, env=UnavailableEnv()))

    check = K09UnplannedRecoveryVerifier().verify(context)

    assert check.passed is False
    assert check.actual["status"] == "unavailable"
    assert check.actual["response"]["error"] == "endpoint unavailable"


def test_k09_cases_record_decision_changing_knowledge_hops():
    for case in SCENARIO.cases:
        assert len(case.knowledge_hops) >= 3
        for hop in case.knowledge_hops:
            assert hop.knowledge_question
            assert hop.expected_concept
            assert hop.version_scope == "TiDB 8.1 self-managed" or "TiDB 8.1" in hop.version_scope
            assert hop.required_environment_binding
            assert hop.decision_changed
            assert hop.counterfactual
            assert hop.allowed_source_scope
            assert hop.visible_evidence


def test_k09_entry_uses_only_the_unified_search_knowledge_tool():
    entry = Path(__file__).parents[2] / "examples" / "run_tidb_business_change_dr_auto_sync_failover_scenario.py"
    source = entry.resolve().read_text(encoding="utf-8")
    assert "AIOPS_TIDB_KB_BACKEND" not in source
    assert "tidb81_k09_extended" not in source
    assert '_action("search_knowledge"' in source
