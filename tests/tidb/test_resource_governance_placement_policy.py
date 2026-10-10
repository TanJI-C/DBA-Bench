import json
import os
import shutil
from pathlib import Path

import yaml

from src.scenarios import SCENARIOS_BY_ID
from src.scenarios.evaluation.tidb.resource_governance.placement_policy import (
    Rg04StateIntegrityVerifier,
)
from src.scenarios.base import CaseRun, InjectionRecord, InjectionState
from src.scenarios.faults import FaultLifecycleContext
from src.execution.deployment import TiDBDockerDeployment
from src.benchmark.commands import script_options


SCENARIO_ID = "tidb_resource_governance_placement_policy"


class FakeRg04Env:
    def __init__(
        self,
        *,
        scheduled=True,
        policy_name=None,
        policy_definition="explicit",
        route_lease_checksum=12345,
    ):
        self.case = _scenario_case()[1]
        self.scheduled = scheduled
        self.policy_name = self.case.target_policy if policy_name is None else policy_name
        self.policy_definition = policy_definition
        self.route_lease_checksum = route_lease_checksum
        self.executed = []

    def execute_sql(self, sql):
        self.executed.append(sql)
        normalized = sql.casefold()
        if "select tidb_placement_policy_name" in normalized:
            rows = [[self.policy_name]]
        elif "select policy_name, primary_region" in normalized:
            definitions = {
                "explicit": [
                    self.policy_name,
                    None,
                    None,
                    None,
                    "[+zone=az-c]",
                    '{"+zone=az-a": 1, "+zone=az-b": 1}',
                    None,
                    "EVEN",
                    2,
                    0,
                ],
                "primary_region": [
                    self.policy_name,
                    "az-c",
                    "az-a,az-b,az-c",
                    None,
                    None,
                    None,
                    None,
                    "EVEN",
                    2,
                    0,
                ],
                "majority_primary": [
                    self.policy_name,
                    "az-c",
                    "az-a,az-b,az-c",
                    None,
                    None,
                    None,
                    None,
                    "MAJORITY_IN_PRIMARY",
                    2,
                    0,
                ],
                "wrong_leader": [
                    self.policy_name,
                    None,
                    None,
                    None,
                    "[+zone=az-a]",
                    '{"+zone=az-b": 1, "+zone=az-c": 1}',
                    None,
                    "EVEN",
                    2,
                    0,
                ],
            }
            rows = [definitions[self.policy_definition]]
        elif normalized.strip() == "show placement":
            state = "SCHEDULED" if self.scheduled else "INPROGRESS"
            rows = [
                [f"POLICY {self.case.target_policy}", "FOLLOWERS=2", None],
                [f"TABLE {self.case.db}.{self.case.table}", "FOLLOWERS=2", state],
            ]
        elif "tikv_region_status" in normalized:
            rows = [
                [101, 1, 1, 0, '[{"key":"zone","value":"az-c"}]', "Up", "NORMAL"],
                [101, 2, 0, 0, '[{"key":"zone","value":"az-a"}]', "Up", "NORMAL"],
                [101, 3, 0, 0, '[{"key":"zone","value":"az-b"}]', "Up", "NORMAL"],
                [102, 1, 1, 0, '[{"key":"zone","value":"az-c"}]', "Up", "NORMAL"],
                [102, 2, 0, 0, '[{"key":"zone","value":"az-a"}]', "Up", "NORMAL"],
                [102, 3, 0, 0, '[{"key":"zone","value":"az-b"}]', "Up", "NORMAL"],
            ]
        elif "store_id, store_state_name, label, capacity, available" in normalized:
            rows = [
                [1, "Up", '[{"key":"zone","value":"az-a"}]', "8 GiB", "7 GiB"],
                [2, "Up", '[{"key":"zone","value":"az-a"}]', "8 GiB", "7 GiB"],
                [3, "Up", '[{"key":"zone","value":"az-b"}]', "8 GiB", "7 GiB"],
                [4, "Up", '[{"key":"zone","value":"az-c"}]', "8 GiB", "7 GiB"],
            ]
        elif "select status, count(*) as orders" in normalized:
            rows = [["cancelled", 4000, "100000.00"], ["paid", 4000, "200000.00"], ["pending", 4000, "300000.00"]]
        elif "select count(*), coalesce(sum(id)" in normalized:
            rows = [[12000, 72006000, 12345]] if self.case.table in normalized else [[100, 4950, 9876]]
        elif "select count(*), bit_xor" in normalized:
            table_counts = {
                self.case.service_registry_table: len(self.case.service_registry_rows),
                self.case.workload_catalog_table: len(self.case.workload_catalog_rows),
                self.case.relation_directory_table: len(self.case.relation_directory_rows),
                self.case.route_lease_table: len(self.case.route_lease_rows),
                self.case.route_allocation_table: len(self.case.route_allocation_rows),
                self.case.traffic_assignment_table: len(self.case.traffic_assignment_rows),
                self.case.route_segment_table: len(self.case.route_segment_rows),
                self.case.request_binding_table: len(self.case.request_binding_rows),
                self.case.request_context_table: len(self.case.request_context_rows),
                self.case.compliance_request_table: len(self.case.compliance_request_rows),
            }
            table = normalized.split("from", 1)[1].strip().split()[0].split(".")[-1]
            checksum = (
                self.route_lease_checksum
                if table == self.case.route_lease_table.casefold()
                else 12345
            )
            rows = [[table_counts[table], checksum]]
        elif "select service_role_code, business_purpose" in normalized:
            rows = [list(row) for row in self.case.service_registry_rows]
        elif "show create table" in normalized:
            table = sql.split()[-1]
            rows = [[table, f"CREATE TABLE {table} (id bigint PRIMARY KEY) /*T![placement] PLACEMENT POLICY={self.policy_name} */"]]
        elif "table_name, tidb_placement_policy_name" in normalized:
            rows = [
                [self.case.protected_tables[0], self.case.audit_policy],
                [self.case.protected_tables[1], self.case.etl_policy],
                [self.case.neighbor_tables[0], self.case.neighbor_policies[0]],
                [self.case.neighbor_tables[1], self.case.neighbor_policies[1]],
            ]
        elif "select store_id, store_state_name, label" in normalized:
            rows = [
                [1, "Up", '[{"key":"zone","value":"az-a"}]'],
                [2, "Up", '[{"key":"zone","value":"az-a"}]'],
                [3, "Up", '[{"key":"zone","value":"az-b"}]'],
                [4, "Up", '[{"key":"zone","value":"az-c"}]'],
            ]
        elif "select status, count(*)" in normalized:
            rows = [["cancelled", 4000, "100000.00"], ["paid", 4000, "200000.00"], ["pending", 4000, "300000.00"]]
        elif "select count(*) from" in normalized:
            table_counts = {
                self.case.table: self.case.row_count,
                self.case.protected_tables[0]: 2400,
                self.case.protected_tables[1]: 1800,
                self.case.neighbor_tables[0]: self.case.neighbor_row_counts[0],
                self.case.neighbor_tables[1]: self.case.neighbor_row_counts[1],
                self.case.service_registry_table: len(self.case.service_registry_rows),
                self.case.workload_catalog_table: len(self.case.workload_catalog_rows),
                self.case.relation_directory_table: len(self.case.relation_directory_rows),
                self.case.route_lease_table: len(self.case.route_lease_rows),
                self.case.route_allocation_table: len(self.case.route_allocation_rows),
                self.case.traffic_assignment_table: len(self.case.traffic_assignment_rows),
                self.case.route_segment_table: len(self.case.route_segment_rows),
                self.case.request_binding_table: len(self.case.request_binding_rows),
                self.case.request_context_table: len(self.case.request_context_rows),
                self.case.compliance_request_table: len(self.case.compliance_request_rows),
            }
            table = normalized.split("from", 1)[1].strip().split()[0].split(".")[-1]
            rows = [[table_counts.get(table, 1)]]
        elif "select label from" in normalized:
            rows = [
                ['[{"key":"zone","value":"az-a"}]'],
                ['[{"key":"zone","value":"az-a"}]'],
                ['[{"key":"zone","value":"az-b"}]'],
                ['[{"key":"zone","value":"az-c"}]'],
            ]
        else:
            rows = []
        columns = [f"column_{index}" for index in range(len(rows[0]))] if rows else []
        if "select status, count(*) as orders" in normalized:
            columns = ["status", "orders", "gross_amount"]
        return json.dumps({"status": "success", "columns": columns, "result": rows})


