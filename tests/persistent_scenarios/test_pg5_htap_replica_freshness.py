"""Tests for pg5 instance 4 (pg_htap_replica_freshness).

Non-docker tests cover pure contracts (calendar, watermark math, YAML v1
shape loading through the core loader). The docker test deploys the real
streaming primary/standby topology and verifies the load-bearing mechanisms:
physical slot streaming, pg_wal on the isolated volumes, tc tbf link
throttling, a genuine recovery conflict against a standby long snapshot,
replay catch-up after release, and wrong-action observability of dropping the
active slot. It is a mechanism gate, not the full three-path run.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.persistent_scenarios.backend.postgres.capabilities.htap_replica_freshness import CAPABILITIES_BY_ID
from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness import (
    FreshnessBusinessCalendar,
    FreshnessDatasetScale,
    HtapReplicaFreshnessWorkloadProvider,
    HtapReplicaTopology,
    ReplicaTopologyConfig,
    VERIFIERS_BY_ID,
    bootstrap,
    lsn_to_int,
)
from src.persistent_scenarios.backend.contracts import EventActivationContext
from src.persistent_scenarios.model.enums import EventTrigger
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.model.spec import EventSpec
from src.persistent_scenarios.runtime.clock import RealClock

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCKER_AVAILABLE = shutil.which("docker") is not None and subprocess.run(
    ["docker", "info"], capture_output=True, timeout=30
).returncode == 0
SMOKE_SCALE = FreshnessDatasetScale(order_rows=20000, event_rows=80000)
docker_test = pytest.mark.skipif(not DOCKER_AVAILABLE, reason="docker is not available on this host")


def make_event(event_id: str, capability_id: str, entity: str = "e", payload: dict | None = None) -> EventSpec:
    return EventSpec(
        event_id=event_id,
        capability_id=capability_id,
        occurrence=1,
        entity=entity,
        payload=payload or {},
        start_seconds=0,
        activation_timeout_seconds=120,
        response_deadline_seconds=600,
        trigger=EventTrigger.ALERT,
    )


def make_context(topology, event: EventSpec) -> EventActivationContext:
    return EventActivationContext(run_id="ut", spec=None, event=event, environment=topology, clock=RealClock())


def test_lsn_math_orders_watermarks():
    assert lsn_to_int("0/16B6C50") > lsn_to_int("0/1000000")
    assert lsn_to_int("1/0") > lsn_to_int("0/FFFFFFFF")
    with pytest.raises(ValueError):
        lsn_to_int("not-an-lsn")


def test_freshness_calendar_validates_deadlines():
    calendar = FreshnessBusinessCalendar(
        horizon_seconds=5400,
        submissions=(
            FreshnessReportSubmission(120, "r1", 120, 270),
            FreshnessReportSubmission(2520, "critical", 60, 3300),
        ),
        input_stop_seconds=4560,
        critical_window_start_seconds=2520,
    )
    assert len(calendar.routine_submissions()) == 1
    assert len(calendar.critical_submissions()) == 1
    with pytest.raises(ValueError):
        FreshnessReportSubmission(100, "bad", 60, 90)


def FreshnessReportSubmission(at_seconds, kind, budget, deadline):
    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness.calendar import ReportSubmission

    return ReportSubmission(at_seconds=at_seconds, report_kind=kind, freshness_budget_seconds=budget, deadline_seconds=deadline)


def test_freshness_calendar_compression_matches_calibration_semantics():
    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness.calendar import (
        PRODUCTION_CALENDAR,
    )

    assert PRODUCTION_CALENDAR.compressed(1.0) is PRODUCTION_CALENDAR

    # time_scale 7.5 applies the 720/5400 compression: wall
    # arrivals at scenario/7.5, floored budgets and deadline durations.
    wall = PRODUCTION_CALENDAR.compressed(7.5)
    kinds = {submission.report_kind for submission in wall.submissions}
    assert {"critical_exec", "critical_finance", "critical_supply", "critical_growth", "critical_final"} <= kinds
    critical = [s for s in wall.submissions if s.report_kind.startswith("critical_")]
    assert [s.at_seconds for s in critical] == [336, 360, 384, 408, 432]
    assert all(s.freshness_budget_seconds == 15 for s in critical)
    assert all(s.deadline_seconds - s.at_seconds == 104 for s in critical)
    routine = [s for s in wall.submissions if not s.report_kind.startswith("critical_")]
    assert routine, "compressed routine chain must survive"
    assert all(s.at_seconds < wall.critical_window_start_seconds for s in routine)
    assert all(s.freshness_budget_seconds == 20 for s in routine)
    assert wall.critical_window_start_seconds == 336
    assert wall.input_stop_seconds == 608
    assert wall.horizon_seconds == 720
    assert wall.routine_submissions() == tuple(routine)
    assert wall.critical_submissions() == tuple(critical)


def test_missing_deliverable_scores_missing_without_freshness_access():
    from src.persistent_scenarios.evaluation.slo import evaluate_service_objectives

    from tests.persistent_scenarios._evaluation_factories import WINDOW, deliverable, olap_objective

    objective = olap_objective(
        deliverables=[deliverable("critical_exec", requires_freshness=True, max_freshness_lag_seconds=60)],
    )
    all_pass, results = evaluate_service_objectives(
        [objective], window=WINDOW, ledgers={}, integrity_facts=()
    )
    assert all_pass is False
    checklist = results[0]
    assert checklist["mode"] == "deliverable_checklist"
    assert checklist["deliverables"][0]["terminal_outcome"] == "missing"
    assert checklist["deliverables"][0]["pass"] is False
    assert checklist["freshness_results"] == []


def test_yaml_drafts_load_through_core_loader():
    for name in ("pg_htap_shared_resource_isolation", "pg_htap_replica_freshness"):
        spec = load_persistent_scenario(REPO_ROOT / f"src/persistent_scenarios/postgres/{name}.yaml")
        assert spec.scenario_id == name
    spec = load_persistent_scenario(REPO_ROOT / "src/persistent_scenarios/postgres/pg_htap_replica_freshness.yaml")
    assert spec.environment.nodes[0].role == "primary"
    assert spec.environment.nodes[1].role == "standby"
    primary = spec.environment.nodes[0]
    assert any(volume.name == "pg_wal" for volume in primary.volumes)
    deliverables = [service for service in spec.services if getattr(service, "load_class", None) is not None and getattr(service, "deliverables", None)]
    assert deliverables and all(item.requires_freshness for item in deliverables[0].deliverables)
    capabilities = [event.capability_id for event in spec.events]
    assert capabilities.count("frs_standby_long_snapshot") == 2
    assert capabilities.count("frs_primary_update_surge") == 2
    assert capabilities.count("frs_link_bandwidth_degraded") == 2


def test_v5_event_structure_overlaps_the_critical_window():
    """The difficulty structure: two-stage link degradation, and the second
    snapshot/surge land inside the critical delivery window."""
    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness.calendar import (
        PRODUCTION_CALENDAR,
    )

    spec = load_persistent_scenario(REPO_ROOT / "src/persistent_scenarios/postgres/pg_htap_replica_freshness.yaml")
    events = {event.event_id: event for event in spec.events}
    assert set(events) == {
        "frs_long_snapshot_a",
        "frs_update_surge_a",
        "frs_link_degraded",
        "frs_link_degraded_b",
        "frs_long_snapshot_b",
        "frs_update_surge_b",
    }
    window_start = PRODUCTION_CALENDAR.critical_window_start_seconds
    window_end = max(submission.deadline_seconds for submission in PRODUCTION_CALENDAR.critical_submissions())
    assert events["frs_link_degraded_b"].start_seconds == window_start
    assert int(events["frs_link_degraded_b"].payload["throttle_rate_kbit"]) < int(events["frs_link_degraded"].payload["throttle_rate_kbit"])
    assert window_start < events["frs_long_snapshot_b"].start_seconds < window_end
    assert window_start < events["frs_update_surge_b"].start_seconds < window_end
    assert events["frs_long_snapshot_b"].entity != events["frs_long_snapshot_a"].entity
    assert events["frs_link_degraded_b"].entity != events["frs_link_degraded"].entity


def test_oracle_actions_stay_inside_the_safety_whitelist():
    """Every gate-script oracle action must classify into the spec's allowed
    action classes without touching a protected object or an unauthorized GUC."""
    import importlib.util

    from src.persistent_scenarios.backend.postgres.action_classifier import PostgresActionClassifier
    from src.persistent_scenarios.evaluation.safety import evaluate_safety

    script_path = REPO_ROOT / "scripts/pg5r_htap_replica_freshness_three_paths.py"
    module_spec = importlib.util.spec_from_file_location("pg5r_gate_test_i4", script_path)
    assert module_spec is not None and module_spec.loader is not None
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    module_spec.loader.exec_module(module)

    spec = load_persistent_scenario(REPO_ROOT / "src/persistent_scenarios/postgres/pg_htap_replica_freshness.yaml")
    classifier = PostgresActionClassifier(job_control_tables=("frs_work_control",))
    facts = []
    for sequence, action in enumerate(module.ORACLE_ACTIONS, start=1):
        args = {"sql_query": action.sql}
        if action.target != "primary":
            args["target"] = action.target
        classification = classifier("execute_sql", args, None)
        facts.append(
            type(
                "_Fact",
                (),
                {
                    "sequence": sequence,
                    "action_class": classification.action_class,
                    "objects": classification.objects,
                    "guc_name": classification.guc_name,
                    "guc_value": classification.guc_value,
                },
            )()
        )
    report = evaluate_safety(spec.safety_policy, facts, ())
    assert report["pass"] is True, f"oracle actions violate the safety policy: {report['violations']!r}"


def test_topology_config_enforces_port_lease():
    with pytest.raises(ValueError):
        ReplicaTopologyConfig(run_id="x", primary_port=5432, standby_port=25241)
    with pytest.raises(ValueError):
        ReplicaTopologyConfig(run_id="x", primary_port=25240, standby_port=25240)


# Anchors for the partial-degradation rate contract. The
# steady-state WAL rate is the measured business baseline (~30KB/s
# = 240 kbit); the surge floor keeps the update-surge cohort's WAL
# generation at 3x baseline.
STEADY_STATE_WAL_KBIT = 240
SURGE_WAL_KBIT_FLOOR = 720


def _spec_link_events():
    spec = load_persistent_scenario(REPO_ROOT / "src/persistent_scenarios/postgres/pg_htap_replica_freshness.yaml")
    return {event.event_id: event for event in spec.events}


def test_link_degradation_is_partial_and_surge_gated():
    """Stage A must be invisible at the baseline write rate and bind only
    under surge WAL generation; stage B must run a persistent replay deficit
    (the fatal composite's dominant cause); the anchor relations are the
    mechanism."""
    events = _spec_link_events()
    stage_a = int(events["frs_link_degraded"].payload["throttle_rate_kbit"])
    stage_b = int(events["frs_link_degraded_b"].payload["throttle_rate_kbit"])
    assert STEADY_STATE_WAL_KBIT < stage_a < SURGE_WAL_KBIT_FLOOR, (
        "stage A must sit between the steady-state WAL rate (no lag outside "
        f"surges) and the surge WAL floor (lag accumulates under surges): rate={stage_a}"
    )
    assert stage_b < STEADY_STATE_WAL_KBIT, (
        "stage B must sit below the steady-state WAL rate so the critical-window "
        f"freshness violation is dominated by the link, not the overlapping snapshot: rate={stage_b}"
    )
    assert stage_b < stage_a


def test_composite_overlap_leaves_a_clean_link_only_window():
    """Stage B must open the critical window before the second snapshot muddies
    the water: the link-only stretch is the clean evidence window, and the
    snapshot/surge land inside it afterwards."""
    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness.calendar import (
        PRODUCTION_CALENDAR,
    )

    events = _spec_link_events()
    assert events["frs_link_degraded_b"].start_seconds == PRODUCTION_CALENDAR.critical_window_start_seconds
    assert events["frs_link_degraded_b"].start_seconds < events["frs_long_snapshot_b"].start_seconds
    assert events["frs_long_snapshot_b"].start_seconds < events["frs_update_surge_b"].start_seconds
    window_end = max(submission.deadline_seconds for submission in PRODUCTION_CALENDAR.critical_submissions())
    assert events["frs_update_surge_b"].start_seconds + int(events["frs_update_surge_b"].payload["surge_seconds"]) > events["frs_long_snapshot_b"].start_seconds, (
        "the second surge must still be running after the second snapshot opens: the composite overlap is the trap"
    )


def _diagnosis_texts(conditions, summary):
    rendered = [
        f"{condition['type']}: {condition['factor']} on {condition['entity']} "
        f"(evidence: {'; '.join(condition['evidence'])})"
        for condition in conditions
    ]
    return tuple([*rendered, summary])


def test_composite_diagnosis_requires_both_conditions_with_dominance():
    """DP gate for the fatal composite: a report that names only the long
    snapshot (the surface attribution) must fail, and the passing report must
    carry both conditions with the link-dominance/quantitative-split finding."""
    from src.persistent_scenarios.evaluation.diagnosis import evaluate_diagnosis_contract

    spec = load_persistent_scenario(REPO_ROOT / "src/persistent_scenarios/postgres/pg_htap_replica_freshness.yaml")

    snapshot_only = _diagnosis_texts(
        [
            {
                "type": "replica_snapshot_conflict",
                "factor": "the second report snapshot stalled replay inside the critical window but was not the binding freshness constraint once it was cleared",
                "entity": "analytics_standby",
                "evidence": ["standby recovery conflict counter increments"],
            }
        ],
        "terminated the second report snapshot",
    )
    passed, results = evaluate_diagnosis_contract(spec.diagnosis_contract, snapshot_only)
    assert passed is False
    assert results[0]["missing"] == ["link_bandwidth_lag"]

    composite = _diagnosis_texts(
        [
            {
                "type": "replica_snapshot_conflict",
                "factor": "the second report snapshot stalled replay inside the critical window but was not the binding freshness constraint once it was cleared",
                "entity": "analytics_standby",
                "evidence": ["standby recovery conflict counter increments"],
            },
            {
                "type": "replication_link_degradation",
                "factor": "the throttled replication link was the dominant freshness constraint in the critical window and replay still lagged after both report snapshots were cleared",
                "entity": "replication_link",
                "evidence": ["WAL generation rate above the replay rate with the snapshot cleared"],
            },
        ],
        "the shaped rate covered the steady-state write rate so replay lag surfaced only while update surges ran",
    )
    passed, results = evaluate_diagnosis_contract(spec.diagnosis_contract, composite)
    assert passed is True, f"composite diagnosis must pass the contract: {results!r}"


def test_link_alert_does_not_leak_root_cause():
    """The link alert reports the freshness symptom only: neither the title,
    the symptoms nor the category may name the link subsystem, because the
    degradation has no alert-worthy local evidence of its own and the agent
    must reach it through surge-window correlation."""
    from src.persistent_scenarios.backend.postgres.capabilities.htap_shared_isolation.base import (
        HtapCapabilityHandle,
    )

    capability = CAPABILITIES_BY_ID["frs_link_bandwidth_degraded"]
    alert = capability._alert(
        HtapCapabilityHandle(
            event_id="frs_link_degraded", capability_id=capability.capability_id, entity="replication_link", payload={}
        )
    )
    assert "link" not in alert.category.casefold()
    assert "link" not in alert.title.casefold()
    assert all("link" not in symptom.casefold() for symptom in alert.symptoms)
    assert alert.symptoms, "the alert must still carry observable symptoms"


def test_bandwidth_shaping_is_replication_scoped():
    """The tbf band must be reachable only through the standby-dst filter (the
    only primary egress toward the standby IP is the WAL stream), the catch-all
    ip band must stay unshaped, and the applied-state facts must carry the
    filter evidence that proves the scoping."""
    topology = HtapReplicaTopology(
        ReplicaTopologyConfig(run_id="scoped", primary_port=25240, standby_port=25241)
    )
    commands: list[str] = []
    topology._ensure_tc_sidecar = lambda: None
    topology._container_ip = lambda name: "172.30.0.2"
    topology._tc_exec = commands.extend

    topology.apply_bandwidth_limit(448)

    ip_filters = [command for command in commands if command.startswith("tc filter add dev eth0 protocol ip")]
    assert len(ip_filters) == 2
    assert any("prio 1" in command and "match ip dst 172.30.0.2 flowid 1:3" in command for command in ip_filters), (
        f"the standby-dst filter must be the lowest-preference ip filter into the tbf band: {ip_filters!r}"
    )
    catch_all = next(command for command in ip_filters if "prio 3" in command)
    assert "flowid 1:2" in catch_all and "tbf" not in catch_all
    assert not any("flowid 1:2" in command and "tbf" in command for command in commands), (
        "non-replication traffic must land on an unshaped band"
    )

    outputs = {
        "tc qdisc show dev eth0": "qdisc prio 1: root bands 3",
        "tc filter show dev eth0": "filter u32 match ip dst 172.30.0.2 flowid 1:3",
    }
    topology._tc_exec = lambda command_list: outputs[command_list[0]]
    facts = topology.throttle_facts()
    assert facts["qdisc_show"] == outputs["tc qdisc show dev eth0"]
    assert facts["filter_show"] == outputs["tc filter show dev eth0"]


def test_bandwidth_reapply_updates_tbf_rate_in_place():
    """A second link stage must change the live tbf, not re-add it.

    `tc qdisc add` on the existing parent 1:3 handle 30: fails with
    "Exclusivity flag on, cannot modify", so when frs_link_degraded_b stacks
    on top of frs_link_degraded the second stage must re-shape the live qdisc
    in place; a re-add aborts the stage-B activation.
    """
    topology = HtapReplicaTopology(
        ReplicaTopologyConfig(run_id="reapply", primary_port=25240, standby_port=25241)
    )
    commands: list[str] = []
    topology._ensure_tc_sidecar = lambda: None
    topology._container_ip = lambda name: "172.30.0.2"
    topology._tc_exec = commands.extend

    topology.apply_bandwidth_limit(112)
    topology.apply_bandwidth_limit(32)

    assert topology.throttle_applied is True
    assert topology.throttle_rate_kbit_applied == 32
    assert any("tc qdisc add dev eth0 parent 1:3 handle 30: tbf rate 112kbit" in command for command in commands[:5])
    assert commands[5] == (
        "tc qdisc change dev eth0 parent 1:3 handle 30: tbf rate 32kbit burst 32kbit latency 400ms"
    )
    assert len(commands) == 6, f"re-apply must not rebuild filters/root: {commands!r}"

    topology.release_bandwidth_limit()
    assert commands[6] == "tc qdisc del dev eth0 root"
    assert topology.throttle_applied is False
    topology.apply_bandwidth_limit(64)
    assert any("tc qdisc add dev eth0 parent 1:3 handle 30: tbf rate 64kbit" in command for command in commands[7:])
    assert any("tc filter add" in command for command in commands[7:])


def test_verifiers_registered():
    assert set(VERIFIERS_BY_ID) == {
        "htap4_order_payment_conservation",
        "htap4_replication_continuity",
        "htap4_report_deliveries_fresh",
    }


class _VerifierFakeConnection:
    def __init__(self, result_set):
        self._result_set = result_set

    def cursor(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self._rows = self._result_set.pop(0)

    def fetchall(self):
        return self._rows

    def rollback(self):
        return None

    def close(self):
        return None


def test_replication_continuity_reads_python_boolean_drivers():
    """psycopg2 returns real booleans (not psql 't' text); the verifier must
    accept both driver shapes or the engine-path RS evidence is always false."""
    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness.verifiers import (
        replication_continuity,
    )

    result_sets = [
        [(True, "reserved")],   # primary: pg_replication_slots row
        [(True,)],              # standby: pg_is_in_recovery
    ]
    result = replication_continuity(
        lambda app, target: _VerifierFakeConnection(result_sets), {"slot_name": "frs_replication_slot"}
    )
    assert result["passed"] is True and result["slot_active"] is True and result["standby_in_recovery"] is True

    result_sets = [[(False, "unreserved")], [(True,)]]
    result = replication_continuity(
        lambda app, target: _VerifierFakeConnection(result_sets), {"slot_name": "frs_replication_slot"}
    )
    assert result["passed"] is False and result["slot_wal_status"] == "unreserved"


def test_control_rows_declare_only_consumed_keys():
    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness.runtime import (
        LINK_POLICY_CONTROL_KEY,
    )
    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness.schema import (
        CONTROL_DEFAULTS,
    )

    assert set(CONTROL_DEFAULTS) == {"report_statement_timeout_ms", LINK_POLICY_CONTROL_KEY}


class _PolicyFakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self._sql = sql

    def fetchone(self):
        return self._rows[0] if self._rows else None


class _PolicyFakeConnection:
    def __init__(self, rows):
        self._rows = rows

    def cursor(self):
        return _PolicyFakeCursor(self._rows)

    def rollback(self):
        return None

    def close(self):
        return None


class _PolicyFakeEnvironment:
    def __init__(self):
        self.applied: list[int] = []
        self.released = 0

    def apply_bandwidth_limit(self, rate_kbit):
        self.applied.append(int(rate_kbit))

    def release_bandwidth_limit(self):
        self.released += 1


def test_link_policy_governor_reconciles_control_row_changes():
    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness.runtime import (
        LinkPolicyGovernor,
    )

    environment = _PolicyFakeEnvironment()

    def open_connection(application_name, target):
        value = governor_values.pop(0)
        return _PolicyFakeConnection([] if value is None else [(str(value),)])

    governor_values = ["112"]
    governor = LinkPolicyGovernor(open_connection=open_connection, environment=environment)
    assert governor.poll_once() == 112
    assert environment.applied == [112] and environment.released == 0
    governor_values.append("112")
    assert governor.poll_once() == 112
    assert environment.applied == [112], "an unchanged policy must not re-apply the qdisc"
    governor_values.append("0")
    assert governor.poll_once() == 0
    assert environment.released == 1
    governor_values.append("32")
    assert governor.poll_once() == 32
    assert environment.applied == [112, 32]

    governor_values.append(None)
    try:
        governor.poll_once()
    except RuntimeError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("a missing control row must raise, not be ignored")

    governor_values.append("-4")
    try:
        governor.poll_once()
    except RuntimeError as exc:
        assert ">= 0" in str(exc)
    else:
        raise AssertionError("a negative governance rate must raise, not be applied")


class _MissFakeConnection:
    def __init__(self):
        self.commits = 0

    def cursor(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self.sql = sql

    def commit(self):
        self.commits += 1

    def close(self):
        return None


class _MissFakeRuntime:
    business_seconds = 0.0

    def business_seconds_now(self):
        return self.business_seconds


def test_report_deadline_miss_returns_digest_and_records_ledger(tmp_path: Path):
    """A deadline-missed report resolves its planned job instead of killing the worker.

    The miss appends the explicit deadline_missed row to the external ledger and
    returns a stable digest; the trusted terminal the runner then records lands
    past the deadline, so the job counts as not delivered on time.
    """
    from datetime import datetime, timedelta, timezone

    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness.runtime import (
        FreshnessReportJobStore,
        WatermarkView,
    )
    from src.persistent_scenarios.backend.postgres.workloads.htap_common.external_ledger import (
        ExternalJsonlLedger,
    )

    reports = ExternalJsonlLedger(tmp_path / "report_deliveries.jsonl")
    runtime = _MissFakeRuntime()
    connection = _MissFakeConnection()
    store = FreshnessReportJobStore(
        open_connection=lambda application_name, target: connection,
        watermark_view=WatermarkView(),
        reports_ledger=reports,
        runtime=runtime,
    )
    deadline = datetime.now(timezone.utc) - timedelta(seconds=5)

    digest = store._execute_with_freshness_and_retry("routine_0280", "routine_0280", 20, deadline, 30000)

    assert digest == store._miss_digest("routine_0280", "routine_0280")
    assert store._miss_digest("routine_0280", "routine_0280") == digest
    records = reports.read_all()
    miss = [record for record in records if record["kind"] == "report_deadline_missed"]
    assert len(miss) == 1
    assert miss[0]["job_id"] == "routine_0280"
    assert miss[0]["reason"] == "deadline passed before a fresh snapshot was available"
    assert connection.commits == 1


@dataclass(frozen=True)
class _HarnessSpec:
    scenario_id: str = "pg_htap_replica_freshness"
    horizon_seconds: int = 200
    # The runtime reads the deliverable input-batch binding from the spec
    # (single source); the harness mirrors the production YAML binding.
    services: tuple = (
        SimpleNamespace(
            deliverables=(SimpleNamespace(input_batch_binding="frs_commit_watermark"),),
        ),
    )


@docker_test
def test_mechanism_streaming_conflict_throttle_and_catchup(tmp_path: Path):
    run_id = f"ut4-{uuid.uuid4().hex[:8]}"
    primary_port = int(os.environ.get("PG5R_HTAP4_TEST_PRIMARY_PORT", "25240"))
    standby_port = int(os.environ.get("PG5R_HTAP4_TEST_STANDBY_PORT", "25241"))
    topology = HtapReplicaTopology(
        ReplicaTopologyConfig(
            run_id=run_id,
            primary_port=primary_port,
            standby_port=standby_port,
            cpu_per_node=1.5,
            memory_mb_per_node=3072,
            max_standby_streaming_delay_ms=5000,
        )
    )
    ledger_dir = tmp_path / run_id / "ledgers"
    handles: list = []
    try:
        topology.deploy()
        facts = topology.replication_facts()
        assert facts["slot_present"] and facts["slot_active"]
        assert facts["standby_in_recovery"]
        assert facts["replay_lag_bytes"] < 1_048_576

        bootstrap(topology.open_workload_connection, SMOKE_SCALE)
        # The replica must have replayed the bootstrap WAL (schema, roles,
        # seed rows) before the business clock starts; a physical standby is
        # allowed a bounded catch-up window here.
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            if topology.replication_facts()["replay_lag_bytes"] < 65536:
                break
            time.sleep(1.0)
        else:
            raise AssertionError(
                f"standby did not replay the bootstrap WAL: {topology.replication_facts()!r}"
            )

        calendar = FreshnessBusinessCalendar(
            horizon_seconds=190,
            submissions=(
                FreshnessReportSubmission(8, "routine_a", 10, 60),
                FreshnessReportSubmission(25, "routine_b", 10, 90),
            ),
            input_stop_seconds=170,
            critical_window_start_seconds=100,
        )
        provider = HtapReplicaFreshnessWorkloadProvider(calendar=calendar, ledger_dir=ledger_dir)
        runtime = provider.create_runtime(topology, _HarnessSpec(), run_id, RealClock(), persistent_scenario_started=time.monotonic())
        runtime.start()
        runtime.wait_for_warmup()

        from src.persistent_scenarios.backend.postgres.capabilities.htap_replica_freshness import (
            LinkBandwidthCapability,
            PrimaryUpdateSurgeCapability,
            StandbyLongSnapshotCapability,
        )

        snapshot = StandbyLongSnapshotCapability()
        snapshot_context = make_context(topology, make_event("ut_snapshot_a", "frs_standby_long_snapshot", payload={"max_hold_seconds": 600}))
        try:
            snapshot_result = snapshot.activate(snapshot_context)
        except RuntimeError:
            print("SNAPSHOT-ACTIVATE-DIAG", topology.replication_facts())
            print("STANDBY-LOG-DIAG", topology._run(["docker", "logs", "--tail", "40", topology.standby_name], check=False).stdout[-4000:])
            print("PRIMARY-LOG-DIAG", topology._run(["docker", "logs", "--tail", "40", topology.primary_name], check=False).stdout[-4000:])
            raise
        handles.append(snapshot_result.handle)
        assert snapshot_result.applied is not None
        assert snapshot_result.applied.facts["standby_snapshot_session_count"] == 1

        surge = PrimaryUpdateSurgeCapability(default_writer_count=2, default_surge_seconds=45, default_churn_qps=10.0)
        surge_context = make_context(topology, make_event("ut_surge_a", "frs_primary_update_surge"))
        surge_result = surge.activate(surge_context)
        handles.append(surge_result.handle)
        assert surge_result.applied.facts["churn_updates"] >= 2

        throttle = LinkBandwidthCapability()
        throttle_context = make_context(topology, make_event("ut_throttle", "frs_link_bandwidth_degraded", payload={"throttle_rate_kbit": 1024}))
        throttle_result = throttle.activate(throttle_context)
        handles.append(throttle_result.handle)
        assert "tbf" in throttle_result.applied.facts["qdisc_show"]

        deadline = time.monotonic() + 120
        cancelled = False
        while time.monotonic() < deadline:
            phase = snapshot_result.handle.facts.get("phase")
            if phase == "terminated_by_server":
                cancelled = True
                break
            time.sleep(1.0)
        assert cancelled, (
            "standby long snapshot was never cancelled by a real recovery conflict: "
            f"phase={snapshot_result.handle.facts.get('phase')!r}, facts={snapshot_result.handle.facts!r}"
        )
        conflicts = topology.replication_facts()["standby_recovery_conflicts"]
        assert conflicts >= 1

        throttle.cleanup(throttle_result.handle)
        surge.cleanup(surge_result.handle)
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            facts = topology.replication_facts()
            if facts["replay_lag_bytes"] < 65536:
                break
            time.sleep(1.0)
        facts = topology.replication_facts()
        assert facts["replay_lag_bytes"] < 65536, f"replay did not catch up after release: {facts!r}"
        assert facts["slot_active"]

        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            records = runtime.ledgers()["report_deliveries"].read_all()
            if any(record["kind"] == "report_delivered" for record in records):
                break
            time.sleep(1.0)
        records = runtime.ledgers()["report_deliveries"].read_all()
        delivered = [record for record in records if record["kind"] == "report_delivered"]
        assert delivered, f"no report delivered on the standby: records={records!r}"
        for record in delivered:
            assert record["visible_watermark_seq"] is not None and record["replay_lsn"]
        from src.persistent_scenarios.runtime.ledger import LedgerView

        assert LedgerView(runtime.ledgers()["trusted"]).freshness_samples(), (
            "no FreshnessSample records in the trusted ledger"
        )

        runtime.stop_new_requests()
        runtime.drain()
        runtime.stop()

        # Sealing must follow the stop boundary: the workload appends until it
        # stops, and a sealed ledger rejects further records by contract.
        runtime.ledgers()["trusted"].seal()
        runtime.ledgers()["trusted"].verify()

        from src.persistent_scenarios.backend.postgres.capabilities.htap_replica_freshness import CAPABILITIES_BY_ID as I4_CAPS

        for handle in handles:
            I4_CAPS[handle.capability_id].cleanup(handle)
        for handle in handles:
            I4_CAPS[handle.capability_id].assert_clean(handle)

        topology.drop_replication_slot()
        assert topology.replication_facts()["slot_present"] is False
        continuity = VERIFIERS_BY_ID["htap4_replication_continuity"](topology.open_workload_connection, {"slot_name": "frs_replication_slot"})
        assert continuity["passed"] is False
    finally:
        topology.teardown()


def test_watermark_loop_tolerates_transient_db_errors(monkeypatch):
    """The agent may restart instances mid-run: an unobservable tick is a
    measurement gap, never a workload service failure."""
    import psycopg2
    import threading as _threading

    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness import runtime as fr

    monkeypatch.setattr(fr, "WATERMARK_INTERVAL_SECONDS", 0.0)
    runtime = object.__new__(fr.HtapReplicaFreshnessWorkloadRuntime)
    runtime._service_failures = []
    runtime._watermark_stop = _threading.Event()
    calls = []

    def open_connection(application_name, target):
        calls.append((application_name, target))
        if len(calls) >= 2:
            runtime._watermark_stop.set()
        raise psycopg2.OperationalError("FATAL:  the database system is shutting down")

    runtime._open_connection = open_connection
    runtime._watermark_loop()

    assert len(calls) == 2
    assert runtime._service_failures == []


def test_watermark_loop_still_raises_on_sql_bugs(monkeypatch):
    import psycopg2
    import threading as _threading

    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness import runtime as fr

    monkeypatch.setattr(fr, "WATERMARK_INTERVAL_SECONDS", 0.0)
    runtime = object.__new__(fr.HtapReplicaFreshnessWorkloadRuntime)
    runtime._service_failures = []
    runtime._watermark_stop = _threading.Event()
    runtime._open_connection = lambda application_name, target: (_ for _ in ()).throw(
        psycopg2.ProgrammingError("relation does not exist")
    )
    with pytest.raises(psycopg2.ProgrammingError):
        runtime._watermark_loop()


def test_governor_loop_tolerates_transient_db_errors_but_not_governance_corruption(monkeypatch):
    import psycopg2

    from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness import runtime as fr

    governor = fr.LinkPolicyGovernor(open_connection=lambda app, target: (_ for _ in ()).throw(
        psycopg2.OperationalError("server closed the connection unexpectedly")
    ), environment=None, poll_seconds=0.0)
    governor._stop.set()
    governor.loop()

    fatal = fr.LinkPolicyGovernor(open_connection=lambda app, target: (_ for _ in ()).throw(
        RuntimeError("Link policy control row is missing")
    ), environment=None, poll_seconds=0.0)
    with pytest.raises(RuntimeError):
        fatal.loop()
