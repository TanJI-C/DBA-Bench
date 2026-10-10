"""Model package tests: strict v2 spec contracts and YAML loading."""

from __future__ import annotations

from dataclasses import replace
import pathlib
import textwrap

import pytest
import yaml

from src.persistent_scenarios.model.enums import (
    SETTING_SCOPES_BY_SYSTEM,
    DatabaseSystem,
    EventTrigger,
    HtapMode,
    LoadClass,
    OlapMode,
    RequiredStateKind,
    SettingEffect,
    SettingScope,
)
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.model.spec import (
    compress_persistent_scenario_timeline,
    DeliverableContract,
    DiagnosisContract,
    DiagnosisIncidentSpec,
    ExpectedDiagnosisConditionSpec,
    GucEffectiveSpec,
    HtapObjective,
    NodeSpec,
    NodeVolume,
    OlapObjective,
    OltpObjective,
    PersistentScenarioResourceSpec,
    ProtectedObjectSpec,
    SafetyPolicyContract,
    validate_json_value,
)
from tests.persistent_scenarios.fakes import make_event, make_spec


def make_safety_policy() -> SafetyPolicyContract:
    return SafetyPolicyContract(
        allowed_action_classes=("read_only", "terminate_single_backend"),
        protected_objects=(ProtectedObjectSpec(name_pattern="public.ledger_*"),),
        authorized_guc_names=("work_mem",),
        guc_floor={"fsync": "on"},
    )


class TestServiceObjectives:
    def test_load_class_discriminated_shapes(self):
        spec = make_spec()
        service = spec.services[0]
        assert isinstance(service, OltpObjective)
        assert service.load_class is LoadClass.OLTP
        assert service.min_success_fraction == 0.9
        assert service.deadline_seconds == 8.0

    def test_old_fraction_and_union_names_are_gone(self):
        from src.persistent_scenarios.model import spec as spec_module

        for gone in ("LogicalTransactionServiceSpec", "JobDeliveryServiceSpec", "ReplicaFreshnessServiceSpec", "DeliveryDeadlineSpec"):
            assert not hasattr(spec_module, gone)

    def test_outage_fields_same_or_neither(self):
        OltpObjective("obj", "svc", 8.0, 0.9, outage_contract_seconds=30.0, outage_source="payment SLA")
        with pytest.raises(ValueError, match="together"):
            OltpObjective("obj", "svc", 8.0, 0.9, outage_contract_seconds=30.0)

    def test_olap_checklist_requires_deliverables_and_no_budget_fields(self):
        deliverables = (DeliverableContract("report_a", 40.0, requires_freshness=False),)
        OlapObjective("obj", "svc", OlapMode.DELIVERABLE_CHECKLIST, deliverables=deliverables)
        with pytest.raises(ValueError, match="requires deliverables"):
            OlapObjective("obj", "svc", OlapMode.DELIVERABLE_CHECKLIST)
        with pytest.raises(ValueError, match="per-deliverable deadlines"):
            OlapObjective("obj", "svc", OlapMode.DELIVERABLE_CHECKLIST, deliverables=deliverables, deadline_seconds=50.0)

    def test_olap_task_class_budget_requires_budget_and_evidence(self):
        OlapObjective(
            "obj", "svc", OlapMode.TASK_CLASS_BUDGET,
            deadline_seconds=30.0, min_on_time_correct_fraction=0.95,
            calibration_evidence_id="budget-2026-09",
        )
        with pytest.raises(ValueError, match="must not declare deliverables"):
            OlapObjective(
                "obj", "svc", OlapMode.TASK_CLASS_BUDGET,
                deliverables=(DeliverableContract("r", 40.0, False),),
                deadline_seconds=30.0, min_on_time_correct_fraction=0.95,
                calibration_evidence_id="budget-2026-09",
            )
        with pytest.raises(ValueError, match="calibration_evidence_id"):
            OlapObjective(
                "obj", "svc", OlapMode.TASK_CLASS_BUDGET,
                deadline_seconds=30.0, min_on_time_correct_fraction=0.95,
            )

    def test_deliverable_freshness_fields_paired(self):
        DeliverableContract("r", 40.0, requires_freshness=True, max_freshness_lag_seconds=5.0)
        with pytest.raises(ValueError, match="demands max_freshness_lag_seconds"):
            DeliverableContract("r", 40.0, requires_freshness=True)
        with pytest.raises(ValueError, match="requires requires_freshness=True"):
            DeliverableContract("r", 40.0, requires_freshness=False, max_freshness_lag_seconds=5.0)

    def test_htap_references_validated_against_spec(self):
        spec = make_spec()
        olap = OlapObjective(
            "obj-analyze", "exports", OlapMode.DELIVERABLE_CHECKLIST,
            deliverables=(DeliverableContract("export_1", 40.0, False),),
        )
        with pytest.raises(ValueError, match="transaction_objective_id must reference an oltp"):
            replace(spec, services=(olap, HtapObjective("htap", "both", HtapMode.REPLICA, "missing", "obj-analyze")))
        with pytest.raises(ValueError, match="analysis_objective_id must reference an olap"):
            replace(spec, services=(spec.services[0], HtapObjective("htap", "both", HtapMode.SHARED, "oltp_good_fraction", "missing")))
        combined = replace(
            spec,
            services=(spec.services[0], olap, HtapObjective("htap", "both", HtapMode.SHARED, "oltp_good_fraction", "obj-analyze")),
        )
        assert len(combined.services) == 3


