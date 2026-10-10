# TiDB 5.1.2 release overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.2.md`
- Source Title: `TiDB 5.1.2 Release Notes`
- Source Heading Path: `TiDB 5.1.2 Release Notes | TiDB 5.1.2 Release Notes > Compatibility changes | TiDB 5.1.2 Release Notes > Improvements`
- Source Line Ranges: `5-71`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `ticdc`, `dumpling`
- Topic Tags: `release-notes`, `compatibility`, `upgrade`, `execution-results`, `auto-analyze`, `scheduling`, `mpp`, `memory-management`, `grpc`, `backup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0228_83bdcc0616`
- Source ID: `tidb-docs-8.1:releases/release-5.1.2.md#tidb-5-1-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a2161f39bf8815fe1170bc162e6237b7d8ea9371bccfdf8a463eab3ac8857825`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.2#tidb-5-1-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when identifying TiDB 5.1.2 compatibility changes and high-level improvements across TiDB, TiKV, PD, TiFlash, TiCDC, and Dumpling.
- Retrieval Keywords: TiDB 5.1.2 Release Notes, Compatibility changes, Improvements, greatest(datetime) union null returns empty string, having clause might not work correctly, group_concat non-bin collation, count(distinct) multiple columns new collation, extract function negative duration, STRICT_TRANS_TABLES invalid date, NO_ZERO_IN_DATE invalid default date, TiCDC compatible version 5.1.0-alpha to 5.2.0-alpha, auto-analyze histogram row count, dynamically modifying TiCDC configurations, Resolved TS message, scatter range scheduler, DATE() function, leader-read, canceling MPP tasks, Unified Sorter, global gRPC connection pool, across major and minor versions, START TRANSACTION ... WITH CONSISTENT SNAPSHOT, SHOW CREATE TABLE
- Follow-up Guidance: The source also lists TiDB 5.1.2 bug fixes in a separate section.
- Classification Note: This is classified as a release chunk because it summarizes release overview content, including compatibility changes that might cause upgrade incompatibilities and improvement items by component.

## Official Source Content

# TiDB 5.1.2 Release Notes

Release Date: September 27, 2021

TiDB version: 5.1.2
## Compatibility changes

+ TiDB

    + The following bug fixes change execution results, which might cause upgrade incompatibilities:

        - Fix the issue that `greatest(datetime) union null` returns empty string [#26532](https://github.com/pingcap/tidb/issues/26532)
        - Fix the issue that the `having` clause might not work correctly [#26496](https://github.com/pingcap/tidb/issues/26496)
        - Fix the wrong execution results that occur when the collations around the `between` expression are different [#27146](https://github.com/pingcap/tidb/issues/27146)
        - Fix the wrong execution results that occur when the column in the `group_concat` function has a non-bin collation [#27429](https://github.com/pingcap/tidb/issues/27429)
        - Fix an issue that using a `count(distinct)` expression on multiple columns returns wrong result when the new collation is enabled [#27091](https://github.com/pingcap/tidb/issues/27091)
        - Fix the result wrong that occurs when the argument of the `extract` function is a negative duration [#27236](https://github.com/pingcap/tidb/issues/27236)
        - Fix the issue that inserting an invalid date does not report an error when the `SQL_MODE` is 'STRICT_TRANS_TABLES' [#26762](https://github.com/pingcap/tidb/issues/26762)
        - Fix the issue that using an invalid default date does not report an error when the `SQL_MODE` is 'NO_ZERO_IN_DATE' [#26766](https://github.com/pingcap/tidb/issues/26766)

+ Tools

    + TiCDC

        - Set the compatible version from `5.1.0-alpha` to `5.2.0-alpha` [#2659](https://github.com/pingcap/tiflow/pull/2659)
## Improvements

+ TiDB

    - Trigger auto-analyze by histogram row count and increase the accuracy of this trigger action  [#24237](https://github.com/pingcap/tidb/issues/24237)

+ TiKV

    - Support dynamically modifying TiCDC configurations [#10645](https://github.com/tikv/tikv/issues/10645)
    - Reduce the size of Resolved TS message to save network bandwidth [#2448](https://github.com/pingcap/tiflow/issues/2448)
    - Limit the counts of peer stats in the heartbeat message reported by a single store [#10621](https://github.com/tikv/tikv/pull/10621)

+ PD

    - Allow empty Regions to be scheduled and use a separate tolerance configuration in scatter range scheduler [#4117](https://github.com/tikv/pd/pull/4117)
    - Improve the performance of synchronizing Region information between PDs [#3933](https://github.com/tikv/pd/pull/3933)
    - Support dynamically adjusting the retry limit of a store based on the generated operator [#3744](https://github.com/tikv/pd/issues/3744)

+ TiFlash

    - Support the `DATE()` function
    - Add Grafana panels for write throughput per instance
    - Optimize the performance of the `leader-read` process
    - Accelerate the process of canceling MPP tasks

+ Tools

    + TiCDC

        - Optimize memory management when the Unified Sorter is using memory to sort data [#2553](https://github.com/pingcap/tiflow/issues/2553)
        - Optimize workerpool for fewer goroutines when concurrency is high  [#2211](https://github.com/pingcap/tiflow/issues/2211)
        - Reduce goroutine usage when a table's Region transfer away from a TiKV node [#2284](https://github.com/pingcap/tiflow/issues/2284)
        - Add a global gRPC connection pool and share gRPC connections among KV clients [#2534](https://github.com/pingcap/tiflow/pull/2534)
        - Prohibit operating TiCDC clusters across major and minor versions [#2599](https://github.com/pingcap/tiflow/pull/2599)

    + Dumpling

        - Support backing up MySQL-compatible databases that do not support `START TRANSACTION ... WITH CONSISTENT SNAPSHOT` and `SHOW CREATE TABLE` [#309](https://github.com/pingcap/dumpling/issues/309)
