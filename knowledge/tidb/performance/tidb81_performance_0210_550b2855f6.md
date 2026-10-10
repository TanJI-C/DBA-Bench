# Sysbench workload performance results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v6.5-performance-benchmarking-with-sysbench.md`
- Source Title: `TiDB Cloud Sysbench Performance Test Report for TiDB v6.5.6`
- Source Heading Path: `TiDB Cloud Sysbench Performance Test Report for TiDB v6.5.6 > Test results | TiDB Cloud Sysbench Performance Test Report for TiDB v6.5.6 > Test results > Point select performance | TiDB Cloud Sysbench Performance Test Report for TiDB v6.5.6 > Test results > Read write performance | TiDB Cloud Sysbench Performance Test Report for TiDB v6.5.6 > Test results > Update non-index performance | TiDB Cloud Sysbench Performance Test Report for TiDB v6.5.6 > Test results > Update index performance | TiDB Cloud Sysbench Performance Test Report for TiDB v6.5.6 > Test results > Insert performance`
- Source Line Ranges: `93-155`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `sysbench`, `benchmark-results`, `tps`, `latency`, `point-select`, `read-write`, `update-non-index`, `update-index`, `insert`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0210_550b2855f6`
- Source ID: `tidb-docs-8.1:tidb-cloud/v6.5-performance-benchmarking-with-sysbench.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `159dfe78cbfe1ab8c6daa82b83c65e2b210ba613c0e99d290109a9f82745c68e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v6.5-performance-benchmarking-with-sysbench#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v6.5-performance-benchmarking-with-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when looking for reported Sysbench TPS and 95% latency results for specific OLTP workloads in the documented v6.5.6 test environment.
- Retrieval Keywords: Sysbench test results, TPS, 95% latency, oltp_point_select, oltp_read_write, oltp_update_non_index, oltp_update_index, oltp_insert, Threads 50 100 200 400, v6.5.6 point select performance, v6.5.6 read write performance, v6.5.6 update non-index performance, v6.5.6 update index performance, v6.5.6 insert performance
- Follow-up Guidance: The source states that these results are for v6.5.6 in the referenced test environment and includes performance charts for each workload.
- Classification Note: This is classified as performance content because the official content presents benchmark result tables with TPS and 95% latency for multiple Sysbench workloads.

## Official Source Content

## Test results

This section introduces the Sysbench performance of v6.5.6 in the [test environment](#test-environment).
### Point select performance

The performance on the `oltp_point_select` workload is as follows:

| Threads | TPS    | 95% latency (ms) |
| :------ | :----- | :--------------- |
| 50      | 34125  | 2.03             |
| 100     | 64987  | 2.07             |
| 200     | 121656 | 2.14             |

![Sysbench point select performance](/media/tidb-cloud/v6.5.6-oltp_select_point.png)
### Read write performance

The performance on the `oltp_read_write` workload is as follows:

| Threads | TPS  | 95% latency (ms) |
| :------ | :--- | :--------------- |
| 50      | 1232 | 46.6             |
| 100     | 2266 | 51.9             |
| 200     | 3578 | 81.5             |

![Sysbench read write performance](/media/tidb-cloud/v6.5.6-oltp_read_write.png)
### Update non-index performance

The performance on the `oltp_update_non_index` workload is as follows:

| Threads | TPS   | 95% latency (ms) |
| :------ | :---- | :--------------- |
| 100     | 11016 | 11.0             |
| 200     | 20640 | 12.1             |
| 400     | 36830 | 13.5             |

![Sysbench update non-index performance](/media/tidb-cloud/v6.5.6-oltp_update_non_index.png)
### Update index performance

The performance on the `oltp_update_index` workload is as follows:

| Threads | TPS   | 95% latency (ms) |
| :------ | :---- | :--------------- |
| 100     | 9270  | 14.0             |
| 200     | 14466 | 18.0             |
| 400     | 22194 | 24.8             |

![Sysbench update index performance](/media/tidb-cloud/v6.5.6-oltp_update_index.png)
### Insert performance

The performance on the `oltp_insert` workload is as follows:

| Threads | TPS   | 95% latency (ms) |
| :------ | :---- | :--------------- |
| 100     | 16008 | 8.13             |
| 200     | 27143 | 10.1             |
| 400     | 40884 | 15.0             |

![Sysbench insert performance](/media/tidb-cloud/v6.5.6-oltp_insert.png)