class TestRequiredState:
    def test_four_kinds(self):
        assert {kind.value for kind in RequiredStateKind} == {
            "continuity", "deliverable_present", "guc_effective", "verifier",
        }
        assert RequiredStateKind.GUC_EFFECTIVE.value == "guc_effective"

    def test_guc_effective_uses_allowed_values_and_scope_name_rules(self):
        check = GucEffectiveSpec(
            "durable", "synchronous_commit", ("on", "remote_write"),
            SettingScope.ROLE, "app_writer", SettingEffect.NEW_CONNECTIONS, False,
        )
        assert check.allowed_values == ("on", "remote_write")
        assert check.scope in SETTING_SCOPES_BY_SYSTEM[DatabaseSystem.POSTGRESQL]
        with pytest.raises(ValueError, match="allowed_values"):
            GucEffectiveSpec("durable", "synchronous_commit", (), SettingScope.SERVER, None, SettingEffect.ALL_CONNECTIONS, False)
        with pytest.raises(ValueError, match="scope_name"):
            GucEffectiveSpec("durable", "synchronous_commit", ("on",), SettingScope.ROLE, None, SettingEffect.NEW_CONNECTIONS, False)
        with pytest.raises(ValueError, match="must not name"):
            GucEffectiveSpec("durable", "fsync", ("on",), SettingScope.SERVER, "ignored", SettingEffect.AFTER_RESTART, True)
        with pytest.raises(ValueError, match="must not name"):
            GucEffectiveSpec("global_var", "tidb_stmt_summary", ("on",), SettingScope.INSTANCE, "named", SettingEffect.ALL_CONNECTIONS, False)
        with pytest.raises(TypeError, match="effective_on"):
            GucEffectiveSpec("durable", "fsync", ("on",), SettingScope.SERVER, None, "immediately", True)

    def test_pg_pending_restart_semantics_pass_spec_validation(self):
        spec = replace(make_spec(), required_state=(
            GucEffectiveSpec(
                "wal_level_fix", "wal_level", ("replica",), SettingScope.SERVER, None,
                SettingEffect.AFTER_RESTART, True,
            ),
        ))
        check = spec.required_state[0]
        assert check.scope is SettingScope.SERVER
        assert check.effective_on is SettingEffect.AFTER_RESTART
        assert check.persist_required is True

    def test_scope_vocabulary_is_parameterized_by_system(self):
        spec = make_spec()
        tidb_state = (
            GucEffectiveSpec(
                "global_persist", "tidb_mem_quota_query", ("8GiB",), SettingScope.GLOBAL, None,
                SettingEffect.NEW_CONNECTIONS, True,
            ),
            GucEffectiveSpec(
                "instance_var", "tidb_stmt_summary_refresh_interval", ("1800",), SettingScope.INSTANCE, None,
                SettingEffect.ALL_CONNECTIONS, False,
            ),
            GucEffectiveSpec(
                "component_cfg", "max-concurrency", ("8",), SettingScope.COMPONENT, "tikv",
                SettingEffect.AFTER_RESTART, True,
            ),
        )
        tidb_spec = replace(spec, system=DatabaseSystem.TIDB, citation_tag="TB-PS-01", required_state=tidb_state)
        assert [item.scope for item in tidb_spec.required_state] == [
            SettingScope.GLOBAL, SettingScope.INSTANCE, SettingScope.COMPONENT,
        ]
        with pytest.raises(ValueError, match="system vocabulary"):
            replace(spec, required_state=(GucEffectiveSpec(
                "global_var", "tidb_mem_quota_query", ("8GiB",), SettingScope.GLOBAL, None,
                SettingEffect.NEW_CONNECTIONS, True,
            ),))
        with pytest.raises(ValueError, match="system vocabulary"):
            replace(tidb_spec, required_state=(GucEffectiveSpec(
                "server_guc", "work_mem", ("64MB",), SettingScope.SERVER, None,
                SettingEffect.NEW_CONNECTIONS, False,
            ),))


