# Compatibility changes and deprecated feature in v6.5.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.0.md`
- Source Title: `TiDB 6.5.0 Release Notes`
- Source Heading Path: `TiDB 6.5.0 Release Notes > Compatibility changes > Configuration file parameters | TiDB 6.5.0 Release Notes > Compatibility changes > Others | TiDB 6.5.0 Release Notes > Deprecated feature`
- Source Line Ranges: `349-375`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `ticdc`, `br`, `sql`
- Topic Tags: `compatibility-changes`, `configuration-parameters`, `system-tables`, `index-acceleration`, `pitr`, `deprecated-features`, `metadata-lock`, `password-policy`, `cdc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0369_1b142fd6bc`
- Source ID: `tidb-docs-8.1:releases/release-6.5.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d9d0a01d5763a02d2ae1615846adc0b1b1b2a6dca047bc6a1c561a2d46543b99`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.5.0 compatibility changes, newly added or deprecated configuration parameters, mysql.user schema changes, index acceleration default behavior, PITR incompatibility notes, or the deprecation of AMEND TRANSACTION.
- Retrieval Keywords: TiDB 6.5.0 compatibility changes, server-memory-quota deprecated, tidb_server_memory_limit, disconnect-on-expired-password, raw-min-ts-outlier-threshold deleted, raft-engine.bytes-per-sync deprecated, cdc.min-ts-interval 200ms, memory-use-ratio PITR log recovery, sink.terminator, sink.date-separator, sink.enable-partition-separator, sink.csv.delimiter, sink.csv.quote, sink.csv.null, sink.csv.include-commit-ts, mysql.user Password_reuse_history, mysql.user Password_reuse_time, index acceleration enabled by default, tidb_ddl_enable_fast_reorg, ALTER TABLE multiple columns or indexes, unique index index acceleration, PITR Point-in-time recovery incompatibility, AMEND TRANSACTION deprecated, Metadata Lock
- Follow-up Guidance: The content points to tidb_server_memory_limit, tidb_ddl_enable_fast_reorg, ALTER TABLE, PITR, and Metadata Lock documentation for related details.
- Classification Note: This is a release-note compatibility and deprecation chunk because it lists configuration file parameter changes, other behavior changes, and a deprecated feature introduced in TiDB 6.5.0.

## Official Source Content

### Configuration file parameters

| Configuration file | Configuration parameter | Change type | Description |
| -------- | -------- | -------- | -------- |
| TiDB | [`server-memory-quota`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#server-memory-quota-new-in-v409) | Deprecated | Starting from v6.5.0, this configuration item is deprecated. Instead, use the system variable [`tidb_server_memory_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit-new-in-v640) to manage memory globally. |
| TiDB | [`disconnect-on-expired-password`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#disconnect-on-expired-password-new-in-v650) | Newly added | Determines whether TiDB disconnects the client connection when the password is expired. The default value is `true`, which means the client connection is disconnected when the password is expired. |
| TiKV | `raw-min-ts-outlier-threshold` | Deleted | This configuration item was deprecated in v6.4.0 and deleted in v6.5.0. |
| TiKV | [`raft-engine.bytes-per-sync`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#bytes-per-sync-2) | Deprecated | Starting from v6.5.0, Raft Engine writes logs to disk directly without buffering. Therefore, this configuration item is deprecated and no longer functional.  |
| TiKV | [`cdc.min-ts-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-ts-interval)  | Modified | To reduce CDC latency, the default value is changed from `"1s"` to `"200ms"`. |
| TiKV | [`memory-use-ratio`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#memory-use-ratio-new-in-v650) | Newly added | Indicates the ratio of available memory to total system memory in PITR log recovery. |
| TiCDC | [`sink.terminator`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | Indicates the row terminator, which is used for separating two data change events. The value is empty by default, which means `\r\n` is used. |
| TiCDC | [`sink.date-separator`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | Indicates the date separator type of the file directory. Value options are `none`, `year`, `month`, and `day`. `none` is the default value and means that the date is not separated. |
| TiCDC | [`sink.enable-partition-separator`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | Specifies whether to use partitions as the separation string. The default value is `false`, which means that partitions in a table are not stored in separate directories. |
| TiCDC | [`sink.csv.delimiter`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | Indicates the delimiter between fields. The value must be an ASCII character and defaults to `,`. |
| TiCDC | [`sink.csv.quote`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | The quotation that surrounds the fields. The default value is `"`. When the value is empty, no quotation is used. |
| TiCDC | [`sink.csv.null`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | Specifies the character displayed when the CSV column is null. The default value is `\N`.|
| TiCDC | [`sink.csv.include-commit-ts`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added| Specifies whether to include commit-ts in CSV rows. The default value is `false`. |
### Others

- Starting from v6.5.0, the `mysql.user` table adds two new columns: `Password_reuse_history` and `Password_reuse_time`.
- Starting from v6.5.0, the [index acceleration](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630) feature is enabled by default. This feature is not fully compatible with [altering multiple columns or indexes in a single `ALTER TABLE` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table). When adding a unique index with the index acceleration, you need to avoid altering other columns or indexes in the same statement. This feature is incompatible with [PITR (Point-in-time recovery)](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) either. When using the index acceleration feature, you need to make sure that no PITR backup task is running in the background; otherwise, unexpected results might occur. For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630).
## Deprecated feature

Starting from v6.5.0, the `AMEND TRANSACTION` mechanism introduced in v4.0.7 is deprecated and replaced by [Metadata Lock](https://docs.pingcap.com/tidb/stable/metadata-lock).
