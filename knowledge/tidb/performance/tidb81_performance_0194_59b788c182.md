# TiFlash execution, shuffle, memory spilling, and replica read variables

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tiflash_fastscan <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tiflash_fine_grained_shuffle_batch_size <span class="version-mark">New in v6.2.0</span> | System Variables > Variable reference > tiflash_fine_grained_shuffle_stream_count <span class="version-mark">New in v6.2.0</span> | System Variables > Variable reference > tiflash_mem_quota_query_per_node <span class="version-mark">New in v7.4.0</span> | System Variables > Variable reference > tiflash_query_spill_ratio <span class="version-mark">New in v7.4.0</span> | System Variables > Variable reference > tiflash_replica_read <span class="version-mark">New in v7.3.0</span>`
- Source Line Ranges: `6046-6128`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `fastscan`, `window-functions`, `fine-grained-shuffle`, `memory-quota`, `query-spilling`, `replica-selection`, `zone-awareness`, `analytical-queries`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0194_59b788c182`
- Source ID: `tidb-docs-8.1:system-variables.md#tiflash-fastscan-span-class-version-mark-new-in-v6-3-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `62e7c0c976bf2dfa4360c8cc4e734d57fbff3fc77cf14363aa147c973970e307`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tiflash-fastscan-span-class-version-mark-new-in-v6-3-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiFlash system variables for FastScan, fine-grained shuffle execution of window functions, query memory quota and query-level spilling, or TiFlash replica selection strategy.
- Retrieval Keywords: tiflash_fastscan, FastScan, does not guarantee the accuracy of the query results or data consistency, tiflash_fine_grained_shuffle_batch_size, tiflash_fine_grained_shuffle_stream_count, window function pushed down to TiFlash, tidb_max_tiflash_threads, tiflash_mem_quota_query_per_node, tiflash_query_spill_ratio, query-level spilling, tidb_max_bytes_before_tiflash_external_sort, tidb_max_bytes_before_tiflash_external_group_by, tidb_max_bytes_before_tiflash_external_join, tiflash_replica_read, all_replicas, closest_adaptive, closest_replicas, The variable tiflash_replica_read is ignored.
- Follow-up Guidance: The content explains that `tiflash_query_spill_ratio` only takes effect when `tiflash_mem_quota_query_per_node` is greater than `0`, and it also describes warnings and zone-attribute conditions for `tiflash_replica_read`.
- Classification Note: This is classified as performance because the content documents TiFlash variables that directly control query execution efficiency, concurrency, memory limits, spilling thresholds, and replica selection behavior.

## Official Source Content

### tiflash_fastscan New in v6.3.0

- Scope: SESSION | GLOBAL
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: `OFF`
- Type: Boolean
- If [FastScan](https://docs.pingcap.com/tidb/stable/tiflash/use-fastscan) is enabled (set to `ON`), TiFlash provides more efficient query performance, but does not guarantee the accuracy of the query results or data consistency.
### tiflash_fine_grained_shuffle_batch_size New in v6.2.0

- Scope: SESSION | GLOBAL
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: `8192`
- Range: `[1, 18446744073709551615]`
- When Fine Grained Shuffle is enabled, the window function pushed down to TiFlash can be executed in parallel. This variable controls the batch size of the data sent by the sender.
- Impact on performance: set a reasonable size according to your business requirements. Improper setting affects the performance. If the value is set too small, for example `1`, it causes one network transfer per Block. If the value is set too large, for example, the total number of rows of the table, it causes the receiving end to spend most of the time waiting for data, and the pipelined computation cannot work. To set a proper value, you can observe the distribution of the number of rows received by the TiFlash receiver. If most threads receive only a few rows, for example a few hundred, you can increase this value to reduce the network overhead.
### tiflash_fine_grained_shuffle_stream_count New in v6.2.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `0`
- Range: `[-1, 1024]`
- When the window function is pushed down to TiFlash for execution, you can use this variable to control the concurrency level of the window function execution. The possible values are as follows:

    * -1: the Fine Grained Shuffle feature is disabled. The window function pushed down to TiFlash is executed in a single thread.
    * 0: the Fine Grained Shuffle feature is enabled. If [`tidb_max_tiflash_threads`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_tiflash_threads-new-in-v610) is set to a valid value (greater than 0), then `tiflash_fine_grained_shuffle_stream_count` is set to the value of [`tidb_max_tiflash_threads`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_tiflash_threads-new-in-v610). Otherwise, it is automatically estimated based on the CPU resources of the TiFlash compute node. The actual concurrency level of the window function on TiFlash is: min(`tiflash_fine_grained_shuffle_stream_count`, the number of physical threads on TiFlash nodes).
    * Integer greater than 0: the Fine Grained Shuffle feature is enabled. The window function pushed down to TiFlash is executed in multiple threads. The concurrency level is: min(`tiflash_fine_grained_shuffle_stream_count`, the number of physical threads on TiFlash nodes).
- Theoretically, the performance of the window function increases linearly with this value. However, if the value exceeds the actual number of physical threads, it instead leads to performance degradation.
### tiflash_mem_quota_query_per_node New in v7.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[-1, 9223372036854775807]`
- This variable limits the maximum memory usage for a query on a TiFlash node. When the memory usage of a query exceeds this limit, TiFlash returns an error and terminates the query. Setting this variable to `-1` or `0` means no limit. When this variable is set to a value greater than `0` and [`tiflash_query_spill_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_query_spill_ratio-new-in-v740) is set to a valid value, TiFlash enables [query-level spilling](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-spill-disk#query-level-spilling).
### tiflash_query_spill_ratio New in v7.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Float
- Default value: `0.7`
- Range: `[0, 0.85]`
- This variable controls the threshold for TiFlash [query-level spilling](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-spill-disk#query-level-spilling). `0` means disabling the automatic query-level spilling. When this variable is greater than `0` and the memory usage of a query exceeds [`tiflash_mem_quota_query_per_node`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_mem_quota_query_per_node-new-in-v740) * `tiflash_query_spill_ratio`, TiFlash triggers query-level spilling, which spills data of supported operators in the query as needed.

> **Note:**
>
> - This variable only takes effect when [`tiflash_mem_quota_query_per_node`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_mem_quota_query_per_node-new-in-v740) is greater than `0`. In other words, if [tiflash_mem_quota_query_per_node](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_mem_quota_query_per_node-new-in-v740) is `0` or `-1`, query-level spilling will not be enabled even if `tiflash_query_spill_ratio` is greater than `0`.
> - When TiFlash query-level spilling is enabled, the spilling thresholds for individual TiFlash operators automatically become invalidated. In other words, if both [`tiflash_mem_quota_query_per_node`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_mem_quota_query_per_node-new-in-v740) and `tiflash_query_spill_ratio` are greater than 0, the three variables [tidb_max_bytes_before_tiflash_external_sort](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_bytes_before_tiflash_external_sort-new-in-v700), [tidb_max_bytes_before_tiflash_external_group_by](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_bytes_before_tiflash_external_group_by-new-in-v700), and [tidb_max_bytes_before_tiflash_external_join](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_bytes_before_tiflash_external_join-new-in-v700) become invalidated automatically, equivalent to setting them to `0`.
### tiflash_replica_read New in v7.3.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `all_replicas`
- Value options: `all_replicas`, `closest_adaptive`, or `closest_replicas`
- This variable is used to set the strategy for selecting TiFlash replicas when a query requires the TiFlash engine.
    - `all_replicas` means using all available TiFlash replicas for analytical computing.
    - `closest_adaptive` means preferring to use TiFlash replicas in the same zone as the TiDB node initiating the query. If replicas in this zone do not contain all the required data, the query will involve TiFlash replicas from other zones along with their corresponding TiFlash nodes.
    - `closest_replicas` means using only TiFlash replicas in the same zone as the TiDB node initiating the query. If replicas in this zone do not contain all the required data, the query will return an error.

> **Note:**
>
> - If TiDB nodes do not have [zone attributes](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels#optional-configure-labels-for-tidb) configured and `tiflash_replica_read` is not set to `all_replicas`, TiFlash ignores the replica selection strategy. Instead, it uses all TiFlash replicas for queries and returns the `The variable tiflash_replica_read is ignored.` warning.
> - If TiFlash nodes do not have [zone attributes](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels#configure-labels-for-tikv-and-tiflash) configured, they are treated as nodes not belonging to any zone.
