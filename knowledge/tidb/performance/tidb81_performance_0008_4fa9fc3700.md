# Sysbench benchmark purpose and AWS EC2 test environment

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v5-vs-v4.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test purpose | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2） | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2） > Hardware configuration | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2） > Software version | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2） > Parameter configuration | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2） > Parameter configuration > TiDB v4.0 configuration | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2） > Parameter configuration > TiKV v4.0 configuration | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2） > Parameter configuration > TiDB v5.0 configuration | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2） > Parameter configuration > TiKV v5.0 configuration | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2） > Parameter configuration > TiDB v4.0 global variable configuration | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test environment (AWS EC2） > Parameter configuration > TiDB v5.0 global variable configuration`
- Source Line Ranges: `5-115`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`, `sql`
- Topic Tags: `sysbench`, `benchmark`, `oltp`, `aws-ec2`, `hardware`, `software-version`, `parameter-configuration`, `global-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0008_4fa9fc3700`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v5-vs-v4.md#tidb-sysbench-performance-test-report-v5-0-vs-v4-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ed1fda910dc3b95d9833cf66440e1d14a2e9a6cc2aaece7cc85e72f4b8520e75`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v5-vs-v4#tidb-sysbench-performance-test-report-v5-0-vs-v4-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v5-vs-v4.md

## Retrieval Guidance

- Use When: Use this chunk when you need the purpose of the Sysbench comparison and the AWS EC2 hardware, software, and TiDB/TiKV configuration details for TiDB v4.0 and v5.0.
- Retrieval Keywords: TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0, Test purpose, AWS EC2, Hardware configuration, Software version, Parameter configuration, TiDB v4.0 configuration, TiKV v4.0 configuration, TiDB v5.0 configuration, TiKV v5.0 configuration, TiDB v4.0 global variable configuration, TiDB v5.0 global variable configuration, prepared-plan-cache.enabled, tikv-client.max-batch-wait-time, tidb_enable_async_commit, tidb_enable_1pc, tidb_enable_clustered_index
- Follow-up Guidance: Refer to the parameter configuration sections for the exact YAML and SQL settings used in each version.
- Classification Note: This chunk is classified as a performance test report for comparing TiDB v5.0 and TiDB v4.0 in an OLTP scenario.

## Official Source Content

# TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0
## Test purpose

This test aims at comparing the Sysbench performance of TiDB v5.0 and TiDB v4.0 in the Online Transactional Processing (OLTP) scenario.
## Test environment (AWS EC2）
### Hardware configuration

| Service type         | EC2 type     | Instance count |
|:----------|:----------|:----------|
| PD        | m5.xlarge |     3     |
| TiKV      | i3.4xlarge|     3     |
| TiDB      | c5.4xlarge|     3     |
| Sysbench  | c5.9xlarge|     1     |
### Software version

| Service type   | Software version    |
|:----------|:-----------|
| PD        | 4.0 and 5.0   |
| TiDB      | 4.0 and 5.0   |
| TiKV      | 4.0 and 5.0   |
| Sysbench  | 1.0.20     |
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
storage.scheduler-worker-pool-size: 5
raftstore.store-pool-size: 3
raftstore.apply-pool-size: 3
rocksdb.max-background-jobs: 3
raftdb.max-background-jobs: 3
raftdb.allow-concurrent-memtable-write: true
server.grpc-concurrency: 6
readpool.unified.min-thread-count: 5
readpool.unified.max-thread-count: 20
readpool.storage.normal-concurrency: 10
pessimistic-txn.pipelined: true
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
storage.scheduler-worker-pool-size: 5
raftstore.store-pool-size: 3
raftstore.apply-pool-size: 3
rocksdb.max-background-jobs: 8
raftdb.max-background-jobs: 4
raftdb.allow-concurrent-memtable-write: true
server.grpc-concurrency: 6
readpool.unified.min-thread-count: 5
readpool.unified.max-thread-count: 20
readpool.storage.normal-concurrency: 10
pessimistic-txn.pipelined: true
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
