# TPC-C benchmark execution steps

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.5-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0`
- Source Heading Path: `TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0 > Test steps`
- Source Line Ranges: `49-112`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `sql`, `tikv`, `ecosystem`
- Topic Tags: `tpcc`, `benchmarking`, `cluster-creation`, `database-setup`, `data-loading`, `go-tpc`, `statistics-collection`, `stress-testing`, `tpmc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0225_521ffd252e`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.5-performance-benchmarking-with-tpcc.md#test-steps`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bda214b58d3bf59a3aee085718c75b829bd3d346806b3f48b3962d9bfddb4da4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-benchmarking-with-tpcc#test-steps
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.5-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the documented steps to run the TiDB Cloud Dedicated TPC-C benchmark, including cluster creation, tpcc database setup, go-tpc data loading, statistics collection, stress testing, and tpmC extraction.
- Retrieval Keywords: Test steps, TiDB Cloud console, Create a TiDB Cloud Dedicated cluster, Connect to TiDB Cloud Dedicated via Private Endpoint, CREATE DATABASE tpcc;, go-tpc, go-tpc tpcc --host ${HOST} --warehouses 1000 prepare -P 4000 -D tpcc -T ${THREAD} --time 2h0m0s -p ${PASSWORD} --ignore-error, ANALYZE TABLE customer, ANALYZE TABLE district, ANALYZE TABLE history, ANALYZE TABLE item, ANALYZE TABLE new_order, ANALYZE TABLE order_line, ANALYZE TABLE orders, ANALYZE TABLE stock, ANALYZE TABLE warehouse, SET tidb_build_stats_concurrency=16;, SET tidb_distsql_scan_concurrency=16;, SET tidb_index_serial_scan_concurrency=16;, go-tpc tpcc --host ${HOST} -P 4000 --warehouses 1000 run -D tpcc -T ${THREAD} --time 2h0m0s -p ${PASSWORD} --ignore-error, NEW_ORDER, tpmC, Max Qualified Throughput
- Follow-up Guidance: The source states that the final metric to extract from the result is the tpmC data of NEW_ORDER, where tpmC measures the number of new orders processed per minute.
- Classification Note: This is classified as performance content because it provides the benchmark execution procedure and workload commands used to measure throughput.

## Official Source Content

## Test steps

This section introduces how to perform the TPC-C performance test step by step.

1. In the [TiDB Cloud console](https://tidbcloud.com/), create a TiDB Cloud Dedicated cluster that meets the [test environment](#tidb-cluster) requirements.

    For more information, see [Create a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster).

2. On the benchmark executor, connect to the newly created cluster and create a database named `tpcc`.

    To connect to the cluster, see [Connect to TiDB Cloud Dedicated via Private Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections).

    To create the `tpcc` database, execute the following SQL statement:

    ```sql
    CREATE DATABASE tpcc;
    ```

3. Load TPC-C data to the `tpcc` database.

    1. The test in this document is implemented based on [go-tpc](https://github.com/pingcap/go-tpc). You can download the test program using the following command:

       ```shell
       curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/pingcap/go-tpc/master/install.sh | sh
       ```

    2. Run the following `go-tpc tpcc` command to import 1,000 warehouses to the `tpcc` database. Replace `${HOST}`, `${THREAD}`, and `${PASSWORD}` with your actual values. This document conducts three tests with the `${THREAD}` value of `50`, `100`, and `200`.

       ```shell
       go-tpc tpcc --host ${HOST} --warehouses 1000 prepare -P 4000 -D tpcc -T ${THREAD} --time 2h0m0s -p ${PASSWORD} --ignore-error
       ```

4. To ensure that the TiDB optimizer can generate the optimal execution plan, execute the following SQL statements to collect statistics before conducting the TPC-C test:

    ```sql
    ANALYZE TABLE customer;
    ANALYZE TABLE district;
    ANALYZE TABLE history;
    ANALYZE TABLE item;
    ANALYZE TABLE new_order;
    ANALYZE TABLE order_line;
    ANALYZE TABLE orders;
    ANALYZE TABLE stock;
    ANALYZE TABLE warehouse;
    ```

    To accelerate the collection of statistics, execute the following SQL statements before collecting:

    ```sql
    SET tidb_build_stats_concurrency=16;
    SET tidb_distsql_scan_concurrency=16;
    SET tidb_index_serial_scan_concurrency=16;
    ```

5. Run the following `go-tpc tpcc` command to conduct stress tests on the TiDB Cloud Dedicated cluster. For each concurrency, the test takes two hours.

    ```shell
    go-tpc tpcc --host ${HOST} -P 4000 --warehouses 1000 run -D tpcc -T ${THREAD} --time 2h0m0s -p ${PASSWORD} --ignore-error
    ```

6. Extract the tpmC data of `NEW_ORDER` from the result.

    TPC-C uses tpmC (transactions per minute) to measure the maximum qualified throughput (MQTh, Max Qualified Throughput). The transactions are the NewOrder transactions and the final unit of measure is the number of new orders processed per minute.
