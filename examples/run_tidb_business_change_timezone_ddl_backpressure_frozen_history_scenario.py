"""Run the frozen-history timezone-ddl scenario in reference or LLM mode."""

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
from src.scenarios.tidb import TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryScenario


SCENARIO = TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryScenario()
UTC = timezone.utc


def _success(result: dict, context: str) -> dict:
    if result.get("status") != "success":
        raise RuntimeError(f"MF-timezone-ddl reference operation failed: context={context!r}, result={result!r}")
    return result


def _utc(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)


def _stamp(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")


def _rows(result: dict, context: str) -> list:
    payload = _success(result, context)
    rows = payload.get("result")
    if not isinstance(rows, list):
        raise TypeError(f"MF-timezone-ddl reference expected SQL rows: context={context!r}, result={result!r}")
    return rows


class FrozenHistoryTimezoneDdlReferenceAgent(BaseAgent):
    """A complete reference path that discovers the historical log window."""

    def __init__(self, case) -> None:
        super().__init__()
        self.case = case

    def _find_failure(self) -> tuple[datetime, datetime]:
        help_result = _success(self.execute("help", {"tool_name": "query_metrics"}, thinking="读取历史指标可见窗口。"), "query metrics help")
        runtime = help_result["definition"]["runtime"]
        visible_start = _utc(runtime["available_start"])
        visible_end = _utc(runtime["available_end"])
        for offset in range(0, 7201, 600):
            window_end = visible_end - timedelta(seconds=offset)
            window_start = window_end - timedelta(seconds=600)
            result = _success(
                self.execute(
                    "read_log",
                    {
                        "target": "ticdc/ticdc-0",
                        "start_timestamp": _stamp(window_start),
                        "end_timestamp": _stamp(window_end),
                        "match_key": "1067",
                        "lines": 20,
                    },
                    thinking="按有限窗口回溯 TiCDC 历史记录，寻找唯一 DDL 错误而不是全局读取历史。",
                ),
                "find failed DDL history",
            )
            records = result["records"]
            if records:
                record_time = _utc(records[0]["timestamp"])
                _success(
                    self.execute(
                        "read_log",
                        {
                            "target": "ticdc/ticdc-0",
                            "start_timestamp": _stamp(record_time - timedelta(seconds=60)),
                            "end_timestamp": _stamp(record_time + timedelta(seconds=540)),
                            "match_key": "1067",
                            "lines": 20,
                        },
                        thinking="收窄到目标窗口，确认 Error 1067 与 DDL 文本。",
                    ),
                    "read failed DDL detail",
                )
                return record_time - timedelta(seconds=60), record_time + timedelta(seconds=540)
        raise RuntimeError("MF-timezone-ddl reference did not find the historical Error 1067 episode")

    def _wait_for_rows(self) -> None:
        projection = "id, amount, state, updated_at, note"
        last = None
        # sink backpressure 排空是本场景设计的一部分，收敛窗口需要覆盖
        # 断点续传后的全量追平（7200s DDL 窗口的同一量级），60 次 × 2s 不够。
        for _ in range(3600):
            status = _success(
                self.execute(
                    "manage_cluster",
                    {"resource": "changefeed", "operation": "get", "target": self.case.changefeed_id},
                    thinking="检查目标 changefeed 当前状态、checkpoint 和 resolved 进度。",
                ),
                "read recovered changefeed",
            )["result"]
            source = _rows(
                self.execute(
                    "execute_sql",
                    {"sql_query": f"SELECT {projection} FROM {self.case.source_db}.{self.case.source_table} ORDER BY id"},
                    thinking="读取上游完整业务真值。",
                ),
                "read source rows",
            )
            downstream = _rows(
                self.execute(
                    "execute_sql",
                    {"sql_query": f"SELECT {projection} FROM {self.case.source_db}.{self.case.source_table} ORDER BY id", "target": "downstream"},
                    thinking="读取下游完整业务真值并与上游比较。",
                ),
                "read downstream rows",
            )
            last = {"status": status, "source_rows": len(source), "downstream_rows": len(downstream)}
            if (
                str(status.get("state", "")).casefold() == "normal"
                and not status.get("error")
                and len(source) >= self.case.seeded_rows + self.case.post_fault_rows + 1
                and source == downstream
            ):
                return
            time.sleep(2)
        raise RuntimeError(f"MF-timezone-ddl reference did not converge: last={last!r}")

    def solve(self) -> dict:
        self.execute(
            "query_metrics",
            {"metric_type": "qps", "start_timestamp": None, "end_timestamp": None, "step_seconds": 120},
            thinking="先从历史 qps 概览定位持续窗口，再关联 TiCDC 记录。",
        )
        start, end = self._find_failure()
        self.execute(
            "execute_sql",
            {
                "target": "history",
                "sql_query": f"SELECT * FROM statement_summary WHERE event_start_utc < '{_stamp(end)}' AND event_end_utc >= '{_stamp(start)}' ORDER BY sum_latency DESC LIMIT 40",
            },
            thinking="关联目标窗口中的业务写入和 schema probe，排除报表近邻。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"SHOW CREATE TABLE {self.case.source_db}.{self.case.ddl_table}"},
            thinking="检查上游 DDL 定义。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SELECT @@session.time_zone, @@global.time_zone"},
            thinking="确认上游 DDL 的 session 时间语义。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"SHOW CREATE TABLE {self.case.source_db}.{self.case.source_table}", "target": "downstream"},
            thinking="确认下游业务表是目标 sink。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SELECT @@session.time_zone, @@global.time_zone, @@system_time_zone", "target": "downstream"},
            thinking="确认下游 +08 时间语义。",
        )
        triggers = _rows(
            self.execute(
                "execute_sql",
                {"sql_query": f"SHOW TRIGGERS FROM {self.case.source_db}", "target": "downstream"},
                thinking="比较业务表慢 trigger 与 archive 健康 trigger 的范围。",
            ),
            "read downstream triggers",
        )
        slow = [row for row in triggers if len(row) >= 4 and str(row[2]).casefold() == self.case.source_table.casefold() and "sleep(" in str(row[3]).casefold()]
        archive = [row for row in triggers if len(row) >= 4 and str(row[0]).casefold() == self.case.archive_trigger.casefold()]
        if len(slow) != 1 or len(archive) != 1:
            raise RuntimeError(f"MF-timezone-ddl reference trigger scope is unexpected: slow={slow!r}, archive={archive!r}")
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"CREATE TABLE {self.case.source_db}.{self.case.ddl_table} ("
                    "id BIGINT PRIMARY KEY, end_time TIMESTAMP NOT NULL DEFAULT '1970-01-01 08:00:01')"
                ),
                "target": "downstream",
            },
            thinking="在下游 +08 session 中创建表示同一 UTC instant 的等价 TIMESTAMP DDL。",
        )
        failed = _success(
            self.execute(
                "manage_cluster",
                {"resource": "changefeed", "operation": "get", "target": self.case.changefeed_id},
                thinking="读取失败 changefeed 的 checkpoint_tso，确认失败 DDL 的权威恢复位点。",
            ),
            "read failed changefeed checkpoint",
        )["result"]
        commit_ts = int(failed["checkpoint_tso"])
        _success(
            self.execute(
                "manage_cluster",
                {
                    "resource": "changefeed",
                    "operation": "recreate",
                    "target": self.case.changefeed_id,
                    "parameters": {"start_ts": commit_ts + 1},
                },
                thinking="从失败 DDL CommitTs 加一的位置重建同一 changefeed，保留后续 DML。",
            ),
            "recreate target changefeed",
        )
        _success(
            self.execute(
                "execute_sql",
                {"sql_query": f"DROP TRIGGER IF EXISTS {self.case.source_db}.{self.case.business_trigger}", "target": "downstream"},
                thinking="只移除已确认作用于业务表的慢 trigger，保留 archive trigger。",
            ),
            "remove business slow trigger",
        )
        self._wait_for_rows()
        return {"report": self.case.reference_report}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the TiDB frozen-history timezone-ddl scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=40)
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--container-name", default="tidb-mf-timezone-ddl")
    parser.add_argument("--diagnosis-match-mode", choices=("exact", "semantic"), default="exact")
    parser.add_argument("--diagnosis-semantic-model", default=None, help="Diagnosis judge model; defaults to --model")
    parser.add_argument("--diagnosis-semantic-config-path", default="config/llm_config.json")
    args = parser.parse_args()

    case = SCENARIO.get_case(args.case)
    env = TiDBEnv(
        run_id=os.environ.get("AIOPS_RUN_ID", args.container_name.removeprefix("aiopsbench-")),
        port_base=args.port,
        return_window_seconds=300,
    )
    if args.mode == "mock":
        agent = FrozenHistoryTimezoneDdlReferenceAgent(case)
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
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
            fault_snapshot_mode="off",
            history_seed=args.seed,
            diagnosis_match_mode=args.diagnosis_match_mode,
            diagnosis_semantic_model=args.diagnosis_semantic_model or args.model,
            diagnosis_semantic_config_path=args.diagnosis_semantic_config_path,
        ),
    ).run()
    print(json.dumps(result, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
