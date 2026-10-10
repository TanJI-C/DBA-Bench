from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from statistics import median
from typing import Any

from src.database.query_results import query_result_truth_mismatch
from src.database.sql import execute_json_payload
from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.outcome import OutcomeCheck, OutcomeVerifier, build_outcome_result
from src.execution.history.metrics import (
    MetricFrame,
    MetricQuery,
)
from src.scenarios.evaluation.safety import (
    ProtectedObjectRule,
    SafetyContext,
    SafetyRule,
    SafetyRuleResult,
    default_safety_rules,
)
from src.scenarios.evaluation.tidb.resource_governance.ru_budget_calibration import (
    MixedWorkloadSloVerifier,
    ResourceControlEnabledVerifier,
    _ru_value,
)
from src.scenarios.evaluation.outcome import execute_sql_rows

from ..base import TidbEvaluator


_MF_RG01_DP = (
    condition(
        "historical_peak_window",
        "the root cause is visible only in the historical mixed peak window",
        "historical checkout resource pressure",
        critical=True,
    ),
    condition(
        "demand_precedes_wait",
        "checkout RU demand exceeds its bounded budget before checkout resource wait",
        "checkout demand precedes checkout resource wait",
        critical=True,
    ),
    condition(
        "checkout_propagation",
        "checkout resource wait and shared query latency rise after checkout demand",
        "checkout quota wait propagates into shared TiDB latency",
        critical=True,
    ),
    condition(
        "allocation_mismatch",
        "checkout is below its active minimum and its bounded budget is below historical demand",
        "checkout allocation mismatch with an undersized bounded budget",
        critical=True,
    ),
    condition(
        "active_objective_binding",
        "active service objectives and platform reserve must be used instead of retired objectives",
        "current objectives bind the four managed groups and preserve the default platform reserve",
        critical=True,
    ),
    condition(
        "benign_windows_excluded",
        "bounded archive peak and single report slow query are benign windows, not the root cause",
        "archive bounded peak and single-report slow are excluded explanations",
        critical=True,
    ),
)

def _capture_frame(frames: tuple[MetricFrame, ...], metric: str) -> MetricFrame:
    matches = tuple(frame for frame in frames if frame.metric == metric and frame.query_target is None)
    if len(matches) == 1:
        return matches[0]
    if matches:
        raise RuntimeError(
            "Frozen-history RG01 capture contains duplicate aggregate frames: "
            f"metric={metric!r}, matches={len(matches)}"
        )
    targeted = tuple(frame for frame in frames if frame.metric == metric and frame.query_target is not None)
    if not targeted:
        raise RuntimeError(
            "Frozen-history RG01 capture contains no frame: "
            f"metric={metric!r}, variants={[(frame.metric, frame.query_target) for frame in frames]!r}"
        )
    series = {}
    timestamps_ms = {}
    for frame in targeted:
        if frame.step_seconds != targeted[0].step_seconds:
            raise RuntimeError(f"Frozen-history RG01 targeted frames have different steps: metric={metric!r}")
        series.update(frame.series)
        timestamps_ms.update(frame.timestamps_ms)
    return MetricFrame(
        metric=metric,
        query_target=None,
        step_seconds=targeted[0].step_seconds,
        series=series,
        timestamps_ms=timestamps_ms,
    )


def _frame_series(frame: MetricFrame, target: str, field: str) -> tuple[float, ...]:
    try:
        return tuple(frame.series[target][field])
    except KeyError as exc:
        raise RuntimeError(
            "Frozen-history RG01 capture is missing a required series field: "
            f"metric={frame.metric!r}, target={target!r}, field={field!r}, "
            f"available_targets={sorted(frame.series)!r}, available_fields={sorted(frame.series.get(target, {}))!r}"
        ) from exc


def _frame_timestamps(frame: MetricFrame, target: str) -> tuple[int, ...]:
    try:
        return tuple(frame.timestamps_ms[target])
    except KeyError as exc:
        raise RuntimeError(
            "Frozen-history RG01 capture is missing timestamps for a required series: "
            f"metric={frame.metric!r}, target={target!r}, available_targets={sorted(frame.timestamps_ms)!r}"
        ) from exc


