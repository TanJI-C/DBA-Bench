# TiCDC Canal-JSON usage, TiDB extension, and event message formats

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-canal-json.md`
- Source Title: `TiCDC Canal-JSON Protocol`
- Source Heading Path: `TiCDC Canal-JSON Protocol | TiCDC Canal-JSON Protocol > Use Canal-JSON | TiCDC Canal-JSON Protocol > TiDB extension field | TiCDC Canal-JSON Protocol > Definitions of message formats | TiCDC Canal-JSON Protocol > Definitions of message formats > DDL Event | TiCDC Canal-JSON Protocol > Definitions of message formats > DML Event | TiCDC Canal-JSON Protocol > Definitions of message formats > WATERMARK Event | TiCDC Canal-JSON Protocol > Definitions of message formats > Data parsing on the consumer side`
- Source Line Ranges: `5-176`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `shared`, `tidb`
- Topic Tags: `canal-json`, `mq-sink`, `sink-uri`, `ddl-event`, `dml-event`, `watermark-event`, `tidb-extension`, `consumer-parsing`, `committs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0067_24e36da07c`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-canal-json.md#ticdc-canal-json-protocol`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `92bcdd712ec4077e7d6139e07c13a0d8ecb94b8b47b43dc92c67b378fb2cba98`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-canal-json#ticdc-canal-json-protocol
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-canal-json.md

## Retrieval Guidance

- Use When: Use this chunk when identifying TiCDC Canal-JSON MQ sink behavior, the `_tidb` extension, DDL/DML/WATERMARK event formats, or consumer-side event parsing rules.
- Retrieval Keywords: TiCDC Canal-JSON Protocol, sink-uri, protocol=canal-json, enable-tidb-extension, _tidb, commitTs, watermarkTs, TIDB_WATERMARK, DDL Event, DML Event, WATERMARK Event, Data parsing on the consumer side, At Least Once semantics, cdc cli changefeed create
- Follow-up Guidance: It also explains that consumers first check `isDdl`, and when `isDdl` is `false`, check whether `type` is `TIDB_WATERMARK` to distinguish WATERMARK from DML events.
- Classification Note: The classification is data_pipeline because the content defines TiCDC message-queue sink event protocols and downstream consumer parsing for changefeed data.

## Official Source Content

# TiCDC Canal-JSON Protocol

