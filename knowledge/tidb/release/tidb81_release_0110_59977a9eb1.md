# TiDB 3.0.17 release notes improvements and bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.17.md`
- Source Title: `TiDB 3.0.17 Release Notes`
- Source Heading Path: `TiDB 3.0.17 Release Notes | TiDB 3.0.17 Release Notes > Improvements | TiDB 3.0.17 Release Notes > Bug Fixes`
- Source Line Ranges: `5-51`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `lightning`
- Topic Tags: `release-notes`, `improvements`, `bug-fixes`, `configuration`, `performance`, `statistics`, `ddl`, `region-merging`, `memory-leak`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0110_59977a9eb1`
- Source ID: `tidb-docs-8.1:releases/release-3.0.17.md#tidb-3-0-17-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c962183ff36f79456c005f71f38861dfd19272a92632666e43f51fd9b3e6256`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.17#tidb-3-0-17-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.17.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.0.17 release-note details about improvements and bug fixes in TiDB, TiKV, or TiDB Lightning, including configuration changes, statistics feedback, DDL, region merging, memory leak, and deprecated settings.
- Retrieval Keywords: TiDB 3.0.17 Release Notes, query-feedback-limit, default value 1024 to 512, statistics feedback mechanism, batch split count, /tiflash/replica HTTP API, history DDL jobs, row count estimation for index equal condition, kill tidb conn_id, hibernate-timeout, region hibernation, rolling update performance, [black-white-list] deprecated, filter format, IndexHashJoin, IndexMergeJoin, SELECT a FROM t HAVING t.a, EXPLAIN FORMAT="dot" FOR CONNECTION, STR_TO_DATE, %r, %h, read stale data during region merging, memory leak during the scheduling process, log-file flag is ignored
- Follow-up Guidance: The source also groups the changes by component under Improvements and Bug Fixes for TiDB, TiKV, and TiDB Lightning.
- Classification Note: This is a self-managed release-notes chunk for TiDB 3.0.17 that summarizes official improvements and bug fixes across shared components including TiDB, TiKV, and TiDB Lightning.

## Official Source Content

# TiDB 3.0.17 Release Notes

Release date: Aug 3, 2020

TiDB version: 3.0.17
## Improvements

+ TiDB

    - Decrease the default value of the `query-feedback-limit` configuration item from 1024 to 512, and improve the statistics feedback mechanism to ease its impact on the cluster [#18770](https://github.com/pingcap/tidb/pull/18770)
    - Limit batch split count for one request [#18694](https://github.com/pingcap/tidb/pull/18694)
    - Accelerate `/tiflash/replica` HTTP API when there are many history DDL jobs in the TiDB cluster [#18386](https://github.com/pingcap/tidb/pull/18386)
    - Improve row count estimation for index equal condition [#17609](https://github.com/pingcap/tidb/pull/17609)
    - Speed up the execution of `kill tidb conn_id` [#18506](https://github.com/pingcap/tidb/pull/18506)

+ TiKV

    - Add the `hibernate-timeout` configuration that delays region hibernation to improve rolling update performance [#8207](https://github.com/tikv/tikv/pull/8207)

+ Tools

    + TiDB Lightning

        - `[black-white-list]` has been deprecated with a newer, easier-to-understand filter format [#332](https://github.com/pingcap/tidb-lightning/pull/332)
## Bug Fixes

+ TiDB

    - Return the actual error message instead of an empty set when a query which contains `IndexHashJoin` or `IndexMergeJoin` encounters a panic [#18498](https://github.com/pingcap/tidb/pull/18498)
    - Fix the unknown column error for SQL statements like `SELECT a FROM t HAVING t.a` [#18432](https://github.com/pingcap/tidb/pull/18432)
    - Forbid adding a primary key for a table when the table has no primary key or when the table already has an integer primary key [#18342](https://github.com/pingcap/tidb/pull/18342)
    - Return an empty set when executing `EXPLAIN FORMAT="dot" FOR CONNECTION` [#17157](https://github.com/pingcap/tidb/pull/17157)
    - Fix `STR_TO_DATE`'s handling for format token '%r', '%h' [#18725](https://github.com/pingcap/tidb/pull/18725)

+ TiKV

    - Fix a bug that might read stale data during region merging [#8111](https://github.com/tikv/tikv/pull/8111)
    - Fix the issue of memory leak during the scheduling process [#8355](https://github.com/tikv/tikv/pull/8355)

+ Tools

    + TiDB Lightning

        - Fix the issue that the `log-file` flag is ignored [#345](https://github.com/pingcap/tidb-lightning/pull/345)
