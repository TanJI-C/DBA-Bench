"""In-memory fakes for the tidb5-oltp instance tests. No real DB involved."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Mapping


class ScriptedCursor:
    def __init__(self, connection: "ScriptedConnection") -> None:
        self._connection = connection
        self._rows: tuple[tuple, ...] = ()
        self.rowcount = -1

    def execute(self, sql: str, args: Any = None) -> None:
        self._connection.executed.append((sql, args))
        self._rows, self.rowcount = self._connection.responder(sql, args)

    def fetchone(self) -> tuple | None:
        return self._rows[0] if self._rows else None

    def fetchall(self) -> tuple[tuple, ...]:
        return self._rows

    def __enter__(self) -> "ScriptedCursor":
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None


class ScriptedConnection:
    """A pymysql-shaped scripted connection."""

    def __init__(self, responder, name: str = "scripted") -> None:
        self._responder = responder
        self.name = name
        self.executed: list[tuple[str, Any]] = []
        self.closed = False
        self.committed = 0

    def cursor(self) -> ScriptedCursor:
        return ScriptedCursor(self)

    def begin(self) -> None:
        self.executed.append(("BEGIN", None))

    def commit(self) -> None:
        self.committed += 1

    def rollback(self) -> None:
        self.executed.append(("ROLLBACK", None))

    def close(self) -> None:
        self.closed = True

    def responder(self, sql: str, args: Any) -> tuple[tuple[tuple, ...], int]:
        return self._responder(sql, args)


def exact_responder(scripted: Mapping[str, tuple[tuple, ...]]):
    """Respond with scripted rows for exact SQL matches; else no rows."""

    def respond(sql: str, _args: Any) -> tuple[tuple[tuple, ...], int]:
        rows = scripted.get(sql, ())
        return rows, len(rows)

    return respond


class FakeConnectionSource:
    """Connection source fake: per-policy connections plus a scripted control."""

    def __init__(self, control_responder) -> None:
        self._control_responder = control_responder
        self.policies: list[Any] = []
        self.control_connection = ScriptedConnection(control_responder, "control")
        self.counts: Mapping[str, int] = {"tidb/tidb-0": 0}

    def connect(self, policy: Any) -> ScriptedConnection:
        self.policies.append(policy)
        return ScriptedConnection(exact_responder({}), f"conn-v{policy.config_version}")

    def connect_control(self) -> ScriptedConnection:
        return ScriptedConnection(self._control_responder, "control")

    def connect_reconcile(self) -> ScriptedConnection:
        return ScriptedConnection(self._control_responder, "reconcile")

    def connection_counts(self) -> Mapping[str, int]:
        return self.counts

    def apply_policy(self, policy: Any) -> None:
        self.policies.append(("apply", policy))


class FakeWorkloadDriver:
    """Driver control surface fake as consumed by the capabilities."""

    def __init__(self, *, applied_version: int = 1, rejected: tuple[Mapping[str, str], ...] = ()) -> None:
        self.config = SimpleNamespace(control_poll_seconds=0.05)
        self.tiers: list[str] = []
        self._applied_version = applied_version
        self._rejected = list(rejected)
        self._planned: set[str] = set()
        self._decided: set[str] = set()

    def apply_tier(self, tier: str) -> None:
        self.tiers.append(tier)

    def current_tier(self) -> str:
        return self.tiers[-1] if self.tiers else "normal"

    def applied_config_version(self) -> int:
        return self._applied_version

    def rejected_publications(self) -> tuple[Mapping[str, str], ...]:
        return tuple(self._rejected)

    def planned_deliverable_ids(self) -> set[str]:
        return set(self._planned)

    def decided_deliverable_ids(self) -> set[str]:
        return set(self._decided)

    def backend_connection_counts(self) -> Mapping[str, int]:
        return {"tidb/tidb-0": 2, "tidb/tidb-1": 5}


class Registry:
    """EventCapabilityRegistry-shaped wrapper over a capability-id mapping."""

    def __init__(self, mapping: Mapping[str, Any]) -> None:
        self._mapping = dict(mapping)

    def capability(self, capability_id: str):
        return self._mapping[capability_id]


@dataclass
class FakeTiDBPort:
    """Environment port fake with an in-memory PD view and scripted control SQL."""

    workload_driver: FakeWorkloadDriver | None = None
    stores: list[dict] = field(default_factory=list)
    io_limits: dict[str, int] = field(default_factory=lambda: {"tikv/tikv-1": 262144000, "tikv/tikv-3": 262144000})
    cpu_limits: dict[str, float] = field(default_factory=lambda: {"tikv/tikv-1": 1.0, "tikv/tikv-2": 1.0, "tikv/tikv-3": 1.0})
    leader_distribution: Mapping[str, int] = field(default_factory=dict)
    region_checks: Mapping[str, list[dict]] = field(default_factory=dict)
    connection_counts: Mapping[str, int] = field(default_factory=lambda: {"tidb/tidb-0": 4, "tidb/tidb-1": 6})
    control_script: Mapping[str, tuple[tuple, ...]] = field(default_factory=dict)
    control_responder: Any = None  # optional dynamic responder(sql, args) -> (rows, rowcount)
    started_tikv: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.set_calls: list[tuple[str, int]] = []
        self.cpu_set_calls: list[tuple[str, float]] = []

    def control_connection(self) -> ScriptedConnection:
        responder = self.control_responder or exact_responder(self.control_script)
        return ScriptedConnection(responder, "port-control")

    def workload(self) -> FakeWorkloadDriver:
        if self.workload_driver is None:
            raise RuntimeError("fake port has no workload driver")
        return self.workload_driver

    def pd_stores(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(self.stores)

    def set_tikv_io_rate_limit(self, target: str, max_bytes_per_sec: int) -> Mapping[str, Any]:
        self.set_calls.append((target, max_bytes_per_sec))
        self.io_limits[target] = max_bytes_per_sec
        return {"max-bytes-per-sec": max_bytes_per_sec}

    def tikv_io_rate_limit(self, target: str) -> Mapping[str, Any]:
        return {"max-bytes-per-sec": self.io_limits[target]}

    def set_tikv_container_cpu_limit(self, target: str, cpus: float) -> Mapping[str, Any]:
        self.cpu_set_calls.append((target, cpus))
        self.cpu_limits[target] = float(cpus)
        return {"target": target, "cpus": float(cpus)}

    def tikv_container_cpu_limit(self, target: str) -> Mapping[str, Any]:
        return {"target": target, "cpus": self.cpu_limits[target]}

    def start_tikv(self, target: str) -> Mapping[str, Any]:
        self.started_tikv.append(target)
        service = target.rsplit("/", 1)[-1]
        self.stores.append({"store": {"id": 4, "address": f"{service}:20160", "state_name": "Up",
                                      "labels": [{"key": "zone", "value": "zone4"}]}})
        return {"target": target, "state": "Up", "store_id": 4}

    def pd_regions_check(self, kind: str) -> tuple[Mapping[str, Any], ...]:
        return tuple(self.region_checks.get(kind, ()))

    def table_leader_distribution(self, table: str) -> Mapping[str, int]:
        return dict(self.leader_distribution)

    def backend_connection_counts(self) -> Mapping[str, int]:
        return dict(self.connection_counts)

    def drain_backend(self, target: str) -> Mapping[str, Any]:
        return {"drained": target}
