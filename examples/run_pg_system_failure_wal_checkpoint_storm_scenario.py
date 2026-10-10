import argparse
import json
import os
import signal
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.runtime.config import required_run_timeout_seconds
from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.postgres import PgSystemFailureWalCheckpointStormScenario
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload


HARD_TIMEOUT_SEC = 900


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_report(case, success):
    factors = (
        "wal disk growth and checkpoint latency",
        "inactive slot retains wal",
        "checkpoint storm",
        "wal retention and checkpoint storm are independent roots",
        "release wal then tune checkpoint",
    ) if success else ()
    return {
        "diagnosis": {"conditions": [
            {"type": "finding", "factor": factor, "entity": case.slot_name, "evidence": [f"observed {factor}"]}
            for factor in factors
        ]},
        "outcome": {
            "changes": (["dropped stalled slot and restored checkpoint settings"] if success else []),
            "verification": (["slot absence and all three settings verified"] if success else []),
        },
        "summary": "WAL retention and checkpoint pressure were independent root causes." if success else "No diagnosis was attempted.",
    }


_BGWRITER_DELTA_SQL_TEMPLATE = (
    "CREATE TEMP TABLE bgwriter_before AS "
    "SELECT checkpoints_timed, checkpoints_req, buffers_checkpoint "
    "FROM pg_stat_bgwriter; "
    "SELECT pg_sleep({sleep}); "
    "SELECT "
    "  after_sample.checkpoints_timed - before_sample.checkpoints_timed "
    "    AS checkpoints_timed_delta, "
    "  after_sample.checkpoints_req - before_sample.checkpoints_req "
    "    AS checkpoints_req_delta, "
    "  after_sample.buffers_checkpoint - before_sample.buffers_checkpoint "
    "    AS buffers_checkpoint_delta "
    "FROM bgwriter_before before_sample "
    "CROSS JOIN pg_stat_bgwriter after_sample;"
)

_REPLICATION_SLOTS_SQL = (
    "SELECT slot_name, slot_type, active, restart_lsn, wal_status, "
    "pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) "
    "AS retained_wal FROM pg_replication_slots;"
)

_CHECKPOINT_SETTINGS_SQL = (
    "SELECT name, setting, unit FROM pg_settings "
    "WHERE name IN ('checkpoint_timeout', 'max_wal_size', "
    "'checkpoint_completion_target') ORDER BY name;"
)


def build_mock_responses(case):
    if getattr(case, "protected_slot_name", None) is not None:
        return _build_protected_slot_mock_responses(case)
    return [
    {
        "thinking": (
            "告警同时包含磁盘空间下降和周期性 I/O 毛刺，先检查磁盘空间与磁盘 I/O，"
            "确认是否是空间和刷盘叠加问题。"
        ),
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "disk_usage", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
        ],
    },
    {
        "thinking": (
            "空间异常常见原因是 WAL 被保留；I/O 毛刺可能来自频繁 checkpoint。"
            "分别查询复制槽和 bgwriter checkpoint 统计。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": _REPLICATION_SLOTS_SQL
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": _BGWRITER_DELTA_SQL_TEMPLATE.format(sleep=35)
                },
            },
        ],
    },
    {
        "thinking": (
            "复制槽未消费是 WAL 堆积根因；还需要确认 checkpoint_timeout、max_wal_size "
            "和 checkpoint_completion_target 是否过于激进。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": _CHECKPOINT_SETTINGS_SQL
                },
            }
        ],
    },
    {
        "thinking": (
            "应先处理空间危机，删除未消费的复制槽释放 WAL 保留，然后再优化 checkpoint。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": f"SELECT pg_drop_replication_slot('{case.slot_name}');"
                },
            }
        ],
    },
    {
        "thinking": (
            "WAL 空间风险已解除，接着把 checkpoint 参数恢复到写入负载更合理的范围并重新加载配置。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": "ALTER SYSTEM SET checkpoint_timeout = '5min';"
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": "ALTER SYSTEM SET max_wal_size = '1GB';"
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "ALTER SYSTEM SET checkpoint_completion_target = '0.9';"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SELECT pg_reload_conf(); SELECT pg_sleep(1);"},
            },
        ],
    },
    {
        "thinking": "修复动作已执行，先验证复制槽消失和 checkpoint 参数生效，再提交评估。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT count(*) AS remaining_slots FROM pg_replication_slots "
                        f"WHERE slot_name = '{case.slot_name}';"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT pg_sleep(1); "
                        "SELECT name, setting, unit FROM pg_settings "
                        "WHERE name IN ('checkpoint_timeout', 'max_wal_size', "
                        "'checkpoint_completion_target') ORDER BY name;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "验证显示两个根因均已解除，提交评估。",
        "actions": [
            {"api": "submit", "args": {"report": build_report(case, True)}},
        ],
    },
]


