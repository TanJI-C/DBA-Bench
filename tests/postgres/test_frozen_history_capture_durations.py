from src.scenarios import POSTGRES_SCENARIO_REGISTRY


FROZEN_HISTORY_SCENARIO_IDS = (
    "pg_health_check_backup_rpo_certification",
    "pg_health_check_autovacuum_sustainability",
    "pg_resource_governance_container_cpu_budget",
    "pg_resource_governance_pgbouncer_connection_budget",
    "pg_system_failure_checkpoint_archive",
    "pg_business_change_lwlock_pgbouncer_cascade",
    "pg_resource_governance_io_context_workload",
    "pg_resource_governance_partition_cleanup",
)

LEGACY_OR_CUSTOM_TELEMETRY_CASES = {
    ("pg_resource_governance_container_cpu_budget", "db_quota_throttle"),
    ("pg_resource_governance_pgbouncer_connection_budget", "pool_partition_shortage_simple"),
    ("pg_business_change_lwlock_pgbouncer_cascade", "replica_lwlock_tipping"),
    ("pg_resource_governance_io_context_workload", "report_is_pressure"),
    ("pg_resource_governance_io_context_workload", "report_is_pressure_simple"),
    ("pg_resource_governance_partition_cleanup", "filesystem_cleanup_pressure"),
    ("pg_resource_governance_partition_cleanup", "filesystem_cleanup_pressure_simple"),
}

# Contract: db_quota_throttle_simple keeps its frozen
# 180s/120s capture design. The longer normal capture is the only real source
# for its captured-benign competitors, and the shorter fault window keeps the
# quota regression from dominating the overview on its own.
FROZEN_CAPTURE_DURATION_CASES = {
    ("pg_resource_governance_container_cpu_budget", "db_quota_throttle_simple"): (180, 120),
}


def test_frozen_history_capture_durations_and_legacy_cases_are_explicit():
    registrations = {
        registration.scenario_id: registration
        for registration in POSTGRES_SCENARIO_REGISTRY
    }
    observed_legacy = set()

    for scenario_id in FROZEN_HISTORY_SCENARIO_IDS:
        for case in registrations[scenario_id].scenario.cases:
            history = case.frozen_history
            if history is None:
                observed_legacy.add((scenario_id, case.case_id))
                continue
            expected_normal, expected_fault = FROZEN_CAPTURE_DURATION_CASES.get(
                (scenario_id, case.case_id), (120, 180)
            )
            assert history.normal_capture_seconds == expected_normal
            assert history.fault_capture_seconds == expected_fault

    assert observed_legacy == LEGACY_OR_CUSTOM_TELEMETRY_CASES
