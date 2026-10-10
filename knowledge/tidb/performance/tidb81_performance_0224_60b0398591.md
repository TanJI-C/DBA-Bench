# TPC-C benchmark overview and test environment

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.5-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0`
- Source Heading Path: `TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0 | TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0 > Test overview | TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0 > Test environment | TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0 > Test environment > TiDB cluster | TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0 > Test environment > Parameter configuration | TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0 > Test environment > Benchmark executor`
- Source Line Ranges: `5-48`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `sql`
- Topic Tags: `tpcc`, `benchmarking`, `oltp`, `test-environment`, `cluster-configuration`, `tikv-parameters`, `benchmark-executor`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0224_60b0398591`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.5-performance-benchmarking-with-tpcc.md#tidb-cloud-tpc-c-performance-test-report-for-tidb-v8-5-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ee850ae3182e0e25342981822730db119f9560d4458ec2b2abb817f9d8373bb3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-benchmarking-with-tpcc#tidb-cloud-tpc-c-performance-test-report-for-tidb-v8-5-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.5-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud Dedicated TPC-C benchmark overview, test environment, cluster sizing, or the TiKV parameter used in the published v8.5.0 test.
- Retrieval Keywords: TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0, TPC-C benchmark overview, OLTP scenario, TiDB Cloud Dedicated, AWS us-west-2, TiDB 16 vCPU 32 GiB x2, TiKV 16 vCPU 64 GiB x3, 1000 GiB storage, raft-engine.prefill-for-recycle = true, prefill-for-recycle, benchmark executor, Amazon EC2 c6a.2xlarge
- Follow-up Guidance: The source notes that for TiDB Cloud, modifying TiKV parameters can be done by contacting PingCAP Support.
- Classification Note: This is classified as performance content because it defines the benchmark purpose, environment, and parameter configuration used to measure TPC-C performance.

## Official Source Content

# TiDB Cloud TPC-C Performance Test Report for TiDB v8.5.0

This document provides the TPC-C performance test steps and results for a TiDB Cloud Dedicated cluster with the TiDB version of v8.5.0. This report can also be used as a reference for the performance of TiDB Self-Managed v8.5.0 clusters.
## Test overview

This test aims at showing the TPC-C performance of TiDB v8.5.0 in the Online Transactional Processing (OLTP) scenario.
## Test environment
### TiDB cluster

The test is conducted on a TiDB cluster with the following settings:

- Cluster type: [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated)
- Cluster version: v8.5.0
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
