# TiDB 5.1 release overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.0.md`
- Source Title: `TiDB 5.1 Release Notes`
- Source Heading Path: `TiDB 5.1 Release Notes | TiDB 5.1 Release Notes > Compatibility changes | TiDB 5.1 Release Notes > Compatibility changes > System variables | TiDB 5.1 Release Notes > Compatibility changes > Configuration file parameters | TiDB 5.1 Release Notes > Compatibility changes > Others | TiDB 5.1 Release Notes > New features`
- Source Line Ranges: `5-71`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `ticdc`, `tiflash`, `sql`
- Topic Tags: `release-notes`, `compatibility`, `system-variables`, `configuration-parameters`, `upgrade`, `deprecated`, `experimental`, `mpp`, `sem`, `stale-read`, `cte`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0220_9dc361c8f2`
- Source ID: `tidb-docs-8.1:releases/release-5.1.0.md#tidb-5-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `83fff963664dd88b3aaa7b3e417decbcbbdeeda56521a1aa2ee8c3df381a1e3d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.0#tidb-5-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.1.0 release overview details, compatibility changes, newly added system variables or configuration parameters, upgrade caveats, deprecated items, or new features such as CTE, Stale Read, MPP, SEM, Lock View, and TiKV write rate limiter.
- Retrieval Keywords: TiDB 5.1 Release Notes, TiDB version 5.1.0, Compatibility changes, System variables, Configuration file parameters, cte_max_recursion_depth, init_connect, tidb_analyze_version, tidb_enable_enhanced_security, tidb_enforce_mpp, tidb_partition_prune_mode, security.enable-sem, performance.committer-concurrency, performance.tcp-no-delay, performance.enforce-mpp, pessimistic-txn.deadlock-history-capacity, INFORMATION_SCHEMA.DEADLOCKS, abort-on-panic, hibernate-regions, old-value-cache-memory-quota, sink-memory-quota, incremental-scan-threads, incremental-scan-concurrency, soft-pending-compaction-bytes-limit, storage.io-rate-limit, resolved-ts.enable, resolved-ts.advance-ts-interval, resolved-ts.scan-lock-pool-size, feedback-probability, panic in the recoverable goroutine, function READ ONLY has only noop implementation, tidb_enable_noop_functions, TiDB Binlog rolling upgrade, clustered indexes, alter table ... modify column, alter table ... change column, TiFlash replicas for system tables, cdc cli changefeed --sort-dir, cdc server --sort-dir, Common Table Expression, Stale Read, Security Enhanced Mode, SEM, MPP mode, Lock View
- Follow-up Guidance: The source also points readers upgrading from an earlier version to check the release notes of all intermediate versions for additional compatibility change notes.
- Classification Note: This chunk is classified as a release note because it summarizes TiDB 5.1.0 new features, compatibility changes in system variables and configuration items, and upgrade-related notes from the official release content.

## Official Source Content

# TiDB 5.1 Release Notes

Release date: June 24, 2021

TiDB version: 5.1.0

In v5.1, the key new features or improvements are as follows:

- Support the Common Table Expression (CTE) feature of MySQL 8.0 to improve the readability and execution efficiency of SQL statements.
- Support changing column types online to improve code development flexibility.
- Introduce a new statistics type to improve query stability, which is enabled as an experimental feature by default.
- Support the dynamic privilege feature of MySQL 8.0 to implement more fine-grained control over certain operations.
- Support directly reading data from the local replica using the Stale Read feature to reduce read latency and improve query performance (Experimental).
- Add the Lock View feature to facilitate database administrators (DBAs) to observe transaction locking events and troubleshoot deadlock problems (Experimental).
- Add TiKV write rate limiter for background tasks to ensure that the latency of read and write requests is stable.
## Compatibility changes

