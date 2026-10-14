import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb import TidbSystemFailureClusteredIndexConsistencyScenario


SCENARIO = TidbSystemFailureClusteredIndexConsistencyScenario()
CASE_ID = "odku_mutable_clustered_pk_index_drift"


def _action(api: str, **args):
    return {"api": api, "args": args}


def _release(operation: str, **args):
    return _action("manage_cluster", resource="release", operation=operation, **args)


def _sql(sql_query: str, **args):
    return _action("execute_sql", sql_query=sql_query, **args)


def _odku(case, account_id: int, state_ts: str, version: int):
    return (
        f"INSERT INTO {case.database}.{case.target_table} "
        "(account_id, state_ts, status, balance_cents, version) "
        f"VALUES ({account_id}, '{state_ts}', '{case.seed_status}', {case.canary_balance_cents}, {version}) "
        "ON DUPLICATE KEY UPDATE "
        "status = VALUES(status), balance_cents = VALUES(balance_cents), version = VALUES(version)"
    )


def _read_current_state_ts(agent: BaseAgent, case) -> str:
    result = agent.execute(
        "execute_sql",
        {
            "sql_query": (
                f"SELECT state_ts FROM {case.database}.{case.target_table} "
                f"WHERE account_id = {case.explicit_canary_account_id} "
                "ORDER BY state_ts DESC LIMIT 1"
            )
        },
        thinking="读取刚刚写入的当前 clustered handle，下一次 ODKU 必须以它作为冲突键。",
    )
    if result["status"] != "success":
        raise RuntimeError(
            "K12 explicit canary could not read the current clustered handle: "
            f"account_id={case.explicit_canary_account_id}, result={result!r}"
        )
    rows = result["result"]
    if len(rows) != 1:
        raise RuntimeError(
            "K12 explicit canary expected exactly one current clustered handle: "
            f"account_id={case.explicit_canary_account_id}, rows={rows!r}"
        )
    return str(rows[0][0])


def _run_explicit_transaction_canary(agent: BaseAgent, case) -> None:
    agent.execute(
        "execute_sql",
        {"sql_query": "START TRANSACTION"},
        thinking="开始显式事务 canary，覆盖与历史事故不同的提交路径。",
    )
    state_ts = case.explicit_canary_timestamp
    for version in (1, 2, 3):
        result = agent.execute(
            "execute_sql",
            {
                "sql_query": _odku(
                    case,
                    case.explicit_canary_account_id,
                    state_ts,
                    version,
                )
            },
            thinking="在显式事务内重复 ODKU，写入后刷新 clustered handle，避免下一次写入继续使用旧主键。",
        )
        if result["status"] != "success":
            raise RuntimeError(
                "K12 explicit canary ODKU failed: "
                f"account_id={case.explicit_canary_account_id}, version={version}, result={result!r}"
            )
        state_ts = _read_current_state_ts(agent, case)
    agent.execute(
        "execute_sql",
        {"sql_query": "COMMIT"},
        thinking="提交显式事务 canary。",
    )


def _component_targets(case):
    topology = case.runtime.topology
    return (
        *(f"pd/pd-{index}" for index in range(topology.pd_count)),
        *(f"tikv/tikv-{index}" for index in range(topology.tikv_count)),
        *(f"tidb/tidb-{index}" for index in range(topology.tidb_count)),
    )


