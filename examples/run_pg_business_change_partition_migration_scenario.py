import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.evaluation.base import evaluation_passed
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import (
    PgBusinessChangePartitionMigrationCase,
    PgBusinessChangePartitionMigrationScenario,
)
from src.scenarios.evaluation.config import add_diagnosis_arguments
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig

_CHILD_PARTITION_BOUNDS = {
    "payment_events_2026_07": ("2026-07-01", "2026-08-01"),
    "payment_events_2026_08": ("2026-08-01", "2026-09-01"),
}


def _child_bounds(child: str) -> tuple[str, str]:
    return _CHILD_PARTITION_BOUNDS[child]


def _activity_sql(case: PgBusinessChangePartitionMigrationCase) -> str:
    return (
        "SELECT pid, application_name, state, wait_event_type, wait_event, "
        "now() - xact_start AS xact_age, left(query, 140) AS last_query "
        "FROM pg_stat_activity WHERE datname = current_database() "
        "AND pid <> pg_backend_pid() ORDER BY pid;"
    )


def _lock_chain_sql(case: PgBusinessChangePartitionMigrationCase) -> str:
    return (
        "SELECT l.pid, a.application_name, l.locktype, l.mode, l.granted, "
        "left(a.query, 120) AS query "
        "FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid "
        "WHERE l.locktype = 'relation' AND a.datname = current_database() "
        "ORDER BY l.granted, l.pid;"
    )


def _own_session_excluded_lock_chain_sql(case: PgBusinessChangePartitionMigrationCase) -> str:
    # Same lock chain as `_lock_chain_sql` but without the agent's own session:
    # a lock-chain probe must not cite its own catalog locks as incident evidence.
    return (
        "SELECT l.pid, a.application_name, l.locktype, l.mode, l.granted, "
        "left(a.query, 120) AS query "
        "FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid "
        "WHERE l.locktype = 'relation' AND a.datname = current_database() "
        "AND l.pid <> pg_backend_pid() "
        "ORDER BY l.granted, l.pid;"
    )


def _blocking_sql(case: PgBusinessChangePartitionMigrationCase) -> str:
    return (
        "SELECT a.pid AS waiting_pid, a.application_name AS waiting_app, "
        "left(a.query, 120) AS waiting_query, pg_blocking_pids(a.pid) AS blockers "
        "FROM pg_stat_activity a "
        "WHERE a.wait_event_type = 'Lock' AND a.datname = current_database();"
    )


