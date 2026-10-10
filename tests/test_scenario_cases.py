import ast
from collections import Counter
import re
import runpy
import inspect
import textwrap
from pathlib import Path

import pytest

from src.scenarios import ALL_SCENARIOS, POSTGRES_SCENARIO_REGISTRY, SCENARIO_REGISTRY, ScenarioCategory
from src.scenarios.base import (
    EMPTY_BACKGROUND_WORKLOAD,
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    FaultPlan,
)
from src.scenarios.faults import BaseFaultInjector


def test_initial_migration_has_one_case_per_scenario():
    assert len(ALL_SCENARIOS) == 117
    assert len({scenario.scenario_id for scenario in ALL_SCENARIOS}) == 117
    for scenario in ALL_SCENARIOS:
        assert re.fullmatch(r"[a-z][a-z0-9_]*", scenario.scenario_id)
        assert len(scenario.cases) >= 1, scenario.scenario_id


def test_postgres_registry_uses_five_task_categories():
    task_registrations = tuple(
        registration
        for registration in POSTGRES_SCENARIO_REGISTRY
        if registration.category is not ScenarioCategory.BASIC
    )
    assert Counter(registration.category for registration in task_registrations) == {
        ScenarioCategory.QUERY_PERF: 9,
        ScenarioCategory.SYSTEM_FAILURE: 16,
        ScenarioCategory.HEALTH_CHECK: 9,
        ScenarioCategory.BUSINESS_CHANGE: 8,
        ScenarioCategory.RESOURCE_GOVERNANCE: 9,
    }
    assert Counter(
        registration.category
        for registration in task_registrations
        for _case in registration.scenario.cases
    ) == {
        ScenarioCategory.QUERY_PERF: 19,
        ScenarioCategory.SYSTEM_FAILURE: 33,
        ScenarioCategory.HEALTH_CHECK: 21,
        ScenarioCategory.BUSINESS_CHANGE: 16,
        ScenarioCategory.RESOURCE_GOVERNANCE: 18,
    }


def test_case_contract_and_fault_plans_are_explicit():
    for scenario in ALL_SCENARIOS:
        for case in scenario.cases:
            assert re.fullmatch(r"[a-z][a-z0-9_]*", case.case_id)
            assert scenario.get_case(case.case_id) is case
            assert isinstance(case.background_workload, BackgroundWorkloadSpec)
            plans = scenario.build_fault_plan(case)
            assert plans and all(isinstance(plan, FaultPlan) for plan in plans)


def test_multi_cause_background_workloads_preserve_scenario_semantics():
    scenarios = {scenario.scenario_id: scenario for scenario in ALL_SCENARIOS}
    connection_bloat = scenarios["pg_system_failure_connection_bloat"].cases[0]
    stale_stats_lock = scenarios["pg_query_perf_stale_stats_lock_contention"].cases[0]
    wal_checkpoint = scenarios["pg_system_failure_wal_checkpoint_storm"].cases[0]

    assert connection_bloat.background_workload.worker_count == 1
    assert connection_bloat.background_workload.profiles
    assert stale_stats_lock.background_workload is EMPTY_BACKGROUND_WORKLOAD
    assert wal_checkpoint.background_workload.worker_count == 6
    assert wal_checkpoint.background_workload.profiles


def test_resource_governance_simple_cases_reduce_scope_without_removing_noise():
    scenarios = {scenario.scenario_id: scenario for scenario in ALL_SCENARIOS}
    resource_ids = (
        "pg_resource_governance_data_archiving",
        "pg_resource_governance_resource_throttling",
        "pg_resource_governance_audit_logging",
        "pg_resource_governance_privilege_masking",
        "pg_resource_governance_host_backup",
        "pg_resource_governance_container_cpu_budget",
    )
    for scenario_id in resource_ids:
        scenario = scenarios[scenario_id]
        assert len(scenario.cases) == 2
        assert scenario.cases[1].case_no == 1

    archive = scenarios["pg_resource_governance_data_archiving"]
    assert archive.cases[1].cold_rows < archive.cases[0].cold_rows
    assert archive.cases[1].background_workload.worker_count == 1
    assert archive.cases[1].background_workload.profiles

    throttle = scenarios["pg_resource_governance_resource_throttling"]
    assert len(throttle.cases[1].noise_roles) < len(throttle.cases[0].noise_roles)
    # single_report_role_limit_simple is Hard: the case-1 workload
    # keeps the full same-domain noise scope instead of a reduced simple scope.
    assert throttle.cases[1].background_workload.worker_count == 4

    audit = scenarios["pg_resource_governance_audit_logging"]
    assert audit.cases[1].worker_count < audit.cases[0].worker_count
    assert audit.cases[1].table != audit.cases[0].table

    masking = scenarios["pg_resource_governance_privilege_masking"]
    assert masking.cases[1].dev_role != masking.cases[0].dev_role
    # customer_support_masking_simple is Hard: the case-1 workload
    # keeps the full same-domain noise scope instead of a reduced simple scope.
    assert masking.cases[1].background_workload.worker_count == 2
    assert len(masking.cases[1].background_workload.profiles) == 6

    host_backup = scenarios["pg_resource_governance_host_backup"]
    assert host_backup.cases[0].case_id == "nightly_backup_read_saturation"
    assert host_backup.cases[1].case_id == "single_backup_reader_simple"
    assert host_backup.cases[1].row_count < host_backup.cases[0].row_count
    assert len(host_backup.cases[1].report_app_names) < len(host_backup.cases[0].report_app_names)

    cpu_budget = scenarios["pg_resource_governance_container_cpu_budget"]
    assert [case.case_no for case in cpu_budget.cases] == [0, 1]
    assert cpu_budget.cases[0].case_id == "db_quota_throttle"
    assert cpu_budget.cases[1].case_id == "db_quota_throttle_simple"
    assert len(cpu_budget.cases[0].sibling_jobs) > len(cpu_budget.cases[1].sibling_jobs)


