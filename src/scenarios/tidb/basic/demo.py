from dataclasses import dataclass

from src.scenarios.evaluation.tidb.basic.demo import TidbDemoForMinimalHealthyEvaluatorCase
from src.scenarios.faults import NoopFaultInjector

from ...base import (
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbDemoCase(TiDBScenarioCase):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbDemoForMinimalHealthyScenarioCase(TidbDemoCase):
    pass


_TIDB_DEMO_CASE = TidbDemoForMinimalHealthyScenarioCase(
    case_id="minimal_healthy",
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
    evaluator=TidbDemoForMinimalHealthyEvaluatorCase,
    title="Minimal TiDB demo scenario without faults.",
    alert="告警或提示：TiDB 集群运行正常，请完成基础健康检查。",
    initial_state={"status": "healthy"},
    expected_target={"status": "healthy"},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(release=TIDB_V8_1_0, pd_count=1, tikv_count=1, tidb_count=1),
)


class TidbDemoScenario(TiDBScenario):
    scenario_id = "tidb_demo"
    description = "Minimal TiDB demo scenario without faults."
    cases = (_TIDB_DEMO_CASE,)

    def build_fault_plan(self, case: TidbDemoCase) -> tuple[FaultPlan, ...]:
        return (FaultPlan(injector_type=NoopFaultInjector, config={}),)
