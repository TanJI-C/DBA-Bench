import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbBusinessChangeCdcDcMigrationScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


SCENARIO = TidbBusinessChangeCdcDcMigrationScenario()
CASE = SCENARIO.cases[0]


def _qualified(case, database: str, table: str) -> str:
    return f"{database}.{table}"


def _feed_status_query(case):
    control = case.control_db
    feed = case.changefeed_table
    return (
        f"SELECT feed_id, state, enabled, last_applied_event_id, resolved_event_id, lag_events "
        f"FROM {control}.{feed} "
        f"WHERE feed_id IN ('{case.forward_feed_id}','{case.reverse_feed_id}') ORDER BY feed_id"
    )


def _migration_state_query(case):
    return (
        f"SELECT phase, current_primary, unsafe_cutover_attempt, rollback_ready, "
        f"target_app_events, reverse_applied_events, p95_latency_ms, "
        f"reverse_ready_observed_at IS NOT NULL AS reverse_ready_observed "
        f"FROM {case.control_db}.{case.migration_table} "
        f"WHERE migration_id='{case.migration_id}'"
    )


def _activate_reverse_sql(case):
    control = case.control_db
    feed = case.changefeed_table
    return (
        f"UPDATE {control}.{feed} SET state='normal', enabled=1, "
        "activated_at=CURRENT_TIMESTAMP(6), last_error=NULL "
        f"WHERE feed_id='{case.reverse_feed_id}' "
        f"AND direction='{case.target_dc}_to_{case.source_dc}' AND state='paused' AND enabled=0 "
        f"AND (SELECT lag_events FROM {control}.{feed} WHERE feed_id='{case.forward_feed_id}')=0"
    )


def _cutover_sql(case):
    control = case.control_db
    feed = case.changefeed_table
    return (
        f"UPDATE {control}.{case.route_table} SET active_dc='{case.target_dc}', route_epoch=2, "
        "changed_at=CURRENT_TIMESTAMP(6) "
        f"WHERE service_name='{case.route_service}' AND active_dc='{case.source_dc}' AND route_epoch=1 "
        f"AND (SELECT state FROM {control}.{feed} WHERE feed_id='{case.forward_feed_id}')='normal' "
        f"AND (SELECT enabled FROM {control}.{feed} WHERE feed_id='{case.forward_feed_id}')=1 "
        f"AND (SELECT lag_events FROM {control}.{feed} WHERE feed_id='{case.forward_feed_id}')=0 "
        f"AND (SELECT state FROM {control}.{feed} WHERE feed_id='{case.reverse_feed_id}')='normal' "
        f"AND (SELECT enabled FROM {control}.{feed} WHERE feed_id='{case.reverse_feed_id}')=1 "
        f"AND (SELECT lag_events FROM {control}.{feed} WHERE feed_id='{case.reverse_feed_id}')=0"
    )


def _business_truth_query(case):
    source = _qualified(case, case.source_db, case.order_table)
    target = _qualified(case, case.target_db, case.order_table)
    digest = "COALESCE(BIT_XOR(CRC32(CONCAT_WS('|',order_id,customer_id,status,amount_cents,region,version))),0)"
    return (
        f"SELECT '{case.source_dc}' AS dc, COUNT(*), COALESCE(SUM(order_id),0), {digest} FROM {source} "
        f"UNION ALL SELECT '{case.target_dc}', COUNT(*), COALESCE(SUM(order_id),0), {digest} FROM {target}"
    )


