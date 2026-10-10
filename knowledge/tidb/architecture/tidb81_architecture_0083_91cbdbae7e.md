# TiDB Cloud Dedicated scalability concepts and component scaling

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/scalability-concepts.md`
- Source Title: `Scalability`
- Source Heading Path: `Scalability | Scalability > Vertical and horizontal scaling | Scalability > TiDB scalability | Scalability > TiKV scalability | Scalability > TiFlash scalability`
- Source Line Ranges: `5-43`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `scalability`, `vertical-scaling`, `horizontal-scaling`, `compute`, `storage`, `availability-zones`, `high-availability`, `replication`, `analytics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0083_91cbdbae7e`
- Source ID: `tidb-docs-8.1:tidb-cloud/scalability-concepts.md#scalability`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ebf448490306d94d89ece9c8331e4902d1dea28ab1e82dab63ecb05f40e782db`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/scalability-concepts#scalability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/scalability-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Cloud Dedicated scaling behavior, including vertical versus horizontal scaling and how TiDB, TiKV, and TiFlash resources can be adjusted separately without service disruption.
- Retrieval Keywords: TiDB Cloud Dedicated scalability, vertical scaling, horizontal scaling, scale up, scale out, compute and storage resources separately, without any service disruption, TiDB scalability, TiKV scalability, TiFlash scalability, node number, vCPU, RAM, storage, 3 available zones, high availability, 3-replica setup, real-time analytics workloads, TiDB Cloud Serverless scales automatically
- Follow-up Guidance: The source also points to Determine Your TiDB Size for cluster sizing information and notes that TiDB Cloud Serverless scales automatically but cannot be manually scaled.
- Classification Note: This is classified as architecture content because it describes the scaling model and component roles of TiDB Cloud Dedicated across TiDB compute, TiKV row-based storage, and TiFlash columnar analytics storage.

## Official Source Content

# Scalability

TiDB Cloud Dedicated lets you adjust its compute and storage resources separately to match your data volume or workload changes. TiDB Cloud Dedicated can do scaling without any service disruption. This flexibility allows organizations to optimize their infrastructure costs while maintaining high performance and availability.

> **Note:**
>
> [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) scales automatically based on your application's workload changes. However, you cannot manually scale a TiDB Cloud Serverless cluster.

> **Tip:**
>
> For information about how to determine the size of a TiDB Cloud Dedicated cluster, see [Determine Your TiDB Size](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster).
## Vertical and horizontal scaling

TiDB Cloud Dedicated supports both vertical (scale up) and horizontal (scale out) scaling.

- Horizontal scaling is the process of adding nodes to your dedicated cluster to distribute the workload.
- Vertical scaling is the process of increasing the vCPU and RAM for your dedicated cluster.

A combination of both vertical and horizontal scaling is also supported in TiDB Cloud Dedicated.
## TiDB scalability

TiDB is for computing only and does not store data. You can configure the node number, vCPU, and RAM for TiDB.

In general, TiDB performance increases linearly with the number of TiDB nodes.
## TiKV scalability

TiKV is responsible for storing row-based data. You can configure the node number, vCPU and RAM, and storage for TiKV. The number of TiKV nodes should be at least 1 set (3 nodes in 3 different available zones) and increase by 3 nodes.

TiDB Cloud deploys TiKV nodes evenly to 3 available zones in the region you select to achieve durability and high availability. In a typical 3-replica setup, your data is distributed evenly among the TiKV nodes across all availability zones and is persisted to the disk of each TiKV node. Although TiKV is mainly used for data storage, the performance of the TiKV node also varies depending on different workloads.
## TiFlash scalability

TiFlash is responsible for storing columnar data. TiFlash synchronizes data from TiKV in real time and supports real-time analytics workloads right out of the box. You can configure the node number, vCPU and RAM, and storage for TiFlash.

TiDB Cloud deploys TiFlash nodes evenly to different availability zones in a region. It is recommended that you configure at least two TiFlash nodes in each TiDB Cloud cluster and create at least two replicas of the data for high availability in your production environment.
