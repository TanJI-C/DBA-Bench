# TPC-C v5.1.0 vs v5.0.2 benchmark environment, configuration, plan, and result

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v5.1-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2`
- Source Heading Path: `TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2 | TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2 > Test overview | TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2 > Test environment (AWS EC2) | TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2 > Hardware configuration | TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2 > Hardware configuration > Software version | TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2 > Hardware configuration > Parameter configuration | TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2 > Hardware configuration > Parameter configuration > TiDB parameter configuration | TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2 > Hardware configuration > Parameter configuration > TiKV parameter configuration | TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2 > Hardware configuration > Parameter configuration > TiDB global variable configuration | TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2 > Test plan | TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2 > Test result`
- Source Line Ranges: `5-93`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `tiup`, `shared`
- Topic Tags: `tpcc`, `benchmark`, `aws-ec2`, `hardware-configuration`, `software-version`, `parameter-configuration`, `global-variables`, `tiup`, `benchmarksql`, `stress-test`, `tpmc`, `performance-result`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0047_b5e71b7b3c`
- Source ID: `tidb-docs-8.1:benchmark/v5.1-performance-benchmarking-with-tpcc.md#tidb-tpc-c-performance-test-report-v5-1-0-vs-v5-0-2`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2782ac7d88ea2950b8c290e9992bff5ca0d7e8eebdb88432e0839b829a765174`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v5.1-performance-benchmarking-with-tpcc#tidb-tpc-c-performance-test-report-v5-1-0-vs-v5-0-2
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v5.1-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB v5.1.0 vs v5.0.2 TPC-C benchmark setup on AWS EC2, including hardware, parameter configuration, BenchmarkSQL test plan, and the reported tpmC comparison result.
- Retrieval Keywords: TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2, AWS EC2, BenchmarkSQL, tiup bench tpcc prepare --warehouses 5000 --db tpcc -H 127.0.0.1 -p 4000, tiup bench tpcc run -U root --db tpcc --host 127.0.0.1 --port 4000 --time 300s --warehouses 5000 --threads {{thread}}, create database tpcc;, tpmC, New Order, v5.1.0, v5.0.2, m5.xlarge, i3.4xlarge, c5.4xlarge, c5.9xlarge, prepared-plan-cache.enabled: true, pessimistic-txn.pipelined: true, set global tidb_enable_async_commit = 1;, set global tidb_enable_1pc = 1;, set global tidb_guarantee_linearizability = 0;, TPC-C performance improved by 2.8%
- Follow-up Guidance: The chunk also provides the exact TiDB and TiKV parameter configuration, TiDB global variable settings, and the sequence of test steps used to obtain the result.
- Classification Note: This chunk is classified as performance for the TiDB component because it reports a benchmark comparison between TiDB v5.1.0 and v5.0.2 with detailed environment, configuration, test procedure, and performance result.

## Official Source Content

# TiDB TPC-C Performance Test Report -- v5.1.0 vs. v5.0.2
## Test overview

This test aims to compare the TPC-H performance of TiDB v5.1.0 and TiDB v5.0.2 in the online analytical processing (OLAP) scenario. The results show that compared with v5.0.2, the TPC-C performance of v5.1.0 is improved by 2.8%.
## Test environment (AWS EC2)
## Hardware configuration

| Service type         | EC2 type     | Instance count |
|:----------|:----------|:----------|
| PD        | m5.xlarge |     3     |
| TiKV      | i3.4xlarge|     3     |
| TiDB      | c5.4xlarge|     3     |
| TPC-C  | c5.9xlarge|     1     |
### Software version

| Service type   | Software version    |
|:----------|:-----------|
| PD        | v5.0.2 and v5.1.0   |
| TiDB      | v5.0.2 and v5.1.0   |
| TiKV      | v5.0.2 and v5.1.0   |
| TiUP  | 1.5.1     |
### Parameter configuration

TiDB v5.1.0 and TiDB v5.0.2 use the same configuration.
#### TiDB parameter configuration

```yaml
log.level: "error"
performance.max-procs: 20
prepared-plan-cache.enabled: true
tikv-client.max-batch-wait-time: 2000000
```
#### TiKV parameter configuration

```yaml
pessimistic-txn.pipelined: true
raftdb.allow-concurrent-memtable-write: true
raftdb.max-background-jobs: 4
raftstore.apply-max-batch-size: 2048
raftstore.apply-pool-size: 3
raftstore.store-max-batch-size: 2048
raftstore.store-pool-size: 3
readpool.storage.normal-concurrency: 10
readpool.unified.max-thread-count: 20
readpool.unified.min-thread-count: 5
rocksdb.max-background-jobs: 8
server.grpc-concurrency: 6
storage.scheduler-worker-pool-size: 20
server.enable-request-batch: false
```
#### TiDB global variable configuration

```sql
set global tidb_hashagg_final_concurrency=1;
set global tidb_hashagg_partial_concurrency=1;
set global tidb_enable_async_commit = 1;
set global tidb_enable_1pc = 1;
set global tidb_guarantee_linearizability = 0;
set global tidb_enable_clustered_index = 1;
```
## Test plan

1. Deploy TiDB v5.1.0 and v5.0.2 using TiUP.
2. Create a database named `tpcc`: `create database tpcc;`.
3. Use BenchmarkSQL to import the TPC-C 5000 Warehouse data: `tiup bench tpcc prepare --warehouses 5000 --db tpcc -H 127.0.0.1 -p 4000`.
4. Execute the `tiup bench tpcc run -U root --db tpcc --host 127.0.0.1 --port 4000 --time 300s --warehouses 5000 --threads {{thread}}` command to perform stress tests on TiDB via HAProxy.
5. Extract the tpmC data of New Order from the result.
## Test result

Compared with v5.0.2, the TPC-C performance of v5.1.0 is **improved by 2.8%**.

![TPC-C](/media/tpcc_v510_vs_v502.png)
