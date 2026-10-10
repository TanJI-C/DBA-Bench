# Compatibility changes for system variables and configuration parameters

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.2.0.md`
- Source Title: `TiDB 7.2.0 Release Notes`
- Source Heading Path: `TiDB 7.2.0 Release Notes > Compatibility changes > System variables | TiDB 7.2.0 Release Notes > Compatibility changes > Configuration file parameters`
- Source Line Ranges: `178-208`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `lightning`, `dm`, `ticdc`
- Topic Tags: `compatibility-changes`, `system-variables`, `configuration-parameters`, `defaults`, `new-parameters`, `deprecated-parameters`, `statistics`, `plan-cache`, `analyze`, `check-constraints`, `table-check`, `pipeline-model`, `transaction-logging`, `rocksdb`, `compaction`, `filters`, `ttl`, `data-import`, `character-set`, `memory-usage`, `shard-merge`, `kafka-protocol`, `delete-events`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0491_a2eedeb15f`
- Source ID: `tidb-docs-8.1:releases/release-7.2.0.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4c056c50b016db9919466502c20dc8bd23ed7130d0b860f1f4dfe7b881556316`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.2.0#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB 7.2.0 compatibility changes for system variables and configuration file parameters across TiDB, TiKV, TiDB Lightning, DM, and TiCDC.
- Retrieval Keywords: TiDB 7.2.0 compatibility changes, system variables, configuration file parameters, last_insert_id, tidb_enable_non_prepared_plan_cache, tidb_remove_orderby_in_subquery, tidb_analyze_skip_column_types, tidb_enable_check_constraint, tidb_enable_fast_table_check, tidb_enable_tiflash_pipeline_model, tidb_expensive_txn_time_threshold, lite-init-stats, force-init-stats, rocksdb.[defaultcf|writecf|lockcf].compaction-guard-min-output-file-size, rocksdb.[defaultcf|writecf|lockcf].optimize-filters-for-memory, rocksdb.[defaultcf|writecf|lockcf].periodic-compaction-seconds, rocksdb.[defaultcf|writecf|lockcf].ribbon-filter-above-level, rocksdb.[defaultcf|writecf|lockcf].ttl, send-kv-pairs, send-kv-size, character-set latin1, strict-optimistic-shard-mode, sink.protocol open-protocol, sink.delete-only-output-handle-key-columns
- Follow-up Guidance: The chunk also states default value changes, newly added parameters, and deprecated parameters, including protocol-specific applicability for some TiCDC settings and analyze-version applicability for tidb_analyze_skip_column_types.
- Classification Note: This is classified as a release chunk because the official content enumerates version-specific compatibility changes in 7.2.0 for system variables and configuration parameters.

## Official Source Content

### System variables

