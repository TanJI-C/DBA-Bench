from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb import TidbSystemFailurePdTotalMetadataLossRecoveryScenario
from src.scenarios.tidb.system_failure.pd_total_metadata_loss_recovery import (
    extract_allocator_high_water,
    extract_original_cluster_id,
)


SCENARIO = TidbSystemFailurePdTotalMetadataLossRecoveryScenario()


def _condition(factor: str, evidence: str) -> dict[str, Any]:
    return {
        "type": "root_cause",
        "factor": factor,
        "entity": "pd_all_metadata_lost_restore_original_cluster",
        "evidence": [evidence],
    }


def _cluster_status(identity: dict[str, Any]) -> dict[str, Any]:
    status = identity["cluster"]
    return {
        "id": int(status["id"]),
    }


def build_full_pass_report(
    case,
    original_id: int,
    new_id: int,
    alloc_id: int,
    maintenance_record_id: str,
) -> dict[str, Any]:
    factors = (
        (
            "all three PD data directories were empty while the original TiKV data remained",
            f"same record_id={maintenance_record_id}: pd-0 before non-empty -> after empty; "
            "pd-1 before non-empty -> after empty; pd-2 before non-empty -> after empty; "
            "TiKV data retained",
        ),
        (
            "the rebuilt PD exposed a new cluster ID and the preserved TiKV members rejected it as a cluster ID mismatch",
            f"pd_identity current cluster_id={new_id} differed from historical cluster_id={original_id}; all TiKV log observations contained the cluster-ID mismatch",
        ),
        (
            "the original cluster ID must be recovered from pre-loss TiKV or PD evidence rather than accepting the rebuilt PD identity",
            f"historical PD/TiKV evidence identified original cluster_id={original_id}, while rebuilt PD cluster_id={new_id}",
        ),
        (
            "the pd-recover alloc-id must be strictly higher than the largest observed allocator high-water value",
            f"historical PD allocator logs had a lower largest new-end than the submitted alloc_id={alloc_id}, satisfying the strict boundary",
        ),
        (
            "pd-recover does not repair TSO, so clock evidence and post-recovery TSO monotonicity are required",
            "pre-recovery clock_status remained within 100 ms and two post-recovery TSO samples advanced beyond the pre-loss sample",
        ),
        (
            "a healthy rebuilt PD endpoint is insufficient because the preserved TiKV Store and Region metadata is not served under the rebuilt identity",
            "post-recovery PD Store inventory contained all original Stores in Up state and INFORMATION_SCHEMA.TIKV_REGION_STATUS matched the pre-loss Region count",
        ),
        (
            "force-new-cluster or accepting the rebuilt cluster ID would create a different cluster and is not recovery of the original data",
            f"one pd-recover execution used original cluster_id={original_id}; no force-new-cluster path was used",
        ),
    )
    return {
        "report": {
            "diagnosis": {
                "conditions": [_condition(factor, evidence) for factor, evidence in factors],
            },
            "outcome": {
                "changes": [
                    "stopped all TiDB and TiKV services before metadata recovery",
                    f"executed the fixed-version pd-recover once with original cluster_id={original_id} and alloc_id={alloc_id}",
                    "atomically restarted the full PD quorum so the recovered identity was loaded across all members",
                    "started the original TiKV and TiDB topology after recovery",
                    f"inserted one authorized event into {case.db}.{case.live_events_table}",
                ],
                "verification": [
                    "the original PD identity and three-member quorum were restored",
                    "all original Stores and Regions rejoined; the pre-recovery clock precondition and TSO checks passed",
                    "orders and order_items checksums stayed unchanged",
                    f"event_id={case.new_event_id} was committed in live_events",
                ],
            },
            "summary": (
                "Total PD metadata loss created a new control-plane identity while the original TiKV data remained. "
                "The original identity and allocator boundary were recovered before the database services were restarted."
            ),
        }
    }


