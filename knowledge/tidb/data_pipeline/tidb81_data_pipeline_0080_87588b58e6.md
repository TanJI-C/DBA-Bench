# TiDB Cloud data streaming and changefeed concepts

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-streaming-concepts.md`
- Source Title: `Data Streaming`
- Source Heading Path: `Data Streaming | Data Streaming > Changefeed`
- Source Line Ranges: `5-22`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`
- Topic Tags: `data-streaming`, `changefeed`, `replication`, `incremental-changes`, `table-filters`, `event-filters`, `kafka`, `mysql`, `cloud-storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0080_87588b58e6`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-streaming-concepts.md#data-streaming`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d2dcc1accdea108f951f540f216b6f817d743bc1eafcc09a60064d1f4e2be639`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-streaming-concepts#data-streaming
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-streaming-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about TiDB Cloud data streaming or changefeed basics, including supported targets, incremental replication behavior, or filtering options.
- Retrieval Keywords: TiDB Cloud data streaming, Changefeed, TiDB Cloud changefeed, stream data changes, replicate data changes, Apache Kafka, MySQL, TiDB Cloud, cloud storage, incremental data changes, existing data must be exported and loaded manually, table filters, event filters, INSERT, DELETE, Changefeed page, scaling, pausing, resuming, editing, deleting
- Follow-up Guidance: The source points to the Changefeed documentation for more information: Changefeed overview.
- Classification Note: This is classified as data_pipeline for the cloud component because the content defines TiDB Cloud changefeed-based streaming and replication of incremental data changes to external systems.

## Official Source Content

# Data Streaming

TiDB Cloud lets you stream data changes from your TiDB Cluster to other systems like Kafka, MySQL, and object storage.

Currently, TiDB Cloud supports streaming data to Apache Kafka, MySQL, TiDB Cloud, and cloud storage.
## Changefeed

TiDB Cloud changefeed is a continuous data stream that helps you replicate data changes from TiDB Cloud to other data services.

On the **Changefeed** page in the TiDB Cloud console, you can create a changefeed, view a list of existing changefeeds, and operate the existing changefeeds (such as scaling, pausing, resuming, editing, and deleting a changefeed).

Replication includes only incremental data changes by default. If existing data must be replicated, it must be exported and loaded into the target system manually before starting the changefeed.

In TiDB Cloud, replication can be tailored by defining table filters (to specify which tables to replicate) and event filters (to include or exclude specific types of events like INSERT or DELETE).

For more information, see [Changefeed](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview).
