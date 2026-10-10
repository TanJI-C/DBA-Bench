from __future__ import annotations

from collections.abc import Mapping
import threading


class TiDBConnectionRouter:
    """Route new application connections across the TiDB SQL endpoints."""

    POLICIES = frozenset({"round_robin", "least_connections"})

    def __init__(self, endpoints: Mapping[str, tuple[str, int]], initial_target: str):
        self._endpoints = dict(endpoints)
        if initial_target not in self._endpoints:
            raise ValueError(
                f"TiDB connection router initial target is unknown: target={initial_target!r}, "
                f"endpoints={sorted(self._endpoints)}"
            )
        self._initial_target = initial_target
        self._policy = "single_instance"
        self._draining: set[str] = set()
        self._connections: dict[int, str] = {}
        self._connection_generations: dict[int, int] = {}
        self._route_counts = {target: 0 for target in self._endpoints}
        self._generation = 0
        self._next_index = 0
        self._lock = threading.RLock()

    @property
    def endpoints(self) -> tuple[str, ...]:
        return tuple(self._endpoints)

    def target_for_new_connection(self) -> str:
        with self._lock:
            if self._policy == "single_instance":
                if self._initial_target in self._draining:
                    raise RuntimeError(
                        "TiDB connection router cannot open a new connection: "
                        f"single target {self._initial_target!r} is draining"
                    )
                return self._initial_target

            candidates = tuple(
                target for target in self._endpoints if target not in self._draining
            )
            if not candidates:
                raise RuntimeError(
                    "TiDB connection router has no backend accepting new connections: "
                    f"policy={self._policy!r}, draining={sorted(self._draining)}"
                )
            if self._policy == "round_robin":
                target = candidates[self._next_index % len(candidates)]
                self._next_index += 1
                return target
            if self._policy == "least_connections":
                return min(
                    candidates,
                    key=lambda candidate: (
                        self._route_counts[candidate],
                        candidates.index(candidate),
                    ),
                )
            raise RuntimeError(f"Unsupported TiDB connection router policy: {self._policy!r}")

    def register_connection(self, connection: object, target: str) -> None:
        with self._lock:
            if target not in self._endpoints:
                raise ValueError(
                    f"Cannot register TiDB connection for unknown target: target={target!r}, "
                    f"endpoints={sorted(self._endpoints)}"
                )
            connection_id = id(connection)
            if connection_id in self._connections:
                raise RuntimeError(
                    f"TiDB connection was registered twice: connection_id={connection_id}, "
                    f"existing_target={self._connections[connection_id]!r}, target={target!r}"
                )
            self._connections[connection_id] = target
            self._connection_generations[connection_id] = self._generation
            self._route_counts[target] += 1

    def release_connection(self, connection: object) -> None:
        with self._lock:
            connection_id = id(connection)
            target = self._connections.pop(connection_id, None)
            if target is None:
                raise RuntimeError(
                    f"TiDB connection was released without registration: connection_id={connection_id}"
                )
            self._connection_generations.pop(connection_id)
            self._route_counts[target] -= 1
            if self._route_counts[target] < 0:
                raise RuntimeError(
                    f"TiDB connection route count became negative: target={target!r}, "
                    f"count={self._route_counts[target]}"
                )

    def should_recycle(self, connection: object) -> bool:
        with self._lock:
            target = self._connections.get(id(connection))
            if target is None:
                raise RuntimeError(
                    f"Cannot inspect unregistered TiDB connection: connection_id={id(connection)}"
                )
            return (
                target in self._draining
                or self._connection_generations[id(connection)] != self._generation
            )

    def invalidate_connections(self) -> None:
        with self._lock:
            self._generation += 1

    def set_policy(self, policy: str) -> dict[str, object]:
        if policy not in self.POLICIES:
            raise ValueError(
                f"Unsupported TiDB connection router policy: policy={policy!r}, "
                f"expected one of {sorted(self.POLICIES)}"
            )
        with self._lock:
            candidates = tuple(target for target in self._endpoints if target not in self._draining)
            if not candidates:
                raise RuntimeError(
                    "Cannot change TiDB connection router policy because every backend is draining: "
                    f"draining={sorted(self._draining)}"
                )
            self._policy = policy
            self._next_index = 0
            return self.status()

    def drain(self, target: str) -> dict[str, object]:
        with self._lock:
            self.validate_drain(target)
            if self._policy == "single_instance" and target != self._initial_target:
                return self.status()
            self._draining.add(target)
            return self.status()

    def validate_drain(self, target: str) -> None:
        with self._lock:
            if target not in self._endpoints:
                raise ValueError(
                    f"Cannot drain unknown TiDB backend: target={target!r}, "
                    f"endpoints={sorted(self._endpoints)}"
                )
            if self._policy == "single_instance" and target != self._initial_target:
                return
            if self._policy == "single_instance":
                raise RuntimeError(
                    "TiDB connection router requires a distributing policy before draining a backend: "
                    f"policy={self._policy!r}, target={target!r}"
                )
            if target in self._draining:
                raise RuntimeError(f"TiDB backend is already draining: target={target!r}")
            if all(candidate in self._draining or candidate == target for candidate in self._endpoints):
                raise RuntimeError(
                    "TiDB connection router cannot drain its last accepting backend: "
                    f"target={target!r}, draining={sorted(self._draining)}"
                )

    def status(self) -> dict[str, object]:
        with self._lock:
            return {
                "policy": self._policy,
                "initial_target": self._initial_target,
                "endpoints": list(self._endpoints),
                "draining": sorted(self._draining),
                "active_connections": dict(self._route_counts),
                "total_active_connections": sum(self._route_counts.values()),
                "route_count": dict(self._route_counts),
                "generation": self._generation,
            }

    def quiesce(self) -> None:
        with self._lock:
            if self._connections:
                raise RuntimeError(
                    "Cannot quiesce TiDB connection router while application connections remain: "
                    f"active_connections={self._route_counts}"
                )

    def reset(self) -> None:
        with self._lock:
            self._connections.clear()
            self._connection_generations.clear()
            self._route_counts = {target: 0 for target in self._endpoints}