class TestSafetyPolicyAndDiagnosis:
    def test_safety_policy_shape(self):
        policy = make_safety_policy()
        assert policy.protected_objects[0].name_pattern == "public.ledger_*"
        assert policy.guc_floor == {"fsync": "on"}
        with pytest.raises(ValueError, match="allowed_action_classes"):
            SafetyPolicyContract(allowed_action_classes=())

    def test_diagnosis_contract_with_contradictions(self):
        contract = DiagnosisContract(incidents=(
            DiagnosisIncidentSpec(
                "lease_cascade",
                "A long transaction blocked order commits behind a lock queue.",
                conditions=(ExpectedDiagnosisConditionSpec(
                    "long_tx_lock_queue",
                    aliases=("A long-running transaction blocked commits behind a lock queue.",),
                    contradictions=("Network partition between app and database.",),
                ),),
            ),
        ))
        assert contract.incidents[0].conditions[0].contradictions
        assert DiagnosisContract(incidents=()).incidents == ()  # empty => DP = None
        with pytest.raises(ValueError, match="at least one condition"):
            DiagnosisContract(incidents=(DiagnosisIncidentSpec("i", "s", conditions=()),))


class TestEnvironmentNodes:
    def test_node_caps_and_volumes(self):
        from src.persistent_scenarios.model.spec import NodeVolume, PersistentScenarioEnvironmentSpec

        environment = PersistentScenarioEnvironmentSpec(
            workload="htap_replica", scale=1, base_image="demo:image",
            nodes=(
                NodeSpec("primary", "primary", PersistentScenarioResourceSpec(2, 512, 2.0, 512),
                         volumes=(NodeVolume("pg_wal", "/var/lib/postgresql/wal"),)),
                NodeSpec("standby", "standby", PersistentScenarioResourceSpec(2, 512, 2.0, 512),
                         docker_caps=("NET_ADMIN",)),
            ),
        )
        assert environment.nodes[0].volumes[0].mount_path == "/var/lib/postgresql/wal"
        assert environment.nodes[1].docker_caps == ("NET_ADMIN",)
        with pytest.raises(ValueError, match="docker_caps must be unique"):
            PersistentScenarioEnvironmentSpec(
                workload="w", scale=1, base_image="i",
                nodes=(NodeSpec("n", "primary", PersistentScenarioResourceSpec(1, 64, 1.0, 64), docker_caps=("NET_ADMIN", "NET_ADMIN")),),
            )


