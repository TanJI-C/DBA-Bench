# tidb system variables: service scope through stats load timeout

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_service_scope <span class="version-mark">New in v7.4.0</span> | System Variables > Variable reference > tidb_session_alias <span class="version-mark">New in v7.4.0</span> | System Variables > Variable reference > tidb_session_plan_cache_size <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > tidb_shard_allocate_step <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_simplified_metrics | System Variables > Variable reference > tidb_skip_ascii_check <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_skip_isolation_level_check | System Variables > Variable reference > tidb_skip_missing_partition_stats <span class="version-mark">New in v7.3.0</span> | System Variables > Variable reference > tidb_skip_utf8_check | System Variables > Variable reference > tidb_slow_log_threshold | System Variables > Variable reference > tidb_slow_query_file | System Variables > Variable reference > tidb_slow_txn_log_threshold <span class="version-mark">New in v7.0.0</span> | System Variables > Variable reference > tidb_snapshot | System Variables > Variable reference > tidb_source_id <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_stats_cache_mem_quota <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_stats_load_pseudo_timeout <span class="version-mark">New in v5.4.0</span>`
- Source Line Ranges: `5170-5370`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`, `sql`, `tikv`, `ticdc`
- Topic Tags: `system-variables`, `service-scope`, `session-alias`, `plan-cache`, `auto-random`, `metrics`, `ascii-validation`, `isolation-levels`, `partition-stats`, `utf8-validation`, `slow-log`, `slow-query`, `slow-transaction`, `snapshot-reads`, `bidirectional-replication`, `statistics-cache`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0741_bac9a62d42`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-service-scope-span-class-version-mark-new-in-v7-4-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6370c6693756cf2aef66ef5f8b0cc2acd325d71338c62e2e75b49ea1b7cb6f8f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-service-scope-span-class-version-mark-new-in-v7-4-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variable reference details for variables from tidb_service_scope through tidb_stats_load_pseudo_timeout, including scope, defaults, ranges, and behavior.
- Retrieval Keywords: tidb_service_scope, tidb_session_alias, tidb_session_plan_cache_size, tidb_shard_allocate_step, tidb_simplified_metrics, tidb_skip_ascii_check, tidb_skip_isolation_level_check, tidb_skip_missing_partition_stats, tidb_skip_utf8_check, tidb_slow_log_threshold, tidb_slow_query_file, tidb_slow_txn_log_threshold, tidb_snapshot, tidb_source_id, tidb_stats_cache_mem_quota, tidb_stats_load_pseudo_timeout, SET_VAR, DXF, prepared plan cache, non-prepared plan cache, AUTO_RANDOM, SHARD_ROW_ID_BITS, INFORMATION_SCHEMA.SLOW_QUERY, slow query log, tx_isolation, ERROR 8048 (HY000), dynamic pruning mode, GlobalStats, pseudo statistics, bi-directional replication
- Follow-up Guidance: The content includes the tx_isolation serializable example with ERROR 8048 (HY000) and points to Task scheduling, Identify Slow Queries, and related feature pages for DXF, plan cache, partitioned tables, and bi-directional replication.
- Classification Note: The supplied content is reference material because it enumerates system variables and their exact scope, persistence, type, default value, range, and documented effect.

## Official Source Content

### tidb_service_scope New in v7.4.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: ""
- Optional value: a string with a length of up to 64 characters. Valid characters include digits `0-9`, letters `a-zA-Z`, underscores `_`, and hyphens `-`.
- This variable is an instance-level system variable. You can use it to control the service scope of each TiDB node under the [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework). The DXF determines which TiDB nodes can be scheduled to execute distributed tasks based on the value of this variable. For specific rules, see [Task scheduling](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework#task-scheduling).
### tidb_session_alias New in v7.4.0

- Scope: SESSION
- Persists to cluster: No
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: ""
- You can use this variable to customize the value of the `session_alias` column in the logs related to the current session, which helps identify the session in troubleshooting. This setting affects the logs of multiple nodes involved in the statement execution (including TiKV). The maximum length of this variable is limited to 64 characters, and any characters exceeding the length will be truncated automatically. Spaces at the end of the value will also be removed automatically.
### tidb_session_plan_cache_size New in v7.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `100`
- Range: `[1, 100000]`
- This variable controls the maximum number of plans that can be cached. [Prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache) and [non-prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache) share the same cache.
- When you upgrade from an earlier version to a v7.1.0 or later version, this variable remains the same value as [`tidb_prepared_plan_cache_size`](#tidb_prepared_plan_cache_size-new-in-v610)
### tidb_shard_allocate_step New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `9223372036854775807`
- Range: `[1, 9223372036854775807]`
- This variable controls the maximum number of continuous IDs to be allocated for the [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/auto-random) or [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/shard-row-id-bits) attribute. Generally, `AUTO_RANDOM` IDs or the `SHARD_ROW_ID_BITS` annotated row IDs are incremental and continuous in one transaction. You can use this variable to solve the hotspot issue in large transaction scenarios.
### tidb_simplified_metrics

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- When this variable is enabled, TiDB does not collect or record the metrics that are not used in the Grafana panels.
### tidb_skip_ascii_check New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to set whether to skip ASCII validation.
- Validating ASCII characters affects the performance. When you are sure that the input characters are valid ASCII characters, you can set the variable value to `ON`.
### tidb_skip_isolation_level_check

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- After this switch is enabled, if an isolation level unsupported by TiDB is assigned to `tx_isolation`, no error is reported. This helps improve compatibility with applications that set (but do not depend on) a different isolation level.

```sql
tidb> set tx_isolation='serializable';
ERROR 8048 (HY000): The isolation level 'serializable' is not supported. Set tidb_skip_isolation_level_check=1 to skip this error
tidb> set tidb_skip_isolation_level_check=1;
Query OK, 0 rows affected (0.00 sec)

