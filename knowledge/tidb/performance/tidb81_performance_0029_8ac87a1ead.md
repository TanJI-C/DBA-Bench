# Sysbench comparison results for v6.2.0 vs v6.1.0

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test results | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test results > Point Select performance | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test results > Update Non-index performance | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test results > Update Index performance | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test results > Read Write performance`
- Source Line Ranges: `151-199`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`
- Topic Tags: `sysbench`, `benchmark-results`, `tps`, `latency`, `point-select`, `update-non-index`, `update-index`, `read-write`, `performance-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0029_8ac87a1ead`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0.md#test-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `41ba8c31242589eb566afaadc7ad4000c57eadf149660f8bef60f6d402f442c6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0#test-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for Sysbench comparison results, TPS, 95% latency, or workload-specific performance differences between TiDB v6.2.0 and v6.1.0.
- Retrieval Keywords: Test results, Point Select performance, Update Non-index performance, Update Index performance, Read Write performance, v6.1.0 TPS, v6.2.0 TPS, 95% latency, TPS improvement (%), Point Select slightly drops by 3.58%, Update Non-index reduced by 0.85%, Update Index reduced by 0.47%, Read Write performance reduced by 1.21%, 300 threads, 600 threads, 900 threads
- Follow-up Guidance: The source includes per-workload charts for Point Select, Update Non-index, Update Index, and Read Write.
- Classification Note: This chunk is classified as performance because it contains the measured Sysbench TPS and latency results and summarizes the performance differences across workloads.

## Official Source Content

## Test results
### Point Select performance

| Threads | v6.1.0 TPS | v6.2.0 TPS | v6.1.0 95% latency (ms) | v6.2.0 95% latency (ms) | TPS improvement (%) |
| :------ | :--------- | :--------- | :---------------------- | :---------------------- | :----------- |
| 300     | 243530.01  | 236885.24  | 1.93                    | 2.07                    | -2.73        |
| 600     | 304121.47  | 291395.84  | 3.68                    | 4.03                    | -4.18        |
| 900     | 327301.23  | 314720.02  | 5                       | 5.47                    | -3.84        |

Compared with v6.1.0, the Point Select performance of v6.2.0 slightly drops by 3.58%.

![Point Select](/media/sysbench_v610vsv620_point_select.png)
### Update Non-index performance

| Threads | v6.1.0 TPS | v6.2.0 TPS | v6.1.0 95% latency (ms) | v6.2.0 95% latency (ms) | TPS improvement (%)  |
| :------ | :--------- | :--------- | :---------------------- | :---------------------- | :----------- |
| 300     | 42608.8    | 42372.82   | 11.45                   | 11.24                   | -0.55        |
| 600     | 54264.47   | 53672.69   | 18.95                   | 18.95                   | -1.09        |
| 900     | 60667.47   | 60116.14   | 26.2                    | 26.68                   | -0.91        |

Compared with v6.1.0, the Update Non-index performance of v6.2.0 is basically unchanged, reduced by 0.85%.

![Update Non-index](/media/sysbench_v610vsv620_update_non_index.png)
### Update Index performance

| Threads | v6.1.0 TPS | v6.2.0 TPS | v6.1.0 95% latency (ms) | v6.2.0 95% latency (ms) | TPS improvement (%) |
| :------ | :--------- | :--------- | :---------------------- | :---------------------- | :----------- |
| 300     | 19384.75   | 19353.58   | 23.52                   | 23.52                   | -0.16        |
| 600     | 24144.78   | 24007.57   | 38.25                   | 37.56                   | -0.57        |
| 900     | 26770.9    | 26589.84   | 51.94                   | 52.89                   | -0.68        |

Compared with v6.1.0, the Update Index performance of v6.2.0 is basically unchanged, reduced by 0.47%.

![Update Index](/media/sysbench_v610vsv620_update_index.png)
### Read Write performance

| Threads | v6.1.0 TPS | v6.2.0 TPS | v6.1.0 95% latency (ms) | v6.2.0 95% latency (ms) | TPS improvement (%) |
| :------ | :--------- | :--------- | :---------------------- | :---------------------- | :----------- |
| 300     | 4849.67    | 4797.59    | 86                      | 84.47                   | -1.07        |
| 600     | 5643.89    | 5565.17    | 161.51                  | 161.51                  | -1.39        |
| 900     | 5954.91    | 5885.22    | 235.74                  | 235.74                  | -1.17        |

Compared with v6.1.0, the Read Write performance of v6.2.0 is reduced by 1.21%.

![Read Write](/media/sysbench_v610vsv620_read_write.png)