def _billing_reverse_mock_responses(case):
    feed_status = _feed_status_query(case)
    migration_state = _migration_state_query(case)
    activate_reverse = _activate_reverse_sql(case)
    cutover = _cutover_sql(case)
    control = case.control_db
    return [
        {
            "thinking": "先确认持续业务负载与延迟，再一次性读取控制面、changefeed、迁移状态和两地业务真值。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
                {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                    f"WHERE TABLE_SCHEMA IN ('{case.control_db}','{case.source_db}','{case.target_db}','{case.archive_db}') "
                    "ORDER BY TABLE_SCHEMA, TABLE_NAME"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT feed_id, direction, source_dc, target_dc, state, enabled, "
                    f"last_applied_event_id, resolved_event_id, lag_events, last_error "
                    f"FROM {control}.{case.changefeed_table} ORDER BY feed_id"
                )}},
                {"api": "execute_sql", "args": {"sql_query": migration_state}},
                {"api": "execute_sql", "args": {"sql_query": _business_truth_query(case)}},
            ],
        },
        {
            "thinking": "等 west->east forward 追平且两地真值一致后激活 east->west 反向链路，一次建立双向就绪状态。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(10)"}},
                {"api": "execute_sql", "args": {"sql_query": feed_status}},
                {"api": "execute_sql", "args": {"sql_query": migration_state}},
                {"api": "execute_sql", "args": {"sql_query": activate_reverse}},
                {"api": "execute_sql", "args": {"sql_query": feed_status}},
                {"api": "execute_sql", "args": {"sql_query": migration_state}},
            ],
        },
        # 轮询等待控制器排空 forward lag；guard 未满足时激活 UPDATE 是幂等 no-op。
        # 重复轮询不增加诊断路径深度，压缩路径仍为 2 跳。
        *[
            {
                "thinking": "forward 尚未追平时保持当前路由，重复确认 changefeed 与迁移状态后重试激活反向链路。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(12)"}},
                    {"api": "execute_sql", "args": {"sql_query": activate_reverse}},
                    {"api": "execute_sql", "args": {"sql_query": feed_status}},
                    {"api": "execute_sql", "args": {"sql_query": migration_state}},
                ],
            }
        ] * 4,
        {
            "thinking": "双向 normal、enabled 且 lag=0 时执行幂等切流，保留观察窗口确认 rollback-ready 后提交报告。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(12)"}},
                {"api": "execute_sql", "args": {"sql_query": activate_reverse}},
                {"api": "execute_sql", "args": {"sql_query": cutover}},
                {"api": "execute_sql", "args": {"sql_query": feed_status}},
                {"api": "execute_sql", "args": {"sql_query": migration_state}},
            ],
        },
        {
            "thinking": "切流后核对反向应用事件、两地业务真值与路由终态，确认 rollback-ready。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(12)"}},
                {"api": "execute_sql", "args": {"sql_query": migration_state}},
                {"api": "execute_sql", "args": {"sql_query": _business_truth_query(case)}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT active_dc, route_epoch FROM {control}.{case.route_table} "
                    f"WHERE service_name='{case.route_service}'"
                )}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def _rollback_route_sql(case):
    return (
        f"UPDATE {case.control_db}.{case.route_table} SET active_dc='{case.source_dc}', "
        "route_epoch=route_epoch+1, changed_at=CURRENT_TIMESTAMP(6) "
        f"WHERE service_name='{case.route_service}' AND active_dc='{case.target_dc}'"
    )


def _mirror_probe_sql(case):
    source = _qualified(case, case.source_db, case.order_table)
    target = _qualified(case, case.target_db, case.order_table)
    return (
        f"SELECT COUNT(*) AS east_only FROM {source} e "
        f"LEFT JOIN {target} w ON e.order_id = w.order_id WHERE w.order_id IS NULL; "
        f"SELECT COUNT(*) AS west_only, MIN(w.order_id) AS min_west_only_id FROM {target} w "
        f"LEFT JOIN {source} e ON e.order_id = w.order_id WHERE e.order_id IS NULL; "
        f"SELECT COUNT(*) AS journal_uncovered FROM {target} w "
        f"LEFT JOIN {source} e ON e.order_id = w.order_id "
        f"LEFT JOIN {case.target_db}.{case.event_table} ev "
        f"ON ev.order_id = w.order_id AND ev.origin_dc = '{case.target_dc}' "
        f"WHERE e.order_id IS NULL AND ev.event_id IS NULL"
    )


def _restore_reverse_coverage_sql(case):
    return (
        f"UPDATE {case.control_db}.{case.changefeed_table} SET region_filter='all' "
        f"WHERE feed_id='{case.reverse_feed_id}' "
        f"AND direction='{case.target_dc}_to_{case.source_dc}' AND state='normal' AND enabled=1"
    )


