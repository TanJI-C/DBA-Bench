# Delete event old field change from v5.4.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-canal-json.md`
- Source Title: `TiCDC Canal-JSON Protocol`
- Source Heading Path: `TiCDC Canal-JSON Protocol > Changes in TiCDC Canal-JSON > Changes in the `Old` field of the `Delete` events`
- Source Line Ranges: `503-545`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `canal-json`, `delete-events`, `old-field`, `version-changes`, `message-format`, `backward-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0625_16cc04d4cb`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-canal-json.md#changes-in-the-old-field-of-the-delete-events`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e1bfd0322b5c8ba20b84f00c5a850a55eaae4471fa1ab7d284b4bdd85abe02e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-canal-json#changes-in-the-old-field-of-the-delete-events
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-canal-json.md

## Retrieval Guidance

- Use When: Use this when checking TiCDC canal-json message format differences for DELETE events, especially how the `old` field changed from before v5.4.0 to v5.4.0 and later.
- Retrieval Keywords: TiCDC Canal-JSON, DELETE event, Delete events, old field, data field, v5.4.0, old null, before v5.4.0, message format, backward compatibility
- Follow-up Guidance: For v5.4.0 and later, deleted row data can be obtained from the `data` field because the `old` field is `null`.
- Classification Note: The classification is release because the content documents a version-specific behavior change in the canal-json `old` field for `Delete` events starting from v5.4.0.

## Official Source Content

### Changes in the `Old` field of the `Delete` events

From v5.4.0, the `old` field of the `Delete` events has changed.

The following is a `Delete` event message. Before v5.4.0, the `old` field contains the same content as the "data" field. In v5.4.0 and later versions, the `old` field is set to null. You can get the deleted data by using the "data" field.

```
{
    "id": 0,
    "database": "test",
    ...
    "type": "DELETE",
    ...
    "sqlType": {
        ...
    },
    "mysqlType": {
        ...
    },
    "data": [
        {
            "c_bigint": "9223372036854775807",
            "c_int": "0",
            "c_mediumint": "8388607",
            "c_smallint": "32767",
            "c_tinyint": "0",
            "id": "2"
        }
    ],
    "old": null,
    // The following is an example before v5.4.0. The `old` field contains the same content as the "data" field.
    "old": [
        {
            "c_bigint": "9223372036854775807",
            "c_int": "0",
            "c_mediumint": "8388607",
            "c_smallint": "32767",
            "c_tinyint": "0",
            "id": "2"
        }
    ]
}
```
