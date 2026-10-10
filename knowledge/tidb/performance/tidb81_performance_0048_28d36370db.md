# TPC-C benchmark report for TiDB v5.2.0 vs v5.1.1

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v5.2-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1`
- Source Heading Path: `TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1 | TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1 > Test overview | TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1 > Test environment (AWS EC2) | TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1 > Hardware configuration | TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1 > Hardware configuration > Software version | TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1 > Hardware configuration > Parameter configuration | TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1 > Hardware configuration > Parameter configuration > TiDB parameter configuration | TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1 > Hardware configuration > Parameter configuration > TiKV parameter configuration | TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1 > Hardware configuration > Parameter configuration > TiDB global variable configuration | TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1 > Test plan | TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1 > Test result`
- Source Line Ranges: `5-93`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `tiup`
- Topic Tags: `tpcc`, `benchmarking`, `oltp`, `aws-ec2`, `hardware-configuration`, `software-version`, `parameter-configuration`, `global-variables`, `benchmarksql`, `tiup`, `stress-testing`, `tpmmc-results`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0048_28d36370db`
- Source ID: `tidb-docs-8.1:benchmark/v5.2-performance-benchmarking-with-tpcc.md#tidb-tpc-c-performance-test-report-v5-2-0-vs-v5-1-1`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f906d3f00ef328d523c842ab7744602af81ca589d5590a700cbf16bde2b01a83`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v5.2-performance-benchmarking-with-tpcc#tidb-tpc-c-performance-test-report-v5-2-0-vs-v5-1-1
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v5.2-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the official TPC-C benchmark comparison between TiDB v5.2.0 and v5.1.1, including the AWS EC2 test environment, BenchmarkSQL workload setup, configuration, and the reported performance change.
- Retrieval Keywords: TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1, TPC-C benchmark report for TiDB v5.2.0 vs v5.1.1, OLTP scenario, AWS EC2, BenchmarkSQL, tiup bench tpcc prepare --warehouses 5000 --db tpcc -H 127.0.0.1 -p 4000, tiup bench tpcc run -U root --db tpcc --host 127.0.0.1 --port 4000 --time 300s --warehouses 5000 --threads {{thread}}, create database tpcc;, tpmC data of New Order, reduced by 4.22%, PD m5.xlarge, TiKV i3.4xlarge, TiDB c5.4xlarge, TPC-C c5.9xlarge, TiUP 1.5.1, prepared-plan-cache.enabled, tikv-client.max-batch-wait-time, pessimistic-txn.pipelined, server.enable-request-batch, tidb_enable_async_commit, tidb_enable_1pc, tidb_guarantee_linearizability, tidb_enable_clustered_index
- Follow-up Guidance: The source also provides the exact hardware configuration, software versions, TiDB and TiKV parameter configuration, TiDB global variable settings, and the five-step test plan used for the benchmark.
- Classification Note: This chunk is classified as performance for the tidb component because the official content is a benchmark report comparing TPC-C OLTP throughput results between TiDB v5.2.0 and v5.1.1.

## Official Source Content

# TiDB TPC-C Performance Test Report -- v5.2.0 vs. v5.1.1
## Test overview

This test aims to compare the TPC-C performance of TiDB v5.2.0 and TiDB v5.1.1 in the online transactional processing (OLTP) scenario. The results show that compared with v5.1.1, the TPC-C performance of v5.2.0 is reduced by 4.22%.
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
| PD        | v5.1.1 and v5.2.0   |
| TiDB      | v5.1.1 and v5.2.0   |
| TiKV      | v5.1.1 and v5.2.0   |
| TiUP  | 1.5.1     |
### Parameter configuration

TiDB v5.2.0 and TiDB v5.1.1 use the same configuration.
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

1. Deploy TiDB v5.2.0 and v5.1.1 using TiUP.
2. Create a database named `tpcc`: `create database tpcc;`.
3. Use BenchmarkSQL to import the TPC-C 5000 Warehouse data: `tiup bench tpcc prepare --warehouses 5000 --db tpcc -H 127.0.0.1 -p 4000`.
4. Execute the `tiup bench tpcc run -U root --db tpcc --host 127.0.0.1 --port 4000 --time 300s --warehouses 5000 --threads {{thread}}` command to perform stress tests on TiDB via HAProxy.
5. Extract the tpmC data of New Order from the result.
## Test result

Compared with v5.1.1, the TPC-C performance of v5.2.0 is **reduced by 4.22%**.

![TPC-C](/media/tpcc_v511_vs_v520.png)