> **Note:**
>
> When upgrading from an earlier TiDB version to v5.1, if you want to know the compatibility change notes of all intermediate versions, you can check the [Release Notes](https://docs.pingcap.com/tidb/stable/releases/release-notes) for the corresponding version.
### System variables

| Variable name   | Change type   | Description   |
|:----------|:-----------|:-----------|
| [`cte_max_recursion_depth`](https://docs.pingcap.com/tidb/stable/system-variables#cte_max_recursion_depth)  | Newly added | Controls the maximum recursion depth in Common Table Expressions. |
| [`init_connect`](https://docs.pingcap.com/tidb/stable/system-variables#init_connect)  | Newly added | Controls the initial connection to a TiDB server. |
| [`tidb_analyze_version`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_version-new-in-v510)  | Newly added | Controls how TiDB collects statistics. The default value of this variable is `2`. This is an experimental feature. |
| [`tidb_enable_enhanced_security`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_enhanced_security) | Newly added | Indicates whether the TiDB server you are connected to has the Security Enhanced Mode (SEM) enabled. This variable setting cannot be changed without restarting the TiDB server. |
| [`tidb_enforce_mpp`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enforce_mpp-new-in-v51) | Newly added | Controls whether to ignore the optimizer's cost estimation and to forcibly use the MPP mode for query execution. The data type of this variable is `BOOL` and the default value is `false`. |
| [`tidb_partition_prune_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_partition_prune_mode-new-in-v51) | Newly added | Specifies whether to enable dynamic pruning mode for partitioned tables. This feature is experimental. The default value of this variable is `static`, which means the dynamic pruning mode for partitioned tables is disabled by default.  |
### Configuration file parameters

| Configuration file | Configuration item | Change type   | Description   |
|:----------|:-----------|:-----------|:-----------|
| TiDB configuration file | [`security.enable-sem`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-sem)  | Newly added  | Controls whether to enable the Security Enhanced Mode (SEM). The default value of this configuration item is `false`, which means the SEM is disabled. |
| TiDB configuration file | `performance.committer-concurrency`  | Modified  | Controls the concurrency number for requests related to commit operations in the commit phase of a single transaction. The default value is changed from `16` to `128`. |
| TiDB configuration file | [`performance.tcp-no-delay`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tcp-no-delay)  | Newly added  | Determines whether to enable TCP_NODELAY at the TCP layer. The default value is `true`, which means TCP_NODELAY is enabled. |
| TiDB configuration file | [`performance.enforce-mpp`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enforce-mpp)  | Newly added  | Controls whether TiDB ignores cost estimates of Optimizer at the instance level and enforces the MPP mode. The default value is `false`. This configuration item controls the initial value of the system variable [`tidb_enforce_mpp`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enforce_mpp-new-in-v51). |
| TiDB configuration file | [`pessimistic-txn.deadlock-history-capacity`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#deadlock-history-capacity)  | Newly added  | Sets the maximum number of deadlock events that can be recorded in the [`INFORMATION_SCHEMA.DEADLOCKS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-deadlocks) table of a single TiDB server. The default value is `10`. |
| TiKV configuration file | [`abort-on-panic`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#abort-on-panic)  | Newly added  | Sets whether the `abort` process allows the system to generate core dump files when TiKV panics. The default value is `false`, which means it is not allowed to generate core dump files. |
| TiKV configuration file | [`hibernate-regions`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#hibernate-regions)  | Modified  | The default value is changed from `false` to `true`. If a Region is idle for a long time, it is automatically set as hibernated. |
| TiKV configuration file | [`old-value-cache-memory-quota`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#old-value-cache-memory-quota)  | Newly added  | Sets the upper limit of memory usage by TiCDC old values. The default value is `512MB`. |
| TiKV configuration file | [`sink-memory-quota`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#sink-memory-quota)  | Newly added  | Sets the upper limit of memory usage by TiCDC data change events. The default value is `512MB`. |
| TiKV configuration file | [`incremental-scan-threads`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#incremental-scan-threads)  | Newly added  | Sets the number of threads for the task of incrementally scanning historical data. The default value is `4`, which means there are four threads for the task.  |
| TiKV configuration file | [`incremental-scan-concurrency`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#incremental-scan-concurrency)  | Newly added  | Sets the maximum number of concurrent executions for the tasks of incrementally scanning historical data. The default value is `6`, which means that six tasks can be concurrently executed at most. |
| TiKV configuration file | [`soft-pending-compaction-bytes-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#soft-pending-compaction-bytes-limit)  | Modified  | The soft limit on the pending compaction bytes. The default value is changed from `"64GB"` to `"192GB"`. |
| TiKV configuration file | [`storage.io-rate-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#storageio-rate-limit)  | Newly added  | Controls the I/O rate of TiKV writes. The default value of `storage.io-rate-limit.max-bytes-per-sec` is `"0MB"`. |
| TiKV configuration file | [`resolved-ts.enable`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable)  | Newly added  | Determines whether to maintain the `resolved-ts` for all Region leaders. The default value is `true`. |
| TiKV configuration file | [`resolved-ts.advance-ts-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#advance-ts-interval)  | Newly added  | The interval at which the `resolved-ts` is forwarded. The default value is `"1s"`. You can change the value dynamically. |
| TiKV configuration file | [`resolved-ts.scan-lock-pool-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#scan-lock-pool-size)  | Newly added  | The number of threads that TiKV uses to scan the MVCC (multi-version concurrency control) lock data when initializing the `resolved-ts`. The default value is `2`. |
### Others

- Before the upgrade, check the value of the TiDB configuration [`feedback-probability`](https://docs.pingcap.com/tidb/v5.1/tidb-configuration-file#feedback-probability). If the value is not 0, the "panic in the recoverable goroutine" error will occur after the upgrade, but this error does not affect the upgrade.
- Upgrade the Go compiler version of TiDB from go1.13.7 to go1.16.4, which improves the TiDB performance. If you are a TiDB developer, upgrade your Go compiler version to ensure a smooth compilation.
- Avoid creating tables with clustered indexes in the cluster that uses TiDB Binlog during the TiDB rolling upgrade.
- Avoid executing statements like `alter table ... modify column` or `alter table ... change column` during the TiDB rolling upgrade.
- Since v5.1, setting the replica of system tables, when building TiFlash replicas for each table, is no longer supported. Before upgrading the cluster, you need to clear the relevant system table replicas; otherwise, the upgrade will fail.
- Deprecate the `--sort-dir` parameter in the `cdc cli changefeed` command of TiCDC. Instead, you can set `--sort-dir` in the `cdc server` command. [#1795](https://github.com/pingcap/tiflow/pull/1795)
- After upgrading to TiDB 5.1, if TiDB returns the "function READ ONLY has only noop implementation" error, you can let TiDB ignore this error by setting the value of [`tidb_enable_noop_functions`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_noop_functions-new-in-v40) to `ON`. This is because the `read_only` variable in MySQL does not yet take effect in TiDB (which is a 'noop' behavior in TiDB). Therefore, even if this variable is set in TiDB, you can still write data into the TiDB cluster.
## New features
