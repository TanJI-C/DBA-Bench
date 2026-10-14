from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb import TidbSystemFailureTableCacheLeaseFrozenHistoryScenario
from src.scenarios.tidb.system_failure.table_cache_lease_frozen_history import _REFERENCE_REPORT


SCENARIO = TidbSystemFailureTableCacheLeaseFrozenHistoryScenario()
REFERENCE_REPORT = _REFERENCE_REPORT
UTC = timezone.utc
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


class TableCacheLeaseTiDBEnv(TiDBEnv):
    FROZEN_HISTORY_PUBLIC_TOOLS = tuple(
        tool for tool in TiDBEnv.FROZEN_HISTORY_PUBLIC_TOOLS if tool != "search_knowledge"
    )


def _mapping(result: object, context: str) -> dict:
    if not isinstance(result, dict) or result.get("status") != "success":
        raise RuntimeError(f"table-cache-lease reference {context} failed: result={result!r}")
    return result


def _series_timestamps(value: object) -> list:
    """Overview grids above 512 points render timestamps as {start,end,step,count}."""
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        start = datetime.strptime(str(value["start"]), TIMESTAMP_FORMAT).replace(tzinfo=UTC)
        step = timedelta(seconds=int(value["step_seconds"]))
        return [(start + step * index).strftime(TIMESTAMP_FORMAT) for index in range(int(value["count"]))]
    raise TypeError(f"table-cache-lease reference overview timestamps are neither a list nor a grid: timestamps={value!r}")


