# TPC-C benchmark purpose and environment configurations

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v5.0-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0`
- Source Heading Path: `TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test purpose | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2) | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2) > Hardware configuration | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2) > Software version | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2) > Parameter configuration | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2) > Parameter configuration > TiDB v4.0 configuration | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2) > Parameter configuration > TiKV v4.0 configuration | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2) > Parameter configuration > TiDB v5.0 configuration | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2) > Parameter configuration > TiKV v5.0 configuration | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2) > Parameter configuration > TiDB v4.0 global variable configuration | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2) > Parameter configuration > TiDB v5.0 global variable configuration`
- Source Line Ranges: `5-118`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`, `sql`
- Topic Tags: `tpcc`, `benchmarking`, `test-environment`, `hardware-configuration`, `software-version`, `parameter-configuration`, `global-variables`, `aws-ec2`, `oltp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0045_7ce9c70474`
- Source ID: `tidb-docs-8.1:benchmark/v5.0-performance-benchmarking-with-tpcc.md#tidb-tpc-c-performance-test-report-v5-0-vs-v4-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6660ef3118683933b9f617867f898e93ee13359e31fa04f2f761596b7cffc98f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v5.0-performance-benchmarking-with-tpcc#tidb-tpc-c-performance-test-report-v5-0-vs-v4-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v5.0-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when you need the stated purpose and exact AWS EC2 hardware, software, TiDB/TiKV parameter, or TiDB global variable settings for the TiDB v5.0 versus v4.0 TPC-C OLTP benchmark environment.
- Retrieval Keywords: TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0, Test purpose, OLTP scenario, AWS EC2, Hardware configuration, PD m5.xlarge 3, TiKV i3.4xlarge 3, TiDB c5.4xlarge 3, TPC-C c5.9xlarge 1, Software version 4.0 and 5.0, BenchmarkSQL, log.level: "error", performance.max-procs: 20, prepared-plan-cache.enabled: true, tikv-client.max-batch-wait-time: 2000000, pessimistic-txn.pipelined: true, raftdb.allow-concurrent-memtable-write: true, raftstore.apply-max-batch-size: 2048, readpool.unified.max-thread-count: 20, server.grpc-concurrency: 6, storage.scheduler-worker-pool-size: 20, server.enable-request-batch: false, set global tidb_hashagg_final_concurrency=1, set global tidb_hashagg_partial_concurrency=1, set global tidb_enable_async_commit = 1, set global tidb_enable_1pc = 1, set global tidb_guarantee_linearizability = 0, set global tidb_enable_clustered_index = 1
- Follow-up Guidance: The source also provides the benchmark test plan steps and the reported TPC-C result comparing v5.0 with v4.0.
- Classification Note: This is classified as performance because the content defines a TPC-C benchmark comparison environment and exact configuration settings used to measure TiDB v5.0 versus v4.0 performance.

## Official Source Content

# TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0
## Test purpose

This test aims at comparing the TPC-C performance of TiDB v5.0 and TiDB v4.0 in the Online Transactional Processing (OLTP) scenario.
## Test environment (AWS EC2)
### Hardware configuration

| Service type   | EC2 type   |    Instance count  |
|:----------|:----------|:----------|
| PD        | m5.xlarge |     3     |
| TiKV      | i3.4xlarge|     3     |
| TiDB      | c5.4xlarge|     3     |
| TPC-C  | c5.9xlarge|     1     |
### Software version

| Service type   | Software version    |
|:----------|:-----------|
| PD        | 4.0 and 5.0   |
| TiDB      | 4.0 and 5.0   |
| TiKV      | 4.0 and 5.0   |
| BenchmarkSQL  | None     |
### Parameter configuration
#### TiDB v4.0 configuration

```yaml
log.level: "error"
performance.max-procs: 20
prepared-plan-cache.enabled: true
tikv-client.max-batch-wait-time: 2000000
```
#### TiKV v4.0 configuration

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
```
#### TiDB v5.0 configuration

```yaml
log.level: "error"
performance.max-procs: 20
prepared-plan-cache.enabled: true
tikv-client.max-batch-wait-time: 2000000
```
#### TiKV v5.0 configuration

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
#### TiDB v4.0 global variable configuration

```sql
set global tidb_hashagg_final_concurrency=1;
set global tidb_hashagg_partial_concurrency=1;
```
#### TiDB v5.0 global variable configuration

```sql
set global tidb_hashagg_final_concurrency=1;
set global tidb_hashagg_partial_concurrency=1;
set global tidb_enable_async_commit = 1;
set global tidb_enable_1pc = 1;
set global tidb_guarantee_linearizability = 0;
set global tidb_enable_clustered_index = 1;
```
