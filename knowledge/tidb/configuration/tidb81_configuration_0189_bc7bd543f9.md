# Kafka large message handling and consumption

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-kafka.md`
- Source Title: `Replicate Data to Kafka`
- Source Heading Path: `Replicate Data to Kafka > Handle messages that exceed the Kafka topic limit > Send handle keys only | Replicate Data to Kafka > Handle messages that exceed the Kafka topic limit > Consume messages with handle keys only | Replicate Data to Kafka > Handle messages that exceed the Kafka topic limit > Send large messages to external storage | Replicate Data to Kafka > Handle messages that exceed the Kafka topic limit > Consume large messages from external storage`
- Source Line Ranges: `419-547`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `kafka`, `sink`, `large-messages`, `handle-key-only`, `claim-check`, `external-storage`, `consumer`, `gc-lifetime`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0189_bc7bd543f9`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-kafka.md#send-handle-keys-only`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3ecbdc6a48b1beaaac6dd9bb9d57a429f394ff2cbc7e7fcff0f00352d95494e1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#send-handle-keys-only
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiCDC Kafka sink details for oversized messages, including handle-key-only output, claim-check external storage, and how consumers recover full data.
- Retrieval Keywords: TiCDC Kafka sink, large-message-handle-option, handle-key-only, claim-check, claim-check-storage-uri, onlyHandleKey, claimCheckLocation, tidb_snapshot, tidb_gc_life_time, external storage, Kafka topic limit
- Follow-up Guidance: If the message contains only the handle key or a claim-check location, the consumer reads the upstream TiDB historical data or the external storage object to restore the complete message.
- Classification Note: This chunk classifies TiCDC Kafka sink behavior for messages exceeding the Kafka topic limit and explains both sending and consuming flows for handle-key-only and external-storage cases.

## Official Source Content

### Send handle keys only

Starting from v7.3.0, TiCDC Kafka sink supports sending only the handle keys when the message size exceeds the limit. This can significantly reduce the message size and avoid changefeed errors and task failures caused by the message size exceeding the Kafka topic limit. Handle Key refers to the following:

* If the table to be replicated has primary key, the primary key is the handle key.
* If the table does not have primary key but has NOT NULL Unique Key, the NOT NULL Unique Key is the handle key.

The sample configuration is as follows:

```toml
[sink.kafka-config.large-message-handle]
# large-message-handle-option is introduced in v7.3.0.
# Defaults to "none". When the message size exceeds the limit, the changefeed fails.
# When set to "handle-key-only", if the message size exceeds the limit, only the handle key is sent in the data field. If the message size still exceeds the limit, the changefeed fails.
large-message-handle-option = "claim-check"
```
### Consume messages with handle keys only

The message format with handle keys only is as follows:

```json
{
    "id": 0,
    "database": "test",
    "table": "tp_int",
    "pkNames": [
        "id"
    ],
    "isDdl": false,
    "type": "INSERT",
    "es": 1639633141221,
    "ts": 1639633142960,
    "sql": "",
    "sqlType": {
        "id": 4
    },
    "mysqlType": {
        "id": "int"
    },
    "data": [
        {
          "id": "2"
        }
    ],
    "old": null,
    "_tidb": {     // TiDB extension fields
        "commitTs": 429918007904436226,  // A TiDB TSO timestamp
        "onlyHandleKey": true
    }
}
```

When a Kafka consumer receives a message, it first checks the `onlyHandleKey` field. If this field exists and is `true`, it means that the message only contains the handle key of the complete data. In this case, to get the complete data, you need to query the upstream TiDB and use [`tidb_snapshot` to read historical data](https://docs.pingcap.com/tidb/stable/read-historical-data).

> **Warning:**
>
> When the Kafka consumer processes data and queries TiDB, the data might have been deleted by GC. You need to [modify the GC Lifetime of the TiDB cluster](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) to a larger value to avoid this situation.
### Send large messages to external storage

Starting from v7.4.0, TiCDC Kafka sink supports sending large messages to external storage when the message size exceeds the limit. Meanwhile, TiCDC sends a message to Kafka that contains the address of the large message in the external storage. This can avoid changefeed failures caused by the message size exceeding the Kafka topic limit.

An example configuration is as follows:

```toml
[sink.kafka-config.large-message-handle]
# large-message-handle-option is introduced in v7.3.0.
# Defaults to "none". When the message size exceeds the limit, the changefeed fails.
# When set to "handle-key-only", if the message size exceeds the limit, only the handle key is sent in the data field. If the message size still exceeds the limit, the changefeed fails.
# When set to "claim-check", if the message size exceeds the limit, the message is sent to external storage.
large-message-handle-option = "claim-check"
claim-check-storage-uri = "s3://claim-check-bucket"
```

When `large-message-handle-option` is set to `"claim-check"`, `claim-check-storage-uri` must be set to a valid external storage address. Otherwise, creating the changefeed will fail.

> **Tip**
>
> For more information about the URI parameters of Amazon S3, GCS, and Azure Blob Storage in TiCDC, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

TiCDC does not clean up messages on external storage services. Data consumers need to manage external storage services on their own.
### Consume large messages from external storage

The Kafka consumer receives a message that contains the address of the large message in the external storage. The message format is as follows:

```json
{
    "id": 0,
    "database": "test",
    "table": "tp_int",
    "pkNames": [
        "id"
    ],
    "isDdl": false,
    "type": "INSERT",
    "es": 1639633141221,
    "ts": 1639633142960,
    "sql": "",
    "sqlType": {
        "id": 4
    },
    "mysqlType": {
        "id": "int"
    },
    "data": [
        {
          "id": "2"
        }
    ],
    "old": null,
    "_tidb": {     // TiDB extension fields
        "commitTs": 429918007904436226,  // A TiDB TSO timestamp
        "claimCheckLocation": "s3:/claim-check-bucket/${uuid}.json"
    }
}
```

If the message contains the `claimCheckLocation` field, the Kafka consumer reads the large message data stored in JSON format according to the address provided by the field. The message format is as follows:

```json
{
  key: "xxx",
  value: "xxx",
}
```

The `key` and `value` fields contain the encoded large message, which should have been sent to the corresponding field in the Kafka message. Consumers can parse the data in these two parts to restore the content of the large message.
