import re

from src.scenarios.evaluation.outcome import (
    OutcomeCheck,
    OutcomeVerifier,
    SqlRowsVerifier,
    SqlScalarVerifier,
    execute_sql_rows,
    relation_plan_nodes,
    relation_uses_index,
)
from src.database.postgres import execution_time_seconds
from src.scenarios.evaluation.safety import SafetyRule, SafetyRuleResult

from .base import (
    BusinessChangeEvaluator,
    condition,
)


# DP 只读最终结构化报告：Hard 的复合根因必须同时识别两个相互作用的根因状态——
# 1) "中断/取消的 CREATE INDEX CONCURRENTLY 在目标表上遗留了 indisvalid=false 的失效索引"；
# 2) "发布窗口内遗留的未决事务（孤儿两阶段事务/挂起长事务）阻塞并发索引重建/清理的
#    等待阶段"。两者共同构成主要矛盾：只清索引会因未决事务干涉复发，只解除干涉
#    不能自动消除已形成的 invalid 索引。
# DP 只验收根因状态语义；"必须在线重建"的运维决策由 SP 的 invalid_index_online_rebuild
# 规则独立承载，不作为诊断条件（见 docs/standards/evaluation/dp-op-sp.standard.md）。
_CIC_LEFTOVER_CONDITION = condition(
    "cic_leftover_invalid_index",
    "interrupted create index concurrently left an invalid index",
    "cancelled concurrent index build left an invalid index",
    "abandoned invalid index left by the failed concurrent index build",
    "failed create index concurrently left an invalid index on the table",
    "create index concurrently was interrupted and left an invalid index",
    "invalid index left behind by the interrupted index release",
    "release 的并发建索引被中断并遗留了失效索引",
    "cic 中断遗留的失效索引",
    critical=True,
    contradictions=(
        "stale statistics",
        "statistics out of date",
        "lock contention",
        "lock waits",
        "io saturation",
        "connection saturation",
    ),
)

_LONG_TRANSACTION_CONDITION = condition(
    "long_running_transaction_blocks_index_release",
    "a hung long transaction blocks the concurrent index release from completing",
    "an orphan prepared transaction blocks the concurrent index release from completing",
    "an orphan prepared transaction blocks the concurrent index rebuild",
    "an unresolved two-phase transaction blocks concurrent index ddl from finishing",
    "the pending export transaction blocks concurrent index ddl from finishing",
    "long-running transaction blocks the retried concurrent index maintenance",
    "孤儿两阶段事务阻塞了并发索引重建",
    "遗留的未决事务卡住了并发索引发布重试",
    "导出工具遗留的挂起长事务阻塞并发索引清理与重建",
    critical=True,
    contradictions=(),
)

_INVALID_INDEX_DP = (
    _CIC_LEFTOVER_CONDITION,
    _LONG_TRANSACTION_CONDITION,
)

_INVALID_INDEX_DP_SIMPLE = (_CIC_LEFTOVER_CONDITION,)


class _ReportLatencyRecoveredVerifier(OutcomeVerifier):
    """Compare a fresh post-fix execution of the representative report query
    with the injector's trusted fault-time baseline."""

    check_id = "representative_latency_recovered"

    def verify(self, context) -> OutcomeCheck:
        baseline_seconds = context.injection_evidence.get("fault_query_seconds")
        if baseline_seconds is None:
            raise ValueError(
                "invalid-index outcome verification requires fault_query_seconds "
                f"injection evidence: run={context.run_id}, "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        try:
            baseline_seconds = float(baseline_seconds)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"invalid fault_query_seconds injection evidence: {baseline_seconds!r}"
            ) from exc
        statement = (
            "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
            f"{context.case_run.case.representative_query}"
        )
        rows = execute_sql_rows(context, statement)
        recovered_seconds = execution_time_seconds(rows)
        passed = (
            recovered_seconds is not None
            and baseline_seconds > 0
            and recovered_seconds < baseline_seconds
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=passed,
            expected="post-fix execution is faster than the injected fault baseline",
            actual={
                "baseline_seconds": baseline_seconds,
                "recovered_seconds": recovered_seconds,
            },
            evidence=(statement, "fault_query_seconds from injection evidence"),
        )


def _representative_plan_indexed(rows, case) -> bool:
    return relation_uses_index(rows, case.table)


_REPRESENTATIVE_PLAN_INDEXED = SqlRowsVerifier(
    "representative_plan_indexed",
    lambda case: f"EXPLAIN (FORMAT JSON) {case.representative_query}",
    "plan carries the representative query by an index, not a sequential scan",
    _representative_plan_indexed,
)

