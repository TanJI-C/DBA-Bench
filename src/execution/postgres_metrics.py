"""PostgreSQL metric catalog and real sampler-backed provider."""

from __future__ import annotations

import hashlib
import json
import math
import threading
from pathlib import Path
from collections import deque
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from src.execution.history.metrics import (
    MetricDefinition,
    MetricFrame,
    MetricQuery,
    MetricService,
    QUERY_METRICS_BOUND_CONTRACT,
    metric_variant_sort_key,
    validate_metric_frame,
)
from src.execution.postgres_history import PG_STATEMENT_SNAPSHOT_SQL


@dataclass(frozen=True, slots=True, kw_only=True)
class PostgresMetricSourceDefinition:
    source: str
    target_shape: str


_POSTGRES_DEFINITIONS = MappingProxyType({
    "cpu": MetricDefinition(
        name="cpu",
        value_fields=("percent",),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=100.0,
    ),
    "memory": MetricDefinition(
        name="memory",
        value_fields=("percent",),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=100.0,
    ),
    "disk_io": MetricDefinition(
        name="disk_io",
        value_fields=("read_mb_per_second", "write_mb_per_second"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "qps": MetricDefinition(
        name="qps",
        value_fields=("queries_per_second",),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "active_connections": MetricDefinition(
        name="active_connections",
        value_fields=("connections",),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "cache_hit_ratio": MetricDefinition(
        name="cache_hit_ratio",
        value_fields=("percent",),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=100.0,
    ),
    # Case-owned samplers may populate these fields from ordinary PostgreSQL
    # system views. Keeping the identities in the shared catalog makes their
    # history frames subject to the same schema, grid, and bounds validation as
    # the generic container metrics.
    "relation_churn": MetricDefinition(
        name="relation_churn",
        value_fields=("updated_tps", "deleted_tps", "inserted_tps", "hot_update_ratio"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "vacuum_cleanup": MetricDefinition(
        name="vacuum_cleanup",
        value_fields=("removed_tps", "active_workers", "heap_blocks_scanned_per_sec"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "dead_tuple_backlog": MetricDefinition(
        name="dead_tuple_backlog",
        value_fields=("estimated_dead_tuples", "estimated_live_tuples"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "maintenance_io": MetricDefinition(
        name="maintenance_io",
        value_fields=("read_mb_per_sec", "write_mb_per_sec", "io_time_ms_per_sec"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "oltp_service": MetricDefinition(
        name="oltp_service",
        value_fields=("transactions_per_sec", "p99_ms", "success_ratio"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "xmin_horizon": MetricDefinition(
        name="xmin_horizon",
        value_fields=("oldest_xmin_age_sec", "blocked_vacuum_workers"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
})

_POSTGRES_SOURCES = MappingProxyType({
    "cpu": PostgresMetricSourceDefinition(source="cgroup_cpu_delta_v1", target_shape="postgres"),
    "memory": PostgresMetricSourceDefinition(source="cgroup_memory_working_set_v1", target_shape="postgres"),
    "disk_io": PostgresMetricSourceDefinition(source="cgroup_io_delta_v1", target_shape="postgres"),
    "qps": PostgresMetricSourceDefinition(source="pg_stat_statements_calls_delta_v1", target_shape="postgres"),
    "active_connections": PostgresMetricSourceDefinition(source="pg_stat_activity_snapshot_v1", target_shape="postgres"),
    "cache_hit_ratio": PostgresMetricSourceDefinition(source="pg_stat_database_delta_v1", target_shape="postgres"),
    "relation_churn": PostgresMetricSourceDefinition(source="pg_stat_user_tables_delta_v1", target_shape="relation"),
    "vacuum_cleanup": PostgresMetricSourceDefinition(source="pg_stat_progress_vacuum_v1", target_shape="relation"),
    "dead_tuple_backlog": PostgresMetricSourceDefinition(source="pg_stat_user_tables_snapshot_v1", target_shape="relation"),
    "maintenance_io": PostgresMetricSourceDefinition(source="cgroup_io_delta_v1", target_shape="postgres"),
    "oltp_service": PostgresMetricSourceDefinition(source="rpo_oltp_probe_v1", target_shape="checkout"),
    "xmin_horizon": PostgresMetricSourceDefinition(source="pg_stat_activity_snapshot_v1", target_shape="postgres"),
})

_POSTGRES_FIXED_TARGET_METRICS = frozenset({
    "cpu",
    "memory",
    "disk_io",
    "qps",
    "active_connections",
    "cache_hit_ratio",
})


class PostgresMetricCatalog:
    system = "postgresql"

    def __init__(
        self,
        *,
        extra_definitions: Mapping[str, MetricDefinition] | None = None,
        extra_sources: Mapping[str, PostgresMetricSourceDefinition] | None = None,
        catalog_version: str = "postgres-metric-catalog-v1",
    ) -> None:
        definitions = dict(_POSTGRES_DEFINITIONS)
        sources = dict(_POSTGRES_SOURCES)
        for raw_name, definition in (extra_definitions or {}).items():
            name = str(raw_name).casefold()
            if name in definitions:
                raise ValueError(f"PostgreSQL metric catalog duplicate definition: metric={name!r}")
            if definition.name.casefold() != name:
                raise ValueError(
                    f"PostgreSQL metric definition name differs from key: key={name!r}, definition={definition!r}"
                )
            definitions[name] = definition
        for raw_name, source in (extra_sources or {}).items():
            name = str(raw_name).casefold()
            if name not in definitions:
                raise ValueError(f"PostgreSQL metric source has no definition: metric={name!r}")
            if name in sources:
                raise ValueError(f"PostgreSQL metric catalog duplicate source: metric={name!r}")
            sources[name] = source
        missing_sources = set(definitions) - set(sources)
        if missing_sources:
            raise ValueError(f"PostgreSQL metric definitions have no source: metrics={sorted(missing_sources)!r}")
        self._definitions = MappingProxyType(definitions)
        self._sources = MappingProxyType(sources)
        self._catalog_version = str(catalog_version)

    @property
    def metric_names(self) -> frozenset[str]:
        return frozenset(self._definitions)

    def definition(self, metric: str) -> MetricDefinition:
        normalized = str(metric).casefold()
        try:
            return self._definitions[normalized]
        except KeyError as exc:
            raise ValueError(
                f"Unknown PostgreSQL time-series metric: metric={metric!r}, expected={sorted(self.metric_names)!r}"
            ) from exc

    def target_variants(self, metric: str, deployment: object) -> tuple[str | None, ...]:
        self.definition(metric)
        return (None,)

    def validate_target(self, metric: str, target: str | None, deployment: object) -> None:
        definition = self.definition(metric)
        if definition.name in _POSTGRES_FIXED_TARGET_METRICS and target is not None:
            raise ValueError(
                f"PostgreSQL metric target must be None: metric={metric!r}, target={target!r}, expected_target=None"
            )
        if definition.name not in _POSTGRES_FIXED_TARGET_METRICS and target is not None and not str(target).strip():
            raise ValueError(
                f"PostgreSQL metric target must be a non-empty selector: metric={metric!r}, target={target!r}"
            )

    def series_target(self, metric: str) -> str:
        return self._sources[str(metric).casefold()].target_shape

    def fingerprint(self) -> str:
        payload = {
            "system": self.system,
            "catalog_version": self._catalog_version,
            "metrics": [
                {
                    "name": definition.name,
                    "fields": definition.value_fields,
                    "lookback_seconds": definition.lookback_seconds,
                    "source_step_seconds": definition.source_step_seconds,
                    "lower_bound": definition.lower_bound,
                    "upper_bound": definition.upper_bound,
                    "target_shape": self._sources[definition.name].target_shape,
                    "source": self._sources[definition.name].source,
                }
                for definition in self._definitions.values()
            ],
            "pg_stat_statements_query": PG_STATEMENT_SNAPSHOT_SQL,
            "cgroup_source_version": "cpu.stat,memory.current,memory.stat,io.stat-v1",
            "target_rule": "fixed postgres series or provider-selected relation/checkout series",
            "sample_interval_seconds": 2,
        }
        return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class CompositePostgresMetricCatalog:
    """Run-local public catalog combining base PG metrics with adapter metrics."""

    system = "postgresql"

    def __init__(self, extensions: Mapping[str, MetricDefinition]) -> None:
        normalized = {str(name).casefold(): definition for name, definition in extensions.items()}
        collisions = sorted(set(normalized).intersection(POSTGRES_METRIC_CATALOG.metric_names))
        if collisions:
            raise ValueError(f"PostgreSQL scenario metric names collide with the base catalog: metrics={collisions!r}")
        self._extensions = MappingProxyType(normalized)

    @property
    def metric_names(self) -> frozenset[str]:
        return frozenset(POSTGRES_METRIC_CATALOG.metric_names | set(self._extensions))

    def definition(self, metric: str) -> MetricDefinition:
        normalized = str(metric).casefold()
        if normalized in self._extensions:
            return self._extensions[normalized]
        return POSTGRES_METRIC_CATALOG.definition(normalized)

    def target_variants(self, metric: str, deployment: object) -> tuple[str | None, ...]:
        self.definition(metric)
        return (None,)

    def series_target(self, metric: str) -> str:
        """Expose the shared catalog target shape for the composite catalog."""
        normalized = str(metric).casefold()
        if normalized in self._extensions:
            return "postgres"
        return POSTGRES_METRIC_CATALOG.series_target(normalized)

    def validate_target(self, metric: str, target: str | None, deployment: object) -> None:
        self.definition(metric)
        if target is not None:
            raise ValueError(
                f"PostgreSQL metric target must be None: metric={metric!r}, target={target!r}, expected_target=None"
            )

    def fingerprint(self) -> str:
        payload = {
            "base": POSTGRES_METRIC_CATALOG.fingerprint(),
            "extensions": {
                name: {
                    "fields": definition.value_fields,
                    "lookback_seconds": definition.lookback_seconds,
                    "source_step_seconds": definition.source_step_seconds,
                    "lower_bound": definition.lower_bound,
                    "upper_bound": definition.upper_bound,
                }
                for name, definition in sorted(self._extensions.items())
            },
        }
        return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


POSTGRES_METRIC_CATALOG = PostgresMetricCatalog()


class PostgresScenarioMetricCatalog:
    """Represent either a standalone or shared Case-owned metric catalog."""

    system = "postgresql"

    def __init__(
        self,
        scenario_provider=None,
        base: PostgresMetricCatalog = POSTGRES_METRIC_CATALOG,
        *,
        definitions: Mapping[str, MetricDefinition] | None = None,
        targets: Mapping[str, tuple[str, ...]] | None = None,
        version: str | None = None,
    ) -> None:
        if scenario_provider is not None and definitions is not None:
            raise TypeError("PostgreSQL scenario catalog accepts either a provider or standalone definitions")
        self.base = base if scenario_provider is not None else None
        self.scenario_provider = scenario_provider
        if scenario_provider is not None:
            definitions = scenario_provider.metric_definitions()
        if definitions is None:
            raise TypeError("PostgreSQL scenario catalog requires a provider or definitions")
        if not isinstance(definitions, Mapping) or not definitions:
            raise ValueError("PostgreSQL scenario metric definitions must be non-empty")
        normalized = {str(name).casefold(): definition for name, definition in definitions.items()}
        if self.base is not None:
            collisions = sorted(set(normalized) & set(self.base.metric_names))
            if collisions:
                raise ValueError(f"Scenario metric names collide with shared PostgreSQL catalog: metrics={collisions!r}")
        self._definitions = MappingProxyType(normalized)
        self._targets = MappingProxyType({
            str(name).casefold(): tuple(values)
            for name, values in (targets or {}).items()
        })
        self._version = str(version or "postgres-scenario-metric-catalog-v1")

    @property
    def metric_names(self) -> frozenset[str]:
        if self.base is None:
            return frozenset(self._definitions)
        return frozenset(set(self.base.metric_names) | set(self._definitions))

    def definition(self, metric: str) -> MetricDefinition:
        normalized = str(metric).casefold()
        if normalized in self._definitions:
            return self._definitions[normalized]
        if self.base is None:
            raise ValueError(
                f"Unknown PostgreSQL scenario metric: metric={metric!r}, expected={sorted(self.metric_names)!r}"
            )
        return self.base.definition(normalized)

    def target_variants(self, metric: str, deployment: object) -> tuple[str | None, ...]:
        normalized = str(metric).casefold()
        if normalized in self._definitions:
            variants = (
                tuple(self.scenario_provider.target_variants(normalized))
                if self.scenario_provider is not None
                else (None, *self._targets.get(normalized, ()))
            )
            if not variants or len(set(variants)) != len(variants):
                raise ValueError(f"Scenario metric target variants must be non-empty and unique: metric={normalized!r}, variants={variants!r}")
            return variants
        if self.base is None:
            raise ValueError(f"Unknown PostgreSQL scenario metric: metric={metric!r}")
        return self.base.target_variants(normalized, deployment)

    def validate_target(self, metric: str, target: str | None, deployment: object) -> None:
        normalized = str(metric).casefold()
        if normalized in self._definitions:
            allowed = self.target_variants(normalized, deployment)
            if target not in allowed:
                raise ValueError(
                    f"Scenario metric target is unavailable: metric={normalized!r}, target={target!r}, "
                    f"allowed={allowed!r}"
                )
            return
        if self.base is None:
            raise ValueError(f"Unknown PostgreSQL scenario metric: metric={metric!r}")
        self.base.validate_target(normalized, target, deployment)

    def series_target(self, metric: str) -> str:
        """Return the public target shape used by the shared tool contract."""
        normalized = str(metric).casefold()
        if normalized not in self._definitions:
            if self.base is None:
                raise ValueError(f"Unknown PostgreSQL scenario metric: metric={metric!r}")
            return self.base.series_target(normalized)
        variants = self.target_variants(normalized, object())
        return "postgres" if variants == (None,) else "scenario_target"

    def fingerprint(self) -> str:
        payload = {
            "base": self.base.fingerprint() if self.base is not None else None,
            "version": self._version,
            "scenario": {
                name: {
                    "fields": definition.value_fields,
                    "lookback_seconds": definition.lookback_seconds,
                    "source_step_seconds": definition.source_step_seconds,
                    "lower_bound": definition.lower_bound,
                    "upper_bound": definition.upper_bound,
                    "targets": self.target_variants(name, object()),
                }
                for name, definition in sorted(self._definitions.items())
            },
        }
        provider_fingerprint = getattr(self.scenario_provider, "fingerprint", None)
        if callable(provider_fingerprint):
            payload["scenario_fingerprint"] = provider_fingerprint()
        return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()


class CompositePostgresMetricProvider:
    """Route shared PG samples and Case-owned samples through one MetricService."""

    def __init__(self, base: "LivePostgresSamplerMetricProvider", scenario_provider, catalog: PostgresScenarioMetricCatalog) -> None:
        self.base = base
        self.scenario_provider = scenario_provider
        self.catalog = catalog
        self.lock = base.lock

    @property
    def available_range(self) -> tuple[int, int]:
        return self.base.available_range

    def reset(self) -> None:
        self.base.reset()
        reset = getattr(self.scenario_provider, "reset", None)
        if callable(reset):
            reset()

    def append_sample(self, timestamp_ms: int, values: Mapping[str, Mapping[str, float]]) -> None:
        self.base.append_sample(timestamp_ms, values)

    def query(self, query: MetricQuery) -> MetricFrame:
        if query.metric in self.scenario_provider.metric_names:
            return self.scenario_provider.query_metric(query)
        return self.base.query(query)

    def capture(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
    ) -> tuple[MetricFrame, ...]:
        shared = tuple(metric for metric in metrics if str(metric).casefold() not in self.scenario_provider.metric_names)
        scenario = tuple(metric for metric in metrics if str(metric).casefold() in self.scenario_provider.metric_names)
        frames = list(self.base.capture(shared, start_epoch_ms, end_epoch_ms, step_seconds)) if shared else []
        if scenario:
            frames.extend(self.scenario_provider.capture(scenario, start_epoch_ms, end_epoch_ms, step_seconds))
        return tuple(frames)
def read_device_io_stats(*, proc_path: str | Path = "/proc/diskstats") -> tuple[int, int]:
    """Read kernel device queue counters for internal history samplers.

    This is a sampler helper, not an Agent tool or a scenario-specific
    aggregation interface. The values are the Linux in-flight and weighted
    I/O-time counters summed across visible block devices.
    """
    in_flight = 0
    weighted_io_ms = 0
    try:
        with Path(proc_path).open(encoding="utf-8") as stream:
            for line in stream:
                fields = line.split()
                if len(fields) < 14:
                    continue
                in_flight += int(fields[11])
                weighted_io_ms += int(fields[13])
    except (OSError, TypeError, ValueError) as exc:
        raise RuntimeError(
            f"PostgreSQL device I/O counters are unavailable: path={proc_path!r}"
        ) from exc
    return in_flight, weighted_io_ms


def _postgres_metric_description(
    definition: MetricDefinition,
    catalog: PostgresMetricCatalog = POSTGRES_METRIC_CATALOG,
) -> str:
    target_shape = catalog.series_target(definition.name)
    fixed_target_metrics = getattr(catalog, "fixed_target_metrics", _POSTGRES_FIXED_TARGET_METRICS)
    if definition.name in fixed_target_metrics:
        target_description = f"query_target=None; series_target={target_shape!r}"
    elif target_shape == "relation":
        target_description = "query_target=relation name or null; series_target=relation name"
    else:
        target_description = f"query_target={target_shape!r} or null; series_target={target_shape!r}"
    bounds = {
        "lower_bound": definition.lower_bound,
        "upper_bound": definition.upper_bound,
    }
    return (
        f"PostgreSQL metric {definition.name}; fields={definition.value_fields!r}; "
        f"{target_description}; bounds={bounds!r}"
    )


POSTGRES_QUERY_METRICS_TOOL_DEFINITION = {
    "tool_name": "query_metrics",
        "tool_description": (
            "查询 PostgreSQL 时序观测。metric 类型、字段、target scope 和数值边界来自当前 "
            "PostgreSQL metric catalog；历史窗口使用 UTC 时间和固定 sampler step。当前状态 SQL 细节使用 "
            "execute_sql。"
    ),
    "parameter_definitions": [
        {
            "parameter_name": "metric_type",
            "data_type": "string",
            "required": True,
            "allowed_values": sorted(POSTGRES_METRIC_CATALOG.metric_names),
            "parameter_description": "Catalog 中声明的 PostgreSQL metric 名称。",
        },
        {
            "parameter_name": "target",
            "data_type": "string|null",
            "required": False,
            "default_value": None,
            "parameter_description": "基础时序 target 省略或为 null；场景 relation/service metric 可用 target 选择实体，省略则返回全部可用 series。",
        },
        {
            "parameter_name": "limit",
            "data_type": "integer|null",
            "required": False,
            "parameter_description": "未指定时间窗时，每个时序 series 返回的最新点数；显式历史窗口保持完整。",
        },
        {
            "parameter_name": "start_timestamp",
            "data_type": "string|null",
            "required": False,
            "parameter_description": "UTC 窗口开始时间，格式 YYYY-MM-DD HH:mm:ss；必须和 end_timestamp 一起提供。",
        },
        {
            "parameter_name": "end_timestamp",
            "data_type": "string|null",
            "required": False,
            "parameter_description": "UTC 窗口结束时间，格式 YYYY-MM-DD HH:mm:ss；必须和 start_timestamp 一起提供。",
        },
        {
            "parameter_name": "step_seconds",
            "data_type": "integer|null",
            "required": False,
            "parameter_description": "固定 sampler step 的正整数倍；显式 history capture 使用 catalog sampler step。",
        },
    ],
    "metric_definitions": [
        {
            "metric_name": definition.name,
            "metric_description": _postgres_metric_description(definition),
            "target_scope": {
                "query_target": (
                    None
                    if definition.name in _POSTGRES_FIXED_TARGET_METRICS
                    else f"{_POSTGRES_SOURCES[definition.name].target_shape}|null"
                ),
                "series_target": (
                    "postgres"
                    if _POSTGRES_SOURCES[definition.name].target_shape == "postgres"
                    else _POSTGRES_SOURCES[definition.name].target_shape
                ),
                "fields": list(definition.value_fields),
                "lower_bound": definition.lower_bound,
                "upper_bound": definition.upper_bound,
            },
        }
        for definition in sorted(
            (POSTGRES_METRIC_CATALOG.definition(metric) for metric in POSTGRES_METRIC_CATALOG.metric_names),
            key=lambda item: item.name,
        )
    ],
    "result_description": (
        "返回固定 UTC epoch-ms 采样网格渲染成的 series；采样不完整或窗口越界返回 error。"
        "长 overview 的 timestamps 使用 {start,end,step_seconds,count} 表示固定网格，"
        "数值数组仍包含每个采样点；显式 2 秒窗口返回逐点 UTC timestamps。"
        + QUERY_METRICS_BOUND_CONTRACT
    ),
}


def postgres_query_metrics_tool_definition(catalog: PostgresMetricCatalog) -> dict:
    """Build the public query_metrics contract from the bound catalog."""
    fixed_target_metrics = getattr(catalog, "fixed_target_metrics", _POSTGRES_FIXED_TARGET_METRICS)
    metric_definitions = []
    for definition in sorted(
        (catalog.definition(metric) for metric in catalog.metric_names),
        key=lambda item: item.name,
    ):
        target_shape = catalog.series_target(definition.name)
        metric_definitions.append({
            "metric_name": definition.name,
            "metric_description": _postgres_metric_description(definition, catalog),
            "target_scope": {
                "query_target": (
                    None
                    if definition.name in fixed_target_metrics
                    else f"{target_shape}|null"
                ),
                "series_target": "postgres" if target_shape == "postgres" else target_shape,
                "fields": list(definition.value_fields),
                "lower_bound": definition.lower_bound,
                "upper_bound": definition.upper_bound,
            },
        })
    return {
        "tool_name": "query_metrics",
        "tool_description": (
            "查询 PostgreSQL 时序观测。metric 类型、字段、target scope 和数值边界来自当前 "
            "PostgreSQL metric catalog；历史窗口使用 UTC 时间和固定 sampler step。"
        ),
        "parameter_definitions": [
            {
                "parameter_name": "metric_type",
                "data_type": "string",
                "required": True,
                "allowed_values": sorted(catalog.metric_names),
                "parameter_description": "当前 catalog 中声明的 PostgreSQL metric 名称。",
            },
            {
                "parameter_name": "target",
                "data_type": "string|null",
                "required": False,
                "default_value": None,
                "parameter_description": "基础时序 target 省略或为 null；relation/service metric 可使用已声明的 target。",
            },
            {
                "parameter_name": "limit",
                "data_type": "integer|null",
                "required": False,
                "parameter_description": "未指定时间窗时，每个时序 series 返回的最新点数；显式历史窗口保持完整。",
            },
            {
                "parameter_name": "start_timestamp",
                "data_type": "string|null",
                "required": False,
                "parameter_description": "UTC 窗口开始时间，格式 YYYY-MM-DD HH:mm:ss；必须和 end_timestamp 一起提供。",
            },
            {
                "parameter_name": "end_timestamp",
                "data_type": "string|null",
                "required": False,
                "parameter_description": "UTC 窗口结束时间，格式 YYYY-MM-DD HH:mm:ss；必须和 start_timestamp 一起提供。",
            },
            {
                "parameter_name": "step_seconds",
                "data_type": "integer|null",
                "required": False,
                "parameter_description": "固定 sampler step 的正整数倍；显式 history capture 使用 catalog sampler step。",
            },
        ],
        "metric_definitions": metric_definitions,
        "result_description": (
            "返回固定 UTC epoch-ms 采样网格渲染成的 series；采样不完整或窗口越界返回 error。"
            "长 overview 的 timestamps 使用 {start,end,step_seconds,count} 表示固定网格，"
            "数值数组仍包含每个采样点；显式 2 秒窗口返回逐点 UTC timestamps。"
            + QUERY_METRICS_BOUND_CONTRACT
        ),
    }


class LivePostgresSamplerMetricProvider:
    """Serve the bounded live PG sampler ring and capture exact windows."""

    def __init__(
        self,
        *,
        sample_interval_sec: int,
        max_points: int = 300,
        catalog: PostgresMetricCatalog = POSTGRES_METRIC_CATALOG,
    ) -> None:
        if sample_interval_sec <= 0:
            raise ValueError(f"PostgreSQL sampler interval must be positive: sample_interval_sec={sample_interval_sec}")
        if max_points <= 0:
            raise ValueError(f"PostgreSQL sampler max_points must be positive: max_points={max_points}")
        self.sample_interval_sec = int(sample_interval_sec)
        self.max_points = int(max_points)
        self.catalog = catalog
        self.lock = threading.RLock()
        self._samples: dict[str, deque[tuple[int, Mapping[str, float]]]] = {
            metric: deque(maxlen=max_points)
            for metric in catalog.metric_names
        }

    @property
    def available_range(self) -> tuple[int, int]:
        with self.lock:
            ranges = {
                metric: (samples[0][0], samples[-1][0])
                for metric, samples in self._samples.items()
                if samples
            }
            if not ranges:
                raise RuntimeError("PostgreSQL metric sampler has no data yet")
            start = max(item[0] for item in ranges.values())
            end = min(item[1] for item in ranges.values())
            if start > end:
                raise RuntimeError(
                    f"PostgreSQL metric sampler has no common data range: ranges={ranges!r}"
                )
            return start, end

    def contiguous_start_ms(self, metrics: tuple[str, ...], minimum_samples: int = 4) -> int | None:
        """Return the start of the latest common fixed-grid sample run."""
        if minimum_samples <= 0:
            raise ValueError(f"minimum_samples must be positive: minimum_samples={minimum_samples}")
        with self.lock:
            timestamp_sets = [
                {timestamp for timestamp, _ in self._samples[self.catalog.definition(metric).name]}
                for metric in metrics
            ]
            if not timestamp_sets:
                return None
            common = sorted(set.intersection(*timestamp_sets))
            if len(common) < minimum_samples:
                return None
            run_start = len(common) - 1
            run_length = 1
            while run_start > 0 and common[run_start] - common[run_start - 1] == self.sample_interval_sec * 1000:
                run_start -= 1
                run_length += 1
            if run_length < minimum_samples:
                return None
            return common[run_start]

    def reset(self) -> None:
        with self.lock:
            for samples in self._samples.values():
                samples.clear()

    def resize(self, max_points: int) -> None:
        """Resize the sampler ring before a capture lifecycle starts."""
        if not isinstance(max_points, int) or isinstance(max_points, bool) or max_points <= 0:
            raise ValueError(f"PostgreSQL sampler max_points must be a positive integer: max_points={max_points!r}")
        with self.lock:
            if max_points == self.max_points:
                return
            self.max_points = max_points
            self._samples = {
                metric: deque(samples, maxlen=max_points)
                for metric, samples in self._samples.items()
            }

    def append_sample(self, timestamp_ms: int, values: Mapping[str, Mapping[str, float]]) -> None:
        with self.lock:
            if not isinstance(timestamp_ms, int) or isinstance(timestamp_ms, bool) or timestamp_ms < 0:
                raise TypeError(f"PostgreSQL sampler timestamp must be a non-negative epoch millisecond integer: timestamp_ms={timestamp_ms!r}")
            if timestamp_ms % (self.sample_interval_sec * 1000):
                raise ValueError(
                    f"PostgreSQL sampler timestamp is not on its fixed grid: timestamp_ms={timestamp_ms}, "
                    f"sample_interval_sec={self.sample_interval_sec}"
                )
            for metric, raw_fields in values.items():
                definition = self.catalog.definition(metric)
                if set(raw_fields) != set(definition.value_fields):
                    raise ValueError(
                        f"PostgreSQL sampler fields differ from catalog: metric={metric!r}, "
                        f"expected={definition.value_fields!r}, actual={tuple(raw_fields)!r}"
                    )
                fields = {field: float(raw_fields[field]) for field in definition.value_fields}
                if any(not math.isfinite(value) for value in fields.values()):
                    raise ValueError(f"PostgreSQL sampler contains non-finite values: metric={metric!r}, values={fields!r}")
                frame = MetricFrame(
                    metric=metric,
                    query_target=None,
                    step_seconds=self.sample_interval_sec,
                    series={
                        self.catalog.series_target(definition.name):
                        {field: (value,) for field, value in fields.items()}
                    },
                    timestamps_ms={self.catalog.series_target(definition.name): (timestamp_ms,)},
                )
                validate_metric_frame(frame, self.catalog)
                samples = self._samples[definition.name]
                if samples and timestamp_ms <= samples[-1][0]:
                    raise ValueError(
                        f"PostgreSQL sampler timestamp is not strictly increasing: metric={definition.name!r}, "
                        f"previous_timestamp_ms={samples[-1][0]}, timestamp_ms={timestamp_ms}"
                    )
                samples.append((timestamp_ms, MappingProxyType(fields)))

    def _frame_from_samples(
        self,
        definition: MetricDefinition,
        selected: tuple[tuple[int, Mapping[str, float]], ...],
    ) -> MetricFrame:
        if not selected:
            raise RuntimeError(f"PostgreSQL metric query has no selected samples: metric={definition.name!r}")
        timestamps = tuple(timestamp for timestamp, _ in selected)
        series = {
            field: tuple(fields[field] for _, fields in selected)
            for field in definition.value_fields
        }
        frame = MetricFrame(
            metric=definition.name,
            query_target=None,
            step_seconds=self.sample_interval_sec,
            series={self.catalog.series_target(definition.name): series},
            timestamps_ms={self.catalog.series_target(definition.name): timestamps},
        )
        validate_metric_frame(frame, self.catalog)
        return frame

    def query(self, query: MetricQuery) -> MetricFrame:
        definition = self.catalog.definition(query.metric)
        if query.target is not None:
            self.catalog.validate_target(definition.name, query.target, object())
        with self.lock:
            samples = self._samples[definition.name]
            if not samples:
                raise RuntimeError(f"PostgreSQL metric sampler has no data: metric={definition.name!r}")
            if query.start_epoch_ms is None:
                end_ms = samples[-1][0]
                start_index = max(0, len(samples) - self.max_points)
                start_ms = samples[start_index][0]
            else:
                start_ms = query.start_epoch_ms
                end_ms = query.end_epoch_ms
            selected = tuple(
                (timestamp, fields)
                for timestamp, fields in samples
                if start_ms <= timestamp <= end_ms
            )
            available_start, available_end = samples[0][0], samples[-1][0]
        if start_ms < available_start or end_ms > available_end:
            raise ValueError(
                f"PostgreSQL metric query exceeds sampler ring buffer: metric={definition.name!r}, "
                f"requested=({start_ms},{end_ms}), available=({available_start},{available_end})"
            )
        frame = self._frame_from_samples(definition, selected)
        step = query.step_seconds or self.sample_interval_sec
        if step <= 0:
            raise ValueError(f"PostgreSQL metric query step must be positive: metric={definition.name!r}, step_seconds={step}")
        if step != self.sample_interval_sec:
            frame = frame.resample(step, start_ms, end_ms)
            validate_metric_frame(frame, self.catalog)
        return frame

    def capture(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
    ) -> tuple[MetricFrame, ...]:
        if start_epoch_ms >= end_epoch_ms:
            raise ValueError(
                f"PostgreSQL metric capture window must be positive: start_epoch_ms={start_epoch_ms}, end_epoch_ms={end_epoch_ms}"
            )
        if step_seconds <= 0:
            raise ValueError(f"PostgreSQL metric capture step must be positive: step_seconds={step_seconds}")
        if (end_epoch_ms - start_epoch_ms) % (step_seconds * 1000):
            raise ValueError(
                f"PostgreSQL metric capture window must align to sampler grid: start_epoch_ms={start_epoch_ms}, "
                f"end_epoch_ms={end_epoch_ms}, step_seconds={step_seconds}"
            )
        if len(set(metrics)) != len(metrics):
            raise ValueError(f"PostgreSQL metric capture has duplicate metrics: metrics={metrics!r}")
        expected_timestamps = tuple(range(start_epoch_ms, end_epoch_ms + 1, step_seconds * 1000))
        copied: list[tuple[MetricDefinition, tuple[tuple[int, Mapping[str, float]], ...]]] = []
        with self.lock:
            for raw_metric in metrics:
                definition = self.catalog.definition(str(raw_metric).casefold())
                samples = tuple(self._samples[definition.name])
                if not samples:
                    raise RuntimeError(f"PostgreSQL metric sampler has no data: metric={definition.name!r}")
                available_start, available_end = samples[0][0], samples[-1][0]
                if start_epoch_ms < available_start or end_epoch_ms > available_end:
                    raise ValueError(
                        f"PostgreSQL metric capture exceeds sampler ring buffer: metric={definition.name!r}, "
                        f"requested=({start_epoch_ms},{end_epoch_ms}), available=({available_start},{available_end})"
                    )
                selected = tuple(
                    (timestamp, fields)
                    for timestamp, fields in samples
                    if start_epoch_ms <= timestamp <= end_epoch_ms
                )
                actual = tuple(timestamp for timestamp, _ in selected)
                if actual != expected_timestamps:
                    raise RuntimeError(
                        f"PostgreSQL metric capture has missing or extra samples: metric={definition.name!r}, "
                        f"expected_timestamps={expected_timestamps!r}, actual_timestamps={actual!r}"
                    )
                copied.append((definition, selected))
        frames = tuple(self._frame_from_samples(definition, selected) for definition, selected in copied)
        if any(tuple(frame.timestamps_ms.values()) != (expected_timestamps,) for frame in frames):
            raise RuntimeError(
                f"PostgreSQL metric capture frames are not timestamp aligned: "
                f"metrics={tuple(frame.metric for frame in frames)!r}"
            )
        return frames


class LivePostgresScenarioMetricProvider:
    """Store aligned raw scenario metrics without converting them to conclusions."""

    def __init__(self, *, catalog: PostgresScenarioMetricCatalog, sample_interval_sec: int, max_points: int) -> None:
        if sample_interval_sec <= 0 or max_points <= 0:
            raise ValueError("Scenario metric provider requires positive sampling and retention limits")
        self.catalog = catalog
        self.sample_interval_sec = int(sample_interval_sec)
        self.lock = threading.RLock()
        self._samples: dict[str, dict[str, deque[tuple[int, Mapping[str, float]]]]] = {
            metric: {} for metric in catalog.metric_names
        }
        self._max_points = int(max_points)

    @property
    def metric_names(self) -> frozenset[str]:
        return self.catalog.metric_names

    @property
    def frames(self) -> tuple[MetricFrame, ...]:
        with self.lock:
            return self._frames_from_samples(tuple(self.catalog.metric_names))

    @property
    def available_range(self) -> tuple[int, int]:
        with self.lock:
            ranges = [
                (samples[0][0], samples[-1][0])
                for metric in self._samples.values()
                for samples in metric.values()
                if samples
            ]
            if not ranges:
                raise RuntimeError("PostgreSQL scenario metric provider has no data yet")
            start = max(item[0] for item in ranges)
            end = min(item[1] for item in ranges)
            if start > end:
                raise RuntimeError(f"PostgreSQL scenario metric provider has no common range: ranges={ranges!r}")
            return start, end

    def append_sample(self, timestamp_ms: int, values: Mapping[str, Mapping[str, Mapping[str, float]]]) -> None:
        if timestamp_ms % (self.sample_interval_sec * 1000):
            raise ValueError(f"Scenario metric timestamp is not aligned: timestamp_ms={timestamp_ms}")
        with self.lock:
            for raw_metric, raw_series in values.items():
                definition = self.catalog.definition(raw_metric)
                series_store = self._samples[definition.name]
                expected_targets = set(self.catalog._targets.get(definition.name, ())) or {"postgres"}
                if set(raw_series) != expected_targets:
                    raise ValueError(
                        f"Scenario metric series targets differ from catalog: metric={definition.name!r}, "
                        f"expected={sorted(expected_targets)!r}, actual={sorted(raw_series)!r}"
                    )
                for target, raw_fields in raw_series.items():
                    if set(raw_fields) != set(definition.value_fields):
                        raise ValueError(
                            f"Scenario metric fields differ from catalog: metric={definition.name!r}, target={target!r}"
                        )
                    fields = MappingProxyType({field: float(raw_fields[field]) for field in definition.value_fields})
                    if any(not math.isfinite(value) for value in fields.values()):
                        raise ValueError(f"Scenario metric contains non-finite values: metric={definition.name!r}")
                    validate_metric_frame(
                        MetricFrame(
                            metric=definition.name,
                            query_target=None,
                            step_seconds=self.sample_interval_sec,
                            series={target: {field: (value,) for field, value in fields.items()}},
                            timestamps_ms={target: (timestamp_ms,)},
                        ),
                        self.catalog,
                    )
                    samples = series_store.setdefault(target, deque(maxlen=self._max_points))
                    if samples and timestamp_ms <= samples[-1][0]:
                        raise ValueError(
                            f"Scenario metric timestamp is not increasing: metric={definition.name!r}, target={target!r}"
                        )
                    samples.append((timestamp_ms, fields))

    def _frame_from_selected(
        self,
        metric: str,
        selected: Mapping[str, tuple[tuple[int, Mapping[str, float]], ...]],
        query_target: str | None,
    ) -> MetricFrame:
        definition = self.catalog.definition(metric)
        series = {
            target: {field: tuple(fields[field] for _, fields in samples) for field in definition.value_fields}
            for target, samples in selected.items()
        }
        timestamps = {target: tuple(timestamp for timestamp, _ in samples) for target, samples in selected.items()}
        frame = MetricFrame(
            metric=definition.name,
            query_target=query_target,
            step_seconds=self.sample_interval_sec,
            series=series,
            timestamps_ms=timestamps,
        )
        validate_metric_frame(frame, self.catalog)
        return frame

    def _frames_from_samples(
        self,
        metrics: tuple[str, ...],
        start_ms: int | None = None,
        end_ms: int | None = None,
    ) -> tuple[MetricFrame, ...]:
        frames = []
        for raw_metric in metrics:
            metric = self.catalog.definition(raw_metric).name
            series_store = self._samples[metric]
            selected = {
                target: tuple(
                    item for item in samples
                    if start_ms is None or (start_ms <= item[0] <= end_ms)
                )
                for target, samples in series_store.items()
            }
            selected = {target: samples for target, samples in selected.items() if samples}
            if not selected:
                raise RuntimeError(f"PostgreSQL scenario metric has no selected samples: metric={metric!r}")
            frames.append(self._frame_from_selected(metric, selected, None))
        return tuple(sorted(frames, key=lambda frame: metric_variant_sort_key((frame.metric, frame.query_target))))

    def capture(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
    ) -> tuple[MetricFrame, ...]:
        if step_seconds <= 0:
            raise ValueError(f"Scenario metric capture step must be positive: step_seconds={step_seconds}")
        expected = tuple(range(start_epoch_ms, end_epoch_ms + 1, step_seconds * 1000))
        with self.lock:
            frames = []
            for raw_metric in metrics:
                metric = self.catalog.definition(raw_metric).name
                selected = {
                    target: tuple(item for item in samples if start_epoch_ms <= item[0] <= end_epoch_ms)
                    for target, samples in self._samples[metric].items()
                }
                if any(tuple(timestamp for timestamp, _ in samples) != expected for samples in selected.values()):
                    raise RuntimeError(f"Scenario metric capture has missing samples: metric={metric!r}")
                frames.append(self._frame_from_selected(metric, selected, None))
            return tuple(sorted(frames, key=lambda frame: metric_variant_sort_key((frame.metric, frame.query_target))))

    def query(self, query: MetricQuery) -> MetricFrame:
        metric = self.catalog.definition(query.metric).name
        self.catalog.validate_target(metric, query.target, object())
        with self.lock:
            selected = {
                target: tuple(
                    item for item in samples
                    if query.start_epoch_ms is None or query.start_epoch_ms <= item[0] <= query.end_epoch_ms
                )
                for target, samples in self._samples[metric].items()
                if query.target is None or target == query.target
            }
            selected = {target: samples for target, samples in selected.items() if samples}
            if not selected:
                raise RuntimeError(f"PostgreSQL scenario metric has no selected samples: metric={metric!r}")
            frame = self._frame_from_selected(metric, selected, query.target)
        step = query.step_seconds or self.sample_interval_sec
        if step != frame.step_seconds:
            timestamp_values = frame.timestamps_ms[next(iter(frame.timestamps_ms))]
            frame = frame.resample(
                step,
                query.start_epoch_ms or timestamp_values[0],
                query.end_epoch_ms or timestamp_values[-1],
            )
        return frame


__all__ = [
    "CompositePostgresMetricCatalog",
    "LivePostgresSamplerMetricProvider",
    "LivePostgresScenarioMetricProvider",
    "PostgresMetricCatalog",
    "PostgresScenarioMetricCatalog",
    "CompositePostgresMetricProvider",
    "POSTGRES_METRIC_CATALOG",
    "POSTGRES_QUERY_METRICS_TOOL_DEFINITION",
    "postgres_query_metrics_tool_definition",
    "read_device_io_stats",
]