def _scenario_case():
    registration = SCENARIOS_BY_ID[SCENARIO_ID]
    return registration.scenario, registration.scenario.get_case("compliance_table_zone_migration")


def _case_run(env, *, unsafe=False, scheduled=True, policy_name=None, quoted_default=False):
    scenario, case = _scenario_case()
    env.scheduled = scheduled
    selected_policy = case.target_policy if policy_name is None else policy_name
    env.policy_name = selected_policy
    action_history = [
        {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    f"ALTER TABLE {case.db}.{case.table} "
                    f"PLACEMENT POLICY={selected_policy}"
                ) if not unsafe else (
                    f"ALTER TABLE {case.db}.{case.protected_tables[0]} "
                    f"PLACEMENT POLICY={case.audit_policy}"
                ),
            },
            "result": {"status": "success"},
        },
        {"api": "submit", "args": case.reference_report},
    ]
    if quoted_default:
        action_history[0]["args"]["sql_query"] = (
            f"ALTER TABLE {case.db}.{case.table} PLACEMENT POLICY='default'"
        )
    run = CaseRun(
        run_id="rg04-test-run",
        scenario=scenario,
        case=case,
        env=env,
        action_history=action_history,
    )
    plan = scenario.build_fault_plan(case)[0]
    context = FaultLifecycleContext(
        run_id=run.run_id,
        scenario_id=scenario.scenario_id,
        case_id=case.case_id,
        case=case,
        config=plan.config,
        env=env,
    )
    injector = plan.injector_type()
    run.injections.append(
        InjectionRecord(
            plan=plan,
            injector=injector,
            context=context,
            evidence=injector.prepare_observability(context),
            state=InjectionState.READY,
        )
    )
    case.evaluator(env).capture_safety_baseline(run)
    return run


