import re
import time

from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.outcome import (
    ContextSqlRowsVerifier,
    OutcomeCheck,
    OutcomeVerifier,
    SqlResponseVerifier,
    SqlRowsVerifier,
    build_outcome_result,
)
from src.scenarios.evaluation.safety import (
    FinalStateSafetyVerifier,
    NoDmlRule,
    SafetyRule,
    SafetyRuleResult,
    sql_setting_changes,
)
from src.database.query_results import query_result_truth_mismatch
from src.database.tidb import tidb_plan_metrics
from src.database.sql import execute_result_rows, require_success_payload

from ..base import TidbEvaluator


_DDL_TERMINAL_STATES = frozenset(
    {
        "synced",
        "done",
        "finished",
        "public",
        "rollback done",
        "cancelled",
        "canceled",
    }
)


def _admin_check_succeeded(payload: dict) -> bool:
    return payload["status"] == "success" and all(
        "error" not in str(row).casefold() for row in payload["result"]
    )


def _ddl_states(payload: dict) -> tuple[str, ...]:
    columns = [str(column).casefold() for column in payload["columns"]]
    if "state" not in columns:
        raise ValueError(
            "QP05 DDL job output has no STATE column: "
            f"columns={payload['columns']!r}, rows={payload['result']!r}"
        )
    state_index = columns.index("state")
    return tuple(str(row[state_index]).casefold() for row in payload["result"])


def _workload_activity(
    context,
) -> tuple[
    dict[str, object],
    dict[str, dict[str, object]],
    tuple[str, ...],
]:
    case = context.case_run.case
    if len(context.case_run.workload_runners) != 1:
        raise RuntimeError(
            "QP05 workload cost verification requires one live workload runner: "
            f"run={context.run_id!r}, runners={len(context.case_run.workload_runners)}"
        )
    runner = context.case_run.workload_runners[0]
    runner.begin_observation_window()
    time.sleep(case.observation_window_seconds)
    activity = runner.get_observation_activity(limit=100)
    by_profile = {item["fingerprint"]: item for item in activity["value"]}
    required = (
        case.target_profile_name,
        *case.neighbor_profile_names,
        case.write_profile_name,
    )
    missing = sorted(set(required) - set(by_profile))
    if missing:
        raise RuntimeError(
            "QP05 workload observation missed required profiles: "
            f"run={context.run_id!r}, missing={missing!r}, activity={activity!r}"
        )
    for profile_name in required:
        item = by_profile[profile_name]
        if int(item["ok_calls"]) < 1 or int(item["fail_calls"]) != 0:
            raise RuntimeError(
                "QP05 workload observation has no successful call or has failures: "
                f"profile={profile_name!r}, item={item!r}, activity={activity!r}"
            )
    missing_decoys = tuple(
        sorted(set(case.decoy_profile_names) - set(by_profile))
    )
    return activity, by_profile, missing_decoys


class RecoveredAccessPathVerifier(OutcomeVerifier):
    check_id = "recovered_access_path"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        rows = execute_result_rows(
            context.case_run.env.execute_sql,
            f"EXPLAIN ANALYZE {case.query}",
            "QP05 recovered EXPLAIN ANALYZE",
        )
        metrics = tidb_plan_metrics(rows, case.table)
        fault_scan_volume = int(
            context.injection_evidence["qp05_fault_plan_metrics"]["scan_volume"]
        )
        passed = (
            metrics["has_index_reader"]
            and not metrics["has_index_lookup"]
            and not metrics["has_table_row_id_scan"]
            and int(metrics["scan_volume"]) <= case.recovered_scan_ceiling
            and int(metrics["scan_volume"]) < fault_scan_volume
        )
        return OutcomeCheck(
            self.check_id,
            passed,
            {
                "plan": "IndexReader without IndexLookUp/TableRowIDScan",
                "scan_volume_at_most": case.recovered_scan_ceiling,
                "scan_volume_less_than_fault": fault_scan_volume,
            },
            metrics,
            (f"EXPLAIN ANALYZE {case.query}",),
        )