def test_multi_cause_simple_cases_reduce_scope_without_flattening_chain():
    scenarios = {scenario.scenario_id: scenario for scenario in ALL_SCENARIOS}
    connection = scenarios["pg_system_failure_connection_bloat"]
    stale_lock = scenarios["pg_query_perf_stale_stats_lock_contention"]
    wal_checkpoint = scenarios["pg_system_failure_wal_checkpoint_storm"]

    for scenario in (connection, stale_lock, wal_checkpoint):
        assert len(scenario.cases) == 2
        assert scenario.cases[1].case_no == 1

    assert connection.cases[1].worker_connections < connection.cases[0].worker_connections
    assert len(connection.cases[1].distractor_app_names) < len(connection.cases[0].distractor_app_names)
    assert connection.cases[1].dead_tuple_threshold > 0

    assert stale_lock.cases[1].waiter_count < stale_lock.cases[0].waiter_count
    assert stale_lock.cases[1].initial_orders < stale_lock.cases[0].initial_orders
    assert stale_lock.cases[1].stale_orders < stale_lock.cases[0].stale_orders

    assert wal_checkpoint.cases[1].slot_name != wal_checkpoint.cases[1].active_slot_name
    assert wal_checkpoint.cases[1].background_workload.worker_count < wal_checkpoint.cases[0].background_workload.worker_count


def test_deadlock_simple_case_reduces_recurrence_and_noise_without_removing_it():
    scenario = next(
        item for item in ALL_SCENARIOS
        if item.scenario_id == "pg_system_failure_deadlock"
    )
    original = scenario.get_case("checkout_order_deadlock")
    simple = scenario.get_case("single_order_pair_deadlock_simple")
    config = scenario.build_fault_plan(simple)[0].config

    assert simple.case_no == 1
    assert simple.trigger_rounds < original.trigger_rounds
    assert simple.business_noise_repeats < original.business_noise_repeats
    assert simple.timeout_noise_count < original.timeout_noise_count
    assert simple.background_workload.worker_count == 1
    assert len(simple.background_workload.profiles) == 1
    assert config["trigger_rounds"] == 1
    assert config["business_noise_repeats"] == 1
    # 调度层控制面仅 checkout 配置；同域噪声扩展（staged 健康 job 对、第二条
    # 良性等待链、池会话、8+8 RAISE 噪声）两 case 共有。
    assert original.plan_sync_registry_table == "plan_sync_job_registry"
    assert simple.plan_sync_registry_table is None
    assert "plan_sync_registry_table" not in config
    assert original.extra_job_pairs == simple.extra_job_pairs != ()
    assert original.decoy2_holder_app == simple.decoy2_holder_app
    assert config["decoy2_table"] == simple.decoy2_table
    assert original.idle_pool_apps and (
        sum(count for _name, count in simple.idle_pool_apps)
        < sum(count for _name, count in original.idle_pool_apps)
    )
    assert simple.log_noise_per_repeat == original.log_noise_per_repeat == 8
    assert simple.warning_noise_per_repeat == original.warning_noise_per_repeat == 8


def test_connection_storm_simple_case_reduces_pool_and_noise_scope():
    scenario = next(
        item for item in ALL_SCENARIOS
        if item.scenario_id == "pg_system_failure_connection_storm"
    )
    original = scenario.get_case("checkout_pool_idle_transaction_storm")
    simple = scenario.get_case("checkout_pool_leak_simple")
    config = scenario.build_fault_plan(simple)[0].config

    assert simple.case_no == 1
    assert simple.max_connections < original.max_connections
    assert simple.idle_in_xact_connections < original.idle_in_xact_connections
    assert simple.noise_idle_connections < original.noise_idle_connections
    assert len(simple.mixed_business_idle_apps) < len(original.mixed_business_idle_apps)
    assert simple.background_workload.worker_count == 1
    assert len(simple.background_workload.profiles) == 1
    assert config["reporting_idle_connections"] == simple.reporting_idle_connections


