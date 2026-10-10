# TiDB 1.0.7 release notes and upgrade order

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-1.0.7.md`
- Source Title: `TiDB 1.0.7 Release Notes`
- Source Heading Path: `TiDB 1.0.7 Release Notes | TiDB 1.0.7 Release Notes > TiDB | TiDB 1.0.7 Release Notes > PD | TiDB 1.0.7 Release Notes > TiKV`
- Source Line Ranges: `5-39`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `release-notes`, `bug-fixes`, `enhancements`, `upgrade-order`, `rolling-upgrade`, `compatibility`, `scheduling`, `tikv-ctl`, `statistics`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0011_6e0fd1cf27`
- Source ID: `tidb-docs-8.1:releases/release-1.0.7.md#tidb-1-0-7-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7d9f392d5fcb7ed2ee8c8c009e03e9941a4bf7e3900fd2168038adf33b8386e7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-1.0.7#tidb-1-0-7-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-1.0.7.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 1.0.7 release notes, the listed bug fixes and enhancements across TiDB, PD, and TiKV, or the rolling upgrade order from 1.0.6 to 1.0.7.
- Retrieval Keywords: TiDB 1.0.7 Release Notes, upgrade from 1.0.6 to 1.0.7, rolling upgrade order PD -> TiKV -> TiDB, FIELD_LIST command, session variable to control the log query, information schema data race, IndexJoin, RunWorker false in DDL, PACK_KEYS syntax, schema info API for the http status server, PD scheduling loss issue, proto3 compatibility issue, TiKV Table Scan, tikv-ctl remote mode, tikv-ctl proto format compatibility, loss of scheduling command from PD, Push metric timeout
- Follow-up Guidance: The source also states that upgrading from 1.0.6 to 1.0.7 follows the rolling upgrade order of PD -> TiKV -> TiDB.
- Classification Note: This is a self-managed release-notes chunk because the official content enumerates version 1.0.7 updates for TiDB, PD, and TiKV and includes the upgrade order.

## Official Source Content

# TiDB 1.0.7 Release Notes

On January 22, 2018, TiDB 1.0.7 is released with the following updates:
## TiDB

- [Optimize the `FIELD_LIST` command](https://github.com/pingcap/tidb/pull/5679)
- [Fix data race of the information schema](https://github.com/pingcap/tidb/pull/5676)
- [Avoid adding read-only statements to history](https://github.com/pingcap/tidb/pull/5661)
- [Add the `session` variable to control the log query](https://github.com/pingcap/tidb/pull/5659)
- [Fix the resource leak issue in statistics](https://github.com/pingcap/tidb/pull/5657)
- [Fix the goroutine leak issue](https://github.com/pingcap/tidb/pull/5624)
- [Add schema info API for the http status server](https://github.com/pingcap/tidb/pull/5256)
- [Fix an issue about `IndexJoin`](https://github.com/pingcap/tidb/pull/5623)
- [Update the behavior when `RunWorker` is false in DDL](https://github.com/pingcap/tidb/pull/5604)
- [Improve the stability of test results in statistics](https://github.com/pingcap/tidb/pull/5609)
- [Support `PACK_KEYS` syntax for the `CREATE TABLE` statement](https://github.com/pingcap/tidb/pull/5602)
- [Add `row_id` column for the null pushdown schema to optimize performance](https://github.com/pingcap/tidb/pull/5447)
## PD

- [Fix possible scheduling loss issue in abnormal conditions](https://github.com/pingcap/pd/pull/921)
- [Fix the compatibility issue with proto3](https://github.com/pingcap/pd/pull/919)
- [Add the log](https://github.com/pingcap/pd/pull/917)
## TiKV

- [Support `Table Scan`](https://github.com/pingcap/tikv/pull/2657)
- [Support the remote mode in tikv-ctl](https://github.com/pingcap/tikv/pull/2377)
- [Fix the format compatibility issue of tikv-ctl proto](https://github.com/pingcap/tikv/pull/2668)
- [Fix the loss of scheduling command from PD](https://github.com/pingcap/tikv/pull/2669)
- [Add timeout in Push metric](https://github.com/pingcap/tikv/pull/2686)

To upgrade from 1.0.6 to 1.0.7, follow the rolling upgrade order of PD -> TiKV -> TiDB.
