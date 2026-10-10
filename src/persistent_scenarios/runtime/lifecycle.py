"""Persistent Scenario runtime lifecycle vocabulary and arrival evidence.

The runtime separates external intent (attempted), actual effect (applied) and
prevention (attempted but blocked by trusted protection). Unknown exceptions
are never wrapped into prevented: they propagate and invalidate the run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from ..model.spec import JSONValue


class FailureClassification(str, Enum):
    AGENT_FAILURE = "agent_failure"
    AGENT_PROVIDER_FAILURE = "agent_provider_failure"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    TOOL_OR_TRACE_FAILURE = "tool_or_trace_failure"
    INVALID_ENVIRONMENT = "invalid_environment"


class EventArrivalStatus(str, Enum):
    PLANNED = "planned"
    APPLIED = "applied"
    PREVENTED = "prevented"
    FAILED = "failed"


class CheckpointReason(str, Enum):
    WARMUP_BASELINE = "warmup_baseline"
    EVENT_ARRIVAL = "event_arrival"
    HORIZON_FINAL = "horizon_final"


# Break-age constants: three independent dynasties.
TRACE_SCHEMA = "persistent_scenario_trace_v2"
EVALUATION_SCHEMA = "persistent_scenario_evaluation_v2"


class IntegrityStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    VERIFICATION_INFRASTRUCTURE_FAILURE = "verification_infrastructure_failure"


class EvidenceStatus(str, Enum):
    CAPTURED = "captured"
    COLLECTOR_FAILURE = "collector_failure"


@dataclass(frozen=True, slots=True)
class EventAttemptEvidence:
    """Proof that the external intent was actually initiated."""

    attempted_at_monotonic: float
    detail: Mapping[str, JSONValue]

    def __post_init__(self) -> None:
        if not isinstance(self.detail, Mapping):
            raise TypeError(f"event attempt detail must be a mapping: value={self.detail!r}")


@dataclass(frozen=True, slots=True)
class AppliedEvidence:
    """Provider-observed impact facts proving the change took effect."""

    observed_at_monotonic: float
    facts: Mapping[str, JSONValue]

    def __post_init__(self) -> None:
        if not isinstance(self.facts, Mapping):
            raise TypeError(f"applied evidence facts must be a mapping: value={self.facts!r}")


@dataclass(frozen=True, slots=True)
class PreventionEvidence:
    """A real attempt blocked by an observed trusted protection state."""

    attempted: EventAttemptEvidence
    mechanism: str
    protection_state: Mapping[str, JSONValue]
    observed_at_monotonic: float

    def __post_init__(self) -> None:
        if not isinstance(self.attempted, EventAttemptEvidence):
            raise TypeError(f"prevention requires attempt evidence: value={self.attempted!r}")
        if not isinstance(self.mechanism, str) or not self.mechanism.strip():
            raise ValueError(f"prevention mechanism must be a non-empty string: value={self.mechanism!r}")
        if not isinstance(self.protection_state, Mapping):
            raise TypeError(f"prevention protection_state must be a mapping: value={self.protection_state!r}")


@dataclass(frozen=True, slots=True)
class ArrivalFacts:
    """Structured arrival result for one Event occurrence."""

    status: EventArrivalStatus
    attempt: EventAttemptEvidence | None
    applied: AppliedEvidence | None
    prevented: PreventionEvidence | None
    arrived_at_monotonic: float

    def __post_init__(self) -> None:
        if not isinstance(self.status, EventArrivalStatus):
            raise TypeError(f"arrival status must be EventArrivalStatus: value={self.status!r}")
        if self.status is EventArrivalStatus.PLANNED:
            raise ValueError("ArrivalFacts cannot be built for a PLANNED event")
        if self.attempt is None:
            raise ValueError(f"arrival requires attempt evidence: status={self.status.value!r}")
        if self.status is EventArrivalStatus.APPLIED:
            if self.applied is None or self.prevented is not None:
                raise ValueError(
                    "applied arrival requires applied evidence and no prevention evidence: "
                    f"applied={self.applied!r}, prevented={self.prevented!r}"
                )
        elif self.status is EventArrivalStatus.PREVENTED:
            if self.prevented is None or self.applied is not None:
                raise ValueError(
                    "prevented arrival requires prevention evidence and no applied evidence: "
                    f"applied={self.applied!r}, prevented={self.prevented!r}"
                )
        elif self.applied is not None or self.prevented is not None:
            raise ValueError(
                f"failed arrival cannot carry applied or prevented evidence: status={self.status.value!r}"
            )


# ---------------------------------------------------------------------------
# Runtime facts: defined in core, built by core/backend,
# consumed by evaluation. Evaluation defines no fact types of its own.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ScoringWindow:
    """The materialized business scoring window, frozen after warmup."""

    scoring_start_monotonic: float
    scoring_end_monotonic: float
    input_stop_monotonic: float

    def __post_init__(self) -> None:
        if not self.scoring_start_monotonic <= self.input_stop_monotonic <= self.scoring_end_monotonic:
            raise ValueError(
                "ScoringWindow must satisfy scoring_start <= input_stop <= scoring_end: "
                f"scoring_start={self.scoring_start_monotonic!r}, input_stop={self.input_stop_monotonic!r}, "
                f"scoring_end={self.scoring_end_monotonic!r}"
            )


@dataclass(frozen=True, slots=True)
class ActionClassification:
    """Backend-provided semantic classification of one agent action."""

    action_class: str
    objects: tuple[str, ...] = ()
    guc_name: str | None = None
    guc_value: str | None = None
    details: Mapping[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.action_class, str) or not self.action_class.strip():
            raise ValueError(f"action_class must be a non-empty string: value={self.action_class!r}")
        if any(not isinstance(obj, str) or not obj.strip() for obj in self.objects):
            raise ValueError(f"action objects must be non-empty strings: value={self.objects!r}")
        if not isinstance(self.details, Mapping):
            raise TypeError(f"action classification details must be a mapping: value={self.details!r}")


@dataclass(frozen=True, slots=True)
class ActionFact:
    """Safety-facing fact for one completed agent environment action."""

    sequence: int
    at_monotonic: float
    action_class: str
    objects: tuple[str, ...]
    guc_name: str | None
    guc_value: str | None
    details: Mapping[str, JSONValue]

    def __post_init__(self) -> None:
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence < 0:
            raise ValueError(f"action fact sequence must be a non-negative integer: value={self.sequence!r}")
        if not isinstance(self.details, Mapping):
            raise TypeError(f"action fact details must be a mapping: value={self.details!r}")


@dataclass(frozen=True, slots=True)
class IntegrityFact:
    """Backend truth-check output for one declared integrity check."""

    check_id: str
    kind: str
    status: IntegrityStatus
    details: Mapping[str, JSONValue]

    def __post_init__(self) -> None:
        if not isinstance(self.check_id, str) or not self.check_id.strip():
            raise ValueError(f"integrity fact check_id must be non-empty: value={self.check_id!r}")
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ValueError(f"integrity fact kind must be non-empty: check_id={self.check_id!r}")
        if not isinstance(self.status, IntegrityStatus):
            raise TypeError(f"integrity fact status must be IntegrityStatus: check_id={self.check_id!r}, value={self.status!r}")
        if not isinstance(self.details, Mapping):
            raise TypeError(f"integrity fact details must be a mapping: check_id={self.check_id!r}, value={self.details!r}")


@dataclass(frozen=True, slots=True)
class RequiredStateEvidence:
    """Final checkpoint sample for one declared required-state check."""

    check_id: str
    status: EvidenceStatus
    facts: Mapping[str, JSONValue]
    captured_at_monotonic: float

    def __post_init__(self) -> None:
        if not isinstance(self.check_id, str) or not self.check_id.strip():
            raise ValueError(f"required-state evidence check_id must be non-empty: value={self.check_id!r}")
        if not isinstance(self.status, EvidenceStatus):
            raise TypeError(
                f"required-state evidence status must be EvidenceStatus: check_id={self.check_id!r}, value={self.status!r}"
            )
        if not isinstance(self.facts, Mapping):
            raise TypeError(f"required-state evidence facts must be a mapping: check_id={self.check_id!r}, value={self.facts!r}")


@dataclass(frozen=True, slots=True)
class RunValidityFact:
    """Runtime conclusion about collection infrastructure and ledger integrity.

    ``ledger_complete=False`` means the collector lost accounts: the run is
    invalid and DP/OP/SP are None. Database business failures never appear
    here - they are business results recorded in the trusted ledgers.
    """

    valid: bool
    classification: str | None
    reason: str | None
    ledger_complete: bool

    def __post_init__(self) -> None:
        if not isinstance(self.valid, bool):
            raise TypeError(f"validity valid must be bool: value={self.valid!r}")
        if not isinstance(self.ledger_complete, bool):
            raise TypeError(f"validity ledger_complete must be bool: value={self.ledger_complete!r}")
        if self.classification is not None:
            FailureClassification(self.classification)
        if not self.valid and self.classification is None:
            raise ValueError("invalid run validity requires a failure classification")


@dataclass(frozen=True, slots=True)
class InputVersions:
    """Version binding every formal result must carry."""

    spec_digest: str
    protocol_version: str
    trace_schema: str
    evaluation_schema: str
    resource_lease_id: str
    calibration_evidence_id: str | None
    code_version: str
