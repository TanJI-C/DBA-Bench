from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Mapping

from src.agent_language import agent_text
from src.database.system import DatabaseSystem
from src.execution.specs import PostgresCaseRuntime, TiDBCaseRuntime

if TYPE_CHECKING:
    from src.scenarios.evaluation.base import BaseEvaluator
    from src.scenarios.frozen_history import FrozenHistorySpec

from src.protocols.report import StructuredReport
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.workloads.specs import BackgroundWorkloadSpec


@dataclass(frozen=True, slots=True, kw_only=True)
class DifficultyCalibration:
    diagnostic_depth: int
    environmental_complexity: float
    reference_run_ids: tuple[str, ...]
    protocol_version: str = "difficulty-v2"

    def __post_init__(self) -> None:
        if self.diagnostic_depth < 1:
            raise ValueError(f"difficulty diagnostic_depth must be >= 1: {self.diagnostic_depth}")
        if not 0 <= self.environmental_complexity <= 1:
            raise ValueError(
                f"difficulty environmental_complexity must be within [0, 1]: {self.environmental_complexity}"
            )
        if not self.reference_run_ids:
            raise ValueError("difficulty requires a reference run")

    @property
    def label(self) -> str:
        return "hard" if self.diagnostic_depth > 2 and self.environmental_complexity >= 0.5 else "easy"

    def as_dict(self) -> dict[str, object]:
        return {
            "protocol_version": self.protocol_version,
            "diagnostic_depth": self.diagnostic_depth,
            "environmental_complexity": self.environmental_complexity,
            "difficulty": self.label,
            "reference_run_ids": list(self.reference_run_ids),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class ScenarioCase:
    case_id: str
    case_no: int
    evaluator: type["BaseEvaluator"]
    title: str
    alert: str
    initial_state: Mapping[str, object]
    expected_target: Mapping[str, object]
    background_workload: BackgroundWorkloadSpec
    reference_report: Mapping[str, object]
    knowledge_contract: Mapping[str, object] | None = None
    frozen_history: "FrozenHistorySpec | None" = None
    frozen_history_adapter: object | None = None
    metric_history_adapter_config: Mapping[str, object] | None = None
    difficulty: DifficultyCalibration | None = None
    # English variant of a Chinese ``alert``; None when ``alert`` is already English.
    alert_en: str | None = None

    def __post_init__(self) -> None:
        StructuredReport.from_mapping(self.reference_report)
        if self.frozen_history is not None:
            self.frozen_history.validate(self.background_workload)

    def agent_alert(self) -> str:
        """The alert in the run's agent language (``alert_en`` when English is selected)."""
        if self.alert_en is None:
            return self.alert
        return agent_text(zh=self.alert, en=self.alert_en)




@dataclass(frozen=True, slots=True, kw_only=True)
class PostgresScenarioCase(ScenarioCase):
    system: ClassVar[DatabaseSystem] = DatabaseSystem.POSTGRESQL
    runtime: PostgresCaseRuntime = field(default_factory=PostgresCaseRuntime)


@dataclass(frozen=True, slots=True, kw_only=True)
class TiDBScenarioCase(ScenarioCase):
    system: ClassVar[DatabaseSystem] = DatabaseSystem.TIDB
    runtime: TiDBCaseRuntime


@dataclass(frozen=True, slots=True, kw_only=True)
class FaultPlan:
    injector_type: type[BaseFaultInjector]
    config: Mapping[str, object]


class BaseScenario(ABC):
    system: DatabaseSystem
    scenario_id: str
    description: str
    cases: tuple[ScenarioCase, ...]

    def __init__(self) -> None:
        case_ids = [case.case_id for case in self.cases]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError(f"Scenario {self.scenario_id!r} has duplicate case IDs: {case_ids}")
        case_numbers = [case.case_no for case in self.cases]
        expected_numbers = list(range(len(self.cases)))
        if case_numbers != expected_numbers:
            raise ValueError(
                f"Scenario {self.scenario_id!r} case_no values must be contiguous: "
                f"expected={expected_numbers}, actual={case_numbers}"
            )
        for case in self.cases:
            if case.system is not self.system:
                raise ValueError(
                    f"Scenario/case system mismatch: scenario={self.scenario_id!r}, "
                    f"scenario_system={self.system.value!r}, case={case.case_id!r}, "
                    f"case_system={case.system.value!r}"
                )
            if case.evaluator.scenario_id != self.scenario_id or case.evaluator.case_id != case.case_id:
                raise ValueError(
                    f"Scenario/evaluator identity mismatch: scenario={self.scenario_id!r}, "
                    f"case={case.case_id!r}, evaluator={case.evaluator.__name__}, "
                    f"evaluator_identity={case.evaluator.scenario_id!r}/{case.evaluator.case_id!r}"
                )

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(
            f"Scenario {self.scenario_id!r} is stateless; move {name!r} to a ScenarioCase or CaseRun"
        )

    def get_case(self, case_id: str) -> ScenarioCase:
        matches = [case for case in self.cases if case.case_id == case_id]
        if len(matches) != 1:
            available = ", ".join(case.case_id for case in self.cases)
            raise KeyError(
                f"Scenario {self.scenario_id!r} expected exactly one case "
                f"matching {case_id!r}; available cases: {available}"
            )
        return matches[0]

    @abstractmethod
    def build_fault_plan(self, case: ScenarioCase) -> tuple[FaultPlan, ...]:
        raise NotImplementedError


class PostgresScenario(BaseScenario):
    system = DatabaseSystem.POSTGRESQL


class TiDBScenario(BaseScenario):
    system = DatabaseSystem.TIDB


@dataclass(slots=True)
class InjectionRecord:
    plan: FaultPlan
    injector: BaseFaultInjector
    context: FaultLifecycleContext
    evidence: Mapping[str, object]
    state: "InjectionState" = field(default_factory=lambda: InjectionState.PLANNED)


class InjectionState(Enum):
    PLANNED = "planned"
    STARTING = "starting"
    RUNNING = "running"
    OBSERVING = "observing"
    READY = "ready"
    QUIESCING = "quiescing"
    QUIESCED = "quiesced"
    RECOVERING = "recovering"
    RECOVERED = "recovered"


@dataclass(slots=True)
class CaseRun:
    run_id: str
    scenario: BaseScenario
    case: ScenarioCase
    env: object
    injections: list[InjectionRecord] = field(default_factory=list)
    workload_runners: list[object] = field(default_factory=list)
    action_history: list[dict] = field(default_factory=list)
    turn_history: list[dict] = field(default_factory=list)
    model_usage: list[dict] = field(default_factory=list)
    background_workload_planned: Mapping[str, object] = field(default_factory=dict)
    background_workload_observed: Mapping[str, object] = field(default_factory=dict)
    safety_baseline: dict[str, object] = field(default_factory=dict)
    metric_history: Mapping[str, object] = field(default_factory=dict)
    evaluation_cache: dict[str, object] = field(default_factory=dict)
