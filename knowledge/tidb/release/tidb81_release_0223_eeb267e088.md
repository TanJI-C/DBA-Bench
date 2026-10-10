# Bug fixes for TiDB, TiKV, PD, and start of TiFlash

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.0.md`
- Source Title: `TiDB 5.1 Release Notes`
- Source Heading Path: `TiDB 5.1 Release Notes > Bug Fixes`
- Source Line Ranges: `255-308`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`
- Topic Tags: `bug-fixes`, `sql-correctness`, `optimizer`, `ddl`, `transactions`, `gc`, `plan-cache`, `mpp`, `collation`, `configuration`, `performance`, `leader-election`, `coprocessor`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0223_eeb267e088`
- Source ID: `tidb-docs-8.1:releases/release-5.1.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1eb94dacf7cdfc571a69d133c98fe88decf41729513143962ad914335c0229b0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.1 bug fixes across TiDB, TiKV, and PD involving wrong query results, optimizer and plan cache behavior, DDL rollback, GC, collation, MPP, coprocessor handling, TiKV startup or point get performance, or PD leader re-election and scheduler panic issues.
- Retrieval Keywords: TiDB 5.1 Bug Fixes, project elimination wrong result empty projection, wrong query results NULL values, Forbid generating MPP plans when the scan contains virtual columns, PointGet TableDual Plan Cache, IndexMerge plan for clustered indexes, BIT-type errors type inference, optimizer hints PointGet, DDL operations might fail when rolling back due to an error, binary literal constant index range, IN clause wrong results, string functions wrong results, REPLACE operations require both INSERT and DELETE privileges, TableDual plans binaries and bytes, prefix index and index join panic, prepared plan cache point get transaction, ascii_bin latin1_bin prefix index, ongoing transaction interrupted by the GC worker, new-collation new-row-format clustered index point query, HAVING clause panic, Apply and Join operators results go wrong, async commit primary lock fallen back cannot be resolved, fm-sketch duplicated records, ErrKeyExists pessimistic rollback, ANSI_QUOTES numeric literals, INSERT INTO table PARTITION ON DUPLICATE KEY UPDATE, GROUP BY and UNION index out of range, CONCAT function collation, collation_server global variable new sessions, coprocessor IN expression signed unsigned integer types, many empty Regions after batch ingesting SST files, TiKV cannot start up after the file dictionary file is damaged, TiCDC OOM reading old values, abort-on-panic configuration, point get performance regression when TiKV is not busy, PD Leader re-election is slow when there are many stores, removing the evict leader scheduler from a non-existent store, statistics are not updated after offline peers are merged
- Follow-up Guidance: This chunk also includes a TiKV addition of the `abort-on-panic` configuration for generating a core dump file when panic occurs, plus PD fixes for slow Leader re-election, evict leader scheduler removal panic, and stale statistics after offline peer merge.
- Classification Note: The official content is a release-notes bug-fix section covering self-managed components TiDB, TiKV, and PD, with one TiKV configuration addition listed alongside fixes.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix the issue that the execution result of project elimination might be wrong when the projection result is empty [#23887](https://github.com/pingcap/tidb/issues/23887)
    - Fix the issue of wrong query results when a column contains `NULL` values in some cases [#23891](https://github.com/pingcap/tidb/issues/23891)
    - Forbid generating MPP plans when the scan contains virtual columns [#23886](https://github.com/pingcap/tidb/issues/23886)
    - Fix the wrong reuse of `PointGet` and `TableDual` in Plan Cache [#23187](https://github.com/pingcap/tidb/issues/23187) [#23144](https://github.com/pingcap/tidb/issues/23144) [#23304](https://github.com/pingcap/tidb/issues/23304) [#23290](https://github.com/pingcap/tidb/issues/23290)
    - Fix the error that occurs when the optimizer builds the `IndexMerge` plan for clustered indexes [#23906](https://github.com/pingcap/tidb/issues/23906)
    - Fix the type inference of the BIT-type errors [#23832](https://github.com/pingcap/tidb/issues/23832)
    - Fix the issue that some optimizer hints do not take effect when the `PointGet` operator exists [#23570](https://github.com/pingcap/tidb/issues/23570)
    - Fix the issue that DDL operations might fail when rolling back due to an error [#23893](https://github.com/pingcap/tidb/issues/23893)
    - Fix the issue that the index range of the binary literal constant is incorrectly built [#23672](https://github.com/pingcap/tidb/issues/23672)
    - Fix the potential wrong results of the `IN` clause in some cases [#23889](https://github.com/pingcap/tidb/issues/23889)
    - Fix the wrong results of some string functions [#23759](https://github.com/pingcap/tidb/issues/23759)
    - Users now need both `INSERT` and `DELETE` privileges on a table to perform `REPLACE` operations [#23909](https://github.com/pingcap/tidb/issues/23909)
    - Users now need both `INSERT` and `DELETE` privileges on a table to perform `REPLACE` operations [#24070](https://github.com/pingcap/tidb/pull/24070)
    - Fix the wrong `TableDual` plans caused by incorrectly comparing binaries and bytes [#23846](https://github.com/pingcap/tidb/issues/23846)
    - Fix the panic issue caused by using the prefix index and index join in some cases [#24547](https://github.com/pingcap/tidb/issues/24547) [#24716](https://github.com/pingcap/tidb/issues/24716) [#24717](https://github.com/pingcap/tidb/issues/24717)
    - Fix the issue that the prepared plan cache of `point get` is incorrectly used by the `point get` statement in the transaction [#24741](https://github.com/pingcap/tidb/issues/24741)
    - Fix the issue of writing the wrong prefix index value when the collation is `ascii_bin` or `latin1_bin` [#24569](https://github.com/pingcap/tidb/issues/24569)
    - Fix the issue that the ongoing transaction might be interrupted by the GC worker [#24591](https://github.com/pingcap/tidb/issues/24591)
    - Fix a bug that the point query might get wrong on the clustered index when `new-collation` is enabled but `new-row-format` is disabled [#24541](https://github.com/pingcap/tidb/issues/24541)
    - Refactor the conversion of partition keys for shuffle hash join [#24490](https://github.com/pingcap/tidb/pull/24490)
    - Fix the panic issue that occurs when building the plan for queries that contain the `HAVING` clause [#24045](https://github.com/pingcap/tidb/issues/24045)
    - Fix the issue that the column pruning improvement causes the `Apply` and `Join` operators' results to go wrong [#23887](https://github.com/pingcap/tidb/issues/23887)
    - Fix a bug that the primary lock fallen back from async commit cannot be resolved [#24384](https://github.com/pingcap/tidb/issues/24384)
    - Fix a GC issue of statistics that might cause duplicated fm-sketch records [#24357](https://github.com/pingcap/tidb/pull/24357)
    - Avoid unnecessary pessimistic rollback when the pessimistic locking receives the `ErrKeyExists` error [#23799](https://github.com/pingcap/tidb/issues/23799)
    - Fix the issue that numeric literals cannot be recognized when the sql_mode contains `ANSI_QUOTES` [#24429](https://github.com/pingcap/tidb/issues/24429)
    - Forbid statements such as `INSERT INTO table PARTITION (<partitions>) ... ON DUPLICATE KEY UPDATE` to read data from non-listed partitions [#24746](https://github.com/pingcap/tidb/issues/24746)
    - Fix the potential `index out of range` error when a SQL statement contains both `GROUP BY` and `UNION` [#24281](https://github.com/pingcap/tidb/issues/24281)
    - Fix the issue that the `CONCAT` function incorrectly handles the collation [#24296](https://github.com/pingcap/tidb/issues/24296)
    - Fix the issue that the `collation_server` global variable does not take effect in new sessions [#24156](https://github.com/pingcap/tidb/pull/24156)

+ TiKV

    - Fix the issue that the coprocessor fails to properly handle the signed or unsigned integer types in the `IN` expression [#9821](https://github.com/tikv/tikv/issues/9821)
    - Fix the issue of many empty Regions after batch ingesting SST files [#964](https://github.com/pingcap/br/issues/964)
    - Fix a bug that TiKV cannot start up after the file dictionary file is damaged [#9886](https://github.com/tikv/tikv/issues/9886)
    - Fix a TiCDC OOM issue caused by reading old values [#9996](https://github.com/tikv/tikv/issues/9996) [#9981](https://github.com/tikv/tikv/issues/9981)
    - Fix the issue of empty value in the secondary index for the clustered primary key column when collation is `latin1_bin` [#24548](https://github.com/pingcap/tidb/issues/24548)
    - Add the `abort-on-panic` configuration, which allows TiKV to generate the core dump file when panic occurs. Users still need to correctly configure the environment to enable core dump [#10216](https://github.com/tikv/tikv/pull/10216)
    - Fix the performance regression issue of `point get` queries that occurs when TiKV is not busy [#10046](https://github.com/tikv/tikv/issues/10046)

+ PD

    - Fix the issue that the PD Leader re-election is slow when there are many stores [#3697](https://github.com/tikv/pd/issues/3697)

    - Fix the panic issue that occurs when removing the evict leader scheduler from a non-existent store [#3660](https://github.com/tikv/pd/issues/3660)
    - Fix the issue that the statistics are not updated after offline peers are merged [#3611](https://github.com/tikv/pd/issues/3611)

+ TiFlash
