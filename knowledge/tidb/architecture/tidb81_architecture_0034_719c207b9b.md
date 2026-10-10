# DR concepts and component architecture

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-solution-introduction.md`
- Source Title: `Overview of TiDB Disaster Recovery Solutions`
- Source Heading Path: `Overview of TiDB Disaster Recovery Solutions | Overview of TiDB Disaster Recovery Solutions > Basic concepts | Overview of TiDB Disaster Recovery Solutions > Component architecture | Overview of TiDB Disaster Recovery Solutions > Component architecture > TiDB | Overview of TiDB Disaster Recovery Solutions > Component architecture > TiCDC | Overview of TiDB Disaster Recovery Solutions > Component architecture > BR`
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `ticdc`, `br`, `pd`
- Topic Tags: `disaster-recovery`, `rto`, `rpo`, `error-tolerance`, `region`, `architecture`, `replication`, `raft`, `snapshot-backup`, `log-backup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0034_719c207b9b`
- Source ID: `tidb-docs-8.1:dr-solution-introduction.md#overview-of-tidb-disaster-recovery-solutions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2eb2b09b6c9b2f21277de8ee603bebc77e9d81f288f87e5a0ed8c83993901d54`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-solution-introduction#overview-of-tidb-disaster-recovery-solutions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-solution-introduction.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for TiDB disaster recovery concepts such as RTO, RPO, error tolerance objective, region, or the DR-oriented architecture roles of TiDB, TiKV, TiFlash, TiCDC, and BR.
- Retrieval Keywords: RTO, Recovery Time Objective, RPO, Recovery Point Objective, error tolerance objective, region, TiDB architecture, TiKV Region, Raft protocol, TiFlash learner role, TiCDC architecture, Capture process, PD's etcd, BR architecture, full snapshot backup, continuous log backup
- Follow-up Guidance: The source also points to later sections that describe specific DR solutions and compare them.
- Classification Note: This chunk is classified as architecture because it defines DR concepts and introduces the component architecture of TiDB, TiCDC, and BR from the perspective of disaster recovery.

## Official Source Content

# Overview of TiDB Disaster Recovery Solutions

This document introduces the disaster recovery (DR) solutions provided by TiDB. The organization of this document is as follows:

- Describes the basic concepts in DR.
- Introduces the architecture of TiDB, TiCDC, and Backup & Restore (BR).
- Describes the DR solutions provided by TiDB.
- Compares these DR solutions.
## Basic concepts

- RTO (Recovery Time Objective): The time required for the system to recover from a disaster.
- RPO (Recovery Point Objective): The maximum amount of data loss that the business can tolerate in a disaster.

The following figure illustrates these two concepts:

![RTO and RPO](/media/dr/rto-rpo.png)

- Error tolerance objective: Because a disaster can affect different regions. In this document, the term error tolerance objective is used to describe the maximum range of a disaster that the system can tolerate.
- Region: This document focuses on regional DR and "region" mentioned here refers to a geographical area or city.
## Component architecture

Before introducing specific DR solutions, this section introduces the architecture of TiDB components from the perspective of DR, including TiDB, TiCDC, and BR.
### TiDB

![TiDB architecture](/media/dr/tidb-architecture.png)

TiDB is designed with an architecture of separated computing and storage:

- TiDB is the SQL computing layer of the system.
- TiKV is the storage layer of the system, and is a row-based storage engine. [Region](https://docs.pingcap.com/tidb/stable/glossary#regionpeerraft-group) is the basic unit for scheduling data in TiKV. A Region is a collection of sorted rows of data. The data in a Region is saved in at least three replicas, and data changes are replicated in the log layer through the Raft protocol.
- An optional component, TiFlash is a columnar storage engine that can be used to speed up analytical queries. Data is replicated from TiKV to TiFlash through the learner role in a Raft group.

TiDB stores three complete data replicas. Therefore, it is naturally capable of DR based on multiple replicas. At the same time, because TiDB uses Raft logs to replicate transaction logs, it can also provide DR based on transaction log replication.
### TiCDC

![TiCDC architecture](/media/ticdc/cdc-architecture.png)

As an incremental data replication tool for TiDB, TiCDC is highly available through PD's etcd. TiCDC pulls data changes from TiKV nodes through multiple Capture processes, and then sorts and merges data changes internally. After that, TiCDC replicates data to multiple downstream systems by using multiple replication tasks. In the preceding architecture diagram:

- TiKV server: sends data changes in the upstream to TiCDC nodes. When TiCDC nodes find the change logs not continuous, they will actively request the TiKV server to provide change logs.
- TiCDC: runs multiple Capture processes. Each Capture process pulls part of the KV change logs, and sorts the pulled data before replicating the changes to different downstream systems.

It can be seen from the preceding architecture diagram that, the architecture of TiCDC is similar to that of a transactional log replication system, but with better scalability and merits of logical data replication. Therefore, TiCDC is a good supplementation for TiDB in the DR scenario.
### BR

![BR architecture](/media/br/br-snapshot-arch.png)

As a backup and restore tool for TiDB, BR can perform full snapshot backup based on a specific time point and continuous log backup of a TiDB cluster. When the TiDB cluster is completely unavailable, you can restore the backup files in a new cluster. BR is usually considered the last resort for data security.
