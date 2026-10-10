"""PostgreSQL Persistent Scenario capability registry (assembly-owned).

This is the ``EventCapabilityRegistry`` registration entry: it resolves
PostgreSQL capability implementations by their declared ``capability_id``,
exactly once per assembly. Static admission — declaration identity, the
activation bound against ``event.activation_timeout_seconds``, and exclusive
``ResourceOwnership`` conflicts across overlapping activation windows — is
owned by the core runtime (``runtime/admission.py``), which resolves
declarations per event through this registry. Per-entity isolation is
expressed by capabilities expanding ``{entity}``/``{occurrence}`` templates
into concrete ``resource_key`` strings inside ``declaration(event)``; the
registry never rewrites declared keys.
"""

from __future__ import annotations

from collections.abc import Sequence

from src.persistent_scenarios.backend.contracts import PersistentScenarioEventCapability


class PostgresEventCapabilityRegistry:
    def __init__(self, capabilities: Sequence[PersistentScenarioEventCapability] = ()):
        self._capabilities: dict[str, PersistentScenarioEventCapability] = {}
        for capability in capabilities:
            capability_id = capability.capability_id
            if not isinstance(capability_id, str) or not capability_id.strip():
                raise ValueError(
                    "PostgreSQL capability registration requires a non-empty capability_id: "
                    f"capability={type(capability).__name__!r}, capability_id={capability_id!r}"
                )
            if capability_id in self._capabilities:
                raise ValueError(
                    "Duplicate PostgreSQL capability registration: "
                    f"capability_id={capability_id!r}, "
                    f"registered={type(self._capabilities[capability_id]).__name__!r}, "
                    f"duplicate={type(capability).__name__!r}"
                )
            self._capabilities[capability_id] = capability

    def capability(self, capability_id: str) -> PersistentScenarioEventCapability:
        if capability_id not in self._capabilities:
            raise ValueError(
                "PostgreSQL capability is not registered: "
                f"capability_id={capability_id!r}, registered={sorted(self._capabilities)!r}"
            )
        return self._capabilities[capability_id]

    def capability_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._capabilities))