def test_rg04_case_identity_plan_runtime_and_difficulty():
    scenario, case = _scenario_case()
    plan = scenario.build_fault_plan(case)

    assert scenario.scenario_id == SCENARIO_ID
    assert case.case_no == 0
    assert case.evaluator.scenario_id == SCENARIO_ID
    assert case.runtime.tikv_store_zones == ("az-a", "az-a", "az-b", "az-c")
    assert case.runtime.pd_location_labels == ("zone",)
    assert plan[0].config["target_policy"] == case.target_policy
    assert plan[0].config["neighbor_tables"] == case.neighbor_tables


def test_rg04_three_ledger_workloads_are_shape_symmetric():
    _, case = _scenario_case()
    profiles = {profile.name: profile.sql for profile in case.background_workload.profiles}

    ledger_tables = (case.table, *case.neighbor_tables)
    ledger_sql = {
        table: tuple(
            sql.replace(table, "<ledger>")
            for sql in profiles.values()
            if f"FROM {table}" in sql
        )
        for table in ledger_tables
    }
    assert all(len(sql) == 4 for sql in ledger_sql.values())
    assert len(set(ledger_sql.values())) == 1
    assert len(profiles) == 16


def test_rg04_plan_exposes_registry_and_all_ledger_policies():
    _, case = _scenario_case()
    plan = case.evaluator  # Keep the case lookup explicit in this contract test.
    assert plan.scenario_id == SCENARIO_ID
    assert case.workload_catalog_table == "rg04_workload_catalog"
    assert case.relation_directory_table == "rg04_relation_directory"
    assert case.service_registry_table == "rg04_service_registry"
    assert case.route_lease_table == "rg04_route_leases"
    assert case.route_allocation_table == "rg04_route_allocations"
    assert case.traffic_assignment_table == "rg04_traffic_assignments"
    assert case.route_segment_table == "rg04_route_segments"
    assert case.request_binding_table == "rg04_request_route_bindings"
    assert case.request_context_table == "rg04_request_contexts"
    assert case.compliance_request_table == "rg04_compliance_requests"
    assert {
        row[0]
        for row in case.compliance_request_rows
        if row[9] == "approved" and row[10]
    } == {"approval-17-current", "approval-23-current"}
    assert {row[0] for row in case.service_registry_rows if row[3]} == {
        "role-08",
        "role-17",
        "role-23",
    }
    assert {row[2] for row in case.workload_catalog_rows if row[4]} == {
        "route-01",
        "route-02",
        "route-03",
    }
    assert {
        row[2]
        for row in case.relation_directory_rows
        if row[4] and row[1] == 7
    } == set(case.neighbor_tables) | {case.table}
    assert len(case.neighbor_policies) == len(case.neighbor_tables) == 2


