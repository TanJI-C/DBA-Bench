# Sysbench test plan and execution commands

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test plan | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test plan > Prepare test data | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test plan > Perform the test`
- Source Line Ranges: `104-150`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiup`
- Topic Tags: `sysbench`, `test-plan`, `data-preparation`, `benchmark-execution`, `oltp`, `restore`, `analyze-table`, `haproxy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0028_28e7ef006a`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0.md#test-plan`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9eee0646b4ce4b71b778461ad92e1d2d48626119d8363aee5b9a605e9b72cf95`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0#test-plan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for the Sysbench test plan, data preparation command, or run command for the OLTP comparison between TiDB v6.2.0 and v6.1.0.
- Retrieval Keywords: Test plan, Prepare test data, Perform the test, sysbench oltp_common, prepare --tables=16 --table-size=10000000, sysbench $testname, --threads=$threads, --time=1200, --report-interval=1, --rand-type=uniform, --db-driver=mysql, --mysql-db=sbtest, --mysql-host=$aws_nlb_host, --mysql-port=$aws_nlb_port, point_select, read_write, update_index, update_non_index, analyze table, HAProxy, restore backup data
- Follow-up Guidance: The source states that after each type of test, the cluster is stopped, overwritten with the backup data from step 4, and restarted.
- Classification Note: This chunk is classified as performance because it documents the benchmark procedure and exact Sysbench commands used to prepare data and execute the workload tests.

## Official Source Content

## Test plan

1. Deploy TiDB v6.2.0 and v6.1.0 using TiUP.
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
