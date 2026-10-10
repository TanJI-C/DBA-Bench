# TiDB enablement and behavior system variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_enable_exchange_partition | System Variables > Variable reference > tidb_enable_extended_stats | System Variables > Variable reference > tidb_enable_external_ts_read <span class="version-mark">New in v6.4.0</span> | System Variables > Variable reference > tidb_external_ts <span class="version-mark">New in v6.4.0</span> | System Variables > Variable reference > tidb_enable_fast_analyze | System Variables > Variable reference > tidb_enable_fast_table_check <span class="version-mark">New in v7.2.0</span> | System Variables > Variable reference > tidb_enable_foreign_key <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_enable_gc_aware_memory_track | System Variables > Variable reference > tidb_enable_global_index <span class="version-mark">New in v7.6.0</span> | System Variables > Variable reference > tidb_enable_non_prepared_plan_cache | System Variables > Variable reference > tidb_enable_non_prepared_plan_cache_for_dml <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > tidb_enable_gogc_tuner <span class="version-mark">New in v6.4.0</span> | System Variables > Variable reference > tidb_enable_historical_stats | System Variables > Variable reference > tidb_enable_historical_stats_for_capture | System Variables > Variable reference > tidb_enable_index_merge <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_enable_index_merge_join | System Variables > Variable reference > tidb_enable_legacy_instance_scope <span class="version-mark">New in v6.0.0</span> | System Variables > Variable reference > tidb_enable_list_partition <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_enable_local_txn | System Variables > Variable reference > tidb_enable_metadata_lock <span class="version-mark">New in v6.3.0</span>`
- Source Line Ranges: `2048-2274`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `cloud`
- Topic Tags: `system-variables`, `feature-flags`, `optimizer`, `statistics`, `plan-cache`, `ddl`, `partitioning`, `foreign-key`, `historical-stats`, `metadata-lock`, `read-timestamp`, `memory-tracking`, `experimental`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0720_b8bb1b8058`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-enable-exchange-partition`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a4503fbfa751fbc865158c4952a6e5f80b72e81c5aca5c76352f52555b3cd563`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-enable-exchange-partition
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the meanings, scope, defaults, deprecation or warning notes, and feature control behavior of TiDB system variables such as tidb_enable_exchange_partition, tidb_enable_extended_stats, tidb_enable_external_ts_read, tidb_external_ts, tidb_enable_fast_analyze, tidb_enable_fast_table_check, tidb_enable_foreign_key, tidb_enable_gc_aware_memory_track, tidb_enable_global_index, tidb_enable_non_prepared_plan_cache, tidb_enable_non_prepared_plan_cache_for_dml, tidb_enable_gogc_tuner, tidb_enable_historical_stats, tidb_enable_historical_stats_for_capture, tidb_enable_index_merge, tidb_enable_index_merge_join, tidb_enable_legacy_instance_scope, tidb_enable_list_partition, tidb_enable_local_txn, and tidb_enable_metadata_lock.
- Retrieval Keywords: tidb_enable_exchange_partition, exchange partitions with tables, tidb_enable_extended_stats, extended statistics, tidb_enable_external_ts_read, tidb_external_ts, external timestamp read, tidb_enable_fast_analyze, Fast Analyze, tidb_enable_fast_table_check, ADMIN CHECK TABLE, ADMIN CHECK INDEX, tidb_enable_foreign_key, FOREIGN KEY, tidb_enable_gc_aware_memory_track, GC-Aware memory track, tidb_enable_global_index, Global indexes, partitioned tables, tidb_enable_non_prepared_plan_cache, Non-prepared plan cache, tidb_enable_non_prepared_plan_cache_for_dml, DML statements, tidb_enable_gogc_tuner, GOGC Tuner, tidb_enable_historical_stats, historical statistics, tidb_enable_historical_stats_for_capture, PLAN REPLAYER CAPTURE, tidb_enable_index_merge, index merge, tidb_enable_index_merge_join, IndexMergeJoin, tidb_enable_legacy_instance_scope, INSTANCE scoped variables, SET SESSION, SET GLOBAL, tidb_enable_list_partition, LIST (COLUMNS) TABLE PARTITION, tidb_enable_local_txn, unreleased feature, tidb_enable_metadata_lock, Metadata lock, running DDL statements
- Follow-up Guidance: This chunk also points to related features and statements including SET_VAR, Introduction to Extended Statistics, exchange partitions with tables, ADMIN CHECK [TABLE|INDEX], Non-prepared plan cache, PLAN REPLAYER CAPTURE, LIST (COLUMNS) TABLE PARTITION, and Metadata lock.
- Classification Note: This is reference content because it enumerates TiDB system variables with their scope, persistence, hint applicability, type, default value, and official cautions or deprecation notes.

## Official Source Content

### tidb_enable_exchange_partition

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to enable the [`exchange partitions with tables`](https://docs.pingcap.com/tidb/stable/partitioned-table#partition-management) feature. The default value is `ON`, that is, `exchange partitions with tables` is enabled by default.
- This variable is deprecated since v6.3.0. Its value will be fixed to the default value `ON`, that is, `exchange partitions with tables` is enabled by default.
### tidb_enable_extended_stats

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable indicates whether TiDB can collect the extended statistic to guide the optimizer. See [Introduction to Extended Statistics](https://docs.pingcap.com/tidb/stable/extended-statistics) for more information.
### tidb_enable_external_ts_read New in v6.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- If this variable is set to `ON`, TiDB reads data with the timestamp specified by [`tidb_external_ts`](#tidb_external_ts-new-in-v640).
### tidb_external_ts New in v6.4.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- If [`tidb_enable_external_ts_read`](#tidb_enable_external_ts_read-new-in-v640) is set to `ON`, TiDB reads data with the timestamp specified by this variable.
### tidb_enable_fast_analyze

> **Warning:**
>
> Starting from v7.5.0, this variable is deprecated.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to set whether to enable the statistics `Fast Analyze` feature.
- If the statistics `Fast Analyze` feature is enabled, TiDB randomly samples about 10,000 rows of data as statistics. When the data is distributed unevenly or the data size is small, the statistics accuracy is low. This might lead to a non-optimal execution plan, for example, selecting a wrong index. If the execution time of the regular `Analyze` statement is acceptable, it is recommended to disable the `Fast Analyze` feature.
### tidb_enable_fast_table_check New in v7.2.0

> **Note:**
>
> This variable does not work for [multi-valued indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#multi-valued-indexes) and prefix indexes.

- Scope: SESSION | GLOBAL
- Persists to the cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to use a checksum-based approach to quickly check the integrity of data and indexes in a table. The default value `ON` means this feature is enabled by default.
- When this variable is enabled, TiDB can execute the [`ADMIN CHECK [TABLE|INDEX]`](/sql-statements/sql-statement-admin-check-table-index.md) statement in a faster way.
### tidb_enable_foreign_key New in v6.3.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: Before v6.6.0, the default value is `OFF`. Starting from v6.6.0, the default value is `ON`.
- This variable controls whether to enable the `FOREIGN KEY` feature.
### tidb_enable_gc_aware_memory_track

> **Warning:**
>
> This variable is an internal variable for debugging in TiDB. It might be removed in a future release. **Do not** set this variable.

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enable GC-Aware memory track.
### tidb_enable_global_index New in v7.6.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- Possible values: `OFF`, `ON`
- This variable controls whether to support creating `Global indexes` for partitioned tables. `Global index` is currently in the development stage. **It is not recommended to modify the value of this system variable**.
### tidb_enable_non_prepared_plan_cache

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enable the [Non-prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache) feature.
- Enabling this feature might incur additional memory and CPU overhead and might not be suitable for all situations. Please determine whether to enable this feature according to your actual scenario.
### tidb_enable_non_prepared_plan_cache_for_dml New in v7.1.0

> **Warning:**
>
> The non-prepared execution plan cache for DML statements is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`.
- This variable controls whether to enable the [Non-prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache) feature for DML statements.
### tidb_enable_gogc_tuner New in v6.4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to enable GOGC Tuner.
### tidb_enable_historical_stats

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to enable historical statistics. The default value changes from `OFF` to `ON`, which means that historical statistics are enabled by default.
### tidb_enable_historical_stats_for_capture