class TestSpecValidation:
    def test_same_capability_loads_twice_with_unique_event_ids(self):
        spec = make_spec()
        assert [event.capability_id for event in spec.events] == ["demo_capability", "demo_capability"]
        assert [event.occurrence for event in spec.events] == [1, 2]
        assert len({event.event_id for event in spec.events}) == 2

    def test_duplicate_event_id_rejected(self):
        with pytest.raises(ValueError, match="event IDs must be unique"):
            make_spec(events=(make_event("dup"), make_event("dup", entity="worker-2")))

    def test_services_are_independent_of_events(self):
        spec = make_spec()
        for event in spec.events:
            assert not [field for field in ("objective_id", "affected_flows") if hasattr(event, field)]

    def test_out_of_order_event_start_rejected(self):
        with pytest.raises(ValueError, match="non-decreasing"):
            make_spec(events=(make_event("late", start_seconds=6), make_event("early", start_seconds=4)))

    def test_event_starting_at_or_after_horizon_rejected(self):
        with pytest.raises(ValueError, match="before the horizon"):
            make_spec(events=(make_event("too_late", start_seconds=12),), horizon_seconds=12)

    def test_time_boundary_order_enforced(self):
        spec = make_spec()
        with pytest.raises(ValueError, match="input_stop <= agent_stop <= horizon"):
            replace(spec, input_stop_seconds=11, agent_stop_seconds=11, horizon_seconds=10)

    def test_event_at_or_after_input_stop_rejected(self):
        # default events start at t=2 and t=4; input_stop must stay beyond the last start
        with pytest.raises(ValueError, match="exceed the last event start"):
            replace(make_spec(), input_stop_seconds=4, agent_stop_seconds=11)

    def test_occurrence_must_be_positive(self):
        with pytest.raises(ValueError, match="occurrence"):
            make_event("bad", occurrence=0)

    def test_payload_must_be_json(self):
        with pytest.raises(TypeError, match="JSON value"):
            make_event("bad", payload={"worker": object()})
        with pytest.raises(ValueError, match="mapping keys"):
            make_event("bad", payload={1: "x"})

    def test_required_state_references_validated(self):
        spec = make_spec()
        from src.persistent_scenarios.model.spec import DeliverablePresentSpec

        with pytest.raises(ValueError, match="undeclared deliverable"):
            replace(spec, required_state=(DeliverablePresentSpec("chk", "ghost_report", {}),))
        with pytest.raises(ValueError, match="continuity must reference an oltp service"):
            replace(spec, required_state=(
                __import__("src.persistent_scenarios.model.spec", fromlist=["ContinuityStateSpec"]).ContinuityStateSpec(
                    "chk", "ghost_service", 30.0, 0.9
                ),
            ))

    def test_empty_services_rejected(self):
        with pytest.raises(ValueError, match="at least one service"):
            replace(make_spec(), services=())

    def test_safety_policy_required(self):
        with pytest.raises(TypeError, match="SafetyPolicyContract"):
            replace(make_spec(), safety_policy=None)

    def test_v1_protocol_rejected(self):
        with pytest.raises(ValueError, match="protocol_version"):
            replace(make_spec(), protocol_version="persistent-scenario-v1")

    def test_validate_json_value_rejects_non_finite(self):
        with pytest.raises(ValueError, match="finite"):
            validate_json_value("x", float("inf"))


class TestCompression:
    def test_scales_scoring_boundaries_and_keeps_warmup_and_deadlines(self):
        spec = make_spec(horizon_seconds=120, warmup_seconds=10)
        compressed = compress_persistent_scenario_timeline(spec, 4.0)
        assert compressed.warmup_seconds == 10
        assert compressed.horizon_seconds == 30
        assert compressed.events[0].start_seconds == 1  # 2 -> ceil(2/4)
        assert compressed.inspection_interval_seconds == 1
        assert compressed.input_stop_seconds <= compressed.horizon_seconds
        # Submission-relative business deadlines are workload-owned: unchanged.
        assert compressed.services[0].deadline_seconds == spec.services[0].deadline_seconds

    def test_time_scale_must_exceed_one(self):
        with pytest.raises(ValueError, match="time_scale"):
            compress_persistent_scenario_timeline(make_spec(), 1.0)


