# TiDB Cloud cluster sizing for TiKV storage nodes

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/size-your-cluster.md`
- Source Title: `Determine Your TiDB Size`
- Source Heading Path: `Determine Your TiDB Size > Size TiKV | Determine Your TiDB Size > Size TiKV > TiKV vCPU and RAM | Determine Your TiDB Size > Size TiKV > TiKV node count | Determine Your TiDB Size > Size TiKV > TiKV node count > Estimate TiKV node count according to data volume | Determine Your TiDB Size > Size TiKV > TiKV node count > Estimate TiKV node count according to expected performance | Determine Your TiDB Size > Size TiKV > TiKV node storage size`
- Source Line Ranges: `80-184`
- Source Scope: `cloud`
- Primary Component: `tikv`
- Related Components: `cloud`, `tidb`, `tiflash`
- Topic Tags: `cluster-sizing`, `storage-scaling`, `vcpu`, `memory`, `node-count`, `data-volume`, `compression-ratio`, `replicas`, `qps`, `latency`, `storage-capacity`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0199_0eba1f91f1`
- Source ID: `tidb-docs-8.1:tidb-cloud/size-your-cluster.md#size-tikv`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e6548fafbf236fda5aef5fafcf2dd553bb8ed0c0bff3df1e93726bbe5d6f14ad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#size-tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/size-your-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when estimating TiDB Cloud Dedicated TiKV storage node sizing from data volume, expected QPS, vCPU and RAM, node count across availability zones, replicas, compression ratio, or node storage capacity.
- Retrieval Keywords: Size TiKV, TiKV vCPU and RAM, TiKV node count, Estimate TiKV node count according to data volume, Estimate TiKV node count according to expected performance, TiKV node storage size, 3 nodes in 3 different Available Zones, 3-replica setup, TiKV compression ratio, 40%, storage usage ratio below 80%, node count = ceil(size of your data * TiKV compression ratio * the number of replicas ÷ TiKV storage usage ratio ÷ one TiKV capacity ÷ 3) * 3, node count = ceil(overall expected performance ÷ performance per node * (1 - performance deviation coefficient)), 8 vCPU, 32 GiB, 8 vCPU, 64 GiB, 16 vCPU, 64 GiB, 32 vCPU, 128 GiB, 4096 GiB, Min node storage, Max node storage, Default node storage, Scale Your TiDB Cluster, you cannot decrease the TiKV node storage size after the cluster creation, TiFlash is unavailable, 4 vCPU TiKV can only be used with 4 vCPU TiDB
- Follow-up Guidance: The source says to compare the TiKV node count estimated from data volume with the count estimated from expected performance and take the larger one as the recommended node count.
- Classification Note: This is classified as performance for the TiKV component because the content covers TiKV storage sizing, horizontal scaling, data-volume and performance formulas, supported node sizes, availability-zone distribution, and storage-capacity limits in TiDB Cloud.

## Official Source Content

## Size TiKV

TiKV is responsible for storing data. It is horizontally scalable.

You can configure node count, vCPU and RAM, and storage for TiKV.

To learn performance test results of different cluster scales, see [TiDB Cloud Performance Reference](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-performance-reference).
### TiKV vCPU and RAM

The supported vCPU and RAM sizes include the following:

| Standard size | High memory size | 
|:---------:|:----------------:|
| 4 vCPU, 16 GiB  |  N/A        |
| 8 vCPU, 32 GiB    | 8 vCPU, 64 GiB        |
| 16 vCPU, 64 GiB  | Coming soon       |
| 32 vCPU, 128 GiB   |  N/A  |

> **Note:**
>
> If the vCPU and RAM size of TiKV is set as **4 vCPU, 16 GiB**, note the following restrictions:
>
> - The node count of TiDB can only be set to 1 or 2, and the node count of TiKV is fixed to 3.
> - 4 vCPU TiKV can only be used with 4 vCPU TiDB.
> - TiFlash is unavailable.
### TiKV node count

The number of TiKV nodes should be **at least 1 set (3 nodes in 3 different Available Zones)**.

TiDB Cloud deploys TiKV nodes evenly to all availability zones (at least 3) in the region you select to achieve durability and high availability. In a typical 3-replica setup, your data is distributed evenly among the TiKV nodes across all availability zones and is persisted to the disk of each TiKV node.

> **Note:**
>
> When you scale your TiDB cluster, nodes in the 3 availability zones are increased or decreased at the same time. For how to scale in or scale out a TiDB cluster based on your needs, see [Scale Your TiDB Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/scale-tidb-cluster).