> **Warning:**
>
> The feature controlled by this variable is not fully functional in the current TiDB version. Do not change the default value.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether the information captured by `PLAN REPLAYER CAPTURE` includes historical statistics by default. The default value `OFF` means that historical statistics are not included by default.
### tidb_enable_index_merge New in v4.0

> **Note:**
>
> - After upgrading a TiDB cluster from versions earlier than v4.0.0 to v5.4.0 or later, this variable is disabled by default to prevent performance regression due to changes of execution plans.
>
> - After upgrading a TiDB cluster from v4.0.0 or later to v5.4.0 or later, this variable remains the setting before the upgrade.
>
> - Since v5.4.0, for a newly deployed TiDB cluster, this variable is enabled by default.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to enable the index merge feature.
### tidb_enable_index_merge_join

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- Specifies whether to enable the `IndexMergeJoin` operator.
- This variable is used only for the internal operation of TiDB. It is **NOT recommended** to adjust it. Otherwise, data correctness might be affected.
### tidb_enable_legacy_instance_scope New in v6.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable permits `INSTANCE` scoped variables to be set using the `SET SESSION` as well as `SET GLOBAL` syntax.
- This option is enabled by default for compatibility with earlier versions of TiDB.
### tidb_enable_list_partition New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to set whether to enable the `LIST (COLUMNS) TABLE PARTITION` feature.
### tidb_enable_local_txn

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used for an unreleased feature. **Do not change the variable value**.
### tidb_enable_metadata_lock New in v6.3.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to set whether to enable the [Metadata lock](https://docs.pingcap.com/tidb/stable/metadata-lock) feature. Note that when setting this variable, you need to make sure that there are no running DDL statements in the cluster. Otherwise, the data might be incorrect or inconsistent.
