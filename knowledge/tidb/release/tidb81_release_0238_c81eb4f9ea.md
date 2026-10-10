# TiDB 5.2.0 overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.2.0.md`
- Source Title: `TiDB 5.2 Release Notes`
- Source Heading Path: `TiDB 5.2 Release Notes | TiDB 5.2 Release Notes > Compatibility changes | TiDB 5.2 Release Notes > Compatibility changes > System variables | TiDB 5.2 Release Notes > Compatibility changes > Configuration file parameters | TiDB 5.2 Release Notes > Compatibility changes > Others | TiDB 5.2 Release Notes > New features`
- Source Line Ranges: `5-71`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `sql`, `ticdc`, `tiflash`, `dm`
- Topic Tags: `release-notes`, `compatibility`, `system-variables`, `configuration-parameters`, `upgrade`, `deprecation`, `security`, `authentication`, `flow-control`, `statement-summary`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0238_c81eb4f9ea`
- Source ID: `tidb-docs-8.1:releases/release-5.2.0.md#tidb-5-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cc5b34cad4dc1b0a53638d50b344bb708316ed63cfecce56b5653e57ed2d9581`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.2.0#tidb-5-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.2.0 release-note details about compatibility changes, new system variables or configuration parameters, upgrade caveats, deprecations, authentication, Auto TLS, statement summary limits, or TiKV flow control settings.
- Retrieval Keywords: TiDB 5.2.0 release notes, Compatibility changes, default_authentication_plugin, tidb_enable_auto_increment_in_generated, tidb_opt_enable_correlation_adjustment, tidb_opt_limit_push_down_threshold, tidb_stmt_summary_max_stmt_count, tidb_enable_streaming deprecated, pessimistic-txn.deadlock-history-collect-retryable, INFORMATION_SCHEMA.DEADLOCKS, security.auto-tls, stmt-summary.max-stmt-count, experimental.allow-expression-index deprecated, raftstore.cmd-batch, raftstore.inspect-interval, raftstore.max-peer-down-duration, server.raft-client-queue-size, storage.flow-control.enable, storage.flow-control.memtables-threshold, storage.flow-control.l0-files-threshold, storage.flow-control.soft-pending-compaction-bytes-limit, storage.flow-control.hard-pending-compaction-bytes-limit, ServerIsBusy, tidb_evolve_plan_baselines, tidb_multi_statement_mode, feedback-probability, panic in the recoverable goroutine, innodb_default_row_format, caching_sha2_password, Auto TLS
- Follow-up Guidance: The content also points to upgrade-related checks such as tidb_evolve_plan_baselines, feedback-probability, and the security.auto-tls setting before upgrade.
- Classification Note: This is a release-notes chunk summarizing TiDB 5.2.0 compatibility changes and new features across TiDB, TiKV, security, upgrade behavior, and related configuration and system variable updates.

## Official Source Content

# TiDB 5.2 Release Notes

Release date: August 27, 2021

TiDB version: 5.2.0

> **Warning:**
>
> Some known issues are found in this version, and these issues are fixed in new versions. It is recommended that you use the latest 5.2.x version.

In v5.2, the key new features and improvements are as follows:

- Support using several functions in expression indexes to greatly improve query performance
- Improve the accuracy of optimizer cardinality estimation to help to select optimal execution plans
- Announce the general availability (GA) for the Lock View feature to observe transaction locking events and troubleshoot deadlock problems
- Add the TiFlash I/O traffic limit feature to improve the stability of read and write for TiFlash
- TiKV introduces a new flow control mechanism to replace the previous RocksDB write stall mechanism to improve the stability of TiKV flow control
- Simplify the operation and maintenance of Data Migration (DM) to reduce the management cost.
- TiCDC supports HTTP protocol OpenAPI to manage TiCDC tasks. It provides a more user-friendly operation method for both Kubernetes and self-hosted environments. (Experimental feature)
## Compatibility changes

