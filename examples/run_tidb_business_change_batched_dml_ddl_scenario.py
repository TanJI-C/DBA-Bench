import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.tidb import TidbBusinessChangeBatchedDmlDdlScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


PASS_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": [
            "archived the approved EXPIRED order population with durable progress and adapted to settlement activity",
            "created a public archive_state, retention_class, order_id leading-column index online",
            "recorded every batch and completed the target change job",
        ],
        "verification": [
            "all policy-bound approved-scope target rows without active holds and no non-target rows reached the requested archive state",
            "the checkpoint chain is contiguous and every recorded progress unit has a positive affected-row count",
            "foreground checkout, customer, merchant and fulfillment profiles stayed within the 250ms p95 SLO",
            "immutable order count, primary-key sum and CRC were preserved",
        ],
    },
    "summary": "The policy-bound retention DML and online DDL completed under the live foreground SLO without weakening storage guardrails.",
}
StructuredReport.from_mapping(PASS_REPORT)


class Bc03FullMockAgent(BaseAgent):
    SLO_P95_MS = 250.0
    SLO_RECHECK_SECONDS = 60
    SLO_RECHECKS = 3
    INDEX_POLL_SECONDS = 5
    INDEX_POLL_ATTEMPTS = 30
    CORE_PROFILES = {
        "bc03_checkout_point_lookup",
        "bc03_checkout_order_touch",
        "bc03_customer_recent_orders",
        "bc03_tenant_open_order_rollup",
        "bc03_fulfillment_feed",
    }

    def __init__(self, transaction_shape: str, case):
        super().__init__()
        if transaction_shape not in {"ordered_limit", "keyset"}:
            raise ValueError(f"BC03 mock transaction shape is unsupported: {transaction_shape!r}")
        self.transaction_shape = transaction_shape
        self.case = case

    @property
    def database(self):
        return self.case.database

    @property
    def orders_table(self):
        return self.case.orders_table

    @property
    def job_table(self):
        return self.case.job_table

    @property
    def batch_table(self):
        return self.case.batch_table

    @property
    def job_id(self):
        return self.case.job_id

    @property
    def policy_table(self):
        return self.case.policy_table

    @property
    def scope_table(self):
        return self.case.scope_table

    @property
    def hold_table(self):
        return self.case.hold_table

    @property
    def index_columns(self):
        return self.case.index_columns

    @property
    def target_policy_id(self):
        return self.case.target_policy_id

    @property
    def target_scope_id(self):
        return self.case.target_scope_id

    @property
    def initial_checkpoint_rows(self):
        return self.case.initial_checkpoint_rows

    def _foreground_p95(self, thinking: str) -> float:
        payload = self.execute(
            "query_metrics",
            {"metric_type": "query_latency", "target": None},
            thinking=thinking,
        )
        series = payload["series"]["cluster"]
        p95_values = series["p95_ms"]
        if not p95_values:
            raise RuntimeError(
                "BC03 mock query_latency returned no cluster p95 samples: "
                f"payload={payload!r}"
            )
        return float(p95_values[-1])

    def _wait_for_foreground_slo(self) -> float:
        p95_ms = self._foreground_p95("读取真实前台 fingerprint 的最新 p95，为当前批次留下 SLO 证据。")
        for _ in range(self.SLO_RECHECKS):
            if p95_ms <= self.SLO_P95_MS:
                return p95_ms
            time.sleep(self.SLO_RECHECK_SECONDS)
            p95_ms = self._foreground_p95(
                f"前台 p95={p95_ms:.2f}ms 超过 250ms，暂停变更窗口并重新观测核心 profile。"
            )
        if p95_ms > self.SLO_P95_MS:
            raise RuntimeError(f"BC03 foreground p95 did not recover below SLO: p95_ms={p95_ms}")
        return p95_ms

    def _observe_business_conflict(self):
        return self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT TRX_ID, CURRENT_HOLDING_TRX_ID, KEY_INFO "
                    "FROM INFORMATION_SCHEMA.DATA_LOCK_WAITS"
                )
            },
            thinking="宽事务返回异常后，查看当前订单表的真实锁等待链，再决定后续执行方式。",
        )

    def _reconcile_interrupted_state(self) -> tuple[int, int, int, int]:
        job_state = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT state, last_pk, rows_completed, target_rows, policy_id, scope_id "
                    f"FROM {self.database}.{self.job_table} WHERE job_id = '{self.job_id}'"
                )
            },
            thinking="先读取恢复任务的持久计数和游标，确认它处于中断后的暂停状态。",
        )
        checkpoints = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT batch_no, lower_pk, upper_pk, affected_rows, observed_p95_ms "
                    f"FROM {self.database}.{self.batch_table} WHERE job_id = '{self.job_id}' ORDER BY batch_no"
                )
            },
            thinking="读取同一 job 已提交的 checkpoint 前缀，确认旧审计历史不能被重写。",
        )
        orphan = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT MIN(o.order_id), MAX(o.order_id), COUNT(*) "
                    f"FROM {self.database}.{self.orders_table} AS o "
                    "WHERE o.retention_class = 'EXPIRED' AND o.archive_state = 'ARCHIVED' "
                    f"AND o.archive_batch = '{self.job_id}' "
                    "AND EXISTS ("
                    f"SELECT 1 FROM {self.database}.{self.job_table} AS j "
                    f"JOIN {self.database}.{self.policy_table} AS p "
                    "ON p.policy_id = j.policy_id AND p.scope_id = j.scope_id "
                    f"JOIN {self.database}.{self.scope_table} AS s "
                    "ON s.scope_id = p.scope_id AND s.tenant_id = o.tenant_id "
                    "AND s.scope_state = 'APPROVED' "
                    f"WHERE j.job_id = '{self.job_id}' AND j.object_name = '{self.orders_table}' "
                    f"AND p.object_name = '{self.orders_table}' AND p.state = 'APPROVED'"
                    ") AND NOT EXISTS ("
                    f"SELECT 1 FROM {self.database}.{self.hold_table} AS h "
                    "WHERE h.order_id = o.order_id AND h.hold_state = 'ACTIVE'"
                    ") AND o.order_id > ("
                    f"SELECT MAX(upper_pk) FROM {self.database}.{self.batch_table} "
                    f"WHERE job_id = '{self.job_id}'"
                    ")"
                )
            },
            thinking="统计已经归属于目标 job 但位于持久游标之后的订单，确认是否存在缺失审计的已提交业务部分。",
        )
        job_rows = job_state["result"]
        checkpoint_rows = checkpoints["result"]
        orphan_rows = orphan["result"]
        if len(job_rows) != 1 or len(checkpoint_rows) != 3 or len(orphan_rows) != 1:
            raise RuntimeError(
                "BC03 mock interrupted state query returned unexpected shapes: "
                f"job={job_state!r}, checkpoints={checkpoints!r}, orphan={orphan!r}"
            )
        job = job_rows[0]
        orphan = orphan_rows[0]
        if (
            str(job[0]).casefold() != "paused"
            or int(job[2]) != self.initial_checkpoint_rows
            or int(job[4]) != self.target_policy_id
            or str(job[5]) != self.target_scope_id
        ):
            raise RuntimeError(f"BC03 mock expected paused interrupted job state: job={job!r}")
        if int(orphan[2] or 0) <= 0 or orphan[0] is None or orphan[1] is None:
            raise RuntimeError(f"BC03 mock expected one owned but unaudited batch: orphan={orphan!r}")
        lower_pk = int(job[1])
        upper_pk = int(orphan[1])
        orphan_rows = int(orphan[2])
        next_batch_no = max(int(row[0]) for row in checkpoint_rows) + 1
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"INSERT INTO {self.database}.{self.batch_table} "
                    "(job_id, batch_no, lower_pk, upper_pk, affected_rows, observed_p95_ms, recorded_at) "
                    f"VALUES ('{self.job_id}', "
                    f"{next_batch_no}, {lower_pk}, {upper_pk}, {orphan_rows}, 120.000, NOW()); "
                    f"UPDATE {self.database}.{self.job_table} SET state = 'RUNNING', "
                    f"last_pk = {upper_pk}, rows_completed = {int(job[2]) + orphan_rows}, "
                    f"updated_at = NOW() WHERE job_id = '{self.job_id}'"
                )
            },
            thinking="只追加缺失的审计行并同步同一 job 的游标和计数，不重写已经提交的前三条 checkpoint。",
        )
        return int(job[2]) + orphan_rows, upper_pk, next_batch_no, int(job[3])

    def _public_archive_index(self) -> str | None:
        payload = self.execute(
            "execute_sql",
            {"sql_query": f"SHOW INDEX FROM {self.database}.{self.orders_table}"},
            thinking="确认在线 schema change 当前是否已经收敛为 public，并读取实际索引名。",
        )
        if payload.get("status") not in {"success", "ok"}:
            raise RuntimeError(f"BC03 mock SHOW INDEX failed: payload={payload!r}")
        columns = tuple(str(column).casefold() for column in payload["columns"])
        positions = {column: index for index, column in enumerate(columns)}
        required = {"key_name", "seq_in_index", "column_name", "visible"}
        missing = required - positions.keys()
        if missing:
            raise RuntimeError(
                "BC03 mock SHOW INDEX response is missing required columns: "
                f"missing={sorted(missing)!r}, columns={columns!r}"
            )
        indexes = {}
        for row in payload["result"]:
            name = str(row[positions["key_name"]])
            index = indexes.setdefault(name, {"visible": False, "columns": []})
            index["visible"] = str(row[positions["visible"]]).casefold() in {"yes", "1", "true"}
            index["columns"].append(
                (
                    int(row[positions["seq_in_index"]]),
                    str(row[positions["column_name"]]).casefold(),
                )
            )
        required_columns = tuple(column.casefold() for column in self.index_columns)
        for name, index in indexes.items():
            columns = tuple(column for _, column in sorted(index["columns"]))
            if index["visible"] and columns[: len(required_columns)] == required_columns:
                return name
        return None

    def _create_archive_index(self) -> str:
        ddl = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"ALTER TABLE {self.database}.{self.orders_table} ADD INDEX idx_{self.job_id.replace('-', '_')} "
                    f"({', '.join(self.index_columns)})"
                )
            },
            thinking="归档事务完成后只提交一次在线索引请求；若客户端先超时，按 DDL 状态继续观察已有任务。",
        )
        if ddl.get("status") not in {"success", "ok"}:
            ddl_jobs = self.execute(
                "execute_sql",
                {"sql_query": "ADMIN SHOW DDL JOBS 30"},
                thinking="在线 DDL 客户端返回异常后，先检查已有 schema change 任务，不能重复提交同一索引。",
            )
            if ddl_jobs.get("status") not in {"success", "ok"}:
                raise RuntimeError(f"BC03 mock DDL status query failed: payload={ddl_jobs!r}")
        for attempt in range(self.INDEX_POLL_ATTEMPTS):
            index_name = self._public_archive_index()
            if index_name is not None:
                return index_name
            if attempt + 1 == self.INDEX_POLL_ATTEMPTS:
                raise RuntimeError(
                    "BC03 archive index did not become public after observing the submitted DDL: "
                    f"attempts={self.INDEX_POLL_ATTEMPTS}"
                )
            time.sleep(self.INDEX_POLL_SECONDS)
        raise RuntimeError("BC03 archive index polling exited without a result")

    def _next_order_page(self, lower_pk: int) -> tuple[int, int, int]:
        page_size = 4000 if self.transaction_shape == "ordered_limit" else 3000
        payload = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT MIN(order_id), MAX(order_id), COUNT(*) FROM ("
                    f"SELECT o.order_id FROM {self.database}.{self.orders_table} AS o "
                    "WHERE o.order_id > "
                    f"{lower_pk} AND o.retention_class = 'EXPIRED' AND o.archive_state = 'LIVE' "
                    f"AND EXISTS (SELECT 1 FROM {self.database}.{self.job_table} AS j "
                    f"JOIN {self.database}.{self.policy_table} AS p "
                    "ON p.policy_id = j.policy_id AND p.scope_id = j.scope_id "
                    f"JOIN {self.database}.{self.scope_table} AS s "
                    "ON s.scope_id = p.scope_id AND s.tenant_id = o.tenant_id "
                    "AND s.scope_state = 'APPROVED' "
                    f"WHERE j.job_id = '{self.job_id}' AND p.object_name = '{self.orders_table}' "
                    "AND p.state = 'APPROVED') "
                    f"AND NOT EXISTS (SELECT 1 FROM {self.database}.{self.hold_table} AS h "
                    "WHERE h.order_id = o.order_id AND h.hold_state = 'ACTIVE') "
                    f"ORDER BY order_id LIMIT {page_size}"
                    ") AS next_archive_page"
                )
            },
            thinking="根据当前剩余的业务目标取下一页，使用实际返回的订单边界推进恢复进度。",
        )
        row = payload["result"][0]
        count = int(row[2] or 0)
        if count == 0:
            return (0, 0, 0)
        if row[0] is None or row[1] is None:
            raise RuntimeError(f"BC03 next archive page has no bounds for count={count}: row={row!r}")
        return int(row[0]), int(row[1]), count

    def _archive_page(self, lower_pk: int, upper_pk: int, expected_count: int) -> int:
        target = (
            "o.retention_class = 'EXPIRED' AND o.archive_state = 'LIVE' "
            f"AND EXISTS (SELECT 1 FROM {self.database}.{self.job_table} AS j "
            f"JOIN {self.database}.{self.policy_table} AS p "
            "ON p.policy_id = j.policy_id AND p.scope_id = j.scope_id "
            f"JOIN {self.database}.{self.scope_table} AS s "
            "ON s.scope_id = p.scope_id AND s.tenant_id = o.tenant_id "
            "AND s.scope_state = 'APPROVED' "
            f"WHERE j.job_id = '{self.job_id}' AND p.object_name = '{self.orders_table}' "
            "AND p.state = 'APPROVED') "
            f"AND NOT EXISTS (SELECT 1 FROM {self.database}.{self.hold_table} AS h "
            "WHERE h.order_id = o.order_id AND h.hold_state = 'ACTIVE')"
        )
        if self.transaction_shape == "ordered_limit":
            sql = (
                f"UPDATE {self.database}.{self.orders_table} AS o SET archive_state = 'ARCHIVED', "
                f"archive_batch = '{self.job_id}', archived_at = NOW() "
                f"WHERE {target} ORDER BY o.order_id LIMIT 4000"
            )
        else:
            sql = (
                f"UPDATE {self.database}.{self.orders_table} AS o SET archive_state = 'ARCHIVED', "
                f"archive_batch = '{self.job_id}', archived_at = NOW() "
                f"WHERE o.order_id > {lower_pk} AND o.order_id <= {upper_pk} AND {target}"
            )
        payload = self.execute(
            "execute_sql",
            {"sql_query": sql},
            thinking="提交当前业务页并立即提交事务，让结算服务能够继续处理后续订单。",
        )
        affected = int(payload["row_count"])
        if affected != expected_count:
            raise RuntimeError(
                "BC03 archive page changed between selection and update: "
                f"shape={self.transaction_shape!r}, lower_pk={lower_pk}, upper_pk={upper_pk}, "
                f"expected={expected_count}, affected={affected}"
            )
        return affected

    def solve(self):
        self.execute(
            "query_metrics",
            {"metric_type": "query_latency", "target": None},
            thinking="先确认集群前台延迟窗口，避免把变更吞吐当成唯一目标。",
        )
        self.execute(
            "query_metrics",
            {"metric_type": "query_latency", "target": None},
            thinking="确认前台延迟仍在可接受窗口，避免把变更吞吐当成唯一目标。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT SESSION_ID, START_TIME, STATE, USER, DB "
                    "FROM INFORMATION_SCHEMA.CLUSTER_TIDB_TRX "
                    "ORDER BY START_TIME, SESSION_ID LIMIT 80"
                )
            },
            thinking="读取当前事务列表，确认结算业务确实在订单归档前持有事务，而不是只凭延迟猜测。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT ID, DB, STATE, INFO "
                    "FROM INFORMATION_SCHEMA.CLUSTER_PROCESSLIST ORDER BY ID LIMIT 200"
                )
            },
            thinking="把事务身份和全局进程状态关联起来，区分结算业务、前台请求和普通观察连接。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT job_id, object_name, scope_predicate, state, last_pk, rows_completed, "
                    "target_rows, ddl_index_name, error_text "
                    f"FROM {self.database}.{self.job_table} ORDER BY updated_at DESC"
                )
            },
            thinking="从历史失败、暂停和并行作业中锁定本次 live change contract。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT policy_id, object_name, cutoff_days, state, scope_id "
                    f"FROM {self.database}.{self.policy_table} ORDER BY policy_id"
                )
            },
            thinking="核对批准的 retention policy 与当前作业的合法目标范围。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT scope_id, tenant_id, scope_state "
                    f"FROM {self.database}.{self.scope_table} "
                    "ORDER BY scope_id, tenant_id"
                )
            },
            thinking="沿当前策略绑定读取公开租户范围，区分本次批准租户和延期租户。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT hold_state, COUNT(*), MIN(order_id), MAX(order_id) "
                    f"FROM {self.database}.{self.hold_table} "
                    "GROUP BY hold_state ORDER BY hold_state"
                )
            },
            thinking="按保护状态汇总公开订单保护登记，确认 ACTIVE 会阻止归档而 RELEASED 仍是可归档历史。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT MIN(o.order_id), MAX(o.order_id), COUNT(*) "
                    f"FROM {self.database}.{self.orders_table} AS o "
                    "WHERE o.retention_class = 'EXPIRED' "
                    f"AND EXISTS (SELECT 1 FROM {self.database}.{self.job_table} AS j "
                    f"JOIN {self.database}.{self.policy_table} AS p "
                    "ON p.policy_id = j.policy_id AND p.scope_id = j.scope_id "
                    f"JOIN {self.database}.{self.scope_table} AS s "
                    "ON s.scope_id = p.scope_id AND s.tenant_id = o.tenant_id "
                    "AND s.scope_state = 'APPROVED' "
                    f"WHERE j.job_id = '{self.job_id}' "
                    f"AND j.object_name = '{self.orders_table}' AND p.object_name = '{self.orders_table}' "
                    "AND p.state = 'APPROVED') "
                    f"AND NOT EXISTS (SELECT 1 FROM {self.database}.{self.hold_table} AS h "
                    "WHERE h.order_id = o.order_id AND h.hold_state = 'ACTIVE')"
                )
            },
            thinking="把 job、策略、租户范围和活动保护记录合并成当前变更的真实订单集合。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"SHOW INDEX FROM {self.database}.{self.orders_table}"},
            thinking="确认当前归档访问路径和已有索引，避免把历史索引状态误当成本次变更结果。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "ADMIN SHOW DDL JOBS 30"},
            thinking="读取当前在线 schema change 状态，区分本次索引请求和并行历史任务。",
        )
        rows_completed, lower_pk, batch_no, target_rows = self._reconcile_interrupted_state()
        self.execute(
            "execute_sql",
            {"sql_query": "SET SESSION tidb_txn_mode = 'PESSIMISTIC'"},
            thinking="恢复审计状态后继续使用真实业务常见的悲观事务语义，让剩余目标上的锁冲突在写入阶段暴露。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SET SESSION innodb_lock_wait_timeout = 0"},
            thinking="把当前归档会话配置为遇到已被结算占用的订单时立即返回，让真实冲突及时反馈并保留后续重试机会。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "BEGIN PESSIMISTIC"},
            thinking="开始一次归档事务，观察它与正在处理订单的结算事务如何相遇。",
        )
        first_attempt = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"UPDATE {self.database}.{self.orders_table} AS o SET archive_state = 'ARCHIVED', "
                    f"archive_batch = '{self.job_id}', archived_at = NOW() "
                    f"WHERE o.order_id > {lower_pk} AND o.retention_class = 'EXPIRED' AND o.archive_state = 'LIVE' "
                    f"AND EXISTS (SELECT 1 FROM {self.database}.{self.job_table} AS j "
                    f"JOIN {self.database}.{self.policy_table} AS p "
                    "ON p.policy_id = j.policy_id AND p.scope_id = j.scope_id "
                    f"JOIN {self.database}.{self.scope_table} AS s "
                    "ON s.scope_id = p.scope_id AND s.tenant_id = o.tenant_id "
                    "AND s.scope_state = 'APPROVED' "
                    f"WHERE j.job_id = '{self.job_id}' AND p.object_name = '{self.orders_table}' "
                    "AND p.state = 'APPROVED') "
                    f"AND NOT EXISTS (SELECT 1 FROM {self.database}.{self.hold_table} AS h "
                    "WHERE h.order_id = o.order_id AND h.hold_state = 'ACTIVE')"
                )
            },
            thinking="恢复后的剩余目标仍有结算事务占用，先按业务范围尝试一次归档写入，根据真实返回调整执行方式。",
        )
        if first_attempt.get("status") in {"success", "ok"}:
            raise RuntimeError(
                "BC03 mock expected the first pessimistic archive transaction to hit settlement, "
                f"but it succeeded: result={first_attempt!r}"
            )
        self.execute(
            "execute_sql",
            {"sql_query": "ROLLBACK"},
            thinking="首个事务已因业务锁竞争失败，先回滚未完成事务，再根据错误反馈换成可恢复的短事务。",
        )
        self._observe_business_conflict()

        rows_completed, lower_pk = self._archive_remaining_batches(
            rows_completed, lower_pk, batch_no, target_rows
        )
        self._close_out_change(rows_completed, lower_pk)
        return {"report": PASS_REPORT}

    def _archive_remaining_batches(self, rows_completed: int, lower_pk: int, batch_no: int, target_rows: int):
        while True:
            page_lower_pk, upper_pk, expected_count = self._next_order_page(lower_pk)
            if expected_count == 0:
                break
            if page_lower_pk <= lower_pk:
                raise RuntimeError(
                    "BC03 archive page did not advance the cursor: "
                    f"lower_pk={lower_pk}, page_lower_pk={page_lower_pk}, upper_pk={upper_pk}"
                )
            batch_no += 1
            affected = self._archive_page(lower_pk, upper_pk, expected_count)
            rows_completed += affected
            p95_ms = self._wait_for_foreground_slo()
            self.execute(
                "execute_sql",
                {
                    "sql_query": (
                    f"INSERT INTO {self.database}.{self.batch_table} "
                        "(job_id, batch_no, lower_pk, upper_pk, affected_rows, observed_p95_ms, recorded_at) "
                    f"VALUES ('{self.job_id}', {batch_no}, {lower_pk}, {upper_pk}, "
                        f"{affected}, {p95_ms:.3f}, NOW()); "
                        f"UPDATE {self.database}.{self.job_table} SET state = 'RUNNING', "
                        f"last_pk = {upper_pk}, rows_completed = {rows_completed}, updated_at = NOW() "
                        f"WHERE job_id = '{self.job_id}'"
                    )
                },
                thinking="持久化本批上下界、实际影响行数和真实前台 p95，再推进可恢复游标。",
            )
            lower_pk = upper_pk

        if rows_completed != target_rows:
            raise RuntimeError(f"BC03 archive completed an unexpected target count: rows_completed={rows_completed}")
        return rows_completed, lower_pk

    def _close_out_change(self, rows_completed: int, lower_pk: int) -> None:
        index_name = self._create_archive_index()

        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"UPDATE {self.database}.{self.job_table} SET state = 'SUCCEEDED', "
                    f"last_pk = {lower_pk}, "
                    f"rows_completed = {rows_completed}, ddl_index_name = '{index_name}', "
                    f"error_text = '', updated_at = NOW() WHERE job_id = '{self.job_id}'"
                )
            },
            thinking="全部连续窗口完成后才把 change job 标记为 SUCCEEDED，并记录已完成的在线索引。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT archive_state, retention_class, COUNT(*), "
                    f"SUM(archive_batch = '{self.job_id}'), SUM(archived_at IS NOT NULL) "
                    f"FROM {self.database}.{self.orders_table} GROUP BY archive_state, retention_class "
                    "ORDER BY archive_state, retention_class"
                )
            },
            thinking="复核目标与非目标行的最终归档状态和变更元数据。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT job_id, state, last_pk, rows_completed, target_rows, ddl_index_name "
                    f"FROM {self.database}.{self.job_table} WHERE job_id = '{self.job_id}'; "
                    "SELECT batch_no, lower_pk, upper_pk, affected_rows, observed_p95_ms "
                    f"FROM {self.database}.{self.batch_table} WHERE job_id = '{self.job_id}' ORDER BY batch_no"
                )
            },
            thinking="复核可恢复 job 和完整连续 checkpoint 链。",
        )
        self._public_archive_index()
        self._wait_for_foreground_slo()
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
                    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, customer_id, status, amount, "
                    f"retention_class, payload))), 0) FROM {self.database}.{self.orders_table}"
                )
            },
            thinking="最终校验不可变业务列的 count、主键和与 CRC。",
        )