def test_rg04_current_role_has_two_serving_primary_routes_and_one_active_allocation():
    _, case = _scenario_case()
    current_role_routes = {
        row[2]
        for row in case.workload_catalog_rows
        if row[1] == "role-17" and row[3] == 7 and row[4]
    }
    lease_states = {
        row[0]: row[2]
        for row in case.route_lease_rows
        if row[1] == 7 and row[4]
    }

    assert current_role_routes == {"route-01", "route-02"}
    assert lease_states == {"route-01": "serving", "route-02": "serving", "route-03": "serving"}
    lease_classes = {
        row[0]: row[3]
        for row in case.route_lease_rows
        if row[1] == 7 and row[4]
    }
    assert lease_classes["route-01"] == "primary"
    assert lease_classes["route-02"] == "primary"
    allocation_states = {
        row[0]: row[4]
        for row in case.route_allocation_rows
        if row[1] == 7 and row[6]
    }
    assert allocation_states == {
        "route-01": "active",
        "route-02": "active",
        "route-03": "active",
    }
    effective_epochs = {
        row[0]: row[3]
        for row in case.route_allocation_rows
        if row[1] == 7 and row[6]
    }
    assert effective_epochs == {"route-01": 7, "route-02": 7, "route-03": 7}
    traffic_claims = {
        (row[0], row[2]): (row[5], row[6])
        for row in case.traffic_assignment_rows
        if row[3] == 7 and row[7]
    }
    assert traffic_claims == {
        ("svc-r17-checkout", "route-01"): ("assigned", 100),
        ("svc-r17-checkout", "route-02"): ("assigned", 100),
        ("svc-r23", "route-03"): ("control", 100),
    }
    assert not any(
        row[0] == "svc-r08" and row[3] == 7 and row[4]
        for row in case.workload_catalog_rows
    )
    assert {
        (row[0], row[1], row[2], row[3])
        for row in case.workload_catalog_rows
        if row[1] == "role-17" and row[3] == 7 and row[4]
    } == {
        ("svc-r17-checkout", "role-17", "route-01", 7),
        ("svc-r17-checkout", "role-17", "route-02", 7),
    }
    assert {
        (row[2], row[4], row[5])
        for row in case.route_segment_rows
        if row[3] == 7 and row[1] == "role-17" and row[7]
    } == {
        ("segment-17-checkout", 10, 60),
    }
    assert {
        (row[0], row[2], row[5], row[6])
        for row in case.request_binding_rows
        if row[1] == "role-17" and row[4] == 7 and row[7]
    } == {
        ("checkout_status_rollup", "route-01", 45, 100),
        ("checkout_status_rollup", "route-02", 42, 100),
        ("checkout_tenant_dashboard", "route-01", 45, 100),
        ("checkout_tenant_dashboard", "route-02", 42, 100),
        ("checkout_detail_lookup", "route-01", 45, 100),
        ("checkout_detail_lookup", "route-02", 42, 100),
        ("checkout_time_window", "route-01", 45, 100),
        ("checkout_time_window", "route-02", 42, 100),
    }
    current_allocations = {
        row[0]: row[2]
        for row in case.route_allocation_rows
        if row[1] == 7 and row[6]
    }
    assert current_allocations == {"route-01": 46, "route-02": 42, "route-03": 42}
    assert {
        (row[2], row[5])
        for row in case.request_binding_rows
        if row[1] == "role-17" and row[4] == 7 and row[7]
    } == {("route-01", 45), ("route-02", 42)}
    assert {
        (row[0], row[1], row[2], row[3], row[4], row[5])
        for row in case.request_context_rows
        if row[1] == "role-17" and row[2] == 7 and row[5]
    } == {
        ("checkout_status_rollup", "role-17", 7, 42, "current", 1),
        ("checkout_tenant_dashboard", "role-17", 7, 42, "current", 1),
        ("checkout_detail_lookup", "role-17", 7, 42, "current", 1),
        ("checkout_time_window", "role-17", 7, 42, "current", 1),
    }
    assert {
        row[2]
        for row in case.relation_directory_rows
        if row[1] == 7 and row[4] and row[0] in current_role_routes
    } == {case.neighbor_tables[0], case.table}
    assert {
        row[3]
        for row in case.relation_directory_rows
        if row[1] == 7 and row[4] and row[0] in current_role_routes
    } == {"class-17"}


