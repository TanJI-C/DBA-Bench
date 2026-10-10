# TiDB 5.2.2 bug fixes for TiDB TiKV PD and TiFlash

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.2.2.md`
- Source Title: `TiDB 5.2.2 Release Notes`
- Source Heading Path: `TiDB 5.2.2 Release Notes > Bug Fixes`
- Source Line Ranges: `43-105`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `lightning`, `br`, `sql`
- Topic Tags: `bug-fixes`, `plan-cache`, `partition-pruning`, `mpp`, `authentication`, `auto-analyze`, `backup-restore`, `tls`, `precheck`, `collation`, `statistics`, `raft`, `gc`, `scheduler`, `startup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0244_ffe7de4a52`
- Source ID: `tidb-docs-8.1:releases/release-5.2.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9ca551d9c2ab55707cb8ed9b8ed22af9feefba6613d00879c705bc6178d3d38`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.2.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.2.2.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB 5.2.2 bug fixes affecting TiDB, TiKV, PD, or TiFlash, especially for planner behavior, MPP, Lightning, BR, TLS, collation, Raft, GC, schedulers, or startup issues.
- Retrieval Keywords: TiDB 5.2.2 bug fixes, plan-cache cannot detect changes of unsigned flags, wrong partition pruning, planner might cache invalid plans for join, wrong index hash join enum, recycling idle connection might block sending requests, TiDB Lightning panic checksum, date_add date_sub wrong results, hour function vectorized expression, connecting to MySQL 5.1 or an older client version, auto analyze might be triggered out of the specified time, tidb_snapshot, BR is not working for clusters with many missing-peer regions, tidb_cast to Int32 is not supported, DECIMAL overflow, MPP node availability detection, MPP task ID, INDEX OUT OF RANGE, invalid cop task execution summaries length, cannot found column in Schema column, TiDB might panic when TiFlash is shutting down, Remove the support for insecure 3DES, offline TiKV nodes during pre-check, pre-check cost too much time, between infer wrong collation, group_concat collation, extract function negative duration, NO_UNSIGNED_SUBTRACTION, Remove useless gRPC logs, data too long error when dumping statistics, TIDB_TRX, CDC adds scan retries frequently due to the Congest error, raft connection is broken when the channel is full, batch messages are too large in Raft client implementation, resolved_ts, response exceeds 4 GiB, snapshot Garbage Collection GC, PD incorrectly delete the peers with data and in pending status, PD does not fix down peers in time, scatter range scheduler cannot schedule empty regions, hot region scheduler, slow leader election caused by stuck region syncer, TiFlash fails to start up, library nsl
- Follow-up Guidance: A separate chunk in the same source lists TiCDC and TiDB Binlog bug fixes for TiDB 5.2.2.
- Classification Note: This is a bug-fix release chunk because the official content enumerates fixed issues by component under the Bug Fixes section.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix the issue that plan-cache cannot detect changes of unsigned flags [#28254](https://github.com/pingcap/tidb/issues/28254)
    - Fix the wrong partition pruning when the partition function is out of range [#28233](https://github.com/pingcap/tidb/issues/28233)
    - Fix the issue that planner might cache invalid plans for `join` in some cases [#28087](https://github.com/pingcap/tidb/issues/28087)
    - Fix wrong index hash join when hash column type is enum [#27893](https://github.com/pingcap/tidb/issues/27893)
    - Fix a batch client bug that recycling idle connection might block sending requests in some rare cases [#27688](https://github.com/pingcap/tidb/pull/27688)
    - Fix the TiDB Lightning panic issue when it fails to perform checksum on a target cluster [#27686](https://github.com/pingcap/tidb/pull/27686)
    - Fix wrong results of the `date_add` and `date_sub` functions in some cases [#27232](https://github.com/pingcap/tidb/issues/27232)
    - Fix wrong results of the `hour` function in vectorized expression [#28643](https://github.com/pingcap/tidb/issues/28643)
    - Fix the authenticating issue when connecting to MySQL 5.1 or an older client version  [#27855](https://github.com/pingcap/tidb/issues/27855)
    - Fix the issue that auto analyze might be triggered out of the specified time when a new index is added [#28698](https://github.com/pingcap/tidb/issues/28698)
    - Fix a bug that setting any session variable invalidates `tidb_snapshot` [#28683](https://github.com/pingcap/tidb/pull/28683)
    - Fix a bug that BR is not working for clusters with many missing-peer regions [#27534](https://github.com/pingcap/tidb/issues/27534)
    - Fix the unexpected error like `tidb_cast to Int32 is not supported` when the unsupported `cast` is pushed down to TiFlash [#23907](https://github.com/pingcap/tidb/issues/23907)
    - Fix the issue that `DECIMAL overflow` is missing in the `%s value is out of range in '%s'`error message  [#27964](https://github.com/pingcap/tidb/issues/27964)
    - Fix a bug that the availability detection of MPP node does not work in some corner cases [#3118](https://github.com/pingcap/tics/issues/3118)
    - Fix the `DATA RACE` issue when assigning `MPP task ID` [#27952](https://github.com/pingcap/tidb/issues/27952)
    - Fix the `INDEX OUT OF RANGE` error for a MPP query after deleting an empty `dual table`. [#28250](https://github.com/pingcap/tidb/issues/28250)
    - Fix the issue of false positive error log `invalid cop task execution summaries length` for MPP queries [#1791](https://github.com/pingcap/tics/issues/1791)
    - Fix the issue of error log `cannot found column in Schema column` for MPP queries [#28149](https://github.com/pingcap/tidb/pull/28149)
    - Fix the issue that TiDB might panic when TiFlash is shutting down [#28096](https://github.com/pingcap/tidb/issues/28096)
    - Remove the support for insecure 3DES (Triple Data Encryption Algorithm) based TLS cipher suites [#27859](https://github.com/pingcap/tidb/pull/27859)
    - Fix the issue that Lightning connects to offline TiKV nodes during pre-check and causes import failures [#27826](https://github.com/pingcap/tidb/pull/27826)
    - Fix the issue that pre-check cost too much time when importing many files to tables [#27605](https://github.com/pingcap/tidb/issues/27605)
    - Fix the issue that rewriting expressions makes `between` infer wrong collation [#27146](https://github.com/pingcap/tidb/issues/27146)
    - Fix the issue that `group_concat` function did not consider the collation [#27429](https://github.com/pingcap/tidb/issues/27429)
    - Fix the result wrong that occurs when the argument of the `extract` function is a negative duration [#27236](https://github.com/pingcap/tidb/issues/27236)
    - Fix the issue that creating partition fails if `NO_UNSIGNED_SUBTRACTION` is set [#26765](https://github.com/pingcap/tidb/issues/26765)
    - Avoid expressions with side effects in column pruning and aggregation pushdown [#27106](https://github.com/pingcap/tidb/issues/27106)
    - Remove useless gRPC logs [#24190](https://github.com/pingcap/tidb/issues/24190)
    - Limit the valid decimal length to fix precision-related issues [#3091](https://github.com/pingcap/tics/issues/3091)
    - Fix the issue of a wrong way to check for overflow in `plus` expression [#26977](https://github.com/pingcap/tidb/issues/26977)
    - Fix the issue of `data too long` error when dumping statistics from the table with `new collation` data [#27024](https://github.com/pingcap/tidb/issues/27024)
    - Fix the issue that the retried transactions' statements are not included in `TIDB_TRX` [#28670](https://github.com/pingcap/tidb/pull/28670)

+ TiKV

    - Fix the issue that CDC adds scan retries frequently due to the Congest error [#11082](https://github.com/tikv/tikv/issues/11082)
    - Fix the issue that the raft connection is broken when the channel is full [#11047](https://github.com/tikv/tikv/issues/11047)
    - Fix the issue that batch messages are too large in Raft client implementation [#9714](https://github.com/tikv/tikv/issues/9714)
    - Fix the issue that some coroutines leak in `resolved_ts` [#10965](https://github.com/tikv/tikv/issues/10965)
    - Fix a panic issue that occurs to the coprocessor when the size of response exceeds 4 GiB [#9012](https://github.com/tikv/tikv/issues/9012)
    - Fix the issue that snapshot Garbage Collection (GC) misses GC snapshot files when snapshot files cannot be garbage collected [#10813](https://github.com/tikv/tikv/issues/10813)
    - Fix a panic issue caused by timeout when processing Coprocessor requests [#10852](https://github.com/tikv/tikv/issues/10852)

+ PD

    - Fix the issue that PD incorrectly delete the peers with data and in pending status because the number of peers exceeds the number of configured peers [#4045](https://github.com/tikv/pd/issues/4045)
    - Fix the issue that PD does not fix down peers in time [#4077](https://github.com/tikv/pd/issues/4077)
    - Fix the issue that the scatter range scheduler cannot schedule empty regions [#4118](https://github.com/tikv/pd/pull/4118)
    - Fix the issue that the key manager cost too much CPU [#4071](https://github.com/tikv/pd/issues/4071)
    - Fix the data race issue that might occur when setting configurations of hot region scheduler [#4159](https://github.com/tikv/pd/issues/4159)
    - Fix slow leader election caused by stuck region syncer [#3936](https://github.com/tikv/pd/issues/3936)

+ TiFlash

    - Fix the issue that TiFlash fails to start up on some platforms due to the absence of library `nsl`

+ Tools
