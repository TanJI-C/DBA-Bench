import argparse
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.database.sql import sql_literal
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator
from src.scenarios.tidb import TidbHealthCheckLongTransactionMvccScenario


_TXN_START_TSO_RE = re.compile(r".*\((?P<tso>[0-9]+)\)$")


def _txn_start_tso(value: object) -> int:
    text = str(value)
    match = _TXN_START_TSO_RE.fullmatch(text)
    if match is None:
        raise ValueError(
            "HC09 expected CLUSTER_PROCESSLIST.TxnStart to end with "
            "a parenthesized numeric TSO: "
            f"value={value!r}"
        )
    return int(match.group("tso"))


def _retaining_sessions(history, checkpoints, registry, transactions):
    transaction_by_id = {int(row[0]): row for row in transactions}
    owner_by_worker = {int(row[0]): (int(row[7]), str(row[8]), str(row[9])) for row in registry}
    candidates = []
    for event in history:
        if str(event[4]) != "RELEASED":
            continue
        worker_id, session_id = int(event[1]), int(event[6])
        owner_session_id, checkpoint_stream, review_batch_id = owner_by_worker[worker_id]
        if session_id == owner_session_id:
            continue
        transaction = transaction_by_id[session_id]
        source_ids = {int(value) for value in str(transaction[2]).split(",")}
        sources = [row for row in checkpoints
                   if str(row[3]) == "COMMITTED" and str(row[5]) == checkpoint_stream
                   and str(row[7]) == review_batch_id and int(row[8]) in source_ids]
        if not sources:
            raise RuntimeError(f"HC09 released reader has no reviewed native source boundary: event={event!r}, transaction={transaction!r}")
        selected = max(sources, key=lambda row: int(row[4]))
        if int(transaction[1]) < int(selected[4]):
            candidates.append([session_id, worker_id, int(transaction[1]), int(selected[4])])
    return candidates


