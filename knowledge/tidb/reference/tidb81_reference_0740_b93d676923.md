# TiDB system variables for request source, runtime filter, schema cache, and memory limits

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_request_source_type <span class="version-mark">New in v7.4.0</span> | System Variables > Variable reference > tidb_retry_limit | System Variables > Variable reference > tidb_row_format_version | System Variables > Variable reference > tidb_runtime_filter_mode <span class="version-mark">New in v7.2.0</span> | System Variables > Variable reference > tidb_runtime_filter_type <span class="version-mark">New in v7.2.0</span> | System Variables > Variable reference > tidb_scatter_region | System Variables > Variable reference > tidb_schema_cache_size <span class="version-mark">New in v8.0.0</span> | System Variables > Variable reference > tidb_schema_version_cache_limit <span class="version-mark">New in v7.4.0</span> | System Variables > Variable reference > tidb_server_memory_limit <span class="version-mark">New in v6.4.0</span> | System Variables > Variable reference > tidb_server_memory_limit_gc_trigger <span class="version-mark">New in v6.4.0</span> | System Variables > Variable reference > tidb_server_memory_limit_sess_min_size <span class="version-mark">New in v6.4.0</span>`
- Source Line Ranges: `5031-5169`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `tiflash`, `br`, `lightning`
- Topic Tags: `system-variables`, `resource-control`, `optimistic-transactions`, `row-format`, `runtime-filter`, `region-scatter`, `schema-cache`, `stale-read`, `memory-limit`, `gc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0740_b93d676923`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-request-source-type-span-class-version-mark-new-in-v7-4-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5b36cb4824836a04389791f0f3296272def970123a2e76e8796a28ad817fc5d9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-request-source-type-span-class-version-mark-new-in-v7-4-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables related to request source type, optimistic transaction retries, row format version, runtime filter settings, region scattering, schema cache limits, stale read schema version caching, and TiDB instance memory limit behavior.
- Retrieval Keywords: tidb_request_source_type, Resource Control, SET @@tidb_request_source_type = "background", tidb_retry_limit, optimistic transactions, automatic retry, tidb_row_format_version, new storage row format, version 1, version 2, tidb_runtime_filter_mode, Runtime Filter, Filter Sender operator, Filter Receiver operator, LOCAL, OFF, tidb_runtime_filter_type, IN, tidb_scatter_region, CREATE TABLE, SHARD_ROW_ID_BITS, PRE_SPLIT_REGIONS, tidb_schema_cache_size, schema cache, LRU, partitioned tables, DROP PARTITION, TRUNCATE, tidb_schema_version_cache_limit, Stale Read, historical schema versions, schema cache misses, tidb_server_memory_limit, tidb_server_memory_limit_gc_trigger, tidb_server_memory_limit_sess_min_size, Golang GC, highest memory usage, 80%, 70%, 128 MiB
- Follow-up Guidance: The content points to related topics for Resource Control, Runtime Filter mode and type, Stale Read, and the SET_VAR optimizer hint applicability of each variable.
- Classification Note: This is reference content because it defines the scope, default values, ranges, possible values, and behavior of multiple TiDB system variables.

## Official Source Content

### tidb_request_source_type New in v7.4.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: `""`
- Possible values: `"ddl"`, `"stats"`, `"br"`, `"lightning"`, `"background"`
- This variable is used to explicitly specify the task type for the current session, which is identified and controlled by [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control). For example: `SET @@tidb_request_source_type = "background"`.
### tidb_retry_limit

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `10`
- Range: `[-1, 9223372036854775807]`
- This variable is used to set the maximum number of the retries for optimistic transactions. When a transaction encounters retryable errors (such as transaction conflicts, very slow transaction commit, or table schema changes), this transaction is re-executed according to this variable. Note that setting `tidb_retry_limit` to `0` disables the automatic retry. This variable only applies to optimistic transactions, not to pessimistic transactions.
### tidb_row_format_version

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `2`
- Range: `[1, 2]`
- Controls the format version of the newly saved data in the table. In TiDB v4.0, the [new storage row format](https://github.com/pingcap/tidb/blob/release-8.1/docs/design/2018-07-19-row-format.md) version `2` is used by default to save new data.
- If you upgrade from a TiDB version earlier than v4.0.0 to v4.0.0 or later versions, the format version is not changed, and TiDB continues to use the old format of version `1` to write data to the table, which means that **only newly created clusters use the new data format by default**.
- Note that modifying this variable does not affect the old data that has been saved, but applies the corresponding version format only to the newly written data after modifying this variable.
### tidb_runtime_filter_mode New in v7.2.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Enumeration
- Default value: `OFF`
- Possible values: `OFF`, `LOCAL`
- Controls the mode of Runtime Filter, that is, the relationship between the **Filter Sender operator** and **Filter Receiver operator**. There are two modes: `OFF` and `LOCAL`. `OFF` means disabling Runtime Filter. `LOCAL` means enabling Runtime Filter in the local mode. For more information, see [Runtime Filter mode](https://docs.pingcap.com/tidb/stable/runtime-filter#runtime-filter-mode).
### tidb_runtime_filter_type New in v7.2.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Enumeration
- Default value: `IN`
- Possible values: `IN`
- Controls the type of predicate used by the generated Filter operator. Currently, only one type is supported: `IN`. For more information, see [Runtime Filter type](https://docs.pingcap.com/tidb/stable/runtime-filter#runtime-filter-type).
### tidb_scatter_region

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- By default, Regions are split for a new table when it is being created in TiDB. After this variable is enabled, the newly split Regions are scattered immediately during the execution of the `CREATE TABLE` statement. This applies to the scenario where data need to be written in batches right after the tables are created in batches, because the newly split Regions can be scattered in TiKV beforehand and do not have to wait to be scheduled by PD. To ensure the continuous stability of writing data in batches, the `CREATE TABLE` statement returns success only after the Regions are successfully scattered. This makes the statement's execution time multiple times longer than that when you disable this variable.
- Note that if `SHARD_ROW_ID_BITS` and `PRE_SPLIT_REGIONS` have been set when a table is created, the specified number of Regions are evenly split after the table creation.
### tidb_schema_cache_size New in v8.0.0

> **Warning:**
>
> The feature controlled by this variable is not yet effective in the current TiDB version. Do not change the default value.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 9223372036854775807]`
- This variable controls the size of the schema cache in TiDB. The unit is byte. The default value is `0`, which means that the cache limit feature is not enabled. When this feature is enabled, TiDB uses the value you set as the maximum available memory limit, and uses the Least Recently Used (LRU) algorithm to cache the required tables, effectively reducing the memory occupied by the schema information.
- If your cluster contains a large number of partitioned tables, or if you frequently perform DDL operations on partitioned tables (such as `TRUNCATE` or `DROP PARTITION`), it is recommended that you set this variable to `0`.
### tidb_schema_version_cache_limit New in v7.4.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `16`
- Range: `[2, 255]`
- This variable limits how many historical schema versions can be cached in a TiDB instance. The default value is `16`, which means that TiDB caches 16 historical schema versions by default.
- Generally, you do not need to modify this variable. When the [Stale Read](https://docs.pingcap.com/tidb/stable/stale-read) feature is used and DDL operations are executed very frequently, it will cause the schema version to change very frequently. Consequently, when Stale Read tries to obtain schema information from a snapshot, it might take a lot of time to rebuild the information due to schema cache misses. In this case, you can increase the value of `tidb_schema_version_cache_limit` (for example, `32`) to avoid the problem of schema cache misses.
- Modifying this variable causes the memory usage of TiDB to increase slightly. Monitor the memory usage of TiDB to avoid OOM problems.
### tidb_server_memory_limit New in v6.4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `80%`
- Range:
    - You can set the value in the percentage format, which means the percentage of the memory usage relative to the total memory. The value range is `[1%, 99%]`.
    - You can also set the value in memory size. The value range is `0` and `[536870912, 9223372036854775807]` in bytes. The memory format with the units "KiB|MiB|GiB|TiB" is supported. `0` means no memory limit.
    - If this variable is set to a memory size that is less than 512 MiB but not `0`, TiDB uses 512 MiB as the actual size.
- This variable specifies the memory limit for a TiDB instance. When the memory usage of TiDB reaches the limit, TiDB cancels the currently running SQL statement with the highest memory usage. After the SQL statement is successfully canceled, TiDB tries to call Golang GC to immediately reclaim memory to relieve memory stress as soon as possible.
- Only the SQL statements with more memory usage than the [`tidb_server_memory_limit_sess_min_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit_sess_min_size-new-in-v640) limit are selected as the SQL statements to be canceled first.
- Currently, TiDB cancels only one SQL statement at a time. After TiDB completely cancels a SQL statement and recovers resources, if the memory usage is still greater than the limit set by this variable, TiDB starts the next cancel operation.
### tidb_server_memory_limit_gc_trigger New in v6.4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `70%`
- Range: `[50%, 99%]`
- The threshold at which TiDB tries to trigger GC. When the memory usage of TiDB reaches the value of `tidb_server_memory_limit` \* the value of `tidb_server_memory_limit_gc_trigger`, TiDB will actively trigger a Golang GC operation. Only one GC operation will be triggered in one minute.
### tidb_server_memory_limit_sess_min_size New in v6.4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `134217728` (which is 128 MiB)
- Range: `[128, 9223372036854775807]`, in bytes. The memory format with the units "KiB|MiB|GiB|TiB" is also supported.
- After you enable the memory limit, TiDB will terminate the SQL statement with the highest memory usage on the current instance. This variable specifies the minimum memory usage of the SQL statement to be terminated. If the memory usage of a TiDB instance that exceeds the limit is caused by too many sessions with low memory usage, you can properly lower the value of this variable to allow more sessions to be canceled.