class FrozenHistoryReferenceAgent(BaseAgent):
    """Structured reference path for the frozen-history Case; it derives the records window from metrics."""

    def __init__(self, case) -> None:
        super().__init__()
        self.case = case

    def solve(self) -> dict:
        help_result = _mapping(
            self.execute("help", {"tool_name": "query_metrics"}, thinking="Read the historical UTC range and query budget first."),
            "history help",
        )
        runtime = help_result["definition"]["runtime"]
        available_start = datetime.strptime(runtime["available_start"], TIMESTAMP_FORMAT).replace(tzinfo=UTC)
        available_end = datetime.strptime(runtime["available_end"], TIMESTAMP_FORMAT).replace(tzinfo=UTC)

        latency = _mapping(
            self.execute(
                "query_metrics",
                # The no-window overview compacts to the newest 20 points by
                # default; request the full 12-hour 60s grid so candidate
                # peak selection sees the entire history.
                {"metric_type": "query_latency", "limit": 720},
                thinking="Locate a candidate window in the 12-hour query-latency overview before reading records.",
            ),
            "query latency overview",
        )
        series = latency["series"]["cluster"]
        series["timestamps"] = _series_timestamps(series["timestamps"])
        qps = _mapping(
            self.execute(
                "query_metrics",
                {"metric_type": "qps", "limit": 720},
                thinking="Compare query-rate changes with latency candidates before selecting the historical window.",
            ),
            "qps overview",
        )
        qps_series = qps["series"]["cluster"]
        qps_series["timestamps"] = _series_timestamps(qps_series["timestamps"])
        candidate_windows = []
        seen_windows = set()
        candidate_series = (
            (series, "p99_ms", 5),
            (series, "p95_ms", 5),
            (series, "average_ms", 5),
            (qps_series, "queries_per_second", 10),
        )
        for metric_series, field, candidate_count in candidate_series:
            values = metric_series[field]
            for peak_index in sorted(range(len(values)), key=values.__getitem__, reverse=True)[:candidate_count]:
                peak_time = datetime.strptime(metric_series["timestamps"][peak_index], TIMESTAMP_FORMAT).replace(tzinfo=UTC)
                window_start = max(available_start, peak_time - timedelta(seconds=240))
                window_end = min(available_end, window_start + timedelta(seconds=480))
                if (window_end - window_start).total_seconds() < 120:
                    raise RuntimeError(
                        "table-cache-lease reference candidate history window is too short: "
                        f"start={window_start!r}, end={window_end!r}, peak={peak_time!r}, metric_field={field!r}"
                    )
                window_key = (window_start, window_end)
                if window_key not in seen_windows:
                    seen_windows.add(window_key)
                    candidate_windows.append(window_key)

        selected_window = None
        for window_start, window_end in candidate_windows:
            start_text = window_start.strftime(TIMESTAMP_FORMAT)
            end_text = window_end.strftime(TIMESTAMP_FORMAT)
            for probe_target in ("tidb/tidb-0", "tidb/tidb-1"):
                probe = _mapping(
                    self.execute(
                        "read_log",
                        {"target": probe_target, "start_timestamp": start_text, "end_timestamp": end_text, "match_key": "Write conflict", "lines": 120},
                        thinking="Validate each metric candidate with same-window 9007 write-conflict evidence before choosing the investigation window.",
                    ),
                    f"candidate component history probe: target={probe_target}, start={start_text}, end={end_text}",
                )
                if probe.get("content"):
                    selected_window = (start_text, end_text)
                    break
            if selected_window is not None:
                break
        if selected_window is None:
            raise RuntimeError(
                "table-cache-lease reference found no metric candidate with same-window table-cache metadata evidence: "
                f"candidate_count={len(candidate_windows)}"
            )
        start_text, end_text = selected_window

        for source in ("component_log", "topsql", "slow_queries"):
            api = "read_log" if source == "component_log" else "execute_sql"
            if source == "component_log":
                args = {"target": "tidb/tidb-0", "start_timestamp": start_text, "end_timestamp": end_text, "lines": 120}
            else:
                table = "statement_summary" if source == "topsql" else "slow_query"
                predicate = f"event_start_utc < '{end_text}' AND event_end_utc >= '{start_text}'" if source == "topsql" else f"event_time_utc >= '{start_text}' AND event_time_utc < '{end_text}'"
                args = {"target": "history", "sql_query": f"SELECT * FROM {table} WHERE {predicate} LIMIT 120"}
            _mapping(
                self.execute(
                    api,
                    args,
                    thinking=f"Query {source} in the same UTC window and preserve source and event order.",
                ),
                f"{source} history query",
            )
        _mapping(
            self.execute(
                "execute_sql",
                {"sql_query": "SELECT tid, lock_type, lease, oldReadLease FROM mysql.table_cache_meta"},
                thinking="Map historical internal keys to current metadata rows without treating static rows as history.",
            ),
            "cache metadata query",
        )
        for table in (
            self.case.cache_table,
            self.case.inventory_table,
            self.case.pricing_table,
            self.case.healthy_cache_table_names[0],
        ):
            _mapping(
                self.execute(
                    "execute_sql",
                    {"sql_query": f"SHOW CREATE TABLE {self.case.db}.{table}"},
                    thinking="Compare current cache markers for causal tables and the same-domain auxiliary table.",
                ),
                f"cache marker query: table={table}",
            )
        _mapping(
            self.execute(
                "execute_sql",
                {"sql_query": "SHOW GLOBAL VARIABLES LIKE 'tidb_table_cache_lease'"},
                thinking="Read the current lease setting and confirm that the latent risk condition remains.",
            ),
            "lease variable query",
        )
        for table in self.case.cache_table_names:
            _mapping(
                self.execute(
                    "execute_sql",
                    {
                        "sql_query": (
                            "SELECT TIDB_TABLE_ID FROM information_schema.tables "
                            f"WHERE TABLE_SCHEMA = '{self.case.db}' AND TABLE_NAME = '{table}'"
                        )
                    },
                    thinking="Map historical table IDs to current schema objects and bound the repair scope.",
                ),
                f"table ID query: table={table}",
            )
        for table in self.case.cache_table_names:
            _mapping(
                self.execute(
                    "execute_sql",
                    {"sql_query": f"ALTER TABLE {self.case.db}.{table} NOCACHE"},
                    thinking="Remove only the three evidence-backed causal cache markers and preserve the auxiliary cache.",
                ),
                f"causal NOCACHE: table={table}",
            )
        return {"report": REFERENCE_REPORT}


def main() -> None:
    parser = argparse.ArgumentParser(description=SCENARIO.description)
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=18)
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--port", type=int, default=4300)
    parser.add_argument("--container-name", default="tidb-table-cache-frozen-history")
    parser.add_argument("--seed", type=int, default=5501)
    args = parser.parse_args()

    case = SCENARIO.get_case(args.case)
    env = TableCacheLeaseTiDBEnv(run_id=args.container_name, port_base=args.port, return_window_seconds=300)
    if args.mode == "mock":
        agent = FrozenHistoryReferenceAgent(case)
    else:
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
        ),
    ).run()
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
