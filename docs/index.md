---
doc_id: docs.index
doc_type: index
status: canonical
audience: [user, contributor]
exposure: public
scope: [shared]
language: en
summary: Index of DBA-Bench guides, standards, scenario contracts, and baseline documentation.
---

# DBA-Bench Documentation Index

This index lists the English documentation tree. Chinese-language counterparts live
under `docs/zh/` (same subdirectory layout, `.zh-CN.md` filename suffix) and are
listed in [the Chinese documentation index](zh/index.md). Browse the guides,
standards, scenario contracts, and baseline documentation below.

## baseline
- `docs/baseline/andromeda_implementation.md`
- `docs/baseline/dbaiops_baseline_implementation.md`
- `docs/baseline/dbot_implementation.md`
- `docs/baseline/panda_baseline_implementation.md`

## catalogs
- `docs/catalogs/case-tags.catalog.md`
- `docs/catalogs/postgresql-scenarios.catalog.md`
- `docs/catalogs/tidb-scenarios.catalog.md`

## figures
- `docs/figures/DBA-Bench_title.png`
- `docs/figures/framework.png`

## guides/benchmark
- `docs/guides/benchmark/connect-remote-agent.guide.md`
- `docs/guides/benchmark/run-experiment.guide.md`
- `docs/guides/benchmark/run-human-browser-console.guide.md`

## guides/evaluation
- `docs/guides/evaluation/semantic-diagnosis-matching.guide.md`

## guides/persistent-scenario
- `docs/guides/persistent-scenario/implement-persistent-scenario.guide.md`

## guides/scenario
- `docs/guides/scenario/implement-scenario-case.guide.md`

## persistent-scenarios/postgresql
- `docs/persistent-scenarios/postgresql/pg-continuous-ops-smoke.contract.md`
- `docs/persistent-scenarios/postgresql/production-portfolio.contract.md`

## persistent-scenarios/tidb
- `docs/persistent-scenarios/tidb/production-portfolio.contract.md`

## scenarios/postgresql/business_change
- `docs/scenarios/postgresql/business_change/pg_business_change_collation_conversion.contract.md`
- `docs/scenarios/postgresql/business_change/pg_business_change_fk_validation.contract.md`
- `docs/scenarios/postgresql/business_change/pg_business_change_invalid_index.contract.md`
- `docs/scenarios/postgresql/business_change/pg_business_change_io_saturation.contract.md`
- `docs/scenarios/postgresql/business_change/pg_business_change_lwlock_pgbouncer_cascade.contract.md`
- `docs/scenarios/postgresql/business_change/pg_business_change_massive_backfill.contract.md`
- `docs/scenarios/postgresql/business_change/pg_business_change_online_ddl.contract.md`
- `docs/scenarios/postgresql/business_change/pg_business_change_partition_migration.contract.md`

## scenarios/postgresql/health_check
- `docs/scenarios/postgresql/health_check/pg_health_check_autovacuum_sustainability.contract.md`
- `docs/scenarios/postgresql/health_check/pg_health_check_backup_recoverability.contract.md`
- `docs/scenarios/postgresql/health_check/pg_health_check_backup_rpo_certification.contract.md`
- `docs/scenarios/postgresql/health_check/pg_health_check_capacity_trend.contract.md`
- `docs/scenarios/postgresql/health_check/pg_health_check_config_drift.contract.md`
- `docs/scenarios/postgresql/health_check/pg_health_check_long_running_tx.contract.md`
- `docs/scenarios/postgresql/health_check/pg_health_check_sequence_exhaustion.contract.md`
- `docs/scenarios/postgresql/health_check/pg_health_check_table_bloat.contract.md`
- `docs/scenarios/postgresql/health_check/pg_health_check_unused_indexes.contract.md`

## scenarios/postgresql/query_perf
- `docs/scenarios/postgresql/query_perf/pg_query_perf_cache_pollution.contract.md`
- `docs/scenarios/postgresql/query_perf/pg_query_perf_heavy_offset_pagination.contract.md`
- `docs/scenarios/postgresql/query_perf/pg_query_perf_implicit_type_conversion.contract.md`
- `docs/scenarios/postgresql/query_perf/pg_query_perf_missing_index.contract.md`
- `docs/scenarios/postgresql/query_perf/pg_query_perf_parameter_sniffing.contract.md`
- `docs/scenarios/postgresql/query_perf/pg_query_perf_sort_spill.contract.md`
- `docs/scenarios/postgresql/query_perf/pg_query_perf_stale_statistics.contract.md`
- `docs/scenarios/postgresql/query_perf/pg_query_perf_stale_stats_lock_contention.contract.md`
- `docs/scenarios/postgresql/query_perf/pg_query_perf_suboptimal_join.contract.md`

