"""Real cgroup-v2 CPU quota governance for PostgreSQL and sibling jobs."""

from __future__ import annotations

import json
import hashlib
import math
import os
import re
import subprocess
import threading
import time
from collections import deque
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Mapping

from src.execution.environment import PGEnv, Tool, lazy_agent_text
from src.execution.history.metrics import MetricService
from src.execution.postgres_metrics import LivePostgresSamplerMetricProvider
from src.execution.history.metrics import (
    MetricDefinition,
    MetricFrame,
    MetricQuery,
    format_utc_timestamp,
    metric_variant_sort_key,
    parse_utc_timestamp,
    render_metric_frame,
    validate_metric_frame,
)
from src.execution.history.records import (
    CapturedRecords,
    HistoricalCoverage,
    HistoricalIntervalRecord,
    HistoricalPointRecord,
    HistoricalRecordSource,
)
from src.scenarios.evaluation.postgres.resource_governance.container_cpu_budget import (
    PgResourceGovernanceContainerCpuBudgetForDbQuotaThrottleEvaluatorCase,
    PgResourceGovernanceContainerCpuBudgetForDbQuotaThrottleSimpleEvaluatorCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)
from src.scenarios.workloads import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    WorkloadProfile,
)

from ...base import (
    CaseResourceSpec,
    DifficultyCalibration,
    FaultPlan,
    PostgresCaseRuntime,
    PostgresScenario,
    PostgresScenarioCase,
)


SCENARIO_ID = "pg_resource_governance_container_cpu_budget"
BASE_IMAGE_NAME = "aiopsbench-pg-initialized:latest"
SIBLING_IMAGE_NAME = "busybox:1.26.2"
EXTERNAL_NEIGHBOR_JOB_ID = "analytics_neighbor"
RESOURCE_GOVERNANCE_CPU_RESOURCES = CaseResourceSpec(
    worker_physical_cores=4,
    worker_memory_mb=4096,
    container_cpu_limit=2.0,
    container_memory_mb=2048,
)

CPU_BUDGET_METRICS = frozenset({
    "host_cpu",
    "host_cpu_pressure",
    "cgroup_cpu_usage",
    "cgroup_cpu_throttle",
    "process_cpu",
    "service_slo",
    "job_progress",
})

