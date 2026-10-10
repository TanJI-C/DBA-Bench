# Sysbench workload performance results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v7.5-performance-benchmarking-with-sysbench.md`
- Source Title: `TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0`
- Source Heading Path: `TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test results | TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test results > Point select performance | TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test results > Read write performance | TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test results > Update non-index performance | TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test results > Update index performance | TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test results > Insert performance`
- Source Line Ranges: `114-176`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`
- Topic Tags: `sysbench`, `benchmark-results`, `tps`, `latency`, `oltp_point_select`, `oltp_read_write`, `oltp_update_non_index`, `oltp_update_index`, `oltp_insert`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0216_431af5e2be`
- Source ID: `tidb-docs-8.1:tidb-cloud/v7.5-performance-benchmarking-with-sysbench.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `63ea21f3f2faea5e3b4e50a0df5a34c9b07db15605c6d21de1aa886ca6904d09`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v7.5-performance-benchmarking-with-sysbench#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v7.5-performance-benchmarking-with-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official Sysbench TPS and 95% latency results for TiDB Cloud v7.5.0 across the listed OLTP workloads and thread counts.
- Retrieval Keywords: Sysbench test results v7.5.0, TPS 95% latency, oltp_point_select performance, oltp_read_write performance, oltp_update_non_index performance, oltp_update_index performance, oltp_insert performance, point select 118651 TPS 2.22 ms, read write 3169 TPS 92.4 ms, update non-index 34011 TPS 14.7 ms, update index 20377 TPS 26.9 ms, insert 37247 TPS 16.4 ms, Threads 50 100 200 400
- Follow-up Guidance: The results are explicitly stated to be for v7.5.0 in the referenced test environment.
- Classification Note: This chunk is classified as performance because it reports benchmark outcome metrics, specifically TPS and 95% latency, for multiple Sysbench workloads.

## Official Source Content

## Test results

This section introduces the Sysbench performance of v7.5.0 in the [test environment](#test-environment).
### Point select performance

The performance on the `oltp_point_select` workload is as follows:

| Threads | TPS     | 95% latency (ms) |
| :------ | :------ | :--------------- |
| 50      | 33,344  | 1.96             |
| 100     | 64,810  | 2.03             |
| 200     | 118,651 | 2.22             |

![Sysbench point select performance](/media/tidb-cloud/v7.5.0-oltp_point_select.png)
### Read write performance

The performance on the `oltp_read_write` workload is as follows:

| Threads | TPS   | 95% latency (ms) |
| :------ | :---- | :--------------- |
| 50      | 1,181 | 49.2             |
| 100     | 2,162 | 54.8             |
| 200     | 3,169 | 92.4             |

![Sysbench read write performance](/media/tidb-cloud/v7.5.0-oltp_read_write.png)
### Update non-index performance

The performance on the `oltp_update_non_index` workload is as follows:

| Threads | TPS    | 95% latency (ms) |
| :------ | :----- | :--------------- |
| 100     | 10,567 | 11.7             |
| 200     | 20,223 | 13.0             |
| 400     | 34,011 | 14.7             |

![Sysbench update non-index performance](/media/tidb-cloud/v7.5.0-oltp_update_non_index.png)
### Update index performance

The performance on the `oltp_update_index` workload is as follows:

| Threads | TPS    | 95% latency (ms) |
| :------ | :----- | :--------------- |
| 100     | 8,896  | 14.7             |
| 200     | 13,718 | 19.0             |
| 400     | 20,377 | 26.9             |

![Sysbench update index performance](/media/tidb-cloud/v7.5.0-oltp_update_index.png)
### Insert performance

The performance on the `oltp_insert` workload is as follows:

| Threads | TPS    | 95% latency (ms) |
| :------ | :----- | :--------------- |
| 100     | 15,132 | 8.58             |
| 200     | 24,756 | 10.8             |
| 400     | 37,247 | 16.4             |

![Sysbench insert performance](/media/tidb-cloud/v7.5.0-oltp_insert.png)
