import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgQueryPerfStaleStatisticsScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSXWorkload


# 讲解主线：本入口脚本先构造真实 TPC-DS branch_order_line 统计信息陈旧，
# 再把一条受影响的 join 查询暴露给 Agent，最后由 evaluator 检查 ANALYZE
# 是否真的让估算误差、join 策略和执行时间恢复。
TARGET_TABLE = "branch_order_line"
# 统计信息场景的关键观测点：reltuples 是优化器旧估算，n_live_tup /
# n_mod_since_analyze 能证明 ANALYZE 后又发生了大量真实数据变更。
TARGET_STATS_SQL = (
    "SELECT c.reltuples, c.relpages, s.n_live_tup, s.last_analyze, s.n_mod_since_analyze "
    "FROM pg_class c "
    "JOIN pg_stat_user_tables s ON s.relid = c.oid "
    f"WHERE c.relname = '{TARGET_TABLE}';"
)
TARGET_INJECTED_ROWS_SQL = (
    "SELECT COUNT(*) FROM branch_order_line "
    "WHERE bol_product_sk BETWEEN 1 AND 40 "
    "AND bol_receipt_number BETWEEN 2000000001 AND 2001000000;"
)


def build_full_score_mock_responses(case):
    target_explain_sql = (
        f"EXPLAIN (ANALYZE, FORMAT JSON) {case.fault_fingerprint_sql.rstrip(';')};"
    )
    if case.case_id == "branch_order_distribution_shift":
        # distributed_window Case 为复合根因——全列 ANALYZE 前先读列级统计
        # 粒度证据（attstattarget），恢复被降级的关键列统计 target 后再 ANALYZE。
        repair_tail = (
            [
                {
                    "thinking": "统计粒度归因：pg_attribute 显示 bol_sold_date_sk 的统计 target 被降级为 1（其余关键列 1000），例行 ANALYZE 只能以 1 桶直方图（2 个边界）重采，无法恢复估计精度。",
                    "action": {
                        "api": "execute_sql",
                        "args": {
                            "sql_query": (
                                "SELECT attname, attstattarget FROM pg_attribute "
                                "WHERE attrelid = 'branch_order_line'::regclass "
                                "AND attname IN ('bol_sold_date_sk', 'bol_product_sk', 'bol_quantity') "
                                "ORDER BY attname;"
                            )
                        },
                    },
                },
                {
                    "thinking": "复合根因修复第一步：把关键日期列统计 target 恢复为默认（-1），使下一次 ANALYZE 以足够粒度重采。",
                    "action": {
                        "api": "execute_sql",
                        "args": {
                            "sql_query": (
                                "ALTER TABLE branch_order_line ALTER COLUMN bol_sold_date_sk "
                                "SET STATISTICS -1;"
                            )
                        },
                    },
                },
            ]
        )
        return [
        {
            "thinking": "先看 topsql——本场景不支持该指标，确认 metric 面不可用后转入语句历史。",
            "action": {
                "api": "query_metrics",
                "args": {"metric_type": "topsql"},
            },
        },
        {
            "thinking": "再看语句历史定位受影响报表：告警报表名同族出现 CALL 记录与上月版本 v8 明文 SQL，必须解析存储过程体才能确定当前报表的对象。",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT queryid, calls, rows, left(query, 220) AS query_text "
                        "FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 20;"
                    )
                },
            },
        },
        {
            "thinking": "解析 BI 存储过程体：CALL 指纹对应 sp_hot_channel_revenue_reforecast，过程内语句不在语句历史，pg_get_functiondef 取得 1 月窗报表 SQL 与其对象。",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT proname, pg_get_functiondef(oid) AS definition "
                        "FROM pg_proc WHERE proname = 'sp_hot_channel_revenue_reforecast';"
                    )
                },
            },
        },
        {
            "thinking": "对过程体中的完整报表 SQL 做 EXPLAIN ANALYZE，检查 branch_order_line 的 estimated rows 和 actual rows 是否严重偏离。",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": target_explain_sql},
            },
        },
        {
            "thinking": "检查 pg_stat_user_tables：last_analyze 晚于漂移写入且 n_mod_since_analyze 很高，与语句历史中的 scoped 维护 ANALYZE 矛盾。",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT s.relname, s.n_live_tup, c.reltuples, s.last_analyze, s.n_mod_since_analyze "
                        "FROM pg_stat_user_tables s JOIN pg_class c ON c.oid = s.relid "
                        "WHERE s.relname = 'branch_order_line';"
                    )
                },
            },
        },
        {
            "thinking": "列级新鲜度归因：对照 pg_stats 中 bol_sold_date_sk/bol_product_sk 的直方图与 1 月窗实际行数，确认关键列统计仍停留在漂移写入前、scoped 维护未覆盖它们。",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT attname, n_distinct, histogram_bounds::text AS histogram_bounds "
                        "FROM pg_stats WHERE tablename = 'branch_order_line' "
                        "AND attname IN ('bol_sold_date_sk', 'bol_product_sk');"
                    )
                },
            },
        },
        {
            "thinking": "窗口实际行数对照：报表窗口实际 9.6 万行而直方图隐含数十行，且上月回放批次日期在窗口之外、直方图可覆盖——漂移来自 reset 前的批量加载。",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT COUNT(*) FROM branch_order_line "
                        "WHERE bol_sold_date_sk BETWEEN 2451911 AND 2451941;"
                    )
                },
            },
        },
        {
            "thinking": "查普通索引，确认商品键已有主键访问路径，排除表达式索引/缺 join key 这类 missing index 根因。",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT indexname, indexdef FROM pg_indexes "
                        "WHERE tablename = 'branch_order_line' "
                        "AND indexdef ILIKE '%bol_product_sk%' "
                        "ORDER BY indexname;"
                    )
                },
            },
        },
        *repair_tail,
        {
            "thinking": "根因是 branch_order_line 统计信息过期且关键列统计粒度被降级，恢复统计 target 后刷新这张被注入故障的目标表即可，不改 SQL、不建索引、不调 planner GUC。",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": "ANALYZE branch_order_line;"},
            },
        },
        {
            "thinking": "重新执行同一条完整 fault query 的 EXPLAIN ANALYZE，验证估算误差下降、计划恢复且执行时间下降。",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": target_explain_sql},
            },
        },
        {
            "thinking": "统计信息已经刷新并验证完成，再次查看 topsql 确认 mean_exec_time 下降，提交结果。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "topsql"}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
        ]
    # 题面只给报表指纹（不内嵌受影响 SQL）；先按指纹定位语句，
    # 再做未过滤修改面调查与组合级新鲜度归因，最后恢复三关键列统计 target 后
    # ANALYZE（复合修复）。
    reference_report = (
        {
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "branch order distribution query",
                        "entity": "branch_order_hot_window_simple",
                        "evidence": [
                            "scripted diagnostic actions observed branch order distribution query"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": "stale branch order statistics",
                        "entity": "branch_order_hot_window_simple",
                        "evidence": [
                            "scripted diagnostic actions observed stale branch order statistics"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": "large row estimate error",
                        "entity": "branch_order_hot_window_simple",
                        "evidence": [
                            "scripted diagnostic actions observed large row estimate error"
                        ],
                    },
                    {
                        "type": "finding",
                        "factor": (
                            "branch_order_line key column statistics targets were degraded to a "
                            "low sampling granularity, so re-analyzing the table cannot capture "
                            "the hot combination in the statistics"
                        ),
                        "entity": "branch_order_hot_window_simple",
                        "evidence": [
                            "scripted diagnostic actions observed branch_order_line key column "
                            "statistics targets degraded to a low sampling granularity"
                        ],
                    },
                ]
            },
            "outcome": {
                "changes": ["applied the case-specific remediation"],
                "verification": ["verified the case-specific final state"],
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification.",
        }
    )
    return [
    {
        "thinking": "先看 topsql 找出 pg_stat_statements 里完整的慢报表 SQL，避免用短 probe 猜根因。",
        "action": {
            "api": "query_metrics",
            "args": {"metric_type": "topsql"},
        },
    },
    {
        "thinking": "题面只给了报表指纹。先在 pg_stat_statements 里按指纹定位受影响报表的完整语句与执行耗时，再基于真实语句文本做计划诊断。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT queryid, calls, total_exec_time, mean_exec_time, "
                    "LEFT(query, 1200) AS query "
                    "FROM pg_stat_statements "
                    "WHERE query ILIKE '%finance_dashboard: branch_hot_window_simple%' "
                    "ORDER BY mean_exec_time DESC LIMIT 5;"
                )
            },
        },
    },
    {
        "thinking": "对定位到的完整报表语句做 EXPLAIN ANALYZE，检查 branch_order_line 的 estimated rows 和 actual rows 是否严重偏离，同时记录 join 另一侧 calendar_day 节点的估计是否准确。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": target_explain_sql},
        },
    },
    {
        "thinking": "报表变慢常见于近期数据形态变化。先做一次未过滤的全库近期修改面调查，看最近哪些表发生了批量修改、是否与受影响报表同窗，再和受影响查询读取的表做归属对照。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT relname, n_live_tup, n_mod_since_analyze, last_analyze "
                    "FROM pg_stat_user_tables "
                    "WHERE n_mod_since_analyze > 0 "
                    "ORDER BY n_mod_since_analyze DESC LIMIT 15;"
                )
            },
        },
    },
    {
        "thinking": "对照受影响查询 join 双方的统计：branch_order_line 是否 last_analyze 早于变更且 n_mod_since_analyze 高；calendar_day 的近期小修改是期间标记维护、不参与报表谓词，且其计划节点估计准确，据此排除维表漂移、锁定事实表统计过期。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT relname, n_live_tup, n_dead_tup, n_mod_since_analyze, last_analyze "
                    "FROM pg_stat_user_tables "
                    "WHERE relname IN ('branch_order_line','calendar_day');"
                )
            },
        },
    },
    {
        "thinking": "语句历史里同表有两条批量 INSERT（上月窗 3000 行 vs 本月窗 1500 行）。对照两个窗口的热组合行数与 last_analyze 的先后：上月组合已被基线 ANALYZE 吸收进统计（计划估计准确），本月组合不在统计内（计划失真来源），完成组合级新鲜度归因。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT 'previous_month' AS batch, count(*) AS rows "
                    "FROM branch_order_line "
                    "WHERE bol_sold_date_sk = 2451880 AND bol_product_sk = 1 AND bol_quantity = 7 "
                    "UNION ALL "
                    "SELECT 'current_month', count(*) "
                    "FROM branch_order_line "
                    "WHERE bol_sold_date_sk = 2451911 AND bol_product_sk = 1 AND bol_quantity = 7 "
                    "ORDER BY 1;"
                )
            },
        },
    },
    {
        "thinking": "对比 pg_class 中 branch_order_line 的 reltuples/relpages，确认统计信息是否与实际行数矛盾。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT relname, reltuples, relpages "
                    "FROM pg_class WHERE relname = 'branch_order_line';"
                )
            },
        },
    },
    {
        "thinking": "查普通索引，确认商品键已有主键访问路径，排除表达式索引/缺 join key 这类 missing index 根因。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT indexname, indexdef FROM pg_indexes "
                    "WHERE tablename = 'branch_order_line' "
                    "AND indexdef ILIKE '%bol_product_sk%' "
                    "ORDER BY indexname;"
                )
            },
        },
    },
    {
        "thinking": "ANALYZE 类修复若失效，通常还有统计采样粒度问题。检查三个关键列的 attstattarget：历史维护把 target 降到了 2，低粒度下 ANALYZE 无法让统计捕获 1500 行的热组合，必须先恢复粒度再 ANALYZE。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT a.attname, a.attstattarget "
                    "FROM pg_attribute a "
                    "WHERE a.attrelid = 'branch_order_line'::regclass "
                    "AND a.attname IN ('bol_product_sk','bol_quantity','bol_sold_date_sk') "
                    "ORDER BY a.attname;"
                )
            },
        },
    },
    {
        "thinking": "根因是 branch_order_line 统计过期且关键列统计粒度被降到 2：只 ANALYZE 不充分。恢复三个关键列的统计 target 到故障前的 1000（extended statistics target 随列 target 连带恢复），再刷新统计。不改 SQL、不建索引、不调 planner GUC。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "ALTER TABLE branch_order_line ALTER COLUMN bol_product_sk SET STATISTICS 1000; "
                    "ALTER TABLE branch_order_line ALTER COLUMN bol_quantity SET STATISTICS 1000; "
                    "ALTER TABLE branch_order_line ALTER COLUMN bol_sold_date_sk SET STATISTICS 1000; "
                    "ANALYZE branch_order_line;"
                )
            },
        },
    },
    {
        "thinking": "重新执行同一条完整 fault query 的 EXPLAIN ANALYZE，验证估算误差下降、计划恢复且执行时间下降。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": target_explain_sql},
        },
    },
    {
        "thinking": "统计信息已经刷新并验证完成，再次查看 topsql 确认 mean_exec_time 下降，提交结果。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {"api": "submit", "args": {"report": reference_report}},
        ],
    },
    ]

ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "不做诊断和修复，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def build_env(case, port: int, container_name: str, image_name: str = None, tool_profile: str = None) -> PGEnv:
    # 使用 TPC-DS scale=1，因为 stale statistics 需要事实表 + 维表 join 才能体现估算偏差。
    workload = TPCDSXWorkload(scale=case.dataset_scale)
    deployment = PGDockerDeployment(
        container_name=container_name,
        resources={
            "cpus": case.deployment_cpus,
            "memory_mb": case.deployment_memory_mb,
            "shm_size": case.deployment_shm_size,
            "disk_quota_mb": workload.disk_quota_mb,
        },
        postgres_user="postgres",
        postgres_password="password",
        postgres_db="testdb",
        port=port,
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=workload.data_dir,
        dataset_manifest_path=workload.manifest_path,
        image_name=image_name or case.base_image_name,
        # harness 鲁棒性（非难度变更）：宿主机被无关负载争用时，fat 镜像数据集
        # 初始化时长方差极大（可达 7-20+ 分钟，600s/1200s/2400s 均可能被
        # 取消）；正常运行 300-500s。
        initialization_timeout_seconds=3600,
    )
    env_kwargs = {"workload": workload, "deployment": deployment, "port": port}
    if tool_profile:
        env_kwargs["tool_profile"] = tool_profile
    env_kwargs.update({
        "allow_sampler_jitter": True,
        "allow_sampler_reconnect": True,
    })
    return PGEnv(**env_kwargs)










