import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb import TidbQueryPerfStatisticsDriftFrozenHistoryScenario
from src.scenarios.tidb.query_perf.statistics_drift_frozen_history import BENIGN_COMPACTION_TABLE
from src.workloads.tidb import TiDBStatisticsDriftWorkload


SCENARIO = TidbQueryPerfStatisticsDriftFrozenHistoryScenario()


class StatisticsDriftFrozenHistoryMockAgent(BaseAgent):
    def __init__(self, case):
        super().__init__()
        self.case = case

    def solve(self):
        case = self.case
        history = self.execute(
            "query_metrics",
            {"metric_type": "statistics_state"},
            thinking="先读取冻结的 statistics_state 全窗口，定位 physical rows、statistics rows 和 modify count 的先后变化。",
        )
        window = history["window"]
        self.execute(
            "query_metrics",
            {"metric_type": "plan_cardinality"},
            thinking="把 target/control digest 的 estimated_rows、actual_rows 和 scanned_rows 与同一窗口对齐。",
        )
        self.execute(
            "query_metrics",
            {"metric_type": "query_latency"},
            thinking="确认集群 p99 的变化晚于局部 cardinality/plan 变化。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT * FROM statement_summary "
                    f"WHERE event_start_utc < '{window['available_end']}' "
                    f"AND event_end_utc >= '{window['available_start']}'"
                ),
                "target": "history",
            },
            thinking="用 TopSQL 和 digest text 对齐历史窗口，排除 control/noise 相似查询。",
        )
        self.execute(
            "read_log",
            {
                "target": "tikv/tikv-0",
                "start_timestamp": window["available_start"],
                "end_timestamp": window["available_end"],
            },
            thinking="检查 ANALYZE、load 和 compaction 的时间证据，而不是只看当前 stats。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SHOW STATS_META WHERE Db_name='{case.db}' "
                    f"AND Table_name LIKE 'mf_qp04_order_events%'"
                )
            },
            thinking="当前状态确认两张 target 的 stats 与 physical truth，区分 control/noise。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"SHOW INDEX FROM {case.db}.{case.table}"},
            thinking="确认 OR predicate 的两个单列索引仍是健康 schema 的一部分。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SHOW VARIABLES LIKE 'tidb_enable_index_merge'"},
            thinking="确认 affected session 的 IndexMerge 状态，而不是修改全局变量。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"ANALYZE TABLE {case.db}.{case.table}"},
            thinking="只刷新第一张 target shard 的统计信息。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"ANALYZE TABLE {case.db}.{case.partner_table}"},
            thinking="刷新第二张 target shard 的统计信息，保持 control/noise 不变。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SET SESSION tidb_enable_index_merge=ON"},
            thinking="只在 affected diagnostic session 恢复 IndexMerge。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"EXPLAIN ANALYZE {case.business_query}"},
            thinking="验证计划已恢复并检查 estimate/actual ratio。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": case.business_query},
            thinking="验证业务聚合结果仍与 fault baseline 一致。",
        )
        return {"report": case.reference_report}


class StatisticsDriftFrozenHistoryZeroAgent(BaseAgent):
    def solve(self):
        return {
            "report": {
                "diagnosis": {"conditions": []},
                "outcome": {"changes": [], "verification": []},
                "summary": "No diagnosis or remediation was attempted.",
            }
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the TiDB frozen-history statistics drift history investigation."
    )
    parser.add_argument(
        "--case",
        required=True,
        choices=[case.case_id for case in SCENARIO.cases],
    )
    parser.add_argument("--mode", choices=("mock", "zero", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=28)
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--port", type=int, default=26920)
    parser.add_argument("--container-name", default="tidb-mf-qp02-statistics-drift")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument(
        "--diagnosis-match-mode",
        choices=("exact", "semantic"),
        default=os.environ.get("AIOPS_DP_MATCH_MODE", "exact"),
    )
    parser.add_argument("--diagnosis-semantic-model")
    parser.add_argument("--diagnosis-semantic-config")
    args = parser.parse_args()

    case = SCENARIO.get_case(args.case)
    workload = TiDBStatisticsDriftWorkload(
        database=case.db,
        tables=(
            case.table,
            case.partner_table,
            case.control_table,
            case.control_partner_table,
            case.noise_table,
            case.noise_partner_table,
        ),
        index_name=case.index_name,
        status_index_name=case.status_index_name,
        target_value=case.target_value,
        status_value=case.status_value,
        initial_rows=case.initial_rows,
        initial_target_rows=case.initial_target_rows,
        maintenance_table=BENIGN_COMPACTION_TABLE,
        maintenance_rows=20_000,
    )
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        workload=workload,
        port_base=args.port,
        return_window_seconds=300,
    )
    if args.mode == "mock":
        agent = StatisticsDriftFrozenHistoryMockAgent(case)
        diagnosis_match_mode = "exact"
    elif args.mode == "zero":
        agent = StatisticsDriftFrozenHistoryZeroAgent()
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
        actual = (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"])
        expected = (True, True, True)
        if actual != expected:
            raise RuntimeError(
                f"frozen-history QP02 mock path failed: expected={expected}, actual={actual}, result={json.dumps(result, ensure_ascii=False, default=str)}"
            )
    print(f"Final result: {json.dumps(result, ensure_ascii=False, default=str)}")


if __name__ == "__main__":
    main()
