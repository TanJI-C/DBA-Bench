"""Bounded Scenario evaluation context."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Mapping

from src.protocols.report import StructuredReport

if TYPE_CHECKING:
    from src.scenarios.base import CaseRun


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
