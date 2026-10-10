# MySQL sink overview, restrictions, and prerequisites

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-mysql.md`
- Source Title: `Sink to MySQL`
- Source Heading Path: `Sink to MySQL | Sink to MySQL > Restrictions | Sink to MySQL > Prerequisites | Sink to MySQL > Prerequisites > Network | Sink to MySQL > Prerequisites > Load existing data (optional) | Sink to MySQL > Prerequisites > Create target tables in MySQL`
- Source Line Ranges: `5-89`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `dumpling`, `tidb`
- Topic Tags: `changefeed`, `mysql sink`, `restrictions`, `prerequisites`, `network`, `vpc peering`, `dns`, `incremental replication`, `data export`, `gc lifetime`, `target tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0211_0524bfc387`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-mysql.md#sink-to-mysql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `85d599f380e5fd4d88c8fbe9d826319a5428f259af1558242269c0bfcd2f9d17`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-mysql#sink-to-mysql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-mysql.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about MySQL sink prerequisites, restrictions, network connectivity, loading existing data, or creating target tables for TiDB Cloud changefeeds.
- Retrieval Keywords: Sink to MySQL, TiDB Cloud Dedicated cluster version v6.1.3 or later, TiDB Cloud Serverless clusters changefeed feature is unavailable, up to 100 changefeeds, restrictions as TiCDC, unsupported scenarios, primary key or a non-null unique index, duplicated data inserted downstream, VPC peering connection, CIDR of the region where your TiDB Cloud cluster is located, Accepter DNS resolution, Cloud SQL Auth proxy, tidb_gc_life_time, SET GLOBAL tidb_gc_life_time = '720h';, Dumpling, mydumper/myloader, SHOW MASTER STATUS, Pos, TSO, Create target tables in MySQL, incremental data
- Follow-up Guidance: If existing data is loaded with Dumpling, the metadata file's `SHOW MASTER STATUS` `Pos` is the TSO used as the start position of the MySQL sink.
- Classification Note: This chunk is classified as configuration because it defines the documented prerequisites, restrictions, network setup details, and required preparation for creating a Sink to MySQL changefeed.

## Official Source Content

# Sink to MySQL

This document describes how to stream data from TiDB Cloud to MySQL using the **Sink to MySQL** changefeed.

> **Note:**
>
> - To use the changefeed feature, make sure that your TiDB Cloud Dedicated cluster version is v6.1.3 or later.
> - For [TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless), the changefeed feature is unavailable.
## Restrictions

- For each TiDB Cloud cluster, you can create up to 100 changefeeds.
- Because TiDB Cloud uses TiCDC to establish changefeeds, it has the same [restrictions as TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview#unsupported-scenarios).
- If the table to be replicated does not have a primary key or a non-null unique index, the absence of a unique constraint during replication could result in duplicated data being inserted downstream in some retry scenarios.
## Prerequisites

Before creating a changefeed, you need to complete the following prerequisites:

- Set up your network connection
- Export and load the existing data to MySQL (optional)
- Create corresponding target tables in MySQL if you do not load the existing data and only want to replicate incremental data to MySQL
### Network

Make sure that your TiDB Cluster can connect to the MySQL service.

If your MySQL service is in an AWS VPC that has no public internet access, take the following steps:

1. [Set up a VPC peering connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) between the VPC of the MySQL service and your TiDB cluster.
2. Modify the inbound rules of the security group that the MySQL service is associated with.

    You must add [the CIDR of the region where your TiDB Cloud cluster is located](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#prerequisite-set-a-cidr-for-a-region) to the inbound rules. Doing so allows the traffic to flow from your TiDB Cluster to the MySQL instance.

3. If the MySQL URL contains a hostname, you need to allow TiDB Cloud to be able to resolve the DNS hostname of the MySQL service.

    1. Follow the steps in [Enable DNS resolution for a VPC peering connection](https://docs.aws.amazon.com/vpc/latest/peering/modify-peering-connections.html#vpc-peering-dns).
    2. Enable the **Accepter DNS resolution** option.

If your MySQL service is in a Google Cloud VPC that has no public internet access, take the following steps:

1. If your MySQL service is Google Cloud SQL, you must expose a MySQL endpoint in the associated VPC of the Google Cloud SQL instance. You may need to use the [**Cloud SQL Auth proxy**](https://cloud.google.com/sql/docs/mysql/sql-proxy) which is developed by Google.
2. [Set up a VPC peering connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) between the VPC of the MySQL service and your TiDB cluster.
3. Modify the ingress firewall rules of the VPC where MySQL is located.

    You must add [the CIDR of the region where your TiDB Cloud cluster is located](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#prerequisite-set-a-cidr-for-a-region) to the ingress firewall rules. Doing so allows the traffic to flow from your TiDB Cluster to the MySQL endpoint.
### Load existing data (optional)

The **Sink to MySQL** connector can only sink incremental data from your TiDB cluster to MySQL after a certain timestamp. If you already have data in your TiDB cluster, you can export and load the existing data of your TiDB cluster into MySQL before enabling **Sink to MySQL**.

To load the existing data:

1. Extend the [tidb_gc_life_time](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) to be longer than the total time of the following two operations, so that historical data during the time is not garbage collected by TiDB.

    - The time to export and import the existing data
    - The time to create **Sink to MySQL**

    For example:

    ```sql
    SET GLOBAL tidb_gc_life_time = '720h';
    ```

2. Use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) to export data from your TiDB cluster, then use community tools such as [mydumper/myloader](https://centminmod.com/mydumper.html) to load data to the MySQL service.

3. From the [exported files of Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#format-of-exported-files), get the start position of MySQL sink from the metadata file:

    The following is a part of an example metadata file. The `Pos` of `SHOW MASTER STATUS` is the TSO of the existing data, which is also the start position of MySQL sink.

    ```
    Started dump at: 2020-11-10 10:40:19
    SHOW MASTER STATUS:
            Log: tidb-binlog
            Pos: 420747102018863124
    Finished dump at: 2020-11-10 10:40:20
    ```
### Create target tables in MySQL

If you do not load the existing data, you need to create corresponding target tables in MySQL manually to store the incremental data from TiDB. Otherwise, the data will not be replicated.
