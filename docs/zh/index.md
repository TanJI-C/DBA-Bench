---
doc_id: docs.index.public
doc_type: index
status: canonical
audience: [user, contributor]
exposure: public
scope: [shared]
language: zh-CN
summary: 中文文档索引；docs/zh/ 是 docs/ 英文文档树的中文镜像。
---

# DBA-Bench 中文文档索引

本目录（`docs/zh/`）收录仓库文档的中文版本，子目录结构与英文文档树 `docs/`
完全镜像，文件名使用 `.zh-CN.md` 后缀。英文原版位于 `docs/` 下的同路径
（不带后缀），清单见 `docs/index.md`。

约定：
- 场景 contract 中的题面（alert）按文档语言呈现：中文版保留中文题面，
  英文版为英文译写；运行时实际下发的题面以 `src/scenarios/` 中的代码为准，
  相关文档内附有说明注记。
- 尚未提供中文版的英文文档（如 `docs/getting-started.md`）仅存在于 `docs/`。

## baseline
- `docs/zh/baseline/andromeda_implementation.zh-CN.md`
- `docs/zh/baseline/dbaiops_baseline_implementation.zh-CN.md`
- `docs/zh/baseline/dbot_implementation.zh-CN.md`
- `docs/zh/baseline/panda_baseline_implementation.zh-CN.md`

## catalogs
- `docs/zh/catalogs/case-tags.catalog.zh-CN.md`
- `docs/zh/catalogs/postgresql-scenarios.catalog.zh-CN.md`
- `docs/zh/catalogs/tidb-scenarios.catalog.zh-CN.md`

## guides/benchmark
- `docs/zh/guides/benchmark/connect-remote-agent.guide.zh-CN.md`
- `docs/zh/guides/benchmark/run-experiment.guide.zh-CN.md`
- `docs/zh/guides/benchmark/run-human-browser-console.guide.zh-CN.md`

## guides/evaluation
- `docs/zh/guides/evaluation/semantic-diagnosis-matching.guide.zh-CN.md`

## guides/persistent-scenario
- `docs/zh/guides/persistent-scenario/implement-persistent-scenario.guide.zh-CN.md`

## guides/scenario
- `docs/zh/guides/scenario/implement-scenario-case.guide.zh-CN.md`

## persistent-scenarios/postgresql
- `docs/zh/persistent-scenarios/postgresql/pg-continuous-ops-smoke.contract.zh-CN.md`
- `docs/zh/persistent-scenarios/postgresql/production-portfolio.contract.zh-CN.md`

## persistent-scenarios/tidb
- `docs/zh/persistent-scenarios/tidb/production-portfolio.contract.zh-CN.md`

## scenarios/postgresql/business_change
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_collation_conversion.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_fk_validation.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_invalid_index.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_io_saturation.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_lwlock_pgbouncer_cascade.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_massive_backfill.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_online_ddl.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/business_change/pg_business_change_partition_migration.contract.zh-CN.md`

## scenarios/postgresql/health_check
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_autovacuum_sustainability.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_backup_recoverability.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_backup_rpo_certification.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_capacity_trend.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_config_drift.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_long_running_tx.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_sequence_exhaustion.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_table_bloat.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/health_check/pg_health_check_unused_indexes.contract.zh-CN.md`

## scenarios/postgresql/query_perf
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_cache_pollution.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_heavy_offset_pagination.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_implicit_type_conversion.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_missing_index.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_parameter_sniffing.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_sort_spill.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_stale_statistics.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_stale_stats_lock_contention.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/query_perf/pg_query_perf_suboptimal_join.contract.zh-CN.md`

## scenarios/postgresql/resource_governance
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_audit_logging.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_container_cpu_budget.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_data_archiving.contract.zh-CN.md` — 冷订单归档，保护业务表和重要基准表，普通辅助表不限制名称。
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_host_backup.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_io_context_workload.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_partition_cleanup.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_pgbouncer_connection_budget.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_privilege_masking.contract.zh-CN.md`
- `docs/zh/scenarios/postgresql/resource_governance/pg_resource_governance_resource_throttling.contract.zh-CN.md`

## scenarios/postgresql/system_failure
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

## scenarios/tidb/business_change
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

## scenarios/tidb/health_check
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

## scenarios/tidb/query_perf
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

## scenarios/tidb/resource_governance
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

## scenarios/tidb/system_failure
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

## standards/evaluation
- `docs/zh/standards/evaluation/dp-op-sp.standard.zh-CN.md`

## standards/knowledge
- `docs/zh/standards/knowledge/postgresql-document-classification.standard.zh-CN.md`
- `docs/zh/standards/knowledge/tidb-knowledge-construction.standard.zh-CN.md`
- `docs/zh/standards/knowledge/tidb-knowledge-usage.standard.zh-CN.md`

## standards/persistent-scenario
- `docs/zh/standards/persistent-scenario/architecture.standard.zh-CN.md`
- `docs/zh/standards/persistent-scenario/difficulty.standard.zh-CN.md`
- `docs/zh/standards/persistent-scenario/evaluation.standard.zh-CN.md`

## standards/scenario
- `docs/zh/standards/scenario/architecture.standard.zh-CN.md`
- `docs/zh/standards/scenario/difficulty.standard.zh-CN.md`
- `docs/zh/standards/scenario/taxonomy.standard.zh-CN.md`

## top-level
- `docs/zh/getting-started.zh-CN.md`
