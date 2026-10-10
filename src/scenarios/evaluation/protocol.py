"""Strict structured submission report used by the evaluator protocol."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from src.scenarios.base import CaseRun


STRUCTURED_REPORT_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["diagnosis", "outcome", "summary"],
    "properties": {
        "diagnosis": {
            "type": "object",
            "additionalProperties": False,
            "required": ["conditions"],
            "properties": {
                "conditions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["type", "factor", "entity", "evidence"],
                        "properties": {
                            "type": {"type": "string"},
                            "factor": {"type": "string"},
                            "entity": {"type": "string"},
                            "evidence": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                }
            },
        },
        "outcome": {
            "type": "object",
            "additionalProperties": False,
            "required": ["changes", "verification"],
            "properties": {
                "changes": {"type": "array", "items": {"type": "string"}},
                "verification": {"type": "array", "items": {"type": "string"}},
                "plan": {
                    "type": "object",
                    "description": "Optional task-specific structured plan artifact.",
                    "additionalProperties": True,
                },
            },
        },
        "summary": {"type": "string"},
    },
}


def structured_submission(
    *,
    factor: str,
    entity: str,
    evidence: list[str],
    changes: list[str],
    verification: list[str],
    summary: str,
) -> dict:
    report = {
        "diagnosis": {
            "conditions": [{
                "type": "root_cause",
                "factor": factor,
                "entity": entity,
                "evidence": evidence,
            }]
        },
        "outcome": {"changes": changes, "verification": verification},
        "summary": summary,
    }
    StructuredReport.from_mapping(report)
    return {"report": report}


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"report field {field!r} must be a non-empty string")
    return value


def _require_string_list(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise TypeError(f"report field {field!r} must be a list of strings")
    return tuple(value)


@dataclass(frozen=True, slots=True)
class DiagnosisCondition:
    type: str
    factor: str
    entity: str
    evidence: tuple[str, ...]

    @classmethod
    def from_mapping(cls, value: object) -> "DiagnosisCondition":
        if not isinstance(value, Mapping):
            raise TypeError("diagnosis condition must be an object")
        expected = {"type", "factor", "entity", "evidence"}
        extra = set(value) - expected
        missing = expected - set(value)
        if missing or extra:
            raise ValueError(
                f"diagnosis condition fields mismatch: missing={sorted(missing)}, extra={sorted(extra)}"
            )
        return cls(
            type=_require_string(value["type"], "diagnosis.conditions[].type"),
            factor=_require_string(value["factor"], "diagnosis.conditions[].factor"),
            entity=_require_string(value["entity"], "diagnosis.conditions[].entity"),
            evidence=_require_string_list(value["evidence"], "diagnosis.conditions[].evidence"),
        )


@dataclass(frozen=True, slots=True)
class DiagnosisReport:
    conditions: tuple[DiagnosisCondition, ...]


@dataclass(frozen=True, slots=True)
class OutcomeReport:
    changes: tuple[str, ...]
    verification: tuple[str, ...]
    plan: Mapping[str, object] | None = None


@dataclass(frozen=True, slots=True)
class StructuredReport:
    diagnosis: DiagnosisReport
    outcome: OutcomeReport
    summary: str

    @classmethod
    def from_mapping(cls, value: object) -> "StructuredReport":
        if not isinstance(value, Mapping):
            raise TypeError("submission report must be an object")
        expected = {"diagnosis", "outcome", "summary"}
        extra = set(value) - expected
        missing = expected - set(value)
        if missing or extra:
            raise ValueError(
                f"submission report fields mismatch: missing={sorted(missing)}, extra={sorted(extra)}"
            )
        diagnosis = value["diagnosis"]
        outcome = value["outcome"]
        if not isinstance(diagnosis, Mapping) or set(diagnosis) != {"conditions"}:
            raise ValueError("report diagnosis must contain exactly the conditions field")
        if not isinstance(outcome, Mapping):
            raise TypeError("report outcome must be an object")
        expected_outcome = {"changes", "verification"}
        extra_outcome = set(outcome) - (expected_outcome | {"plan"})
        missing_outcome = expected_outcome - set(outcome)
        if missing_outcome or extra_outcome:
            raise ValueError(
                "report outcome fields mismatch: "
                f"missing={sorted(missing_outcome)}, extra={sorted(extra_outcome)}"
            )
        conditions = diagnosis["conditions"]
        if not isinstance(conditions, list):
            raise TypeError("report diagnosis.conditions must be a list")
        plan = outcome.get("plan")
        if plan is not None and not isinstance(plan, Mapping):
            raise TypeError("report outcome.plan must be an object when present")
        return cls(
            diagnosis=DiagnosisReport(tuple(DiagnosisCondition.from_mapping(item) for item in conditions)),
            outcome=OutcomeReport(
                changes=_require_string_list(outcome["changes"], "outcome.changes"),
                verification=_require_string_list(outcome["verification"], "outcome.verification"),
                plan=dict(plan) if plan is not None else None,
            ),
            summary=_require_string(value["summary"], "summary"),
        )


def structured_reference_report(
    *,
    case_id: str,
    factors: tuple[str, ...],
    changes: tuple[str, ...],
    verification: tuple[str, ...],
    summary: str,
) -> dict:
    report = {
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": factor,
                    "entity": case_id,
                    "evidence": [f"reference path observed {factor}"],
                }
                for factor in factors
            ]
        },
        "outcome": {"changes": list(changes), "verification": list(verification)},
        "summary": summary,
    }
    StructuredReport.from_mapping(report)
    return report


EMPTY_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {"changes": [], "verification": []},
    "summary": "No diagnosis or remediation was attempted.",
}

StructuredReport.from_mapping(EMPTY_REPORT)

UNPARSEABLE_SUBMISSION_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {"changes": [], "verification": []},
    "summary": "Submission was not a schema-valid structured report and was evaluated as a failed claim.",
}

StructuredReport.from_mapping(UNPARSEABLE_SUBMISSION_REPORT)


def parse_submission_report(value: object) -> tuple["StructuredReport", str | None]:
    """Parse an agent submit report, treating schema violations as failed claims.

    Valid submissions keep the strict ``StructuredReport`` contract. A final
    submission that violates the schema must not crash the scenario process:
    it parses into ``UNPARSEABLE_SUBMISSION_REPORT`` so report-dependent DP/OP
    checks fail while system-state Outcome/Safety verifiers keep their existing
    semantics, and the returned reason is recorded in the evaluation result.
    """
    try:
        return StructuredReport.from_mapping(value), None
    except (TypeError, ValueError) as exc:
        return (
            StructuredReport.from_mapping(UNPARSEABLE_SUBMISSION_REPORT),
            f"{type(exc).__name__}: {exc}",
        )


@dataclass(frozen=True, slots=True)
class EvaluationContext:
    """Read-only context shared by Diagnosis, Outcome and Safety passes."""

    case_run: "CaseRun"
    report: StructuredReport
    submission_parse_error: str | None = None

    @property
    def run_id(self) -> str:
        return self.case_run.run_id

    @property
    def scenario_id(self) -> str:
        return self.case_run.scenario.scenario_id

    @property
    def case_id(self) -> str:
        return self.case_run.case.case_id

    @property
    def case_no(self) -> int:
        return self.case_run.case.case_no

    @property
    def action_history(self) -> tuple[dict, ...]:
        return tuple(self.case_run.action_history)

    @property
    def injection_evidence(self) -> Mapping[str, object]:
        return MappingProxyType({
            key: value
            for record in self.case_run.injections
            for key, value in record.evidence.items()
        })
