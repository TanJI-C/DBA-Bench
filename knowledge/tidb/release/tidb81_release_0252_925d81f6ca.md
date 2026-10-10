# TiDB 5.3 overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.0.md`
- Source Title: `TiDB 5.3 Release Notes`
- Source Heading Path: `TiDB 5.3 Release Notes | TiDB 5.3 Release Notes > Compatibility changes | TiDB 5.3 Release Notes > Compatibility changes > System variables | TiDB 5.3 Release Notes > Compatibility changes > Configuration file parameters`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `lightning`, `sql`
- Topic Tags: `release-notes`, `compatibility`, `system-variables`, `configuration-parameters`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0252_925d81f6ca`
- Source ID: `tidb-docs-8.1:releases/release-5.3.0.md#tidb-5-3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cd37dae18c0bcd493dbb3543e4bb029abbceeb823beb5ba598169d9277537771`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.0#tidb-5-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.3.0 release-note compatibility changes to system variables or configuration file parameters across TiDB, TiKV, PD, and TiDB Lightning.
- Retrieval Keywords: TiDB 5.3 Release Notes, Compatibility changes, System variables, Configuration file parameters, tidb_enable_noop_functions, CREATE TEMPORARY TABLE, DROP TEMPORARY TABLE, tidb_enable_pseudo_for_outdated_stats, pseudo-estimate-ratio, tidb_enable_tso_follower_proxy, TSO Follower Proxy, tidb_tso_client_batch_max_wait_time, tidb_tmp_table_max_size, temporary table, prepared-plan-cache.capacity, storage.reserve-space, memory-usage-limit, raftstore.store-io-pool-size, raftstore.raft-write-size-limit, raftstore.raft-msg-flush-interval, raftstore.raft-reject-transfer-leader-duration, log.file.max-days, log.file.max-backups, patrol-region-interval, max-snapshot-count, max-pending-peer-count, meta-schema-name, lightning_metadata
- Follow-up Guidance: The source also points readers upgrading from an earlier version to the Release Notes of intermediate versions for additional compatibility change notes.
- Classification Note: This is a release-notes compatibility chunk because it enumerates modified, newly added, and deleted system variables and configuration items introduced in TiDB 5.3.0.

## Official Source Content

# TiDB 5.3 Release Notes

Release date: November 30, 2021

TiDB version: 5.3.0

In v5.3, the key new features or improvements are as follows:

+ Introduce temporary tables to simplify your application logic and improve performance
+ Support setting attributes for tables and partitions
+ Support creating users with the least privileges on TiDB Dashboard to enhance system security
+ Optimize the timestamp processing flow in TiDB to improve the overall performance
+ Enhance the performance of TiDB Data Migration (DM) so that data is migrated from MySQL to TiDB with lower latency
+ Support parallel import using multiple TiDB Lightning instances to improve the efficiency of full data migration
+ Support saving and restoring the on-site information of a cluster with a single SQL statement, which helps improve the efficiency of troubleshooting issues relating to execution plans
+ Support the continuous profiling experimental feature to improve the observability of database performance
+ Continue optimizing the storage and computing engines to improve the system performance and stability
+ Reduce the write latency of TiKV by separating I/O operations from Raftstore thread pool (disabled by default)
## Compatibility changes

