# Compatibility changes for configuration parameters and related behavior

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.4.0.md`
- Source Title: `TiDB 6.4.0 Release Notes`
- Source Heading Path: `TiDB 6.4.0 Release Notes > Compatibility changes > Configuration file parameters | TiDB 6.4.0 Release Notes > Compatibility changes > Others`
- Source Line Ranges: `307-332`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `dm`, `ticdc`, `br`, `lightning`, `dumpling`
- Topic Tags: `compatibility`, `configuration-parameters`, `system-variables`, `upgrade-impact`, `deprecation`, `default-values`, `restore-behavior`, `import-behavior`, `privileges`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0358_5f6b09c0b6`
- Source ID: `tidb-docs-8.1:releases/release-6.4.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9f773acab5d0a35ee42ccb4ea92aee29b23b2d247a116f83cf9eacb1cf2e1de`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.4.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when identifying TiDB 6.4.0 compatibility changes in configuration parameters, default values, system table restore behavior, Lightning import behavior, or TiCDC privilege requirements after upgrade.
- Retrieval Keywords: TiDB 6.4.0 compatibility changes, tidb_memory_usage_alarm_ratio, memory-usage-alarm-ratio deleted, pessimistic-txn.constraint-check-in-place-pessimistic, tidb_constraint_check_in_place_pessimistic, tidb-max-reuse-chunk, tidb-max-reuse-column, cdc.raw-min-ts-outlier-threshold deprecated, causal-ts.alloc-ahead-buffer, causal-ts.renew-batch-max-size, raftstore.apply-yield-write-size, tso-update-physical-interval, data-encryption-method sm4-ctr, routes.route-rule-1.extract-table, routes.route-rule-1.extract-schema, routes.route-rule-1.extract-source, transaction-atomicity default none, mysql.user User_attributes Token_issuer, column count mismatch mysql.user, Dumpling exported files .origin, Lightning unsupported compression formats, SYSTEM_VARIABLES_ADMIN, SUPER, TiCDC Syncpoint feature
- Follow-up Guidance: The source also states that restoring system tables in the `mysql` schema from earlier versions to TiDB v6.4.0 can trigger `column count mismatch` for `mysql.user`, and that TiDB Lightning now fails on files matching Dumpling export naming formats but ending with uncompressed suffixes such as `.origin`.
- Classification Note: This is a release-note compatibility chunk because it enumerates deleted, newly added, deprecated, and modified configuration items and other behavior changes that can affect upgrades to TiDB 6.4.0.

## Official Source Content

### Configuration file parameters

| Configuration file | Configuration parameter | Change type | Description |
| -------- | -------- | -------- | -------- |
| TiDB | `tidb_memory_usage_alarm_ratio` | Deleted | This configuration item is no longer effective. |
| TiDB | `memory-usage-alarm-ratio` | Deleted | Replaced by the system variable [`tidb_memory_usage_alarm_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_memory_usage_alarm_ratio). If this configuration item has been configured in a TiDB version earlier than v6.4.0, it will not take effect after the upgrade. |
| TiDB | [`pessimistic-txn.constraint-check-in-place-pessimistic`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#constraint-check-in-place-pessimistic-new-in-v640) | Newly added | Controls the default value of the system variable [`tidb_constraint_check_in_place_pessimistic`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place_pessimistic-new-in-v630). The default value is `true`. |
| TiDB | [`tidb-max-reuse-chunk`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb-max-reuse-chunk-new-in-v640) | Newly added | Controls the maximum cached chunk objects of chunk allocation. The default value is `64`.|
| TiDB | [`tidb-max-reuse-column`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb-max-reuse-column-new-in-v640) | Newly added | Controls the maximum cached column objects of chunk allocation. The default value is `256`. |
| TiKV | [`cdc.raw-min-ts-outlier-threshold`](https://docs.pingcap.com/tidb/v6.2/tikv-configuration-file#raw-min-ts-outlier-threshold-new-in-v620) | Deprecated | This configuration item is no longer effective. |
| TiKV | [`causal-ts.alloc-ahead-buffer`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#alloc-ahead-buffer-new-in-v640) | Newly added | The pre-allocated TSO cache size (in duration). The default value is `3s`. |
| TiKV | [`causal-ts.renew-batch-max-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#renew-batch-max-size-new-in-v640)| Newly added | Controls the maximum number of TSOs in a timestamp request. The default value is `8192`. |
| TiKV | [`raftstore.apply-yield-write-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#apply-yield-write-size-new-in-v640) | Newly added | Controls the maximum number of bytes that the Apply thread can write for one FSM (Finite-state Machine) in one round of poll. The default value is `32KiB`. This is a soft limit. |
| PD | [`tso-update-physical-interval`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#tso-update-physical-interval) | Newly added | Takes effect starting from v6.4.0 and controls the interval at which PD updates the physical time of TSO. The default value is `50ms`. |
| TiFlash | [`data-encryption-method`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflash-learnertoml-file) | Modified | Introduces a new value option `sm4-ctr`. When this configuration item is set to `sm4-ctr`, data is encrypted using SM4 before being stored. |
| DM | [`routes.route-rule-1.extract-table`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced) | Newly added | Optional. Used in the sharding scenario for extracting the source information of sharded tables. The extracted information will be written to the merged table in the downstream to identify the data source. If this parameter is configured, you need to manually create a merged table in the downstream in advance. |
| DM | [`routes.route-rule-1.extract-schema`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced) | Newly added | Optional. Used in the sharding scenario for extracting the source information of sharded schemas. The extracted information will be written to the merged table in the downstream to identify the data source. If this parameter is configured, you need to manually create a merged table in the downstream in advance. |
| DM | [`routes.route-rule-1.extract-source`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced) | Newly added | Optional. Used in the sharding scenario for extracting the source instance information. The extracted information will be written to the merged table in the downstream to identify the data source. If this parameter is configured, you need to manually create a merged table in the downstream in advance. |
| TiCDC | [`transaction-atomicity`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql#configure-sink-uri-for-mysql-or-tidb) | Modified | Changes the default value from `table` to `none`. This change helps reduce replication latency and OOM risks. In addition, TiCDC now only splits a few transactions (the size of a single transaction exceeds 1024 rows), instead of all transactions. |
### Others

- Starting from v6.4.0, the `mysql.user` table adds two new columns: `User_attributes` and `Token_issuer`. If you [restore system tables in the `mysql` schema](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#restore-tables-in-the-mysql-schema) from backup data of earlier TiDB versions to TiDB v6.4.0, BR will report the `column count mismatch` error for the `mysql.user` table. If you do not restore system tables in the `mysql` schema, this error will not be reported.
- For files whose names match the [format of Dumpling exported files](https://docs.pingcap.com/tidb/stable/dumpling-overview#format-of-exported-files) but end with uncompressed formats (such as `test-schema-create.sql.origin` and `test.table-schema.sql.origin`), the way how TiDB Lightning handles them is changed. Before v6.4.0, if the files to be imported include such files, TiDB Lightning skips importing such files. Starting from v6.4.0, TiDB Lightning assumes that such files use unsupported compression formats, so the import task will fail.
- Starting with v6.4.0, only the changefeed with the `SYSTEM_VARIABLES_ADMIN` or `SUPER` privilege can use the TiCDC Syncpoint feature.
