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
class ContainerPauseCase(PostgresScenarioCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class ContainerPauseForPrimaryContainerPausedScenarioCase(ContainerPauseCase):
    pass

_CONTAINERPAUSESCENARIO_CASE = ContainerPauseForPrimaryContainerPausedScenarioCase(
    case_id='primary_container_paused',
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [],
            "verification": []
        },
        "summary": "No diagnosis or remediation was attempted."
    },
    case_no=0,
    evaluator=ContainerPauseForPrimaryContainerPausedEvaluatorCase,
    title='Simulates container freeze via docker pause.',
    alert='告警或提示：Simulates container freeze via docker pause.',
    alert_en="Alert or notice: Simulates container freeze via docker pause.",
    initial_state={'status': 'healthy'},
    expected_target={'status': 'recovered'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
)


import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import (
    PgQueryPerfFaultFingerprintProbe,
    _cancel_open_connection,
    _join_thread,
    _json_object,
    _json_response,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)

class PrimaryContainerPausedInjector(BaseFaultInjector):
    """
    通过 docker pause/unpause 模拟容器级别的"冻结"故障。
    目标容器由 env.container_name 提供。
    """

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._pause(env)

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._pause(env)

    def _pause(self, env) -> None:
        import subprocess
        container_name = env.deployment.container_name
        self._container_name = container_name
        print(f"[FaultInjector:PrimaryContainerPausedInjector] Pausing container '{container_name}'...")
        subprocess.run(
            ["docker", "pause", container_name],
            check=True,
            capture_output=True,
        )

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {}

    def quiesce(self, context: FaultLifecycleContext):
        pass

    def recover(self, context: FaultLifecycleContext):
        import subprocess
        print(f"[FaultInjector:PrimaryContainerPausedInjector] Unpausing container '{self._container_name}'...")
        subprocess.run(
            ["docker", "unpause", self._container_name],
            check=True,
            capture_output=True,
        )
class ContainerPauseScenario(PostgresScenario):
    scenario_id = 'container_pause'
    description = 'Simulates container freeze via docker pause.'
    cases = (_CONTAINERPAUSESCENARIO_CASE,)

    def build_fault_plan(self, case: ContainerPauseCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PrimaryContainerPausedInjector,
                config={
                },
            ),
        )