def run_with_orchestrator(
    env, scenario, case, agent, run_config, max_turns: int,
):
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        max_turns=max_turns,
        run_config=run_config,
    )
    result = orchestrator.run()
    return result, orchestrator.action_history


def print_evaluation_basis(label: str, result: dict):
    print(f"[Evaluation:{label}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")

def run_mock_full(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Stale Statistics Full-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfStaleStatisticsScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=13)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Stale Statistics Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgQueryPerfStaleStatisticsScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(ZERO_SCORE_MOCK_RESPONSES)
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str,
    port: int,
    container_name: str,
    model: str = None,
    config_path: str = "config/llm_config.json",
    max_turns: int = 30,
    run_config: OrchestratorRunConfig = None,
    agent_name: str = "llm",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
    dbot_tool_profile: str = "general_knowledge",
    ) -> float:
    print("=" * 60)
    print(f"AiOpsBench PostgreSQL - Stale Statistics {agent_name.upper()}Agent Path")
    print("=" * 60)

    max_turns = min(max_turns, 30)
    try:
        agent = build_agent(
            agent_name=agent_name,
            model=model,
            config_path=config_path,
            dbaiops_graph=dbaiops_graph,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"[{agent_name.upper()}AGENT_BLOCKED] {exc}")
        return 0.0

    tool_profile = dbot_tool_profile if agent_name == "dbot" else None

    scenario = PgQueryPerfStaleStatisticsScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case,
        port,
        container_name,
        image_name=None,
        tool_profile=tool_profile,
    )
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
                print(
                    f"[{agent_name.upper()}AGENT_BLOCKED] Agent reached max_turns without submit; "
                    "this is recorded as an execution blocker, not a scenario setup failure."
                )
    print_evaluation_basis(agent_name, result)
    return passed


