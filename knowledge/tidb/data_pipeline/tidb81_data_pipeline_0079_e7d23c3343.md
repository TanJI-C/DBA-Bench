# TiDB Cloud sink overview, restrictions, and prerequisites

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-tidb-cloud.md`
- Source Title: `Sink to TiDB Cloud`
- Source Heading Path: `Sink to TiDB Cloud | Sink to TiDB Cloud > Restrictions | Sink to TiDB Cloud > Prerequisites`
- Source Line Ranges: `5-59`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `dumpling`, `tidb`
- Topic Tags: `changefeed`, `sink`, `restrictions`, `prerequisites`, `tso`, `gc-lifetime`, `export`, `import`, `metadata`, `serverless`, `dedicated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0079_e7d23c3343`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-tidb-cloud.md#sink-to-tidb-cloud`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `79ed03c53c0c478836500738170fc05976e686d2006b2b6ad75c6f225377b737`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-tidb-cloud#sink-to-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-tidb-cloud.md

## Retrieval Guidance

- Use When: Use this chunk when you need the overview, restrictions, or prerequisites for streaming data from a TiDB Cloud Dedicated cluster to a TiDB Cloud Serverless cluster with Sink to TiDB Cloud.
- Retrieval Keywords: Sink to TiDB Cloud, stream data from a TiDB Cloud Dedicated cluster to a TiDB Cloud Serverless cluster, Changefeed feature v6.1.3 or later, up to 100 changefeeds, same restrictions as TiCDC, unsupported scenarios, primary key or non-null unique index, duplicated data inserted downstream, AWS Oregon us-west-2, AWS Frankfurt eu-central-1, AWS Singapore ap-southeast-1, AWS Tokyo ap-northeast-1, created after November 9, 2022, same project and the same region, private endpoints, incremental data after a certain TSO, tidb_gc_life_time, SET GLOBAL tidb_gc_life_time = '720h';, Dumpling, TiDB Cloud Serverless Import, metadata file, SHOW MASTER STATUS, Pos, start position of TiDB Cloud sink
- Follow-up Guidance: The source explains that before creating a changefeed you export existing data with Dumpling, import it to TiDB Cloud Serverless, and get the start TSO from the Dumpling metadata file `SHOW MASTER STATUS` `Pos`.
- Classification Note: This is classified as data_pipeline because the content defines changefeed sink scope, replication restrictions, region and network constraints, and prerequisite data export, import, and TSO preparation.

## Official Source Content

# Sink to TiDB Cloud

This document describes how to stream data from a TiDB Cloud Dedicated cluster to a TiDB Cloud Serverless cluster.

> **Note:**
>
> To use the Changefeed feature, make sure that your TiDB Cloud Dedicated cluster version is v6.1.3 or later.
## Restrictions

- For each TiDB Cloud cluster, you can create up to 100 changefeeds.
- Because TiDB Cloud uses TiCDC to establish changefeeds, it has the same [restrictions as TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview#unsupported-scenarios).
- If the table to be replicated does not have a primary key or a non-null unique index, the absence of a unique constraint during replication could result in duplicated data being inserted downstream in some retry scenarios.
- The **Sink to TiDB Cloud** feature is only available to TiDB Cloud Dedicated clusters that are in the following AWS regions and created after November 9, 2022:

    - AWS Oregon (us-west-2)
    - AWS Frankfurt (eu-central-1)
    - AWS Singapore (ap-southeast-1)
    - AWS Tokyo (ap-northeast-1)

- The source TiDB Cloud Dedicated cluster and the destination TiDB Cloud Serverless cluster must be in the same project and the same region.
- The **Sink to TiDB Cloud** feature only supports network connection via private endpoints. When you create a changefeed to stream data from a TiDB Cloud Dedicated cluster to a TiDB Cloud Serverless cluster, TiDB Cloud will automatically set up the private endpoint connection between the two clusters.
## Prerequisites

The **Sink to TiDB Cloud** connector can only sink incremental data from a TiDB Cloud Dedicated cluster to a TiDB Cloud Serverless cluster after a certain [TSO](https://docs.pingcap.com/tidb/stable/glossary#tso).

Before creating a changefeed, you need to export existing data from the source TiDB Cloud Dedicated cluster and load the data to the destination TiDB Cloud Serverless cluster.

1. Extend the [tidb_gc_life_time](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) to be longer than the total time of the following two operations, so that historical data during the time is not garbage collected by TiDB.

    - The time to export and import the existing data
    - The time to create **Sink to TiDB Cloud**

    For example:

    ```sql
    SET GLOBAL tidb_gc_life_time = '720h';
    ```

2. Use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) to export data from your TiDB Cloud Dedicated cluster, then use [TiDB Cloud Serverless Import](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files-serverless) to load data to the destination TiDB Cloud Serverless cluster.

3. From the [exported files of Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#format-of-exported-files), get the start position of TiDB Cloud sink from the metadata file:

    The following is a part of an example metadata file. The `Pos` of `SHOW MASTER STATUS` is the TSO of the existing data, which is also the start position of TiDB Cloud sink.

    ```
    Started dump at: 2023-03-28 10:40:19
    SHOW MASTER STATUS:
            Log: tidb-binlog
            Pos: 420747102018863124
    Finished dump at: 2023-03-28 10:40:20
    ```
