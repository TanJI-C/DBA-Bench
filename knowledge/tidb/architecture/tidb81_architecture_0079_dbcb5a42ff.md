# Multi-AZ high availability for TiDB Cloud Dedicated

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/high-availability-with-multi-az.md`
- Source Title: `High Availability in TiDB Cloud Dedicated`
- Source Heading Path: `High Availability in TiDB Cloud Dedicated`
- Source Line Ranges: `5-22`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `high availability`, `multi-az`, `raft`, `failover`, `load balancer`, `replication`, `durability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0079_dbcb5a42ff`
- Source ID: `tidb-docs-8.1:tidb-cloud/high-availability-with-multi-az.md#high-availability-in-tidb-cloud-dedicated`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9ac98357ada318623ff198c10e500f99fb037871c322a30f714486a2b7664f65`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/high-availability-with-multi-az#high-availability-in-tidb-cloud-dedicated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/high-availability-with-multi-az.md

## Retrieval Guidance

- Use When: Use this chunk when answering how TiDB Cloud Dedicated provides multi-AZ high availability across TiDB, TiKV, and TiFlash nodes, including replication, load balancer routing, and automatic failover.
- Retrieval Keywords: TiDB Cloud Dedicated high availability, multi-AZ, availability zones, Raft consensus algorithm, Raft Groups, automatic failover, load balancer, TiDB node, TiKV node, TiFlash node, 3-replica setup, Raft Learner, durability, safely replicated, at least two TiDB nodes, minimum number of TiKV nodes is 3, at least two TiFlash nodes, at least two replicas
- Follow-up Guidance: The source also states component-specific minimum or recommended counts: at least two TiDB nodes, a minimum of three TiKV nodes, and at least two TiFlash nodes with at least two replicas for high availability in production environment.
- Classification Note: This chunk is classified as architecture because it describes the high availability design of TiDB Cloud Dedicated, including component roles, cross-availability-zone deployment, replication mechanisms, and failover behavior.

## Official Source Content

# High Availability in TiDB Cloud Dedicated

TiDB uses the Raft consensus algorithm to ensure that data is highly available and safely replicated throughout storage in Raft Groups. Data is redundantly copied between storage nodes and placed in different availability zones to protect against machine or data center failures. With automatic failover, TiDB ensures that your service is always on.

TiDB Cloud Dedicated clusters consist of three major components: TiDB node, TiKV node, and TiFlash node. The high availability implementation of each component for TiDB Cloud Dedicated is as follows:

* **TiDB node**

    TiDB is for computing only and does not store data. It is horizontally scalable. TiDB Cloud Dedicated deploys TiDB nodes evenly to different availability zones in a region. When a user executes a SQL request, the request first passes through a load balancer deployed across availability zones, and then the load balancer distributes the request to different TiDB nodes for execution. It is recommended that each TiDB Cloud Dedicated cluster has at least two TiDB nodes for high availability.

* **TiKV node**

    [TiKV](https://docs.pingcap.com/tidb/stable/tikv-overview) is the row-based storage layer of TiDB Cloud Dedicated cluster with horizontal scalability. The minimum number of TiKV nodes for a TiDB Cloud Dedicated cluster is 3. TiDB Cloud Dedicated deploys TiKV nodes evenly to all availability zones (at least 3) in the region you select to achieve durability and high availability. In a typical 3-replica setup, your data is distributed evenly among the TiKV nodes across all availability zones and is persisted to the disk of each TiKV node.

* **TiFlash node**

    [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash-overview), as a columnar storage extension of TiKV, is the key component that makes TiDB essentially a Hybrid Transactional/Analytical Processing (HTAP) database. In TiFlash, the columnar replicas are asynchronously replicated according to the Raft Learner consensus algorithm. TiDB Cloud Dedicated deploys TiFlash nodes evenly to different availability zones in a region. It is recommended that you configure at least two TiFlash nodes in each TiDB Cloud Dedicated cluster and create at least two replicas of the data for high availability in your production environment.