tidb> set tx_isolation='serializable';
Query OK, 0 rows affected, 1 warning (0.00 sec)
```
### tidb_skip_missing_partition_stats New in v7.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- When accessing a partitioned table in [dynamic pruning mode](https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode), TiDB aggregates the statistics of each partition to generate GlobalStats. This variable controls the generation of GlobalStats when partition statistics are missing.

    - If this variable is `ON`, TiDB skips missing partition statistics when generating GlobalStats so the generation of GlobalStats is not affected.
    - If this variable is `OFF`, TiDB stops generating GlobalStats when it detects any missing partition statistics.
### tidb_skip_utf8_check

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to set whether to skip UTF-8 validation.
- Validating UTF-8 characters affects the performance. When you are sure that the input characters are valid UTF-8 characters, you can set the variable value to `ON`.

> **Note:**
>
> If the character check is skipped, TiDB might fail to detect illegal UTF-8 characters written by the application, cause decoding errors when `ANALYZE` is executed, and introduce other unknown encoding issues. If your application cannot guarantee the validity of the written string, it is not recommended to skip the character check.
### tidb_slow_log_threshold

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `300`
- Range: `[-1, 9223372036854775807]`
- Unit: Milliseconds
- This variable outputs the threshold value of the time consumed by the slow log, and is set to 300 milliseconds by default. When the time consumed by a query is larger than this value, this query is considered as a slow query and its log is output to the slow query log. Note that when the output level of [`log.level`](https://docs.pingcap.com/tidb/v8.1/tidb-configuration-file#level) is `"debug"`, all queries are recorded in the slow query log, regardless of the setting of this variable.
### tidb_slow_query_file

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- When `INFORMATION_SCHEMA.SLOW_QUERY` is queried, only the slow query log name set by `slow-query-file` in the configuration file is parsed. The default slow query log name is "tidb-slow.log". To parse other logs, set the `tidb_slow_query_file` session variable to a specific file path, and then query `INFORMATION_SCHEMA.SLOW_QUERY` to parse the slow query log based on the set file path.

For details, see [Identify Slow Queries](https://docs.pingcap.com/tidb/stable/identify-slow-queries).
### tidb_slow_txn_log_threshold New in v7.0.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Unsigned integer
- Default value: `0`
- Range: `[0, 9223372036854775807]`
- Unit: Milliseconds
- This variable sets the threshold for slow transaction logging. When the execution time of a transaction exceeds this threshold, TiDB logs detailed information about the transaction. When the value is set to `0`, this feature is disabled.
### tidb_snapshot

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- This variable is used to set the time point at which the data is read by the session. For example, when you set the variable to "2017-11-11 20:20:20" or a TSO number like "400036290571534337", the current session reads the data of this moment.
### tidb_source_id New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1`
- Range: `[1, 15]`

- This variable is used to configure the different cluster IDs in a [bi-directional replication](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-bidirectional-replication) cluster.

- This variable is used to configure the different cluster IDs in a [bi-directional replication](https://docs.pingcap.com/tidb/stable/ticdc-bidirectional-replication) cluster.
### tidb_stats_cache_mem_quota New in v6.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Unit: Byte
- Default value: `0`, which means that the memory quota is automatically set to half of the total memory size of the TiDB instance.
- Range: `[0, 1099511627776]`
- This variable sets the memory quota for the TiDB statistics cache.
### tidb_stats_load_pseudo_timeout New in v5.4.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls how TiDB behaves when the waiting time of SQL optimization reaches the timeout to synchronously load complete column statistics. The default value `ON` means that the SQL optimization gets back to using pseudo statistics after the timeout. If this variable to `OFF`, SQL execution fails after the timeout.