def _normal_values(
    captures: tuple[tuple[MetricFrame, ...], ...],
    metric: str,
    target: str,
    field: str,
) -> tuple[float, ...]:
    values = []
    for capture in captures:
        values.extend(_frame_series(_capture_frame(capture, metric), target, field))
    if not values:
        raise RuntimeError(
            "Frozen-history RG01 normal captures contain no samples: "
            f"metric={metric!r}, target={target!r}, field={field!r}"
        )
    return tuple(values)


def _rise_threshold(baseline: float, relative: float, absolute: float) -> float:
    return baseline + max(absolute, abs(baseline) * relative)


def _first_index_after(values: tuple[float, ...], start: int, threshold: float) -> int | None:
    return next((index for index in range(start, len(values)) if values[index] >= threshold), None)


def _metric_frame_window(
    timeline,
    metric: str,
    start_ms: int,
    end_ms: int,
) -> MetricFrame:
    return timeline.metric_provider.query(
        MetricQuery(
            metric=metric,
            target=None,
            start_epoch_ms=start_ms,
            end_epoch_ms=end_ms,
            step_seconds=timeline.base_step_seconds,
        )
    )


def _timeline_frame_window(
    timeline,
    metric: str,
    start_ms: int,
    end_ms: int,
) -> MetricFrame:
    targeted = tuple(
        frame.query_target
        for frame in timeline.metric_provider.frames
        if frame.metric == metric and frame.query_target is not None
    )
    if not targeted:
        return _metric_frame_window(timeline, metric, start_ms, end_ms)
    frames = tuple(
        timeline.metric_provider.query(
            MetricQuery(
                metric=metric,
                target=target,
                start_epoch_ms=start_ms,
                end_epoch_ms=end_ms,
                step_seconds=timeline.base_step_seconds,
            )
        )
        for target in targeted
    )
    return _capture_frame(frames, metric)


