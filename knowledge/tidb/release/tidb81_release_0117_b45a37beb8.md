# TiDB 3.0.20 release notes: compatibility changes, improvements, and bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.20.md`
- Source Title: `TiDB 3.0.20 Release Notes`
- Source Heading Path: `TiDB 3.0.20 Release Notes | TiDB 3.0.20 Release Notes > Compatibility Change | TiDB 3.0.20 Release Notes > Improvements | TiDB 3.0.20 Release Notes > Bug Fixes`
- Source Line Ranges: `5-60`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `release-notes`, `compatibility`, `deprecation`, `improvements`, `bug-fixes`, `pessimistic-transactions`, `statistics`, `load-data`, `slow-log`, `sql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0117_b45a37beb8`
- Source ID: `tidb-docs-8.1:releases/release-3.0.20.md#tidb-3-0-20-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `333468e14ba73ee49a051d6f540d3950f1ac88472268c2247313d521f77a08aa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.20#tidb-3-0-20-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.20.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.0.20 release-note details about compatibility changes, improvements, or bug fixes across TiDB, TiKV, and PD.
- Retrieval Keywords: TiDB 3.0.20 Release Notes, 3.0.20 compatibility change, enable-streaming deprecate, LOAD DATA preparing statement error, end_point_slow_log_threshold, pessimistic transactions transaction status cache, INFORMATION_SCHEMA.TIDB_HOT_REGIONS inaccurate statistics, DELETE database name not pure lower representation, recursive view stack overflow, TiKV client goroutine leak, year type wrong default zero value, index lookup join goroutine leak, INSERT SELECT FOR UPDATE malformed packet, unknown time zone posixrules, unsigned integer to bit type conversion, bit type column corrupted default value, Enum or Set equal condition incorrect results, != any() wrong behavior, BETWEEN AND type conversion invalid results, ADDDATE compatibility issue, Enum column correct default value, SELECT DATE_ADD('2007-03-28 22:08:28',INTERVAL "-2.-2" SECOND), modifying the column type incorrect default value, timestamp function float decimal wrong result, statistics potential deadlock, overflown float type data is inserted, key exists when key is locked and deleted in a committed transaction, PD too many logs stale Regions
- Follow-up Guidance: The source groups the changes into Compatibility Change, Improvements, and Bug Fixes, with items listed under TiDB, TiKV, and PD.
- Classification Note: This chunk is classified as a release note because it announces TiDB 3.0.20 and enumerates compatibility changes, improvements, and bug fixes for multiple components.

## Official Source Content

# TiDB 3.0.20 Release Notes

Release date: December 25, 2020

TiDB version: 3.0.20
## Compatibility Change

+ TiDB

    - Deprecate the `enable-streaming` configuration item [#21054](https://github.com/pingcap/tidb/pull/21054)
## Improvements

+ TiDB

    - Raise an error when preparing the `LOAD DATA` statement [#21222](https://github.com/pingcap/tidb/pull/21222)

+ TiKV

    - Add the `end_point_slow_log_threshold` configuration item [#9145](https://github.com/tikv/tikv/pull/9145)
## Bug Fixes

+ TiDB

    - Fix the incorrect cache of the transaction status for pessimistic transactions [#21706](https://github.com/pingcap/tidb/pull/21706)
    - Fix the issue of inaccurate statistics that occurs when querying `INFORMATION_SCHEMA.TIDB_HOT_REGIONS` [#21319](https://github.com/pingcap/tidb/pull/21319)
    - Fix the issue that `DELETE` might not delete data correctly when the database name is not in a pure lower representation [#21205](https://github.com/pingcap/tidb/pull/21205)
    - Fix the issue of stack overflow that occurs when building the recursive view [#21000](https://github.com/pingcap/tidb/pull/21000)
    - Fix the issue of goroutine leak in TiKV client [#20863](https://github.com/pingcap/tidb/pull/20863)
    - Fix the wrong default zero value for the `year` type [#20828](https://github.com/pingcap/tidb/pull/20828)
    - Fix the issue of goroutine leak in index lookup join [#20791](https://github.com/pingcap/tidb/pull/20791)
    - Fix the issue that executing `INSERT SELECT FOR UPDATE` returns the malformed packet in the pessimistic transaction [#20681](https://github.com/pingcap/tidb/pull/20681)
    - Fix the unknown time zone `'posixrules'` [#20605](https://github.com/pingcap/tidb/pull/20605)
    - Fix the issue that occurs when converting the unsigned integer type to the bit type [#20362](https://github.com/pingcap/tidb/pull/20362)
    - Fix the corrupted default value of the bit type column [#20339](https://github.com/pingcap/tidb/pull/20339)
    - Fix the potentially incorrect results when one of the equal condition is the `Enum` or `Set` type [#20296](https://github.com/pingcap/tidb/pull/20296)
    - Fix a wrong behavior of `!= any()` [#20061](https://github.com/pingcap/tidb/pull/20061)
    - Fix the issue that type conversion in `BETWEEN...AND...` returns invalid results [#21503](https://github.com/pingcap/tidb/pull/21503)
    - Fix a compatibility issue with the `ADDDATE` function [#21008](https://github.com/pingcap/tidb/pull/21008)
    - Set the correct default value for newly added `Enum` column [#20999](https://github.com/pingcap/tidb/pull/20999)
    - Fix the result of SQL statements like `SELECT DATE_ADD('2007-03-28 22:08:28',INTERVAL "-2.-2" SECOND)` to be compatible with MySQL [#20627](https://github.com/pingcap/tidb/pull/20627)
    - Fix the incorrect default value when modifying the column type [#20532](https://github.com/pingcap/tidb/pull/20532)
    - Fix the issue that the `timestamp` function gets wrong result when the input argument is the `float` or `decimal` type [#20469](https://github.com/pingcap/tidb/pull/20469)
    - Fix a potential deadlock issue in statistics [#20424](https://github.com/pingcap/tidb/pull/20424)
    - Fix the issue that the overflown float type data is inserted [#20251](https://github.com/pingcap/tidb/pull/20251)

+ TiKV

    - Fix the issue that an error is returned indicating that a key exists when this key is locked and deleted in a committed transaction [#8931](https://github.com/tikv/tikv/pull/8931)

+ PD

    - Fix the issue that too many logs are printed when starting PD and when there are too many stale Regions [#3064](https://github.com/pingcap/pd/pull/3064)
