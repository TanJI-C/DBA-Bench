# Create replication task parameters and example request

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-open-api-v2.md`
- Source Title: `TiCDC OpenAPI v2`
- Source Heading Path: `TiCDC OpenAPI v2 > Create a replication task > Parameter descriptions | TiCDC OpenAPI v2 > Create a replication task > Example`
- Source Line Ranges: `287-386`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tikv`
- Topic Tags: `openapi`, `changefeed`, `replication-task`, `request-parameters`, `sink-config`, `filter-rules`, `mounter`, `dispatchers`, `cloud-storage`, `csv`, `debezium`, `open-protocol`, `example-request`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0768_f08746eb95`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-open-api-v2.md#parameter-descriptions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c86d7973909b3ea4423632a7b3f805ffdd3e876d62097c4fd354004214c69758`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2#parameter-descriptions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-open-api-v2.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiCDC OpenAPI v2 request parameters for creating a replication task, including filter rules, mounter settings, sink configuration, and the example POST request to /api/v2/changefeeds.
- Retrieval Keywords: TiCDC OpenAPI v2 create replication task parameters, POST /api/v2/changefeeds, changefeed_id, sink_uri, ignore_delete_value_expr, ignore_event, ignore_insert_value_expr, ignore_sql, ignore_update_new_value_expr, ignore_update_old_value_expr, matcher, mounter worker_num, sink column_selectors, sink csv delimiter include_commit_ts null quote binary_encoding_method, sink dispatchers default ts index-value table, sink protocol canal-json open-protocol avro debezium simple, schema_registry, transaction_atomicity, only_output_updated_columns, cloud_storage_config, date_separator, terminator, sink.open output_old_value, sink.debezium output_old_value, file_cleanup_cron_spec, output_raw_change_event, blackhole://, 200 OK
- Follow-up Guidance: If the request succeeds, the API returns 200 OK; if it fails, it returns an error message and error code.
- Classification Note: This is reference content because it enumerates request parameter names, types, supported values, and an example API request for creating a TiCDC replication task.

## Official Source Content

| Parameter name | Description |
|:-----------------|:---------------------------------------|
| `ignore_delete_value_expr`     | `STRING ARRAY` type. For example, `"name = 'john'"` means to filter out DELETE DML statements containing the `name = 'john'` condition. (Optional)            |
| `ignore_event`                 | `STRING ARRAY` type. For example, `["insert"]` indicates that the INSERT events are filtered out. (Optional)     |
| `ignore_insert_value_expr`     | `STRING ARRAY` type. For example, `"id >= 100"` means to filter out INSERT DML statements that match the `id >= 100` condition. (Optional)                |
| `ignore_sql`                   | `STRING ARRAY` type. For example, `["^drop", "add column"]` means to filter out DDL statements that start with `DROP` or contain `ADD COLUMN`. (Optional)  |
| `ignore_update_new_value_expr` | `STRING ARRAY` type. For example, `"gender = 'male'"` means to filter out the UPDATE DML statements with the new value `gender = 'male'`. (Optional)          |
| `ignore_update_old_value_expr` | `STRING ARRAY` type. For example, `"age < 18"` means to filter out the UPDATE DML statements with the old value `age < 18`. (Optional)                  |
| `matcher`                      | `STRING ARRAY` type. It works as an allowlist. For example, `["test.worker"]` means that the filter rule applies only to the `worker` table in the `test` database. (Optional)          |

The `mounter` parameter is described as follows:

| Parameter name | Description |
|:-----------------|:---------------------------------------|
| `worker_num` | `INT` type. The number of Mounter threads. Mounter is used to decode the data output from TiKV. The default value is `16`. (Optional)   |

The `sink` parameters are described as follows:

| Parameter name | Description                                                                                                                                                                                                    |
|:-----------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `column_selectors`      | The column selector configuration. (Optional)                                                                                                                                                                  |
| `csv`                   | The CSV configuration. (Optional)                                                                                                                                                                              |
| `date_separator`        | `STRING` type. Indicates the date separator type of the file directory. Value options are `none`, `year`, `month`, and `day`. `none` is the default value and means that the date is not separated. (Optional) |
| `dispatchers`           | An configuration array for event dispatching. (Optional)                                                                                                                                                       |
| `encoder_concurrency`   | `INT` type. The number of encoder threads in the MQ sink. The default value is `16`. (Optional)                                                                                                                |
| `protocol`              | `STRING` type. For MQ sinks, you can specify the protocol format of the message. The following protocols are currently supported: `canal-json`, `open-protocol`, `avro`, `debezium`, and `simple`.               |
| `schema_registry`       | `STRING` type. The schema registry address. (Optional)                                                                                                                                                         |
| `terminator`            | `STRING` type. The terminator is used to separate two data change events. The default value is null, which means `"\r\n"` is used as the terminator. (Optional)                                                |
| `transaction_atomicity` | `STRING` type. The atomicity level of the transaction. (Optional)                                                                                                                                              |
| `only_output_updated_columns` | `BOOLEAN` type. For MQ sinks using the `canal-json` or `open-protocol` protocol, you can specify whether only output the modified columns. The default value is `false`. (Optional) |
| `cloud_storage_config` | The storage sink configuration. (Optional) |
| `open`                        | The Open Protocol configuration. (Optional)                                                                             |
| `debezium`                    | The Debezium Protocol configuration. (Optional)                                                                             |