## scenarios/postgresql/resource_governance
- `docs/scenarios/postgresql/resource_governance/pg_resource_governance_audit_logging.contract.md`
- `docs/scenarios/postgresql/resource_governance/pg_resource_governance_container_cpu_budget.contract.md`
- `docs/scenarios/postgresql/resource_governance/pg_resource_governance_data_archiving.contract.md`
- `docs/scenarios/postgresql/resource_governance/pg_resource_governance_host_backup.contract.md`
- `docs/scenarios/postgresql/resource_governance/pg_resource_governance_io_context_workload.contract.md`
- `docs/scenarios/postgresql/resource_governance/pg_resource_governance_partition_cleanup.contract.md`
- `docs/scenarios/postgresql/resource_governance/pg_resource_governance_pgbouncer_connection_budget.contract.md`
- `docs/scenarios/postgresql/resource_governance/pg_resource_governance_privilege_masking.contract.md`
- `docs/scenarios/postgresql/resource_governance/pg_resource_governance_resource_throttling.contract.md`

## scenarios/postgresql/system_failure
- `docs/scenarios/postgresql/system_failure/pg_system_failure_auto_analyze_storm.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_checkpoint_archive.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_connection_bloat.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_connection_storm.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_cpu_lock_spin.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_deadlock.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_fd_exhaustion.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_io_checkpoint_spikes.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_lock_contention.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_noisy_neighbor.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_oom.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_page_corruption.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_temp_file_explosion.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_wal_accumulation.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_wal_checkpoint_storm.contract.md`
- `docs/scenarios/postgresql/system_failure/pg_system_failure_xid_wraparound.contract.md`

## scenarios/tidb/business_change
- `docs/scenarios/tidb/business_change/tidb_business_change_batched_dml_ddl.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_cdc_dc_migration.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_dm_replace.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_dr_auto_sync_failover.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_large_table_batch_dml.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_lightning_checkpoint.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_online_ddl_pause_resume.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_pitr_checkpoint_recovery.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_rolling_upgrade.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_table_recovery.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_timezone_ddl_backpressure.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_timezone_ddl_backpressure_frozen_history.contract.md`
- `docs/scenarios/tidb/business_change/tidb_business_change_x86_arm64_migration.contract.md`

## scenarios/tidb/health_check
- `docs/scenarios/tidb/health_check/tidb_health_check_auto_analyze_drift.contract.md`
- `docs/scenarios/tidb/health_check/tidb_health_check_backup_recoverability.contract.md`
- `docs/scenarios/tidb/health_check/tidb_health_check_empty_region_leader_skew.contract.md`
- `docs/scenarios/tidb/health_check/tidb_health_check_empty_region_leader_skew_frozen_history.contract.md`
- `docs/scenarios/tidb/health_check/tidb_health_check_gc_safepoint_pin.contract.md`
- `docs/scenarios/tidb/health_check/tidb_health_check_lightning_preflight.contract.md`
- `docs/scenarios/tidb/health_check/tidb_health_check_long_transaction_mvcc.contract.md`
- `docs/scenarios/tidb/health_check/tidb_health_check_placement_policy.contract.md`
- `docs/scenarios/tidb/health_check/tidb_health_check_syncpoint_consistency.contract.md`
- `docs/scenarios/tidb/health_check/tidb_health_check_ticdc_replication_trend.contract.md`
- `docs/scenarios/tidb/health_check/tidb_health_check_ticdc_replication_trend_frozen_history.contract.md`

## scenarios/tidb/query_perf
- `docs/scenarios/tidb/query_perf/tidb_query_perf_case_when_in_cartesian_semi_join.contract.md`
- `docs/scenarios/tidb/query_perf/tidb_query_perf_index_merge_selection_failure.contract.md`
- `docs/scenarios/tidb/query_perf/tidb_query_perf_index_order_correlation.contract.md`
- `docs/scenarios/tidb/query_perf/tidb_query_perf_like_escape_range.contract.md`
- `docs/scenarios/tidb/query_perf/tidb_query_perf_noncovering_index_tail_latency.contract.md`
- `docs/scenarios/tidb/query_perf/tidb_query_perf_optimistic_write_conflict.contract.md`
- `docs/scenarios/tidb/query_perf/tidb_query_perf_optimistic_write_conflict_frozen_history.contract.md`
- `docs/scenarios/tidb/query_perf/tidb_query_perf_set_autocommit_storm.contract.md`
- `docs/scenarios/tidb/query_perf/tidb_query_perf_set_autocommit_storm_frozen_history.contract.md`
- `docs/scenarios/tidb/query_perf/tidb_query_perf_statistics_drift.contract.md`
- `docs/scenarios/tidb/query_perf/tidb_query_perf_statistics_drift_frozen_history.contract.md`

