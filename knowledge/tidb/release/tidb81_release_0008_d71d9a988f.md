# TiDB 1.0.4 release notes and upgrade order

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-1.0.4.md`
- Source Title: `TiDB 1.0.4 Release Notes`
- Source Heading Path: `TiDB 1.0.4 Release Notes | TiDB 1.0.4 Release Notes > TiDB | TiDB 1.0.4 Release Notes > TiKV`
- Source Line Ranges: `5-24`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `release-notes`, `bug-fixes`, `performance-improvements`, `upgrade-order`, `rolling-upgrade`, `statistics-loading`, `show-variables`, `add-index`, `rename-table`, `alter-user`, `drop-user`, `snapshot-apply`, `reverse-scan`, `decimal-encoding`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0008_d71d9a988f`
- Source ID: `tidb-docs-8.1:releases/release-1.0.4.md#tidb-1-0-4-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ff03035d2a84048510deb40f891870ebdd7f24f9bae858d19fcb69293c255cc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-1.0.4#tidb-1-0-4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-1.0.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 1.0.4 release notes, its listed TiDB and TiKV fixes and performance improvements, or the documented rolling upgrade order from 1.0.3 to 1.0.4.
- Retrieval Keywords: TiDB 1.0.4 Release Notes, upgrade from 1.0.3 to 1.0.4, rolling upgrade order PD -> TiKV -> TiDB, speed up loading of the statistics when starting the tidb-server, show variables statement performance, Add Index combined indexes, Rename Table move a table to another database, Alter/Drop User statement, snapshot is applied performance issue, reverse scan after removing a lot of data, wrong encoded result for the Decimal type
- Follow-up Guidance: The source states that to upgrade from 1.0.3 to 1.0.4, follow the rolling upgrade order of PD -> TiKV -> TiDB.
- Classification Note: This is a self-managed release-notes chunk covering TiDB 1.0.4 changes in shared components with specific TiDB and TiKV bug fixes, performance improvements, and upgrade sequencing.

## Official Source Content

# TiDB 1.0.4 Release Notes

On December 11, 2017, TiDB 1.0.4 is released with the following updates:
## TiDB

- [Speed up the loading of the statistics when starting the `tidb-server`](https://github.com/pingcap/tidb/pull/5362)
- [Improve the performance of the `show variables` statement](https://github.com/pingcap/tidb/pull/5363)
- [Fix a potential issue when using the `Add Index` statement to handle the combined indexes](https://github.com/pingcap/tidb/pull/5323)
- [Fix a potential issue when using the `Rename Table` statement to move a table to another database](https://github.com/pingcap/tidb/pull/5314)
- [Accelerate the effectiveness for the `Alter/Drop User` statement](https://github.com/pingcap/tidb/pull/5226)
## TiKV

- [Fix a possible performance issue when a snapshot is applied](https://github.com/pingcap/tikv/pull/2559)
- [Fix the performance issue for reverse scan after removing a lot of data](https://github.com/pingcap/tikv/pull/2559)
- [Fix the wrong encoded result for the Decimal type under special circumstances](https://github.com/pingcap/tikv/pull/2571)

To upgrade from 1.0.3 to 1.0.4, follow the rolling upgrade order of PD -> TiKV -> TiDB.