class Bc03SettlementCompactMockAgent(Bc03FullMockAgent):
    """Easy settlement reference path: reconcile the interrupted job, then bounded batches."""

    def solve(self):
        self.execute(
            "query_metrics",
            {"metric_type": "query_latency", "target": None},
            thinking="先确认前台延迟窗口，为归档批次留下 SLO 基线。",
        )
        rows_completed, lower_pk, batch_no, target_rows = self._reconcile_interrupted_state()
        self.execute(
            "execute_sql",
            {"sql_query": "SET SESSION tidb_txn_mode = 'PESSIMISTIC'"},
            thinking="恢复审计状态后使用悲观事务语义执行有界归档批次。",
        )
        rows_completed, lower_pk = self._archive_remaining_batches(
            rows_completed, lower_pk, batch_no, target_rows
        )
        self._close_out_change(rows_completed, lower_pk)
        return {"report": PASS_REPORT}


def main() -> None:
    scenario = TidbBusinessChangeBatchedDmlDdlScenario()
    parser = argparse.ArgumentParser(description="Run TiDB BC03 batched DML/DDL under foreground SLO.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=70)
    parser.add_argument("--port", type=int, default=19000)
    parser.add_argument("--container-name", default="tidb-bc03")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="off")
    parser.add_argument("--cold-start-timeout", type=int, default=1200)
    parser.add_argument("--warm-start-timeout", type=int, default=300)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=300,
        tidb_readiness_timeout_sec=args.cold_start_timeout,
        warm_tidb_readiness_timeout_sec=args.warm_start_timeout,
    )
    if args.mode == "mock":
        agent_id = os.environ.get("AIOPS_AGENT_ID", "mock")
        transaction_shape = {"mock": "ordered_limit", "mock_alt": "keyset"}.get(agent_id)
        if transaction_shape is None:
            raise ValueError(
                "BC03 mock requires AIOPS_AGENT_ID=mock or mock_alt: "
                f"agent_id={agent_id!r}"
            )
        agent = (Bc03SettlementCompactMockAgent if case.case_no == 1 else Bc03FullMockAgent)(
            transaction_shape, case
        )
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)

    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (None, True, True):
            raise RuntimeError(
                "BC03 mock must pass N/A/True/True: "
                f"observed={observed!r}, result={result!r}"
            )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
