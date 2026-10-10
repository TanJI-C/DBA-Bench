"""Adapters binding pg5 instance capability/driver implementations to core.

The instance packages speak a module-local mirror of the frozen protocols
(``EventOccurrence``/``CapabilityContext``/module-local ``EventActivationResult``
and the ``BusinessLedger`` evidence ledger). This module is the only place
where that dialect is translated into the frozen core shapes:

- ``InstanceCapabilityAdapter`` implements the core
  ``PersistentScenarioEventCapability`` protocol around one instance
  capability. Handles are the objects the instance capability returns in
  ``EventActivationResult.handle``; the adapter keeps the handle ->
  (capability, activation context) binding for ``alert``/``cleanup``/
  ``assert_clean`` dispatch.
- ``InstanceWorkloadRuntime`` implements the core
  ``PersistentWorkloadRuntime`` protocol around an instance driver and owns
  the run's core ``TrustedLedger``. The driver keeps its own hash-chained
  business evidence; after its threads stop, ``translate`` replays the
  terminal ledger state into the core ledger (retry merging and terminal
  semantics are decided by the instance ledger, the core ledger records the
  same facts in the frozen vocabulary evaluation consumes).
"""

from __future__ import annotations

import hashlib
import json
from math import ceil
from pathlib import Path
from typing import Mapping

from src.persistent_scenarios.backend.contracts import (
    AppliedEvidence,
    CapabilityDeclaration,
    EventActivationContext,
    EventActivationResult,
    EventAlertPayload,
    OwnershipMode,
    ResourceOwnership,
)
from src.persistent_scenarios.model.spec import EventSpec
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    LedgerTerminal,
    TransactionAttempt,
    TrustedLedger,
)
from src.persistent_scenarios.runtime.lifecycle import (
    EventAttemptEvidence,
    PreventionEvidence,
)

from .workloads.oltp_core.capability import (
    CapabilityContext,
    EventOccurrence,
)
from .workloads.oltp_core.ledger import (
    AttemptOutcome as InstanceAttemptOutcome,
    BusinessLedger,
)


class InstanceRunResources:
    """Per-run instance resources shared by capabilities and the driver."""

    def __init__(self, *, source, admin_source, evidence, driver):
        self.source = source
        self.admin_source = admin_source
        self.evidence = evidence
        self.driver = driver


