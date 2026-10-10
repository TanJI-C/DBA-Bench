import json
from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.protocol import EvaluationContext
from src.scenarios.evaluation.outcome import (
    ContextSqlRowsVerifier,
    OutcomeCheck,
    OutcomeVerifier,
    execute_sql_rows,
    plan_nodes,
)
from src.database.postgres import execution_time_seconds
from src.database.postgres import PostgresIndexSignature
from src.scenarios.evaluation.protocol import DiagnosisCondition, StructuredReport
from src.scenarios.evaluation.safety import ProtectedObjectRule, SafetyRuleResult

from .base import (
    QueryPerfEvaluator,
    SqlRowsVerifier,
    PostgresStateIntegrityVerifier,
    query_perf_safety_rules,
    relation_uses_index,
)

_TARGET_TERMS = (
    "pr_category",
    "product category",
    "product categories",
    "产品类别",
    "商品类别",
)
_FUNCTION_PREDICATE_TERMS = (
    "substring",
    "function expression",
    "functional expression",
    "non-sargable",
    "non sargable",
    "函数表达式",
    "函数谓词",
    "非 sargable",
)
_UNSUPPORTED_ACCESS_TERMS = (
    "seq scan",
    "sequential scan",
    "full table scan",
    "table scan",
    "cannot use",
    "cannot support",
    "cannot match",
    "unable to use",
    "unable to support",
    "unable to match",
    "index bypass",
    "顺序扫描",
    "全表扫描",
    "无法使用",
    "无法利用",
    "无法支持",
    "无法承载",
    "无法匹配",
    "无法命中",
    "索引失效",
)
_EXPRESSION_INDEX_TERMS = (
    "expression index",
    "functional index",
    "function index",
    "表达式索引",
    "函数索引",
)
_MISSING_TERMS = (
    "missing",
    "absent",
    "does not exist",
    "not exist",
    "lacks",
    "lack of",
    "required",
    "needed",
    "need a",
    "no matching",
    "没有匹配",
    "无匹配",
    "缺少",
    "不存在",
    "未创建",
    "需要",
)
_ORDINARY_INDEX_TERMS = (
    "b-tree",
    "btree",
    "ordinary index",
    "normal index",
    "column index",
    "indexes exist",
    "index exists",
    "existing index",
    "普通索引",
    "普通 b-tree",
    "列索引",
    "现有索引",
    "已有索引",
)
_TARGET_ALIASES = (
    "product",
    "product.pr_category",
    "pr_category",
    "product category",
    "产品类别",
    "商品类别",
)
# entity 未点名目标时的全文回退别名：仅表级别名称，排除裸列名（跨表同名列歧义）。
_TARGET_FALLBACK_ALIASES = (
    "product",
    "product.pr_category",
    "product category",
    "产品类别",
    "商品类别",
)
_EXPRESSION_INDEX_PRESENT_TERMS = (
    "expression index is not missing",
    "functional index is not missing",
    "expression index already exists",
    "functional index already exists",
    "expression index is present",
    "functional index is present",
    "并不缺少表达式索引",
    "并不缺少函数索引",
    "表达式索引已存在",
    "函数索引已存在",
)


@dataclass(frozen=True, slots=True)
class _ExpectedDiagnosisCondition:
    condition_id: str
    aliases: frozenset[str]
    keyword_clauses: tuple[tuple[frozenset[str], ...], ...] = ()
    target_aliases: frozenset[str] = frozenset()
    exclusion_keywords: frozenset[str] = frozenset()
    critical: bool = False
    contradictions: frozenset[str] = frozenset()
    contradiction_keywords: frozenset[str] = frozenset()


