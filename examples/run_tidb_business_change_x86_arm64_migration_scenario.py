import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbBusinessChangeX86Arm64MigrationScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


CASE_ID = "offline_x86_to_arm64_online_migration"
SCENARIO = TidbBusinessChangeX86Arm64MigrationScenario()
CASE = SCENARIO.get_case(CASE_ID)


def _migration_actions() -> tuple[tuple[str, str | None], ...]:
    return (
        ("merge_offline_mirror", None),
        ("verify_arm64_bundle", None),
        ("backup_tiup_metadata", None),
        ("copy_monitor_history", None),
        *( ("add_arm64_pd", f"pd-arm64-{index}") for index in range(3) ),
        ("transfer_pd_leader", "pd-arm64-0"),
        *( ("retire_x86_pd", f"pd-x86-{index}") for index in range(3) ),
        *( ("add_arm64_tikv", f"tikv-arm64-{index}") for index in range(3) ),
        *( ("rebalance_tikv", f"tikv-arm64-{index}") for index in range(3) ),
        *( ("retire_x86_tikv", f"tikv-x86-{index}") for index in range(3) ),
        *( ("add_arm64_tidb", f"tidb-arm64-{index}") for index in range(2) ),
        ("verify_business_checksum", None),
        ("prepare_rollback", None),
        ("cutover_to_arm64", None),
        *( ("retire_x86_tidb", f"tidb-x86-{index}") for index in range(2) ),
    )


MIGRATION_ACTIONS = _migration_actions()
PRE_CUTOVER_ACTIONS = MIGRATION_ACTIONS[:-5]
FINAL_MIGRATION_ACTIONS = MIGRATION_ACTIONS[-5:]


def _migration_actions_sql(
    case,
    actions: tuple[tuple[str, str | None], ...],
) -> str:
    values = ", ".join(
        f"({case.migration_id!r}, '{action}', {repr(component) if component is not None else 'NULL'})"
        for action, component in actions
    )
    return (
        f"INSERT INTO {case.control_db}.{case.actions_table} "
        "(migration_id, action_name, component) VALUES "
        + values
    )