> **Note:**
>
> When upgrading from an earlier TiDB version to v5.2, if you want to know the compatibility change notes of all intermediate versions, you can check the [Release Note](https://docs.pingcap.com/tidb/stable/releases/release-notes) for the corresponding version.
### System variables

| Variable name    |  Change type    |  Description  |
| :---------- | :----------- | :----------- |
| [`default_authentication_plugin`](https://docs.pingcap.com/tidb/stable/system-variables#default_authentication_plugin) | Newly added | Sets the authentication method that the server advertises. The default value is `mysql_native_password`.  |
| [`tidb_enable_auto_increment_in_generated`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_auto_increment_in_generated) | Newly added | Determines whether to include the `AUTO_INCREMENT` columns when creating a generated column or an expression index. The default value is `OFF`.  |
| [`tidb_opt_enable_correlation_adjustment`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_correlation_adjustment) | Newly added | Controls whether the optimizer estimates the number of rows based on column order correlation. The default value is `ON`.  |
| [`tidb_opt_limit_push_down_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_limit_push_down_threshold) | Newly added | Sets the threshold that determines whether to push the Limit or TopN operator down to TiKV. The default value is `100`.  |
| [`tidb_stmt_summary_max_stmt_count`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stmt_summary_max_stmt_count-new-in-v40) | Modified | Sets the maximum number of statements that the statement summary tables store in memory. The default value is changed from `200` to `3000`.  |
| `tidb_enable_streaming` | Deprecated | The system variable `enable-streaming` is deprecated and it is not recommended to use it any more.  |
### Configuration file parameters

| Configuration file    |  Configuration item    |  Change type    |  Description    |
| :---------- | :----------- | :----------- | :----------- |
| TiDB configuration file  | [`pessimistic-txn.deadlock-history-collect-retryable`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#deadlock-history-collect-retryable) |  Newly added  | Controls whether the [`INFORMATION\_SCHEMA.DEADLOCKS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-deadlocks) table collects retryable deadlock error messages or not.  |
| TiDB configuration file  | [`security.auto-tls`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#auto-tls) |  Newly added  | Determines whether to automatically generate the TLS certificates on startup. The default value is `false`.  |
| TiDB configuration file  | `stmt-summary.max-stmt-count` | Modified | Indicates the maximum number of SQL categories allowed to be saved in the statement summary tables. The default value is changed from `200` to `3000`.  |
| TiDB configuration file  | `experimental.allow-expression-index`  | Deprecated | The `allow-expression-index` configuration in the TiDB configuration file is deprecated.  |
| TiKV configuration file  | [`raftstore.cmd-batch`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#cmd-batch)  |  Newly added  | Controls whether to enable batch processing of the requests. When it is enabled, the write performance is significantly improved. The default value is `true`.  |
| TiKV configuration file  | [`raftstore.inspect-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#inspect-interval)  |  Newly added  | At a certain interval, TiKV inspects the latency of the Raftstore component. This configuration item specifies the interval of the inspection. If the latency exceeds this value, this inspection is marked as timeout. The default value is `500ms`.  |
| TiKV configuration file  | [`raftstore.max-peer-down-duration`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#max-peer-down-duration)  | Modified | Indicates the longest inactive duration allowed for a peer. A peer with timeout is marked as `down`, and PD tries to delete it later. The default value is changed from `5m` to `10m`.  |
| TiKV configuration file  | [`server.raft-client-queue-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raft-client-queue-size)  |  Newly added  | Specifies the queue size of the Raft messages in TiKV. The default value is `8192`.  |
| TiKV configuration file  | [`storage.flow-control.enable`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable)  |  Newly added  | Determines whether to enable the flow control mechanism. The default value is `true`.  |
| TiKV configuration file  | [`storage.flow-control.memtables-threshold`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#memtables-threshold)  |  Newly added  | When the number of kvDB memtables reaches this threshold, the flow control mechanism starts to work. The default value is `5`.  |
| TiKV configuration file  | [`storage.flow-control.l0-files-threshold`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#l0-files-threshold)  |  Newly added  | When the number of kvDB L0 files reaches this threshold, the flow control mechanism starts to work. The default value is `9`.  |
| TiKV configuration file  | [`storage.flow-control.soft-pending-compaction-bytes-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#soft-pending-compaction-bytes-limit)  |  Newly added  | When the pending compaction bytes in KvDB reach this threshold, the flow control mechanism starts to reject some write requests and reports the `ServerIsBusy` error. The default value is "192GB".  |
| TiKV configuration file  | [`storage.flow-control.hard-pending-compaction-bytes-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#hard-pending-compaction-bytes-limit)  |  Newly added  | When the pending compaction bytes in KvDB reach this threshold, the flow control mechanism rejects all write requests and reports the `ServerIsBusy` error. The default value is "1024GB".  |
### Others

- Before the upgrade, check whether the value of the [`tidb_evolve_plan_baselines`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_evolve_plan_baselines-new-in-v40) system variable is `ON`. If the value is `ON`, set it to `OFF`; otherwise, the upgrade will fail.
- For TiDB clusters upgraded from v4.0 to v5.2, the default value of [`tidb_multi_statement_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_multi_statement_mode-new-in-v4011) changes from `WARN` to `OFF`.
- Before the upgrade, check the value of the TiDB configuration [`feedback-probability`](https://docs.pingcap.com/tidb/v5.2/tidb-configuration-file#feedback-probability). If the value is not `0`, the "panic in the recoverable goroutine" error will occur after the upgrade, but this error does not affect the upgrade.
- TiDB is now compatible with MySQL 5.7's noop variable `innodb_default_row_format`. Setting this variable has no effect. [#23541](https://github.com/pingcap/tidb/issues/23541)
- Starting from TiDB 5.2, to improve system security, it is recommended (but not mandatory) to encrypt the transport layer for connections from clients. TiDB provides the Auto TLS feature to automatically configure and enable encryption in TiDB. To use the Auto TLS feature, before the TiDB upgrade, set [`security.auto-tls`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#auto-tls) in the TiDB configuration file to `true`.
- Support the `caching_sha2_password` authentication method to make migration from MySQL 8.0 easier and to improve security.
## New features