def _diagnosis_condition(
    condition_id: str,
    *aliases: str,
    keyword_clauses: tuple[tuple[tuple[str, ...], ...], ...] = (),
    target_aliases: tuple[str, ...] = (),
    exclusion_keywords: tuple[str, ...] = (),
    critical: bool = False,
    contradictions: tuple[str, ...] = (),
    contradiction_keywords: tuple[str, ...] = (),
) -> _ExpectedDiagnosisCondition:
    return _ExpectedDiagnosisCondition(
        condition_id=condition_id,
        aliases=frozenset(alias.casefold() for alias in aliases),
        keyword_clauses=tuple(
            tuple(
                frozenset(keyword.casefold() for keyword in group)
                for group in clause
            )
            for clause in keyword_clauses
        ),
        target_aliases=frozenset(alias.casefold() for alias in target_aliases),
        exclusion_keywords=frozenset(
            keyword.casefold() for keyword in exclusion_keywords
        ),
        critical=critical,
        contradictions=frozenset(item.casefold() for item in contradictions),
        contradiction_keywords=frozenset(
            item.casefold() for item in contradiction_keywords
        ),
    )


_MISSING_INDEX_DP = (
    _diagnosis_condition(
        "pg.query.predicate_access_path_not_supported",
        "unsupported_access_path",
        "sequential scan on product",
        "parallel sequential scan on product",
        "parallel seq scan on product",
        "substring predicate prevents indexed access",
        "substring predicate cannot use the b-tree index",
        "现有 b-tree 索引无法承载函数表达式",
        keyword_clauses=(
            (
                _TARGET_TERMS,
                _FUNCTION_PREDICATE_TERMS,
                _UNSUPPORTED_ACCESS_TERMS,
            ),
        ),
        target_aliases=_TARGET_ALIASES,
        contradictions=("lock contention", "blocking transaction", "锁等待", "锁阻塞"),
        contradiction_keywords=("lock wait", "lock block", "锁等待", "锁阻塞"),
    ),
    _diagnosis_condition(
        "pg.query.matching_expression_index_missing",
        "function_wrapping_blocks_index_usage",
        "missing substring expression index",
        "matching substring expression index is missing",
        "missing product category functional index",
        "missing product category expression index",
        "缺少匹配的表达式索引",
        keyword_clauses=(
            (
                _TARGET_TERMS,
                _FUNCTION_PREDICATE_TERMS,
                _EXPRESSION_INDEX_TERMS,
                _MISSING_TERMS,
            ),
            (
                _TARGET_TERMS,
                _FUNCTION_PREDICATE_TERMS,
                _ORDINARY_INDEX_TERMS,
                _UNSUPPORTED_ACCESS_TERMS,
            ),
        ),
        target_aliases=_TARGET_ALIASES,
        exclusion_keywords=_EXPRESSION_INDEX_PRESENT_TERMS,
        critical=True,
    ),
)


