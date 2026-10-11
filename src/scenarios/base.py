import shlex
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import re
from typing import TYPE_CHECKING, ClassVar, Mapping

if TYPE_CHECKING:
    from src.scenarios.evaluation.base import BaseEvaluator

from src.agent_language import agent_text
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.workloads import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    EMPTY_BACKGROUND_WORKLOAD,
)


class DatabaseSystem(str, Enum):
    POSTGRESQL = "postgresql"
    TIDB = "tidb"


@dataclass(frozen=True, slots=True, kw_only=True)
class PostgresRuntimeSpec:
    parameters: tuple[tuple[str, str], ...]

    def as_command_line(self) -> str:
        # pg_ctl parses this shell fragment before passing each -c assignment
        # to postgres; quote values such as log_line_prefix that contain spaces.
        return " ".join(
            f"-c {shlex.quote(f'{name}={value}')}" for name, value in self.parameters
        )

    def parameter(self, name: str) -> str:
        matches = [value for parameter_name, value in self.parameters if parameter_name == name]
        if len(matches) != 1:
            raise KeyError(
                f"PostgreSQL runtime parameter {name!r} must appear exactly once: "
                f"parameters={self.parameters!r}"
            )
        return matches[0]


@dataclass(frozen=True, slots=True, kw_only=True)
class CaseResourceSpec:
    worker_physical_cores: int
    worker_memory_mb: int
    container_cpu_limit: float
    container_memory_mb: int

    def __post_init__(self) -> None:
        values = {
            "worker_physical_cores": self.worker_physical_cores,
            "worker_memory_mb": self.worker_memory_mb,
            "container_cpu_limit": self.container_cpu_limit,
            "container_memory_mb": self.container_memory_mb,
        }
        invalid = {name: value for name, value in values.items() if value <= 0}
        if invalid:
            raise ValueError(f"Case resource contract values must be positive: {invalid}")
        if self.worker_physical_cores < self.container_cpu_limit:
            raise ValueError(
                "Worker CPU reservation must cover its deployment limit: "
                f"worker_physical_cores={self.worker_physical_cores}, "
                f"container_cpu_limit={self.container_cpu_limit}"
            )
        if self.worker_memory_mb < self.container_memory_mb:
            raise ValueError(
                "Worker memory reservation must cover its deployment limit: "
                f"worker_memory_mb={self.worker_memory_mb}, "
                f"container_memory_mb={self.container_memory_mb}"
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class TiDBTopologySpec:
    pd_count: int
    tikv_count: int
    tidb_count: int
    tiflash_count: int = 0
    deferred_tikv_count: int = 0

    def __post_init__(self) -> None:
        counts = {
            "pd": self.pd_count,
            "tikv": self.tikv_count,
            "tidb": self.tidb_count,
        }
        invalid = {node_type: count for node_type, count in counts.items() if count <= 0}
        if invalid:
            raise ValueError(f"TiDB topology node counts must be positive: {invalid}")
        if self.tiflash_count not in (0, 1):
            raise ValueError(
                "TiDB Docker topology supports zero or one TiFlash store: "
                f"tiflash_count={self.tiflash_count}"
            )
        if self.deferred_tikv_count < 0 or self.deferred_tikv_count >= self.tikv_count:
            raise ValueError(
                "TiDB deferred_tikv_count must be non-negative and smaller than tikv_count: "
                f"deferred_tikv_count={self.deferred_tikv_count}, tikv_count={self.tikv_count}"
            )

    @property
    def initial_tikv_count(self) -> int:
        return self.tikv_count - self.deferred_tikv_count

    def count(self, node_type: str) -> int:
        return {
            "pd": self.pd_count,
            "tikv": self.tikv_count,
            "tidb": self.tidb_count,
            "tiflash": self.tiflash_count,
        }[node_type]


@dataclass(frozen=True, slots=True, kw_only=True)
class PostgresCaseRuntime:
    resources: CaseResourceSpec | None = None
    parameters: PostgresRuntimeSpec | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class TiDBCaseRuntime:
    topology: TiDBTopologySpec
    resources: CaseResourceSpec
    release: "TiDBReleaseSpec"
    sql_timeout_seconds: int
    upgrade_release: "TiDBReleaseSpec | None" = None
    image_group_key: str | None = None
    tikv_shared_volume_root: str | None = None
    tikv_store_zones: tuple[str, ...] = ()
    pd_location_labels: tuple[str, ...] = ()
    bootstrap_cache_enabled: bool = True
    tikv_config_writable: bool = False
    tikv_io_rate_limit_strict: bool = False
    # Per-case TiKV server config overrides (TOML section -> key -> value), rendered into
    # every TiKV node's tikv.toml at deploy time. None (default) leaves all deployments
    # byte-identical to the shared template.
    tikv_server_config_overrides: Mapping[str, Mapping[str, object]] | None = None
    readiness_timeout_seconds: int = 1800
    pd_cpu_limit: float = 1.0
    tikv_memory_mb: int = 2048
    tidb_memory_mb: int = 1024

    def __post_init__(self) -> None:
        if self.tikv_memory_mb <= 0:
            raise ValueError(
                f"TiKV memory limit must be positive: tikv_memory_mb={self.tikv_memory_mb}"
            )
        if self.tidb_memory_mb <= 0:
            raise ValueError(f"TiDB memory limit must be positive: tidb_memory_mb={self.tidb_memory_mb}")
        if self.readiness_timeout_seconds <= 0:
            raise ValueError(
                "TiDB readiness timeout must be positive: "
                f"readiness_timeout_seconds={self.readiness_timeout_seconds}"
            )
        if self.pd_cpu_limit <= 0:
            raise ValueError(f"TiDB PD CPU limit must be positive: pd_cpu_limit={self.pd_cpu_limit!r}")
        if self.tikv_server_config_overrides is not None:
            overrides = self.tikv_server_config_overrides
            if not isinstance(overrides, Mapping) or not overrides or not all(
                isinstance(section, str) and bool(section)
                and isinstance(keys, Mapping) and bool(keys)
                for section, keys in overrides.items()
            ):
                raise ValueError(
                    "TiKV server config overrides must be a non-empty two-level "
                    f"TOML section mapping: value={overrides!r}"
                )
    replication: "TiDBReplicationRuntime | None" = None


@dataclass(frozen=True, slots=True, kw_only=True)
class TiDBReplicationRuntime:
    """Auxiliary replication topology owned by a TiDB scenario."""

    ticdc_image: str
    downstream_image: str
    ticdc_cpu_limit: float
    ticdc_memory_mb: int
    downstream_cpu_limit: float
    downstream_memory_mb: int
    ticdc_count: int = 1
    ticdc_cluster_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        images = (self.ticdc_image, self.downstream_image)
        if any("@sha256:" not in image for image in images):
            raise ValueError(f"TiDB replication images must be digest-pinned: images={images!r}")
        resources = {
            "ticdc_cpu_limit": self.ticdc_cpu_limit,
            "ticdc_memory_mb": self.ticdc_memory_mb,
            "downstream_cpu_limit": self.downstream_cpu_limit,
            "downstream_memory_mb": self.downstream_memory_mb,
            "ticdc_count": self.ticdc_count,
        }
        invalid = {name: value for name, value in resources.items() if value <= 0}
        if invalid:
            raise ValueError(f"TiDB replication resources must be positive: {invalid}")
        if self.ticdc_cluster_ids and len(self.ticdc_cluster_ids) != self.ticdc_count:
            raise ValueError(
                "TiDB replication ticdc_cluster_ids must cover every TiCDC capture: "
                f"ticdc_count={self.ticdc_count}, ticdc_cluster_ids={self.ticdc_cluster_ids!r}"
            )
        reserved = {"owner", "capture", "task", "changefeed", "job", "meta"}
        invalid_cluster_ids = [
            cluster_id
            for cluster_id in self.ticdc_cluster_ids
            if re.fullmatch(r"[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*", cluster_id) is None
            or cluster_id in reserved
        ]
        if invalid_cluster_ids:
            raise ValueError(
                "TiDB replication ticdc_cluster_ids must use valid non-reserved identifiers: "
                f"invalid={invalid_cluster_ids!r}"
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class TiDBReleaseSpec:
    version: str
    pd_image: str
    tikv_image: str
    tidb_image: str
    tiflash_image: str | None
    tidb_extra_args: tuple[str, ...]

    def __post_init__(self) -> None:
        images = tuple(
            image
            for image in (self.pd_image, self.tikv_image, self.tidb_image, self.tiflash_image)
            if image is not None
        )
        if any("@sha256:" not in image for image in images):
            raise ValueError(
                f"TiDB release images must be digest-pinned: version={self.version!r}, images={images!r}"
            )


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
