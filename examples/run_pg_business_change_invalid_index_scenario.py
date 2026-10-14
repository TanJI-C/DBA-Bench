import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.base import evaluation_passed
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import (
    PgBusinessChangeInvalidIndexCase,
    PgBusinessChangeInvalidIndexScenario,
)
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


def build_mock_responses(case: PgBusinessChangeInvalidIndexCase):
    table = case.table
    invalid_index = case.invalid_index_name
    release_log_table = case.release_log_table or "ops_release_task_log"
    release_task_name = case.release_task_name or "store_sales_report_index_release"
    has_stall = bool(case.controller_app_name)
    conditional_drop = (
        "DO $$ BEGIN "
        f"IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
        f"WHERE c.relname = '{invalid_index}' AND n.nspname = 'public') THEN "
        f"EXECUTE 'DROP INDEX {invalid_index}'; "
        "END IF; END $$;"
    )
    diagnosis_actions = [
        {"api": "query_metrics", "args": {"metric_type": "workload_activity", "target": None}},
        {"api": "execute_sql", "args": {"sql_query": f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {case.representative_query}"}},
        {"api": "execute_sql", "args": {"sql_query":
            "SELECT t.relname AS table_name, c.relname AS index_name, i.indisvalid, i.indisready, "
            "pg_get_indexdef(i.indexrelid) AS indexdef "
            "FROM pg_index i JOIN pg_class t ON t.oid = i.indrelid "
            "JOIN pg_class c ON c.oid = i.indexrelid "
            f"WHERE t.relname IN ('{table}', '{case.peer_table}') "
            "ORDER BY t.relname, c.relname;"}},
        {"api": "execute_sql", "args": {"sql_query":
            f"SELECT task_name, target_object, status, attempts, last_error FROM {release_log_table} ORDER BY task_name;"}},
    ]
    stall_diagnosis = []
    stall_remediation = []
    freeze_diagnosis = []
    freeze_remediation = []
    if case.ddl_freeze_trigger_name:
        # 发布窗口 DDL 冻结：修复索引前必须发现并解除泄漏的变更冻结。
        freeze_diagnosis.append({"api": "execute_sql", "args": {"sql_query":
            "SELECT evtname, evtevent, evtfoid::regproc AS handler, evtenabled "
            "FROM pg_event_trigger ORDER BY evtname;"}}
        )
        freeze_remediation.append({"api": "execute_sql", "args": {"sql_query":
            f"DROP EVENT TRIGGER {case.ddl_freeze_trigger_name};"}}
        )
    if has_stall:
        stall_diagnosis.append({"api": "execute_sql", "args": {"sql_query":
            "SELECT pid, usename, application_name, state, wait_event_type, wait_event, "
            "xact_start, state_change, left(query, 120) AS query FROM pg_stat_activity "
            "WHERE datname = current_database() AND pid <> pg_backend_pid() "
            "ORDER BY state, application_name;"}}
        )
        # in-doubt prepared transaction 的处置方向依据交付台账裁决：批次已被
        # 下游确认接收且不会重发，必须 COMMIT PREPARED 补完源库提交（ROLLBACK
        # 会不可逆丢弃该批次业务数据）。
        stall_diagnosis.append({"api": "execute_sql", "args": {"sql_query":
            f"SELECT batch_id, target_table, row_count, delivery_status, "
            f"redelivery_policy, committed_at FROM {case.export_ledger_table} "
            "ORDER BY batch_id;"}}
        )
        stall_remediation.append({"api": "execute_sql", "args": {"sql_query":
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            f"WHERE application_name = '{case.controller_app_name}' "
            "AND pid <> pg_backend_pid();"}}
        )
        stall_remediation.append({"api": "execute_sql", "args": {"sql_query":
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            f"WHERE application_name = '{case.retry_app_name}' "
            "AND pid <> pg_backend_pid();"}}
        )
        stall_remediation.append({"api": "execute_sql", "args": {"sql_query":
            f"COMMIT PREPARED '{case.export_prepare_gid}';"}}
        )
    responses = [
        {
            "thinking": "门店销量报表变慢且发布任务失败。先看 workload_activity 找变慢的报表指纹，再确认当前执行计划与目录中的索引状态。",
            "actions": diagnosis_actions + stall_diagnosis + freeze_diagnosis,
        },
        {
            "thinking": f"确认 {table} 上存在 indisvalid=false 的遗留索引 {invalid_index}，来自被中断的并发建索引发布。"
            + ("重试 DIC 卡在控制器 SUE 锁上，导出工具崩溃遗留的孤儿两阶段事务又卡住并发 DDL 的事务等待阶段：先终止控制器与重试会话；台账确认该批次已被下游接收且不会重发，因此 COMMIT PREPARED 补完源库提交，最后清理并在线重建。" if has_stall else (
                f"该遗留索引带着发布模板残留的谓词「{case.invalid_index_predicate}」，与报表按门店过滤的访问模式没有蕴含关系，"
                "即使修复其 valid 状态也无法承载代表查询；同时 pg_event_trigger 里存在发布窗口遗留的 DDL 冻结「"
                f"{case.ddl_freeze_trigger_name}」，会拒绝一切手工 CREATE INDEX：先解除冻结，"
                "再清理失效索引并以正确、无谓词的定义 CONCURRENTLY 重建，不阻塞线上写入。"
                if case.invalid_index_predicate else
                "清理失效索引并以 CONCURRENTLY 重建，不阻塞线上写入。"
            )),
            "actions": stall_remediation + freeze_remediation + [
                {"api": "execute_sql", "args": {"sql_query": conditional_drop}},
                {"api": "execute_sql", "args": {"sql_query":
                    f"CREATE INDEX CONCURRENTLY idx_{table}_store_date "
                    f"ON {table} ({case.store_column}, {case.date_column});"}},
            ],
        },
        {
            "thinking": "复查目录无失效索引、计划已走索引扫描、延迟恢复、导出批次已完整落地，然后提交。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query":
                    f"SELECT count(*) AS invalid_indexes FROM pg_index i "
                    f"JOIN pg_class t ON t.oid = i.indrelid WHERE t.relname = '{table}' AND i.indisvalid = false;"}},
                {"api": "execute_sql", "args": {"sql_query": f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {case.representative_query}"}},
                *([
                    {"api": "execute_sql", "args": {"sql_query":
                        f"SELECT count(*) FROM {case.export_inbox_table} "
                        f"WHERE batch_id = '{case.export_prepare_gid}';"}},
                ] if has_stall else []),
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]
    return responses


def run_mode(args, scenario, case, mode, container_name, run_config):
    # allow_sampler_reconnect: fault-snapshot save 会 stop/commit/start PostgreSQL，
    # 采样线程必须在重启窗口内自愈重连。
    env = PGEnv(port=args.port, allow_sampler_jitter=True, allow_sampler_reconnect=True)
    env.deployment.container_name = container_name
    if mode == "mock":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(build_mock_responses(case))
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses([{"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": EMPTY_REPORT}}}])
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    default_max_turns = {"mock": 10, "zero": 3, "llm": 25}
    max_turns = args.max_turns if args.max_turns is not None else default_max_turns[mode]
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=max_turns, run_config=run_config)
    return orchestrator.run()


def main():
    scenario = PgBusinessChangeInvalidIndexScenario()
    parser = argparse.ArgumentParser(description="Run PgBusinessChangeInvalidIndexScenario.")
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario.cases],
    )
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-run-pg-business-change-invalid-index-scenario")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    args = parser.parse_args()
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