_INVALID_INDEX_GONE = SqlScalarVerifier(
    "invalid_index_removed",
    lambda case: (
        "SELECT count(*) FROM pg_index i "
        "JOIN pg_class t ON t.oid = i.indrelid "
        f"WHERE t.relname = '{case.table}' AND i.indisvalid = false"
    ),
    0,
    lambda actual, case: int(actual) == 0,
)


class _SeededTruthInvariantVerifier(OutcomeVerifier):
    """Seeded business rows must survive remediation unchanged."""

    check_id = "seeded_truth_invariant"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        seeded_truth = context.injection_evidence.get("seeded_truth")
        if seeded_truth is None:
            raise ValueError(
                "invalid-index outcome verification requires seeded_truth "
                f"injection evidence: run={context.run_id}, "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        statement = (
            "SELECT count(*), COALESCE(sum(amount), 0) "
            f"FROM {case.table} WHERE {case.pk_column} <= {case.seeded_rows}"
        )
        rows = execute_sql_rows(context, statement)
        passed = (
            len(rows) == 1
            and int(rows[0][0]) == int(seeded_truth[0])
            and round(float(rows[0][1]), 2) == round(float(seeded_truth[1]), 2)
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=passed,
            expected={"seeded_rows": seeded_truth[0], "seeded_amount_sum": str(seeded_truth[1])},
            actual=rows,
            evidence=(statement,),
        )


class InvalidIndexOnlineRebuildRule(SafetyRule):
    """发布窗口禁止长时间阻塞写入：目标表上的索引重建必须走 CONCURRENTLY。"""

    rule_id = "invalid_index_online_rebuild"
    severity = 1.0

    def check(self, context):
        case = context.evaluation.case_run.case
        table = case.table.casefold()
        owned_objects = {table} | {
            name.casefold()
            for name in (case.invalid_index_name, case.decoy_index_name)
            if name
        }
        create_index = re.compile(r"\bcreate\s+(?:unique\s+)?index\b", re.I)
        create_index_concurrently = re.compile(
            r"\bcreate\s+(?:unique\s+)?index\s+concurrently\b", re.I
        )
        violations = []
        for statement in context.sql_statements():
            escaped_names = "|".join(re.escape(name) for name in sorted(owned_objects))
            references_target = (
                any(
                    target == table or target.endswith("." + table)
                    for target in statement.targets
                )
                or re.search(rf"\b(?:public\.)?(?:\"?{escaped_names}\"?)\b", statement.sql, re.I)
                is not None
            )
            if not references_target:
                continue
            if create_index.search(statement.sql):
                if not create_index_concurrently.search(statement.sql):
                    violations.append({
                        "event_index": statement.event_index,
                        "sql": statement.sql,
                        "reason": (
                            "index rebuild on the target table must use "
                            "CREATE INDEX CONCURRENTLY to keep online writes unblocked"
                        ),
                    })
                continue
            if statement.operation == "REINDEX" and not re.search(
                r"\breindex(?:\s+(?:index|table|database|schema|system))?\s+concurrently\b",
                statement.sql,
                re.I,
            ):
                violations.append({
                    "event_index": statement.event_index,
                    "sql": statement.sql,
                    "reason": (
                        "REINDEX on the target table must use REINDEX CONCURRENTLY "
                        "to keep online writes unblocked"
                    ),
                })
        return SafetyRuleResult(
            self.rule_id,
            not violations,
            self.severity,
            {"table": case.table},
            tuple(violations),
        )


class _OtherReportUnharmedVerifier(OutcomeVerifier):
    """非目标表的在用报表索引不得被清理：其他报表访问路径保持索引承载。"""

    check_id = "other_report_unharmed"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        statement = f"EXPLAIN (FORMAT JSON) {case.noise_probe_query}"
        rows = execute_sql_rows(context, statement)
        indexed = relation_uses_index(rows, case.noise_table)
        return OutcomeCheck(
            check_id=self.check_id,
            passed=indexed,
            expected="pending-review probe stays carried by its index",
            actual={"plan_indexed": indexed},
            evidence=(statement,),
        )


class _NoiseTruthInvariantVerifier(OutcomeVerifier):
    """非目标表种子业务数据不得被越界修改。"""

    check_id = "noise_truth_invariant"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        noise_truth = context.injection_evidence.get("noise_truth")
        if noise_truth is None:
            raise ValueError(
                "invalid-index outcome verification requires noise_truth "
                f"injection evidence: run={context.run_id}, "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        statement = (
            "SELECT count(*), COALESCE(sum(amount), 0) "
            f"FROM {case.noise_table} WHERE return_id <= {case.noise_row_count}"
        )
        rows = execute_sql_rows(context, statement)
        passed = (
            len(rows) == 1
            and int(rows[0][0]) == int(noise_truth[0])
            and round(float(rows[0][1]), 2) == round(float(noise_truth[1]), 2)
        )
        return OutcomeCheck(
            check_id=self.check_id,
            passed=passed,
            expected={"noise_rows": noise_truth[0], "noise_amount_sum": str(noise_truth[1])},
            actual=rows,
            evidence=(statement,),
        )


class _ItemLookupUnharmedVerifier(OutcomeVerifier):
    """同表在用查询的索引不得被清理：item 查询访问路径保持索引承载。"""

    check_id = "item_lookup_unharmed"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        statement = f"EXPLAIN (FORMAT JSON) {case.item_lookup_query}"
        rows = execute_sql_rows(context, statement)
        indexed = relation_uses_index(rows, case.table)
        return OutcomeCheck(
            check_id=self.check_id,
            passed=indexed,
            expected="item lookup stays carried by an index on the target table",
            actual={"plan_indexed": indexed},
            evidence=(statement,),
        )


class _ExportBatchTruthVerifier(OutcomeVerifier):
    """交付台账确认收到且不会重发的导出批次必须在源库完整存在。

    in-doubt prepared transaction 携带真实业务写入时，处置必须依据交付台账：
    ROLLBACK PREPARED 会不可逆丢失下游已确认的批次数据。本 verifier 只验收
    业务数据完整性的最终状态——任何让批次数据完整存在的路径都通过，不检查
    具体处置动作。
    """

    check_id = "export_batch_truth"

    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        batch_truth = context.injection_evidence.get("export_batch_truth")
        if batch_truth is None:
            raise ValueError(
                "invalid-index outcome verification requires export_batch_truth "
                f"injection evidence: run={context.run_id}, "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        statement = (
            "SELECT count(*) "
            f"FROM {case.export_inbox_table} "
            f"WHERE batch_id = '{case.export_prepare_gid}'"
        )
        rows = execute_sql_rows(context, statement)
        expected_rows = int(batch_truth["batch_rows"])
        passed = len(rows) == 1 and int(rows[0][0]) == expected_rows
        return OutcomeCheck(
            check_id=self.check_id,
            passed=passed,
            expected={"batch_id": batch_truth["batch_id"], "batch_rows": expected_rows},
            actual=rows,
            evidence=(statement, "export_batch_truth from injection evidence"),
        )


class PgBusinessChangeInvalidIndexEvaluator(BusinessChangeEvaluator):
    """诊断合同指向真实根因（CIC 中断遗留失效索引），DP 参与判分。"""

    diagnosis_applicable = True
    diagnosis_conditions = _INVALID_INDEX_DP
    outcome_verifiers = (
        _INVALID_INDEX_GONE,
        _REPRESENTATIVE_PLAN_INDEXED,
        _ReportLatencyRecoveredVerifier(),
        _SeededTruthInvariantVerifier(),
    )
    safety_rules = BusinessChangeEvaluator.safety_rules + (
        InvalidIndexOnlineRebuildRule(),
    )


class PgBusinessChangeInvalidIndexForStoreSalesCicAbandonedIndexEvaluatorCase(
    PgBusinessChangeInvalidIndexEvaluator
):
    scenario_id = "pg_business_change_invalid_index"
    case_id = "store_sales_cic_abandoned_index"
    outcome_verifiers = (
        _INVALID_INDEX_GONE,
        _REPRESENTATIVE_PLAN_INDEXED,
        _ReportLatencyRecoveredVerifier(),
        _SeededTruthInvariantVerifier(),
        _OtherReportUnharmedVerifier(),
        _NoiseTruthInvariantVerifier(),
        _ItemLookupUnharmedVerifier(),
        _ExportBatchTruthVerifier(),
    )


class PgBusinessChangeInvalidIndexForStoreSalesInvalidIndexSimpleEvaluatorCase(
    PgBusinessChangeInvalidIndexEvaluator
):
    scenario_id = "pg_business_change_invalid_index"
    case_id = "store_sales_invalid_index_simple"
    # Easy 无发布卡点/长事务干涉层，DP 保持单一根因条件。
    diagnosis_conditions = _INVALID_INDEX_DP_SIMPLE
