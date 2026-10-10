# Kafka replication behavior and Open Protocol event details

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-faq.md`
- Source Title: `TiCDC FAQs`
- Source Heading Path: `TiCDC FAQs > Why does the latency from TiCDC to Kafka become higher and higher? | TiCDC FAQs > When TiCDC replicates data to Kafka, can I control the maximum size of a single message in TiDB? | TiCDC FAQs > If I modify a row multiple times in a transaction, will TiCDC output multiple row change events? | TiCDC FAQs > When TiCDC replicates data to Kafka, does a message contain multiple types of data changes? | TiCDC FAQs > When TiCDC replicates data to Kafka, how do I view the timestamp, table name, and schema name in the output of TiCDC Open Protocol? | TiCDC FAQs > When TiCDC replicates data to Kafka, how do I know the timestamp of the data changes in a message? | TiCDC FAQs > How does TiCDC Open Protocol represent `null`? | TiCDC FAQs > How can I tell if a Row Changed Event of TiCDC Open Protocol is an `INSERT` event or an `UPDATE` event?`
- Source Line Ranges: `233-292`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `shared`
- Topic Tags: `kafka`, `latency`, `message-size`, `open-protocol`, `row-change`, `event-format`, `timestamp`, `null`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0072_f9e7b0b19d`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-faq.md#why-does-the-latency-from-ticdc-to-kafka-become-higher-and-higher`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2b3d2cce01e1cfff0ddbeed2df72f3eeb6651c20a5243c528c10f60eacba4684`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#why-does-the-latency-from-ticdc-to-kafka-become-higher-and-higher
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-faq.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiCDC replication to Kafka, including growing latency, Kafka message sizing, Open Protocol message fields, row change semantics, or how `null` and event types are represented.
- Retrieval Keywords: latency from TiCDC to Kafka, message.max.bytes, replica.fetch.max.bytes, fetch.message.max.bytes, max-message-bytes, max-batch-size, open-protocol, avro, canal-json, row change events, ts, scm, tbl, unix timestamp, null type code 6, "p" and "u" fields, "d" field, INSERT event, UPDATE event, DELETE event
- Follow-up Guidance: The content refers to TiCDC Open Protocol event format, column type code, and Row Changed Event format for more information.
- Classification Note: This is classified as data_pipeline because the content focuses on Kafka delivery behavior, batching and message size controls, and the structure of TiCDC Open Protocol events.

## Official Source Content

## Why does the latency from TiCDC to Kafka become higher and higher?

* Check [how do I view the state of TiCDC replication tasks](#how-do-i-view-the-state-of-ticdc-replication-tasks).
* Adjust the following parameters of Kafka:

    * Increase the `message.max.bytes` value in `server.properties` to `1073741824` (1 GB).
    * Increase the `replica.fetch.max.bytes` value in `server.properties` to `1073741824` (1 GB).
    * Increase the `fetch.message.max.bytes` value in `consumer.properties` to make it larger than the `message.max.bytes` value.
## When TiCDC replicates data to Kafka, can I control the maximum size of a single message in TiDB?

When `protocol` is set to `avro` or `canal-json`, messages are sent per row change. A single Kafka message contains only one row change and is generally no larger than Kafka's limit. Therefore, there is no need to limit the size of a single message. If the size of a single Kafka message does exceed Kafka's limit, refer to [Why does the latency from TiCDC to Kafka become higher and higher?](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#why-does-the-latency-from-ticdc-to-kafka-become-higher-and-higher).

When `protocol` is set to `open-protocol`, messages are sent in batches. Therefore, one Kafka message might be excessively large. To avoid this situation, you can configure the `max-message-bytes` parameter to control the maximum size of data sent to the Kafka broker each time (optional, `10MB` by default). You can also configure the `max-batch-size` parameter (optional, `16` by default) to specify the maximum number of change records in each Kafka message.
## If I modify a row multiple times in a transaction, will TiCDC output multiple row change events?

No. When you modify the same row in one transaction multiple times, TiDB only sends the latest modification to TiKV. Therefore, TiCDC can only obtain the result of the latest modification.
## When TiCDC replicates data to Kafka, does a message contain multiple types of data changes?

Yes. A single message might contain multiple `update`s or `delete`s, and `update` and `delete` might co-exist.
## When TiCDC replicates data to Kafka, how do I view the timestamp, table name, and schema name in the output of TiCDC Open Protocol?

The information is included in the key of Kafka messages. For example:

```json
{
    "ts":<TS>,
    "scm":<Schema Name>,
    "tbl":<Table Name>,
    "t":1
}
```

For more information, refer to [TiCDC Open Protocol event format](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-protocol#event-format).
## When TiCDC replicates data to Kafka, how do I know the timestamp of the data changes in a message?

You can get the unix timestamp by moving `ts` in the key of the Kafka message by 18 bits to the right.
## How does TiCDC Open Protocol represent `null`?

In TiCDC Open Protocol, the type code `6` represents `null`.

| Type | Code | Output Example | Note |
|:--|:--|:--|:--|
| Null | 6 | `{"t":6,"v":null}` | |

For more information, refer to [TiCDC Open Protocol column type code](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-protocol#column-type-code).
## How can I tell if a Row Changed Event of TiCDC Open Protocol is an `INSERT` event or an `UPDATE` event?

* `UPDATE` event contains both `"p"` and `"u"` fields
* `INSERT` event only contains the `"u"` field
* `DELETE` event only contains the `"d"` field

For more information, refer to [Open protocol Row Changed Event format](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-protocol#row-changed-event).
