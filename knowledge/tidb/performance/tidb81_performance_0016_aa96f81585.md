# Sysbench test plan and execution commands

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v5.3.0-vs-v5.2.2.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v5.3.0 vs. v5.2.2`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v5.3.0 vs. v5.2.2 > Test plan | TiDB Sysbench Performance Test Report -- v5.3.0 vs. v5.2.2 > Test plan > Prepare test data | TiDB Sysbench Performance Test Report -- v5.3.0 vs. v5.2.2 > Test plan > Perform the test`
- Source Line Ranges: `108-154`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiup`, `shared`
- Topic Tags: `sysbench`, `test-plan`, `data-preparation`, `workload-execution`, `concurrency`, `backup-restore`, `oltp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0016_aa96f81585`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v5.3.0-vs-v5.2.2.md#test-plan`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f97b87a50387c3adeb15ea09c717d1cffd21ced507ed339d22d61acc30a6daf0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v5.3.0-vs-v5.2.2#test-plan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v5.3.0-vs-v5.2.2.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented Sysbench test plan, data preparation command, or workload execution command for the TiDB v5.3.0 versus v5.2.2 benchmark.
- Retrieval Keywords: Sysbench test plan TiDB v5.3.0 v5.2.2, deploy using TiUP, import 16 tables each table with 10 million rows, analyze table, back up the data used for restore before different concurrency tests, point_select, read_write, update_index, update_non_index, 20 minutes, sysbench oltp_common, prepare --tables=16 --table-size=10000000, --threads=16, --rand-type=uniform, --db-driver=mysql, --mysql-db=sbtest, --mysql-host=$aws_nlb_host, --mysql-port=$aws_nlb_port, sysbench $testname, --time=1200, --report-interval=1, run --tables=16 --table-size=10000000, perform stress tests on TiDB via HAProxy
- Follow-up Guidance: The source says that after each type of test is completed, the cluster is stopped, overwritten with the backup data from step 4, and restarted.
- Classification Note: This is classified as performance content because it describes the benchmark procedure and exact Sysbench commands used to prepare data and run OLTP workloads.

## Official Source Content

## Test plan

1. Deploy TiDB v5.3.0 and v5.2.2 using TiUP.
2. Use Sysbench to import 16 tables, each table with 10 million rows of data.
3. Execute the `analyze table` statement on each table.
4. Back up the data used for restore before different concurrency tests, which ensures data consistency for each test.
5. Start the Sysbench client to perform the `point_select`, `read_write`, `update_index`, and `update_non_index` tests. Perform stress tests on TiDB via HAProxy. For each concurrency under each workload, the test takes 20 minutes.
6. After each type of test is completed, stop the cluster, overwrite the cluster with the backup data in step 4, and restart the cluster.
### Prepare test data

Run the following command to prepare the test data:

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

Run the following command to perform the test:

```bash
sysbench $testname \
    --threads=$threads \
    --time=1200 \
    --report-interval=1 \
    --rand-type=uniform \
    --db-driver=mysql \
    --mysql-db=sbtest \
    --mysql-host=$aws_nlb_host \
    --mysql-port=$aws_nlb_port \
    run --tables=16 --table-size=10000000
```
