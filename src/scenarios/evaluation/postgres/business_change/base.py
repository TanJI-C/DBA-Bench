import json

from src.scenarios.evaluation.protocol import EvaluationContext
from src.scenarios.evaluation.base import BaseEvaluator
from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.outcome import REPORT_OUTCOME_FIELDS, ReportTermsVerifier, SqlRowsVerifier, SqlScalarVerifier, build_outcome_result


def _outcome(evaluator, context):
    checks = tuple(verifier.verify(context) for verifier in evaluator.outcome_verifiers)
    report_ids = {v.check_id for v in evaluator.outcome_verifiers if isinstance(v, ReportTermsVerifier)}
    return build_outcome_result(
        checks,
        report_fields_used=REPORT_OUTCOME_FIELDS if report_ids else (),
        trusted_artifacts_used=tuple(c.check_id for c in checks if c.check_id not in report_ids),
    )


class BusinessChangeEvaluator(BaseEvaluator):
    diagnosis_applicable = False

    def OutcomePassFunc(self, context):
        return _outcome(self, context)
