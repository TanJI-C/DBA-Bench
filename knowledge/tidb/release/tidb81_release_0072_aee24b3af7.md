# TiDB optimizer, server, and DDL fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.3.md`
- Source Title: `TiDB 2.1.3 Release Notes`
- Source Heading Path: `TiDB 2.1.3 Release Notes > TiDB`
- Source Line Ranges: `10-41`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `prepared-plan-cache`, `range-computing`, `cast`, `generated-column`, `histogram`, `sort-merge-join`, `rowid`, `allow_invalid_dates`, `timezone`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0072_aee24b3af7`
- Source ID: `tidb-docs-8.1:releases/release-2.1.3.md#tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `85c1ad050984d1273c1e7b6d85b08b3ab512feb7ca9867855c462b6531c11866`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.3#tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.3.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 2.1.3 fixes and changes in SQL Optimizer/Executor, Server, or DDL such as Prepared Plan Cache, Sort Merge Join, TIME cast behavior, SQL mode, and table alteration behavior.
- Retrieval Keywords: Prepared Plan Cache panic, Range computing prefix index, CAST(str AS TIME(N)) return null, illegal TIME format, CAST(AS TIME) precision is too big, Generated Column UPDATE panic, statistics histogram upper bound overflow, _tidb_rowid range construction queries, avoid full table scan, Sort Merge Join Cartesian product, Sort Merge Join wrong result, statistics worker cannot resume after panic, CASE clause JSON type, non-TiDB hint warning instead of error, TIMEZONE validity, QueryDurationHistogram, ALLOW_INVALID_DATES, RENAME TABLE compatibility, ADD INDEX take effect immediately, ADD COLUMN UPDATE panic, creating Table Partition concurrently, utf8 to utf8mb4, Shard Bits overflow, SHOW CREATE TABLE column character sets, varchar maximum length limit utf8mb4, ALTER TABLE TRUNCATE TABLE PARTITION, resolve the charset when the charset is not provided
- Follow-up Guidance: The chunk groups the changes under SQL Optimizer/Executor, Server, and DDL in the TiDB section of the TiDB 2.1.3 release notes.
- Classification Note: This is classified as a TiDB release chunk because the content lists TiDB-specific fixes and feature changes across optimizer, server, and DDL areas.

## Official Source Content

## TiDB

+ SQL Optimizer/Executor
    - Fix the panic issue of Prepared Plan Cache in some cases [#8826](https://github.com/pingcap/tidb/pull/8826)
    - Fix the issue that Range computing is wrong when the index is a prefix index [#8851](https://github.com/pingcap/tidb/pull/8851)
    - Make `CAST(str AS TIME(N))` return null if the string is in the illegal `TIME` format when `SQL_MODE` is not strict [#8966](https://github.com/pingcap/tidb/pull/8966)
    - Fix the panic issue of Generated Column during the process of `UPDATE` in some cases [#8980](https://github.com/pingcap/tidb/pull/8980)
    - Fix the upper bound overflow issue of the statistics histogram in some cases [#8989](https://github.com/pingcap/tidb/pull/8989)
    - Support Range for `_tidb_rowid` construction queries, to avoid full table scan and reduce cluster stress [#9059](https://github.com/pingcap/tidb/pull/9059)
    - Return an error when the `CAST(AS TIME)` precision is too big [#9058](https://github.com/pingcap/tidb/pull/9058)
    - Allow using `Sort Merge Join` in the Cartesian product [#9037](https://github.com/pingcap/tidb/pull/9037)
    - Fix the issue that the statistics worker cannot resume after the panic in some cases [#9085](https://github.com/pingcap/tidb/pull/9085)
    - Fix the issue that `Sort Merge Join` returns the wrong result in some cases [#9046](https://github.com/pingcap/tidb/pull/9046)
    - Support returning the JSON type in the `CASE` clause [#8355](https://github.com/pingcap/tidb/pull/8355)
+ Server
    - Return a warning instead of an error when the non-TiDB hint exists in the comment [#8766](https://github.com/pingcap/tidb/pull/8766)
    - Verify the validity of the configured TIMEZONE value [#8879](https://github.com/pingcap/tidb/pull/8879)
    - Optimize the `QueryDurationHistogram` metrics item to display more statement types [#8875](https://github.com/pingcap/tidb/pull/8875)
    - Fix the lower bound overflow issue of bigint in some cases [#8544](https://github.com/pingcap/tidb/pull/8544)
    - Support the `ALLOW_INVALID_DATES` SQL mode [#9110](https://github.com/pingcap/tidb/pull/9110)
+ DDL
    - Fix a `RENAME TABLE` compatibility issue to keep the behavior consistent with that of MySQL [#8808](https://github.com/pingcap/tidb/pull/8808)
    - Support making concurrent changes of `ADD INDEX` take effect immediately [#8786](https://github.com/pingcap/tidb/pull/8786)
    - Fix the `UPDATE` panic issue during the process of `ADD COLUMN` in some cases [#8906](https://github.com/pingcap/tidb/pull/8906)
    - Fix the issue of concurrently creating Table Partition in some cases [#8902](https://github.com/pingcap/tidb/pull/8902)
    - Support converting the `utf8` character set to `utf8mb4` [#8951](https://github.com/pingcap/tidb/pull/8951) [#9152](https://github.com/pingcap/tidb/pull/9152)
    - Fix the issue of Shard Bits overflow [#8976](https://github.com/pingcap/tidb/pull/8976)
    - Support outputting the column character sets in `SHOW CREATE TABLE` [#9053](https://github.com/pingcap/tidb/pull/9053)
    - Fix the issue of the maximum length limit of the varchar type column in `utf8mb4` [#8818](https://github.com/pingcap/tidb/pull/8818)
    - Support `ALTER TABLE TRUNCATE TABLE PARTITION` [#9093](https://github.com/pingcap/tidb/pull/9093)
    - Resolve the charset when the charset is not provided [#9147](https://github.com/pingcap/tidb/pull/9147)
