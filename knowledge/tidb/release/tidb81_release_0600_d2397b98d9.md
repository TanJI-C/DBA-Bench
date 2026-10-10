# TiDB 8.1.1 overview, compatibility changes, and offline package changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.1.md`
- Source Title: `TiDB 8.1.1 Release Notes`
- Source Heading Path: `TiDB 8.1.1 Release Notes | TiDB 8.1.1 Release Notes > Compatibility changes | TiDB 8.1.1 Release Notes > Offline package changes`
- Source Line Ranges: `5-27`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `lightning`, `sql`, `tikv`
- Topic Tags: `release-notes`, `compatibility-changes`, `csv-import`, `import-into`, `line-terminator`, `hashagg-spill`, `grpc-compression`, `offline-package`, `binary-package`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0600_d2397b98d9`
- Source ID: `tidb-docs-8.1:releases/release-8.1.1.md#tidb-8-1-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ba4c865b799a2d9b9cf847bbf4499db077dd8553031076d2567544c187485f47`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.1#tidb-8-1-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.1.1 compatibility changes affecting CSV import behavior, the default of tidb_enable_parallel_hashagg_spill, the scope of TiKV server.grpc-compression-type, or offline package contents.
- Retrieval Keywords: TiDB 8.1.1 Release Notes, Compatibility changes, Offline package changes, TiDB Lightning, strict-format = true, CSV file, terminator, \r, \n, \r\n, exception when parsing the CSV file data, IMPORT INTO, SPLIT_FILE, LINES_TERMINATED_BY, tidb_enable_parallel_hashagg_spill, default value ON to OFF, incorrect query results, disk spill during parallel calculation, upgraded to v8.1.1 from v8.0.0 or v8.1.0, server.grpc-compression-type, gRPC response messages sent from TiKV to TiDB, Enabling compression might consume more CPU resources, arbiter removed, TiDB-community-toolkit, binary package
- Follow-up Guidance: For upgraded clusters from v8.0.0 or v8.1.0, the content states that tidb_enable_parallel_hashagg_spill remains ON after upgrade and recommends manually changing it to OFF.
- Classification Note: This is a release-notes chunk because the official content lists TiDB 8.1.1 compatibility changes and an offline package change across Lightning, IMPORT INTO, TiDB, TiKV, and the binary package.

## Official Source Content

# TiDB 8.1.1 Release Notes

Release date: August 27, 2024

TiDB version: 8.1.1

Quick access: [Quick start](https://docs.pingcap.com/tidb/v8.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v8.1/production-deployment-using-tiup)
## Compatibility changes

- When using TiDB Lightning to import a CSV file, if you set `strict-format = true` to split a large CSV file into multiple small CSV files to improve concurrency and import performance, you need to explicitly specify `terminator`. The values can be `\r`, `\n` or `\r\n`. Failure to specify a line terminator might result in an exception when parsing the CSV file data. [#37338](https://github.com/pingcap/tidb/issues/37338) @[lance6716](https://github.com/lance6716)
- When using [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) to import a CSV file, if you specify the `SPLIT_FILE` parameter to split a large CSV file into multiple small CSV files to improve concurrency and import performance, you need to explicitly specify the line terminator `LINES_TERMINATED_BY`. The values can be `\r`, `\n` or `\r\n`. Failure to specify a line terminator might result in an exception when parsing the CSV file data. [#37338](https://github.com/pingcap/tidb/issues/37338) @[lance6716](https://github.com/lance6716)
- Change the default value of the [`tidb_enable_parallel_hashagg_spill`](https://docs.pingcap.com/tidb/v8.1/system-variables#tidb_enable_parallel_hashagg_spill-new-in-v800) variable from `ON` to `OFF` to avoid incorrect query results caused by disk spill during parallel calculation. For clusters upgraded to v8.1.1 from v8.0.0 or v8.1.0, this variable will remain at its previous default value of `ON` after the upgrade, and it is recommended to manually change it to `OFF`. [#55290](https://github.com/pingcap/tidb/issues/55290) @[xzhangxian1008](https://github.com/xzhangxian1008)
- Change the scope of the TiKV configuration item [`server.grpc-compression-type`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#grpc-compression-type):

    - In v8.1.0, this configuration item only affects the compression algorithm of gRPC messages between TiKV nodes.
    - Starting from v8.1.1, this configuration item also affects the compression algorithm of gRPC response messages sent from TiKV to TiDB. Enabling compression might consume more CPU resources. [#17176](https://github.com/tikv/tikv/issues/17176) @[ekexium](https://github.com/ekexium)
## Offline package changes

In v8.1.1, `arbiter` is removed from the `TiDB-community-toolkit` [binary package](https://docs.pingcap.com/tidb/stable/binary-package).