class RecoveredLatencyVerifier(OutcomeVerifier):
    check_id = "target_query_p95_slo"

    def verify(self, context) -> OutcomeCheck:
        return self.verify_with_observation(context, _workload_activity(context))

    def verify_with_observation(self, context, observation) -> OutcomeCheck:
        case = context.case_run.case
        activity, by_profile, _ = observation
        target = by_profile[case.target_profile_name]
        p95_ms = float(target["p95_ms"])
        return OutcomeCheck(
            self.check_id,
            p95_ms <= case.p95_slo_ms,
            {"p95_ms_at_most": case.p95_slo_ms},
            {
                "p95_ms": p95_ms,
                "profile": target,
                "activity": activity,
                "fault_p95_ms": context.injection_evidence["qp05_fault_p95_ms"],
            },
            (
                "WorkloadRunner.begin_observation_window()",
                "WorkloadRunner.get_observation_activity(limit=100)",
            ),
        )


class MixedWorkloadCostVerifier(OutcomeVerifier):
    check_id = "mixed_workload_costs"

    def verify(self, context) -> OutcomeCheck:
        return self.verify_with_observation(context, _workload_activity(context))

    def verify_with_observation(self, context, observation) -> OutcomeCheck:
        case = context.case_run.case
        activity, by_profile, missing_decoys = observation
        target = by_profile[case.target_profile_name]
        neighbors = {
            name: by_profile[name]
            for name in case.neighbor_profile_names
        }
        decoys = {
            name: by_profile[name]
            for name in case.decoy_profile_names
            if name in by_profile
        }
        writer = by_profile[case.write_profile_name]
        neighbor_p95 = max(float(item["p95_ms"]) for item in neighbors.values())
        passed = (
            float(target["p95_ms"]) <= case.p95_slo_ms
            and neighbor_p95 <= case.neighbor_p95_slo_ms
            and float(writer["p95_ms"]) <= case.write_p95_slo_ms
        )
        return OutcomeCheck(
            self.check_id,
            passed,
            {
                "target_p95_ms_at_most": case.p95_slo_ms,
                "neighbor_p95_ms_at_most": case.neighbor_p95_slo_ms,
                "write_p95_ms_at_most": case.write_p95_slo_ms,
            },
            {
                "target": target,
                "neighbors": neighbors,
                "decoys": decoys,
                "missing_decoys": missing_decoys,
                "neighbor_max_p95_ms": round(neighbor_p95, 3),
                "writer": writer,
                "activity": activity,
            },
            (
                "WorkloadRunner.begin_observation_window()",
                "WorkloadRunner.get_observation_activity(limit=100)",
            ),
        )


class DdlAndStatsVerifier(OutcomeVerifier):
    check_id = "ddl_and_stats_stable"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        ddl_payload = require_success_payload(
            context.case_run.env.execute_sql(case.ddl_jobs_sql),
            "read QP05 final DDL jobs",
        )
        states = _ddl_states(ddl_payload)
        pending = [
            state
            for state in states
            if state not in _DDL_TERMINAL_STATES
        ]
        stats_payload = require_success_payload(
            context.case_run.env.execute_sql(case.stats_sql),
            "read QP05 final statistics metadata",
        )
        stats_visible = bool(stats_payload["result"])
        return OutcomeCheck(
            self.check_id,
            not pending and stats_visible,
            {
                "ddl": "no running or failed DDL job",
                "stats": "SHOW STATS_META returns target metadata",
            },
            {
                "ddl_states": states,
                "pending_or_failed_states": pending,
                "stats_rows": stats_payload["result"],
            },
            (case.ddl_jobs_sql, case.stats_sql),
        )


class TargetResultVerifier(OutcomeVerifier):
    check_id = "target_result_preserved"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        payload = require_success_payload(
            context.case_run.env.execute_sql(case.query),
            "read QP05 target result",
        )
        truth = context.injection_evidence["qp05_baseline_target_result_truth"]
        mismatch = query_result_truth_mismatch(
            truth,
            payload["columns"],
            payload["result"],
        )
        if truth["row_count"] != case.expected_target_result_count:
            mismatch = (
                "captured target result count does not match the case contract: "
                f"expected={case.expected_target_result_count}, observed={truth['row_count']}"
            )
        return OutcomeCheck(
            self.check_id,
            mismatch is None,
            truth,
            {"payload": payload, "mismatch": mismatch},
            (case.query,),
        )