def _billing_migration_mock_responses(case):
    return [
        {
            "thinking": "用一次就绪核查同时确认 billing scope 与 fraud rehearsal 的区分、离线包兼容性、TiUP 元数据备份和监控历史保留。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT TYPE, INSTANCE, VERSION FROM information_schema.cluster_info ORDER BY TYPE, INSTANCE"}},
                {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT migration_id, step_no, action_name, component, prerequisite, status "
                            f"FROM {case.control_db}.{case.runbook_table} ORDER BY migration_id, step_no"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT migration_id, business_scope, request_status, phase, active_arch, target_arch "
                            f"FROM {case.control_db}.{case.state_table} ORDER BY migration_id"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT component, arch, version, available, expected_digest, observed_digest "
                            f"FROM {case.control_db}.{case.artifacts_table} ORDER BY component, arch"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT migration_id, node_id, component, arch, state, leader, region_count "
                            f"FROM {case.control_db}.{case.nodes_table} ORDER BY component, node_id"
                        )
                    },
                },
            ],
        },
        {
            "thinking": "观察在线 intent 后一次提交切流前的全部前置动作，由控制器按 runbook 前置次序逐项推进。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT COUNT(*), SUM(status = 'processed'), SUM(status = 'pending') "
                            f"FROM {case.control_db}.{case.intents_table}"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": _migration_actions_sql(case, PRE_CUTOVER_ACTIONS)},
                },
            ],
        },
        {
            "thinking": "等待前置拓扑动作与在线 intent 收敛，确认 checksum 前置条件后提交 checksum、回退点、切流和退役动作。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(15)"}},
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT action_id, migration_id, action_name, component, status, error_message "
                            f"FROM {case.control_db}.{case.actions_table} ORDER BY action_id"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT migration_id, business_scope, phase, active_arch, rollback_ready, cutover_epoch, p95_latency_ms "
                            f"FROM {case.control_db}.{case.state_table}"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT COUNT(*), SUM(status = 'processed'), SUM(status = 'pending'), "
                            f"COUNT(DISTINCT processed_order_id) FROM {case.control_db}.{case.intents_table}"
                        )
                    },
                },
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(15)"}},
                {
                    "api": "execute_sql",
                    "args": {"sql_query": _migration_actions_sql(case, FINAL_MIGRATION_ACTIONS)},
                },
            ],
        },
        {
            "thinking": "等待校验、切流和退役完成，读取最终 action、迁移状态、业务真值和监控历史后提交变更报告。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(30)"}},
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT action_id, migration_id, action_name, component, status, error_message "
                            f"FROM {case.control_db}.{case.actions_table} ORDER BY action_id"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT migration_id, business_scope, phase, active_arch, rollback_ready, cutover_epoch, p95_latency_ms "
                            f"FROM {case.control_db}.{case.state_table}"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT COUNT(*), SUM(order_id), SUM(amount_cents), SUM(tenant_id) "
                            f"FROM {case.business_db}.{case.orders_table} WHERE order_id <= {case.seed_rows}"
                        )
                    },
                },
                {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
                {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def build_mock_responses(case):
    if case.case_no == 1:
        return _billing_migration_mock_responses(case)
    return [
    {
        "thinking": "建立在线业务、离线包、组件架构和迁移 runbook 基线。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT TYPE, INSTANCE, VERSION FROM information_schema.cluster_info ORDER BY TYPE, INSTANCE"}},
            {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT migration_id, step_no, action_name, component, prerequisite, status "
                        f"FROM {case.control_db}.{case.runbook_table} ORDER BY migration_id, step_no"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT migration_id, business_scope, request_status, phase, active_arch, target_arch "
                        f"FROM {case.control_db}.{case.state_table} ORDER BY migration_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT component, arch, version, available, expected_digest, observed_digest "
                        f"FROM {case.control_db}.{case.artifacts_table} ORDER BY component, arch"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT migration_id, node_id, component, arch, state, leader, region_count "
                        f"FROM {case.control_db}.{case.nodes_table} ORDER BY component, node_id"
                    )
                },
            },
        ],
    },
    {
        "thinking": "先观察在线 intent，再提交到切流前的前置动作；控制器会逐项推进，避免长事务阻塞在线写入。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT COUNT(*), SUM(status = 'processed'), SUM(status = 'pending') "
                        f"FROM {case.control_db}.{case.intents_table}"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": _migration_actions_sql(case, PRE_CUTOVER_ACTIONS)},
            },
        ],
    },
    {
        "thinking": "等待前置拓扑动作和在线 intent 收敛，再检查是否满足 checksum 的前置条件。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(15)"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT action_id, migration_id, action_name, component, status, error_message "
                        f"FROM {case.control_db}.{case.actions_table} ORDER BY action_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT migration_id, business_scope, phase, active_arch, rollback_ready, cutover_epoch, p95_latency_ms "
                        f"FROM {case.control_db}.{case.state_table}"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT COUNT(*), SUM(status = 'processed'), SUM(status = 'pending'), "
                        f"COUNT(DISTINCT processed_order_id) FROM {case.control_db}.{case.intents_table}"
                    )
                },
            },
            {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(15)"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT COUNT(*), SUM(status = 'processed'), SUM(status = 'pending'), "
                        f"COUNT(DISTINCT processed_order_id) FROM {case.control_db}.{case.intents_table}"
                    )
                },
            },
        ],
    },
    {
        "thinking": "前置动作已完成，提交 checksum、回退点、切流和旧 TiDB 退役动作。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {"sql_query": _migration_actions_sql(case, FINAL_MIGRATION_ACTIONS)},
            },
        ],
    },
    {
        "thinking": "等待最后的校验、切流和退役动作完成，再读取最终控制面状态。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(15)"}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT action_id, migration_id, action_name, component, status, error_message "
                        f"FROM {case.control_db}.{case.actions_table} ORDER BY action_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT migration_id, business_scope, phase, active_arch, rollback_ready, cutover_epoch, p95_latency_ms "
                        f"FROM {case.control_db}.{case.state_table}"
                    )
                },
            },
            # Let the live controller drain the intent queue and retry the SLO-gated cutover.
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(30)"}},
        ],
    },
    {
        "thinking": "检查最终 action 状态、迁移状态、业务真值和监控历史。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT action_id, migration_id, action_name, component, status, error_message "
                        f"FROM {case.control_db}.{case.actions_table} ORDER BY action_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT COUNT(*), SUM(order_id), SUM(amount_cents), SUM(tenant_id) "
                        f"FROM {case.business_db}.{case.orders_table} WHERE order_id <= {case.seed_rows}"
                    )
                },
            },
            {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
            {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
        ],
    },
    {
        "thinking": "迁移完成后提交结构化变更报告。",
        "action": {"api": "submit", "args": {"report": case.reference_report}},
    },
    ]


FULL_SCORE_MOCK_RESPONSES = build_mock_responses(CASE)


def main() -> None:
    scenario = SCENARIO
    parser = argparse.ArgumentParser(description="Run TiDB BC08 x86-to-arm64 migration.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=40)
    parser.add_argument("--port", type=int, default=4700)
    parser.add_argument("--container-name", default="tidb-bc08")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
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
            system_prompt="You are a TiDB DBA agent.",
            use_native_tools=False,
        )
        agent.set_mock_responses(build_mock_responses(case))
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (None, True, True):
            raise RuntimeError(
                f"BC08 mock must pass OP/SP with DP=None, observed={observed!r}, result={result!r}"
            )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
