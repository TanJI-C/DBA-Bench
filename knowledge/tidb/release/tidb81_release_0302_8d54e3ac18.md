# Other compatibility changes and downgrade notes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.0.md`
- Source Title: `TiDB 6.1.0 Release Notes`
- Source Heading Path: `TiDB 6.1.0 Release Notes > Compatibility changes > Others`
- Source Line Ranges: `294-325`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `dashboard`, `dm`, `ticdc`
- Topic Tags: `compatibility`, `prepared-plan-cache`, `analyze-status`, `panic-behavior`, `dynamic-configuration`, `system-variables`, `upgrade`, `downgrade`, `avro`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0302_8d54e3ac18`
- Source ID: `tidb-docs-8.1:releases/release-6.1.0.md#others`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c9ecdef0acc7ff6ffbab5f111a23bd5c9f5b2d294e3878918a52e7219d96b711`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.0#others
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.1.0 other compatibility changes, upgrade behavior for converted configuration items, dynamic TiKV configuration support, or downgrade limitations related to TiCDC.
- Retrieval Keywords: TiDB 6.1.0 others compatibility, Prepared Plan Cache enabled by default, Prepare Execute requests, capacity=100, SHOW ANALYZE STATUS cluster-level tasks, SHOW ANALYZE STATUS instance-level tasks, tidb_analyze_version = 2, Job_info analyze option, damaged SST files TiKV panic 1 hour, dynamic-config modify TiKV configuration dynamically, raftstore.raft-entry-max-size, quota.foreground-cpu-time, quota.foreground-write-bandwidth, quota.foreground-read-bandwidth, quota.max-delay-duration, server.grpc-memory-pool-quota, server.max-grpc-send-msg-len, server.raft-msg-max-batch-size, configuration file parameters converted to system variables, automatic update occurs only once during the upgrade, deprecated configuration items are no longer effective, Dashboard page is removed from DM WebUI, dispatchers.topic cannot be downgraded earlier than v6.1.0, dispatchers.partition cannot be downgraded earlier than v6.1.0, TiCDC Changefeed Avro protocol cannot be downgraded earlier than v6.1.0
- Follow-up Guidance: The chunk explicitly states downgrade restrictions for TiCDC when `dispatchers.topic` and `dispatchers.partition` are enabled and when a Changefeed uses the Avro protocol.
- Classification Note: This is a release-note compatibility chunk because it summarizes behavior changes, upgrade semantics, dynamic configuration support, UI removal, and downgrade notes introduced in TiDB 6.1.0.

## Official Source Content

### Others

* Enable Prepared Plan Cache by default

    Prepared Plan Cache is enabled by default in new clusters to cache the execution plans for `Prepare` / `Execute` requests. In the subsequent execution, query plan optimization can be skipped and thus leads to a performance boost. Upgraded clusters inherit the configuration from the configuration file. New clusters use the new default values, which means Prepared Plan Cache is enabled by default and each session can cache 100 plans at most (`capacity=100`). For the memory consumption of this feature, see [memory management of Prepared Plan Cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#memory-management-of-prepared-plan-cache).

* Prior to TiDB v6.1.0, `SHOW ANALYZE STATUS` shows instance-level tasks and the task records are cleared after TiDB restarts. Since TiDB v6.1.0, `SHOW ANALYZE STATUS` shows cluster-level tasks, and the task records persist after the restart. When `tidb_analyze_version = 2`, the `Job_info` column adds the `analyze option` information.

* Damaged SST files in TiKV might cause the TiKV process to panic. Before TiDB v6.1.0, damaged SST files caused TiKV to panic immediately. Since TiDB v6.1.0, the TiKV process will panic 1 hour after SST files are damaged.

* The following TiKV configuration items support [modifying values dynamically](https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-dynamically):

    * `raftstore.raft-entry-max-size`
    * `quota.foreground-cpu-time`
    * `quota.foreground-write-bandwidth`
    * `quota.foreground-read-bandwidth`
    * `quota.max-delay-duration`
    * `server.grpc-memory-pool-quota`
    * `server.max-grpc-send-msg-len`
    * `server.raft-msg-max-batch-size`

* In v6.1.0, some configuration file parameters are converted to system variables. For v6.1.0 clusters upgraded (including online and offline upgrades ) from earlier versions, note that:

    * If the configuration items specified in the configuration file before the upgrade already exist, TiDB will automatically update the values of the configured items to those of the corresponding system variables during the upgrade process. In this way, after the upgrade, the system behavior does not change thanks to parameter optimization.
    * The automatic update mentioned above occurs only once during the upgrade. After the upgrade, the deprecated configuration items are no longer effective.

* The Dashboard page is removed from DM WebUI.

* When `dispatchers.topic` and `dispatchers.partition` are enabled, TiCDC cannot be downgraded to versions earlier than v6.1.0.

* TiCDC Changefeed using the Avro protocol cannot be downgraded to versions earlier than v6.1.0.
