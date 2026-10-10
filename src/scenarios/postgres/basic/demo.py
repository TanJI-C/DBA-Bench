from dataclasses import dataclass

from src.scenarios.evaluation.postgres.basic import (
    ContainerPauseForPrimaryContainerPausedEvaluatorCase,
    CpuOverloadForHostCpuSaturationEvaluatorCase,
    DemoForMinimalHealthyEvaluatorCase,
)

from src.scenarios.faults import NoopFaultInjector
from ...base import (
    PostgresScenario,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    PostgresScenarioCase,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class DemoCase(PostgresScenarioCase):
    # Demo 用临时健康容器，不参与 fault snapshot 机制
    snapshot_unsafe: bool = True

@dataclass(frozen=True, slots=True, kw_only=True)
class DemoForMinimalHealthyScenarioCase(DemoCase):
    pass

_DEMOSCENARIO_CASE = DemoForMinimalHealthyScenarioCase(
    case_id='minimal_healthy',
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "applied the case-specific remediation"
            ],
            "verification": [
                "verified the case-specific final state"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=DemoForMinimalHealthyEvaluatorCase,
    title='Minimal demo scenario without any faults.',
    alert='告警或提示：Minimal demo scenario without any faults.',
    initial_state={'status': 'healthy'},
    expected_target={'status': 'healthy'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
)


class DemoScenario(PostgresScenario):
    scenario_id = 'demo'
    description = 'Minimal demo scenario without any faults.'
    cases = (_DEMOSCENARIO_CASE,)

    def build_fault_plan(self, case: DemoCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=NoopFaultInjector,
                config={
                },
            ),
        )
