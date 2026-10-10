# Sysbench v4.0 versus v3.0 performance results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v4-vs-v3.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test results | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test results > Point Select performance | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test results > Update Non-index performance | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test results > Update Index performance | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test results > Read-write performance`
- Source Line Ranges: `147-207`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `sysbench`, `benchmark-results`, `qps`, `latency`, `point-select`, `update-non-index`, `update-index`, `read-write`, `throughput-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0007_f71f5fef00`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v4-vs-v3.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `963101da23b00e99442323fb1c867e4735517ccee65251dc021e4d1adb795903`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v4-vs-v3#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v4-vs-v3.md

## Retrieval Guidance

- Use When: Use this chunk when you need the recorded QPS, 95% latency, and improvement percentages for Sysbench Point Select, Update Non-index, Update Index, and Read-write tests comparing TiDB v4.0 with v3.0.
- Retrieval Keywords: Test results, Point Select performance, Update Non-index performance, Update Index performance, Read-write performance, v3.0 QPS, v4.0 QPS, 95% latency, QPS improvement, Compared with v3.0, the Point Select performance of TiDB v4.0 has increased by 14%, Compared with v3.0, the Update Non-index performance of TiDB v4.0 has increased by 15%, Compared with v3.0, the Update Index performance of TiDB v4.0 has increased by 17%, Compared with v3.0, the read-write performance of TiDB v4.0 has increased by 31%, 150 threads, 300 threads, 600 threads, 900 threads, 1200 threads, 1500 threads
- Follow-up Guidance: The source also includes per-thread result tables and chart image references for each workload type.
- Classification Note: This chunk is classified as performance because it reports benchmark throughput and latency results for multiple Sysbench workloads across thread counts.

## Official Source Content

## Test results
### Point Select performance

| Threads   | v3.0 QPS   | v3.0 95% latency (ms)   | v4.0 QPS   | v4.0 95% latency (ms)   | QPS improvement |
|:----------|:----------|:----------|:----------|:----------|:----------|
| 150        | 117085.701 |     1.667     | 118165.1357        | 1.608 |     0.92%     |
| 300      | 200621.4471|     2.615     | 207774.0859        | 2.032 |     3.57%     |
| 600      | 283928.9323|     4.569     | 320673.342        | 3.304 |     12.94%     |
| 900  | 343218.2624|     6.686     | 383913.3855        | 4.652 |     11.86%     |
| 1200  | 347200.2366|     8.092     | 408929.4372        | 6.318 |     17.78%     |
| 1500  | 366406.2767|     10.562     | 418268.8856        | 7.985 |     14.15%     |

Compared with v3.0, the Point Select performance of TiDB v4.0 has increased by 14%.

![Point Select](/media/sysbench-v4vsv3-point-select.png)
### Update Non-index performance

| Threads   | v3.0 QPS   | v3.0 95% latency (ms)   | v4.0 QPS   | v4.0 95% latency (ms)   | QPS improvement |
|:----------|:----------|:----------|:----------|:----------|:----------|
| 150        | 15446.41024 |     11.446     | 16954.39971        | 10.844 |     9.76%     |
| 300      | 22276.15572|     17.319     | 24364.44689        | 16.706 |     9.37%     |
| 600      | 28784.88353|     29.194     | 31635.70833        | 28.162 |     9.90%    |
| 900  | 32194.15548|     42.611     | 35787.66078        | 38.942 |     11.16%     |
| 1200  | 33954.69114|     58.923     | 38552.63158        | 51.018 |     13.54%     |
| 1500  | 35412.0032|     74.464     | 40859.63755        | 62.193 |     15.38%     |

Compared with v3.0, the Update Non-index performance of TiDB v4.0 has increased by 15%.

![Update Non-index](/media/sysbench-v4vsv3-update-non-index.png)
### Update Index performance

| Threads   | v3.0 QPS   | v3.0 95% latency (ms)   | v4.0 QPS   | v4.0 95% latency (ms)   | QPS improvement |
|:----------|:----------|:----------|:----------|:----------|:----------|
| 150        | 11164.40571 |     16.706     | 11954.73635        | 16.408 |     7.08%     |
| 300      | 14460.98057|     28.162     | 15243.40899        | 28.162 |     5.41%     |
| 600      | 17112.73036|     53.85     | 18535.07515        | 50.107 |     8.31%    |
| 900  | 18233.83426|     86.002     | 20339.6901        | 70.548 |     11.55%     |
| 1200  | 18622.50283|     127.805     | 21390.25122        | 94.104 |     14.86%     |
| 1500  | 18980.34447|     170.479     | 22359.996        | 114.717 |     17.81%     |

Compared with v3.0, the Update Index performance of TiDB v4.0 has increased by 17%.

![Update Index](/media/sysbench-v4vsv3-update-index.png)
### Read-write performance

| Threads   | v3.0 QPS   | v3.0 95% latency (ms)   | v4.0 QPS   | v4.0 95% latency (ms)   | QPS improvement |
|:----------|:----------|:----------|:----------|:----------|:----------|
| 150        | 43768.33633 |     71.83     | 53912.63705        | 59.993 |     23.18%     |
| 300      | 55655.63589|     121.085     | 71327.21336        | 97.555 |     28.16%     |
| 600      | 64642.96992|     223.344     | 84487.75483        | 176.731 |     30.70%    |
| 900  | 68947.25293|     325.984     | 90177.94612        | 257.95 |     30.79%     |
| 1200  | 71334.80099|     434.829     | 92779.71507        | 344.078 |     30.06%     |
| 1500  | 72069.9115|     580.017     | 95088.50812        | 434.829 |     31.94%     |

Compared with v3.0, the read-write performance of TiDB v4.0 has increased by 31%.

![Read Write](/media/sysbench-v4vsv3-read-write.png)
