"""Ports consumed by PersistentScenario runtime coordinators."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from .lifecycle import FailureClassification


class EventActivationError(RuntimeError):
    def __init__(self, message: str, handle: object | None = None):
        super().__init__(message)
        self.handle = handle


class PersistentScenarioProviderError(RuntimeError):
    """A trusted environment or provider failed during an PersistentScenario run."""


class PersistentScenarioEnvironmentInvalidError(PersistentScenarioProviderError):
    """The provider could not prove the injected environment contract."""


class PersistentScenarioAgentProviderError(RuntimeError):
    """The external Agent provider failed before producing an action."""


class PersistentScenarioAgentProtocolError(RuntimeError):
    """The Agent returned an invalid PersistentScenario-v2 control structure."""


class PersistentScenarioEvaluationProvider(Protocol):
    """Evaluation boundary injected into the runtime by the composition root."""

    def evaluate(self, persistent_scenario_run: object) -> Mapping[str, Any]: ...

    def evaluate_baseline(self, persistent_scenario_run: object, safety: Mapping[str, object]) -> Mapping[str, Any]: ...

    def invalid_run(
        self,
        persistent_scenario_run: object,
        classification: FailureClassification,
        reason: str,
    ) -> Mapping[str, Any]: ...
