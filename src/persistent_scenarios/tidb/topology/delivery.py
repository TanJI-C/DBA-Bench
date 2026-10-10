"""Maintenance delivery predicates for the topology change work orders.

Each predicate reads trusted facts only (PD store records, SQL placement
state, port connection counts) and returns a JSON-able fact mapping whose
``satisfied`` field decides delivery. A predicate error is an infrastructure
error and propagates; it is never treated as delivery failure.
"""

from __future__ import annotations

from typing import Any, Mapping


def store_state(port: Any, target: str) -> Mapping[str, Any] | None:
    """The PD store record for a service identity (e.g. tikv/tikv-3), if registered."""
    service = target.rsplit("/", 1)[-1]
    address = f"{service}:20160"
    for store in port.pd_stores():
        record = store["store"]
        if str(record.get("address")) == address:
            return record
    return None


def store_scaleout_satisfied(port: Any, connection: Any, target: str) -> Mapping[str, Any]:
    store = store_state(port, target)
    return {
        "satisfied": store is not None and str(store.get("state_name")) == "Up",
        "target": target,
        "store": None if store is None else {
            "id": store.get("id"),
            "state_name": store.get("state_name"),
            "labels": store.get("labels"),
        },
    }


def placement_satisfied(
    port: Any, connection: Any, target: str, *, expected_constraint: str | None = None
) -> Mapping[str, Any]:
    """Delivery = the tracked table carries an explicit, converged placement
    that implements the change plan's constraint (e.g. the learner on the
    reserve zone).

    Measured TiDB v8.1 semantics (four states probed on a real cluster):
    a table without an explicit placement policy returns NO SHOW PLACEMENT
    row at all (the DEFAULT layout is invisible), and an attached policy
    shows its constraint text in the Placement column (e.g.
    ``CONSTRAINTS="[+zone=zone1]" FOLLOWERS=2``) with Scheduling_State
    PENDING while unsatisfiable and SCHEDULED once converged. Dropping the
    placement to fake delivery therefore fails twice: NO-ROW is not
    satisfied, and the constraint text is missing.
    ``information_schema.placement_rules`` does not exist on v8.1.0 (probe
    error 1146), so SHOW PLACEMENT FOR TABLE is the trusted SQL surface.
    """
    from .schema import SHOW_PLACEMENT_SQL

    with connection.cursor() as cursor:
        cursor.execute(SHOW_PLACEMENT_SQL)
        rows = cursor.fetchall()
    connection.commit()
    if not rows:
        return {
            "satisfied": False,
            "target": target,
            "state": "NO-ROW",
            "raw_row": None,
            "expected_constraint": expected_constraint,
        }
    # SHOW PLACEMENT FOR TABLE columns: Target, Placement, State.
    state = str(rows[0][2]).casefold()
    placement_text = str(rows[0][1])
    constraint_present = expected_constraint is None or expected_constraint in placement_text
    return {
        "satisfied": state in ("scheduled", "protected") and constraint_present,
        "target": target,
        "state": state,
        "raw_row": [str(value) for value in rows[0]],
        "expected_constraint": expected_constraint,
        "constraint_present": constraint_present,
    }


def tidb_drain_satisfied(port: Any, connection: Any, target: str) -> Mapping[str, Any]:
    counts = port.backend_connection_counts()
    remaining = int(counts.get(target, 0))
    return {
        "satisfied": remaining == 0,
        "target": target,
        "remaining_connections": remaining,
        "connection_counts": {str(key): int(value) for key, value in counts.items()},
    }


def store_retired_satisfied(port: Any, connection: Any, target: str) -> Mapping[str, Any]:
    store = store_state(port, target)
    satisfied = store is None or str(store.get("state_name")) == "Tombstone"
    return {
        "satisfied": satisfied,
        "target": target,
        "store": None if store is None else {
            "id": store.get("id"),
            "state_name": store.get("state_name"),
        },
    }


DELIVERY_PREDICATES: dict[str, Any] = {
    "store_scaleout": store_scaleout_satisfied,
    "placement_satisfied": placement_satisfied,
    "tidb_drain": tidb_drain_satisfied,
    "store_retired": store_retired_satisfied,
}