def _restore_reverse_ordering_sql(case):
    return (
        f"UPDATE {case.control_db}.{case.changefeed_table} SET apply_ordering='authority_epoch' "
        f"WHERE feed_id='{case.reverse_feed_id}'"
    )


def _restore_reverse_namespace_sql(case):
    return (
        f"UPDATE {case.control_db}.{case.changefeed_table} SET namespace_binding='source_incarnation', source_incarnation_filter='{case.target_incarnation}', event_namespace=("
        f"SELECT incarnation_id FROM {case.control_db}.stream_incarnations "
        f"WHERE source_dc='{case.target_dc}' AND service_name='{case.route_service}' "
        "AND lifecycle='current') "
        f"WHERE feed_id='{case.reverse_feed_id}' "
        f"AND direction='{case.target_dc}_to_{case.source_dc}' AND state='normal' AND enabled=1"
    )


def _replay_reverse_sql(case):
    return (
        f"UPDATE {case.control_db}.{case.changefeed_table} "
        "SET last_applied_event_id=0 "
        f"WHERE feed_id='{case.reverse_feed_id}' "
        f"AND direction='{case.target_dc}_to_{case.source_dc}' AND state='normal' AND enabled=1"
    )


def _checkout_replay_mock_responses(case, *, rollback=False):
    control = case.control_db
    reads = [
        f"SELECT * FROM {control}.{case.route_table} ORDER BY service_name",
        f"SELECT * FROM {control}.{case.changefeed_table} ORDER BY feed_id",
        f"SELECT * FROM {control}.{case.migration_table} ORDER BY migration_id",
        f"SELECT * FROM {control}.{case.validation_table} ORDER BY request_id",
        f"SELECT * FROM {control}.checkpoint_imports ORDER BY import_id",
        f"SELECT * FROM {control}.stream_incarnations ORDER BY incarnation_id",
        f"SELECT * FROM {control}.handoff_decisions ORDER BY decision_id",
        f"SELECT * FROM {control}.migration_audit ORDER BY audit_id LIMIT 50",
        f"SELECT * FROM {control}.replication_observations ORDER BY observation_id DESC LIMIT 50",
        f"SELECT * FROM {control}.service_slo_samples ORDER BY sample_id DESC LIMIT 50",
    ]
    responses = [
        {
            "thinking": "先定位服务路由和业务镜像，读取未经预关联的控制面与负载证据。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
                {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
                *[{"api": "execute_sql", "args": {"sql_query": sql}} for sql in reads],
                {"api": "execute_sql", "args": {"sql_query": _business_truth_query(case)}},
            ],
        },
        {
            "thinking": "当前水位不代表历史投递完整；比较两地订单，并关联反向事件、导入位置类型和活跃游标。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(10)"}},
                {"api": "execute_sql", "args": {"sql_query": _feed_status_query(case)}},
                {"api": "execute_sql", "args": {"sql_query": _mirror_probe_sql(case)}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT w.order_id,e.status,w.status,e.amount_cents,w.amount_cents, "
                    f"e.version,w.version,e.updated_at,w.updated_at FROM {case.target_db}.{case.order_table} w "
                    f"JOIN {case.source_db}.{case.order_table} e ON e.order_id=w.order_id "
                    "WHERE e.status<>w.status OR e.amount_cents<>w.amount_cents OR e.version<>w.version "
                    "ORDER BY w.order_id"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SHOW CREATE TABLE {control}.{case.changefeed_table}"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT event_id, order_id, origin_dc, event_source, origin_event_id, region, source_incarnation, event_namespace, version, updated_at "
                    f"FROM {case.target_db}.{case.event_table} ORDER BY event_id LIMIT 100"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT event_id, order_id, origin_dc, origin_event_id, source_incarnation, event_namespace, "
                    f"version, updated_at FROM {case.source_db}.{case.event_table} "
                    f"WHERE origin_dc='{case.target_dc}' ORDER BY event_id LIMIT 100"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT w.order_id, ev.event_id, ev.origin_dc, ev.region, f.region_filter, f.last_applied_event_id "
                    f"FROM {case.target_db}.{case.order_table} w "
                    f"LEFT JOIN {case.source_db}.{case.order_table} e ON e.order_id=w.order_id "
                    f"JOIN {case.target_db}.{case.event_table} ev ON ev.order_id=w.order_id "
                    f"JOIN {control}.{case.changefeed_table} f ON f.feed_id='{case.reverse_feed_id}' "
                    f"WHERE e.order_id IS NULL AND ev.origin_dc='{case.target_dc}' ORDER BY w.order_id"
                )}},
            ],
        },
        {
            "thinking": "关联公开交接回执与outboxmode；保留已激活旧producer业务，排除被中止validation投影，再恢复当前producer持续投递。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {control}.{case.changefeed_table} SET region_filter='all', "
                    f"namespace_binding='source_incarnation', event_namespace='reference-activated-history', "
                    f"source_incarnation_filter='{case.previous_target_incarnation}', apply_ordering='authority_epoch', "
                    f"last_applied_event_id=0,resolved_event_id=0 WHERE feed_id='{case.reverse_feed_id}'"
                )}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(12)"}},
                {"api": "execute_sql", "args": {"sql_query": _restore_reverse_ordering_sql(case)}},
                {"api": "execute_sql", "args": {"sql_query": _restore_reverse_namespace_sql(case)}},
                {"api": "execute_sql", "args": {"sql_query": _restore_reverse_coverage_sql(case)}},
                {"api": "execute_sql", "args": {"sql_query": _replay_reverse_sql(case)}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(12)"}},
                {"api": "execute_sql", "args": {"sql_query": _feed_status_query(case)}},
                {"api": "execute_sql", "args": {"sql_query": _business_truth_query(case)}},
                {"api": "execute_sql", "args": {"sql_query": _mirror_probe_sql(case)}},
            ],
        },
    ]
    if rollback:
        responses.append({
            "thinking": "镜像完整后才允许安全回退；路由更新接受等价写法，业务真值不得有残差。",
            "action": {"api": "execute_sql", "args": {"sql_query": _rollback_route_sql(case)}},
        })
    responses.extend([
        {
            "thinking": "观察双向投递、最终镜像和服务延迟，确认收口依赖真实业务完整性。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(8)"}},
                {"api": "execute_sql", "args": {"sql_query": _feed_status_query(case)}},
                {"api": "execute_sql", "args": {"sql_query": _migration_state_query(case)}},
                {"api": "execute_sql", "args": {"sql_query": _mirror_probe_sql(case)}},
                {"api": "execute_sql", "args": {"sql_query": _business_truth_query(case)}},
            ],
        },
        {"thinking": "完整镜像与安全回退能力已验证。", "action": {"api": "submit", "args": {"report": case.reference_report}}},
    ])
    return responses


def build_mock_responses(case):
    if case.case_no == 1:
        return _billing_reverse_mock_responses(case)
    return _checkout_replay_mock_responses(case)


MOCK_RESPONSES = build_mock_responses(CASE)


def main():
    parser = argparse.ArgumentParser(description="Run the TiDB BC02 online CDC migration scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--port", type=int, default=4400)
    parser.add_argument("--container-name", default="tidb-bc02-cdc-migration")
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    args = parser.parse_args()
    if args.mode == "llm" and not args.model:
        parser.error("--model is required when --mode=llm")
    case = SCENARIO.get_case(args.case)
    env = TiDBEnv(run_id=args.container_name.removeprefix("aiopsbench-"), port_base=args.port)
    if args.mode == "mock":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a TiDB DBA agent.", use_native_tools=False)
        agent.set_mock_responses(build_mock_responses(case))
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    result = Orchestrator(
        env,
        SCENARIO,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode),
    ).run()
    if args.mode == "mock" and (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) != (None, True, True):
        raise AssertionError(f"BC02 mock path failed: result={result}")


if __name__ == "__main__":
    main()
