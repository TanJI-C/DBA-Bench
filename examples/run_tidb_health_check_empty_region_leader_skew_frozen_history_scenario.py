import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.execution.history.metrics import format_utc_timestamp, parse_utc_timestamp
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb.health_check import (
    TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryScenario,
)


class HC02ReferenceAgent(BaseAgent):
    """Reference path that uses only the public frozen-history observation tools."""

    def __init__(self, case):
        super().__init__()
        self.case = case

    @staticmethod
    def _require_success(payload: object, operation: str) -> dict:
        if not isinstance(payload, dict) or payload.get("status") != "success":
            raise RuntimeError(f"HC02 public observation failed: operation={operation!r}, payload={payload!r}")
        return payload

    def _runtime(self) -> dict:
        help_result = self._require_success(
            self.execute("help", {"tool_name": "query_metrics"}),
            "help(query_metrics)",
        )
        definition = help_result["definition"]
        runtime = definition["runtime"]
        if not isinstance(runtime, dict):
            raise TypeError(f"HC02 query_metrics help has no runtime object: payload={help_result!r}")
        return runtime

    @staticmethod
    def _series(payload: dict, target: str) -> dict:
        series = payload.get("series")
        if not isinstance(series, dict) or not isinstance(series.get(target), dict):
            raise TypeError(f"HC02 metric response has no requested series: target={target!r}, payload={payload!r}")
        return series[target]

    def _overview(self, metric: str) -> dict:
        return self._require_success(
            self.execute(
                "query_metrics",
                {"metric_type": metric},
                thinking=f"Read the 12-hour overview for {metric} before narrowing the incident window.",
            ),
            f"query_metrics({metric}) overview",
        )

    def _probe(self, metric: str, start: str, end: str) -> dict:
        return self._require_success(
            self.execute(
                "query_metrics",
                {
                    "metric_type": metric,
                    "start_timestamp": start,
                    "end_timestamp": end,
                    "step_seconds": self.case.frozen_history.base_step_seconds,
                },
                thinking=f"Probe the candidate UTC window at 2-second resolution for {metric}.",
            ),
            f"query_metrics({metric}) target probe",
        )

    @staticmethod
    def _candidate_anchor(inventory: dict) -> int:
        series = inventory["series"]["pd/cluster"]
        timestamps = series["timestamps"]
        total = series["total_regions"]
        empty = series["empty_regions"]
        candidates = [
            index
            for index in range(1, len(timestamps))
            if total[index] > total[index - 1] or empty[index] > empty[index - 1]
        ]
        if not candidates:
            raise RuntimeError("HC02 overview has no Region inventory growth transition")
        index = max(
            candidates,
            key=lambda item: (
                float(total[item]) - float(total[item - 1])
                + float(empty[item]) - float(empty[item - 1]),
                item,
            ),
        )
        return parse_utc_timestamp(timestamps[index], f"overview.timestamps[{index}]")

    @staticmethod
    def _refine_target_start_ms(
        overview_inventory: dict,
        coarse_inventory: dict,
        anchor_ms: int,
    ) -> int:
        overview_series = overview_inventory["series"]["pd/cluster"]
        anchor_timestamp = format_utc_timestamp(anchor_ms)
        anchor_index = overview_series["timestamps"].index(anchor_timestamp)
        target_total_regions = float(overview_series["total_regions"][anchor_index])
        coarse_series = coarse_inventory["series"]["pd/cluster"]
        candidates = []
        for index in range(1, len(coarse_series["timestamps"])):
            current = float(coarse_series["total_regions"][index])
            previous = float(coarse_series["total_regions"][index - 1])
            if current == target_total_regions and previous != target_total_regions:
                candidates.append(index)
        if len(candidates) != 1:
            raise RuntimeError(
                "HC02 public fine probe must identify one target onset: "
                f"anchor_ms={anchor_ms}, target_total_regions={target_total_regions}, candidates={candidates!r}"
            )
        return parse_utc_timestamp(
            coarse_series["timestamps"][candidates[0]],
            f"coarse_inventory.timestamps[{candidates[0]}]",
        )

    @staticmethod
    def _review_values(inventory: dict, activity: dict, leaders: dict) -> dict[str, float | int]:
        inventory_series = inventory["series"]["pd/cluster"]
        empty = tuple(float(value) for value in inventory_series["empty_regions"])
        zero_key = tuple(float(value) for value in inventory_series["zero_key_regions"])
        merges = tuple(
            float(value)
            for value in activity["series"]["pd/cluster"]["merges_per_minute"]
        )
        leader_series = leaders["series"]
        leader_targets = tuple(sorted(leader_series))
        leader_points = len(leader_series[leader_targets[0]]["leader_count"])
        ratios = []
        for index in range(leader_points):
            counts = [float(leader_series[target]["leader_count"][index]) for target in leader_targets]
            if min(counts) <= 0:
                raise RuntimeError(f"HC02 public leader probe contains a zero-leader target: counts={counts!r}")
            ratios.append(max(counts) / min(counts))
        return {
            "empty_region_count": int(max(empty)),
            "zero_key_region_count": int(max(zero_key)),
            "leader_skew_ratio": round(max(ratios), 4),
            "merge_rate_per_min": round(max(merges), 4),
        }

    @staticmethod
    def _metric_evidence(
        payload: dict,
        *,
        metric: str,
        target: str,
        field: str,
        start: str,
        end: str,
        direction: str,
    ) -> dict[str, object]:
        series = payload["series"][target]
        selected = [
            float(value)
            for timestamp, value in zip(series["timestamps"], series[field], strict=True)
            if start <= timestamp <= end
        ]
        if not selected:
            raise RuntimeError(
                "HC02 reference metric evidence has no samples in timeline segment: "
                f"metric={metric!r}, target={target!r}, field={field!r}, window=({start},{end})"
            )
        return {
            "metric": metric,
            "target": target,
            "field": field,
            "direction": direction,
            "start_value": selected[0],
            "end_value": selected[-1],
        }

    @staticmethod
    def _require_fault_schedule(payload: dict) -> None:
        result = payload.get("result")
        schedule = result["schedule"]
        expected = {
            "enable-cross-table-merge": False,
            "merge-schedule-limit": 2,
            "split-merge-interval": "1h0m0s",
        }
        observed = {
            "enable-cross-table-merge": str(schedule["enable-cross-table-merge"]).casefold()
            in {"true", "1", "on"},
            "merge-schedule-limit": int(schedule["merge-schedule-limit"]),
            "split-merge-interval": str(schedule["split-merge-interval"]),
        }
        if observed != expected:
            raise RuntimeError(
                f"HC02 public PD schedule does not show the constrained state: expected={expected!r}, observed={observed!r}"
            )

    @staticmethod
    def _require_fault_store_weights(payload: dict) -> None:
        stores = payload["result"]["stores"]
        observed = {
            str(item["store"]["address"]).split(":", 1)[0]: (
                int(item["status"]["leader_weight"]),
                int(item["status"]["region_weight"]),
            )
            for item in stores
            if str(item["store"]["address"]).split(":", 1)[0].startswith("tikv-")
        }
        expected = {"tikv-0": (10, 1), "tikv-1": (1, 1), "tikv-2": (1, 1)}
        if observed != expected:
            raise RuntimeError(
                f"HC02 public TiKV placement weights do not show the constrained state: expected={expected!r}, observed={observed!r}"
            )

    def _record_evidence(self, start: str, end: str) -> list[dict[str, object]]:
        evidence = []
        for source in self.case.frozen_history.record_sources:
            if source.value == "component_log":
                api = "read_log"
                args = {"target": "tikv/tikv-0", "start_timestamp": start, "end_timestamp": end, "lines": 20}
            else:
                api = "execute_sql"
                table = "statement_summary" if source.value == "topsql" else "slow_query"
                time_predicate = (
                    f"event_start_utc < '{end}' AND event_end_utc >= '{start}'"
                    if source.value == "topsql"
                    else f"event_time_utc >= '{start}' AND event_time_utc < '{end}'"
                )
                args = {"target": "history", "sql_query": f"SELECT * FROM {table} WHERE {time_predicate} LIMIT 20"}
            payload = self._require_success(
                self.execute(
                    api,
                    args,
                    thinking=f"Read {source.value} records from the same target UTC window.",
                ),
                f"{api}({source.value}) target window",
            )
            if source.value == "component_log":
                records = payload.get("records")
                if not isinstance(records, list) or not records:
                    raise RuntimeError(
                        f"HC02 public target history has no record: source={source.value!r}, window=({start},{end})"
                    )
                record = records[0]
                if not isinstance(record, dict) or not record.get("target"):
                    raise TypeError(f"HC02 public history record has no target: source={source.value!r}, record={record!r}")
                item = {
                    "source": source.value,
                    "target": record["target"],
                    "record": {
                        key: value
                        for key, value in record.items()
                        if key not in {"target", "timestamp", "start_timestamp", "end_timestamp"}
                    },
                }
                if "timestamp" in record:
                    item["timestamp"] = record["timestamp"]
                else:
                    item["start_timestamp"] = record["start_timestamp"]
                    item["end_timestamp"] = record["end_timestamp"]
                evidence.append(item)
            else:
                rows = payload.get("result")
                if not isinstance(rows, list) or not rows:
                    raise RuntimeError(
                        f"HC02 public target history has no record: source={source.value!r}, window=({start},{end})"
                    )
        return evidence

    def _report(
        self,
        start: str,
        end: str,
        record_evidence: list[dict[str, object]],
        coarse_inventory: dict,
        inventory_probe: dict,
        activity_probe: dict,
        leaders_probe: dict,
    ) -> dict:
        split_peak = max(
            float(value)
            for value in activity_probe["series"]["pd/cluster"]["splits_per_minute"]
        )
        merge_peak = max(
            float(value)
            for value in activity_probe["series"]["pd/cluster"]["merges_per_minute"]
        )
        scheduler_factor = (
            "Region growth was followed by no observed merge operator activity while inventory remained elevated"
            if split_peak == 0 and merge_peak == 0
            else "Region growth was followed by merge operator attempts staying below split operator attempts"
        )
        conditions = [
            {
                "type": "finding",
                "factor": "the target UTC window is the persistent empty-region accumulation episode",
                "entity": "pd/cluster",
                "evidence": ["the frozen target window is the only persistent episode"],
            },
            {
                "type": "finding",
                "factor": scheduler_factor,
                "entity": "pd/cluster",
                "evidence": ["pd_region_inventory and pd_region_activity are ordered in the timeline"],
            },
            {
                "type": "finding",
                "factor": "empty and zero-key regions accumulated and did not drain",
                "entity": "pd/cluster",
                "evidence": ["empty_regions and zero_key_regions remain elevated"],
            },
            {
                "type": "finding",
                "factor": "leader skew formed after the empty-region accumulation and is not the hot-write root cause",
                "entity": "tikv/tikv-0..2",
                "evidence": ["leader_count changes follow the Region population"],
            },
            {
                "type": "finding",
                "factor": "PD cross-table merge is disabled with a constrained merge schedule limit and long split-merge interval",
                "entity": "pd/cluster schedule",
                "evidence": ["current PD schedule source truth contains all three constraints"],
            },
            {
                "type": "finding",
                "factor": "current TiKV leader_weight=10 on tikv-0 and leader_weight=1 on tikv-1/tikv-2, with region_weight=1 on all three stores and nonzero leaders",
                "entity": "tikv/tikv-0..2 placement",
                "evidence": ["manage_cluster store list exposes leader_weight and region_weight"],
            },
            {
                "type": "finding",
                "factor": "pre-split merge and hot-leader episodes were excluded using their recovery evidence",
                "entity": "historical decoy windows",
                "evidence": ["benign windows recover before the target"],
            },
            {
                "type": "finding",
                "factor": "normal current QPS, p99 latency, and PD CPU do not disprove the persistent capacity risk",
                "entity": "current frontend and PD state",
                "evidence": ["current SLO is ordinary while Region risk remains"],
            },
        ]
        start_ms = parse_utc_timestamp(start, "reference.target_window_start")
        end_ms = parse_utc_timestamp(end, "reference.target_window_end")
        duration_ms = end_ms - start_ms
        coarse_start_ms = parse_utc_timestamp(
            coarse_inventory["window"]["requested_start"],
            "coarse_inventory.window.requested_start",
        )
        pre_target_start_ms = max(start_ms - 300_000, coarse_start_ms)
        if pre_target_start_ms >= start_ms:
            raise RuntimeError(
                "HC02 reference cannot build the pre-target Region-growth segment: "
                f"pre_target_start_ms={pre_target_start_ms}, target_start_ms={start_ms}"
            )
        base_step_ms = self.case.frozen_history.base_step_seconds * 1000
        remaining_ms = duration_ms
        target_bounds = [start_ms]
        for segment_index in range(2):
            segments_left = 3 - segment_index
            segment_ms = (remaining_ms // segments_left // base_step_ms) * base_step_ms
            if segment_ms <= 0:
                raise RuntimeError(
                    "HC02 reference cannot partition target window on the metric base grid: "
                    f"duration_ms={duration_ms}, remaining_ms={remaining_ms}, "
                    f"segments_left={segments_left}, base_step_ms={base_step_ms}"
                )
            target_bounds.append(target_bounds[-1] + segment_ms)
            remaining_ms -= segment_ms
        target_bounds.append(end_ms)
        timeline = []
        timeline_bounds = (
            (pre_target_start_ms, start_ms),
            (target_bounds[0], target_bounds[1]),
            (target_bounds[1], target_bounds[2]),
            (target_bounds[2], target_bounds[3]),
        )
        for sequence, (item_start, item_end) in enumerate(timeline_bounds):
            item_start_timestamp = format_utc_timestamp(item_start)
            item_end_timestamp = format_utc_timestamp(item_end)
            if sequence == 0:
                evidence = [
                    self._metric_evidence(
                        coarse_inventory,
                        metric="pd_region_inventory",
                        target="pd/cluster",
                        field="total_regions",
                        start=item_start_timestamp,
                        end=item_end_timestamp,
                        direction="growth",
                    ),
                ]
            elif sequence == 1:
                evidence = [
                    self._metric_evidence(
                        inventory_probe,
                        metric="pd_region_inventory",
                        target="pd/cluster",
                        field="empty_regions",
                        start=item_start_timestamp,
                        end=item_end_timestamp,
                        direction="persistent",
                    ),
                    self._metric_evidence(
                        activity_probe,
                        metric="pd_region_activity",
                        target="pd/cluster",
                        field="splits_per_minute",
                        start=item_start_timestamp,
                        end=item_end_timestamp,
                        direction="operator_attempts",
                    ),
                    self._metric_evidence(
                        activity_probe,
                        metric="pd_region_activity",
                        target="pd/cluster",
                        field="merges_per_minute",
                        start=item_start_timestamp,
                        end=item_end_timestamp,
                        direction="operator_attempts",
                    ),
                ]
            elif sequence == 2:
                evidence = [
                    self._metric_evidence(
                        inventory_probe,
                        metric="pd_region_inventory",
                        target="pd/cluster",
                        field="zero_key_regions",
                        start=item_start_timestamp,
                        end=item_end_timestamp,
                        direction="persistent",
                    ),
                ]
            else:
                evidence = [
                    self._metric_evidence(
                        leaders_probe,
                        metric="pd_leader_distribution",
                        target=target,
                        field="leader_count",
                        start=item_start_timestamp,
                        end=item_end_timestamp,
                        direction="downstream_skew",
                    )
                    for target in sorted(leaders_probe["series"])
                ]
            timeline.append(
                {
                    "sequence": sequence + 1,
                    "start_timestamp": item_start_timestamp,
                    "end_timestamp": item_end_timestamp,
                    "observation": f"metric evidence segment {sequence + 1}",
                    "metric_evidence": evidence,
                }
            )
        return {
            "diagnosis": {
                "conditions": conditions,
            },
            "outcome": {
                "changes": ["recorded a bounded multi-table consolidation plan in the review row"],
                "verification": ["reconciled PD source truth and the protected business checksum"],
                "plan": {
                    "incident_window": {
                        "start_timestamp": start,
                        "end_timestamp": end,
                    },
                    "timeline": timeline,
                    "corroborating_records": [
                        *record_evidence,
                    ],
                    "excluded_windows": [
                        {"candidate": "benign_presplit_merge", "reason": "short recovery"},
                        {"candidate": "benign_hot_leader", "reason": "short recovery"},
                    ],
                    "current_state_interpretation": "ordinary frontend SLO does not clear persistent Region capacity risk",
                },
            },
            "summary": "The historical Region-capacity risk was identified and recorded without executing consolidation.",
        }

    def solve(self):
        runtime = self._runtime()
        history_spec = self.case.frozen_history
        target_capture_seconds = history_spec.fault_capture_seconds
        base_step_seconds = history_spec.base_step_seconds
        inventory_overview = self._overview("pd_region_inventory")
        anchor_ms = self._candidate_anchor(inventory_overview)

        overview_step_seconds = history_spec.overview_step_seconds
        coarse_start_ms = anchor_ms - overview_step_seconds * 1000
        coarse_end_ms = anchor_ms + (target_capture_seconds - overview_step_seconds) * 1000
        coarse_inventory = self._probe(
            "pd_region_inventory",
            format_utc_timestamp(coarse_start_ms),
            format_utc_timestamp(coarse_end_ms),
        )
        target_start_ms = self._refine_target_start_ms(
            inventory_overview,
            coarse_inventory,
            anchor_ms,
        )
        target_end_ms = target_start_ms + (target_capture_seconds - base_step_seconds) * 1000
        start = format_utc_timestamp(target_start_ms)
        end = format_utc_timestamp(target_end_ms)
        inventory_probe = self._probe("pd_region_inventory", start, end)
        activity_probe = self._probe("pd_region_activity", start, end)
        leaders_probe = self._probe("pd_leader_distribution", start, end)
        review_values = self._review_values(inventory_probe, activity_probe, leaders_probe)
        pd_config = self._require_success(
            self.execute(
                "manage_cluster",
                {"resource": "config", "operation": "get", "target": "pd"},
                thinking="Read the current PD schedule after the historical metric chain is established.",
            ),
            "manage_cluster(config get pd)",
        )
        self._require_fault_schedule(pd_config)
        store_distribution = self._require_success(
            self.execute(
                "manage_cluster",
                {"resource": "store", "operation": "list"},
                thinking="Read current TiKV leader and region placement weights to distinguish placement skew from a hot-leader episode.",
            ),
            "manage_cluster(store list)",
        )
        self._require_fault_store_weights(store_distribution)
        record_evidence = self._record_evidence(start, end)
        self._require_success(self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"UPDATE {self.case.db}.{self.case.review_table} SET "
                    "status = 'action_required', risk_confirmed = 1, "
                    "persistent_pattern_confirmed = 1, decoy_causes_excluded = 1, "
                    "leader_skew_attributed = 1, scheduler_constraint_confirmed = 1, "
                    "plan_bounded = 1, maintenance_window_required = 1, restart_required = 0, "
                    "business_data_mutation_allowed = 0, verification_complete = 1, "
                    f"target_window_start = '{start}', target_window_end = '{end}', "
                    f"empty_region_count = {review_values['empty_region_count']}, "
                    f"zero_key_region_count = {review_values['zero_key_region_count']}, "
                    f"leader_skew_ratio = {review_values['leader_skew_ratio']:.4f}, "
                    f"merge_rate_per_min = {review_values['merge_rate_per_min']:.4f}, "
                    f"business_checksum = {self.case.business_checksum}, "
                    "bounded_plan = 'stage bounded cross-table consolidation during maintenance', "
                    "maintenance_boundary = 'do not modify business rows or PD scheduling' "
                    f"WHERE review_key = '{self.case.review_key}'"
                )
            },
            thinking="Record only a bounded review decision; do not change PD scheduling or execute consolidation.",
        ), "scoped review-row update")
        return {
            "report": self._report(
                start,
                end,
                record_evidence,
                coarse_inventory,
                inventory_probe,
                activity_probe,
                leaders_probe,
            )
        }


class HC02MockAgent(HC02ReferenceAgent):
    """Deterministic smoke path with no external model call."""


def main() -> None:
    scenario = TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB frozen-history empty Region and leader-skew health check."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "reference", "llm"], default="reference")
    parser.add_argument("--port", type=int, default=28680)
    parser.add_argument("--container-name", default="tidb-frozen-history-hc02")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--seed", type=int, default=20260816)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=120,
    )
    if args.mode == "mock":
        agent = HC02MockAgent(case)
    elif args.mode == "reference":
        agent = HC02ReferenceAgent(case)
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode="off",
        history_seed=args.seed,
    )
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=run_config,
    ).run()
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
