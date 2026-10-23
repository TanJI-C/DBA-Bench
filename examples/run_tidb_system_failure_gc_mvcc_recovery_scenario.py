from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.scenarios.tidb import (
    TidbSystemFailureGcMvccRecoveryForRecoverMvccAfterAsyncCommitLockScenarioCase,
    TidbSystemFailureGcMvccRecoveryScenario,
)
from src.scenarios.tidb.system_failure.gc_mvcc_recovery import (
    K01_BACKFILL_COMMIT_ROWS,
    K01_BACKFILL_POLL_SECONDS,
    K01_RECOVERY_TASK_NO,
    K01_RECOVERY_TASK_STATUS,
    K01_RECOVERY_TASK_TABLE,
    _decode_abnormal_async_commit_lock,
    _encode_memcomparable_key,
    _read_compact_bytes,
    _read_var_u64,
    _select_region_for_key,
    _table_row_key,
    k01_crc,
)
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb.system_failure.runtime.gc_mvcc_recovery import GcMvccRecoveryEnv
from src.scenarios.evaluation.config import add_diagnosis_arguments
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


def _success(result: dict, context: str) -> dict:
    if result.get("status") != "success":
        raise RuntimeError(f"K01 reference action failed: context={context!r}, result={result!r}")
    return result


def _decode_lock_type_and_start_ts(value_hex: str) -> tuple[str, int]:
    value = bytes.fromhex(value_hex)
    lock_type = chr(value[0])
    primary, offset = _read_compact_bytes(value, 1, "primary_key")
    start_ts, _ = _read_var_u64(value, offset, "start_ts")
    return lock_type, start_ts


