"""Environment port consumed by the tidb5 OLTP instance packages.

The TiDB Persistent Scenario backend (assembly owned by the backend package)
must hand each instance an object satisfying ``TiDBPersistentEnvironmentPort``.
Real-run scripts construct an adapter over the existing bounded
``TiDBEnv``/``TiDBDockerDeployment``; focused tests
use structural fakes. Every method is load-bearing: a missing capability is a
missing public interface and must fail loudly, never degrade.
"""

from __future__ import annotations

import threading
from typing import Any, Mapping, Protocol


class DBConnection(Protocol):
    """A real pymysql-style connection (autocommit off)."""

    def cursor(self) -> Any: ...
    def begin(self) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...


class TiDBPersistentEnvironmentPort(Protocol):
    """Trusted environment services for the OLTP persistent instances.

    ``control_connection`` returns a trusted control-plane connection that the
    agent cannot reach through its SQL tool: it backs the control tables the
    capabilities publish through and the business truth the verifiers read.
    """

    def control_connection(self) -> DBConnection: ...

    def workload(self) -> Any:
        """The instance workload driver runtime (capability control surface)."""

    def pd_stores(self) -> tuple[Mapping[str, Any], ...]:
        """Raw PD store records, each carrying at least
        ``{"store": {"id", "address", "state_name", "labels": [...]}}``."""

    def set_tikv_io_rate_limit(self, target: str, max_bytes_per_sec: int) -> Mapping[str, Any]: ...

    def tikv_io_rate_limit(self, target: str) -> Mapping[str, Any]: ...

    def set_tikv_container_cpu_limit(self, target: str, cpus: float) -> Mapping[str, Any]:
        """Apply a reversible container-level CPU ceiling to one TiKV node
        (slow-node form: the store keeps serving, Raft majority stays intact).
        Returns the observed limit facts after the update."""

    def tikv_container_cpu_limit(self, target: str) -> Mapping[str, Any]:
        """Observed container CPU limit facts (nanoseconds-based Docker fields)
        for one TiKV node."""

    def start_tikv(self, target: str) -> Mapping[str, Any]:
        """Bring a reserved (deferred) TiKV online as a new PD store."""

    def pd_regions_check(self, kind: str) -> tuple[Mapping[str, Any], ...]:
        """PD region health check (e.g. kind="miss-peer" | "down-peer"); returns region records."""

    def table_leader_distribution(self, table: str) -> Mapping[str, int]:
        """Leader count per store address for one business table
        (proves which store actually carries the table's hot regions)."""

    def backend_connection_counts(self) -> Mapping[str, int]:
        """Per-TiDB-backend client connection counts (e.g. tidb/tidb-0 -> 7)."""

    def drain_backend(self, target: str) -> Mapping[str, Any]:
        """Stop accepting new client connections on one TiDB backend while
        existing connections keep running to natural completion."""


class ControlEnvironmentPort:
    """Shared building block for script-side adapters: lazy trusted connections."""

    def __init__(self, connect: Any) -> None:
        self._connect = connect
        self._lock = threading.Lock()

    def control_connection(self) -> DBConnection:
        return self._connect("tidb5-control")
