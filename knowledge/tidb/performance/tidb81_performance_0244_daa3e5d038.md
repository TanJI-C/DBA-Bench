# Edge case tuning for TSO, coprocessor cache, and chunk size

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-performance-tuning-config.md`
- Source Title: `Configure TiDB for Optimal Performance`
- Source Heading Path: `Configure TiDB for Optimal Performance > Edge cases and optimizations > Common edge cases | Configure TiDB for Optimal Performance > Edge cases and optimizations > High TSO wait for high-frequency small queries | Configure TiDB for Optimal Performance > Edge cases and optimizations > High TSO wait for high-frequency small queries > Troubleshooting | Configure TiDB for Optimal Performance > Edge cases and optimizations > High TSO wait for high-frequency small queries > Solution 1: low-precision TSO | Configure TiDB for Optimal Performance > Edge cases and optimizations > Tune coprocessor cache for read-heavy workloads | Configure TiDB for Optimal Performance > Edge cases and optimizations > Optimize chunk size for workload characteristics`
- Source Line Ranges: `225-315`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`
- Topic Tags: `edge-cases`, `tso-wait`, `low-precision-tso`, `stale-reads`, `coprocessor-cache`, `read-heavy`, `chunk-size`, `oltp`, `olap`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0244_daa3e5d038`
- Source ID: `tidb-docs-8.1:tidb-performance-tuning-config.md#common-edge-cases`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c8411f06d3491bbc8f29ef3fb505119771cb9bf6b7a839ec9b7e3736885cddd6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-performance-tuning-config#common-edge-cases
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-performance-tuning-config.md

## Retrieval Guidance

- Use When: Use this chunk when you need guidance for self-managed TiDB edge-case performance tuning involving high TSO wait, low-precision TSO, coprocessor cache settings, or tidb_max_chunk_size for OLTP and OLAP workloads.
- Retrieval Keywords: TSO wait, high-frequency small queries, Performance Overview > SQL Execute Time Overview, SQL Execute Time Overview, tidb_low_resolution_tso, low-precision TSO, stale reads, SET GLOBAL tidb_low_resolution_tso=ON, tidb_enable_batch_dml, coprocessor cache, Coprocessor Cache, tikv-client.copr-cache, capacity-mb = 4096, admission-max-ranges = 5000, admission-max-result-mb = 10, admission-min-process-ms = 0, read-heavy workloads, tidb_max_chunk_size, SET GLOBAL tidb_max_chunk_size = 128, SET GLOBAL tidb_max_chunk_size = 4096, OLTP workloads, OLAP workloads, point queries, small range scans, aggregations, large table scans
- Follow-up Guidance: The source says to apply these optimizations carefully and test thoroughly because their effectiveness might vary based on your use case and data patterns.
- Classification Note: This is classified as performance for TiDB with related PD and TiKV components because the content covers query latency, TSO wait, TiKV coprocessor cache tuning, and execution chunk sizing in self-managed deployments.

## Official Source Content

### Common edge cases

The following lists some common edge cases:

- High TSO wait for high-frequency small queries
- Choose the proper max chunk size for different workloads
- Tune coprocessor cache for read-heavy workloads
- Optimize chunk size for workload characteristics
- Optimize transaction mode and DML type for different workloads
- Optimize `GROUP BY` and `DISTINCT` operations with TiKV pushdown
- Optimize statistics collection during batch operations
- Optimize thread pool settings for different instance types

The following sections explain how to handle each of these cases. You need to adjust different parameters or use specific TiDB features for each scenario.

> **Note:**
>
> Apply these optimizations carefully and test thoroughly, as their effectiveness might vary based on your use case and data patterns.
### High TSO wait for high-frequency small queries
#### Troubleshooting

If your workload involves frequent small transactions or queries that frequently request timestamps, TSO (Timestamp Oracle) can become a performance bottleneck. To check if TSO wait time is impacting your system, check the [**Performance Overview > SQL Execute Time Overview**](https://docs.pingcap.com/tidb/stable/grafana-performance-overview-dashboard#sql-execute-time-overview) panel. If TSO wait time constitutes a large portion of your SQL execution time, consider the following optimizations:

- Use low-precision TSO (enable [`tidb_low_resolution_tso`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_low_resolution_tso)) for read operations that do not need strict consistency. For more information, see [Solution 1: use low-precision TSO](#solution-1-low-precision-tso).
- Enable [`tidb_enable_batch_dml`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_batch_dml) to reduce TSO requests for batch operations.
#### Solution 1: low-precision TSO

You can reduce TSO wait time by enabling the low-precision TSO feature ([`tidb_low_resolution_tso`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_low_resolution_tso)). After this feature is enabled, TiDB uses the cached timestamp to read data, reducing TSO wait time at the expense of potentially stale reads.

This optimization is particularly effective in the following scenarios:

- Read-heavy workloads where slight staleness is acceptable.
- Scenarios where reducing query latency is more important than absolute consistency.
- Applications that can tolerate reads that are a few seconds behind the latest committed state.

Benefits and trade-offs:

- Reduce query latency by enabling stale reads with a cached TSO, eliminating the need to request new timestamps.
- Balance performance against data consistency: this feature is only suitable for scenarios where stale reads are acceptable. It is not recommended to use it when strict data consistency is required.

To enable this optimization:

```sql
SET GLOBAL tidb_low_resolution_tso=ON;
```
### Tune coprocessor cache for read-heavy workloads

You can improve query performance for read-heavy workloads by optimizing the [coprocessor cache](https://docs.pingcap.com/tidb/stable/coprocessor-cache). This cache stores the results of coprocessor requests, reducing repeated computations of frequently accessed data. To optimize cache performance, perform the following steps:

1. Monitor the cache hit ratio using the metrics described in [Coprocessor Cache](https://docs.pingcap.com/tidb/stable/coprocessor-cache#view-the-grafana-monitoring-panel).
2. Increase the cache size to improve hit rates for larger working sets.
3. Adjust the admission threshold based on query patterns.

The following lists some recommended settings for a read-heavy workload:

```toml
[tikv-client.copr-cache]
capacity-mb = 4096
admission-max-ranges = 5000
admission-max-result-mb = 10
admission-min-process-ms = 0
```
### Optimize chunk size for workload characteristics

The [`tidb_max_chunk_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_chunk_size) system variable sets the maximum number of rows in a chunk during the execution process. Adjusting this value based on your workload can improve performance.

- For OLTP workloads with large concurrency and small transactions:

    - Set the value between `128` and `256` rows (the default value is `1024`).
    - This reduces memory usage and makes limit queries faster.
    - Use case: point queries, small range scans.

    ```sql
    SET GLOBAL tidb_max_chunk_size = 128;
    ```

- For OLAP or analytical workloads with complex queries and large result sets:

    - Set the value between `1024` and `4096` rows.
    - This increases throughput when scanning large amounts of data.
    - Use case: aggregations, large table scans.

    ```sql
    SET GLOBAL tidb_max_chunk_size = 4096;
    ```
