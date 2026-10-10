# Sysbench workload performance results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.1-performance-benchmarking-with-sysbench.md`
- Source Title: `TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0`
- Source Heading Path: `TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test results | TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test results > Point select performance | TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test results > Read write performance | TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test results > Update non-index performance | TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test results > Update index performance | TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test results > Insert performance`
- Source Line Ranges: `119-181`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `sysbench`, `benchmark-results`, `tps`, `latency`, `point-select`, `read-write`, `update-non-index`, `update-index`, `insert`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0220_c80603ed7e`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.1-performance-benchmarking-with-sysbench.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `731d61f4c3dd2eb4dd5e81ac4de39846cefe7962b5022b4e4d50d6ecb735ef78`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.1-performance-benchmarking-with-sysbench#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.1-performance-benchmarking-with-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the published Sysbench TPS and 95% latency results for TiDB v8.1.0 workloads in the documented test environment.
- Retrieval Keywords: Test results, Point select performance, Read write performance, Update non-index performance, Update index performance, Insert performance, oltp_point_select TPS latency, oltp_read_write TPS latency, oltp_update_non_index TPS latency, oltp_update_index TPS latency, oltp_insert TPS latency, 95% latency ms, Threads 50 100 200 400, v8.1.0 Sysbench results
- Follow-up Guidance: The source presents separate result tables and figures for oltp_point_select, oltp_read_write, oltp_update_non_index, oltp_update_index, and oltp_insert.
- Classification Note: This is classified as performance content because it provides measured benchmark outcomes in TPS and 95% latency for multiple Sysbench workloads.

## Official Source Content

## Test results

This section introduces the Sysbench performance of v8.1.0 in the [test environment](#test-environment).
### Point select performance

The performance on the `oltp_point_select` workload is as follows:

| Threads |  TPS | 95% latency (ms)|
|:--------|:----------|:----------|
| 50 | 32,741  | 1.96 |
| 100 | 62,545 | 2.03 |
| 200 | 111,470 | 2.48 |

![Sysbench point select performance](/media/tidb-cloud/v8.1.0_oltp_point_select.png)
### Read write performance

The performance on the `oltp_read_write` workload is as follows:

| Threads |  TPS | 95% latency (ms)|
|:--------|:----------|:----------|
| 50 | 1,232 | 46.6 |
| 100 | 2,341 | 51 |
| 200 | 3,240 | 109  |

![Sysbench read write performance](/media/tidb-cloud/v8.1.0_oltp_read_write.png)
### Update non-index performance

The performance on the `oltp_update_non_index` workload is as follows:

| Threads |  TPS | 95% latency (ms)|
|:--------|:----------|:----------|
| 100 | 14,000  | 9.39 |
| 200 | 25,215  | 10.5 |
| 400 | 42,550  | 12.8 |

![Sysbench update non-index performance](/media/tidb-cloud/v8.1.0_oltp_update_non_index.png)
### Update index performance

The performance on the `oltp_update_index` workload is as follows:

| Threads |  TPS | 95% latency (ms)|
|:--------|:----------|:----------|
| 100 | 11,188   | 11.7 |
| 200 | 17,805  | 14.7 |
| 400 | 24,575  | 23.5 |

![Sysbench update index performance](/media/tidb-cloud/v8.1.0_oltp_update_index.png)
### Insert performance

The performance on the `oltp_insert` workload is as follows:

| Threads |  TPS | 95% latency (ms)|
|:--------|:----------|:----------|
| 100 | 18,339  | 7.3|
| 200 | 29,387  | 9.73 |
| 400 | 42,712  | 14.2 |

![Sysbench insert performance](/media/tidb-cloud/v8.1.0_oltp_insert.png)
