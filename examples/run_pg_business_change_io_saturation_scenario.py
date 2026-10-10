import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.postgres import PgBusinessChangeIoSaturationScenario
from src.execution.deployment import PGDockerDeployment
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig







def build_report(case, success: bool) -> dict:
    if not success:
        return {
            "diagnosis": {"conditions": []},
            "outcome": {"changes": [], "verification": []},
            "summary": "No diagnosis or remediation was attempted.",
        }
    if case.fault_variant == "wal_archive_backlog":
        factors = (
            "disk io and query latency",
            "wal retained by stalled slot",
            "stalled archive replication slot",
            "wal backlog causes checkpoint write amplification",
            "drop only stalled archive slot",
        )
        entity = case.wal_slot_name
    elif case.report_role_work_mem:
        factors = (
            "multiple unrelated slow queries",
            "disk io saturation",
            "background maintenance io pressure",
            "reports are io victims",
            "role level work_mem regression",
            "terminate only maintenance session",
        )
        entity = case.maintenance_app_name
    else:
        factors = (
            "multiple unrelated slow queries",
            "disk io saturation",
            "background maintenance io pressure",
            "reports are io victims",
            "terminate only maintenance session",
        )
        entity = case.maintenance_app_name
    return {
        "diagnosis": {"conditions": [
            {
                "type": "finding",
                "factor": factor,
                "entity": entity,
                "evidence": [f"metrics and PostgreSQL state confirmed {factor}"],
            }
            for factor in factors
        ]},
        "outcome": {
            "changes": [f"removed only the root-cause target {entity}"],
            "verification": ["target state, protected state, I/O, and victim queries were rechecked"],
        },
        "summary": "The slow queries were victims of shared I/O pressure, not individual SQL regressions.",
    }