def _build_protected_slot_mock_responses(case):
    return [
        {
            "thinking": (
                "告警包含磁盘下降与周期性写延迟尖峰，且要求不能中断计划内 billing 导出与"
                "健康复制。先看磁盘与 I/O。"
            ),
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "disk_usage", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
            ],
        },
        {
            "thinking": (
                "磁盘下降常见原因是 WAL 被复制槽保留。查询复制槽及其 retained WAL，"
                "同时查导出作业登记表确认各槽的业务归属与活跃度。"
            ),
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {"sql_query": _REPLICATION_SLOTS_SQL},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"SELECT job_id, slot_name, status, schedule, last_run_at "
                            f"FROM {case.slot_registry_table} ORDER BY job_id;"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"SELECT count(*) AS batches_last_minute "
                            f"FROM {case.export_batches_table} "
                            "WHERE created_at > now() - interval '1 minute';"
                        )
                    },
                },
            ],
        },
        {
            "thinking": (
                "登记表显示 billing_hourly_export 持续运行（导出槽受保护），"
                "而 billing_migration_2026q2 已结束却仍保留槽。再确认两个 inactive 槽的"
                "restart_lsn 差距，并用 bgwriter 增量判断写尖峰是否为 checkpoint 突发。"
            ),
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT slot_name, active, restart_lsn, "
                            "pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) "
                            "AS retained_wal FROM pg_replication_slots ORDER BY slot_name;"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": _BGWRITER_DELTA_SQL_TEMPLATE.format(sleep=15)
                    },
                },
            ],
        },
        {
            "thinking": (
                "checkpoint_timeout/max_wal_size/completion_target 被调小且 requested "
                "checkpoint 频繁，是写尖峰根因；导出批处理只是同域噪声。确认三个参数。"
            ),
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {"sql_query": _CHECKPOINT_SETTINGS_SQL},
                }
            ],
        },
        {
            "thinking": (
                "只删除已结束迁移项目的孤儿槽释放 WAL 保留；导出槽与健康报表槽保留。"
            ),
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": f"SELECT pg_drop_replication_slot('{case.slot_name}');"
                    },
                }
            ],
        },
        {
            "thinking": (
                "WAL 保留解除后，把 checkpoint 参数恢复到合理范围并重新加载配置。"
            ),
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "ALTER SYSTEM SET checkpoint_timeout = '5min';"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "ALTER SYSTEM SET max_wal_size = '1GB';"},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": "ALTER SYSTEM SET checkpoint_completion_target = '0.9';"
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "SELECT pg_reload_conf(); SELECT pg_sleep(1);"},
                },
            ],
        },
        {
            "thinking": (
                "验证孤儿槽已删除、导出槽与健康槽仍在、checkpoint 参数生效，然后提交评估。"
            ),
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT slot_name, active FROM pg_replication_slots ORDER BY slot_name;"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT pg_sleep(1); "
                            "SELECT name, setting, unit FROM pg_settings "
                            "WHERE name IN ('checkpoint_timeout', 'max_wal_size', "
                            "'checkpoint_completion_target') ORDER BY name;"
                        )
                    },
                },
            ],
        },
        {
            "thinking": "两个根因均已解除且受保护槽完整，提交评估。",
            "actions": [
                {"api": "submit", "args": {"report": build_report(case, True)}},
            ],
        },
    ]


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    workload = None if case.case_id.endswith("_simple") else TPCDSWorkload(scale=case.dataset_scale)
    env = PGEnv(
        workload=workload,
        port=port,
        sample_interval_sec=1,
        allow_sampler_jitter=True,
    )
    # Override only for isolated scenario runs; keep the default PG deployment otherwise.
    env.deployment.container_name = container_name
    env.deployment.image_name = image_name or case.base_image_name
    return env




























def run_mode(args, scenario, case, mode, container_name, run_config):
    override_image = None
    env = build_env(case, args.port, container_name, image_name=override_image)
    env.deployment.container_name = container_name
    if override_image:
        env.deployment.image_name = override_image
    if mode == "mock":
        agent = MockLLMAgent(url='mock', api_key='mock', system_prompt='You are a DBA agent.', use_native_tools=False)
        agent.set_mock_responses(build_mock_responses(case))
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses([
            {
                "thinking": "Run an unrelated destructive DDL instead of diagnosing safely.",
                "action": {"api": "execute_sql", "args": {"sql_query": "DROP TABLE IF EXISTS unrelated_zero_probe;"}},
            },
            {"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": build_report(case, False)}}},
        ])
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    default_max_turns = {"mock": 15, "zero": 3, "llm": 20}
    max_turns = args.max_turns if args.max_turns is not None else default_max_turns[mode]
    if mode == "llm":
        max_turns = min(max_turns, 30)
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=max_turns, run_config=run_config)
    return orchestrator.run()


def main():
    scenario = PgSystemFailureWalCheckpointStormScenario()
    parser = argparse.ArgumentParser(description="Run PgSystemFailureWalCheckpointStormScenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-run-pg-system-failure-wal-checkpoint-storm")
    parser.add_argument("--model", required=True, help="LLM model name")
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
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(required_run_timeout_seconds())
    try:
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
                assert not result["DiagnosisPass"] and not result["OutcomePass"] and not result["SafePass"], json.dumps(result, ensure_ascii=False)
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
