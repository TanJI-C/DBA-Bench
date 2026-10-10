# Sysbench benchmark procedure and commands

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test plan | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test plan > Prepare test data | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test plan > Perform the test`
- Source Line Ranges: `104-150`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiup`, `shared`
- Topic Tags: `test-plan`, `data-preparation`, `benchmark-execution`, `sysbench-commands`, `analyze-table`, `backup-restore`, `concurrency-testing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0022_cd44aa191a`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0.md#test-plan`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2126660e45fe7748c3864a423e59bf1262730993919ddd914c239324a7f9e67e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0#test-plan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching for the Sysbench test plan, data preparation command, runtime command, or the benchmark procedure including analyze table, backup and restore, concurrency testing, and HAProxy-based stress testing.
- Retrieval Keywords: Test plan, Prepare test data, Perform the test, Deploy TiDB v6.0.0 and v5.4.0 using TiUP, analyze table, Back up the data used for restore before different concurrency tests, point_select, read_write, update_index, update_non_index, 20 minutes, sysbench oltp_common, prepare --tables=16 --table-size=10000000, sysbench $testname, --time=1200, --report-interval=1, --mysql-db=sbtest, --mysql-host=$aws_nlb_host, --mysql-port=$aws_nlb_port, run --tables=16 --table-size=10000000
- Follow-up Guidance: The procedure states that after each type of test is completed, the cluster is stopped, overwritten with the backup data from step 4, and then restarted.
- Classification Note: This is classified as performance content because it documents the benchmark execution procedure and exact Sysbench commands used to run the comparison.

## Official Source Content

## Test plan

1. Deploy TiDB v6.0.0 and v5.4.0 using TiUP.
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