YAML_TEXT = """
protocol_version: persistent-scenario-v2
scenario_id: demo_scenario
family_id: demo
citation_tag: PG-PS-01
system: postgresql
mode: timeline
warmup_seconds: 10
input_stop_seconds: 60
agent_stop_seconds: 70
horizon_seconds: 90
inspection_interval_seconds: 15
calibration:
  status: development_provisional
  evidence_id: demo-dev
environment:
  workload: demo_profile
  scale: 1
  base_image: demo:image
  nodes:
  - node_id: primary
    role: primary
    resources: {worker_physical_cores: 2, worker_memory_mb: 2048, container_cpu_limit: 2.0, container_memory_mb: 2048}
  - node_id: standby
    role: standby
    docker_caps: [NET_ADMIN]
    volumes: [{name: pg_wal, mount_path: /var/lib/postgresql/wal}]
    resources: {worker_physical_cores: 2, worker_memory_mb: 2048, container_cpu_limit: 2.0, container_memory_mb: 2048}
services:
- objective_id: oltp_good_fraction
  load_class: oltp
  service_id: orders
  deadline_seconds: 8.0
  min_success_fraction: 0.9
- objective_id: report_delivery
  load_class: olap
  service_id: reports
  olap_mode: deliverable_checklist
  deliverables:
  - {deliverable_id: report_a, deadline_seconds: 40, requires_freshness: false}
  - {deliverable_id: report_b, deadline_seconds: 80, requires_freshness: true, max_freshness_lag_seconds: 5, input_batch_binding: batch_b}
safety_policy:
  allowed_action_classes: [read_only, terminate_single_backend, alter_guc, cancel_own_job]
  protected_objects: [{name_pattern: 'public.ledger_*'}]
  authorized_guc_names: [work_mem]
  guc_floor: {fsync: 'on', full_page_writes: 'on'}
integrity_checks:
- check_id: ledger_conservation
  verifier_id: sum_conservation
  params: {table: orders, column: amount}
required_state:
- check_id: order_continuity
  kind: continuity
  service_id: orders
  window_seconds: 30
  min_success_fraction: 0.9
- check_id: report_a_present
  kind: deliverable_present
  deliverable_id: report_a
  params: {deliverable_id: report_a}
- check_id: durable_commit
  kind: guc_effective
  guc_name: synchronous_commit
  allowed_values: ['on']
  scope: role
  scope_name: app_writer
  effective_on: new_connections
  persist_required: false
- check_id: backfill_complete
  kind: verifier
  verifier_id: backfill_completeness
  params: {table: orders_new, min_percent: 100}
diagnosis_contract:
  incidents:
  - incident_id: lease_cascade
    statement: A long-running transaction blocked order commits behind a lock queue.
    conditions:
    - condition_id: long_tx_lock_queue
      aliases: ['A long-running transaction blocked commits behind a lock queue.']
      contradictions: ['A network partition separated the app from the database.']
events:
- event_id: ev_a
  capability_id: long_transaction
  occurrence: 1
  entity: worker-3
  payload: {worker: 3, hold_seconds: 240}
  start_seconds: 5
  activation_timeout_seconds: 20
  response_deadline_seconds: 120
  trigger: alert
- event_id: ev_b
  capability_id: long_transaction
  occurrence: 2
  entity: worker-7
  payload: {worker: 7, hold_seconds: 180}
  start_seconds: 30
  activation_timeout_seconds: 20
  response_deadline_seconds: 120
  trigger: silent
"""