Canal-JSON is a data exchange format protocol defined by [Alibaba Canal](https://github.com/alibaba/canal). In this document, you can learn how Canal-JSON data formats are implemented in TiCDC, including the TiDB extension field, the definitions of the Canal-JSON data formats, and comparison with the official Canal.
## Use Canal-JSON

When using Message Queue (MQ) as the downstream Sink, you can specify Canal-JSON in `sink-uri`. TiCDC wraps and constructs Canal-JSON messages with Event as the basic unit, and sends TiDB data change Events to the downstream.

There are three types of Events:

* DDL Event: Represents a DDL change record. It is sent after an upstream DDL statement is successfully executed. The DDL Event is sent to the MQ Partition with the index being 0.
* DML Event: Represents a row data change record. This type of Event is sent when a row change occurs. It contains the information about the row after the change occurs.
* WATERMARK Event: Represents a special time point. It indicates that the Events received before this point is complete. It applies only to the TiDB extension field and takes effect when you set `enable-tidb-extension` to `true` in `sink-uri`.

The following is an example of using `Canal-JSON`:

```shell
cdc cli changefeed create --server=http://127.0.0.1:8300 --changefeed-id="kafka-canal-json" --sink-uri="kafka://127.0.0.1:9092/topic-name?kafka-version=2.4.0&protocol=canal-json"
```
## TiDB extension field

The Canal-JSON protocol is originally designed for MySQL. It does not contain important fields such as the TiDB-specific unique identifier for the CommitTS transaction. To solve this problem, TiCDC appends a TiDB extension field to the Canal-JSON protocol format. After you set `enable-tidb-extension` to `true` (`false` by default) in `sink-uri`, TiCDC behaves as follows when generating Canal-JSON messages:

* TiCDC sends DML Event and DDL Event messages that contain a field named `_tidb`.
* TiCDC sends WATERMARK Event messages.

The following is an example:

```shell
cdc cli changefeed create --server=http://127.0.0.1:8300 --changefeed-id="kafka-canal-json-enable-tidb-extension" --sink-uri="kafka://127.0.0.1:9092/topic-name?kafka-version=2.4.0&protocol=canal-json&enable-tidb-extension=true"
```
## Definitions of message formats

This section describes the formats of DDL Event, DML Event and WATERMARK Event, and how the data is parsed on the consumer side.
### DDL Event

TiCDC encodes a DDL Event into the following Canal-JSON format.

```json
{
    "id": 0,
    "database": "test",
    "table": "",
    "pkNames": null,
    "isDdl": true,
    "type": "QUERY",
    "es": 1639633094670,
    "ts": 1639633095489,
    "sql": "drop database if exists test",
    "sqlType": null,
    "mysqlType": null,
    "data": null,
    "old": null,
    "_tidb": {     // TiDB extension field
        "commitTs": 429918007904436226  // A TiDB TSO timestamp
    }
}
```

The fields are explained as follows.

| Field      | Type   | Description                                                             |
|:----------|:-------|:-------------------------------------------------------------------------|
| id        | Number | The default value is 0 in TiCDC.                                         |
| database  | String | The name of the database where the row is located                        |
| table     | String | The name of the table where the row is located                           |
| pkNames   | Array  | The names of all the columns that make up the primary key                |
| isDdl     | Bool   | Whether the message is a DDL event                                       |
| type      | String | Event types defined by Canal-JSON                                        |
| es        | Number | 13-bit (millisecond) timestamp when the event that generated the message happened     |
| ts        | Number | 13-bit (millisecond) timestamp when TiCDC generated the message                       |
| sql       | String | When isDdl is `true`, records the corresponding DDL statement                           |
| sqlType   | Object | When isDdl is `false`, records how the data type of each column is represented in Java  |
| mysqlType | object | When isDdl is `false`, records how the data type of each column is represented in MySQL |
| data      | Object | When isDdl is `false`, records the name of each column and its data value       |
| old       | Object | Only if the message is generated by an update Event, records the name of each column and the data value before the update |
| _tidb     | Object | TiDB extension field. It exists only if you set `enable-tidb-extension` to `true`. The value of `commitTs` is the TSO of the transaction that caused the row to change. |
### DML Event

TiCDC encodes a row of DML data change event as follows:

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
        "c_bigint": -5,
        "c_int": 4,
        "c_mediumint": 4,
        "c_smallint": 5,
        "c_tinyint": -6,
        "id": 4
    },
    "mysqlType": {
        "c_bigint": "bigint",
        "c_int": "int",
        "c_mediumint": "mediumint",
        "c_smallint": "smallint",
        "c_tinyint": "tinyint",
        "id": "int"
    },
    "data": [
        {
            "c_bigint": "9223372036854775807",
            "c_int": "2147483647",
            "c_mediumint": "8388607",
            "c_smallint": "32767",
            "c_tinyint": "127",
            "id": "2"
        }
    ],
    "old": null,
    "_tidb": {     // TiDB extension field
        "commitTs": 429918007904436226  // A TiDB TSO timestamp
    }
}
```
### WATERMARK Event

TiCDC sends a WATERMARK Event only when you set `enable-tidb-extension` to `true`. The value of the `type` field is `TIDB_WATERMARK`. The Event contains the `_tidb` field, and the field contains only one parameter `watermarkTs`. The value of `watermarkTs` is the TSO recorded when the Event is sent.

When you receive an Event of this type, all Events with `commitTs` less than `watermarkTs` have been sent. Because TiCDC provides the "At Least Once" semantics, data might be sent repeatedly. If a subsequent Event with `commitTs` less than `watermarkTs` is received, you can safely ignore this Event.

The following is an example of the WATERMARK Event.

```json
{
    "id": 0,
    "database": "",
    "table": "",
    "pkNames": null,
    "isDdl": false,
    "type": "TIDB_WATERMARK",
    "es": 1640007049196,
    "ts": 1640007050284,
    "sql": "",
    "sqlType": null,
    "mysqlType": null,
    "data": null,
    "old": null,
    "_tidb": {     // TiDB extension field
        "watermarkTs": 429918007904436226  // A TiDB TSO timestamp
    }
}
```
### Data parsing on the consumer side

As you can see from the example above, Canal-JSON has a unified data format, with different field filling rules for different Event types. Consumers can parse data in this JSON format using a unified method, and then determine the Event type by checking the field values:

* When `isDdl` is `true`, the message contains a DDL Event.
* When `isDdl` is `false`, you need to further check the `type` field. If `type` is `TIDB_WATERMARK`, it is a WATERMARK Event; otherwise, it is a DML Event.
