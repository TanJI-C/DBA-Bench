# TiDB 2.1 RC1 TiDB compatibility DML DDL and partition updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-rc.1.md`
- Source Title: `TiDB 2.1 RC1 Release Notes`
- Source Heading Path: `TiDB 2.1 RC1 Release Notes > TiDB`
- Source Line Ranges: `72-101`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `release-notes`, `compatibility`, `dml`, `ddl`, `table-partition`, `load-data`, `add-index`, `parallel-ddl`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0046_1571cd6cb9`
- Source ID: `tidb-docs-8.1:releases/release-2.1-rc.1.md#tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a2ccb52cd00604ca6a7b077c7948f6ea28d709d24350c8e025bbeceb4f9d17da`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-rc.1#tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-rc.1.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 2.1 RC1 release-note details about compatibility syntax support, DML and DDL fixes, add-index behavior, parallel DDL, and experimental table partition support.
- Retrieval Keywords: TiDB 2.1 RC1 Release Notes, DML, DDL, Table Partition, Experimental, LOAD DATA, CHARACTER SET syntax, IDENTIFIED WITH, CURRENT_TIMESTAMP, SHOW CREATE TABLE, ADD INDEX, UNIQUE-KEY index, tidb_ddl_reorg_priority, admin show ddl jobs <number>, parallel DDL job execution, information_schema.tables, AUTO-INCREMENT, Range Partition, top level partition
- Follow-up Guidance: 
- Classification Note: The official content is a continuation of the TiDB 2.1 RC1 release notes focused on compatibility updates together with DML, DDL, and experimental Table Partition items.

## Official Source Content

- Fix the column size of `SET` and `ENUM` types in `information_schema` [#7347](https://github.com/pingcap/tidb/pull/7347)
    - Support the `NATIONAL CHARACTER` syntax of statements for creating a table [#7378](https://github.com/pingcap/tidb/pull/7378)
    - Support the `CHARACTER SET` syntax in the `LOAD DATA` statement [#7391](https://github.com/pingcap/tidb/pull/7391)
    - Fix the column information of the `SET` and `ENUM` types [#7417](https://github.com/pingcap/tidb/pull/7417)
    - Support the `IDENTIFIED WITH` syntax in the `CREATE USER` statement [#7402](https://github.com/pingcap/tidb/pull/7402)
    - Fix the precision losing issue during `TIMESTAMP` computing process [#7418](https://github.com/pingcap/tidb/pull/7418)
    - Support the validity verification of more `SYSTEM` variables [#7196](https://github.com/pingcap/tidb/pull/7196)
    - Fix the incorrect result when the `CHAR_LENGTH` function computes the binary string [#7410](https://github.com/pingcap/tidb/pull/7410)
    - Fix the incorrect `CONCAT` result in a statement involving `GROUP BY` [#7448](https://github.com/pingcap/tidb/pull/7448)
    - Fix the imprecise type length issue when casting the `DECIMAL` type to the `STRING` type [#7451](https://github.com/pingcap/tidb/pull/7451)
- DML
    - Fix the stability issue of the `Load Data` statement [#6927](https://github.com/pingcap/tidb/pull/6927)
    - Fix the memory usage issue when performing some `Batch` operations [#7086](https://github.com/pingcap/tidb/pull/7086)
    - Improve the performance of the `Replace Into` statement [#7027](https://github.com/pingcap/tidb/pull/7027)
    - Fix the inconsistent precision issue when writing `CURRENT_TIMESTAMP` [#7355](https://github.com/pingcap/tidb/pull/7355)
- DDL
    - Improve the method of DDL judging whether `Schema` is replicated to avoid misjudgement in some cases [#7319](https://github.com/pingcap/tidb/pull/7319)
    - Fix the `SHOW CREATE TABLE` result in adding index process [#6993](https://github.com/pingcap/tidb/pull/6993)
    - Allow the default value of `text`/`blob`/`json` to be NULL in non-restrict `sql-mode` [#7230](https://github.com/pingcap/tidb/pull/7230)
    - Fix the `ADD INDEX` issue in some cases [#7142](https://github.com/pingcap/tidb/pull/7142)
    - Increase the speed of adding `UNIQUE-KEY` index operation largely [#7132](https://github.com/pingcap/tidb/pull/7132)
    - Fix the truncating issue of the prefix index in UTF-8 character set [#7109](https://github.com/pingcap/tidb/pull/7109)
    - Add the environment variable `tidb_ddl_reorg_priority` to control the priority of the `add-index` operation [#7116](https://github.com/pingcap/tidb/pull/7116)
    - Fix the display issue of `AUTO-INCREMENT` in `information_schema.tables` [#7037](https://github.com/pingcap/tidb/pull/7037)
    - Support the `admin show ddl jobs <number>` command and support output specified number of DDL jobs [#7028](https://github.com/pingcap/tidb/pull/7028)
    - Support parallel DDL job execution [#6955](https://github.com/pingcap/tidb/pull/6955)
- [Table Partition](https://github.com/pingcap/tidb/projects/6) (Experimental)
    - Support top level partition
    - Support `Range Partition`