_CPU_BUDGET_DEFINITIONS = {
    "host_cpu": MetricDefinition(
        name="host_cpu",
        value_fields=("usage_percent", "idle_percent", "load1", "run_queue"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "host_cpu_pressure": MetricDefinition(
        name="host_cpu_pressure",
        value_fields=("some_percent", "full_percent"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "cgroup_cpu_usage": MetricDefinition(
        name="cgroup_cpu_usage",
        value_fields=("usage_cores", "quota_cores", "periods_delta"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "cgroup_cpu_throttle": MetricDefinition(
        name="cgroup_cpu_throttle",
        value_fields=("nr_throttled_delta", "throttled_usec_delta", "pressure_some_percent"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "process_cpu": MetricDefinition(
        name="process_cpu",
        value_fields=("cpu_percent", "runnable_processes"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "service_slo": MetricDefinition(
        name="service_slo",
        value_fields=("throughput_per_sec", "p99_ms", "success_ratio"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=0.0,
        upper_bound=None,
    ),
    "job_progress": MetricDefinition(
        name="job_progress",
        value_fields=("completed_units", "units_per_sec", "deadline_remaining_sec"),
        lookback_seconds=0,
        source_step_seconds=2,
        lower_bound=None,
        upper_bound=None,
    ),
}


class CpuBudgetMetricCatalog:
    """Public frozen-history schema for the cgroup CPU governance case."""

    system = "postgresql"

    @property
    def metric_names(self) -> frozenset[str]:
        return CPU_BUDGET_METRICS

    @property
    def fixed_target_metrics(self) -> frozenset[str]:
        # Every query target is None; the returned entity aliases are
        # run-local series targets selected after the history is assembled.
        return CPU_BUDGET_METRICS

    def series_target(self, metric: str) -> str:
        self.definition(metric)
        return "run-local"

    def definition(self, metric: str) -> MetricDefinition:
        normalized = str(metric).casefold()
        try:
            return _CPU_BUDGET_DEFINITIONS[normalized]
        except KeyError as exc:
            raise ValueError(
                f"Unknown CPU budget metric: metric={metric!r}, expected={sorted(self.metric_names)!r}"
            ) from exc

    def target_variants(self, metric: str, deployment: object) -> tuple[str | None, ...]:
        self.definition(metric)
        return (None,)

    def validate_target(self, metric: str, target: str | None, deployment: object) -> None:
        self.definition(metric)
        if target is not None and not re.fullmatch(r"entity_[1-9][0-9]*", str(target)):
            raise ValueError(
                f"CPU budget metric target must be None or a run-local entity alias: "
                f"metric={metric!r}, target={target!r}"
            )

    def fingerprint(self) -> str:
        payload = {
            "system": self.system,
            "catalog_version": "pg-rg2-cpu-budget-v1",
            "metrics": [
                {
                    "name": definition.name,
                    "fields": definition.value_fields,
                    "source_step_seconds": definition.source_step_seconds,
                    "lower_bound": definition.lower_bound,
                    "upper_bound": definition.upper_bound,
                }
                for definition in sorted(_CPU_BUDGET_DEFINITIONS.values(), key=lambda item: item.name)
            ],
            "target_rule": "capture query_target=None; optional filters use run-local series aliases",
        }
        return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


def _json_result(value: object) -> dict:
    if isinstance(value, str):
        return json.loads(value)
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object, got {type(value).__name__}")
    return value


def _safe_name(value: str) -> str:
    return re.sub(r"[^a-z0-9_.-]+", "-", value.casefold()).strip("-")


def _parse_cpu_max(value: str) -> float | None:
    parts = value.strip().split()
    if len(parts) != 2:
        raise ValueError(f"invalid cgroup cpu.max: {value!r}")
    if parts[0] == "max":
        return None
    quota, period = int(parts[0]), int(parts[1])
    if quota <= 0 or period <= 0:
        raise ValueError(f"invalid cgroup cpu.max values: {value!r}")
    return quota / period


def _parse_cpu_stat(value: str) -> dict[str, int]:
    result = {}
    for line in value.splitlines():
        parts = line.split()
        if len(parts) == 2:
            result[parts[0]] = int(parts[1])
    return result


def _parse_psi(value: str) -> dict[str, float]:
    result = {}
    for line in value.splitlines():
        parts = line.split()
        if not parts:
            continue
        scope = parts[0]
        for item in parts[1:]:
            if "=" not in item:
                continue
            key, raw = item.split("=", 1)
            if key.startswith("avg"):
                result[f"{scope}_{key}"] = float(raw)
    return result


@dataclass(frozen=True, slots=True, kw_only=True)
class CpuBudgetSiblingJob:
    job_id: str
    kind: str
    initial_quota_cores: float
    minimum_quota_cores: float
    initial_weight: int
    deadline_seconds: float
    managed: bool = True
    cpu_burn_loops: int = 1

    def __post_init__(self) -> None:
        if not _IDENTIFIER.fullmatch(self.job_id):
            raise ValueError(f"invalid sibling job id: {self.job_id!r}")
        if self.initial_quota_cores <= 0 or self.minimum_quota_cores <= 0:
            raise ValueError("sibling CPU quotas must be positive")
        if self.minimum_quota_cores > self.initial_quota_cores:
            raise ValueError("sibling minimum quota cannot exceed initial quota")
        if self.initial_weight < 1 or self.deadline_seconds <= 0 or self.cpu_burn_loops < 1:
            raise ValueError("invalid sibling scheduling contract")


@dataclass(frozen=True, slots=True, kw_only=True)
class CpuBudgetExternalJob:
    job_id: str
    role: str
    reserved_quota_cores: float
    weight: int
    deadline_seconds: float | None
    minimum_quota_cores: float | None

    def __post_init__(self) -> None:
        if not _IDENTIFIER.fullmatch(self.job_id):
            raise ValueError(f"invalid external job id: {self.job_id!r}")
        if self.reserved_quota_cores <= 0 or self.weight < 1:
            raise ValueError("invalid external job reservation")
        if self.deadline_seconds is not None and self.deadline_seconds <= 0:
            raise ValueError("invalid external job deadline")
        if self.minimum_quota_cores is not None and self.minimum_quota_cores <= 0:
            raise ValueError("invalid external job minimum quota")


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceContainerCpuBudgetCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    sibling_image: str
    host_cpu_budget_cores: float
    external_neighbor_reserved_quota_cores: float
    external_neighbor_job_id: str
    external_neighbor_role: str
    external_neighbor_weight: int
    external_neighbor_deadline_seconds: float | None
    external_neighbor_minimum_quota_cores: float | None
    external_neighbor_jobs: tuple[CpuBudgetExternalJob, ...]
    initial_db_quota_cores: float
    fault_db_quota_cores: float
    recovery_db_quota_cores: float
    reference_db_quota_cores: float
    reference_sibling_quota_cores: tuple[float, ...]
    initial_db_weight: int
    fault_db_weight: int
    min_host_headroom_percent: float
    max_post_fix_host_psi_avg10: float
    max_post_fix_db_psi_avg10: float
    max_post_fix_throttled_usec: int
    max_oltp_p99_ms: float
    min_oltp_success_rate: float
    min_report_qps: float
    validation_window_seconds: float
    oltp_profile_name: str
    report_profile_names: tuple[str, ...]
    sibling_jobs: tuple[CpuBudgetSiblingJob, ...]

    @property
    def fault_image_name(self) -> str:
        suffix = self.case_id.replace("_", "-")
        return f"aiopsbench-pg-fault-{SCENARIO_ID.replace('_', '-')}-{suffix}:initialized"


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceContainerCpuBudgetForDbQuotaThrottleScenarioCase(
    PgResourceGovernanceContainerCpuBudgetCase
):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceContainerCpuBudgetForDbQuotaThrottleSimpleScenarioCase(
    PgResourceGovernanceContainerCpuBudgetCase
):
    pass


class CpuBudgetPGEnv(PGEnv):
    """PGEnv with only the cgroup controls owned by this scenario."""

    # Keep legacy controller aliases accepted by the non-history Case's
    # internal compatibility path; frozen-history schemas still derive their
    # public enum from the case-owned catalog below.
    AGENT_METRICS = CPU_BUDGET_METRICS | frozenset({
        "resource_history",
        "cpu_budget",
        "cgroup_cpu",
        "resource_governance_cpu",
        "workload_activity",
    })

    def metric_history_catalog(self):
        if getattr(self, "_case", None) is not None and getattr(self._case, "frozen_history", None) is not None:
            return CpuBudgetMetricCatalog()
        return super().metric_history_catalog()

    def configure_case(self, case) -> None:
        if getattr(case, "frozen_history", None) is not None:
            # PGEnv builds the public tool schema from _metric_catalog. Keep
            # that catalog aligned with the case-owned history catalog so the
            # model can see the seven raw cgroup metrics it is expected to
            # reason over instead of unrelated generic PG sampler metrics.
            # The controller-owned history path has no frozen_history
            # adapter, so the shared metric service must be rebuilt here too;
            # otherwise bind_metric_history validates the frozen cgroup frames
            # against the generic PostgreSQL sampler catalog.
            self._metric_catalog = CpuBudgetMetricCatalog()
            history_spec = case.frozen_history
            max_points = max(
                300,
                (
                    max(history_spec.normal_capture_seconds, history_spec.fault_capture_seconds)
                    + self.sample_interval_sec - 1
                ) // self.sample_interval_sec + 60,
            )
            self._metric_service = MetricService(
                catalog=self._metric_catalog,
                live=LivePostgresSamplerMetricProvider(
                    sample_interval_sec=self.sample_interval_sec,
                    max_points=max_points,
                    catalog=self._metric_catalog,
                ),
            )
        super().configure_case(case)

    def _ensure_baseline(self) -> None:
        """Do not warm synthetic generic metric history for this real cgroup scenario."""
        print(
            "[Env:CpuBudgetPGEnv] Skipping generic PG metric baseline; "
            "resource history is collected from real cgroup/proc/workload state."
        )

    def _start_sampler(self) -> None:
        """Keep generic PG sampler out of the evidence path for this scenario."""
        print(
            "[Env:CpuBudgetPGEnv] Generic PG sampler disabled; "
            "query_metrics(resource_history) owns observability."
        )

    def configure_history_observability(self, spec) -> None:
        """Keep frozen-history setup on the controller-owned cgroup history."""
        if getattr(self._case, "frozen_history", None) is None:
            return super().configure_history_observability(spec)
        controller = getattr(self, "_cpu_budget_controller", None)
        if controller is None or not controller._prepared:
            raise RuntimeError(
                "CPU budget history configuration requires a prepared cgroup controller"
            )
        print(
            "[Env:CpuBudgetPGEnv] Using prepared cgroup history controller; "
            "generic PostgreSQL sampler is not part of this Case."
        )

    def deploy(self):
        super().deploy()
        if getattr(self._case, "frozen_history", None) is not None:
            run_id = f"history-{getattr(self.deployment, 'container_name', 'pg')}"
            controller = getattr(self, "_cpu_budget_controller", None)
            if controller is None:
                controller = CpuBudgetController(self, self._case, run_id)
            try:
                controller.prepare_history()
            except Exception:
                # Frozen-history setup runs before an injector reaches RUNNING,
                # so its normal teardown hook cannot own partial sibling state.
                controller.recover()
                raise

    def capture_metric_history(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
        *,
        metric_targets: Mapping[str, tuple[str | None, ...]] | None = None,
        rate_windows: Mapping[str, int] | None = None,
    ) -> tuple[MetricFrame, ...]:
        if set(metrics) <= CPU_BUDGET_METRICS:
            controller = getattr(self, "_cpu_budget_controller", None)
            if controller is None:
                raise RuntimeError("CPU budget metric history requires an active controller")
            return controller.capture_metric_history(
                metrics,
                start_epoch_ms,
                end_epoch_ms,
                step_seconds,
                metric_targets=metric_targets,
                rate_windows=rate_windows,
            )
        return super().capture_metric_history(
            metrics,
            start_epoch_ms,
            end_epoch_ms,
            step_seconds,
            metric_targets=metric_targets,
            rate_windows=rate_windows,
        )

    def bind_metric_history(self, timeline) -> None:
        return super().bind_metric_history(timeline)

    def capture_history_records(
        self,
        sources: tuple[HistoricalRecordSource, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
    ) -> CapturedRecords:
        # Frozen-history CPU budget Cases own their record surface (operation
        # events + controller-captured TOPSQL competitors) and keep the generic
        # physical sampler out of the evidence path, so route the whole query
        # to the active controller instead of the shared physical dispatch.
        if getattr(getattr(self, "_case", None), "frozen_history", None) is not None:
            controller = getattr(self, "_cpu_budget_controller", None)
            if controller is None:
                raise RuntimeError("CPU budget record history requires an active controller")
            return controller.capture_history_records(sources, start_epoch_ms, end_epoch_ms)
        return super().capture_history_records(sources, start_epoch_ms, end_epoch_ms)

    def attach_cpu_budget_controller(self, controller: "CpuBudgetController") -> None:
        self._cpu_budget_controller = controller
        self.attach_scenario_metric_provider(controller)

    def detach_cpu_budget_controller(self) -> None:
        self._cpu_budget_controller = None
        self.detach_scenario_metric_provider()

    def teardown(self):
        # Frozen-history capture can fail before the injector reaches RUNNING;
        # own the controller cleanup at the environment boundary as well.
        controller = getattr(self, "_cpu_budget_controller", None)
        if controller is not None:
            try:
                controller.recover()
            finally:
                self._cpu_budget_controller = None
        return super().teardown()

    def configure_workload_session(self, connection, profile):
        """Keep scenario workload SQL out of the diagnostic TopSQL shortcut."""
        super().configure_workload_session(connection, profile)
        with connection.cursor() as cur:
            cur.execute("SET LOCAL pg_stat_statements.track = 'none';")

    @Tool(
        alias="query_metrics",
        tool_id="query_metrics",
        description=lazy_agent_text(
            zh=(
                "查询正式 CPU budget 历史观测。使用 host_cpu、host_cpu_pressure、"
                "cgroup_cpu_usage、cgroup_cpu_throttle、process_cpu、service_slo 和 job_progress "
                "分别观察 host、PostgreSQL/sibling cgroup、进程族、业务 SLO 和后台进度；"
                "返回原始字段与 run-local series target，不提供 shortage 或 recommended policy 结论。"
                "workload_activity 只用于确认后台 workload 仍在运行，不返回延迟排名。"
                "连接状态、数据库/表/WAL/temp 细节、慢 SQL、TopSQL 和 dead tuples "
                "请使用 execute_sql 自行查询、筛选和解释。"
            ),
            en=(
                "Query the formal CPU budget history observations. Use host_cpu, host_cpu_pressure, "
                "cgroup_cpu_usage, cgroup_cpu_throttle, process_cpu, service_slo and job_progress "
                "to observe the host, the PostgreSQL/sibling cgroups, process families, business SLO and background progress respectively; "
                "returns raw fields and run-local series targets, and provides no shortage or recommended policy conclusions. "
                "workload_activity only confirms that the background workload is still running and returns no latency ranking. "
                "For connection states, database/table/WAL/temp details, slow SQL, TopSQL and dead tuples, "
                "query, filter and interpret them yourself with execute_sql."
            ),
        ),
        arg_descriptions={
            "metric_type": lazy_agent_text(
                zh="指标类型，可用 host_cpu、host_cpu_pressure、cgroup_cpu_usage、cgroup_cpu_throttle、process_cpu、service_slo、job_progress 或 workload_activity",
                en="Metric type: host_cpu, host_cpu_pressure, cgroup_cpu_usage, cgroup_cpu_throttle, process_cpu, service_slo, job_progress or workload_activity",
            ),
            "target": lazy_agent_text(
                zh="可选的 run-local series target 过滤；省略时返回该 metric 的全部实体",
                en="Optional run-local series target filter; when omitted, all entities of the metric are returned",
            ),
            "limit": lazy_agent_text(
                zh="未指定时间窗时每个 series 返回的最新点数；显式历史窗口保持完整",
                en="Number of latest points returned per series when no time window is given; an explicit history window is returned in full",
            ),
            "start_timestamp": lazy_agent_text(zh="时间窗开始，可选", en="Time window start, optional"),
            "end_timestamp": lazy_agent_text(zh="时间窗结束，可选", en="Time window end, optional"),
        },
    )
    def _query_metrics_for_agent(
        self,
        metric_type: str,
        target: str = None,
        limit: int = None,
        start_timestamp: str = None,
        end_timestamp: str = None,
        step_seconds: int = None,
    ) -> str:
        # Native tool callers occasionally serialize numeric arguments as strings.
        # Normalize them here so a malformed workload_activity slice cannot look
        # like a missing observation during diagnosis.
        if isinstance(limit, str):
            try:
                limit = int(limit)
            except ValueError:
                return json.dumps({
                    "status": "error",
                    "error": f"limit must be an integer, got {limit!r}",
                }, ensure_ascii=False)
        if isinstance(step_seconds, str):
            try:
                step_seconds = int(step_seconds)
            except ValueError:
                return json.dumps({
                    "status": "error",
                    "error": f"step_seconds must be an integer, got {step_seconds!r}",
                }, ensure_ascii=False)
        if (
            str(metric_type).casefold()
            in {"resource_history", "cpu_budget", "cgroup_cpu", "resource_governance_cpu"}
            and getattr(getattr(self, "_case", None), "frozen_history", None) is not None
        ):
            return self.query_metrics(
                metric_type=metric_type,
                target=target,
                limit=limit,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                step_seconds=step_seconds,
            )
        if str(metric_type).casefold() == "workload_activity":
            # Keep this endpoint useful for checking that work is alive, but do
            # not expose a point-in-time latency ranking as a root-cause hint.
            # The case is intentionally solved from the cross-entity history.
            try:
                runner = getattr(self, "_workload_runner", None)
                if runner is None:
                    return json.dumps({
                        "status": "error",
                        "metric": "workload_activity",
                        "error": "workload runner not attached",
                    }, ensure_ascii=False)
                activity = runner.get_activity(limit=limit or 20)
                controller = getattr(self, "_cpu_budget_controller", None)
                profile_names = (
                    [profile.name for profile in controller.case.background_workload.profiles]
                    if controller is not None else []
                )
                profile_aliases = getattr(controller, "agent_profile_aliases", None) or {
                    name: f"workload_{index}"
                    for index, name in enumerate(profile_names, start=1)
                }
                payload = {
                    "status": "success",
                    "metric": "workload_activity",
                    "kind": "snapshot",
                    "snapshot": {
                        "total_runs": activity.get("total_runs", 0),
                        "active_profiles": activity.get("active_profiles", 0),
                        "worker_count": activity.get("worker_count", 0),
                        "profiles": [
                            {
                                key: (
                                    profile_aliases.get(item[key], item[key])
                                    if key == "fingerprint" else item[key]
                                )
                                for key in ("fingerprint", "calls", "ok_calls", "fail_calls", "last_ok")
                                if key in item
                            }
                            for item in activity.get("value", ())
                            if isinstance(item, dict)
                        ],
                    },
                }
                snapshot = payload.get("snapshot", {})
                profiles = snapshot.get("profiles", [])
                snapshot["profiles"].sort(key=lambda item: str(item.get("fingerprint", "")))
                return json.dumps(payload, ensure_ascii=False, default=str)
            except (TypeError, ValueError, AttributeError):
                return json.dumps({
                    "status": "error",
                    "metric": "workload_activity",
                    "error": "workload activity observation failed",
                }, ensure_ascii=False)
        if str(metric_type).casefold() in {"resource_history", "cpu_budget", "cgroup_cpu", "resource_governance_cpu"}:
            # The shared agent wrapper gates frozen-history Cases to their formal
            # required metrics before the Case can explain its own contract.
            # Route the legacy CPU budget aliases to this Case's query_metrics
            # so the rejection carries the case-owned guidance instead of the
            # generic unknown-metric error.
            return self.query_metrics(
                metric_type=metric_type,
                target=target,
                limit=limit,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                step_seconds=step_seconds,
            )
        result = super()._query_metrics_for_agent(
            metric_type=metric_type,
            target=target,
            limit=limit,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            step_seconds=step_seconds,
        )
        return result

    def query_metrics(
        self,
        metric_type: str,
        target: str = None,
        threshold_ms: int = None,
        tables: str = None,
        limit: int = None,
        start_timestamp: str = None,
        end_timestamp: str = None,
        step_seconds: int = None,
    ) -> str:
        controller = getattr(self, "_cpu_budget_controller", None)
        metric_lower = str(metric_type).casefold()
        if metric_lower in CPU_BUDGET_METRICS:
            timeline = getattr(self, "_history_timeline", None)
            if timeline is None:
                return json.dumps({
                    "status": "error",
                    "metric": metric_lower,
                    "error": "CPU budget historical observations are not bound",
                }, ensure_ascii=False)
            try:
                explicit_window = start_timestamp is not None or end_timestamp is not None
                start_ms = parse_utc_timestamp(start_timestamp, "start_timestamp") if explicit_window else timeline.visible_start_ms
                end_ms = parse_utc_timestamp(end_timestamp, "end_timestamp") if explicit_window else timeline.visible_end_ms
                if (start_timestamp is None) != (end_timestamp is None):
                    raise ValueError("start_timestamp and end_timestamp must be provided together")
                requested_step = step_seconds or (
                    timeline.base_step_seconds if explicit_window else timeline.overview_step_seconds
                )
                frame = timeline.metric_provider.query(MetricQuery(
                    metric=metric_lower,
                    target=None,
                    start_epoch_ms=start_ms,
                    end_epoch_ms=end_ms,
                    step_seconds=requested_step,
                ))
                if target is not None:
                    if target not in frame.series:
                        raise ValueError(
                            f"Unknown {metric_lower} series target: target={target!r}, "
                            f"available={sorted(frame.series)!r}"
                        )
                    frame = MetricFrame(
                        metric=frame.metric,
                        query_target=frame.query_target,
                        step_seconds=frame.step_seconds,
                        series={target: frame.series[target]},
                        timestamps_ms={target: frame.timestamps_ms[target]},
                    )
                rendered = json.loads(render_metric_frame(
                    frame,
                    available_start_ms=timeline.visible_start_ms,
                    available_end_ms=timeline.visible_end_ms,
                    requested_start_ms=start_ms,
                    requested_end_ms=end_ms,
                    step_seconds=frame.step_seconds,
                    # Match the shared PostgreSQL frozen-history contract:
                    # callers may bound a no-window overview to the newest N
                    # points, while explicit evidence windows remain complete.
                    max_points=limit if not explicit_window else None,
                ))
                contract = controller.agent_contract() if controller is not None else {}
                rendered["entity_scope"] = contract.get("entity_scope", {})
                rendered["public_constraints"] = contract.get("public_constraints", {})
                return json.dumps(rendered, ensure_ascii=False, separators=(",", ":"))
            except (ValueError, RuntimeError, TypeError, KeyError) as exc:
                return json.dumps({"status": "error", "metric": metric_lower, "error": str(exc)}, ensure_ascii=False)
        if str(metric_type).casefold() in {"resource_history", "cpu_budget", "cgroup_cpu", "resource_governance_cpu"}:
            if getattr(getattr(self, "_case", None), "frozen_history", None) is not None:
                return json.dumps({
                    "status": "error",
                    "metric": metric_lower,
                    "error": "CPU budget history must use the declared metric types; resource_history is not available for this task",
                }, ensure_ascii=False)
            if controller is None:
                return json.dumps({"status": "error", "error": "CPU budget controller is not active"})
            return json.dumps(controller.metric_payload(), ensure_ascii=False, default=str)
        return super().query_metrics(
            metric_type=metric_type,
            target=target,
            threshold_ms=threshold_ms,
            tables=tables,
            limit=limit,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            step_seconds=step_seconds,
        )

    @Tool(
        description=lazy_agent_text(
            zh=(
                "有界调整指标结果中标记为 managed=true 的共享实体资源策略；"
                "支持 set_resource_limit、set_scheduling_weight、set_peer_limit、set_peer_weight。"
                "不支持无限资源、停止必要工作、主机级调度或 SQL tenant 隔离。"
            ),
            en=(
                "Make bounded adjustments to the resource policies of shared entities marked managed=true in the metric results; "
                "supports set_resource_limit, set_scheduling_weight, set_peer_limit, set_peer_weight. "
                "Unlimited resources, stopping necessary work, host-level scheduling and SQL tenant isolation are not supported."
            ),
        ),
        arg_descriptions={
            "action": lazy_agent_text(
                zh=(
                    "set_resource_limit、set_scheduling_weight、set_peer_limit、set_peer_weight；"
                    "其他普通 PG action 仍可用"
                ),
                en=(
                    "set_resource_limit, set_scheduling_weight, set_peer_limit, set_peer_weight; "
                    "the other ordinary PG actions remain available"
                ),
            ),
            "target": lazy_agent_text(
                zh="使用指标结果返回的 entity_id 或兼容的已知目标名；只能调整 managed=true 实体",
                en="Use an entity_id returned in the metric results or a compatible known target name; only managed=true entities can be adjusted",
            ),
            "value": lazy_agent_text(
                zh="资源上限使用 cores 浮点数，调度权重使用 1-10000 整数",
                en="Resource limits use a floating-point number of cores; scheduling weights use an integer from 1 to 10000",
            ),
        },
    )
    def manage_instance(self, action: str, target: str = None, value: str = None) -> str:
        controller = getattr(self, "_cpu_budget_controller", None)
        if action in {
            "set_resource_limit",
            "set_scheduling_weight",
            "set_peer_limit",
            "set_peer_weight",
            "set_cpu_quota",
            "set_cpu_weight",
            "set_sibling_quota",
            "set_sibling_weight",
            "stop_sibling",
            "pause_sibling",
            "set_host_scheduler",
        }:
            if controller is None:
                return json.dumps({"status": "error", "error": "CPU budget controller is not active"})
            return json.dumps(
                controller.apply_action(action, target, value),
                ensure_ascii=False,
                default=str,
            )
        return super().manage_instance(action=action, target=target, value=value)


class CpuBudgetController:
    """Owns all run-scoped containers and samples their real cgroup state."""

    SAMPLE_INTERVAL_SECONDS = 0.5
    HISTORY_SIZE = 1200
    JOB_HEARTBEAT_BATCH = 2000
    BUSINESS_ACTIVITY_BUCKET = 2
    JOB_ACTIVITY_BUCKET = 20_000
    RESOURCE_ACTIVITY_BUCKET_USEC = 100_000

    def __init__(self, env: CpuBudgetPGEnv, case: PgResourceGovernanceContainerCpuBudgetCase, run_id: str):
        self.env = env
        self.case = case
        self.run_id = run_id
        token = _safe_name(run_id)[-28:] or "run"
        prefix = f"shared-workload-{token}"
        self.network_name = f"{prefix}-network"
        self.volume_name = f"{prefix}-volume"
        run_digest = hashlib.sha256(str(run_id).encode("utf-8")).digest()
        self.network_subnet = f"10.253.{run_digest[0]}.0/24"
        self.db_container = env.deployment.container_name
        self.job_containers = {
            job.job_id: f"{prefix}-{job.job_id}" for job in case.sibling_jobs
        }
        self.external_neighbor_jobs = case.external_neighbor_jobs
        self.external_neighbor_containers = {
            job.job_id: f"{prefix}-{job.job_id}" for job in self.external_neighbor_jobs
        }
        self.external_neighbor_job_id = case.external_neighbor_job_id
        self.external_neighbor_container = self.external_neighbor_containers[self.external_neighbor_job_id]
        canonical_entities = ["database", *self.job_containers, *self.external_neighbor_containers]
        if case.frozen_history is not None:
            # Keep frozen-history Cases' public aliases stable: owned siblings,
            # protected neighbors, then database. Roles remain public in every
            # metric response, so this is an identity convention for run-local
            # decoy targeting, not a diagnosis shortcut.
            ordered_entities = [
                *self.job_containers,
                *self.external_neighbor_containers,
                "database",
            ]
        else:
            ordered_entities = sorted(
                canonical_entities,
                key=lambda entity: run_digest[canonical_entities.index(entity) % len(run_digest)],
            )
        self.agent_entity_aliases = {
            entity: f"entity_{index}"
            for index, entity in enumerate(ordered_entities, start=1)
        }
        self.agent_entity_aliases_reverse = {
            alias: entity for entity, alias in self.agent_entity_aliases.items()
        }
        profile_names = [profile.name for profile in case.background_workload.profiles]
        self.agent_profile_aliases = {
            profile: "workload_" + hashlib.sha256(
                f"{run_id}::business-profile::{profile}".encode("utf-8")
            ).hexdigest()[:10]
            for profile in profile_names
        }
        self.agent_target_aliases = {
            self.agent_entity_aliases["database"]: self.db_container,
            **{
                self.agent_entity_aliases[job_id]: container
                for job_id, container in self.job_containers.items()
            },
        }
        self.agent_external_aliases = {
            self.agent_entity_aliases[job_id]: container
            for job_id, container in self.external_neighbor_containers.items()
        }
        self._history: deque[dict] = deque(maxlen=self.HISTORY_SIZE)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()
        self._remediation_baseline: dict[str, int] = {}
        self._started = False
        self._prepared = False
        self._operation_events: list[dict[str, object]] = []
        self._db_policy_weight = case.initial_db_weight
        self._cgroup_paths: dict[str, Path] = {}
        self._normal_policy_stop = threading.Event()
        self._normal_policy_thread: threading.Thread | None = None
        self._normal_policy_maintenance_complete = False
        self._normal_policy_maintenance_error: str | None = None
        self._target_policy_stop = threading.Event()
        self._target_policy_thread: threading.Thread | None = None
        self._target_sql_records: list[HistoricalIntervalRecord] = []
        self._policy_windows_stop = threading.Event()
        self._policy_windows_thread: threading.Thread | None = None
        self._policy_windows_complete = False
        self._policy_windows_error: str | None = None

    def agent_contract(self) -> dict[str, object]:
        metrics = {
            metric: {
                "fields": list(_CPU_BUDGET_DEFINITIONS[metric].value_fields),
                "unit": {
                    "host_cpu": "percent/cores",
                    "host_cpu_pressure": "PSI percent",
                    "cgroup_cpu_usage": "cores/count",
                    "cgroup_cpu_throttle": "count/microseconds/PSI percent",
                    "process_cpu": "percent/count",
                    "service_slo": "per-second/milliseconds/ratio",
                    "job_progress": "units/units-per-second/seconds",
                }[metric],
            }
            for metric in sorted(CPU_BUDGET_METRICS)
        }
        neutral_hard_scope = self.case.case_id == "db_quota_throttle"
        entity_scope = {
            self.agent_entity_aliases["database"]: {
                "role": "managed_workload" if neutral_hard_scope else "database",
                "managed": True,
                "actionable": True,
                "budget_scope": "managed",
                "minimum_quota_cores": None,
                "reserved_quota_cores": None,
                "deadline_seconds": None,
            }
        }
        managed_entities = [self.agent_entity_aliases["database"]]
        for job in self.case.sibling_jobs:
            alias = self.agent_entity_aliases[job.job_id]
            entity_scope[alias] = {
                "role": "managed_workload" if neutral_hard_scope else job.kind,
                "managed": bool(job.managed),
                "actionable": bool(job.managed),
                "budget_scope": "managed" if job.managed else "protected",
                "minimum_quota_cores": None if neutral_hard_scope else job.minimum_quota_cores,
                "reserved_quota_cores": None,
                "deadline_seconds": None if neutral_hard_scope else job.deadline_seconds,
            }
            if job.managed:
                managed_entities.append(alias)
        protected_entities = []
        for external_job in self.case.external_neighbor_jobs:
            alias = self.agent_entity_aliases[external_job.job_id]
            entity_scope[alias] = {
                "role": "protected_neighbor" if neutral_hard_scope else external_job.role,
                "managed": False,
                "actionable": False,
                "budget_scope": "excluded_neighbor",
                "minimum_quota_cores": external_job.minimum_quota_cores,
                "reserved_quota_cores": external_job.reserved_quota_cores,
                "deadline_seconds": external_job.deadline_seconds,
            }
            protected_entities.append(alias)
        public_constraints = {
            "host_cpu_budget_cores": self.case.host_cpu_budget_cores,
            "minimum_host_headroom_percent": self.case.min_host_headroom_percent,
            "required_job_deadline_seconds": max(job.deadline_seconds for job in self.case.sibling_jobs),
            "managed_budget_scope": managed_entities,
            "excluded_neighbor_scope": protected_entities,
            **({
                "minimum_managed_sibling_quota_cores": min(
                    job.minimum_quota_cores for job in self.case.sibling_jobs if job.managed
                ),
            } if not neutral_hard_scope else {}),
            "outcome_thresholds": {
                "host_psi_some_avg10_max": self.case.max_post_fix_host_psi_avg10,
                "db_psi_some_avg10_max": self.case.max_post_fix_db_psi_avg10,
                "post_fix_throttled_usec_max": self.case.max_post_fix_throttled_usec,
                "oltp_p99_ms_max": self.case.max_oltp_p99_ms,
                "oltp_success_ratio_min": self.case.min_oltp_success_rate,
                "report_qps_min": self.case.min_report_qps,
            },
            "validation_window_seconds": self.case.validation_window_seconds,
            "replay_sampling": {
                "sample_interval_seconds": self.SAMPLE_INTERVAL_SECONDS,
                "summary_semantics": (
                    "trusted replay samples continuously across the published validation window; every sample must satisfy the public invariants and the returned summary carries the final sample plus the failing-sample rollup"
                    if neutral_hard_scope else
                    "trusted replay returns the final live sample at the end of the published validation window"
                ),
            },
        }
        if not neutral_hard_scope:
            # The hard Case keeps the recovery band and per-entity quota
            # bounds private: the Agent must derive both the faulted entity
            # and the safe amplitude from demand evidence, not read them as a
            # published answer. Minimum managed quota stays public so the
            # budget arithmetic remains checkable, and safety enforcement
            # (action rejection + final-state verifier) is unchanged.
            public_constraints["recovery_db_quota_upper_bound_cores"] = self.case.recovery_db_quota_cores
            public_constraints["recovery_db_quota_lower_exclusive_cores"] = self.case.fault_db_quota_cores
            public_constraints["recovery_db_quota_upper_bound_cores"] = self.case.recovery_db_quota_cores
            public_constraints["recovery_db_quota_lower_exclusive_cores"] = self.case.fault_db_quota_cores
        return {
            "case_id": self.case.case_id,
            "frozen_history": True,
            "metrics": metrics,
            "entity_scope": entity_scope,
            "records": {
                "operation_event": {
                    "filters": ["event_type", "entity", "contains"],
                    "event_types": ["quota_revision"],
                },
                **({
                    "statement_summary": {
                        "query_surface": "execute_sql(target='history')",
                        "time_columns": ["event_start_utc", "event_end_utc"],
                    },
                } if neutral_hard_scope else {}),
            },
            "target_semantics": "series target aliases are stable for this run and must be correlated across metrics",
            "public_constraints": public_constraints,
        }

    def _record_operation_event(
        self,
        *,
        event_type: str,
        entity: str,
        old_quota: float | None,
        new_quota: float | None,
        old_weight: int | None,
        new_weight: int | None,
        actor: str,
        message: str = "bounded CPU policy revision applied",
        policy_old_weight: int | None = None,
        policy_new_weight: int | None = None,
    ) -> None:
        self._operation_events.append({
            "timestamp_ms": int(time.time() * 1000),
            "event_type": event_type,
            "entity": self.agent_entity_aliases.get(entity, entity),
            "old_weight": old_weight,
            "new_weight": new_weight,
            "policy_old_weight": policy_old_weight,
            "policy_new_weight": policy_new_weight,
            # Keep exact policy values for local audit/debugging, while the
            # public operation_event contract makes the Agent correlate the
            # revision with raw quota and throttle metrics itself.  Actor and
            # message stay private so maintenance cannot be filtered as a
            # disguised fault label.
            "_audit_actor": actor,
            "_audit_message": message,
            "_audit_old_quota_cores": old_quota,
            "_audit_new_quota_cores": new_quota,
        })

    def _normal_policy_maintenance(self) -> None:
        """Capture a real, harmless policy revision near the normal-window tail."""
        if self._normal_policy_stop.wait(150.0):
            self._normal_policy_maintenance_error = "maintenance cancelled before the normal capture tail"
            return
        changed = False
        changed_sibling = False
        sibling_job = None
        sibling_container = None
        sibling_quota = None
        try:
            before = self._read_cgroup(self.db_container)
            # Keep the normal scheduler revision real for the Simple case as
            # well: its published healthy DB quota is below the Hard case's
            # historical 1.8-core maintenance level.
            maintenance_quota = max(0.1, min(1.8, self.case.initial_db_quota_cores - 0.1))
            if before.get("cpu_max_cores") is None or float(before["cpu_max_cores"]) < maintenance_quota:
                self._normal_policy_maintenance_error = "baseline DB quota was unavailable for maintenance"
                return
            updated = self._update_container(self.db_container, quota=maintenance_quota)
            self._record_operation_event(
                event_type="quota_revision",
                entity="database",
                old_quota=float(before["cpu_max_cores"]),
                new_quota=float(updated.get("cpu_max_cores") or maintenance_quota),
                old_weight=int(before.get("cpu.weight") or 0),
                new_weight=int(updated.get("cpu.weight") or 0),
                actor="scheduler",
                message="routine bounded CPU policy maintenance started",
            )
            changed = True
            # Keep a real, bounded sibling reconciliation in the normal
            # capture. It stays above the published minimum and is restored
            # before target capture, so it is a benign policy/throttle
            # candidate rather than a second fault.
            if self.case.case_id == "db_quota_throttle_simple" and self.case.sibling_jobs:
                sibling_job = self.case.sibling_jobs[0]
                sibling_container = self.job_containers[sibling_job.job_id]
                sibling_before = self._read_cgroup(sibling_container)
                sibling_quota = max(
                    sibling_job.minimum_quota_cores,
                    sibling_job.initial_quota_cores - 0.10,
                )
                sibling_updated = self._update_container(
                    sibling_container,
                    quota=sibling_quota,
                )
                self._record_operation_event(
                    event_type="quota_revision",
                    entity=sibling_job.job_id,
                    old_quota=float(sibling_before.get("cpu_max_cores") or sibling_job.initial_quota_cores),
                    new_quota=float(sibling_updated.get("cpu_max_cores") or sibling_quota),
                    old_weight=int(sibling_before.get("cpu.weight") or 0),
                    new_weight=int(sibling_updated.get("cpu.weight") or 0),
                    actor="scheduler",
                    message="routine required-job quota reconciliation started",
                )
                changed_sibling = True
            self._normal_policy_stop.wait(2.0)
        except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as exc:
            self._normal_policy_maintenance_error = f"maintenance failed: {exc}"
            return
        finally:
            if changed_sibling and sibling_container is not None and sibling_job is not None:
                try:
                    sibling_restored = self._update_container(
                        sibling_container,
                        quota=sibling_job.initial_quota_cores,
                    )
                    self._record_operation_event(
                        event_type="quota_revision",
                        entity=sibling_job.job_id,
                        old_quota=float(sibling_quota or sibling_job.initial_quota_cores),
                        new_quota=float(sibling_restored.get("cpu_max_cores") or sibling_job.initial_quota_cores),
                        old_weight=int(sibling_restored.get("cpu.weight") or 0),
                        new_weight=int(sibling_restored.get("cpu.weight") or sibling_job.initial_weight),
                        actor="scheduler",
                        message="routine required-job quota reconciliation completed",
                    )
                except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as exc:
                    self._normal_policy_maintenance_error = f"sibling maintenance restore failed: {exc}"
            if changed:
                try:
                    restored = self._update_container(
                        self.db_container,
                        quota=self.case.initial_db_quota_cores,
                    )
                    self._record_operation_event(
                        event_type="quota_revision",
                        entity="database",
                        old_quota=maintenance_quota,
                        new_quota=float(restored.get("cpu_max_cores") or self.case.initial_db_quota_cores),
                        old_weight=int(restored.get("cpu.weight") or 0),
                        new_weight=int(restored.get("cpu.weight") or 0),
                        actor="scheduler",
                        message="routine bounded CPU policy maintenance completed",
                    )
                    self._normal_policy_maintenance_complete = True
                except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as exc:
                    self._normal_policy_maintenance_error = f"maintenance restore failed: {exc}"

    def _start_normal_policy_maintenance(self) -> None:
        if self._normal_policy_thread is not None and self._normal_policy_thread.is_alive():
            return
        self._normal_policy_stop.clear()
        self._normal_policy_maintenance_complete = False
        self._normal_policy_maintenance_error = None
        self._normal_policy_thread = threading.Thread(
            target=self._normal_policy_maintenance,
            name=f"cpu-budget-normal-policy-{self.case.case_id}",
            daemon=True,
        )
        self._normal_policy_thread.start()

    def _stop_normal_policy_maintenance(self) -> None:
        self._normal_policy_stop.set()
        if self._normal_policy_thread is not None and self._normal_policy_thread.is_alive():
            self._normal_policy_thread.join(timeout=40)
        if self._normal_policy_thread is not None and self._normal_policy_thread.is_alive():
            raise RuntimeError("normal policy maintenance did not stop before fault installation")
        self._normal_policy_thread = None

    def _target_policy_maintenance(self) -> None:
        """Reconcile declared workload policy while the incident is active."""
        if self.case.case_id != "db_quota_throttle_simple":
            for delay_seconds in (8.0, 18.0, 18.0):
                if self._target_policy_stop.wait(delay_seconds):
                    return
                self._target_policy_maintenance_cycle()
            return

        # A stale workload-class binding is the upstream fault. As in a real
        # declarative controller, direct execution-state quota edits are
        # overwritten until the binding (represented by cpu.weight) is fixed.
        while not self._target_policy_stop.wait(2.0):
            try:
                before = self._read_cgroup(self.db_container)
                weight = int(before.get("cpu.weight") or 0)
                quota = float(before.get("cpu_max_cores") or 0.0)
                with self._lock:
                    policy_weight = self._db_policy_weight
                if policy_weight >= self.case.initial_db_weight:
                    continue
                if abs(quota - self.case.fault_db_quota_cores) > 1e-6:
                    updated = self._update_container(
                        self.db_container,
                        quota=self.case.fault_db_quota_cores,
                    )
                else:
                    updated = before
                self._record_operation_event(
                    event_type="quota_revision",
                    entity="database",
                    old_quota=quota,
                    new_quota=float(updated.get("cpu_max_cores") or self.case.fault_db_quota_cores),
                    old_weight=weight,
                    new_weight=int(updated.get("cpu.weight") or weight),
                    actor="policy_controller",
                    message="declared workload policy reconciled",
                    policy_old_weight=policy_weight,
                    policy_new_weight=policy_weight,
                )
            except (OSError, RuntimeError, subprocess.SubprocessError, TypeError, ValueError):
                continue

    def _target_policy_maintenance_cycle(self) -> None:
        """Apply one short weight-only reconciliation and restore it."""
        changed_db = False
        changed_sibling = False
        sibling_container = None
        sibling_job = None
        try:
            if self.case.case_id == "db_quota_throttle":
                self._capture_target_sql_competitor()
            before = self._read_cgroup(self.db_container)
            current_weight = int(before.get("cpu.weight") or 0)
            if current_weight <= 1:
                return
            # A scheduler reconciliation can be a minimal weight revision;
            # keep the event meaningful without creating a second pressure
            # pressure event beside the quota fault.
            maintenance_weight = max(1, current_weight - 1)
            updated = self._update_container(self.db_container, weight=maintenance_weight)
            changed_db = True
            self._record_operation_event(
                event_type="quota_revision",
                entity="database",
                old_quota=float(before.get("cpu_max_cores") or self.case.fault_db_quota_cores),
                new_quota=float(updated.get("cpu_max_cores") or self.case.fault_db_quota_cores),
                old_weight=current_weight,
                new_weight=int(updated.get("cpu.weight") or maintenance_weight),
                actor="scheduler",
                message="routine bounded CPU weight reconciliation started during quota policy window",
            )
            if self.case.sibling_jobs:
                sibling_job = self.case.sibling_jobs[0]
                sibling_container = self.job_containers[sibling_job.job_id]
                sibling_before = self._read_cgroup(sibling_container)
                sibling_weight = int(sibling_before.get("cpu.weight") or 0)
                if sibling_weight > 1:
                    sibling_maintenance_weight = max(1, sibling_weight - 1)
                    sibling_updated = self._update_container(
                        sibling_container,
                        weight=sibling_maintenance_weight,
                    )
                    changed_sibling = True
                    self._record_operation_event(
                        event_type="quota_revision",
                        entity=sibling_job.job_id,
                        old_quota=float(sibling_before.get("cpu_max_cores") or sibling_job.initial_quota_cores),
                        new_quota=float(sibling_updated.get("cpu_max_cores") or sibling_job.initial_quota_cores),
                        old_weight=sibling_weight,
                        new_weight=int(sibling_updated.get("cpu.weight") or sibling_maintenance_weight),
                        actor="scheduler",
                        message="routine required-job weight reconciliation started during quota policy window",
                    )
            # Keep the reconciliation observable in the target history while
            # limiting its effect on the live quota/throttle replay.
            self._target_policy_stop.wait(0.5)
        except (OSError, RuntimeError, subprocess.SubprocessError, ValueError):
            return
        finally:
            if changed_sibling and sibling_container is not None and sibling_job is not None:
                try:
                    sibling_restored = self._update_container(
                        sibling_container,
                        weight=sibling_job.initial_weight,
                    )
                    self._record_operation_event(
                        event_type="quota_revision",
                        entity=sibling_job.job_id,
                        old_quota=float(sibling_restored.get("cpu_max_cores") or sibling_job.initial_quota_cores),
                        new_quota=float(sibling_restored.get("cpu_max_cores") or sibling_job.initial_quota_cores),
                        old_weight=int(sibling_restored.get("cpu.weight") or 0),
                        new_weight=int(sibling_restored.get("cpu.weight") or sibling_job.initial_weight),
                        actor="scheduler",
                        message="routine required-job weight reconciliation completed",
                    )
                except (OSError, RuntimeError, subprocess.SubprocessError, ValueError):
                    pass
            if changed_db:
                try:
                    restored = self._update_container(
                        self.db_container,
                        weight=self.case.initial_db_weight,
                    )
                    self._record_operation_event(
                        event_type="quota_revision",
                        entity="database",
                        old_quota=float(restored.get("cpu_max_cores") or self.case.fault_db_quota_cores),
                        new_quota=float(restored.get("cpu_max_cores") or self.case.fault_db_quota_cores),
                        old_weight=int(restored.get("cpu.weight") or 0),
                        new_weight=int(restored.get("cpu.weight") or self.case.initial_db_weight),
                        actor="scheduler",
                        message="routine bounded CPU weight reconciliation completed",
                    )
                except (OSError, RuntimeError, subprocess.SubprocessError, ValueError):
                    pass

    def _start_target_policy_maintenance(self) -> None:
        if self._target_policy_thread is not None and self._target_policy_thread.is_alive():
            return
        self._target_policy_stop.clear()
        self._target_policy_thread = threading.Thread(
            target=self._target_policy_maintenance,
            name=f"cpu-budget-target-policy-{self.case.case_id}",
            daemon=True,
        )
        self._target_policy_thread.start()

    def _capture_target_sql_competitor(self) -> None:
        """Capture a real completed batch query as a target-window hypothesis."""
        statement = (
            "SELECT sum((g * 29) % 1000003), avg(length(md5(g::text))) "
            "FROM generate_series(1, 120000) AS g"
        )
        start_ms = int(time.time() * 1000)
        result = self.env.execute_sql(statement)
        end_ms = max(start_ms + 1, int(time.time() * 1000))
        payload = json.loads(result) if isinstance(result, str) else result
        if not isinstance(payload, dict) or payload.get("status") != "success":
            raise RuntimeError(f"target SQL competitor failed: {payload!r}")
        digest = hashlib.sha256(statement.encode("utf-8")).hexdigest()[:16]
        self._target_sql_records.append(HistoricalIntervalRecord(
            source=HistoricalRecordSource.TOPSQL,
            target="postgres",
            start_ms=start_ms,
            end_ms=end_ms,
            payload={
                "digest": digest,
                "sql_text": statement,
                "exec_count": 1,
                "sum_latency": float(end_ms - start_ms),
                "avg_latency": float(end_ms - start_ms),
                "rows": 1,
            },
        ))

    def _benign_policy_windows(self) -> None:
        """Hold real, fully restored benign policy windows inside the normal capture.

        The database window mirrors the fault quota so the assembled history
        contains a complete incident-shaped bundle that recovered on its own.
        The external-neighbor burst and required-sibling rebalance add
        same-domain quota and host-load competitors so no single quota step or
        entity fluctuation identifies the incident. Only the target regression
        persists to the present.
        """
        deadline = time.monotonic() + 600
        while not self._normal_policy_maintenance_complete and time.monotonic() < deadline:
            if self._policy_windows_stop.wait(1.0):
                return
        if not self._normal_policy_maintenance_complete:
            self._policy_windows_error = "benign policy windows missed the normal capture phase"
            return
        failures: list[str] = []
        # Phase 1: cost-saving window on the database at the fault quota.
        if self._policy_windows_stop.wait(30.0):
            return
        self._hold_benign_window(
            "database",
            self.db_container,
            quota=min(float(self.case.initial_db_quota_cores), float(self.case.fault_db_quota_cores)),
            restore_quota=float(self.case.initial_db_quota_cores),
            duration_seconds=110.0,
            start_message="planned cost-saving CPU window started",
            end_message="planned cost-saving CPU window completed",
            failures=failures,
        )
        # Phase 2: temporary external-neighbor expansion creates a real
        # host-busy window with a healthy database quota.
        if self._policy_windows_stop.wait(10.0):
            return
        external_job = self.external_neighbor_jobs[0]
        self._hold_benign_window(
            external_job.job_id,
            self.external_neighbor_containers[external_job.job_id],
            quota=float(external_job.reserved_quota_cores) + 0.30,
            restore_quota=float(external_job.reserved_quota_cores),
            duration_seconds=80.0,
            start_message="external neighbor burst window started",
            end_message="external neighbor burst window completed",
            failures=failures,
        )
        # Phase 3: required-sibling quota rebalance inside its published minimum.
        if self._policy_windows_stop.wait(5.0):
            return
        sibling_job = self.case.sibling_jobs[0]
        self._hold_benign_window(
            sibling_job.job_id,
            self.job_containers[sibling_job.job_id],
            quota=max(float(sibling_job.minimum_quota_cores), float(sibling_job.initial_quota_cores) - 0.20),
            restore_quota=float(sibling_job.initial_quota_cores),
            duration_seconds=80.0,
            start_message="required-job quota rebalance started",
            end_message="required-job quota rebalance completed",
            failures=failures,
        )
        if failures:
            self._policy_windows_error = "; ".join(failures)
        else:
            self._policy_windows_complete = True

    def _hold_benign_window(
        self,
        entity: str,
        container: str,
        *,
        quota: float,
        restore_quota: float,
        duration_seconds: float,
        start_message: str,
        end_message: str,
        failures: list[str],
    ) -> None:
        changed = False
        try:
            before = self._read_cgroup(container)
            updated = self._update_container(container, quota=quota)
            changed = True
            self._record_operation_event(
                event_type="quota_revision",
                entity=entity,
                old_quota=float(before.get("cpu_max_cores") or 0.0),
                new_quota=float(updated.get("cpu_max_cores") or quota),
                old_weight=int(before.get("cpu.weight") or 0),
                new_weight=int(updated.get("cpu.weight") or 0),
                actor="scheduler",
                message=start_message,
            )
            self._policy_windows_stop.wait(duration_seconds)
        except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as exc:
            failures.append(f"{start_message}: {exc}")
        finally:
            if changed:
                try:
                    restored = self._update_container(container, quota=restore_quota)
                    # One real sample must observe the restored value before
                    # this thread returns, so coarse grids never render the
                    # window as a run of single-tick dips.
                    self._sample_once()
                    self._record_operation_event(
                        event_type="quota_revision",
                        entity=entity,
                        old_quota=quota,
                        new_quota=float(restored.get("cpu_max_cores") or restore_quota),
                        old_weight=int(restored.get("cpu.weight") or 0),
                        new_weight=int(restored.get("cpu.weight") or 0),
                        actor="scheduler",
                        message=end_message,
                    )
                except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as exc:
                    failures.append(f"{end_message}: {exc}")

    def _start_policy_windows(self) -> None:
        if self.case.case_id not in {"db_quota_throttle", "db_quota_throttle_simple"}:
            return
        if self._policy_windows_thread is not None and self._policy_windows_thread.is_alive():
            return
        self._policy_windows_stop.clear()
        self._policy_windows_complete = False
        self._policy_windows_error = None
        self._policy_windows_thread = threading.Thread(
            target=self._benign_policy_windows,
            name=f"cpu-budget-policy-windows-{self.case.case_id}",
            daemon=True,
        )
        self._policy_windows_thread.start()

    def _stop_policy_windows(self, *, require_complete: bool) -> None:
        self._policy_windows_stop.set()
        if self._policy_windows_thread is not None and self._policy_windows_thread.is_alive():
            self._policy_windows_thread.join(timeout=120)
        if self._policy_windows_thread is not None and self._policy_windows_thread.is_alive():
            if require_complete:
                raise RuntimeError("benign policy windows did not stop before the fault installation")
        self._policy_windows_thread = None
        if require_complete:
            if self._policy_windows_error is not None:
                raise RuntimeError(f"benign policy windows prerequisite failed: {self._policy_windows_error}")
            if not self._policy_windows_complete:
                raise RuntimeError("benign policy windows did not complete inside the normal capture")

    def _stop_target_policy_maintenance(self) -> None:
        self._target_policy_stop.set()
        if self._target_policy_thread is not None and self._target_policy_thread.is_alive():
            self._target_policy_thread.join(timeout=15)
        if self._target_policy_thread is not None and self._target_policy_thread.is_alive():
            raise RuntimeError("target policy maintenance did not stop during recovery")
        self._target_policy_thread = None

    def _entity_for_container(self, container: str) -> str:
        if container == self.db_container:
            return "database"
        for entity, owned_container in self.job_containers.items():
            if container == owned_container:
                return entity
        return container

    def capture_history_records(
        self,
        sources: tuple[HistoricalRecordSource, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
    ) -> CapturedRecords:
        visible_events = [
            event for event in self._operation_events
            if HistoricalRecordSource.OPERATION_EVENT in sources
            and start_epoch_ms <= int(event["timestamp_ms"]) <= end_epoch_ms
        ]
        if HistoricalRecordSource.OPERATION_EVENT in sources and not visible_events and self._started:
            # Fault installation can land in the gap between normal and target
            # captures. Expose that boundary revision at target start while
            # retaining its real application time in the public payload.
            applied = max(
                (event for event in self._operation_events if int(event["timestamp_ms"]) <= start_epoch_ms),
                key=lambda event: int(event["timestamp_ms"]),
                default=None,
            )
            if applied is not None:
                visible_events = [{
                    **applied,
                    "timestamp_ms": start_epoch_ms,
                    "_audit_apply_time_ms": int(applied["timestamp_ms"]),
                    "actor": "history_capture",
                    "message": "bounded CPU policy revision observed at target-window start",
                }]
        # Policy weight is a raw control-plane field needed to distinguish the
        # stale workload-class binding from its low-quota symptom. Exact quota,
        # actor and message remain private so records do not become a diagnosis.
        public_fields = {
            "event_type", "entity", "old_weight", "new_weight",
            "policy_old_weight", "policy_new_weight",
        }
        records = tuple(
            HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="postgres",
                timestamp_ms=int(event["timestamp_ms"]),
                payload={
                    key: value
                    for key, value in event.items()
                    if key in public_fields and value is not None
                },
            )
            for event in visible_events
        )
        interval_records = tuple(
            record
            for record in self._target_sql_records
            if HistoricalRecordSource.TOPSQL in sources
            and start_epoch_ms <= record.start_ms
            and record.end_ms <= end_epoch_ms
        )
        if (
            HistoricalRecordSource.TOPSQL in sources
            and self.case.case_id == "db_quota_throttle"
            and self._started
            and not interval_records
        ):
            raise RuntimeError("target history has no completed SQL competitor record")
        return CapturedRecords(
            point_records=records,
            interval_records=interval_records,
            coverage=tuple(
                HistoricalCoverage(
                    source=source,
                    target="postgres",
                    start_ms=start_epoch_ms,
                    end_ms=end_epoch_ms,
                )
                for source in (HistoricalRecordSource.OPERATION_EVENT, HistoricalRecordSource.TOPSQL)
                if source in sources
            ),
        )

    def _run(self, args: list[str], *, check: bool = False, timeout: float = 20) -> subprocess.CompletedProcess:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        if check and result.returncode != 0:
            raise RuntimeError(
                f"command failed: {' '.join(args)}; stderr={result.stderr.strip()!r}"
            )
        return result

    def _run_idempotent_docker(self, args: list[str], *, timeout: float = 20, retries: int = 3) -> subprocess.CompletedProcess:
        last_error: subprocess.TimeoutExpired | None = None
        for attempt in range(retries):
            try:
                return self._run(args, check=True, timeout=timeout)
            except subprocess.TimeoutExpired as exc:
                last_error = exc
                if attempt + 1 < retries:
                    time.sleep(1.0)
        assert last_error is not None
        raise last_error

    def _validate_host_capability(self) -> None:
        controllers = Path("/sys/fs/cgroup/cgroup.controllers")
        if not controllers.is_file() or "cpu" not in controllers.read_text(encoding="utf-8"):
            raise RuntimeError(
                "BLOCKER: host does not expose cgroup v2 CPU controller; "
                "cannot distinguish DB quota throttle from host saturation without fabricating metrics"
            )
        try:
            available_cpus = len(os.sched_getaffinity(0))
        except AttributeError:
            available_cpus = os.cpu_count() or 0
        meminfo = Path("/proc/meminfo").read_text(encoding="utf-8")
        memory_kb = next(
            int(line.split()[1])
            for line in meminfo.splitlines()
            if line.startswith("MemTotal:")
        )
        required = self.case.runtime.resources
        if available_cpus < required.worker_physical_cores or memory_kb * 1024 < required.worker_memory_mb * 1024 * 1024:
            raise RuntimeError(
                "BLOCKER: deployment resources cannot separate host saturation, DB quota throttle, "
                f"and DB internal CPU; available_cpus={available_cpus}, memory_mb={memory_kb / 1024:.0f}, "
                f"required_cores={required.worker_physical_cores}, required_memory_mb={required.worker_memory_mb}"
            )
        root_cpu_max = Path("/sys/fs/cgroup/cpu.max")
        if root_cpu_max.is_file() and root_cpu_max.read_text(encoding="utf-8").strip().startswith("0 "):
            raise RuntimeError("BLOCKER: host cgroup has no usable CPU budget")

    def _cleanup_command(self, args: list[str], *, timeout: float = 60) -> None:
        try:
            self._run(args, timeout=timeout)
        except (OSError, subprocess.SubprocessError):
            # Cleanup is best effort; the next explicit run-scoped cleanup
            # command and the Docker daemon remain the source of truth.
            pass

    def _cleanup_runtime(self) -> None:
        self._stop_sampling()
        for container in self.external_neighbor_containers.values():
            self._cleanup_command(["docker", "rm", "-f", container])
        for container in self.job_containers.values():
            self._cleanup_command(["docker", "rm", "-f", container])
        # The orchestrator tears down the PostgreSQL container after the injector;
        # disconnect it before removing this run's network so cleanup is complete.
        self._cleanup_command(
            ["docker", "network", "disconnect", "-f", self.network_name, self.db_container],
        )
        self._cleanup_command(["docker", "network", "rm", self.network_name])
        self._cleanup_command(["docker", "volume", "rm", self.volume_name])

    def _run_job_container(self, command: list[str], container: str) -> None:
        """Handle Docker creating a run-scoped container before the client times out."""
        try:
            self._run(command, check=True, timeout=120)
            return
        except subprocess.TimeoutExpired as exc:
            state = None
            inspect_error: subprocess.TimeoutExpired | None = None
            for attempt in range(3):
                try:
                    state = self._run(
                        ["docker", "inspect", "--format", "{{.State.Status}}", container],
                        timeout=30,
                    )
                    break
                except subprocess.TimeoutExpired as status_error:
                    inspect_error = status_error
                    if attempt + 1 < 3:
                        time.sleep(1.0)
            if state is None:
                assert inspect_error is not None
                try:
                    self._run_idempotent_docker(["docker", "start", container], timeout=120)
                except (RuntimeError, subprocess.TimeoutExpired) as start_error:
                    raise RuntimeError(
                        f"could not inspect or start owned sibling container after docker timeout: "
                        f"container={container!r}"
                    ) from start_error
                return
            status = state.stdout.strip() if state.returncode == 0 else ""
            if status == "created":
                self._run_idempotent_docker(["docker", "start", container], timeout=120)
                return
            if status == "running":
                return
            raise RuntimeError(
                f"owned sibling container did not become runnable after docker timeout: "
                f"container={container!r}, status={status!r}"
            ) from exc

    def _create_runtime(self) -> None:
        image = self.case.sibling_image
        if self._run(["docker", "image", "inspect", image]).returncode != 0:
            raise RuntimeError(f"sibling fault image is unavailable: image={image!r}")
        self._run([
            "docker", "network", "create",
            "--subnet", self.network_subnet,
            "--label", f"aiopsbench.scenario={SCENARIO_ID}",
            "--label", f"aiopsbench.case={self.case.case_id}",
            self.network_name,
        ], check=True, timeout=120)
        self._run([
            "docker", "volume", "create",
            "--label", f"aiopsbench.scenario={SCENARIO_ID}",
            "--label", f"aiopsbench.case={self.case.case_id}",
            self.volume_name,
        ], check=True, timeout=120)
        connected = self._run(
            ["docker", "network", "connect", self.network_name, self.db_container],
            timeout=120,
        )
        if connected.returncode != 0 and "already exists" not in connected.stderr.casefold():
            raise RuntimeError(f"cannot connect PostgreSQL container to owned network: {connected.stderr.strip()}")
        for job in self.case.sibling_jobs:
            container = self.job_containers[job.job_id]
            burn_loops = max(1, int(job.cpu_burn_loops))
            script = (
                "i=0; "
                f"job_dir=/run/{job.job_id}; mkdir -p \"$job_dir\"; "
                "while :; do "
                f"n=$((i+{self.JOB_HEARTBEAT_BATCH})); while [ $i -lt $n ]; do "
                f"i=$((i+1)); j=0; while [ $j -lt {burn_loops} ]; do j=$((j+1)); done; done; "
                "printf '%s|%s|running\\n' \"$i\" \"$(date +%s)\" > \"$job_dir/job.state.tmp\"; "
                "mv -f \"$job_dir/job.state.tmp\" \"$job_dir/job.state\"; "
                "sleep 0.05; "
                "done"
            )
            self._run_job_container([
                "docker", "run", "-d",
                "--name", container,
                "--network", self.network_name,
                "--cpus", str(job.initial_quota_cores),
                "--cpu-shares", str(job.initial_weight),
                "-v", f"{self.volume_name}:/run:rw",
                image, "sh", "-c", script,
            ], container)
        for external_job in self.external_neighbor_jobs:
            neighbor_script = (
                "i=0; "
                f"job_dir=/run/{external_job.job_id}; mkdir -p \"$job_dir\"; "
                "while :; do "
                f"n=$((i+{self.JOB_HEARTBEAT_BATCH})); while [ $i -lt $n ]; do i=$((i+1)); done; "
                "printf '%s|%s|running\\n' \"$i\" \"$(date +%s)\" > \"$job_dir/job.state.tmp\"; "
                "mv -f \"$job_dir/job.state.tmp\" \"$job_dir/job.state\"; "
                "sleep 0.05; "
                "done"
            )
            container = self.external_neighbor_containers[external_job.job_id]
            self._run_job_container([
                "docker", "run", "-d",
                "--name", container,
                "--network", self.network_name,
                "--cpus", str(external_job.reserved_quota_cores),
                "--cpu-shares", str(external_job.weight),
                "-v", f"{self.volume_name}:/run:rw",
                image, "sh", "-c", neighbor_script,
            ], container)

    def _read_file(self, container: str, path: str) -> str:
        result = self._run(["docker", "exec", container, "cat", path])
        if result.returncode != 0:
            raise RuntimeError(
                f"cannot read cgroup evidence: container={container!r}, path={path!r}, "
                f"stderr={result.stderr.strip()!r}"
            )
        return result.stdout.strip()

    def _container_cgroup_path(self, container: str) -> Path:
        cached = self._cgroup_paths.get(container)
        if cached is not None:
            return cached
        inspected = self._run(["docker", "inspect", "--format", "{{.State.Pid}}", container])
        if inspected.returncode != 0:
            raise RuntimeError(
                f"cannot inspect cgroup owner: container={container!r}, stderr={inspected.stderr.strip()!r}"
            )
        try:
            pid = int(inspected.stdout.strip())
            cgroup_lines = Path(f"/proc/{pid}/cgroup").read_text(encoding="utf-8").splitlines()
            relative = next(line.split(":", 2)[2] for line in cgroup_lines if line.startswith("0::"))
        except (IndexError, OSError, StopIteration, ValueError) as exc:
            raise RuntimeError(
                f"cannot resolve cgroup v2 path: container={container!r}, pid={inspected.stdout.strip()!r}"
            ) from exc
        if not relative.startswith("/") or ".." in Path(relative).parts:
            raise RuntimeError(
                f"unexpected cgroup v2 path: container={container!r}, relative={relative!r}"
            )
        cgroup_path = Path("/sys/fs/cgroup") / relative.lstrip("/")
        if not (cgroup_path / "cpu.max").is_file():
            raise RuntimeError(
                f"cgroup v2 CPU files are unavailable: container={container!r}, path={str(cgroup_path)!r}"
            )
        self._cgroup_paths[container] = cgroup_path
        return cgroup_path

    def _read_process_cpu(self, container: str) -> tuple[dict, ...]:
        result = self._run([
            "docker", "exec", container, "sh", "-c",
            "ps -eo pid=,ppid=,pcpu=,comm=,args= --sort=-pcpu | head -n 12",
        ])
        if result.returncode != 0:
            return ()
        rows = []
        for line in result.stdout.splitlines():
            parts = line.strip().split(None, 4)
            if len(parts) != 5:
                continue
            try:
                command = parts[3]
                args = parts[4][:160]
                if command in {"ps", "head"} or "ps -eo" in args:
                    continue
                rows.append({
                    "pid": int(parts[0]),
                    "ppid": int(parts[1]),
                    "cpu_percent": float(parts[2]),
                    "command": command,
                    "args": args,
                })
            except ValueError:
                continue
        return tuple(rows)

    def _read_cgroup(self, container: str) -> dict:
        cgroup_path = self._container_cgroup_path(container)
        try:
            cpu_max = (cgroup_path / "cpu.max").read_text(encoding="utf-8").strip()
            cpu_stat_raw = (cgroup_path / "cpu.stat").read_text(encoding="utf-8").strip()
            pressure_raw = (cgroup_path / "cpu.pressure").read_text(encoding="utf-8").strip()
            weight = (cgroup_path / "cpu.weight").read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RuntimeError(
                f"cannot read host cgroup evidence: container={container!r}, path={str(cgroup_path)!r}"
            ) from exc
        return {
            "cpu.max": cpu_max,
            "cpu_max_cores": _parse_cpu_max(cpu_max),
            "cpu.weight": int(weight),
            "cpu.stat": _parse_cpu_stat(cpu_stat_raw),
            "cpu.pressure": _parse_psi(pressure_raw),
            "process_cpu": self._read_process_cpu(container),
        }

    @staticmethod
    def _read_host_cpu() -> tuple[dict[str, int], float]:
        line = next(
            line for line in Path("/proc/stat").read_text(encoding="utf-8").splitlines()
            if line.startswith("cpu ")
        )
        values = [int(value) for value in line.split()[1:]]
        keys = ("user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal")
        stats = dict(zip(keys, values))
        pressure = _parse_psi(Path("/proc/pressure/cpu").read_text(encoding="utf-8"))
        stats["psi_some_avg10"] = pressure.get("some_avg10", 0.0)
        stats["psi_full_avg10"] = pressure.get("full_avg10", 0.0)
        try:
            load1, _, _ = os.getloadavg()
            running = float(Path("/proc/loadavg").read_text(encoding="utf-8").split()[3].split("/", 1)[0])
        except (AttributeError, IndexError, OSError, ValueError):
            load1, running = 0.0, 0.0
        stats["load1"] = float(load1)
        stats["run_queue"] = float(running)
        return stats, float(pressure.get("some_avg10", 0.0))

    def _read_job_state(self, container: str, job_id: str) -> dict:
        fallback = {"running": False, "progress": 0, "progress_epoch": None}
        for attempt in range(3):
            result = self._run(["docker", "exec", container, "cat", f"/run/{job_id}/job.state"])
            if result.returncode == 0:
                parts = result.stdout.strip().split("|")
                if len(parts) == 3:
                    try:
                        epoch = float(parts[1])
                        progress = int(parts[0])
                    except ValueError:
                        pass
                    else:
                        return {
                            "running": parts[2] == "running",
                            "progress": progress,
                            "progress_epoch": epoch,
                            "progress_age_seconds": max(0.0, time.time() - epoch),
                        }
            if attempt < 2:
                time.sleep(0.05)
        return fallback

    def _snapshot(self) -> dict:
        host_cpu, host_psi = self._read_host_cpu()
        with self._lock:
            previous = next(
                (item for item in reversed(self._history) if "error" not in item),
                None,
            )
        host_idle = 100.0
        if previous:
            before = previous["host"]["cpu_totals"]
            current_total = sum(host_cpu[k] for k in ("user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal"))
            before_total = sum(before[k] for k in ("user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal"))
            total_delta = current_total - before_total
            idle_delta = host_cpu["idle"] - before["idle"]
            host_idle = round(100.0 * idle_delta / total_delta, 3) if total_delta > 0 else 100.0
        database = self._read_cgroup(self.db_container)
        jobs = {
            job.job_id: {
                "container": self.job_containers[job.job_id],
                "cgroup": self._read_cgroup(self.job_containers[job.job_id]),
                "job": self._read_job_state(self.job_containers[job.job_id], job.job_id),
                "deadline_seconds": job.deadline_seconds,
                "minimum_quota_cores": job.minimum_quota_cores,
                "managed": job.managed,
            }
            for job in self.case.sibling_jobs
        }
        external_neighbors = {
            external_job.job_id: {
                "container": self.external_neighbor_containers[external_job.job_id],
                "managed": False,
                "role": external_job.role,
                "reserved_quota_cores": external_job.reserved_quota_cores,
                "deadline_seconds": external_job.deadline_seconds,
                "minimum_quota_cores": external_job.minimum_quota_cores,
                "cgroup": self._read_cgroup(self.external_neighbor_containers[external_job.job_id]),
                "job": self._read_job_state(
                    self.external_neighbor_containers[external_job.job_id], external_job.job_id
                ),
            }
            for external_job in self.external_neighbor_jobs
        }
        activity_counts = {}
        runner = getattr(self.env, "_workload_runner", None)
        if runner is not None:
            try:
                activity_counts = runner.get_live_activity_counts()
            except (AttributeError, TypeError, ValueError):
                # Sampling resource state must remain valid while a runner is
                # being initialized or replaced during teardown.
                activity_counts = {}
        database_usage_usec = int(database.get("cpu.stat", {}).get("usage_usec", 0))
        database_activity_count = database_usage_usec // self.RESOURCE_ACTIVITY_BUCKET_USEC
        if not database_activity_count:
            # Keep unit tests and the short setup window observable before the
            # first cgroup counter is available. Live runs use cgroup usage.
            database_activity_count = sum(
                int(values.get("ok_calls", 0))
                for values in activity_counts.values()
                if isinstance(values, dict)
            ) // self.BUSINESS_ACTIVITY_BUCKET
        for state in jobs.values():
            usage_usec = int(state["cgroup"].get("cpu.stat", {}).get("usage_usec", 0))
            state["activity_count"] = usage_usec // self.RESOURCE_ACTIVITY_BUCKET_USEC
            if not state["activity_count"]:
                state["activity_count"] = int(state["job"].get("progress", 0)) // self.JOB_ACTIVITY_BUCKET
        for state in external_neighbors.values():
            usage_usec = int(state["cgroup"].get("cpu.stat", {}).get("usage_usec", 0))
            state["activity_count"] = usage_usec // self.RESOURCE_ACTIVITY_BUCKET_USEC
            if not state["activity_count"]:
                state["activity_count"] = int(state["job"].get("progress", 0)) // self.JOB_ACTIVITY_BUCKET
        workload = {}
        if runner is not None:
            try:
                activity = runner.get_activity(limit=50)
                workload = {
                    str(item.get("fingerprint")): {
                        key: item.get(key)
                        for key in ("calls", "ok_calls", "fail_calls", "mean_ms", "p95_ms", "last_ok")
                    }
                    for item in activity.get("value", ())
                    if item.get("fingerprint")
                }
            except Exception:
                # Resource sampling remains valid when the workload ring is
                # momentarily empty during setup or teardown.
                workload = {}
            try:
                observed = runner.get_observed()
                for profile_name, values in observed.get("profiles", {}).items():
                    attempts = int(values.get("attempts", 0))
                    successes = int(values.get("successes", 0))
                    workload.setdefault(profile_name, {}).update({
                        "throughput_per_sec": float(values.get("success_qps", 0.0)),
                        "p99_ms": float(values.get("p99_latency_ms", 0.0)),
                        "success_ratio": successes / attempts if attempts else 0.0,
                    })
            except (AttributeError, TypeError, ValueError):
                pass
        database_activity_age = 0.0
        snapshot_timestamp = time.time()
        runner = getattr(self.env, "_workload_runner", None)
        if runner is not None:
            recent = getattr(runner, "_recent", ()) if runner is not None else ()
            successful = [item for item in reversed(tuple(recent)) if item.get("ok")]
            if successful:
                # Use the previous completed request when available. The most
                # recent request is often completed immediately before a sample,
                # which made the database entity uniquely report age=0.
                activity_sample = successful[1] if len(successful) > 1 else successful[0]
                database_activity_age = max(
                    0.0,
                    snapshot_timestamp - float(activity_sample.get("timestamp", snapshot_timestamp)),
                )
            elif runner.started_at is not None:
                # A newly started workload has no completed request yet. Use the
                # shared observation-window age instead of an infinity sentinel,
                # which would identify the database entity by field shape.
                database_activity_age = max(
                    0.0,
                    snapshot_timestamp - float(runner.started_at),
                )
        return {
            "timestamp": snapshot_timestamp,
            "host": {
                "cpu_totals": host_cpu,
                "idle_percent": host_idle,
                "headroom_percent": host_idle,
                "psi_some_avg10": host_psi,
            },
            "database": database,
            "jobs": jobs,
            "external_neighbors": external_neighbors,
            "workload": workload,
            "activity_age_seconds": database_activity_age,
            "activity_count": database_activity_count,
        }

    def _metric_values(self, snapshot: dict, previous: dict | None) -> dict[str, dict[str, dict[str, float]]]:
        current_timestamp = float(snapshot["timestamp"])
        previous_timestamp = float(previous["timestamp"]) if previous is not None else current_timestamp
        elapsed = max(current_timestamp - previous_timestamp, self.SAMPLE_INTERVAL_SECONDS)

        entities = {
            "database": snapshot["database"],
            **{
                job_id: state["cgroup"]
                for job_id, state in snapshot.get("jobs", {}).items()
            },
            **{
                job_id: state["cgroup"]
                for job_id, state in snapshot.get("external_neighbors", {}).items()
            },
        }
        previous_entities = {
            "database": previous.get("database", {}) if previous else {},
            **{
                job_id: state.get("cgroup", {})
                for job_id, state in (previous or {}).get("jobs", {}).items()
            },
            **{
                job_id: state.get("cgroup", {})
                for job_id, state in (previous or {}).get("external_neighbors", {}).items()
            },
        }

        def alias(entity: str) -> str:
            return self.agent_entity_aliases[entity]

        def counter(state: dict, name: str) -> float:
            return float(state.get("cpu.stat", {}).get(name, 0))

        values: dict[str, dict[str, dict[str, float]]] = {
            "host_cpu": {
                "host": {
                    "usage_percent": max(0.0, 100.0 - float(snapshot["host"].get("idle_percent", 100.0))),
                    "idle_percent": max(0.0, float(snapshot["host"].get("idle_percent", 100.0))),
                    "load1": max(0.0, float(snapshot["host"].get("cpu_totals", {}).get("load1", 0.0))),
                    "run_queue": max(0.0, float(snapshot["host"].get("cpu_totals", {}).get("run_queue", 0.0))),
                },
            },
            "host_cpu_pressure": {
                "host": {
                    "some_percent": max(0.0, float(snapshot["host"].get("psi_some_avg10", 0.0))),
                    "full_percent": max(0.0, float(snapshot["host"].get("cpu_totals", {}).get("psi_full_avg10", 0.0))),
                },
            },
            "cgroup_cpu_usage": {},
            "cgroup_cpu_throttle": {},
            "process_cpu": {},
            "service_slo": {},
            "job_progress": {},
        }
        for entity, state in entities.items():
            previous_state = previous_entities.get(entity, {})
            usage_delta = max(0.0, counter(state, "usage_usec") - counter(previous_state, "usage_usec"))
            periods_delta = max(0.0, counter(state, "nr_periods") - counter(previous_state, "nr_periods"))
            throttled_delta = max(0.0, counter(state, "nr_throttled") - counter(previous_state, "nr_throttled"))
            throttled_usec_delta = max(0.0, counter(state, "throttled_usec") - counter(previous_state, "throttled_usec"))
            process_rows = state.get("process_cpu", ())
            values["cgroup_cpu_usage"][alias(entity)] = {
                "usage_cores": usage_delta / (elapsed * 1_000_000.0),
                "quota_cores": max(0.0, float(state.get("cpu_max_cores") or 0.0)),
                "periods_delta": periods_delta,
            }
            values["cgroup_cpu_throttle"][alias(entity)] = {
                "nr_throttled_delta": throttled_delta,
                "throttled_usec_delta": throttled_usec_delta,
                "pressure_some_percent": max(0.0, float(state.get("cpu.pressure", {}).get("some_avg10", 0.0))),
            }
            values["process_cpu"][alias(entity)] = {
                # BusyBox 1.26.2 does not expose the procps `ps -o` fields;
                # cgroup usage is still a real process-family CPU observation.
                "cpu_percent": max(
                    0.0,
                    sum(float(row.get("cpu_percent", 0.0)) for row in process_rows)
                    if process_rows else usage_delta / (elapsed * 10_000.0),
                ),
                "runnable_processes": float(
                    sum(1 for row in process_rows if float(row.get("cpu_percent", 0.0)) > 0.0)
                    if process_rows else (1 if usage_delta > 0 else 0)
                ),
            }

        for profile in self.case.background_workload.profiles:
            workload = snapshot.get("workload", {}).get(profile.name, {})
            profile_alias = self.agent_profile_aliases[profile.name]
            values["service_slo"][profile_alias] = {
                "throughput_per_sec": max(0.0, float(workload.get("throughput_per_sec", 0.0))),
                "p99_ms": max(0.0, float(workload.get("p99_ms", 0.0))),
                "success_ratio": max(0.0, min(1.0, float(workload.get("success_ratio", 0.0)))),
            }

        for entity, state in {
            **snapshot.get("jobs", {}),
            **snapshot.get("external_neighbors", {}),
        }.items():
            job_state = state.get("job", {})
            previous_state = {
                **(previous or {}).get("jobs", {}).get(entity, {}),
                **(previous or {}).get("external_neighbors", {}).get(entity, {}),
            }
            progress = float(job_state.get("progress", 0))
            previous_progress = float(previous_state.get("job", {}).get("progress", progress))
            deadline = state.get("deadline_seconds")
            age = float(job_state.get("progress_age_seconds", 0.0))
            values["job_progress"][alias(entity)] = {
                "completed_units": max(0.0, progress),
                "units_per_sec": max(0.0, (progress - previous_progress) / elapsed),
                "deadline_remaining_sec": float(deadline) - age if deadline is not None else 0.0,
            }
        return values

    def _sample_once(self) -> dict:
        snapshot = self._snapshot()
        with self._lock:
            previous = next(
                (item for item in reversed(self._history) if "error" not in item),
                None,
            )
            snapshot["metric_values"] = self._metric_values(snapshot, previous)
            self._history.append(snapshot)
        return snapshot

    def capture_metric_history(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
        *,
        metric_targets: Mapping[str, tuple[str | None, ...]] | None = None,
        rate_windows: Mapping[str, int] | None = None,
    ) -> tuple[MetricFrame, ...]:
        if step_seconds <= 0 or step_seconds % 2:
            raise ValueError(f"CPU budget history step must be a positive multiple of 2 seconds: step_seconds={step_seconds}")
        metric_names = tuple(dict.fromkeys(str(metric).casefold() for metric in metrics))
        unknown = sorted(set(metric_names) - CPU_BUDGET_METRICS)
        if unknown:
            raise ValueError(f"Unknown CPU budget history metrics: metrics={unknown!r}")
        with self._lock:
            snapshots = tuple(item for item in self._history if "error" not in item and "metric_values" in item)
        if not snapshots:
            raise RuntimeError("CPU budget metric history has no samples")
        requested_timestamps = tuple(range(start_epoch_ms, end_epoch_ms + 1, step_seconds * 1000))
        selected = []
        for timestamp_ms in requested_timestamps:
            candidate = min(snapshots, key=lambda item: abs(int(item["timestamp"] * 1000) - timestamp_ms))
            distance_ms = abs(int(candidate["timestamp"] * 1000) - timestamp_ms)
            # A snapshot includes a few real process/heartbeat reads, so the
            # host-side sample phase can drift slightly from the 2-second grid.
            # Reuse only a nearby real sample; do not synthesize or interpolate.
            # Reuse only real samples: within the soft bound silently,
            # between soft and hard bounds with an audit warning, and never
            # synthesize or interpolate. Beyond the hard bound the capture is
            # evidence, not a grid, and fails loudly.
            soft_bound_ms = max(8_000, step_seconds * 1_500)
            hard_bound_ms = max(60_000, soft_bound_ms * 4)
            if distance_ms > hard_bound_ms:
                raise RuntimeError(
                    "CPU budget metric history has no sample near requested grid point: "
                    f"timestamp_ms={timestamp_ms}, nearest_distance_ms={distance_ms}, "
                    f"hard_bound_ms={hard_bound_ms}"
                )
            if distance_ms > soft_bound_ms:
                print(
                    "[CpuBudgetController] history grid reused a drifted real sample: "
                    f"timestamp_ms={timestamp_ms}, nearest_distance_ms={distance_ms}"
                )
            selected.append(candidate)
        catalog = CpuBudgetMetricCatalog()
        frames = []
        for metric in metric_names:
            first_values = selected[0]["metric_values"].get(metric, {})
            series_targets = tuple(sorted(first_values))
            series = {
                target: {
                    field: tuple(
                        float(item["metric_values"][metric][target][field])
                        for item in selected
                    )
                    for field in catalog.definition(metric).value_fields
                }
                for target in series_targets
            }
            frame = MetricFrame(
                metric=metric,
                query_target=None,
                step_seconds=step_seconds,
                series=series,
                timestamps_ms={target: requested_timestamps for target in series_targets},
            )
            validate_metric_frame(frame, catalog)
            frames.append(frame)
        return tuple(sorted(frames, key=lambda frame: metric_variant_sort_key((frame.metric, frame.query_target))))

    def _sampling_loop(self) -> None:
        # Fixed-tick schedule: a slow sample (docker contention, host load)
        # must not accumulate phase drift; the next tick stays on the grid.
        next_tick = time.monotonic()
        while not self._stop.is_set():
            try:
                self._sample_once()
            except Exception as exc:
                with self._lock:
                    self._history.append({"timestamp": time.time(), "error": str(exc)})
            next_tick += self.SAMPLE_INTERVAL_SECONDS
            delay = next_tick - time.monotonic()
            self._stop.wait(delay if delay > 0 else 0.0)

    def _start_sampling(self) -> None:
        self._stop.clear()
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = threading.Thread(
            target=self._sampling_loop,
            name=f"cpu-budget-sampler-{self.case.case_id}",
            daemon=True,
        )
        self._thread.start()

    def _stop_sampling(self) -> None:
        self._stop.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=5)
        self._thread = None

    def _container_exists(self, container: str) -> bool:
        # Recovery must stay idempotent: an already-removed container (external
        # cleanup, parallel teardown) means the policy is gone, not an error.
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", container],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"

    def _update_container(self, container: str, *, quota: float | None = None, weight: int | None = None) -> dict:
        command = ["docker", "update"]
        if quota is not None:
            # Docker converts --cpus to nanocpus; avoid passing a binary-float
            # artifact such as 0.19999999999999998 to that parser.
            cpu_arg = format(
                Decimal(str(quota)).quantize(Decimal("0.000000001")),
                "f",
            ).rstrip("0").rstrip(".") or "0"
            command.extend(["--cpus", cpu_arg])
        if weight is not None:
            command.extend(["--cpu-shares", str(weight)])
        command.append(container)
        self._run_idempotent_docker(command)
        state = self._read_cgroup(container)
        return {
            "cpu.max": state["cpu.max"],
            "cpu_max_cores": state["cpu_max_cores"],
            "cpu.weight": state["cpu.weight"],
        }

    def _reset_remediation_baseline(self) -> None:
        state = self._read_cgroup(self.db_container)["cpu.stat"]
        self._remediation_baseline = {
            "nr_throttled": state.get("nr_throttled", 0),
            "throttled_usec": state.get("throttled_usec", 0),
        }

    def _seed_normal_catalog_observation(self) -> None:
        """Leave reproducible same-domain history near the real workload queries."""
        # These are ordinary completed probes, not synthetic metric rows. They
        # make a one-shot pg_stat_statements/TopSQL lookup contain healthy CPU
        # work with similar query shapes; the live diagnosis still comes from
        # correlating the resource and business time series.
        for statement in (
            "SELECT count(*) FROM pg_class AS c "
            "JOIN pg_attribute AS a ON a.attrelid = c.oid "
            "WHERE a.attnum > 0 AND NOT a.attisdropped;",
            "SELECT sum((g * 19) % 1000003) FROM generate_series(1, 45000) AS g;",
            "SELECT avg(length(md5(g::text))) FROM generate_series(1, 30000) AS g;",
        ):
            self.env.execute_sql(statement)

    def apply_action(self, action: str, target: str | None, value: str | None) -> dict:
        if action in {"stop_sibling", "pause_sibling", "set_host_scheduler"}:
            return {
                "status": "error",
                "error": "unsafe CPU governance action is not supported for this task",
                "action": action,
            }
        if not value:
            return {"status": "error", "error": "value is required", "action": action}
        target = target or ""
        if target in self.agent_external_aliases:
            return {
                "status": "error",
                "error": "target is outside this run's resource contract",
                "target": target,
            }
        if target in self.agent_target_aliases:
            resolved = self.agent_target_aliases[target]
        elif target == "postgres":
            resolved = self.db_container
        elif target in self.job_containers.values():
            resolved = target
        elif target in self.job_containers:
            resolved = self.job_containers[target]
        else:
            return {"status": "error", "error": "target is outside this run's resource contract", "target": target}
        try:
            try:
                old_state = self._read_cgroup(resolved)
            except (OSError, RuntimeError, TypeError, ValueError, subprocess.SubprocessError):
                old_state = {}
            if value.casefold() == "max":
                return {"status": "error", "error": "unbounded CPU quota is forbidden", "target": target}
            numeric = float(value)
            if not math.isfinite(numeric) or numeric <= 0:
                raise ValueError("quota must be a finite positive number")
            if action in {
                "set_resource_limit",
                "set_peer_limit",
                "set_cpu_quota",
                "set_sibling_quota",
            }:
                # Safety follows the resolved entity, not the action spelling.
                # A generic set_resource_limit call can still target a sibling.
                is_database_limit = resolved == self.db_container
                if is_database_limit and numeric > self.case.recovery_db_quota_cores:
                    return {"status": "error", "error": "DB quota exceeds case safety bound", "target": target}
                if not is_database_limit:
                    job = next((job for job in self.case.sibling_jobs if self.job_containers[job.job_id] == resolved), None)
                    if job is None or numeric < job.minimum_quota_cores:
                        return {"status": "error", "error": "sibling quota would miss its minimum budget", "target": target}
                projected_total = numeric
                if resolved != self.db_container:
                    db_state = self._read_cgroup(self.db_container)
                    projected_total += float(db_state["cpu_max_cores"])
                for job in self.case.sibling_jobs:
                    job_container = self.job_containers[job.job_id]
                    if job_container != resolved:
                        job_state = self._read_cgroup(job_container)
                        projected_total += float(job_state["cpu_max_cores"])
                if projected_total > self.case.host_cpu_budget_cores + 1e-9:
                    # The rejection stays qualitative: echoing the projected
                    # total would hand the Agent the full budget arithmetic
                    # (every entity's live quota) through trial-and-error.
                    return {
                        "status": "error",
                        "error": "managed CPU quota sum would exceed case host budget",
                        "target": target,
                        "host_cpu_budget_cores": self.case.host_cpu_budget_cores,
                    }
                result = self._update_container(resolved, quota=numeric)
            elif action in {
                "set_scheduling_weight",
                "set_peer_weight",
                "set_cpu_weight",
                "set_sibling_weight",
            }:
                weight = int(value)
                if weight < 1 or weight > 10000:
                    raise ValueError("cpu.weight must be between 1 and 10000")
                if resolved != self.db_container:
                    job = next((job for job in self.case.sibling_jobs if self.job_containers[job.job_id] == resolved), None)
                    if job is None or weight < 10:
                        return {"status": "error", "error": "sibling weight would permanently starve a required job", "target": target}
                result = self._update_container(resolved, weight=weight)
            else:
                return {"status": "error", "error": f"unsupported CPU governance action: {action}"}
        except (ValueError, subprocess.SubprocessError, RuntimeError) as exc:
            return {"status": "error", "error": str(exc), "target": target, "action": action}
        policy_old_weight = None
        policy_new_weight = None
        if resolved == self.db_container and action in {
            "set_scheduling_weight", "set_peer_weight", "set_cpu_weight", "set_sibling_weight",
        }:
            policy_old_weight = self._db_policy_weight
            policy_new_weight = int(value)
            with self._lock:
                self._db_policy_weight = policy_new_weight
        self._record_operation_event(
            event_type="quota_revision",
            entity=self._entity_for_container(resolved),
            old_quota=float(old_state.get("cpu_max_cores") or 0.0),
            new_quota=float(result.get("cpu_max_cores") or 0.0),
            old_weight=int(old_state.get("cpu.weight") or 0),
            new_weight=int(result.get("cpu.weight") or 0),
            actor="agent",
            policy_old_weight=policy_old_weight,
            policy_new_weight=policy_new_weight,
        )
        self._reset_remediation_baseline()
        return {"status": "success", "action": action, "target": target, "state": result}

    def metric_payload(self) -> dict:
        try:
            current = self._sample_once()
        except Exception as exc:
            return {"status": "error", "metric": "resource_history", "error": str(exc)}
        with self._lock:
            history = tuple(item for item in self._history if "error" not in item)
        database_history = history[-120:]
        timestamps = [
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(item["timestamp"]))
            for item in database_history
        ]
        entity_history = {}
        for job in self.case.sibling_jobs:
            entity_history[job.job_id] = [item["jobs"][job.job_id] for item in database_history]
        for external_job in self.case.external_neighbor_jobs:
            entity_history[external_job.job_id] = [
                item["external_neighbors"][external_job.job_id]
                for item in database_history
            ]
        entity_aliases = dict(self.agent_entity_aliases)
        entities = [{
            "entity_id": entity_aliases["database"],
            "action_target": entity_aliases["database"],
            "managed": True,
            "activity_age_field": "activity_age_seconds",
            "activity_count_field": "activity_count",
            # The public resource API uses one schema for all managed entities.
            # Empty fields here used to identify PostgreSQL before any time-series
            # comparison, so the database gets the same neutral progress contract
            # shape as the sibling jobs. These fields are observational metadata,
            # not additional OP requirements.
            "deadline_seconds": 2.0,
            "minimum_quota_cores": 0.2,
            "reserved_quota_cores": None,
        }]
        for job in self.case.sibling_jobs:
            entity_id = entity_aliases[job.job_id]
            entity_aliases[job.job_id] = entity_id
            entities.append({
                "entity_id": entity_id,
                "action_target": entity_id,
                "managed": bool(job.managed),
                "activity_age_field": "activity_age_seconds",
                "activity_count_field": "activity_count",
                "deadline_seconds": job.deadline_seconds,
                "minimum_quota_cores": job.minimum_quota_cores,
                "reserved_quota_cores": None,
            })
        for external_job in self.case.external_neighbor_jobs:
            entity_id = entity_aliases[external_job.job_id]
            entity_aliases[external_job.job_id] = entity_id
            entities.append({
                "entity_id": entity_id,
                "action_target": entity_id,
                "managed": False,
                "activity_age_field": "activity_age_seconds",
                "activity_count_field": "activity_count",
                "deadline_seconds": None,
                "minimum_quota_cores": None,
                "reserved_quota_cores": external_job.reserved_quota_cores,
            })
        entities.sort(key=lambda item: item["entity_id"])

        # This is the agent-facing view.  The full current snapshot remains
        # available internally for OP/SP, while diagnosis receives only public
        # ownership metadata and aligned histories to correlate itself.
        payload = {
            "status": "success",
            "metric": "resource_history",
            "kind": "series",
            "host_cpu_budget_cores": self.case.host_cpu_budget_cores,
            "entities": entities,
            "series": {
                "timestamps": timestamps,
                "host_headroom_percent": [item["host"]["headroom_percent"] for item in database_history],
                "host_psi_some_avg10": [item["host"]["psi_some_avg10"] for item in database_history],
            },
        }
        database_observations = []
        for item in database_history:
            database_observation = dict(item["database"])
            database_observation["activity_age_seconds"] = item.get(
                "activity_age_seconds",
                float("inf"),
            )
            database_observation["activity_count"] = item.get("activity_count", 0)
            database_observations.append(database_observation)
        all_entity_observations = {
            "database": database_observations,
            **entity_history,
        }
        for entity, observations in all_entity_observations.items():
            prefix = entity_aliases[entity]
            payload["series"][f"{prefix}_cpu_max_cores"] = [
                item["cpu_max_cores"] if entity == "database" else item["cgroup"]["cpu_max_cores"]
                for item in observations
            ]
            payload["series"][f"{prefix}_throttled_usec"] = [
                item["cpu.stat"].get("throttled_usec", 0)
                if entity == "database" else item["cgroup"]["cpu.stat"].get("throttled_usec", 0)
                for item in observations
            ]
            payload["series"][f"{prefix}_psi_some_avg10"] = [
                item["cpu.pressure"].get("some_avg10", 0.0)
                if entity == "database" else item["cgroup"]["cpu.pressure"].get("some_avg10", 0.0)
                for item in observations
            ]
            payload["series"][f"{prefix}_activity_age_seconds"] = [
                item.get("activity_age_seconds", float("inf")) if entity == "database"
                else item.get("job", {}).get("progress_age_seconds", float("inf"))
                for item in observations
            ]
            payload["series"][f"{prefix}_activity_count"] = [
                item.get("activity_count", 0)
                for item in observations
            ]
        profile_names = [profile.name for profile in self.case.background_workload.profiles]
        for profile_name in profile_names:
            safe_profile = self.agent_profile_aliases[profile_name].split("_", 1)[1]
            for key in ("mean_ms", "p95_ms", "calls", "ok_calls", "fail_calls"):
                payload["series"][f"workload_{safe_profile}_{key}"] = [
                    (item.get("workload", {}).get(profile_name, {}).get(key, 0.0))
                    for item in database_history
                ]
        return payload

    def _workload_observed(self) -> dict:
        runner = getattr(self.env, "_workload_runner", None)
        if runner is None:
            return {"profiles": {}}
        return runner.get_observed()

    def final_outcome(self) -> dict:
        runner = getattr(self.env, "_workload_runner", None)
        if runner is not None:
            runner.begin_observation_window()
            # Populate the cumulative business SLO with enough real requests
            # before the first official replay sample. The 30-second replay
            # still starts only after the cgroup delta baseline is reset, and
            # warmup failures remain in the cumulative success ratio.
            runner.wait_for_profile_attempts(
                self.case.oltp_profile_name,
                minimum_attempts=10,
                timeout_seconds=10.0,
            )
            self._reset_remediation_baseline()
        else:
            self._reset_remediation_baseline()
        deadline = time.monotonic() + self.case.validation_window_seconds
        last = None
        failing_samples = []
        sample_count = 0
        while True:
            try:
                current = self._sample_once()
                observed = self._workload_observed()
                profiles = observed.get("profiles", {})
                oltp = profiles.get(self.case.oltp_profile_name, {})
                report_qps = sum(
                    float(profiles.get(name, {}).get("success_qps", 0.0))
                    for name in self.case.report_profile_names
                )
                db_stats = current["database"]["cpu.stat"]
                baseline = self._remediation_baseline
                post_fix_throttled = max(0, db_stats.get("throttled_usec", 0) - baseline.get("throttled_usec", 0))
                attempts = int(oltp.get("attempts", 0))
                successes = int(oltp.get("successes", 0))
                success_rate = successes / attempts if attempts else 0.0
                jobs = {}
                for job in self.case.sibling_jobs:
                    state = current["jobs"][job.job_id]
                    job_state = state["job"]
                    jobs[job.job_id] = {
                        "running": job_state.get("running", False),
                        "progress_age_seconds": job_state.get("progress_age_seconds", float("inf")),
                        "deadline_seconds": job.deadline_seconds,
                        "quota_cores": state["cgroup"]["cpu_max_cores"],
                        "minimum_quota_cores": job.minimum_quota_cores,
                    }
                last = {
                    "host_headroom_percent": current["host"]["headroom_percent"],
                    "host_psi_some_avg10": current["host"]["psi_some_avg10"],
                    "db_cpu_max_cores": current["database"]["cpu_max_cores"],
                    "db_cpu_weight": current["database"]["cpu.weight"],
                    "db_pressure_some_avg10": current["database"]["cpu.pressure"].get("some_avg10", 0.0),
                    "post_fix_throttled_usec": post_fix_throttled,
                    "oltp_p99_ms": float(oltp.get("p99_latency_ms", oltp.get("mean_latency_ms", 0.0))),
                    "oltp_success_rate": success_rate,
                    "report_qps": report_qps,
                    "host_cpu_budget_cores": self.case.host_cpu_budget_cores,
                    "total_quota_cores": round(
                        float(current["database"]["cpu_max_cores"] or 0.0)
                        + sum(float(state["cgroup"]["cpu_max_cores"] or 0.0) for state in current["jobs"].values()),
                        6,
                    ),
                    "validation_window_seconds": self.case.validation_window_seconds,
                    "jobs": jobs,
                }
                # Sustained-SLO semantics: every sample inside the published
                # validation window must satisfy the public invariants. A fix
                # that only looks healthy at the final tick does not pass.
                failures = []
                if last["host_headroom_percent"] < self.case.min_host_headroom_percent:
                    failures.append("host_headroom_percent")
                if last["host_psi_some_avg10"] > self.case.max_post_fix_host_psi_avg10:
                    failures.append("host_psi_some_avg10")
                if last["db_pressure_some_avg10"] > self.case.max_post_fix_db_psi_avg10:
                    failures.append("db_psi_some_avg10")
                if last["post_fix_throttled_usec"] > self.case.max_post_fix_throttled_usec:
                    failures.append("post_fix_throttled_usec")
                if last["oltp_p99_ms"] > self.case.max_oltp_p99_ms:
                    failures.append("oltp_p99_ms")
                if last["oltp_success_rate"] < self.case.min_oltp_success_rate:
                    failures.append("oltp_success_rate")
                if last["report_qps"] < self.case.min_report_qps:
                    failures.append("report_qps")
                if last["total_quota_cores"] > self.case.host_cpu_budget_cores:
                    failures.append("total_quota_cores")
                if any(
                    not item["running"]
                    or item["progress_age_seconds"] > item["deadline_seconds"]
                    or (item["quota_cores"] or 0) < item["minimum_quota_cores"]
                    for item in jobs.values()
                ):
                    failures.append("required_jobs")
                last["passed"] = not failures
                sample_count += 1
                if failures:
                    failing_samples.append({
                        "sample_index": sample_count,
                        "failures": failures,
                        "oltp_p99_ms": last["oltp_p99_ms"],
                        "post_fix_throttled_usec": last["post_fix_throttled_usec"],
                        "db_pressure_some_avg10": last["db_pressure_some_avg10"],
                        "job_progress_age_seconds": {
                            job_id: item["progress_age_seconds"] for job_id, item in jobs.items()
                        },
                    })
                if time.monotonic() >= deadline:
                    if self.case.case_id == "db_quota_throttle":
                        last["passed"] = not failing_samples
                    last["window"] = {
                        "validation_window_seconds": self.case.validation_window_seconds,
                        "sample_count": sample_count,
                        "all_samples_passed": not failing_samples,
                        "failing_samples": failing_samples[-10:],
                        "failing_sample_count": len(failing_samples),
                    }
                    return last
            except Exception as exc:
                last = {"passed": False, "error": str(exc)}
                if time.monotonic() >= deadline:
                    last["window"] = {
                        "validation_window_seconds": self.case.validation_window_seconds,
                        "sample_count": sample_count,
                        "all_samples_passed": False,
                        "failing_samples": failing_samples[-10:],
                        "failing_sample_count": len(failing_samples),
                    }
                    return last
            time.sleep(0.5)

    def safety_state(self) -> dict:
        try:
            current = self._sample_once()
            return {
            "db_cpu_max_cores": current["database"]["cpu_max_cores"],
            "external_neighbors": {
                neighbor_id: {
                    "managed": item["managed"],
                    "running": item["job"].get("running", False),
                    "quota_cores": item["cgroup"]["cpu_max_cores"],
                    "reserved_quota_cores": item["reserved_quota_cores"],
                }
                for neighbor_id, item in current.get("external_neighbors", {}).items()
            },
            "jobs": {
                    job.job_id: {
                        "running": current["jobs"][job.job_id]["job"].get("running", False),
                        "quota_cores": current["jobs"][job.job_id]["cgroup"]["cpu_max_cores"],
                        "minimum_quota_cores": job.minimum_quota_cores,
                    }
                    for job in self.case.sibling_jobs
                },
            }
        except Exception as exc:
            return {"error": str(exc)}

    def prepare_history(self) -> None:
        if self._prepared:
            return
        self._validate_host_capability()
        self._cleanup_runtime()
        self._create_runtime()
        self._update_container(self.db_container, quota=self.case.initial_db_quota_cores, weight=self.case.initial_db_weight)
        self._seed_normal_catalog_observation()
        self.env.attach_cpu_budget_controller(self)
        self._reset_remediation_baseline()
        self._start_sampling()
        self._start_normal_policy_maintenance()
        self._start_policy_windows()
        # The standard Case has no separate normal-capture phase, but its
        # controller still requires the scheduled 150-second benign policy
        # revision before installing the quota fault.
        deadline = time.monotonic() + 180
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                self._sample_once()
                if self._normal_policy_maintenance_error is not None:
                    raise RuntimeError(self._normal_policy_maintenance_error)
                if self._normal_policy_maintenance_complete:
                    self._prepared = True
                    return
            except Exception as exc:
                last_error = exc
                if self._normal_policy_maintenance_error is not None:
                    break
            time.sleep(0.5)
        raise RuntimeError(
            "history-ready failed: PostgreSQL cgroup history did not produce a sample; "
            f"last_error={last_error!r}"
        ) from last_error

    def install(self) -> None:
        if self._started:
            return
        self.prepare_history()
        self._stop_normal_policy_maintenance()
        self._stop_policy_windows(require_complete=True)
        maintenance_events = [
            event for event in self._operation_events
            if event.get("_audit_actor") == "scheduler"
            and event.get("event_type") == "quota_revision"
        ]
        if not self._normal_policy_maintenance_complete or len(maintenance_events) < 2:
            detail = self._normal_policy_maintenance_error or "expected two scheduler revisions were not captured"
            raise RuntimeError(f"frozen-history maintenance prerequisite failed: {detail}")
        before_fault = self._read_cgroup(self.db_container)
        fault_state = self._update_container(
            self.db_container,
            quota=self.case.fault_db_quota_cores,
            weight=self.case.fault_db_weight,
        )
        if self.case.case_id == "db_quota_throttle_simple":
            self._record_operation_event(
                event_type="quota_revision",
                entity="database",
                old_quota=self.case.initial_db_quota_cores,
                new_quota=self.case.fault_db_quota_cores,
                old_weight=int(before_fault.get("cpu.weight") or 0),
                new_weight=int(fault_state.get("cpu.weight") or self.case.fault_db_weight),
                actor="fault_injector",
                policy_old_weight=self.case.initial_db_weight,
                policy_new_weight=self.case.fault_db_weight,
            )
        else:
            # A quota regression does not announce itself in the audit feed:
            # the fault keeps only a console-level audit line, so the Agent
            # must build the causal chain from raw telemetry instead of reading
            # a public revision event whose entity and timestamp coincide with
            # the fault.
            print(
                "[CpuBudgetController] audit-only fault revision: "
                f"database quota {self.case.initial_db_quota_cores} -> {self.case.fault_db_quota_cores} cores"
            )
        with self._lock:
            self._db_policy_weight = self.case.fault_db_weight
        self._reset_remediation_baseline()
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                current = self._sample_once()
                db = current["database"]
                if _parse_cpu_max(db["cpu.max"]) is not None and db["cpu_max_cores"] <= self.case.fault_db_quota_cores + 0.05:
                    self._started = True
                    self._start_target_policy_maintenance()
                    return
            except Exception:
                pass
            time.sleep(0.5)
        raise RuntimeError("fault-ready failed: PostgreSQL cgroup did not expose the requested CPU quota")

    def activate(self) -> None:
        self.install()

    def quiesce(self) -> None:
        if self.case.frozen_history is not None:
            # Freeze the live sampler after capture, but keep the controller and
            # run-scoped cgroups available for Agent remediation and trusted replay.
            # The Simple case's declarative policy controller is part of the
            # live fault and must keep running through remediation/replay.
            # Other cases retain their bounded capture-only maintenance.
            if self.case.case_id != "db_quota_throttle_simple":
                self._stop_target_policy_maintenance()
            self._stop_policy_windows(require_complete=False)
            self._stop_sampling()
            return
        self._cleanup_runtime()
        self.env.detach_cpu_budget_controller()
        self._started = False
        self._prepared = False

    def recover(self) -> None:
        failures = []
        try:
            self._stop_target_policy_maintenance()
        except Exception as exc:
            failures.append(("stop target policy maintenance", exc))
        try:
            self._stop_policy_windows(require_complete=False)
        except Exception as exc:
            failures.append(("stop cost-saving window", exc))
        try:
            self._stop_normal_policy_maintenance()
        except Exception as exc:
            failures.append(("stop normal policy maintenance", exc))
        try:
            self._stop_sampling()
        except Exception as exc:
            failures.append(("stop sampling", exc))
        try:
            if self._container_exists(self.db_container):
                self._update_container(
                    self.db_container,
                    quota=self.case.initial_db_quota_cores,
                    weight=self.case.initial_db_weight,
                )
        except Exception as exc:
            failures.append(("restore database CPU policy", exc))
        try:
            self._cleanup_runtime()
        except Exception as exc:
            failures.append(("clean up run-scoped CPU resources", exc))
        try:
            self.env.detach_cpu_budget_controller()
        except Exception as exc:
            failures.append(("detach CPU budget controller", exc))
        self._started = False
        self._prepared = False
        if failures:
            details = "; ".join(f"{operation}: {exc!r}" for operation, exc in failures)
            raise RuntimeError(f"CPU budget recovery failed: {details}") from failures[0][1]


class PgResourceGovernanceContainerCpuBudgetInjector(BaseFaultInjector):
    retain_workload_after_metric_history = True

    def __init__(self) -> None:
        self.controller: CpuBudgetController | None = None

    def _case(self, context: FaultLifecycleContext) -> PgResourceGovernanceContainerCpuBudgetCase:
        if not isinstance(context.case, PgResourceGovernanceContainerCpuBudgetCase):
            raise TypeError(f"unexpected case type: {type(context.case).__name__}")
        return context.case

    def install(self, context: FaultLifecycleContext) -> None:
        existing = getattr(context.env, "_cpu_budget_controller", None)
        if isinstance(existing, CpuBudgetController) and existing.case is self._case(context):
            self.controller = existing
        else:
            self.controller = CpuBudgetController(context.env, self._case(context), context.run_id)
        self.controller.install()

    def activate(self, context: FaultLifecycleContext) -> None:
        if self.controller is None:
            self.controller = CpuBudgetController(context.env, self._case(context), context.run_id)
        self.controller.activate()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        if self.controller is None or not self.controller._started:
            raise RuntimeError("CPU budget fault is not ready for observability")
        if self._case(context).frozen_history is not None:
            return {"frozen_history": {"status": "ready"}}
        payload = self.controller.metric_payload()
        if payload.get("status") != "success":
            raise RuntimeError(f"CPU budget observability failed: {payload}")
        return {"resource_history": payload}

    def quiesce(self, context: FaultLifecycleContext) -> None:
        if self.controller is not None:
            self.controller.quiesce()

    def recover(self, context: FaultLifecycleContext) -> None:
        if self.controller is not None:
            self.controller.recover()
            self.controller = None


_EMPTY_DIAG_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": ["Applied a bounded CPU quota or scheduling policy within the task budget"],
        "verification": [
            "OLTP p99 and success rate satisfy the case contract",
            "report throughput, required job deadlines, host headroom and CPU pressure satisfy the case contract",
        ],
    },
    "summary": "CPU budget policy was validated against the OLTP, report and required-job replay.",
}


def _workloads(*, simple: bool) -> BackgroundWorkloadSpec:
    profiles = [
        WorkloadProfile(
            name="checkout_api",
            sql=(
                "SELECT sum((g * 17) % 1000003) FROM generate_series(1, 480000) AS g"
                if simple
                else "SELECT sum((g * 17) % 1000003) FROM generate_series(1, 60000) AS g"
            ),
            qps=1.6 if simple else 2.0,
            tier="MEDIUM",
            application_name="app_a",
        ),
        WorkloadProfile(
            name="finance_report" if simple else "revenue_report",
            sql="SELECT avg(length(md5(g::text))) FROM generate_series(1, 40000) AS g",
            qps=0.18 if simple else 0.35,
            tier="LIGHT",
            application_name="app_b",
        ),
    ]
    if simple:
        profiles.append(WorkloadProfile(
            name="settlement_probe",
            sql="SELECT sum((g * 19) % 1000003) FROM generate_series(1, 180000) AS g",
            qps=0.12,
            tier="LIGHT",
            application_name="app_c",
        ))
        profiles.append(WorkloadProfile(
            name="settlement_shadow",
            # A low-rate reconciliation query creates a real same-domain
            # process/load fingerprint without contaminating the post-fix
            # PSI replay. It is healthy without the quota fault and must be
            # separated from quota contact by comparing the raw timeline.
            sql="SELECT sum((g * 23) % 1000003) FROM generate_series(1, 30000) AS g",
            qps=0.02,
            tier="LIGHT",
            application_name="app_d",
        ))
    if not simple:
        profiles.append(WorkloadProfile(
            name="archive_delivery",
            sql="SELECT count(*), sum(g % 97) FROM generate_series(1, 30000) AS g",
            qps=0.22,
            tier="LIGHT",
            application_name="app_c",
        ))
        profiles.append(WorkloadProfile(
            name="inventory_projection",
            sql="SELECT avg(length(md5(g::text))) FROM generate_series(1, 36000) AS g",
            qps=0.18,
            tier="LIGHT",
            application_name="app_d",
        ))
        profiles.append(WorkloadProfile(
            name="checkout_campaign_burst",
            # A real intermittent online burst shares the database cgroup and
            # raises process CPU/service latency without changing its quota.
            # It is therefore a same-entity competing hypothesis rather than
            # a synthetic metric spike or an unrelated second fault.
            sql="SELECT sum((g * 31) % 1000003) FROM generate_series(1, 90000) AS g",
            qps=0.55,
            tier="MEDIUM",
            application_name="app_campaign",
            activity_period_seconds=90.0,
            activity_active_seconds=18.0,
        ))
        profiles.append(WorkloadProfile(
            name="inventory_reconciliation_burst",
            # A slower periodic reconciliation supplies a second real SQL/CPU
            # burst with a different cadence. Successful completion and the
            # lack of a matching persistent quota transition let an agent
            # exclude it by correlating TopSQL, cgroup and SLO timelines.
            sql="SELECT avg(length(md5((g * 37)::text))) FROM generate_series(1, 140000) AS g",
            qps=0.16,
            tier="LIGHT",
            application_name="app_reconciliation",
            activity_period_seconds=120.0,
            activity_active_seconds=24.0,
        ))
    return BackgroundWorkloadSpec(
        profiles=tuple(profiles),
        worker_count=2 if simple else 6,
        seed=0xC0A0 if simple else 0xC0FFEE,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        warmup_seconds=4,
)


_HARD_FROZEN_HISTORY_HISTORY = FrozenHistorySpec(
    schema_version=1,
    duration_seconds=12 * 60 * 60,
    normal_capture_seconds=300,
    fault_capture_seconds=300,
    base_step_seconds=2,
    overview_step_seconds=60,
    block_min_seconds=100,
    block_max_seconds=150,
    transition_seconds=2,
    target_age_seconds_range=(600, 600),
    required_metrics=(
        "host_cpu", "host_cpu_pressure", "cgroup_cpu_usage",
        "cgroup_cpu_throttle", "process_cpu", "service_slo", "job_progress",
    ),
    record_sources=(HistoricalRecordSource.OPERATION_EVENT, HistoricalRecordSource.TOPSQL),
    decoys=(
        HistoryDecoySpec(
            decoy_id="host-busy", kind=DecoyKind.CAPTURED_BENIGN,
            metric="host_cpu", field="usage_percent", target=None,
            direction=DecoyDirection.SPIKE, count=1, duration_seconds=60,
            minimum_deviation_mad=0.5,
        ),
        HistoryDecoySpec(
            decoy_id="db-process-burst", kind=DecoyKind.CAPTURED_BENIGN,
            metric="process_cpu", field="cpu_percent", target=None,
            direction=DecoyDirection.SPIKE, count=1, duration_seconds=20,
            minimum_deviation_mad=0.05, after_target=True, allow_reverse=True,
        ),
        HistoryDecoySpec(
            decoy_id="sibling-pressure", kind=DecoyKind.CAPTURED_BENIGN,
            metric="cgroup_cpu_throttle", field="throttled_usec_delta", target=None,
            direction=DecoyDirection.SPIKE, count=1, duration_seconds=60,
            minimum_deviation_mad=0.1,
        ),
        HistoryDecoySpec(
            decoy_id="pre-target-neighbor-quota-raise", kind=DecoyKind.CAPTURED_BENIGN,
            # The controller holds a real, fully restored external-neighbor
            # burst window during the normal capture. This decoy pins that
            # quota raise immediately before the target so quota movement
            # alone does not localize the regression.
            metric="cgroup_cpu_usage", field="quota_cores", target="entity_4",
            direction=DecoyDirection.SPIKE, count=1, duration_seconds=40,
            minimum_deviation_mad=0.3,
        ),
        HistoryDecoySpec(
            decoy_id="pre-target-planned-quota-window", kind=DecoyKind.CAPTURED_BENIGN,
            # The controller holds a real, fully restored cost-saving window at
            # the fault quota during the normal capture. This decoy pins that
            # complete incident-shaped bundle (quota contact plus real
            # throttle/PSI/service impact) immediately before the target; only
            # the target regression persists to the present.
            metric="cgroup_cpu_usage", field="quota_cores", target="entity_5",
            direction=DecoyDirection.DIP, count=1, duration_seconds=60,
            minimum_deviation_mad=0.5,
        ),
    ),
    max_points_per_series=2_000,
    max_scalar_samples_per_response=30_000,
    max_history_records_per_response=100,
    max_history_query_seconds=900,
    decoys_adjacent_to_target=True,
)


_HARD_CASE = PgResourceGovernanceContainerCpuBudgetForDbQuotaThrottleScenarioCase(
    case_id="db_quota_throttle",
    case_no=0,
    evaluator=PgResourceGovernanceContainerCpuBudgetForDbQuotaThrottleEvaluatorCase,
    title="PostgreSQL container and three required sibling jobs share a fixed capacity.",
    alert=(
        "P1 alert: online request performance degraded."
    ),
    initial_state={"db_quota": "bounded", "host_headroom": "available", "required_jobs": 3},
    expected_target={"oltp": "within_slo", "report": "minimum_throughput", "jobs": "within_deadline"},
    background_workload=_workloads(simple=False),
    frozen_history=_HARD_FROZEN_HISTORY_HISTORY,
    reference_report=_EMPTY_DIAG_REPORT,
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.612903,
        reference_run_ids=(
            "run_pg_resource_governance_container_cpu_budget_db_quota_throttle_MockLLMAgent",
        ),
    ),
    runtime=PostgresCaseRuntime(resources=RESOURCE_GOVERNANCE_CPU_RESOURCES),
    base_image_name=BASE_IMAGE_NAME,
    workload_tag="initialized",
    sibling_image=SIBLING_IMAGE_NAME,
    host_cpu_budget_cores=1.60,
    external_neighbor_reserved_quota_cores=0.20,
    external_neighbor_job_id=EXTERNAL_NEIGHBOR_JOB_ID,
    external_neighbor_role="external_analytics_neighbor",
    external_neighbor_weight=128,
    external_neighbor_deadline_seconds=None,
    external_neighbor_minimum_quota_cores=None,
    external_neighbor_jobs=(CpuBudgetExternalJob(
        job_id=EXTERNAL_NEIGHBOR_JOB_ID,
        role="external_analytics_neighbor",
        reserved_quota_cores=0.20,
        weight=128,
        deadline_seconds=None,
        minimum_quota_cores=None,
    ),),
    initial_db_quota_cores=2.0,
    fault_db_quota_cores=0.35,
    fault_db_weight=1024,
    recovery_db_quota_cores=1.0,
    reference_db_quota_cores=0.90,
    reference_sibling_quota_cores=(0.20, 0.30, 0.20),
    initial_db_weight=1024,
    min_host_headroom_percent=15.0,
    max_post_fix_host_psi_avg10=70.0,
    max_post_fix_db_psi_avg10=2.0,
    max_post_fix_throttled_usec=100_000,
    max_oltp_p99_ms=300.0,
    min_oltp_success_rate=0.90,
    min_report_qps=0.30,
    validation_window_seconds=30.0,
    oltp_profile_name="checkout_api",
    report_profile_names=("revenue_report", "archive_delivery"),
    sibling_jobs=(
        CpuBudgetSiblingJob(job_id="backup_worker", kind="backup", initial_quota_cores=0.45, minimum_quota_cores=0.20, initial_weight=512, deadline_seconds=2.0),
        CpuBudgetSiblingJob(job_id="compression_worker", kind="compression", initial_quota_cores=0.45, minimum_quota_cores=0.30, initial_weight=512, deadline_seconds=2.0, cpu_burn_loops=12),
        CpuBudgetSiblingJob(job_id="transfer_worker", kind="etl", initial_quota_cores=0.45, minimum_quota_cores=0.20, initial_weight=512, deadline_seconds=2.0),
    ),
)

_SIMPLE_FROZEN_HISTORY_HISTORY = FrozenHistorySpec(
    schema_version=1,
    duration_seconds=6 * 60 * 60,
    # This case's frozen design keeps a longer normal
    # capture: it is the only real source for the captured-benign competitors,
    # and a 120-second incident window keeps the quota regression from
    # dominating the overview on its own.
    normal_capture_seconds=180,
    fault_capture_seconds=120,
    base_step_seconds=2,
    overview_step_seconds=20,
    block_min_seconds=20,
    block_max_seconds=60,
    # Keep one real two-second sample between the adjacent healthy capture
    # and the target fault bundle. This makes the competitor genuinely
    # adjacent while preserving a visible phase boundary.
    transition_seconds=2,
    # Keep the incident well inside the six-hour history, with enough real
    # history on both sides for captured-benign competitors. The agent must
    # locate it from the raw metric overview before querying public events.
    target_age_seconds_range=(10_800, 10_800),
    required_metrics=(
        "host_cpu",
        "host_cpu_pressure",
        "cgroup_cpu_usage",
        "cgroup_cpu_throttle",
        "process_cpu",
        "service_slo",
        "job_progress",
    ),
    record_sources=(HistoricalRecordSource.OPERATION_EVENT,),
    decoys=(
        HistoryDecoySpec(
            decoy_id="post-target-host-busy",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="host_cpu",
            field="usage_percent",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=20,
            minimum_deviation_mad=0.5,
            after_target=True,
        ),
        HistoryDecoySpec(
            decoy_id="pre-target-workload-burst",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="service_slo",
            # Keep the real healthy workload burst immediately before the
            # target bundle. Required-job and healthy DB competitors are also
            # captured immediately before the target, so the agent must
            # establish the propagation order rather than follow one spike.
            field="throughput_per_sec",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=60,
            minimum_deviation_mad=0.5,
        ),
        HistoryDecoySpec(
            decoy_id="post-target-db-process-burst",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="process_cpu",
            field="cpu_percent",
            target="entity_3",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=20,
            minimum_deviation_mad=0.1,
            after_target=True,
        ),
        HistoryDecoySpec(
            decoy_id="pre-target-db-load-burst",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="cgroup_cpu_usage",
            field="usage_cores",
            target="entity_3",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=20,
            minimum_deviation_mad=0.1,
        ),
        HistoryDecoySpec(
            decoy_id="pre-target-planned-quota-window",
            kind=DecoyKind.CAPTURED_BENIGN,
            # The controller holds a real, fully restored cost-saving window at
            # the fault quota during the normal capture. This decoy pins that
            # complete incident-shaped bundle (quota contact plus real
            # throttle/PSI/service impact) immediately before the target; only
            # the target regression persists to the present.
            metric="cgroup_cpu_usage",
            field="quota_cores",
            target="entity_3",
            direction=DecoyDirection.DIP,
            count=1,
            duration_seconds=54,
            minimum_deviation_mad=0.5,
        ),
        HistoryDecoySpec(
            decoy_id="recent-workload-burst",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="service_slo",
            # Use the real runner's short-window throughput signal.  The
            # runner's cumulative p99 can be flat during a healthy low-load
            # capture, which would make a valid captured-benign source
            # depend on host scheduling noise.
            field="throughput_per_sec",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=60,
            minimum_deviation_mad=0.5,
            after_target=True,
        ),
        HistoryDecoySpec(
            decoy_id="recent-db-process-burst",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="process_cpu",
            field="cpu_percent",
            target="entity_3",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=60,
            minimum_deviation_mad=0.1,
            after_target=True,
        ),
        HistoryDecoySpec(
            decoy_id="db-load-burst",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="cgroup_cpu_usage",
            field="usage_cores",
            target="entity_3",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=20,
            minimum_deviation_mad=0.1,
            after_target=True,
        ),
        HistoryDecoySpec(
            decoy_id="pre-target-backup-load-burst",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="cgroup_cpu_usage",
            field="usage_cores",
            target="entity_1",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=20,
            # The required sibling's heartbeat workload is intentionally
            # low-intensity. A 0.1-MAD threshold keeps this a real captured
            # fluctuation across host schedulers without synthesizing a
            # second incident or depending on one Docker cadence.
            minimum_deviation_mad=0.1,
        ),
        HistoryDecoySpec(
            decoy_id="pre-target-backup-throttle-burst",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="cgroup_cpu_throttle",
            field="throttled_usec_delta",
            target="entity_1",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=40,
            minimum_deviation_mad=0.1,
        ),
        HistoryDecoySpec(
            decoy_id="pre-target-db-throttle-burst",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="cgroup_cpu_throttle",
            field="throttled_usec_delta",
            target="entity_3",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=40,
            # A normal, quota-healthy DB can still show a short throttle
            # burst under real workload scheduling. The target must be
            # distinguished by quota contact and service propagation.
            minimum_deviation_mad=0.1,
        ),
        HistoryDecoySpec(
            decoy_id="pre-target-sibling-quota-rebalance",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="cgroup_cpu_usage",
            field="quota_cores",
            target="entity_1",
            direction=DecoyDirection.DIP,
            count=1,
            duration_seconds=34,
            minimum_deviation_mad=0.1,
        ),
        HistoryDecoySpec(
            decoy_id="pre-target-neighbor-burst",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="cgroup_cpu_usage",
            field="usage_cores",
            target="entity_2",
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=34,
            minimum_deviation_mad=0.1,
        ),
        HistoryDecoySpec(
            decoy_id="pre-target-host-busy-extended",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="host_cpu",
            field="usage_percent",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=34,
            minimum_deviation_mad=0.1,
        ),
    ),
    max_points_per_series=2_000,
    # Four workload profiles expose 4 * 3 * 1080 = 12,960 scalar samples in
    # the service_slo overview. Keep that public overview complete; returning
    # a budget error would turn a valid diagnostic step into infrastructure
    # noise.
    max_scalar_samples_per_response=14_000,
    max_history_query_seconds=900,
    max_history_records_per_response=100,
    decoys_adjacent_to_target=True,
)

_EASY_CASE = PgResourceGovernanceContainerCpuBudgetForDbQuotaThrottleSimpleScenarioCase(
    case_id="db_quota_throttle_simple",
    case_no=1,
    evaluator=PgResourceGovernanceContainerCpuBudgetForDbQuotaThrottleSimpleEvaluatorCase,
    title="Checkout and reporting workloads are falling behind.",
    alert=(
        "P2 workload governance alert: one request workload and a low-intensity report became slow "
        "while another required work unit still needs continuous progress. Restore the published service and "
        "progress objectives, then prove the next replay meets their limits."
    ),
    initial_state={"db_quota": "bounded", "host_headroom": "available", "required_jobs": 1},
    expected_target={"oltp": "within_slo", "report": "minimum_throughput", "jobs": "within_deadline"},
    background_workload=_workloads(simple=True),
    reference_report={
        "diagnosis": {"conditions": [
            {
                "type": "root_cause",
                "factor": "stale workload-class policy binding changed the database scheduling weight",
                "entity": "database",
                "evidence": ["operation events show the database weight diverging from its healthy baseline"],
            },
            {
                "type": "causal_chain",
                "factor": "policy controller repeatedly reconciles the database to the low CPU quota",
                "entity": "database",
                "evidence": ["a direct quota correction regresses while the stale weight remains"],
            },
            {
                "type": "exclusion",
                "factor": "host CPU exhaustion and healthy sibling are excluded",
                "entity": "database",
                "evidence": ["host headroom remains available while database throttle and service latency rise"],
            },
        ]},
        "outcome": {
            "changes": ["Restored the database workload-class binding and re-partitioned bounded managed CPU quota"],
            "verification": [
                "OLTP p99 and success rate satisfy the case contract",
                "report throughput, required job deadlines, host headroom and CPU pressure satisfy the case contract",
            ],
        },
        "summary": "A stale database workload-class binding drove repeated low-quota reconciliation; the binding and bounded allocation were restored.",
    },
    frozen_history=_SIMPLE_FROZEN_HISTORY_HISTORY,
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.608696,
        reference_run_ids=(
            "reference-249__pg_resource_governance_container_cpu_budget__db_quota_throttle_simple__mock__r001",
        ),
    ),
    runtime=PostgresCaseRuntime(resources=RESOURCE_GOVERNANCE_CPU_RESOURCES),
    base_image_name=BASE_IMAGE_NAME,
    workload_tag="initialized",
    sibling_image=SIBLING_IMAGE_NAME,
    host_cpu_budget_cores=1.20,
    external_neighbor_reserved_quota_cores=0.20,
    external_neighbor_job_id="backup_shadow",
    external_neighbor_role="backup",
    external_neighbor_weight=512,
    external_neighbor_deadline_seconds=2.0,
    external_neighbor_minimum_quota_cores=0.18,
    external_neighbor_jobs=(CpuBudgetExternalJob(
        job_id="backup_shadow",
        role="backup",
        reserved_quota_cores=0.20,
        weight=512,
        deadline_seconds=2.0,
        minimum_quota_cores=0.18,
    ),),
    initial_db_quota_cores=0.90,
    fault_db_quota_cores=0.45,
    recovery_db_quota_cores=0.90,
    reference_db_quota_cores=0.90,
    reference_sibling_quota_cores=(0.30,),
    initial_db_weight=1024,
    fault_db_weight=256,
    min_host_headroom_percent=15.0,
    max_post_fix_host_psi_avg10=70.0,
    max_post_fix_db_psi_avg10=6.0,
    max_post_fix_throttled_usec=1_000_000,
    max_oltp_p99_ms=2500.0,
    min_oltp_success_rate=0.90,
    min_report_qps=0.08,
    validation_window_seconds=12.0,
    oltp_profile_name="checkout_api",
    report_profile_names=("finance_report",),
    sibling_jobs=(
        # The required backup grew into a larger standing reservation: any
        # passing governance must re-partition the shared budget (lower the
        # sibling inside its published minimum while raising the database
        # enough to clear the replay thresholds); a one-sided database raise
        # can no longer fit the 1.20-core managed budget.
        CpuBudgetSiblingJob(job_id="backup_worker", kind="backup", initial_quota_cores=0.60, minimum_quota_cores=0.18, initial_weight=512, deadline_seconds=2.0),
    ),
)


class PgResourceGovernanceContainerCpuBudgetScenario(PostgresScenario):
    scenario_id = SCENARIO_ID
    description = "Governs a PostgreSQL container and required same-host work units under a fixed shared capacity."
    cases = (_HARD_CASE, _EASY_CASE)

    def build_fault_plan(self, case: PgResourceGovernanceContainerCpuBudgetCase) -> tuple[FaultPlan, ...]:
        return (FaultPlan(
            injector_type=PgResourceGovernanceContainerCpuBudgetInjector,
            config={
                "sibling_image": case.sibling_image,
                "fault_db_quota_cores": case.fault_db_quota_cores,
                "host_cpu_budget_cores": case.host_cpu_budget_cores,
            },
        ),)
