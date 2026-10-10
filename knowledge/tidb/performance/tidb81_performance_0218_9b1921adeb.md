# Sysbench benchmark overview and test environment

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.1-performance-benchmarking-with-sysbench.md`
- Source Title: `TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0`
- Source Heading Path: `TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 | TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test overview | TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test environment | TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test environment > TiDB cluster | TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test environment > Parameter configuration | TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0 > Test environment > Benchmark executor`
- Source Line Ranges: `5-63`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `sql`
- Topic Tags: `sysbench`, `benchmarking`, `oltp`, `test-environment`, `cluster-configuration`, `parameter-configuration`, `plan-cache`, `raft-engine`, `benchmark-executor`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0218_9b1921adeb`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.1-performance-benchmarking-with-sysbench.md#tidb-cloud-sysbench-performance-test-report-for-tidb-v8-1-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1fa261c20871b3c8e4acfc4e14fd9f680a2675430c9219cd3f1af9ac3e46aaf3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.1-performance-benchmarking-with-sysbench#tidb-cloud-sysbench-performance-test-report-for-tidb-v8-1-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.1-performance-benchmarking-with-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud Dedicated Sysbench benchmark overview, exact test environment, or benchmark parameter settings for TiDB v8.1.0.
- Retrieval Keywords: TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0, Sysbench benchmark overview, Online Transactional Processing OLTP, TiDB Cloud Dedicated, AWS us-west-2, TiDB 16 vCPU 32 GiB, TiKV 16 vCPU 64 GiB, 1000 GiB, tidb_session_plan_cache_size, SET GLOBAL tidb_session_plan_cache_size = 1000, prefill-for-recycle, raft-engine.prefill-for-recycle = false, raft-engine.prefill-for-recycle = true, benchmark executor, Amazon EC2 c6a.2xlarge, sysbench 1.0.20, LuaJIT 2.1.0-beta2
- Follow-up Guidance: The source also states that for TiDB Cloud, modifying TiKV parameters can be done by contacting PingCAP Support.
- Classification Note: This is classified as performance content because it defines the OLTP benchmark scope, cluster and executor hardware, and test parameter configuration used for the measured results.

## Official Source Content

# TiDB Cloud Sysbench Performance Test Report for TiDB v8.1.0

This document provides the Sysbench performance test steps and results for a TiDB Cloud Dedicated cluster with the TiDB version of v8.1.0. This report can also be used as a reference for the performance of TiDB Self-Managed v8.1.0 clusters.
## Test overview

This test aims at showing the Sysbench performance of TiDB v8.1.0 in the Online Transactional Processing (OLTP) scenario.
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

The system variable [`tidb_session_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_plan_cache_size-new-in-v710) controls the maximum number of plans that can be cached. The default value is `100`. For each workload, this document conducts tests with `tidb_session_plan_cache_size` set to `1000`:

```sql
SET GLOBAL tidb_session_plan_cache_size = 1000;
```

> **Note:**
>
> For TiDB Cloud, to modify the TiKV parameters of your cluster, you can contact [PingCAP Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for help.

The TiKV parameter [`prefill-for-recycle`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#prefill-for-recycle-new-in-v700) can make log recycling effective immediately after initialization. This document conducts tests based on different workloads with the following `prefill-for-recycle` configuration:

- For the `oltp_point_select` workload, use the default value of the [`prefill-for-recycle`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#prefill-for-recycle-new-in-v700) parameter:

    ```yaml
    raft-engine.prefill-for-recycle = false
    ```

- For `oltp_insert`, `oltp_read_write`, `oltp_update_index`, and `oltp_update_non_index` workloads, enable the [`prefill-for-recycle`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#prefill-for-recycle-new-in-v700) parameter:

    ```yaml
    raft-engine.prefill-for-recycle = true
    ```
### Benchmark executor

The benchmark executor sends SQL queries to the TiDB cluster. In this test, its hardware configuration is as follows:

- Machine type: Amazon EC2 (us-west-2)
- Instance type: c6a.2xlarge
- Sysbench version: sysbench 1.0.20 (using bundled LuaJIT 2.1.0-beta2)
