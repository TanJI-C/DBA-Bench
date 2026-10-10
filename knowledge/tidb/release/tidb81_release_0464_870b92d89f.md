# Release overview and TiCDC compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.3.md`
- Source Title: `TiDB 7.1.3 Release Notes`
- Source Heading Path: `TiDB 7.1.3 Release Notes | TiDB 7.1.3 Release Notes > Compatibility changes`
- Source Line Ranges: `5-22`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `shared`
- Topic Tags: `release-date`, `version`, `compatibility-changes`, `changefeed`, `case-sensitivity`, `sql-mode`, `redo-log`, `compression`, `object-storage`, `concurrency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0464_870b92d89f`
- Source ID: `tidb-docs-8.1:releases/release-7.1.3.md#tidb-7-1-3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2b7ff2af69bb4a310bed8a41bc004736c6a72eddc807a5785f852967995a974c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.3#tidb-7-1-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.3 TiCDC compatibility changes or new changefeed configuration items introduced in this release.
- Retrieval Keywords: TiDB 7.1.3 Release Notes, Compatibility changes, TiCDC Changefeed, case-sensitive, default value changed from true to false, case-insensitive table and database names, sql-mode, TiCDC parse DDL statements, encoding-worker-num, flush-worker-num, redo module concurrency parameters, compression, redo log files, sink.cloud-storage-config, automatic cleanup of historical data, object storage
- Follow-up Guidance: The source also states that TiDB 7.1.3 was released on December 21, 2023.
- Classification Note: This is classified as a release item for TiCDC because the content is in the TiDB 7.1.3 release notes and focuses on TiCDC compatibility changes and changefeed configuration additions.

## Official Source Content

# TiDB 7.1.3 Release Notes

Release date: December 21, 2023

TiDB version: 7.1.3

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.1/production-deployment-using-tiup)
## Compatibility changes

- After further testing, the default value of the TiCDC Changefeed configuration item [`case-sensitive`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) is changed from `true` to `false`. This means that by default, table and database names in the TiCDC configuration file are case-insensitive [#10047](https://github.com/pingcap/tiflow/issues/10047) @[sdojjy](https://github.com/sdojjy)
- TiCDC Changefeed introduces the following new configuration items:
    - [`sql-mode`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to set the [SQL mode](https://docs.pingcap.com/tidb/v7.1/ticdc-ddl#sql-mode) used by TiCDC to parse DDL statements when TiCDC replicates data [#9876](https://github.com/pingcap/tiflow/issues/9876) @[asddongmen](https://github.com/asddongmen)
    - [`encoding-worker-num`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) and [`flush-worker-num`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to set different concurrency parameters for the redo module based on specifications of different machines [#10048](https://github.com/pingcap/tiflow/issues/10048) @[CharlesCheung96](https://github.com/CharlesCheung96)
    - [`compression`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to configure the compression behavior of redo log files [#10176](https://github.com/pingcap/tiflow/issues/10176) @[sdojjy](https://github.com/sdojjy)
    - [`sink.cloud-storage-config`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config): enables you to set the automatic cleanup of historical data when replicating data to object storage [#10109](https://github.com/pingcap/tiflow/issues/10109) @[CharlesCheung96](https://github.com/CharlesCheung96)