`sink.column_selectors` is an array. The parameters are described as follows:

| Parameter name | Description |
|:-----------------|:---------------------------------------|
| `columns` | `STRING ARRAY` type. The column array.                 |
| `matcher` | `STRING ARRAY` type. The matcher configuration. It has the same matching syntax as the filter rule does.  |

The `sink.csv` parameters are described as follows:

| Parameter name | Description |
|:-----------------|:---------------------------------------|
| `delimiter`              | `STRING` type. The character used to separate fields in the CSV file. The value must be an ASCII character and defaults to `,`.     |
| `include_commit_ts`      | `BOOLEAN` type. Whether to include commit-ts in CSV rows. The default value is `false`. |
| `null`                   | `STRING` type. The character that is displayed when a CSV column is null. The default value is `\N`. |
| `quote`                  | `STRING` type. The quotation character used to surround fields in the CSV file. If the value is empty, no quotation is used. The default value is `"`. |
| `binary_encoding_method` | `STRING` type. The encoding method of binary data, which can be `"base64"` or `"hex"`. The default value is `"base64"`. |

`sink.dispatchers`: for the sink of MQ type, you can use this parameter to configure the event dispatcher. The following dispatchers are supported: `default`, `ts`, `index-value`, and `table`. The dispatcher rules are as follows:

- `default`: dispatches events in the `table` mode.
- `ts`: uses the commitTs of the row change to create the hash value and dispatch events.
- `index-value`: uses the name and value of the selected HandleKey column to create the hash value and dispatch events.
- `table`: uses the schema name of the table and the table name to create the hash value and dispatch events.

`sink.dispatchers` is an array. The parameters are described as follows:

| Parameter name | Description |
|:-----------------|:---------------------------------------|
| `matcher`   | `STRING ARRAY` type. It has the same matching syntax as the filter rule does. |
| `partition` | `STRING` type. The target partition for dispatching events.    |
| `topic`     | `STRING` type. The target topic for dispatching events.        |

`sink.cloud_storage_config` parameters are described as follows:
| Parameter name | Description |
|:-----------------|:---------------------------------------|
| `worker_count`   | `INT` type. The concurrency for saving data changes to the downstream cloud storage.  |
| `flush_interval`   | `STRING` type. The interval for saving data changes to the downstream cloud storage. |
| `file_size`   | `INT` type. A data change file is saved to the cloud storage when the number of bytes in this file exceeds the value of this parameter. |
| `file_expiration_days`   | `INT` type. The duration to retain files, which takes effect only when `date-separator` is configured as `day`. |
| `file_cleanup_cron_spec`   | `STRING` type. The running cycle of the scheduled cleanup task, compatible with the crontab configuration, with a format of `<Second> <Minute> <Hour> <Day of the month> <Month> <Day of the week (Optional)>`. |
| `flush_concurrency`   | `INT` type. The concurrency for uploading a single file. |
| `output_raw_change_event`   | `BOOLEAN` type. Controls whether to output the original data change event for a non-MySQL sink. |

`sink.open` parameters are described as follows:

| Parameter name     | Description                                                                                                                                                                |
|:-------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `output_old_value` | `BOOLEAN` type. It controls whether to output the value before the row data changes. The default value is `true`. When it is disabled, the UPDATE event does not output the "p" field. |

`sink.debezium` parameters are described as follows:

| Parameter name     | Description                                                                                                                                                                   |
|:-------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `output_old_value` | `BOOLEAN` type. It controls whether to output the value before the row data changes. The default value is true. When it is disabled, the UPDATE event does not output the "before" field. |
### Example

The following request creates a replication task with an ID of `test5` and `sink_uri` of `blackhome://`.

```shell
curl -X POST -H "Content-type: application/json" http://127.0.0.1:8300/api/v2/changefeeds -d '{"changefeed_id":"test5","sink_uri":"blackhole://"}'
```

If the request is successful, `200 OK` is returned. If the request fails, an error message and error code are returned.
