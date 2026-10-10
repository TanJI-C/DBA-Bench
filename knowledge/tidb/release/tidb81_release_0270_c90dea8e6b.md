# Compatibility changes for parameters and behavior

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.4.0.md`
- Source Title: `TiDB 5.4 Release Notes`
- Source Heading Path: `TiDB 5.4 Release Notes > Compatibility changes > Configuration file parameters | TiDB 5.4 Release Notes > Compatibility changes > Others`
- Source Line Ranges: `101-142`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `dm`, `ticdc`, `lightning`
- Topic Tags: `compatibility`, `configuration-parameters`, `system-behavior`, `log-configuration`, `plan-cache`, `pitr`, `dm-documentation`, `kafka-sink`, `raft-engine`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0270_c90dea8e6b`
- Source ID: `tidb-docs-8.1:releases/release-5.4.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4730d23a7fe6a2dbcb01dbebd1078fdd38810af12f3e708c52c3060c319c227a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.4.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB 5.4 compatibility changes in configuration parameters, default values, deleted settings, or changed system behavior across TiDB, TiKV, PD, TiFlash, DM, TiCDC, and TiDB Lightning.
- Retrieval Keywords: TiDB 5.4 compatibility changes, stats-load-concurrency, stats-load-queue-size, snap-generator-pool-size, log.file.max-size, log.file.max-days, log.file.max-backups, raft-engine, backup.enable-auto-tune, log-level, log-format, log-file, log-rotation-size, log.level, log.format, log.file.filename, log.enable-timestamp, log-rotation-timespan, allow-remove-leader, raft-msg-flush-interval, PD log.level, profile.default.enable_elastic_threadpool, storage.format_version, logger.count, status.metrics_port, raftstore.apply-pool-size, raftstore.store-pool-size, collation_compatible, max-message-bytes, partition-num, meta-schema-name, task-info-schema-name, incremental-import, information_schema.TIDB_HOT_REGIONS_HISTORY, Plan Cache SQL binding invalidates cached plan, cdclog-based PITR no longer supported, lc_time_names read-only, tidb_store_limit scope GLOBAL
- Follow-up Guidance: The chunk also points to related details in the TiKV configuration file log and raft-engine sections, the DM overview, and Character Set and Collation references mentioned in the release note.
- Classification Note: This is a release-note compatibility summary because the content enumerates newly added, modified, and deleted parameters plus behavior changes introduced in TiDB 5.4.0.

## Official Source Content

### Configuration file parameters

|  Configuration file    |  Configuration |  Change type  | Description    |
| :---------- | :----------- | :----------- | :----------- |
| TiDB | [`stats-load-concurrency`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#stats-load-concurrency-new-in-v540) | Newly added |  Controls the maximum number of columns that the TiDB synchronously loading statistics feature can process concurrently. The default value is `5`.  |
| TiDB | [`stats-load-queue-size`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#stats-load-queue-size-new-in-v540)   | Newly added |  Controls the maximum number of column requests that the TiDB synchronously loading statistics feature can cache. The default value is`1000`.  |
| TiKV | [`snap-generator-pool-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#snap-generator-pool-size-new-in-v540) | Newly added | The size of the `snap-generator` thread pool. The default value is `2`. |
| TiKV | `log.file.max-size`, `log.file.max-days`, `log.file.max-backups` | Newly added  | For details, see [TiKV Configuration File - `log.file`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#logfile-new-in-v540). |
| TiKV | `raft-engine` | Newly added | Includes `enable`, `dir`, `batch-compression-threshold`, `bytes-per-sync`, `target-file-size`, `purge-threshold`, `recovery-mode`, `recovery-read-block-size`, `recovery-read-block-size`, and `recovery-threads`. For details, see [TiKV Configuration File - `raft-engine`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raft-engine).|
| TiKV | [`backup.enable-auto-tune`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-auto-tune-new-in-v540) | Newly added | In v5.3.0, the default value is `false`. Since v5.4.0, the default value is changed to `true`. This parameter controls whether to limit the resources used by backup tasks to reduce the impact on the cluster when the cluster resource utilization is high. In the default configuration, the speed of backup tasks might slow down. |
| TiKV | `log-level`, `log-format`, `log-file`, `log-rotation-size` | Modified | The names of TiKV log parameters are replaced with the names that are consistent with TiDB log parameters, which are `log.level`, `log.format`, `log.file.filename`, and `log.enable-timestamp`. If you only set the old parameters, and their values are set to non-default values, the old parameters remain compatible with the new parameters. If both old and new parameters are set, the new parameters take effect. For details, see [TiKV Configuration File - log](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#log-new-in-v540). |
| TiKV  |  `log-rotation-timespan`  | Deleted |  The timespan between log rotations. After this timespan passes, a log file is rotated, which means a timestamp is appended to the file name of the current log file, and a new log file is created. |
| TiKV | `allow-remove-leader` | Deleted  | Determines whether to allow deleting the main switch. |
| TiKV | `raft-msg-flush-interval` | Deleted | Determines the interval at which Raft messages are sent in batches. The Raft messages are sent in batches at every interval specified by this configuration item. |
| PD | [`log.level`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#level) | Modified | The default value is changed from "INFO" to "info", guaranteed to be case-insensitive. |
| TiFlash | [`profile.default.enable_elastic_threadpool`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) | Newly added  |  Determines whether to enable or disable the elastic thread pool function. Enabling this configuration item can significantly improve TiFlash CPU utilization in high concurrency scenarios. The default value is `false`. |
| TiFlash | [`storage.format_version`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) | Newly added | Specifies the version of DTFile. The default value is `2`, under which hashes are embedded in the data file. You can also set the value to `3`. When it is `3`, the data file contains metadata and token data checksum, and supports multiple hash algorithms. |
| TiFlash | [`logger.count`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) | Modified | The default value is changed to `10`. |
| TiFlash | [`status.metrics_port`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) | Modified | The default value is changed to `8234`. |
| TiFlash | [`raftstore.apply-pool-size`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflash-learnertoml-file) | Newly added | The allowable number of threads in the pool that flushes Raft data to storage. The default value is `4`. |
| TiFlash | [`raftstore.store-pool-size`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflash-learnertoml-file) | Newly added | The allowable number of threads that process Raft, which is the size of the Raftstore thread pool. The default value is `4`. |
| TiDB Data Migration (DM)  | [`collation_compatible`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced) | Newly added | The mode to sync the default collation in `CREATE` SQL statements. The value options are "loose" (by default) and "strict".  |
| TiCDC | `max-message-bytes` | Modified| Change the default value of `max-message-bytes` in Kafka sink to `104857601` (10MB)  |
| TiCDC | `partition-num`     | Modified | Change the default value of `partition-num` in Kafka Sink from `4` to `3`. It makes TiCDC send messages to Kafaka partitions more evenly. |
| TiDB Lightning | `meta-schema-name` | Modified | Specifies the schema name for the metadata in the target TiDB. From v5.4.0, this schema is created only if you have enabled [parallel import](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import) (the corresponding parameter is `tikv-importer.incremental-import = true`). |
| TiDB Lightning | `task-info-schema-name` |  Newly added  | Specifies the name of the database where duplicated data is stored when TiDB Lightning detects conflicts. By default, the value is "lightning_task_info". Specify this parameter only if you have enabled the "duplicate-resolution" feature. |
| TiDB Lightning | `incremental-import` | Newly added | Determines whether to allow importing data to tables where data already exists. The default value is `false`. |
### Others

- An interface is added between TiDB and PD. When you use the `information_schema.TIDB_HOT_REGIONS_HISTORY` system table, TiDB needs to use PD in the corresponding version.
- TiDB Server, PD Server, and TiKV Server start using a unified naming method for the log-related parameters to manage log names, output formats, and the rules for rotation and expiration. For details, see [TiKV configuration file - log](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#log-new-in-v540).
- Since v5.4.0, if you create a SQL binding for an execution plan that has been cached via Plan Cache, the binding invalidates the plan already cached for the corresponding query. The new binding does not affect execution plans cached before v5.4.0.
- In v5.3 and earlier versions, [TiDB Data Migration (DM)](https://docs.pingcap.com/tidb-data-migration/v5.3/) documentation is independent of TiDB documentation. Since v5.4, DM documentation is integrated into TiDB documentation with the same version. You can directly read [DM documentation](https://docs.pingcap.com/tidb/stable/dm/dm-overview) without accessing the DM documentation site.
- Remove the experimental feature of Point-in-time recovery (PITR) along with cdclog. Since v5.4.0, cdclog-based PITR and cdclog are no longer supported.
- Make the behavior of setting system variables to the "DEFAULT" more MySQL-compatible [#29680](https://github.com/pingcap/tidb/pull/29680)
- Set the system variable `lc_time_names` to read-only [#30084](https://github.com/pingcap/tidb/pull/30084)
- Set the scope of `tidb_store_limit` from INSTANCE or GLOBAL to GLOBAL [#30756](https://github.com/pingcap/tidb/pull/30756)
- Forbid converting the integer type column to the time type column when the column contains zero [#25728](https://github.com/pingcap/tidb/pull/25728)
- Fix the issue that no error is reported for the `Inf` or `NAN` value when inserting floating-point values [#30148](https://github.com/pingcap/tidb/pull/30148)
- Fix the issue that the `REPLACE` statement incorrectly changes other rows when the auto ID is out of range [#30301](https://github.com/pingcap/tidb/pull/30301)
