import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbHealthCheckTiCdcReplicationTrendScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


SCENARIO = TidbHealthCheckTiCdcReplicationTrendScenario()


def _rows(result: dict, context: str) -> list:
    if result.get("status") != "success":
        raise RuntimeError(f"HC05 mock {context} failed: result={result!r}")
    rows = result.get("result")
    if not isinstance(rows, list):
        raise TypeError(f"HC05 mock {context} returned invalid rows: result={result!r}")
    return rows


class HC05FullMockAgent(BaseAgent):
    """Deterministic full-path agent using live evidence and terminal verification."""

    def __init__(self, case):
        super().__init__()
        self.case = case

    def solve(self):
        case = self.case
        self.execute(
            "query_metrics",
            {"metric_type": "qps"},
            thinking="先确认当前 TiDB 查询/业务负载仍在运行，避免用停业务掩盖复制延迟。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT observed_at, changefeed_id, state, checkpoint_lag_seconds, "
                    "source_transaction_rows, sink_transaction_rows, downstream_index_count, "
                    "lag_slope_seconds_per_minute FROM benchops.hc05_replication_observations "
                    "ORDER BY observed_at DESC LIMIT 16"
                )
            },
            thinking="读取原始复制 observation；统一 TiDB 工具面不把复制快照注册为通用 metric。",
        )
        self.execute(
            "manage_cluster",
            {"resource": "changefeed", "operation": "get", "target": case.changefeed_id},
            thinking="读取当前 changefeed 状态、TSO、lag 和原始 execution config。",
        )
        if case.case_id == "ticdc_replication_capacity_review":
            self.execute(
                "manage_cluster",
                {"resource": "changefeed", "operation": "pause", "target": case.changefeed_id},
                thinking="TiCDC 8.1 只允许在暂停状态修改 sink execution config；短暂停止当前 changefeed，不停止业务流量。",
            )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT history_id, changefeed_id, observed_at, checkpoint_lag_seconds, "
                    "sink_rows_per_second, source_qps, source_transaction_rows, "
                    "sink_transaction_rows, downstream_index_count, sink_max_txn_row, "
                    "lag_slope_seconds_per_minute FROM benchops.hc05_capacity_history "
                    "ORDER BY history_id DESC LIMIT 32"
                )
            },
            thinking="用交错的长期 stream 样本区分一次 burst，并比较 target 与 sibling 的原始执行形状。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SHOW INDEX FROM benchops.hc05_event_log"
                ),
                "target": "downstream",
            },
            thinking="读取下游真实 catalog，确认业务表上的完整 index path，不修改受保护对象。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT table_name, row_count, id_checksum FROM ("
                    "SELECT 'orders' AS table_name, COUNT(*) AS row_count, COALESCE(SUM(order_id), 0) AS id_checksum "
                    "FROM benchops.hc05_orders UNION ALL "
                    "SELECT 'payments', COUNT(*), COALESCE(SUM(payment_id), 0) "
                    "FROM benchops.hc05_payments UNION ALL "
                    "SELECT 'inventory', COUNT(*), COALESCE(SUM(sku_id), 0) "
                    "FROM benchops.hc05_inventory UNION ALL "
                    "SELECT 'events', COUNT(*), COALESCE(SUM(event_id), 0) "
                    "FROM benchops.hc05_event_log) AS business_summary ORDER BY table_name"
                )
            },
            thinking="把业务真值和复制状态分开核对，排除下游数据损坏。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT state, checkpoint_lag_seconds, error_count, source_event_rows, replica_event_rows "
                    f"FROM {case.db}.{case.observation_table} ORDER BY observation_id DESC LIMIT 1"
                )
            },
            thinking="读取当前可审计的复制观测，确认状态与业务水位。",
        )
        self.execute(
            "manage_cluster",
            {"resource": "service", "operation": "get", "target": "ticdc/ticdc-0"},
            thinking="确认复制组件的当前资源配置，并与吞吐和 checkpoint 趋势交叉核对。",
        )
        self.execute(
            "manage_cluster",
            {"resource": "service", "operation": "get", "target": "downstream/mysql-0"},
            thinking="确认下游 sink 的可逆资源限制也在授权边界内。",
        )
        if case.case_id == "ticdc_replication_capacity_review":
            self.execute(
                "manage_cluster",
                {
                    "resource": "changefeed",
                    "operation": "update",
                    "target": case.changefeed_id,
                    "parameters": {
                        "max_txn_row": case.source_batch_rows,
                        "worker_count": 8,
                        "batch_dml_enable": True,
                    },
                },
                thinking="先修正已观察到的 transaction shape，保留下游业务索引，再用持续窗口验证。",
            )
            self.execute(
                "manage_cluster",
                {"resource": "changefeed", "operation": "resume", "target": case.changefeed_id},
                thinking="恢复当前 changefeed，让新的 execution config 在持续业务流量下生效。",
            )
            self.execute(
                "manage_cluster",
                {
                    "resource": "service",
                    "operation": "resize",
                    "target": "ticdc/ticdc-0",
                    "parameters": {"cpu_limit": case.max_authorized_sink_cpu},
                },
                thinking="在授权边界内把复制组件扩到允许上限，不停止业务、不重启数据库组件。",
            )
        self.execute(
            "manage_cluster",
            {
                "resource": "service",
                "operation": "resize",
                "target": "downstream/mysql-0",
                "parameters": {"cpu_limit": case.max_authorized_downstream_cpu},
            },
            thinking="在授权边界内恢复下游 sink 资源，不停止业务、不改写业务数据。",
        )
        deadline = time.monotonic() + 240
        snapshot = None
        healthy_samples = 0
        required_healthy_samples = case.convergence_samples
        while time.monotonic() < deadline:
            rows = _rows(
                self.execute(
                    "execute_sql",
                    {
                        "sql_query": (
                            f"SELECT state, checkpoint_lag_seconds, error_count, source_event_rows, replica_event_rows "
                            f"FROM {case.db}.{case.observation_table} ORDER BY observation_id DESC LIMIT 1"
                        )
                    },
                    thinking="等待审计观测在持续写入下收敛，并检查 feed 没有 error。",
                ),
                "current replication observation",
            )
            if len(rows) != 1 or len(rows[0]) != 5:
                raise RuntimeError(f"HC05 mock current replication observation has invalid shape: rows={rows!r}")
            state, lag_seconds, error_count, source_rows, replica_rows = rows[0]
            snapshot = {
                "state": str(state),
                "lag_seconds": float(lag_seconds),
                "error_count": int(error_count),
                "source_event_rows": int(source_rows),
                "replica_event_rows": int(replica_rows),
            }
            if (
                snapshot["state"] in {"normal", "running"}
                and snapshot["error_count"] == 0
                and float(snapshot["lag_seconds"]) <= case.max_lag_slo_seconds
            ):
                healthy_samples += 1
                if healthy_samples == required_healthy_samples:
                    break
            else:
                healthy_samples = 0
            time.sleep(case.convergence_interval_seconds)
        else:
            raise RuntimeError(f"HC05 mock did not converge: snapshot={snapshot!r}")

        return {"report": case.reference_report}