class ClusteredIndexConsistencyFullMockAgent(BaseAgent):
    def solve(self):
        case = SCENARIO.get_case(CASE_ID)
        self.execute(
            "manage_cluster",
            {"resource": "release", "operation": "get"},
            thinking="先确认当前集群 release，避免把组件不可用或版本问题误判为业务索引故障。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT VARIABLE_NAME, VARIABLE_VALUE FROM mysql.tidb "
                    "WHERE VARIABLE_NAME IN ('tidb_txn_assertion_level', 'tidb_enable_clustered_index') "
                    "ORDER BY VARIABLE_NAME"
                )
            },
            thinking="读取 assertion 和 clustered-index 变量的实际 scope，再判断它们只是检测条件还是历史修复。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": f"SHOW CREATE TABLE {case.database}.{case.target_table}",
            },
            thinking="确认目标列的 ON UPDATE CURRENT_TIMESTAMP、复合 clustered primary key 和二级索引结构。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME, NON_UNIQUE "
                    "FROM information_schema.statistics "
                    f"WHERE TABLE_SCHEMA='{case.database}' AND TABLE_NAME='{case.target_table}' "
                    "ORDER BY INDEX_NAME, SEQ_IN_INDEX"
                )
            },
            thinking="把二级索引列顺序与 clustered handle 的组成分开记录。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT event_id, account_id, event_state, event_kind, status, balance_cents, version "
                    f"FROM {case.database}.{case.ledger_table} ORDER BY event_id"
                )
            },
            thinking="先读取 append-only ledger 作为业务真值，不能把出现差异的某一条物理访问路径直接当成真值。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT account_id, state_ts, status, balance_cents, version FROM {case.database}.{case.target_table} "
                    "USE INDEX (PRIMARY) ORDER BY account_id, state_ts"
                )
            },
            thinking="读取 clustered primary path 的原始行和 handle 值。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT account_id, state_ts, status, balance_cents, version FROM {case.database}.{case.target_table} "
                    f"USE INDEX ({case.target_index}) ORDER BY account_id, state_ts"
                )
            },
            thinking="读取二级索引 path 并与 primary path 对比，不把 optimizer 选择当作一致性证明。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"ADMIN CHECK TABLE {case.database}.{case.target_table}"},
            thinking="使用官方一致性检查确认错误是否来自记录和索引维护，而不是普通查询缓存。",
        )
        self.execute(
            "read_log",
            {"target": "tidb/tidb-0", "lines": 120, "match_key": "8141"},
            thinking="查看 TiDB 可见日志中的 assertion 证据，保留 start/commit 线索但不依赖日志唯一定位。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SET GLOBAL tidb_txn_assertion_level = 'STRICT'"},
            thinking="提高后续事务的断言级别；这只能阻止新 drift，不能替代历史数据修复。",
        )
        for target in _component_targets(case):
            self.execute(
                "manage_cluster",
                {"resource": "release", "operation": "upgrade", "target": target},
                thinking=f"按 PD、TiKV、TiDB 顺序将 {target} 滚动升级到 fixed release，并让每个组件完成就绪检查。",
            )
        self.execute(
            "manage_cluster",
            {"resource": "release", "operation": "get"},
            thinking="升级后重新读取当前/目标 release，确认不是只替换单个 TiDB binary。",
        )
        self.execute(
            "manage_cluster",
            {"resource": "service", "operation": "list"},
            thinking="确认所有数据库组件仍然可用，再开始数据修复。",
        )
        for target in _component_targets(case):
            if target.startswith("tidb/"):
                self.execute(
                    "execute_sql",
                    {
                        "target": target,
                        "sql_query": "SELECT @@global.tidb_txn_assertion_level, @@session.tidb_txn_assertion_level",
                    },
                    thinking=f"在 {target} 建立 global/session assertion level 的 endpoint 证据。",
                )
        self.execute(
            "execute_sql",
            {
                "sql_query": f"ALTER TABLE {case.database}.{case.target_table} DROP INDEX {case.target_index}",
            },
            thinking="clustered record 是可依赖的 canonical 物理基准时，先删除受影响 secondary index。",
        )
        index_sql = (
            f"ALTER TABLE {case.database}.{case.target_table} "
            f"ADD INDEX {case.target_index} (account_id, status, state_ts)"
        )
        index_result = self.execute(
            "execute_sql",
            {"sql_query": index_sql},
            thinking="从当前 clustered records 重建全部受影响二级索引，不修改 append-only ledger。",
        )
        if index_result["status"] != "success":
            self.execute(
                "execute_sql",
                {"sql_query": index_sql},
                thinking="二级索引 DDL 返回明确错误后，重试同一个已授权的幂等重建操作。",
            )
        self.execute(
            "execute_sql",
            {"sql_query": f"ADMIN CHECK TABLE {case.database}.{case.target_table}"},
            thinking="第一次修复闭环检查：索引重建后官方 consistency check 必须成功。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT account_id, state_ts, status, balance_cents, version FROM {case.database}.{case.target_table} "
                    f"USE INDEX ({case.target_index}) ORDER BY account_id, state_ts"
                )
            },
            thinking="验证重建后的二级索引访问路径与 clustered path 返回同一业务行。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": f"SELECT * FROM {case.database}.{case.canary_plan_table} ORDER BY canary_id",
            },
            thinking="读取公开 canary contract，严格限定后续写入的 account、时间、路径和重复次数。",
        )
        for version in (1, 2):
            self.execute(
                "execute_sql",
                {
                    "sql_query": _odku(
                        case,
                        case.autocommit_canary_account_id,
                        case.autocommit_canary_timestamp,
                        version,
                    )
                },
                thinking="fixed release 下执行 autocommit ODKU canary，确认 handle 变化不会再产生 assertion 或 index drift。",
            )
        _run_explicit_transaction_canary(self, case)
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT account_id, status, balance_cents, version FROM {case.database}.{case.target_table} "
                    f"WHERE account_id IN ({case.autocommit_canary_account_id}, {case.explicit_canary_account_id}) "
                    "ORDER BY account_id"
                )
            },
            thinking="复核两个 canary 的业务列和版本。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"ADMIN CHECK TABLE {case.database}.{case.target_table}"},
            thinking="最终官方一致性检查覆盖历史 rows 和新 canary rows。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT event_id, account_id, event_state, status, balance_cents, version "
                    f"FROM {case.database}.{case.ledger_table} ORDER BY event_id"
                )
            },
            thinking="确认 append-only ledger 未被修复动作覆盖。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT account_id, state_ts, version FROM {case.database}.{case.healthy_nonclustered_table} "
                    "ORDER BY account_id"
                )
            },
            thinking="确认非 clustered 健康邻居未被误修复。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT account_id, state_ts, version FROM {case.database}.{case.healthy_no_odku_table} "
                    "ORDER BY account_id"
                )
            },
            thinking="确认没有 ODKU 的健康邻居未被误修复。",
        )
        return {"report": SCENARIO.get_case(CASE_ID).reference_report}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run TiDB K12 clustered primary-key and secondary-index consistency scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=60)
    parser.add_argument("--port", type=int, default=48640)
    parser.add_argument("--container-name", default="tidb-system-failure-k12")
    args = parser.parse_args()

    case = SCENARIO.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = ClusteredIndexConsistencyFullMockAgent()
    else:
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode="off",
        diagnosis_match_mode="semantic" if args.mode == "llm" else "exact",
        diagnosis_semantic_model=args.model,
        diagnosis_semantic_config_path=args.config_path,
    )
    result = Orchestrator(
        env,
        SCENARIO,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=run_config,
    ).run()
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
