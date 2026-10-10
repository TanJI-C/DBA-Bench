# Sysbench benchmark execution steps

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.1-performance-benchmarking-with-sysbench.md`
- Source Title: `TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0`
- Source Heading Path: `TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test steps`
- Source Line Ranges: `64-118`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `sql`, `ecosystem`
- Topic Tags: `sysbench`, `benchmarking`, `test-steps`, `cluster-creation`, `database-creation`, `data-loading`, `prepare-command`, `run-command`, `workloads`, `concurrency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0219_7f58a1f40e`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.1-performance-benchmarking-with-sysbench.md#test-steps`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `15de8cf95225415138b954dfe7bdb8328c8b9111908f61090a208588668fdbfa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.1-performance-benchmarking-with-sysbench#test-steps
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.1-performance-benchmarking-with-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the official step-by-step procedure and exact commands to run the Sysbench benchmark against a TiDB Cloud Dedicated cluster.
- Retrieval Keywords: Test steps, TiDB Cloud console, Create a TiDB Cloud Dedicated cluster, CREATE DATABASE sbtest, sbtest database, sysbench prepare, sysbench oltp_common, prepare --tables=32 --table-size=10000000, sysbench run, oltp_point_select, oltp_read_write, oltp_update_non_index, oltp_update_index, oltp_insert, --time=1200, --report-interval=10, --mysql-ignore-errors=1062,2013,8028,9007, --auto-inc=false, Connect to TiDB Cloud Dedicated via Private Endpoint
- Follow-up Guidance: The source specifies concurrency values of 50, 100, and 200 for oltp_point_select and oltp_read_write, and 100, 200, and 400 for the other workloads, with each test running for 20 minutes.
- Classification Note: This is classified as performance content because it documents the benchmark execution workflow, including cluster creation, data loading, workloads, and run command parameters.

## Official Source Content

## Test steps

This section introduces how to perform the Sysbench performance test step by step.

1. In the [TiDB Cloud console](https://tidbcloud.com/), create a TiDB Cloud Dedicated cluster that meets the [test environment](#tidb-cluster) requirements.

    For more information, see [Create a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster).

2. On the benchmark executor, connect to the newly created cluster and create a database named `sbtest`.

    To connect to the cluster, see [Connect to TiDB Cloud Dedicated via Private Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections).

    To create the `sbtest` database, execute the following SQL statement:

    ```sql
    CREATE DATABASE sbtest;
    ```

3. Load Sysbench data to the `sbtest` database.

    1. The test in this document is implemented based on [sysbench](https://github.com/akopytov/sysbench). To install sysbench, see [Building and installing from source](https://github.com/akopytov/sysbench#building-and-installing-from-source).

    2. Run the following `sysbench prepare` command to import 32 tables and 10,000,000 rows to the `sbtest` database. Replace `${HOST}`, `${PORT}`, `${THREAD}`, and `${PASSWORD}` with your actual values.

      ```shell
      sysbench oltp_common \
         --threads=${THREAD} \
         --db-driver=mysql \
         --mysql-db=sbtest \
         --mysql-host=${HOST} \
         --mysql-port=${PORT} \
         --mysql-user=root \
         --mysql-password=${PASSWORD} \
         prepare --tables=32 --table-size=10000000
      ```

4. Run the following `sysbench run` command to conduct Sysbench performance tests on different workloads. This document conducts tests on five workloads: `oltp_point_select`, `oltp_read_write`, `oltp_update_non_index`, `oltp_update_index`, and `oltp_insert`. For each workload, this document conducts three tests with different values for the `${THREAD}` variable. For `oltp_point_select` and `oltp_read_write`, the values are `50`, `100`, and `200`. For other workloads, the values are `100`, `200`, and `400`. For each concurrency, the test takes 20 minutes.

    ```shell
    sysbench ${WORKLOAD} run \
      --mysql-host=${HOST} \
      --mysql-port=${PORT} \
      --mysql-user=root \
      --db-driver=mysql \
      --mysql-db=sbtest \
      --threads=${THREAD} \
      --time=1200 \
      --report-interval=10 \
      --tables=32 \
      --table-size=10000000 \
      --mysql-ignore-errors=1062,2013,8028,9007 \
      --auto-inc=false \
      --mysql-password=${PASSWORD}
    ```
