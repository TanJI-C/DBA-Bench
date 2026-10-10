# TiFlash, optimizer, statistics, CDC, and utf8 check variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_batch_pending_tiflash_count <span class="version-mark">New in v6.0</span> | System Variables > Variable reference > tidb_broadcast_join_threshold_count <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_broadcast_join_threshold_size <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_build_stats_concurrency | System Variables > Variable reference > tidb_build_sampling_stats_concurrency <span class="version-mark">New in v7.5.0</span> | System Variables > Variable reference > tidb_capture_plan_baselines <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_cdc_write_source <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_check_mb4_value_in_utf8`
- Source Line Ranges: `1322-1417`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `ticdc`, `sql`
- Topic Tags: `tiflash-replica`, `broadcast-join`, `mpp`, `manual-analyze`, `sampling`, `plan-baselines`, `statement-summary`, `cdc`, `utf8-validation`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0163_cf1b8f43e8`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-batch-pending-tiflash-count-span-class-version-mark-new-in-v6-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9fb2bfca06ecf034f446ca86a11cf91e2108470880392e4af48b6ee3d89936e0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-batch-pending-tiflash-count-span-class-version-mark-new-in-v6-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB system variables related to TiFlash replica batching, MPP broadcast join thresholds, manual ANALYZE concurrency, baseline capturing, TiCDC write source tagging, or utf8 BMP enforcement.
- Retrieval Keywords: tidb_batch_pending_tiflash_count, ALTER DATABASE SET TIFLASH REPLICA, tidb_broadcast_join_threshold_count, tidb_broadcast_join_threshold_size, Broadcast Hash Join, Shuffled Hash Join, tidb_prefer_broadcast_join_by_exchange_data_size, tidb_build_stats_concurrency, tidb_build_sampling_stats_concurrency, tidb_capture_plan_baselines, baseline capturing, statement summary, tidb_cdc_write_source, written by TiCDC, Do not manually modify this variable in any case, tidb_check_mb4_value_in_utf8, Basic Multilingual Plane, utf8mb4, FAQs After Upgrade
- Follow-up Guidance: The content adds that baseline capturing depends on statement summary, the broadcast join thresholds do not take effect after tidb_prefer_broadcast_join_by_exchange_data_size is enabled, and tidb_check_mb4_value_in_utf8 might need to be disabled when upgrading from earlier TiDB versions with more relaxed utf8 checking.
- Classification Note: This is classified as configuration because it lists TiDB system variables with scope, defaults, ranges, and behavior across optimizer, statistics, TiFlash, TiCDC, and character set validation topics.

## Official Source Content

### tidb_batch_pending_tiflash_count New in v6.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `4000`
- Range: `[0, 4294967295]`
- Specifies the maximum number of permitted unavailable tables when you use `ALTER DATABASE SET TIFLASH REPLICA` to add TiFlash replicas. If the number of unavailable tables exceeds this limit, the operation will be stopped or setting TiFlash replicas for the remaining tables will be very slow.
### tidb_broadcast_join_threshold_count New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `10240`
- Range: `[0, 9223372036854775807]`
- Unit: Rows
- If the objects of the join operation belong to a subquery, the optimizer cannot estimate the size of the subquery result set. In this situation, the size is determined by the number of rows in the result set. If the estimated number of rows in the subquery is less than the value of this variable, the Broadcast Hash Join algorithm is used. Otherwise, the Shuffled Hash Join algorithm is used.
- This variable will not take effect after [`tidb_prefer_broadcast_join_by_exchange_data_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_prefer_broadcast_join_by_exchange_data_size-new-in-v710) is enabled.
### tidb_broadcast_join_threshold_size New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `104857600` (100 MiB)
- Range: `[0, 9223372036854775807]`
- Unit: Bytes
- If the table size is less than the value of the variable, the Broadcast Hash Join algorithm is used. Otherwise, the Shuffled Hash Join algorithm is used.
- This variable will not take effect after [`tidb_prefer_broadcast_join_by_exchange_data_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_prefer_broadcast_join_by_exchange_data_size-new-in-v710) is enabled.
### tidb_build_stats_concurrency

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `2`. The default value is `4` for v7.4.0 and earlier versions.
- Range: `[1, 256]`
- Unit: Threads
- This variable controls the concurrency for building statistics during manual `ANALYZE`, such as the number of table or partition analysis tasks that can be processed simultaneously.
### tidb_build_sampling_stats_concurrency New in v7.5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Unit: Threads
- Default value: `2`
- Range: `[1, 256]`
- This variable controls the following aspects of `ANALYZE` concurrency:
    - The concurrency for merging samples collected from different Regions.
    - The concurrency for collecting statistics on special indexes (such as indexes on generated virtual columns), for example, the number of indexes that TiDB can concurrently collect statistics for.
### tidb_capture_plan_baselines New in v4.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether to enable the [baseline capturing](https://docs.pingcap.com/tidb/stable/sql-plan-management#baseline-capturing) feature. This feature depends on the statement summary, so you need to enable the statement summary before you use baseline capturing.
- After this feature is enabled, the historical SQL statements in the statement summary are traversed periodically, and bindings are automatically created for SQL statements that appear at least twice.
### tidb_cdc_write_source New in v6.5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: SESSION
- Persists to cluster: No
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 15]`
- When this variable is set to a value other than 0, data written in this session is considered to be written by TiCDC. This variable can only be modified by TiCDC. Do not manually modify this variable in any case.
### tidb_check_mb4_value_in_utf8

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to enforce that the `utf8` character set only stores values from the [Basic Multilingual Plane (BMP)](https://en.wikipedia.org/wiki/Plane_(Unicode)#Basic_Multilingual_Plane). To store characters outside the BMP, it is recommended to use the `utf8mb4` character set.
- You might need to disable this option when upgrading your cluster from an earlier version of TiDB where the `utf8` checking was more relaxed. For details, see [FAQs After Upgrade](https://docs.pingcap.com/tidb/stable/upgrade-faq).
