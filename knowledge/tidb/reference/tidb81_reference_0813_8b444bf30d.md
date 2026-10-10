# TiDB Cloud system variable limitations and notes

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/limited-sql-features.md`
- Source Title: `Limited SQL Features on TiDB Cloud`
- Source Heading Path: `Limited SQL features on TiDB Cloud > System variables`
- Source Line Ranges: `122-242`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `system-variables`, `read-only`, `not-supported`, `serverless`, `dedicated`, `security-enhanced-mode`, `password-policy`, `plan-replayer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0813_8b444bf30d`
- Source ID: `tidb-docs-8.1:tidb-cloud/limited-sql-features.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6df7b47f970b3f5b05de1bb0ff6b24d5cc08920ab85e673138429e865b84edcd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/limited-sql-features#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/limited-sql-features.md

## Retrieval Guidance

- Use When: Use this when looking up which TiDB Cloud system variables are unsupported, read-only, or constrained in Dedicated and Serverless.
- Retrieval Keywords: TiDB Cloud system variables, TiDB Cloud Dedicated, TiDB Cloud Serverless, read-only, Not supported, Security Enhanced Mode (SEM), validate_password.policy, PLAN REPLAYER, require_secure_transport
- Follow-up Guidance: Check the table and footnotes for the specific variable to see whether it is read-only, not supported, always enabled, or constrained by SEM or password policy.
- Classification Note: This is a reference table of TiDB Cloud system variable limitations and notes for Dedicated and Serverless.

## Official Source Content

## System variables

