import argparse
import time
from datetime import datetime, timedelta

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import StructuredReport
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb.resource_governance.br_slo_frozen_history import (
    TidbResourceGovernanceBrSloAdaptiveThrottlingFrozenHistoryScenario,
)


PASS_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "temporal_cause",
                "factor": "BR progress rises before TiKV shared I/O and CPU saturation, then historical checkout p99 crosses 35 ms; the live controller guard uses checkout p95 > 35 ms",
                "entity": "target historical window",
                "evidence": ["the historical sequence is BR progress, shared TiKV pressure, then checkout SLO breach"],
            },
            {
                "type": "target_identity",
                "factor": "the paused run-scoped BR job and storage path are the target historical episode",
                "entity": "the current PAUSED_FOR_REVIEW job",
                "evidence": ["the current job and controller storage path match the target episode"],
            },
            {
                "type": "root_cause",
                "factor": "BR maintenance and foreground checkout share TiKV disk, network, and CPU resources",
                "entity": "tikv/tikv-0, tikv/tikv-1, tikv/tikv-2",
                "evidence": ["all TiKV resource series rise with BR activity while checkout demand does not rise first"],
            },
            {
                "type": "root_cause",
                "factor": "backup auto-tune is disabled and the maintenance budget is too strong for the foreground SLO",
                "entity": "TiKV backup configuration and the target BR job",
                "evidence": ["SHOW CONFIG reports auto-tune=false at the target episode"],
            },
            {
                "type": "exclusion",
                "factor": "OLAP burst, compaction, off-peak small backup, and checkout QPS flash are excluded by timing or healthy SLO",
                "entity": "historical decoy windows",
                "evidence": ["the competing windows do not have the target BR identity and causal order"],
            },
        ]
    },
    "outcome": {
        "changes": ["enabled the bounded TiKV backup budget and resumed the existing BR job through its controller"],
        "verification": [
            "the same run-scoped job completed all ranges with checksum 100%",
            "the original artifact and checkout SLO are healthy",
            "the orders business truth is unchanged",
        ],
    },
    "summary": "The historical BR resource incident was identified and the existing job was safely continued without changing business data.",
}
StructuredReport.from_mapping(PASS_REPORT)


def _target_history_window(latency_history, history_help, case):
    if latency_history.get("status") != "success":
        raise RuntimeError(
            "Frozen-history mock cannot locate target history from query_latency: "
            f"observation={latency_history!r}"
        )
    latency_window = latency_history["window"]
    series = latency_history["series"]["cluster"]
    p99_values = series["p99_ms"]
    timestamps = series["timestamps"]
    if not p99_values:
        raise RuntimeError("Frozen-history mock cannot locate target history: cluster.p99_ms is empty")
    if not isinstance(timestamps, dict):
        raise RuntimeError(
            "Frozen-history mock query_latency history must use the frozen UTC grid form: "
            f"timestamps_type={type(timestamps).__name__}"
        )
    timestamp_count = int(timestamps["count"])
    if timestamp_count != len(p99_values):
        raise RuntimeError(
            "Frozen-history mock query_latency timestamp count differs from p99 values: "
            f"timestamp_count={timestamp_count}, p99_count={len(p99_values)}"
        )
    step_seconds = int(timestamps["step_seconds"])
    expected_step = int(case.frozen_history.base_step_seconds)
    if step_seconds != expected_step:
        raise RuntimeError(
            "Frozen-history mock query_latency history step differs from the Case contract: "
            f"step_seconds={step_seconds}, expected={expected_step}"
        )
    timestamp_start = datetime.strptime(timestamps["start"], "%Y-%m-%d %H:%M:%S")
    peak_index = min(range(len(p99_values)), key=lambda index: (-p99_values[index], index))
    target_start = timestamp_start + timedelta(seconds=peak_index * step_seconds)
    target_start -= timedelta(seconds=step_seconds)
    target_end = target_start + timedelta(seconds=case.frozen_history.fault_capture_seconds)
    available_start = datetime.strptime(latency_window["available_start"], "%Y-%m-%d %H:%M:%S")
    available_end = datetime.strptime(latency_window["available_end"], "%Y-%m-%d %H:%M:%S")
    help_available_start = datetime.strptime(
        history_help["definition"]["runtime"]["available_start"], "%Y-%m-%d %H:%M:%S"
    )
    help_available_end = datetime.strptime(
        history_help["definition"]["runtime"]["available_end"], "%Y-%m-%d %H:%M:%S"
    )
    if (available_start, available_end) != (help_available_start, help_available_end):
        raise RuntimeError(
            "Frozen-history mock query tools disagree on the public history range: "
            f"query_metrics=({available_start!r}, {available_end!r}), "
            f"execute_sql(history)=({help_available_start!r}, {help_available_end!r})"
        )
    if target_start < available_start or target_end > available_end:
        raise RuntimeError(
            "Frozen-history mock p99 peak does not identify a complete bounded target window: "
            f"target=({target_start!r}, {target_end!r}), available=({available_start!r}, {available_end!r})"
        )
    return {
        "start_timestamp": target_start.strftime("%Y-%m-%d %H:%M:%S"),
        "end_timestamp": target_end.strftime("%Y-%m-%d %H:%M:%S"),
    }


