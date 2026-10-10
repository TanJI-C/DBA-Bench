import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.postgres import PgBusinessChangeFkValidationScenario
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
    if case.fault_variant == "storm":
        factors = (
            "the queued access exclusive alter request makes every later lock request on order_items queue behind it",
            "the fk validate constraint job keeps failing and the constraint is still not valid",
            "an orphaned prepared transaction holds the weak lock that blocks the pipeline ddl",
            "all queries and writes on order_items queue behind the lock chain",
            "after unblocking, the fk validation must still complete with convalidated true",
            "the same governance rollout also left the order_items_peer foreign key not valid and pending validation",
            "legacy orphan order rows violate the foreign key so replaying validate constraint fails until the orphan data is remediated",
        )
        changes = [
            "resolved the orphaned prepared transaction with ROLLBACK PREPARED, cancelled the queued pipeline DDL request, stopped the failing validation job, removed the legacy orphan order rows that failed validation, and reran VALIDATE CONSTRAINT for both rollout foreign keys",
        ]
    else:
        factors = (
            "the fk validate constraint session waits for the maintenance transaction lock",
            "the fk validate constraint session is still pending",
            "after cancelling the validate it must be replayed until convalidated is true",
        )
        changes = [
            "terminated the stuck maintenance transaction so the validation job could proceed",
        ]
    return {
        "diagnosis": {"conditions": [
            {
                "type": "finding",
                "factor": factor,
                "entity": "fk_order_items_customer",
                "evidence": [f"pg_stat_activity, pg_locks and pg_constraint confirmed: {factor}"],
            }
            for factor in factors
        ]},
        "outcome": {
            "changes": changes,
            "verification": [
                "lock queue drained, business reads restored, and fk_order_items_customer is convalidated=true",
            ],
        },
        "summary": "The FK validation lock-queue incident was resolved and the governance goal verified.",
    }


def build_mock_agent(case):
    if case.fault_variant == "storm":
        mock_responses = [
            {
                "thinking": "发布后接口超时且流水线第 3 步卡住，先看 pg_stat_activity 全量会话与等待状态。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT pid, application_name, state, wait_event_type, wait_event, "
                        "now() - xact_start AS tx_age, left(query, 90) AS query "
                        "FROM pg_stat_activity WHERE datname = current_database() "
                        "AND backend_type = 'client backend' ORDER BY xact_start NULLS LAST;"
                    )}},
                ],
            },
            {
                "thinking": "大量会话 wait_event=Lock。用 pg_blocking_pids/pg_locks 建立等待链，找到队列头。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT a.pid, a.application_name, l.mode, l.granted, "
                        "array_to_string(pg_blocking_pids(a.pid), ',') AS blockers "
                        "FROM pg_stat_activity a LEFT JOIN pg_locks l ON l.pid = a.pid "
                        "WHERE a.datname = current_database() AND l.relation = 'order_items'::regclass "
                        "ORDER BY l.granted, a.pid; "
                        "SELECT l.pid, l.mode, l.granted FROM pg_locks l "
                        "WHERE l.relation = 'order_items'::regclass AND l.granted AND l.pid IS NULL; "
                        "SELECT gid, owner, prepared FROM pg_prepared_xacts;"
                    )}},
                ],
            },
            {
                "thinking": "等待链是业务会话 ← 排队 ALTER(AEL) ← 孤儿 prepared transaction(ASE, 无会话)。确认外键校验状态与流水线各步的尝试记录。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT conname, convalidated FROM pg_constraint "
                        "WHERE conrelid = 'order_items'::regclass;"
                    )}},
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT step_no, step_name, status, attempts, last_error "
                        "FROM fk_release_pipeline ORDER BY step_no;"
                    )}},
                ],
            },
            {
                "thinking": "先取消排队的 ALTER（撤掉 AccessExclusiveLock 请求），解除锁队列停摆。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT pg_cancel_backend(pid) FROM pg_stat_activity "
                        "WHERE application_name = 'fkrollout-ddl-pipeline-step3';"
                    )}},
                ],
            },
            {
                "thinking": "阻塞源是孤儿 prepared transaction（两阶段提交遗留，无会话可终止）：ROLLBACK PREPARED 解除它持有的弱锁。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "ROLLBACK PREPARED 'bi-report-daily-close-20260910';"
                    )}},
                ],
            },
            {
                "thinking": "校验作业会话被只读配置钉死、永远无法自愈：终止该作业会话，由 DBA 直接重放 VALIDATE CONSTRAINT；同一治理发布在 order_items_peer 上的外键也还未校验，一并重放。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE application_name = 'fkrollout-fk-validate-job-2';"
                    )}},
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SET statement_timeout = 0; "
                        "SET lock_timeout = '5s'; "
                        "ALTER TABLE order_items VALIDATE CONSTRAINT fk_order_items_customer; "
                        "ALTER TABLE order_items_peer VALIDATE CONSTRAINT fk_order_items_peer_customer;"
                    )}},
                ],
            },
            {
                "thinking": "重放 VALIDATE 报外键违例：存量订单行引用了客户主数据中不存在的客户。先反连接盘点全部孤儿订单行，确认治理范围。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT count(*) AS orphan_rows, min(o.customer_id), max(o.customer_id) "
                        "FROM order_items o LEFT JOIN customers c ON o.customer_id = c.id "
                        "WHERE c.id IS NULL;"
                    )}},
                ],
            },
            {
                "thinking": "这些是遗留渠道的脏数据，且只有它们违反外键：定向删除孤儿订单行（不碰任何合法订单），随后两个外键的 VALIDATE 即可真实完成。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "DELETE FROM order_items o "
                        "WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.id = o.customer_id) "
                        "RETURNING o.id, o.customer_id; "
                        "SET statement_timeout = 0; SET lock_timeout = '5s'; "
                        "ALTER TABLE order_items VALIDATE CONSTRAINT fk_order_items_customer; "
                        "ALTER TABLE order_items_peer VALIDATE CONSTRAINT fk_order_items_peer_customer;"
                    )}},
                ],
            },
            {
                "thinking": "等待校验完成，然后确认锁队列清空、两个外键 convalidated=true、业务可读。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT pg_sleep(25); "
                        "SELECT count(*) AS waiting FROM pg_locks WHERE NOT granted "
                        "AND relation = 'order_items'::regclass; "
                        "SELECT conname, convalidated FROM pg_constraint "
                        "WHERE conname IN ('fk_order_items_customer', 'fk_order_items_peer_customer'); "
                        "SELECT step_no, status, attempts FROM fk_release_pipeline ORDER BY step_no;"
                    )}},
                ],
            },
            {
                "thinking": "业务恢复且数据治理目标达成，提交。",
                "actions": [{"api": "submit", "args": {"report": build_report(case, True)}}],
            },
        ]
    else:
        mock_responses = [
            {
                "thinking": "校验作业超期且查询偶发变慢，先看 pg_stat_activity 找到校验会话。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT pid, application_name, state, wait_event_type, wait_event, "
                        "left(query, 90) AS query FROM pg_stat_activity "
                        "WHERE datname = current_database() AND backend_type = 'client backend' "
                        "ORDER BY query_start NULLS LAST;"
                    )}},
                ],
            },
            {
                "thinking": "validate 在等 ShareUpdateExclusive，查 pg_locks 确认它排在维护事务之后。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT a.pid, a.application_name, l.mode, l.granted "
                        "FROM pg_stat_activity a LEFT JOIN pg_locks l ON l.pid = a.pid "
                        "WHERE l.relation = 'order_items'::regclass ORDER BY l.granted, a.pid;"
                    )}},
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT conname, convalidated FROM pg_constraint "
                        "WHERE conrelid = 'order_items'::regclass;"
                    )}},
                ],
            },
            {
                "thinking": "终止卡住的维护事务释放 ShareUpdateExclusiveLock，validate 即可获授并完成校验。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE application_name = 'fkrollout-metrics-rollup-maintenance';"
                    )}},
                ],
            },
            {
                "thinking": "等待 validate 完成，确认 convalidated=true、无锁等待、读取恢复。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": (
                        "SELECT pg_sleep(25); "
                        "SELECT count(*) AS waiting FROM pg_locks WHERE NOT granted "
                        "AND relation = 'order_items'::regclass; "
                        "SELECT conname, convalidated FROM pg_constraint "
                        "WHERE conrelid = 'order_items'::regclass;"
                    )}},
                ],
            },
            {
                "thinking": "治理目标达成，提交。",
                "actions": [{"api": "submit", "args": {"report": build_report(case, True)}}],
            },
        ]
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(mock_responses)
    return agent


