# TiDB Cloud cluster sizing for TiDB compute nodes

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/size-your-cluster.md`
- Source Title: `Determine Your TiDB Size`
- Source Heading Path: `Determine Your TiDB Size | Determine Your TiDB Size > Size TiDB | Determine Your TiDB Size > Size TiDB > TiDB vCPU and RAM | Determine Your TiDB Size > Size TiDB > TiDB node count`
- Source Line Ranges: `5-79`
- Source Scope: `cloud`
- Primary Component: `tidb`
- Related Components: `cloud`, `tikv`, `tiflash`
- Topic Tags: `cluster-sizing`, `compute-scaling`, `vcpu`, `memory`, `node-count`, `qps`, `latency`, `availability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0198_5e7cf1341c`
- Source ID: `tidb-docs-8.1:tidb-cloud/size-your-cluster.md#determine-your-tidb-size`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `288c333eac0563849ad8bac3add9b358793198268f635a30640078a465300f6a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#determine-your-tidb-size
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/size-your-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when estimating TiDB Cloud Dedicated TiDB compute node sizing by vCPU, RAM, node count, workload QPS, latency target, or high availability constraints.
- Retrieval Keywords: TiDB Cloud Dedicated, Size TiDB, TiDB vCPU and RAM, TiDB node count, 4 vCPU, 16 GiB, 8 vCPU, 16 GiB, 8 vCPU, 32 GiB, 16 vCPU, 32 GiB, 16 vCPU, 64 GiB, 32 vCPU, 64 GiB, 32 vCPU, 128 GiB, TiDB Cloud Support, TiFlash is unavailable, 4 vCPU TiDB can only be used with 4 vCPU TiKV, node count = ceil(overall expected performance ÷ performance per node * (1 - performance deviation coefficient)), QPS (P95 ≈ 100ms), QPS (P99 ≈ 300ms), QPS (P99 ≈ 100ms), mixed workload, read workload, write workload, performance deviation coefficient, at least two TiDB nodes
- Follow-up Guidance: The source points to TiDB Cloud Performance Reference for performance test results of different cluster scales.
- Classification Note: This is classified as performance for the TiDB component because the content explains TiDB compute sizing, scaling behavior, supported vCPU and RAM sizes, node-count guidance, and workload-based QPS estimates in TiDB Cloud.

## Official Source Content

# Determine Your TiDB Size

This document describes how to determine the size of a TiDB Cloud Dedicated cluster.

> **Note:**
>
> You cannot change the size of a [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) cluster.
## Size TiDB

TiDB is for computing only and does not store data. It is horizontally scalable.

You can configure node count, vCPU, and RAM for TiDB.

To learn performance test results of different cluster scales, see [TiDB Cloud Performance Reference](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-performance-reference).
### TiDB vCPU and RAM

The supported vCPU and RAM sizes include the following:

| Standard size | High memory size | 
|:---------:|:----------------:|
| 4 vCPU, 16 GiB  | N/A          |
| 8 vCPU, 16 GiB    | 8 vCPU, 32 GiB        |
| 16 vCPU, 32 GiB  | 16 vCPU, 64 GiB         |
| 32 vCPU, 64 GiB   | 32 vCPU, 128 GiB        |

> **Note:**
>
> To use the **32 vCPU, 128 GiB** size of TiDB, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
>
> If the vCPU and RAM size of TiDB is set as **4 vCPU, 16 GiB**, note the following restrictions:
>
> - The node count of TiDB can only be set to 1 or 2, and the node count of TiKV is fixed to 3.
> - 4 vCPU TiDB can only be used with 4 vCPU TiKV.
> - TiFlash is unavailable.
### TiDB node count

For high availability, it is recommended that you configure at least two TiDB nodes for each TiDB Cloud cluster.

In general, TiDB performance increases linearly with the number of TiDB nodes. However, when the number of TiDB nodes exceeds 8, the performance increment becomes slightly less than linearly proportional. For each additional 8 nodes, the performance deviation coefficient is about 5%.

For example:

- When there are 9 TiDB nodes, the performance deviation coefficient is about 5%, so the TiDB performance is about `9 * (1 - 5%) = 8.55` times the performance of a single TiDB node.
- When there are 16 TiDB nodes, the performance deviation coefficient is about 10%, so the TiDB performance is `16 * (1 - 10%) = 14.4` times the performance of a single TiDB node.

For a specified latency of a TiDB node, the TiDB performance varies depending on the different read-write ratios.

The performance of an 8 vCPU, 16 GiB TiDB node in different workloads is as follows:

| Workload | QPS (P95 ≈ 100ms) | QPS (P99 ≈ 300ms) | QPS (P99 ≈ 100ms) |
|----------|-------------------|-------------------|-------------------|
| Read     | 18,900            | 9,450             | 6,300             |
| Mixed    | 15,500            | 7,750             | 5,200             |
| Write    | 18,000            | 9,000             | 6,000             |

If the number of TiDB nodes is less than 8, the performance deviation coefficient is nearly 0%, so the TiDB performance of 16 vCPU, 32 GiB TiDB nodes is roughly twice that of 8 vCPU, 16 GiB TiDB nodes. If the number of TiDB nodes exceeds 8, it is recommended to choose 16 vCPU, 32 GiB TiDB nodes as this will require fewer nodes, which means smaller performance deviation coefficient.

When planning your cluster size, you can estimate the number of TiDB nodes according to your workload type, your overall expected performance (QPS), and the performance of a single TiDB node corresponding to the workload type using the following formula:

`node count = ceil(overall expected performance ÷ performance per node * (1 - performance deviation coefficient))`

In the formula, you need to calculate `node count = ceil(overall expected performance ÷ performance per node)` first to get a rough node count, and then use the corresponding performance deviation coefficient to get the final result of the node count.

For example, your overall expected performance is 110,000 QPS under a mixed workload, your P95 latency is about 100 ms, and you want to use 8 vCPU, 16 GiB TiDB nodes. Then, you can get the estimated TiDB performance of an 8 vCPU, 16 GiB TiDB node from the preceding table (which is `15,500`), and calculate a rough number of TiDB nodes as follows:

`node count = ceil(110,000 ÷ 15,500) = 8`

As the performance deviation coefficient of 8 nodes is about 5%, the estimated TiDB performance is `8 * 15,500 * (1 - 5%) = 117,800`, which can meet your expected performance of 110,000 QPS.

Therefore, 8 TiDB nodes (8 vCPU, 16 GiB) are recommended for you.
