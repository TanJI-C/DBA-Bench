# TiDB and TiFlash limits for chunking, paging, memory, and cache quotas

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_max_bytes_before_tiflash_external_sort <span class="version-mark">New in v7.0.0</span> | System Variables > Variable reference > tidb_max_chunk_size | System Variables > Variable reference > tidb_max_delta_schema_count <span class="version-mark">New in v2.1.18 and v3.0.5</span> | System Variables > Variable reference > tidb_max_paging_size <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_max_tiflash_threads <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_mem_oom_action <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_mem_quota_analyze <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_mem_quota_apply_cache <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_mem_quota_binding_cache <span class="version-mark">New in v6.0.0</span>`
- Source Line Ranges: `3587-3724`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`
- Topic Tags: `system-variables`, `memory-quota`, `oom-action`, `chunk-size`, `paging`, `schema-cache`, `tiflash-spill`, `thread-concurrency`, `analyze`, `binding-cache`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0728_c472e53b21`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-max-bytes-before-tiflash-external-sort-span-class-version-mark-new-in-v7-0-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4da0b3f85f54b1f5566a0c27ed6d2c5801f5739614502cb44f4202d5246e10df`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-max-bytes-before-tiflash-external-sort-span-class-version-mark-new-in-v7-0-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables that control TiFlash TopN or Sort spill thresholds, chunk row limits, schema version cache count, coprocessor paging size, TiFlash execution threads, OOM behavior, ANALYZE memory quota, Apply cache quota, or binding cache memory thresholds.
- Retrieval Keywords: tidb_max_bytes_before_tiflash_external_sort, max_bytes_before_external_sort, TiFlash Spill to Disk, TopN, Sort, spill to disk, tidb_max_chunk_size, tidb_init_chunk_size, chunk size, rows in a chunk, tidb_max_delta_schema_count, schema versions cached, tidb_max_paging_size, coprocessor paging request, RPC count between TiDB and TiKV, full table scan, tidb_max_tiflash_threads, profiles.default.max_threads, tidb_mem_oom_action, tidb_mem_quota_query, CANCEL, LOG, TiDB Memory Control, tidb_mem_quota_analyze, ANALYZE TABLE, auto_analyze, run-auto-analyze, tidb_mem_quota_apply_cache, Apply operator, tidb_mem_quota_binding_cache, admin reload bindings, caching bindings
- Follow-up Guidance: If the binding cache threshold is modified, run `admin reload bindings` to reload bindings and validate the modification.
- Classification Note: This chunk is reference content because it defines variable scope, type, default value, range, units, and behavior for multiple TiDB system variables related to memory, paging, chunking, TiFlash, and cache limits.

## Official Source Content

### tidb_max_bytes_before_tiflash_external_sort New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `-1`
- Range: `[-1, 9223372036854775807]`
- This variable is used to specify the maximum memory usage of the TopN and Sort operators in TiFlash, in bytes. When the memory usage exceeds the specified value, TiFlash triggers the TopN and Sort operators to spill to disk. When the value of this variable is `-1`, TiDB does not pass this variable to TiFlash. Only when the value of this variable is greater than or equal to `0`, TiDB passes this variable to TiFlash. When the value of this variable is `0`, it means that the memory usage is unlimited, that is, TiFlash TopN and Sort operators will not trigger spilling. For details, see [TiFlash Spill to Disk](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-spill-disk).

