# Sysbench workload performance results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.5-performance-benchmarking-with-sysbench.md`
- Source Title: `TiDB Cloud Sysbench Performance Test Report for TiDB v8.5.0`
- Source Heading Path: `TiDB Cloud Sysbench Performance Test Report for TiDB v8.5.0 > Test results | TiDB Cloud Sysbench Performance Test Report for TiDB v8.5.0 > Test results > Point select performance | TiDB Cloud Sysbench Performance Test Report for TiDB v8.5.0 > Test results > Read write performance | TiDB Cloud Sysbench Performance Test Report for TiDB v8.5.0 > Test results > Update non-index performance | TiDB Cloud Sysbench Performance Test Report for TiDB v8.5.0 > Test results > Update index performance | TiDB Cloud Sysbench Performance Test Report for TiDB v8.5.0 > Test results > Insert performance`
- Source Line Ranges: `119-181`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `sysbench`, `benchmark-results`, `tps`, `latency`, `point-select`, `read-write`, `update-non-index`, `update-index`, `insert`, `workloads`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0223_ee27b3cf6e`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.5-performance-benchmarking-with-sysbench.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6b06ad01c8d7122a9ca46c18726f1feaa15f09b9c09d853e0f090fc4445d1286`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-benchmarking-with-sysbench#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.5-performance-benchmarking-with-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented TPS and 95% latency results for specific Sysbench workloads in the TiDB Cloud v8.5.0 test environment.
- Retrieval Keywords: Sysbench test results, v8.5.0, TPS, 95% latency, point select performance, read write performance, update non-index performance, update index performance, insert performance, oltp_point_select, oltp_read_write, oltp_update_non_index, oltp_update_index, oltp_insert, 32,733 TPS, 107,795 TPS, 3,187 TPS, 39,547 TPS, 25,369 TPS, 48,621 TPS
- Follow-up Guidance: 
- Classification Note: This is classified as performance content because it reports benchmark throughput and latency measurements for multiple Sysbench workloads.

## Official Source Content

## Test results

This section introduces the Sysbench performance of v8.5.0 in the [test environment](#test-environment).
### Point select performance

The performance on the `oltp_point_select` workload is as follows:

| Threads |  TPS | 95% latency (ms)|
|:--------|:----------|:----------|
| 50 | 32,733  | 1.94 |
| 100 | 62,123 | 2.04 |
| 200 | 107,795 | 2.56 |

![Sysbench point select performance](/media/tidb-cloud/v8.5.0_oltp_point_select.png)
### Read write performance

The performance on the `oltp_read_write` workload is as follows:

| Threads |  TPS | 95% latency (ms)|
|:--------|:----------|:----------|
| 50 | 1,258 | 45.8 |
| 100 | 2,243 | 52 |
| 200 | 3,187 | 94.7  |

![Sysbench read write performance](/media/tidb-cloud/v8.5.0_oltp_read_write.png)
### Update non-index performance

The performance on the `oltp_update_non_index` workload is as follows:

| Threads |  TPS | 95% latency (ms)|
|:--------|:----------|:----------|
| 100 | 12,969  | 10.10 |
| 200 | 23,265  | 11.2 |
| 400 | 39,547  | 13.2 |

![Sysbench update non-index performance](/media/tidb-cloud/v8.5.0_oltp_update_non_index.png)
### Update index performance

The performance on the `oltp_update_index` workload is as follows:

| Threads |  TPS | 95% latency (ms)|
|:--------|:----------|:----------|
| 100 | 11,678  | 11.0 |
| 200 | 17,685  | 14.8 |
| 400 | 25,369  | 20.4 |

![Sysbench update index performance](/media/tidb-cloud/v8.5.0_oltp_update_index.png)
### Insert performance

The performance on the `oltp_insert` workload is as follows:

| Threads |  TPS | 95% latency (ms)|
|:--------|:----------|:----------|
| 100 | 18,409  | 7.28|
| 200 | 30,943  | 8.28 |
| 400 | 48,621  | 11.2 |

![Sysbench insert performance](/media/tidb-cloud/v8.5.0_oltp_insert.png)
