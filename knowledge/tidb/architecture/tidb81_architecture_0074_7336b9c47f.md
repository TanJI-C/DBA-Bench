# TiDB Binlog overview and Pump architecture

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-overview.md`
- Source Title: `TiDB Binlog Overview`
- Source Heading Path: `TiDB Binlog Cluster Overview | TiDB Binlog Cluster Overview > TiDB Binlog architecture | TiDB Binlog Cluster Overview > TiDB Binlog architecture > Pump`
- Source Line Ranges: `5-34`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `sql`, `shared`
- Topic Tags: `binlog`, `architecture`, `pump`, `replication`, `backup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0074_7336b9c47f`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-overview.md#tidb-binlog-cluster-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8d01e716d8693bb2f8a35df42f69b4af5e179665348310b720ced4fdd8ae76bf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview#tidb-binlog-cluster-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks what TiDB Binlog is, what near real-time backup and replication it provides, or what role Pump plays in the TiDB Binlog architecture.
- Retrieval Keywords: TiDB Binlog Cluster Overview, TiDB Binlog architecture, Pump, record the binlogs generated in TiDB, sort the binlogs based on the commit time of the transaction, send binlogs to Drainer, near real-time backup and replication, real-time backup and restoration, data replication, TiCDC alternative solution, PITR alternative solution
- Follow-up Guidance: The same source also describes Drainer, `binlogctl`, and the main features of Pump and Drainer in the TiDB Binlog cluster.
- Classification Note: This is classified as architecture because the content defines TiDB Binlog, its cluster composition of Pump and Drainer, and the Pump data flow responsibilities.

## Official Source Content

# TiDB Binlog Cluster Overview

This document introduces the architecture and the deployment of the cluster version of TiDB Binlog.

TiDB Binlog is a tool used to collect binlog data from TiDB and provide near real-time backup and replication to downstream platforms.

TiDB Binlog has the following features:

* **Data replication:** replicate the data in the TiDB cluster to other databases
* **Real-time backup and restoration:** back up the data in the TiDB cluster and restore the TiDB cluster when the cluster fails

> **Note:**
>
> - TiDB Binlog is not compatible with some features introduced in TiDB v5.0 and they cannot be used together. For details, see [Notes](#notes).
> - Starting from TiDB v7.5.0, technical support for the data replication feature of TiDB Binlog is no longer provided. It is strongly recommended to use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) as an alternative solution for data replication.
> - Although TiDB v7.5.0 still supports the real-time backup and restoration feature of TiDB Binlog, this component will be completely deprecated in future versions. It is recommended to use [PITR](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) as an alternative solution for data recovery.
## TiDB Binlog architecture

The TiDB Binlog architecture is as follows:

![TiDB Binlog architecture](/media/tidb-binlog-cluster-architecture.png)

The TiDB Binlog cluster is composed of Pump and Drainer.
### Pump

[Pump](https://github.com/pingcap/tidb-binlog/blob/release-8.1/pump) is used to record the binlogs generated in TiDB, sort the binlogs based on the commit time of the transaction, and send binlogs to Drainer for consumption.
