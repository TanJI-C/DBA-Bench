# TiDB 5.4.1 bug fixes for TiDB and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.4.1.md`
- Source Title: `TiDB 5.4.1 Release Notes`
- Source Heading Path: `TiDB 5.4.1 Release Notes > Bug Fixes`
- Source Line Ranges: `48-100`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `pd`, `ticdc`
- Topic Tags: `release-notes`, `bug-fixes`, `wrong-results`, `panic`, `oom`, `privileges`, `load-data`, `replica-read`, `merge`, `resolved-ts`, `recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0279_44c53b067d`
- Source ID: `tidb-docs-8.1:releases/release-5.4.1.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `401f9871d84bc1c5ae45a3c65d8b5ca9cfd8dd38fad215b594c6173426a8a106`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.4.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.4.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.4.1 bug fixes related to wrong results, panic, OOM, privileges, load data, replica read, merge, resolved_ts, or TiCDC recovery.
- Retrieval Keywords: TiDB 5.4.1 Release Notes, Bug Fixes, date_format, MySQL-incompatible, ENUM, SET, Merge Join, wrong result, correlated subquery, TiFlash, ChunkRPC, OOM, tidb_super_read_only, tidb_restricted_read_only, load data panic, invalid transaction, index lookup join, left join, granting the all privilege, prepared statement, MySQL binary protocol, compress(), tidb_enable_vectorized_expression, INFORMATION_SCHEMA.ATTRIBUTES, @@tidb_enable_parallel_apply, NO_ZERO_DATE, INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY, NOWAIT, GBK, gbk_bin, Unknown character set, TiKV panic, merged Region, stale messages, replica reads, linearizability, resolved_ts, Write Conflict, resource metering, slow score, TiCDC recovery
- Follow-up Guidance: 
- Classification Note: This is a bug-fixes release chunk listing TiDB and TiKV fixes for correctness, stability, memory, transaction, privilege, charset, replica read, and recovery issues in TiDB 5.4.1.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix the issue that `date_format` in TiDB handles `'\n'` in a MySQL-incompatible way [#32232](https://github.com/pingcap/tidb/issues/32232)
    - Fix the issue that TiDB writes wrong data due to the wrong encoding of the `ENUM` or `SET` column [#32302](https://github.com/pingcap/tidb/issues/32302)
    - Fix the issue that the Merge Join operator gets wrong results in certain cases [#33042](https://github.com/pingcap/tidb/issues/33042)
    - Fix the issue that TiDB gets a wrong result when a correlated subquery returns a constant  [#32089](https://github.com/pingcap/tidb/issues/32089)
    - Fix the issue that TiDB gets the wrong result when using TiFlash to scan tables with empty range although TiFlash does not support reading tables with empty range yet [#33083](https://github.com/pingcap/tidb/issues/33083)
    - Fix the issue that the `MAX` or `MIN` function on the `ENUM` or `SET` column returns a wrong result when the new collation is enabled in TiDB [#31638](https://github.com/pingcap/tidb/issues/31638)
    - Fix a bug that CTE might be blocked when a query reports errors [#31302](https://github.com/pingcap/tidb/issues/31302)
    - Fix wrong range calculation results for Nulleq function on Enum values [#32428](https://github.com/pingcap/tidb/issues/32428)
    - Fix TiDB OOM when exporting data using ChunkRPC [#31981](https://github.com/pingcap/tidb/issues/31981) [#30880](https://github.com/pingcap/tidb/issues/30880)
    - Fix a bug that `tidb_super_read_only` is not automatically enabled when `tidb_restricted_read_only` is enabled [#31745](https://github.com/pingcap/tidb/issues/31745)
    - Fix the issue that the `greatest` or `least` function with collation gets a wrong result [#31789](https://github.com/pingcap/tidb/issues/31789)
    - Fix load data panic if the data is broken at an escape character [#31589](https://github.com/pingcap/tidb/issues/31589)
    - Fix the `invalid transaction` error when executing a query using index lookup join [#30468](https://github.com/pingcap/tidb/issues/30468)
    - Fix wrong results of deleting data of multiple tables using `left join` [#31321](https://github.com/pingcap/tidb/issues/31321)
    - Fix a bug that TiDB may dispatch duplicate tasks to TiFlash [#32814](https://github.com/pingcap/tidb/issues/32814)
    - Fix the issue that granting the `all` privilege might fail in clusters that are upgraded from v4.0 [#33588](https://github.com/pingcap/tidb/issues/33588)
    - Fix the session panic that occurs when executing the prepared statement after table schema change with the MySQL binary protocol [#33509](https://github.com/pingcap/tidb/issues/33509)
    - Fix the issue that executing SQL statements that have the `compress()` expression with `tidb_enable_vectorized_expression` enabled will fail [#33397](https://github.com/pingcap/tidb/issues/33397)
    - Fix the issue of high CPU usage by the `reArrangeFallback` function [#30353](https://github.com/pingcap/tidb/issues/30353)
    - Fix the issue that the table attributes are not indexed when a new partition is added and the issue that the table range information is not updated when the partition changes [#33929](https://github.com/pingcap/tidb/issues/33929)
    - Fix a bug that the `TopN` statistical information of a table during the initialization is not correctly sorted  [#34216](https://github.com/pingcap/tidb/issues/34216)
    - Fix the error that occurs when reading from the `INFORMATION_SCHEMA.ATTRIBUTES` table by skipping the unidentifiable table attributes [#33665](https://github.com/pingcap/tidb/issues/33665)
    - Fix a bug that even if `@@tidb_enable_parallel_apply` is set, the `Apply` operator is not paralleled when an `order` property exists [#34237](https://github.com/pingcap/tidb/issues/34237)
    - Fix a bug that `'0000-00-00 00:00:00'` can be inserted into a `datetime` column when `sql_mode` is set to `NO_ZERO_DATE` [#34099](https://github.com/pingcap/tidb/issues/34099)
    - Fix the issue that the TiDB server might run out of memory when the `INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY` table is queried. This issue can be triggered when you check slow queries on the Grafana dashboard [#33893](https://github.com/pingcap/tidb/issues/33893)
    - Fix a bug that in the `NOWAIT` statement, a transaction being executed does not return immediately when encountering a lock [#32754](https://github.com/pingcap/tidb/issues/32754)
    - Fix a bug that causes a failure when creating a table with the `GBK` charset and `gbk_bin` collation [#31308](https://github.com/pingcap/tidb/issues/31308)
    - Fix a bug that when `enable-new-charset` is `on`, creating a `GBK` charset table with collation fails with the "Unknown character set" error [#31297](https://github.com/pingcap/tidb/issues/31297)

+ TiKV

    - Fix the issue that TiKV panics and destroys peers unexpectedly because the target Region to be merged is invalid [#12232](https://github.com/tikv/tikv/issues/12232)
    - Fix a bug that stale messages cause TiKV to panic [#12023](https://github.com/tikv/tikv/issues/12023)
    - Fix the issue of intermittent packet loss and out of memory (OOM) caused by the overflow of memory metrics [#12160](https://github.com/tikv/tikv/issues/12160)
    - Fix the potential panic issue that occurs when TiKV performs profiling on Ubuntu 18.04 [#9765](https://github.com/tikv/tikv/issues/9765)
    - Fix a bug that replica reads might violate the linearizability [#12109](https://github.com/tikv/tikv/issues/12109)
    - Fix the TiKV panic issue that occurs when the target peer is replaced with the peer that is destroyed without being initialized when merging a Region [#12048](https://github.com/tikv/tikv/issues/12048)
    - Fix a bug that TiKV might panic if it has been running for 2 years or more [#11940](https://github.com/tikv/tikv/issues/11940)
    - Reduce the TiCDC recovery time by reducing the number of the Regions that require the Resolve Locks step [#11993](https://github.com/tikv/tikv/issues/11993)
    - Fix the panic issue caused by deleting snapshot files when the peer status is `Applying` [#11746](https://github.com/tikv/tikv/issues/11746)
    - Fix the issue that destroying a peer might cause high latency [#10210](https://github.com/tikv/tikv/issues/10210)
    - Fix the panic issue caused by invalid assertion in resource metering [#12234](https://github.com/tikv/tikv/issues/12234)
    - Fix the issue that slow score calculation is inaccurate in some corner cases [#12254](https://github.com/tikv/tikv/issues/12254)
    - Fix the OOM issue caused by the `resolved_ts` module and add more metrics [#12159](https://github.com/tikv/tikv/issues/12159)
    - Fix the issue that successfully committed optimistic transactions may report the `Write Conflict` error when the network is poor [#34066](https://github.com/pingcap/tidb/issues/34066)
    - Fix the TiKV panic issue that occurs when replica read is enabled on a poor network [#12046](https://github.com/tikv/tikv/issues/12046)

+ PD
