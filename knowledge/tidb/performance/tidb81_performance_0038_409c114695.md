# Sysbench benchmark setup, versions, and configuration

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v3.0-performance-benchmarking-with-sysbench.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test purpose | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test version, time, and place | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test environment | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test plan | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test plan > TiDB version information | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test plan > v3.0.0 | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test plan > v2.1.13 | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test plan > TiDB parameter configuration | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test plan > TiKV parameter configuration | TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1 > Test plan > Cluster topology`
- Source Line Ranges: `5-161`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `sysbench`, `oltp`, `benchmarking`, `test-environment`, `test-plan`, `version-comparison`, `parameter-configuration`, `cluster-topology`, `plan-cache`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0038_409c114695`
- Source ID: `tidb-docs-8.1:benchmark/v3.0-performance-benchmarking-with-sysbench.md#tidb-sysbench-performance-test-report-v3-0-vs-v2-1`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `067ba84196d1c3d62d9e83c5ebd8dc3cf81742925c1e65164b5cfebeb1630a47`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v3.0-performance-benchmarking-with-sysbench#tidb-sysbench-performance-test-report-v3-0-vs-v2-1
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v3.0-performance-benchmarking-with-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the Sysbench benchmark setup for comparing TiDB v3.0.0 and v2.1.13, including environment, commands, parameter configuration, and cluster topology.
- Retrieval Keywords: TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1, v3.0.0 vs. v2.1.13, Sysbench 1.0.17, AWS EC2, CentOS-7.6.1810-Nitro, sysbench oltp_common prepare --tables=16 --table-size=10000000, run --tables=16 --table-size=10000000, prepared-plan-cache enabled = true, set global tidb_hashagg_final_concurrency=1, set global tidb_hashagg_partial_concurrency=1, set global tidb_disable_txn_auto_retry=0, tikv-client max-batch-wait-time = 2000000, readpool.storage normal-concurrency = 10, server grpc-concurrency = 6, rocksdb.defaultcf block-cache-size = 14GB, rocksdb.writecf block-cache-size = 8GB, rocksdb.lockcf block-cache-size = 1GB, raftstore apply-pool-size = 3, raftstore store-pool-size = 3, cluster topology, 3 * Sysbench, PD r5d.xlarge, TiKV c5d.4xlarge, TiDB c5.4xlarge
- Follow-up Guidance: The same document also provides Sysbench test results for `Point Select`, `Update Non-Index`, `Update Index`, and `Read Write` with QPS and 95% latency.
- Classification Note: This is classified as performance content because it defines the benchmark purpose, workload, versions, hardware environment, configuration parameters, and topology used for the Sysbench OLTP comparison.

## Official Source Content

# TiDB Sysbench Performance Test Report -- v3.0 vs. v2.1
## Test purpose

This test aims to compare the performance of TiDB 3.0 and TiDB 2.1 in the OLTP scenario.
## Test version, time, and place

TiDB version: v3.0.0 vs. v2.1.13

Time: June, 2019

Place: Beijing
## Test environment

This test runs on AWS EC2 and uses the CentOS-7.6.1810-Nitro (ami-028946f4cffc8b916) image. The components and types of instances are as follows:

| Component  |  Instance type  |
| :--- | :-------- |
|  PD   | r5d.xlarge |
| TiKV  | c5d.4xlarge |
| TiDB  | c5.4xlarge |

Sysbench version: 1.0.17
## Test plan

Use Sysbench to import **16 tables, with 10,000,000 rows in each table**. Start three sysbench to add pressure to three TiDB instances. The number of concurrent requests increases incrementally. A single concurrent test lasts 5 minutes.

Prepare data using the following command:

```sh
sysbench oltp_common \
    --threads=16 \
    --rand-type=uniform \
    --db-driver=mysql \
    --mysql-db=sbtest \
    --mysql-host=$tidb_host \
    --mysql-port=$tidb_port \
    --mysql-user=root \
    --mysql-password=password \
    prepare --tables=16 --table-size=10000000
```

Then test TiDB using the following command:

```sh
sysbench $testname \
    --threads=$threads \
    --time=300 \
    --report-interval=15 \
    --rand-type=uniform \
    --rand-seed=$RANDOM \
    --db-driver=mysql \
    --mysql-db=sbtest \
    --mysql-host=$tidb_host \
    --mysql-port=$tidb_port \
    --mysql-user=root \
    --mysql-password=password \
    run --tables=16 --table-size=10000000
```
### TiDB version information
### v3.0.0

| Component  |                 GitHash                |
| :--- | :-------------------------------------- |
| TiDB  | `8efbe62313e2c1c42fd76d35c6f020087eef22c2` |
| TiKV  | `a467f410d235fa9c5b3c355e3b620f81d3ac0e0c` |
|  PD   | `70aaa5eee830e21068f1ba2d4c9bae59153e5ca3` |
### v2.1.13

| Component  |                 GitHash                  |
| :--- | :-------------------------------------- |
| TiDB  | `6b5b1a6802f9b8f5a22d8aab24ac80729331e1bc` |
| TiKV  | `b3cf3c8d642534ea6fa93d475a46da285cc6acbf` |
|  PD   | `886362ebfb26ef0834935afc57bcee8a39c88e54` |
### TiDB parameter configuration

Enable the prepared plan cache in both TiDB v2.1 and v3.0 (`point select` and `read write` are not enabled in v2.1 for optimization reasons):

```toml
[prepared-plan-cache]
enabled = true
```

Then configure global variables:

```sql
set global tidb_hashagg_final_concurrency=1;
```

```sql
set global tidb_hashagg_partial_concurrency=1;
```

```sql
set global tidb_disable_txn_auto_retry=0;
```

In addition, make the following configuration in v3.0:

```toml
[tikv-client]
max-batch-wait-time = 2000000
```
### TiKV parameter configuration

Configure the global variable in both TiDB v2.1 and v3.0:

```toml
log-level = "error"
[readpool.storage]
normal-concurrency = 10
[server]
grpc-concurrency = 6
[rocksdb.defaultcf]
block-cache-size = "14GB"
[rocksdb.writecf]
block-cache-size = "8GB"
[rocksdb.lockcf]
block-cache-size = "1GB"
```

In addition, make the following configuration in v3.0:

```toml
[raftstore]
apply-pool-size = 3
store-pool-size = 3
```
### Cluster topology

|                 Machine IP                  |  Deployment instance  |
| :-------------------------------------- | :--------- |
|                172.31.8.8                | 3 * Sysbench |
| 172.31.7.80, 172.31.5.163, 172.31.11.123 |      PD      |
| 172.31.4.172, 172.31.1.155, 172.31.9.210 |     TiKV     |
| 172.31.7.80, 172.31.5.163, 172.31.11.123 |     TiDB     |
