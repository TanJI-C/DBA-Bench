# Bug fixes for TiDB and TiKV in 5.3.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.0.md`
- Source Title: `TiDB 5.3 Release Notes`
- Source Heading Path: `TiDB 5.3 Release Notes > Bug Fixes`
- Source Line Ranges: `317-374`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `lightning`, `br`, `tiflash`, `pd`
- Topic Tags: `bug-fixes`, `query-plans`, `partitioning`, `mpp`, `tls`, `lightning`, `backup-restore`, `raftstore`, `cdc`, `gc`, `performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0259_e609d8126a`
- Source ID: `tidb-docs-8.1:releases/release-5.3.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ce41295be55b676fc7d307f96ea4afc58d9ca23349e8baca2bfe27fcf6c1243e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 5.3.0 bug fixes for wrong execution plans, partition pruning, plan cache, MPP, Lightning, BR, TiFlash pushdown, TLS cipher suites, transaction visibility, or TiKV raftstore, CDC, GC, coprocessor, and scan performance issues.
- Retrieval Keywords: TiDB 5.3.0 Bug Fixes, wrong execution plan, shallow copy of schema columns, aggregation operators on partitioned tables, plan cache unsigned flags, wrong partition pruning, planner might cache invalid plans for join, IndexLookUpJoin enum, TiDB Lightning panic checksum, BR many missing-peer Regions, tidb_cast to Int32 is not supported, MPP task ID, invalid cop task execution summaries length, cannot found column in Schema column, 3DES TLS cipher suites, group_concat collation, TIDB_TRX, plugin_dir, CONVERT_TZ returns NULL, CREATE SCHEMA character_set_server collation_server, Raftstore deadlock when migrating Regions, CDC scan retries Congest error, resolved_ts coroutines leak, snapshot Garbage Collection misses GC snapshot files, poor scan performance MVCC Deletion versions compaction filter GC
- Follow-up Guidance: The chunk also includes related 5.3.0 fixes for PD in the following release notes section.
- Classification Note: This is a release-notes bug-fix summary covering multiple self-managed components, primarily TiDB and TiKV, under TiDB 5.3 Release Notes > Bug Fixes.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix an error that occurs during execution caused by the wrong execution plan. The wrong execution plan is caused by the shallow copy of schema columns when pushing down the aggregation operators on partitioned tables [#27797](https://github.com/pingcap/tidb/issues/27797) [#26554](https://github.com/pingcap/tidb/issues/26554)
    - Fix the issue that `plan cache` cannot detect changes of unsigned flags [#28254](https://github.com/pingcap/tidb/issues/28254)
    - Fix the wrong partition pruning when the partition function is out of range [#28233](https://github.com/pingcap/tidb/issues/28233)
    - Fix the issue that planner might cache invalid plans for `join` in some cases [#28087](https://github.com/pingcap/tidb/issues/28087)
    - Fix wrong `IndexLookUpJoin` when hash column type is `enum` [#27893](https://github.com/pingcap/tidb/issues/27893)
    - Fix a batch client bug that recycling idle connection might block sending requests in some rare cases [#27688](https://github.com/pingcap/tidb/pull/27688)
    - Fix the TiDB Lightning panic issue when it fails to perform checksum on a target cluster [#27686](https://github.com/pingcap/tidb/pull/27686)
    - Fix wrong results of the `date_add` and `date_sub` functions in some cases [#27232](https://github.com/pingcap/tidb/issues/27232)
    - Fix wrong results of the `hour` function in vectorized expression [#28643](https://github.com/pingcap/tidb/issues/28643)
    - Fix the authenticating issue when connecting to MySQL 5.1 or an older client version  [#27855](https://github.com/pingcap/tidb/issues/27855)
    - Fix the issue that auto analyze might be triggered out of the specified time when a new index is added [#28698](https://github.com/pingcap/tidb/issues/28698)
    - Fix a bug that setting any session variable invalidates `tidb_snapshot` [#28683](https://github.com/pingcap/tidb/pull/28683)
    - Fix a bug that BR is not working for clusters with many missing-peer Regions [#27534](https://github.com/pingcap/tidb/issues/27534)
    - Fix the unexpected error like `tidb_cast to Int32 is not supported` when the unsupported `cast` is pushed down to TiFlash [#23907](https://github.com/pingcap/tidb/issues/23907)
    - Fix the issue that `DECIMAL overflow` is missing in the `%s value is out of range in '%s'`error message  [#27964](https://github.com/pingcap/tidb/issues/27964)
    - Fix a bug that the availability detection of MPP node does not work in some corner cases [#3118](https://github.com/pingcap/tics/issues/3118)
    - Fix the `DATA RACE` issue when assigning `MPP task ID` [#27952](https://github.com/pingcap/tidb/issues/27952)
    - Fix the `INDEX OUT OF RANGE` error for a MPP query after deleting an empty `dual table` [#28250](https://github.com/pingcap/tidb/issues/28250)
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
    - Fix the wrong default value of the `plugin_dir` configuration [#28084](https://github.com/pingcap/tidb/issues/28084)
    - Fix the issue that the `CONVERT_TZ` function returns `NULL` when it is given a named timezone and a UTC offset [#8311](https://github.com/pingcap/tidb/issues/8311)
    - Fix the issue that `CREATE SCHEMA` does not use the character set specified by `character_set_server` and `collation_server` for new schemas if none are provided as part of the statement [#27214](https://github.com/pingcap/tidb/issues/27214)

+ TiKV

    - Fix the issue of unavailable TiKV caused by Raftstore deadlock when migrating Regions. The workaround is to disable the scheduling and restart the unavailable TiKV [#10909](https://github.com/tikv/tikv/issues/10909)
    - Fix the issue that CDC adds scan retries frequently due to the Congest error [#11082](https://github.com/tikv/tikv/issues/11082)
    - Fix the issue that the Raft connection is broken when the channel is full [#11047](https://github.com/tikv/tikv/issues/11047)
    - Fix the issue that batch messages are too large in Raft client implementation [#9714](https://github.com/tikv/tikv/issues/9714)
    - Fix the issue that some coroutines leak in `resolved_ts` [#10965](https://github.com/tikv/tikv/issues/10965)
    - Fix a panic issue that occurs to the coprocessor when the size of response exceeds 4 GiB [#9012](https://github.com/tikv/tikv/issues/9012)
    - Fix the issue that snapshot Garbage Collection (GC) misses GC snapshot files when snapshot files cannot be garbage collected [#10813](https://github.com/tikv/tikv/issues/10813)
    - Fix a panic issue caused by timeout when processing Coprocessor requests [#10852](https://github.com/tikv/tikv/issues/10852)
    - Fix a memory leak caused by monitoring data of statistics threads [#11195](https://github.com/tikv/tikv/issues/11195)
    - Fix a panic issue caused by getting the cgroup information from some platforms [#10980](https://github.com/tikv/tikv/pull/10980)
    - Fix the issue of poor scan performance because MVCC Deletion versions are not dropped by compaction filter GC [#11248](https://github.com/tikv/tikv/pull/11248)

+ PD
