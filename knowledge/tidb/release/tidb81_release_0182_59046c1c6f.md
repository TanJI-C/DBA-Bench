# 4.0.3 bug fixes across TiDB, TiKV, PD, Dashboard, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.3.md`
- Source Title: `TiDB 4.0.3 Release Notes`
- Source Heading Path: `TiDB 4.0.3 Release Notes > Bug Fixes`
- Source Line Ranges: `102-174`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`, `tiflash`, `ticdc`, `br`, `dumpling`, `lightning`
- Topic Tags: `release-notes`, `bug-fixes`, `stability`, `correctness`, `tls`, `tso`, `placement-rules`, `safepoint`, `memory-leak`, `backup`, `dump`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0182_59046c1c6f`
- Source ID: `tidb-docs-8.1:releases/release-4.0.3.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `55a197e41a942825fbb3c500394e5f6d7f86bc05fb00217ece5b3e314fdbaf59`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.3#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.3 bug fixes across TiDB, TiKV, PD, TiDB Dashboard, TiFlash, and related tools for issues involving execution errors, stale reads, TSO, placement rules, safepoint, TLS, backup, dump, or replication.
- Retrieval Keywords: TiDB 4.0.3 Release Notes, Bug Fixes, IndexHashJoin, IndexMergeJoin, Index Join, ADMIN REPAIR TABLE, REPLACE INTO, generated columns, new collation, Green GC, TiFlash engine, gRPC transportReader, OOM error, stale data during merging, min/max function, TSO stream, getSchedulers, balance-leader-scheduler, placement rules, service safepoint, BR, dumpling, hot region scheduler, store limit, TiDB Dashboard, TLS scenarios, TiFlash crashes after renaming the primary key column, Learner Read, Remove Region, TiCDC leaks memory, unquoted table name, backup time might be negative, Dumpling omits the NULL value, --r, TiDB Lightning --log-file, TiDB Binlog, Drainer, checkpoint
- Follow-up Guidance: This chunk groups the fixes by component: TiDB, TiKV, PD, TiDB Dashboard, TiFlash, and tools including TiCDC, BR, Dumpling, TiDB Lightning, and TiDB Binlog.
- Classification Note: The content is classified as a release-notes bug-fixes entry because it enumerates resolved defects in TiDB 4.0.3 across multiple components and tools.

## Official Source Content

## Bug Fixes

+ TiDB

    - Return an error instead of an empty set for `IndexHashJoin` when an error occurs during execution [#18586](https://github.com/pingcap/tidb/pull/18586)
    - Fix the recurring panic when gRPC transportReader is broken [#18562](https://github.com/pingcap/tidb/pull/18562)
    - Fix the issue that Green GC does not scan locks on offline stores which might cause data incompleteness [#18550](https://github.com/pingcap/tidb/pull/18550)
    - Forbid processing a non-read-only statement using TiFlash engine [#18534](https://github.com/pingcap/tidb/pull/18534)
    - Return the actual error message when a query connection panics [#18500](https://github.com/pingcap/tidb/pull/18500)
    - Fix the issue that the `ADMIN REPAIR TABLE` execution fails to reload the table metadata on the TiDB node [#18323](https://github.com/pingcap/tidb/pull/18323)
    - Fix the data inconsistency issue occurred because the lock of a written and deleted primary key in one transaction is resolved by another transaction [#18291](https://github.com/pingcap/tidb/pull/18291)
    - Make spilling disk work well [#18288](https://github.com/pingcap/tidb/pull/18288)
    - Fix the error reported when the `REPLACE INTO` statement works on the table that contains generated columns [#17907](https://github.com/pingcap/tidb/pull/17907)
    - Return the OOM error when the `IndexHashJoin` and `IndexMergeJoin` workers panic [#18527](https://github.com/pingcap/tidb/pull/18527)
    - Fix the bug that the execution of `Index Join` might return wrong results in special cases when the index used by `Index Join` contains the integer primary key [#18565](https://github.com/pingcap/tidb/pull/18565)
    - Fix the issue that when the new collation is enabled on the cluster, the data updated on columns with the new collation in a transaction cannot be read through the unique index [#18703](https://github.com/pingcap/tidb/pull/18703)

+ TiKV

    - Fix the issue that reads might get stale data during merging [#8113](https://github.com/tikv/tikv/pull/8113)
    - Fix the issue that collation does not work on the `min`/`max` function when aggregation is pushed down to TiKV [#8108](https://github.com/tikv/tikv/pull/8108)

+ PD

    - Fix the issue that creating TSO stream might be blocked for a while if the server crashes [#2648](https://github.com/pingcap/pd/pull/2648)
    - Fix the issue that `getSchedulers` might cause a data race [#2638](https://github.com/pingcap/pd/pull/2638)
    - Fix the issue that deleting the scheduler might cause deadlocks [#2637](https://github.com/pingcap/pd/pull/2637)
    - Fix the bug that placement rules are not considered when `balance-leader-scheduler` is enabled [#2636](https://github.com/pingcap/pd/pull/2636)
    - Fix the issue that sometimes service `safepoint` cannot be set properly, which might make BR and dumpling fail [#2635](https://github.com/pingcap/pd/pull/2635)
    - Fix the issue that the target store in `hot region scheduler` is incorrectly selected [#2627](https://github.com/pingcap/pd/pull/2627)
    - Fix the issue that the TSO request might take too long when PD leader is switched [#2622](https://github.com/pingcap/pd/pull/2622)
    - Fix the issue of stale scheduler after leader change [#2608](https://github.com/pingcap/pd/pull/2608)
    - Fix the issue that sometimes replicas of a Region cannot be adjusted to the best location when placement rules are enabled [#2605](https://github.com/pingcap/pd/pull/2605)
    - Fix the issue that the deployment path of the store is not updated according to the change of deployment directory [#2600](https://github.com/pingcap/pd/pull/2600)
    - Prevent `store limit` from changing to zero [#2588](https://github.com/pingcap/pd/pull/2588)

+ TiDB Dashboard

    - Fix the TiDB connection error when TiDB is scaled out [#689](https://github.com/pingcap-incubator/tidb-dashboard/pull/689)
    - Fix the issue that TiFlash instances are not displayed in the log searching page [#680](https://github.com/pingcap-incubator/tidb-dashboard/pull/680)
    - Fix the issue of metric selection reset after refreshing the overview page [#663](https://github.com/pingcap-incubator/tidb-dashboard/pull/663)
    - Fix a connection issue in some TLS scenarios [#660](https://github.com/pingcap-incubator/tidb-dashboard/pull/660)
    - Fix the issue that the language dropdown box is not displayed correctly in some cases [#677](https://github.com/pingcap-incubator/tidb-dashboard/pull/677)

+ TiFlash

    - Fix the issue that TiFlash crashes after renaming the primary key column
    - Fix the issue that concurrent `Learner Read` and `Remove Region` might cause deadlocks

+ Tools

    + TiCDC

        - Fix the issue that TiCDC leaks memory in some cases [#704](https://github.com/pingcap/tiflow/pull/704)
        - Fix the issue that unquoted table name causes the SQL syntax error [#676](https://github.com/pingcap/tiflow/pull/676)
        - Fix the issue that the processor does not fully exit after `p.stop` is called [#693](https://github.com/pingcap/tiflow/pull/693)

    + Backup & Restore (BR)

        - Fix the issue that the backup time might be negative [#405](https://github.com/pingcap/br/pull/405)

    + Dumpling

        - Fix the issue that Dumpling omits the `NULL` value when `--r` is specified [#119](https://github.com/pingcap/dumpling/pull/119)
        - Fix the bug that flushing tables might not work for tables to dump [#117](https://github.com/pingcap/dumpling/pull/117)

    + TiDB Lightning

        - Fix the issue that `--log-file` does not take effect [#345](https://github.com/pingcap/tidb-lightning/pull/345)

    + TiDB Binlog

        - Fix the issue that when TiDB Binlog replicates data to the downstream with TLS enabled, Drainer cannot be started which occurs because TLS is not enabled on the database driver used to update the checkpoint [#988](https://github.com/pingcap/tidb-binlog/pull/988)
