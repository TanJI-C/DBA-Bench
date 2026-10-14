"""Run the frozen-history set-autocommit TiDB scenario.

The reference agent is kept as a structured mock path for later calibration.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb import TidbQueryPerfSetAutocommitStormFrozenHistoryScenario
from src.scenarios.tidb.query_perf.set_autocommit_storm_frozen_history import _REFERENCE_REPORT


SCENARIO = TidbQueryPerfSetAutocommitStormFrozenHistoryScenario()
REFERENCE_REPORT = _REFERENCE_REPORT
UTC = timezone.utc
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def _success(result: object, context: str) -> dict:
    if not isinstance(result, dict) or result.get("status") != "success":
        raise RuntimeError(f"MF-set-autocommit reference operation failed: context={context!r}, result={result!r}")
    return result


def _rows(result: object, context: str) -> list:
    payload = _success(result, context)
    rows = payload.get("result")
    if not isinstance(rows, list):
        raise TypeError(f"MF-set-autocommit reference expected SQL rows: context={context!r}, result={result!r}")
    return rows


def _utc(value: str) -> datetime:
    return datetime.strptime(value, TIMESTAMP_FORMAT).replace(tzinfo=UTC)


def _stamp(value: datetime) -> str:
    return value.astimezone(UTC).strftime(TIMESTAMP_FORMAT)


class FrozenHistoryReferenceAgent(BaseAgent):
    """A complete reference path that derives the bounded history window from metrics."""

    def __init__(self, case) -> None:
        super().__init__()
        self.case = case

    def _history_runtime(self) -> tuple[datetime, datetime]:
        payload = _success(
            self.execute(
                "help",
                {"tool_name": "query_metrics"},
                thinking="先读取冻结历史的 UTC 边界、采样步长和查询预算。",
            ),
            "history help",
        )
        runtime = payload["definition"]["runtime"]
        return _utc(runtime["available_start"]), _utc(runtime["available_end"])

    def _select_history_window(self, available_start: datetime, available_end: datetime) -> tuple[str, str]:
        latency = _success(
            self.execute(
                "query_metrics",
                {"metric_type": "query_latency"},
                thinking="先用 12 小时 query latency overview 找候选窗口，不把当前静态 assignment 当作历史根因。",
            ),
            "query latency overview",
        )
        series = latency["series"]["cluster"]
        p95_values = series["p95_ms"]
        peak_index = max(range(len(p95_values)), key=p95_values.__getitem__)
        peak_time = _utc(series["timestamps"][peak_index])
        window_start = max(available_start, peak_time - timedelta(seconds=240))
        window_end = min(available_end, window_start + timedelta(seconds=480))
        if (window_end - window_start).total_seconds() < 120:
            raise RuntimeError(
                "MF-set-autocommit reference history window is too short: "
                f"start={window_start!r}, end={window_end!r}, peak={peak_time!r}"
            )
        return _stamp(window_start), _stamp(window_end)

    def _read_history(self, start_timestamp: str, end_timestamp: str) -> None:
        for metric in ("cpu", "qps", "query_latency", "active_connections"):
            self.execute(
                "query_metrics",
                {
                    "metric_type": metric,
                    "start_timestamp": start_timestamp,
                    "end_timestamp": end_timestamp,
                    "step_seconds": 60,
                },
                thinking="在同一 bounded UTC 窗口读取原始指标，比较顺序、目标实体和 healthy sibling。",
            )
        for source in ("component_log", "topsql", "slow_queries"):
            if source == "component_log":
                api = "read_log"
                args = {"target": "tidb/tidb-0", "start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "lines": 200}
            else:
                api = "execute_sql"
                table = "statement_summary" if source == "topsql" else "slow_query"
                time_predicate = (
                    f"event_start_utc < '{end_timestamp}' AND event_end_utc >= '{start_timestamp}'"
                    if source == "topsql"
                    else f"event_time_utc >= '{start_timestamp}' AND event_time_utc < '{end_timestamp}'"
                )
                args = {"target": "history", "sql_query": f"SELECT * FROM {table} WHERE {time_predicate} LIMIT 200"}
            self.execute(
                api,
                args,
                thinking=f"在同一 bounded UTC 窗口交叉查询 {source}，区分当前目标与已结束的 benign episode。",
            )

    def _read_current_control_plane(self) -> None:
        case = self.case
        self.execute(
            "help",
            {"tool_name": "execute_sql"},
            thinking="先确认当前 SQL connection surface，再读取应用控制面和 TiDB 标准观察面。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT INSTANCE, ID, USER, RESOURCE_GROUP, SESSION_ALIAS, DB, STATE, INFO "
                    "FROM information_schema.cluster_processlist "
                    "WHERE SESSION_ALIAS <> '' ORDER BY INSTANCE, ID LIMIT 200"
                )
            },
            thinking="用 resource group 和 session alias 将异常 statement 映射到具体 cohort。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT cohort_id, service_name, resource_group, session_alias_prefix, traffic_weight, "
                    f"pool_size, connector_revision, checkout_revision, enabled, deployment_lane, "
                    f"session_binding_mode, session_lease_mode FROM {case.db}.{case.assignments_table} "
                    "ORDER BY cohort_id"
                )
            },
            thinking="比较四个在线 cohort 的 current assignment 和容量不变量。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT revision_id, use_local_session_state, elide_set_autocommits, "
                    f"cache_server_configuration, always_send_set_isolation FROM {case.db}.{case.connector_table} "
                    "ORDER BY revision_id"
                )
            },
            thinking="把 connector revision 作为相关近邻，避免把 shared revision 静态猜测当充分根因。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT revision_id, reset_mode, reset_count, validation_mode, transaction_boundary_mode "
                    f"FROM {case.db}.{case.checkout_table} ORDER BY revision_id"
                )
            },
            thinking="比较 checkout reset 语义与四个 online combination。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT revision_id, revision_kind, scope, owner_cohort_id, "
                    f"use_local_session_state, elide_set_autocommits, cache_server_configuration, "
                    f"always_send_set_isolation, reset_mode, reset_count, validation_mode, "
                    f"transaction_boundary_mode, session_lease_mode FROM {case.db}.{case.revision_catalog_table} "
                    "ORDER BY revision_id"
                )
            },
            thinking="确认 shared 与 target-owned revision 边界及 session lease 注册关系。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT cohort_id, desired_connector_revision, desired_checkout_revision, "
                    f"desired_deployment_lane, desired_session_binding_mode, desired_session_lease_mode, "
                    f"generation, applied_generation, rollout_state, last_reconcile_at "
                    f"FROM {case.db}.{case.rollouts_table} ORDER BY cohort_id"
                )
            },
            thinking="区分 runtime_rollouts desired generation 与 runtime_assignments current state。",
        )

    def _wait_for_reconcile(self) -> None:
        case = self.case
        deadline = time.monotonic() + 45.0
        sql = (
            f"SELECT a.connector_revision, a.checkout_revision, a.deployment_lane, "
            f"a.session_binding_mode, a.session_lease_mode, r.desired_connector_revision, "
            f"r.desired_checkout_revision, r.desired_deployment_lane, r.desired_session_binding_mode, "
            f"r.desired_session_lease_mode, r.generation, r.applied_generation, r.rollout_state "
            f"FROM {case.db}.{case.assignments_table} AS a "
            f"JOIN {case.db}.{case.rollouts_table} AS r ON r.cohort_id = a.cohort_id "
            f"WHERE a.cohort_id = '{case.target_cohort}'"
        )
        while time.monotonic() < deadline:
            row = _rows(self.execute("execute_sql", {"sql_query": sql}, thinking="等待目标 desired/current generation 收敛。"), "wait for rollout convergence")
            if len(row) != 1:
                raise RuntimeError(f"MF-set-autocommit target rollout query returned unexpected rows: rows={row!r}")
            current = row[0]
            if (
                current[0] == current[5]
                and current[1] == current[6]
                and current[2] == current[7]
                and current[3] == current[8]
                and current[4] == current[9] == "fixed"
                and int(current[10]) == int(current[11])
                and str(current[12]).casefold() == "applied"
            ):
                return
            time.sleep(1.0)
        raise RuntimeError(f"MF-set-autocommit target rollout did not converge within 45 seconds: sql={sql!r}")

    def solve(self) -> dict:
        available_start, available_end = self._history_runtime()
        start_timestamp, end_timestamp = self._select_history_window(available_start, available_end)
        self._read_history(start_timestamp, end_timestamp)
        self._read_current_control_plane()

        case = self.case
        repair_sql = (
            f"UPDATE {case.db}.{case.rollouts_table} SET desired_session_lease_mode='fixed', "
            f"generation=generation+1, rollout_state='pending' WHERE cohort_id='{case.target_cohort}'"
        )
        self.execute(
            "execute_sql",
            {"sql_query": repair_sql},
            thinking="只更新 cohort-d desired session lease mode，保留 lane、capacity、healthy siblings 和业务数据。",
        )
        self._wait_for_reconcile()
        self.execute(
            "manage_cluster",
            {"resource": "service", "operation": "list"},
            thinking="确认修复后 PD、TiKV、TiDB 节点健康且拓扑未变化；fresh workload 验收由可信 evaluator 完成。",
        )
        return {"report": REFERENCE_REPORT}


def main() -> None:
    parser = argparse.ArgumentParser(description=SCENARIO.description)
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--mode", choices=("mock", "llm"), default="llm")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--port", type=int, default=4700)
    parser.add_argument("--container-name", default="tidb-mf-set-autocommit-set-autocommit-frozen-history")
    parser.add_argument("--fault-snapshot-mode", choices=("off",), default="off")
    args = parser.parse_args()

    case = SCENARIO.get_case(args.case)
    env = TiDBEnv(
        run_id=os.environ.get("AIOPS_RUN_ID", args.container_name.removeprefix("aiopsbench-")),
        port_base=args.port,
        return_window_seconds=300,
    )
    agent = FrozenHistoryReferenceAgent(case) if args.mode == "mock" else build_experiment_agent(
        model=args.model,
        config_path=args.config_path,
        use_native_tools=True,
        max_output_tokens=args.max_output_tokens,
    )
    result = Orchestrator(
        env,
        SCENARIO,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
            history_seed=args.seed,
            diagnosis_match_mode="exact",
        ),
    ).run()
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