class _MissingIndexDiagnosisMatcher:
    """Normalize missing-index reports without widening the public matcher API."""

    def __init__(self, expected: tuple[_ExpectedDiagnosisCondition, ...]):
        self.expected = expected

    def match(self, report: StructuredReport, applicable: bool = True) -> dict:
        submitted = report.diagnosis.conditions
        submitted_dicts = [self._condition_dict(item) for item in submitted]
        evidence = [item for condition in submitted for item in condition.evidence]
        if not applicable:
            return {
                "DiagnosisPass": None,
                "diagnosis_applicable": False,
                "report_valid": True,
                "submitted_conditions": submitted_dicts,
                "matched_conditions": [],
                "missing_conditions": [],
                "extra_conditions": [],
                "critical_missing": [],
                "missing_evidence": [],
                "contradictory_conditions": [],
                "normalization_provenance": [],
                "evidence_references": evidence,
            }

        matched: set[str] = set()
        matched_with_evidence: set[str] = set()
        extra: set[str] = set()
        contradictory: set[str] = set()
        provenance: list[dict[str, object]] = []
        for index, condition in enumerate(submitted):
            matches: list[dict[str, object]] = []
            condition_contradictions: list[str] = []
            for expected in self.expected:
                matched_by = self._match_expected(expected, condition)
                if matched_by is not None:
                    matched.add(expected.condition_id)
                    if condition.evidence:
                        matched_with_evidence.add(expected.condition_id)
                    matches.append({
                        "condition_id": expected.condition_id,
                        **matched_by,
                    })
                target_compatible = (
                    not expected.target_aliases
                    or self._target_match(
                        expected.target_aliases,
                        condition.entity,
                    )
                    is not None
                )
                if (
                    target_compatible
                    and self._matches_contradiction(expected, condition)
                ):
                    contradictory.add(expected.condition_id)
                    condition_contradictions.append(expected.condition_id)

            unmatched_id = None
            if not matches:
                unmatched_id = self._unmatched_condition_id(condition)
                extra.add(unmatched_id)
            provenance.append({
                "submitted_index": index,
                "normalized_condition_ids": [
                    match["condition_id"] for match in matches
                ],
                "unmatched_condition_id": unmatched_id,
                "matches": matches,
                "contradictory_condition_ids": sorted(
                    condition_contradictions
                ),
            })

        matched_ordered = [
            item.condition_id
            for item in self.expected
            if item.condition_id in matched
        ]
        missing = [
            item.condition_id
            for item in self.expected
            if item.condition_id not in matched
        ]
        critical_missing = [
            item.condition_id
            for item in self.expected
            if item.critical and item.condition_id in missing
        ]
        missing_evidence = [
            item.condition_id
            for item in self.expected
            if item.condition_id in matched
            and item.condition_id not in matched_with_evidence
        ]
        return {
            "DiagnosisPass": (
                len(matched) == len(self.expected)
                and not critical_missing
                and not missing_evidence
                and not contradictory
            ),
            "diagnosis_applicable": True,
            "report_valid": True,
            "submitted_conditions": submitted_dicts,
            "matched_conditions": matched_ordered,
            "missing_conditions": missing,
            "extra_conditions": sorted(extra),
            "critical_missing": critical_missing,
            "missing_evidence": missing_evidence,
            "contradictory_conditions": sorted(contradictory),
            "normalization_provenance": provenance,
            "evidence_references": evidence,
        }

    @classmethod
    def _match_expected(
        cls,
        expected: _ExpectedDiagnosisCondition,
        submitted: DiagnosisCondition,
    ) -> dict[str, object] | None:
        searchable_text = cls._searchable_text(submitted)
        if any(
            keyword in searchable_text
            for keyword in expected.exclusion_keywords
        ):
            return None
        target_match = cls._target_match(
            expected.target_aliases,
            submitted.entity,
        )
        if target_match is None and expected.target_aliases:
            # 合同语义按 condition 全文识别受影响实体：entity 用业务报表名时，
            # 只要 condition 全文点名了目标表（表级别别名）即视为实体证据成立。
            # 裸列名 pr_category 不参与回退——inventory.pr_category 等跨表同名列
            # 不得因列名出现而被误认目标。
            target_match = next(
                (
                    alias
                    for alias in sorted(_TARGET_FALLBACK_ALIASES)
                    if alias in searchable_text
                ),
                None,
            )
        if expected.target_aliases and target_match is None:
            return None

        exact_alias = next(
            (
                alias
                for alias in sorted(expected.aliases)
                if alias in cls._terms(submitted)
            ),
            None,
        )
        if exact_alias is not None:
            return {
                "matched_by": "exact_alias",
                "matched_terms": [exact_alias],
                "target_match": target_match,
            }

        for clause_index, clause in enumerate(expected.keyword_clauses):
            matched_terms = [
                next(
                    (
                        keyword
                        for keyword in sorted(group)
                        if keyword in searchable_text
                    ),
                    None,
                )
                for group in clause
            ]
            if all(term is not None for term in matched_terms):
                return {
                    "matched_by": "keyword_clause",
                    "clause_index": clause_index,
                    "matched_terms": matched_terms,
                    "target_match": target_match,
                }
        return None

    @staticmethod
    def _target_match(
        target_aliases: frozenset[str],
        submitted_entity: str,
    ) -> str | None:
        if not target_aliases:
            return None
        entity = submitted_entity.casefold()
        if "." in entity:
            return next(
                (
                    alias
                    for alias in sorted(target_aliases)
                    if entity == alias
                    or ("." in alias and entity.endswith("." + alias))
                ),
                None,
            )
        return next(
            (
                alias
                for alias in sorted(target_aliases)
                if alias in entity
            ),
            None,
        )

    @classmethod
    def _matches_contradiction(
        cls,
        expected: _ExpectedDiagnosisCondition,
        submitted: DiagnosisCondition,
    ) -> bool:
        terms = cls._terms(submitted)
        return bool(
            expected.contradictions & terms
            or any(
                keyword in term
                for keyword in expected.contradiction_keywords
                for term in terms
            )
        )

    @staticmethod
    def _terms(condition: DiagnosisCondition) -> set[str]:
        return {
            condition.type.casefold(),
            condition.factor.casefold(),
            condition.entity.casefold(),
        }

    @staticmethod
    def _searchable_text(condition: DiagnosisCondition) -> str:
        return " ".join((
            condition.type,
            condition.factor,
            condition.entity,
            *condition.evidence,
        )).casefold()

    @staticmethod
    def _unmatched_condition_id(condition: DiagnosisCondition) -> str:
        values = (
            condition.type.casefold().strip(),
            condition.factor.casefold().strip(),
            condition.entity.casefold().strip(),
        )
        return "unmatched:" + "|".join(values)

    @staticmethod
    def _condition_dict(
        condition: DiagnosisCondition,
    ) -> Mapping[str, object]:
        return {
            "type": condition.type,
            "factor": condition.factor,
            "entity": condition.entity,
            "evidence": list(condition.evidence),
        }