## scenarios/tidb/resource_governance
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_br_slo_adaptive_throttling.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_br_slo_adaptive_throttling_frozen_history.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_connection_balancing.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_empty_region_merge_budget.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_lightning_budget.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_lightning_budget_frozen_history.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_pd_api_security.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_placement_policy.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_rg06.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_ru_budget_calibration.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_ru_budget_calibration_frozen_history.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_runaway_query.contract.md`
- `docs/scenarios/tidb/resource_governance/tidb_resource_governance_sql_binding.contract.md`

## scenarios/tidb/system_failure
- `docs/scenarios/tidb/system_failure/tidb_system_failure_br_permission.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_clustered_index_consistency.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_deadlock.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_gc_mvcc_recovery.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_lock_contention.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_mdl_blocking.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_pd_metadata_recovery.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_pending_offline.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_region_unavailable.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_sf01.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_sf02.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_table_cache_lease.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_table_cache_lease_frozen_history.contract.md`
- `docs/scenarios/tidb/system_failure/tidb_system_failure_ticdc_gc_safepoint.contract.md`

## standards/evaluation
- `docs/standards/evaluation/dp-op-sp.standard.md`

## standards/knowledge
- `docs/standards/knowledge/postgresql-document-classification.standard.md`
- `docs/standards/knowledge/tidb-knowledge-construction.standard.md`
- `docs/standards/knowledge/tidb-knowledge-usage.standard.md`

## standards/persistent-scenario
- `docs/standards/persistent-scenario/architecture.standard.md`
- `docs/standards/persistent-scenario/difficulty.standard.md`
- `docs/standards/persistent-scenario/evaluation.standard.md`

## standards/scenario
- `docs/standards/scenario/architecture.standard.md`
- `docs/standards/scenario/difficulty.standard.md`
- `docs/standards/scenario/taxonomy.standard.md`

## top-level
- `docs/getting-started.md`

## zh
- `docs/zh/getting-started.zh-CN.md`
- `docs/zh/index.md`

## zh/baseline
- `docs/zh/baseline/andromeda_implementation.zh-CN.md`
- `docs/zh/baseline/dbaiops_baseline_implementation.zh-CN.md`
- `docs/zh/baseline/dbot_implementation.zh-CN.md`
- `docs/zh/baseline/panda_baseline_implementation.zh-CN.md`

## zh/catalogs
- `docs/zh/catalogs/case-tags.catalog.zh-CN.md`
- `docs/zh/catalogs/postgresql-scenarios.catalog.zh-CN.md`
- `docs/zh/catalogs/tidb-scenarios.catalog.zh-CN.md`

## zh/guides/benchmark
- `docs/zh/guides/benchmark/run-experiment.guide.zh-CN.md`
- `docs/zh/guides/benchmark/run-human-browser-console.guide.zh-CN.md`

## zh/guides/evaluation
- `docs/zh/guides/evaluation/semantic-diagnosis-matching.guide.zh-CN.md`

## zh/guides/persistent-scenario
- `docs/zh/guides/persistent-scenario/implement-persistent-scenario.guide.zh-CN.md`

## zh/guides/scenario
- `docs/zh/guides/scenario/implement-scenario-case.guide.zh-CN.md`

## zh/persistent-scenarios/postgresql
- `docs/zh/persistent-scenarios/postgresql/pg-continuous-ops-smoke.contract.zh-CN.md`
- `docs/zh/persistent-scenarios/postgresql/production-portfolio.contract.zh-CN.md`

## zh/persistent-scenarios/tidb
- `docs/zh/persistent-scenarios/tidb/production-portfolio.contract.zh-CN.md`

## zh/scenarios/postgresql/business_change
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_collation_conversion.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_fk_validation.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_invalid_index.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_io_saturation.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_lwlock_pgbouncer_cascade.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_massive_backfill.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_online_ddl.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_partition_migration.contract.zh-CN.md`

## zh/scenarios/postgresql/health_check
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_autovacuum_sustainability.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_backup_recoverability.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_backup_rpo_certification.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_capacity_trend.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_config_drift.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_long_running_tx.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_sequence_exhaustion.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_table_bloat.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_unused_indexes.contract.zh-CN.md`

## zh/scenarios/postgresql/query_perf
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_cache_pollution.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_heavy_offset_pagination.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_implicit_type_conversion.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_missing_index.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_parameter_sniffing.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_sort_spill.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_stale_statistics.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_stale_stats_lock_contention.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_suboptimal_join.contract.zh-CN.md`