class K01ReferenceMockAgent(BaseAgent):
    """A dynamic reference path used only for smoke validation."""

    def __init__(
        self,
        case: TidbSystemFailureGcMvccRecoveryForRecoverMvccAfterAsyncCommitLockScenarioCase,
    ):
        super().__init__()
        self.case = case

    def _write_after_schema_recovery(self, sql):
        deadline = time.monotonic() + self.case.runtime.sql_timeout_seconds
        while True:
            result = self.execute(
                "execute_sql", {"sql_query": sql},
                thinking="恢复后按工单授权规格写入恰好一笔验证行。",
            )
            if result["status"] == "success":
                return result
            if "error=(8027," not in result["error"]:
                _success(result, "authorized verification write")
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "K01 TiDB schema did not recover before the authorized write deadline: "
                    f"sql={sql!r}, timeout_seconds={self.case.runtime.sql_timeout_seconds}, "
                    f"result={result!r}"
                )
            time.sleep(K01_BACKFILL_POLL_SECONDS)

    def solve(self):
        knowledge = _success(
            self.execute(
                "search_knowledge",
                {
                    "query": "TiKV 8.1 recover-mvcc async commit min_commit_ts start_ts",
                    "source_scope": "self_managed",
                    "top_k": 5,
                    "kb_type": "recovery",
                    "component": "tikv",
                },
                thinking="先检索目标版本的 lock codec 和 recover-mvcc 边界，再把一般知识绑定到现场证据。",
            ),
            "unified TiDB knowledge",
        )
        if not any("recover-mvcc" in row.get("content", "") for row in knowledge.get("results", [])):
            raise RuntimeError(f"K01 reference knowledge did not return recover-mvcc semantics: result={knowledge!r}")
        self.execute(
            "manage_cluster",
            {"resource": "service", "operation": "list"},
            thinking="先确认所有 PD/TiKV/TiDB 服务身份和双 TiDB endpoint。",
        )
        stores = _success(
            self.execute(
                "manage_cluster",
                {"resource": "store", "operation": "list"},
                thinking="从当前 PD 读取真实 Store identity，不假定静态 Store ID。",
            ),
            "store list",
        )["result"]["stores"]
        store_targets_by_id = {
            int(item["store"]["id"]): "tikv/" + str(item["store"]["address"]).split(":", 1)[0]
            for item in stores
        }
        table_rows = _success(
            self.execute(
                "execute_sql",
                {
                    "sql_query": (
                        "SELECT TIDB_TABLE_ID FROM INFORMATION_SCHEMA.TABLES "
                        f"WHERE TABLE_SCHEMA = '{self.case.db}' AND TABLE_NAME = '{self.case.target_table}'"
                    )
                },
                thinking="先读取目标表 ID；TiKV row key 的 Region 归属不能由表名直接推断。",
            ),
            "target table ID query",
        )["result"]
        if len(table_rows) != 1:
            raise RuntimeError(f"K01 reference expected one target table ID: rows={table_rows!r}")
        target_key = _table_row_key(int(table_rows[0][0]), self.case.target_row_id)
        encoded_target_key_hex = _encode_memcomparable_key(target_key).hex().upper()
        region_rows = _success(
            self.execute(
                "execute_sql",
                {
                    "sql_query": (
                        "SELECT REGION_ID, START_KEY, END_KEY "
                        "FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
                        f"WHERE DB_NAME = '{self.case.db}' AND TABLE_NAME = '{self.case.target_table}' "
                        "AND IS_INDEX = 0 ORDER BY START_KEY"
                    )
                },
                thinking="读取目标表所有实时 Region 边界，用编码后的目标 row key 绑定唯一包含它的 Region。",
            ),
            "target Region key-range query",
        )["result"]
        region_candidates = [
            (int(row[0]), str(row[1] or ""), str(row[2] or ""))
            for row in region_rows
        ]
        region_id, start_key, end_key = _select_region_for_key(
            region_candidates,
            encoded_target_key_hex,
        )
        region = _success(
            self.execute(
                "manage_cluster",
                {
                    "resource": "region",
                    "operation": "get",
                    "target": f"region/{region_id}",
                    "parameters": {"region_id": region_id},
                },
                thinking=(
                    "读取目标 row key 所在 Region 的当前 peer 集合和 leader；"
                    f"key_range=({start_key},{end_key})。"
                ),
            ),
            "region get",
        )["result"]
        store_targets = [
            store_targets_by_id[int(peer["store_id"])]
            for peer in region["peers"]
        ]
        lock_scan = _success(
            self.execute(
                "manage_cluster",
                {
                    "resource": "mvcc_lock",
                    "operation": "list",
                    "target": f"region/{region_id}",
                    "parameters": {"store_targets": store_targets},
                },
                thinking="在精确 Region 边界内逐 peer 查看 lock CF 原始记录，并保留原始字节证据。",
            ),
            "mvcc lock scan",
        )["result"]
        scan_records = [record for peer in lock_scan["peers"] for record in peer["records"]]
        decoded_records = {}
        for record in scan_records:
            lock_type, start_ts = _decode_lock_type_and_start_ts(record["value_hex"])
            decoded_records.setdefault(record["key_hex"].upper(), (lock_type, start_ts, record))
        orphan_candidates = {
            key_hex: entry for key_hex, entry in decoded_records.items()
            if entry[0] == "P"
        }
        if len(orphan_candidates) != 1:
            decoded_summary = {key: (entry[0], entry[1]) for key, entry in decoded_records.items()}
            raise RuntimeError(
                "K01 reference expects exactly one Put-type stale lock record in the recovery "
                f"Region: decoded={decoded_summary!r}"
            )
        orphan_key_hex, (_, orphan_start_ts, orphan_record) = next(iter(orphan_candidates.items()))
        orphan_facts = _decode_abnormal_async_commit_lock(orphan_record["value_hex"], target_key)
        if orphan_facts["min_commit_ts"] > orphan_facts["start_ts"]:
            raise RuntimeError(
                "K01 reference orphan lock must violate the async-commit invariant: "
                f"facts={orphan_facts!r}"
            )
        if orphan_start_ts != orphan_facts["start_ts"]:
            raise RuntimeError(
                "K01 reference lock decode is inconsistent: "
                f"header_start_ts={orphan_start_ts!r}, facts={orphan_facts!r}"
            )
        _success(
            self.execute(
                "execute_sql",
                {
                        "sql_query": (
                            "SELECT SESSION_ID, STATE, start_time, "
                            "All_SQL_DIGESTS FROM INFORMATION_SCHEMA.TIDB_TRX ORDER BY SESSION_ID"
                        )
                },
                thinking="识别仍在途的合法业务事务（operator backfill 与 investigator 会话），它们与异常锁必须区别对待。",
            ),
            "in-flight transaction query",
        )["result"]
        while True:
            progress_rows = _success(
                self.execute(
                    "execute_sql",
                    {
                        "sql_query": (
                            f"SELECT COUNT(*) FROM {self.case.db}.{self.case.backfill_progress_table}"
                        )
                    },
                    thinking="读取 backfill 进度信号；在途事务提交后再执行恢复，避免破坏活锁。",
                ),
                "backfill progress query",
            )["result"]
            if int(progress_rows[0][0]) >= K01_BACKFILL_COMMIT_ROWS:
                break
            time.sleep(K01_BACKFILL_POLL_SECONDS)
        ticket_rows = _success(
            self.execute(
                "execute_sql",
                {
                    "sql_query": (
                        f"SELECT authorized_row_id, authorized_amount, authorized_payload, authorized_row_crc "
                        f"FROM {self.case.db}.{K01_RECOVERY_TASK_TABLE} "
                        f"WHERE task_no = '{K01_RECOVERY_TASK_NO}' AND task_status = '{K01_RECOVERY_TASK_STATUS}'"
                    )
                },
                thinking="读取恢复任务工单的授权行规格；验收写入必须严格按工单执行。",
            ),
            "recovery task ticket query",
        )["result"]
        expected_ticket = [[
            self.case.new_write_id,
            self.case.new_write_amount,
            self.case.new_write_payload,
            k01_crc(self.case.new_write_id, self.case.new_write_amount),
        ]]
        if ticket_rows != expected_ticket:
            raise RuntimeError(
                "K01 reference ticket must publish exactly the authorized write spec: "
                f"expected={expected_ticket!r}, ticket_rows={ticket_rows!r}"
            )
        (authorized_id, authorized_amount, authorized_payload, authorized_crc) = ticket_rows[0]
        self.execute(
            "manage_cluster",
            {"resource": "gc_status", "operation": "get"},
            thinking="读取 GC safepoint、last-run 和 Resolve Locks 等原始 phase series。",
        )
        inspection = _success(
            self.execute(
                "manage_cluster",
                {
                    "resource": "storage_maintenance",
                    "operation": "preflight",
                    "target": f"region/{region_id}",
                    "parameters": {"store_targets": store_targets},
                },
                thinking="在执行修改前，对同一 Region 和完整 peer 集合执行固定版本 recover-mvcc read-only inspect，取得解析凭证。",
            ),
            "storage maintenance preflight",
        )["result"]
        resolve_parameters = {"inspection_id": inspection["preflight_id"]}
        if self.case.case_no == 0:
            resolve_parameters.update(
                key=orphan_key_hex, lock_type="P", start_ts=orphan_start_ts,
            )
        _success(
            self.execute(
                "manage_cluster",
                {
                    "resource": "mvcc_lock",
                    "operation": "resolve",
                    "target": f"region/{region_id}",
                    "parameters": resolve_parameters,
                },
                thinking=(
                    "只解析已解码证实的 orphan async-commit 锁，提交 key、'P' 类型与 start_ts 解码凭证。"
                    if self.case.case_no == 0 else
                    "使用预检查凭证对已确认的目标 Region 执行 recover-mvcc。"
                ),
            ),
            "mvcc lock resolve",
        )
        verify_scan = _success(
            self.execute(
                "manage_cluster",
                {
                    "resource": "mvcc_lock",
                    "operation": "list",
                    "target": f"region/{region_id}",
                    "parameters": {"store_targets": store_targets},
                },
                thinking="复核 orphan 锁已从每个 Region peer 的 lock CF 消失，且全部活锁仍在。",
            ),
            "post-resolve lock scan",
        )["result"]
        remaining_orphan = [
            record
            for peer in verify_scan["peers"]
            for record in peer["records"]
            if record["key_hex"].upper() == orphan_key_hex
        ]
        if remaining_orphan:
            raise RuntimeError(
                f"K01 reference resolved lock must be absent from every peer: remaining={remaining_orphan!r}"
            )
        self._write_after_schema_recovery(
            f"INSERT INTO {self.case.db}.{self.case.target_table} "
            f"(id, amount, payload, row_crc) VALUES "
            f"({authorized_id}, {authorized_amount}, "
            f"'{authorized_payload}', "
            f"CRC32('k01:{authorized_id}:{authorized_amount}'))"
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT COUNT(*), SUM(amount), BIT_XOR(row_crc) FROM {self.case.db}.{self.case.target_table}; "
                    f"SELECT COUNT(*), SUM(amount), BIT_XOR(row_crc) FROM {self.case.db}.{self.case.healthy_table}; "
                    f"SELECT COUNT(*), SUM(amount), BIT_XOR(row_crc) FROM {self.case.db}.{self.case.long_tx_table}"
                )
            },
            thinking="闭合 target、healthy 和合法 long transaction 的业务 truth 校验。",
        )
        self.execute(
            "manage_cluster",
            {"resource": "gc_status", "operation": "get"},
            thinking="最终复核 safepoint 单调性和 GC phase 可观察性。",
        )
        return {"report": self.case.reference_report}