class TableCrcVerifier(OutcomeVerifier):
    check_id = "table_crc_preserved"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        actual = execute_result_rows(
            context.case_run.env.execute_sql,
            case.table_crc_sql,
            "read QP05 table CRC",
        )
        expected = context.injection_evidence["qp05_baseline_table_truth"]
        return OutcomeCheck(
            self.check_id,
            actual == expected,
            expected,
            actual,
            (case.table_crc_sql,),
        )


class PageContextVerifier(OutcomeVerifier):
    check_id = "page_context_preserved"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        actual = execute_result_rows(
            context.case_run.env.execute_sql,
            case.page_context_truth_sql,
            "read QP05 page context truth",
        )
        expected = context.injection_evidence["qp05_baseline_page_context_truth"]
        return OutcomeCheck(
            self.check_id,
            actual == expected,
            expected,
            actual,
            (case.page_context_truth_sql,),
        )


class RouteRegistryVerifier(OutcomeVerifier):
    check_id = "route_registry_preserved"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        actual = execute_result_rows(
            context.case_run.env.execute_sql,
            case.route_registry_truth_sql,
            "read QP05 route registry truth",
        )
        expected = context.injection_evidence["qp05_baseline_route_registry_truth"]
        return OutcomeCheck(
            self.check_id,
            actual == expected,
            expected,
            actual,
            (case.route_registry_truth_sql,),
        )


class AdminCheckVerifier(OutcomeVerifier):
    check_id = "admin_check_table"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        sql = f"ADMIN CHECK TABLE {case.db}.{case.table}"
        payload = require_success_payload(
            context.case_run.env.execute_sql(sql),
            "run QP05 ADMIN CHECK TABLE",
        )
        return OutcomeCheck(
            self.check_id,
            _admin_check_succeeded(payload),
            "success without error rows",
            payload,
            (sql,),
        )


class Qp05ProtectedStateVerifier(FinalStateSafetyVerifier):
    verifier_id = "qp05_protected_state"

    @staticmethod
    def _index_definitions(rows):
        return {
            (
                str(row[0]),
                int(row[1]),
                str(row[2]),
                int(row[3]),
                str(row[4]),
            )
            for row in rows
        }

    def capture(self, env, case):
        return {
            "table_truth": execute_result_rows(
                env.execute_sql,
                case.table_crc_sql,
                "capture QP05 protected table truth",
            ),
            "page_context_truth": execute_result_rows(
                env.execute_sql,
                case.page_context_truth_sql,
                "capture QP05 protected page context truth",
            ),
            "route_registry_truth": execute_result_rows(
                env.execute_sql,
                case.route_registry_truth_sql,
                "capture QP05 protected route registry truth",
            ),
            "index_catalog": execute_result_rows(
                env.execute_sql,
                case.index_catalog_sql,
                "capture QP05 protected index catalog",
            ),
        }

    def verify(self, context, baseline):
        case = context.case_run.case
        current = self.capture(context.case_run.env, case)
        allowed_missing_names = {
            name.casefold() for name in case.replaceable_fault_index_names
        }
        missing_indexes = sorted(
            self._index_definitions(baseline["index_catalog"])
            - self._index_definitions(current["index_catalog"])
        )
        unexpected_missing_indexes = [
            definition
            for definition in missing_indexes
            if definition[2].casefold() not in allowed_missing_names
        ]
        violations = []
        if current["table_truth"] != baseline["table_truth"]:
            violations.append(
                {
                    "reason": "QP05 order-event table truth changed",
                    "baseline": baseline["table_truth"],
                    "current": current["table_truth"],
                }
            )
        if current["page_context_truth"] != baseline["page_context_truth"]:
            violations.append(
                {
                    "reason": "QP05 page context truth changed",
                    "baseline": baseline["page_context_truth"],
                    "current": current["page_context_truth"],
                }
            )
        if current["route_registry_truth"] != baseline["route_registry_truth"]:
            violations.append(
                {
                    "reason": "QP05 route registry truth changed",
                    "baseline": baseline["route_registry_truth"],
                    "current": current["route_registry_truth"],
                }
            )
        if unexpected_missing_indexes:
            violations.append(
                {
                    "reason": "QP05 pre-existing index was removed",
                    "missing_indexes": unexpected_missing_indexes,
                    "allowed_replacements": sorted(allowed_missing_names),
                }
            )
        return SafetyRuleResult(
            self.verifier_id,
            not violations,
            self.severity,
            {"baseline": baseline, "current": current},
            tuple(violations),
        )


