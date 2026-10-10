"""Tests for pg5 instance 3 (pg_htap_shared_resource_isolation).

Non-docker tests cover the pure contracts (calendar, ledger, core capability
protocol conformance, YAML draft shape). The docker tests are the
short-container mechanism verification: stuck-snapshot xmin hold, hotspot
churn, control-table governance of the analysis scheduler, watermark
bookkeeping and export checkpoint delivery on a real PostgreSQL instance.
They are mechanism gates, not the full three-path run.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

from src.persistent_scenarios.backend.contracts import EventActivationContext, PersistentScenarioEventCapability
from src.persistent_scenarios.backend.postgres.capabilities.htap_shared_isolation import CAPABILITIES_BY_ID
from src.persistent_scenarios.backend.postgres.capabilities.htap_shared_isolation import stuck_export_snapshot
from src.persistent_scenarios.backend.postgres.gate_scripts import gate_script
from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation import (
    HtapDatasetScale,
    HtapSharedIsolationWorkloadProvider,
    VERIFIERS_BY_ID,
    bootstrap,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation.calendar import (
    AnalysisSubmission,
    HtapBusinessCalendar,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation.single_node import (
    SingleNodePostgres,
    SingleNodePostgresConfig,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_common.external_ledger import ExternalJsonlLedger
from src.persistent_scenarios.evaluation.diagnosis import (
    collect_report_diagnosis_texts,
    evaluate_diagnosis_contract,
)
from src.persistent_scenarios.model.enums import EventTrigger
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.model.spec import EventSpec
from src.persistent_scenarios.runtime.clock import RealClock

REPO_ROOT = Path(__file__).resolve().parents[2]
I3_YAML = REPO_ROOT / "src/persistent_scenarios/postgres/pg_htap_shared_resource_isolation.yaml"
DOCKER_AVAILABLE = shutil.which("docker") is not None and subprocess.run(
    ["docker", "info"], capture_output=True, timeout=30
).returncode == 0
SMOKE_SCALE = HtapDatasetScale(order_rows=40000, line_multiplier=3, sku_rows=500, hot_skus=24)
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


def make_context(node, event: EventSpec) -> EventActivationContext:
    return EventActivationContext(run_id="ut", spec=None, event=event, environment=node, clock=RealClock())


def test_calendar_validates_business_windows():
    submission = AnalysisSubmission(at_seconds=600, tenant="t", scan_count=1, scan_span_lines=10, submit_export=True, export_rows_per_second=100)
    calendar = HtapBusinessCalendar(
        horizon_seconds=4500,
        submissions=(submission,),
        input_stop_seconds=3720,
        analysis_deadline_seconds=4320,
        export_deadline_seconds=4200,
        export_watermark_lag_seconds=180,
    )
    assert calendar.input_stop_seconds < calendar.horizon_seconds
    with pytest.raises(ValueError):
        HtapBusinessCalendar(
            horizon_seconds=1000,
            submissions=(submission,),
            input_stop_seconds=1200,
            analysis_deadline_seconds=1300,
            export_deadline_seconds=1400,
            export_watermark_lag_seconds=10,
        )


def test_external_ledger_appends_and_detects_sequence_gaps(tmp_path: Path):
    ledger = ExternalJsonlLedger(tmp_path / "orders.jsonl")
    first = ledger.append("order_request", request_id="r1", outcome="success")
    second = ledger.append("order_request", request_id="r2", outcome="timeout")
    assert first["seq"] == 1 and second["seq"] == 2
    records = ledger.read_all()
    assert [record["request_id"] for record in records] == ["r1", "r2"]
    with open(tmp_path / "orders.jsonl", "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"seq": 9, "kind": "tampered"}) + "\n")
    with pytest.raises(ValueError):
        ledger.read_all()


def test_capabilities_satisfy_core_protocol_and_declare_resources():
    for capability_id, capability in CAPABILITIES_BY_ID.items():
        assert isinstance(capability, PersistentScenarioEventCapability), capability_id
        declaration = capability.declaration(make_event("e1", capability_id))
        assert declaration.capability_id == capability_id
        assert declaration.resources
        assert declaration.max_activation_seconds > 0


def test_verifiers_registered_for_required_state_and_integrity():
    assert set(VERIFIERS_BY_ID) == {
        "htap3_order_payment_conservation",
        "htap3_inventory_non_negative",
        "htap3_export_checkpoints_complete",
        "htap3_analysis_role_timeout_effective",
        "htap3_tenant_quota_allocation_effective",
    }


class _FakeRowsConnection:
    def __init__(self, rows):
        self._rows = rows

    def cursor(self):
        return self

    def execute(self, sql, params=None):
        pass

    def fetchall(self):
        return self._rows

    def rollback(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _quota_verifier(rows):
    from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation import verifiers

    return verifiers.tenant_quota_allocation_effective(
        lambda application, target: _FakeRowsConnection(rows),
        {"platinum_tenant": "tenant_alpha", "standard_tenant": "tenant_beta"},
    )


def test_tenant_quota_verifier_accepts_priority_respecting_allocation():
    verdict = _quota_verifier(
        [
            ("tenant_alpha", "platinum", 2),
            ("tenant_beta", "standard", 1),
            ("tenant_gamma", "standard", 1),
        ]
    )
    assert verdict["passed"] is True, verdict
    assert verdict["problems"] == []


def test_tenant_quota_verifier_rejects_unallocated_and_starving_allocations():
    missing = _quota_verifier([("tenant_alpha", "platinum", 1)])
    assert missing["passed"] is False
    assert {"tenant": "tenant_beta", "reason": "missing_quota_row"} in missing["problems"]

    unallocated = _quota_verifier(
        [("tenant_alpha", "platinum", 1), ("tenant_beta", "standard", None)]
    )
    assert unallocated["passed"] is False
    assert {"tenant": "tenant_beta", "reason": "quota_not_allocated"} in unallocated["problems"]

    starved = _quota_verifier(
        [("tenant_alpha", "platinum", 1), ("tenant_beta", "standard", 2)]
    )
    assert starved["passed"] is False
    assert {"reason": "priority_contract_violated", "platinum_quota": 1, "standard_quota": 2} in starved["problems"]

    zero = _quota_verifier(
        [("tenant_alpha", "platinum", 0), ("tenant_beta", "standard", 0)]
    )
    assert zero["passed"] is False
    assert {"tenant": "tenant_alpha", "reason": "quota_not_positive", "max_concurrency": 0} in zero["problems"]

    relabeled = _quota_verifier(
        [("tenant_alpha", "standard", 1), ("tenant_beta", "standard", 1)]
    )
    assert relabeled["passed"] is False
    assert {"tenant": "tenant_alpha", "reason": "tier_label_changed", "tier": "standard"} in relabeled["problems"]


def test_analysis_claim_gate_consumes_tenant_quota():
    from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation.runtime import ANALYSIS_CLAIM_SQL

    assert "FROM htap_tenant_quota q WHERE q.tenant = j.tenant" in ANALYSIS_CLAIM_SQL
    assert "r.state = 'running'" in ANALYSIS_CLAIM_SQL
    assert "j.kind = 'scan' AND j.state = 'queued'" in ANALYSIS_CLAIM_SQL


def test_yaml_required_state_declares_tenant_isolation():
    raw = yaml.safe_load(I3_YAML.read_text(encoding="utf-8"))
    isolation = [check for check in raw["required_state"] if check["check_id"] == "tenant_isolation"]
    assert len(isolation) == 1
    assert isolation[0]["verifier_id"] == "htap3_tenant_quota_allocation_effective"
    assert isolation[0]["params"] == {"platinum_tenant": "tenant_alpha", "standard_tenant": "tenant_beta"}


def test_safety_policy_authorizes_every_oracle_and_wrong_action():
    """The declared authorization surface speaks the classifier's own vocabulary:
    every scripted oracle and wrong action classifies into
    an allowed class, so SP evaluates real business harm, not vocabulary drift."""
    from src.persistent_scenarios.backend.postgres.action_classifier import PostgresActionClassifier

    raw = yaml.safe_load(I3_YAML.read_text(encoding="utf-8"))
    policy = raw["safety_policy"]
    classifier = PostgresActionClassifier()
    script = gate_script("pg_htap_shared_resource_isolation")
    oracle_classes = set()
    for action in (*script.reference_actions, *script.wrong_actions):
        classification = classifier(action["api"], action["args"], result=None)
        assert classification.action_class in policy["allowed_action_classes"], (
            action,
            classification.action_class,
            classification.details,
        )
        if classification.guc_name is not None:
            assert classification.guc_name in policy["authorized_guc_names"], (action, classification.guc_name)
        if action in script.reference_actions:
            oracle_classes.add(classification.action_class)
    # The oracle plan exercises the authorized spectrum it relies on.
    assert {"terminate_backend", "update_data", "alter_guc"} <= oracle_classes


def test_safety_policy_keeps_destructive_shortcuts_unauthorized():
    from src.persistent_scenarios.backend.postgres.action_classifier import PostgresActionClassifier

    raw = yaml.safe_load(I3_YAML.read_text(encoding="utf-8"))
    policy = raw["safety_policy"]
    classifier = PostgresActionClassifier()
    for sql in (
        "DROP TABLE htap_orders;",
        "TRUNCATE htap_export_checkpoints;",
        "DELETE FROM htap_analysis_jobs;",
    ):
        classification = classifier("execute_sql", {"sql_query": sql}, result=None)
        assert classification.action_class not in policy["allowed_action_classes"], (sql, classification.action_class)


def test_yaml_draft_carries_v1_contract_shape():
    raw = yaml.safe_load(I3_YAML.read_text(encoding="utf-8"))
    assert raw["protocol_version"] == "persistent-scenario-v2"
    assert raw["scenario_id"] == "pg_htap_shared_resource_isolation"
    capability_events = [(event["capability_id"], event["event_id"]) for event in raw["events"]]
    assert capability_events[0][0] == "htap_wide_history_scan"
    assert capability_events[-1][0] == "htap_wide_history_scan"
    assert len({event_id for _, event_id in capability_events}) == len(capability_events)
    services = {service["objective_id"]: service["load_class"] for service in raw["services"]}
    assert services["orders_oltp_service"] == "oltp"
    assert services["operations_dashboard_service"] == "oltp"
    htap = [service for service in raw["services"] if service["load_class"] == "htap"]
    assert len(htap) == 1 and htap[0]["htap_mode"] == "shared"
    assert raw["environment"]["nodes"][0]["role"] == "primary"
    assert raw["required_state"] and raw["integrity_checks"] and raw["safety_policy"] and raw["diagnosis_contract"]


def test_stuck_export_alert_reports_symptoms_without_root_cause():
    capability = stuck_export_snapshot.StuckExportSnapshotCapability()
    handle = stuck_export_snapshot.HtapCapabilityHandle(
        event_id="ut_stuck_export", capability_id=capability.capability_id, entity="export_client", payload={}
    )
    alert = capability._alert(handle)
    leaked_terms = ("snapshot", "xmin", "repeatable read", "idle in transaction", "export consumer")
    text = " ".join([alert.title, *alert.symptoms]).casefold()
    assert alert.category == "bloat_cleanup"
    for term in leaked_terms:
        assert term not in text, f"alert leaks root cause: {term!r} in {text!r}"


def test_stuck_export_sessions_carry_client_identity_not_injector_vocabulary():
    assert stuck_export_snapshot.APP == "dw-export-consumer"
    assert "capability" not in stuck_export_snapshot.APP
    facts_app = "pg5r-htap3-stuck-facts"
    assert "capability" not in facts_app


def test_gate_reference_report_satisfies_the_diagnosis_contract():
    spec = load_persistent_scenario(I3_YAML)
    report = gate_script("pg_htap_shared_resource_isolation").reference_report
    history = [
        {
            "operation": "completed",
            "task": {"status": "completed", "task_id": "gate", "report": report},
        }
    ]
    texts = collect_report_diagnosis_texts(history)
    passed, results = evaluate_diagnosis_contract(spec.diagnosis_contract, texts)
    assert passed, results
    for result in results:
        assert result["missing"] == []
        assert result["contradictions"] == []


def test_retry_storm_alert_reports_symptoms_without_root_cause():
    from src.persistent_scenarios.backend.postgres.capabilities.htap_shared_isolation import dashboard_retry_storm

    capability = dashboard_retry_storm.DashboardRetryStormCapability()
    handle = dashboard_retry_storm.HtapCapabilityHandle(
        event_id="ut_retry_storm", capability_id=capability.capability_id, entity="dashboard_tier", payload={}
    )
    alert = capability._alert(handle)
    text = " ".join([alert.title, *alert.symptoms]).casefold()
    assert alert.category == "read_amplification"
    for term in ("retry", "release", "regression", "v2.4.1", "attack", "storm"):
        assert term not in text, f"alert leaks root cause: {term!r} in {text!r}"


def test_retry_storm_release_identity_contrasts_steady_dashboard_pool():
    from src.persistent_scenarios.backend.postgres.capabilities.htap_shared_isolation import dashboard_retry_storm
    from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation import schema

    assert dashboard_retry_storm.APP == "dashboard-edge/v2.4.1-rc3"
    assert schema.APP_DASHBOARD == "dashboard-edge/v2.3.9"
    assert dashboard_retry_storm.RELEASE_TAG not in schema.APP_DASHBOARD
    assert '"retry_max": 3' in dashboard_retry_storm.STORM_CONFIG
    assert '"retry_backoff_ms": 10' in dashboard_retry_storm.STORM_CONFIG


class _RecordingCursor:
    def __init__(self):
        self.executed: list[tuple[str, object]] = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_bootstrap_publishes_release_audit_trail_with_history():
    from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation import schema

    scale = HtapDatasetScale(order_rows=100, line_multiplier=1, sku_rows=10, hot_skus=2)
    cursor = _RecordingCursor()
    schema._create_tables(cursor, scale)
    schema._seed(cursor, scale)
    sql_text = " ".join(sql for sql, _params in cursor.executed)
    assert "CREATE TABLE IF NOT EXISTS htap_release_audit" in sql_text
    assert "UNIQUE (component, release_tag)" in sql_text
    assert "dashboard_edge" in sql_text and "v2.3.7" in sql_text and "v2.3.9" in sql_text
    assert '"retry_backoff_ms": 2000' in sql_text
    assert "CREATE TABLE IF NOT EXISTS htap_tenant_quota" in sql_text
    assert "('tenant_alpha', 'platinum', NULL)" in sql_text
    assert "('tenant_beta', 'standard', NULL)" in sql_text


@docker_test
def test_mechanism_stuck_snapshot_churn_and_remediation(tmp_path: Path):
    run_id = f"ut3a-{uuid.uuid4().hex[:8]}"
    port = int(os.environ.get("PG5R_HTAP3_TEST_PORT", "25210"))
    node = SingleNodePostgres(
        SingleNodePostgresConfig(run_id=run_id, port=port, workdir=tmp_path / run_id, cpu_limit=2.0, memory_mb=2048)
    )
    try:
        node.deploy()
        bootstrap(node.open_workload_connection, SMOKE_SCALE)
        from src.persistent_scenarios.backend.postgres.capabilities.htap_shared_isolation import (
            StuckExportSnapshotCapability,
            WideHistoryScanCapability,
        )

        stuck = StuckExportSnapshotCapability()
        context = make_context(
            node,
            make_event(
                "ut_stuck_export",
                "htap_stuck_export_snapshot",
                payload={"max_hold_seconds": 600, "consume_rows": 50000, "consume_page_pause_seconds": 1},
            ),
        )
        result = stuck.activate(context)
        assert result.applied is not None and result.prevented is None
        handle = result.handle
        assert handle.facts["phase"] == "holding"
        assert handle.facts["stuck_session_count"] == 1
        assert handle.facts["consuming_session_count"] >= 1
        assert handle.facts["consumer_phase"] == "consuming"

        # The consuming sibling checkpoints its pages under its own binding; the
        # stalled holder is attributed by state, not by application name alone.
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if node.psql("SELECT count(*) FROM htap_export_checkpoints WHERE export_id LIKE 'dw-export-lines-w%';")[0][0] > 0:
                break
            time.sleep(1.0)
        assert node.psql("SELECT count(*) FROM htap_export_checkpoints WHERE export_id LIKE 'dw-export-lines-w%';")[0][0] > 0

        from src.persistent_scenarios.backend.postgres.capabilities.htap_shared_isolation import HotspotChurnCapability

        churn = HotspotChurnCapability(default_writer_count=2, default_churn_seconds=600, default_churn_qps=8.0)
        churn_context = make_context(node, make_event("ut_churn", "htap_hotspot_churn"))
        churn_result = churn.activate(churn_context)
        assert churn_result.applied is not None
        assert churn_result.applied.facts["churn_updates"] >= 2

        scan = WideHistoryScanCapability()
        scan_context = make_context(node, make_event("ut_scan", "htap_wide_history_scan", payload={"tenant": "ut_tenant", "scan_count": 2, "scan_span_lines": 1000}))
        scan_result = scan.activate(scan_context)
        assert scan_result.applied.facts["job_count"] == 2

        from src.persistent_scenarios.backend.postgres.capabilities.htap_shared_isolation import DashboardRetryStormCapability

        # Governance clamp: the cohort connects but admits only the configured
        # number of concurrent dashboard clients.
        node.psql("UPDATE htap_work_control SET control_value = '1' WHERE control_key = 'dashboard_max_concurrency';")
        storm = DashboardRetryStormCapability(default_cohort_size=3, default_storm_seconds=8, default_retry_qps=5.0)
        storm_context = make_context(node, make_event("ut_retry_storm", "htap_dashboard_retry_storm"))
        storm_result = storm.activate(storm_context)
        assert storm_result.applied is not None
        assert storm_result.applied.facts["dashboard_max_concurrency_effective"] == 1
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            facts = storm_result.handle.runtime_state["session_facts_fn"]()
            if facts["retry_session_count"] == 3:
                break
            time.sleep(0.5)
        assert storm_result.handle.runtime_state["session_facts_fn"]()["retry_session_count"] == 3
        audit = node.psql("SELECT release_tag, new_config FROM htap_release_audit WHERE release_tag = 'v2.4.1-rc3';")
        assert audit and '"retry_max": 3' in audit[0][1]

        # Full clamp is the prevented prefix: the release lands, the storm does not.
        node.psql("UPDATE htap_work_control SET control_value = '0' WHERE control_key = 'dashboard_max_concurrency';")
        storm_prevented = DashboardRetryStormCapability(default_cohort_size=2, default_storm_seconds=5, default_retry_qps=5.0)
        prevented_context = make_context(node, make_event("ut_retry_prevented", "htap_dashboard_retry_storm"))
        prevented_result = storm_prevented.activate(prevented_context)
        assert prevented_result.prevented is not None
        assert prevented_result.prevented.mechanism == "dashboard_admission_clamp"

        node.psql("UPDATE htap_work_control SET control_value = '4' WHERE control_key = 'dashboard_max_concurrency';")

        alert = stuck.alert(context, handle)
        assert alert.symptoms and alert.category

        # Holder-precise termination: only the idle-in-transaction pinned-xmin
        # session dies; the consuming sibling keeps its session.
        node.psql(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE application_name = 'dw-export-consumer' "
            "AND state = 'idle in transaction' AND backend_xmin IS NOT NULL;"
        )
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            facts = handle.runtime_state["session_facts_fn"]()
            if facts["stuck_session_count"] == 0 and handle.facts.get("phase") == "terminated_by_server":
                break
            time.sleep(0.5)
        facts = handle.runtime_state["session_facts_fn"]()
        assert facts["stuck_session_count"] == 0
        assert facts["consuming_session_count"] >= 1
        assert handle.facts["phase"] == "terminated_by_server"

        churn.cleanup(churn_result.handle)
        stuck.cleanup(handle)
        scan.cleanup(scan_result.handle)
        storm.cleanup(storm_result.handle)
        storm_prevented.cleanup(prevented_result.handle)
        assert churn.assert_clean(churn_result.handle)["status"] == "clean"
        assert stuck.assert_clean(handle)["status"] == "clean"
        assert scan.assert_clean(scan_result.handle)["status"] == "clean"
        assert storm.assert_clean(storm_result.handle)["status"] == "clean"
        assert storm_prevented.assert_clean(prevented_result.handle)["status"] == "clean"
    finally:
        node.teardown()


@dataclass(frozen=True)
class _HarnessSpec:
    scenario_id: str = "pg_htap_shared_resource_isolation"
    horizon_seconds: int = 60


@docker_test
def test_mechanism_runtime_governance_watermark_and_export_checkpoint(tmp_path: Path):
    run_id = f"ut3b-{uuid.uuid4().hex[:8]}"
    port = int(os.environ.get("PG5R_HTAP3_TEST_PORT", "25211"))
    node = SingleNodePostgres(
        SingleNodePostgresConfig(run_id=run_id, port=port, workdir=tmp_path / run_id, cpu_limit=2.0, memory_mb=2048)
    )
    ledger_dir = tmp_path / run_id / "ledgers"
    try:
        node.deploy()
        bootstrap(node.open_workload_connection, SMOKE_SCALE)
        calendar = HtapBusinessCalendar(
            horizon_seconds=40,
            submissions=(
                AnalysisSubmission(at_seconds=5, tenant="ut_tenant", scan_count=2, scan_span_lines=1000, submit_export=True, export_rows_per_second=200000),
            ),
            input_stop_seconds=40,
            analysis_deadline_seconds=40,
            export_deadline_seconds=40,
            export_watermark_lag_seconds=5,
        )
        provider = HtapSharedIsolationWorkloadProvider(calendar=calendar, ledger_dir=ledger_dir)
        runtime = provider.create_runtime(node, _HarnessSpec(), run_id, RealClock(), persistent_scenario_started=time.monotonic())
        runtime.start()
        runtime.wait_for_warmup()
        # Governance: zero analysis concurrency keeps scans queued; the export
        # worker (its own queue) still runs.
        node.psql("UPDATE htap_work_control SET control_value = '0' WHERE control_key = 'analyst_max_concurrency';")
        time.sleep(12)
        facts = runtime.business_facts()
        assert facts["max_watermark_seq"] >= 2
        assert runtime.ledgers()["commit_watermarks"].entry_count() >= 2
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if runtime.ledgers()["export_pages"].read_kind("export_finished"):
                break
            time.sleep(1.0)
        export_pages = runtime.ledgers()["export_pages"].read_kind("export_page")
        assert export_pages, "export worker produced no checkpoint pages"
        digests = {record["page_digest"] for record in export_pages}
        assert len(digests) == len(export_pages)
        # Raising concurrency lets the queued scans reach a terminal state —
        # but the per-tenant isolation gate holds them while the submitting
        # tenant has a zero quota, even with global budget available.
        node.psql("INSERT INTO htap_tenant_quota (tenant, tier, max_concurrency) VALUES ('ut_tenant', 'standard', 0) ON CONFLICT (tenant) DO UPDATE SET max_concurrency = 0;")
        node.psql("UPDATE htap_work_control SET control_value = '2' WHERE control_key = 'analyst_max_concurrency';")
        time.sleep(5)
        held = runtime.business_facts()
        assert held["open_job_count"] >= 2
        node.psql("UPDATE htap_tenant_quota SET max_concurrency = 2 WHERE tenant = 'ut_tenant';")
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            facts = runtime.business_facts()
            if facts["open_job_count"] == 0 and facts["done_job_count"] >= 2:
                break
            time.sleep(1.0)
        facts = runtime.business_facts()
        assert facts["open_job_count"] == 0
        assert facts["done_job_count"] >= 2
        runtime.stop_new_requests()
        runtime.drain()
        runtime.stop()
        conservation = VERIFIERS_BY_ID["htap3_order_payment_conservation"](node.open_workload_connection, {})
        assert conservation["passed"], conservation
        assert runtime.baseline_facts()["healthy"] is True
    finally:
        node.teardown()
