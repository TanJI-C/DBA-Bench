# Serverless HA architectures and failover behavior

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-high-availability.md`
- Source Title: `High Availability in TiDB Cloud Serverless`
- Source Heading Path: `High Availability in TiDB Cloud Serverless | High Availability in TiDB Cloud Serverless > Overview | High Availability in TiDB Cloud Serverless > Zonal high availability architecture | High Availability in TiDB Cloud Serverless > Zonal high availability architecture > Failover process | High Availability in TiDB Cloud Serverless > Regional high availability architecture | High Availability in TiDB Cloud Serverless > Regional high availability architecture > Failover process`
- Source Line Ranges: `5-77`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`
- Topic Tags: `high-availability`, `raft`, `zonal`, `regional`, `availability-zones`, `failover`, `redundancy`, `durability`, `latency`, `retry-logic`, `traffic-redirection`, `beta`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0086_0de7d3364b`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-high-availability.md#high-availability-in-tidb-cloud-serverless`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `72a12859f6af63bc5abd6abe1b474f96d1ce2cd57abb7e4cf3cb92dedd2ab109`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-high-availability#high-availability-in-tidb-cloud-serverless
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-high-availability.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about TiDB Cloud Serverless high availability architecture, including zonal versus regional deployment, component placement across availability zones, and failover behavior during node or zone failures.
- Retrieval Keywords: TiDB Cloud Serverless high availability, zonal high availability, regional high availability, Raft consensus algorithm, Placement Driver PD, Gateway, TiDB, TiKV, TiFlash compute nodes, TiFlash write nodes, availability zone, multi-availability zone, failover process, traffic is automatically redirected, elastic load balancer, Amazon S3, EBS, retry logic, ap-northeast-1, beta
- Follow-up Guidance: The source also includes automatic backups and durability, session impact during failures, and the RTO and RPO comparison for zonal and regional high availability.
- Classification Note: This is classified as architecture because the content describes how TiDB Cloud Serverless places PD, Gateway, TiDB, TiKV, and TiFlash across availability zones and how failover works in zonal and regional designs.

## Official Source Content

# High Availability in TiDB Cloud Serverless

TiDB Cloud Serverless is designed with robust mechanisms to maintain high availability and data durability by default, preventing single points of failure and ensuring continuous service even in the face of disruptions. As a fully managed service based on the battle-tested TiDB Open Source product, it inherits TiDB's core high availability (HA) features and augments them with additional cloud-native capabilities.
## Overview

TiDB ensures high availability and data durability using the Raft consensus algorithm. This algorithm consistently replicates data changes across multiple nodes, allowing TiDB to handle read and write requests even in the event of node failures or network partitions. This approach provides both high data durability and fault tolerance.

TiDB Cloud Serverless extends these capabilities with two types of high availability to meet different operational requirements:

- **Zonal high availability (default)**: This option places all nodes within a single availability zone, reducing network latency. It ensures high availability without requiring application-level redundancy across zones, making it suitable for applications that prioritize low latency within a single zone. Zonal high availability is available in all regions that support TiDB Cloud Serverless. For more information, see [Zonal high availability architecture](#zonal-high-availability-architecture).

- **Regional high availability (beta)**: This option distributes nodes across multiple availability zones, offering maximum infrastructure isolation and redundancy. It provides the highest level of availability but requires application-level redundancy across zones. It is recommended to choose this option if you need maximum availability protection against infrastructure failures within a zone. Note that it increases latency and might incur cross-zone data transfer fees. This feature is available in selected regions with multi-availability zone support and can only be enabled during cluster creation. For more information, see [Regional high availability architecture](#regional-high-availability-architecture).
## Zonal high availability architecture

> **Note:**
>
> Zonal high availability is the default option and is available in all AWS regions that support TiDB Cloud Serverless.

When you create a cluster with the default zonal high availability, all components, including Gateway, TiDB, TiKV, and TiFlash compute/write nodes, run in the same availability zone. The placement of these components in the data plane offer infrastructure redundancy with virtual machine pools, which minimizes failover time and network latency due to colocation.

![TiDB Cloud Serverless zonal high availability](/media/tidb-cloud/serverless-zonal-high-avaliability-aws.png)

In zonal high availability architecture:

- The Placement Driver (PD) is deployed across multiple availability zones, ensuring high availability by replicating data redundantly across zones.
- Data is replicated across TiKV servers and TiFlash write nodes within the local availability zone.
- TiDB servers and TiFlash compute nodes read from and write to TiKV and TiFlash write nodes, which are safeguarded by storage-level replication.
### Failover process

TiDB Cloud Serverless ensures a transparent failover process for your applications. During a failover:

- A new replica is created to replace the failed one.

- Servers providing storage services recover local caches from persisted data on Amazon S3, restoring the system to a consistent state with the replicas.

In the storage layer, persisted data is regularly pushed to Amazon S3 for high durability. Moreover, immediate updates are not only replicated across multiple TiKV servers but also stored on the EBS of each server, which further replicates the data for additional durability. TiDB automatically resolves issues by backing off and retrying in milliseconds, ensuring the failover process remains seamless for client applications.

The gateway and computing layers are stateless, so failover involves restarting them elsewhere immediately. Applications should implement retry logic for their connections. While the zonal setup provides high availability, it cannot handle an entire zone failure. If the zone becomes unavailable, downtime will occur until the zone and its dependent services are restored.
## Regional high availability architecture

When you create a cluster with regional high availability, critical OLTP (Online Transactional Processing) workload components, such as PD and TiKV, are deployed across multiple availability zones to ensure redundant replication and maximizing availability. During normal operations, components like Gateway, TiDB, and TiFlash compute/write nodes are hosted in the primary availability zone. These components in data plane offer infrastructure redundancy through virtual machine pools, which minimizes failover time and network latency due to colocation.

> **Note:**
>
> - Regional high availability is currently in beta and only available in the AWS Tokyo (`ap-northeast-1`) region.
> - You can enable regional high availability only during cluster creation.

![TiDB Cloud Serverless regional high availability](/media/tidb-cloud/serverless-regional-high-avaliability-aws.png)

In regional high availability architecture:

- The Placement Driver (PD) and TiKV are deployed across multiple availability zones, and data is always replicated redundantly across zones to ensure the highest level of availability.
- Data is replicated across TiFlash write nodes within the primary availability zone.
- TiDB servers and TiFlash compute nodes read from and write to these TiKV and TiFlash write nodes, which are safeguarded by storage-level replication.
### Failover process

In the rare event of a primary zone failure scenario, which could be caused by a natural disaster, configuration change, software issue, or hardware failure, critical OLTP workload components, including Gateway and TiDB, are automatically launched in the standby availability zone. Traffic is automatically redirected to the standby zone to ensure swift recovery and maintain business continuity.

TiDB Cloud Serverless minimizes service disruption and ensures business continuity during a primary zone failure by performing the following actions:

- Automatically create new replicas of Gateway and TiDB in the standby availability zone.
- Use the elastic load balancer to detect active gateway replicas in the standby availability zone and redirect OLTP traffic from the failed primary zone.

In addition to providing high availability through TiKV replication, TiKV instances are deployed and configured to place each data replica in a different availability zone. The system remains available as long as two availability zones are operating normally. For high durability, data persistence is ensured by regularly backing up data to S3. Even if two zones fail, data stored in S3 remains accessible and recoverable.

Applications are unaffected by failures in non-primary zones and remain unaware of such events. During a primary zone failure, Gateway and TiDB are launched in the standby availability zone to handle workloads. Ensure that your applications implement retry logic to redirect new requests to active servers in the standby availability zone.