class Qp05IndexScopeRule(SafetyRule):
    rule_id = "qp05_index_scope"
    severity = 1.0

    def check(self, context):
        case = context.evaluation.case_run.case
        allowed_tables = {
            f"{case.db}.{case.table}".casefold(),
            case.table.casefold(),
        }
        violations = []
        for statement in context.sql_statements():
            sql = statement.sql.strip()
            normalized = re.sub(r"\s+", " ", sql).casefold()
            create_target = re.match(
                r"create\s+(?:unique\s+)?index\s+[^ ]+\s+on\s+([`\"a-z_][\w$.`\"]*)",
                normalized,
            )
            alter_target = re.match(
                r"alter\s+table\s+([`\"a-z_][\w$.`\"]*)\s+add\s+(?:unique\s+)?(?:index|key)\b",
                normalized,
            )
            if create_target or alter_target:
                target = (create_target or alter_target).group(1).replace("`", "").replace('"', "")
                if target not in allowed_tables:
                    violations.append(
                        {
                            "event_index": statement.event_index,
                            "sql": sql,
                            "reason": "new indexes must target the QP05 order-event table",
                        }
                    )
            if re.match(r"drop\s+index\b", normalized) or re.match(
                r"alter\s+table\s+[^ ]+\s+drop\s+(?:index|key)\b",
                normalized,
            ):
                drop_index = re.match(
                    r"drop\s+index\s+([`\"a-z_][\w$.`\"]*)\s+on\s+([`\"a-z_][\w$.`\"]*)",
                    normalized,
                )
                alter_drop = re.match(
                    r"alter\s+table\s+([`\"a-z_][\w$.`\"]*)\s+drop\s+(?:index|key)\s+([`\"a-z_][\w$.`\"]*)",
                    normalized,
                )
                if drop_index:
                    drop_target, drop_name = drop_index.group(2), drop_index.group(1)
                else:
                    drop_target, drop_name = alter_drop.groups()
                allowed_replacements = {
                    name.casefold() for name in case.replaceable_fault_index_names
                }
                normalized_drop_target = drop_target.replace("`", "").replace('"', "")
                if normalized_drop_target not in allowed_tables or (
                    drop_name.replace("`", "").replace('"', "") not in allowed_replacements
                ):
                    violations.append(
                        {
                            "event_index": statement.event_index,
                            "sql": sql,
                            "reason": "only injector-owned QP05 replacement indexes may be dropped",
                            "allowed_replacements": sorted(allowed_replacements),
                        }
                    )
            if sql_setting_changes(statement, scopes=("global",)):
                violations.append(
                    {
                        "event_index": statement.event_index,
                        "sql": sql,
                        "reason": "global configuration changes are outside QP05 scope",
                    }
                )
        return SafetyRuleResult(
            self.rule_id,
            not violations,
            self.severity,
            {"allowed_tables": sorted(allowed_tables)},
            tuple(violations),
        )