class HC05ZeroAgent(BaseAgent):
    """Calibration agent that observes nothing and leaves the fault untouched."""

    def solve(self):
        return {
            "report": {
                "diagnosis": {"conditions": []},
                "outcome": {"changes": [], "verification": []},
                "summary": "No remediation was attempted.",
            }
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the TiDB HC05 TiCDC replication trend scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "zero", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--port", type=int, default=26800)
    parser.add_argument("--container-name", default="tidb-hc05-ticdc-rewrite")
    parser.add_argument(
        "--diagnosis-match-mode",
        choices=("exact", "semantic"),
        default=os.environ.get("AIOPS_DP_MATCH_MODE", "exact"),
    )
    parser.add_argument("--diagnosis-semantic-model")
    parser.add_argument("--diagnosis-semantic-config-path")
    args = parser.parse_args()

    diagnosis_semantic_model = (
        args.diagnosis_semantic_model
        or os.environ.get("AIOPS_DP_SEMANTIC_MODEL")
        or args.model
    )
    diagnosis_semantic_config_path = (
        args.diagnosis_semantic_config_path
        or os.environ.get("AIOPS_DP_SEMANTIC_CONFIG")
        or "config/llm_config.json"
    )

    case = SCENARIO.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = HC05FullMockAgent(case)
        diagnosis_match_mode = "exact"
    elif args.mode == "zero":
        agent = HC05ZeroAgent()
        diagnosis_match_mode = "exact"
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
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
            diagnosis_match_mode=diagnosis_match_mode,
            diagnosis_semantic_model=diagnosis_semantic_model,
            diagnosis_semantic_config_path=diagnosis_semantic_config_path,
        ),
    ).run()
    if args.mode == "mock":
        expected = (True, True, True)
        actual = (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"])
        if actual != expected:
            raise RuntimeError(f"HC05 mock path failed: expected={expected}, actual={actual}, result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
