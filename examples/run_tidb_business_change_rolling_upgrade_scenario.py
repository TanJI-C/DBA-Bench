import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbBusinessChangeRollingUpgradeScenario
from src.execution.deployment import TiDBDockerDeployment
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


SUCCESS_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": [
            "Completed compatibility precheck, logical backup manifest, and online PD TiKV TiDB rolling upgrade from v6.5.0 to v7.5.0.",
            "Kept RPO=0 and did not mutate the business table; TiKV leaders were migrated before each node replacement.",
        ],
        "verification": [
            "Before and after canary queries returned the same semantic result on every TiDB endpoint and sessions reconnected.",
            "Prometheus monitoring coverage was checked for all PD TiKV TiDB targets; query p95 stayed within the SLO.",
            "DDL owner, server-version, new collation, statistics compatibility and rollback conditions were reviewed; rollback is bounded by the v6.5.0 backup and RPO=0.",
        ],
    },
    "summary": "The rolling upgrade completed with business semantics, monitoring coverage, SLO and rollback boundaries verified.",
}


def _action(api: str, **args):
    return {"api": api, "args": args}


def _release(operation: str, **args):
    return _action("manage_cluster", resource="release", operation=operation, **args)


def _service(operation: str, **args):
    return _action("manage_cluster", resource="service", operation=operation, **args)


def _monitoring():
    return _action("manage_cluster", resource="monitoring", operation="get")


def _cluster_info_sql(case):
    return _action(
        "execute_sql",
        sql_query=(
            "SELECT TYPE, INSTANCE, VERSION, START_TIME, UPTIME "
            "FROM information_schema.cluster_info ORDER BY TYPE, INSTANCE"
        ),
    )


def _component_targets(case):
    topology = case.runtime.topology
    return (
        *(f"pd/pd-{index}" for index in range(topology.pd_count)),
        *(f"tikv/tikv-{index}" for index in range(topology.tikv_count)),
        *(f"tidb/tidb-{index}" for index in range(topology.tidb_count)),
    )


def _billing_rollout_mock_responses(case):
    component_targets = _component_targets(case)
    return [
        {
            "thinking": "一次建立安全变更边界：兼容性 precheck、可回退备份、升级前 canary 语义与前台基线。",
            "actions": [
                _release("prepare"),
                _release("snapshot"),
                _release("verify", parameters={"phase": "before"}),
                _cluster_info_sql(case),
                _action("query_metrics", metric_type="active_connections"),
                _action("query_metrics", metric_type="query_latency"),
            ],
        },
        {
            "thinking": "按 PD、TiKV、TiDB 顺序一次完成滚动升级，再核对 canary 语义、监控覆盖和 p95 后提交变更报告。",
            "actions": [
                *(_release("upgrade", target=target) for target in component_targets),
                _release("verify", parameters={"phase": "after"}),
                _monitoring(),
                _cluster_info_sql(case),
                _action("query_metrics", metric_type="query_latency"),
                _action("submit", report=case.reference_report),
            ],
        },
    ]


def build_mock_responses(case):
    if case.case_no == 1:
        return _billing_rollout_mock_responses(case)
    topology = case.runtime.topology
    component_targets = _component_targets(case)
    pd_end = topology.pd_count
    tikv_end = pd_end + topology.tikv_count
    return [
        {
            "thinking": "First establish the live source version, compatibility state, backup boundary, and canary semantic baseline before changing any component.",
            "actions": [
                _release("prepare"),
            ],
        },
        {
            "thinking": "The first health check may observe a store still converging after startup; repeat the precheck before creating the rollback boundary.",
            "actions": [
                _release("prepare"),
                _release("prepare"),
                _release("prepare"),
                _release("snapshot"),
                _release("verify", parameters={"phase": "before"}),
                _cluster_info_sql(case),
                _action("query_metrics", metric_type="active_connections"),
                _action("query_metrics", metric_type="query_latency"),
            ],
        },
        {
            "thinking": "Upgrade the control plane one PD member at a time and observe cluster health after every replacement.",
            "actions": [
                *(_release("upgrade", target=target) for target in component_targets[:pd_end]),
                _cluster_info_sql(case),
                _service("list"),
            ],
        },
        {
            "thinking": "Upgrade TiKV in the safe phase after PD is complete; the deployment migrates leaders before recreating each store.",
            "actions": [
                *(_release("upgrade", target=target) for target in component_targets[pd_end:tikv_end]),
                _action("manage_cluster", resource="store", operation="list"),
                _action("manage_cluster", resource="operator", operation="list"),
                _action("query_metrics", metric_type="disk_io"),
            ],
        },
        {
            "thinking": "Upgrade TiDB nodes one by one, verify reconnect and business semantics, then verify monitoring and SLO before submitting the report.",
            "actions": [
                *(_release("upgrade", target=target) for target in component_targets[tikv_end:]),
                _release("verify", parameters={"phase": "after"}),
                _monitoring(),
                _cluster_info_sql(case),
                _action("query_metrics", metric_type="query_latency"),
                _action("submit", report=SUCCESS_REPORT),
            ],
        },
    ]


def main() -> None:
    scenario = TidbBusinessChangeRollingUpgradeScenario()
    parser = argparse.ArgumentParser(
        description="Run TiDB BC01: v6.5 to v7.5 online rolling upgrade and business acceptance."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=40)
    parser.add_argument("--port", type=int, default=4780)
    parser.add_argument("--container-name", default="tidb-bc01-rolling-upgrade")
    parser.add_argument("--storage-key", required=True)
    parser.add_argument("--storage-root", required=True)
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    deployment = TiDBDockerDeployment(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        storage_key=args.storage_key,
        storage_root=args.storage_root,
    )
    env = TiDBEnv(deployment=deployment)
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
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
