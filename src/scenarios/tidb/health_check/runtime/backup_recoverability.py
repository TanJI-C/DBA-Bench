"""BackupRecoverabilityEnv: Case-specific capabilities and mutable run state.

Generic TiDB execution remains in src.execution.environments.tidb.
"""

from src.execution.environments.tidb import TiDBEnv
import hashlib
import json
import os
import shutil
import time
from typing import Any, Dict
from src.execution.tools import Tool


class BackupRecoverabilityEnv(TiDBEnv):
    HC04_RESTORE_TOOLS = (
        "inspect_backup_archive",
        "repair_backup_archive",
        "run_isolated_restore",
        "inspect_isolated_restore",
    )

    def __init__(self, *args, **kwargs):
        self._hc04_restore_runtime = None
        self._hc04_restore_attempt_no = 0
        super().__init__(*args, **kwargs)

    def configure_hc04_restore_runtime(self, runtime: Dict[str, Any]) -> None:
        if self._hc04_restore_runtime is not None:
            raise RuntimeError(
                f"TiDB HC04 restore runtime is already configured: run_id={self.run_id!r}"
            )
        self._hc04_restore_runtime = dict(runtime)
        self._hc04_restore_attempt_no = 0
        tools = tuple(spec.tool_id for spec in self.get_tool_specs()
                      if spec.tool_id not in self.HC04_RESTORE_TOOLS)
        self._configure_tools((*tools, *self.HC04_RESTORE_TOOLS))

    def clear_hc04_restore_runtime(self) -> None:
        if self._hc04_restore_runtime is None:
            raise RuntimeError(
                f"TiDB HC04 restore runtime is not configured: run_id={self.run_id!r}"
            )
        self._hc04_restore_runtime = None
        self._hc04_restore_attempt_no = 0
        self._configure_tools(tuple(spec.tool_id for spec in self.get_tool_specs()
                                    if spec.tool_id not in self.HC04_RESTORE_TOOLS))

    def _require_hc04_restore_runtime(self) -> Dict[str, Any]:
        if self._hc04_restore_runtime is None:
            raise ValueError(
                f"TiDB HC04 restore runtime is not configured: run_id={self.run_id!r}"
            )
        return self._hc04_restore_runtime

    def _hc04_rows(self, sql: str, params: tuple = ()) -> list[tuple]:
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql, params)
            return list(cursor.fetchall())

    def _hc04_execute(self, sql: str, params: tuple = ()) -> None:
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql, params)

    @staticmethod
    def _hc04_hash(path: str) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _hc04_approved_source(self, runtime: Dict[str, Any], target_segment: str) -> tuple[int, str]:
        rows = self._hc04_rows(
            f"SELECT a.source_object_id, a.source_segment, o.segment_name, o.checksum "
            f"FROM {runtime['db']}.{runtime['approval_table']} a "
            f"JOIN {runtime['db']}.{runtime['object_inventory_table']} o "
            "ON o.object_id = a.source_object_id "
            "WHERE a.request_key = %s AND a.selected_backup_id = %s "
            "AND a.source_segment = %s "
            "AND a.source_role = 'primary' AND a.restore_mode = 'isolated' "
            "AND a.approval_state = 'APPROVED' AND a.approved_by = 'dr-owner' "
            "ORDER BY a.approved_at DESC, a.approval_id DESC LIMIT 1",
            (runtime["request_key"], runtime["selected_backup_id"], target_segment),
        )
        if len(rows) != 1:
            raise RuntimeError(
                "HC04 approved source must identify exactly one object: "
                f"request_key={runtime['request_key']!r}, "
                f"selected_backup_id={runtime['selected_backup_id']!r}, rows={rows!r}"
            )
        source_object_id, source_segment, catalog_segment, catalog_checksum = rows[0]
        if str(source_segment) != target_segment or str(catalog_segment) != target_segment:
            raise RuntimeError(
                "HC04 approved source segment does not match the active fault: "
                f"source_object_id={source_object_id!r}, source_segment={source_segment!r}, "
                f"catalog_segment={catalog_segment!r}, target_segment={target_segment!r}"
            )
        source_path = runtime["object_files"].get(int(source_object_id))
        if source_path is None or not os.path.isfile(source_path):
            raise RuntimeError(
                "HC04 approved source object is not readable: "
                f"source_object_id={source_object_id!r}, source_path={source_path!r}"
            )
        source_checksum = self._hc04_hash(source_path)
        if source_checksum != str(catalog_checksum):
            raise RuntimeError(
                "HC04 approved source checksum disagrees with archive inventory: "
                f"source_object_id={source_object_id!r}, catalog_checksum={catalog_checksum!r}, "
                f"actual_checksum={source_checksum!r}"
            )
        return int(source_object_id), source_checksum

    @Tool(
        description=(
            "查看指定 backup 的对象存储 inventory 和 log-segment continuity 未过滤结果。结果来自当前 case 的"
            "真实对象文件及 TiDB 审计表，不是提交报告的解析结果；需要结合恢复请求和审批记录判断对象关系。"
        ),
        arg_descriptions={
            "backup_id": "批准恢复请求中的 backup_id",
        },
    )
    def inspect_backup_archive(self, backup_id: str) -> str:
        runtime = self._require_hc04_restore_runtime()
        if backup_id != runtime["selected_backup_id"]:
            raise ValueError(
                "HC04 archive inspection target is outside the approved request: "
                f"requested={backup_id!r}, approved={runtime['selected_backup_id']!r}"
            )
        object_rows = self._hc04_rows(
            f"SELECT object_id, backup_id, segment_name, region, object_status, readable, replicated, legal_hold, checksum "
            f"FROM {runtime['db']}.{runtime['object_inventory_table']} "
            "WHERE backup_id = %s ORDER BY object_id DESC",
            (backup_id,),
        )
        segment_rows = self._hc04_rows(
            f"SELECT segment_name, present, checksum_status, object_status, replica_status, usable_for_restore "
            f"FROM {runtime['db']}.{runtime['log_segment_table']} "
            "WHERE backup_id = %s ORDER BY segment_id DESC",
            (backup_id,),
        )
        return json.dumps({
            "status": "success",
            "backup_id": backup_id,
            "objects": object_rows,
            "segments": segment_rows,
        }, ensure_ascii=False, default=str)

    @Tool(
        description=(
            "从当前 case 已登记的归档对象副本恢复一个指定 segment。工具只允许复制对象存储中的"
            "现有对象，不允许修改 TiDB 业务表、审计请求或生产集群；复制后会按实际 SHA-256 更新"
            "归档可用性状态。返回值只表示复制操作完成，最终恢复能力需要通过后续状态检查确认。"
        ),
        arg_descriptions={
            "source_object_id": "对象目录中的源 object_id",
            "target_segment": "要修复的 segment_name",
        },
    )
    def repair_backup_archive(self, source_object_id: int, target_segment: str) -> str:
        runtime = self._require_hc04_restore_runtime()
        if target_segment not in runtime["fault_segments"]:
            raise ValueError(
                "HC04 archive repair target is outside the active fault: "
                f"requested={target_segment!r}, fault_segments={runtime['fault_segments']!r}"
            )
        source_row = self._hc04_rows(
            f"SELECT object_id, backup_id, segment_name, checksum FROM {runtime['db']}.{runtime['object_inventory_table']} "
            "WHERE object_id = %s",
            (source_object_id,),
        )
        if len(source_row) != 1:
            raise ValueError(
                "HC04 archive repair source object must identify exactly one object: "
                f"source_object_id={source_object_id!r}, rows={source_row!r}"
            )
        object_id, source_backup_id, source_segment, source_catalog_checksum = source_row[0]
        if str(source_segment) != target_segment:
            raise ValueError(
                "HC04 archive repair source segment does not match target: "
                f"source_object_id={source_object_id!r}, source_segment={source_segment!r}, "
                f"target_segment={target_segment!r}"
            )
        source_path = runtime["object_files"].get(int(object_id))
        target_path = runtime["primary_object_paths"][target_segment]
        if source_path is None or not os.path.isfile(source_path):
            raise RuntimeError(
                "HC04 archive repair source object is not readable: "
                f"source_object_id={source_object_id!r}, source_backup_id={source_backup_id!r}, "
                f"source_path={source_path!r}"
            )
        approved_source_object_id, approved_checksum = self._hc04_approved_source(runtime, target_segment)
        shutil.copyfile(source_path, target_path)
        actual_checksum = self._hc04_hash(target_path)
        valid = (
            actual_checksum == str(source_catalog_checksum)
            and actual_checksum == approved_checksum
            and int(object_id) == approved_source_object_id
        )
        self._hc04_execute(
            f"UPDATE {runtime['db']}.{runtime['object_inventory_table']} "
            "SET object_status = %s, readable = 1, replicated = %s, checksum = %s "
            "WHERE object_id = %s",
            (
                "AVAILABLE" if valid else "CORRUPT",
                1 if valid else 0,
                actual_checksum,
                runtime["primary_object_ids"][target_segment],
            ),
        )
        self._hc04_execute(
            f"UPDATE {runtime['db']}.{runtime['log_segment_table']} "
            "SET present = 1, checksum_status = %s, object_status = %s, replica_status = %s, usable_for_restore = %s "
            "WHERE backup_id = %s AND segment_name = %s",
            (
                "OK" if valid else "MISMATCH",
                "READABLE" if valid else "READABLE_BUT_INVALID",
                "REPLICATED" if valid else "NOT_REPLICATED",
                1 if valid else 0,
                runtime["selected_backup_id"],
                target_segment,
            ),
        )
        return json.dumps({
            "status": "success",
            "operation": "repair_backup_archive",
            "source_object_id": int(object_id),
            "source_backup_id": str(source_backup_id),
            "target_segment": target_segment,
        }, ensure_ascii=False)

    def _hc04_source_truth(self, runtime: Dict[str, Any]) -> dict[str, tuple[int, int]]:
        queries = {
            runtime["orders_table"]: f"SELECT COUNT(*), COALESCE(SUM(order_id), 0) FROM {runtime['db']}.{runtime['snapshot_orders_table']}",
            runtime["order_lines_table"]: f"SELECT COUNT(*), COALESCE(SUM(line_id), 0) FROM {runtime['db']}.{runtime['snapshot_order_lines_table']}",
            runtime["payments_table"]: f"SELECT COUNT(*), COALESCE(SUM(payment_id), 0) FROM {runtime['db']}.{runtime['snapshot_payments_table']}",
            runtime["inventory_table"]: f"SELECT COUNT(*), COALESCE(SUM(sku_id), 0) FROM {runtime['db']}.{runtime['snapshot_inventory_table']}",
        }
        return {
            table: tuple(int(value) for value in self._hc04_rows(sql)[0])
            for table, sql in queries.items()
        }

    def _hc04_restore_tables(self, runtime: Dict[str, Any]) -> tuple[dict, ...]:
        tables = (
            (runtime["orders_table"], runtime["snapshot_orders_table"], runtime["sandbox_orders_table"], "order_id"),
            (runtime["order_lines_table"], runtime["snapshot_order_lines_table"], runtime["sandbox_order_lines_table"], "line_id"),
            (runtime["payments_table"], runtime["snapshot_payments_table"], runtime["sandbox_payments_table"], "payment_id"),
            (runtime["inventory_table"], runtime["snapshot_inventory_table"], runtime["sandbox_inventory_table"], "sku_id"),
        )
        truth = self._hc04_source_truth(runtime)
        checks = []
        for table, snapshot, sandbox, key in tables:
            self._hc04_execute(f"DELETE FROM {runtime['db']}.{sandbox}")
            self._hc04_execute(
                f"INSERT INTO {runtime['db']}.{sandbox} SELECT * FROM {runtime['db']}.{snapshot}"
            )
            row = self._hc04_rows(
                f"SELECT COUNT(*), COALESCE(SUM({key}), 0) FROM {runtime['db']}.{sandbox}"
            )[0]
            restored = (int(row[0]), int(row[1]))
            expected = truth[table]
            checks.append({
                "table_name": table,
                "source_rows": expected[0],
                "restored_rows": restored[0],
                "source_checksum": expected[1],
                "restored_checksum": restored[1],
                "checksum_status": "MATCH" if restored == expected else "MISMATCH",
            })
        return tuple(checks)

    @Tool(
        description=(
            "在独立的 HC04 sandbox 中重新执行恢复验证。失败或成功都会写入 restore attempt、"
            "checkpoint 和四张关键表的实际校验结果；调用结果只报告恢复状态，详细状态需要单独检查。"
        ),
    )
    def run_isolated_restore(self) -> str:
        runtime = self._require_hc04_restore_runtime()
        self._hc04_restore_attempt_no += 1
        attempt_id = f"{runtime['selected_drill_id']}-attempt-{self._hc04_restore_attempt_no:03d}"
        started = time.monotonic()
        valid_chain = True
        for segment in runtime["fault_segments"]:
            _, expected_checksum = self._hc04_approved_source(runtime, segment)
            object_hash = self._hc04_hash(runtime["primary_object_paths"][segment])
            chain_rows = self._hc04_rows(
                f"SELECT usable_for_restore, checksum_status FROM {runtime['db']}.{runtime['log_segment_table']} "
                "WHERE backup_id = %s AND segment_name = %s",
                (runtime["selected_backup_id"], segment),
            )
            valid_chain = valid_chain and (
                len(chain_rows) == 1
                and int(chain_rows[0][0]) == 1
                and str(chain_rows[0][1]).casefold() == "ok"
                and object_hash == expected_checksum
            )
        if valid_chain:
            checks = self._hc04_restore_tables(runtime)
            success = all(item["checksum_status"] == "MATCH" for item in checks)
            checkpoint_status = "COMPLETE" if success else "FAILED"
            checksum_status = "MATCH" if success else "MISMATCH"
            restore_status = "SUCCESS" if success else "FAILED"
            failure_class = "NONE" if success else "CHECKSUM_VALIDATION_FAILED"
            log_excerpt = "isolated restore completed and all critical table checks matched" if success else "isolated restore copied data but critical table checks did not match"
        else:
            checks = tuple()
            success = False
            checkpoint_status = "GAP"
            checksum_status = "NOT_VERIFIED"
            restore_status = "FAILED"
            failure_class = "CHECKPOINT_NOT_REACHED"
            log_excerpt = "isolated restore did not reach the requested checkpoint"
        duration = max(1, int(round(time.monotonic() - started)))
        observed_rto_seconds = duration
        observed_rpo_seconds = 0 if success else None
        source_truth = self._hc04_source_truth(runtime)
        total_source_rows = sum(value[0] for value in source_truth.values())
        restored_rows = sum(item["restored_rows"] for item in checks)
        self._hc04_execute(
            f"INSERT INTO {runtime['db']}.{runtime['restore_attempt_table']} "
            "(attempt_id, drill_id, backup_id, status, isolated, checkpoint_status, checksum_status, "
            "observed_rpo_seconds, observed_rto_seconds, restore_duration_seconds, failure_class, log_excerpt) "
            "VALUES (%s, %s, %s, %s, 1, %s, %s, %s, %s, %s, %s, %s)",
            (
                attempt_id,
                runtime["selected_drill_id"],
                runtime["selected_backup_id"],
                restore_status,
                checkpoint_status,
                checksum_status,
                observed_rpo_seconds,
                observed_rto_seconds,
                duration,
                failure_class,
                log_excerpt,
            ),
        )
        self._hc04_execute(
            f"UPDATE {runtime['db']}.{runtime['restore_drill_table']} SET status = %s, checkpoint_status = %s, "
            "checksum_status = %s, restore_duration_seconds = %s, business_crc_status = %s, "
            "source_rows = %s, restored_rows = %s, failure_class = %s, log_excerpt = %s WHERE drill_id = %s",
            (
                restore_status,
                checkpoint_status,
                checksum_status,
                duration,
                "MATCH" if success else "NOT_VERIFIED",
                total_source_rows,
                restored_rows,
                failure_class,
                log_excerpt,
                runtime["selected_drill_id"],
            ),
        )
        self._hc04_execute(
            f"DELETE FROM {runtime['db']}.{runtime['restore_check_table']} WHERE drill_id = %s",
            (runtime["selected_drill_id"],),
        )
        if checks:
            for item in checks:
                self._hc04_execute(
                    f"INSERT INTO {runtime['db']}.{runtime['restore_check_table']} "
                    "(drill_id, table_name, source_rows, restored_rows, source_checksum, restored_checksum, checksum_status, critical) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, 1)",
                    (
                        runtime["selected_drill_id"], item["table_name"], item["source_rows"], item["restored_rows"],
                        item["source_checksum"], item["restored_checksum"], item["checksum_status"],
                    ),
                )
        return json.dumps({
            "status": "success",
            "operation": "run_isolated_restore",
            "attempt_id": attempt_id,
            "restore_status": restore_status,
            "checkpoint_status": checkpoint_status,
            "checksum_status": checksum_status,
        }, ensure_ascii=False, default=str)

    @Tool(
        description="读取 HC04 当前 restore attempts、最后一次恢复状态和 sandbox 校验结果。",
    )
    def inspect_isolated_restore(self) -> str:
        runtime = self._require_hc04_restore_runtime()
        attempts = self._hc04_rows(
            f"SELECT attempt_id, status, checkpoint_status, checksum_status, failure_class FROM {runtime['db']}.{runtime['restore_attempt_table']} "
            "WHERE drill_id = %s ORDER BY attempt_id",
            (runtime["selected_drill_id"],),
        )
        checks = self._hc04_rows(
            f"SELECT table_name, source_rows, restored_rows, source_checksum, restored_checksum, checksum_status "
            f"FROM {runtime['db']}.{runtime['restore_check_table']} WHERE drill_id = %s ORDER BY table_name",
            (runtime["selected_drill_id"],),
        )
        return json.dumps({"status": "success", "attempts": attempts, "checks": checks}, ensure_ascii=False, default=str)