def build_agent(
    agent_name: str,
    model: str = None,
    config_path: str = "config/llm_config.json",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
):
    return build_experiment_agent(
        model=model,
        config_path=config_path,
        use_native_tools=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Run the PG stale statistics query performance scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15447)
    parser.add_argument("--container-name", default="aiopsbench-pg-queryperf-02")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--llm-config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot. Default: general_knowledge.")
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    parser.add_argument(
        "--diagnosis-match-mode",
        choices=["exact", "semantic"],
        default="exact",
        help="DP matching strategy: exact alias matching or semantic judge.",
    )
    parser.add_argument(
        "--diagnosis-semantic-model",
        default=None,
        help="Judge model key in --diagnosis-semantic-config used by semantic DP matching; defaults to --model.",
    )
    parser.add_argument(
        "--diagnosis-semantic-config",
        default="config/llm_config.json",
        help="LLM config file that must contain --diagnosis-semantic-model.",
    )
    scenario_definition = PgQueryPerfStaleStatisticsScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
        diagnosis_match_mode=args.diagnosis_match_mode,
        diagnosis_semantic_model=args.diagnosis_semantic_model or args.model,
        diagnosis_semantic_config_path=args.diagnosis_semantic_config,
    )

    if args.max_turns > 30:
        raise ValueError("--max-turns must be <= 30")
    if args.mode in ("mock", "all"):
        run_mock_full(args.case, args.port, args.container_name, run_config)
    if args.mode in ("zero", "all"):
        run_mock_zero(args.case, args.port, args.container_name, run_config)
    if args.mode in ("llm", "all"):
        run_llm(args.case,
            args.port,
            args.container_name,
            args.model,
            args.llm_config,
            args.max_turns,
            run_config,
            agent_name=args.agent,
            dbaiops_graph=args.dbaiops_graph,
            dbot_tool_profile=args.dbot_tool_profile,
        )


if __name__ == "__main__":
    main()
