# TiCDC Debezium protocol overview and Kafka changefeed usage

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-debezium.md`
- Source Title: `TiCDC Debezium Protocol`
- Source Heading Path: `TiCDC Debezium Protocol | TiCDC Debezium Protocol > Use the Debezium message format`
- Source Line Ranges: `5-25`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `debezium`, `kafka`, `changefeed`, `sink-uri`, `protocol`, `row-changed-events`, `schema-output`, `committs`, `clusterid`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0071_463d557964`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-debezium.md#ticdc-debezium-protocol`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `380fe3d7f9c55f76011e8a46d7149e3345fcf6b4ed44da147c4ba3e2e8c42ee5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-debezium#ticdc-debezium-protocol
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-debezium.md

## Retrieval Guidance

- Use When: Use this chunk when you need the overview of TiCDC Debezium protocol behavior for a Kafka changefeed, including sink-uri protocol settings, supported event types, optional schema output, and TiCDC-specific fields.
- Retrieval Keywords: TiCDC Debezium Protocol, Kafka downstream sink, sink-uri, protocol=debezium, cdc cli changefeed create, kafka://127.0.0.1:9092/topic-name?kafka-version=2.4.0&protocol=debezium, Debezium style output format, Row Changed events, DDL events ignored, WATERMARK events ignored, debezium-disable-schema, CommitTs, ClusterID
- Follow-up Guidance: The source also explains that the Debezium protocol only supports Row Changed events, ignores DDL and WATERMARK events, and can disable schema output with `debezium-disable-schema`.
- Classification Note: This is classified as data_pipeline because the content describes configuring TiCDC changefeeds to send TiDB change events to Kafka in Debezium message format.

## Official Source Content

# TiCDC Debezium Protocol

[Debezium](https://debezium.io/) is a tool for capturing database changes. It converts each captured database change into a message called an "event" and sends these events to Kafka. Starting from v8.0.0, TiCDC supports sending TiDB changes to Kafka using a Debezium style output format, simplifying migration from MySQL databases for users who had previously been using Debezium's MySQL integration.
## Use the Debezium message format

When you use Kafka as the downstream sink, specify the `protocol` field as `debezium` in `sink-uri` configuration. Then TiCDC encapsulates the Debezium messages based on the events and sends TiDB data change events to the downstream.

Currently, the Debezium protocol only supports Row Changed events and directly ignores DDL events and WATERMARK events. A Row changed event represents a data change in a row. When a row changes, the Row Changed event is sent, including relevant information about the row both before and after the change. A WATERMARK event marks the replication progress of a table, indicating that all events earlier than the watermark have been sent to the downstream.

The configuration example for using the Debezium message format is as follows:

```shell
cdc cli changefeed create --server=http://127.0.0.1:8300 --changefeed-id="kafka-debezium" --sink-uri="kafka://127.0.0.1:9092/topic-name?kafka-version=2.4.0&protocol=debezium"
```

The Debezium output format contains the schema information of the current row so that downstream consumers can better understand the data structure of the current row. For scenarios where schema information is unnecessary, you can also disable the schema output by setting the `debezium-disable-schema` parameter to `true` in the changefeed configuration file or `sink-uri`.

In addition, the original Debezium format does not include important fields such as the unique transaction identifier of the `CommitTS` in TiDB. To ensure data integrity, TiCDC adds two fields, `CommitTs` and `ClusterID`, to the Debezium format to identify the relevant information of TiDB data changes.
