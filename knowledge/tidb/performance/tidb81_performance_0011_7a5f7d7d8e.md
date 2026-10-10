# Sysbench test overview, environment, configuration, and procedure

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v5.1.0-vs-v5.0.2.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test overview | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test environment (AWS EC2） | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test environment (AWS EC2） > Hardware configuration | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test environment (AWS EC2） > Software version | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test environment (AWS EC2） > Parameter configuration | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test environment (AWS EC2） > Parameter configuration > TiDB parameter configuration | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test environment (AWS EC2） > Parameter configuration > TiKV parameter configuration | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test environment (AWS EC2） > Parameter configuration > TiDB global variable configuration | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test plan | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test plan > Prepare test data | TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2 > Test plan > Perform the test`
- Source Line Ranges: `5-125`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `tiup`
- Topic Tags: `sysbench`, `oltp`, `benchmarking`, `aws`, `hardware`, `software-version`, `parameter-configuration`, `global-variables`, `test-plan`, `data-preparation`, `test-execution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0011_7a5f7d7d8e`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v5.1.0-vs-v5.0.2.md#tidb-sysbench-performance-test-report-v5-1-0-vs-v5-0-2`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d39616fb44c7dc8f9029a4a671783306cc09e7937baa853c26d10e771f34db78`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v5.1.0-vs-v5.0.2#tidb-sysbench-performance-test-report-v5-1-0-vs-v5-0-2
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v5.1.0-vs-v5.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the Sysbench benchmark setup, AWS EC2 environment, TiDB and TiKV parameter configuration, global variables, or the exact prepare and run procedure for comparing TiDB v5.1.0 and v5.0.2 in an OLTP scenario.
- Retrieval Keywords: TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2, AWS EC2 hardware configuration, PD m5.xlarge, TiKV i3.4xlarge, TiDB c5.4xlarge, Sysbench c5.9xlarge, Sysbench 1.0.20, log.level, performance.max-procs, prepared-plan-cache.enabled, tikv-client.max-batch-wait-time, storage.scheduler-worker-pool-size, raftstore.store-pool-size, raftstore.apply-pool-size, rocksdb.max-background-jobs, raftdb.max-background-jobs, raftdb.allow-concurrent-memtable-write, server.grpc-concurrency, readpool.unified.min-thread-count, readpool.unified.max-thread-count, readpool.storage.normal-concurrency, pessimistic-txn.pipelined, server.enable-request-batch, set global tidb_hashagg_final_concurrency=1, set global tidb_hashagg_partial_concurrency=1, set global tidb_enable_async_commit = 1, set global tidb_enable_1pc = 1, set global tidb_guarantee_linearizability = 0, set global tidb_enable_clustered_index = 1, analyze table, sysbench oltp_common prepare --tables=16 --table-size=10000000, sysbench point_select read_write update_index update_non_index, HAProxy, TiUP
- Follow-up Guidance: The same document also provides comparative QPS and 95% latency results for Point Select, Update Non-index, Update Index, and Read Write tests.
- Classification Note: This chunk is classified as performance because it defines the benchmark environment, configuration, workload, and execution method used for the Sysbench comparison.

## Official Source Content

# TiDB Sysbench Performance Test Report -- v5.1.0 vs. v5.0.2
## Test overview

This test aims at comparing the Sysbench performance of TiDB v5.1.0 and TiDB v5.0.2 in the Online Transactional Processing (OLTP) scenario. The results show that compared with v5.0.2, the Point Select performance of v5.1.0 is improved by 19.4%, and the performance of the Read Write and Update Index is slightly reduced.
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
| PD        | v5.0.2 and v5.1.0   |
| TiDB      | v5.0.2 and v5.1.0   |
| TiKV      | v5.0.2 and v5.1.0   |
| Sysbench  | 1.0.20     |
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

1. Deploy TiDB v5.1.0 and v5.0.2 using TiUP.
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
