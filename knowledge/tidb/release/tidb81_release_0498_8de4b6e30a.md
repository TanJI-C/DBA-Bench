# Compatibility parameter changes, system table addition, and deprecated features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.3.0.md`
- Source Title: `TiDB 7.3.0 Release Notes`
- Source Heading Path: `TiDB 7.3.0 Release Notes > Compatibility changes > Configuration file parameters | TiDB 7.3.0 Release Notes > Compatibility changes > System tables | TiDB 7.3.0 Release Notes > Deprecated features`
- Source Line Ranges: `190-228`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `lightning`, `br`, `ticdc`
- Topic Tags: `compatibility`, `configuration-parameters`, `system-tables`, `deprecated-features`, `defaults`, `partitioned-raft-kv`, `lightning-conflict-handling`, `kafka-message-size`, `azure-blob`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0498_8de4b6e30a`
- Source ID: `tidb-docs-8.1:releases/release-7.3.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8cbfc45832d0dc63915275a7cb0dafb6d492b8e267c9810e78690475a31a68d2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.3.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when identifying TiDB 7.3.0 compatibility changes for configuration parameters, the new system table, or deprecated features across TiDB, TiKV, TiFlash, TiDB Lightning, BR, and TiCDC.
- Retrieval Keywords: TiDB 7.3.0 compatibility changes, enable-32bits-connection-id, in-mem-slow-query-recent-num, in-mem-slow-query-topn-num, coprocessor.region-bucket-size, raft-engine.format-version, storage.engine="partitioned-raft-kv", raftdb.max-total-wal-size, rocksdb.[defaultcf|writecf|lockcf].compaction-guard-min-output-file-size, rocksdb.[defaultcf|writecf|lockcf].format-version, rocksdb.lockcf.write-buffer-size, rocksdb.max-total-wal-size, rocksdb.stats-dump-period, rocksdb.write-buffer-limit, storage.block-cache.capacity, storage.format_version, tikv-importer.incremental-import, tikv-importer.parallel-import, tikv-importer.on-duplicate, conflict.strategy, conflict.threshold, conflict.max-record-rows, enable-diagnose-logs, azblob.encryption-scope, azblob.encryption-key, large-message-handle-option, sink.csv.binary-encoding-method, mysql.tidb_timers, Fast Analyze deprecated, incremental collection deprecated
- Follow-up Guidance: The content also states that `mysql.tidb_timers` is newly added and that `Fast Analyze` and statistics incremental collection will be deprecated in v7.5.0.
- Classification Note: This is a release-note compatibility summary because the official content lists newly added, modified, deleted, and deprecated items plus a new system table in TiDB 7.3.0.

## Official Source Content

