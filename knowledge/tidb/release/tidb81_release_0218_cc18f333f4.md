# TiDB 5.0.6 bug fixes for TiDB and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.6.md`
- Source Title: `TiDB 5.0.6 Release Notes`
- Source Heading Path: `TiDB 5.0.6 Release Notes > Bug fixes`
- Source Line Ranges: `60-115`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `ticdc`, `lightning`
- Topic Tags: `release-notes`, `bug-fixes`, `transactions`, `mpp`, `planner`, `vectorized-expression`, `raft`, `gc`, `memory`, `panic`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0218_cc18f333f4`
- Source ID: `tidb-docs-8.1:releases/release-5.0.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7c547f69d5eb7d9a0b2cb7441e6e6031f715d8c37dbd5c82477062ba9ce70b07`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.0.6 bug fixes for TiDB and TiKV, especially specific panics, wrong results, MPP issues, Raft issues, GC or memory problems, and TiCDC-related fixes in TiKV.
- Retrieval Keywords: TiDB 5.0.6 bug fixes, optimistic transaction conflicts block each other, invalid cop task execution summaries length, DML and DDL statements executed concurrently panic, privilege check fail grant revoke global level privileges, ALTER TABLE ADD INDEX panic, enforce-mpp does not take effect, CASE WHEN ENUM panic, microsecond function vectorized expressions wrong results, auto analyze incomplete log information, hour function vectorized expression wrong results, tidb_cast to Int32 is not supported, MPP node availability detection, DATA RACE assigning MPP task ID, INDEX OUT OF RANGE MPP query dual table, inserting invalid date values concurrently panic, can not found column in Schema column, TiFlash is shutting down panic, join reorder index out of range, IF and CASE WHEN ENUM wrong results, CONCAT IFNULL TIME(3) wrong result, GREATEST LEAST unsigned BIGINT wrong results, JSON type column joins CHAR type column canceled, lazy existence check untouched key optimization data inconsistency, window functions different results when using a transaction or not, cast(integer as char) union string wrong results, casting Decimal to String length information wrong, Column in field list is ambiguous natural join, tidb_enable_vectorized_expression GREATEST inconsistent, planner might cache invalid plans for join, index out of range [1] with length 1 aggregation join, down TiKV node causes the resolved timestamp to lag, batch messages are too large in Raft client implementation, Region merge ConfChange Snapshot panic, reverse table scan memory lock, GC tasks might cause TiKV to be OOM, by-instance gRPC requests latency inaccurate, memory leak statistics threads, TiCDC panic downstream database is missing, TiCDC scan retries frequently due to the Congest error, Raft connection is broken when the channel is full, TiDB Lightning imports data files do not exist panic, Max Min Int64 signed integer wrong calculation result, node gets snapshots metadata accurately, backup thread pool leak
- Follow-up Guidance: The chunk groups the fixes by component and includes TiKV fixes for resolved timestamp lag, Raft client message size, GC-task OOM risk, monitoring-thread memory leak, and TiCDC-related panic and retry issues.
- Classification Note: This is a bug-fix release chunk because the official content enumerates corrected defects in TiDB and TiKV for TiDB 5.0.6.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that optimistic transaction conflicts might cause transactions to block each other [#11148](https://github.com/tikv/tikv/issues/11148)
    - Fix the issue of false positive error log `invalid cop task execution summaries length` for MPP queries [#1791](https://github.com/pingcap/tics/issues/1791)
    - Fix the panic that might occur when DML and DDL statements are executed concurrently [#30940](https://github.com/pingcap/tidb/issues/30940)
    - Fix the `privilege check fail` error when performing the `grant` and `revoke` operations to grant and revoke global level privileges [#29675](https://github.com/pingcap/tidb/issues/29675)
    - Fix the TiDB panic when executing the `ALTER TABLE.. ADD INDEX` statement in some cases [#27687](https://github.com/pingcap/tidb/issues/27687)
    - Fix the issue that the `enforce-mpp` configuration does not take effect in v5.0.4 [#29252](https://github.com/pingcap/tidb/issues/29252)
    - Fix the panic when using the `CASE WHEN` function on the `ENUM` data type [#29357](https://github.com/pingcap/tidb/issues/29357)
    - Fix wrong results of the `microsecond` function in vectorized expressions [#29244](https://github.com/pingcap/tidb/issues/29244)
    - Fix the issue of incomplete log information from the `auto analyze` result [#29188](https://github.com/pingcap/tidb/issues/29188)
    - Fix wrong results of the `hour` function in vectorized expression [#28643](https://github.com/pingcap/tidb/issues/28643)
    - Fix the unexpected error like `tidb_cast to Int32 is not supported` when the unsupported `cast` is pushed down to TiFlash [#23907](https://github.com/pingcap/tidb/issues/23907)
    - Fix a bug that the availability detection of MPP node does not work in some corner cases [#3118](https://github.com/pingcap/tics/issues/3118)
    - Fix the `DATA RACE` issue when assigning `MPP task ID` [#27952](https://github.com/pingcap/tidb/issues/27952)
    - Fix the `INDEX OUT OF RANGE` error for a MPP query after deleting an empty `dual table` [#28250](https://github.com/pingcap/tidb/issues/28250)
    - Fix the TiDB panic when inserting invalid date values concurrently [#25393](https://github.com/pingcap/tidb/issues/25393)
    - Fix the unexpected `can not found column in Schema column` error for queries in the MPP mode [#30980](https://github.com/pingcap/tidb/issues/30980)
    - Fix the issue that TiDB might panic when TiFlash is shutting down [#28096](https://github.com/pingcap/tidb/issues/28096)
    - Fix the unexpected `index out of range` error when the planner is doing join reorder [#24095](https://github.com/pingcap/tidb/issues/24095)
    - Fix wrong results of the control functions (such as `IF` and `CASE WHEN`) when using the `ENUM` type data as parameters of such functions [#23114](https://github.com/pingcap/tidb/issues/23114)
    - Fix the wrong result of `CONCAT(IFNULL(TIME(3))` [#29498](https://github.com/pingcap/tidb/issues/29498)
    - Fix wrong results of `GREATEST` and `LEAST` when passing in unsigned `BIGINT` arguments [#30101](https://github.com/pingcap/tidb/issues/30101)
    - Fix the issue that a SQL operation is canceled when its JSON type column joins its `CHAR` type column [#29401](https://github.com/pingcap/tidb/issues/29401)
    - Fix the data inconsistency issue caused by incorrect usage of lazy existence check and untouched key optimization [#30410](https://github.com/pingcap/tidb/issues/30410)
    - Fix the issue that window functions might return different results when using a transaction or not [#29947](https://github.com/pingcap/tidb/issues/29947)
    - Fix the issue that the SQL statements that contain `cast(integer as char) union string` return wrong results [#29513](https://github.com/pingcap/tidb/issues/29513)
    - Fix the issue that the length information is wrong when casting `Decimal` to `String` [#29417](https://github.com/pingcap/tidb/issues/29417)
    - Fix the issue that the `Column 'col_name' in field list is ambiguous` error is reported unexpectedly when a SQL statement contains natural join [#25041](https://github.com/pingcap/tidb/issues/25041)
    - Fix the issue that the `GREATEST` function returns inconsistent results due to different values of `tidb_enable_vectorized_expression` (set to `on` or `off`) [#29434](https://github.com/pingcap/tidb/issues/29434)
    - Fix the issue that the planner might cache invalid plans for `join` in some cases [#28087](https://github.com/pingcap/tidb/issues/28087)
    - Fix the issue that the `index out of range [1] with length 1` error is reported when a SQL statement evaluates an aggregation result on the result of join in some cases [#1978](https://github.com/pingcap/tics/issues/1978)

+ TiKV

    - Fix the issue that a down TiKV node causes the resolved timestamp to lag [#11351](https://github.com/tikv/tikv/issues/11351)
    - Fix the issue that batch messages are too large in Raft client implementation [#9714](https://github.com/tikv/tikv/issues/9714)
    - Fix a panic issue that occurs when Region merge, ConfChange, and Snapshot happen at the same time in extreme conditions [#11475](https://github.com/tikv/tikv/issues/11475)
    - Fix the issue that TiKV cannot detect the memory lock when TiKV perform a reverse table scan [#11440](https://github.com/tikv/tikv/issues/11440)
    - Fix the issue of negative sign when the decimal divide result is zero [#29586](https://github.com/pingcap/tidb/issues/29586)
    - Fix the issue that the accumulation of GC tasks might cause TiKV to be OOM (out of memory) [#11410](https://github.com/tikv/tikv/issues/11410)
    - Fix the issue that the average latency of the by-instance gRPC requests is inaccurate in TiKV metrics [#11299](https://github.com/tikv/tikv/issues/11299)
    - Fix a memory leak caused by monitoring data of statistics threads [#11195](https://github.com/tikv/tikv/issues/11195)
    - Fix the issue of TiCDC panic that occurs when the downstream database is missing [#11123](https://github.com/tikv/tikv/issues/11123)
    - Fix the issue that TiCDC adds scan retries frequently due to the Congest error [#11082](https://github.com/tikv/tikv/issues/11082)
    - Fix the issue that the Raft connection is broken when the channel is full [#11047](https://github.com/tikv/tikv/issues/11047)
    - Fix the issue of TiKV panic that occurs when the files do not exist when TiDB Lightning imports data [#10438](https://github.com/tikv/tikv/issues/10438)
    - Fix the issue that TiDB cannot correctly identify whether the `Int64` types in `Max`/`Min` functions are a signed integer or not, which causes the wrong calculation result of `Max`/`Min` [#10158](https://github.com/tikv/tikv/issues/10158)
    - Fix the issue that the node of a TiKV replica is down after the node gets snapshots because TiKV cannot modify the metadata accurately [#10225](https://github.com/tikv/tikv/issues/10225)
    - Fix the leak issue of the backup thread pool [#10287](https://github.com/tikv/tikv/issues/10287)
    - Fix the issue of casting illegal strings into floating-point numbers [#23322](https://github.com/pingcap/tidb/issues/23322)

+ PD
