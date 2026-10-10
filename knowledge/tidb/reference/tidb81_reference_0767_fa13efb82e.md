# Create replication task parameter descriptions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-open-api-v2.md`
- Source Title: `TiCDC OpenAPI v2`
- Source Heading Path: `TiCDC OpenAPI v2 > Create a replication task > Parameter descriptions`
- Source Line Ranges: `247-286`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `openapi`, `changefeed`, `replication-task`, `parameters`, `redo-log`, `filter`, `sync-point`, `case-sensitivity`, `gc-safe-point`, `bdr`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0767_fa13efb82e`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-open-api-v2.md#parameter-descriptions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a9daa7a4609439fab3fc86817cff6b05374ebcc8e0731001ff7464ae1584edea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2#parameter-descriptions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-open-api-v2.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiCDC OpenAPI v2 create replication task parameter descriptions, including changefeed options for bidirectional replication, case sensitivity, GC safe point checking, redo log consistency, filter rules, and sync point settings.
- Retrieval Keywords: TiCDC OpenAPI v2 create replication task parameter descriptions, bdr_mode, case_sensitive, check_gc_safe_point, consistent, redo log, enable_sync_point, filter, force_replicate, ignore_ineligible_table, memory_quota, mounter, sink, sync_point_interval, sync_point_retention, flush_interval, level, max_log_size, storage, use_file_backend, encoding_worker_num, flush_worker_num, compression, lz4, flush_concurrency, event_filters, ignore_txn_start_ts, rules, table schema filtering, sync point, GC safe point, bidirectional replication
- Follow-up Guidance: The source also enumerates the nested `consistent` parameters and `filter` parameters, and notes that `filter.event_filters` parameters are described separately.
- Classification Note: This is reference content because it lists parameter names, types, defaults, optionality, and brief descriptions for the TiCDC OpenAPI v2 create replication task request.

## Official Source Content

| Parameter name | Description                                                                                                                                                                                                                                                                                                                     |
| :------------------------ |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `bdr_mode`                | `BOOLEAN` type. Determines whether to enable [bidirectional replication](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-bidirectional-replication). The default value is `false`. (Optional)                                                                                                                                                                   |
| `case_sensitive`          | `BOOLEAN` type. Determines whether to be case-sensitive when filtering table names. Starting from v6.5.6, v7.1.3, and v7.5.0, the default value changes from `true` to `false`. (Optional)                                                                                                                                       |
| `check_gc_safe_point`     | `BOOLEAN` type. Determines whether to check that the start time of the replication task is earlier than the GC time. The default value is `true`. (Optional)                                                                                                                                                                    |
| `consistent`              | The configuration parameters of redo log. (Optional)                                                                                                                                                                                                                                                                            |
| `enable_sync_point`       | `BOOLEAN` type. Determines whether to enable `sync point`. (Optional)                                                                                                                                                                                                                                                           |
| `filter`                  | The configuration parameters of `filter`. (Optional)                                                                                                                                                                                                                                                                            |
| `force_replicate`         | `BOOLEAN` type. The default value is `false`. When you set it to `true`, the replication task forcibly replicates the tables without unique indexes. (Optional)                                                                                                                                                                 |
| `ignore_ineligible_table` | `BOOLEAN` type. The default value is `false`. When you set it to `true`, the replication task ignores the tables that cannot be replicated. (Optional)                                                                                                                                                                          |
| `memory_quota`            | `UINT64` type. The memory quota for the replication task. (Optional)                                                                                                                                                                                                                                                            |
| `mounter`                 | The  configuration parameters of `mounter`. (Optional)                                                                                                                                                                                                                                                                          |
| `sink`                    | The configuration parameters of `sink`. (Optional)                                                                                                                                                                                                                                                                              |
| `sync_point_interval`     | `STRING` type. Note that the returned value is a time in nanosecond of the `UINT64` type. When the `sync point` feature is enabled, this parameter specifies the interval at which Syncpoint aligns the upstream and downstream snapshots. The default value is `10m` and the minimum value is `30s`. (Optional)                |
| `sync_point_retention`    | `STRING` type. Note that the returned value is a time in nanosecond of the `UINT64` type. When the `sync point` feature is enabled, this parameter specifies how long the data is retained by Syncpoint in the downstream table. When this duration is exceeded, the data is cleaned up. The default value is `24h`. (Optional) |

The `consistent` parameters are described as follows:

| Parameter name | Description |
|:-----------------|:---------------------------------------|
| `flush_interval` | `UINT64` type. The interval to flush redo log files. (Optional) |
| `level`          | `STRING` type. The consistency level of the replicated data. (Optional)    |
| `max_log_size`   | `UINT64` type. The maximum value of redo log. (Optional)      |
| `storage`        | `STRING` type. The destination address of the storage. (Optional)            |
| `use_file_backend` | `BOOL` type. Specifies whether to store the redo log in a local file. (Optional) |
| `encoding_worker_num` | `INT` type. The number of encoding and decoding workers in the redo module. (Optional)             |
| `flush_worker_num`    | `INT` type. The number of flushing workers in the redo module. (Optional)             |
| `compression`         | `STRING` type. The behavior to compress redo log files. Available options are `""` and `"lz4"`. The default value is `""`, which means no compression. (Optional) |
| `flush_concurrency`   | `INT` type. The concurrency for uploading a single file. The default value is `1`, which means concurrency is disabled. (Optional)                                     |

The `filter` parameters are described as follows:

| Parameter name | Description |
|:-----------------|:---------------------------------------|
| `event_filters`       | The configuration to filter events. (Optional)  |
| `ignore_txn_start_ts` | `UINT64 ARRAY` type. Specifying this will ignore transactions that specify `start_ts`, such as `[1, 2]`. (Optional)   |
| `rules`               | `STRING ARRAY` type. The rules for table schema filtering, such as `['foo*.*', 'bar*.*']`. For more information, see [Table Filter](https://docs.pingcap.com/tidb/stable/table-filter). (Optional)  |

The `filter.event_filters` parameters are described as follows. For more information, see [Changefeed Log Filters](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-filter).
