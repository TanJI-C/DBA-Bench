# 6.6.0 configuration file parameter changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Compatibility changes > Configuration file parameters`
- Source Line Ranges: `382-419`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dm`, `ticdc`, `tiflash`, `lightning`, `ecosystem`
- Topic Tags: `compatibility`, `configuration-parameters`, `defaults`, `deleted-settings`, `deprecated-settings`, `new-settings`, `modified-settings`, `telemetry`, `resource-control`, `statement-summary`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0422_96ccd82013`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ff5ad2bb4ca158850b27a57b143062b360d46bbb52b386bab7e76b93fa505358`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when locating TiDB 6.6.0 release-note details about configuration file parameter changes, including deleted, modified, deprecated, and newly added settings across TiDB, TiKV, PD, DM, TiCDC, TiFlash, TiDB Lightning, sync-diff-inspector, and TiSpark.
- Retrieval Keywords: TiDB 6.6.0 configuration file parameters, Compatibility changes configuration file parameters, rocksdb.enable-statistics, raftdb.enable-statistics, storage.block-cache.shared, on-duplicate, enable-telemetry, rocksdb.defaultcf.block-size, rocksdb.writecf.block-size, rocksdb.defaultcf.block-cache-size, rocksdb.writecf.block-cache-size, rocksdb.lockcf.block-cache-size, import-mode, profile.default.max_memory_usage_for_all_queries, consistent.storage, initialize-sql-file, tidb_stmt_summary_enable_persistent, tidb_stmt_summary_file_max_backups, tidb_stmt_summary_file_max_days, tidb_stmt_summary_file_max_size, tidb_stmt_summary_filename, resource-control.enabled, storage.engine, rocksdb.write-buffer-flush-oldest-first, rocksdb.write-buffer-limit, pd-server.enable-gogc-tuner, pd-server.gc-tuner-threshold, pd-server.server-memory-limit-gc-trigger, pd-server.server-memory-limit, scheduler.region-per-span, compress-kv-pairs, checksum-physical, disk-quota-physical, on-duplicate-logical, on-duplicate-physical, sorting-dir-physical, skip-non-existing-table, spark.tispark.replica_read, spark.tispark.replica_read.label
- Follow-up Guidance: The chunk also states the exact change type and description for each parameter, such as default value changes, replacement by new parameters, added value options, and whether a setting is only available when creating a cluster.
- Classification Note: This is classified as a release chunk because it is a TiDB 6.6.0 release-notes table summarizing compatibility-related configuration parameter changes for multiple components.

## Official Source Content

| Configuration file | Configuration parameter | Change type | Description |
| -------- | -------- | -------- | -------- |
| TiKV  | `rocksdb.enable-statistics` | Deleted | This configuration item specifies whether to enable RocksDB statistics. Starting from v6.6.0, this item is deleted. RocksDB statistics are enabled for all clusters by default to help diagnostics. For details, see [#13942](https://github.com/tikv/tikv/pull/13942). |
| TiKV  | `raftdb.enable-statistics` | Deleted | This configuration item specifies whether to enable Raft RocksDB statistics. Starting from v6.6.0, this item is deleted. Raft RocksDB statistics are enabled for all clusters by default to help diagnostics. For details, see [#13942](https://github.com/tikv/tikv/pull/13942). |
| TiKV | `storage.block-cache.shared` | Deleted | Starting from v6.6.0, this configuration item is deleted, and the block cache is enabled by default and cannot be disabled. For details, see [#12936](https://github.com/tikv/tikv/issues/12936). |
| DM | `on-duplicate` |  Deleted | This configuration item controls the methods to resolve conflicts during the full import phase. In v6.6.0, new configuration items `on-duplicate-logical` and `on-duplicate-physical` are introduced to replace `on-duplicate`. |
| TiDB | [`enable-telemetry`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-telemetry-new-in-v402-and-deprecated-in-v810) | Modified | Starting from v6.6.0, the default value changes from `true` to `false`, which means that telemetry is disabled by default in TiDB. |
| TiKV  | [`rocksdb.defaultcf.block-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#block-size) and [`rocksdb.writecf.block-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#block-size)  |  Modified  |   The default values change from `64K` to `32K`.  |
| TiKV | [`rocksdb.defaultcf.block-cache-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#block-cache-size), [`rocksdb.writecf.block-cache-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#block-cache-size), [`rocksdb.lockcf.block-cache-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#block-cache-size) | Deprecated | Starting from v6.6.0, these configuration items are deprecated. For details, see [#12936](https://github.com/tikv/tikv/issues/12936). |
| PD | [`enable-telemetry`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-telemetry) | Modified | Starting from v6.6.0, the default value changes from `true` to `false`, which means that telemetry is disabled by default in TiDB Dashboard. |
| DM | [`import-mode`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full) |  Modified | The possible values of this configuration item are changed from `"sql"` and `"loader"` to `"logical"` and `"physical"`. The default value is `"logical"`, which means using TiDB Lightning's logical import mode to import data. |
| TiFlash |  [`profile.default.max_memory_usage_for_all_queries`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file)  |  Modified  |  Specifies the memory usage limit for the generated intermediate data in all queries. Starting from v6.6.0, the default value changes from `0` to `0.8`, which means the limit is 80% of the total memory. |
| TiCDC  | [`consistent.storage`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql#prerequisites)  |  Modified  | This configuration item specifies the path under which redo log backup is stored. Two more value options are added for `scheme`, GCS, and Azure. |
| TiDB | [`initialize-sql-file`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#initialize-sql-file-new-in-v660) | Newly added | This configuration item specifies the SQL script to be executed when the TiDB cluster is started for the first time. The default value is empty. |
| TiDB | [`tidb_stmt_summary_enable_persistent`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_enable_persistent-new-in-v660) | Newly added | This configuration item controls whether to enable statements summary persistence. The default value is `false`, which means this feature is not enabled by default. |
| TiDB | [`tidb_stmt_summary_file_max_backups`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_file_max_backups-new-in-v660) | Newly added | When statements summary persistence is enabled, this configuration specifies the maximum number of data files that can be persisted. `0` means no limit on the number of files. |
| TiDB | [`tidb_stmt_summary_file_max_days`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_file_max_days-new-in-v660) | Newly added | When statements summary persistence is enabled, this configuration specifies the maximum number of days to keep persistent data files. |
| TiDB | [`tidb_stmt_summary_file_max_size`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_file_max_size-new-in-v660) | Newly added | When statements summary persistence is enabled, this configuration specifies the maximum size of a persistent data file (in MiB). |
| TiDB | [`tidb_stmt_summary_filename`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_filename-new-in-v660) | Newly added | When statements summary persistence is enabled, this configuration specifies the file to which persistent data is written. |
| TiKV | [`resource-control.enabled`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#resource-control) | Newly added | Whether to enable scheduling for user foreground read/write requests according to the Request Unit (RU) of the corresponding resource groups. The default value is `false`, which means to disable scheduling according to the RU of the corresponding resource groups. |
| TiKV | [`storage.engine`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#engine-new-in-v660) | Newly added | This configuration item specifies the type of the storage engine. Value options are `"raft-kv"` and `"partitioned-raft-kv"`. This configuration item can only be specified when creating a cluster and cannot be modified once being specified. |
| TiKV | [`rocksdb.write-buffer-flush-oldest-first`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#write-buffer-flush-oldest-first-new-in-v660) | Newly added | This configuration item specifies the flush strategy used when the memory usage of `memtable` of the current RocksDB reaches the threshold.  |
| TiKV | [`rocksdb.write-buffer-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#write-buffer-limit-new-in-v660) | Newly added | This configuration item specifies the limit on total memory used by `memtable` of all RocksDB instances in a single TiKV. The default value is 25% of the total machine memory.  |
| PD  | [`pd-server.enable-gogc-tuner`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-gogc-tuner-new-in-v660) | Newly added | This configuration item controls whether to enable the GOGC tuner, which is disabled by default. |
| PD  | [`pd-server.gc-tuner-threshold`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#gc-tuner-threshold-new-in-v660) | Newly added | This configuration item specifies the maximum memory threshold ratio for tuning GOGC. The default value is `0.6`. |
| PD  | [`pd-server.server-memory-limit-gc-trigger`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#server-memory-limit-gc-trigger-new-in-v660) | Newly added | This configuration item specifies the threshold ratio at which PD tries to trigger GC. The default value is `0.7`. |
| PD  | [`pd-server.server-memory-limit`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#server-memory-limit-new-in-v660) | Newly added | This configuration item specifies the memory limit ratio for a PD instance. The value `0` means no memory limit. |
| TiCDC | [`scheduler.region-per-span`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | This configuration item controls whether to split a table into multiple replication ranges based on the number of Regions, and these ranges can be replicated by multiple TiCDC nodes. The default value is `50000`. |
| TiDB Lightning | [`compress-kv-pairs`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) | Newly added | This configuration item controls whether to enable compression when sending KV pairs to TiKV in the physical import mode. The default value is empty, meaning that the compression is not enabled. |
| DM | [`checksum-physical`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full) | Newly added | This configuration item controls whether DM performs `ADMIN CHECKSUM TABLE <table>` for each table to verify data integrity after the import. The default value is `"required"`, which performs admin checksum after the import. If checksum fails, DM pauses the task and you need to manually handle the failure. |
| DM | [`disk-quota-physical`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full) | Newly added | This configuration item sets the disk quota. It corresponds to the [`disk-quota` configuration](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#configure-disk-quota-new-in-v620) of TiDB Lightning. |
| DM | [`on-duplicate-logical`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full) | Newly added | This configuration item controls how DM resolves conflicting data in the logical import mode. The default value is `"replace"`, which means using the new data to replace the existing data. |
| DM | [`on-duplicate-physical`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full) | Newly added | This configuration item controls how DM resolves conflicting data in the physical import mode. The default value is `"none"`, which means not resolving conflicting data. `"none"` has the best performance, but might lead to inconsistent data in the downstream database. |
| DM | [`sorting-dir-physical`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full) | Newly added | This configuration item specifies the directory used for local KV sorting in the physical import mode. The default value is the same as the `dir` configuration. |
| sync-diff-inspector | [`skip-non-existing-table`](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview#configuration-file-description) | Newly added | This configuration item controls whether to skip checking upstream and downstream data consistency when tables in the downstream do not exist in the upstream.  |
| TiSpark | [`spark.tispark.replica_read`](https://docs.pingcap.com/tidb/stable/tispark-overview#tispark-configurations) | Newly added | This configuration item controls the type of replicas to be read. The value options are `leader`, `follower`, and `learner`. |
| TiSpark | [`spark.tispark.replica_read.label`](https://docs.pingcap.com/tidb/stable/tispark-overview#tispark-configurations) | Newly added | This configuration item is used to set labels for the target TiKV node. |