def build_full_score_mock_agent(case):
    if getattr(case, "fault_variant", "") == "wal_archive_backlog":
        mock_responses = [
            {
                "thinking": "告警同时提到 I/O、慢报表和 WAL/archive backlog，先看慢查询确认报表是否只是共同受害者。",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None}},
                ],
            },
            {
                "thinking": "多条报表同时慢，继续看磁盘 I/O 是否存在共享资源压力。",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
                ],
            },
            {
                "thinking": "I/O 高不能只归因给报表 SQL，检查 WAL 归档/复制槽保留状态。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT slot_name, active, restart_lsn, wal_status, pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_bytes FROM pg_replication_slots WHERE slot_name IN ('{case.wal_slot_name}', '{case.healthy_slot_name}') ORDER BY retained_bytes DESC NULLS LAST;"}},
                    {"api": "execute_sql", "args": {"sql_query": "SELECT archived_count, failed_count, last_failed_wal, last_failed_time FROM pg_stat_archiver;"}},
                ],
            },
            {
                "thinking": "确认目标 replication slot 保留 WAL，后台 writer 造成 I/O 压力，报表只是受害者。删除停滞 slot，让 backlog 释放。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_drop_replication_slot('{case.wal_slot_name}');"}},
                ],
            },
            {
                "thinking": "复查 slot 已清理、慢报表会话退出、I/O 恢复趋势。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_sleep(2); SELECT slot_name, active, wal_status FROM pg_replication_slots WHERE slot_name IN ('{case.wal_slot_name}', '{case.healthy_slot_name}') ORDER BY slot_name; SELECT application_name, state FROM pg_stat_activity WHERE application_name = '{case.maintenance_app_name}' OR application_name LIKE '{case.slow_query_app_prefix}%';"}},
                    {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
                    {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None}},
                ],
            },
            {
                "thinking": "WAL backlog 根因已清除，提交。",
                "actions": [{"api": "submit", "args": {"report": build_report(case, True)}}],
            },
        ]
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(mock_responses)
        return agent

    if case.report_role_work_mem:
        mock_responses = [
            {
                "thinking": "两个运营报表同时慢，先看 slow_queries 和磁盘 I/O，确认是否存在共同资源压力。",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None}},
                    {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
                ],
            },
            {
                "thinking": "查询 pg_stat_activity，区分维护会话、报表会话、调度会话和其他在途维护负载，并记录报表会话的 usename。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pid, usename, application_name, state, wait_event_type, wait_event, now() - query_start AS duration, query FROM pg_stat_activity WHERE datname = current_database() AND backend_type = 'client backend' ORDER BY query_start NULLS LAST;"}},
                ],
            },
            {
                "thinking": "维护会话属于调度体系，先看调度表确认哪个作业会重新拉起该会话、哪些作业必须保持运行；同时审计数据库与角色各作用域的 work_mem 覆盖，找出作用于报表角色的病态条目。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT job_name, worker_application, enabled, restart_delay_seconds, last_heartbeat_at FROM {case.schedule_table} ORDER BY job_name;"}},
                    {"api": "execute_sql", "args": {"sql_query": "SELECT r.rolname, d.datname, s.setconfig FROM pg_db_role_setting s LEFT JOIN pg_roles r ON r.oid = s.setrole LEFT JOIN pg_database d ON d.oid = s.setdatabase WHERE s.setconfig::text LIKE '%work_mem%';"}},
                ],
            },
            {
                "thinking": f"报表会话以 {case.report_role_name} 运行，其角色在当前库上的 work_mem 低于服务器默认值，是参数回归；db 级与健康角色的覆盖是正常调优，保持不动。先停用根因作业，防止调度器重新拉起维护会话。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"UPDATE {case.schedule_table} SET enabled = false WHERE job_name = '{case.culprit_job_name}';"}},
                ],
            },
            {
                "thinking": f"复位 {case.report_role_name} 在当前数据库作用域的 work_mem 回归。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"ALTER ROLE {case.report_role_name} IN DATABASE testdb RESET work_mem;"}},
                ],
            },
            {
                "thinking": f"停用调度项后，终止残留的维护会话 {case.maintenance_app_name}。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{case.maintenance_app_name}' AND pid <> pg_backend_pid();"}},
                ],
            },
            {
                "thinking": "复查维护会话不再出现、参数已复位且健康覆盖保留、受害者报表退出、调度表健康作业心跳正常、I/O 回落。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_sleep(6); SELECT application_name, state FROM pg_stat_activity WHERE application_name = '{case.maintenance_app_name}' OR application_name LIKE '{case.slow_query_app_prefix}%' OR application_name = '{case.twin_app_name}'; SELECT r.rolname, d.datname, s.setconfig FROM pg_db_role_setting s LEFT JOIN pg_roles r ON r.oid = s.setrole LEFT JOIN pg_database d ON d.oid = s.setdatabase; SELECT job_name, enabled, last_heartbeat_at FROM {case.schedule_table};"}},
                    {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
                ],
            },
            {
                "thinking": "共享 I/O 压力与参数回归均已解除，提交。",
                "actions": [{"api": "submit", "args": {"report": build_report(case, True)}}],
            },
        ]
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(mock_responses)
        return agent

    if case.scheduler_app_name:
        worker_apps = ", ".join([f"'{case.maintenance_app_name}'"] + [f"'{app}'" for app, _task in case.decoy_workers])
        mock_responses = [
            {
                "thinking": "告警是多条 TPC-DS 报表同时慢，先查看 slow_queries，确认是不是多条不相关查询一起变慢。",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None}},
                ],
            },
            {
                "thinking": "慢查询并非单条 SQL，转向系统资源，检查磁盘 I/O 是否饱和。",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
                ],
            },
            {
                "thinking": "查询 pg_stat_activity，观察后台常驻 worker 会话、报表会话与调度会话的构成。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": "SELECT pid, application_name, state, wait_event_type, wait_event, now() - query_start AS duration, query FROM pg_stat_activity WHERE datname = current_database() AND backend_type = 'client backend' ORDER BY query_start NULLS LAST;"}},
                ],
            },
            {
                "thinking": "多个 worker 会话同属一个批处理框架且入口同形，先查调度表和作业运行审计，建立 job→worker→task 映射。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT job_name, worker_application, worker_task, enabled, restart_delay_seconds, last_heartbeat_at FROM {case.schedule_table} ORDER BY job_name;"}},
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT job_name, started_at, source FROM {case.job_run_table} ORDER BY started_at;"}},
                ],
            },
            {
                "thinking": "调度审计无法单独区分重负载作业，且三个 worker 的语句文本同形、入口函数分支仅差 WHERE 过滤；间隔多次采样 pg_stat_activity 建立 wait_event 频率分布，持续处于 IO:BufFileWrite/DataFileWrite 的会话才是饱和源。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pid, application_name, wait_event_type, wait_event, query FROM pg_stat_activity WHERE datname = current_database() AND backend_type = 'client backend' AND application_name IN ({worker_apps}) ORDER BY application_name;"}},
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_sleep(4); SELECT pid, application_name, wait_event_type, wait_event, query FROM pg_stat_activity WHERE datname = current_database() AND backend_type = 'client backend' AND application_name IN ({worker_apps}) ORDER BY application_name;"}},
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_sleep(4); SELECT pid, application_name, wait_event_type, wait_event, query FROM pg_stat_activity WHERE datname = current_database() AND backend_type = 'client backend' AND application_name IN ({worker_apps}) ORDER BY application_name;"}},
                ],
            },
            {
                "thinking": f"采样频率分布显示 {case.maintenance_app_name} 以 IO wait 为主，其余 worker 几乎全程 PgSleep；结合调度表 task 映射与入口函数中全表排序与过滤小排序的体量差异，根因是调度作业 {case.culprit_job_name} 的全表排序重建循环。先停用该调度项，防止 8 秒级联重启。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"UPDATE {case.schedule_table} SET enabled = false WHERE job_name = '{case.culprit_job_name}';"}},
                ],
            },
            {
                "thinking": f"停用调度项后，终止残留的 culprit 会话 {case.maintenance_app_name}，不触碰 decoy 与健康作业。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{case.maintenance_app_name}' AND pid <> pg_backend_pid();"}},
                ],
            },
            {
                "thinking": "复查 culprit 会话不再出现、受害者退出、其余 worker 与健康作业心跳正常。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_sleep(6); SELECT application_name, state FROM pg_stat_activity WHERE application_name IN ({worker_apps}) OR application_name LIKE '{case.slow_query_app_prefix}%'; SELECT job_name, enabled, last_heartbeat_at FROM {case.schedule_table};"}},
                ],
            },
            {
                "thinking": "确认磁盘 I/O 回落。",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
                ],
            },
            {
                "thinking": "调度项已停用、culprit 会话已终止、其余 worker 与健康作业保活，提交。",
                "actions": [{"api": "submit", "args": {"report": build_report(case, True)}}],
            },
        ]
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(mock_responses)
        return agent

    if case.report_role_work_mem:
        mock_responses = [
            {
                "thinking": "两个运营报表同时慢，先看 slow_queries 和磁盘 I/O，确认是否存在共同资源压力。",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None}},
                    {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
                ],
            },
            {
                "thinking": "查询 pg_stat_activity，区分维护会话、报表会话和其他在途维护负载。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pid, application_name, state, wait_event_type, wait_event, now() - query_start AS duration, query FROM pg_stat_activity WHERE datname = current_database() AND backend_type = 'client backend' ORDER BY query_start NULLS LAST;"}},
                ],
            },
            {
                "thinking": f"维护会话 {case.maintenance_app_name} 持续重建临时表制造 I/O 压力；另一个 keeper 会话是低频 VACUUM，不构成主要矛盾，不动它。先终止维护会话。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{case.maintenance_app_name}' AND pid <> pg_backend_pid();"}},
                ],
            },
            {
                "thinking": "报表会话仍以异常 temp 消耗运行，审计数据库与角色级参数覆盖，定位作用于报表角色的 work_mem 回归。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": "SELECT r.rolname, s.setdatabase, s.setconfig FROM pg_db_role_setting s LEFT JOIN pg_roles r ON r.oid = s.setrole WHERE s.setconfig::text LIKE '%work_mem%';"}},
                ],
            },
            {
                "thinking": "确认 report_reader 角色级 work_mem 被调低，复位该角色的默认值。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"ALTER ROLE {case.report_role_name} RESET work_mem;"}},
                ],
            },
            {
                "thinking": "复查维护会话消失、参数已复位、受害者报表退出，I/O 回落。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_sleep(6); SELECT application_name, state FROM pg_stat_activity WHERE application_name = '{case.maintenance_app_name}' OR application_name LIKE '{case.slow_query_app_prefix}%' OR application_name = '{case.twin_app_name}'; SELECT r.rolname, s.setconfig FROM pg_db_role_setting s LEFT JOIN pg_roles r ON r.oid = s.setrole;"}},
                    {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
                ],
            },
            {
                "thinking": "共享 I/O 压力与参数回归均已解除，提交。",
                "actions": [{"api": "submit", "args": {"report": build_report(case, True)}}],
            },
        ]
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(mock_responses)
        return agent

    mock_responses = [
        {
            "thinking": "告警是多条 TPC-DS 报表同时慢，先查看 slow_queries，确认是不是多条不相关查询一起变慢。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None}},
            ],
        },
        {
            "thinking": "慢查询并非单条 SQL，转向系统资源，检查磁盘 I/O 是否饱和。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
            ],
        },
        {
            "thinking": "I/O 指标异常，需要查询 pg_stat_activity，把慢查询会话和后台报表刷新会话关联起来。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT pid, application_name, state, wait_event_type, wait_event, now() - query_start AS duration, query FROM pg_stat_activity WHERE datname = current_database() AND (application_name = '{case.maintenance_app_name}' OR application_name LIKE '{case.slow_query_app_prefix}%' OR state = 'active') ORDER BY query_start NULLS LAST;"}},
            ],
        },
        {
            "thinking": f"发现后台维护会话 {case.maintenance_app_name} 正在持续制造 I/O 压力，应终止该刷新任务而不是逐条改写业务 SQL。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{case.maintenance_app_name}' AND pid <> pg_backend_pid();"}},
            ],
        },
        {
            "thinking": "后台报表刷新任务已终止，复查后台会话、慢查询和磁盘 I/O 指标，确认查询恢复。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_sleep(1); SELECT application_name, state, wait_event_type, query FROM pg_stat_activity WHERE application_name = '{case.maintenance_app_name}' OR application_name LIKE '{case.slow_query_app_prefix}%' ORDER BY application_name;"}},
                {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
            ],
        },
        {
            "thinking": "多条慢查询已恢复，根因是后台报表刷新任务造成 I/O 饱和，提交。",
            "actions": [{"api": "submit", "args": {"report": build_report(case, True)}}],
        },
    ]
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(mock_responses)
    return agent





def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    # Custom deployment is only needed to isolate concurrent validation runs.
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=image_name or case.base_image_name,
    )
    return PGEnv(workload=None, deployment=deployment, port=port, allow_sampler_jitter=True)




















































def run_mode(args, scenario, case, mode, container_name, run_config):
    env = build_env(case, args.port, container_name, image_name=None)
    if mode == "mock":
        agent = build_full_score_mock_agent(case)
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses([{"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": build_report(case, False)}}}])
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    max_turns = {"mock": 10, "zero": 3, "llm": args.max_turns}[mode]
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=max_turns, run_config=run_config)
    return orchestrator.run()


def main():
    scenario = PgBusinessChangeIoSaturationScenario()
    parser = argparse.ArgumentParser(description="Run PgBusinessChangeIoSaturationScenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-run-pg-business-change-io-saturation")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
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
            assert result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"], json.dumps(result, ensure_ascii=False)
        elif mode == "zero":
            # A no-op run takes no actions, so it cannot violate any safety rule;
            # SafePass is only meaningful for runs that attempted a repair.
            assert not result["DiagnosisPass"] and not result["OutcomePass"], json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    main()
