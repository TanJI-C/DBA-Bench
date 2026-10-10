"""Metric catalog for the PostgreSQL replica-fleet scenario.

These are bounded observations assembled from the real fleet endpoints.  The
catalog deliberately describes measurements and target scope only; it does
not expose a root-cause or repair label.
"""

from __future__ import annotations

import hashlib
import json
from types import MappingProxyType

from src.execution.history.metrics import MetricDefinition
from src.execution.postgres_metrics import PostgresMetricCatalog


_FLEET_DEFINITIONS = MappingProxyType({
    "router_distribution": MetricDefinition(
        name="router_distribution",
        value_fields=("active_replicas", "traffic_share_percent", "requests_per_sec"),
        lookback_seconds=2,
        source_step_seconds=1,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "replica_service": MetricDefinition(
        name="replica_service",
        value_fields=("queries_per_sec", "p95_ms", "p99_ms", "active_backends", "replay_lag_sec"),
        lookback_seconds=2,
        source_step_seconds=1,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "replica_lwlock": MetricDefinition(
        name="replica_lwlock",
        value_fields=("lock_manager_waiters", "waiter_ms_per_sec", "slowpath_backends"),
        lookback_seconds=2,
        source_step_seconds=1,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "query_footprint": MetricDefinition(
        name="query_footprint",
        value_fields=("transactions_per_sec", "mean_relation_locks", "slowpath_fraction"),
        lookback_seconds=2,
        source_step_seconds=1,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "pgbouncer_pool": MetricDefinition(
        name="pgbouncer_pool",
        value_fields=("sv_active", "sv_idle", "cl_waiting", "maxwait_sec"),
        lookback_seconds=2,
        source_step_seconds=1,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "primary_service": MetricDefinition(
        name="primary_service",
        value_fields=("write_tps", "p99_ms", "replication_lag_max_sec"),
        lookback_seconds=2,
        source_step_seconds=1,
        lower_bound=0.0,
        upper_bound=None,
    ),
})
FLEET_METRIC_NAMES = frozenset(_FLEET_DEFINITIONS)


class ReplicaFleetMetricCatalog(PostgresMetricCatalog):
    """Base PostgreSQL metrics plus the public fleet observation contract."""

    system = "postgresql-replica-fleet"

    @property
    def metric_names(self) -> frozenset[str]:
        return frozenset((*super().metric_names, *FLEET_METRIC_NAMES))

    def definition(self, metric: str) -> MetricDefinition:
        normalized = str(metric).casefold()
        if normalized in _FLEET_DEFINITIONS:
            return _FLEET_DEFINITIONS[normalized]
        return super().definition(normalized)

    def target_variants(self, metric: str, deployment: object) -> tuple[str | None, ...]:
        normalized = str(metric).casefold()
        self.definition(normalized)
        if normalized in {"router_distribution", "replica_service", "replica_lwlock"}:
            replicas = tuple(getattr(deployment, "replica_names", ()))
            if not replicas:
                replicas = tuple(f"replica_{index}" for index in range(3))
            return (None, *replicas)
        if normalized == "query_footprint":
            return (None, "checkout_read_footprint", "checkout_read_footprint_simple", "report_pool")
        if normalized == "pgbouncer_pool":
            return (None, "read_pool", "report_pool")
        return (None,)

    def series_target(self, metric: str) -> str:
        normalized = str(metric).casefold()
        if normalized in {"router_distribution", "replica_service", "replica_lwlock"}:
            return "replica"
        if normalized == "query_footprint":
            return "query_family"
        if normalized == "pgbouncer_pool":
            return "pool"
        if normalized == "primary_service":
            return "postgres"
        return super().series_target(normalized)

    def validate_target(self, metric: str, target: str | None, deployment: object) -> None:
        normalized = str(metric).casefold()
        if normalized not in _FLEET_DEFINITIONS:
            return super().validate_target(normalized, target, deployment)
        allowed = self.target_variants(normalized, deployment)
        if target not in allowed:
            raise ValueError(
                f"Replica fleet metric target is not available: metric={normalized!r}, target={target!r}, "
                f"allowed={allowed!r}"
            )

    def fingerprint(self) -> str:
        payload = {
            "base": super().fingerprint(),
            "catalog_version": "postgres-replica-fleet-metric-catalog-v1",
            "metrics": {
                name: {
                    "fields": definition.value_fields,
                    "lookback_seconds": definition.lookback_seconds,
                    "source_step_seconds": definition.source_step_seconds,
                }
                for name, definition in _FLEET_DEFINITIONS.items()
            },
            "target_rule": "fleet observations expose all stable replica and pool identities",
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


REPLICA_FLEET_METRIC_CATALOG = ReplicaFleetMetricCatalog()


__all__ = ["FLEET_METRIC_NAMES", "ReplicaFleetMetricCatalog", "REPLICA_FLEET_METRIC_CATALOG"]
