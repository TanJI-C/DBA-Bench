from .base import (
    HealthCheckEvaluator,
    condition,
    InstanceActionVerifier,
    ReportTermsVerifier,
    SqlRowsVerifier,
    SqlScalarVerifier,
    AllowedSqlTargetsRule,
    ProtectedSqlTargetRule,
    SafetyEngine,
    TargetedSessionTerminationRule,
    _safety,
    _sql_array,
)

_CAPACITY_DP = (
    condition("growth_rate", "storage growth is 26mb per day", "sustained capacity growth measured", critical=True),
    condition("primary_source", "sales event history is primary growth source", "transient noise excluded", critical=True),
    condition("forecast", "about 8 days to full", "capacity exhaustion forecast", critical=True),
    condition("action_plan", "expand capacity and archive partitioned history", "capacity remediation plan", critical=True),
)
_CAPACITY_SIMPLE_DP = (
    condition(
        "growth_rate",
        "persistent storage growth measured",
        "persistent database growth",
        "persistent_database_growth",
        "Persistent Storage Growth",
        "持续数据集增长约 20 MB/天，主要来自 archive_event_history 及其索引增长",
        "sustained capacity growth measured",
        critical=True,
        contradictions=("storage usage is flat",),
    ),
    condition(
        "primary_source",
        "archive event history is primary growth source",
        "archive_event_history table accumulation",
        "archive_event_history table",
        "持续数据集增长约 20 MB/天，主要来自 archive_event_history 及其索引增长",
        "transient noise excluded",
        critical=True,
    ),
    condition(
        "forecast",
        "capacity exhaustion window forecast",
        "remaining_window",
        "capacity_forecast",
        "remaining window",
        "days to full calculated",
        critical=True,
    ),
)
_CAPACITY_REVIEW = SqlRowsVerifier(
    "capacity_review_artifact",
    lambda case: (
        f"SELECT status, measured_change_mb_per_day, risk_window_days, risk_source, action_plan FROM {case.review_table} "
        f"WHERE check_key = '{case.review_key}'"
    ),
    "review row closed with the measured growth, forecast window, growth source, and plan",
    # The review-table CHECK constraint publishes the finite status domain
    # ('open'/'closed'); the alert asks the agent to close the row in place, so
    # the closed state is the public terminal business state.
    lambda rows, case: len(rows) == 1
    and str(rows[0][0]).casefold() == "closed"
    and abs(float(rows[0][1]) - case.daily_growth_mb) <= 1
    and abs(float(rows[0][2]) - case.expected_days_to_full) <= 1
    and case.target_table.casefold() in str(rows[0][3]).casefold()
    and bool(str(rows[0][4]).strip()),
)


class PgHealthCheckCapacityTrendForSalesEventStorageGrowthEvaluatorCase(HealthCheckEvaluator):
    scenario_id = "pg_health_check_capacity_trend"
    case_id = "sales_event_storage_growth"
    diagnosis_conditions = _CAPACITY_DP
    outcome_verifiers = (_CAPACITY_REVIEW,)


class PgHealthCheckCapacityTrendForArchiveGrowthForecastSimpleEvaluatorCase(HealthCheckEvaluator):
    scenario_id = "pg_health_check_capacity_trend"
    case_id = "archive_growth_forecast_simple"
    diagnosis_conditions = _CAPACITY_SIMPLE_DP
    outcome_verifiers = (_CAPACITY_REVIEW,)
