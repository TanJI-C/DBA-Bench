"""Shared builders for Persistent Scenario evaluation tests (interface v1 shapes).

Run facts are real core types; spec-side contracts are constructed from the core
model dataclasses; business ledgers go through the real ``TrustedLedger`` write
path so the ``LedgerView`` materialization (including outstanding finalization)
is exercised exactly as in production.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from src.persistent_scenarios.model.enums import (
    HtapMode,
    LoadClass,
    OlapMode,
    RequiredStateKind,
    SettingEffect,
    SettingScope,
)
from src.persistent_scenarios.model.spec import (
    DeliverableContract,
    DiagnosisContract,
    DiagnosisIncidentSpec,
    ExpectedDiagnosisConditionSpec,
    GucEffectiveSpec,
    ContinuityStateSpec,
    DeliverablePresentSpec,
    HtapObjective,
    OlapObjective,
    OltpObjective,
    ProtectedObjectSpec,
    SafetyPolicyContract,
    VerifierStateSpec,
)
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    JobAttempt,
    JobAttemptOutcome,
    LedgerTerminal,
    FreshnessSample,
    TransactionAttempt,
    TrustedLedger,
)
from src.persistent_scenarios.runtime.lifecycle import (
    ActionFact,
    AppliedEvidence,
    ArrivalFacts,
    EventAttemptEvidence,
    EventArrivalStatus,
    InputVersions,
    IntegrityFact,
    IntegrityStatus,
    PreventionEvidence,
    RequiredStateEvidence,
    RunValidityFact,
    ScoringWindow,
)


WINDOW = ScoringWindow(scoring_start_monotonic=0.0, scoring_end_monotonic=100.0, input_stop_monotonic=80.0)

INPUT_VERSIONS = InputVersions(
    spec_digest="spec-digest-1",
    protocol_version="persistent-scenario-v2",
    trace_schema="persistent_scenario_trace_v2",
    evaluation_schema="persistent_scenario_evaluation_v2",
    resource_lease_id="pg5r-eval-test",
    calibration_evidence_id="cal-1",
    code_version="test-code",
)


# ---------------------------------------------------------------------------
# Trusted ledger builder
# ---------------------------------------------------------------------------


class LedgerBuilder:
    """Writes a real TrustedLedger and materializes a sealed LedgerView."""

    def __init__(self, ledger_id: str, root: Path):
        from uuid import uuid4

        self._ledger = TrustedLedger(ledger_id, Path(root) / f"{ledger_id}-{uuid4().hex[:8]}.jsonl")

    def plan_transaction(
        self,
        business_id,
        service_id="orders",
        planned_at=1.0,
        deadline_at=11.0,
        tx_kind="order",
    ):
        self._ledger.append_planned_transaction(
            business_id=business_id,
            service_id=service_id,
            tx_kind=tx_kind,
            planned_at_monotonic=planned_at,
            deadline_at_monotonic=deadline_at,
        )
        return self

    def attempt_transaction(self, business_id, index=1, started=1.0, ended=2.0, outcome=AttemptOutcome.COMMITTED):
        self._ledger.append_transaction_attempt(
            business_id=business_id,
            attempt=TransactionAttempt(index, started, ended, outcome, {}),
        )
        return self

    def complete_transaction(self, business_id, completed_at, digest="digest-ok"):
        self._ledger.append_transaction_terminal(
            business_id=business_id,
            terminal=LedgerTerminal.COMPLETED,
            completed_at_monotonic=completed_at,
            result_digest=digest,
        )
        return self

    def terminal_transaction(self, business_id, terminal: LedgerTerminal):
        self._ledger.append_transaction_terminal(
            business_id=business_id,
            terminal=terminal,
            completed_at_monotonic=None,
            result_digest=None,
        )
        return self

    def plan_job(
        self,
        job_id,
        service_id="reports",
        submitted_at=10.0,
        deadline_at=40.0,
        batch_version="batch-a",
        job_kind="report",
        input_snapshot=None,
    ):
        self._ledger.append_job_planned(
            job_id=job_id,
            service_id=service_id,
            job_kind=job_kind,
            batch_version=batch_version,
            input_snapshot=input_snapshot,
            submitted_at_monotonic=submitted_at,
            deadline_at_monotonic=deadline_at,
        )
        return self

    def attempt_job(self, job_id, index=1, queued=10.0, started=11.0, ended=12.0, outcome=JobAttemptOutcome.SUCCEEDED):
        self._ledger.append_job_attempt(
            job_id=job_id,
            attempt=JobAttempt(index, queued, started, ended, outcome, {}),
        )
        return self

    def deliver_job(self, job_id, delivered_at, digest="digest-ok"):
        self._ledger.append_job_terminal(
            job_id=job_id,
            terminal=LedgerTerminal.COMPLETED,
            delivered_at_monotonic=delivered_at,
            result_digest=digest,
        )
        return self

    def terminal_job(self, job_id, terminal: LedgerTerminal):
        self._ledger.append_job_terminal(
            job_id=job_id,
            terminal=terminal,
            delivered_at_monotonic=None,
            result_digest=None,
        )
        return self

    def freshness(self, sample_id, at, lag=3.0, primary="primary/lsn/100", replica="replica/lsn/97"):
        self._ledger.append_freshness_sample(
            FreshnessSample(sample_id, at, primary, replica, lag, {})
        )
        return self

    def trusted(self, now=1_000.0):
        """Finalize outstanding records, seal and verify, like the engine does."""
        self._ledger.finalize_outstanding(now)
        self._ledger.seal()
        self._ledger.verify()
        return self._ledger


# ---------------------------------------------------------------------------
# Spec-side contracts (core model dataclasses)
# ---------------------------------------------------------------------------


def oltp_objective(
    objective_id="oltp-1",
    service_id="orders",
    deadline_seconds=10.0,
    min_success_fraction=0.9,
    outage_contract_seconds=None,
    outage_source=None,
):
    return OltpObjective(
        objective_id=objective_id,
        service_id=service_id,
        deadline_seconds=deadline_seconds,
        min_success_fraction=min_success_fraction,
        outage_contract_seconds=outage_contract_seconds,
        outage_source=outage_source,
        load_class=LoadClass.OLTP,
    )


def deliverable(
    deliverable_id,
    deadline_seconds=30.0,
    requires_freshness=False,
    max_freshness_lag_seconds=None,
    input_batch_binding=None,
):
    return DeliverableContract(
        deliverable_id=deliverable_id,
        deadline_seconds=deadline_seconds,
        requires_freshness=requires_freshness,
        max_freshness_lag_seconds=max_freshness_lag_seconds,
        input_batch_binding=input_batch_binding,
    )


def olap_objective(
    objective_id="olap-1",
    service_id="reports",
    mode=OlapMode.DELIVERABLE_CHECKLIST,
    deliverables=(),
    deadline_seconds=None,
    min_on_time_correct_fraction=None,
    calibration_evidence_id=None,
):
    return OlapObjective(
        objective_id=objective_id,
        service_id=service_id,
        olap_mode=mode,
        deliverables=tuple(deliverables),
        deadline_seconds=deadline_seconds,
        min_on_time_correct_fraction=min_on_time_correct_fraction,
        calibration_evidence_id=calibration_evidence_id,
        load_class=LoadClass.OLAP,
    )


def htap_objective(
    objective_id="htap-1",
    service_id="htap-service",
    mode=HtapMode.SHARED,
    transaction_objective_id="oltp-1",
    analysis_objective_id="olap-1",
):
    return HtapObjective(
        objective_id=objective_id,
        service_id=service_id,
        htap_mode=mode,
        transaction_objective_id=transaction_objective_id,
        analysis_objective_id=analysis_objective_id,
        load_class=LoadClass.HTAP,
    )


def safety_policy(
    allowed_action_classes=("terminate_backend", "cancel_job", "alter_guc"),
    protected_objects=(),
    authorized_guc_names=("statement_timeout",),
    guc_floor=None,
    read_only_action_classes=(),
):
    return SafetyPolicyContract(
        allowed_action_classes=tuple(allowed_action_classes),
        protected_objects=tuple(ProtectedObjectSpec(pattern) for pattern in protected_objects),
        authorized_guc_names=tuple(authorized_guc_names),
        guc_floor=dict(guc_floor or {"fsync": "on", "full_page_writes": "on"}),
        read_only_action_classes=tuple(read_only_action_classes),
    )


def continuity_check(check_id="orders-continuity", service_id="orders", window_seconds=20.0, min_success_fraction=0.9):
    return ContinuityStateSpec(
        check_id=check_id,
        service_id=service_id,
        window_seconds=window_seconds,
        min_success_fraction=min_success_fraction,
        kind=RequiredStateKind.CONTINUITY,
    )


def deliverable_present_check(check_id="archive-delivered", deliverable_id="archive_2026", params=None):
    return DeliverablePresentSpec(
        check_id=check_id,
        deliverable_id=deliverable_id,
        params=params if params is not None else {"deliverable_id": deliverable_id},
        kind=RequiredStateKind.DELIVERABLE_PRESENT,
    )


def guc_check(
    check_id="guc-fsync",
    guc_name="fsync",
    allowed_values=("on",),
    scope=SettingScope.SERVER,
    scope_name=None,
    effective_on=SettingEffect.NEW_CONNECTIONS,
    persist_required=False,
):
    return GucEffectiveSpec(
        check_id=check_id,
        guc_name=guc_name,
        allowed_values=tuple(allowed_values),
        scope=scope,
        scope_name=scope_name,
        effective_on=effective_on,
        persist_required=persist_required,
        kind=RequiredStateKind.GUC_EFFECTIVE,
    )


def verifier_check(check_id="backfill-complete", verifier_id="backfill_completeness", params=None):
    return VerifierStateSpec(
        check_id=check_id,
        verifier_id=verifier_id,
        params=dict(params or {}),
        kind=RequiredStateKind.VERIFIER,
    )


def diagnosis_contract(incidents=()):
    return DiagnosisContract(incidents=tuple(incidents))


def incident(incident_id="incident-1", conditions=(), statement="business incident explanation"):
    return DiagnosisIncidentSpec(incident_id=incident_id, statement=statement, conditions=tuple(conditions))


def condition(condition_id="c1", aliases=("long transaction holding the lock",), contradictions=()):
    return ExpectedDiagnosisConditionSpec(
        condition_id=condition_id, aliases=tuple(aliases), contradictions=tuple(contradictions)
    )


# ---------------------------------------------------------------------------
# Run facts (core runtime types)
# ---------------------------------------------------------------------------


def action_fact(sequence, action_class, objects=(), guc_name=None, guc_value=None, at=20.0, details=None):
    return ActionFact(sequence, at, action_class, tuple(objects), guc_name, guc_value, details or {})


def integrity_fact(check_id, status=IntegrityStatus.PASSED, kind="ledger_conservation", details=None):
    return IntegrityFact(check_id, kind, status, details or {})


def required_state_evidence(check_id, facts, status=None, captured=99.0):
    from src.persistent_scenarios.runtime.lifecycle import EvidenceStatus

    return RequiredStateEvidence(check_id, status or EvidenceStatus.CAPTURED, facts, captured)


def applied_arrival(arrival=10.0, facts=None, attempt_detail=None):
    return ArrivalFacts(
        status=EventArrivalStatus.APPLIED,
        attempt=EventAttemptEvidence(arrival - 1.0, attempt_detail or {"issued": True}),
        applied=AppliedEvidence(arrival, facts or {"lock_queue": 3}),
        prevented=None,
        arrived_at_monotonic=arrival,
    )


def prevented_arrival(arrival=10.0, mechanism="scoped_statement_timeout", protection=None):
    return ArrivalFacts(
        status=EventArrivalStatus.PREVENTED,
        attempt=EventAttemptEvidence(arrival - 1.0, {"issued": True}),
        applied=None,
        prevented=PreventionEvidence(
            EventAttemptEvidence(arrival - 1.0, {"issued": True}),
            mechanism,
            protection or {"timeout_ms": 5000},
            arrival,
        ),
        arrived_at_monotonic=arrival,
    )


def failed_arrival(arrival=10.0, error="activation precondition missing"):
    return ArrivalFacts(
        status=EventArrivalStatus.FAILED,
        attempt=EventAttemptEvidence(arrival - 1.0, {"error": error}),
        applied=None,
        prevented=None,
        arrived_at_monotonic=arrival,
    )


def event_run(event_id, arrival, occurrence=1, capability_id="capability.long_tx", entity="order", planned_start=10.0):
    return SimpleNamespace(
        event_id=event_id,
        capability_id=capability_id,
        occurrence=occurrence,
        entity=entity,
        planned_start_monotonic=planned_start,
        arrival=arrival,
    )


def mailbox_completion(task_id, conditions, summary, revision=1, at=30.0, operation="completed", status="completed"):
    return {
        "revision": revision,
        "operation": operation,
        "at_monotonic": at,
        "task": {
            "task_id": task_id,
            "status": status,
            "report": {"diagnosis": {"conditions": list(conditions)}, "summary": summary},
        },
    }


def validity(valid=True, ledger_complete=True, classification=None, reason=None):
    if (not valid or not ledger_complete) and classification is None:
        classification = "infrastructure_failure"
    return RunValidityFact(valid, classification, reason, ledger_complete)


def spec(
    services=(),
    required_state=(),
    safety_policy=None,
    diagnosis_contract=None,
    scenario_id="pg-eval-scenario",
):
    if safety_policy is None:
        safety_policy = SafetyPolicyContract(
            allowed_action_classes=("terminate_backend", "cancel_job", "alter_guc"),
            authorized_guc_names=("statement_timeout",),
            guc_floor={"fsync": "on", "full_page_writes": "on"},
        )
    return SimpleNamespace(
        scenario_id=scenario_id,
        services=tuple(services),
        required_state=tuple(required_state),
        safety_policy=safety_policy,
        diagnosis_contract=diagnosis_contract if diagnosis_contract is not None else DiagnosisContract(),
    )


def run(
    spec_value,
    *,
    window=WINDOW,
    validity_value=None,
    ledgers=(),
    integrity_facts=(),
    required_state_evidence=(),
    mailbox_history=(),
    action_facts=(),
    safety_checkpoints=(),
    events=(),
):
    return SimpleNamespace(
        run_id="run-eval-1",
        spec=spec_value,
        business_window=window,
        validity=validity_value if validity_value is not None else validity(),
        ledgers={f"ledger-{index}": ledger for index, ledger in enumerate(ledgers)},
        integrity_facts=list(integrity_facts),
        required_state_evidence=list(required_state_evidence),
        mailbox_history=list(mailbox_history),
        action_facts=list(action_facts),
        safety_checkpoints=list(safety_checkpoints),
        events=tuple(events),
        input_versions=INPUT_VERSIONS,
    )


__all__ = [
    "INPUT_VERSIONS",
    "LedgerBuilder",
    "WINDOW",
    "action_fact",
    "applied_arrival",
    "continuity_check",
    "deliverable",
    "deliverable_present_check",
    "diagnosis_contract",
    "event_run",
    "failed_arrival",
    "guc_check",
    "htap_objective",
    "incident",
    "integrity_fact",
    "mailbox_completion",
    "olap_objective",
    "oltp_objective",
    "prevented_arrival",
    "required_state_evidence",
    "run",
    "safety_policy",
    "spec",
    "validity",
    "verifier_check",
]
