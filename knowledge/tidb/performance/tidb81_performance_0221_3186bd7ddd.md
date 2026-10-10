# TPC-C benchmark setup, execution steps, and results for TiDB Cloud Dedicated v8.1.0

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.1-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB Cloud TPC-C Performance Test Report for TiDB v8.1.0`
- Source Heading Path: `TiDB Cloud TPC-C Performance Test Report for TiDB v8.1.0 | TiDB Cloud TPC-C Performance Test Report for TiDB v8.1.0 > Test overview | TiDB Cloud TPC-C Performance Test Report for TiDB v8.1.0 > Test environment | TiDB Cloud TPC-C Performance Test Report for TiDB v8.1.0 > Test environment > TiDB cluster | TiDB Cloud TPC-C Performance Test Report for TiDB v8.1.0 > Test environment > Parameter configuration | TiDB Cloud TPC-C Performance Test Report for TiDB v8.1.0 > Test environment > Benchmark executor | TiDB Cloud TPC-C Performance Test Report for TiDB v8.1.0 > Test steps | TiDB Cloud TPC-C Performance Test Report for TiDB v8.1.0 > Test results`
- Source Line Ranges: `5-123`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `sql`
- Topic Tags: `tpcc`, `benchmarking`, `oltp`, `test-environment`, `parameter-configuration`, `cluster-sizing`, `data-loading`, `statistics-collection`, `stress-testing`, `tpmc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0221_3186bd7ddd`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.1-performance-benchmarking-with-tpcc.md#tidb-cloud-tpc-c-performance-test-report-for-tidb-v8-1-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6e9f0248d08567d6f900c22139ba59f30a11fcaaa52919843a23ca93ed659689`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.1-performance-benchmarking-with-tpcc#tidb-cloud-tpc-c-performance-test-report-for-tidb-v8-1-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.1-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the official TPC-C benchmarking setup, execution steps, parameter settings, and tpmC results for a TiDB Cloud Dedicated cluster running TiDB v8.1.0.
- Retrieval Keywords: TiDB Cloud TPC-C Performance Test Report for TiDB v8.1.0, TiDB Cloud Dedicated, v8.1.0, TPC-C, OLTP, AWS us-west-2, 16 vCPU, 32 GiB, 16 vCPU, 64 GiB, prefill-for-recycle, raft-engine.prefill-for-recycle = true, CREATE DATABASE tpcc;, go-tpc tpcc, --warehouses 1000 prepare, --warehouses 1000 run, ANALYZE TABLE customer, SET tidb_build_stats_concurrency=16, SET tidb_distsql_scan_concurrency=16, SET tidb_index_serial_scan_concurrency=16, NEW_ORDER, tpmC, 43,660, 75,495, 102,013
- Follow-up Guidance: The source also notes that this report can be used as a reference for the performance of TiDB Self-Managed v8.1.0 clusters.
- Classification Note: This is classified as performance content because the official document defines a benchmark environment, workload commands, statistics collection, stress-test procedure, and measured tpmC throughput results.

## Official Source Content

# TiDB Cloud TPC-C Performance Test Report for TiDB v8.1.0

This document provides the TPC-C performance test steps and results for a TiDB Cloud Dedicated cluster with the TiDB version of v8.1.0. This report can also be used as a reference for the performance of TiDB Self-Managed v8.1.0 clusters.
## Test overview

This test aims at showing the TPC-C performance of TiDB v8.1.0 in the Online Transactional Processing (OLTP) scenario.
## Test environment
### TiDB cluster

The test is conducted on a TiDB cluster with the following settings:

- Cluster type: [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated)
- Cluster version: v8.1.0
- Cloud provider: AWS (us-west-2)
- Cluster configuration:

    | Node type | Node size | Node quantity | Node storage |
    |:----------|:----------|:----------|:----------|
    | TiDB      | 16 vCPU, 32 GiB | 2 | N/A |
    | TiKV      | 16 vCPU, 64 GiB | 3 | 1000 GiB |
### Parameter configuration

> **Note:**
>
> For TiDB Cloud, to modify the TiKV parameters of your cluster, you can contact [PingCAP Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for help.

The TiKV parameter [`prefill-for-recycle`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#prefill-for-recycle-new-in-v700) can make log recycling effective immediately after initialization. This document conducts tests with `prefill-for-recycle` enabled:

```yaml
raft-engine.prefill-for-recycle = true
```
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

The TPC-C performance of v8.1.0 in the [test environment](#test-environment) is as follows:

| Threads |  v8.1.0 tpmC |
|:--------|:----------|
| 50  | 43,660  |
| 100 | 75,495  |
| 200 | 102,013  |

![TPC-C](/media/tidb-cloud/v8.1.0_tpcc.png)