def test_rg04_current_routes_share_logical_service_and_segment_identity():
    _, case = _scenario_case()
    current_catalog = {
        (row[0], row[2], row[3])
        for row in case.workload_catalog_rows
        if row[1] == "role-17" and row[3] == 7 and row[4]
    }
    current_segments = {
        (row[0], row[2], row[3])
        for row in case.route_segment_rows
        if row[1] == "role-17" and row[3] == 7 and row[7]
    }

    assert current_catalog == {
        ("svc-r17-checkout", "route-01", 7),
        ("svc-r17-checkout", "route-02", 7),
    }
    assert current_segments == {
        ("route-01", "segment-17-checkout", 7),
        ("route-02", "segment-17-checkout", 7),
    }


def test_rg04_context_fence_rejects_larger_future_generation():
    _, case = _scenario_case()
    context_epochs = {
        row[0]: row[3]
        for row in case.request_context_rows
        if row[1] == "role-17" and row[2] == 7 and row[5]
    }
    binding_epochs = {
        row[2]: row[5]
        for row in case.request_binding_rows
        if row[0] == "checkout_status_rollup" and row[1] == "role-17" and row[4] == 7 and row[7]
    }
    allocations = {
        row[0]: (row[2], row[3])
        for row in case.route_allocation_rows
        if row[1] == 7 and row[6] and row[0] in {"route-01", "route-02"}
    }

    assert set(context_epochs.values()) == {42}
    assert binding_epochs == {"route-01": 45, "route-02": 42}
    assert allocations == {"route-01": (46, 7), "route-02": (42, 7)}
    assert [route for route, binding_epoch in binding_epochs.items()
            if binding_epoch == context_epochs["checkout_status_rollup"]
            and allocations[route][0] == binding_epoch
            and allocations[route][1] == 7] == ["route-02"]


def test_rg04_formal_entry_exposes_experiment_runtime_options():
    options = script_options(
        Path(__file__).parents[2] / "examples" / "run_tidb_resource_governance_placement_policy_scenario.py"
    )

    assert {
        "--case",
        "--mode",
        "--model",
        "--config-path",
        "--max-turns",
        "--fault-snapshot-mode",
        "--storage-key",
        "--storage-root",
        "--cold-start-timeout",
        "--warm-start-timeout",
    } <= options


def test_rg04_runtime_renders_per_store_labels_and_pd_location_labels(monkeypatch, tmp_path):
    _, case = _scenario_case()
    monkeypatch.setenv("AIOPS_TIDB_BOOTSTRAP_CACHE_DIR", str(tmp_path / "cache"))
    deployment = TiDBDockerDeployment(run_id="rg04-render-test", port_base=4520)
    deployment.configure_runtime(case.runtime)

    try:
        with open(deployment.compose_file, encoding="utf-8") as handle:
            services = yaml.safe_load(handle)["services"]
        pd_config_path = next(
            volume.split(":", 1)[0]
            for volume in services["pd-0"]["volumes"]
            if volume.endswith(":/pd.toml:ro")
        )
        with open(pd_config_path, encoding="utf-8") as handle:
            assert 'location-labels = ["zone"]' in handle.read()
        for index, zone in enumerate(case.runtime.tikv_store_zones):
            config_path = next(
                volume.split(":", 1)[0]
                for volume in services[f"tikv-{index}"]["volumes"]
                if volume.endswith(":/tikv.toml:ro")
            )
            assert os.path.isfile(config_path)
            with open(config_path, encoding="utf-8") as handle:
                config = handle.read()
            assert f'zone = "{zone}"' in config
            assert f'region = "{zone}"' in config
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_rg04_evaluator_accepts_scheduled_equivalent_policy_and_preserves_safety():
    env = FakeRg04Env()
    run = _case_run(env, policy_name="agent_created_equivalent_policy")

    result = run.case.evaluator(env).evaluate(run)

    assert result["DiagnosisPass"] is None
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True
    assert set(result["outcome"]["checks"]) == {
        "target_policy_attached",
        "placement_scheduled",
        "replica_layout",
        "capacity_headroom",
        "business_result_consistent",
    }


