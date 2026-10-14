"""Run the PG-RG-MF01 PgBouncer connection-budget scenario."""

import argparse
from dataclasses import replace
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.base import evaluation_passed
from src.protocols.report import EMPTY_REPORT
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.execution.specs import HostPortLayout
from src.execution.history.metrics import format_utc_timestamp
from src.execution.history.records import HistoricalRecordSource
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.postgres.resource_governance.pgbouncer_connection_budget import (
    PGBOUNCER_PORTS,
    PgResourceGovernancePgbouncerConnectionBudgetScenario,
)


def _response(api: str, args: dict, thinking: str) -> dict:
    return {"thinking": thinking, "action": {"api": api, "args": args}}


def build_full_score_mock_responses(case, history_window=None):
    responses = [
        _response(
            "query_metrics",
            {"metric_type": "pgbouncer_pool_clients", "target": f"{case.dbname}/{case.checkout_user}"},
            "先从 frozen history 查看 checkout pool 的原始 waiting、active 和 maxwait 时间序列。",
        ),
        _response(
            "query_metrics",
            {"metric_type": "pgbouncer_pool_servers", "target": f"{case.dbname}/{case.checkout_user}"},
            "比较 checkout pool 的 server 分布，确认 waiting 上升不是整个数据库都没有 backend。",
        ),
        _response(
            "query_metrics",
            {"metric_type": "database_capacity", "target": None},
            "联合数据库 active connections 和 CPU，确认仍有 headroom，不能扩大全局预算。",
        ),
        _response(
            "query_metrics",
            {"metric_type": "service_slo", "target": "checkout"},
            "查看 checkout SLO 的时间变化，再与 report 和 ETL 的业务进度比较。",
        ),
    ]
    if history_window is not None:
        responses.append(
            _response(
                "read_log",
                {
                    "log_type": "operation_event",
                    "start_timestamp": format_utc_timestamp(history_window[0]),
                    "end_timestamp": format_utc_timestamp(history_window[1]),
                    "target": "pgbouncer",
                    "filters": {"entity": "pgbouncer"},
                    "lines": 50,
                },
                "在 metric 窗口内查询公共 operation_event，确认配置 revision 和 workload 阶段，而不是读取物理 history 表。",
            )
        )
    responses.extend([
        _response(
            "manage_instance",
            {"action": "pgbouncer_show_config"},
            "查看真实 PgBouncer 配置和 pool mode，确认 PostgreSQL max_connections 不应被扩大。",
        ),
        _response(
            "manage_instance",
            {"action": "pgbouncer_show_pools"},
            "查看各 database/user pool 的等待和 server 状态，并保留合法报表噪声。",
        ),
        _response(
            "execute_sql",
            {"sql_query": "SELECT current_setting('max_connections')::integer AS max_connections;"},
            "确认数据库总连接预算是固定的，再处理 pool partition shortage。",
        ),
        _response(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT rolname, rolconnlimit FROM pg_roles "
                    "WHERE rolname IN ('checkout_user','report_user','etl_user') "
                    "ORDER BY rolname;"
                )
            },
            "检查 PostgreSQL role-level connection partition，不能只看 PgBouncer SHOW POOLS。",
        ),
        _response(
            "execute_sql",
            {
                "sql_query": (
                    f"ALTER ROLE {case.checkout_user} CONNECTION LIMIT "
                    f"{case.recovered_checkout_role_connection_limit};"
                )
            },
            "恢复 checkout role 的有界连接能力，再在固定总预算内分配 PgBouncer pool。",
        ),
        _response(
            "manage_instance",
            {"action": "pgbouncer_set_config", "target": "default_pool_size", "value": "4"},
            "在固定总预算内提高共享 pool 的可用分区，同时保留 per-user 公平性约束，不修改 PostgreSQL max_connections。",
        ),
        _response(
            "manage_instance",
            {"action": "pgbouncer_set_config", "target": "reserve_pool_size", "value": "0"},
            "不依赖额外 reserve ceiling，避免短 burst 把固定下游预算挤出 reporting/ETL。",
        ),
        _response(
            "manage_instance",
            {"action": "pgbouncer_set_config", "target": "max_user_connections", "value": str(case.recovered_checkout_role_connection_limit)},
            "设置与恢复后的 checkout 分区一致的每用户上限，随后 reload 并通过真实 replay 验收公平性。",
        ),
        _response(
            "manage_instance",
            {"action": "pgbouncer_set_config", "target": "max_db_connections", "value": str(case.max_database_connections)},
            "保持固定的 PgBouncer 下游数据库预算，不扩大 PostgreSQL 或 PgBouncer 的连接 ceiling。",
        ),
        _response("manage_instance", {"action": "pgbouncer_reload"}, "让 PgBouncer 重新加载有界策略。"),
        _response(
            "manage_instance",
            {"action": "pgbouncer_show_pools"},
            "验证 queue 收敛、checkout/report/ETL pool 都仍然可见。",
        ),
        _response(
            "submit",
            {"report": case.reference_report},
            "提交资源策略交付和真实 workload replay 的验收结果。",
        ),
    ])
    return responses


