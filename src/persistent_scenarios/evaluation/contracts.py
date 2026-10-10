"""Result schema constants and trusted diagnosis records owned by evaluation.

All runtime fact types (scoring window, business ledgers, arrival evidence, action
facts, integrity facts, required-state evidence, run validity, input versions) are
defined by core and live in ``runtime/lifecycle.py``,
``runtime/ledger.py`` and ``runtime/state.py``; evaluation only consumes them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


SCHEMA_ID = "persistent_scenario_evaluation_v2"
SCHEMA_VERSION = 2
EVALUATOR_VERSION = "pg5-eval-v2"


class LedgerIncompleteError(RuntimeError):
    """The trusted collector lost ledger records or verification evidence.

    This is an evaluation-facility failure: the run is invalid (DP/OP/SP = None),
    never a model or business failure.
    """


@dataclass(frozen=True, slots=True)
class TrustedDiagnosis:
    """Kept as the backend capability diagnosis record (see backend/contracts.py)."""

    applicable: bool
    passed: bool | None
    facts: Mapping[str, object]

    def __post_init__(self) -> None:
        if not isinstance(self.applicable, bool):
            raise TypeError(f"Trusted diagnosis applicability must be bool: value={self.applicable!r}")
        if self.applicable and not isinstance(self.passed, bool):
            raise TypeError(f"Applicable trusted diagnosis must have a bool result: passed={self.passed!r}")
        if not self.applicable and self.passed is not None:
            raise ValueError(f"Non-applicable trusted diagnosis must have passed=None: passed={self.passed!r}")
        if not isinstance(self.facts, Mapping):
            raise TypeError(f"Trusted diagnosis facts must be a mapping: value={self.facts!r}")


@dataclass(frozen=True, slots=True)
class TrustedOutcome:
    passed: bool
    diagnosis: Mapping[str, object]
    facts: Mapping[str, object]


class DiagnosisProvider(Protocol):
    def evaluate_diagnosis(self, event: object, event_run: object, environment: object) -> TrustedDiagnosis: ...
