# Compatibility changes, configuration parameters, and removed feature

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.2.0.md`
- Source Title: `TiDB 6.2.0 Release Notes`
- Source Heading Path: `TiDB 6.2.0 Release Notes > Compatibility changes > Configuration file parameters | TiDB 6.2.0 Release Notes > Compatibility changes > Others | TiDB 6.2.0 Release Notes > Removed feature`
- Source Line Ranges: `267-325`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `dm`, `lightning`, `pd`, `sql`, `ticdc`, `tidb`, `tiflash`, `tikv`
- Topic Tags: `compatibility`, `configuration-parameters`, `system-variables`, `ddl`, `pitr`, `log-backup`, `tiflash-replica`, `downgrade-limitation`, `dynamic-configuration`, `binary-plan`, `rawkv`, `deprecated-features`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0329_f40dad0305`
- Source ID: `tidb-docs-8.1:releases/release-6.2.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9d9cb308cde20ca173e109066dba4d8b89cfd1a7d3fa764f4d2312dd61ea6533`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.2.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.2.0 compatibility changes, added or deleted configuration parameters, new system tables, DDL or PITR behavior changes, TiFlash downgrade limitations, or the removed RawKV backup and restore feature.
- Retrieval Keywords: TiDB 6.2.0 Release Notes, feedback-probability, query-feedback-limit, server.simplify-metrics, quota.background-cpu-time, quota.background-write-bandwidth, quota.background-read-bandwidth, quota.enable-auto-tune, rocksdb.enable-pipelined-commit, gc-merge-rewrite, log-backup.enable, log-backup.file-size-limit, log-backup.initial-scan-pending-memory-quota, log-backup.max-flush-interval, log-backup.initial-scan-rate-limit, log-backup.num-threads, log-backup.temp-path, rocksdb.defaultcf.format-version, rocksdb.writecf.format-version, rocksdb.lockcf.format-version, replication-mode.dr-auto-sync.wait-async-timeout, replication-mode.dr-auto-sync.wait-sync-timeout, storage.format_version, profiles.default.dt_enable_read_thread, profiles.default.dt_page_gc_threshold, --overwrite-checkpoint-ts, --no-confirm, mode, worker-count, row-error-delay, tikv-importer.store-write-bwlimit, tikv-importer.disk-quota, TiFlash format_version cannot be downgraded from 4 to 3, dt_enable_logical_split, PITR limitations, exchange partition, --with-sys-table=true, ALTER TABLE multiple columns or indexes, split.region-cpu-overload-threshold-ratio, dynamic configuration, binary_plan, information_schema.statements_summary, information_schema.slow_query, SHOW TABLE ... REGIONS, SCHEDULING_CONSTRAINTS, SCHEDULING_STATE, TiKV-CDC, ROLLBACK TO SAVEPOINT, SELECT tidb_version(), INFORMATION_SCHEMA.VARIABLES_INFO, PERFORMANCE_SCHEMA.SESSION_VARIABLES, backing up and restoring RawKV using BR is deprecated
- Follow-up Guidance: The source also points to the TiFlash Upgrade Guide, PITR limitations, dynamic configuration, and TiKV configuration references for more details on the listed items.
- Classification Note: This is a release-note compatibility and feature-change summary for self-managed TiDB 6.2.0 across multiple components, including configuration changes, behavioral differences, and a deprecated feature.

## Official Source Content

### Configuration file parameters

