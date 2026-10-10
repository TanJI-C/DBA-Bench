# TiDB 2.1 RC2 TiDB release changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-rc.2.md`
- Source Title: `TiDB 2.1 RC2 Release Notes`
- Source Heading Path: `TiDB 2.1 RC2 Release Notes | TiDB 2.1 RC2 Release Notes > TiDB`
- Source Line Ranges: `5-88`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `release-notes`, `sql-optimizer`, `execution-engine`, `statistics`, `server`, `compatibility`, `expressions`, `dml`, `ddl`, `goclient`, `table-partition`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0049_f3772e9a98`
- Source ID: `tidb-docs-8.1:releases/release-2.1-rc.2.md#tidb-2-1-rc2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b5204eb001d019a284076096c19b8999adc23f6e33c26ad0b7c3ea3ee2a327fe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-rc.2#tidb-2-1-rc2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-rc.2.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 2.1 RC2 release-note details for TiDB changes across SQL optimizer, execution engine, statistics, server, compatibility, expressions, DML, DDL, TiKV Go Client, or experimental table partition features.
- Retrieval Keywords: TiDB 2.1 RC2 Release Notes, TiDB 2.1 RC2 TiDB release changes, SQL Optimizer, SQL Execution Engine, Statistics, Server, Compatibility, Expressions, DML, DDL, TiKV Go Client, Table Partition, PointGet operator for the UPDATE statement, ANALYZE TABLE WITH BUCKETS, USER1 signal, Admin statement requires the Super_priv privilege, ddl/owner/resign, json_contains, json_contains_path, LOAD DATA IGNORE LINES, information_schema.tables.data_length, top 30 slow queries in the last week
- Follow-up Guidance: For component-specific changes in the same release note, see the PD section for PD feature, improvement, and bug fix items.
- Classification Note: The official content is a self-managed TiDB release-notes section for TiDB in version 2.1 RC2, listing changes by subsystem and feature area.

## Official Source Content

# TiDB 2.1 RC2 Release Notes

On September 14, 2018, TiDB 2.1 RC2 is released. Compared with TiDB 2.1 RC1, this release has great improvement in stability, SQL optimizer, statistics information, and execution engine.
## TiDB