def build_zero_score_mock_responses(case):
    return [
        _response(
            "manage_instance",
            {"action": "pgbouncer_set_config", "target": "pool_mode", "value": "statement"},
            "错误地切换到会破坏事务语义的 statement pooling。",
        ),
        _response("submit", {"report": EMPTY_REPORT}, "没有完成安全的连接预算治理。"),
    ]


class PgBouncerHistoryPGEnv(PGEnv):
    """Start generic history when the Case exposes TopSQL or component logs."""

    def configure_history_observability(self, spec) -> None:
        if any(
            source in spec.record_sources
            for source in (
                HistoricalRecordSource.TOPSQL,
                HistoricalRecordSource.COMPONENT_LOG,
            )
        ):
            self.disable_generic_sampler = False
        return super().configure_history_observability(spec)


def build_env(case, port: int, container_name: str, image_name: str | None = None) -> PGEnv:
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=image_name or case.base_image_name,
    )
    # Frozen-history RG1 captures the shared PostgreSQL sampler and scenario-owned
    # PgBouncer sampler on the same 2-second grid.
    env = PgBouncerHistoryPGEnv(
        workload=None,
        deployment=deployment,
        port=port,
        sample_interval_sec=2,
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )
    return env


def run_mode(case_id: str, mode: str, args) -> dict:
    scenario = PgResourceGovernancePgbouncerConnectionBudgetScenario()
    if args.seed is not None:
        os.environ["AIOPS_SEED"] = str(args.seed)
    os.environ["AIOPS_PGBOUNCER_PORT"] = str(args.pgbouncer_port)
    case = scenario.get_case(case_id)
    case = replace(case, runtime=replace(case.runtime,
        host_ports=HostPortLayout(offsets=(0, args.pgbouncer_port - args.port))))
    env = build_env(case, args.port, f"{args.container_name}-{case_id}-{mode}")
    if mode == "mock":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a PostgreSQL DBA agent.", use_native_tools=False)
        agent.set_mock_responses(build_full_score_mock_responses(case))
        def prepare_mock_after_setup(environment):
            timeline = getattr(environment, "_history_timeline", None)
            if timeline is None:
                return
            target_window = timeline.audit["target_window"]
            start_ms = max(
                int(timeline.visible_start_ms),
                int(target_window["start_ms"]) - 10 * 60 * 1000,
            )
            end_ms = min(
                int(timeline.visible_end_ms),
                int(target_window["end_ms"]) + 10 * 60 * 1000,
            )
            agent.set_mock_responses(build_full_score_mock_responses(case, (start_ms, end_ms)))
        agent.prepare_after_setup = prepare_mock_after_setup
        max_turns = 20
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a PostgreSQL DBA agent.", use_native_tools=False)
        agent.set_mock_responses(build_zero_score_mock_responses(case))
        max_turns = 4
    else:
        agent_mode = os.environ.get("AIOPS_AGENT_MODE", args.mode)
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
            reasoning_effort=args.reasoning_effort if agent_mode in {"llm", "v-expel"} else None,
        )
        max_turns = min(args.max_turns, 30)
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        max_turns=max_turns,
        run_config=run_config,
    )
    result = orchestrator.run()
    # The evaluator result is the experiment result, including an honest
    # logical failure.  Do not turn a failed Mock/LLM outcome into a process
    # failure: the runner must preserve DP/OP/SP so it is not mistaken for an
    # environment-invalid run.
    print(f"[{mode}] case={case_id} DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")
    return result


def main() -> None:
    scenario = PgResourceGovernancePgbouncerConnectionBudgetScenario()
    parser = argparse.ArgumentParser(description="Run PG-RG-MF01 PgBouncer connection-budget scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=PGBOUNCER_PORTS["postgres"])
    parser.add_argument("--pgbouncer-port", type=int, default=PGBOUNCER_PORTS["pgbouncer"])
    parser.add_argument("--container-name", default="aiopsbench-pg-rg-pgbouncer")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--reasoning-effort", choices=("low", "medium", "high", "xhigh"), default="xhigh")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    args = parser.parse_args()
    modes = ("mock", "zero", "llm") if args.mode == "all" else (args.mode,)
    for mode in modes:
        run_mode(args.case, mode, args)


if __name__ == "__main__":
    main()
