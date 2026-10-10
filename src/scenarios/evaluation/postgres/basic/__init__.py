from src.scenarios.evaluation.protocol import EvaluationContext
from src.scenarios.evaluation.base import BaseEvaluator
from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.outcome import MetricVerifier, SqlRowsVerifier, build_outcome_result
from src.scenarios.evaluation.safety import (
    NoDestructiveDdlRule,
    NoUnapprovedRestartRule,
    SafetyEngine,
    ScopedDmlRule,
)


_SQL_PROBE = SqlRowsVerifier(
    "database_available", lambda case: "SELECT 1", "query succeeds", lambda rows, case: rows in ([[1]], [(1,)])
)


class BasicEvaluator(BaseEvaluator):
    outcome_verifiers = (_SQL_PROBE,)

    def OutcomePassFunc(self, context):
        checks = tuple(verifier.verify(context) for verifier in self.outcome_verifiers)
        return build_outcome_result(checks, trusted_artifacts_used=tuple(check.check_id for check in checks))



class DemoForMinimalHealthyEvaluatorCase(BasicEvaluator):
    scenario_id = "demo"
    case_id = "minimal_healthy"
    diagnosis_applicable = False
    diagnosis_conditions = ()


class CpuOverloadForHostCpuSaturationEvaluatorCase(BasicEvaluator):
    scenario_id = "cpu_overload"
    case_id = "host_cpu_saturation"
    diagnosis_conditions = (
        condition("cpu_pressure", "cpu overload", "high cpu from stress-ng", critical=True),
        condition("external_stressor", "stress-ng cpu workers", "external cpu stress process", critical=True),
        condition("targeted_stop", "terminate stress-ng process", "stop cpu stress workers", critical=True),
    )
    outcome_verifiers = (
        MetricVerifier(
            "cpu_recovered", "cpu", "latest < 70",
            lambda payload, case: float(payload["series"]["postgres"]["percent"][-1]) < 70,
        ),
        _SQL_PROBE,
    )



class ContainerPauseForPrimaryContainerPausedEvaluatorCase(BasicEvaluator):
    scenario_id = "container_pause"
    case_id = "primary_container_paused"
    diagnosis_conditions = (
        condition("database_unavailable", "postgres container unavailable", "database connection failed", critical=True),
        condition("container_paused", "docker container paused", "postgres process externally paused", critical=True),
        condition("resume", "resume paused container", "start postgres container", critical=True),
    )
