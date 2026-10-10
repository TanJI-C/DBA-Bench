# TiDB 5.1.2 bug fixes across database, storage, scheduling, analytics, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.2.md`
- Source Title: `TiDB 5.1.2 Release Notes`
- Source Heading Path: `TiDB 5.1.2 Release Notes > Bug fixes`
- Source Line Ranges: `72-144`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `dumpling`, `ticdc`
- Topic Tags: `release-notes`, `bug-fixes`, `wrong-results`, `panic`, `deadlock`, `locking`, `rollback`, `disk-full`, `data-inconsistency`, `mpp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0229_dba1b70d30`
- Source ID: `tidb-docs-8.1:releases/release-5.1.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2b74b417530198dab0fe194acbc0fbcdb8991361466653414a4cded45aa94e74`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.1.2 bug fixes affecting wrong results, panic, deadlock, locking, rollback, disk full, data inconsistency, MPP, or tool behavior.
- Retrieval Keywords: TiDB 5.1.2 bug fixes, index hash join ENUM wrong results, pd is timeout, can not found column in Schema column, TiDB might panic when TiFlash is shutting down, CTE dead lock IndexLookupJoin, INFORMATION_SCHEMA.DEADLOCKS, TABLESAMPLE partitioned tables, /debug/sub-optimal-plan, SELECT FOR UPDATE normal table joins partitioned table, PointGet lite version of resolving lock, TiKV upgraded from v3.x panic, corrupted snapshot files disk full, slow log of TiKV coprocessor, slogger thread overloaded, Coprocessor requests times out panic, Titan enabled, rolled back to v5.0.x, left pessimistic locks, down peers in time, replication.max-replicas, hot Region scheduler, evict leader scheduler, TiFlash establish MPP connections, MPP queries hang forever, data inconsistency multiple disks, wrong results new collation, Backup & Restore average speed, Dumpling show table status incorrect results, sort-engine option
- Follow-up Guidance: The source enumerates bug fixes by component: TiDB, TiKV, PD, TiFlash, Backup & Restore (BR), and Dumpling.
- Classification Note: This is classified as a release chunk because it is the bug-fix section of the TiDB 5.1.2 release notes, organized by product component and issue type.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the potential wrong results of index hash join when the hash column is the `ENUM` type [#27893](https://github.com/pingcap/tidb/issues/27893)
    - Fix a batch client bug that recycle idle connection might block sending requests in some rare cases [#27678](https://github.com/pingcap/tidb/pull/27678)
    - Fix the issue that the overflow check of the `FLOAT64` type is different with that of MySQL [#23897](https://github.com/pingcap/tidb/issues/23897)
    - Fix the issue that TiDB returns an `unknow` error while it should return the `pd is timeout` error [#26147](https://github.com/pingcap/tidb/issues/26147)
    - Fix the wrong character set and collation for the `case when` expression [#26662](https://github.com/pingcap/tidb/issues/26662)
    - Fix the potential `can not found column in Schema column` error for MPP queries [#28148](https://github.com/pingcap/tidb/pull/28148)
    - Fix a bug that TiDB might panic when TiFlash is shutting down [#28096](https://github.com/pingcap/tidb/issues/28096)
    - Fix the issue of wrong range caused by using `enum like 'x%'` [#27130](https://github.com/pingcap/tidb/issues/27130)
    - Fix the Common Table Expression (CTE) dead lock issue when used with IndexLookupJoin [#27410](https://github.com/pingcap/tidb/issues/27410)
    - Fix a bug that retryable deadlocks are incorrectly recorded into the `INFORMATION_SCHEMA.DEADLOCKS` table [#27400](https://github.com/pingcap/tidb/issues/27400)
    - Fix the issue that the `TABLESAMPLE` query result from partitioned tables is not sorted as expected [#27349](https://github.com/pingcap/tidb/issues/27349)
    - Remove the unused `/debug/sub-optimal-plan` HTTP API  [#27265](https://github.com/pingcap/tidb/pull/27265)
    - Fix a bug that the query might return wrong results when the hash partitioned table deals with unsigned data [#26569](https://github.com/pingcap/tidb/issues/26569)
    - Fix a bug that creating partition fails if `NO_UNSIGNED_SUBTRACTION` is set [#26765](https://github.com/pingcap/tidb/issues/26765)
    - Fix the issue that the `distinct` flag is missing when `Apply` is converted to `Join` [#26958](https://github.com/pingcap/tidb/issues/26958)
    - Set a block duration for the newly recovered TiFlash node to avoid blocking queries during this time [#26897](https://github.com/pingcap/tidb/pull/26897)
    - Fix a bug that might occur when the CTE is referenced more than once [#26212](https://github.com/pingcap/tidb/issues/26212)
    - Fix a CTE bug when MergeJoin is used [#25474](https://github.com/pingcap/tidb/issues/25474)
    - Fix a bug that the `SELECT FOR UPDATE` statement does not correctly lock the data when a normal table joins a partitioned table [#26251](https://github.com/pingcap/tidb/issues/26251)
    - Fix the issue that the `SELECT FOR UPDATE` statement returns an error when a normal table joins a partitioned table [#26250](https://github.com/pingcap/tidb/issues/26250)
    - Fix the issue that `PointGet` does not use the lite version of resolving lock [#26562](https://github.com/pingcap/tidb/pull/26562)

+ TiKV

    - Fix a panic issue that occurs after TiKV is upgraded from v3.x to later versions [#10902](https://github.com/tikv/tikv/issues/10902)
    - Fix the potential disk full issue caused by corrupted snapshot files [#10813](https://github.com/tikv/tikv/issues/10813)
    - Make the slow log of TiKV coprocessor only consider the time spent on processing requests [#10841](https://github.com/tikv/tikv/issues/10841)
    - Drop log instead of blocking threads when the slogger thread is overloaded and the queue is filled up [#10841](https://github.com/tikv/tikv/issues/10841)
    - Fix a panic issue that occurs when processing Coprocessor requests times out [#10852](https://github.com/tikv/tikv/issues/10852)
    - Fix the TiKV panic issue that occurs when upgrading from a pre-5.0 version with Titan enabled [#10842](https://github.com/tikv/tikv/pull/10842)
    - Fix the issue that TiKV of a newer version cannot be rolled back to v5.0.x [#10842](https://github.com/tikv/tikv/pull/10842)
    - Fix the issue that TiKV might delete files before ingesting data to RocksDB [#10438](https://github.com/tikv/tikv/issues/10438)
    - Fix the parsing failure caused by the left pessimistic locks [#26404](https://github.com/pingcap/tidb/issues/26404)

+ PD

    - Fix the issue that PD does not fix the down peers in time [#4077](https://github.com/tikv/pd/issues/4077)
    - Fix the issue that the replica count of the default placement rules stays constant after `replication.max-replicas` is updated [#3886](https://github.com/tikv/pd/issues/3886)
    - Fix a bug that PD might panic when scaling out TiKV [#3868](https://github.com/tikv/pd/issues/3868)
    - Fix a bug that the hot Region scheduler cannot work when the cluster has the evict leader scheduler [#3697](https://github.com/tikv/pd/issues/3697)

+ TiFlash

    - Fix the issue of unexpected results when TiFlash fails to establish MPP connections
    - Fix the potential issue of data inconsistency that occurs when TiFlash is deployed on multiple disks
    - Fix a bug that MPP queries get wrong results when TiFlash server is under high load
    - Fix a potential bug that MPP queries hang forever
    - Fix the panic issue when operating store initialization and DDL simultaneously
    - Fix a bug of incorrect results that occurs when queries contain filters like `CONSTANT`, `<`, `<=`, `>`, `>=`, or `COLUMN`
    - Fix the potential panic issue when `Snapshot` is applied simultaneously with multiple DDL operations
    - Fix the issue that the store size in metrics is inaccurate under heavy writing
    - Fix the potential issue that TiFlash cannot garbage-collect the delta data after running for a long time
    - Fix the issue of wrong results when the new collation is enabled
    - Fix the potential panic issue that occurs when resolving locks
    - Fix a potential bug that metrics display wrong values

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that the average speed is not accurate during data backup and restore [#1405](https://github.com/pingcap/br/issues/1405)

    + Dumpling

        - Fix the issue that Dumpling is pending when `show table status` returns incorrect results in some MySQL versions (8.0.3 and 8.0.23) [#322](https://github.com/pingcap/dumpling/issues/322)
        - Fix the CLI compatibility issue with 4.0.x clusters on the default `sort-engine` option [#2373](https://github.com/pingcap/tiflow/issues/2373)

    + TiCDC