| Variable | TiDB Cloud Dedicated | TiDB Cloud Serverless |
|:-|:-|:-|
| `datadir` | No limitation | Not supported [^1] |
| `interactive_timeout` | No limitation | Read-only [^10] |
| `max_allowed_packet` | No limitation | Read-only [^10] |
| `plugin_dir` | No limitation | Not supported [^8] |
| `plugin_load` | No limitation | Not supported [^8] |
| `require_secure_transport` | Not supported [^12] | Read-only [^10] |
| `skip_name_resolve` | No limitation | Read-only [^10] |
| `sql_log_bin` | No limitation | Read-only [^10] |
| `tidb_analyze_skip_column_types` | No limitation | Read-only [^10] |
| `tidb_cdc_write_source` | No limitation | Read-only [^10] |
| `tidb_check_mb4_value_in_utf8` | Not supported [^4] | Not supported [^4] |
| `tidb_config` | Not supported [^4] | Not supported [^4] |
| `tidb_ddl_disk_quota` | No limitation | Read-only [^10] |
| `tidb_ddl_enable_fast_reorg` | No limitation | Read-only [^10] |
| `tidb_ddl_error_count_limit` | No limitation | Read-only [^10] |
| `tidb_ddl_flashback_concurrency` | No limitation | Read-only [^10] |
| `tidb_ddl_reorg_batch_size` | No limitation | Read-only [^10] |
| `tidb_ddl_reorg_priority` | No limitation | Read-only [^10] |
| `tidb_ddl_reorg_worker_cnt` | No limitation | Read-only [^10] |
| `tidb_enable_1pc` | No limitation | Read-only [^10] |
| `tidb_enable_async_commit` | No limitation | Read-only [^10] |
| `tidb_enable_auto_analyze` | No limitation | Read-only [^10] |
| `tidb_enable_collect_execution_info` | Not supported [^4] | Not supported [^4] |
| `tidb_enable_ddl` | No limitation | Read-only [^10] |
| `tidb_enable_gc_aware_memory_track` | No limitation | Read-only [^10] |
| `tidb_enable_gogc_tuner` | No limitation | Read-only [^10] |
| `tidb_enable_local_txn` | No limitation | Read-only [^10] |
| `tidb_enable_resource_control` | No limitation | Read-only [^10] |
| `tidb_enable_slow_log` | Not supported [^4] | Not supported [^4] |
| `tidb_enable_stmt_summary` | No limitation | Read-only [^10] |
| `tidb_enable_telemetry` | Not supported [^4] | Not supported [^4] |
| `tidb_enable_top_sql` | No limitation | Read-only [^10] |
| `tidb_enable_tso_follower_proxy` | No limitation | Read-only [^10] |
| `tidb_expensive_query_time_threshold` | Not supported [^4] | Not supported [^4] |
| `tidb_force_priority` | Not supported [^4] | Not supported [^4] |
| `tidb_gc_concurrency` | No limitation | Read-only [^10] |
| `tidb_gc_enable` | No limitation | Read-only [^10] |
| `tidb_gc_max_wait_time` | No limitation | Read-only [^10] |
| `tidb_gc_run_interval` | No limitation | Read-only [^10] |
| `tidb_gc_scan_lock_mode` | No limitation | Read-only [^10] |
| `tidb_general_log` | Not supported [^4] | Not supported [^4] |
| `tidb_generate_binary_plan` | No limitation | Read-only [^10] |
| `tidb_gogc_tuner_threshold` | No limitation | Read-only [^10] |
| `tidb_guarantee_linearizability` | No limitation | Read-only [^10] |
| `tidb_isolation_read_engines` | No limitation | Read-only [^10] |
| `tidb_log_file_max_days` | No limitation | Read-only [^10] |
| `tidb_memory_usage_alarm_ratio` | Not supported [^4] | Not supported [^4] |
| `tidb_metric_query_range_duration` | Not supported [^4] | Not supported [^4] |
| `tidb_metric_query_step` | Not supported [^4] | Not supported [^4] |
| `tidb_opt_write_row_id` | Not supported [^4] | Not supported [^4] |
| `tidb_placement_mode` | No limitation | Read-only [^10] |
| `tidb_pprof_sql_cpu` | Not supported [^4] | Not supported [^4] |
| `tidb_record_plan_in_slow_log` | Not supported [^4] | Not supported [^4] |
| `tidb_redact_log` | Not supported [^4] | Not supported [^4] |
| `tidb_restricted_read_only` | Not supported [^4] | Not supported [^4] |
| `tidb_row_format_version` | Not supported [^4] | Not supported [^4] |
| `tidb_scatter_region` | No limitation | Read-only [^10] |
| `tidb_server_memory_limit` | No limitation | Read-only [^10] |
| `tidb_server_memory_limit_gc_trigger` | No limitation | Read-only [^10] |
| `tidb_server_memory_limit_sess_min_size` | No limitation | Read-only [^10] |
| `tidb_simplified_metrics` | No limitation | Read-only [^10] |
| `tidb_slow_query_file` | Not supported [^4] | Not supported [^4] |
| `tidb_slow_log_threshold` | Not supported [^4] | Not supported [^4] |
| `tidb_slow_txn_log_threshold` | Not supported [^4] | Not supported [^4] |
| `tidb_stats_load_sync_wait` | No limitation | Read-only [^10] |
| `tidb_stmt_summary_history_size` | No limitation | Read-only [^10] |
| `tidb_stmt_summary_internal_query` | No limitation | Read-only [^10] |
| `tidb_stmt_summary_max_sql_length` | No limitation | Read-only [^10] |
| `tidb_stmt_summary_max_stmt_count` | No limitation | Read-only [^10] |
| `tidb_stmt_summary_refresh_interval` | No limitation | Read-only [^10] |
| `tidb_sysproc_scan_concurrency` | No limitation | Read-only [^10] |
| `tidb_top_sql_max_meta_count` | Not supported [^4] | Not supported [^4] |
| `tidb_top_sql_max_time_series_count` | Not supported [^4] | Not supported [^4] |
| `tidb_tso_client_batch_max_wait_time` | No limitation | Read-only [^10] |
| `tidb_ttl_delete_batch_size` | No limitation | Read-only [^10] |
| `tidb_ttl_delete_rate_limit` | No limitation | Read-only [^10] |
| `tidb_ttl_delete_worker_count` | No limitation | Read-only [^10] |
| `tidb_ttl_job_schedule_window_end_time` | No limitation | Read-only [^10] |
| `tidb_ttl_job_schedule_window_start_time` | No limitation | Read-only [^10] |
| `tidb_ttl_running_tasks` | No limitation | Read-only [^10] |
| `tidb_ttl_scan_batch_size` | No limitation | Read-only [^10] |
| `tidb_ttl_scan_worker_count` | No limitation | Read-only [^10] |
| `tidb_txn_mode` | No limitation | Read-only [^10] |
| `tidb_wait_split_region_finish` | No limitation | Read-only [^10] |
| `tidb_wait_split_region_timeout` | No limitation | Read-only [^10] |
| `txn_scope` | No limitation | Read-only [^10] |
| `validate_password.enable` | No limitation | Always enabled [^9] |
| `validate_password.length` | No limitation | At least `8` [^9] |
| `validate_password.mixed_case_count` | No limitation | At least `1` [^9] |
| `validate_password.number_count` | No limitation | At least `1` [^9] |
| `validate_password.policy` | No limitation | Can only be `MEDIUM` or `STRONG` [^9] |
| `validate_password.special_char_count` | No limitation | At least `1` [^9] |
| `wait_timeout` | No limitation | Read-only [^10] |

[^1]: Configuring data placement is not supported on TiDB Cloud Serverless.

[^2]: Configuring resource groups is not supported on TiDB Cloud Serverless.

[^3]: To perform [Back up and Restore](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore-serverless) operations on TiDB Cloud Serverless, you can use the TiDB Cloud console instead.

[^4]: The feature is unavailable in [Security Enhanced Mode (SEM)](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_enhanced_security).

[^5]: To track [Slow Query](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#slow-query) on TiDB Cloud Serverless, you can use the TiDB Cloud console instead.

[^6]: To perform [Statement Analysis](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#statement-analysis) on TiDB Cloud Serverless, you can use the TiDB Cloud console instead.

[^7]: Drainer and Pump are not supported on TiDB Cloud.

[^8]: Plugin is not supported on TiDB Cloud Serverless.

[^9]: TiDB Cloud Serverless enforces strong password policy.

[^10]: The variable is read-only on TiDB Cloud Serverless.
[^11]: TiDB Cloud Serverless does not support downloading the file exported by `PLAN REPLAYER` through `${tidb-server-status-port}` as in the [example](https://docs.pingcap.com/tidb/stable/sql-plan-replayer#examples-of-exporting-cluster-information). Instead, TiDB Cloud Serverless generates a [presigned URL](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html) for you to download the file. Note that this URL remains valid for 10 hours after generation.

[^12]: Not supported. Enabling `require_secure_transport` for TiDB Cloud Dedicated clusters will result in SQL client connection failures.
