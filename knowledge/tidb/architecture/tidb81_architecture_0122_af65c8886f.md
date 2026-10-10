# Two-AZ one-region deployment overview and architecture

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/two-data-centers-in-one-city-deployment.md`
- Source Title: `Two Availability Zones in One Region Deployment`
- Source Heading Path: `Two Availability Zones in One Region Deployment | Two Availability Zones in One Region Deployment > Introduction | Two Availability Zones in One Region Deployment > Deployment architecture`
- Source Line Ranges: `5-34`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `tidb`
- Topic Tags: `multi-az`, `disaster-recovery`, `dr-auto-sync`, `raft`, `replication`, `availability-zones`, `region`, `learner-replica`, `voter-replica`, `status-switch`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0122_af65c8886f`
- Source ID: `tidb-docs-8.1:two-data-centers-in-one-city-deployment.md#two-availability-zones-in-one-region-deployment`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5babfeb2d6378e4b4ce9c525f9f2be872cd13128a0bca4c4d2aeb26caf0ac0db`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/two-data-centers-in-one-city-deployment#two-availability-zones-in-one-region-deployment
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/two-data-centers-in-one-city-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for the architecture, replica layout, or replication states of a two availability zones in one region or two data centers in one city deployment.
- Retrieval Keywords: Two Availability Zones in One Region Deployment, two availability zones in one region, two data centers in one city, DR Auto-Sync mode, Raft protocol, three Voter replicas in AZ1, two Voter replicas along with one Learner replica in AZ2, sync, async, sync-recover, status switch, primary AZ, disaster recovery AZ
- Follow-up Guidance: For topology configuration, Placement Rules, and enabling DR Auto-Sync mode, see the configuration and status switch sections in the same document.
- Classification Note: This chunk is classified as architecture because it describes the deployment overview, replica distribution across AZ1 and AZ2, Raft-based consistency, and the sync, async, and sync-recover statuses.

## Official Source Content

# Two Availability Zones in One Region Deployment

This document introduces the deployment mode of two availability zones (AZs) in one region, including the architecture, configuration, how to enable this deployment mode, and how to use replicas in this mode.

The term "region" in this document refers to a geographic area, while the capitalized "Region" refers to a basic unit of data storage in TiKV. "AZ" refers to an isolated location within a region, and each region has multiple AZs. The solution described in this document also applies to the scenario where multiple data centers are located in a single city.
## Introduction

TiDB usually adopts the multi-AZ deployment solution to ensure high availability and disaster recovery capability. The multi-AZ deployment solution includes multiple deployment modes, such as multiple AZs in one region and multiple AZs in two regions. This document introduces the deployment mode of two AZs in one region. Deployed in this mode, TiDB can also meet the requirements of high availability and disaster recovery, with a lower cost. This deployment solution adopts Data Replication Auto Synchronous mode, or the DR Auto-Sync mode.

Under the mode of two AZs in one region, the two AZs are less than 50 kilometers apart. They are usually located in the same region or in two adjacent regions. The network latency between the two AZs is lower than 1.5 milliseconds and the bandwidth is higher than 10 Gbps.
## Deployment architecture

This section takes the example of a region where two availability zones AZ1 and AZ2 are located respectively in the east and west. AZ1 is the primary AZ and AZ2 is the disaster recovery (DR) AZ.

The architecture of the cluster deployment is as follows:

- The cluster has six replicas: three Voter replicas in AZ1, and two Voter replicas along with one Learner replica in AZ2. For the TiKV component, each rack has a proper label.
- The Raft protocol is adopted to ensure consistency and high availability of data, which is transparent to users.

![2-AZ-in-1-region architecture](/media/two-dc-replication-1.png)

This deployment solution defines three statuses to control and identify the replication status of the cluster, which restricts the replication mode of TiKV. The replication mode of the cluster can automatically and adaptively switch between the three statuses. For details, see the [Status switch](#status-switch) section.

- **sync**: Synchronous replication mode. In this mode, at least one replica in the disaster recovery AZ synchronizes with the primary AZ. The Raft algorithm ensures that each log is replicated to the DR based on the label.
- **async**: Asynchronous replication mode. In this mode, the disaster recovery AZ is not fully synchronized with the primary AZ. The Raft algorithm follows the majority protocol to replicate logs.
- **sync-recover**: Synchronous recovery mode. In this mode, the disaster recovery AZ is not fully synchronized with the primary AZ. Raft gradually switches to the label replication mode and then reports the label information to PD.