class InstanceCapabilityAdapter:
    """Core capability protocol around one instance capability."""

    def __init__(self, inner, resources_by_run_id):
        self._inner = inner
        self._resources_by_run_id = resources_by_run_id
        self.capability_id = inner.capability_id
        self._activations: dict[int, tuple[object, CapabilityContext]] = {}

    def _occurrence(self, event: EventSpec) -> EventOccurrence:
        return EventOccurrence(
            event_id=event.event_id,
            capability_id=event.capability_id,
            occurrence_index=event.occurrence,
            entity=event.entity,
            params=dict(event.payload),
        )

    def _instance_context(self, context: EventActivationContext, occurrence: EventOccurrence) -> CapabilityContext:
        resources = self._resources_by_run_id.get(context.run_id)
        if resources is None:
            raise ValueError(
                "Instance run resources are not registered for this run: "
                f"run_id={context.run_id!r}, capability_id={self.capability_id!r}, "
                f"event_id={context.event.event_id!r}"
            )
        return CapabilityContext(
            run_id=context.run_id,
            occurrence=occurrence,
            clock=context.clock,
            source=resources.source,
            admin_source=resources.admin_source,
            evidence=resources.evidence,
            driver=resources.driver,
        )

    def declaration(self, event: EventSpec) -> CapabilityDeclaration:
        declaration = self._inner.declaration(self._occurrence(event))
        resources = tuple(
            ResourceOwnership(
                resource_key=ownership.resource_key,
                resource_kind=ownership.resource_kind,
                mode=OwnershipMode(ownership.mode),
            )
            for ownership in declaration.ownership
        )
        if not resources:
            raise ValueError(
                "Instance capability declared no owned resources: "
                f"capability_id={self.capability_id!r}, event_id={event.event_id!r}"
            )
        return CapabilityDeclaration(
            capability_id=event.capability_id,
            resources=resources,
            max_activation_seconds=max(1, ceil(declaration.max_activation_seconds)),
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        occurrence = self._occurrence(context.event)
        instance_context = self._instance_context(context, occurrence)
        started_at = context.clock.monotonic()
        result = self._inner.activate(instance_context)
        handle = result.handle
        if handle is None:
            raise ValueError(
                "Instance capability activation returned no handle: "
                f"capability_id={self.capability_id!r}, event_id={context.event.event_id!r}; "
                "alert/cleanup dispatch cannot be bound without it"
            )
        attempt = EventAttemptEvidence(
            attempted_at_monotonic=started_at,
            detail=dict(result.attempt),
        )
        if result.outcome == "applied":
            core_result = EventActivationResult(
                handle=handle,
                attempt=attempt,
                applied=AppliedEvidence(
                    observed_at_monotonic=context.clock.monotonic(),
                    facts=dict(result.attempt),
                ),
                prevented=None,
            )
        elif result.outcome == "prevented":
            mechanism = result.attempt.get("mechanism")
            protection_state = result.attempt.get("protection_state")
            if not isinstance(mechanism, str) or not mechanism.strip():
                raise ValueError(
                    "Instance prevented activation must report a mechanism: "
                    f"capability_id={self.capability_id!r}, event_id={context.event.event_id!r}, "
                    f"attempt={dict(result.attempt)!r}"
                )
            if not isinstance(protection_state, Mapping):
                raise ValueError(
                    "Instance prevented activation must report its protection state: "
                    f"capability_id={self.capability_id!r}, event_id={context.event.event_id!r}, "
                    f"attempt={dict(result.attempt)!r}"
                )
            core_result = EventActivationResult(
                handle=handle,
                attempt=attempt,
                applied=None,
                prevented=PreventionEvidence(
                    attempted=attempt,
                    mechanism=mechanism,
                    protection_state=dict(protection_state),
                    observed_at_monotonic=context.clock.monotonic(),
                ),
            )
        else:
            raise ValueError(
                f"Instance activation outcome must be applied or prevented: "
                f"capability_id={self.capability_id!r}, event_id={context.event.event_id!r}, "
                f"outcome={result.outcome!r}"
            )
        self._activations[id(handle)] = (self._inner, instance_context)
        return core_result

    def _activation(self, handle: object) -> tuple[object, CapabilityContext]:
        try:
            return self._activations[id(handle)]
        except KeyError:
            raise ValueError(
                "Instance capability handle was not activated through this adapter: "
                f"capability_id={self.capability_id!r}, handle={handle!r}"
            ) from None

    def alert(self, context: EventActivationContext, handle: object) -> EventAlertPayload:
        inner, instance_context = self._activation(handle)
        payload = inner.alert(instance_context, handle)
        return EventAlertPayload(
            title=str(payload["title"]),
            symptoms=tuple(str(symptom) for symptom in payload["symptoms"]),
            severity=str(payload["severity"]),
            category=str(payload["category"]),
        )

    def cleanup(self, handle: object) -> None:
        inner, instance_context = self._activation(handle)
        inner.cleanup(handle)

    def assert_clean(self, handle: object) -> Mapping[str, object]:
        inner, instance_context = self._activation(handle)
        return inner.assert_clean(handle)


_INSTANCE_ATTEMPT_OUTCOMES: Mapping[InstanceAttemptOutcome, AttemptOutcome] = {
    InstanceAttemptOutcome.COMMITTED: AttemptOutcome.COMMITTED,
    InstanceAttemptOutcome.BUSINESS_REJECTED: AttemptOutcome.ABORTED,
    InstanceAttemptOutcome.TIMEOUT: AttemptOutcome.TIMED_OUT,
    InstanceAttemptOutcome.CONNECTION_REFUSED: AttemptOutcome.CONNECTION_REFUSED,
    InstanceAttemptOutcome.ERROR: AttemptOutcome.ABORTED,
}

_INSTANCE_TERMINALS: Mapping[InstanceAttemptOutcome, LedgerTerminal] = {
    InstanceAttemptOutcome.COMMITTED: LedgerTerminal.COMPLETED,
    InstanceAttemptOutcome.BUSINESS_REJECTED: LedgerTerminal.INCOMPLETE_ERROR,
    InstanceAttemptOutcome.TIMEOUT: LedgerTerminal.INCOMPLETE_TIMEOUT,
    InstanceAttemptOutcome.CONNECTION_REFUSED: LedgerTerminal.INCOMPLETE_ERROR,
    InstanceAttemptOutcome.ERROR: LedgerTerminal.INCOMPLETE_ERROR,
    InstanceAttemptOutcome.PENDING_AT_CLOSE: LedgerTerminal.INCOMPLETE_OUTSTANDING,
}


def adapt_capability_registry(registry) -> list:
    """The instance capability objects of one module-local registry, in id order."""

    return [registry.capability(capability_id) for capability_id in registry.ids()]


def translate_business_ledger(
    ledger: BusinessLedger,
    trusted: TrustedLedger,
    *,
    service_id: str,
) -> None:
    """Replay terminal instance ledger state into the core trusted ledger.

    Must run after the instance driver stopped: every logical operation has a
    terminal outcome by then, so the core ledger receives complete records and
    ``finalize_outstanding`` has nothing left to close.
    """

    for op in ledger.ops():
        trusted.append_planned_transaction(
            business_id=op.op_id,
            service_id=service_id,
            tx_kind=op.flow_id,
            planned_at_monotonic=op.scheduled_at,
            deadline_at_monotonic=op.deadline_at,
        )
        for index, attempt in enumerate(op.attempts, start=1):
            trusted.append_transaction_attempt(
                business_id=op.op_id,
                attempt=TransactionAttempt(
                    attempt_index=index,
                    started_at_monotonic=attempt.started_at,
                    ended_at_monotonic=attempt.ended_at,
                    outcome=_INSTANCE_ATTEMPT_OUTCOMES[attempt.outcome],
                    detail={"original_outcome": attempt.outcome.value, "detail": attempt.detail},
                ),
            )
        terminal = _INSTANCE_TERMINALS[op.terminal.outcome]
        if terminal is LedgerTerminal.COMPLETED:
            trusted.append_transaction_terminal(
                business_id=op.op_id,
                terminal=terminal,
                completed_at_monotonic=op.terminal.ended_at,
                result_digest=None,
            )
        else:
            trusted.append_transaction_terminal(
                business_id=op.op_id,
                terminal=terminal,
                completed_at_monotonic=None,
                result_digest=None,
            )


def _job_result_digest(record: Mapping[str, object]) -> str:
    """Fingerprint a delivered job's terminal evidence record.

    The ledger requires a result digest for every COMPLETED job terminal;
    instance evidence records carry the delivery facts (rows moved, completion
    time), so the digest is the canonical fingerprint of that delivery.
    """
    payload = {key: record[key] for key in sorted(record) if key != "at"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


class InstanceWorkloadRuntime:
    """Core workload protocol around one instance driver plus its core ledger.

    Transaction facts come from the instance ``BusinessLedger`` (translated at
    drain time). Deliverable job records come from the instance evidence
    chain, which must carry ``job_planned`` / ``job_terminal`` records with the
    job identity and delivery truth; a declared deliverable without its
    instance-side job records fails the run loudly instead of silently
    shrinking the delivery checklist.
    """

    def __init__(
        self,
        driver,
        trusted_ledger: TrustedLedger,
        evidence,
        *,
        transaction_service_id: str,
        horizon_seconds: float,
        input_stop_seconds: float,
        job_service_ids: Mapping[str, str] = (),
        job_ids: tuple[str, ...] = (),
        job_deadline_seconds: Mapping[str, float] = (),
    ):
        self._driver = driver
        self._evidence = evidence
        self.trusted_ledger = trusted_ledger
        self._transaction_service_id = transaction_service_id
        self._horizon_seconds = float(horizon_seconds)
        self._input_stop_seconds = float(input_stop_seconds)
        self._job_service_ids = dict(job_service_ids)
        self._job_ids = tuple(job_ids)
        self._job_deadline_seconds = dict(job_deadline_seconds)
        self._stopped = False
        self._scoring_end_monotonic: float | None = None
        self._input_stop_monotonic: float | None = None

    @property
    def driver(self):
        return self._driver

    @property
    def scoring_end_monotonic(self) -> float:
        if self._scoring_end_monotonic is None:
            raise ValueError("Instance workload runtime has no scoring end before warmup completes")
        return self._scoring_end_monotonic

    @property
    def input_stop_monotonic(self) -> float:
        if self._input_stop_monotonic is None:
            raise ValueError("Instance workload runtime has no input stop before warmup completes")
        return self._input_stop_monotonic

    def start(self) -> None:
        self._driver.start()

    def wait_for_warmup(self) -> float:
        scoring_started = self._driver.wait_for_warmup()
        self._scoring_end_monotonic = scoring_started + self._horizon_seconds
        self._input_stop_monotonic = scoring_started + self._input_stop_seconds
        return scoring_started

    def stop_new_requests(self) -> None:
        self._driver.stop_new_requests()

    def drain(self) -> None:
        if self._stopped:
            return
        self._driver.stop_and_drain()
        self._stopped = True
        translate_business_ledger(
            self._driver.ledger,
            self.trusted_ledger,
            service_id=self._transaction_service_id,
        )
        self._translate_jobs()

    def stop(self) -> None:
        self.drain()

    def _translate_jobs(self) -> None:
        planned: dict[str, dict] = {}
        terminals: dict[str, dict] = {}
        for envelope in self._evidence_records():
            record = envelope["record"] if "record" in envelope else envelope
            kind = record.get("kind")
            if kind == "job_planned":
                planned[str(record["job_id"])] = record
            elif kind == "job_terminal":
                terminals[str(record["job_id"])] = record
        for job_id in self._job_ids:
            if job_id not in planned:
                # A deliverable whose job never started is a business result:
                # evaluation reports the checklist item as missing.
                continue
            plan = planned[job_id]
            submitted_at = float(plan["at"])
            deadline_seconds = self._job_deadline_seconds.get(job_id)
            if deadline_seconds is None:
                raise ValueError(
                    "Declared deliverable job has no deadline contract: "
                    f"job_id={job_id!r}, known={sorted(self._job_deadline_seconds)!r}"
                )
            self.trusted_ledger.append_job_planned(
                job_id=job_id,
                service_id=self._job_service_ids.get(job_id, self._transaction_service_id),
                job_kind=str(plan.get("job_kind", job_id)),
                batch_version=None,
                input_snapshot=None,
                submitted_at_monotonic=submitted_at,
                deadline_at_monotonic=submitted_at + deadline_seconds,
            )
            terminal_record = terminals.get(job_id)
            if terminal_record is None:
                # The job is still in flight at the scoring end: the core
                # ledger seals it as an explicit outstanding loss.
                continue
            status = str(terminal_record.get("status", ""))
            if status == "completed":
                completed_at = terminal_record.get("completed_at")
                self.trusted_ledger.append_job_terminal(
                    job_id=job_id,
                    terminal=LedgerTerminal.COMPLETED,
                    delivered_at_monotonic=(
                        float(completed_at) if completed_at is not None else None
                    ),
                    result_digest=_job_result_digest(terminal_record),
                )
            else:
                self.trusted_ledger.append_job_terminal(
                    job_id=job_id,
                    terminal=LedgerTerminal.INCOMPLETE_CANCELLED,
                    delivered_at_monotonic=None,
                    result_digest=None,
                )

    def _evidence_records(self) -> list[dict]:
        import json

        records = []
        with self._evidence.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                records.append(json.loads(line))
        return records

    def ledgers(self) -> Mapping[str, TrustedLedger]:
        return {"commerce": self.trusted_ledger}

    def baseline_facts(self) -> Mapping[str, object]:
        return self._driver.baseline_facts()


class HtapWorkloadRuntimeAdapter:
    """Core workload protocol around one htap instance runtime.

    The instance runtime already speaks the lifecycle protocol; the adapter
    narrows the ledger surface to the engine contract. The instance's external
    JSONL ledgers (export pages, commit watermarks, report deliveries) stay
    instance-internal evidence consumed through SQL verifiers — the engine
    seal/verify loop and the evaluator only ever see the core-shaped trusted
    ledger.
    """

    def __init__(self, runtime, *, horizon_seconds: float, input_stop_seconds: float):
        self._runtime = runtime
        self._horizon_seconds = float(horizon_seconds)
        self._input_stop_seconds = float(input_stop_seconds)
        self._scoring_end_monotonic: float | None = None
        self._input_stop_monotonic: float | None = None

    @property
    def scoring_end_monotonic(self) -> float:
        if self._scoring_end_monotonic is None:
            raise ValueError("Htap workload runtime has no scoring end before warmup completes")
        return self._scoring_end_monotonic

    @property
    def input_stop_monotonic(self) -> float:
        if self._input_stop_monotonic is None:
            raise ValueError("Htap workload runtime has no input stop before warmup completes")
        return self._input_stop_monotonic

    def start(self) -> None:
        self._runtime.start()

    def wait_for_warmup(self) -> float:
        scoring_started = self._runtime.wait_for_warmup()
        self._scoring_end_monotonic = scoring_started + self._horizon_seconds
        self._input_stop_monotonic = scoring_started + self._input_stop_seconds
        return scoring_started

    def stop_new_requests(self) -> None:
        self._runtime.stop_new_requests()

    def drain(self) -> None:
        self._runtime.drain()

    def stop(self) -> None:
        self._runtime.stop()

    def ledgers(self) -> Mapping[str, TrustedLedger]:
        ledgers = self._runtime.ledgers()
        trusted = ledgers.get("trusted")
        if not isinstance(trusted, TrustedLedger):
            raise ValueError(
                "Htap instance runtime exposes no core trusted ledger: "
                f"ledger_keys={sorted(ledgers)!r}"
            )
        return {"trusted": trusted}

    def baseline_facts(self) -> Mapping[str, object]:
        return self._runtime.baseline_facts()


_JOB_TERMINALS = {
    "completed": LedgerTerminal.COMPLETED,
    "incomplete_timeout": LedgerTerminal.INCOMPLETE_TIMEOUT,
    "incomplete_error": LedgerTerminal.INCOMPLETE_ERROR,
    "incomplete_cancelled": LedgerTerminal.INCOMPLETE_CANCELLED,
    "incomplete_outstanding": LedgerTerminal.INCOMPLETE_OUTSTANDING,
}


def evidence_ledger_path(evidence_root: Path, run_id: str, name: str) -> Path:
    """Deterministic per-run evidence path beneath the run output directory."""

    return Path(evidence_root) / "persistent-scenario-evidence" / run_id / f"{name}.jsonl"
