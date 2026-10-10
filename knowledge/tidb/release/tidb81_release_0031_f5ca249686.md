# TiDB 2.0.3 release notes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0.3.md`
- Source Title: `TiDB 2.0.3 Release Notes`
- Source Heading Path: `TiDB 2.0.3 Release Notes | TiDB 2.0.3 Release Notes > TiDB | TiDB 2.0.3 Release Notes > PD | TiDB 2.0.3 Release Notes > TiKV`
- Source Line Ranges: `5-37`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `release-notes`, `bug-fixes`, `compatibility`, `stability`, `sql`, `scheduling`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0031_f5ca249686`
- Source ID: `tidb-docs-8.1:releases/release-2.0.3.md#tidb-2-0-3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2c004037b8a00caa6266e588e5e5c99f4770aa418458cf2e5516ecf612cb4057`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0.3#tidb-2-0-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0.3.md

## Retrieval Guidance

- Use When: Use this when you need the TiDB 2.0.3 release notes for a summary of compatibility, stability, SQL, PD, and TiKV changes.
- Retrieval Keywords: TiDB 2.0.3 Release Notes, June 1, 2018, system compatibility, stability, Support modifying the log level online, COM_CHANGE_USER, TIME type parameters, BETWEEN expression, SHOW CREATE TABLE, LIMIT clause, YEAR type, ON DUPLICATE KEY UPDATE, CEIL, DIV calculation, ADMIN CHECK TABLE, MAX/MIN, JOIN, IN expression, Prepare, Plan Cache, hot-cache metrics, obsolete Regions, learner flag, do_div_mod
- Follow-up Guidance: 
- Classification Note: This is a release note entry for TiDB 2.0.3, covering changes under TiDB, PD, and TiKV.

## Official Source Content

# TiDB 2.0.3 Release Notes

On June 1, 2018, TiDB 2.0.3 is released. Compared with TiDB 2.0.2, this release has great improvement in system compatibility and stability.
## TiDB

- Support modifying the log level online
- Support the `COM_CHANGE_USER` command
- Support using the `TIME` type parameters under the binary protocol
- Optimize the cost estimation of query conditions with the `BETWEEN` expression
- Do not display the `FOREIGN KEY` information in the result of `SHOW CREATE TABLE`
- Optimize the cost estimation for queries with the `LIMIT` clause
- Fix the issue about the `YEAR` type as the unique index
- Fix the issue about `ON DUPLICATE KEY UPDATE` in conditions without the unique index
- Fix the compatibility issue of the `CEIL` function
- Fix the accuracy issue of the `DIV` calculation in the `DECIMAL` type
- Fix the false alarm of `ADMIN CHECK TABLE`
- Fix the panic issue of `MAX`/`MIN` under specific expression parameters
- Fix the issue that the result of `JOIN` is null in special conditions
- Fix the `IN` expression issue when building and querying Range
- Fix a Range calculation issue when using `Prepare` to query and `Plan Cache` is enabled
- Fix the issue that the Schema information is frequently loaded in abnormal conditions
## PD

- Fix the panic issue when collecting hot-cache metrics in specific conditions
- Fix the issue about scheduling of the obsolete Regions
## TiKV

- Fix the bug that the learner flag mistakenly reports to PD
- Report an error instead of getting a result if `divisor/dividend` is 0 in `do_div_mod`