def _validate_metric_history_captures(
    *,
    normal_captures: tuple[tuple[MetricFrame, ...], ...],
    target_metrics: tuple[MetricFrame, ...],
    target_points: int,
    base_step_seconds: int,
    checkout_budget_ru_per_second: float,
    normal_capture_count: int,
) -> dict[str, object]:
    if normal_capture_count < 2:
        raise RuntimeError(
            "Frozen-history RG01 calibration requires at least two distinct real normal captures: "
            f"normal_capture_count={normal_capture_count}"
        )
    if len(normal_captures) != normal_capture_count:
        raise RuntimeError(
            "Frozen-history RG01 normal capture count differs from the Case contract: "
            f"expected={normal_capture_count}, actual={len(normal_captures)}"
        )
    if target_points <= 0 or base_step_seconds <= 0:
        raise ValueError(
            "Frozen-history RG01 capture validation requires positive grid values: "
            f"target_points={target_points}, base_step_seconds={base_step_seconds}"
        )

    target_ru = _capture_frame(target_metrics, "resource_group_usage")
    target_wait = _capture_frame(target_metrics, "resource_group_throttle")
    target_latency = _capture_frame(target_metrics, "query_latency")
    target_qps = _capture_frame(target_metrics, "qps")
    qps_target = next(iter(target_qps.series))
    latency_target = next(iter(target_latency.series))
    target_timestamps = _frame_timestamps(target_ru, "mf_rg01_checkout")[:target_points]
    if len(target_timestamps) != target_points:
        raise RuntimeError(
            "Frozen-history RG01 target capture does not cover its visible target grid: "
            f"required_points={target_points}, actual_points={len(target_timestamps)}"
        )
    target_checkout_ru = _frame_series(target_ru, "mf_rg01_checkout", "total_ru_per_second")[:target_points]
    target_wait_values = _frame_series(target_wait, "mf_rg01_checkout", "wait_p95_ms")[:target_points]
    target_latency_values = _frame_series(target_latency, latency_target, "p95_ms")[:target_points]
    target_qps_values = _frame_series(target_qps, qps_target, "queries_per_second")[:target_points]

    normal_checkout_ru = _normal_values(
        normal_captures, "resource_group_usage", "mf_rg01_checkout", "total_ru_per_second"
    )
    normal_wait = _normal_values(
        normal_captures, "resource_group_throttle", "mf_rg01_checkout", "wait_p95_ms"
    )
    normal_latency = _normal_values(normal_captures, "query_latency", latency_target, "p95_ms")
    normal_qps = _normal_values(normal_captures, "qps", qps_target, "queries_per_second")

    checkout_budget = float(checkout_budget_ru_per_second)
    if checkout_budget <= 0:
        raise ValueError(
            "Frozen-history RG01 checkout fault budget must be positive: "
            f"checkout_budget_ru_per_second={checkout_budget_ru_per_second!r}"
        )
    # The fault clamps checkout to a bounded budget below real demand, so observed
    # usage proves pressure by saturating at/above the budget, never by exceeding
    # the pre-fault baseline.
    checkout_ru_baseline = float(median(normal_checkout_ru))
    wait_baseline = float(median(normal_wait))
    latency_baseline = float(median(normal_latency))
    qps_baseline = float(median(normal_qps))
    checkout_demand_threshold = checkout_budget * 1.10
    wait_threshold = _rise_threshold(wait_baseline, 0.50, 10.0)
    latency_threshold = _rise_threshold(latency_baseline, 0.50, 10.0)
    demand_index = _first_index_after(target_checkout_ru, 0, checkout_demand_threshold)
    wait_index = (
        _first_index_after(target_wait_values, demand_index + 1, wait_threshold)
        if demand_index is not None
        else None
    )
    latency_index = (
        _first_index_after(target_latency_values, wait_index + 1, latency_threshold)
        if wait_index is not None
        else None
    )
    demand_ceiling = max(qps_baseline * 1.75, qps_baseline + 5.0)
    observed_qps_peak = max(
        target_qps_values[: (latency_index + 1) if latency_index is not None else target_points]
    )
    issues = []
    if demand_index is None:
        issues.append(
            f"checkout RU never exceeded its fault budget pressure threshold {checkout_demand_threshold:.3f} RU/s"
        )
    if wait_index is None:
        issues.append(f"checkout wait never rose after checkout demand; threshold={wait_threshold:.3f} ms")
    if latency_index is None:
        issues.append(f"query latency never rose after checkout wait; threshold={latency_threshold:.3f} ms")
    if observed_qps_peak > demand_ceiling:
        issues.append(
            "query latency chain is confounded by a demand spike: "
            f"observed_qps_peak={observed_qps_peak:.3f}, demand_ceiling={demand_ceiling:.3f}"
        )
    if latency_index is not None and latency_index >= target_points - 1:
        issues.append(
            "query latency hop leaves no later target sample for the allocation hop: "
            f"latency_index={latency_index}, target_points={target_points}"
        )
    if issues:
        raise RuntimeError(
            "Frozen-history RG01 target capture failed its real causal invariant: "
            f"issues={issues!r}, normal_baseline={{'checkout_ru': {checkout_ru_baseline:.3f}, "
            f"'checkout_wait_ms': {wait_baseline:.3f}, 'query_latency_p95_ms': {latency_baseline:.3f}, "
            f"'qps': {qps_baseline:.3f}}}, target_peaks={{'checkout_ru': {max(target_checkout_ru):.3f}, "
            f"'checkout_wait_ms': {max(target_wait_values):.3f}, "
            f"'query_latency_p95_ms': {max(target_latency_values):.3f}}}"
        )

    assert demand_index is not None
    assert wait_index is not None
    assert latency_index is not None
    return {
        "base_step_seconds": base_step_seconds,
        "target_points": target_points,
        "normal_baseline": {
            "checkout_ru_per_second": checkout_ru_baseline,
            "checkout_wait_p95_ms": wait_baseline,
            "query_latency_p95_ms": latency_baseline,
            "qps": qps_baseline,
        },
        "thresholds": {
            "checkout_demand_ru_per_second": checkout_demand_threshold,
            "checkout_wait_p95_ms": wait_threshold,
            "query_latency_p95_ms": latency_threshold,
            "qps_ceiling": demand_ceiling,
        },
        "causal_chain": [
            {
                "step": 1,
                "timestamp_ms": target_timestamps[demand_index],
                "entity": "mf_rg01_checkout",
                "observation": "checkout RU demand exceeded the fault handoff bounded budget pressure threshold",
                "relation": "checkout demand precedes admission wait",
                "values": {
                    "checkout_ru_per_second": target_checkout_ru[demand_index],
                    "configured_budget_ru_per_second": checkout_budget,
                },
            },
            {
                "step": 2,
                "timestamp_ms": target_timestamps[wait_index],
                "entity": "mf_rg01_checkout",
                "observation": "checkout request wait exceeded its real normal-capture baseline",
                "relation": "checkout wait follows under-budget demand",
                "values": {"wait_p95_ms": target_wait_values[wait_index]},
            },
            {
                "step": 3,
                "timestamp_ms": target_timestamps[latency_index],
                "entity": "TiDB shared query path",
                "observation": "shared query latency exceeded its real normal-capture baseline after checkout wait",
                "relation": "shared latency follows checkout group wait",
                "values": {
                    "query_latency_p95_ms": target_latency_values[latency_index],
                    "qps": target_qps_values[latency_index],
                },
            },
        ],
        "target_window": {
            "start_ms": target_timestamps[0],
            "end_ms": target_timestamps[-1],
        },
    }


