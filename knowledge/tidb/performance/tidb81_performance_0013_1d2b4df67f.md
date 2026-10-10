# Sysbench benchmark overview, environment, configuration, and test plan

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v5.2.0-vs-v5.1.1.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test overview | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test environment (AWS EC2） | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test environment (AWS EC2） > Hardware configuration | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test environment (AWS EC2） > Software version | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test environment (AWS EC2） > Parameter configuration | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test environment (AWS EC2） > Parameter configuration > TiDB parameter configuration | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test environment (AWS EC2） > Parameter configuration > TiKV parameter configuration | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test environment (AWS EC2） > Parameter configuration > TiDB global variable configuration | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test plan | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test plan > Prepare test data | TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1 > Test plan > Perform the test`
- Source Line Ranges: `5-125`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `tiup`
- Topic Tags: `sysbench`, `benchmarking`, `oltp`, `aws-ec2`, `hardware-configuration`, `software-version`, `parameter-configuration`, `global-variables`, `test-plan`, `data-preparation`, `workload-execution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0013_1d2b4df67f`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v5.2.0-vs-v5.1.1.md#tidb-sysbench-performance-test-report-v5-2-0-vs-v5-1-1`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `283f946820a69c316a0af671c41997a276fb73c026e50f682f5f782d98cc6d89`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v5.2.0-vs-v5.1.1#tidb-sysbench-performance-test-report-v5-2-0-vs-v5-1-1
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v5.2.0-vs-v5.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the Sysbench benchmark setup, AWS EC2 environment, TiDB and TiKV parameter configuration, TiDB global variables, or the exact data preparation and test execution commands for comparing TiDB v5.2.0 and v5.1.1 in an OLTP scenario.
- Retrieval Keywords: TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1, AWS EC2 hardware configuration, PD m5.xlarge, TiKV i3.4xlarge, TiDB c5.4xlarge, Sysbench c5.9xlarge, Sysbench 1.1.0-ead2689, performance.max-procs: 20, prepared-plan-cache.enabled: true, tikv-client.max-batch-wait-time: 2000000, storage.scheduler-worker-pool-size: 5, server.enable-request-batch: false, pessimistic-txn.pipelined: true, set global tidb_enable_async_commit = 1;, set global tidb_enable_1pc = 1;, set global tidb_guarantee_linearizability = 0;, set global tidb_enable_clustered_index = 1;, analyze table, HAProxy, sysbench oltp_common prepare --tables=16 --table-size=10000000, sysbench $testname --time=300 run --tables=16 --table-size=10000000
- Follow-up Guidance: The source also lists the benchmark results for point_select, update_non_index, update_index, and read_write workloads with QPS and 95% latency comparisons.
- Classification Note: This chunk is classified as performance because it defines the benchmark environment, component settings, workload plan, and Sysbench commands used to measure TiDB OLTP performance.

## Official Source Content

# TiDB Sysbench Performance Test Report -- v5.2.0 vs. v5.1.1
## Test overview

This test aims at comparing the Sysbench performance of TiDB v5.2.0 and TiDB v5.1.1 in the Online Transactional Processing (OLTP) scenario. The results show that compared with v5.1.1, the Point Select performance of v5.2.0 is improved by 11.03%, and the performance of other scenarios is slightly reduced.
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
| PD        | v5.1.1 and v5.2.0   |
| TiDB      | v5.1.1 and v5.2.0   |
| TiKV      | v5.1.1 and v5.2.0   |
| Sysbench  | 1.1.0-ead2689   |
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
2. Use Sysbench to import 16 tables, each table with 10 million rows of data.
3. Execute the `analyze table` statement on each table.
4. Back up the data used for restore before different concurrency tests, which ensures data consistency for each test.
5. Start the Sysbench client to perform the `point_select`, `read_write`, `update_index`, and `update_non_index` tests. Perform stress tests on TiDB via HAProxy. The test takes 5 minutes.
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

Execute the following command to perform the test:

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