## zh/scenarios/postgresql/resource_governance
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_audit_logging.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_container_cpu_budget.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_data_archiving.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_host_backup.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_io_context_workload.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_partition_cleanup.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_pgbouncer_connection_budget.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_privilege_masking.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_resource_throttling.contract.zh-CN.md`

## zh/scenarios/postgresql/system_failure
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_auto_analyze_storm.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_checkpoint_archive.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_connection_bloat.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_connection_storm.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_cpu_lock_spin.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_deadlock.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_fd_exhaustion.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_io_checkpoint_spikes.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_lock_contention.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_noisy_neighbor.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_oom.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_page_corruption.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_temp_file_explosion.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_wal_accumulation.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_wal_checkpoint_storm.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/system_failure/pg_system_failure_xid_wraparound.contract.zh-CN.md`

## zh/scenarios/tidb/business_change
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_batched_dml_ddl.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_cdc_dc_migration.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_dm_replace.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_dr_auto_sync_failover.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_large_table_batch_dml.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_lightning_checkpoint.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_online_ddl_pause_resume.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_pitr_checkpoint_recovery.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_rolling_upgrade.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_table_recovery.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_timezone_ddl_backpressure.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_timezone_ddl_backpressure_frozen_history.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/business_change/tidb_business_change_x86_arm64_migration.contract.zh-CN.md`

## zh/scenarios/tidb/health_check
- `docs/zh/scenarios/tidb/health_check/tidb_health_check_auto_analyze_drift.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/health_check/tidb_health_check_backup_recoverability.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/health_check/tidb_health_check_empty_region_leader_skew.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/health_check/tidb_health_check_empty_region_leader_skew_frozen_history.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/health_check/tidb_health_check_gc_safepoint_pin.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/health_check/tidb_health_check_lightning_preflight.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/health_check/tidb_health_check_long_transaction_mvcc.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/health_check/tidb_health_check_placement_policy.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/health_check/tidb_health_check_syncpoint_consistency.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/health_check/tidb_health_check_ticdc_replication_trend.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/health_check/tidb_health_check_ticdc_replication_trend_frozen_history.contract.zh-CN.md`

## zh/scenarios/tidb/query_perf
- `docs/zh/scenarios/tidb/query_perf/tidb_query_perf_case_when_in_cartesian_semi_join.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/query_perf/tidb_query_perf_index_merge_selection_failure.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/query_perf/tidb_query_perf_index_order_correlation.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/query_perf/tidb_query_perf_like_escape_range.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/query_perf/tidb_query_perf_noncovering_index_tail_latency.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/query_perf/tidb_query_perf_optimistic_write_conflict.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/query_perf/tidb_query_perf_optimistic_write_conflict_frozen_history.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/query_perf/tidb_query_perf_set_autocommit_storm.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/query_perf/tidb_query_perf_set_autocommit_storm_frozen_history.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/query_perf/tidb_query_perf_statistics_drift.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/query_perf/tidb_query_perf_statistics_drift_frozen_history.contract.zh-CN.md`

## zh/scenarios/tidb/resource_governance
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_br_slo_adaptive_throttling.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_br_slo_adaptive_throttling_frozen_history.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_connection_balancing.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_empty_region_merge_budget.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_lightning_budget.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_lightning_budget_frozen_history.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_pd_api_security.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_placement_policy.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_rg06.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_ru_budget_calibration.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_ru_budget_calibration_frozen_history.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_runaway_query.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/resource_governance/tidb_resource_governance_sql_binding.contract.zh-CN.md`

## zh/scenarios/tidb/system_failure
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_br_permission.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_clustered_index_consistency.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_deadlock.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_gc_mvcc_recovery.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_lock_contention.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_mdl_blocking.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_pd_metadata_recovery.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_pending_offline.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_region_unavailable.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_sf01.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_sf02.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_table_cache_lease.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_table_cache_lease_frozen_history.contract.zh-CN.md`
- `docs/zh/scenarios/tidb/system_failure/tidb_system_failure_ticdc_gc_safepoint.contract.zh-CN.md`

## zh/standards/evaluation
- `docs/zh/standards/evaluation/dp-op-sp.standard.zh-CN.md`

## zh/standards/knowledge
- `docs/zh/standards/knowledge/postgresql-document-classification.standard.zh-CN.md`
- `docs/zh/standards/knowledge/tidb-knowledge-construction.standard.zh-CN.md`
- `docs/zh/standards/knowledge/tidb-knowledge-usage.standard.zh-CN.md`

## zh/standards/persistent-scenario
- `docs/zh/standards/persistent-scenario/architecture.standard.zh-CN.md`
- `docs/zh/standards/persistent-scenario/difficulty.standard.zh-CN.md`
- `docs/zh/standards/persistent-scenario/evaluation.standard.zh-CN.md`

## zh/standards/scenario
- `docs/zh/standards/scenario/architecture.standard.zh-CN.md`
- `docs/zh/standards/scenario/difficulty.standard.zh-CN.md`
- `docs/zh/standards/scenario/taxonomy.standard.zh-CN.md`
