# Sysbench benchmark results across query types

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v3.0-performance-benchmarking-with-sysbench.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test result | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test result > `Point Select` test | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test result > `Update Non-Index` test | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test result > `Update Index` test | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test result > `Read Write` test`
- Source Line Ranges: `162-288`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `sysbench`, `benchmark-results`, `qps`, `latency`, `point-select`, `update-non-index`, `update-index`, `read-write`, `version-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0039_f3c11b3fcf`
- Source ID: `tidb-docs-8.1:benchmark/v3.0-performance-benchmarking-with-sysbench.md#test-result`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1220def4bde9017eac4677e547a810675ecca9ae6bfd55b7c7220302b57d176e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v3.0-performance-benchmarking-with-sysbench#test-result
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v3.0-performance-benchmarking-with-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when the user is looking for Sysbench benchmark results comparing TiDB v3.0 and v2.1 by workload type, thread count, QPS, and 95% latency.
- Retrieval Keywords: Test result, Point Select test, Update Non-Index test, Update Index test, Read Write test, QPS, 95% latency(ms), Threads 150 300 600 900 1200 1500, v2.1, v3.0, sysbench_v4_point_select.png, sysbench_v4_update_non_index.png, sysbench_v4_update_index.png, sysbench_v4_read_write.png
- Follow-up Guidance: The same document also includes the test environment, Sysbench commands, parameter configuration, and cluster topology used to produce these results.
- Classification Note: This is classified as performance content because it reports measured Sysbench throughput and latency results across multiple OLTP query types for TiDB v3.0 and v2.1.

## Official Source Content

## Test result
### `Point Select` test

**v2.1:**

| Threads |   QPS    | 95% latency(ms) |
| :------- | :-------- | :------------- |
| 150     | 240304.06 |            1.61 |
| 300     | 276635.75 |            2.97 |
| 600     | 307838.06 |            5.18 |
| 900     | 323667.93 |            7.30 |
| 1200    | 330925.73 |            9.39 |
| 1500    | 336250.38 |           11.65 |

<!-- plan cache enabled
| Threads |    QPS    | 95% latency(ms) |
| :------- | :--------| :-------------- |
| 150     | 175247.08 |            2.35 |
| 300     | 189423.99 |            4.41 |
| 600     | 197425.51 |            8.43 |
| 900     | 202451.18 |           12.08 |
| 1200    | 204908.95 |           15.83 |
| 1500    | 206572.53 |           19.65 |
-->

**v3.0:**

| Threads |    QPS    | 95% latency(ms) |
| :------- | :-------- | :-------------- |
| 150     | 334219.04 |            0.64 |
| 300     | 456444.86 |            1.10 |
| 600     | 512177.48 |            2.11 |
| 900     | 525945.13 |            3.13 |
| 1200    | 534577.36 |            4.18 |
| 1500    | 533944.64 |            5.28 |

![point select](/media/sysbench_v4_point_select.png)
### `Update Non-Index` test

**v2.1:**

| Threads |   QPS    | 95% latency (ms) |
| :------- | :------- | :-------------- |
| 150     | 21785.37 |            8.58 |
| 300     | 28979.27 |           13.70 |
| 600     | 34629.72 |           24.83 |
| 900     | 36410.06 |           43.39 |
| 1200    | 37174.15 |           62.19 |
| 1500    | 37408.88 |           87.56 |

**v3.0:**

| Threads |   QPS    | 95% latency (ms) |
| :------- | :------- | :-------------- |
| 150     | 28045.75 |            6.67 |
| 300     | 39237.77 |            9.91 |
| 600     | 49536.56 |           16.71 |
| 900     | 55963.73 |           22.69 |
| 1200    | 59904.02 |           29.72 |
| 1500    | 62247.95 |           42.61 |

![update non-index](/media/sysbench_v4_update_non_index.png)
### `Update Index` test

**v2.1:**

| Threads |   QPS    | 95% latency(ms) |
| :------- | :------- | :-------------- |
| 150     | 14378.24 |           13.22 |
| 300     | 16916.43 |           24.38 |
| 600     | 17636.11 |           57.87 |
| 900     | 17740.92 |           95.81 |
| 1200    | 17929.24 |          130.13 |
| 1500    | 18012.80 |          161.51 |

**v3.0:**

| Threads |   QPS    | 95% latency(ms) |
| :------- | :------- | :-------------- |
| 150     | 19047.32 |           10.09 |
| 300     | 24467.64 |           16.71 |
| 600     | 28882.66 |           31.94 |
| 900     | 30298.41 |           57.87 |
| 1200    | 30419.40 |           92.42 |
| 1500    | 30643.55 |          125.52 |

![update index](/media/sysbench_v4_update_index.png)
### `Read Write` test

**v2.1:**

| Threads |    QPS    | 95% latency(ms) |
| :------- | :-------- | :-------------- |
| 150     |  85140.60 |           44.98 |
| 300     |  96773.01 |           82.96 |
| 600     | 105139.81 |          153.02 |
| 900     | 110041.83 |          215.44 |
| 1200    | 113242.70 |          277.21 |
| 1500    | 114542.19 |          337.94 |

<!-- plan cache enabled
| Treads |    QPS    | 95% latency(ms) |
| :------- | :-------- | :-------------- |
| 150     |  81339.88 |           47.47 |
| 300     |  94455.29 |           86.00 |
| 600     | 103125.91 |          161.51 |
| 900     | 105984.81 |          235.74 |
| 1200    | 106639.19 |          320.17 |
| 1500    | 107312.93 |          390.30 |
-->

**v3.0:**

| Threads |    QPS    | 95% latency(ms) |
| :------- | :-------- | :-------------- |
| 150     | 105692.08 |           35.59 |
| 300     | 129769.69 |           58.92 |
| 600     | 141430.86 |          114.72 |
| 900     | 144371.76 |          170.48 |
| 1200    | 143344.37 |          223.34 |
| 1500    | 144567.91 |          277.21 |

![read write](/media/sysbench_v4_read_write.png)