class K01ZeroMockAgent(BaseAgent):
    def solve(self):
        return {
            "report": {
                "diagnosis": {"conditions": []},
                "outcome": {"changes": [], "verification": []},
                "summary": "No diagnosis or remediation was attempted.",
            }
        }


def main() -> None:
    scenario = TidbSystemFailureGcMvccRecoveryScenario()
    parser = argparse.ArgumentParser(description=scenario.description)
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "zero", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=28)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--port", type=int, default=47620)
    parser.add_argument("--container-name", default="aiopsbench-tidb-k01-gc-mvcc")
    parser.add_argument("--fault-snapshot-mode", choices=("off",), default="off")
    add_diagnosis_arguments(parser)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = GcMvccRecoveryEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = K01ReferenceMockAgent(case)
    elif args.mode == "zero":
        agent = K01ZeroMockAgent()
    else:
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
            max_output_tokens=args.max_output_tokens,
        )
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
            diagnosis_match_mode=args.diagnosis_match_mode,
            diagnosis_semantic_model=args.diagnosis_semantic_model,
            diagnosis_semantic_config_path=args.diagnosis_semantic_config_path,
        ),
    ).run()
    if args.mode == "mock" and (
        result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]
    ) != (True, True, True):
        raise AssertionError(f"K01 reference path did not pass DP/OP/SP: {json.dumps(result, ensure_ascii=False)}")
    print(f"Final result: {json.dumps(result, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
