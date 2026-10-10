from .base import (
    HealthCheckEvaluator,
    condition,
    InstanceActionVerifier,
    SqlRowsVerifier,
    SqlScalarVerifier,
    AllowedSqlTargetsRule,
    ProtectedSqlTargetRule,
    SafetyEngine,
    TargetedSessionTerminationRule,
    _safety,
    _sql_array,
)

_BLOAT_DP = (
    condition("bloat_measurement", "target table and index bloat measured", "store returns bloat exceeds noise", critical=True),
    condition("target_relation", "store returns is the true bloat target", "noise tables excluded", critical=True),
)
_BLOAT_SIMPLE_DP = (
    condition(
        "bloat_measurement",
        "store returns dead tuples and index growth measured",
        "target bloat measured",
        "dead_tuple_bloat",
        "storage_bloat",
        "dead_tuples_accumulation",
        "store_returns表有287,514个活元组和12,000个死元组",
        "死元组数量和比例显著高于其他候选关系，需要清理并刷新统计信息。",
        critical=True,
        contradictions=("store returns has no bloat",),
    ),
    condition(
        "target_relation",
        "store returns exceeds the comparison table",
        "noise table excluded",
        "public.store_returns",
        "store_returns",
        "store_returns is the true bloat target",
        "受影响表大小适中，适合在维护窗口执行普通 VACUUM；不需要对最大表或全库做维护。",
        critical=True,
    ),
)
_BLOAT_LOW = SqlScalarVerifier(
    "dead_tuples_cleaned", lambda case: f"SELECT COALESCE(n_dead_tup, 0) FROM pg_stat_user_tables WHERE relname = '{case.target_table}'",
    "below one injection batch", lambda actual, case: int(actual) < case.batch_size,
)
_INDEX_VALID = SqlScalarVerifier(
    "target_index_valid", lambda case: f"SELECT count(*) FROM pg_index i JOIN pg_class c ON c.oid=i.indexrelid WHERE c.relname='{case.index_name}' AND i.indisvalid",
    1, lambda actual, case: int(actual) == 1,
)


class PgHealthCheckTableBloatForStoreReturnsTableIndexBloatEvaluatorCase(HealthCheckEvaluator):
    scenario_id = "pg_health_check_table_bloat"
    case_id = "store_returns_table_index_bloat"
    diagnosis_conditions = _BLOAT_DP
    outcome_verifiers = (_BLOAT_LOW, _INDEX_VALID)


class PgHealthCheckTableBloatForStoreReturnsBloatSimpleEvaluatorCase(HealthCheckEvaluator):
    scenario_id = "pg_health_check_table_bloat"
    case_id = "store_returns_bloat_simple"
    diagnosis_conditions = _BLOAT_SIMPLE_DP
    outcome_verifiers = (_BLOAT_LOW, _INDEX_VALID)