Although TiKV is mainly used for data storage, the performance of the TiKV node also varies depending on different workloads. Therefore, when planning the number of TiKV nodes, you need to estimate it according to both your [**data volume**](#estimate-tikv-node-count-according-to-data-volume) and [expected performance](#estimate-tikv-node-count-according-to-expected-performance), and then take the larger of the two estimates as the recommended node count.
#### Estimate TiKV node count according to data volume

You can calculate a recommended number of TiKV nodes according to your data volume as follows:

`node count = ceil(size of your data * TiKV compression ratio * the number of replicas ÷ TiKV storage usage ratio ÷ one TiKV capacity ÷ 3) * 3`

Generally, it is recommended to keep the usage ratio of TiKV storage below 80%. The number of replicas in TiDB Cloud is 3 by default. The maximum storage capacity of an 8 vCPU, 64 GiB TiKV node is 4096 GiB.

Based on historical data, the average TiKV compression ratio is around 40%.

Suppose that the size of your MySQL dump files is 20 TB and the TiKV compression ratio is 40%. Then, you can calculate a recommended number of TiKV nodes according to your data volume as follows:

`node count = ceil(20 TB * 40% * 3 ÷ 0.8 ÷ 4096 GiB ÷ 3) * 3 = 9`
#### Estimate TiKV node count according to expected performance

Similarly as TiDB performance, TiKV performance increases linearly with the number of TiKV nodes. However, when the number of TiKV nodes exceeds 8, the performance increment becomes slightly less than linearly proportional. For each additional 8 nodes, the performance deviation coefficient is about 5%.

For example:

- When there are 9 TiKV nodes, the performance deviation coefficient is about 5%, so the TiKV performance is about `9 * (1 - 5%) = 8.55` times the performance of a single TiKV node.
- When there are 18 TiKV nodes, the performance deviation coefficient is about 10%, so the TiKV performance is `18 * (1 - 10%) = 16.2` times the performance of a single TiKV node.

For a specified latency of a TiKV node, the TiKV performance varies depending on the different read-write ratios.

The performance of an 8 vCPU, 32 GiB TiKV node in different workloads is as follows:

| Workload | QPS (P95 ≈ 100ms) | QPS (P99 ≈ 300ms) | QPS (P99 ≈ 100ms) |
|----------|-------------------|-------------------|-------------------|
| Read     | 28,000            | 14,000            | 7,000             |
| Mixed    | 17,800            | 8,900             | 4,450             |
| Write    | 14,500            | 7,250             | 3,625             |

If the number of TiKV nodes is less than 8, the performance deviation coefficient is nearly 0%, so the performance of 16 vCPU, 64 GiB TiKV nodes is roughly twice that of 8 vCPU, 32 GiB TiKV nodes. If the number of TiKV nodes exceeds 8, it is recommended to choose 16 vCPU, 64 GiB TiKV nodes as this will require fewer nodes, which means smaller performance deviation coefficient.

When planning your cluster size, you can estimate the number of TiKV nodes according to your workload type, your overall expected performance (QPS), and the performance of a single TiKV node corresponding to the workload type using the following formula:

`node count = ceil(overall expected performance ÷ performance per node * (1 - performance deviation coefficient))`

In the formula, you need to calculate `node count = ceil(overall expected performance ÷ performance per node)` first to get a rough node count, and then use the corresponding performance deviation coefficient to get the final result of the node count.

For example, your overall expected performance is 110,000 QPS under a mixed workload, your P95 latency is about 100 ms, and you want to use 8 vCPU, 32 GiB TiKV nodes. Then, you can get the estimated TiKV performance of an 8 vCPU, 32 GiB TiKV node from the preceding table (which is `17,800`), and calculate a rough number of TiKV nodes as follows:

`node count = ceil(110,000 / 17,800 ) = 7`

As 7 is less than 8, the performance deviation coefficient of 7 nodes is 0. The estimated TiKV performance is `7 * 17,800 * (1 - 0) = 124,600`, which can meet your expected performance of 110,000 QPS.

Therefore, 7 TiKV nodes (8 vCPU, 32 GiB) are recommended for you according to your expected performance.

Next, you can compare the TiKV node count calculated according to data volume with the number calculated according to your expected performance, and take the larger one as a recommended number of your TiKV nodes.
### TiKV node storage size

The supported node storage sizes of different TiKV vCPUs are as follows:

| TiKV vCPU | Min node storage | Max node storage | Default node storage |
|:---------:|:----------------:|:----------------:|:--------------------:|
| 4 vCPU    | 200 GiB          |     2048 GiB     | 500 GiB              |
| 8 vCPU    | 200 GiB          |     4096 GiB     | 500 GiB              |
| 16 vCPU   | 200 GiB          |     4096 GiB     | 500 GiB              |
| 32 vCPU   | 200 GiB          |     4096 GiB     | 500 GiB              |

> **Note:**
>
> You cannot decrease the TiKV node storage size after the cluster creation.
