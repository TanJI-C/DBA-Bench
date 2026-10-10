# TPC-C v4.0 vs v3.0 benchmark environment, plan, and result

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v4.0-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0`
- Source Heading Path: `TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test purpose | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Hardware configuration | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Software version | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > TiDB v3.0 configuration | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > TiKV v3.0 configuration | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > TiDB v4.0 configuration | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > TiKV v4.0 configuration | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test environment (AWS EC2) > Parameter configuration > Global variable configuration | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test plan | TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0 > Test result`
- Source Line Ranges: `5-130`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `tiup`, `ecosystem`
- Topic Tags: `tpcc`, `benchmarksql`, `oltp`, `aws-ec2`, `hardware-configuration`, `software-version`, `parameter-configuration`, `global-variables`, `test-plan`, `performance-comparison`, `tpmc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0041_b0d0e3fdd0`
- Source ID: `tidb-docs-8.1:benchmark/v4.0-performance-benchmarking-with-tpcc.md#tidb-tpc-c-performance-test-report-v4-0-vs-v3-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `54edb6e53f3d4113e3a7276b5e58be912f3b1e008e5a8a915363320b35c12658`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v4.0-performance-benchmarking-with-tpcc#tidb-tpc-c-performance-test-report-v4-0-vs-v3-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v4.0-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the official TPC-C benchmark setup and result comparing TiDB 4.0 with TiDB 3.0, including AWS EC2 environment, BenchmarkSQL workflow, parameter configuration, and tpmC outcome.
- Retrieval Keywords: TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0, TPC-C v4.0 vs v3.0, OLTP scenario, AWS EC2, BenchmarkSQL, TiUP, TPC-C 5000 Warehouse, runSQL.sh ./props.mysql sql.mysql/tableCreates.sql, runSQL.sh ./props.mysql sql.mysql/indexCreates.sql, analyze table, runBenchmark.sh ./props.mysql, tpmC, New Order, 50% increased, prepared-plan-cache.enabled, tikv-client.max-batch-wait-time, storage.scheduler-worker-pool-size, server.grpc-concurrency, readpool.unified.min-thread-count, pessimistic-txn.pipelined, tidb_hashagg_final_concurrency, tidb_hashagg_partial_concurrency, tidb_disable_txn_auto_retry
- Follow-up Guidance: The source also provides the exact TiDB v3.0 and v4.0, TiKV v3.0 and v4.0, and global variable configuration values used in the benchmark plan.
- Classification Note: This chunk is classified as performance because it documents a TPC-C benchmarking environment, test plan, configuration, and a measured tpmC comparison result for TiDB 4.0 versus TiDB 3.0.

## Official Source Content

# TiDB TPC-C Performance Test Report -- v4.0 vs. v3.0
## Test purpose

This test aims to compare the TPC-C performance of TiDB 4.0 and TiDB 3.0 in the Online Transactional Processing (OLTP) scenario.
## Test environment (AWS EC2)
### Hardware configuration

| Service type   | EC2 type   |    Instance count  |
|:----------|:----------|:----------|
| PD        | m5.xlarge |     3     |
| TiKV      | i3.4xlarge|     3     |
| TiDB      | c5.4xlarge|     3     |
| TPC-C     | m5.4xlarge|     1     |
### Software version

| Service type   | Software version    |
|:----------|:-----------|
| PD        | 3.0 and 4.0   |
| TiDB      | 3.0 and 4.0   |
| TiKV      | 3.0 and 4.0   |
| BenchmarkSQL  | None     |
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

2. Use BenchmarkSQL to import the TPC-C 5000 Warehouse data.

    1. Compile BenchmarkSQL:

        ```bash
        git clone https://github.com/pingcap/benchmarksql && cd benchmarksql && ant
        ```

    2. Enter the `run` directory, edit the `props.mysql` file according to the actual situation, and modify the `conn`, `warehouses`, `loadWorkers`, `terminals`, and `runMins` configuration items.

    3. Execute the `runSQL.sh ./props.mysql sql.mysql/tableCreates.sql` command.

    4. Execute the `runSQL.sh ./props.mysql sql.mysql/indexCreates.sql` command.

    5. Run MySQL client and execute the `analyze table` statement on every table.

3. Execute the `runBenchmark.sh ./props.mysql` command.

4. Extract the tpmC data of New Order from the result.
## Test result

According to the test statistics, the TPC-C performance of TiDB v4.0 has **increased by 50%** compared with that of TiDB v3.0.

![TPC-C](/media/tpcc-v4vsv3.png)