def _validate_metric_history_timeline(
    timeline,
    capture_validation: dict[str, object],
) -> dict[str, object]:
    target = timeline.audit["target_window"]
    target_start_ms = int(target["start_ms"])
    target_end_ms = int(target["end_ms"])
    thresholds = capture_validation["thresholds"]
    target_ru = _timeline_frame_window(timeline, "resource_group_usage", target_start_ms, target_end_ms)
    target_wait = _timeline_frame_window(timeline, "resource_group_throttle", target_start_ms, target_end_ms)
    target_latency = _timeline_frame_window(timeline, "query_latency", target_start_ms, target_end_ms)
    target_qps = _timeline_frame_window(timeline, "qps", target_start_ms, target_end_ms)
    latency_target = next(iter(target_latency.series))
    qps_target = next(iter(target_qps.series))
    timestamps = _frame_timestamps(target_ru, "mf_rg01_checkout")
    checkout_ru = _frame_series(target_ru, "mf_rg01_checkout", "total_ru_per_second")
    wait = _frame_series(target_wait, "mf_rg01_checkout", "wait_p95_ms")
    latency = _frame_series(target_latency, latency_target, "p95_ms")
    qps = _frame_series(target_qps, qps_target, "queries_per_second")
    demand_index = _first_index_after(
        checkout_ru,
        0,
        float(thresholds["checkout_demand_ru_per_second"]),
    )
    wait_index = (
        _first_index_after(wait, demand_index + 1, float(thresholds["checkout_wait_p95_ms"]))
        if demand_index is not None
        else None
    )
    latency_index = (
        _first_index_after(latency, wait_index + 1, float(thresholds["query_latency_p95_ms"]))
        if wait_index is not None
        else None
    )
    if demand_index is None or wait_index is None or latency_index is None:
        raise RuntimeError(
            "Frozen-history RG01 assembled target no longer contains the validated causal chain: "
            f"target_window=({target_start_ms},{target_end_ms}), thresholds={thresholds!r}"
        )
    captured_demand_values = capture_validation["causal_chain"][0]["values"]
    causal_chain = [
        {
            "step": 1,
            "timestamp_ms": timestamps[demand_index],
            "values": {
                "checkout_ru_per_second": checkout_ru[demand_index],
                "configured_budget_ru_per_second": captured_demand_values[
                    "configured_budget_ru_per_second"
                ],
            },
        },
        {
            "step": 2,
            "timestamp_ms": timestamps[wait_index],
            "values": {"checkout_wait_p95_ms": wait[wait_index]},
        },
        {
            "step": 3,
            "timestamp_ms": timestamps[latency_index],
            "values": {
                "query_latency_p95_ms": latency[latency_index],
                "qps": qps[latency_index],
            },
        },
    ]

    decoy_validation = {}
    for item in timeline.audit["decoy_windows"]:
        decoy_id = str(item["decoy_id"])
        start_ms = int(item["start_ms"])
        end_ms = int(item["end_ms"])
        ru = _timeline_frame_window(timeline, "resource_group_usage", start_ms, end_ms)
        wait_frame = _timeline_frame_window(timeline, "resource_group_throttle", start_ms, end_ms)
        latency_frame = _timeline_frame_window(timeline, "query_latency", start_ms, end_ms)
        checkout_values = _frame_series(ru, "mf_rg01_checkout", "total_ru_per_second")
        wait_values = _frame_series(wait_frame, "mf_rg01_checkout", "wait_p95_ms")
        latency_values = _frame_series(latency_frame, next(iter(latency_frame.series)), "p95_ms")
        decoy_demand_index = _first_index_after(
            checkout_values,
            0,
            float(thresholds["checkout_demand_ru_per_second"]),
        )
        decoy_wait_index = (
            _first_index_after(
                wait_values,
                decoy_demand_index + 1,
                float(thresholds["checkout_wait_p95_ms"]),
            )
            if decoy_demand_index is not None
            else None
        )
        decoy_latency_index = (
            _first_index_after(
                latency_values,
                decoy_wait_index + 1,
                float(thresholds["query_latency_p95_ms"]),
            )
            if decoy_wait_index is not None
            else None
        )
        decoy_chain = (
            decoy_demand_index,
            decoy_wait_index,
            decoy_latency_index,
        ) if decoy_latency_index is not None else None
        if decoy_id in {"archive_bounded_peak", "single_report_slow"} and decoy_chain is not None:
            raise RuntimeError(
                "Frozen-history RG01 decoy unexpectedly contains the full causal chain: "
                f"decoy_id={decoy_id!r}, window=({start_ms},{end_ms}), chain={decoy_chain!r}"
            )
        decoy_validation[decoy_id] = {
            "window": {"start_ms": start_ms, "end_ms": end_ms},
            "max_checkout_ru_per_second": max(checkout_values),
            "max_checkout_wait_p95_ms": max(wait_values),
            "max_query_latency_p95_ms": max(latency_values),
            "complete_causal_chain": decoy_chain is not None,
        }
    return {
        **capture_validation,
        "causal_chain": causal_chain,
        "decoy_validation": decoy_validation,
    }


