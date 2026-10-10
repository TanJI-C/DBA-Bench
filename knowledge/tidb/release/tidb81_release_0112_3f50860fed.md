# TiDB 3.0.19 release notes: compatibility changes, improvements, and bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.19.md`
- Source Title: `TiDB 3.0.19 Release Notes`
- Source Heading Path: `TiDB 3.0.19 Release Notes | TiDB 3.0.19 Release Notes > Compatibility Changes | TiDB 3.0.19 Release Notes > Improvements | TiDB 3.0.19 Release Notes > Bug Fixes`
- Source Line Ranges: `5-53`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tidb`, `tikv`, `lightning`
- Topic Tags: `release-notes`, `compatibility`, `improvements`, `bug-fixes`, `failure-recovery`, `qps`, `concurrency`, `sync-log`, `alerts`, `privilege-checks`, `schema-changes`, `table-locks`, `sql-operators`, `panic-handling`, `csv`, `strict-mode`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0112_3f50860fed`
- Source ID: `tidb-docs-8.1:releases/release-3.0.19.md#tidb-3-0-19-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1519b9b202f68c6dd9ccc3d75b20ddb8867b6d91b3803e15e972e9133dfff9ae`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.19#tidb-3-0-19-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.19.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.0.19 release-note details about compatibility changes, improvements, or bug fixes across PD, TiDB, TiKV, and TiDB Lightning.
- Retrieval Keywords: TiDB 3.0.19 Release Notes, 3.0.19, Compatibility Changes, Improvements, Bug Fixes, pingcap/pd, tikv/pd, failure recovery QPS, union operator concurrency, sync-log true nonadjustable, PD restart alert rule, slow-log file does not exist, SHOW STATS_META, SHOW STATS_BUCKET, decimal type to integer type, ENUM SET type column constraint, table locks after a panic, OR operator WHERE clause, missing reason phrases, illegal UTF characters in CSV, strict mode, TiDB Lightning
- Follow-up Guidance: The source groups the changes under Compatibility Changes, Improvements, and Bug Fixes for PD, TiDB, TiKV, and TiDB Lightning.
- Classification Note: This is a self-managed release-notes chunk summarizing compatibility changes, performance and operational improvements, and bug fixes in TiDB 3.0.19.

## Official Source Content

# TiDB 3.0.19 Release Notes

Release date: September 25, 2020

TiDB version: 3.0.19
## Compatibility Changes

+ PD

    - Change the import path from `pingcap/pd` to `tikv/pd` [#2779](https://github.com/pingcap/pd/pull/2779)
    - Change the copyright information from `PingCAP, Inc` to `TiKV Project Authors` [#2777](https://github.com/pingcap/pd/pull/2777)
## Improvements

+ TiDB

    - Mitigate the impact of failure recovery on QPS performance [#19764](https://github.com/pingcap/tidb/pull/19764)
    - Support adjusting the concurrency of the `union` operator [#19885](https://github.com/pingcap/tidb/pull/19885)

+ TiKV

    - Set `sync-log` to `true` as a nonadjustable value [#8636](https://github.com/tikv/tikv/pull/8636)

+ PD

    - Add an alert rule for PD restart [#2789](https://github.com/pingcap/pd/pull/2789)
## Bug Fixes

+ TiDB

    - Fix the query error that occurs when the `slow-log` file does not exist [#20050](https://github.com/pingcap/tidb/pull/20050)
    - Add the privilege check for `SHOW STATS_META` and `SHOW STATS_BUCKET` [#19759](https://github.com/pingcap/tidb/pull/19759)
    - Forbid changing the decimal type to the integer type [#19681](https://github.com/pingcap/tidb/pull/19681)
    - Fix the issue that the constraint is not checked when altering the `ENUM`/`SET` type column [#20045](https://github.com/pingcap/tidb/pull/20045)
    - Fix the bug that tidb-server does not release table locks after a panic [#20021](https://github.com/pingcap/tidb/pull/20021)
    - Fix the bug that the `OR` operator is not handled correctly in the `WHERE` clause [#19901](https://github.com/pingcap/tidb/pull/19901)

+ TiKV

    - Fix the bug that TiKV panics when parsing responses with missing reason phrases [#8540](https://github.com/tikv/tikv/pull/8540)

+ Tools

    + TiDB Lightning

        - Fix the issue that the TiDB Lightning process does not exit in time when encountering illegal UTF characters in CSV in the strict mode [#378](https://github.com/pingcap/tidb-lightning/pull/378)