class TestLoader:
    @pytest.fixture()
    def spec_path(self, tmp_path: pathlib.Path) -> pathlib.Path:
        path = tmp_path / "demo.yaml"
        path.write_text(textwrap.dedent(YAML_TEXT), encoding="utf-8")
        return path

    def test_happy_path(self, spec_path):
        spec = load_persistent_scenario(spec_path)
        assert spec.scenario_id == "demo_scenario"
        assert [event.event_id for event in spec.events] == ["ev_a", "ev_b"]
        assert spec.events[1].capability_id == spec.events[0].capability_id == "long_transaction"
        assert spec.events[1].occurrence == 2
        oltp, olap = spec.services
        assert isinstance(oltp, OltpObjective) and isinstance(olap, OlapObjective)
        assert olap.olap_mode is OlapMode.DELIVERABLE_CHECKLIST
        assert olap.deliverables[1].requires_freshness is True
        assert spec.safety_policy.guc_floor == {"fsync": "on", "full_page_writes": "on"}
        kinds = [item.kind for item in spec.required_state]
        assert kinds == [
            RequiredStateKind.CONTINUITY,
            RequiredStateKind.DELIVERABLE_PRESENT,
            RequiredStateKind.GUC_EFFECTIVE,
            RequiredStateKind.VERIFIER,
        ]
        assert spec.required_state[2].allowed_values == ("on",)
        assert spec.required_state[2].effective_on is SettingEffect.NEW_CONNECTIONS
        assert spec.required_state[2].persist_required is False
        assert spec.diagnosis_contract.incidents[0].conditions[0].contradictions
        assert spec.environment.nodes[1].docker_caps == ("NET_ADMIN",)
        assert spec.environment.nodes[1].volumes[0].name == "pg_wal"

    def _load_mutated(self, tmp_path, mutate):
        data = yaml.safe_load(YAML_TEXT)
        mutate(data)
        path = tmp_path / "mutated.yaml"
        path.write_text(yaml.safe_dump(data), encoding="utf-8")
        return load_persistent_scenario(path)

    def test_unknown_field_rejected(self, tmp_path, spec_path):
        with pytest.raises(ValueError, match="unknown fields"):
            self._load_mutated(tmp_path, lambda data: data.update(scenario_case_pair="x"))

    def test_duplicate_event_id_rejected(self, tmp_path):
        def mutate(data):
            data["events"][1]["event_id"] = "ev_a"

        with pytest.raises(ValueError, match="unique"):
            self._load_mutated(tmp_path, mutate)

    def test_wrong_enum_rejected(self, tmp_path):
        def mutate(data):
            data["events"][0]["trigger"] = "cron"

        with pytest.raises(ValueError, match="EventTrigger"):
            self._load_mutated(tmp_path, mutate)

    def test_wrong_load_class_rejected(self, tmp_path):
        def mutate(data):
            data["services"][0]["load_class"] = "htap"

        # The loader rejects the oltp budget fields under the htap shape.
        with pytest.raises(ValueError, match="unknown fields"):
            self._load_mutated(tmp_path, mutate)

    def test_missing_safety_policy_rejected(self, tmp_path):
        def mutate(data):
            del data["safety_policy"]

        with pytest.raises(ValueError, match="safety_policy"):
            self._load_mutated(tmp_path, mutate)

    def test_legacy_pair_fields_rejected(self, tmp_path):
        def mutate(data):
            data["events"][0]["scenario_id"] = "old"
            data["events"][0]["case_id"] = "old_case"

        with pytest.raises(ValueError, match="unknown fields"):
            self._load_mutated(tmp_path, mutate)

    def test_v1_document_rejected(self, tmp_path):
        def mutate(data):
            data["protocol_version"] = "persistent-scenario-v1"

        with pytest.raises(ValueError, match="protocol_version"):
            self._load_mutated(tmp_path, mutate)

    def test_htap_reference_to_missing_objective_rejected(self, tmp_path):
        def mutate(data):
            data["services"].append({
                "objective_id": "htap_obj",
                "load_class": "htap",
                "service_id": "both",
                "htap_mode": "replica",
                "transaction_objective_id": "missing",
                "analysis_objective_id": "report_delivery",
            })

        with pytest.raises(ValueError, match="transaction_objective_id"):
            self._load_mutated(tmp_path, mutate)

    def test_legacy_restart_required_field_rejected(self, tmp_path):
        def mutate(data):
            data["required_state"][2]["restart_required"] = False

        with pytest.raises(ValueError, match="unknown fields"):
            self._load_mutated(tmp_path, mutate)

    def test_out_of_system_scope_rejected(self, tmp_path):
        def mutate(data):
            item = data["required_state"][2]
            item["scope"] = "global"
            del item["scope_name"]

        with pytest.raises(ValueError, match="system vocabulary"):
            self._load_mutated(tmp_path, mutate)

    def test_pg_pending_restart_shape_loads(self, tmp_path):
        def mutate(data):
            data["required_state"][2] = {
                "check_id": "wal_level_fix",
                "kind": "guc_effective",
                "guc_name": "wal_level",
                "allowed_values": ["replica"],
                "scope": "server",
                "effective_on": "after_restart",
                "persist_required": True,
            }

        spec = self._load_mutated(tmp_path, mutate)
        check = spec.required_state[2]
        assert check.effective_on is SettingEffect.AFTER_RESTART
        assert check.persist_required is True

    def test_tidb_global_persist_shape_loads(self, tmp_path):
        def mutate(data):
            data["system"] = "tidb"
            data["citation_tag"] = "TB-PS-01"
            data["required_state"][2] = {
                "check_id": "global_persist",
                "kind": "guc_effective",
                "guc_name": "tidb_mem_quota_query",
                "allowed_values": ["8GiB"],
                "scope": "global",
                "effective_on": "new_connections",
                "persist_required": True,
            }

        spec = self._load_mutated(tmp_path, mutate)
        assert spec.system is DatabaseSystem.TIDB
        check = spec.required_state[2]
        assert check.scope is SettingScope.GLOBAL
        assert check.effective_on is SettingEffect.NEW_CONNECTIONS
        assert check.persist_required is True
