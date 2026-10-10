# TiDB Binlog tutorial introduction, overview, and architecture

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/get-started-with-tidb-binlog.md`
- Source Title: `TiDB Binlog Tutorial`
- Source Heading Path: `TiDB Binlog Tutorial | TiDB Binlog Tutorial > TiDB Binlog Overview | TiDB Binlog Tutorial > Architecture`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `dm`
- Topic Tags: `tutorial`, `overview`, `architecture`, `pump`, `drainer`, `replication`, `incremental-backup`, `migration`, `mariadb`, `kafka`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0073_e1573a3b69`
- Source ID: `tidb-docs-8.1:tidb-binlog/get-started-with-tidb-binlog.md#tidb-binlog-tutorial`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b0c45984c0d18811268adc14a0bf54700be466f9ab5fc3e969b1975c6e208925`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/get-started-with-tidb-binlog#tidb-binlog-tutorial
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/get-started-with-tidb-binlog.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs a TiDB Binlog tutorial overview, architecture summary, or an explanation of Pump and Drainer in a simple self-managed deployment that pushes data to MariaDB or other downstream platforms.
- Retrieval Keywords: TiDB Binlog Tutorial, TiDB Binlog Overview, Architecture, Pump, Drainer, binary log data, real-time data backup and replication, incremental backups, replicate data from one TiDB cluster to another, Kafka, MariaDB, MySQL, TiDB DM, Data Migration, downstream platform, pump cluster, clustered architecture of Pump
- Follow-up Guidance: For more information, see the TiDB Binlog Cluster User Guide linked from the tutorial.
- Classification Note: This is classified as architecture because the content introduces TiDB Binlog concepts, describes Pump and Drainer roles, and explains the clustered data flow to downstream destinations.

## Official Source Content

# TiDB Binlog Tutorial

This tutorial starts with a simple TiDB Binlog deployment with a single node of each component (Placement Driver, TiKV Server, TiDB Server, Pump, and Drainer), set up to push data into a MariaDB Server instance.

This tutorial is targeted toward users who have some familiarity with the [TiDB Architecture](https://docs.pingcap.com/tidb/stable/tidb-architecture), who may have already set up a TiDB cluster (not mandatory), and who wants to gain hands-on experience with TiDB Binlog. This tutorial is a good way to "kick the tires" of TiDB Binlog and to familiarize yourself with the concepts of its architecture.

> **Warning:**
>
> The instructions to deploy TiDB in this tutorial should **not** be used to deploy TiDB in a production or development setting.

This tutorial assumes you're using a modern Linux distribution on x86-64. A minimal CentOS 7 installation running in VMware is used in this tutorial for the examples. It's recommended that you start from a clean install, so that you aren't impacted by quirks of your existing environment. If you don't want to use local virtualization, you can easily start a CentOS 7 VM using your cloud service.
## TiDB Binlog Overview

TiDB Binlog is a solution to collect binary log data from TiDB and provide real-time data backup and replication. It pushes incremental data updates from a TiDB Server cluster into downstream platforms.

You can use TiDB Binlog for incremental backups, to replicate data from one TiDB cluster to another, or to send TiDB updates through Kafka to a downstream platform of your choice.

TiDB Binlog is particularly useful when you migrate data from MySQL or MariaDB to TiDB, in which case you may use the TiDB DM (Data Migration) platform to get data from a MySQL/MariaDB cluster into TiDB, and then use TiDB Binlog to keep a separate, downstream MySQL/MariaDB instance/cluster in sync with your TiDB cluster. TiDB Binlog enables application traffic to TiDB to be pushed to a downstream MySQL or MariaDB instance/cluster, which reduces the risk of a migration to TiDB because you can easily revert the application to MySQL or MariaDB without downtime or data loss.

See [TiDB Binlog Cluster User Guide](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview) for more information.
## Architecture

TiDB Binlog comprises two components: the **Pump** and the **Drainer**. Several Pump nodes make up a pump cluster. Each Pump node connects to TiDB Server instances and receives updates made to each of the TiDB Server instances in a cluster. A Drainer connects to the Pump cluster and transforms the received updates into the correct format for a particular downstream destination, for example, Kafka, another TiDB Cluster or a MySQL/MariaDB server.

![TiDB-Binlog architecture](/media/tidb-binlog-cluster-architecture.png)

The clustered architecture of Pump ensures that updates won't be lost as new TiDB Server instances join or leave the TiDB Cluster or Pump nodes join or leave the Pump cluster.
