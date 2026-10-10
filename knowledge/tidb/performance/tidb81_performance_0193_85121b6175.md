# Execution, metrics, paging, and MPP system variables

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_merge_join_concurrency | System Variables > Variable reference > tidb_merge_partition_stats_concurrency | System Variables > Variable reference > tidb_enable_async_merge_global_stats <span class="version-mark">New in v7.5.0</span> | System Variables > Variable reference > tidb_metric_query_range_duration <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_metric_query_step <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_min_paging_size <span class="version-mark">New in v6.2.0</span> | System Variables > Variable reference > tidb_mpp_store_fail_ttl`
- Source Line Ranges: `3820-3899`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`, `shared`
- Topic Tags: `concurrency`, `merge-join`, `statistics`, `metrics-schema`, `prometheus`, `paging`, `coprocessor`, `mpp`, `tiflash`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0193_85121b6175`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-merge-join-concurrency`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5d2557f70606c5a1f626951a2dec441c2e0f537bc1f1234d27b334485860e593`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-merge-join-concurrency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB system variables that control MergeJoin concurrency, partition TopN merge concurrency, asynchronous global statistics merge, METRICS_SCHEMA Prometheus query parameters, coprocessor paging size, or TiFlash MPP request avoidance after node startup.
- Retrieval Keywords: tidb_merge_join_concurrency, MergeJoin operator, tidb_merge_partition_stats_concurrency, merging TopN results of partitioned tables, tidb_enable_async_merge_global_stats, merge global statistics asynchronously, OOM issues, tidb_metric_query_range_duration, tidb_metric_query_step, METRICS_SCHEMA, Prometheus statement, tidb_min_paging_size, coprocessor paging request process, IndexLookup with Limit, tidb_enable_paging, tidb_max_paging_size, tidb_mpp_store_fail_ttl, newly started TiFlash node
- Follow-up Guidance: The content also references tidb_enable_paging and tidb_max_paging_size for paging behavior related to TPCH performance.
- Classification Note: This is classified as performance because the variables tune execution concurrency, statistics merging, metrics query generation, paging behavior, and MPP request routing that affect query execution characteristics.

## Official Source Content

### tidb_merge_join_concurrency

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Range: `[1, 256]`
- Default value: `1`
- This variable sets the concurrency of the `MergeJoin` operator when a query is executed.
- It is **NOT recommended** to set this variable. Modifying the value of this variable might cause data correctness issues.
### tidb_merge_partition_stats_concurrency

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `1`
- This variable controls the concurrency for merging TopN results of partitioned tables.
### tidb_enable_async_merge_global_stats New in v7.5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`. When you upgrade TiDB from a version earlier than v7.5.0 to v7.5.0 or a later version, the default value is `OFF`.
- This variable is used for TiDB to merge global statistics asynchronously to avoid OOM issues.
### tidb_metric_query_range_duration New in v4.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `60`
- Range: `[10, 216000]`
- Unit: Seconds
- This variable is used to set the range duration of the Prometheus statement generated when querying `METRICS_SCHEMA`.
### tidb_metric_query_step New in v4.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `60`
- Range: `[10, 216000]`
- Unit: Seconds
- This variable is used to set the step of the Prometheus statement generated when querying `METRICS_SCHEMA`.
### tidb_min_paging_size New in v6.2.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `128`
- Range: `[1, 9223372036854775807]`
- Unit: Rows
- This variable is used to set the minimum number of rows during the coprocessor paging request process. Setting it to a too small value increases the RPC request count between TiDB and TiKV, while setting it to a too large value might cause a performance decrease when executing queries using IndexLookup with Limit. The default value of this variable brings better performance in OLTP scenarios than in OLAP scenarios. If the application only uses TiKV as the storage engine, consider increasing the value of this variable when executing OLAP workload queries, which might bring you better performance.

![Paging size impact on TPCH](/media/paging-size-impact-on-tpch.png)

As shown in this diagram, when [`tidb_enable_paging`](#tidb_enable_paging-new-in-v540) is enabled, the performance of TPCH is affected by the settings of `tidb_min_paging_size` and [`tidb_max_paging_size`](#tidb_max_paging_size-new-in-v630). The vertical axis is the execution time, and it is the smaller the better.
### tidb_mpp_store_fail_ttl

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Duration
- Default value: `60s`
- The newly started TiFlash node does not provide services. To prevent queries from failing, TiDB limits the tidb-server sending queries to the newly started TiFlash node. This variable indicates the time range in which the newly started TiFlash node is not sent requests.