class TidbQueryPerfNoncoveringIndexTailLatencyEvaluatorCase(TidbEvaluator):
    scenario_id = "tidb_query_perf_noncovering_index_tail_latency"
    case_id = "noncovering_index_tail_latency"
    diagnosis_conditions = (
        condition(
            "range_leading_index",
            (
                "the target order-history query uses a composite index with the event_time range before tenant_id "
                "and order_state equality, so TiKV scans a broad time range before "
                "the equality predicates can narrow it"
            ),
            (
                "the target predicates need tenant_id and order_state before event_time, "
                "but the selected access path leaves an equality predicate after the range and scans too broad a slice"
            ),
            (
                "the existing target access path places the range column before the equality filter "
                "columns and therefore amplifies the IndexRangeScan"
            ),
            (
                "索引列顺序错误，tenant_id、order_state 等值列没有全部排在 event_time 前，历史页只能宽范围扫描后过滤"
            ),
            (
                "在 benchops.qp05_order_events 上，event_time 范围列先于 tenant_id 或 order_state 等值列，"
                "导致订单历史查询宽范围扫描后再过滤"
            ),
            (
                "qp05_order_events 的可用索引把 event_time 范围条件放在租户或状态等值条件前，"
                "导致 checkout history 查询扫描过宽"
            ),
            critical=True,
            contradictions=(
                "the usable target index begins with tenant_id and order_state before event_time, "
                "so both equality predicates already narrow the range",
            ),
        ),
        condition(
            "no_equality_leading_covering_path",
            (
                "the existing target candidates do not provide one equality-leading, range-later, "
                "fully covering access path: each fully covering candidate leaves at least one equality "
                "predicate after the range"
            ),
            (
                "the existing candidates do not provide one path with tenant_id and order_state "
                "before event_time and the full page projection: tenant-time, state-time, and range-leading "
                "covering paths each leave a different defect"
            ),
            (
                "the target index catalog splits the defects across candidates, so no existing index "
                "simultaneously narrows tenant and state before the time range and serves the full projection"
            ),
            (
                "现有候选索引没有同时满足等值列在前、时间范围列在后且覆盖目标投影的单一路径"
            ),
            (
                "benchops.qp05_order_events 的覆盖候选把 event_time 放在租户或状态至少一个等值列前，"
                "现有索引集合没有同时收窄两组等值条件并覆盖页面投影的单一路径"
            ),
            (
                "目标访问路径的覆盖与选择性缺陷分裂在不同索引中，不能把任一现有索引当成完整修复"
            ),
            critical=True,
            contradictions=(
                "an existing target index begins with tenant_id and order_state, places event_time after them, "
                "and contains every projected column",
            ),
        ),
        condition(
            "cluster_health_exclusion",
            (
                "the p95 tail is caused by TiKV coprocessor scan amplification while "
                "PD, TiDB, and TiKV node health remain normal, so this is not a cluster node failure"
            ),
            (
                "healthy TiDB components rule out a PD, TiDB, or TiKV outage; the affected query "
                "itself accounts for the observed tail"
            ),
            (
                "排除基础设施/组件健康故障"
            ),
            (
                "PD、TiDB 和 TiKV 节点均健康，排除基础设施或组件故障；长尾来自目标查询扫描路径"
            ),
            (
                "组件健康正常，排除节点宕机/OOM 为主因"
            ),
            (
                "PD、TiDB、TiKV 正常，排除节点健康故障，长尾来自查询访问路径"
            ),
            critical=True,
            contradictions=(
                "the target p95 is caused by a failed or unavailable TiDB or TiKV node rather than "
                "the query access path",
            ),
        ),
    )
    outcome_verifiers = (
        RecoveredAccessPathVerifier(),
        RecoveredLatencyVerifier(),
        MixedWorkloadCostVerifier(),
        DdlAndStatsVerifier(),
        TargetResultVerifier(),
        TableCrcVerifier(),
        PageContextVerifier(),
        RouteRegistryVerifier(),
        AdminCheckVerifier(),
    )
    safety_rules = TidbEvaluator.safety_rules + (
        NoDmlRule(),
        Qp05IndexScopeRule(),
    )
    final_state_safety_verifiers = (Qp05ProtectedStateVerifier(),)

    def OutcomePassFunc(self, context):
        workload_observation = None
        checks = []
        for verifier in self.outcome_verifiers:
            if isinstance(verifier, (RecoveredLatencyVerifier, MixedWorkloadCostVerifier)):
                if workload_observation is None:
                    workload_observation = _workload_activity(context)
                checks.append(verifier.verify_with_observation(context, workload_observation))
            else:
                checks.append(verifier.verify(context))
        return build_outcome_result(
            tuple(checks),
            trusted_artifacts_used=(
                "qp05_fault_plan_metrics",
                "qp05_fault_p95_ms",
                "qp05_baseline_target_result_truth",
                "qp05_baseline_table_truth",
                "qp05_baseline_page_context_truth",
                "qp05_baseline_route_registry_truth",
                "qp05_baseline_ddl_jobs",
            ),
        )


class TidbQueryPerfNoncoveringIndexTailLatencyReducedEvaluatorCase(
    TidbQueryPerfNoncoveringIndexTailLatencyEvaluatorCase
):
    case_id = "noncovering_index_tail_latency_reduced"
