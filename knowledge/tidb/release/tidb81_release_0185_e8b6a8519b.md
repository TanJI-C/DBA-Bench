# Bug fixes across TiDB, TiKV, PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.5.md`
- Source Title: `TiDB 4.0.5 Release Notes`
- Source Heading Path: `TiDB 4.0.5 Release Notes > Bug Fixes`
- Source Line Ranges: `102-177`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `dumpling`, `ticdc`, `lightning`
- Topic Tags: `bug-fixes`, `sql-execution`, `transactions`, `partitioning`, `collation`, `leader-election`, `scheduling`, `tso`, `placement-rules`, `backup`, `restore`, `changefeed`, `import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0185_e8b6a8519b`
- Source ID: `tidb-docs-8.1:releases/release-4.0.5.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `352711e374cf6b6039c10f2bb3e5384b03519d96c0db22cce487730590a6d77d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.5#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.5 bug fixes across TiDB, TiKV, PD, TiFlash, BR, Dumpling, TiCDC, or TiDB Lightning for specific errors, incorrect query results, scheduling, TSO, changefeed, backup, restore, or import issues.
- Retrieval Keywords: TiDB 4.0.5 Bug Fixes, should ensure all columns have the same length, ErrTruncate/Overflow, builtinCastRealAsDecimalSig, pre_split_regions, partitioned table, large transaction terminated prematurely, collation functions wrong query results, getAutoIncrementID(), tidb_snapshot, table not exist, unknown column error, select a from t having t.a, hash partitioned table overflow unexpected negative number, ADMIN REPAIR TABLE, SET CHARSET, STR_TO_DATE %r %h, cluster_info table, pessimistic transactions, union select for update, PointGet, BatchPointGet, IndexLookUp, Apply operator, UnionScan, anti-semi-join, EXECUTE expensive query log panic, index join ENUM SET, NULL value exists on the index column, global configuration data race, temporary directory disk spill, decimal type hash key, indexed virtual generated column wrong value, runtime statistics concurrent execution, leader election, Hibernate Region, hibernate-timeout, memory leak during scheduling, TSO request might fail at the time of leader change, placement rules, Balance Leader does not work, unhealthy stores, TiFlash cannot start normally after upgrading, special characters, duplicated calculation of total KV and total bytes, import mode does not work in the first 5 minutes, FTWRL lock is not released in time, failed changefeed cannot be removed, invalid delete events, GC safepoint, network I/O waiting blocks tasks to exit, mistakenly replicated to the downstream, syntax error on empty binary/hex literals, TiDB backend
- Follow-up Guidance: The chunk lists the affected component and the exact bug or behavior fixed in TiDB 4.0.5, including specific statements, functions, operators, configuration items, and tool features.
- Classification Note: This is a release-notes bug-fix summary because the official content enumerates fixes in TiDB 4.0.5 across multiple components and tools.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix the `should ensure all columns have the same length` error that occurs because the `ErrTruncate/Overflow` error is incorrectly handled in the `builtinCastRealAsDecimalSig` function [#18967](https://github.com/pingcap/tidb/pull/18967)
    - Fix the issue that the `pre_split_regions` table option does not work in the partitioned table [#18837](https://github.com/pingcap/tidb/pull/18837)
    - Fix the issue that might cause a large transaction to be terminated prematurely [#18813](https://github.com/pingcap/tidb/pull/18813)
    - Fix the issue that using the `collation` functions get wrong query results [#18735](https://github.com/pingcap/tidb/pull/18735)
    - Fix the bug that the `getAutoIncrementID()` function does not consider the `tidb_snapshot` session variable, which might cause the dumper tool to fail with the `table not exist` error [#18692](https://github.com/pingcap/tidb/pull/18692)
    - Fix the `unknown column error` for SQL statement like `select a from t having t.a` [#18434](https://github.com/pingcap/tidb/pull/18434)
    - Fix the panic issue that writing the 64-bit unsigned type into the hash partitioned table causes overflow and gets an unexpected negative number when the partition key is the integer type [#18186](https://github.com/pingcap/tidb/pull/18186)
    - Fix the wrong behavior of the `char` function [#18122](https://github.com/pingcap/tidb/pull/18122)
    - Fix the issue that the `ADMIN REPAIR TABLE` statement cannot parse integer in the expressions on the range partition [#17988](https://github.com/pingcap/tidb/pull/17988)
    - Fix the wrong behavior of the `SET CHARSET` statement [#17289](https://github.com/pingcap/tidb/pull/17289)
    - Fix the bug caused by the wrong collation setting which leads to the wrong result of the `collation` function [#17231](https://github.com/pingcap/tidb/pull/17231)
    - Fix the issue that `STR_TO_DATE`'s handling of the format tokens '%r', '%h' is inconsistent with that of MySQL [#18727](https://github.com/pingcap/tidb/pull/18727)
    - Fix issues that the TiDB version information is inconsistent with that of PD/TiKV in the `cluster_info` table [#18413](https://github.com/pingcap/tidb/pull/18413)
    - Fix the existent checks for pessimistic transactions [#19004](https://github.com/pingcap/tidb/pull/19004)
    - Fix the issue that executing `union select for update` might cause concurrent race [#19006](https://github.com/pingcap/tidb/pull/19006)
    - Fix the wrong query result when `apply` has a child of the `PointGet` operator [#19046](https://github.com/pingcap/tidb/pull/19046)
    - Fix the incorrect result that occurs when `IndexLookUp` is in the inner side of the `Apply` operator [#19496](https://github.com/pingcap/tidb/pull/19496)
    - Fix the incorrect result of `anti-semi-join` queries [#19472](https://github.com/pingcap/tidb/pull/19472)
    - Fix the incorrect result caused by the mistaken usage of `BatchPointGet` [#19456](https://github.com/pingcap/tidb/pull/19456)
    - Fix the incorrect result that occurs when `UnionScan` is in the inner side of the `Apply` operator [#19496](https://github.com/pingcap/tidb/pull/19496)
    - Fix the panic caused by using the `EXECUTE` statement to print an expensive query log [#17419](https://github.com/pingcap/tidb/pull/17419)
    - Fix the index join error when the join key is `ENUM` or `SET` [#19235](https://github.com/pingcap/tidb/pull/19235)
    - Fix the issue that the query range cannot be built when the `NULL` value exists on the index column [#19358](https://github.com/pingcap/tidb/pull/19358)
    - Fix the data race issue caused by updating the global configuration [#17964](https://github.com/pingcap/tidb/pull/17964)
    - Fix the panic issue occurs when modifying the character set in an uppercase schema [#19286](https://github.com/pingcap/tidb/pull/19286)
    - Fix an unexpected error caused by changing the temporary directory during the disk spill action [#18970](https://github.com/pingcap/tidb/pull/18970)
    - Fix the wrong hash key for the decimal type [#19131](https://github.com/pingcap/tidb/pull/19131)
    - Fix the issue that the `PointGet` and `BatchPointGet` operators do not consider the partition selection syntax and get incorrect results [#19141](https://github.com/pingcap/tidb/issues/19141)
    - Fix the incorrect results when using the `Apply` operator together with the `UnionScan` operator [#19104](https://github.com/pingcap/tidb/issues/19104)
    - Fix the bug that causes the indexed virtual generated column to return wrong value [#17989](https://github.com/pingcap/tidb/issues/17989)
    - Add the lock for runtime statistics to fix a panic caused by concurrent execution [#18983](https://github.com/pingcap/tidb/pull/18983)

+ TiKV

    - Speed up leader election when Hibernate Region is enabled [#8292](https://github.com/tikv/tikv/pull/8292)
    - Fix the memory leak issue during scheduling [#8357](https://github.com/tikv/tikv/pull/8357)
    - Add the `hibernate-timeout` configuration item to prevent the leader from becoming hibernate too fast [#8208](https://github.com/tikv/tikv/pull/8208)

+ PD

    - Fix the bug that the TSO request might fail at the time of leader change [#2666](https://github.com/tikv/pd/pull/2666)
    - Fix the issue that sometimes Region replicas cannot be scheduled to the optimal state when placement rules are enabled [#2720](https://github.com/tikv/pd/pull/2720)
    - Fix the issue that `Balance Leader` does not work when placement rules are enabled [#2726](https://github.com/tikv/pd/pull/2726)
    - Fix the issue that unhealthy stores are not filtered from store load statistics [#2805](https://github.com/tikv/pd/pull/2805)

+ TiFlash

    - Fix the issue that TiFlash cannot start normally after upgrading from an earlier version if the name of the database or table contains special characters
    - Fix the issue that the TiFlash process cannot exit if any exceptions are thrown during initialization

+ Tools

    + Backup & Restore (BR)

        - Fix the issue of duplicated calculation of total KV and total bytes in the backup summary log [#472](https://github.com/pingcap/br/pull/472)
        - Fix the issue that the import mode does not work in the first 5 minutes after switching to this mode [#473](https://github.com/pingcap/br/pull/473)

    + Dumpling

        - Fix the issue that FTWRL lock is not released in time [#128](https://github.com/pingcap/dumpling/pull/128)

    + TiCDC

        - Fix the issue that the failed `changefeed` cannot be removed [#782](https://github.com/pingcap/tiflow/pull/782)
        - Fix invalid `delete` events by selecting one unique index as the handle index [#787](https://github.com/pingcap/tiflow/pull/787)
        - Fix the bug that GC safepoint is forwarded beyond the checkpoint of stopped `changefeed` [#797](https://github.com/pingcap/tiflow/pull/797)
        - Fix the bug that the network I/O waiting blocks tasks to exit [#825](https://github.com/pingcap/tiflow/pull/825)
        - Fix the bug that some unnecessary data might be mistakenly replicated to the downstream [#743](https://github.com/pingcap/tiflow/issues/743)

    + TiDB Lightning

        - Fix the syntax error on empty binary/hex literals when using TiDB backend [#357](https://github.com/pingcap/tidb-lightning/pull/357)