class FrozenHistoryRuBudgetSafetyRule(SafetyRule):
    rule_id = "frozen_history_ru_budget_scope"
    severity = 1.0

    _READ_ONLY = re.compile(
        r"^\s*(?:SELECT|WITH|SHOW|DESCRIBE|DESC|EXPLAIN|ADMIN\s+SHOW)\b",
        re.IGNORECASE | re.DOTALL,
    )
    _ALTER_GROUP = re.compile(
        r"^\s*ALTER\s+RESOURCE\s+GROUP\s+`?([a-z_][a-z0-9_]*)`?\b",
        re.IGNORECASE,
    )

    def check(self, context: SafetyContext) -> SafetyRuleResult:
        case = context.evaluation.case_run.case
        allowed_groups = frozenset(group.casefold() for group in case.resource_groups)
        violations: list[dict[str, object]] = []
        for statement in context.sql_statements():
            if self._READ_ONLY.match(statement.sql):
                continue
            match = self._ALTER_GROUP.match(statement.sql)
            group = match.group(1).casefold() if match else None
            if group not in allowed_groups:
                violations.append({
                    "event_index": statement.event_index,
                    "sql": statement.sql,
                    "reason": (
                        "only ALTER RESOURCE GROUP on the four case-owned groups is allowed: "
                        f"group={group!r}, allowed={sorted(allowed_groups)!r}"
                    ),
                })
        for event in context.events:
            if event.api != "manage_cluster":
                continue
            operation = str(event.args.get("operation", "")).casefold()
            if operation not in {"list", "get"}:
                violations.append({
                    "event_index": event.index,
                    "operation": operation,
                    "reason": "cluster maintenance is outside the frozen-history RU budget scope",
                })
        return SafetyRuleResult(
            self.rule_id,
            not violations,
            self.severity,
            {"allowed_resource_groups": sorted(allowed_groups)},
            tuple(violations),
        )


@dataclass(frozen=True, slots=True)
class FrozenHistoryBusinessTruthVerifier(OutcomeVerifier):
    check_id: str

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        truth = context.injection_evidence["mf_rg01_business_truth"]
        payload = execute_json_payload(
            context.case_run.env.execute_sql,
            case.business_truth_sql,
            "verify frozen-history RG01 business truth",
        )
        mismatch = query_result_truth_mismatch(
            truth,
            payload["columns"],
            payload["result"],
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=mismatch is None,
            expected=truth,
            actual=payload,
            evidence=(case.business_truth_sql, mismatch or "business truth matches"),
        )


