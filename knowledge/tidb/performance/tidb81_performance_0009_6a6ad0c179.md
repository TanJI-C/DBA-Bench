# Sysbench benchmark test plan and execution commands

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v5-vs-v4.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test plan | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test plan > Prepare test data | TiDB Sysbench Performance Test Report -- v5.0 vs. v4.0 > Test plan > Perform the test`
- Source Line Ranges: `116-162`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiup`, `tidb`, `sql`
- Topic Tags: `test-plan`, `data-prepare`, `sysbench-command`, `analyze-table`, `backup-restore`, `concurrency-testing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0009_6a6ad0c179`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v5-vs-v4.md#test-plan`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `af75979b7043c86e5f2afb05d13a01ddac3a0ba58930fd71214f0a3053c5b006`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v5-vs-v4#test-plan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v5-vs-v4.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Sysbench test plan, data preparation, or exact command lines for preparing and running the benchmark.
- Retrieval Keywords: Test plan, Prepare test data, Perform the test, sysbench oltp_common, prepare --tables=16 --table-size=10000000, run --tables=16 --table-size=10000000, analyze table, AWS NLB, point_select, read_write, update_index, update_non_index, warm-up takes 1 minute, test takes 5 minutes, backup data used for restore
- Follow-up Guidance: The test plan also describes backing up restore data, restarting the cluster, and overwriting it between concurrency tests.
- Classification Note: This chunk is classified as a performance test plan describing deployment, data preparation, and Sysbench execution steps.

## Official Source Content

## Test plan

1. Deploy TiDB v5.0 and v4.0 using TiUP.
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
