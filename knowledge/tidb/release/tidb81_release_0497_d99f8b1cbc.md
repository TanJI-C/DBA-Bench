# Compatibility changes, behavior changes, and system variables

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.3.0.md`
- Source Title: `TiDB 7.3.0 Release Notes`
- Source Heading Path: `TiDB 7.3.0 Release Notes > Compatibility changes | TiDB 7.3.0 Release Notes > Compatibility changes > Behavior changes | TiDB 7.3.0 Release Notes > Compatibility changes > System variables | TiDB 7.3.0 Release Notes > Compatibility changes > Configuration file parameters`
- Source Line Ranges: `150-189`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `br`, `lightning`, `ticdc`
- Topic Tags: `upgrade-compatibility`, `behavior-changes`, `mpp`, `tiflash`, `full-restore`, `empty-cluster-check`, `deprecated-parameters`, `conflict-strategy`, `changefeed-errors`, `open-protocol`, `system-variables`, `configuration-parameters`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0497_d99f8b1cbc`
- Source ID: `tidb-docs-8.1:releases/release-7.3.0.md#compatibility-changes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `33b53374126a79127cd4ea47c9a9e6afc37b6af7fd8b75139441a0fa4b2cb6d9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.3.0#compatibility-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB 7.3.0 upgrade compatibility changes, behavior changes, and newly added or modified system variables across TiDB, TiFlash, BR, TiDB Lightning, and TiCDC.
- Retrieval Keywords: Compatibility changes, Behavior changes, upgrade from v7.2.0 to v7.3.0, MPP, TiFlash, tidb_allow_mpp, tidb_allow_tiflash_cop, empty cluster check, full data restoration, --filter, tikv-importer.on-duplicate, conflict.strategy, max-error, conflict.threshold, TiCDC, Kafka sink, Avro protocol, force-replicate, delete-only-output-handle-key-columns, changefeed, Open Protocol, UPDATE events only output the changed columns, tidb_opt_enable_mpp_shared_cte_execution, tidb_lock_unchanged_keys, tidb_opt_enable_non_eval_scalar_subquery, tidb_skip_missing_partition_stats, tiflash_replica_read
- Follow-up Guidance: The note says that if upgrading from v7.1.0 or earlier versions to v7.3.0, you might also need to check compatibility changes introduced in intermediate versions.
- Classification Note: This is classified as a release compatibility chunk because it summarizes upgrade-impacting behavior changes and lists the affected system variables and configuration parameter changes in TiDB 7.3.0.

## Official Source Content

## Compatibility changes

> **Note:**
>
> This section provides compatibility changes you need to know when you upgrade from v7.2.0 to the current version (v7.3.0). If you are upgrading from v7.1.0 or earlier versions to the current version, you might also need to check the compatibility changes introduced in intermediate versions.
### Behavior changes

* TiDB

    - MPP is a distributed computing framework provided by the TiFlash engine, which allows data exchange between nodes and provides high-performance, high-throughput SQL algorithms. Compared with other protocols, the MPP protocol is more mature and can provide better task and resource management. Starting from v7.3.0, when TiDB pushes computation tasks to TiFlash, the optimizer only generates execution plans using the MPP protocol by default. If [`tidb_allow_mpp`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_mpp-new-in-v50) is set to `OFF`, queries might return errors after you upgrade TiDB. It is recommended that you check the value of `tidb_allow_mpp` and set it to `ON` before the upgrade. If you still need the optimizer to choose one of the Cop, BatchCop, and MPP protocols for generating execution plans based on cost estimates, you can set the [`tidb_allow_tiflash_cop`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_tiflash_cop-new-in-v730) variable to `ON`.

* Backup & Restore (BR)

    - BR adds an empty cluster check before performing a full data restoration. By default, restoring data to a non-empty cluster is not allowed. If you want to force the restoration, you can use the `--filter` option to specify the corresponding table name to restore data to.

* TiDB Lightning

    - `tikv-importer.on-duplicate` is deprecated and replaced by [`conflict.strategy`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task).
    - The `max-error` parameter, which controls the maximum number of non-fatal errors that TiDB Lightning can tolerate before stopping the migration task, no longer limits import data conflicts. The [`conflict.threshold`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) parameter now controls the maximum number of conflicting records that can be tolerated.

* TiCDC

    - When Kafka sink uses Avro protocol, if the `force-replicate` parameter is set to `true`, TiCDC reports an error when creating a changefeed.
    - Due to incompatibility between `delete-only-output-handle-key-columns` and `force-replicate` parameters, when both parameters are enabled, TiCDC reports an error when creating a changefeed.
    - When the output protocol is Open Protocol, the `UPDATE` events only output the changed columns.
### System variables

| Variable name | Change type | Description |
|--------|------------------------------|------|
| [`tidb_opt_enable_mpp_shared_cte_execution`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_mpp_shared_cte_execution-new-in-v720) | Modified | This system variable takes effect starting from v7.3.0. It controls whether non-recursive Common Table Expressions (CTEs) can be executed in TiFlash MPP. |
| [`tidb_allow_tiflash_cop`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_tiflash_cop-new-in-v730) | Newly added | This system variable is used to select the protocol for generating execution plans when TiDB pushes computation tasks down to TiFlash. |
| [`tidb_lock_unchanged_keys`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_lock_unchanged_keys-new-in-v711-and-v730) | Newly added | This variable is used to control in certain scenarios whether to lock the keys that are involved but not modified in a transaction. |
| [`tidb_opt_enable_non_eval_scalar_subquery`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_non_eval_scalar_subquery-new-in-v730) | Newly added | Controls whether the `EXPLAIN` statement disables the execution of constant subqueries that can be expanded at the optimization stage.  |
| [`tidb_skip_missing_partition_stats`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_skip_missing_partition_stats-new-in-v730) | Newly added | This variable controls the generation of GlobalStats when partition statistics are missing. |
| [`tiflash_replica_read`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_replica_read-new-in-v730) | Newly added | Controls the strategy for selecting TiFlash replicas when a query requires the TiFlash engine. |
### Configuration file parameters