def build_full_score_mock_agent(case: PgBusinessChangePartitionMigrationCase):
    conflict_pred = (
        f"WHERE event_time >= '{case.conflict_bound_start}' "
        f"AND event_time < '{case.conflict_bound_end}'"
    )
    reconcile_sql = "\n".join(
        f"INSERT INTO {child} "
        "(payment_id, payment_ref, channel, amount, event_time, payload) "
        "SELECT payment_id, payment_ref, channel, amount, event_time, payload "
        f"FROM {case.default_partition} WHERE event_time >= '{start}' "
        f"AND event_time < '{end}' "
        f"AND payment_id NOT IN (SELECT payment_id FROM {child});\n"
        f"DELETE FROM {case.default_partition} WHERE event_time >= '{start}' "
        f"AND event_time < '{end}';"
        for child, (start, end) in (
            (child, _child_bounds(child)) for child in case.staging_children
        )
    )
    attach_sql = "\n".join(
        f"SET lock_timeout = '10s'; ALTER TABLE {case.parent_table} ATTACH PARTITION "
        f"{child} FOR VALUES FROM ('{start}') TO ('{end}');"
        for child, (start, end) in (
            (child, _child_bounds(child)) for child in case.staging_children
        )
    )
    verify_topology_sql = (
        "SELECT child.relname, child.relispartition, "
        "pg_get_expr(child.relpartbound, child.oid) AS bound "
        "FROM pg_inherits i "
        "JOIN pg_class child ON child.oid = i.inhrelid "
        f"WHERE i.inhparent = '{case.parent_table}'::regclass "
        "ORDER BY child.relname;"
    )
    if case.preflight_validation_attempt:
        mock_responses = [
            {
                "thinking": "业务停摆尖峰先看吞吐与连接水位，确认是否属于锁等待型停摆。",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "qps", "target": None}},
                    {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
                ],
            },
            {
                "thinking": "查看会话与锁链：找出谁在等待、谁持有阻塞锁。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": _activity_sql(case)}},
                    {"api": "execute_sql", "args": {"sql_query": _blocking_sql(case)}},
                    {"api": "execute_sql", "args": {"sql_query": _lock_chain_sql(case)}},
                ],
            },
            {
                "thinking": "迁移作业状态表记录了每次 ATTACH 的真实结果，先读它。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT attempt_id, step, status, detail, recorded_at FROM {case.job_status_table} ORDER BY attempt_id;"}},
                ],
            },
            {
                "thinking": "验证失败的根源在 default 分区的数据边界：统计落在待挂载区间内的行，与历史脏行区分，并核对上次中断作业在 staging 表留下的部分迁移残留与 in-doubt prepared 事务。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT count(*) AS conflict_rows FROM {case.default_partition} WHERE event_time >= '{case.conflict_bound_start}' AND event_time < '{case.conflict_bound_end}';"}},
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT count(*) AS legacy_dirty_rows FROM {case.default_partition} WHERE event_time < '2026-07-01';"}},
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT count(*) AS staging_residual_rows FROM {case.staging_children[-1]} WHERE event_time >= '{case.conflict_bound_start}' AND event_time < '{case.conflict_bound_end}';"}},
                    {"api": "execute_sql", "args": {"sql_query": "SELECT transaction, gid, prepared, owner FROM pg_prepared_xacts;"}},
                ],
            },
            {
                "thinking": "修复顺序：先结束阻塞链（长报表事务与已暂停的迁移会话）。重放仍超时说明还有无会话的锁持有者：用 pg_locks 的 pid 为空条目经虚拟事务关联 transactionid 锁与 pg_prepared_xacts 逐个定位 in-doubt 事务归属，再按台账语义推导各自方向——batch-2 被校验器否决（DELETE 行数 12000 vs 计划 4500）必须 ROLLBACK PREPARED 恢复误删行；batch-3 的重试 worker 已直接提交同 ref 批次，prepared 副本是重复副本，ROLLBACK PREPARED 丢弃；随后对 default 全部区间行做对账迁移——补入 staging、清空 default，保证数据不丢也不重复。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{case.report_application_name}' AND pid <> pg_backend_pid();"}},
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name LIKE '{case.worker_application_name}%' AND pid <> pg_backend_pid();"}},
                    {"api": "execute_sql", "args": {"sql_query": "ROLLBACK PREPARED '2pc-9f4c7a1e3d';"}},
                    {"api": "execute_sql", "args": {"sql_query": "ROLLBACK PREPARED '2pc-c7b25e8f40';"}},
                    {"api": "execute_sql", "args": {"sql_query": reconcile_sql}},
                ],
            },
            {
                "thinking": "数据边界已修复，重放 ATTACH PARTITION 完成改造，使用短 lock_timeout 防止再次排队停摆。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": attach_sql}},
                ],
            },
            {
                "thinking": "验证分区拓扑与 default 分区边界，并确认种子支付数据守恒。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": verify_topology_sql}},
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT count(*) AS remaining_conflict_rows FROM {case.default_partition} WHERE event_time >= '{case.conflict_bound_start}' AND event_time < '{case.conflict_bound_end}';"}},
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT count(*) AS seed_rows FROM (SELECT payment_ref FROM {case.legacy_table} WHERE payment_ref LIKE '{case.seed_ref_prefix}%' UNION ALL SELECT payment_ref FROM {case.parent_table} WHERE payment_ref LIKE '{case.seed_ref_prefix}%') s;"}},
                ],
            },
            {
                "thinking": "改造完成且数据守恒，提交结构化报告。",
                "actions": [{"api": "submit", "args": {"report": case.reference_report}}],
            },
        ]
    else:
        mock_responses = [
            {
                "thinking": "ATTACH 缓慢且查询偶发变慢，先看会话与锁链，找到阻塞 ATTACH 的事务。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": _activity_sql(case)}},
                    {"api": "execute_sql", "args": {"sql_query": _blocking_sql(case)}},
                    {"api": "execute_sql", "args": {"sql_query": _own_session_excluded_lock_chain_sql(case)}},
                ],
            },
            {
                "thinking": "迁移作业状态表记录了入账批次、搬行步骤与每次 ATTACH 的真实结果，先读它确认各会话与残留的来历。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT attempt_id, step, status, detail, recorded_at FROM {case.job_status_table} ORDER BY attempt_id;"}},
                ],
            },
            {
                "thinking": "重放 ATTACH 前先确认 default 分区在待挂载区间内没有数据，这是安全重放的前提。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT count(*) AS conflict_rows FROM {case.default_partition} WHERE event_time >= '{case.conflict_bound_start}' AND event_time < '{case.conflict_bound_end}';"}},
                ],
            },
            {
                "thinking": "default 分区无越界行。结束持锁的打开事务释放锁：长报表事务持有分区树 AccessShare，未提交的搬行会话持有 staging 表 RowExclusive，两者都阻塞 ATTACH 的 AccessExclusiveLock。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{case.report_application_name}' AND pid <> pg_backend_pid();"}},
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{case.backfill_application_name}' AND pid <> pg_backend_pid();"}},
                ],
            },
            {
                "thinking": "作业台账显示入账批次的 2PC attempt 1 还留在 prepared 状态，先在 pg_prepared_xacts 里确认残留事务与 gid。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": "SELECT gid, prepared, owner, database FROM pg_prepared_xacts;"}},
                ],
            },
            {
                "thinking": "台账显示同一批次已由重试 worker attempt 2 提交完成，prepared 的 attempt 1 是重复副本：必须 ROLLBACK PREPARED 丢弃副本并释放它持有的 staging 锁；若 COMMIT PREPARED 会把同一支付批次重复入账。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"ROLLBACK PREPARED '{case.prepared_move_gid}';"}},
                ],
            },
            {
                "thinking": "重放 ATTACH PARTITION，使用短 lock_timeout 防止再次长排队。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": attach_sql}},
                ],
            },
            {
                "thinking": "验证分区拓扑与数据完整性后提交。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": verify_topology_sql}},
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT count(*) AS seed_rows FROM (SELECT payment_ref FROM {case.legacy_table} WHERE payment_ref LIKE '{case.seed_ref_prefix}%' UNION ALL SELECT payment_ref FROM {case.parent_table} WHERE payment_ref LIKE '{case.seed_ref_prefix}%') s;"}},
                ],
            },
            {
                "thinking": "改造完成，提交结构化报告。",
                "actions": [{"api": "submit", "args": {"report": case.reference_report}}],
            },
        ]
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(mock_responses)
    return agent


