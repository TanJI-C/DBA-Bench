import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.evaluation.config import add_diagnosis_arguments
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb.system_failure.pending_offline import (
    SF07_GLOBAL_SCOPE_TABLE,
    SF07_SCHEDULE_BASELINE,
    TidbSystemFailurePendingOfflineScenario,
)
from src.scenarios.evaluation.tidb.system_failure.pending_offline import (
    ONLINE_UNSAFE_DP_FACTORS,
)


SCENARIO = TidbSystemFailurePendingOfflineScenario()


def _condition(factor: str, entity: str, evidence: list[str]) -> dict:
    return {
        "type": "finding",
        "factor": factor,
        "entity": entity,
        "evidence": evidence,
    }


def build_report(
    case,
    failed_store_ids: tuple[int, ...],
    affected_region_ids: tuple[int, ...],
    affected_table_id: int,
    affected_index_ids: tuple[int, ...],
    global_scope_region_ids: tuple[int, ...],
    pre_fault_tso: int,
) -> dict:
    failed = ", ".join(str(store_id) for store_id in failed_store_ids)
    regions = ", ".join(str(region_id) for region_id in affected_region_ids)
    global_regions = ", ".join(str(region_id) for region_id in global_scope_region_ids)
    return {
        "report": {
            "diagnosis": {
                "conditions": [
                    _condition(
                        ONLINE_UNSAFE_DP_FACTORS[0],
                        f"{case.db}.{case.table}; regions=[{regions}]",
                        [f"affected Regions lost two of three peers; failed_store_ids=[{failed}]"],
                    ),
                    _condition(
                        ONLINE_UNSAFE_DP_FACTORS[1],
                        "PD/TiDB/TiKV v8.1 Online Unsafe Recovery",
                        ["cluster release and official Online Unsafe Recovery documentation"],
                    ),
                    _condition(
                        ONLINE_UNSAFE_DP_FACTORS[2],
                        f"failed_store_ids=[{failed}]",
                        [
                            "the request used every permanently failed Store observed in Store and peer evidence",
                            f"same-incident recovery-scope Regions were mapped: [{global_regions}]",
                        ],
                    ),
                    _condition(
                        ONLINE_UNSAFE_DP_FACTORS[3],
                        "PD global recovery task",
                        ["accepted registration was followed by polling until Unsafe recovery finished"],
                    ),
                    _condition(
                        ONLINE_UNSAFE_DP_FACTORS[4],
                        f"table_id={affected_table_id}; index_ids={list(affected_index_ids)!r}",
                        [f"record and index Region scope was mapped from Region metadata: regions=[{regions}]"],
                    ),
                    _condition(
                        ONLINE_UNSAFE_DP_FACTORS[5],
                        f"pre_fault_tso={pre_fault_tso}",
                        ["the report separates the last confirmed boundary from the unconfirmed write window"],
                    ),
                ]
            },
            "outcome": {
                "changes": [
                    f"submitted one Online Unsafe Recovery request for failed_store_ids=[{failed}]",
                    "waited for the PD task to reach Unsafe recovery finished",
                    "restored the captured PD scheduling values after the terminal state",
                    f"inserted the authorized canary order {case.new_write_id} after recovery",
                ],
                "verification": [
                    "checkout record/index and sf07_payments recovery-scope Regions have a leader and three normal peers",
                    "the failed Stores have no residual peers and are terminal",
                    "ADMIN CHECK TABLE and the business truth query pass",
                    "the healthy reconciliation table remains unchanged",
                ],
                "plan": {
                    "last_confirmed_boundary": (
                        f"@@tidb_current_ts={pre_fault_tso}; pre-fault truth was captured before the Store failures"
                    ),
                    "unconfirmed_write_window": (
                        "writes after the last confirmed boundary and before terminal recovery remain unconfirmed; "
                        "they were not claimed as committed"
                    ),
                    "observed_rpo": (
                        "Online Unsafe Recovery is lossy; only the post-recovery truth and the authorized canary "
                        "were verified"
                    ),
                },
            },
            "summary": (
                "The two-of-three peer loss and the same-incident global recovery scope were recovered with v8.1 "
                "Online Unsafe Recovery, with the complete failed Store set, terminal task state, and RPO boundary audited."
            ),
        }
    }


