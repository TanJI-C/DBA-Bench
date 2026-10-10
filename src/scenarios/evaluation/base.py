"""Unified evaluator lifecycle for the DP/OP/SP protocol."""

from abc import ABC
from typing import TYPE_CHECKING, Any

from src.scenarios.evaluation.protocol import (
    EvaluationContext,
    parse_submission_report,
)
from src.scenarios.evaluation.diagnosis import (
    DiagnosisMatchingStrategy,
    ExactDiagnosisMatcher,
    ExpectedCondition,
)
from src.scenarios.evaluation.efficiency import EfficiencyCalculator
from src.scenarios.evaluation.outcome import CompositeOutcomeVerifier, OutcomeVerifier
from src.scenarios.evaluation.safety import (
    FinalStateSafetyVerifier,
    SafetyEngine,
    SafetyRule,
    default_safety_rules,
)

if TYPE_CHECKING:
    from src.scenarios.base import CaseRun


def evaluation_passed(result: dict) -> bool:
    diagnosis = result["DiagnosisPass"]
    return (
        (diagnosis is True or diagnosis is None)
        and result["OutcomePass"] is True
        and result["SafePass"] is True
    )


class BaseEvaluator(ABC):
    scenario_id: str
    case_id: str
    diagnosis_applicable: bool = True
    diagnosis_conditions: tuple[ExpectedCondition, ...]
    outcome_verifiers: tuple[OutcomeVerifier, ...]
    safety_rules: tuple[SafetyRule, ...] = default_safety_rules()
    final_state_safety_verifiers: tuple[FinalStateSafetyVerifier, ...] = ()

    def __init__(self, env: object, diagnosis_matcher: DiagnosisMatchingStrategy | None = None):
        self.env = env
        self.diagnosis_matcher = diagnosis_matcher or ExactDiagnosisMatcher()

    def evaluate(self, case_run: "CaseRun") -> dict[str, Any]:
        if case_run.case.evaluator is not type(self):
            raise TypeError(
                f"{case_run.scenario.scenario_id}/{case_run.case.case_id} binds "
                f"{case_run.case.evaluator}, got {type(self)}"
            )
        if self.scenario_id != case_run.scenario.scenario_id or self.case_id != case_run.case.case_id:
            raise ValueError(
                f"evaluator identity mismatch: evaluator={self.scenario_id}/{self.case_id}, "
                f"case={case_run.scenario.scenario_id}/{case_run.case.case_id}"
            )
        submissions = [
            action.get("args")
            for action in case_run.action_history
            if action.get("api") == "submit"
        ]
        if len(submissions) != 1:
            raise ValueError(
                f"expected exactly one submit report for {case_run.run_id}, got {len(submissions)}"
            )
        report, parse_error = parse_submission_report(submissions[0])
        context = EvaluationContext(case_run, report, submission_parse_error=parse_error)
        self._reset_trusted_session_role(context)
        diagnosis = self.DiagnosisPassFunc(context)
        outcome = self.OutcomePassFunc(context)
        safety = self.SafePassFunc(context, outcome)
        if parse_error is not None:
            diagnosis = {
                **diagnosis,
                "report_valid": False,
                "submission_parse_error": parse_error,
            }
        return {
            "run_id": context.run_id,
            "scenario_id": context.scenario_id,
            "case_id": context.case_id,
            "case_no": context.case_no,
            "evaluator": type(self).__name__,
            "DiagnosisPass": diagnosis["DiagnosisPass"],
            "OutcomePass": outcome["OutcomePass"],
            "SafePass": safety["SafePass"],
            "diagnosis": diagnosis,
            "outcome": outcome,
            "safety": safety,
            "efficiency": EfficiencyCalculator().calculate(context),
        }

    def _reset_trusted_session_role(self, context: EvaluationContext) -> None:
        """Outcome and safety verification must read final state as the trusted
        operator role. Agents may legally probe with SET ROLE and leave the
        shared session under a constrained role; role-parameterized catalog
        checks still work there, but visibility-filtered catalogs such as
        information_schema would hide objects and corrupt verification."""
        system = getattr(context.case_run.scenario, "system", None)
        system_value = getattr(system, "value", system)
        if system_value != "postgresql":
            return
        for statement in ("RESET SESSION AUTHORIZATION;", "RESET ROLE;"):
            try:
                context.case_run.env.execute_sql(statement)
            except Exception:
                # Best-effort trusted-session restore; fakes and already-clean
                # sessions must not break evaluation. Real role leaks are the
                # failure mode this reset exists to remove.
                continue

    def DiagnosisPassFunc(self, context: EvaluationContext) -> dict[str, Any]:
        return self.diagnosis_matcher.match(
            self.diagnosis_conditions,
            context.report,
            applicable=self.diagnosis_applicable,
        )

    def OutcomePassFunc(self, context: EvaluationContext) -> dict[str, Any]:
        return CompositeOutcomeVerifier(self.outcome_verifiers).verify_all(context)

    def SafePassFunc(self, context: EvaluationContext, outcome_result: dict[str, Any]) -> dict[str, Any]:
        return SafetyEngine(self.safety_rules, self.final_state_safety_verifiers).evaluate(context, outcome_result)

    def capture_safety_baseline(self, case_run: "CaseRun") -> None:
        if case_run.safety_baseline:
            raise ValueError(f"safety baseline already captured for run={case_run.run_id}")
        case_run.safety_baseline.update({
            verifier.verifier_id: verifier.capture(case_run.env, case_run.case)
            for verifier in self.final_state_safety_verifiers
        })
