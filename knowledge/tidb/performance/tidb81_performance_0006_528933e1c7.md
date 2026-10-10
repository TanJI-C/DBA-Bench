# Sysbench benchmark setup and test procedure

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v4-vs-v3.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test purpose | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2） | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2） > Hardware configuration | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2） > Software version | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2） > Parameter configuration | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2） > Parameter configuration > TiDB v3.0 configuration | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2） > Parameter configuration > TiKV v3.0 configuration | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2） > Parameter configuration > TiDB v4.0 configuration | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2） > Parameter configuration > TiKV v4.0 configuration | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2） > Parameter configuration > Global variable configuration | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test plan | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test plan > Prepare test data | TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0 > Test plan > Perform the test`
- Source Line Ranges: `5-146`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `tiup`, `shared`
- Topic Tags: `sysbench`, `benchmarking`, `oltp`, `test-environment`, `hardware`, `software-version`, `parameter-configuration`, `global-variables`, `test-plan`, `data-preparation`, `workload-execution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0006_528933e1c7`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v4-vs-v3.md#tidb-sysbench-performance-test-report-v4-0-vs-v3-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e8573a710d184a61aa4a51efa99cde648acc3ea30af29db49dfe3612b8eaf4dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v4-vs-v3#tidb-sysbench-performance-test-report-v4-0-vs-v3-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v4-vs-v3.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact Sysbench benchmark environment, parameter configuration, global variables, and test procedure for comparing TiDB v4.0 and v3.0 in an OLTP scenario.
- Retrieval Keywords: TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0, AWS EC2 hardware configuration, PD m5.xlarge 3, TiKV i3.4xlarge 3, TiDB c5.4xlarge 3, Sysbench m5.4xlarge 1, Sysbench 1.0.20, prepared-plan-cache.enabled, tikv-client.max-batch-wait-time, storage.scheduler-worker-pool-size, server.grpc-concurrency, readpool.unified.min-thread-count, pessimistic-txn.pipelined, set global tidb_hashagg_final_concurrency=1, set global tidb_hashagg_partial_concurrency=1, set global tidb_disable_txn_auto_retry=0, analyze table, sysbench oltp_common prepare --tables=16 --table-size=10000000, sysbench $testname --time=300 --report-interval=1, point_select, read_write, update_index, update_non_index, AWS NLB, TiUP
- Follow-up Guidance: The source also provides the exact Sysbench prepare command and run command used for the tests.
- Classification Note: This chunk is classified as performance because it defines the benchmark purpose, environment, configuration, and workload execution steps used to measure TiDB OLTP performance.

## Official Source Content

# TiDB Sysbench Performance Test Report -- v4.0 vs. v3.0
## Test purpose

This test aims to compare the Sysbench performance of TiDB 4.0 and TiDB 3.0 in the Online Transactional Processing (OLTP) scenario.
## Test environment (AWS EC2）
### Hardware configuration

| Service type         | EC2 type     | Instance count |
|:----------|:----------|:----------|
| PD        | m5.xlarge |     3     |
| TiKV      | i3.4xlarge|     3     |
| TiDB      | c5.4xlarge|     3     |
| Sysbench  | m5.4xlarge|     1     |
### Software version

| Service type   | Software version    |
|:----------|:-----------|
| PD        | 3.0 and 4.0   |
| TiDB      | 3.0 and 4.0   |
| TiKV      | 3.0 and 4.0   |
| Sysbench  | 1.0.20     |
### Parameter configuration
#### TiDB v3.0 configuration

```yaml
log.level: "error"
performance.max-procs: 20
prepared-plan-cache.enabled: true
tikv-client.max-batch-wait-time: 2000000
```
#### TiKV v3.0 configuration

```yaml
storage.scheduler-worker-pool-size: 5
raftstore.store-pool-size: 3
raftstore.apply-pool-size: 3
rocksdb.max-background-jobs: 3
raftdb.max-background-jobs: 3
raftdb.allow-concurrent-memtable-write: true
server.grpc-concurrency: 6
readpool.storage.normal-concurrency: 10
readpool.coprocessor.normal-concurrency: 5
```
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
#### Global variable configuration

```sql
set global tidb_hashagg_final_concurrency=1;
set global tidb_hashagg_partial_concurrency=1;
set global tidb_disable_txn_auto_retry=0;
```
## Test plan

1. Deploy TiDB v4.0 and v3.0 using TiUP.
2. Use Sysbench to import 16 tables, each table with 10 million rows of data.
3. Execute the `analyze table` statement on each table.
4. Back up the data used for restore before different concurrency tests, which ensures data consistency for each test.
5. Start the Sysbench client to perform the `point_select`, `read_write`, `update_index`, and `update_non_index` tests. Perform stress tests on TiDB via AWS NLB. In each type of test, the warm-up takes 1 minute and the test takes 5 minutes.
6. After each type of test is completed, stop the cluster, overwrite the cluster with the backup data in step 4, and restart the cluster.
### Prepare test data

Execute the following command to prepare the test data:

```bash
sysbench oltp_common \
    --threads=16 \
    --rand-type=uniform \
    --db-driver=mysql \
    --mysql-db=sbtest \
    --mysql-host=$aws_nlb_host \
    --mysql-port=$aws_nlb_port \
    --mysql-user=root \
    --mysql-password=password \
    prepare --tables=16 --table-size=10000000
```
### Perform the test

Execute the following command to perform the test.

```bash
sysbench $testname \
    --threads=$threads \
    --time=300 \
    --report-interval=1 \
    --rand-type=uniform \
    --db-driver=mysql \
    --mysql-db=sbtest \
    --mysql-host=$aws_nlb_host \
    --mysql-port=$aws_nlb_port \
    run --tables=16 --table-size=10000000
```
