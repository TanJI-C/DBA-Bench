# Release overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.6.md`
- Source Title: `TiDB 7.1.6 Release Notes`
- Source Heading Path: `TiDB 7.1.6 Release Notes | TiDB 7.1.6 Release Notes > Compatibility changes`
- Source Line Ranges: `5-23`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `ticdc`, `lightning`, `tikv`, `pd`
- Topic Tags: `release-date`, `compatibility-changes`, `http-api`, `ddl-history`, `oom-prevention`, `update-splitting`, `mysql-sink`, `thresholdts`, `csv-import`, `strict-format`, `line-terminator`, `grpc-compression`, `cpu-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0479_e3bdf0c8f1`
- Source ID: `tidb-docs-8.1:releases/release-7.1.6.md#tidb-7-1-6-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `49e17e19b03beeb613036e2fe357ef77f2622a02b3f21e581fcafca10e007aef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.6#tidb-7-1-6-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.6 release date information or compatibility changes affecting the TiDB HTTP API, TiCDC MySQL sink split-update behavior, TiDB Lightning strict-format CSV import, or TiKV gRPC compression scope.
- Retrieval Keywords: TiDB 7.1.6 Release Notes, Release date November 21 2024, Compatibility changes, DDL historical tasks, TiDB HTTP API, default limit of 2048, OOM issues, TiCDC, MySQL sink, UPDATE event, DELETE and INSERT events, commitTS, thresholdTS, PD, split update events for mysql sinks, TiDB Lightning, strict-format, CSV files, line terminator, TiKV, server.grpc-compression-type, gRPC response messages, CPU resources
- Follow-up Guidance: The chunk points to the TiCDC documentation page about split update events for MySQL sinks for more information.
- Classification Note: This is a release-note compatibility-changes section summarizing behavior and scope changes introduced in TiDB 7.1.6 across TiDB, TiCDC, Lightning, and TiKV.

## Official Source Content

# TiDB 7.1.6 Release Notes

Release date: November 21, 2024

TiDB version: 7.1.6

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.1/production-deployment-using-tiup)
## Compatibility changes

- Set a default limit of 2048 for DDL historical tasks retrieved through the [TiDB HTTP API](https://github.com/pingcap/tidb/blob/release-7.1/docs/tidb_http_api.md) to prevent OOM issues caused by excessive historical tasks [#55711](https://github.com/pingcap/tidb/issues/55711) @[joccau](https://github.com/joccau)
- In earlier versions, when processing a transaction containing `UPDATE` changes, if the primary key or non-null unique index value is modified in an `UPDATE` event, TiCDC splits this event into `DELETE` and `INSERT` events. Starting from v7.1.6, when using the MySQL sink, TiCDC splits an `UPDATE` event into `DELETE` and `INSERT` events if the transaction `commitTS` for the `UPDATE` change is less than TiCDC `thresholdTS` (which is the current timestamp fetched from PD when TiCDC starts replicating the corresponding table to the downstream). This behavior change addresses the issue of downstream data inconsistencies caused by the potentially incorrect order of `UPDATE` events received by TiCDC, which can lead to an incorrect order of split `DELETE` and `INSERT` events. For more information, see [documentation](https://docs.pingcap.com/tidb/v7.1/ticdc-split-update-behavior#split-update-events-for-mysql-sinks). [#10918](https://github.com/pingcap/tiflow/issues/10918) @[lidezhu](https://github.com/lidezhu)
- Must set the line terminator when using TiDB Lightning `strict-format` to import CSV files [#37338](https://github.com/pingcap/tidb/issues/37338) @[lance6716](https://github.com/lance6716)
- Change the scope of the TiKV configuration item [`server.grpc-compression-type`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#grpc-compression-type):

    - In v7.1.x versions earlier than v7.1.6, this configuration item only affects the compression algorithm of gRPC messages between TiKV nodes.
    - Starting from v7.1.6, this configuration item also affects the compression algorithm of gRPC response messages sent from TiKV to TiDB. Enabling compression might consume more CPU resources. [#17176](https://github.com/tikv/tikv/issues/17176) @[ekexium](https://github.com/ekexium)