class BrSloFrozenHistoryMockAgent(BaseAgent):
    def __init__(self, case):
        super().__init__()
        self.case = case

    def solve(self):
        latency_observation = self.execute(
            "query_metrics",
            {"metric_type": "query_latency", "target": None},
            thinking="先读取冻结历史的前台延迟，确认当前快照已经恢复不代表历史没有事故。",
        )
        metric_observations = (
            ("query_latency", latency_observation),
            (
                "disk_io",
                self.execute(
                    "query_metrics",
                    {"metric_type": "disk_io", "target": "tikv/tikv-0"},
                    thinking="把 TiKV I/O 与 BR/checkout 的时间顺序结合，而不是只看当前 p95。",
                ),
            ),
            (
                "cpu",
                self.execute(
                    "query_metrics",
                    {"metric_type": "cpu", "target": "tikv/tikv-0"},
                    thinking="检查 TiKV CPU 是否和 BR 进度同步上升，排除只看磁盘的单一解释。",
                ),
            ),
            (
                "network_io",
                self.execute(
                    "query_metrics",
                    {"metric_type": "network_io", "target": "tikv/tikv-0"},
                    thinking="检查共享网络路径是否也参与资源竞争，而不是把 I/O 当成唯一证据。",
                ),
            ),
            (
                "qps",
                self.execute(
                    "query_metrics",
                    {"metric_type": "qps", "target": None},
                    thinking="对照 checkout 需求曲线，确认延迟上升不是业务 QPS 先增加造成的。",
                ),
            ),
        )
        for metric, observation in metric_observations:
            if observation.get("status") != "success":
                raise RuntimeError(
                    "Frozen-history mock metric observation failed: "
                    f"metric={metric!r}, observation={observation!r}"
                )
        history_help = self.execute(
            "help",
            {"tool_name": "execute_sql"},
            thinking="先读取 SQL 连接面的 UTC 窗口和查询预算。",
        )
        overview_window = latency_observation["window"]
        latency_history = self.execute(
            "query_metrics",
            {
                "metric_type": "query_latency",
                "target": None,
                "start_timestamp": overview_window["available_start"],
                "end_timestamp": overview_window["available_end"],
            },
            thinking="用显式窗口在基础步长网格上读取完整冻结历史，定位 p99 峰值。",
        )
        target_window = _target_history_window(latency_history, history_help, self.case)
        component_history = self.execute(
            "read_log",
            {"target": "tikv/tikv-0", **target_window, "lines": 20},
            thinking="读取 p99 峰值对应的冻结日志窗口，确认组件证据。",
        )
        if component_history["status"] != "success":
            raise RuntimeError(
                "Frozen-history mock target history query failed: "
                f"component_log={component_history!r}"
            )
        jobs = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT job_id, state, total_ranges, ranges_succeeded, ranges_failed, checksum_status, storage_path "
                    f"FROM {self.case.database}.{self.case.job_table} "
                    "WHERE state='PAUSED_FOR_REVIEW' ORDER BY started_at DESC, job_id DESC"
                )
            },
            thinking="只从当前状态找正在 review 的目标 job，排除历史成功/失败维护记录。",
        )
        rows = jobs["result"]
        if len(rows) != 1:
            raise RuntimeError(f"Frozen-history mock expected one paused target job: rows={rows!r}")
        job_id = str(rows[0][0])
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SHOW CONFIG WHERE type='tikv' "
                    "AND name IN ('backup.enable-auto-tune', 'backup.num-threads')"
                )
            },
            thinking="确认所有 TiKV 的初始 backup budget 与 auto-tune 状态。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SET CONFIG tikv `backup.enable-auto-tune` = 'true'"},
            thinking="恢复官方 auto-tune 保护，避免用禁用保护换取维护吞吐。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SET CONFIG tikv `backup.num-threads` = '1'"},
            thinking="把 maintenance threads 收敛到公开的 1..2 安全预算。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"UPDATE {self.case.database}.{self.case.controller_table} "
                    "SET requested_action='RESUME' "
                    f"WHERE job_id='{job_id}' AND controller_state='PAUSED_FOR_REVIEW'"
                )
            },
            thinking="通过公开 controller 请求继续同一个 paused job，不启动新 job。",
        )
        deadline = time.monotonic() + 420
        while time.monotonic() < deadline:
            status = self.execute(
                "execute_sql",
                {
                    "sql_query": (
                        f"SELECT state, total_ranges, ranges_succeeded, ranges_failed, checksum_status "
                        f"FROM {self.case.database}.{self.case.job_table} WHERE job_id='{job_id}'"
                    )
                },
                thinking="等待真实 BR 进程继续推进并验证 range/checksum，而不是只相信 controller 返回。",
            )
            if status.get("status") != "success":
                # The BR controller rewrites the job row while the resume is
                # in flight; an unconclusive read sample is retried within the
                # same deadline instead of aborting the diagnosis.
                time.sleep(4)
                continue
            state, total, succeeded, failed, checksum = status["result"][0]
            if str(state).upper() == "SUCCEEDED":
                if int(total) <= 0 or int(succeeded) != int(total) or int(failed) != 0 or str(checksum) != "100%":
                    raise RuntimeError(f"Frozen-history mock observed invalid completed job: row={status['result'][0]!r}")
                time.sleep(30)
                break
            if str(state).upper() == "FAILED":
                raise RuntimeError(f"Frozen-history mock observed failed job: row={status['result'][0]!r}")
            time.sleep(4)
        else:
            raise RuntimeError(f"Frozen-history mock target job did not finish: job_id={job_id!r}")
        self.execute(
            "execute_sql",
            {"sql_query": self.case.business_query},
            thinking="用 orders 真值确认 BR 治理没有修改业务数据。",
        )
        return {"report": PASS_REPORT}