> **Note:**
>
> - If a TiDB cluster has multiple TiFlash nodes, TopN and Sort are usually distributedly executed on multiple TiFlash nodes. This variable controls the maximum memory usage of the TopN and Sort operators on a single TiFlash node.
> - When this variable is set to `-1`, TiFlash determines the maximum memory usage of the TopN and Sort operators based on the value of its own configuration item [`max_bytes_before_external_sort`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#tiflash-configuration-parameters).

> **Note:**
>
> - If a TiDB cluster has multiple TiFlash nodes, TopN and Sort are usually distributedly executed on multiple TiFlash nodes. This variable controls the maximum memory usage of the TopN and Sort operators on a single TiFlash node.
> - When this variable is set to `-1`, TiFlash determines the maximum memory usage of the TopN and Sort operators based on the value of its own configuration item `max_bytes_before_external_sort`.
### tidb_max_chunk_size

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1024`
- Range: `[32, 2147483647]`
- Unit: Rows
- This variable is used to set the maximum number of rows in a chunk during the execution process. Setting to too large of a value may cause cache locality issues. The recommended value for this variable is no larger than 65536. The number of rows for a chunk directly affects the amount of memory required for a single query. You can roughly estimate the memory needed for a single chunk by considering the total width of all columns in the query and the number of rows for the chunk. Combining this with the concurrency of the executor, you can make a rough estimation of the total memory required for a single query. It is recommended that the total memory for a single chunk does not exceed 16 MiB. When the query involves a large amount of data and a single chunk is insufficient to handle all the data, TiDB processes it multiple times, doubling the chunk size with each processing iteration, starting from [`tidb_init_chunk_size`](#tidb_init_chunk_size) until the chunk size reaches the value of `tidb_max_chunk_size`.
### tidb_max_delta_schema_count New in v2.1.18 and v3.0.5

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1024`
- Range: `[100, 16384]`
- This variable is used to set the maximum number of schema versions (the table IDs modified for corresponding versions) allowed to be cached. The value range is 100 ~ 16384.
### tidb_max_paging_size New in v6.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `50000`
- Range: `[1, 9223372036854775807]`
- Unit: Rows
- This variable is used to set the maximum number of rows during the coprocessor paging request process. Setting it to too small a value increases the RPC count between TiDB and TiKV, while setting it to too large a value results in excessive memory usage in some cases, such as loading data and full table scan. The default value of this variable brings better performance in OLTP scenarios than in OLAP scenarios. If the application only uses TiKV as the storage engine, consider increasing the value of this variable when executing OLAP workload queries, which might bring you better performance.
### tidb_max_tiflash_threads New in v6.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `[-1, 256]`
- Unit: Threads
- This variable is used to set the maximum concurrency for TiFlash to execute a request. The default value is `-1`, indicating that this system variable is invalid and the maximum concurrency depends on the setting of the TiFlash configuration `profiles.default.max_threads`. When the value is `0`, the maximum number of threads is automatically configured by TiFlash.
### tidb_mem_oom_action New in v6.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `CANCEL`
- Possible values: `CANCEL`, `LOG`

- Specifies what operation TiDB performs when a single SQL statement exceeds the memory quota specified by `tidb_mem_quota_query` and cannot be spilled over to disk. See [TiDB Memory Control](https://docs.pingcap.com/tidb/stable/configure-memory-usage) for details.

- Specifies what operation TiDB performs when a single SQL statement exceeds the memory quota specified by [`tidb_mem_quota_query`](#tidb_mem_quota_query) and cannot be spilled over to disk.

- The default value is `CANCEL`, but in TiDB v4.0.2 and earlier versions, the default value is `LOG`.
- This setting was previously a `tidb.toml` option (`oom-action`), but changed to a system variable starting from TiDB v6.1.0.
### tidb_mem_quota_analyze New in v6.1.0

> **Warning:**
>
> Currently, the `ANALYZE` memory quota is an experimental feature, and the memory statistics might be inaccurate in production environments.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `[-1, 9223372036854775807]`
- Unit: Bytes
- This variable controls the maximum memory usage of TiDB updating statistics. Such a memory usage occurs when you manually execute [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) and when TiDB automatically analyzes tasks in the background. When the total memory usage exceeds this threshold, user-executed `ANALYZE` will exit, and an error message is reported that reminds you to try a lower sampling rate or retry later. If the automatic task in the TiDB background exits because the memory threshold is exceeded, and the sampling rate used is higher than the default value, TiDB will retry the update using the default sampling rate. When this variable value is negative or zero, TiDB does not limit the memory usage of both the manual and automatic update tasks.

> **Note:**
>
> `auto_analyze` will be triggered in a TiDB cluster only when `run-auto-analyze` is enabled in the TiDB startup configuration file.
### tidb_mem_quota_apply_cache New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `33554432` (32 MiB)
- Range: `[0, 9223372036854775807]`
- Unit: Bytes
- This variable is used to set the memory usage threshold of the local cache in the `Apply` operator.
- The local cache in the `Apply` operator is used to speed up the computation of the `Apply` operator. You can set the variable to `0` to disable the `Apply` cache feature.
### tidb_mem_quota_binding_cache New in v6.0.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `67108864`
- Range: `[0, 2147483647]`
- Unit: Bytes
- This variable is used to set the threshold of the memory used for caching bindings.
- If a system creates or captures excessive bindings, resulting in overuse of memory space, TiDB returns a warning in the log. In this case, the cache cannot hold all available bindings or determine which bindings to store. For this reason, some queries might miss their bindings. To address this problem, you can increase the value of this variable, which increases the memory used for caching bindings. After modifying this parameter, you need to run `admin reload bindings` to reload bindings and validate the modification.
