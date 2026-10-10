from src.scenarios.evaluation.protocol import EvaluationContext
from src.scenarios.evaluation.base import BaseEvaluator
from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.outcome import (
    ActionOrderVerifier,
    EventuallySqlScalarVerifier,
    SqlRowsVerifier,
    SqlScalarVerifier,
    build_outcome_result,
)
from src.scenarios.evaluation.safety import (
    NoDestructiveDdlRule,
    NoUnapprovedRestartRule,
    ProtectedSqlTargetRule,
    SafetyEngine,
    ScopedDmlRule,
    TargetedSessionTerminationRule,
)


def _outcome(evaluator, context):
    checks = tuple(verifier.verify(context) for verifier in evaluator.outcome_verifiers)
    return build_outcome_result(checks, trusted_artifacts_used=tuple(check.check_id for check in checks))
