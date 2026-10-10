# IME for hotspot MVCC reads

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.5-performance-highlights.md`
- Source Title: `TiDB Cloud Performance Highlights for TiDB v8.5.0`
- Source Heading Path: `TiDB Cloud Performance Highlights for TiDB v8.5.0 > Hotspot reads with excessive MVCC versions | TiDB Cloud Performance Highlights for TiDB v8.5.0 > Hotspot reads with excessive MVCC versions > Challenge | TiDB Cloud Performance Highlights for TiDB v8.5.0 > Hotspot reads with excessive MVCC versions > Solution | TiDB Cloud Performance Highlights for TiDB v8.5.0 > Hotspot reads with excessive MVCC versions > Test environment | TiDB Cloud Performance Highlights for TiDB v8.5.0 > Hotspot reads with excessive MVCC versions > Test results`
- Source Line Ranges: `25-62`
- Source Scope: `cloud`
- Primary Component: `tikv`
- Related Components: `tidb`
- Topic Tags: `mvcc`, `hotspot`, `in-memory-engine`, `query-latency`, `throughput`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0228_6cd3ab7781`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.5-performance-highlights.md#hotspot-reads-with-excessive-mvcc-versions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `31b3782e810282a245650dd6a4e6c3522dd23b4ded19439a4163c2010f47ebc7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-highlights#hotspot-reads-with-excessive-mvcc-versions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.5-performance-highlights.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving information about hotspot read performance degradation caused by excessive MVCC versions and the effect of enabling TiKV In-Memory Engine (IME).
- Retrieval Keywords: Hotspot reads with excessive MVCC versions, Multi-Version Concurrency Control (MVCC) versions, In-Memory Engine (IME), tikv_configs, [in-memory-engine], enable = true, long GC times 24 hours, query latency decreases by 50%, throughput increases by 100%, Disable IME, Enable IME
- Follow-up Guidance: The chunk includes a test environment with TiDB and TiKV topology, the IME configuration block, and comparative TPS, QPS, average latency, and P95 latency results.
- Classification Note: This is classified as TiKV performance content because the official content attributes the solution to TiKV In-Memory Engine and measures read latency and throughput improvements.

## Official Source Content

## Hotspot reads with excessive MVCC versions
### Challenge

In some user scenarios, the following challenges might occur:

- Frequent version updates: in some workloads, the data is updated and read very frequently.
- Long retention of historical versions: to meet business requirements, such as supporting flashback to specific time points, users might configure overly long GC (Garbage Collection) times (such as 24 hours). This results in an excessive accumulation of Multi-Version Concurrency Control (MVCC) versions, which significantly reduces query efficiency.

The accumulation of MVCC versions creates a large gap between the requested data and the processed data, leading to degraded read performance.
### Solution

To address this issue, TiKV introduces [In-Memory Engine (IME)](https://docs.pingcap.com/tidb/stable/tikv-in-memory-engine). By caching the latest versions in memory, TiKV reduces the impact of historical versions on read performance, significantly improving query efficiency.
### Test environment

- Cluster topology: TiDB (16 vCPU, 32 GiB) \* 1 + TiKV (16 vCPU, 32 GiB) \* 6
- Cluster configurations:

    ```
    tikv_configs:
    [in-memory-engine]
    enable = true
    ```

- Dataset: 24 GiB storage size with about 340 Regions, containing frequently updated data
- Workload: rows requiring scans contain numerous MVCC versions introduced by frequent updates
### Test results

The query latency decreases by 50%, and the throughput increases by 100%.

| Configuration | Duration (s) | Threads | TPS | QPS | Average latency (ms) | P95 latency (ms) |
| --- |  --- |  --- |  --- |  --- |  --- |  --- |
| Disable IME | 3600 | 10 | 123.8 | 1498.3 | 80.76 | 207.82 |
| Enable IME | 3600 | 10 | 238.2 | 2881.5 | 41.99 | 78.60 |
