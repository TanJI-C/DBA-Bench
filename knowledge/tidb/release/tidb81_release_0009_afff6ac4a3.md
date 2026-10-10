# TiDB 1.0.5 release notes and upgrade order

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-1.0.5.md`
- Source Title: `TiDB 1.0.5 Release Notes`
- Source Heading Path: `TiDB 1.0.5 Release Notes | TiDB 1.0.5 Release Notes > TiDB | TiDB 1.0.5 Release Notes > PD | TiDB 1.0.5 Release Notes > TiKV`
- Source Line Ranges: `5-33`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `release-notes`, `bug-fixes`, `enhancements`, `upgrade-order`, `rolling-upgrade`, `slow-query`, `timezone`, `auto-increment`, `leader-balancing`, `bootstrap`, `cpu-id`, `space-collection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0009_afff6ac4a3`
- Source ID: `tidb-docs-8.1:releases/release-1.0.5.md#tidb-1-0-5-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b962be70c506c09e38bccf99d22f339a1834d328b586bdbbef817e5757e866c6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-1.0.5#tidb-1-0-5-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-1.0.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 1.0.5 release notes, included bug fixes and enhancements across TiDB, PD, and TiKV, or the rolling upgrade order from 1.0.4 to 1.0.5.
- Retrieval Keywords: TiDB 1.0.5 Release Notes, upgrade from 1.0.4 to 1.0.5, rolling upgrade order PD -> TiKV -> TiDB, Show Create Table, Auto_Increment ID, slow queries into a separate file, TimeZone variable from TiKV, Analyze statements process the public table/index only, set transaction read only, tx_read_only, leaders stop balancing, bootstrapping panic, get_cpuid, dynamic-level-bytes, space collection
- Follow-up Guidance: The source states that upgrading from 1.0.4 to 1.0.5 follows the rolling upgrade order of PD -> TiKV -> TiDB.
- Classification Note: This is a self-managed release-notes chunk summarizing TiDB 1.0.5 fixes and enhancements for the shared TiDB, PD, and TiKV components, including the documented upgrade order.

## Official Source Content

# TiDB 1.0.5 Release Notes

On December 26, 2017, TiDB 1.0.5 is released with the following updates:
## TiDB

- [Add the max value for the current Auto_Increment ID in the `Show Create Table` statement.](https://github.com/pingcap/tidb/pull/5489)
- [Fix a potential goroutine leak.](https://github.com/pingcap/tidb/pull/5486)
- [Support outputting slow queries into a separate file.](https://github.com/pingcap/tidb/pull/5484)
- [Load the `TimeZone` variable from TiKV when creating a new session.](https://github.com/pingcap/tidb/pull/5479)
- [Support the schema state check so that the `Show Create Table`and `Analyze` statements process the public table/index only.](https://github.com/pingcap/tidb/pull/5474)
- [The `set transaction read only` should affect the `tx_read_only` variable.](https://github.com/pingcap/tidb/pull/5491)
- [Clean up incremental statistic data when rolling back.](https://github.com/pingcap/tidb/pull/5391)
- [Fix the issue of missing index length in the `Show Create Table` statement.](https://github.com/pingcap/tidb/pull/5421)
## PD

- Fix the issue that the leaders stop balancing under some circumstances.
    - [869](https://github.com/pingcap/pd/pull/869)
    - [874](https://github.com/pingcap/pd/pull/874)
- [Fix potential panic during bootstrapping.](https://github.com/pingcap/pd/pull/889)
## TiKV

- Fix the issue that it is slow to get the CPU ID using the [`get_cpuid`](https://github.com/pingcap/tikv/pull/2611) function.
- Support the [`dynamic-level-bytes`](https://github.com/pingcap/tikv/pull/2605) parameter to improve the space collection situation.

To upgrade from 1.0.4 to 1.0.5, follow the rolling upgrade order of PD -> TiKV -> TiDB.