class PendingOfflineFullMockAgent(MockLLMAgent):
    """Reference path for the complete Online Unsafe Recovery contract."""

    def __init__(self, case, **kwargs):
        super().__init__(**kwargs)
        self.case = case

    @staticmethod
    def _state_name(item: dict) -> str:
        return str(item["store"]["state_name"]).casefold()

    @staticmethod
    def _store_ids_for_nodes(stores: list[dict], nodes: tuple[str, ...]) -> tuple[int, ...]:
        by_node = {}
        for item in stores:
            service = str(item["store"]["address"]).split(":", 1)[0]
            node = f"tikv/{service}"
            if node in by_node:
                raise RuntimeError(f"SF07 reference found duplicate Store mapping: node={node!r}")
            by_node[node] = int(item["store"]["id"])
        missing = [node for node in nodes if node not in by_node]
        if missing:
            raise RuntimeError(
                f"SF07 reference could not map configured TiKV nodes: missing={missing!r}, observed={sorted(by_node)!r}"
            )
        return tuple(sorted(by_node[node] for node in nodes))

    @staticmethod
    def _recovery_text(response: dict) -> str:
        result = response.get("result", {})
        output = result.get("output") if isinstance(result, dict) else result
        return json.dumps(output, ensure_ascii=False, default=str).casefold()

    def solve(self):
        stores_response = self.execute(
            "manage_cluster",
            {"resource": "store", "operation": "list"},
            thinking="先从 Store 状态和 Region peer 证据确定永久失败集合，不把第一个报错 Store 当成完整答案。",
        )
        stores = stores_response["result"]["stores"]
        failed_store_ids = self._store_ids_for_nodes(stores, self.case.failed_nodes)
        healthy_store_ids = self._store_ids_for_nodes(stores, self.case.healthy_nodes)
        maintenance_store_ids = self._store_ids_for_nodes(stores, self.case.maintenance_nodes)
        maintenance_items = [
            item for item in stores if int(item["store"]["id"]) in maintenance_store_ids
        ]
        if len(failed_store_ids) != 3 or len(healthy_store_ids) != 3 or len(maintenance_items) != 1:
            raise RuntimeError(
                "SF07 reference expected three failed, three healthy, and one maintenance-only TiKV Store: "
                f"failed_store_ids={failed_store_ids!r}, healthy_store_ids={healthy_store_ids!r}, "
                f"maintenance_store_ids={maintenance_store_ids!r}, stores={stores!r}"
            )
        maintenance_item = maintenance_items[0]
        if self._state_name(maintenance_item) not in {"up", "serving"}:
            raise RuntimeError(
                "SF07 reference maintenance-only Store is not serving outside the incident: "
                f"item={maintenance_item!r}"
            )

        scope = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT REGION_ID, TABLE_ID, INDEX_ID, IS_INDEX "
                    "FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
                    f"WHERE DB_NAME = '{self.case.db}' AND TABLE_NAME = '{self.case.table}' "
                    "ORDER BY REGION_ID, IS_INDEX, INDEX_ID"
                )
            },
            thinking="把受影响业务表的 record 与 index Region 映射出来，避免只检查 record path。",
        )
        scope_rows = scope["result"]
        affected_region_ids = tuple(sorted({int(row[0]) for row in scope_rows}))
        table_ids = {int(row[1]) for row in scope_rows}
        affected_index_ids = tuple(sorted({int(row[2]) for row in scope_rows if row[2] is not None}))
        if (
            not affected_region_ids
            or len(table_ids) != 1
            or not affected_index_ids
            or {int(row[3]) for row in scope_rows} != {0, 1}
        ):
            raise RuntimeError(
                "SF07 reference found incomplete record/index scope: "
                f"rows={scope_rows!r}, region_ids={affected_region_ids!r}, table_ids={table_ids!r}, "
                f"index_ids={affected_index_ids!r}"
            )
        affected_table_id = next(iter(table_ids))

        global_scope = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT REGION_ID, TABLE_ID, INDEX_ID, IS_INDEX "
                    "FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
                    f"WHERE DB_NAME = '{self.case.db}' AND TABLE_NAME = '{SF07_GLOBAL_SCOPE_TABLE}' "
                    "ORDER BY REGION_ID, IS_INDEX, INDEX_ID"
                )
            },
            thinking="把同一事故中 checkout 之外的 failed Store Region 也纳入全局 recovery scope，不能只按目标表推导失败集合。",
        )
        global_scope_region_ids = tuple(sorted({int(row[0]) for row in global_scope["result"]}))
        if not global_scope_region_ids:
            raise RuntimeError("SF07 reference found no global failed Store recovery scope")
        recovery_region_ids = tuple(sorted(set(affected_region_ids) | set(global_scope_region_ids)))

        peers_by_region = {}
        for region_id in affected_region_ids:
            region = self.execute(
                "manage_cluster",
                {
                    "resource": "region",
                    "operation": "get",
                    "parameters": {"region_id": region_id},
                },
                thinking="通过 PD Region metadata 直接确认每个受影响 Region 的两个永久失败 peer，避免在故障 Region 上扫描 SQL peer 视图。",
            )["result"]
            peers_by_region[region_id] = {int(peer["store_id"]) for peer in region["peers"]}
        target_failed_store_ids = set().union(*peers_by_region.values()) & set(failed_store_ids)
        if set(peers_by_region) != set(affected_region_ids) or len(target_failed_store_ids) != 2 or any(
            len(peers_by_region[region_id]) != 3
            or len(peers_by_region[region_id] & set(failed_store_ids)) != 2
            or not (peers_by_region[region_id] & set(healthy_store_ids))
            for region_id in affected_region_ids
        ):
            raise RuntimeError(
                "SF07 reference found an unexpected failed-peer mapping: "
                f"failed_store_ids={failed_store_ids!r}, target_failed_store_ids={sorted(target_failed_store_ids)!r}, "
                f"peers_by_region={peers_by_region!r}"
            )

        boundary = self.execute(
            "execute_sql",
            {"sql_query": "SELECT @@tidb_current_ts"},
            thinking="记录最后确认的时间边界，Online Unsafe Recovery 后不宣称一般性零丢失。",
        )
        pre_fault_tso = int(boundary["result"][0][0])
        self.execute(
            "execute_sql",
            {"sql_query": f"SELECT COUNT(*), SUM(amount), BIT_XOR(row_crc) FROM {self.case.db}.{self.case.table}"},
            thinking="记录受影响业务 truth，恢复后用完整性与授权 canary 闭环验收。",
        )
        healthy_truth = self.execute(
            "execute_sql",
            {"sql_query": f"SELECT COUNT(*), SUM(amount) FROM {self.case.db}.{self.case.healthy_table}"},
            thinking="记录健康 reconciliation 邻居作为 scope 反事实。",
        )
        config = self.execute(
            "manage_cluster",
            {"resource": "config", "operation": "get", "target": "pd"},
            thinking="保存 PD scheduling baseline；Online Unsafe Recovery 完成后必须核对全局门控。",
        )
        baseline_schedule = dict(SF07_SCHEDULE_BASELINE)
        current_schedule = config["result"]["schedule"]
        if any(str(current_schedule[key]) != "0" for key in baseline_schedule):
            raise RuntimeError(
                "SF07 reference expected the injected scheduling gate to be zero before recovery: "
                f"schedule={current_schedule!r}"
            )
        self.execute(
            "manage_cluster",
            {"resource": "unsafe_recovery", "operation": "get"},
            thinking="确认 PD recovery 在提交前没有已运行的任务。",
        )
        self.execute(
            "manage_cluster",
            {
                "resource": "unsafe_recovery",
                "operation": "start",
                "parameters": {"failed_store_ids": list(failed_store_ids)},
            },
            thinking="使用 v8.1 产品入口一次提交完整 failed Store 集合；Success 只代表 accepted。",
        )

        terminal_status = None
        for attempt in range(30):
            status = self.execute(
                "manage_cluster",
                {"resource": "unsafe_recovery", "operation": "get"},
                thinking=f"轮询 PD Online Unsafe Recovery 状态，第 {attempt + 1} 次；只接受 Finished 终态。",
            )
            recovery_text = self._recovery_text(status)
            if "unsafe recovery finished" in recovery_text:
                terminal_status = status
                break
            if "unsafe recovery failed" in recovery_text:
                raise RuntimeError(f"SF07 Online Unsafe Recovery failed: status={status!r}")
            if attempt < 29:
                self.execute(
                    "execute_sql",
                    {"sql_query": "SELECT SLEEP(10)"},
                    thinking="PD recovery 是异步任务，等待下一个 Store heartbeat 再观察。",
                )
        if terminal_status is None:
            raise RuntimeError("SF07 Online Unsafe Recovery did not reach Finished within the reference window")

        current_config = self.execute(
            "manage_cluster",
            {"resource": "config", "operation": "get", "target": "pd"},
            thinking="Finished 后立即恢复 PD 全局 scheduling，让被 demote 的 failed peer 可以完成清理。",
        )
        for key, value in baseline_schedule.items():
            if str(current_config["result"]["schedule"][key]) != str(value):
                self.execute(
                    "manage_cluster",
                    {
                        "resource": "config",
                        "operation": "update",
                        "target": "pd",
                        "parameters": {"key": f"schedule.{key}", "value": value},
                    },
                    thinking=f"Recovery 已 Finished，恢复 PD scheduling baseline: {key}={value!r}。",
                )

        settled = False
        recoverable_store_ids = set(healthy_store_ids) | set(maintenance_store_ids)
        for attempt in range(30):
            settled_stores = self.execute(
                "manage_cluster",
                {"resource": "store", "operation": "list"},
                thinking=f"Finished 后等待 failed Store 终态和 Region peer 清理，第 {attempt + 1} 次。",
            )["result"]["stores"]
            settled_peers = self.execute(
                "execute_sql",
                {
                    "sql_query": (
                        "SELECT REGION_ID, STORE_ID FROM INFORMATION_SCHEMA.TIKV_REGION_PEERS "
                        "WHERE STORE_ID IN ("
                        + ",".join(str(store_id) for store_id in failed_store_ids)
                        + ") OR REGION_ID IN ("
                        + ",".join(str(region_id) for region_id in recovery_region_ids)
                        + ") ORDER BY REGION_ID, STORE_ID"
                    )
                },
                thinking="确认 failed Store 没有 failed learner 残留，且每个 affected Region 都有三个健康 peer。",
            )["result"]
            store_by_id = {int(item["store"]["id"]): item for item in settled_stores}
            peer_map = {}
            failed_residual = []
            for region_id, store_id in settled_peers:
                region_id = int(region_id)
                store_id = int(store_id)
                peer_map.setdefault(region_id, set()).add(store_id)
                if store_id in failed_store_ids:
                    failed_residual.append((region_id, store_id))
            settled = (
                not failed_residual
                and all(
                    len(peer_map.get(region_id, set())) == 3
                    and peer_map[region_id] <= recoverable_store_ids
                    for region_id in recovery_region_ids
                )
            )
            if settled:
                break
            if attempt < 29:
                self.execute(
                    "execute_sql",
                    {"sql_query": "SELECT SLEEP(10)"},
                    thinking="等待 Unsafe Recovery 后 failed learner 清理和副本调度收敛。",
                )
        if not settled:
            raise RuntimeError(
                "SF07 affected Regions did not settle after Online Unsafe Recovery: "
                f"failed_store_ids={failed_store_ids!r}, affected_region_ids={affected_region_ids!r}"
            )

        self.execute(
            "execute_sql",
            {"sql_query": "SELECT SLEEP(10)"},
            thinking="Region peer 已收敛，再等待 TiDB schema lease 刷新后执行唯一授权 canary，避免把控制面收敛延迟误判为写入失败。",
        )

        self.execute(
            "execute_sql",
            {"sql_query": f"ADMIN CHECK TABLE {self.case.db}.{self.case.table}"},
            thinking="恢复后同时检查 record/index 一致性，不能用一次 checksum 代替 ADMIN CHECK。",
        )
        insert_sql = (
            f"INSERT INTO {self.case.db}.{self.case.table} "
            "(order_id, tenant_id, amount, status, payload) VALUES "
            f"({self.case.new_write_id}, {self.case.new_write_tenant_id}, {self.case.new_write_amount}, "
            f"'{self.case.new_write_status}', '{self.case.new_write_payload}')"
        )
        insert_result = {}
        for attempt in range(12):
            insert_result = self.execute(
                "execute_sql",
                {"sql_query": insert_sql},
                thinking="只执行题面授权的一个 post-terminal canary write，用于证明恢复后的读写闭环。",
            )
            if insert_result.get("status") != "error":
                break
            if "Information schema is out of date" not in str(insert_result.get("error", "")):
                break
            if attempt < 11:
                self.execute(
                    "execute_sql",
                    {"sql_query": "SELECT SLEEP(10)"},
                    thinking=f"TiDB schema lease 仍在追赶（第 {attempt + 1} 次重试前等待），避免把控制面收敛延迟误判为写入失败。",
                )
        if insert_result.get("status") == "error":
            raise RuntimeError(
                "SF07 authorized canary write did not succeed: "
                f"result={insert_result!r}"
            )
        self.execute(
            "execute_sql",
            {"sql_query": f"SELECT COUNT(*), SUM(amount), BIT_XOR(row_crc) FROM {self.case.db}.{self.case.table}"},
            thinking="核对原 truth 加授权 canary 的最终业务结果。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"SELECT COUNT(*), SUM(amount) FROM {self.case.db}.{self.case.healthy_table}"},
            thinking=f"确认健康邻居 truth 未变化，预期={healthy_truth['result']!r}。",
        )
        return build_report(
            self.case,
            failed_store_ids,
            affected_region_ids,
            affected_table_id,
            affected_index_ids,
            global_scope_region_ids,
            pre_fault_tso,
        )


def main():
    parser = argparse.ArgumentParser(description=SCENARIO.description)
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=96)
    parser.add_argument("--port", type=int, default=4500)
    parser.add_argument("--container-name", default="tidb-sf07-online-unsafe-recovery")
    add_diagnosis_arguments(parser)
    args = parser.parse_args()

    case = SCENARIO.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = PendingOfflineFullMockAgent(
            case,
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB v8.1 recovery DBA.",
            use_native_tools=False,
        )
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    result = Orchestrator(
        env,
        SCENARIO,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            diagnosis_match_mode=args.diagnosis_match_mode,
            diagnosis_semantic_model=args.diagnosis_semantic_model,
            diagnosis_semantic_config_path=args.diagnosis_semantic_config_path,
        ),
    ).run()
    if args.mode == "mock" and (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) != (True, True, True):
        raise AssertionError(
            f"SF07 Online Unsafe Recovery reference path did not pass all dimensions: "
            f"{json.dumps(result, ensure_ascii=False)}"
        )
    print(f"Final result: {json.dumps(result, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