def test_auto_analyze_simple_case_reduces_tables_workers_and_noise():
    scenario = next(
        item for item in ALL_SCENARIOS
        if item.scenario_id == "pg_system_failure_auto_analyze_storm"
    )
    original = scenario.get_case("sales_tables_auto_analyze_storm")
    simple = scenario.get_case("store_sales_auto_analyze_storm_simple")
    config = scenario.build_fault_plan(simple)[0].config
    original_config = scenario.build_fault_plan(original)[0].config

    assert simple.case_no == 1
    assert len(simple.tables) < len(original.tables)
    assert len(simple.noise_tables) < len(original.noise_tables)
    assert simple.background_workload.worker_count == 1
    assert len(simple.background_workload.profiles) == 2
    assert config["tables"] == ("store_sales",)
    assert config["noise_tables"] == ("store_returns",)
    assert config["table_reloptions"] == (
        (
            "store_returns",
            (
                ("autovacuum_analyze_scale_factor", "0.0001"),
                ("autovacuum_analyze_threshold", "5"),
            ),
        ),
    )
    assert config["protected_reloptions"] == (
        (
            "inventory",
            (
                ("autovacuum_analyze_scale_factor", "0.0001"),
                ("autovacuum_analyze_threshold", "300"),
            ),
        ),
    )
    assert original_config["table_reloptions"] == (
        (
            "web_sales",
            (
                ("autovacuum_analyze_scale_factor", "0.0001"),
                ("autovacuum_analyze_threshold", "5"),
            ),
        ),
    )
    assert original_config["protected_reloptions"] == (
        (
            "inventory",
            (
                ("autovacuum_analyze_scale_factor", "0.0001"),
                ("autovacuum_analyze_threshold", "300"),
            ),
        ),
        (
            "customer_demographics",
            (
                ("autovacuum_analyze_scale_factor", "0.0006"),
                ("autovacuum_analyze_threshold", "100"),
            ),
        ),
        (
            "store_returns",
            (
                ("autovacuum_analyze_scale_factor", "0.005"),
                ("autovacuum_analyze_threshold", "150"),
            ),
        ),
    )
    assert config["require_completed_autoanalyze"] is True
    assert config["completion_timeout_seconds"] == 90


def test_health_check_cases_preserve_scenario_environment_semantics():
    scenarios = {scenario.scenario_id: scenario for scenario in ALL_SCENARIOS}
    health_check_ids = (
        "pg_health_check_backup_recoverability",
        "pg_health_check_capacity_trend",
        "pg_health_check_config_drift",
        "pg_health_check_long_running_tx",
        "pg_health_check_sequence_exhaustion",
        "pg_health_check_table_bloat",
        "pg_health_check_unused_indexes",
    )
    for scenario_id in health_check_ids:
        assert scenarios[scenario_id].cases[0].background_workload is EMPTY_BACKGROUND_WORKLOAD

    initialized_image_ids = (
        "pg_health_check_backup_recoverability",
        "pg_health_check_capacity_trend",
        "pg_health_check_config_drift",
        "pg_health_check_sequence_exhaustion",
    )
    for scenario_id in initialized_image_ids:
        case = scenarios[scenario_id].cases[0]
        assert case.base_image_name == "aiopsbench-pg-initialized:latest"
        assert case.workload_tag == "initialized"


