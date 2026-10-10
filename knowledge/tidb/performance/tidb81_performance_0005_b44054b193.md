# Sysbench v2.1 vs v2.0 benchmark plan and results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v3.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test purpose | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test version, time, and place | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test environment | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test plan | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test plan > TiDB version information | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test plan > v2.1.0-rc.2 | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test plan > v2.0.6 | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test plan > TiDB parameter configuration | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test plan > TiKV parameter configuration | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test plan > Cluster topology | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test result | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test result > `Point Select` test | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test result > `Update Non-Index` test | TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0 > Test result > `Update Index` test`
- Source Line Ranges: `5-142`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `ecosystem`
- Topic Tags: `sysbench`, `benchmark`, `oltp`, `qps`, `latency`, `point-select`, `update-non-index`, `update-index`, `test-environment`, `cluster-topology`, `configuration`, `version-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0005_b44054b193`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v3.md#tidb-sysbench-performance-test-report-v2-1-vs-v2-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `064d0c10a6f45d1a2013c663ae92f74b4cf83cd5da297353daa2a589a30da1c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v3#tidb-sysbench-performance-test-report-v2-1-vs-v2-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the official Sysbench comparison between TiDB v2.1.0-rc.2 and v2.0.6 for OLTP workloads where the working set fits in memory, including test environment, topology, TiKV settings, and QPS and 95% latency results for Point Select, Update Non-Index, and Update Index.
- Retrieval Keywords: TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0, v2.1.0-rc.2 vs. v2.0.6, OLTP where the working set fits in memory, Sysbench 1.1.0, 16 tables, 10,000,000 rows in each table, HAProxy, Point Select, Update Non-Index, Update Index, QPS, 95% Latency (ms), readpool.storage normal-concurrency = 8, server grpc-concurrency = 8, raftstore sync-log = false, rocksdb.defaultcf block-cache-size = "60GB", rocksdb.writecf block-cache-size = "20GB", cluster topology, TiDB parameter configuration, TiKV parameter configuration, GitHash, v2.1 point select 50%, self-managed benchmark
- Follow-up Guidance: The chunk also provides the exact test environment, component GitHash values for TiDB, TiKV, and PD, and the per-thread benchmark tables for 64, 128, 256, 512, and 1024 threads.
- Classification Note: This chunk is classified as performance for the TiDB component because the official content is a benchmark report comparing throughput and latency results between TiDB 2.1 and TiDB 2.0 under Sysbench OLTP tests.

## Official Source Content

# TiDB Sysbench Performance Test Report -- v2.1 vs. v2.0
## Test purpose

This test aims to compare the performance of TiDB 2.1 and TiDB 2.0 for OLTP where the working set fits in memory.
## Test version, time, and place

TiDB version: v2.1.0-rc.2 vs. v2.0.6

Time: September, 2018

Place: Beijing, China
## Test environment

IDC machine:

| Type | Name |
| :-: | :-: |
| OS | Linux (CentOS 7.3.1611) |
| CPU | 40 vCPUs, Intel(R) Xeon(R) CPU E5-2630 v4 @ 2.20GHz |
| RAM | 128GB |
| DISK | Optane 500GB SSD \* 1 |

Sysbench version: 1.1.0
## Test plan

Use Sysbench to import **16 tables, with 10,000,000 rows in each table**. With the HAProxy, requests are sent to the cluster at an incremental concurrent number. A single concurrent test lasts 5 minutes.
### TiDB version information
### v2.1.0-rc.2

| Component | GitHash |
| :-: | :-: |
| TiDB | 08e56cd3bae166b2af3c2f52354fbc9818717f62 |
| TiKV | 57e684016dafb17dc8a6837d30224be66cbc7246 |
| PD | 6a7832d2d6e5b2923c79683183e63d030f954563 |
### v2.0.6

