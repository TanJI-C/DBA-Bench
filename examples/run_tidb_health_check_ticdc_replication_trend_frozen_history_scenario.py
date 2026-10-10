from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb.health_check import (
    TidbHealthCheckTiCdcReplicationTrendFrozenHistoryScenario,
)


SCENARIO = TidbHealthCheckTiCdcReplicationTrendFrozenHistoryScenario()
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def _target_window_from_progress(
    progress_series: dict,
    step_seconds: int,
    target_points: int,
) -> dict[str, str]:
    """Recover the frozen target window from the served checkpoint-lag series.

    The assembler appends the captured fault bundle, then holds the bundle's
    last value to the end of visible history (post_target_mode=HOLD_TARGET).
    The trailing constant suffix is therefore the plateau artifact, and the
    target window is the ``target_points`` samples ending at its first index.
    """
    window = progress_series["timestamps"]
    series_start = datetime.strptime(window["start"], TIMESTAMP_FORMAT)
    step = timedelta(seconds=step_seconds)
    lags = [float(value) for value in progress_series["checkpoint_lag_seconds"]]
    if len(lags) < target_points + 2:
        raise RuntimeError(
            "HC01 reference path received a truncated checkpoint-lag series: "
            f"point_count={len(lags)}, target_points={target_points}"
        )
    plateau_value = lags[-1]
    plateau_start = len(lags) - 1
    while plateau_start > 0 and lags[plateau_start - 1] == plateau_value:
        plateau_start -= 1
    target_start = plateau_start - (target_points - 1)
    if target_start < 1:
        raise RuntimeError(
            "HC01 reference path could not locate the plateau before the frozen target window: "
            f"point_count={len(lags)}, plateau_start={plateau_start}, "
            f"plateau_value={plateau_value}, target_points={target_points}"
        )
    baseline_before = lags[max(0, target_start - 60):target_start]
    if max(lags[target_start:plateau_start + 1]) <= max(baseline_before):
        raise RuntimeError(
            "HC01 reference path found no sustained degradation above baseline at the recovered window: "
            f"plateau_start={plateau_start}, plateau_value={plateau_value}, "
            f"bundle_max={max(lags[target_start:plateau_start + 1])}, "
            f"baseline_max={max(baseline_before)}"
        )
    return {
        "start_timestamp": (series_start + step * target_start).strftime(TIMESTAMP_FORMAT),
        "end_timestamp": (series_start + step * plateau_start).strftime(TIMESTAMP_FORMAT),
    }


def _require_success(payload: object, operation: str) -> dict:
    if not isinstance(payload, dict) or payload.get("status") != "success":
        raise RuntimeError(f"HC01 reference operation failed: operation={operation!r}, payload={payload!r}")
    return payload


def _wait_changefeed_state(agent: BaseAgent, changefeed_id: str, expected_state: str) -> dict:
    deadline = time.monotonic() + 180
    while True:
        payload = _require_success(
            agent.execute(
                "manage_cluster",
                {"resource": "changefeed", "operation": "get", "target": changefeed_id},
                thinking=f"确认 changefeed 已进入 {expected_state} 状态。",
            ),
            f"manage_cluster(changefeed get, expected_state={expected_state})",
        )
        state = str(payload["result"]["state"]).casefold()
        if state == expected_state:
            return payload
        if time.monotonic() > deadline:
            raise RuntimeError(
                f"HC01 changefeed did not reach state {expected_state!r} in time: "
                f"changefeed_id={changefeed_id!r}, last_state={state!r}, payload={payload!r}"
            )
        time.sleep(2)


