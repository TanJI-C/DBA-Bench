import argparse
from datetime import datetime, timezone
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbSystemFailureSf02Scenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


SCENARIO = TidbSystemFailureSf02Scenario()


def _condition(factor: str, entity: str, evidence: str) -> dict:
    return {
        "type": "root_cause",
        "factor": factor,
        "entity": entity,
        "evidence": [evidence],
    }


def build_full_pass_report(case, target_node: str, target_store_id: int) -> dict:
    return {
        "report": {
            "diagnosis": {
                "conditions": [
                    _condition(
                        "The named target settlement transaction committed after its ordinary 2PC lock TTL window and returned TiDB error 8022 / TxnLockNotFound; the current row is not an ordinary 9007 conflict or a persistent blocker.",
                        target_node,
                        f"target_store_id={target_store_id}; target attempt is scope=target and final_state=commit_failed",
                    ),
                    _condition(
                        "The failed transaction's primary table and key are in sf02_settlement_payload_b; its primary Region leader or peer set intersects the degraded Store, while the orders Region is a healthy sibling and cannot identify the target by itself.",
                        target_node,
                        "target primary table/key and payload_b Region peer/leader map to the degraded Store; orders Region is a healthy sibling",
                    ),
                    _condition(
                        "The target Store has a Store-scoped storage I/O limiter and persistence tail in the target transaction window; the deferred near Store can have the same cap without owning the target primary Region, so the incident is local rather than cluster-wide.",
                        target_node,
                        "target and near Store config history, disk_io, query latency and Store log overlap the target window",
                    ),
                    _condition(
                        "The target Store's write, Raft, or apply persistence tail begins before the 3 second TTL renewal deadline and overlaps the target primary transaction, explaining why the foreground path cannot persist and acknowledge the lock heartbeat in time.",
                        target_node,
                        "target persistence tail begins before the lock_ttl_ms=3000 deadline and overlaps the primary attempt",
                    ),
                    _condition(
                        "The primary lock heartbeat was not renewed before TTL expiry, then the lock reaper acquired the same payload_b primary key and committed before the target commit returned 8022.",
                        target_node,
                        "lock_ttl_events/attempt phase shows reaper_after_ttl before the target 8022 commit_failed row",
                    ),
                    _condition(
                        "The failed named settlement attempt rolled back its order, payload, and job writes; recovery requires restoring the exact Store path and retrying only the target settlement business transaction, not manually writing attempt or ledger rows or skipping the update.",
                        case.target_job_id,
                        "target order, payload workset, and job were baseline after rollback and the retry writes are scoped to the named job",
                    ),
                ]
            },
            "outcome": {
                "changes": [
                    f"restored the original storage.io-rate-limit on {target_node}",
                    f"retried {case.target_job_id} for order {case.target_order_id} with the requested delta",
                    "recorded one applied settlement ledger entry",
                ],
                "verification": [
                    "the target Store configuration exactly matches its pre-fault configuration",
                    "the business Region has three Up peers and a valid leader",
                    "the target order is settled with the requested amount and retry payload",
                    "the target job is committed and all decoy tables and non-target Store configs are unchanged",
                    "the business count, amount sum, and BIT_XOR(row_crc) match the expected post-settlement checksum",
                ],
            },
            "summary": (
                "A single TiKV Store write-I/O throttle delayed Raft/apply persistence and lost the target "
                "ordinary 2PC lock TTL renewal. The exact Store was restored before the settlement was retried "
                "and the business invariants were checked."
            ),
        }
    }