def test_alert_causality_cases_preserve_fault_strength_and_workloads():
    scenarios = {scenario.scenario_id: scenario for scenario in ALL_SCENARIOS}
    cache = scenarios["pg_query_perf_cache_pollution"]
    cpu_lock = scenarios["pg_system_failure_cpu_lock_spin"]
    io_saturation = scenarios["pg_business_change_io_saturation"]

    assert len(cache.cases) == 3
    assert len(cpu_lock.cases) == 3
    assert len(io_saturation.cases) == 3
    assert cache.cases[0].background_workload is EMPTY_BACKGROUND_WORKLOAD
    assert "without blindly increasing memory" in cache.cases[0].alert
    assert cache.cases[1].case_id == "billing_export_scan_cache_churn"
    assert cache.cases[1].scan_app_name == "billing_export_scan"
    assert cpu_lock.cases[0].background_workload is EMPTY_BACKGROUND_WORKLOAD
    assert cpu_lock.cases[1].case_id == "checkout_retry_lock_blocker_simple"
    assert cpu_lock.cases[1].waiter_count < cpu_lock.cases[0].waiter_count
    assert 0 < cpu_lock.cases[1].decoy_waiter_count < cpu_lock.cases[0].decoy_waiter_count
    assert 0 < cpu_lock.cases[1].decoy_spinner_count < cpu_lock.cases[0].decoy_spinner_count
    advisory_cpu = cpu_lock.cases[2]
    assert advisory_cpu.case_id == "advisory_lock_retry_cpu_storm"
    assert advisory_cpu.fault_variant == "advisory_lock_spin"
    assert advisory_cpu.advisory_lock_key != advisory_cpu.decoy_advisory_lock_key

    io_case = io_saturation.cases[0]
    assert io_case.background_workload.worker_count == 6
    assert io_case.background_workload.seed == 0
    io_config = io_saturation.build_fault_plan(io_case)[0].config
    assert io_config["maintenance_worker_count"] == 1
    assert io_config["startup_timeout_seconds"] == 10.0
    assert io_config["minimum_io_mb_per_sec"] == 20.0
    assert io_config["io_observability_timeout_seconds"] == 120.0
    assert io_case.worker_entry_function == "run_batch_cycle"
    assert io_case.worker_task_name == "metric_flush"
    assert io_config["worker_entry_function"] == "run_batch_cycle"
    assert io_config["worker_task_name"] == "metric_flush"
    assert io_config["decoy_workers"] == (("etl-worker-12", "inventory_sync"), ("etl-worker-13", "archive_tick"))
    assert io_case.preserved_job_names == ("nightly_archive_check", "inventory_sync_worker", "archive_tick_worker")
    assert io_case.culprit_job_name not in io_case.preserved_job_names
    assert io_case.disabled_job_name not in io_case.preserved_job_names
    simple_io = io_saturation.cases[1]
    assert simple_io.case_id == "vacuum_report_io_victim_simple"
    assert simple_io.background_workload.worker_count == 2
    assert len(simple_io.background_workload.profiles) == 2
    assert simple_io.minimum_io_mb_per_sec < io_case.minimum_io_mb_per_sec
    assert len(simple_io.slow_queries_2) == 2
    assert simple_io.scheduler_app_name == "ops-batch-scheduler-02"
    assert simple_io.schedule_table == "ops_batch_job_schedule"
    assert simple_io.culprit_job_name == "ops_maintenance_vacuum"
    assert simple_io.healthy_job_name == "nightly_archive_check"
    assert simple_io.report_role_name == "report_reader"
    assert simple_io.bi_role_name == "bi_viewer"
    assert simple_io.database_work_mem == "64MB"
    simple_io_config = io_saturation.build_fault_plan(simple_io)[0].config
    assert simple_io_config["scheduler_app_name"] == "ops-batch-scheduler-02"
    assert simple_io_config["bi_role_work_mem"] == "32MB"
    assert simple_io_config["report_work_mem_floor"] == "8MB"
    wal_io = io_saturation.cases[2]
    assert wal_io.case_id == "archive_backlog_io_pressure"
    assert wal_io.fault_variant == "wal_archive_backlog"
    assert wal_io.wal_slot_name == "billing_archive_stalled"
    assert wal_io.healthy_slot_name == "orders_reporting_healthy"

    long_tx_cache = cache.cases[2]
    assert long_tx_cache.case_id == "analytics_cursor_cache_churn"
    assert long_tx_cache.fault_variant == "long_tx_cache_churn"
    assert long_tx_cache.dead_tuple_threshold > 0


def test_alert_causality_entries_preserve_mode_contracts():
    examples = Path("examples")
    cache_source = (examples / "run_pg_query_perf_cache_pollution_scenario.py").read_text()
    cpu_source = (examples / "run_pg_system_failure_cpu_lock_spin_scenario.py").read_text()
    io_source = (examples / "run_pg_business_change_io_saturation_scenario.py").read_text()

    assert "pg_terminate_backend" in cache_source
    assert "pg_cancel_backend" not in cache_source
    assert 'container_prefix = f"{args.container_name}-{case.case_id}"' in cache_source
    assert 'max_turns = {"mock": 10, "zero": 3, "llm": args.max_turns}[mode]' in cpu_source
    assert 'default=20' in cpu_source
    assert 'max_turns = {"mock": 10, "zero": 3, "llm": args.max_turns}[mode]' in io_source
    assert 'default=30' in io_source
    for source in (cpu_source, io_source):
        assert 'f"{args.container_name}-{case.case_id}-{mode}"' in source


