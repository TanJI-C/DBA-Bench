# Bug fixes across TiDB, TiKV, PD, and TiFlash section start

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.4.md`
- Source Title: `TiDB 5.1.4 Release Notes`
- Source Heading Path: `TiDB 5.1.4 Release Notes > Bug fixes`
- Source Line Ranges: `61-120`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `ticdc`, `tiup`
- Topic Tags: `release-notes`, `bug-fixes`, `memory-leak`, `slow-log`, `panic`, `wrong-results`, `join`, `batchcommands`, `data-inconsistency`, `window-functions`, `vectorized-expression`, `mpp`, `gc`, `deadlock`, `resolved-ts`, `resource-metering`, `grafana`, `scheduling`, `leader-election`, `hotspot`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0233_e4d8e1f44f`
- Source ID: `tidb-docs-8.1:releases/release-5.1.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `875e4d9618a2a74470f77e8f1d46bef0eccfaaa55367c600776f22703c64847f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.1.4 bug fixes related to specific errors, wrong results, panics, memory leaks, MPP issues, TiKV GC and resolved_ts behavior, or PD scheduling and hotspot fixes.
- Retrieval Keywords: TiDB 5.1.4 Release Notes, Bug fixes, tidb_analyze_version, memory leak, MaxDays, MaxBackups, slow log, INSERT ... SELECT ... ON DUPLICATE KEY UPDATE, panic, JOIN on ENUM type columns, INDEX HASH JOIN, send on closed channel, BatchCommands, max-batch-size, optimistic transaction mode, data index inconsistency, window functions, Decimal to String, GREATEST, tidb_enable_vectorized_expression, optimizer cache invalid plans, microsecond function, hour function, ALTER TABLE.. ADD INDEX, MPP node, MPP task ID, INDEX OUT OF RANGE, invalid cop task execution summaries length, tidb_skip_isolation_level_check, tiup bench, unsafe_destroy_range, GC worker, destroying a peer high latency, any_value, Prepare Merge, deadlock, flame graphs, prewrite request, pessimistic transactions, resource-metering.enabled, resolved_ts, GC can not work, tikv-ctl, down TiKV node causes the resolved timestamp to lag, Region merge, ConfChange, Snapshot, reverse table scan, negative sign when the decimal divide result is zero, TiCDC panic when the downstream database is missing, Congest error, batch messages are too large, Grafana dashboard, region scatterer, flow-round-by-digit, slow leader election, stuck region syncer, evict leader scheduler, cold hotspot data, scheduling operator cannot fail fast
- Follow-up Guidance: This chunk starts the Bug fixes section and the supplied content ends at the TiFlash heading without further TiFlash bug-fix details.
- Classification Note: This is a release-notes bug-fixes chunk listing corrected issues across TiDB, TiKV, and PD, with the TiFlash bug-fixes section header at the end.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix a memory leak bug that occurs when the system variable `tidb_analyze_version` is set to `2` [#32499](https://github.com/pingcap/tidb/issues/32499)
    - Fix the issue that the `MaxDays` and `MaxBackups` configurations do not take effect for the slow log [#25716](https://github.com/pingcap/tidb/issues/25716)
    - Fix the issue that executing the `INSERT ... SELECT ... ON DUPLICATE KEY UPDATE` statement gets panic [#28078](https://github.com/pingcap/tidb/issues/28078)
    - Fix the wrong result that might occur when performing `JOIN` on `ENUM` type columns [#27831](https://github.com/pingcap/tidb/issues/27831)
    - Fix the issue that INDEX HASH JOIN returns the `send on closed channel` error [#31129](https://github.com/pingcap/tidb/issues/31129)
    - Fix the issue that using the [`BatchCommands`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#max-batch-size) API might block sending TiDB requests to TiKV in some rare cases [#32500](https://github.com/pingcap/tidb/issues/32500)
    - Fix the issue of potential data index inconsistency in optimistic transaction mode [#30410](https://github.com/pingcap/tidb/issues/30410)
    - Fix the issue that window functions might return different results when using a transaction or not [#29947](https://github.com/pingcap/tidb/issues/29947)
    - Fix the issue that the length information is wrong when casting `Decimal` to `String` [#29417](https://github.com/pingcap/tidb/issues/29417)
    - Fix the issue that the `GREATEST` function returns incorrect result that occurs when setting the `tidb_enable_vectorized_expression` vectorized expression to `off` [#29434](https://github.com/pingcap/tidb/issues/29434)
    - Fix the issue that the optimizer might cache invalid plans for `join` in some cases [#28087](https://github.com/pingcap/tidb/issues/28087)
    - Fix wrong results of the `microsecond` and `hour` functions in vectorized expressions [#29244](https://github.com/pingcap/tidb/issues/29244) [#28643](https://github.com/pingcap/tidb/issues/28643)
    - Fix the TiDB panic when executing the `ALTER TABLE.. ADD INDEX` statement in some cases [#27687](https://github.com/pingcap/tidb/issues/27687)
    - Fix a bug that the availability detection of MPP node does not work in some corner cases [#3118](https://github.com/pingcap/tics/issues/3118)
    - Fix the `DATA RACE` issue when assigning `MPP task ID` [#27952](https://github.com/pingcap/tidb/issues/27952)
    - Fix the `INDEX OUT OF RANGE` error for a MPP query after deleting an empty `dual table` [#28250](https://github.com/pingcap/tidb/issues/28250)
    - Fix the issue of false positive error log `invalid cop task execution summaries length` for MPP queries [#1791](https://github.com/pingcap/tics/issues/1791)
    - Fix the issue that SET GLOBAL tidb_skip_isolation_level_check=1 doesn't affect new session settings [#27897](https://github.com/pingcap/tidb/issues/27897)
    - Fix the `index out of range` issue that occurs when `tiup bench` runs for a long time [#26832](https://github.com/pingcap/tidb/issues/26832)

+ TiKV

    - Fix a bug that TiKV cannot delete a range of data (`unsafe_destroy_range` cannot be executed) when the GC worker is busy [#11903](https://github.com/tikv/tikv/issues/11903)
    - Fix the issue that destroying a peer might cause high latency [#10210](https://github.com/tikv/tikv/issues/10210)
    - Fix a bug that the `any_value` function returns a wrong result when regions are empty [#11735](https://github.com/tikv/tikv/issues/11735)
    - Fix the issue that deleting an uninitialized replica might cause an old replica to be recreated [#10533](https://github.com/tikv/tikv/issues/10533)
    - Fix the metadata corruption issue when `Prepare Merge` is triggered after a new election is finished but the isolated peer is not informed [#11526](https://github.com/tikv/tikv/issues/11526)
    - Fix the deadlock issue that happens occasionally when coroutines run too fast [#11549](https://github.com/tikv/tikv/issues/11549)
    - Fix the potential deadlock and memory leak issues when profiling flame graphs [#11108](https://github.com/tikv/tikv/issues/11108)
    - Fix the rare data inconsistency issue when retrying a prewrite request in pessimistic transactions [#11187](https://github.com/tikv/tikv/issues/11187)
    - Fix a bug that the configuration `resource-metering.enabled` does not work [#11235](https://github.com/tikv/tikv/issues/11235)
    - Fix the issue that some coroutines leak in `resolved_ts` [#10965](https://github.com/tikv/tikv/issues/10965)
    - Fix the issue of reporting false "GC can not work" alert under low write flow [#9910](https://github.com/tikv/tikv/issues/9910)
    - Fix a bug that tikv-ctl cannot return the correct Region-related information [#11393](https://github.com/tikv/tikv/issues/11393)
    - Fix the issue that a down TiKV node causes the resolved timestamp to lag [#11351](https://github.com/tikv/tikv/issues/11351)
    - Fix a panic issue that occurs when Region merge, ConfChange, and Snapshot happen at the same time in extreme conditions [#11475](https://github.com/tikv/tikv/issues/11475)
    - Fix the issue that TiKV cannot detect the memory lock when TiKV performs a reverse table scan [#11440](https://github.com/tikv/tikv/issues/11440)
    - Fix the issue of negative sign when the decimal divide result is zero [#29586](https://github.com/pingcap/tidb/issues/29586)
    - Fix a memory leak caused by the monitoring data of statistics threads [#11195](https://github.com/tikv/tikv/issues/11195)
    - Fix the issue of TiCDC panic that occurs when the downstream database is missing [#11123](https://github.com/tikv/tikv/issues/11123)
    - Fix the issue that TiCDC adds scan retries frequently due to the Congest error [#11082](https://github.com/tikv/tikv/issues/11082)
    - Fix the issue that batch messages are too large in Raft client implementation [#9714](https://github.com/tikv/tikv/issues/9714)
    - Collapse some uncommon storage-related metrics in Grafana dashboard [#11681](https://github.com/tikv/tikv/issues/11681)

+ PD

    - Fix a bug that the schedule generated by the region scatterer might decrease the number of peers [#4565](https://github.com/tikv/pd/issues/4565)
    - Fix the issue that Region statistics are not affected by `flow-round-by-digit` [#4295](https://github.com/tikv/pd/issues/4295)
    - Fix slow leader election caused by stuck region syncer [#3936](https://github.com/tikv/pd/issues/3936)
    - Support that the evict leader scheduler can schedule regions with unhealthy peers [#4093](https://github.com/tikv/pd/issues/4093)
    - Fix the issue that the cold hotspot data cannot be deleted from the hotspot statistics [#4390](https://github.com/tikv/pd/issues/4390)
    - Fix a panic issue that occurs after the TiKV node is removed [#4344](https://github.com/tikv/pd/issues/4344)
    - Fix the issue that the scheduling operator cannot fail fast because the target store is down [#3353](https://github.com/tikv/pd/issues/3353)

+ TiFlash