class Sf02FullPassMockAgent(MockLLMAgent):
    def __init__(self, case, **kwargs):
        super().__init__(**kwargs)
        self.case = case

    def solve(self):
        store_payload = self.execute(
            "manage_cluster",
            {"resource": "store", "operation": "list"},
            thinking="先查看原始 Store 状态，再把业务 Region、事务窗口和单节点运行时配置分别关联起来。",
        )
        if store_payload.get("status") != "success":
            raise RuntimeError(f"SF02 mock Store observation failed: result={store_payload!r}")
        stores = store_payload["result"]["stores"]
        if len(stores) != 4:
            raise RuntimeError(f"SF02 mock expected exactly four TiKV Stores including deferred near: stores={stores!r}")
        attempts_payload = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT attempt_id, scope, order_id, error_code, elapsed_ms, "
                    f"error_text, start_ts, commit_ts, lock_ttl_ms, primary_table, primary_key_value, "
                    f"primary_key_hash, lock_heartbeat_ts, renewal_count, reaper_ts, phase, final_state, observed_at "
                    f"FROM {self.case.db}.{self.case.attempt_table} "
                    "ORDER BY observed_at DESC, attempt_id DESC LIMIT 48"
                )
            },
            thinking="读取事务尝试记录，确认失败状态、业务 primary key 和锁 TTL，而不是接受一个汇总事故快照。",
        )
        if attempts_payload.get("status") != "success":
            raise RuntimeError(f"SF02 mock transaction observation failed: result={attempts_payload!r}")
        attempts = [
            dict(zip(attempts_payload["columns"], row))
            for row in attempts_payload["result"]
        ]
        retry_plan_payload = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT job_id, order_id, requested_delta, workset_rows, payload_event_start, "
                    f"payload_event_end, order_status, job_state, order_payload, payload_prefix, "
                    f"payload_state, order_row_crc, order_crc_rule, payload_crc_rule, ledger_state, "
                    f"retry_strategy FROM {self.case.db}.{self.case.retry_plan_table} "
                    f"WHERE job_id='{self.case.target_job_id}'"
                )
            },
            thinking="读取公开的 settlement retry plan 和表约束，按业务契约构造重试，不反推隐藏 CRC 真值。",
        )
        if retry_plan_payload.get("status") != "success" or len(retry_plan_payload.get("result", [])) != 1:
            raise RuntimeError(f"SF02 mock expected one public retry plan row: result={retry_plan_payload!r}")
        retry_plan = dict(zip(retry_plan_payload["columns"], retry_plan_payload["result"][0]))
        configs = {}
        for item in stores:
            target = f"tikv/{str(item['store']['address']).split(':', 1)[0]}"
            config_payload = self.execute(
                "manage_cluster",
                {"resource": "config", "operation": "get", "target": target},
                thinking="逐个读取 TiKV 运行时配置，避免把某个 Store 的状态预先标为故障目标。",
            )
            configs[target] = config_payload["result"]["storage"]["io_rate_limit"]
        target_attempts = [
            attempt
            for attempt in attempts
            if attempt["scope"] == "target"
        ]
        if len(target_attempts) != 1 or target_attempts[0]["final_state"] != "commit_failed":
            raise RuntimeError(f"SF02 mock expected one failed target attempt: attempts={target_attempts!r}")
        if target_attempts[0]["primary_table"] != self.case.payload_tables[1] or int(
            target_attempts[0]["primary_key_value"]
        ) != 1:
            raise RuntimeError(
                "SF02 mock expected the target attempt primary key to be payload_b event_id=1: "
                f"attempt={target_attempts[0]!r}"
            )

        regions_payload = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SHOW TABLE {self.case.db}.{self.case.payload_tables[1]} REGIONS"
                )
            },
            thinking="根据 attempt 的业务 primary key 在多个 payload_b key range 中选择物理 primary Region。",
        )
        if regions_payload.get("status") != "success":
            raise RuntimeError(f"SF02 mock payload_b Region observation failed: result={regions_payload!r}")
        regions = regions_payload["result"]
        if len(regions) != 4:
            raise RuntimeError(f"SF02 mock expected four payload_b Regions: regions={regions!r}")
        target_region_id = int(regions[0][0])
        target_store_id = int(regions[0][4])
        target_nodes = [
            f"tikv/{str(item['store']['address']).split(':', 1)[0]}"
            for item in stores
            if int(item["store"]["id"]) == target_store_id
        ]
        if len(target_nodes) != 1:
            raise RuntimeError(f"SF02 mock expected one target Store from primary attempt mapping: stores={stores!r}")
        target_node = target_nodes[0]
        near_nodes = [
            target
            for target, config in configs.items()
            if config["max-bytes-per-sec"] == "256KiB" and target != target_node
        ]
        if len(near_nodes) != 1:
            raise RuntimeError(f"SF02 mock expected one same-cap deferred near Store: configs={configs!r}")
        if int(next(item["store"]["id"] for item in stores if item["store"]["address"].startswith(target_node.rsplit("/", 1)[1]))) != target_store_id:
            raise RuntimeError(
                f"SF02 mock target Store mismatch: target_node={target_node!r}, "
                f"target_store_id={target_store_id}, stores={stores!r}"
            )

        config_history_payload = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT store_node, store_id, max_bytes_per_sec, mode, strict_mode, observed_ts_ms "
                    f"FROM {self.case.db}.sf02_store_config_history ORDER BY observed_ts_ms, history_id"
                )
            },
            thinking="读取所有 Store 的原始配置样本和时间，和 Region、事务窗口及运行时指标交叉关联。",
        )
        if config_history_payload.get("status") != "success":
            raise RuntimeError(
                f"SF02 mock config history observation failed: result={config_history_payload!r}"
            )
        history_columns = config_history_payload["columns"]
        history_rows = [dict(zip(history_columns, row)) for row in config_history_payload["result"]]
        observed_store_ids = {int(row["store_id"]) for row in history_rows}
        expected_store_ids = {int(item["store"]["id"]) for item in stores}
        if not expected_store_ids <= observed_store_ids:
            raise RuntimeError(
                "SF02 mock expected raw config samples for every Store: "
                f"expected={sorted(expected_store_ids)!r}, observed={sorted(observed_store_ids)!r}"
            )
        fault_active_ms = int(target_attempts[0]["lock_heartbeat_ts"])
        reaper_ms = int(target_attempts[0]["reaper_ts"])
        latency_start = datetime.fromtimestamp(
            (fault_active_ms - 1000) / 1000,
            tz=timezone.utc,
        ).strftime("%Y-%m-%d %H:%M:%S")
        latency_end = datetime.fromtimestamp(
            (reaper_ms + 6000) / 1000,
            tz=timezone.utc,
        ).strftime("%Y-%m-%d %H:%M:%S")
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT REGION_ID, STORE_ID, IS_LEADER, STATUS, DOWN_SECONDS "
                    "FROM INFORMATION_SCHEMA.TIKV_REGION_PEERS ORDER BY REGION_ID, STORE_ID"
                )
            },
            thinking="交叉核对 payload primary 和 orders sibling 的三副本、leader 与 peer 健康状态。",
        )
        self.execute(
            "query_metrics",
            {"metric_type": "disk_io", "target": target_node},
            thinking="对比目标 Store 与其它 Store 的真实 I/O 时序，而不是只看一次提交错误。",
        )
        latency_payload = self.execute(
            "query_metrics",
            {"metric_type": "disk_io", "target": near_nodes[0]},
            thinking="检查同 cap 的 deferred near Store 是否拥有 target primary Region 和同一提交重叠。",
        )
        self.execute(
            "query_metrics",
            {
                "metric_type": "query_latency",
                "start_timestamp": latency_start,
                "end_timestamp": latency_end,
            },
            thinking="确认提交窗口附近的 TiDB 请求长尾与事务失败窗口重叠。",
        )
        if latency_payload.get("status") != "success":
            raise RuntimeError(f"SF02 mock latency observation failed: result={latency_payload!r}")
        self.execute(
            "read_log",
            {"target": target_node, "lines": 80},
            thinking="读取目标 TiKV 日志，补充 Store 侧慢请求和锁清理证据。",
        )
        if configs[target_node]["max-bytes-per-sec"] != "256KiB":
            raise RuntimeError(
                "SF02 mock expected the target Store to retain the injected same-cap limiter before repair: "
                f"target={target_node!r}, config={configs[target_node]!r}"
            )
        repair = self.execute(
            "manage_cluster",
            {
                "resource": "config",
                "operation": "update",
                "target": target_node,
                "parameters": {
                    "key": "storage.io-rate-limit.max-bytes-per-sec",
                    "value": 0,
                },
            },
            thinking="只恢复由 Region/Store/I/O 证据共同定位出的一个目标 Store 原始 I/O 配置。",
        )
        if repair.get("status") != "success":
            raise RuntimeError(f"SF02 mock Store config repair failed: target={target_node!r}, result={repair!r}")
        payload_updates = []
        for table_index, table in enumerate(self.case.payload_tables, start=1):
            payload_expr = (
                f"CONCAT('{retry_plan['payload_prefix']}', '-', {table_index}, '-', "
                f"LPAD(event_id, 4, '0'))"
            )
            crc_expr = (
                f"CRC32(CONCAT({table_index}, ':', event_id, ':', {payload_expr}, "
                f"':{retry_plan['payload_state']}'))"
            )
            payload_updates.append(
                f"UPDATE {self.case.db}.{table} SET payload={payload_expr}, row_crc={crc_expr}, "
                f"state='{retry_plan['payload_state']}' "
                f"WHERE event_id BETWEEN {retry_plan['payload_event_start']} AND {retry_plan['payload_event_end']};"
            )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "START TRANSACTION; "
                    f"UPDATE {self.case.db}.{self.case.business_table} "
                    f"SET amount=amount+{retry_plan['requested_delta']}, status='{retry_plan['order_status']}', "
                    f"row_crc={retry_plan['order_row_crc']}, payload='{retry_plan['order_payload']}' "
                    f"WHERE order_id={retry_plan['order_id']}; "
                    + " ".join(payload_updates)
                    + " "
                    f"UPDATE {self.case.db}.{self.case.job_table} SET state='{retry_plan['job_state']}', "
                    f"retry_strategy='{retry_plan['retry_strategy']}' "
                    f"WHERE job_id='{retry_plan['job_id']}' AND order_id={retry_plan['order_id']}; "
                    f"INSERT INTO {self.case.db}.{self.case.ledger_table} "
                    "(job_id, order_id, delta, state) VALUES "
                    f"('{retry_plan['job_id']}', {retry_plan['order_id']}, {retry_plan['requested_delta']}, "
                    f"'{retry_plan['ledger_state']}'); "
                    "COMMIT"
                )
            },
            thinking="恢复 Store 后以一个有边界的事务重试订单、关闭目标任务并写入一条 ledger，保留所有 decoy。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT o.order_id, o.amount, o.status, o.row_crc, j.state, "
                    f"COUNT(l.ledger_id) FROM {self.case.db}.{self.case.business_table} o "
                    f"JOIN {self.case.db}.{self.case.job_table} j ON j.order_id=o.order_id "
                    f"LEFT JOIN {self.case.db}.{self.case.ledger_table} l ON l.job_id=j.job_id "
                    f"WHERE o.order_id={self.case.target_order_id} AND j.job_id='{self.case.target_job_id}' "
                    "GROUP BY o.order_id, o.amount, o.status, o.row_crc, j.state"
                )
            },
            thinking="提交前后分别复核目标业务行、任务和 ledger 关系，避免只看 SQL 成功返回。",
        )
        self.execute(
            "manage_cluster",
            {"resource": "service", "operation": "list"},
            thinking="最终确认三个 TiKV Store 仍然可用，修复没有扩大故障范围。",
        )
        target_store_id = int(target_store_id)
        return build_full_pass_report(self.case, target_node, target_store_id)


def main() -> None:
    parser = argparse.ArgumentParser(description=SCENARIO.description)
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--llm-config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--port", type=int, default=4700)
    parser.add_argument("--container-name", default="tidb-sf02-slow-store")
    args = parser.parse_args()
    if args.mode == "llm" and not args.model:
        raise ValueError("--model is required when --mode=llm")

    case = SCENARIO.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=300,
    )
    if args.mode == "mock":
        agent = Sf02FullPassMockAgent(
            case,
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB storage reliability DBA.",
            use_native_tools=False,
        )
    else:
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.llm_config,
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
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (True, True, True):
            raise AssertionError(
                f"SF02 mock path must pass DP/OP/SP: observed={observed!r}, result={json.dumps(result, ensure_ascii=False)}"
            )
    print(f"Final result: {json.dumps(result, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