def test_query_performance_cases_preserve_baseline_resources_and_workloads():
    scenarios = {scenario.scenario_id: scenario for scenario in ALL_SCENARIOS}
    no_workload_ids = (
        "pg_query_perf_heavy_offset_pagination",
        "pg_query_perf_implicit_type_conversion",
        "pg_query_perf_parameter_sniffing",
        "pg_query_perf_sort_spill",
        "pg_query_perf_stale_statistics",
        "pg_query_perf_suboptimal_join",
    )
    for scenario_id in no_workload_ids:
        assert scenarios[scenario_id].cases[0].background_workload is EMPTY_BACKGROUND_WORKLOAD

    implicit = scenarios["pg_query_perf_implicit_type_conversion"].cases[0]
    parameter = scenarios["pg_query_perf_parameter_sniffing"].cases[0]
    stale = scenarios["pg_query_perf_stale_statistics"].cases[0]
    suboptimal = scenarios["pg_query_perf_suboptimal_join"].cases[0]
    assert implicit.deployment_memory_mb == 512
    assert parameter.deployment_memory_mb == 512
    assert (stale.deployment_cpus, stale.deployment_memory_mb, stale.deployment_shm_size) == (
        0.5,
        256,
        "128m",
    )
    assert (suboptimal.deployment_memory_mb, suboptimal.deployment_shm_size) == (256, "128m")
    suboptimal_simple = scenarios["pg_query_perf_suboptimal_join"].get_case(
        "daily_account_summary_planner_drift"
    )
    assert suboptimal_simple.case_no == 1
    assert suboptimal_simple.evaluator.__name__.endswith("DailyAccountSummaryEvaluatorCase")
    assert suboptimal_simple.fault_fingerprint_sql.count("JOIN") == 1
    assert suboptimal_simple.background_workload is EMPTY_BACKGROUND_WORKLOAD

    missing = scenarios["pg_query_perf_missing_index"].cases[0]
    assert missing.background_workload.worker_count == 6
    assert (
        missing.background_workload.start_phase
        is BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY
    )
    missing_simple = scenarios["pg_query_perf_missing_index"].get_case(
        "product_category_prefix_simple"
    )
    assert missing_simple.alert.startswith(
        "Alert: postgres-primary-1 reporting API response time has spiked"
    )
    assert missing_simple.alert.endswith(
        "Hint: focus on access paths — the query plan changed recently."
    )
    leaked_root_cause_terms = (
        "unsupported access path",
        "non-sargable",
        "expression index",
        "functional index",
        "missing index",
    )
    assert not any(
        term in missing_simple.alert.casefold()
        for term in leaked_root_cause_terms
    )

    sort = scenarios["pg_query_perf_sort_spill"]
    assert sort.cases[0].deployment_memory_mb == 768
    assert sort.cases[0].max_safe_work_mem == "256MB"
    sort_config = sort.build_fault_plan(sort.cases[0])[0].config
    assert sort_config["start_fingerprint_probe"] is False
    assert sort_config["recommended_work_mem"] == "256MB"
    sort_simple = sort.get_case("branch_order_sort_spill_simple")
    assert sort_simple.case_no == 1
    assert sort_simple.background_workload is EMPTY_BACKGROUND_WORKLOAD
    assert "work_mem" not in sort_simple.alert.casefold()


def test_resource_governance_cases_preserve_workload_and_environment_semantics():
    scenarios = {scenario.scenario_id: scenario for scenario in ALL_SCENARIOS}
    expected_workloads = {
        "pg_resource_governance_audit_logging": (2, 0, BackgroundWorkloadStartPhase.AFTER_FAULTS, 4),
        "pg_resource_governance_data_archiving": (2, 0, BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY, 3),
        "pg_resource_governance_privilege_masking": (2, 0, BackgroundWorkloadStartPhase.AFTER_FAULTS, 4),
        "pg_resource_governance_resource_throttling": (2, 0, BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY, 4),
    }
    for scenario_id, expected in expected_workloads.items():
        workload = scenarios[scenario_id].cases[0].background_workload
        assert (
            workload.worker_count,
            workload.seed,
            workload.start_phase,
            workload.warmup_seconds,
        ) == expected

    archiving = scenarios["pg_resource_governance_data_archiving"].cases[0]
    assert "一年以前冷数据" in archiving.alert
    for scenario_id in expected_workloads:
        case = scenarios[scenario_id].cases[0]
        assert case.base_image_name == "aiopsbench-pg-initialized:latest"
        assert case.workload_tag == "initialized"

    lightning = scenarios["tidb_resource_governance_lightning_budget"].cases[0]
    assert lightning.background_workload.worker_count == 6
    assert lightning.background_workload.start_phase is BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY
    assert lightning.row_count == 600000
    assert lightning.source_file_count == 6

    resource_governance_cases = [
        case
        for scenario in ALL_SCENARIOS
        if scenario.scenario_id.startswith("tidb_resource_governance_")
        for case in scenario.cases
    ]
    assert len(resource_governance_cases) == 23


