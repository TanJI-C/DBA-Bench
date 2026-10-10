# TiDB 2.1 Beta overview and TiDB improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-beta.md`
- Source Title: `TiDB 2.1 Beta Release Notes`
- Source Heading Path: `TiDB 2.1 Beta Release Notes | TiDB 2.1 Beta Release Notes > TiDB`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `release-notes`, `sql-optimizer`, `execution-engine`, `server`, `compatibility`, `dml`, `ddl`, `performance`, `stability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0038_1f366a2d41`
- Source ID: `tidb-docs-8.1:releases/release-2.1-beta.md#tidb-2-1-beta-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5c28aa84b0e78deeda2af62f8592f2c011c089db288d5e347c9c25932613d740`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-beta#tidb-2-1-beta-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-beta.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 2.1 Beta release-note details about TiDB SQL optimizer, execution engine, server, compatibility, DML, and DDL changes compared with TiDB 2.0.
- Retrieval Keywords: TiDB 2.1 Beta Release Notes, TiDB 2.1 Beta, SQL Optimizer, Index Join, correlated subquery, Filter pushdown, Index Hint, Join Hint, UPDATE, DELETE, TIDM_SMJ, ABS, CEIL, FLOOR, IS TRUE, IS FALSE, IF, IFNULL, parallel Hash Aggregate, parallel Project, Hash Join, INSERT ON DUPLICATE KEY UPDATE, CONCAT_WS, HTTP API, scatter the distribution of table Regions, auto_analyze_ratio, general log, log level online, server side cursor, SHOW PRIVILEGES, bit aggregate function ALL, INSERT INTO SELECT, PlanCache, tidb_retry_limit, tidb_disable_txn_auto_retry, Affected Rows, CreateTable, ADD INDEX, Alter table add column, SHOW CREATE TABLE, select tidb_is_ddl_owner(), AlterTableForce, AlterTableRenameIndex, admin show ddl jobs
- Follow-up Guidance: The same release notes also include PD and TiKV changes, including compatibility notes about rollback and upgrade behavior.
- Classification Note: This is a self-managed TiDB release-notes chunk focused on TiDB component improvements and fixes across optimizer, execution engine, server, compatibility, DML, and DDL topics.

## Official Source Content

# TiDB 2.1 Beta Release Notes

On June 29, 2018, TiDB 2.1 Beta is released! Compared with TiDB 2.0, this release has great improvement in stability, SQL optimizer, statistics information, and execution engine.
## TiDB

- SQL Optimizer
    - Optimize the selection range of `Index Join` to improve the execution performance
    - Optimize correlated subquery, push down `Filter`, and extend the index range, to improve the efficiency of some queries by orders of magnitude
    - Support `Index Hint` and `Join Hint` in the `UPDATE` and `DELETE` statements
    - Validate Hint `TIDM_SMJ` when no available index exists
    - Support pushdown of the `ABS`, `CEIL`, `FLOOR`, `IS TRUE`, and `IS FALSE` functions
    - Handle the `IF` and `IFNULL` functions especially in the constant folding process
- SQL Execution Engine
    - Implement parallel `Hash Aggregate` operators and improve the computing performance of `Hash Aggregate` by 350% in some scenarios
    - Implement parallel `Project` operators and improve the performance by 74% in some scenarios
    - Read the data of the `Inner` table and `Outer` table of `Hash Join` concurrently to improve the execution performance
    - Fix incorrect results of `INSERT … ON DUPLICATE KEY UPDATE …` in some scenarios
    - Fix incorrect results of the `CONCAT_WS`, `FLOOR`, `CEIL`, and `DIV` built-in functions
- Server
    - Add the HTTP API to scatter the distribution of table Regions in the TiKV cluster
    - Add the `auto_analyze_ratio` system variable to control the threshold value of automatic `Analyze`
    - Add the HTTP API to control whether to open the general log
    - Add the HTTP API to modify the log level online
    - Add the user information in the general log and the slow query log
    - Support the server side cursor
- Compatibility
    - Support more MySQL syntax
    - Make the `bit` aggregate function support the `ALL` parameter
    - Support the `SHOW PRIVILEGES` statement
- DML
    - Decrease the memory usage of the `INSERT INTO SELECT` statement
    - Fix the performance issue of `PlanCache`
    - Add the `tidb_retry_limit` system variable to control the automatic retry times of transactions
    - Add the `tidb_disable_txn_auto_retry` system variable to control whether the transaction tries automatically
    - Fix the accuracy issue of the written data of the `time` type
    - Support the queue of locally conflicted transactions to optimize the conflicted transaction performance
    - Fix `Affected Rows` of the `UPDATE` statement
    - Optimize the statement performance of `insert ignore on duplicate key update`
- DDL
    - Optimize the execution speed of the `CreateTable` statement
    - Optimize the execution speed of `ADD INDEX` and improve it greatly in some scenarios
    - Fix the issue that the number of added columns by `Alter table add column` exceeds the limit of the number of table columns
    - Fix the issue that DDL job retries lead to an increasing pressure on TiKV in abnormal conditions
    - Fix the issue that TiDB continuously reloads the schema information in abnormal conditions
    - Do not output the `FOREIGN KEY` related information in the result of `SHOW CREATE TABLE`
    - Support the `select tidb_is_ddl_owner()` statement to facilitate judging whether TiDB is `DDL Owner`
    - Fix the issue that the index is deleted in the `Year` type in some scenarios
    - Fix the renaming table issue in the concurrent execution scenario
    - Support the `AlterTableForce` syntax
    - Support the `AlterTableRenameIndex` syntax with `FromKey` and `ToKey`
    - Add the table name and database name in the output information of `admin show ddl jobs`
