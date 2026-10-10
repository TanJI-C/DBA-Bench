# Sysbench v5.0 versus v4.0 performance results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v5-vs-v4.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test results | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test results > Point Select performance | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test results > Update Non-index performance | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test results > Update Index performance | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test results > Read Write performance`
- Source Line Ranges: `163-223`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `test-results`, `qps`, `latency`, `point-select`, `update-non-index`, `update-index`, `read-write`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0010_21e592b423`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v5-vs-v4.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `32268a3f30533959ba00d94930cccc85d1e5d124cf26e56bcdf80e313004e886`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v5-vs-v4#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v5-vs-v4.md

## Retrieval Guidance

- Use When: Use this chunk when you need the measured QPS and 95% latency comparison results for Point Select, Update Non-index, Update Index, or Read Write tests.
- Retrieval Keywords: Test results, Point Select performance, Update Non-index performance, Update Index performance, Read Write performance, v4.0 QPS, v5.0 QPS, v4.0 95% latency (ms), v5.0 95% latency (ms), QPS improvement, 150 threads, 300 threads, 600 threads, 900 threads, 1200 threads, 1500 threads
- Follow-up Guidance: See the per-thread result tables and the summary sentences under each workload for the reported improvement percentages.
- Classification Note: This chunk is classified as performance test results comparing TiDB v5.0 and v4.0 across multiple Sysbench workloads.

## Official Source Content

## Test results
### Point Select performance

| Threads   | v4.0 QPS   | v4.0 95% latency (ms)   | v5.0 QPS   | v5.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
| 150        | 159451.19        | 1.32        | 177876.25        | 1.23        | 11.56%     |
| 300        | 244790.38        | 1.96        | 252675.03        | 1.82        | 3.22%     |
| 600        | 322929.05        | 3.75        | 331956.84        | 3.36        | 2.80%     |
| 900        | 364840.05        | 5.67        | 365655.04        | 5.09        | 0.22%     |
| 1200        | 376529.18        | 7.98        | 366507.47        | 7.04        | -2.66%     |
| 1500        | 368390.52        | 10.84        | 372476.35        | 8.90        | 1.11%     |

Compared with v4.0, the Point Select performance of TiDB v5.0 has increased by 2.7%.

![Point Select](/media/sysbench_v5vsv4_point_select.png)
### Update Non-index performance

| Threads   | v4.0 QPS   | v4.0 95% latency (ms)   | v5.0 QPS   | v5.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
| 150        | 17243.78        | 11.04        | 30866.23        | 6.91        | 79.00%     |
| 300        | 25397.06        | 15.83        | 45915.39        | 9.73        | 80.79%     |
| 600        | 33388.08        | 25.28        | 60098.52        | 16.41        | 80.00%     |
| 900        | 38291.75        | 36.89        | 70317.41        | 21.89        | 83.64%     |
| 1200        | 41003.46        | 55.82        | 76376.22        | 28.67        | 86.27%     |
| 1500        | 44702.84        | 62.19        | 80234.58        | 34.95        | 79.48%     |

Compared with v4.0, the Update Non-index performance of TiDB v5.0 has increased by 81%.

![Update Non-index](/media/sysbench_v5vsv4_update_non_index.png)
### Update Index performance

| Threads   | v4.0 QPS   | v4.0 95% latency (ms)   | v5.0 QPS   | v5.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
| 150        | 11736.21        | 17.01        | 15631.34        | 17.01        | 33.19%     |
| 300        | 15435.95        | 28.67        | 19957.06        | 22.69        | 29.29%     |
| 600        | 18983.21        | 49.21        | 23218.14        | 41.85        | 22.31%     |
| 900        | 20855.29        | 74.46        | 26226.76        | 53.85        | 25.76%     |
| 1200        | 21887.64        | 102.97        | 28505.41        | 69.29        | 30.24%     |
| 1500        | 23621.15        | 110.66        | 30341.06        | 82.96        | 28.45%     |

Compared with v4.0, the Update Index performance of TiDB v5.0 has increased by 28%.

![Update Index](/media/sysbench_v5vsv4_update_index.png)
### Read Write performance

| Threads   | v4.0 QPS   | v4.0 95% latency (ms)   | v5.0 QPS   | v5.0 95% latency (ms)   | QPS improvement   |
|:----------|:----------|:----------|:----------|:----------|:----------|
| 150        | 59979.91        | 61.08        | 66098.57        | 55.82        | 10.20%     |
| 300        | 77118.32        | 102.97        | 84639.48        | 90.78        | 9.75%     |
| 600        | 90619.52        | 183.21        | 101477.46        | 167.44        | 11.98%     |
| 900        | 97085.57        | 267.41        | 109463.46        | 240.02        | 12.75%     |
| 1200        | 106521.61        | 331.91        | 115416.05        | 320.17        | 8.35%     |
| 1500        | 116278.96        | 363.18        | 118807.5        | 411.96        | 2.17%     |

Compared with v4.0, the read-write performance of TiDB v5.0 has increased by 9%.

![Read Write](/media/sysbench_v5vsv4_read_write.png)