def test_system_failure_cases_preserve_workload_lifecycle_semantics():
    scenarios = {scenario.scenario_id: scenario for scenario in ALL_SCENARIOS}
    no_workload_ids = (
        "pg_system_failure_connection_storm",
        "pg_system_failure_lock_contention",
        "pg_system_failure_noisy_neighbor",
        "pg_system_failure_oom",
        "pg_system_failure_temp_file_explosion",
        "pg_system_failure_wal_accumulation",
        "pg_system_failure_xid_wraparound",
    )
    for scenario_id in no_workload_ids:
        assert scenarios[scenario_id].cases[0].background_workload is EMPTY_BACKGROUND_WORKLOAD

    page_corruption = scenarios["pg_system_failure_page_corruption"]
    order_line_page = page_corruption.cases[0]
    assert order_line_page.case_id == "order_line_audit_page_corruption"
    assert order_line_page.background_workload.worker_count == 1
    assert len(order_line_page.background_workload.profiles) == 3

    lock_contention = scenarios["pg_system_failure_lock_contention"]
    simple_lock = lock_contention.get_case("customer_profile_lock_queue_simple")
    assert len(lock_contention.cases) == 2
    assert simple_lock.case_no == 1
    assert simple_lock.background_workload.worker_count == 1
    assert len(simple_lock.background_workload.profiles) == 1
    assert simple_lock.waiter_count < lock_contention.cases[0].waiter_count
    assert simple_lock.idle_noise_count < lock_contention.cases[0].idle_noise_count

    noisy_neighbor = scenarios["pg_system_failure_noisy_neighbor"]
    simple_neighbor = noisy_neighbor.get_case("single_archive_cpu_neighbor_simple")
    assert len(noisy_neighbor.cases) == 2
    assert simple_neighbor.case_no == 1
    assert simple_neighbor.worker_count == 1
    assert simple_neighbor.production_noise is False
    assert simple_neighbor.background_workload.worker_count == 1
    assert len(simple_neighbor.background_workload.profiles) == 1

    checkpoint = scenarios["pg_system_failure_io_checkpoint_spikes"]
    simple_checkpoint = checkpoint.get_case("single_checkout_checkpoint_spike_simple")
    assert len(checkpoint.cases) == 2
    assert simple_checkpoint.case_no == 1
    assert simple_checkpoint.table != checkpoint.cases[0].table
    assert simple_checkpoint.background_workload.worker_count == 1
    assert len(simple_checkpoint.background_workload.profiles) == 1

    wal = scenarios["pg_system_failure_wal_accumulation"]
    simple_wal = wal.get_case("abandoned_report_slot_wal_retention_simple")
    assert len(wal.cases) == 2
    assert simple_wal.case_no == 1
    assert simple_wal.production_noise is False
    assert simple_wal.stale_slot_names == (
        "analytics_report_backfill_abandoned",
        "analytics_backfill_abandoned_legacy",
        "report_export_retry_stale",
    )
    assert len(simple_wal.fresh_slot_names) == 6
    assert len(simple_wal.registry_rows) == 9
    assert all(row.purpose and row.ack_minutes_ago > 0 for row in simple_wal.registry_rows)
    assert simple_wal.background_workload.worker_count == 1

    temp = scenarios["pg_system_failure_temp_file_explosion"]
    simple_temp = temp.get_case("daily_sales_temp_exhaustion_simple")
    assert len(temp.cases) == 2
    assert simple_temp.case_no == 1
    assert simple_temp.production_noise is False
    assert simple_temp.tmpfs_size_mb < temp.cases[0].tmpfs_size_mb
    assert simple_temp.background_workload.worker_count == 1

    fd = scenarios["pg_system_failure_fd_exhaustion"]
    simple_fd = fd.get_case("report_export_fd_exhaustion_simple")
    assert len(fd.cases) == 2
    assert simple_fd.case_no == 1
    assert simple_fd.production_noise is False
    assert simple_fd.table_count < fd.cases[0].table_count
    assert simple_fd.background_workload.worker_count == 1

    auto_analyze = scenarios["pg_system_failure_auto_analyze_storm"].cases[0].background_workload
    assert (
        auto_analyze.worker_count,
        auto_analyze.seed,
        auto_analyze.start_phase,
        auto_analyze.warmup_seconds,
    ) == (6, 0, BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY, 10)

    for scenario_id in (
        "pg_system_failure_deadlock",
        "pg_system_failure_fd_exhaustion",
        "pg_system_failure_io_checkpoint_spikes",
    ):
        workload = scenarios[scenario_id].cases[0].background_workload
        assert workload.worker_count == 6
        assert workload.seed == 0
        assert workload.start_phase is BackgroundWorkloadStartPhase.BEFORE_FAULTS

    deadlock_names = {
        profile.name
        for profile in scenarios["pg_system_failure_deadlock"].cases[0].background_workload.profiles
    }
    assert any(name.startswith("distraction_") for name in deadlock_names)
    assert any(name.startswith("log_noise_") for name in deadlock_names)

    checkpoint_names = {
        profile.name
        for profile in scenarios["pg_system_failure_io_checkpoint_spikes"].cases[0].background_workload.profiles
    }
    assert any(name.startswith("checkpoint_log_noise_") for name in checkpoint_names)
    assert any(name.startswith("checkpoint_temp_spill_") for name in checkpoint_names)

    xid_case = scenarios["pg_system_failure_xid_wraparound"].cases[0]
    assert (
        xid_case.checkout_idle_connections,
        xid_case.retry_idle_connections,
        xid_case.monitor_noise_connections,
    ) == (36, 4, 6)
    assert xid_case.replay_worker_instances == 2
    assert xid_case.commit_writer_enabled is True
    assert xid_case.batch_control_table == "ops_batch_control"
    assert xid_case.batch_control_job == "ledger_settlement_replay"
    assert xid_case.batch_control_template_table == "ops_batch_control_template"
    assert xid_case.commit_failure_table == "checkout_commit_failures"
    simple_xid = scenarios["pg_system_failure_xid_wraparound"].get_case(
        "billing_freeze_blocked_simple"
    )
    assert simple_xid.case_no == 1
    assert simple_xid.production_noise is True
    assert simple_xid.prepared_transaction_name == "billing_settlement_prep_20260706"
    assert simple_xid.protected_session_name == "billing_settlement_batch"
    assert simple_xid.replay_worker_instances == 0
    assert simple_xid.commit_writer_enabled is False
    assert simple_xid.batch_control_table == ""
    assert simple_xid.batch_control_template_table == ""
    assert (
        scenarios["pg_system_failure_xid_wraparound"]
        .cases[0]
        .prepared_transaction_name
        == ""
    )
    assert simple_xid.background_workload.worker_count == 1

    page_corruption = scenarios["pg_system_failure_page_corruption"]
    simple_page = page_corruption.get_case("invoice_page_corruption_triage_simple")
    assert len(page_corruption.cases) == 2
    assert simple_page.case_no == 1
    assert simple_page.row_count < page_corruption.cases[0].row_count
    assert simple_page.background_workload.worker_count == 1

    oom = scenarios["pg_system_failure_oom"]
    simple_oom = oom.get_case("restart_shared_buffers_oom_simple")
    assert len(oom.cases) == 2
    assert simple_oom.case_no == 1
    assert simple_oom.production_noise is False
    assert simple_oom.work_mem == "8MB"
    assert simple_oom.background_workload.worker_count == 1


