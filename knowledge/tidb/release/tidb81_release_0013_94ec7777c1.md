# TiDB 1.0.8 TiDB changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-1.0.8.md`
- Source Title: `TiDB 1.0.8 Release Notes`
- Source Heading Path: `TiDB 1.0.8 Release Notes > TiDB`
- Source Line Ranges: `10-23`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `outer join`, `insert ignore`, `shardrowid`, `dml`, `prepare`, `statistics`, `drop column`, `add column`, `gc`, `create index`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0013_94ec7777c1`
- Source ID: `tidb-docs-8.1:releases/release-1.0.8.md#tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `85b8412769d9cbdfa43b6aa91a589717a3aafd66796a3f9d7cba4354cdf64c7c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-1.0.8#tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-1.0.8.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 1.0.8 changes related to SQL behavior, DML limits, GC, statistics, or CREATE INDEX syntax support.
- Retrieval Keywords: Outer Join, InsertIntoIgnore, ShardRowID, DML statements number within a transaction, default value is 5000, Prepare statement, statistics delta, Drop Column, Add Column After, GC process, CREATE INDEX
- Follow-up Guidance: The chunk lists TiDB updates including fixes for Outer Join, Prepare statement aliases, Drop Column, Add Column After, GC improvements, and CREATE INDEX syntax support.
- Classification Note: This is classified as a TiDB release change list because the content enumerates TiDB-specific fixes, optimizations, limitations, and syntax support added in 1.0.8.

## Official Source Content

## TiDB

- [Fix issues in the `Outer Join` result in some scenarios](https://github.com/pingcap/tidb/pull/5712)
- [Optimize the performance of the `InsertIntoIgnore` statement](https://github.com/pingcap/tidb/pull/5738)
- [Fix the issue in the `ShardRowID` option](https://github.com/pingcap/tidb/pull/5751)
- [Add limitation (Configurable, the default value is 5000) to the DML statements number within a transaction](https://github.com/pingcap/tidb/pull/5754)
- [Fix an issue in the Table/Column aliases returned by the `Prepare` statement](https://github.com/pingcap/tidb/pull/5776)
- [Fix an issue in updating statistics delta](https://github.com/pingcap/tidb/pull/5787)
- [Fix a panic error in the `Drop Column` statement](https://github.com/pingcap/tidb/pull/5805)
- [Fix an DML issue when running the `Add Column After` statement](https://github.com/pingcap/tidb/pull/5818)
- [Improve the stability of the GC process by ignoring the regions with GC errors](https://github.com/pingcap/tidb/pull/5815)
- [Run GC concurrently to accelerate the GC process](https://github.com/pingcap/tidb/pull/5850)
- [Provide syntax support for the `CREATE INDEX` statement](https://github.com/pingcap/tidb/pull/5853)