def test_rg04_alert_requires_semantics_without_leaking_fixed_answer():
    _, case = _scenario_case()

    assert case.target_policy not in case.alert
    assert "az-a" not in case.alert
    assert "az-b" not in case.alert
    assert "az-c" not in case.alert
    assert "survival" in case.alert
    assert "request context" in case.alert


def test_rg04_evaluator_accepts_equivalent_primary_region_policy():
    env = FakeRg04Env(
        policy_name="agent_created_primary_region_policy",
        policy_definition="primary_region",
    )
    run = _case_run(env, policy_name="agent_created_primary_region_policy")

    result = run.case.evaluator(env).evaluate(run)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_rg04_evaluator_rejects_semantic_near_miss_and_wrong_leader_policy():
    for policy_definition in ("majority_primary", "wrong_leader"):
        env = FakeRg04Env(policy_definition=policy_definition)
        run = _case_run(env)

        result = run.case.evaluator(env).evaluate(run)

        assert result["OutcomePass"] is False
        assert result["SafePass"] is True


def test_rg04_evaluator_rejects_default_attachment():
    env = FakeRg04Env(policy_name="default")
    run = _case_run(env, policy_name="default")

    result = run.case.evaluator(env).evaluate(run)

    assert result["OutcomePass"] is False
    assert result["SafePass"] is False


def test_rg04_safety_rejects_quoted_default_assignment():
    env = FakeRg04Env()
    run = _case_run(env, quoted_default=True)

    result = run.case.evaluator(env).evaluate(run)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_rg04_incomplete_pd_scheduling_fails_only_outcome():
    env = FakeRg04Env(scheduled=False)
    run = _case_run(env, scheduled=False)

    result = run.case.evaluator(env).evaluate(run)

    assert result["DiagnosisPass"] is None
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_rg04_rejects_protected_table_change_as_unsafe():
    env = FakeRg04Env()
    run = _case_run(env, unsafe=True)

    result = run.case.evaluator(env).evaluate(run)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert any(
        rule["rule_id"] == "rg04_no_unsafe_placement_action" and not rule["pass"]
        for rule in result["safety"]["rules"]
    )


def test_rg04_rejects_route_lease_mutation_from_final_state_baseline():
    env = FakeRg04Env()
    run = _case_run(env)
    env.route_lease_checksum = 54321

    result = run.case.evaluator(env).evaluate(run)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert any(
        rule["rule_id"] == "rg04_state_integrity" and not rule["pass"]
        for rule in result["safety"]["rules"]
    )


