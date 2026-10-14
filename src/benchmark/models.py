from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from src.persistent_scenarios.model.spec import PersistentScenarioResourceSpec
from src.execution.specs import CaseResourceSpec, HostPortLayout
from src.database.system import DatabaseSystem


TERMINAL_STATUSES = {"succeeded", "failed", "timed_out", "interrupted"}
RUN_STATUSES = {"pending", "completed", "invalid", "infrastructure_failure", "model_failure"}


class ScenarioKind(str, Enum):
    BOUNDED = "bounded"
    PERSISTENT = "persistent"


@dataclass(frozen=True)
class AgentSpec:
    id: str
    mode: str
    model: str | None = None
    reasoning_effort: str | None = None
    max_turns: int = 30
    max_output_tokens: int | None = None
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IsolationDemandSpec:
    physical_cores_per_worker: int
    memory_mb_per_worker: int
    numa_policy: str


@dataclass(frozen=True)
class IsolationPolicySpec:
    numa_policy: str
    cpuset_cpus: str | None = None


@dataclass(frozen=True)
class WorkerAllocation:
    id: str
    physical_cores: tuple[str, ...]
    cpuset_cpus: str
    cpuset_mems: str
    cpu_capacity: float
    memory_capacity_mb: int


@dataclass(frozen=True)
class RuntimeSpec:
    concurrency: int = 1
    timeout_seconds: int = 1800
    port_base: int = 16432
    container_prefix: str = "aiopsbench-experiment"
    fault_snapshot: str = "auto"
    llm_config: str = "config/llm_config.json"
    tidb_storage_key: str | None = None
    tidb_storage_root: str | None = None
    tidb_cold_start_timeout_sec: int = 900
    tidb_warm_start_timeout_sec: int = 300
    postgres_cold_start_timeout_sec: int = 600
    postgres_storage_root: str | None = None
    diagnosis_match_mode: str = "exact"
    diagnosis_semantic_model: str = "Qwen/Qwen3-4B-Instruct-2507"
    agent_language: str = "zh"
    isolation: IsolationPolicySpec | None = None
    run_mode: str = "formal"
    time_scale: float = 1.0


@dataclass(frozen=True)
class BoundedScenarioRunSpec:
    experiment_id: str
    run_id: str
    system: DatabaseSystem
    scenario_id: str
    script: str
    category: str
    case_id: str
    agent: AgentSpec
    repetition: int
    seed: int
    port: int
    resources: CaseResourceSpec | None = None
    host_ports: HostPortLayout = HostPortLayout()
    scenario_kind: ScenarioKind = ScenarioKind.BOUNDED


@dataclass(frozen=True)
class PersistentScenarioRunSpec:
    experiment_id: str
    run_id: str
    scenario_id: str
    system: DatabaseSystem
    agent: AgentSpec
    repetition: int
    seed: int
    port: int
    resources: PersistentScenarioResourceSpec | None = None
    host_ports: HostPortLayout = HostPortLayout()
    scenario_kind: ScenarioKind = ScenarioKind.PERSISTENT


@dataclass
class RunRecord:
    experiment_id: str
    run_id: str
    system: str
    scenario_id: str | None
    case_id: str | None
    category: str | None
    script: str | None
    agent_id: str
    agent_mode: str
    model: str | None
    repetition: int
    seed: int
    port: int
    status: str = "pending"
    run_status: str = "pending"
    attempt: int = 0
    retry_count: int = 0
    timeout_seconds: int | None = None
    started_at: str | None = None
    finished_at: str | None = None
    duration_seconds: float | None = None
    return_code: int | None = None
    failure_category: str | None = None
    error: str | None = None
    diagnosis_pass: bool | None = None
    outcome_pass: bool | None = None
    safe_pass: bool | None = None
    evaluator: str | None = None
    case_no: int | None = None
    valid_for_aggregate: bool = False
    evaluation: dict[str, Any] = field(default_factory=dict)
    trace_path: str | None = None
    evaluator_path: str | None = None
    stdout_path: str | None = None
    attempt_path: str | None = None
    command: list[str] = field(default_factory=list)
    provider: str | None = None
    attempts: list[dict[str, Any]] = field(default_factory=list)
    worker_id: str | None = None
    physical_cores: tuple[str, ...] = ()
    cpuset_cpus: str | None = None
    cpuset_mems: str | None = None
    worker_cpu_capacity: float | None = None
    worker_memory_capacity_mb: int | None = None
    container_cpu_limit: float | None = None
    container_memory_mb: int | None = None
    runtime_evidence: dict[str, Any] = field(default_factory=lambda: {"status": "pending"})
    cleanup_evidence: dict[str, Any] = field(default_factory=lambda: {"status": "pending"})
    process_runtime_path: str | None = None
    runtime_audit_path: str | None = None
    cleanup_audit_path: str | None = None
    scenario_kind: str = ScenarioKind.BOUNDED.value
    service_objectives_pass: bool | None = None
    data_integrity_pass: bool | None = None
    required_state_pass: bool | None = None

    @classmethod
    def from_spec(cls, spec: BoundedScenarioRunSpec | PersistentScenarioRunSpec) -> "RunRecord":
        if isinstance(spec, PersistentScenarioRunSpec):
            return cls(
                experiment_id=spec.experiment_id,
                run_id=spec.run_id,
                system=spec.system.value,
                scenario_id=spec.scenario_id,
                case_id=None,
                category=None,
                script=None,
                agent_id=spec.agent.id,
                agent_mode=spec.agent.mode,
                model=spec.agent.model,
                repetition=spec.repetition,
                seed=spec.seed,
                port=spec.port,
                scenario_kind=spec.scenario_kind.value,
            )
        return cls(
            experiment_id=spec.experiment_id,
            run_id=spec.run_id,
            system=spec.system.value,
            scenario_id=spec.scenario_id,
            case_id=spec.case_id,
            category=spec.category,
            script=spec.script,
            agent_id=spec.agent.id,
            agent_mode=spec.agent.mode,
            model=spec.agent.model,
            repetition=spec.repetition,
            seed=spec.seed,
            port=spec.port,
            scenario_kind=spec.scenario_kind.value,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunRecord":
        values = {
            "attempt_path": None,
            "runtime_evidence": {"status": "pending"},
            "cleanup_evidence": {"status": "pending"},
            **data,
            "physical_cores": tuple(data["physical_cores"]),
        }
        return cls(**values)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
