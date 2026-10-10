# TPC-C benchmark report for TiDB v3.0 vs v2.1

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v3.0-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1`
- Source Heading Path: `TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 | TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 > Test purpose | TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 > Test version, time, and place | TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 > Test environment | TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 > Test plan | TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 > Test plan > TiDB version information | TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 > Test plan > v3.0.0 | TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 > Test plan > v2.1.13 | TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 > Test plan > TiDB parameter configuration | TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 > Test plan > TiKV parameter configuration | TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 > Test plan > Cluster topology | TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1 > Test result`
- Source Line Ranges: `5-97`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `sql`, `shared`
- Topic Tags: `tpcc`, `benchmarksql`, `performance-testing`, `test-environment`, `test-plan`, `version-comparison`, `parameter-configuration`, `cluster-topology`, `throughput`, `tpmc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0040_9359881ed0`
- Source ID: `tidb-docs-8.1:benchmark/v3.0-performance-benchmarking-with-tpcc.md#tidb-tpc-c-performance-test-report-v3-0-vs-v2-1`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e74c608eb375a93a8db6c6ea537d5288fff9108a427b5b51c3105b8d1098e60`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v3.0-performance-benchmarking-with-tpcc#tidb-tpc-c-performance-test-report-v3-0-vs-v2-1
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v3.0-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TPC-C benchmark performance between TiDB v3.0.0 and v2.1.13, including BenchmarkSQL setup, cluster topology, parameter configuration, and tpmC results.
- Retrieval Keywords: TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1, v3.0.0 vs. v2.1.13, BenchmarkSQL 5.0, 5.0-mysql-support-opt, 1000 warehouses, HAProxy, tpmC, Threads 128 256 512, prepared_plan_cache enabled = true, max-procs = 20, default TiKV configuration, 2*TiDB 2*TiKV 1*pd, performance has increased by 450%
- Follow-up Guidance: The content also provides the test environment, component GitHash values for TiDB, TiKV, and PD, and the exact tpmC results for thread counts 128, 256, and 512.
- Classification Note: This is classified as performance content because it is a benchmark report focused on throughput comparison for TiDB using TPC-C and BenchmarkSQL under a specified test environment and topology.

## Official Source Content

# TiDB TPC-C Performance Test Report -- v3.0 vs. v2.1
## Test purpose

This test aims to compare the TPC-C performance of TiDB 3.0 and TiDB 2.1.
## Test version, time, and place

TiDB version: v3.0.0 vs. v2.1.13

Time: June, 2019

Place: Beijing
## Test environment

IDC machine:

| Type | Name |
| :-- | :-- |
| OS | Linux (CentOS 7.3.1611) |
| CPU | 40 vCPUs, Intel(R) Xeon(R) CPU E5-2630 v4 @ 2.20GHz |
| RAM | 128GB |
| DISK | 1.5TB SSD \* 2 |

This test uses the open-source BenchmarkSQL 5.0 as the TPC-C testing tool and adds the support for the MySQL protocol. You can download the testing program by using the following command:

```shell
git clone -b 5.0-mysql-support-opt https://github.com/pingcap/benchmarksql.git
```
## Test plan

Use BenchmarkSQL to load the data of **1000 warehouses** into the TiDB cluster. By using HAProxy, send concurrent requests to the cluster at an incremental number. A single concurrent test lasts 10 minutes.
### TiDB version information
### v3.0.0

| Component | GitHash |
| :-- | :-- |
| TiDB | 46c38e15eba43346fb3001280c5034385171ee20 |
| TiKV | a467f410d235fa9c5b3c355e3b620f81d3ac0e0c |
| PD | 70aaa5eee830e21068f1ba2d4c9bae59153e5ca3 |
### v2.1.13

| Component | GitHash |
| :-- | :-- |
| TiDB | 6b5b1a6802f9b8f5a22d8aab24ac80729331e1bc |
| TiKV | b3cf3c8d642534ea6fa93d475a46da285cc6acbf |
| PD | 886362ebfb26ef0834935afc57bcee8a39c88e54 |
### TiDB parameter configuration

```toml
[log]
level = "error"
[performance]
max-procs = 20
[prepared_plan_cache]
enabled = true
```
### TiKV parameter configuration

The default TiKV configuration is used in both v2.1 and v3.0.
### Cluster topology

| Machine IP | Deployment instance |
| :-- | :-- |
| 172.16.4.75 | 2\*TiDB 2\*TiKV 1\*pd |
| 172.16.4.76 | 2\*TiDB 2\*TiKV 1\*pd |
| 172.16.4.77 | 2\*TiDB 2\*TiKV 1\*pd |
## Test result

| Version | Threads | tpmC |
| :-- | :-- | :-- |
| v3.0 | 128  | 44068.55 |
| v3.0 | 256  | 47094.06  |
| v3.0 | 512  | 48808.65 |
| v2.1 | 128  | 10641.71  |
| v2.1 | 256  | 10861.62 |
| v2.1 | 512  | 10965.39 |

![point select](/media/tpcc-2.1-3.0.png)

According to the testing statistics, the performance of TiDB 3.0 **has increased by 450%** than that of TiDB 2.1.
