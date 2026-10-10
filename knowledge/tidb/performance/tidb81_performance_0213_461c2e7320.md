# Sysbench performance results across OLTP workloads

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v7.1-performance-benchmarking-with-sysbench.md`
- Source Title: `TiDB Cloud Sysbench Performance Test Report for TiDB v7.1.3`
- Source Heading Path: `TiDB Cloud Sysbench Performance Test Report for TiDB v7.1.3 > Test results | TiDB Cloud Sysbench Performance Test Report for TiDB v7.1.3 > Test results > Point select performance | TiDB Cloud Sysbench Performance Test Report for TiDB v7.1.3 > Test results > Read write performance | TiDB Cloud Sysbench Performance Test Report for TiDB v7.1.3 > Test results > Update non-index performance | TiDB Cloud Sysbench Performance Test Report for TiDB v7.1.3 > Test results > Update index performance | TiDB Cloud Sysbench Performance Test Report for TiDB v7.1.3 > Test results > Insert performance`
- Source Line Ranges: `114-176`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `sysbench`, `benchmark-results`, `oltp`, `point-select`, `read-write`, `update-non-index`, `update-index`, `insert`, `tps`, `latency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0213_461c2e7320`
- Source ID: `tidb-docs-8.1:tidb-cloud/v7.1-performance-benchmarking-with-sysbench.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4b136854a7b994a61ad1eccc904c8a5e74a1cee3c17d97f20908fa2e8da7b23d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v7.1-performance-benchmarking-with-sysbench#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v7.1-performance-benchmarking-with-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when you need the reported Sysbench TPS and 95% latency results for specific OLTP workloads in the TiDB v7.1.3 test environment.
- Retrieval Keywords: Sysbench test results v7.1.3, Point select performance, Read write performance, Update non-index performance, Update index performance, Insert performance, oltp_point_select TPS latency, oltp_read_write TPS latency, oltp_update_non_index TPS latency, oltp_update_index TPS latency, oltp_insert TPS latency, 95% latency (ms), Threads 50 100 200 400
- Follow-up Guidance: The source states that these results are for the test environment described earlier in the same report.
- Classification Note: This is classified as performance content because it provides benchmark outcome tables with TPS and 95% latency for multiple Sysbench OLTP workloads.

## Official Source Content

## Test results

This section introduces the Sysbench performance of v7.1.3 in the [test environment](#test-environment).
### Point select performance

The performance on the `oltp_point_select` workload is as follows:

| Threads | TPS    | 95% latency (ms) |
| :------ | :----- | :--------------- |
| 50      | 35309  | 1.93             |
| 100     | 64853  | 2.00             |
| 200     | 118462 | 2.22             |

![Sysbench point select performance](/media/tidb-cloud/v7.1.3-oltp_select_point.png)
### Read write performance

The performance on the `oltp_read_write` workload is as follows:

| Threads | TPS  | 95% latency (ms) |
| :------ | :--- | :--------------- |
| 50      | 1218 | 48.3             |
| 100     | 2235 | 53.9             |
| 200     | 3380 | 87.6             |

![Sysbench read write performance](/media/tidb-cloud/v7.1.3-oltp_read_write.png)
### Update non-index performance

The performance on the `oltp_update_non_index` workload is as follows:

| Threads | TPS   | 95% latency (ms) |
| :------ | :---- | :--------------- |
| 100     | 10928 | 11.7             |
| 200     | 19985 | 12.8             |
| 400     | 35621 | 14.7             |

![Sysbench update non-index performance](/media/tidb-cloud/v7.1.3-oltp_update_non_index.png)
### Update index performance

The performance on the `oltp_update_index` workload is as follows:

| Threads | TPS   | 95% latency (ms) |
| :------ | :---- | :--------------- |
| 100     | 8854  | 14.7             |
| 200     | 14414 | 18.6             |
| 400     | 21997 | 25.3             |

![Sysbench update index performance](/media/tidb-cloud/v7.1.3-oltp_update_index.png)
### Insert performance

The performance on the `oltp_insert` workload is as follows:

| Threads | TPS   | 95% latency (ms) |
| :------ | :---- | :--------------- |
| 100     | 15575 | 8.13             |
| 200     | 25078 | 11.0             |
| 400     | 38436 | 15.6             |

![Sysbench insert performance](/media/tidb-cloud/v7.1.3-oltp_insert.png)
