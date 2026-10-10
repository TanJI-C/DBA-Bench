import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb.health_check import TidbHealthCheckEmptyRegionLeaderSkewScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator


CASE_ID = "regional_job_empty_region_skew_review"

def full_pass_mock_responses(case) -> list[dict]:
    return [
    {
        "thinking": "这是例行巡检，先观察 Region 规模、TopSQL 和 workload 活动，再区分短时窗口与持续风险。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "region_count"}},
            {"api": "query_metrics", "args": {"metric_type": "topsql"}},
            {"api": "query_metrics", "args": {"metric_type": "workload_activity"}},
        ],
    },
    {
        "thinking": "用年龄窗口、时间趋势、配置历史和 store 分布交叉确认持续风险，排除短时 split 与 hot-store 候选。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT metric_name, target, MIN(value), MAX(value), COUNT(DISTINCT sample_ts) "
                        "FROM benchops.hc03_pd_region_samples "
                        "GROUP BY metric_name, target ORDER BY metric_name, target"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT config_key, config_value, observed_at "
                        "FROM benchops.hc03_pd_config ORDER BY observed_at, config_key"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT COUNT(*), SUM(is_empty = 1), SUM(approximate_keys = 0), "
                        f"SUM(is_empty = 1 AND TIMESTAMPDIFF(MINUTE, first_seen_at, last_seen_at) >= {case.persistent_age_minutes}), "
                        f"SUM(approximate_keys = 0 AND TIMESTAMPDIFF(MINUTE, first_seen_at, last_seen_at) >= {case.persistent_age_minutes}), "
                        f"SUM(is_empty = 1 AND TIMESTAMPDIFF(MINUTE, first_seen_at, last_seen_at) < {case.persistent_age_minutes}) "
                        "FROM benchops.hc03_region_inventory"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT store_id, leader_count, persistent_leader_count, recent_leader_count, region_count "
                        "FROM benchops.hc03_store_distribution ORDER BY store_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": "SELECT COUNT(*), SUM(event_id) FROM benchops.hc03_business_events",
                },
            },
        ],
    },
    {
        "thinking": "把源事实压缩成结构化巡检结论，只更新 review row，不改业务数据或 PD 配置。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "UPDATE benchops.hc03_region_capacity_review SET "
                        "status = 'action_required', "
                        "risk_confirmed = 1, persistent_pattern_confirmed = 1, decoy_causes_excluded = 1, "
                        "leader_skew_attributed = 1, scheduler_constraint_confirmed = 1, plan_bounded = 1, "
                        "plan_cross_table = 1, maintenance_window_required = 1, restart_required = 0, "
                        "business_data_mutation_allowed = 0, verification_complete = 1, "
                        "risk_entity = 'persistent capacity review for an uneven Region population', "
                        f"empty_region_count = {case.expected_empty_region_count}, zero_key_region_count = {case.expected_zero_key_region_count}, "
                        f"persistent_empty_region_count = {case.persistent_empty_region_count}, persistent_zero_key_region_count = {case.persistent_zero_key_region_count}, "
                        f"recent_empty_region_count = {case.recent_empty_region_count}, total_region_count = {case.expected_total_region_count}, "
                        f"empty_ratio = {case.expected_empty_ratio:.4f}, persistent_empty_ratio = {case.expected_persistent_empty_ratio:.4f}, "
                        f"leader_skew_ratio = {case.expected_leader_skew_ratio:.4f}, persistent_leader_skew_ratio = {case.expected_persistent_leader_skew_ratio:.4f}, "
                        f"merge_rate_per_min = {case.expected_merge_rate_per_min:.4f}, observation_window_minutes = {case.observation_window_minutes}, "
                        "recommended_action = 'stage an equivalent multi-table consolidation plan in a controlled maintenance window', "
                        "safety_boundary = 'preserve business rows and keep healthy components running', "
                        "verification = 'reconciled source counts, effective configuration, trend window and event-id sum', "
                        f"business_checksum = {case.business_checksum} "
                        f"WHERE review_key = '{case.review_key}'"
                    )
                },
            },
        ],
    },
    {
        "thinking": "这是无根因的日常健康检查，提交 N/A diagnosis 和可复核的巡检结论。",
        "action": {
            "api": "submit",
            "args": {"report": case.reference_report},
        },
    },
    ]


def main() -> None:
    scenario = TidbHealthCheckEmptyRegionLeaderSkewScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB HC03 empty-region capacity health-check scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--port", type=int, default=28640)
    parser.add_argument("--container-name", default="tidb-hc03-empty-region")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA agent performing a routine health check.",
            use_native_tools=False,
        )
        agent.set_mock_responses(full_pass_mock_responses(case))
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    result = Orchestrator(env, scenario, case, agent, max_turns=args.max_turns).run()
    if args.mode == "mock":
        expected = (None, True, True)
        actual = (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"])
        if actual != expected:
            raise RuntimeError(f"HC03 mock path failed: expected={expected}, actual={actual}, result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
