# Transaction info, binding, locking, logging, TSO, and auto analyze variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_last_txn_info <span class="version-mark">New in v4.0.9</span> | System Variables > Variable reference > tidb_last_plan_replayer_token <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_load_based_replica_read_threshold <span class="version-mark">New in v7.0.0</span> | System Variables > Variable reference > `tidb_load_binding_timeout` <span class="version-mark">New in v8.0.0</span> | System Variables > Variable reference > `tidb_lock_unchanged_keys` <span class="version-mark">New in v7.1.1 and v7.3.0</span> | System Variables > Variable reference > tidb_log_file_max_days <span class="version-mark">New in v5.3.0</span> | System Variables > Variable reference > tidb_low_resolution_tso | System Variables > Variable reference > `tidb_low_resolution_tso_update_interval` <span class="version-mark">New in v8.0.0</span> | System Variables > Variable reference > tidb_max_auto_analyze_time <span class="version-mark">New in v6.1.0</span>`
- Source Line Ranges: `3406-3530`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `sql`
- Topic Tags: `system-variables`, `transactions`, `plan-replayer`, `replica-read`, `bindings`, `locking`, `logging`, `tso`, `auto-analyze`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0726_294aad9d1b`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-last-txn-info-span-class-version-mark-new-in-v4-0-9-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `77bc71ea9e2cf7d9f3b1eb2b403e254183c5ced2aa1e77ff779b9798d6d87398`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-last-txn-info-span-class-version-mark-new-in-v4-0-9-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables for last transaction info, PLAN REPLAYER DUMP result token, load-based replica read threshold, binding load timeout, unchanged key locking, log retention days, low-precision TSO, low-resolution TSO update interval, or automatic ANALYZE execution time limits.
- Retrieval Keywords: tidb_last_txn_info, last transaction information, transaction scope, start and commit TS, two-phase, one-phase, async commit, tidb_last_plan_replayer_token, PLAN REPLAYER DUMP, tidb_load_based_replica_read_threshold, load-based replica read, estimated queue time, follower node, tidb_load_binding_timeout, loading bindings timeout, tidb_lock_unchanged_keys, INSERT IGNORE, REPLACE, UPDATE, unique keys not changed, tidb_log_file_max_days, max-days, current TiDB instance, tidb_low_resolution_tso, low-precision TSO, cached timestamp, tidb_low_resolution_tso_update_interval, tidb_max_auto_analyze_time, automatic ANALYZE tasks
- Follow-up Guidance: The content also points to Troubleshoot Hotspot Issues for load-based replica read and to the max-days configuration and tidb_low_resolution_tso_update_interval references for related details.
- Classification Note: This is reference content because it defines variable scope, type, default or range, persistence, and the exact behavior of multiple TiDB system variables.

## Official Source Content

### tidb_last_txn_info New in v4.0.9

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- This variable is used to get the last transaction information within the current session. It is a read-only variable. The transaction information includes:
    - The transaction scope.
    - The start and commit TS.
    - The transaction commit mode, which might be a two-phase, one-phase, or async commit.
    - The information of transaction fallback from async commit or one-phase commit to two-phase commit.
    - The error encountered.
### tidb_last_plan_replayer_token New in v6.3.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- This variable is read-only and is used to obtain the result of the last `PLAN REPLAYER DUMP` execution in the current session.
### tidb_load_based_replica_read_threshold New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `"1s"`
- Range: `[0s, 1h]`
- Type: String
- This variable is used to set the threshold for triggering load-based replica read. When the estimated queue time of the leader node exceeds the threshold, TiDB prioritizes reading data from the follower node. The format is a time duration, such as `"100ms"` or `"1s"`. For more details, see [Troubleshoot Hotspot Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#scatter-read-hotspots).

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `"1s"`
- Range: `[0s, 1h]`
- Type: String
- This variable is used to set the threshold for triggering load-based replica read. When the estimated queue time of the leader node exceeds the threshold, TiDB prioritizes reading data from the follower node. The format is a time duration, such as `"100ms"` or `"1s"`. For more details, see [Troubleshoot Hotspot Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#scatter-read-hotspots).
### `tidb_load_binding_timeout` New in v8.0.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `200`
- Range: `(0, 2147483647]`
- Unit: Milliseconds
- This variable is used to control the timeout of loading bindings. If the execution time of loading bindings exceeds this value, the loading will stop.
### `tidb_lock_unchanged_keys` New in v7.1.1 and v7.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to lock specific keys in the following scenarios. When the value is set to `ON`, these keys are locked. When the value is set to `OFF`, these keys are not locked.
    - Duplicate keys in `INSERT IGNORE` and `REPLACE` statements. Before v6.1.6, these keys were not locked. This issue has been fixed in [#42121](https://github.com/pingcap/tidb/issues/42121).
    - Unique keys in `UPDATE` statements when the values of the keys are not changed. Before v6.5.2, these keys were not locked. This issue has been fixed in [#36438](https://github.com/pingcap/tidb/issues/36438).
- To maintain the consistency and rationality of the transaction, it is not recommended to change this value. If upgrading TiDB causes severe performance issues due to these two fixes, and the behavior without locks is acceptable (see the preceding issues), you can set this variable to `OFF`.
### tidb_log_file_max_days New in v5.3.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 2147483647]`

- This variable is used to set the maximum days that the log is retained on the current TiDB instance. Its value defaults to the value of the [`max-days`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#max-days) configuration in the configuration file. Changing the variable value only affects the current TiDB instance. After TiDB is restarted, the variable value is reset and the configuration value is not affected.

- This variable is used to set the maximum days that the log is retained on the current TiDB instance.
### tidb_low_resolution_tso

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to set whether to enable the low-precision TSO feature. After this feature is enabled, TiDB uses the cached timestamp to read data. The cached timestamp is updated every 2 seconds by default. Starting from v8.0.0, you can configure the update interval by [`tidb_low_resolution_tso_update_interval`](#tidb_low_resolution_tso_update_interval-new-in-v800).
- The main applicable scenario is to reduce the overhead of acquiring TSO for small read-only transactions when reading old data is acceptable.
### `tidb_low_resolution_tso_update_interval` New in v8.0.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `2000`
- Range: `[10, 60000]`
- Unit: Milliseconds
- This variable is used to set the update interval of the cached timestamp used in the low-precision TSO feature, in milliseconds.
- This variable is only available when [`tidb_low_resolution_tso`](#tidb_low_resolution_tso) is enabled.
### tidb_max_auto_analyze_time New in v6.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `43200`
- Range: `[0, 2147483647]`
- Unit: Seconds
- This variable is used to specify the maximum execution time of automatic `ANALYZE` tasks. When the execution time of an automatic `ANALYZE` task exceeds the specified time, the task will be terminated. When the value of this variable is `0`, there is no limit to the maximum execution time of automatic `ANALYZE` tasks.