class TiCdcReplicationTrendFrozenHistoryReferenceAgent(BaseAgent):
    """A deterministic path that uses only the Case's public tools."""

    def __init__(self, case) -> None:
        super().__init__()
        self.case = case

    def _summary_rows(self, case, watermark: int | None, target: str | None, operation: str) -> list:
        events_filter = f" WHERE event_id <= {int(watermark)}" if watermark is not None else ""
        payload = _require_success(
            self.execute(
                "execute_sql",
                {
                    "sql_query": (
                        "SELECT table_name, row_count, id_checksum FROM ("
                        f"SELECT 'orders' AS table_name, COUNT(*) AS row_count, COALESCE(SUM(order_id), 0) AS id_checksum FROM {case.db}.{case.orders_table} UNION ALL "
                        f"SELECT 'payments', COUNT(*), COALESCE(SUM(payment_id), 0) FROM {case.db}.{case.payments_table} UNION ALL "
                        f"SELECT 'inventory', COUNT(*), COALESCE(SUM(sku_id), 0) FROM {case.db}.{case.inventory_table} UNION ALL "
                        f"SELECT 'events', COUNT(*), COALESCE(SUM(event_id), 0) FROM {case.db}.{case.events_table}"
                        f"{events_filter}"
                        ") AS business_summary ORDER BY table_name"
                    ),
                    **({"target": target} if target else {}),
                },
                thinking="核对四表业务真值。",
            ),
            operation,
        )["result"]
        return [[str(value) for value in row] for row in payload]

    def _wait_sink_caught_up(self, case) -> None:
        deadline = time.monotonic() + 2400
        samples = []
        while True:
            watermark = int(
                _require_success(
                    self.execute(
                        "execute_sql",
                        {"sql_query": f"SELECT COALESCE(MAX(event_id), 0) FROM {case.db}.{case.events_table}"},
                        thinking="读取源端当前事件水位。",
                    ),
                    "source watermark query",
                )["result"][0][0]
            )
            primary = self._summary_rows(case, watermark, None, "primary watermark checksum query")
            replica = self._summary_rows(case, watermark, "downstream", "replica watermark checksum query")
            if primary == replica:
                return
            samples.append((time.monotonic(), watermark, primary, replica))
            if time.monotonic() > deadline:
                trend = "; ".join(
                    f"t+{int(when - samples[0][0])}s gap={int(p[1]) - int(r[1])}"
                    for when, _, p, r in samples[:: max(1, len(samples) // 10)]
                )
                raise RuntimeError(
                    f"HC01 sink did not catch up to the source watermark: watermark={watermark!r}, "
                    f"primary={primary!r}, replica={replica!r}, trend=[{trend}]"
                )
            time.sleep(5)

    def solve(self) -> dict:
        case = self.case
        history_help = _require_success(
            self.execute(
                "help",
                {"tool_name": "query_metrics"},
                thinking="先读取冻结历史的 UTC 范围和查询预算。",
            ),
            "help(query_metrics)",
        )
        runtime = history_help["definition"]["runtime"]
        available_start = runtime["available_start"]
        available_end = runtime["available_end"]
        progress_target = f"changefeed/{case.changefeed_id}"
        progress = _require_success(
            self.execute(
                "query_metrics",
                {
                    "metric_type": "ticdc_progress",
                    "target": progress_target,
                    "start_timestamp": available_start,
                    "end_timestamp": available_end,
                    "step_seconds": case.frozen_history.base_step_seconds,
                },
                thinking="用细粒度 checkpoint lag 找出持续超出三秒的历史窗口，而不是把当前 Normal 状态当成结论。",
            ),
            "query_metrics(ticdc_progress)",
        )
        progress_series = progress["series"][progress_target]
        target_window = _target_window_from_progress(
            progress_series,
            case.frozen_history.base_step_seconds,
            case.frozen_history.fault_capture_seconds
            // case.frozen_history.base_step_seconds,
        )

        for metric, target in (
            ("qps", None),
            ("cpu", "ticdc/ticdc-0"),
            ("cpu", "downstream/mysql-0"),
            ("network_io", "ticdc/ticdc-0"),
            ("network_io", "downstream/mysql-0"),
            ("ticdc_sink", progress_target),
        ):
            metric_args = {
                "metric_type": metric,
                "target": target,
                **target_window,
                "step_seconds": case.frozen_history.base_step_seconds,
            }
            _require_success(
                self.execute(
                    "query_metrics",
                    metric_args,
                    thinking="把 source、sink 和资源时序对齐，确认是持续容量问题而不是一次性尖峰。",
                ),
                f"query_metrics({metric}, target={target})",
            )
        for source in case.frozen_history.record_sources:
            if source.value == "component_log":
                api = "read_log"
                args = {"target": "ticdc/ticdc-0", **target_window, "lines": 200}
            else:
                api = "execute_sql"
                table = "statement_summary" if source.value == "topsql" else "slow_query"
                predicate = f"event_start_utc < '{target_window['end_timestamp']}' AND event_end_utc >= '{target_window['start_timestamp']}'" if source.value == "topsql" else f"event_time_utc >= '{target_window['start_timestamp']}' AND event_time_utc < '{target_window['end_timestamp']}'"
                args = {"target": "history", "sql_query": f"SELECT * FROM {table} WHERE {predicate} LIMIT 200"}
            _require_success(
                self.execute(
                    api,
                    args,
                    thinking="在同一 UTC 窗口核对日志、TopSQL 和慢查询，排除相邻干扰事件。",
                ),
                f"{api}({source.value})",
            )

        _require_success(
            self.execute(
                "manage_cluster",
                {"resource": "changefeed", "operation": "get", "target": case.changefeed_id},
                thinking="读取当前 changefeed 状态和执行参数，区分 Normal 状态与历史交付新鲜度。",
            ),
            "manage_cluster(changefeed get)",
        )
        _require_success(
            self.execute(
                "execute_sql",
                {"sql_query": f"SHOW INDEX FROM {case.db}.{case.events_table}", "target": "downstream"},
                thinking="比较同一逻辑事件表的上下游索引路径，确认下游额外写放大。",
            ),
            "SHOW INDEX downstream event table",
        )
        _require_success(
            self.execute(
                "execute_sql",
                {"sql_query": "SHOW GLOBAL VARIABLES LIKE 'tidb_gc_life_time'"},
                thinking="核对 GC 保留窗口，为复制延迟恢复保留安全余量。",
            ),
            "SHOW GLOBAL VARIABLES tidb_gc_life_time",
        )
        _require_success(
            self.execute(
                "execute_sql",
                {
                    "sql_query": (
                        "SELECT table_name, row_count, id_checksum FROM ("
                        f"SELECT 'orders' AS table_name, COUNT(*) AS row_count, COALESCE(SUM(order_id), 0) AS id_checksum FROM {case.db}.{case.orders_table} UNION ALL "
                        f"SELECT 'payments', COUNT(*), COALESCE(SUM(payment_id), 0) FROM {case.db}.{case.payments_table} UNION ALL "
                        f"SELECT 'inventory', COUNT(*), COALESCE(SUM(sku_id), 0) FROM {case.db}.{case.inventory_table} UNION ALL "
                        f"SELECT 'events', COUNT(*), COALESCE(SUM(event_id), 0) FROM {case.db}.{case.events_table}"
                        ") AS business_summary ORDER BY table_name"
                    )
                },
                thinking="把上下游业务真值与复制状态分开核对，排除数据损坏。",
            ),
            "business checksum query",
        )
        for target, limit, reason in (
            (
                "ticdc/ticdc-0",
                case.max_authorized_sink_cpu,
                "在授权范围内增加 TiCDC 处理资源。",
            ),
            (
                "downstream/mysql-0",
                case.max_authorized_downstream_cpu,
                "在授权范围内增加下游 MySQL 处理资源。",
            ),
        ):
            _require_success(
                self.execute(
                    "manage_cluster",
                    {
                        "resource": "service",
                        "operation": "resize",
                        "target": target,
                        "parameters": {"cpu_limit": limit},
                    },
                    thinking=reason,
                ),
                f"manage_cluster(service resize {target})",
            )
        _require_success(
            self.execute(
                "manage_cluster",
                {"resource": "changefeed", "operation": "pause", "target": case.changefeed_id},
                thinking="TiCDC 8.1 只接受已暂停 changefeed 的执行配置更新，先短暂暂停复制，业务写入不受影响。",
            ),
            "manage_cluster(changefeed pause)",
        )
        _wait_changefeed_state(self, case.changefeed_id, "stopped")
        _require_success(
            self.execute(
                "manage_cluster",
                {
                    "resource": "changefeed",
                    "operation": "update",
                    "target": case.changefeed_id,
                    "parameters": {
                        "worker_count": 32,
                        "max_txn_row": case.source_batch_rows,
                        "batch_dml_enable": True,
                    },
                },
                thinking="在暂停窗口内把 sink 事务批量大小恢复到与 source 批次相称的公开范围。",
            ),
            "manage_cluster(changefeed update)",
        )
        _require_success(
            self.execute(
                "manage_cluster",
                {"resource": "changefeed", "operation": "resume", "target": case.changefeed_id},
                thinking="执行配置已恢复，立即恢复复制并确认 changefeed 回到 Normal。",
            ),
            "manage_cluster(changefeed resume)",
        )
        _wait_changefeed_state(self, case.changefeed_id, "normal")
        self._wait_sink_caught_up(case)
        return {
                "report": {
                    **case.reference_report,
                    "outcome": {
                        **case.reference_report["outcome"],
                        "plan": {
                            "observation_window": target_window,
                        },
                    },
                }
        }


class TiCdcReplicationTrendFrozenHistoryZeroAgent(BaseAgent):
    def solve(self) -> dict:
        return {
            "report": {
                "diagnosis": {"conditions": []},
                "outcome": {"changes": [], "verification": []},
                "summary": "No diagnosis or remediation was attempted.",
            }
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=SCENARIO.description)
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "zero", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=28)
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--seed", type=int, default=20260816)
    parser.add_argument("--port", type=int, default=26800)
    parser.add_argument("--container-name", default="tidb-mf-hc01-ticdc")
    parser.add_argument(
        "--diagnosis-match-mode",
        choices=("exact", "semantic"),
        default=os.environ.get("AIOPS_DP_MATCH_MODE", "exact"),
    )
    parser.add_argument("--diagnosis-semantic-model")
    parser.add_argument("--diagnosis-semantic-config")
    args = parser.parse_args()
    case = SCENARIO.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=300,
    )
    if args.mode == "mock":
        agent = TiCdcReplicationTrendFrozenHistoryReferenceAgent(case)
        diagnosis_match_mode = "exact"
    elif args.mode == "zero":
        agent = TiCdcReplicationTrendFrozenHistoryZeroAgent()
        diagnosis_match_mode = "exact"
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
            max_output_tokens=args.max_output_tokens,
        )
        diagnosis_match_mode = args.diagnosis_match_mode
    result = Orchestrator(
        env,
        SCENARIO,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode="off",
            history_seed=args.seed,
            diagnosis_match_mode=diagnosis_match_mode,
            diagnosis_semantic_model=(
                args.diagnosis_semantic_model
                or os.environ.get("AIOPS_DP_SEMANTIC_MODEL")
                or args.model
            ),
            diagnosis_semantic_config_path=(
                args.diagnosis_semantic_config
                or os.environ.get("AIOPS_DP_SEMANTIC_CONFIG")
                or args.config_path
            ),
        ),
    ).run()
    if args.mode == "mock":
        actual = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if actual != (True, True, True):
            raise RuntimeError(
                "HC01 frozen-history mock did not pass all contracts: "
                f"actual={actual!r}, result={json.dumps(result, ensure_ascii=False, default=str)}"
            )
    print(json.dumps(result, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