class HC09FullMockAgent(MockLLMAgent):
    def __init__(self, case):
        super().__init__(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA completing a structured health review.",
            use_native_tools=False,
        )
        self.case = case

    def _sql(self, sql_query: str, thinking: str):
        result = self.execute(
            "execute_sql",
            {"sql_query": sql_query},
            thinking=thinking,
        )
        if result.get("status") != "success":
            raise RuntimeError(
                f"HC09 reference SQL failed: sql={sql_query!r}, result={result!r}"
            )
        return result.get("result", [])

    def solve(self):
        transactions = self._sql(
            "SELECT SESSION_ID, ID, RELATED_TABLE_IDS "
            "FROM INFORMATION_SCHEMA.CLUSTER_TIDB_TRX "
            "ORDER BY ID, SESSION_ID",
            "先读取未过滤事务列表，确认历史版本窗口对应多组仍活动的 snapshot。",
        )
        expected_transaction_count = (
            len(self.case.worker_aliases)
            + 1
            + len(self.case.non_blocking_abandoned_worker_ids)
        )
        if len(transactions) < expected_transaction_count:
            raise RuntimeError(
                "HC09 reference returned too few transactions: "
                f"expected_at_least={expected_transaction_count}, rows={transactions!r}"
            )

        processlist = self._sql(
            "SELECT ID, SESSION_ALIAS, TxnStart, COMMAND "
            "FROM INFORMATION_SCHEMA.CLUSTER_PROCESSLIST "
            "ORDER BY ID LIMIT 200",
            "读取进程列表，把相似 worker alias、事务起点和仅有连接的历史会话区分开。",
        )
        expected_process_count = expected_transaction_count + len(self.case.historical_processlist_aliases)
        if len(processlist) < expected_process_count:
            raise RuntimeError(
                "HC09 reference returned too few named sessions: "
                f"expected_at_least={expected_process_count}, rows={processlist!r}"
            )

        registry = self._sql(
            self.case.lease_registry_sql,
            "检查当前 generation 的 worker registry，确认 current session 保护范围。",
        )
        history = self._sql(
            self.case.lease_history_sql,
            "读取 worker handoff history，找出状态相同但 session 不同的 abandoned 候选。",
        )
        checkpoints = self._sql(
            self.case.checkpoint_sql,
            "读取全部 checkpoint；按当前worker注册的业务stream选择source边界，按公开review_batch_id限定本次closed batch；publication先后不表示源提交顺序。",
        )
        counts = (len(registry), len(history), len(checkpoints))
        expected = (
            len(self.case.worker_aliases),
            self.case.history_row_count,
            self.case.checkpoint_row_count,
        )
        if counts != expected:
            raise RuntimeError(
                f"HC09 reference business evidence mismatch: expected={expected}, observed={counts}"
            )

        catalog = self._sql(
            f"SELECT TABLE_SCHEMA, TABLE_NAME, TIDB_TABLE_ID FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = {sql_literal(self.case.database)} ORDER BY TABLE_NAME",
            "读取完整业务schema原生catalog，将事务RELATED_TABLE_IDS与实际source/checkpoint关联。",
        )
        source_ids = {int(row[2]) for row in catalog if f"{row[0]}.{row[1]}" in self.case.qualified_business_tables}
        if any(int(row[8]) not in source_ids for row in checkpoints):
            raise RuntimeError(f"HC09 checkpoint references a non-business native source: catalog={catalog!r}, checkpoints={checkpoints!r}")
        candidates = _retaining_sessions(history, checkpoints, registry, transactions)
        if self.case.settled_source_table is not None:
            released_ids = {int(row[6]) for row in history if str(row[4]) == "RELEASED"}
            oldest = min((row for row in transactions if int(row[0]) in released_ids), key=lambda row: int(row[1]))
            if int(oldest[0]) in {int(row[0]) for row in candidates}:
                raise RuntimeError(f"HC09 oldest-unowned shortcut unexpectedly selects target: oldest={oldest!r}, candidates={candidates!r}")
            global_boundary = max(int(row[4]) for row in checkpoints)
            global_candidates = [row for row in transactions if int(row[0]) in released_ids and int(row[1]) < global_boundary]
            if len(global_candidates) != 2:
                raise RuntimeError(f"HC09 global cutoff must misclassify both source readers: candidates={global_candidates!r}")
        if len(candidates) != 1:
            raise RuntimeError(
                "HC09 reference expected exactly one pre-write abandoned session: "
                f"candidates={candidates!r}"
            )
        target_session_id = int(candidates[0][0])
        target_worker_id = int(candidates[0][1])
        review_batch = next(str(row[9]) for row in registry if int(row[0]) == target_worker_id)
        stream = next(str(row[8]) for row in registry if int(row[0]) == target_worker_id)
        target_sources = {int(value) for row in transactions if int(row[0]) == target_session_id for value in str(row[2]).split(",")}
        published_last = max(
            (row for row in checkpoints if int(row[8]) in target_sources
             and str(row[3]) == "COMMITTED" and str(row[5]) == stream
             and str(row[7]) == review_batch),
            key=lambda row: str(row[2]),
        )
        if int(candidates[0][2]) < int(published_last[4]):
            raise RuntimeError(
                "HC09 reference did not expose the latest-publication counterexample: "
                f"candidate={candidates[0]!r}, latest_publication={published_last!r}"
            )
        before_repair = self._sql(
            "SELECT DISTINCT ID, SESSION_ALIAS, TxnStart FROM INFORMATION_SCHEMA.CLUSTER_PROCESSLIST "
            f"WHERE ID = {target_session_id}",
            "确认仅阅读或采用最新publication仍留下真实候选；这是未修复反例。",
        )
        if len(before_repair) != 1:
            raise RuntimeError(f"HC09 no-op counterexample lost its live candidate: {before_repair!r}")
        self._sql(
            f"KILL TIDB CONNECTION {target_session_id}",
            "只结束唯一写入前 abandoned session，保留 current worker 和 post-write retry。",
        )

        aliases = self.case.worker_aliases + self.case.historical_processlist_aliases
        alias_sql = ",".join(f"'{alias}'" for alias in aliases)
        remaining = None
        for _ in range(10):
            remaining = self._sql(
                "SELECT ID, SESSION_ALIAS, TxnStart "
                "FROM INFORMATION_SCHEMA.CLUSTER_PROCESSLIST "
                f"WHERE SESSION_ALIAS IN ({alias_sql}) ORDER BY ID",
                "复核目标已经消失，同时保护集合仍完整。",
            )
            remaining_ids = {int(row[0]) for row in remaining}
            expected_remaining = len(self.case.worker_aliases) + len(self.case.non_blocking_abandoned_worker_ids) + len(self.case.historical_processlist_aliases)
            if target_session_id not in remaining_ids and len(remaining_ids) == expected_remaining:
                break
            time.sleep(0.2)
        else:
            raise RuntimeError(
                "HC09 reference repair did not converge to the expected session scope: "
                f"target_session_id={target_session_id}, expected_remaining={expected_remaining}, remaining={remaining!r}"
            )

        integrity = self._sql(
            self.case.integrity_sql,
            f"复核两类保护状态：每个源 {self.case.versioned_row_count} 行新版本，以及完整业务源总行数和 CRC。",
        )
        if len(integrity) != 1 or len(integrity[0]) != 3:
            raise RuntimeError(
                f"HC09 reference integrity result is invalid: rows={integrity!r}"
            )

        return {"report": self.case.reference_report}


def main():
    scenario = TidbHealthCheckLongTransactionMvccScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB HC09 long-transaction MVCC health-check scenario."
    )
    parser.add_argument(
        "--case",
        required=True,
        choices=[case.case_id for case in scenario.cases],
    )
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--port", type=int, default=4800)
    parser.add_argument("--container-name", default="tidb-health-check-hc09")
    args = parser.parse_args()

    if args.mode == "llm" and not args.model:
        raise ValueError("--model is required when --mode=llm")

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    agent = (
        HC09FullMockAgent(case)
        if args.mode == "mock"
        else build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    )
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        pretty_print=False,
        max_turns=args.max_turns,
    ).run()
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