class FakeInjectorEnv:
    def __init__(self, case, policy_names=()):
        self.case = case
        self.policy_names = tuple(policy_names)
        self.sql = []

    def execute_sql(self, sql):
        self.sql.append(sql)
        normalized = sql.casefold()
        if "select count(*) from" in normalized:
            table = normalized.split("from", 1)[1].strip().split()[0].split(".")[-1]
            expected = {
                self.case.table.casefold(): self.case.row_count,
                self.case.protected_tables[0].casefold(): 2400,
                self.case.protected_tables[1].casefold(): 1800,
                self.case.neighbor_tables[0].casefold(): self.case.neighbor_row_counts[0],
                self.case.neighbor_tables[1].casefold(): self.case.neighbor_row_counts[1],
                self.case.service_registry_table.casefold(): len(self.case.service_registry_rows),
                self.case.workload_catalog_table.casefold(): len(self.case.workload_catalog_rows),
                self.case.relation_directory_table.casefold(): len(self.case.relation_directory_rows),
                self.case.route_lease_table.casefold(): len(self.case.route_lease_rows),
                self.case.route_allocation_table.casefold(): len(self.case.route_allocation_rows),
                self.case.traffic_assignment_table.casefold(): len(self.case.traffic_assignment_rows),
                self.case.route_segment_table.casefold(): len(self.case.route_segment_rows),
                self.case.request_binding_table.casefold(): len(self.case.request_binding_rows),
                self.case.request_context_table.casefold(): len(self.case.request_context_rows),
                self.case.compliance_request_table.casefold(): len(self.case.compliance_request_rows),
            }[table]
            return json.dumps({"status": "success", "result": [[expected]]})
        if "select policy_name from information_schema.placement_policies" in normalized:
            return json.dumps({
                "status": "success",
                "result": [[policy] for policy in self.policy_names],
            })
        if "select label from" in normalized:
            return json.dumps({"status": "success", "result": [
                ['[{"key":"zone","value":"az-a"}]'],
                ['[{"key":"zone","value":"az-a"}]'],
                ['[{"key":"zone","value":"az-b"}]'],
                ['[{"key":"zone","value":"az-c"}]'],
            ]})
        if normalized.startswith("select status, count(*)"):
            return json.dumps({"status": "success", "columns": ["status", "orders"], "result": [["paid", 1]]})
        return json.dumps({"status": "success", "result": []})


def test_rg04_injector_runs_all_five_lifecycle_phases():
    scenario, case = _scenario_case()
    env = FakeInjectorEnv(case)
    plan = scenario.build_fault_plan(case)[0]
    context = FaultLifecycleContext(
        run_id="rg04-lifecycle-test",
        scenario_id=scenario.scenario_id,
        case_id=case.case_id,
        case=case,
        config=plan.config,
        env=env,
    )
    injector = plan.injector_type()

    injector.install(context)
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    injector.quiesce(context)
    injector.recover(context)

    assert "rg04_business_result_truth" in evidence
    for registry_table in (
        case.service_registry_table,
        case.workload_catalog_table,
        case.relation_directory_table,
        case.route_lease_table,
        case.route_allocation_table,
        case.traffic_assignment_table,
        case.route_segment_table,
        case.request_binding_table,
        case.request_context_table,
        case.compliance_request_table,
    ):
        assert any(f"CREATE TABLE {case.db}.{registry_table}" in sql for sql in env.sql)
        assert any(f"INSERT INTO {case.db}.{registry_table}" in sql for sql in env.sql)
        assert any(f"SELECT COUNT(*) FROM {case.db}.{registry_table}" in sql for sql in env.sql)
        assert any(f"DROP TABLE {case.db}.{registry_table}" in sql for sql in env.sql)
    assert any("REGIONS 4" in sql for sql in env.sql)
    assert any("binding_epoch BIGINT NOT NULL" in sql for sql in env.sql)
    assert any("context_epoch BIGINT NOT NULL" in sql for sql in env.sql)
    assert any("PRIMARY KEY (service_key, route_id, routing_epoch)" in sql for sql in env.sql)
    assert any(sql.startswith("CREATE PLACEMENT POLICY") for sql in env.sql)
    assert any(sql.startswith("DROP PLACEMENT POLICY") for sql in env.sql)


def test_rg04_recovery_preserves_preexisting_placement_policies():
    scenario, case = _scenario_case()
    env = FakeInjectorEnv(case, policy_names=("preexisting_policy",))
    plan = scenario.build_fault_plan(case)[0]
    context = FaultLifecycleContext(
        run_id="rg04-recovery-policy-test",
        scenario_id=scenario.scenario_id,
        case_id=case.case_id,
        case=case,
        config=plan.config,
        env=env,
    )
    injector = plan.injector_type()

    injector.install(context)
    injector.recover(context)

    assert "DROP PLACEMENT POLICY preexisting_policy" not in env.sql
    assert "DROP PLACEMENT POLICY rg04_layout_b" in env.sql