* SQL Optimizer
    * Put forward a proposal of the next generation Planner [#7543](https://github.com/pingcap/tidb/pull/7543)
    * Improve the optimization rules of constant propagation [#7276](https://github.com/pingcap/tidb/pull/7276)
    * Enhance the computing logic of `Range` to enable it to handle multiple `IN` or `EQUAL` conditions simultaneously [#7577](https://github.com/pingcap/tidb/pull/7577)
    * Fix the issue that the estimation result of `TableScan` is incorrect when `Range` is empty [#7583](https://github.com/pingcap/tidb/pull/7583)
    * Support the `PointGet` operator for the `UPDATE` statement [#7586](https://github.com/pingcap/tidb/pull/7586)
    * Fix the panic issue during the process of executing the `FirstRow` aggregate function in some conditions [#7624](https://github.com/pingcap/tidb/pull/7624)
* SQL Execution Engine
    * Fix the potential `DataRace` issue when the `HashJoin` operator encounters an error [#7554](https://github.com/pingcap/tidb/pull/7554)
    * Make the `HashJoin` operator read the inner table and build the hash table simultaneously [#7544](https://github.com/pingcap/tidb/pull/7544)
    * Optimize the performance of Hash aggregate operators [#7541](https://github.com/pingcap/tidb/pull/7541)
    * Optimize the performance of Join operators [#7493](https://github.com/pingcap/tidb/pull/7493), [#7433](https://github.com/pingcap/tidb/pull/7433)
    * Fix the issue that the result of `UPDATE JOIN` is incorrect when the Join order is changed [#7571](https://github.com/pingcap/tidb/pull/7571)
    * Improve the performance of Chunk's iterator [#7585](https://github.com/pingcap/tidb/pull/7585)
* Statistics
    * Fix the issue that the auto Analyze work repeatedly analyzes the statistics [#7550](https://github.com/pingcap/tidb/pull/7550)
    * Fix the statistics update error that occurs when there is no statistics change [#7530](https://github.com/pingcap/tidb/pull/7530)
    * Use the RC isolation level and low priority when building `Analyze` requests [#7496](https://github.com/pingcap/tidb/pull/7496)
    * Support enabling statistics auto-analyze on certain period of a day [#7570](https://github.com/pingcap/tidb/pull/7570)
    * Fix the panic issue when logging the statistics information [#7588](https://github.com/pingcap/tidb/pull/7588)
    * Support configuring the number of buckets in the histogram using the `ANALYZE TABLE WITH BUCKETS` statement [#7619](https://github.com/pingcap/tidb/pull/7619)
    * Fix the panic issue when updating an empty histogram [#7640](https://github.com/pingcap/tidb/pull/7640)
    * Update `information_schema.tables.data_length` using the statistics information [#7657](https://github.com/pingcap/tidb/pull/7657)
* Server
    * Add Trace related dependencies [#7532](https://github.com/pingcap/tidb/pull/7532)
    * Enable the `mutex profile` feature of Golang  [#7512](https://github.com/pingcap/tidb/pull/7512)
    * The `Admin` statement requires the `Super_priv` privilege [#7486](https://github.com/pingcap/tidb/pull/7486)
    * Forbid users to `Drop` crucial system tables [#7471](https://github.com/pingcap/tidb/pull/7471)
    * Switch from `juju/errors` to `pkg/errors` [#7151](https://github.com/pingcap/tidb/pull/7151)
    * Complete the functional prototype of SQL Tracing [#7016](https://github.com/pingcap/tidb/pull/7016)
    * Remove the goroutine pool [#7564](https://github.com/pingcap/tidb/pull/7564)
    * Support viewing the goroutine information using the `USER1` signal [#7587](https://github.com/pingcap/tidb/pull/7587)
    * Set the internal SQL to high priority while TiDB is started [#7616](https://github.com/pingcap/tidb/pull/7616)
    * Use different labels to filter internal SQL and user SQL in monitoring metrics [#7631](https://github.com/pingcap/tidb/pull/7631)
    * Store the top 30 slow queries in the last week to the TiDB server [#7646](https://github.com/pingcap/tidb/pull/7646)
    * Put forward a proposal of setting the global system time zone for the TiDB cluster [#7656](https://github.com/pingcap/tidb/pull/7656)
    * Enrich the error message of "GC life time is shorter than transaction duration" [#7658](https://github.com/pingcap/tidb/pull/7658)
    * Set the global system time zone when starting the TiDB cluster [#7638](https://github.com/pingcap/tidb/pull/7638)
* Compatibility
    * Add the unsigned flag for the `Year` type [#7542](https://github.com/pingcap/tidb/pull/7542)
    * Fix the issue of configuring the result length of the `Year` type in the `Prepare`/`Execute` mode [#7525](https://github.com/pingcap/tidb/pull/7525)
    * Fix the issue of inserting zero timestamp in the `Prepare`/`Execute` mode [#7506](https://github.com/pingcap/tidb/pull/7506)
    * Fix the error handling issue of the integer division [#7492](https://github.com/pingcap/tidb/pull/7492)
    * Fix the compatibility issue when processing `ComStmtSendLongData` [#7485](https://github.com/pingcap/tidb/pull/7485)
    * Fix the error handling issue during the process of converting string to integer [#7483](https://github.com/pingcap/tidb/pull/7483)
    * Optimize the accuracy of values in the `information_schema.columns_in_table` table [#7463](https://github.com/pingcap/tidb/pull/7463)
    * Fix the compatibility issue when writing or updating the string type of data using the MariaDB client [#7573](https://github.com/pingcap/tidb/pull/7573)
    * Fix the compatibility issue of aliases of the returned value [#7600](https://github.com/pingcap/tidb/pull/7600)
    * Fix the issue that the `NUMERIC_SCALE` value of the float type is incorrect in the `information_schema.COLUMNS` table [#7602](https://github.com/pingcap/tidb/pull/7602)
    * Fix the issue that Parser reports an error when the single line comment is empty [#7612](https://github.com/pingcap/tidb/pull/7612)
* Expressions
    * Check the value of `max_allowed_packet` in the `insert` function [#7528](https://github.com/pingcap/tidb/pull/7528)
    * Support the built-in function `json_contains`  [#7443](https://github.com/pingcap/tidb/pull/7443)
    * Support the built-in function `json_contains_path` [#7596](https://github.com/pingcap/tidb/pull/7596)
    * Support the built-in function `encode/decode` [#7622](https://github.com/pingcap/tidb/pull/7622)
    * Fix the issue that some time related functions are not compatible with the MySQL behaviors in some cases [#7636](https://github.com/pingcap/tidb/pull/7636)
    * Fix the compatibility issue of parsing the time type of data in string [#7654](https://github.com/pingcap/tidb/pull/7654)
    * Fix the issue that the time zone is not considered when computing the default value of the `DateTime` data [#7655](https://github.com/pingcap/tidb/pull/7655)
* DML
    * Set correct `last_insert_id` in the `InsertOnDuplicateUpdate` statement [#7534](https://github.com/pingcap/tidb/pull/7534)
    * Reduce the cases of updating the `auto_increment_id` counter [#7515](https://github.com/pingcap/tidb/pull/7515)
    * Optimize the error message of `Duplicate Key` [#7495](https://github.com/pingcap/tidb/pull/7495)
    * Fix the `insert...select...on duplicate key update` issue [#7406](https://github.com/pingcap/tidb/pull/7406)
    * Support the `LOAD DATA IGNORE LINES` statement [#7576](https://github.com/pingcap/tidb/pull/7576)
* DDL
    * Add the DDL job type and the current schema version information in the monitor [#7472](https://github.com/pingcap/tidb/pull/7472)
    * Complete the design of the `Admin Restore Table` feature [#7383](https://github.com/pingcap/tidb/pull/7383)
    * Fix the issue that the default value of the `Bit` type exceeds 128 [#7249](https://github.com/pingcap/tidb/pull/7249)
    * Fix the issue that the default value of the `Bit` type cannot be `NULL` [#7604](https://github.com/pingcap/tidb/pull/7604)
    * Reduce the interval of checking `CREATE TABLE/DATABASE` in the DDL queue [#7608](https://github.com/pingcap/tidb/pull/7608)
    * Use the `ddl/owner/resign` HTTP interface ro release the DDL owner and start electing a new owner [#7649](https://github.com/pingcap/tidb/pull/7649)
* TiKV Go Client
    * Support the issue that the `Seek` operation only obtains `Key` [#7419](https://github.com/pingcap/tidb/pull/7419)
* [Table Partition](https://github.com/pingcap/tidb/projects/6) (Experimental)
    * Fix the issue that the `Bigint` type cannot be used as the partition key  [#7520](https://github.com/pingcap/tidb/pull/7520)
    * Support the rollback operation when an issue occurs during adding an index in the partitioned table [#7437](https://github.com/pingcap/tidb/pull/7437)
