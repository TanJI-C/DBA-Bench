import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb.business_change.runtime.pitr_checkpoint_recovery import PitrCheckpointRecoveryEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb import TidbBusinessChangePitrCheckpointRecoveryScenario


SCENARIO = TidbBusinessChangePitrCheckpointRecoveryScenario()
K08_ENABLED_TOOLS = (
    "query_metrics",
    "execute_sql",
    "manage_cluster",
    "read_log",
    "search_knowledge",
    "help",
    "submit",
    "exit",
)


def _assert_restore_log_table_rewrite(log_result, table_name: str) -> None:
    content = log_result["content"]
    rewrite_line = next(
        (
            line
            for line in content.splitlines()
            if f"[table={table_name}]" in line
            and re.search(r"\[oldID=\d+\]\s+\[newID=\d+\]", line)
        ),
        None,
    )
    if rewrite_line is None:
        raise RuntimeError(
            "K08 reference log has no raw rewrite record for the touched table: "
            f"table={table_name!r}"
        )


class PitrReferenceMockAgent(BaseAgent):
    """Exercise the reference path with TSO and cluster IDs read from the runtime."""

    def __init__(self, reference_report):
        super().__init__()
        self.reference_report = reference_report

    def solve(self):
        self.execute(
            "search_knowledge",
            {
                "query": "TiDB 8.1 BR PITR checkpoint downstream table identity ID mapping external table recreation retry",
                "source_scope": "self_managed",
                "top_k": 5,
            },
            thinking="先确认当前 BR 版本的 checkpoint 是否保存 downstream table identity/ID mapping，以及外部同形表重建对 retry 的影响。",
        )
        attempts = self.execute(
            "manage_cluster",
            {"resource": "restore", "operation": "list"},
            thinking="列出当前请求的所有 restore attempt，区分历史 attempt 与中断的 log restore。",
        )
        selected_attempt = next(
            row[0]
            for row in attempts["result"]["attempts"]
            if row[0] == SCENARIO.get_case("resume_failed_pitr_without_breaking_chain").selected_attempt_id
        )
        inspected = self.execute(
            "manage_cluster",
            {"resource": "restore", "operation": "get", "target": selected_attempt},
            thinking="把失败阶段、checkpoint、upstream/target identity、时间边界和 partial target 外部操作关联起来。",
        )
        self.execute(
            "read_log",
            {"target": "br/restore", "lines": 200},
            thinking="核对 BR 原始输出中的 checkpoint 持久化和 log restore 阶段；日志只是阶段证据，不足以证明 partial target 可 resume。",
        )
        catalog_query = (
            "SELECT COLUMN_NAME, ORDINAL_POSITION, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY "
            "FROM information_schema.columns "
            "WHERE TABLE_SCHEMA='benchops' AND TABLE_NAME='k08_orders' "
            "ORDER BY ORDINAL_POSITION"
        )
        source_catalog = self.execute(
            "execute_sql",
            {"target": "primary", "sql_query": catalog_query},
            thinking="先确认 source 的业务表定义没有漂移；source 与 target 的表名和 schema 相同并不能单独证明 checkpoint identity 仍兼容。",
        )
        target_catalog = self.execute(
            "execute_sql",
            {"target": "replica", "sql_query": catalog_query},
            thinking="对照 partial target 的业务定义；普通 columns/index/rows 相同仍不能证明 BR 保存的 downstream ID mapping 没有失效。",
        )
        identity_query = (
            "SELECT TABLE_NAME, TIDB_TABLE_ID FROM information_schema.tables "
            "WHERE TABLE_SCHEMA='benchops' AND TABLE_NAME='k08_orders'"
        )
        source_identity = self.execute(
            "execute_sql",
            {"target": "primary", "sql_query": identity_query},
            thinking="读取 source 的 TiDB table identity，建立 checkpoint rewrite 记录与 source catalog 的现场绑定。",
        )
        target_identity = self.execute(
            "execute_sql",
            {"target": "replica", "sql_query": identity_query},
            thinking="读取 partial target 的 TiDB table identity，和 BR 原始 rewrite 记录及 source catalog 共同判断 checkpoint 是否仍绑定当前 target。",
        )
        restore_log = self.execute(
            "read_log",
            {"target": "br/restore", "lines": 200, "match_key": "replace info"},
            thinking="从原始 BR 日志中定位 checkpoint 持久化前的业务表 rewrite/ID 记录；日志字段需要结合 TiDB/BR checkpoint 知识解释。",
        )
        source_map = {str(row[0]): int(row[1]) for row in source_identity["result"]}
        current_map = {str(row[0]): int(row[1]) for row in target_identity["result"]}
        _assert_restore_log_table_rewrite(
            restore_log,
            SCENARIO.get_case("resume_failed_pitr_without_breaking_chain").operator_touch_target_table,
        )
        checkpoint_map = source_map
        if source_catalog["result"] != target_catalog["result"]:
            raise RuntimeError("K08 reference path observed an unexpected business catalog drift")
        if checkpoint_map == current_map:
            raise RuntimeError(f"K08 reference path did not observe target table identity drift: checkpoint={checkpoint_map!r}, current={current_map!r}")
        self.execute(
            "manage_cluster",
            {
                "resource": "restore",
                "operation": "abandon",
                "target": selected_attempt,
            },
            thinking="checkpoint 的 upstream/time identity 虽匹配，但 target-side TIDB_TABLE_ID 已与 checkpoint map 不同；同名同 schema 同数据仍不能安全 replay ID mapping，先显式 abandon 旧 checkpoint，再使用相同 requested target 在新 isolated target clean restart。",
        )
        self.execute(
            "manage_cluster",
            {
                "resource": "restore",
                "operation": "restart",
                "target": selected_attempt,
            },
            thinking="旧 partial target 和 checkpoint 已显式 abandoned，使用相同 snapshot/log chain、requested target 和新的 isolated cluster 启动 clean restart。",
        )
        self.execute(
            "manage_cluster",
            {
                "resource": "restore",
                "operation": "wait",
                "target": selected_attempt,
            },
            thinking="等待原始 restore attempt 到达终态。",
        )
        self.execute(
            "execute_sql",
            {
                "target": "replica",
                "sql_query": (
                    "SELECT marker, COUNT(*) FROM benchops.k08_markers "
                    "WHERE marker IN ('target-window-b', 'post-target-c') "
                    "GROUP BY marker ORDER BY marker"
                ),
            },
            thinking="验证 target marker 时间边界，确认 post-target marker 没有进入 isolated target。",
        )
        self.execute(
            "execute_sql",
            {
                "target": "primary",
                "sql_query": (
                    "SELECT COUNT(*), COALESCE(SUM(order_id),0), "
                    "(SELECT COUNT(*) FROM benchops.k08_markers WHERE marker='post-target-c') "
                    "FROM benchops.k08_orders"
                ),
            },
            thinking="复核 source 业务真值和 post-target marker 未被 PITR 改写。",
        )
        self.execute(
            "execute_sql",
            {
                "target": "primary",
                "sql_query": (
                    "SELECT request_id, continuity_status, object_hash_status "
                    "FROM benchops_k08.k08_backup_requests "
                    "WHERE request_id='k08-pitr-orders-20260818'"
                ),
            },
            thinking="通过 SQL 控制面复核当前 snapshot/log continuity 和对象完整性，确认恢复没有改写 source 或 backup。",
        )
        return {"report": self.reference_report}


def main():
    parser = argparse.ArgumentParser(
        description="Run the TiDB K08 interrupted PITR/checkpoint recovery scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--port", type=int, default=5920)
    parser.add_argument("--container-name", default="aiopsbench-tidb-k08")
    args = parser.parse_args()
    case = SCENARIO.get_case(args.case)
    env = PitrCheckpointRecoveryEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        enabled_tools=K08_ENABLED_TOOLS,
    )
    if args.mode == "mock":
        agent = PitrReferenceMockAgent(case.reference_report)
    else:
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    result = Orchestrator(
        env,
        SCENARIO,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode="off"),
    ).run()
    if args.mode == "mock":
        actual = (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"])
        if actual != (True, True, True):
            raise RuntimeError(f"K08 reference mock path failed: result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