class PartitionMigrationPGEnv(PGEnv):
    # Agent 的连接治理动作（ALLOW_CONNECTIONS false、批量 pg_terminate_backend）会
    # 临时打断 sampler 连接，agent 恢复连接可能持续数分钟；观测基础设施不应因此
    # 永久失效（PGEnv 重连机制先例：oom / fd_exhaustion 等场景入口）。
    SAMPLER_RECONNECT_TIMEOUT_SEC = 900.0


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    # Custom deployment is only needed to isolate concurrent validation runs.
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=image_name or case.base_image_name,
    )
    return PartitionMigrationPGEnv(
        workload=None, deployment=deployment, port=port,
        allow_sampler_jitter=True, allow_sampler_reconnect=True,
    )


def run_mode(args, scenario, case, mode, container_name, run_config):
    env = build_env(case, args.port, container_name, image_name=None)
    if mode == "mock":
        agent = build_full_score_mock_agent(case)
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses([{"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": EMPTY_REPORT}}}])
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    max_turns = {"mock": 12, "zero": 3, "llm": args.max_turns}[mode]
    run_config.diagnosis_match_mode = args.diagnosis_match_mode
    run_config.diagnosis_semantic_model = args.diagnosis_semantic_model
    run_config.diagnosis_semantic_config_path = args.diagnosis_semantic_config_path
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=max_turns, run_config=run_config)
    return orchestrator.run()


def main():
    scenario = PgBusinessChangePartitionMigrationScenario()
    parser = argparse.ArgumentParser(description="Run PgBusinessChangePartitionMigrationScenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument(
        "--container-name",
        default="aiopsbench-run-pg-business-change-partition-migration-scenario",
    )
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    add_diagnosis_arguments(parser)
    args = parser.parse_args()
    if args.max_turns > 30:
        raise ValueError("--max-turns must be <= 30")
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )
    case = scenario.get_case(args.case)
    modes = ("mock", "zero", "llm") if args.mode == "all" else (args.mode,)
    for mode in modes:
        result = run_mode(
            args,
            scenario,
            case,
            mode,
            f"{args.container_name}-{case.case_id}-{mode}",
            run_config,
        )
        print(f"[{mode}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")
        if mode == "mock":
            assert evaluation_passed(result), json.dumps(result, ensure_ascii=False)
        elif mode == "zero":
            assert not evaluation_passed(result), json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    main()
