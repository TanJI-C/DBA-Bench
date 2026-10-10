"""Business-truth verifiers for the online topology change instance.

Same call convention as the hotspot package:
``verifier(port, connection, ledger_view, params) -> Mapping``. Trade-side
integrity verifiers are shared with the hotspot package (same business
service); topology verifiers check the maintenance end state and replica
safety from trusted PD facts.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..hotspot.verifiers import (
    VERIFIERS as _TRADE_VERIFIERS,
    commerce_ledger_conservation,
    orders_idempotency_uniqueness,
    unknown_commit_dedup,
)
from .delivery import DELIVERY_PREDICATES, placement_satisfied


def maintenance_final_state(
    port: Any, connection: Any, ledger_view: Any, params: Mapping[str, Any]
) -> Mapping[str, Any]:
    """The published maintenance contract must hold in the final environment.

    params (from the work order, all required): ``reserve_tikv``,
    ``retire_tikv``, ``drain_backend``, ``placement_expected_constraint``.
    Every delivery predicate is evaluated against trusted facts at final
    sampling time.
    """
    failures: list[str] = []
    facts: dict[str, Any] = {}
    targets = {
        "store_scaleout": params["reserve_tikv"],
        "store_retired": params["retire_tikv"],
        "tidb_drain": params["drain_backend"],
    }
    for kind, target in targets.items():
        predicate = DELIVERY_PREDICATES[kind]
        result = predicate(port, connection, target)
        facts[kind] = result
        if not result["satisfied"]:
            failures.append(f"{kind} not satisfied for {target!r}: facts={result!r}")
    placement = placement_satisfied(
        port,
        connection,
        params.get("placement_table", "ops.maintenance_tracking"),
        expected_constraint=params["placement_expected_constraint"],
    )
    facts["placement_satisfied"] = placement
    if not placement["satisfied"]:
        failures.append(
            f"placement_satisfied not satisfied: facts={placement!r}"
        )
    return {
        "passed": not failures,
        "failures": failures,
        "facts": facts,
    }


def replica_safety_after_change(
    port: Any, connection: Any, ledger_view: Any, params: Mapping[str, Any]
) -> Mapping[str, Any]:
    """No region may lose quorum or peers through the topology change."""
    max_missing = int(params.get("max_missing_peer_regions", 0))
    max_down = int(params.get("max_down_peer_regions", 0))
    missing = port.pd_regions_check("miss-peer")
    down = port.pd_regions_check("down-peer")
    failures: list[str] = []
    if len(missing) > max_missing:
        failures.append(
            f"missing-peer regions exceed the safety bound: count={len(missing)}, bound={max_missing}, "
            f"regions={[str(region.get('id')) for region in missing[:10]]!r}"
        )
    if len(down) > max_down:
        failures.append(
            f"down-peer regions exceed the safety bound: count={len(down)}, bound={max_down}, "
            f"regions={[str(region.get('id')) for region in down[:10]]!r}"
        )
    return {
        "passed": not failures,
        "failures": failures,
        "missing_peer_regions": len(missing),
        "down_peer_regions": len(down),
    }


def maintenance_jobs_delivered(
    port: Any, connection: Any, ledger_view: Any, params: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Every work-order deliverable recorded delivery in the trusted ledger."""
    from src.persistent_scenarios.runtime.ledger import LedgerTerminal

    failures: list[str] = []
    jobs = ledger_view.jobs()
    for job in jobs:
        if job.terminal is not LedgerTerminal.COMPLETED:
            failures.append(
                f"maintenance deliverable not delivered: job_id={job.job_id!r}, terminal={job.terminal.value}"
            )
        elif not job.delivered_on_time:
            failures.append(
                f"maintenance deliverable delivered late: job_id={job.job_id!r}, "
                f"deadline={job.deadline_at_monotonic}, delivered={job.delivered_at_monotonic}"
            )
    return {
        "passed": not failures,
        "failures": failures,
        "deliverables": len(jobs),
    }


VERIFIERS: dict[str, Any] = {
    **_TRADE_VERIFIERS,
    "maintenance_final_state": maintenance_final_state,
    "replica_safety_after_change": replica_safety_after_change,
    "maintenance_jobs_delivered": maintenance_jobs_delivered,
}

__all__ = [
    "commerce_ledger_conservation",
    "orders_idempotency_uniqueness",
    "unknown_commit_dedup",
    "maintenance_final_state",
    "replica_safety_after_change",
    "maintenance_jobs_delivered",
    "VERIFIERS",
]
