# TiDB architecture components overview

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-architecture.md`
- Source Title: `TiDB Architecture`
- Source Heading Path: `TiDB Architecture | TiDB Architecture > TiDB server | TiDB Architecture > Placement Driver (PD) server | TiDB Architecture > Storage servers | TiDB Architecture > Storage servers > TiKV server | TiDB Architecture > Storage servers > TiFlash server`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `tiflash`, `tiproxy`, `dashboard`, `sql`
- Topic Tags: `architecture`, `distributed-system`, `sql-layer`, `metadata`, `storage`, `regions`, `transactions`, `high-availability`, `columnar-analytics`, `scalability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0071_119cde4c91`
- Source ID: `tidb-docs-8.1:tidb-architecture.md#tidb-architecture`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `298b29335082a6d3abbfde1677620cab277c558253c1c6d5719eecf4e131c0b3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-architecture#tidb-architecture
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-architecture.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for a TiDB architecture overview or the roles of TiDB server, PD server, TiKV server, TiFlash server, TiProxy, Dashboard, Regions, transactions, scalability, or high availability.
- Retrieval Keywords: TiDB Architecture, TiDB server, Placement Driver (PD) server, PD server, TiKV server, TiFlash server, TiProxy, TiDB Dashboard, MySQL protocol, stateless SQL layer, distributed execution plan, metadata managing component, transaction IDs, Region, StartKey, EndKey, distributed transactional key-value storage engine, Snapshot Isolation, three replicas by default, automatic failover, column storage, analytical processing, horizontal scalability, load balancing components, LVS, HAProxy, ProxySQL, F5
- Follow-up Guidance: The source also describes that TiDB server handles SQL parsing and optimization, PD stores cluster metadata and topology and allocates transaction IDs, TiKV stores replicated Region data, and TiFlash is a columnar storage server for analytical processing.
- Classification Note: This chunk is classified as architecture because the official content summarizes the distributed TiDB system design and the responsibilities of its core components across SQL, metadata, and storage layers.

## Official Source Content

# TiDB Architecture

Compared with the traditional standalone databases, TiDB has the following advantages:

* Has a distributed architecture with flexible and elastic scalability.
* Fully compatible with the MySQL protocol, common features and syntax of MySQL. To migrate your applications to TiDB, you do not need to change a single line of code in many cases.
* Supports high availability with automatic failover when a minority of replicas fail; transparent to applications.
* Supports ACID transactions, suitable for scenarios requiring strong consistency such as bank transfer.

* Provides a rich series of [data migration tools](https://docs.pingcap.com/tidb/stable/migration-overview) for migrating, replicating, or backing up data.

As a distributed database, TiDB is designed to consist of multiple components. These components communicate with each other and form a complete TiDB system. The architecture is as follows:

![TiDB Architecture](/media/tidb-architecture-v6.png)
## TiDB server

The [TiDB server](https://docs.pingcap.com/tidb/stable/tidb-computing) is a stateless SQL layer that exposes the connection endpoint of the MySQL protocol to the outside. The TiDB server receives SQL requests, performs SQL parsing and optimization, and ultimately generates a distributed execution plan. It is horizontally scalable and provides the unified interface to the outside through the load balancing components such as TiProxy, Linux Virtual Server (LVS), HAProxy, ProxySQL or F5. It does not store data and is only for computing and SQL analyzing, transmitting actual data read request to TiKV nodes (or TiFlash nodes).
## Placement Driver (PD) server

The [PD server](https://docs.pingcap.com/tidb/stable/tidb-scheduling) is the metadata managing component of the entire cluster. It stores metadata of real-time data distribution of every single TiKV node and the topology structure of the entire TiDB cluster, provides the TiDB Dashboard management UI, and allocates transaction IDs to distributed transactions. The PD server is "the brain" of the entire TiDB cluster because it not only stores metadata of the cluster, but also sends data scheduling command to specific TiKV nodes according to the data distribution state reported by TiKV nodes in real time. In addition, the PD server consists of three nodes at least and has high availability. It is recommended to deploy an odd number of PD nodes.
## Storage servers
### TiKV server

The [TiKV server](https://docs.pingcap.com/tidb/stable/tidb-storage) is responsible for storing data. TiKV is a distributed transactional key-value storage engine.

[Region](https://docs.pingcap.com/tidb/stable/glossary#regionpeerraft-group) is the basic unit to store data. Each Region stores the data for a particular Key Range which is a left-closed and right-open interval from StartKey to EndKey.

[Region](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#region) is the basic unit to store data. Each Region stores the data for a particular Key Range which is a left-closed and right-open interval from StartKey to EndKey.

Multiple Regions exist in each TiKV node. TiKV APIs provide native support to distributed transactions at the key-value pair level and supports the Snapshot Isolation level isolation by default. This is the core of how TiDB supports distributed transactions at the SQL level. After processing SQL statements, the TiDB server converts the SQL execution plan to an actual call to the TiKV API. Therefore, data is stored in TiKV. All the data in TiKV is automatically maintained in multiple replicas (three replicas by default), so TiKV has native high availability and supports automatic failover.
### TiFlash server

The [TiFlash server](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview) is a special type of storage server. Unlike ordinary TiKV nodes, TiFlash stores data by column, mainly designed to accelerate analytical processing.
