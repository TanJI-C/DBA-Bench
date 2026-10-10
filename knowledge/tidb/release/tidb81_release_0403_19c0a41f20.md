# Release overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.6.md`
- Source Title: `TiDB 6.5.6 Release Notes`
- Source Heading Path: `TiDB 6.5.6 Release Notes | TiDB 6.5.6 Release Notes > Compatibility changes`
- Source Line Ranges: `5-25`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `ticdc`
- Topic Tags: `release-notes`, `compatibility`, `system-variables`, `security-enhanced-mode`, `optimizer`, `hash-join`, `changefeed`, `case-sensitivity`, `sql-mode`, `redo`, `compression`, `retry`, `object-storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0403_19c0a41f20`
- Source ID: `tidb-docs-8.1:releases/release-6.5.6.md#tidb-6-5-6-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9122aae3852349bdb21675b3b3d34fb6def48949f7c00fbff0e39c2c68a6e5b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.6#tidb-6-5-6-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.6.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.5.6 compatibility changes involving system variables or TiCDC changefeed configuration defaults and new options.
- Retrieval Keywords: TiDB 6.5.6 Compatibility changes, require_secure_transport, Security Enhanced Mode, SEM, tidb_opt_enable_hash_join, hash join optimizer, TiCDC Changefeed case-sensitive default false, case-insensitive table and database names, sql-mode, encoding-worker-num, flush-worker-num, compression, changefeed-error-stuck-duration, sink.cloud-storage-config, redo module, object storage automatic cleanup
- Follow-up Guidance: The chunk also lists that TiCDC changefeed adds sql-mode, encoding-worker-num, flush-worker-num, compression, changefeed-error-stuck-duration, and sink.cloud-storage-config configuration items.
- Classification Note: This is a release-notes compatibility section because it describes behavior changes and newly introduced system variables and changefeed configuration items in TiDB 6.5.6.

## Official Source Content

# TiDB 6.5.6 Release Notes

Release date: December 7, 2023

TiDB version: 6.5.6

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.5/production-deployment-using-tiup)
## Compatibility changes

- Prohibit setting [`require_secure_transport`](https://docs.pingcap.com/tidb/v6.5/system-variables#require_secure_transport-new-in-v610) to `ON` in Security Enhanced Mode (SEM) to prevent potential connectivity issues for users [#47665](https://github.com/pingcap/tidb/issues/47665) @[tiancaiamao](https://github.com/tiancaiamao)
- Introduce the [`tidb_opt_enable_hash_join`](https://docs.pingcap.com/tidb/v6.5/system-variables#tidb_opt_enable_hash_join-new-in-v656) system variable to control whether the optimizer selects hash joins for tables [#46695](https://github.com/pingcap/tidb/issues/46695) @[coderplay](https://github.com/coderplay)
- After further testing, the default value of the TiCDC Changefeed configuration item [`case-sensitive`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) is changed from `true` to `false`. This means that by default, table and database names in the TiCDC configuration file are case-insensitive [#10047](https://github.com/pingcap/tiflow/issues/10047) @[sdojjy](https://github.com/sdojjy)
- TiCDC Changefeed introduces the following new configuration items:
    - [`sql-mode`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to set the [SQL mode](https://docs.pingcap.com/tidb/v6.5/ticdc-ddl#sql-mode) used by TiCDC to parse DDL statements when TiCDC replicates data [#9876](https://github.com/pingcap/tiflow/issues/9876) @[asddongmen](https://github.com/asddongmen)
    - [`encoding-worker-num`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) and [`flush-worker-num`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to set different concurrency parameters for the redo module based on specifications of different machines [#10048](https://github.com/pingcap/tiflow/issues/10048) @[CharlesCheung96](https://github.com/CharlesCheung96)
    - [`compression`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to configure the compression behavior of redo log files [#10176](https://github.com/pingcap/tiflow/issues/10176) @[sdojjy](https://github.com/sdojjy)
    - [`changefeed-error-stuck-duration`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to set the duration for which the changefeed is allowed to automatically retry when internal errors or exceptions occur [#9875](https://github.com/pingcap/tiflow/issues/9875) @[asddongmen](https://github.com/asddongmen)
    - [`sink.cloud-storage-config`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to set the automatic cleanup of historical data when replicating data to object storage [#10109](https://github.com/pingcap/tiflow/issues/10109) @[CharlesCheung96](https://github.com/CharlesCheung96)