def test_temp_file_explosion_hard_case_keeps_internal_limit_out_of_alert():
    scenarios = {scenario.scenario_id: scenario for scenario in ALL_SCENARIOS}
    simple_temp = scenarios["pg_system_failure_temp_file_explosion"].get_case(
        "daily_sales_temp_exhaustion_simple"
    )

    assert "cancelled retry batch" in simple_temp.alert
    assert "32mb" not in simple_temp.alert.casefold()
    assert "64mb" not in simple_temp.alert.casefold()


def test_rewritten_alerts_keep_root_cause_out_and_public_contract_in():
    scenarios = {scenario.scenario_id: scenario for scenario in ALL_SCENARIOS}

    def alert_of(scenario_id: str, case_id: str) -> str:
        return scenarios[scenario_id].get_case(case_id).alert

    billing = alert_of("pg_query_perf_cache_pollution", "billing_export_scan_cache_churn")
    assert "ops_workload_controls" in billing
    for term in ("billing_export_scan", "evicting checkout hot pages", "paus"):
        assert term not in billing.casefold()

    cursor = alert_of("pg_query_perf_cache_pollution", "analytics_cursor_cache_churn")
    assert "ops_workload_controls" in cursor
    for term in ("analytics cursor", "old snapshot", "one large scan", "memory sizing"):
        assert term not in cursor.casefold()

    stale = alert_of("pg_query_perf_stale_statistics", "branch_order_hot_window_simple")
    for term in ("estimates far fewer rows", "table statistics", "recent data changes"):
        assert term not in stale.casefold()

    sniffing = alert_of("pg_query_perf_parameter_sniffing", "branch_order_year_skew_simple")
    assert "bind-sensitive" not in sniffing.casefold()

    burst = alert_of("pg_system_failure_wal_checkpoint_storm", "billing_slot_checkpoint_burst_simple")
    for term in ("release the unsafe wal retention", "tune checkpoint pressure"):
        assert term not in burst.casefold()

    oom = alert_of("pg_system_failure_oom", "restart_shared_buffers_oom_simple")
    for term in ("persistent setting", "runtime budget", "process exit class"):
        assert term not in oom.casefold()

    advisory = alert_of("pg_system_failure_cpu_lock_spin", "advisory_lock_retry_cpu_storm")
    for term in ("lock primitive", "compute-heavy sql", "retry pressure"):
        assert term not in advisory.casefold()

    waiter = alert_of(
        "pg_query_perf_stale_stats_lock_contention", "checkout_stale_stats_single_waiter_simple"
    )
    for term in ("idle transaction", "stale optimizer statistics"):
        assert term not in waiter.casefold()

    spikes = alert_of("pg_system_failure_io_checkpoint_spikes", "checkout_checkpoint_spikes")
    assert spikes.endswith("verify the reproducibility of the fix, and then submit.")
    assert "..." not in spikes