| Configuration file | Configuration parameter | Change type | Description |
| -------- | -------- | -------- | -------- |
| TiDB | [`enable-32bits-connection-id`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-32bits-connection-id-new-in-v730) | Newly added | Controls whether to enable the 32-bit connection ID feature. |
| TiDB | [`in-mem-slow-query-recent-num`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#in-mem-slow-query-recent-num-new-in-v730) | Newly added | Controls the number of recently used slow queries that are cached in memory. |
| TiDB | [`in-mem-slow-query-topn-num`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#in-mem-slow-query-topn-num-new-in-v730) | Newly added | Controls the number of slowest queries that are cached in memory. |
| TiKV | [`coprocessor.region-bucket-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-bucket-size-new-in-v610) | Modified | Changes the default value from `96MiB` to `50MiB`. |
| TiKV | [`raft-engine.format-version`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#format-version-new-in-v630) | Modified | When using Partitioned Raft KV (`storage.engine="partitioned-raft-kv"`), Ribbon filter is used. Therefore, TiKV changes the default value from `2` to `5`. |
| TiKV | [`raftdb.max-total-wal-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#max-total-wal-size-1) | Modified | When using Partitioned Raft KV (`storage.engine="partitioned-raft-kv"`), TiKV skips writing WAL. Therefore, TiKV changes the default value from `"4GB"` to `1`, meaning that WAL is disabled. |
| TiKV | [<code>rocksdb.\[defaultcf\|writecf\|lockcf\].compaction-guard-min-output-file-size</code>](/tikv-configuration-file.md#compaction-guard-min-output-file-size) | Modified | Changes the default value from `"1MB"` to `"8MB"` to resolve the issue that compaction speed cannot keep up with the write speed during large data writes. |
| TiKV | [<code>rocksdb.\[defaultcf\|writecf\|lockcf\].format-version</code>](/tikv-configuration-file.md#format-version-new-in-v620) | Modified | When using Partitioned Raft KV (`storage.engine="partitioned-raft-kv"`), Ribbon filter is used. Therefore, TiKV changes the default value from `2` to `5`. |
| TiKV | [`rocksdb.lockcf.write-buffer-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#write-buffer-size) | Modified | When using Partitioned Raft KV (`storage.engine="partitioned-raft-kv"`), to speed up compaction on lockcf, TiKV changes the default value from `"32MB"` to `"4MB"`. |
| TiKV | [`rocksdb.max-total-wal-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#max-total-wal-size) | Modified | When using Partitioned Raft KV (`storage.engine="partitioned-raft-kv"`), TiKV skips writing WAL. Therefore, TiKV changes the default value from `"4GB"` to `1`, meaning that WAL is disabled. |
| TiKV | [`rocksdb.stats-dump-period`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#stats-dump-period) | Modified | When using Partitioned Raft KV (`storage.engine="partitioned-raft-kv"`), to disable redundant log printing, changes the default value from `"10m"` to `"0"`. |
| TiKV | [`rocksdb.write-buffer-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#write-buffer-limit-new-in-v660) | Modified | To reduce the memory overhead of memtables, when `storage.engine="raft-kv"`, TiKV changes the default value from 25% of the memory of the machine to `0`, which means no limit. When using Partitioned Raft KV (`storage.engine="partitioned-raft-kv"`), TiKV changes the default value from 25% to 20% of the memory of the machine. |
| TiKV | [`storage.block-cache.capacity`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#capacity) | Modified | When using Partitioned Raft KV (`storage.engine="partitioned-raft-kv"`), to compensate for the memory overhead of memtables, TiKV changes the default value from 45% to 30% of the size of total system memory. |
| TiFlash | [`storage.format_version`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration) | Modified | Introduces a new DTFile format `format_version = 5` to reduce the number of physical files by merging smaller files. Note that this format is experimental and not enabled by default. |
| TiDB Lightning  | `tikv-importer.incremental-import` | Deleted | TiDB Lightning parallel import parameter. Because it could easily be mistaken as an incremental import parameter, this parameter is now renamed to `tikv-importer.parallel-import`. If a user passes in the old parameter name, it will be automatically converted to the new one. |
| TiDB Lightning  | `tikv-importer.on-duplicate` | Deprecated | Controls action to do when trying to insert a conflicting record in the logical import mode. Starting from v7.3.0, this parameter is replaced by [`conflict.strategy`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task). |
| TiDB Lightning | [`conflict.max-record-rows`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) | Newly added | The new version of strategy to handle conflicting data. It controls the maximum number of rows in the `conflict_records` table. The default value is 100. |
| TiDB Lightning  | [`conflict.strategy`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) | Newly added | The new version of strategy to handle conflicting data. It includes the following options: "" (TiDB Lightning does not detect and process conflicting data), `error` (terminate the import and report an error if a primary or unique key conflict is detected in the imported data), `replace` (when encountering data with conflicting primary or unique keys, the new data is retained and the old data is overwritten.), `ignore` (when encountering data with conflicting primary or unique keys, the old data is retained and the new data is ignored.). The default value is "", that is, TiDB Lightning does not detect and process conflicting data. |
| TiDB Lightning  | [`conflict.threshold`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) | Newly added | Controls the upper limit of the conflicting data. When `conflict.strategy="error"`, the default value is `0`. When `conflict.strategy="replace"` or `conflict.strategy="ignore"`, you can set it as a maxint. |
| TiDB Lightning  | [`enable-diagnose-logs`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) | Newly added | Controls whether to enable the diagnostic logs. The default value is `false`, that is, only the logs related to the import are output, and the logs of other dependent components are not output. When you set it to `true`, logs from both the import process and other dependent components are output, and GRPC debugging is enabled, which can be used for diagnosis. |
|TiDB Lightning  | [`tikv-importer.parallel-import`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) | Newly added | TiDB Lightning parallel import parameter. It replaces the existing `tikv-importer.incremental-import` parameter, which could be mistaken as an incremental import parameter and misused. |
|BR  | `azblob.encryption-scope` | Newly added | BR provides encryption scope support for Azure Blob Storage. |
|BR  | `azblob.encryption-key` | Newly added | BR provides encryption key support for Azure Blob Storage. |
| TiCDC | [`large-message-handle-option`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#handle-messages-that-exceed-the-kafka-topic-limit) | Newly added | Empty by default, which means that when the message size exceeds the limit of Kafka topic, the changefeed fails. When this configuration is set to `"handle-key-only"`, if the message exceeds the size limit, only the handle key will be sent to reduce the message size; if the reduced message still exceeds the limit, then the changefeed fails. |
| TiCDC | [`sink.csv.binary-encoding-method`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | The encoding method of binary data, which can be `'base64'` or `'hex'`. The default value is `'base64'`. |
### System tables

- Add a new system table `mysql.tidb_timers` to store the metadata of internal timers.
## Deprecated features

* TiDB

    - The [`Fast Analyze`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_fast_analyze) feature (experimental) for statistics will be deprecated in v7.5.0.
    - The [incremental collection](https://docs.pingcap.com/tidb/v7.3/statistics#incremental-collection) feature for statistics will be deprecated in v7.5.0.
