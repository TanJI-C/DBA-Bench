"""Make `pytest tests/` work from a clean clone without an editable install.

Imports of the `src` and `scripts` packages resolve against this checkout
regardless of the working directory or site-packages editable finders (which,
in linked-worktree setups, may point at a different checkout).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# TPC-DS query text is not redistributable; users fetch it from tpc.org into
# data/workloads/tpcds/queries/ (see docs/getting-started.md). Scenario modules
# parse those queries at import time, so the test modules below cannot even be
# collected until the queries exist. Keep the list in sync when adding a
# TPC-DS-backed test module.
_TPCDS_FIRST_QUERY = ROOT / "data" / "workloads" / "tpcds" / "queries" / "query_0.sql"
_TPCDS_BACKED_TESTS = frozenset(
    """
    tests/benchmark/test_persistent_scenario_adapter.py
    tests/benchmark/test_runner.py
    tests/contracts/test_system_contracts.py
    tests/persistent_scenarios/test_pg5_warehouse_reporting.py
    tests/persistent_scenarios/test_pg5_workload_wiring.py
    tests/postgres/test_alert_causality_evaluators.py
    tests/postgres/test_audit_logging_contract.py
    tests/postgres/test_business_change_invalid_index.py
    tests/postgres/test_business_change_simplified_cases.py
    tests/postgres/test_cache_pollution_evaluators.py
    tests/postgres/test_checkpoint_archive_scenario.py
    tests/postgres/test_connection_bloat_hardening.py
    tests/postgres/test_container_cpu_budget.py
    tests/postgres/test_evaluator_followup_regressions.py
    tests/postgres/test_fault_activation_contracts.py
    tests/postgres/test_fault_install_runtime.py
    tests/postgres/test_fault_injector_runtime_cleanup.py
    tests/postgres/test_fk_validation_scenario.py
    tests/postgres/test_frozen_history_capture_durations.py
    tests/postgres/test_health_check_autovacuum_sustainability.py
    tests/postgres/test_health_check_backup_rpo_certification.py
    tests/postgres/test_health_check_evaluators.py
    tests/postgres/test_heavy_offset_injector.py
    tests/postgres/test_heavy_offset_simplified_case.py
    tests/postgres/test_io_context_workload.py
    tests/postgres/test_lock_contention_hard_case.py
    tests/postgres/test_lwlock_pgbouncer_cascade.py
    tests/postgres/test_multi_cause_evaluators.py
    tests/postgres/test_partition_cleanup.py
    tests/postgres/test_partition_cleanup_telemetry.py
    tests/postgres/test_partition_migration_scenario.py
    tests/postgres/test_pgbouncer_connection_budget.py
    tests/postgres/test_pg_continuous_ops_migration.py
    tests/postgres/test_pg_frozen_history_rg1.py
    tests/postgres/test_pg_query_perf_missing_index_injector.py
    tests/postgres/test_query_perf_evaluators.py
    tests/postgres/test_query_perf_observability_contracts.py
    tests/postgres/test_remaining_evaluators.py
    tests/postgres/test_resource_governance_lifecycle.py
    tests/postgres/test_scenario_environment_lifecycle.py
    tests/postgres/test_system_failure_evaluators.py
    tests/postgres/test_system_failure_noisy_neighbor_hardening.py
    tests/postgres/test_wal_checkpoint_storm_workload_profiles.py
    tests/test_case_attributes_consistency.py
    tests/test_cli_persistent_scenario_gate_resources.py
    tests/test_evaluator_layout.py
    tests/test_evaluator_protocol.py
    tests/test_pg_full_reference_report.py
    tests/test_remote_agent_commands.py
    tests/test_runner_port_rebase.py
    tests/test_scenario_cases.py
    tests/test_semantic_diagnosis.py
    tests/test_trusted_outcomes.py
    tests/test_workload_runner_scheduling.py
    tests/tidb/test_business_change_timezone_ddl_backpressure_frozen_history.py
    tests/tidb/test_business_change_timezone_ddl_backpressure.py
    tests/tidb/test_case_when_in_cartesian_semi_join.py
    tests/tidb/test_clustered_index_consistency.py
    tests/tidb/test_deadlock_scenario.py
    tests/tidb/test_gc_mvcc_recovery.py
    tests/tidb/test_health_check_backup_recoverability.py
    tests/tidb/test_health_check_empty_region_leader_skew_frozen_history.py
    tests/tidb/test_health_check_empty_region_leader_skew.py
    tests/tidb/test_health_check_gc_safepoint_pin.py
    tests/tidb/test_health_check_lightning_preflight.py
    tests/tidb/test_health_check_ticdc_replication_trend_frozen_history.py
    tests/tidb/test_health_check_ticdc_replication_trend.py
    tests/tidb/test_like_escape_range.py
    tests/tidb/test_lock_contention_evaluator.py
    tests/tidb/test_pd_total_metadata_loss_recovery.py
    tests/tidb/test_qp05_noncovering_index_tail_latency.py
    tests/tidb/test_reclassified_alert_case_expansion.py
    tests/tidb/test_resource_governance_br_slo_frozen_history.py
    tests/tidb/test_resource_governance_connection_balancing.py
    tests/tidb/test_resource_governance_empty_region_merge_budget.py
    tests/tidb/test_resource_governance_lightning_budget_frozen_history.py
    tests/tidb/test_resource_governance_placement_policy.py
    tests/tidb/test_resource_governance.py
    tests/tidb/test_resource_governance_rg01.py
    tests/tidb/test_resource_governance_ru_budget_calibration_frozen_history.py
    tests/tidb/test_sf01_pd_metadata_recovery.py
    tests/tidb/test_sf02_slow_store_lock_ttl.py
    tests/tidb/test_statistics_drift_frozen_history.py
    tests/tidb/test_statistics_drift.py
    tests/tidb/test_system_failure_case_expansion.py
    tests/tidb/test_system_failure_simplified_cases.py
    tests/tidb/test_system_failure_ticdc_gc_safepoint.py
    tests/tidb/test_workload_runner_database_hooks.py
    """.split()
)


def pytest_ignore_collect(collection_path, config):
    if _TPCDS_FIRST_QUERY.exists():
        return None
    return collection_path.resolve().relative_to(ROOT).as_posix() in _TPCDS_BACKED_TESTS
