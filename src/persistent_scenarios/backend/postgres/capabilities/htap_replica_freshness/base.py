"""Shared plumbing re-export for the pg5 replica-freshness capabilities."""

from ..htap_shared_isolation.base import (  # noqa: F401
    CoreProtocolCapability,
    HtapCapabilityHandle,
    PreventedActivation,
    diagnosis_not_required,
    exclusive,
    injection_failed,
    outcome,
    shared,
)

__all__ = [
    "CoreProtocolCapability",
    "HtapCapabilityHandle",
    "PreventedActivation",
    "diagnosis_not_required",
    "exclusive",
    "injection_failed",
    "outcome",
    "shared",
]