| Variable name | Change type | Description |
|--------|------------------------------|------|
| [`last_insert_id`](https://docs.pingcap.com/tidb/stable/system-variables#last_insert_id) | Modified | Changes the maximum value from `9223372036854775807` to `18446744073709551615` to be consistent with that of MySQL. |
| [`tidb_enable_non_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_non_prepared_plan_cache) | Modified | Changes the default value from `OFF` to `ON` after further tests, meaning that non-prepared execution plan cache is enabled. |
| [`tidb_remove_orderby_in_subquery`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_remove_orderby_in_subquery-new-in-v610) | Modified | Changes the default value from `OFF` to `ON` after further tests, meaning that the optimizer removes the `ORDER BY` clause in a subquery. |
| [`tidb_analyze_skip_column_types`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_skip_column_types-new-in-v720) | Newly added | Controls which types of columns are skipped for statistics collection when executing the `ANALYZE` command to collect statistics. The variable is only applicable for [`tidb_analyze_version = 2`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_version-new-in-v510). When using the syntax of `ANALYZE TABLE t COLUMNS c1, ..., cn`, if the type of a specified column is included in `tidb_analyze_skip_column_types`, the statistics of this column will not be collected. |
| [`tidb_enable_check_constraint`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_check_constraint-new-in-v720) | Newly added | Controls whether to enable `CHECK` constraints. The default value is `OFF`, which means this feature is disabled. |
| [`tidb_enable_fast_table_check`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_fast_table_check-new-in-v720) | Newly added | Controls whether to use a checksum-based approach to quickly check the consistency of data and indexes in a table. The default value is `ON`, which means this feature is enabled. |
| [`tidb_enable_tiflash_pipeline_model`](https://docs-archive.pingcap.com/tidb/v7.2/system-variables#tidb_enable_tiflash_pipeline_model-new-in-v720) | Newly added | Controls whether to enable the new execution model of TiFlash, the [pipeline model](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-pipeline-model). The default value is `OFF`, which means the pipeline model is disabled. |
| [`tidb_expensive_txn_time_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_expensive_txn_time_threshold-new-in-v720) | Newly added | Controls the threshold for logging expensive transactions, which is 600 seconds by default. When the duration of a transaction exceeds the threshold, and the transaction is neither committed nor rolled back, it is considered an expensive transaction and will be logged. |
### Configuration file parameters

| Configuration file | Configuration parameter | Change type | Description |
| -------- | -------- | -------- | -------- |
| TiDB | [`lite-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#lite-init-stats-new-in-v710) | Modified | Changes the default value from `false` to `true` after further tests, meaning that TiDB uses lightweight statistics initialization by default during TiDB startup to improve the initialization efficiency. |
| TiDB | [`force-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#force-init-stats-new-in-v657-and-v710) | Modified | Changes the default value from `false` to `true` to align with [`lite-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#lite-init-stats-new-in-v710), meaning that TiDB waits for statistics initialization to finish before providing services during TiDB startup. |
| TiKV | [<code>rocksdb.\[defaultcf\|writecf\|lockcf\].compaction-guard-min-output-file-size</code>](/tikv-configuration-file.md#compaction-guard-min-output-file-size) | Modified | Changes the default value from `"8MB"` to `"1MB"` to reduce the data volume of compaction tasks in RocksDB. |
| TiKV | [<code>rocksdb.\[defaultcf\|writecf\|lockcf\].optimize-filters-for-memory</code>](/tikv-configuration-file.md#optimize-filters-for-memory-new-in-v720) | Newly added | Controls whether to generate Bloom/Ribbon filters that minimize memory internal fragmentation. |
| TiKV | [<code>rocksdb.\[defaultcf\|writecf\|lockcf\].periodic-compaction-seconds</code>](/tikv-configuration-file.md#periodic-compaction-seconds-new-in-v720) | Newly added | Controls the time interval for periodic compaction. SST files with updates older than this value will be selected for compaction and rewritten to the same level where these SST files originally reside. |
| TiKV | [<code>rocksdb.\[defaultcf\|writecf\|lockcf\].ribbon-filter-above-level</code>](/tikv-configuration-file.md#ribbon-filter-above-level-new-in-v720) | Newly added | Controls whether to use Ribbon filters for levels greater than or equal to this value and use non-block-based bloom filters for levels less than this value. |
| TiKV | [<code>rocksdb.\[defaultcf\|writecf\|lockcf\].ttl</code>](/tikv-configuration-file.md#ttl-new-in-v720) | Newly added | SST files with updates older than the TTL will be automatically selected for compaction. |
| TiDB Lightning | `send-kv-pairs` | Deprecated | Starting from v7.2.0, the parameter `send-kv-pairs` is deprecated. You can use [`send-kv-size`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) to control the maximum size of one request when sending data to TiKV in physical import mode. |
| TiDB Lightning | [`character-set`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) | Modified | Introduces a new value option `latin1` for the supported character sets of data import. You can use this option to import source files with the Latin-1 character set. |
| TiDB Lightning | [`send-kv-size`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) | Newly added | Specify the maximum size of one request when sending data to TiKV in physical import mode. When the size of key-value pairs reaches the specified threshold, TiDB Lightning will immediately send them to TiKV. This avoids the OOM problems caused by TiDB Lightning nodes accumulating too many key-value pairs in memory when importing large wide tables. By adjusting this parameter, you can find a balance between memory usage and import speed, improving the stability and efficiency of the import process. |
| Data Migration | [`strict-optimistic-shard-mode`](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-optimistic) | Newly added | This configuration item is used to be compatible with the DDL shard merge behavior in TiDB Data Migration v2.0. You can enable this configuration item in optimistic mode. After this is enabled, the replication task will be interrupted when it encounters a Type 2 DDL statement. In scenarios where there are dependencies between DDL changes in multiple tables, a timely interruption can be made. You need to manually process the DDL statements of each table before resuming the replication task to ensure data consistency between the upstream and the downstream. |
| TiCDC | [`sink.protocol`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Modified | Introduces a new value option `"open-protocol"` when the downstream is Kafka. Specifies the protocol format used for encoding messages. |
| TiCDC | [`sink.delete-only-output-handle-key-columns`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Newly added | Specifies the output of DELETE events. This parameter is valid only for `"canal-json"` and `"open-protocol"` protocols. The default value is `false`, which means outputting all columns. When you set it to `true`, only primary key columns or unique index columns are output. |
