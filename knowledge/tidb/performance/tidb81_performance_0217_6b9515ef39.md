# TPC-C benchmark environment, procedure, and results for TiDB Cloud v7.5.0

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v7.5-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB Cloud TPC-C Performance Test Report for TiDB v7.5.0`
- Source Heading Path: `TiDB Cloud TPC-C Performance Test Report for TiDB v7.5.0 | TiDB Cloud TPC-C Performance Test Report for TiDB v7.5.0 > Test overview | TiDB Cloud TPC-C Performance Test Report for TiDB v7.5.0 > Test environment | TiDB Cloud TPC-C Performance Test Report for TiDB v7.5.0 > Test environment > TiDB cluster | TiDB Cloud TPC-C Performance Test Report for TiDB v7.5.0 > Test environment > Benchmark executor | TiDB Cloud TPC-C Performance Test Report for TiDB v7.5.0 > Test steps | TiDB Cloud TPC-C Performance Test Report for TiDB v7.5.0 > Test results`
- Source Line Ranges: `6-112`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `tpcc`, `benchmarking`, `oltp`, `test-environment`, `cluster-configuration`, `benchmark-executor`, `data-loading`, `statistics-collection`, `stress-test`, `tpmc`, `results`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0217_6b9515ef39`
- Source ID: `tidb-docs-8.1:tidb-cloud/v7.5-performance-benchmarking-with-tpcc.md#tidb-cloud-tpc-c-performance-test-report-for-tidb-v7-5-0`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `509e94b0b09dc92c7bd6818f1208565fc051de5d89720786993bf03dc1162014`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v7.5-performance-benchmarking-with-tpcc#tidb-cloud-tpc-c-performance-test-report-for-tidb-v7-5-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v7.5-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the official TiDB Cloud v7.5.0 TPC-C benchmark setup, test procedure, and tpmC results for an OLTP performance reference.
- Retrieval Keywords: TiDB Cloud TPC-C Performance Test Report for TiDB v7.5.0, TiDB Cloud Dedicated, v7.5.0, TPC-C, OLTP, AWS us-west-2, go-tpc, CREATE DATABASE tpcc, go-tpc tpcc --host ${HOST} --warehouses 1000 prepare, go-tpc tpcc --host ${HOST} -P 4000 --warehouses 1000 run, ANALYZE TABLE customer, tidb_build_stats_concurrency, tidb_distsql_scan_concurrency, tidb_index_serial_scan_concurrency, tpmC, NEW_ORDER, 41,426, 71,499, 97,389
- Follow-up Guidance: The source also includes the TiDB cluster and benchmark executor environment details, the statistics collection SQL, and the thread counts 50, 100, and 200 used for the two-hour stress tests.
- Classification Note: This is classified as performance content because the official content is a TPC-C performance test report that documents the benchmark environment, execution steps, and throughput results for TiDB Cloud Dedicated v7.5.0.

## Official Source Content

# TiDB Cloud TPC-C Performance Test Report for TiDB v7.5.0

This document provides the TPC-C performance test steps and results for a TiDB Cloud Dedicated cluster with the TiDB version of v7.5.0. This report can also be used as a reference for the performance of TiDB Self-Managed v7.5.0 clusters.
## Test overview

This test aims at showing the TPC-C performance of TiDB v7.5.0 in the Online Transactional Processing (OLTP) scenario.
## Test environment
### TiDB cluster

The test is conducted on a TiDB cluster with the following settings:

- Cluster type: [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated)
- Cluster version: v7.5.0
- Cloud provider: AWS (us-west-2)
- Cluster configuration:

   | Node type | Node size       | Node quantity | Node storage |
   | :-------- | :-------------- | :------------ | :----------- |
   | TiDB      | 16 vCPU, 32 GiB | 2             | N/A          |
   | TiKV      | 16 vCPU, 64 GiB | 3             | 1000 GiB     |
### Benchmark executor

The benchmark executor sends SQL queries to the TiDB cluster. In this test, its hardware configuration is as follows:

- Machine type: Amazon EC2 (us-west-2)
- Instance type: c6a.2xlarge
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
## Test results

The TPC-C performance of v7.5.0 in the [test environment](#test-environment) is as follows:

| Threads | v7.5.0 tpmC |
| :------ | :---------- |
| 50      | 41,426      |
| 100     | 71,499      |
| 200     | 97,389      |

![TPC-C](/media/tidb-cloud/v7.5.0_tpcc.png)
