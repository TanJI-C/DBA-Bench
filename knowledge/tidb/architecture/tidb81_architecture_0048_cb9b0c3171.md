# 3-AZ deployment architecture and Raft-based availability

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/multi-data-centers-in-one-city-deployment.md`
- Source Title: `Multiple Availability Zones in One Region Deployment`
- Source Heading Path: `Multiple Availability Zones in One Region Deployment | Multiple Availability Zones in One Region Deployment > Raft protocol | Multiple Availability Zones in One Region Deployment > Three AZs in one region deployment | Multiple Availability Zones in One Region Deployment > Three AZs in one region deployment > Simple architecture | Multiple Availability Zones in One Region Deployment > Three AZs in one region deployment > Optimized architecture`
- Source Line Ranges: `5-93`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `raft`, `availability-zones`, `high-availability`, `disaster-recovery`, `leader-election`, `network-latency`, `topology`, `placement-rules`, `tso`, `read-performance`, `write-latency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0048_cb9b0c3171`
- Source ID: `tidb-docs-8.1:multi-data-centers-in-one-city-deployment.md#multiple-availability-zones-in-one-region-deployment`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7ac45015142354a1519675b7213bea825f7b693de5fe485b06039bc2bf7f29fd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/multi-data-centers-in-one-city-deployment#multiple-availability-zones-in-one-region-deployment
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/multi-data-centers-in-one-city-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when explaining TiDB 3-AZ deployment architecture, Raft-based availability, leader election behavior, and the latency tradeoffs of simple versus optimized multi-AZ layouts in one region.
- Retrieval Keywords: 3-AZ deployment architecture, Raft protocol, majority protocol, leader election, Multiple Availability Zones in One Region Deployment, TiDB TiKV PD across three AZs, RPO = 0, within 20 seconds in most cases, two-phase commit, TimeStamp Oracle, TSO, PD leader, TiKV Region leader, network latency across AZs, optimized architecture, config set label-property reject-leader LabelName labelValue, member leader transfer pdName1, member leader_priority pdName1 5, placement rules
- Follow-up Guidance: The source also provides a scheduling policy template for evicting leaders to one AZ and transferring PD leadership, with a note that starting from TiDB v5.2 the `label-property` configuration is not supported by default and placement rules are used to set the replica policy.
- Classification Note: This chunk is classified as architecture because it describes the Raft-based high-availability design, failure tolerance conditions, and deployment topology tradeoffs for TiDB, TiKV, and PD across three AZs.

## Official Source Content

# Multiple Availability Zones in One Region Deployment

As a distributed SQL database, TiDB combines the best features of the traditional relational database and the scalability of the NoSQL database, and is highly available across availability zones (AZs). This document introduces the deployment of multiple AZs in one region.

The term "region" in this document refers to a geographic area, while the capitalized "Region" refers to a basic unit of data storage in TiKV. "AZ" refers to an isolated location within a region, and each region has multiple AZs. The solution described in this document also applies to the scenario where multiple data centers are located in a single city.
## Raft protocol

Raft is a distributed consensus algorithm. Using this algorithm, both PD and TiKV, among components of the TiDB cluster, achieve disaster recovery of data, which is implemented through the following mechanisms:

- The essential role of Raft members is to perform log replication and act as a state machine. Among Raft members, data replication is implemented by replicating logs. Raft members change their own states in different conditions to elect a leader to provide services.
- Raft is a voting system that follows the majority protocol. In a Raft group, if a member gets the majority of votes, its membership changes to leader. In other words, when the majority of nodes remain in the Raft group, a leader can be elected to provide services.

To take advantage of Raft's reliability, the following conditions must be met in a real deployment scenario:

- Use at least three servers in case one server fails.
- Use at least three racks in case one rack fails.
- Use at least three AZs in case one AZ fails.
- Deploy TiDB in at least three regions in case data safety issue occurs in one region.

The native Raft protocol does not have good support for an even number of replicas. Considering the impact of cross-region network latency, three AZs in the same region might be the most suitable solution to a highly available and disaster tolerant Raft deployment.
## Three AZs in one region deployment

TiDB clusters can be deployed in three AZs in the same region. In this solution, data replication across the three AZs is implemented using the Raft protocol within the cluster. These three AZs can provide read and write services at the same time. Data consistency is not affected even if one AZ fails.
### Simple architecture

TiDB, TiKV, and PD are distributed among three AZs, which is the most common deployment with the highest availability.

![3-AZ Deployment Architecture](/media/deploy-3dc.png)

**Advantages:**

- All replicas are distributed among three AZs, with high availability and disaster recovery capability.
- No data will be lost if one AZ is down (RPO = 0).
- Even if one AZ is down, the other two AZs will automatically start leader election and automatically resume services within a certain period (within 20 seconds in most cases). See the following diagram for more information:

![Disaster Recovery for 3-AZ Deployment](/media/deploy-3dc-dr.png)

**Disadvantages:**

The performance can be affected by the network latency.

- For writes, all the data has to be replicated to at least two AZs. Because TiDB uses a two-phase commit for writes, the write latency is at least twice the latency of the network between two AZs.
- The read performance will also be affected by the network latency if the leader is not in the same AZ with the TiDB node that sends the read request.
- Each TiDB transaction needs to obtain TimeStamp Oracle (TSO) from the PD leader. So if the TiDB and PD leaders are not in the same AZ, the performance of the transactions will also be affected by the network latency because each transaction with the write request has to obtain TSO twice.
### Optimized architecture

If not all of the three AZs need to provide services to the applications, you can dispatch all the requests to one AZ and configure the scheduling policy to migrate the TiKV Region leader and PD leader to the same AZ. In this way, neither obtaining TSO nor reading TiKV Regions will be impacted by the network latency across AZs. If this AZ is down, the PD leader and TiKV Region leader will be automatically elected in other surviving AZs, and you just need to switch the requests to the AZs that are still alive.

![Read Performance Optimized 3-AZ Deployment](/media/deploy-3dc-optimize.png)

**Advantages:**

The cluster's read performance and the capability to get TSO are improved. A configuration template of scheduling policy is as follows:

```shell
-- Evicts all leaders of other AZs to the AZ that provides services to the application.
config set label-property reject-leader LabelName labelValue

-- Migrates PD leaders and sets priority.
member leader transfer pdName1
member leader_priority pdName1 5
member leader_priority pdName2 4
member leader_priority pdName3 3
```

> **Note:**
>
> Starting from TiDB v5.2, the `label-property` configuration is not supported by default. To set the replica policy, use the [placement rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules).

**Disadvantages:**

- Write scenarios are still affected by network latency across AZs. This is because Raft follows the majority protocol and all written data must be replicated to at least two AZs.
- The TiDB server that provides services is only in one AZ.
- All application traffic is processed by one AZ and the performance is limited by the network bandwidth pressure of that AZ.
- The capability to get TSO and the read performance are affected by whether the PD server and TiKV server are up in the AZ that processes application traffic. If these servers are down, the application is still affected by the cross-center network latency.
