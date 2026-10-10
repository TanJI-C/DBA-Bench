# Sysbench benchmark overview environment and test steps

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v7.5-performance-benchmarking-with-sysbench.md`
- Source Title: `TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0`
- Source Heading Path: `TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 | TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test overview | TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test environment | TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test environment > TiDB cluster | TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test environment > Parameter configuration | TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test environment > Benchmark executor | TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0 > Test steps`
- Source Line Ranges: `6-113`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `sql`
- Topic Tags: `sysbench`, `benchmarking`, `oltp`, `test-environment`, `cluster-configuration`, `parameter-configuration`, `prefill-for-recycle`, `benchmark-executor`, `workload-setup`, `data-loading`, `private-endpoint`, `sql-connection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0215_4789bfcea0`
- Source ID: `tidb-docs-8.1:tidb-cloud/v7.5-performance-benchmarking-with-sysbench.md#tidb-cloud-sysbench-performance-test-report-for-tidb-v7-5-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5f297472e2febe0cc4c18de023d568522bc5be6c8e763a1612f8dcc4497802c0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v7.5-performance-benchmarking-with-sysbench#tidb-cloud-sysbench-performance-test-report-for-tidb-v7-5-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v7.5-performance-benchmarking-with-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official TiDB Cloud v7.5.0 Sysbench benchmark setup, environment details, parameter settings, and step-by-step workload execution commands.
- Retrieval Keywords: TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0, TiDB Cloud Dedicated, v7.5.0, AWS us-west-2, TiDB 16 vCPU 32 GiB, TiKV 16 vCPU 64 GiB 1000 GiB, raft-engine.prefill-for-recycle, prefill-for-recycle, oltp_point_select, oltp_insert, oltp_read_write, oltp_update_index, oltp_update_non_index, Amazon EC2 c6a.2xlarge, sysbench 1.0.20, CREATE DATABASE sbtest;, sysbench oltp_common prepare --tables=32 --table-size=10000000, sysbench ${WORKLOAD} run, --mysql-ignore-errors=1062,2013,8028,9007, --auto-inc=false, Private Endpoint, sbtest database
- Follow-up Guidance: The document also provides test results with TPS and 95% latency for the five workloads in the same test environment.
- Classification Note: This chunk is classified as performance because it defines the benchmark environment, workload configuration, and execution steps for measuring Sysbench OLTP performance.

## Official Source Content

# TiDB Cloud Sysbench Performance Test Report for TiDB v7.5.0

This document provides the Sysbench performance test steps and results for a TiDB Cloud Dedicated cluster with the TiDB version of v7.5.0. This report can also be used as a reference for the performance of TiDB Self-Managed v7.5.0 clusters.
## Test overview

This test aims at showing the Sysbench performance of TiDB v7.5.0 in the Online Transactional Processing (OLTP) scenario.
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
### Parameter configuration

> **Note:**
>
> For TiDB Cloud, to modify the TiKV parameters of your cluster, you can contact [PingCAP Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for help.

The TiKV parameter [`prefill-for-recycle`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#prefill-for-recycle-new-in-v700) can make log recycling effective immediately after initialization. This document conducts tests based on different workloads with the following `prefill-for-recycle` configuration:

- For the `oltp_point_select` workload, use the default value of the [`prefill-for-recycle`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#prefill-for-recycle-new-in-v700) parameter:

    ```yaml
    raft-engine.prefill-for-recycle = false
    ```

- For `oltp_insert`, `oltp_read_write` , `oltp_update_index`, and `oltp_update_non_index` workloads, enable the [`prefill-for-recycle`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#prefill-for-recycle-new-in-v700) parameter:

    ```yaml
    raft-engine.prefill-for-recycle = true
    ```
### Benchmark executor

The benchmark executor sends SQL queries to the TiDB cluster. In this test, its hardware configuration is as follows:

- Machine type: Amazon EC2 (us-west-2)
- Instance type: c6a.2xlarge
- Sysbench version: sysbench 1.0.20 (using bundled LuaJIT 2.1.0-beta2)
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

4. Run the following `sysbench run` command to conduct Sysbench performance tests on different workloads. This document conducts tests on five workloads: `oltp_point_select`, `oltp_read_write`, `oltp_update_non_index`, `oltp_update_index`, and `oltp_insert`. For each workload, this document conducts three tests with the `${THREAD}` value of `100`, `200`, and `400`. For each concurrency, the test takes 20 minutes.

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