def build_env(case, port: int, container_name: str) -> PGEnv:
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=case.base_image_name,
    )
    # 场景 quiesce 会按 application_name 终止后端；个别后端异常死亡会让 sampler
    # 连接被波及。允许 sampler 自恢复，避免基础设施层面的连接事件污染运行收尾。
    return PGEnv(
        workload=None,
        deployment=deployment,
        port=port,
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )


def run_mode(args, scenario, case, mode, container_name, run_config):
    env = build_env(case, args.port, container_name)
    if mode == "mock":
        agent = build_mock_agent(case)
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses([{"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": build_report(case, False)}}}])
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    max_turns = {"mock": 10, "zero": 3, "llm": args.max_turns}[mode]
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=max_turns, run_config=run_config)
    return orchestrator.run()


def main():
    scenario = PgBusinessChangeFkValidationScenario()
    parser = argparse.ArgumentParser(description="Run PgBusinessChangeFkValidationScenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15461)
    parser.add_argument("--container-name", default="aiopsbench-run-pg-business-change-fk-validation")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    parser.add_argument("--diagnosis-match-mode", choices=("exact", "semantic"), default="exact")
    parser.add_argument("--diagnosis-semantic-model")
    parser.add_argument("--diagnosis-semantic-config")
    args = parser.parse_args()
    if args.max_turns > 30:
        raise ValueError("--max-turns must be <= 30")
    if args.mode != "llm" and args.diagnosis_match_mode == "semantic":
        raise ValueError("semantic diagnosis matching requires --mode llm")
    if args.diagnosis_match_mode == "semantic" and args.diagnosis_semantic_model != args.model:
        raise ValueError("semantic diagnosis judge model must match the agent model")
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
        diagnosis_match_mode=args.diagnosis_match_mode,
        diagnosis_semantic_model=args.diagnosis_semantic_model or OrchestratorRunConfig().diagnosis_semantic_model,
        diagnosis_semantic_config_path=args.diagnosis_semantic_config or args.config_path,
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
            # zero 未执行任何动作：SP 合法通过（没有可判定的动作风险），只断言 DP/OP 失败。
            assert not result["DiagnosisPass"] and not result["OutcomePass"], json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    main()
