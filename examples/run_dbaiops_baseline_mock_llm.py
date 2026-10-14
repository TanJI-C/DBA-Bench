"""Smoke: real PG scenario + real DbaiopsAgent + scripted LLM (no model calls).

Extends the official run_pg_query_perf_missing_index_scenario.py mock path to
the DBAIOps baseline: the scenario's fault snapshot, real graph evolution, ADF,
anomaly confirmation and report finalization all run for real; only the inner
LLM is a scripted stub replaying the case's full-score action sequence.
"""

import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.execution.environments.postgres import PGEnv
from src.scenarios.postgres import PgQueryPerfMissingIndexScenario
from src.agents.baselines.dbaiops.agent import DbaiopsAgent
from src.agents.agent import LLMAgent
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSXWorkload

CONTAINER_NAME = "aiopsbench-pg-dbaiops-smoke"
PORT = 15432


def build_full_score_replies(case):
    """The official full-score script (see
    run_pg_query_perf_missing_index_scenario.py), shaped as
    (thinking, actions) turns for DbaiopsAgent's inner-LLM seam."""
    target_explain_sql = (
        "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
        f"{case.fault_fingerprint_sql.rstrip(';')};"
    )
    index_check_sql = (
        "SELECT indexname, indexdef FROM pg_indexes "
        f"WHERE tablename = '{case.table}' "
        f"AND (indexdef ILIKE '%{case.column}%' OR indexdef ILIKE '%substring%');"
    )
    create_index_sql = (
        f"CREATE INDEX IF NOT EXISTS {case.remediation_index_name} "
        f"ON {case.table} ((substring({case.column}, 1, 3)));"
    )
    return [
        ("先看 topsql 找出 mean_exec_time 最高的故障指纹查询。", [
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
        ]),
        ("对告警中的完整复杂查询做 EXPLAIN ANALYZE，确认 substring 触发顺序扫描。", [
            {"api": "execute_sql", "args": {"sql_query": target_explain_sql}},
        ]),
        (f"检查 {case.table} 表索引定义，确认缺少表达式索引。", [
            {"api": "execute_sql", "args": {"sql_query": index_check_sql}},
        ]),
        ("创建 evaluator 合同允许的 substring 表达式索引。", [
            {"api": "execute_sql", "args": {"sql_query": create_index_sql}},
        ]),
        ("复查 topsql 并重新 EXPLAIN，确认故障查询执行时间下降。", [
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {"api": "execute_sql", "args": {"sql_query": target_explain_sql}},
        ]),
        ("重复验证同一查询，排除冷缓存开销。", [
            {"api": "execute_sql", "args": {"sql_query": target_explain_sql}},
        ]),
        ("目标查询已恢复索引访问路径，提交结构化报告。", [
            {"api": "submit", "args": {"report": {
                "diagnosis": {"conditions": [
                    {"type": "finding",
                     "factor": "sequential scan on product",
                     "entity": "product",
                     "evidence": ["EXPLAIN ANALYZE showed a sequential scan on product "
                                  "for the substring predicate"]},
                    {"type": "finding",
                     "factor": "missing substring expression index",
                     "entity": "product",
                     "evidence": ["pg_indexes listed no expression index over "
                                  "substring(pr_category, 1, 3)"]},
                    {"type": "finding",
                     "factor": "substring predicate forces sequential scan",
                     "entity": "product",
                     "evidence": ["the substring predicate forces sequential scan on "
                                  "product for the reporting query"]},
                ]},
                "outcome": {
                    "changes": [f"created {case.remediation_index_name}"],
                    "verification": ["repeated EXPLAIN ANALYZE confirmed index usage"],
                },
                "summary": "Missing substring expression index created; reporting query recovered.",
            }}},
        ]),
    ]


def mock_report(case):
    """Final RootCauseAnalyser report text covering the exact-DP aliases."""
    return (
        "Root cause analysis: the reporting query filters "
        f"{case.table} with substring({case.column}, 1, 3) = 'Sho'. "
        "Evidence: EXPLAIN ANALYZE showed a sequential scan on product, because the "
        "substring predicate prevents indexed access on the pr_category column. "
        "The matching substring expression index is missing — index inspection on "
        f"{case.table} listed no expression index over substring({case.column}, 1, 3). "
        "Remediation applied: created "
        f"{case.remediation_index_name} ON {case.table} ((substring({case.column}, 1, 3))) "
        "via execute_sql. Verification: repeated EXPLAIN ANALYZE on the same complex "
        "query no longer performs a sequential scan on product and the workload "
        "topsql latency for the fault fingerprint dropped. "
        "Follow-up: keep auto-analyze scheduled so statistics stay fresh."
    )


def build_env(case):
    env = PGEnv(
        workload=TPCDSXWorkload(scale=case.dataset_scale),
        port=PORT,
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )
    # Unique container name: the shared host prunes the generic default name.
    env.deployment.container_name = CONTAINER_NAME
    env.deployment.image_name = case.base_image_name
    # NOTE: keep the calibrated default container resources — the injector's
    # acceptance gate requires the fault scan to stay slow (>=5s), and the
    # official mock path runs under the same defaults.
    return env


def main():
    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")

    env = build_env(case)
    agent = DbaiopsAgent(
        model="mock",
        graph_path="data/knowledge_graph/pg_experience_graph.json",
        config_path="config/llm_config.json",
    )
    inner_llm = LLMAgent(model="mock", url="mock", api_key="mock", use_native_tools=True)
    replies = iter(build_full_score_replies(case))
    inner_llm._next_llm_actions = lambda max_empty_retries: next(replies)
    inner_llm.call_text = lambda prompt, system_prompt=None: mock_report(case)
    agent._llm = inner_llm

    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        max_turns=30,
        run_config=OrchestratorRunConfig(),  # auto: uses the fresh fault snapshot
    )
    evaluation = orchestrator.run()

    print("\n================ SMOKE SUMMARY ================")
    print("matched trigger:", agent._matched_trigger.id if agent._matched_trigger else None)
    print("graph nodes loaded:", len(agent._graph.nodes))
    print("diagnosis report is mock:", agent._diagnosis_report == mock_report(case))
    print("executed changes:", agent._executed_changes)
    apis = {}
    for action in agent.action_history:
        apis[action["api"]] = apis.get(action["api"], 0) + 1
    print("gateway actions by api:", apis)
    print("evaluation:", json.dumps(evaluation, ensure_ascii=False, default=str)[:1500])
    passed = (
        evaluation["DiagnosisPass"] and evaluation["OutcomePass"] and evaluation["SafePass"]
    )
    print(f"SMOKE RESULT: {'PASS' if passed else 'FAIL'} (DP={evaluation['DiagnosisPass']}, "
          f"OP={evaluation['OutcomePass']}, SP={evaluation['SafePass']})")
    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