def _build_environment(args):
    if (args.storage_key is None) != (args.storage_root is None):
        raise ValueError("--storage-key and --storage-root must be supplied together")
    return TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=300,
        storage_key=args.storage_key,
        storage_root=args.storage_root,
        tidb_readiness_timeout_sec=args.cold_start_timeout,
        warm_tidb_readiness_timeout_sec=args.warm_start_timeout,
    )


def main():
    scenario = TidbResourceGovernanceBrSloAdaptiveThrottlingFrozenHistoryScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB BR SLO frozen history calibration Case.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=42)
    parser.add_argument("--seed", type=int, default=20260816)
    parser.add_argument("--port", type=int, default=19100)
    parser.add_argument("--container-name", default="tidb-mf-rg03")
    parser.add_argument("--fault-snapshot-mode", choices=("off",), default="off")
    parser.add_argument("--storage-key")
    parser.add_argument("--storage-root")
    parser.add_argument("--cold-start-timeout", type=int, default=900)
    parser.add_argument("--warm-start-timeout", type=int, default=300)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = _build_environment(args)
    if args.mode == "mock":
        agent = BrSloFrozenHistoryMockAgent(case)
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
            history_seed=args.seed,
        ),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (True, True, True):
            raise RuntimeError(f"Frozen-history mock must pass True/True/True, observed={observed!r}, result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