def test_scenarios_cannot_hold_runtime_state():
    scenario = ALL_SCENARIOS[0]
    with pytest.raises(AttributeError, match="is stateless"):
        scenario.injector = object()


def test_fault_injectors_define_one_uniform_lifecycle_protocol():
    injector_types = {
        plan.injector_type
        for scenario in ALL_SCENARIOS
        for case in scenario.cases
        for plan in scenario.build_fault_plan(case)
    }
    lifecycle_methods = {
        "install",
        "activate",
        "prepare_observability",
        "quiesce",
        "recover",
    }
    for injector_type in injector_types:
        assert "prepare_snapshot" not in injector_type.__dict__, injector_type.__name__
        for method_name in lifecycle_methods:
            assert method_name in injector_type.__dict__, (injector_type.__name__, method_name)
            parameters = inspect.signature(
                injector_type.__dict__[method_name]
            ).parameters
            assert list(parameters) == ["self", "context"], (
                injector_type.__name__,
                method_name,
                parameters,
            )


def test_fault_injectors_do_not_expose_legacy_name_api():
    assert not hasattr(BaseFaultInjector, "get_name")
    for scenario in ALL_SCENARIOS:
        for case in scenario.cases:
            for plan in scenario.build_fault_plan(case):
                assert not hasattr(plan.injector_type, "get_name")


def test_fault_injector_lifecycle_has_no_reflection_or_exception_fallbacks():
    source = Path(inspect.getsourcefile(BaseFaultInjector)).read_text()
    tree = ast.parse(source)
    lifecycle_methods = {
        "install",
        "activate",
        "prepare_observability",
        "quiesce",
        "recover",
    }
    violations = []
    for class_node in (node for node in tree.body if isinstance(node, ast.ClassDef)):
        for method in (
            node
            for node in class_node.body
            if isinstance(node, ast.FunctionDef) and node.name in lifecycle_methods
        ):
            for node in ast.walk(method):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id in {"getattr", "hasattr"}
                ):
                    violations.append(
                        (class_node.name, method.name, node.lineno, node.func.id)
                    )
                if isinstance(node, ast.Try) and node.handlers:
                    violations.append(
                        (class_node.name, method.name, node.lineno, "except")
                    )
    assert not violations, violations


def test_fault_injector_private_method_calls_resolve_on_the_class():
    injector_types = {
        plan.injector_type
        for scenario in ALL_SCENARIOS
        for case in scenario.cases
        for plan in scenario.build_fault_plan(case)
    }
    for injector_type in injector_types:
        tree = ast.parse(textwrap.dedent(inspect.getsource(injector_type)))
        private_calls = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "self"
            and node.func.attr.startswith("_")
        }
        missing = sorted(name for name in private_calls if not hasattr(injector_type, name))
        assert not missing, (injector_type.__name__, missing)


def test_fault_plan_config_has_no_injector_defaults():
    source = Path(inspect.getsourcefile(BaseFaultInjector)).read_text()
    assert "config.get(" not in source


def test_pg_deployment_identity_lives_in_cases():
    for scenario in ALL_SCENARIOS:
        if not scenario.scenario_id.startswith("pg_"):
            continue
        case = scenario.cases[0]
        assert case.base_image_name.startswith("aiopsbench-pg-")
        assert case.workload_tag


def test_formal_entry_scripts_require_explicit_case():
    examples = Path("examples")
    scripts = sorted(examples.glob("run_pg_*_scenario.py"))
    scripts += sorted(examples.glob("run_tidb_*_scenario.py"))
    formal_registrations = [
        registration
        for registration in SCENARIO_REGISTRY
        if registration.entrypoint is not None
    ]

    assert len(scripts) == len(formal_registrations)
    assert {path.name for path in scripts} == {
        registration.entrypoint for registration in formal_registrations
    }
    for path in scripts:
        source = path.read_text()
        assert '"--case"' in source
        assert "required=True" in source
        assert "workload_runner_profiles" not in source
        runpy.run_path(str(path), run_name=f"scenario_entry_{path.stem}")
        if path.name.startswith("run_pg_"):
            assert not re.search(
                r"^(SCENARIO_ID|BASE_IMAGE_NAME|WORKLOAD_TAG)\s*=",
                source,
                re.MULTILINE,
            )
