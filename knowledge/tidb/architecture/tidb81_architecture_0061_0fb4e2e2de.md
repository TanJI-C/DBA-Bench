# Three-AZ Two-Region deployment architecture and topology

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/three-data-centers-in-two-cities-deployment.md`
- Source Title: `Three Availability Zones in Two Regions Deployment`
- Source Heading Path: `Three Availability Zones in Two Regions Deployment | Three Availability Zones in Two Regions Deployment > Overview | Three Availability Zones in Two Regions Deployment > Deployment architecture | Three Availability Zones in Two Regions Deployment > Deployment architecture > Deployment details`
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `multi-az`, `cross-region`, `high-availability`, `disaster-recovery`, `raft`, `replica-placement`, `leader-placement`, `topology`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0061_0fb4e2e2de`
- Source ID: `tidb-docs-8.1:three-data-centers-in-two-cities-deployment.md#three-availability-zones-in-two-regions-deployment`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9797639e7aab68e7d1e4d8692a1dffdb5a03c7234e474edcb2c94cef0aea642b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/three-data-centers-in-two-cities-deployment#three-availability-zones-in-two-regions-deployment
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/three-data-centers-in-two-cities-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the official architecture, topology, or availability characteristics of a three availability zones in two regions TiDB deployment.
- Retrieval Keywords: Three Availability Zones in Two Regions Deployment, three AZs in two regions, three-data-centers-in-two-cities deployment, Seattle and San Francisco, AZ1 AZ2 AZ3, five replicas, Region leaders restricted to two AZs, Raft algorithm, cross-region high availability, disaster recovery AZ, multi-AZ topology, rack labels, TiDB cluster deployed to three AZs in two regions, Drainer incremental backup
- Follow-up Guidance: The source also includes deployment details such as racks rac1 through rac6, TiDB and PD placement, TiKV instance placement, monitoring components, and Drainer for incremental backup.
- Classification Note: This is classified as architecture because the content describes the deployment overview, node and replica distribution, leader placement constraints, and the stated advantages and disadvantages of the topology.

## Official Source Content

# Three Availability Zones in Two Regions Deployment

This document introduces the architecture and configuration of the three availability zones (AZs) in two regions deployment.

The term "region" in this document refers to a geographic area, while the capitalized "Region" refers to a basic unit of data storage in TiKV. "AZ" refers to an isolated location within a region, and each region has multiple AZs. The solution described in this document also applies to the scenario where multiple data centers are located in a single city.
## Overview

The architecture of three AZs in two regions is a highly available and disaster tolerant deployment solution that provides a production data AZ, a disaster recovery AZ in the same region, and a disaster recovery AZ in another region. In this mode, the three AZs in two regions are interconnected. If one AZ fails or suffers from a disaster, other AZs can still operate well and take over the key applications or all applications. Compared with the multi-AZ in one region deployment, this solution has the advantage of cross-region high availability and can survive region-level natural disasters.

The distributed database TiDB natively supports the three-AZ-in-two-region architecture by using the Raft algorithm, and guarantees the consistency and high availability of data within a database cluster. Because the network latency across AZs in the same region is relatively low, the application traffic can be dispatched to two AZs in the same region, and the traffic load can be shared by these two AZs by controlling the distribution of TiKV Region leaders and PD leaders.
## Deployment architecture

This section takes the example of Seattle and San Francisco to explain the deployment mode of three AZs in two regions for the distributed database of TiDB.

In this example, two AZs (AZ1 and AZ2) are located in Seattle and another AZ (AZ3) is located in San Francisco. The network latency between AZ1 and AZ2 is lower than 3 milliseconds. The network latency between AZ3 and AZ1/AZ2 in Seattle is about 20 milliseconds (ISP dedicated network is used).

The architecture of the cluster deployment is as follows:

- The TiDB cluster is deployed to three AZs in two regions: AZ1 in Seattle, AZ2 in Seattle, and AZ3 in San Francisco.
- The cluster has five replicas, two in AZ1, two in AZ2, and one in AZ3. For the TiKV component, each rack has a label, which means that each rack has a replica.
- The Raft protocol is adopted to ensure consistency and high availability of data, which is transparent to users.

![3-AZ-in-2-region architecture](/media/three-data-centers-in-two-cities-deployment-01.png)

This architecture is highly available. The distribution of Region leaders is restricted to the two AZs (AZ1 and AZ2) that are in the same region (Seattle). Compared with the three-AZ solution in which the distribution of Region leaders is not restricted, this architecture has the following advantages and disadvantages:

- **Advantages**

    - Region leaders are in AZs of the same region with low latency, so the write is faster.
    - The two AZs can provide services at the same time, so the resource usage rate is higher.
    - If one AZ fails, services are still available and data safety is ensured.

- **Disadvantages**

    - Because the data consistency is achieved by the Raft algorithm, when two AZs in the same region fail at the same time, only one surviving replica remains in the disaster recovery AZ in another region (San Francisco). This cannot meet the requirement of the Raft algorithm that most replicas survive. As a result, the cluster can be temporarily unavailable. Maintenance staff needs to recover the cluster from the one surviving replica and a small amount of hot data that has not been replicated will be lost. But this case is a rare occurrence.
    - Because the ISP dedicated network is used, the network infrastructure of this architecture has a high cost.
    - Five replicas are configured in three AZs in two regions, data redundancy increases, which brings a higher storage cost.
### Deployment details

The configuration of the three AZs in two regions (Seattle and San Francisco) deployment plan is illustrated as follows:

![3-AZ-2-region](/media/three-data-centers-in-two-cities-deployment-02.png)

From the preceding illustration, you can see that Seattle has two AZs: AZ1 and AZ2. AZ1 has three sets of racks: rac1, rac2, and rac3. AZ2 has two racks: rac4 and rac5. The AZ3 in San Francisco has the rac6 rack.

In the rac1 of AZ1, one server is deployed with TiDB and PD services, and the other two servers are deployed with TiKV services. Each TiKV server is deployed with two TiKV instances (tikv-server). This is similar to rac2, rac4, rac5, and rac6.

The TiDB server, the control machine, and the monitoring server are on rac3. The TiDB server is deployed for regular maintenance and backup. Prometheus, Grafana, and the restore tools are deployed on the control machine and monitoring machine.

Another backup server can be added to deploy Drainer. Drainer saves binlog data to a specified location by outputting files, to achieve incremental backup.