| Component | GitHash |
| :-: | :-: |
| TiDB | b13bc08462a584a085f377625a7bab0cc0351570 |
| TiKV | 57c83dc4ebc93d38d77dc8f7d66db224760766cc |
| PD | b64716707b7279a4ae822be767085ff17b5f3fea |
### TiDB parameter configuration

The default TiDB configuration is used in both v2.1 and v2.0.
### TiKV parameter configuration

The following TiKV configuration is used in both v2.1 and v2.0:

```txt
[readpool.storage]
normal-concurrency = 8
[server]
grpc-concurrency = 8
[raftstore]
sync-log = false
[rocksdb.defaultcf]
block-cache-size = "60GB"
[rocksdb.writecf]
block-cache-size = "20GB"
```
### Cluster topology

| Machine IP | Deployment instance |
| :-: | :-: |
| 172.16.30.31 | 1\*Sysbench 1\*HAProxy |
| 172.16.30.32 | 1\*TiDB 1\*pd 1\*TiKV |
| 172.16.30.33 | 1\*TiDB 1\*TiKV |
| 172.16.30.34 | 1\*TiDB 1\*TiKV |
## Test result
### `Point Select` test

| Version | Threads | QPS | 95% Latency (ms) |
| :-: | :-: | :-: | :-: |
| v2.1 | 64   | 111481.09 | 1.16  |
| v2.1 | 128  | 145102.62 | 2.52  |
| v2.1 | 256  | 161311.9  | 4.57  |
| v2.1 | 512  | 184991.19 | 7.56  |
| v2.1 | 1024 | 230282.74 | 10.84 |
| v2.0 | 64   | 75285.87  | 1.93  |
| v2.0 | 128  | 92141.79  | 3.68  |
| v2.0 | 256  | 107464.93 | 6.67  |
| v2.0 | 512  | 121350.61 | 11.65 |
| v2.0 | 1024 | 150036.31 | 17.32 |

![point select](/media/sysbench_v3_point_select.png)

According to the statistics above, the `Point Select` query performance of TiDB 2.1 has increased by **50%** than that of TiDB 2.0.
### `Update Non-Index` test

| Version | Threads | QPS | 95% Latency (ms) |
| :-: | :-: | :-: | :-: |
| v2.1 | 64   | 18946.09 | 5.77   |
| v2.1 | 128  | 22022.82 | 12.08  |
| v2.1 | 256  | 24679.68 | 25.74  |
| v2.1 | 512  | 25107.1  | 51.94  |
| v2.1 | 1024 | 27144.92 | 106.75 |
| v2.0 | 64   | 16316.85 | 6.91   |
| v2.0 | 128  | 20944.6  | 11.45  |
| v2.0 | 256  | 24017.42 | 23.1   |
| v2.0 | 512  | 25994.33 | 46.63  |
| v2.0 | 1024 | 27917.52 | 92.42  |

![update non-index](/media/sysbench_v3_update_non_index.png)

According to the statistics above, the `Update Non-Index` write performance of TiDB 2.1 and TiDB 2.0 is almost the same.
### `Update Index` test

| Version | Threads | QPS | 95% Latency (ms) |
| :-: | :-: | :-: | :-: |
| v2.1 | 64   | 9934.49  | 12.08  |
| v2.1 | 128  | 10505.95 | 25.28  |
| v2.1 | 256  | 11007.7  | 55.82  |
| v2.1 | 512  | 11198.81 | 106.75 |
| v2.1 | 1024 | 11591.89 | 200.47 |
| v2.0 | 64   | 9754.68  | 11.65  |
| v2.0 | 128  | 10603.31 | 24.38  |
| v2.0 | 256  | 11011.71 | 50.11  |
| v2.0 | 512  | 11162.63 | 104.84 |
| v2.0 | 1024 | 12067.63 | 179.94 |

![update index](/media/sysbench_v3_update_index.png)

According to the statistics above, the `Update Index` write performance of TiDB 2.1 and TiDB 2.0 is almost the same.
