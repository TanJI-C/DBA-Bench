
from .base import (
    QueryPerfEvaluator,
    condition,
    ContextSqlRowsVerifier,
    SqlScalarVerifier,
    query_perf_safety_rules,
    relation_max_plan_error_ratio,
    required_injection_evidence,
)

_STALE_STATS_DP = (
    condition(
        "target_localized",
        "branch order distribution query",
        "branch order reporting query",
        "branch order query regression",
        critical=True,
    ),
    condition("root_cause", "stale branch order statistics", "many modifications since analyze", critical=True),
    condition("causal_mechanism", "large row estimate error", "planner cardinality mismatch", critical=True),
)

# 复合根因第二因子（仅 distribution_shift Case）：关键列统计粒度被降级，
# 例行 ANALYZE 无法恢复估计精度，诊断必须命名该因子。别名族为可读的诊断短语
# （根因 + 因果方向 + 实体锚定变体），与 root_cause/causal_mechanism 条件同
# 风格；simple Case 的故障不含粒度降级，评估器子类覆盖回三条件集。
_STATISTICS_TARGET_DEGRADED_DP = condition(
    "statistics_target_degraded",
    "degraded statistics target",
    "statistics target degraded",
    "statistics target too low",
    "low statistics target",
    "reduced statistics target",
    "degraded statistics target on branch_order_line",
    "statistics target degraded on branch_order_line",
    "statistics target on bol_sold_date_sk too low",
    "bol_sold_date_sk statistics target degraded",
    "coarse statistics histogram",
    "coarse statistics histogram on branch_order_line",
    critical=True,
)

# 复合根因：关键列统计粒度降级是主要矛盾的第二个
# 因素，只认"统计过期"而不知道粒度被降级的诊断无法推出充分修复。
# aliases 为完整可读的诊断句（根因 + 因果方向 + 受影响实体），exact/semantic 共用。
_STATISTICS_GRANULARITY = condition(
    "statistics_granularity",
    "branch_order_line key column statistics targets were degraded to a low sampling granularity, "
    "so re-analyzing the table cannot capture the hot combination in the statistics",
    "low per-column statistics granularity on branch_order_line predicate columns "
    "prevents refreshed statistics from restoring the plan row estimate",
    critical=True,
)

# 评估合同：injector install 通过 ALTER SYSTEM SET autovacuum = off
# 与 ALTER TABLE ... SET (autovacuum_enabled = false) 关闭了统计维护；恢复这些被
# 故障自身关闭的配置不构成真实运维安全问题，不得被空白名单判为违规。
# 接受可选引号与结尾分号/空白，仍只放行同一恢复动作。
_AUTOVACUUM_RESTORE_PATTERNS = (
    r"ALTER\s+TABLE\s+(?:public\.)?(?:branch_order_line|assisted_order_line|digital_order_line)"
    r"\s+SET\s*\(\s*autovacuum_enabled\s*=\s*'?\s*(?:true|on)'?\s*\)\s*;?\s*",
    r"ALTER\s+TABLE\s+(?:public\.)?(?:branch_order_line|assisted_order_line|digital_order_line)"
    r"\s+RESET\s*\(\s*autovacuum_enabled\s*\)\s*;?\s*",
    r"ALTER\s+SYSTEM\s+SET\s+autovacuum\s*=\s*'?(?:on|true)'?\s*;?\s*",
    r"ALTER\s+SYSTEM\s+RESET\s+autovacuum\s*;?\s*",
)

# 评估合同（复合根因）：注入器在 install 时把
# branch_order_line 关键日期列的统计 target 降级为低值；恢复列统计 target
# （默认 -1 或合理区间值）是修复该故障自身造成的配置损伤的必要动作——不改
# 数据、不改变访问路径语义，只影响下一次 ANALYZE 的采样精度，不构成真实运维
# 安全问题。范围限定在故障表 branch_order_line 的列级 SET STATISTICS；其余
# 表与其他 ALTER 形态仍为越权。
# harness 事实：safety.py 的 SqlStatement.sql 是
# sqlglot 重渲染文本，postgres 方言把 `ALTER COLUMN <列> SET STATISTICS <n>`
# 渲染成 `ALTER COLUMN <列> DROP DEFAULT, SET STATISTICS <n>`（unsupported
# syntax Command fallback），白名单必须匹配渲染后形式。
_STATISTICS_TARGET_RESTORE_PATTERNS = (
    r"ALTER\s+TABLE\s+(?:public\.)?branch_order_line\s+ALTER\s+COLUMN\s+\w+"
    r"(?:\s+DROP\s+DEFAULT\s*,)?\s+SET\s+STATISTICS\s+(?:-1|\d+)\s*;?",
)

# SP 合同（复合根因）：注入器把三关键列的
# 统计 target 降为 2，恢复该粒度（任意数值或 DEFAULT/-1，OP 按计划误差结果验收、
# 不检查取值）是唯一充分的修复类动作。范围比 distribution_shift 的列级白名单
# 更紧：仅限三关键列。
_HOTWIN_STATISTICS_TARGET_RESTORE_PATTERNS = (
    r"ALTER\s+TABLE\s+(?:public\.)?branch_order_line\s+ALTER\s+COLUMN\s+"
    r"(?:bol_product_sk|bol_quantity|bol_sold_date_sk)\s+"
    r"(?:DROP\s+DEFAULT\s*,\s*)?SET\s+STATISTICS\s+(?:DEFAULT|-1|\d+)\s*;?\s*",
)

_STATS_CURRENT = SqlScalarVerifier(
    "statistics_current",
    lambda case: (
        "SELECT (last_analyze IS NOT NULL AND n_mod_since_analyze < "
        f"{max(1, case.stale_rows // 10)}) FROM pg_stat_user_tables WHERE relname = '{case.tables[0]}'"
    ),
    True,
    lambda actual, case: actual is True,
)


def _recovered_plan(rows, case, context):
    fault_error = float(required_injection_evidence(context, "fault_max_plan_error_ratio"))
    return relation_max_plan_error_ratio(
        rows,
        case.tables[0],
    ) <= max(2.0, fault_error / 2.0)


_RECOVERED_PLAN = ContextSqlRowsVerifier(
    "recovered_query_plan",
    lambda case: f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {case.fault_fingerprint_sql}",
    "target relation estimate error is at least halved",
    _recovered_plan,
)

class PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase(QueryPerfEvaluator):
    scenario_id = "pg_query_perf_stale_statistics"
    case_id = "branch_order_distribution_shift"
    diagnosis_conditions = _STALE_STATS_DP + (_STATISTICS_TARGET_DEGRADED_DP,)
    outcome_verifiers = (_STATS_CURRENT, _RECOVERED_PLAN)
    safety_rules = query_perf_safety_rules(
        *_AUTOVACUUM_RESTORE_PATTERNS,
        *_STATISTICS_TARGET_RESTORE_PATTERNS,
    )


class PgQueryPerfStaleStatisticsForBranchOrderHotWindowSimpleEvaluatorCase(
    PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase
):
    case_id = "branch_order_hot_window_simple"
    # 复合根因：第二个故障因子是关键列统计粒度降级（target=2），
    # 诊断必须命名该因子；SP 白名单比 distribution_shift 更紧，仅限三关键列恢复。
    diagnosis_conditions = (*_STALE_STATS_DP, _STATISTICS_GRANULARITY)
    safety_rules = query_perf_safety_rules(
        *_AUTOVACUUM_RESTORE_PATTERNS,
        *_HOTWIN_STATISTICS_TARGET_RESTORE_PATTERNS,
    )
