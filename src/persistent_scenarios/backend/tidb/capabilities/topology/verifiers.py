"""Business-truth verifier bindings for the topology instance package."""

from __future__ import annotations

from typing import Any, Callable, Mapping

from src.persistent_scenarios.tidb.topology.verifiers import (
    maintenance_final_state,
    maintenance_jobs_delivered,
    replica_safety_after_change,
)


def _params_verifier(func: Callable[..., Mapping[str, Any]], required: tuple[str, ...]) -> Callable[..., Mapping[str, Any]]:
    def verify(port: Any, connection: Any, ledger_view: Any, params: Mapping[str, Any]) -> Mapping[str, Any]:
        missing = sorted(name for name in required if name not in params)
        if missing:
            raise ValueError(f"{func.__name__} is missing required params: missing={missing!r}")
        return func(port, connection, ledger_view, params)

    verify.verifier_id = func.__name__
    return verify


maintenance_final_state_verifier = _params_verifier(
    maintenance_final_state, ("reserve_tikv", "retire_tikv", "drain_backend")
)
replica_safety_after_change_verifier = _params_verifier(replica_safety_after_change, ())
maintenance_jobs_delivered_verifier = _params_verifier(maintenance_jobs_delivered, ())

VERIFIERS: tuple[tuple[str, Callable[..., Mapping[str, Any]]], ...] = (
    ("maintenance_final_state", maintenance_final_state_verifier),
    ("replica_safety_after_change", replica_safety_after_change_verifier),
    ("maintenance_jobs_delivered", maintenance_jobs_delivered_verifier),
)