class K03FullPassMockAgent(MockLLMAgent):
    """Reference path that derives all dynamic recovery identifiers from live evidence."""

    def __init__(self, case):
        super().__init__(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB distributed-systems recovery DBA.",
            use_native_tools=False,
        )
        self.case = case

    def _call(self, api: str, args: dict[str, Any], thinking: str) -> dict[str, Any]:
        result = self.execute(api, args, thinking=thinking)
        if result.get("status") != "success":
            raise RuntimeError(f"K03 reference action failed: api={api!r}, args={args!r}, result={result!r}")
        return result

    def solve(self) -> dict[str, Any]:
        self._call(
            "manage_cluster",
            {"resource": "service", "operation": "list"},
            "先确认声明的三 PD、三 TiKV、两 TiDB 服务身份和当前运行状态。",
        )
        identity_payload = self._call(
            "manage_cluster",
            {"resource": "pd_identity", "operation": "get"},
            "读取当前重建 PD 的原始身份、成员、Leader 和 Store 快照。",
        )
        current_inspection_payload = self._call(
            "manage_cluster",
            {"resource": "pd_recovery", "operation": "inspect"},
            "先读取当前重建 PD 目录和同域维护观测，确认当前健康快照不能单独代表原集群。",
        )
        maintenance_index = current_inspection_payload["result"]["historical_evidence"]["maintenance_index"]
        maintenance_inspections = []
        for record in maintenance_index:
            record_id = record["record_id"]
            for service in ("pd-0", "pd-1", "pd-2"):
                maintenance_inspections.append(
                    self._call(
                        "manage_cluster",
                        {
                            "resource": "pd_recovery",
                            "operation": "inspect",
                            "target": f"pd/{service}",
                            "parameters": {
                                "view": "history",
                                "phase": "maintenance",
                                "record_id": record_id,
                            },
                        },
                        f"读取维护 index 的 {record_id} 在 {service} 上的原始目录阶段，比较同一窗口的成员范围。",
                    )
                )
        full_loss_record_ids = []
        for record in maintenance_index:
            record_id = record["record_id"]
            snapshots = [
                payload["result"].get("data_inventory")
                for payload in maintenance_inspections
                if payload["result"]["historical_evidence"]["maintenance_record"]["record_id"] == record_id
            ]
            if len(snapshots) != 3 or any(snapshot is None for snapshot in snapshots):
                continue
            if all(
                int(snapshot["after"]["file_count"]) == 0
                for snapshot in snapshots
            ):
                full_loss_record_ids.append((record["observed_at"], record_id))
        if not full_loss_record_ids:
            raise RuntimeError(
                f"K03 reference expected at least one full-loss maintenance window: records={full_loss_record_ids!r}"
            )
        full_loss_record_id = max(full_loss_record_ids)[1]
        identity_inspections = []
        for service in ("pd-0", "pd-1", "pd-2"):
            identity_inspections.append(
                self._call(
                    "manage_cluster",
                    {
                        "resource": "pd_recovery",
                        "operation": "inspect",
                        "target": f"pd/{service}",
                        "parameters": {
                            "view": "history",
                            "phase": "identity",
                            "record_id": full_loss_record_id,
                        },
                    },
                    f"读取同一维护窗口 {full_loss_record_id} 的 {service} raw identity/allocator 日志，关联原 cluster ID。",
                )
            )
        clock_payload = self._call(
            "manage_cluster",
            {"resource": "clock_status", "operation": "list"},
            "在恢复前确认所有运行中数据库容器的 wall-clock 偏移满足公开限制。",
        )
        if int(clock_payload["result"]["max_abs_offset_ms"]) > self.case.clock_offset_limit_ms:
            raise RuntimeError(f"K03 reference clock precondition failed: result={clock_payload!r}")
        current_identity = identity_payload["result"]
        current_inspection = current_inspection_payload["result"]
        maintenance_inventory = {
            "before_maintenance": {},
            "after_wipe_before_rebuild": {},
        }
        for payload in maintenance_inspections:
            record = payload["result"]["historical_evidence"]["maintenance_record"]
            if record["record_id"] != full_loss_record_id:
                continue
            for phase, snapshots in payload["result"]["data_inventory"].items():
                maintenance_inventory["before_maintenance" if phase == "before" else "after_wipe_before_rebuild"].update(
                    {payload["result"]["historical_evidence"]["maintenance_record"]["target"].rsplit("/", 1)[1]: snapshots}
                )
        maintenance_inspection = {"data_inventory": maintenance_inventory}
        identity_inspection = {
            "historical_evidence": {
                "pd_logs": {
                    target: lines
                    for payload in identity_inspections
                    for target, lines in payload["result"]["historical_evidence"]["pd_logs"].items()
                }
            }
        }
        inspection = {
            "data_inventory": maintenance_inspection["data_inventory"],
            "historical_evidence": identity_inspection["historical_evidence"],
        }
        current_inventory = current_inspection["data_inventory"]["current"]
        if any(int(snapshot["file_count"]) == 0 for snapshot in current_inventory.values()):
            raise RuntimeError(f"K03 reference expected rebuilt PD directories to be non-empty: inventory={current_inventory!r}")
        historical_logs = inspection["historical_evidence"]["pd_logs"]
        original_status = {"id": extract_original_cluster_id(historical_logs)}
        rebuilt_status = _cluster_status(current_identity)
        if original_status["id"] == rebuilt_status["id"]:
            raise RuntimeError(
                f"K03 reference expected distinct original and rebuilt cluster IDs: "
                f"original={original_status!r}, rebuilt={rebuilt_status!r}"
            )
        allocator_high_water = extract_allocator_high_water(
            inspection["historical_evidence"]["pd_logs"]
        )
        alloc_id = allocator_high_water + 1
        pd_targets = tuple(f"pd/{name}" for name in ("pd-0", "pd-1", "pd-2"))
        database_targets = tuple(
            f"{component}/{index}"
            for component, count in (("tikv", 3), ("tidb", 2))
            for index in (f"{component}-{i}" for i in range(count))
        )
        for target in database_targets:
            self._call(
                "manage_cluster",
                {"resource": "service", "operation": "stop", "target": target},
                "停止 TiDB/TiKV，满足 pd-recover 防止数据交互的前置条件。",
            )
        recovery = self._call(
            "manage_cluster",
            {
                "resource": "pd_recovery",
                "operation": "execute",
                "target": pd_targets[0],
                "parameters": {
                    "cluster_id": original_status["id"],
                    "alloc_id": alloc_id,
                    "recovery_branch": "entirely_rebuild",
                    "record_id": full_loss_record_id,
                },
            },
            "使用历史原 cluster ID 和严格高于 allocator high-water 的 alloc-id 执行一次固定版本 pd-recover。",
        )
        if recovery["result"]["cluster_id"] != original_status["id"]:
            raise RuntimeError(f"K03 reference recovery used the wrong cluster ID: result={recovery!r}")
        self._call(
            "manage_cluster",
            {"resource": "service", "operation": "restart", "target": "pd"},
            "原子重启全部 PD，使原 cluster identity 在整个 PD quorum 中同时生效。",
        )
        for target in database_targets:
            self._call(
                "manage_cluster",
                {"resource": "service", "operation": "start", "target": target},
                "恢复原始 TiKV/TiDB 服务，等待 Store/Region 元数据重新注册。",
            )
        self._call(
            "manage_cluster",
            {"resource": "pd_identity", "operation": "get"},
            "确认恢复后的 PD 身份、成员和 Store 元数据，而不是只看端口健康。",
        )
        self._call(
            "execute_sql",
            {
                "sql_query": (
                    f"INSERT INTO {self.case.db}.{self.case.live_events_table} "
                    f"(event_id, payload) VALUES ({self.case.new_event_id}, 'k03-reference-recovery')"
                )
            },
            "只在原集群控制面恢复后写入题面授权的一个 live event。",
        )
        self._call(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT COUNT(*), SUM(amount), BIT_XOR(record_crc) "
                    f"FROM {self.case.db}.{self.case.orders_table}"
                )
            },
            "复核受保护 orders 的数量、金额和 checksum。",
        )
        self._call(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT COUNT(*), SUM(qty), BIT_XOR(item_crc) "
                    f"FROM {self.case.db}.{self.case.order_items_table}"
                )
            },
            "复核受保护 order_items 的数量、数量和 checksum。",
        )
        self._call(
            "manage_cluster",
            {"resource": "clock_status", "operation": "list"},
            "复核恢复后的时钟偏移。",
        )
        self._call(
            "execute_sql",
            {"sql_query": "SELECT @@tidb_current_ts"},
            "采样恢复后的 TSO，确认它高于故障前且仍然递增。",
        )
        return build_full_pass_report(
            self.case,
            original_status["id"],
            rebuilt_status["id"],
            alloc_id,
            full_loss_record_id,
        )