> **Note:**
>
> When upgrading from an earlier TiDB version to v5.3.0, if you want to know the compatibility change notes of all intermediate versions, you can check the [Release Notes](https://docs.pingcap.com/tidb/stable/releases/release-notes) of the corresponding version.
### System variables

|  Variable name    |  Change type    |  Description    |
| :---------- | :----------- | :----------- |
| [`tidb_enable_noop_functions`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_noop_functions-new-in-v40) | Modified |  Temporary tables are now supported by TiDB so `CREATE TEMPORARY TABLE` and `DROP TEMPORARY TABLE` no longer require enabling `tidb_enable_noop_functions`. |
| [`tidb_enable_pseudo_for_outdated_stats`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_pseudo_for_outdated_stats-new-in-v530) | Newly added | Controls the behavior of the optimizer when the statistics on a table expire. The default value is `ON`. When the number of modified rows in the table is greater than 80% of the total rows (This ratio can be adjusted by the configuration [`pseudo-estimate-ratio`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#pseudo-estimate-ratio)), the optimizer considers that the statistics other than the total number of rows are no longer reliable and use pseudo statistics instead. When you set the value as `OFF`, even if the statistics expire, the optimizer still uses them. |
|[`tidb_enable_tso_follower_proxy`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tso_follower_proxy-new-in-v530) | Newly added  | Determines whether to enable or disable the TSO Follower Proxy feature. The default value is `OFF`, which means the TSO Follower Proxy feature is disabled. At this time, TiDB only gets TSO from PD leader. When this feature is enabled, TiDB evenly sends the requests to all PD nodes when acquiring TSO. The PD follower then forwards the TSO requests to reduce the CPU pressure of PD leader. |
|[`tidb_tso_client_batch_max_wait_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_tso_client_batch_max_wait_time-new-in-v530) | Newly added |  Sets the maximum waiting time for a batch saving operation when TiDB requests TSO from PD. The default value is `0`, which means no additional waiting. |
| [`tidb_tmp_table_max_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_tmp_table_max_size-new-in-v530) | Newly added  | Limits the maximum size of a single [temporary table](https://docs.pingcap.com/tidb/stable/temporary-tables). If the temporary table exceeds this size, an error will occur. |
### Configuration file parameters

|  Configuration file    |  Configuration item  | Change type |  Description  |
| :---------- | :----------- | :----------- | :----------- |
| TiDB | [`prepared-plan-cache.capacity`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#capacity)  | Modified | Controls the number of cached statements. The default value is changed from `100` to `1000`.|
| TiKV | [`storage.reserve-space`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#reserve-space) | Modified | Controls space reserved for disk protection when TiKV is started. Starting from v5.3.0, 80% of the reserved space is used as the extra disk space required for operations and maintenance when the disk space is insufficient, and the other 20% is used to store temporary files. |
| TiKV | `memory-usage-limit` | Modified  | This configuration item is new in TiDB v5.3.0 and its value is calculated based on storage.block-cache.capacity. |
| TiKV | [`raftstore.store-io-pool-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#store-io-pool-size-new-in-v530) | Newly added | The allowable number of threads that process Raft I/O tasks, which is the size of the StoreWriter thread pool. When you modify the size of this thread pool, refer to [Performance tuning for TiKV thread pools](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools). |
| TiKV | [`raftstore.raft-write-size-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raft-write-size-limit-new-in-v530) | Newly added | Determines the threshold at which Raft data is written into the disk. If the data size is larger than the value of this configuration item, the data is written to the disk. When the value of `raftstore.store-io-pool-size` is `0`, this configuration item does not take effect. |
| TiKV | `raftstore.raft-msg-flush-interval` | Newly added | Determines the interval at which Raft messages are sent in batches. The Raft messages in batches are sent at every interval specified by this configuration item. When the value of `raftstore.store-io-pool-size` is `0`, this configuration item does not take effect. |
| TiKV | `raftstore.raft-reject-transfer-leader-duration`  | Deleted | Determines the smallest duration that a Leader is transferred to a newly added node. |
| PD | [`log.file.max-days`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-days) | Modified | Controls the maximum number of days that logs are retained for. The default value is changed from `1` to `0`. |
| PD | [`log.file.max-backups`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-backups) | Modified | Controls the maximum number of logs that are retained for. The default value is changed from `7` to `0`.  |
| PD | [`patrol-region-interval`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#patrol-region-interval) | Modified | Controls the running frequency at which replicaChecker checks the health state of a Region. The smaller this value is, the faster replicaChecker runs. Normally, you do not need to adjust this parameter. The default value is changed from `100ms` to `10ms`. |
| PD | [`max-snapshot-count`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-snapshot-count) | Modified | Controls the maximum number of snapshots that a single store receives or sends at the same time. PD schedulers depend on this configuration to prevent the resources used for normal traffic from being preempted. The default value is changed from `3` to `64`. |
| PD | [`max-pending-peer-count`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-pending-peer-count) | Modified | Controls the maximum number of pending peers in a single store. PD schedulers depend on this configuration to prevent too many Regions with outdated logs from being generated on some nodes. The default value is changed from `16` to `64`. |
| TiD Lightning | `meta-schema-name` | Newly added | The schema name where the meta information for each TiDB Lightning instance is stored in the target cluster. The default value is "lightning_metadata". |