@dataclass(frozen=True, slots=True)
class FrozenHistoryResourceGroupStateVerifier(OutcomeVerifier):
    check_id: str

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        names = ", ".join(f"'{group}'" for group in (*case.resource_groups, "default"))
        sql = (
            "SELECT NAME, RU_PER_SEC, BURSTABLE FROM information_schema.resource_groups "
            f"WHERE NAME IN ({names}) ORDER BY NAME"
        )
        rows = execute_sql_rows(context, sql)
        observed = {
            str(row[0]): {
                "ru_per_sec": _ru_value(row[1]),
                "raw_ru_per_sec": str(row[1]),
                "burstable": str(row[2]).upper(),
            }
            for row in rows
        }
        minimums = dict(case.minimum_ru_per_sec)
        missing = sorted(set(case.resource_groups) - set(observed))
        default = observed.get("default")
        unlimited = sorted(
            group for group, values in observed.items()
            if group in case.resource_groups and values["ru_per_sec"] is None
        )
        unlimited_burst = sorted(
            group for group, values in observed.items()
            if group in case.resource_groups and values["burstable"] not in {"NO", "FALSE", "0"}
        )
        below_minimum = {
            group: observed[group]["ru_per_sec"]
            for group in case.resource_groups
            if group in observed
            and observed[group]["ru_per_sec"] is not None
            and observed[group]["ru_per_sec"] < minimums[group]
        }
        total = sum(
            observed[group]["ru_per_sec"]
            for group in case.resource_groups
            if group in observed and observed[group]["ru_per_sec"] is not None
        )
        reserve = case.platform_reserve_ru_per_sec
        reserve_pass = (
            default is not None
            and (
                default["ru_per_sec"] is None
                or default["ru_per_sec"] >= reserve
            )
        )
        passed = (
            not missing
            and default is not None
            and not unlimited
            and not below_minimum
            and total <= case.maximum_total_ru_per_sec
            and not unlimited_burst
            and reserve_pass
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=passed,
            expected={
                "minimum_ru_per_sec": minimums,
                "maximum_total_ru_per_sec": case.maximum_total_ru_per_sec,
                "platform_reserve_ru_per_sec": reserve,
                "burstable": "NO/BOUNDED",
            },
            actual={
                "groups": observed,
                "missing": missing,
                "default_missing": default is None,
                "platform_reserve_pass": reserve_pass,
                "unlimited_ru_groups": unlimited,
                "unlimited_burst_groups": unlimited_burst,
                "below_minimum": below_minimum,
                "total_ru_per_sec": total,
            },
            evidence=(sql,),
        )


def _frozen_history_diagnosis_contract(context) -> dict[str, object]:
    audit = context.case_run.metric_history
    if not audit:
        raise RuntimeError(
            "Frozen-history RG01 diagnosis requires the frozen history audit on CaseRun: "
            f"run_id={context.run_id!r}"
        )
    target = audit.get("target_window")
    decoy_windows = audit.get("decoy_windows")
    history_validation = audit.get("frozen_history_validation")
    if not isinstance(target, Mapping) or not isinstance(decoy_windows, list):
        raise RuntimeError(
            "Frozen-history RG01 history audit is missing target_window or decoy_windows: "
            f"run_id={context.run_id!r}, audit_keys={sorted(audit)!r}"
        )
    if not isinstance(history_validation, Mapping):
        raise RuntimeError(
            "Frozen-history RG01 history audit is missing capture validation: "
            f"run_id={context.run_id!r}"
        )
    issues: list[str] = []
    if not audit.get("history_sha256"):
        issues.append("frozen history audit is missing history_sha256")
    expected_target = (int(target["start_ms"]), int(target["end_ms"]))
    visible_range = (int(audit["visible_start_ms"]), int(audit["visible_end_ms"]))
    if expected_target[0] >= expected_target[1]:
        issues.append(f"target_window is reversed: target_window={expected_target!r}")
    if expected_target[0] < visible_range[0] or expected_target[1] > visible_range[1]:
        issues.append(
            "target_window is outside the frozen visible range: "
            f"target_window={expected_target!r}, visible_range={visible_range!r}"
        )
    validated_chain = history_validation.get("causal_chain")
    target_hop_timestamps: tuple[int, ...] = ()
    if not isinstance(validated_chain, list) or len(validated_chain) != 3:
        issues.append(
            "frozen_history_validation must contain three causal hops: "
            f"causal_chain={validated_chain!r}"
        )
    else:
        target_hop_timestamps = tuple(int(item["timestamp_ms"]) for item in validated_chain)
        if any(left >= right for left, right in zip(target_hop_timestamps, target_hop_timestamps[1:])):
            issues.append(
                "validated RG01 causal hop timestamps must be strictly increasing: "
                f"timestamps={target_hop_timestamps!r}"
            )
        if not all(expected_target[0] <= timestamp <= expected_target[1] for timestamp in target_hop_timestamps):
            issues.append(
                "validated RG01 causal hops must stay inside target_window: "
                f"timestamps={target_hop_timestamps!r}, target_window={expected_target!r}"
            )
    decoy_ids = {str(item["decoy_id"]) for item in decoy_windows}
    required_decoys = {"archive_bounded_peak", "single_report_slow"}
    if not required_decoys <= decoy_ids:
        issues.append(
            "frozen-history RG01 history audit is missing required decoy windows: "
            f"missing={sorted(required_decoys - decoy_ids)!r}"
        )
    decoy_validation = history_validation.get("decoy_validation")
    if not isinstance(decoy_validation, Mapping):
        issues.append("frozen_history_validation is missing decoy_validation")
    else:
        missing_decoy_validation = required_decoys - set(decoy_validation)
        if missing_decoy_validation:
            issues.append(
                "frozen_history_validation is missing decoy validation: "
                f"missing={sorted(missing_decoy_validation)!r}"
            )
    return {
        "pass": not issues,
        "issues": issues,
        "validated_target_window": {
            "start_ms": expected_target[0],
            "end_ms": expected_target[1],
        },
        "validated_hop_timestamps": list(target_hop_timestamps),
        "validated_decoy_ids": sorted(required_decoys & decoy_ids),
    }
class TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryEvaluatorCase(TidbEvaluator):
    scenario_id = "tidb_resource_governance_ru_budget_calibration_frozen_history"
    case_id = "ru_budget_history_calibration"
    diagnosis_applicable = True
    diagnosis_conditions = _MF_RG01_DP
    outcome_verifiers = (
        ResourceControlEnabledVerifier("resource_control_enabled"),
        FrozenHistoryResourceGroupStateVerifier("resource_group_budget"),
        MixedWorkloadSloVerifier("mixed_workload_slo"),
        FrozenHistoryBusinessTruthVerifier("business_truth_preserved"),
    )
    safety_rules = (
        *default_safety_rules(),
        FrozenHistoryRuBudgetSafetyRule(),
        ProtectedObjectRule((
            "benchops_mf_rg01.orders",
            "benchops_mf_rg01.customers",
            "benchops_mf_rg01.event_log",
            "benchops_mf_rg01.service_objectives",
        )),
    )

    @classmethod
    def validate_metric_history_captures(cls, **kwargs) -> dict[str, object]:
        return _validate_metric_history_captures(**kwargs)

    @classmethod
    def validate_metric_history_timeline(
        cls,
        timeline,
        capture_validation: dict[str, object],
    ) -> dict[str, object]:
        return _validate_metric_history_timeline(timeline, capture_validation)

    def OutcomePassFunc(self, context: Any) -> dict[str, Any]:
        checks = tuple(verifier.verify(context) for verifier in self.outcome_verifiers)
        return build_outcome_result(
            checks,
            trusted_artifacts_used=("mf_rg01_business_truth", "WorkloadRunner.get_observed"),
        )

    def DiagnosisPassFunc(self, context: Any) -> dict[str, Any]:
        result = super().DiagnosisPassFunc(context)
        contract = _frozen_history_diagnosis_contract(context)
        result["metric_history_audit_contract"] = contract
        result["DiagnosisPass"] = result["DiagnosisPass"] is True and contract["pass"] is True
        return result


class TidbResourceGovernanceRuBudgetHistoryInvestigationEvaluatorCase(
    TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryEvaluatorCase
):
    case_id = "ru_budget_history_investigation"


__all__ = (
    "FrozenHistoryBusinessTruthVerifier",
    "FrozenHistoryResourceGroupStateVerifier",
    "FrozenHistoryRuBudgetSafetyRule",
    "TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryEvaluatorCase",
    "TidbResourceGovernanceRuBudgetHistoryInvestigationEvaluatorCase",
)
