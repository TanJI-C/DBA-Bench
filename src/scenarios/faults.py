from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass

@dataclass(frozen=True, slots=True, kw_only=True)
class FaultLifecycleContext:
    """Immutable facts shared by every phase of one fault injection."""

    run_id: str
    scenario_id: str
    case_id: str
    case: object
    config: Mapping[str, object]
    env: object

class BaseFaultInjector(ABC):
    """One fault unit controlled by the Orchestrator lifecycle."""

    @abstractmethod
    def install(self, context: FaultLifecycleContext) -> None:
        """Create the complete fault in a fresh environment."""
        raise NotImplementedError

    @abstractmethod
    def activate(self, context: FaultLifecycleContext) -> None:
        """Validate existing persistent state and rebuild runtime-only symptoms."""
        raise NotImplementedError

    @abstractmethod
    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        """Build agent-visible evidence and return evaluator evidence."""
        raise NotImplementedError

    @abstractmethod
    def quiesce(self, context: FaultLifecycleContext) -> None:
        """Leave only image-persistable fault state and stop runtime resources."""
        raise NotImplementedError

    @abstractmethod
    def recover(self, context: FaultLifecycleContext) -> None:
        """Remove the fault and release all runtime resources."""
        raise NotImplementedError

    def attach_workload_runner_factory(self, factory) -> None:
        self._workload_runner_factory = factory

    def configure_history_adapter(self, context: FaultLifecycleContext) -> None:
        """Register Case-owned metric/history adapters before Case validation."""
        return None

    def prepare_metric_history(self, context: FaultLifecycleContext) -> None:
        """Prepare scenario-owned live observations before normal capture.

        Frozen-history orchestration calls this hook before the generic history
        sampler starts. It is intentionally internal lifecycle plumbing: the
        Agent still sees only the shared metric/query-history tools.
        """
    def prepare_history_observability(self, context: FaultLifecycleContext) -> None:
        """Prepare real observation infrastructure before frozen-history normal capture."""
        return None

    def create_workload_runner(self, env, profiles, worker_count):
        factory = getattr(self, "_workload_runner_factory", None)
        if factory is None:
            raise RuntimeError(
                f"{type(self).__name__} requires the orchestration workload runner factory"
            )
        return factory(env, profiles=profiles, worker_count=worker_count)


class NoopFaultInjector(BaseFaultInjector):
    """Lifecycle participant for scenarios that intentionally inject no fault."""

    def install(self, context: FaultLifecycleContext) -> None:
        print(f"[FaultInjector:{type(self).__name__}] No fault injected.")

    def activate(self, context: FaultLifecycleContext) -> None:
        print(f"[FaultInjector:{type(self).__name__}] No fault activated.")

    def prepare_observability(
        self,
        context: FaultLifecycleContext,
    ) -> Mapping[str, object]:
        return {}

    def quiesce(self, context: FaultLifecycleContext) -> None:
        return None

    def recover(self, context: FaultLifecycleContext) -> None:
        print(f"[FaultInjector:{type(self).__name__}] No fault to recover.")
