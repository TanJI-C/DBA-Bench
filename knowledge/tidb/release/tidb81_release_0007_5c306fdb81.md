# TiDB 1.0.3 release notes and upgrade order

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-1.0.3.md`
- Source Title: `TiDB 1.0.3 Release Notes`
- Source Heading Path: `TiDB 1.0.3 Release Notes | TiDB 1.0.3 Release Notes > TiDB | TiDB 1.0.3 Release Notes > PD | TiDB 1.0.3 Release Notes > TiKV`
- Source Line Ranges: `5-33`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `release-notes`, `bug-fixes`, `performance-optimization`, `configuration-options`, `scheduler-api`, `rolling-upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0007_5c306fdb81`
- Source ID: `tidb-docs-8.1:releases/release-1.0.3.md#tidb-1-0-3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `afc9471d70ca25cdad7f64e5ec80ae8a2541fd22b9b35442bec9f0fb11090636`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-1.0.3#tidb-1-0-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-1.0.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 1.0.3 release notes, its listed fixes and optimizations across TiDB, PD, and TiKV, or the documented rolling upgrade order from 1.0.2 to 1.0.3.
- Retrieval Keywords: TiDB 1.0.3 Release Notes, upgrade from 1.0.2 to 1.0.3, rolling upgrade order of PD -> TiKV -> TiDB, TokenLimit option, default database in slow query logs, remove the DDL statement from query duration metrics, query cost estimation, index prefix issue when creating tables, pushing down the expressions for the Float type to TiKV, slow to add index for tables with discrete integer primary index, reduce the unnecessary statistics updates, transaction retry, support adding more types of schedulers using API, deadlock issue with the PD client, wrong leader value for NotLeader, chunk size is too large in the coprocessor
- Follow-up Guidance: The source states that to upgrade from 1.0.2 to 1.0.3, follow the rolling upgrade order of PD -> TiKV -> TiDB.
- Classification Note: This chunk is classified as a self-managed release note because it lists TiDB 1.0.3 updates for TiDB, PD, and TiKV and includes the upgrade order.

## Official Source Content

# TiDB 1.0.3 Release Notes

On November 28, 2017, TiDB 1.0.3 is released with the following updates:
## TiDB

- [Optimize the performance in transaction conflicts scenario](https://github.com/pingcap/tidb/pull/5051)
- [Add the `TokenLimit` option in the config file](https://github.com/pingcap/tidb/pull/5107)
- [Output the default database in slow query logs](https://github.com/pingcap/tidb/pull/5107)
- [Remove the DDL statement from query duration metrics](https://github.com/pingcap/tidb/pull/5107)
- [Optimize the query cost estimation](https://github.com/pingcap/tidb/pull/5140)
- [Fix the index prefix issue when creating tables](https://github.com/pingcap/tidb/pull/5149)
- [Support pushing down the expressions for the Float type to TiKV](https://github.com/pingcap/tidb/pull/5153)
- [Fix the issue that it is slow to add index for tables with discrete integer primary index](https://github.com/pingcap/tidb/pull/5155)
- [Reduce the unnecessary statistics updates](https://github.com/pingcap/tidb/pull/5164)
- [Fix a potential issue during the transaction retry](https://github.com/pingcap/tidb/pull/5219)
## PD

- Support adding more types of schedulers using API
## TiKV

- Fix the deadlock issue with the PD client
- Fix the issue that the wrong leader value is prompted for `NotLeader`
- Fix the issue that the chunk size is too large in the coprocessor

To upgrade from 1.0.2 to 1.0.3, follow the rolling upgrade order of PD -> TiKV -> TiDB.
