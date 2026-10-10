# TiDB 1.0.6 release notes and upgrade order

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-1.0.6.md`
- Source Title: `TiDB 1.0.6 Release Notes`
- Source Heading Path: `TiDB 1.0.6 Release Notes | TiDB 1.0.6 Release Notes > TiDB | TiDB 1.0.6 Release Notes > PD | TiDB 1.0.6 Release Notes > TiKV`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `sql`
- Topic Tags: `release-notes`, `bug-fixes`, `sql-syntax`, `ddl`, `statistics`, `timezone`, `group-concat`, `hot-region-scheduler`, `rolling-upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0010_bfb884dc09`
- Source ID: `tidb-docs-8.1:releases/release-1.0.6.md#tidb-1-0-6-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `943c5c4448bdbe2675e9a7400f9a666bc9e66cb56a815713476b9a8b35a40128`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-1.0.6#tidb-1-0-6-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-1.0.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 1.0.6 release-note details, including specific SQL syntax additions, bug fixes, and the rolling upgrade order from 1.0.5 to 1.0.6.
- Retrieval Keywords: TiDB 1.0.6 Release Notes, 1.0.6 release notes, upgrade from 1.0.5 to 1.0.6, rolling upgrade order of PD -> TiKV -> TiDB, Alter Table Auto_Increment syntax, Null Json issue in statistics, Cost Based computation, shard the implicit row ID, avoid write hot spot for a single table, potential DDL issue, timezone setting in curtime sysdate curdate, SEPARATOR syntax in the GROUP_CONCAT function, wrong return type issue of the GROUP_CONCAT function, hot-region scheduler store selection problem, PD, TiKV None
- Follow-up Guidance: The source states that to upgrade from 1.0.5 to 1.0.6, the rolling upgrade order is PD -> TiKV -> TiDB.
- Classification Note: This chunk is classified as a self-managed release note because it summarizes TiDB 1.0.6 updates across TiDB, PD, and TiKV and includes the documented upgrade order.

## Official Source Content

# TiDB 1.0.6 Release Notes

On January 08, 2018, TiDB 1.0.6 is released with the following updates:
## TiDB

- [Support the `Alter Table Auto_Increment` syntax](https://github.com/pingcap/tidb/pull/5511)
- [Fix the bug in Cost Based computation and the `Null Json` issue in statistics](https://github.com/pingcap/tidb/pull/5556)
- [Support the extension syntax to shard the implicit row ID to avoid write hot spot for a single table](https://github.com/pingcap/tidb/pull/5559)
- [Fix a potential DDL issue](https://github.com/pingcap/tidb/pull/5562)
- [Consider the timezone setting in the `curtime`, `sysdate` and `curdate` functions](https://github.com/pingcap/tidb/pull/5564)
- [Support the `SEPARATOR` syntax in the `GROUP_CONCAT` function](https://github.com/pingcap/tidb/pull/5569)
- [Fix the wrong return type issue of the `GROUP_CONCAT` function.](https://github.com/pingcap/tidb/pull/5582)
## PD

- [Fix store selection problem of hot-region scheduler](https://github.com/pingcap/pd/pull/898)
## TiKV

None.

To upgrade from 1.0.5 to 1.0.6, follow the rolling upgrade order of PD -> TiKV -> TiDB.
