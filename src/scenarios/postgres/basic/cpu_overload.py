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
class CpuOverloadCase(PostgresScenarioCase):
    workers: int

@dataclass(frozen=True, slots=True, kw_only=True)
class CpuOverloadForHostCpuSaturationScenarioCase(CpuOverloadCase):
    pass

_CPUOVERLOADSCENARIO_CASE = CpuOverloadForHostCpuSaturationScenarioCase(
    case_id='host_cpu_saturation',
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
    evaluator=CpuOverloadForHostCpuSaturationEvaluatorCase,
    title='Simulates CPU overload on a PostgreSQL container via stress-ng.',
    alert='告警或提示：Simulates CPU overload on a PostgreSQL container via stress-ng.',
    alert_en="Alert or notice: Simulates CPU overload on a PostgreSQL container via stress-ng.",
    initial_state={'status': 'healthy', 'metric_cpu_percent': 15},
    expected_target={'status': 'recovered', 'metric_cpu_percent': '< 70'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    workers=4,
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

class HostCpuSaturationInjector(BaseFaultInjector):
    """
    基于 stress-ng 的 CPU 负载注入器（单机 PostgreSQL 场景使用）。
    通过 stress-ng --cpu N 让指定核心打满。
    目标容器由 env.container_name 提供。
    """

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._run(config, env)

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._run(config, env)

    def _run(self, config: Mapping[str, object], env) -> None:
        workers = config['workers']
        container_name = getattr(env, "container_name", None)
        print(f"[FaultInjector:HostCpuSaturationInjector] Injecting CPU stress with {workers} workers on container '{container_name}'...")
        # Demo 中不真实执行 stress-ng，只打印
        print(f"[FaultInjector:HostCpuSaturationInjector] (Simulated) stress-ng --cpu {workers} --timeout 60s")

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {}

    def quiesce(self, context: FaultLifecycleContext):
        pass

    def recover(self, context: FaultLifecycleContext):
        print(f"[FaultInjector:HostCpuSaturationInjector] Stopping CPU stress...")


class CpuOverloadScenario(PostgresScenario):
    scenario_id = 'cpu_overload'
    description = 'Simulates CPU overload on a PostgreSQL container via stress-ng.'
    cases = (_CPUOVERLOADSCENARIO_CASE,)

    def build_fault_plan(self, case: CpuOverloadCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=HostCpuSaturationInjector,
                config={
                    'workers': case.workers,
                },
            ),
        )
