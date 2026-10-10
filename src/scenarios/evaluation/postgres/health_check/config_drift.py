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

_CONFIG_DP = (
    condition("memory_resize", "host memory resized to 64gb", "memory capacity changed", critical=True),
    condition("config_drift", "postgres memory settings drift from baseline", "pending restart configuration drift", critical=True),
    condition("noise_excluded", "work_mem and max connections are not drift targets", "operational noise excluded", critical=True),
    condition("recommendation", "recommend shared buffers effective cache and maintenance work mem", "memory config plan", critical=True),
    condition("restart_plan", "shared buffers maintenance restart window", "rollback and validation plan", critical=True),
)
_CONFIG_SIMPLE_DP = (
    condition(
        "memory_resize",
        "host memory capacity increased",
        "host memory resized to 64gb",
        "stale_cache_sizing",
        "Stale Cache Sizing (Post-Resize)",
        "shared_buffers=1GB on 252GB node (0.4% of RAM)",
        "memory capacity changed",
        critical=True,
    ),
    condition(
        "config_drift",
        "postgres cache settings remain on the old baseline",
        "memory configuration drift",
        "stale_planner_cache_assumption",
        "configuration",
        "shared_buffers",
        "effective_cache_size",
        "108 GB OS page cache invisible to planner due to low effective_cache_size",
        "Underutilized OS Page Cache",
        critical=True,
        contradictions=("cache settings match the current baseline",),
    ),
)
def _has_expected_drift(rows, case):
    settings = {str(row[0]): row for row in rows}
    required = tuple(case.recommended_params)
    changed = tuple(
        name for name in required
        if str(case.recommended_params[name]).casefold() != str(case.old_baseline_params[name]).casefold()
    )
    return (
        len(rows) == len(required)
        and all(len(row) == 5 for row in rows)
        and set(settings) == set(required)
        and all(int(row[4]) == case.memory_limit_mb for row in rows)
        and bool(changed)
        and all(
            str(settings[name][1]).casefold() == str(case.old_baseline_params[name]).casefold()
            for name in required
        )
    )


_DRIFT_STATE = SqlRowsVerifier(
    "configuration_drift_present",
    lambda case: (
        "WITH live_capacity AS ("
        f"SELECT memory_mb FROM {case.ops_schema}.instance_inventory "
        "WHERE source = 'container-cgroup-live' ORDER BY observed_at DESC LIMIT 1"
        ") SELECT p.name, current_setting(p.name), p.source, p.pending_restart, c.memory_mb "
        "FROM pg_settings p CROSS JOIN live_capacity c WHERE p.name = ANY(" +
        "ARRAY[" + ",".join(f"'{name}'" for name in case.recommended_params) + "]) ORDER BY p.name"
    ),
    "64GB live capacity with three target settings still on the old baseline",
    _has_expected_drift,
)
_CONFIG_PLAN = ReportTermsVerifier("memory_configuration_plan", ("shared_buffers", "effective_cache_size", "maintenance_work_mem"))
_RESTART_PLAN = ReportTermsVerifier("restart_risk_plan", ("maintenance window", "rollback"))
_SIMPLE_CONFIG_PLAN = ReportTermsVerifier("cache_configuration_plan", ("shared_buffers", "effective_cache_size"))


class PgHealthCheckConfigDriftForMemoryResizeConfigDriftEvaluatorCase(HealthCheckEvaluator):
    scenario_id = "pg_health_check_config_drift"
    case_id = "memory_resize_config_drift"
    diagnosis_conditions = _CONFIG_DP
    outcome_verifiers = (_DRIFT_STATE, _CONFIG_PLAN, _RESTART_PLAN)


class PgHealthCheckConfigDriftForCacheBaselineDriftSimpleEvaluatorCase(HealthCheckEvaluator):
    scenario_id = "pg_health_check_config_drift"
    case_id = "cache_baseline_drift_simple"
    diagnosis_conditions = _CONFIG_SIMPLE_DP
    outcome_verifiers = (_DRIFT_STATE, _SIMPLE_CONFIG_PLAN, _RESTART_PLAN)