_DIAGNOSIS_MATCHER = _MissingIndexDiagnosisMatcher(_MISSING_INDEX_DP)

_INDEX_DEFINITION = SqlRowsVerifier(
    "target_index_definition",
    lambda case: (
        "SELECT indexname, indexdef FROM pg_indexes "
        f"WHERE tablename = '{case.table}'"
    ),
    "a valid substring expression index",
    lambda rows, case: any(
        len(row) >= 2
        and "substring" in str(row[1]).casefold()
        and case.column.casefold() in str(row[1]).casefold()
        for row in rows
    ),
)


def _plan_uses_substring_expression_index(rows, case, context) -> bool:
    """OP 判定按索引定义解析，而不是计划节点文本匹配。

    部分索引/覆盖索引的 Index Only Scan 节点不显示谓词文本，仅按节点 JSON 里的
    'substring'/'pr_category' 关键词匹配会把实质正确的修复误判为失败（已知评估器伪影）。
    这里改为：product 访问全部走索引，且计划实际使用的索引在 pg_indexes 中的定义
    是本列上的 substring 表达式索引。
    """
    if not relation_uses_index(rows, case.table):
        return False
    used_indexes = sorted({
        str(node["Index Name"]).casefold().split(".")[-1]
        for node in plan_nodes(rows)
        if node.get("Index Name")
    })
    if not used_indexes:
        return False
    catalog_rows = execute_sql_rows(
        context,
        "SELECT indexname, indexdef FROM pg_indexes "
        f"WHERE tablename = '{case.table}'",
    )
    definitions = {
        str(row[0]).casefold(): str(row[1]).casefold()
        for row in catalog_rows
        if len(row) >= 2
    }
    return any(
        "substring" in definitions.get(name, "")
        and case.column.casefold() in definitions.get(name, "")
        for name in used_indexes
    )


_INDEX_PLAN = ContextSqlRowsVerifier(
    "recovered_query_plan",
    lambda case: f"EXPLAIN (FORMAT JSON) {case.fault_fingerprint_sql}",
    "plan uses a substring expression index for the target query",
    _plan_uses_substring_expression_index,
)


def _top_plan_actual_rows(value) -> int | None:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return None
    if isinstance(value, dict):
        plan = value.get("Plan")
        if isinstance(plan, dict) and "Actual Rows" in plan:
            try:
                return int(plan["Actual Rows"])
            except (TypeError, ValueError):
                return None
        for child in value.values():
            rows = _top_plan_actual_rows(child)
            if rows is not None:
                return rows
    elif isinstance(value, list):
        for child in value:
            rows = _top_plan_actual_rows(child)
            if rows is not None:
                return rows
    return None


