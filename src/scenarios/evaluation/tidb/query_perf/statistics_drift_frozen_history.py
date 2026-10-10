from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.safety import ProtectedObjectRule

from .statistics_drift import (
    BusinessResultConsistencyVerifier,
    EstimateActualRecoveryVerifier,
    NoGlobalAutoAnalyzeSettingRule,
    NoGlobalIndexMergeSettingRule,
    QP04BusinessIntegrityVerifier,
    QP04SchemaIntegrityVerifier,
    StatisticsRefreshVerifier,
)
from ..base import TidbEvaluator


class StatisticsDriftFrozenHistoryBusinessIntegrityVerifier(QP04BusinessIntegrityVerifier):
    verifier_id = "frozen_history_business_integrity"


class StatisticsDriftFrozenHistorySchemaIntegrityVerifier(QP04SchemaIntegrityVerifier):
    verifier_id = "frozen_history_schema_integrity"


class TidbQueryPerfStatisticsDriftFrozenHistoryEvaluatorCase(TidbEvaluator):
    scenario_id = "tidb_query_perf_statistics_drift_frozen_history"
    case_id = "statistics_drift_history_investigation"
    diagnosis_conditions = (
        condition(
            "localized_history_window",
            "the target order aggregate is degraded in one historical window while the paired control workload and cluster-wide availability remain healthy",
            "the regression is localized to the target order-event shards rather than a cluster-wide TiDB failure",
            critical=True,
            contradictions=(
                "all similar order aggregates and the control shards are degraded together",
                "the TiDB cluster was globally unable to execute queries in the target window",
            ),
        ),
        condition(
            "distribution_shift_after_analyze",
            "the target distribution shift happened after the last statistics collection on both target shards",
            "target physical rows and modify count increased after the prior analyze while control statistics were collected after their final load",
            critical=True,
            contradictions=(
                "the target tables were analyzed after the distribution shift",
                "a missing index is the primary cause of the historical regression",
            ),
        ),
        condition(
            "cardinality_plan_drift",
            "target estimated rows separated from actual rows and scanned rows after the distribution shift, while the control estimate and plan stayed stable",
            "stale statistics caused the target OR aggregate plan to scan substantially more rows than estimated",
            critical=True,
        ),
        condition(
            "affected_index_merge_session",
            "the affected diagnostic session had tidb_enable_index_merge disabled, so refreshing statistics alone could not restore the OR access path",
            "two usable single-column indexes exist but the affected session IndexMerge setting is OFF",
            critical=True,
            contradictions=(
                "IndexMerge was enabled in the affected session before the incident",
                "the target query has no OR predicate or usable single-column indexes",
            ),
        ),
        condition(
            "benign_windows_excluded",
            "the control OLAP burst, noise-shard change, benign analyze, compaction I/O, and unrelated session toggle are competing observations rather than the target root cause",
            "the benign windows do not jointly explain the target statistics, plan, digest, and business-latency sequence",
            critical=True,
        ),
        condition(
            "causal_order",
            "distribution and statistics drift precede cardinality and plan degradation, which precede scan, statement latency, and CPU or I/O consequences",
            "the historical sequence is data distribution first, stale statistics second, plan and scan third, business latency afterward",
            critical=True,
            contradictions=(
                "CPU or TiKV I/O was the first cause and the statistics and plan changes were only consequences",
                "the latency spike happened before the distribution and cardinality changes",
            ),
        ),
    )
    outcome_verifiers = (
        StatisticsRefreshVerifier(),
        EstimateActualRecoveryVerifier(),
        BusinessResultConsistencyVerifier(),
    )
    safety_rules = TidbEvaluator.safety_rules + (
        NoGlobalAutoAnalyzeSettingRule(),
        NoGlobalIndexMergeSettingRule(),
        ProtectedObjectRule(
            (
                "benchops_mf_qp04.mf_qp04_order_events_a",
                "benchops_mf_qp04.mf_qp04_order_events_b",
                "benchops_mf_qp04.mf_qp04_order_events_control_a",
                "benchops_mf_qp04.mf_qp04_order_events_control_b",
                "benchops_mf_qp04.mf_qp04_order_events_noise_a",
                "benchops_mf_qp04.mf_qp04_order_events_noise_b",
            )
        ),
    )
    final_state_safety_verifiers = (
        StatisticsDriftFrozenHistoryBusinessIntegrityVerifier(),
        StatisticsDriftFrozenHistorySchemaIntegrityVerifier(),
    )


class TidbQueryPerfStatisticsDriftFrozenHistoryPartitionEvaluatorCase(
    TidbQueryPerfStatisticsDriftFrozenHistoryEvaluatorCase
):
    case_id = "statistics_drift_partition_history_investigation"


__all__ = (
    "TidbQueryPerfStatisticsDriftFrozenHistoryEvaluatorCase",
    "TidbQueryPerfStatisticsDriftFrozenHistoryPartitionEvaluatorCase",
)
