# Debezium DML message structure and data type mapping

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-debezium.md`
- Source Title: `TiCDC Debezium Protocol`
- Source Heading Path: `TiCDC Debezium Protocol > Message format definition | TiCDC Debezium Protocol > Message format definition > DML event | TiCDC Debezium Protocol > Message format definition > Data type mapping`
- Source Line Ranges: `26-138`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `message-format`, `dml-events`, `json`, `payload`, `schema`, `field-definitions`, `type-mapping`, `decimal`, `binary-encoding`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0764_94864d9bf0`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-debezium.md#message-format-definition`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b57a31d6646f3bbdbc0879bcc145a9e0a5439c6706e5aaa90f5e15bfbedb4899`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-debezium#message-format-definition
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-debezium.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Debezium DML JSON structure emitted by TiCDC, the meanings of key payload and schema fields, or the documented data type mapping differences.
- Retrieval Keywords: Message format definition, DML event, payload.op, payload.ts_ms, payload.before, payload.after, payload.source.commit_ts, payload.source.db, payload.source.table, schema.fields, connector":"TiCDC, commit_ts, cluster_id, Data type mapping, Debezium data type mapping rules, binary.handling.mode, Base64, BINARY flag, DECIMAL, NUMERIC, float64
- Follow-up Guidance: The source also lists mapping differences for unsupported spatial data types, Base64 string encoding for string-like types with the BINARY flag, and float64 representation for `DECIMAL` and `NUMERIC`.
- Classification Note: This is classified as reference because the content defines the exact Debezium DML message fields and documents data type mapping details.

## Official Source Content

## Message format definition

This section describes the format definition of the DML event output in the Debezium format.
### DML event

TiCDC encodes a DML event in the following format:

```json
{
    "payload":{
        "ts_ms":1707103832957,
        "transaction":null,
        "op":"c",
        "before":null,
        "after":{
            "a":4,
            "b":2
        },
        "source":{
            "version":"2.4.0.Final",
            "connector":"TiCDC",
            "name":"default",
            "ts_ms":1707103832263,
            "snapshot":"false",
            "db":"test",
            "table":"t2",
            "server_id":0,
            "gtid":null,
            "file":"",
            "pos":0,
            "row":0,
            "thread":0,
            "query":null,
            "commit_ts":447507027004751877,
            "cluster_id":"default"
        }
    },
    "schema":{
        "type":"struct",
        "optional":false,
        "name":"default.test.t2.Envelope",
        "version":1,
        "fields":{
            {
                "type":"struct",
                "optional":true,
                "name":"default.test.t2.Value",
                "field":"before",
                "fields":[
                    {
                        "type":"int32",
                        "optional":false,
                        "field":"a"
                    },
                    {
                        "type":"int32",
                        "optional":true,
                        "field":"b"
                    }
                ]
            },
            {
                "type":"struct",
                "optional":true,
                "name":"default.test.t2.Value",
                "field":"after",
                "fields":[
                    {
                        "type":"int32",
                        "optional":false,
                        "field":"a"
                    },
                    {
                        "type":"int32",
                        "optional":true,
                        "field":"b"
                    }
                ]
            },
            {
                "type":"string",
                "optional":false,
                "field":"op"
            },
            ...
        }
    }
}
```

The key fields of the preceding JSON data are explained as follows:

| Field      | Type   | Description                                            |
|:----------|:-------|:-------------------------------------------------------|
| payload.op        | String | The type of the change event. `"c"` indicates an `INSERT` event, `"u"` indicates an `UPDATE` event, and `"d"` indicates a `DELETE` event.  |
| payload.ts_ms     | Number | The timestamp (in milliseconds) when TiCDC generates this message. |
| payload.before    | JSON   | The data value before the change event of a statement. For `"c"` events, the value of the `before` field is `null`.     |
| payload.after     | JSON   | The data value after the change event of a statement. For `"d"` events, the value of the `after` field is `null`.     |
| payload.source.commit_ts     | Number  | The `CommitTs` identifier when TiCDC generates this message.       |
| payload.source.db     | String   | The name of the database where the event occurs.    |
| payload.source.table     | String  |  The name of the table where the event occurs.   |
| schema.fields     | JSON   |  The type information of each field in the payload, including the schema information of the row data before and after the change.   |
### Data type mapping

The data format mapping in the TiCDC Debezium message basically follows the [Debezium data type mapping rules](https://debezium.io/documentation/reference/2.4/connectors/mysql.html#mysql-data-types), which is generally consistent with the native message of the Debezium Connector for MySQL. However, for some data types, the following differences exist between TiCDC Debezium and Debezium Connector messages:

- Currently, TiDB does not support spatial data types, including GEOMETRY, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, MULTIPOLYGON, and GEOMETRYCOLLECTION.

- For string-like data types, including Varchar, String, VarString, TinyBlob, MediumBlob, BLOB, and LongBlob, when the column has the BINARY flag, TiCDC encodes it as a String type after encoding it in Base64; when the column does not have the BINARY flag, TiCDC encodes it directly as a String type. The native Debezium Connector encodes it in different ways according to `binary.handling.mode`.

- For the Decimal data type, including `DECIMAL` and `NUMERIC`, TiCDC uses the float64 type to represent it. The native Debezium Connector encodes it in float32 or float64 according to the different precision of the data type.
