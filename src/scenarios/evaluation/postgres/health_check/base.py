from src.scenarios.evaluation.protocol import EvaluationContext
from src.scenarios.evaluation.base import BaseEvaluator
from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.outcome import (
    InstanceActionVerifier,
    OutcomeCheck,
    REPORT_OUTCOME_FIELDS,
    ReportTermsVerifier,
    SqlRowsVerifier,
    SqlScalarVerifier,
    build_outcome_result,
)
from src.scenarios.evaluation.safety import (
    AllowedSqlTargetsRule,
    NoDestructiveDdlRule,
    NoUnapprovedRestartRule,
    ProtectedSqlTargetRule,
    SafetyEngine,
    ScopedDmlRule,
    TargetedSessionTerminationRule,
)


def _outcome(evaluator, context):
    checks = tuple(verifier.verify(context) for verifier in evaluator.outcome_verifiers)
    report_ids = {
        verifier.check_id for verifier in evaluator.outcome_verifiers if isinstance(verifier, ReportTermsVerifier)
    }
    return build_outcome_result(
        checks,
        report_fields_used=REPORT_OUTCOME_FIELDS if report_ids else (),
        trusted_artifacts_used=tuple(check.check_id for check in checks if check.check_id not in report_ids),
    )


def _safety(*extra):
    return (
        NoDestructiveDdlRule(),
        ScopedDmlRule(),
        NoUnapprovedRestartRule(),
        TargetedSessionTerminationRule(),
        *extra,
    )


class HealthCheckEvaluator(BaseEvaluator):
    def OutcomePassFunc(self, context):
        return _outcome(self, context)


def _sql_array(values):
    return "ARRAY[" + ",".join("'" + value.replace("'", "''") + "'" for value in values) + "]"
