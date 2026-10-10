"""System metric catalog resolver used by orchestration and experiments."""

from __future__ import annotations

from src.scenarios.base import DatabaseSystem


def metric_catalog_for_system(system: DatabaseSystem):
    if system is DatabaseSystem.POSTGRESQL:
        from src.execution.postgres_metrics import POSTGRES_METRIC_CATALOG

        return POSTGRES_METRIC_CATALOG
    if system is DatabaseSystem.TIDB:
        from src.execution.tidb_metrics import TIDB_METRIC_CATALOG

        return TIDB_METRIC_CATALOG
    raise ValueError(f"Unsupported database system for metric catalog: system={system!r}")