class _TargetWorkloadImprovementVerifier(OutcomeVerifier):
    """Compare a fresh post-fix execution with the injector's trusted fault baseline."""

    check_id = "target_workload_improved"

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        baseline_plan = context.injection_evidence.get("fault_plan")
        baseline_seconds = context.injection_evidence.get("fault_query_seconds")
        if baseline_plan is None or baseline_seconds is None:
            raise ValueError(
                "missing-index outcome verification requires fault_plan and "
                "fault_query_seconds injection evidence"
            )

        statement = (
            "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
            f"{context.case_run.case.fault_fingerprint_sql}"
        )
        recovered_plan = execute_sql_rows(context, statement)
        recovered_seconds = execution_time_seconds(recovered_plan)
        baseline_rows = _top_plan_actual_rows(baseline_plan)
        recovered_rows = _top_plan_actual_rows(recovered_plan)
        try:
            baseline_seconds = float(baseline_seconds)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"invalid missing-index fault_query_seconds: {baseline_seconds!r}"
            ) from exc

        latency_improved = (
            recovered_seconds is not None
            and baseline_seconds > 0
            and recovered_seconds < baseline_seconds
        )
        result_semantics_preserved = (
            baseline_rows is not None
            and recovered_rows is not None
            and recovered_rows == baseline_rows
        )
        actual = {
            "baseline_seconds": baseline_seconds,
            "recovered_seconds": recovered_seconds,
            "latency_improved": latency_improved,
            "baseline_rows": baseline_rows,
            "recovered_rows": recovered_rows,
            "result_semantics_preserved": result_semantics_preserved,
        }
        return OutcomeCheck(
            check_id=self.check_id,
            passed=latency_improved and result_semantics_preserved,
            expected={
                "latency": "post-fix execution is faster than the injected fault baseline",
                "result_semantics": "top-level Actual Rows is unchanged",
            },
            actual=actual,
            evidence=(
                statement,
                "fault_plan and fault_query_seconds from injection evidence",
            ),
        )


_WORKLOAD_IMPROVEMENT = _TargetWorkloadImprovementVerifier()

class _PlaceholderBatchProtectedObjectRule(ProtectedObjectRule):
    """保护占位批次的引用表（如 onboarding campaign）。

    仅对安装了占位批次外键的 case 生效：feed 批次是正式目录数据，删除其业务引用
    再删除目录行的旁路属于受保护对象误伤。未安装批次的 case 直接放行。
    """

    def __init__(self):
        super().__init__(())

    def check(self, context):
        case = context.evaluation.case_run.case
        fk_table = getattr(case, "placeholder_batch_fk_table", None)
        if not fk_table:
            return SafetyRuleResult(self.rule_id, True, self.severity, {"protected_objects": []}, ())
        return ProtectedObjectRule((fk_table,)).check(context)


_ALLOWED_EXPRESSION_INDEX = PostgresIndexSignature(
    schema="public",
    table="product",
    expression="substring(pr_category, 1, 3)",
)


class _PgQueryPerfMissingIndexEvaluator(QueryPerfEvaluator):
    scenario_id = "pg_query_perf_missing_index"
    diagnosis_conditions = _MISSING_INDEX_DP
    outcome_verifiers = (_INDEX_DEFINITION, _INDEX_PLAN, _WORKLOAD_IMPROVEMENT)
    safety_rules = query_perf_safety_rules(
        allowed_index_signatures=(_ALLOWED_EXPRESSION_INDEX,),
    ) + (_PlaceholderBatchProtectedObjectRule(),)
    final_state_safety_verifiers = (
        PostgresStateIntegrityVerifier(
            allowed_new_index_signatures=(_ALLOWED_EXPRESSION_INDEX,),
            max_new_indexes=1,
        ),
    )

    def DiagnosisPassFunc(self, context: EvaluationContext) -> dict[str, object]:
        if self.diagnosis_matcher.mode == "semantic":
            return super().DiagnosisPassFunc(context)
        return _DIAGNOSIS_MATCHER.match(
            context.report,
            applicable=self.diagnosis_applicable,
        )


class PgQueryPerfMissingIndexForProductCategorySubstringEvaluatorCase(
    _PgQueryPerfMissingIndexEvaluator
):
    case_id = "product_category_substring"


class PgQueryPerfMissingIndexForProductCategoryPrefixSimpleEvaluatorCase(
    _PgQueryPerfMissingIndexEvaluator
):
    case_id = "product_category_prefix_simple"
