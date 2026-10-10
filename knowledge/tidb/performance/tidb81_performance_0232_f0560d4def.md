# TiKV scaling test environments, results, and benchmark links

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.5-performance-highlights.md`
- Source Title: `TiDB Cloud Performance Highlights for TiDB v8.5.0`
- Source Heading Path: `TiDB Cloud Performance Highlights for TiDB v8.5.0 > TiKV scaling performance > Test environment > Merging small Regions | TiDB Cloud Performance Highlights for TiDB v8.5.0 > TiKV scaling performance > Test environment > Scaling out TiKV nodes | TiDB Cloud Performance Highlights for TiDB v8.5.0 > TiKV scaling performance > Test results | TiDB Cloud Performance Highlights for TiDB v8.5.0 > Benchmark`
- Source Line Ranges: `217-248`
- Source Scope: `cloud`
- Primary Component: `tikv`
- Related Components: `tidb`, `cloud`
- Topic Tags: `scaling`, `region-merge`, `benchmark`, `tpcc`, `sysbench`, `test-results`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0232_f0560d4def`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.5-performance-highlights.md#merging-small-regions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f9c86e4a594c2e1d78aca68c6e73f7930ffa55787cdfda12ec4b7a8e171bec48`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-highlights#merging-small-regions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.5-performance-highlights.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud v8.5.0 TiKV scaling performance test environments, measured Region merge and scale-out results, or benchmark report links.
- Retrieval Keywords: TiDB Cloud Performance Highlights for TiDB v8.5.0, TiKV scaling performance, Merging small Regions, Scaling out TiKV nodes, small Region merge speed improves by about 10 times, Region merging duration 20 2, TiKV scaling performance improves by over 40%, TiKV scaling out duration 5 3.5, TPC-C dataset with 20,000 warehouses, nearly 1 million small tables, automatic merging of small Regions, scaling out TiKV nodes from 4 to 7, TPC-C performance test report, Sysbench performance test report
- Follow-up Guidance: The source also points to the TPC-C performance test report and Sysbench performance test report for v8.5.0 performance.
- Classification Note: This is classified as performance for the TiKV component in cloud scope because the content provides TiKV scaling test environments, quantitative duration comparisons, and benchmark references for TiDB Cloud v8.5.0.

## Official Source Content

#### Merging small Regions

- Cluster topology: TiDB (16 vCPU, 32 GiB) \* 1 + TiKV (16 vCPU, 32 GiB) \* 3
- Dataset: nearly 1 million small tables, with the size of each table < 2 MiB
- Workload: automatic merging of small Regions
#### Scaling out TiKV nodes

- Cluster topology: TiDB (16 vCPU, 32 GiB) \* 1 + TiKV (16 vCPU, 32 GiB) \* 4
- Dataset: TPC-C dataset with 20,000 warehouses
- Workload: scaling out TiKV nodes from 4 to 7
### Test results

The small Region merge speed improves by about 10 times.

| Metric | Without improvement | With improvement |
| --- |  --- |  --- |
| Region merging duration (hrs) | 20 | 2 |

TiKV scaling performance improves by over 40%, and TiKV node scaling out duration gains a 30% reduction.

| Metric | Without improvement | With improvement |
| --- |  --- |  --- |
| TiKV scaling out duration (hrs) | 5 | 3.5 |
## Benchmark

In addition to the preceding test data, you can refer to the following benchmark results for v8.5.0 performance:

- [TPC-C performance test report](https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-benchmarking-with-tpcc)
- [Sysbench performance test report](https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-benchmarking-with-sysbench)