| Configuration file | Configuration | Change type | Description |
| --- | --- | --- | --- |
| TiDB | feedback-probability | Deleted | This configuration is no longer effective and is not recommended. |
| TiDB | query-feedback-limit | Deleted | This configuration is no longer effective and is not recommended. |
| TiKV | [server.simplify-metrics](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#simplify-metrics-new-in-v620) | Newly added | This configuration specifies whether to simplify the returned monitoring metrics. |
| TiKV | [quota.background-cpu-time](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#background-cpu-time-new-in-v620) | Newly added | This configuration specifies the soft limit on the CPU resources used by TiKV background to process read and write requests. |
| TiKV | [quota.background-write-bandwidth](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#background-write-bandwidth-new-in-v620) | Newly added | This configuration specifies the soft limit on the bandwidth with which background transactions write data (not effective currently). |
| TiKV | [quota.background-read-bandwidth](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#background-read-bandwidth-new-in-v620) | Newly added | This configuration specifies the soft limit on the bandwidth with which background transactions and the Coprocessor read data (not effective currently). |
| TiKV | [quota.enable-auto-tune](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-auto-tune-new-in-v620) | Newly added | This configuration specifies whether to enable the auto-tuning of quota. If this configuration item is enabled, TiKV dynamically adjusts the quota for the background requests based on the load of TiKV instances. |
| TiKV | rocksdb.enable-pipelined-commit | Deleted | This configuration is no longer effective. |
| TiKV | gc-merge-rewrite | Deleted | This configuration is no longer effective. |
| TiKV | [log-backup.enable](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-new-in-v620) | Newly added | This configuration controls whether to enable log backup on TiKV. |
| TiKV | [log-backup.file-size-limit](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#file-size-limit-new-in-v620) | Newly added | This configuration specifies the size limit on log backup data. Once this limit is reached, data is automatically flushed to external storage. |
| TiKV | [log-backup.initial-scan-pending-memory-quota](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#initial-scan-pending-memory-quota-new-in-v620) | Newly added | This configuration specifies the quota of cache used for storing incremental scan data. |
| TiKV | [log-backup.max-flush-interval](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#max-flush-interval-new-in-v620) | Newly added | This configuration specifies the maximum interval for writing backup data to external storage in log backup. |
| TiKV | [log-backup.initial-scan-rate-limit](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#initial-scan-rate-limit-new-in-v620) | Newly added | This configuration specifies the rate limit on throughput in an incremental data scan in log backup. |
| TiKV | [log-backup.num-threads](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#num-threads-new-in-v620) | Newly added | This configuration specifies the number of threads used in log backup. |
| TiKV | [log-backup.temp-path](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#temp-path-new-in-v620) | Newly added | This configuration specifies temporary path to which log files are written before being flushed to external storage. |
| TiKV | [rocksdb.defaultcf.format-version](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#format-version-new-in-v620) | Newly added | The format version of SST files. |
| TiKV | [rocksdb.writecf.format-version](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#format-version-new-in-v620) | Newly added | The format version of SST files. |
| TiKV | [rocksdb.lockcf.format-version](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#format-version-new-in-v620) | Newly added | The format version of SST files. |
| PD | replication-mode.dr-auto-sync.wait-async-timeout | Deleted | This configuration does not take effect and is deleted. |
| PD | replication-mode.dr-auto-sync.wait-sync-timeout | Deleted | This configuration does not take effect and is deleted. |
| TiFlash | [`storage.format_version`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) | Modified | The default value of `format_version` changes to `4`, the default format for v6.2.0 and later versions, which reduces write amplification and background task resource consumption. |
| TiFlash | [profiles.default.dt_enable_read_thread](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) | Newly added | This configuration controls whether to use the thread pool to handle read requests from the storage engine. The default value is `false`. |
| TiFlash | [profiles.default.dt_page_gc_threshold](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) | Newly added | This configuration specifies the minimum ratio of valid data in a PageStorage data file. |
| TiCDC | [--overwrite-checkpoint-ts](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed#resume-a-replication-task) | Newly added | This configuration is added to the `cdc cli changefeed resume` sub-command. |
| TiCDC | [--no-confirm](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed#resume-a-replication-task) | Newly added | This configuration is added to the `cdc cli changefeed resume` sub-command.|
| DM | [mode](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced) | Newly added | This configuration is a validator parameter. Optional values are `full`, `fast`, and `none`. The default value is `none`, which does not validate the data. |
| DM | [worker-count](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced) | Newly added | This configuration is a validator parameter and specifies the number of validation workers in the background. The default value is `4`. |
| DM | [row-error-delay](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced) | Newly added | This configuration is a validator parameter. If a row is not validated within the specified time, it will be marked as an error row. The default value is 30m, which means 30 minutes. |
| TiDB Lightning | [tikv-importer.store-write-bwlimit](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) | Newly added | This configuration determines the write bandwidth when TiDB Lightning writes data to each TiKV Store. The default value is `0`, indicating the bandwidth is not limited. |
| TiDB Lightning | [tikv-importer.disk-quota](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#configure-disk-quota-new-in-v620) | Newly added | This configuration limits the storage space used by TiDB Lightning. |
### Others

- TiFlash `format_version` cannot be downgraded from `4` to `3`. For details, see [TiFlash Upgrade Guide](https://docs.pingcap.com/tidb/stable/tiflash-upgrade-guide).
- In v6.2.0 and later versions, it is strongly recommended to keep the default value `false` of `dt_enable_logical_split` and not to change it to `true`. For details, see known issue [#5576](https://github.com/pingcap/tiflash/issues/5576).
- If the backup cluster has a TiFlash replica, after you perform PITR, the restoration cluster does not contain the data in the TiFlash replica. To restore data from the TiFlash replica, you need to manually configure TiFlash replicas. Executing the `exchange partition` DDL statement might result in a failure of PITR. If the upstream database uses TiDB Lightning's physical import mode to import data, the data cannot be backed up in log backup. It is recommended to perform a full backup after the data import. For other compatibility issues of PITR, see [PITR limitations](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview#before-you-use).
- Since TiDB v6.2.0, you can restore table in `mysql` schema by specifying the parameter `--with-sys-table=true` when restoring data.
- When you execute the `ALTER TABLE` statement to add, drop, or modify multiple columns or indexes, TiDB checks table consistency by comparing the table before and after statement execution, regardless of the change in the same DDL statement. The execution order of the DDLs is not fully compatible with MySQL in some scenarios.
- If the TiDB component is v6.2.0 or later, the TiKV component should not be earlier than v6.2.0.
- TiKV adds a configuration item `split.region-cpu-overload-threshold-ratio` that supports [dynamic configuration](https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-dynamically).
- Slow query logs, `information_schema.statements_summary`, and `information_schema.slow_query`can export `binary_plan`, or execution plans encoded in the binary format.
- Two columns are added to the `SHOW TABLE ... REGIONS` statement: `SCHEDULING_CONSTRAINTS` and `SCHEDULING_STATE`, which respectively indicate Region scheduling constraints in Placement in SQL and the current scheduling state.
- Since TiDB v6.2.0, you can capture data changes of RawKV via [TiKV-CDC](https://github.com/tikv/migration/tree/main/cdc).
- When `ROLLBACK TO SAVEPOINT` is used to roll back a transaction to a specified savepoint, MySQL releases the locks held only after the specified savepoint, while in TiDB pessimistic transaction, TiDB does not immediately release the locks held after the specified savepoint. Instead, TiDB releases all locks when the transaction is committed or rolled back.
- Since TiDB v6.2.0, the `SELECT tidb_version()` statement also returns Store type (tikv or unistore).
- TiDB no longer has hidden system variables.
- TiDB v6.2.0 introduces two new system tables:
    - `INFORMATION_SCHEMA.VARIABLES_INFO`: used for viewing information about TiDB system variables.
    - `PERFORMANCE_SCHEMA.SESSION_VARIABLES`: used for viewing information about TiDB session-level system variables.
## Removed feature

Since TiDB v6.2.0, backing up and restoring RawKV using BR is deprecated.