def _configure_knowledge(args: argparse.Namespace) -> tuple[str, ...] | None:
    if args.knowledge_condition == "unified":
        return None
    if args.knowledge_condition == "none":
        return tuple(tool for tool in TiDBEnv.PUBLIC_TOOLS if tool != "search_knowledge")
    raise ValueError(f"Unsupported K03 knowledge condition: condition={args.knowledge_condition!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=SCENARIO.description)
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--llm-config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=128)
    parser.add_argument("--port", type=int, default=4910)
    parser.add_argument("--container-name", default="tidb-k03-pd-recovery")
    parser.add_argument(
        "--knowledge-condition",
        choices=("unified", "none"),
        default="unified",
        help=(
            "正式运行使用主仓库统一 hierarchical 知识库；none 仅用于 matched no-KB ablation，"
            "不会切换 source、collection 或 index。"
        ),
    )
    parser.add_argument("--diagnosis-match-mode", choices=("exact", "semantic"), default=None)
    parser.add_argument("--diagnosis-semantic-model", default=None, help="Diagnosis judge model; defaults to --model")
    parser.add_argument(
        "--diagnosis-semantic-config",
        "--diagnosis-semantic-config-path",
        dest="diagnosis_semantic_config_path",
        default=None,
    )
    args = parser.parse_args()
    knowledge_condition = os.environ.get("AIOPS_K03_KNOWLEDGE_CONDITION", args.knowledge_condition)
    if knowledge_condition not in {"unified", "none"}:
        raise ValueError(
            "Unsupported K03 knowledge condition from AIOPS_K03_KNOWLEDGE_CONDITION: "
            f"condition={knowledge_condition!r}"
        )
    args.knowledge_condition = knowledge_condition
    enabled_tools = _configure_knowledge(args)
    case = SCENARIO.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=300,
        enabled_tools=enabled_tools,
    )
    if args.mode == "mock":
        agent = K03FullPassMockAgent(case)
    else:
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.llm_config,
            use_native_tools=True,
        )
    diagnosis_match_mode = args.diagnosis_match_mode or ("semantic" if args.mode == "llm" else "exact")
    result = Orchestrator(
        env,
        SCENARIO,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode="off",
            diagnosis_match_mode=diagnosis_match_mode,
            diagnosis_semantic_model=args.diagnosis_semantic_model or args.model,
            diagnosis_semantic_config_path=args.diagnosis_semantic_config_path or args.llm_config,
        ),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (True, True, True):
            raise AssertionError(
                "K03 mock path must pass DP/OP/SP: "
                f"observed={observed!r}, result={json.dumps(result, ensure_ascii=False)}"
            )
    print(f"Final result: {json.dumps(result, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
