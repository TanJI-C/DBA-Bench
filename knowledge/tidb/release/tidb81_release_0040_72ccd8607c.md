# TiDB 2.1 GA release overview and TiDB enhancements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-ga.md`
- Source Title: `TiDB 2.1 GA Release Notes`
- Source Heading Path: `TiDB 2.1 GA Release Notes | TiDB 2.1 GA Release Notes > TiDB`
- Source Line Ranges: `5-135`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `release-notes`, `sql-optimizer`, `sql-executor`, `statistics`, `expressions`, `server`, `http-api`, `system-variables`, `slow-queries`, `ddl`, `compatibility`, `performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0040_72ccd8607c`
- Source ID: `tidb-docs-8.1:releases/release-2.1-ga.md#tidb-2-1-ga-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fd8f26333dd3f226fd5ea14fc8168b65debf8aaf57e8b0b5164b32236d4e0fb3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-ga#tidb-2-1-ga-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-ga.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 2.1 GA release-note details about TiDB SQL optimizer, SQL executor, statistics, expressions, server, DDL, compatibility, slow query, HTTP API, and system variable enhancements.
- Retrieval Keywords: TiDB 2.1 GA Release Notes, TiDB 2.1 GA, SQL Optimizer, Index Join, TIDB_SMJ, TIDB_INLJ, UPDATE and DELETE hint support, ABS CEIL FLOOR IS TRUE IS FALSE, EXPLAIN hierarchy structure, SQL executor, parallel Hash Aggregate, parallel Project, Hash Join, REPLACE INTO, single statement memory upper limit, EXPLAIN ANALYZE, auto ANALYZE, ANALYZE TABLE WITH BUCKETS, json_contains, json_contains_path, encode/decode, Server Side Cursor, HTTP API, general log, auto_analyze_ratio, tidb_retry_limit, tidb_disable_txn_auto_retry, admin show slow, tidb_slow_log_threshold, tidb_query_log_max_len, ADD INDEX, tidb_is_ddl_owner(), ALTER TABLE FORCE, ALTER TABLE RENAME KEY TO, admin show ddl jobs, ddl/owner/resign, SHOW PRIVILEGES, LOAD DATA IGNORE LINES, IDENTIFIED WITH, Show ProcessList
- Follow-up Guidance: The source also points to related references for `EXPLAIN ANALYZE`, HTTP API, `admin show slow`, and system variables such as `auto_analyze_ratio`, `tidb_retry_limit`, `tidb_disable_txn_auto_retry`, `tidb_slow_log_threshold`, and `tidb_query_log_max_len`.
- Classification Note: This chunk is classified under the TiDB component because the official content lists TiDB 2.1 GA enhancements across optimizer, executor, statistics, expressions, server behavior, DDL, and compatibility features.

## Official Source Content

# TiDB 2.1 GA Release Notes

On November 30, 2018, TiDB 2.1 GA is released. See the following updates in this release. Compared with TiDB 2.0, this release has great improvements in stability, performance, compatibility, and usability.
## TiDB

+ SQL Optimizer

    - Optimize the selection range of `Index Join` to improve the execution performance

    - Optimize the selection of outer table for `Index Join` and use the table with smaller estimated value of Row Count the as the outer table

    - Optimize Join Hint `TIDB_SMJ` so that Merge Join can be used even without proper index available

    - Optimize Join Hint `TIDB_INLJ` to specify the Inner table to Join

    - Optimize correlated subquery, push down Filter, and extend the index selection range, to improve the efficiency of some queries by orders of magnitude

    - Support using Index Hint and Join Hint in the `UPDATE` and `DELETE` statement

    - Support pushing down more functions: `ABS`/`CEIL`/`FLOOR`/`IS TRUE`/`IS FALSE`

    - Optimize the constant folding algorithm for the `IF` and `IFNULL` built-in functions

    - Optimize the output of the `EXPLAIN` statement and use hierarchy structure to show the relationship between operators

+ SQL executor

    - Refactor all the aggregation functions and improve execution efficiency of the `Stream` and `Hash` aggregation operators

    - Implement the parallel `Hash Aggregate` operators and improve the computing performance by 350% in some scenarios

    - Implement the parallel `Project` operators and improve the performance by 74% in some scenarios

    - Read the data of the Inner table and Outer table of `Hash Join` concurrently to improve the execution performance

    - Optimize the execution speed of the `REPLACE INTO` statement and increase the performance nearly by 10 times

    - Optimize the memory usage of the time data type and decrease the memory usage of the time data type by fifty percent

    - Optimize the point select performance and improve the point select efficiency result of Sysbench by 60%

    - Improve the performance of TiDB on inserting or updating wide tables by 20 times

    - Support configuring the memory upper limit of a single statement in the configuration file

    - Optimize the execution of Hash Join, if the Join type is Inner Join or Semi Join and the inner table is empty, return the result without reading data from the outer table

    - Support using the [`EXPLAIN ANALYZE` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze) to check the runtime statistics including the execution time and the number of returned rows of each operator

+ Statistics

    - Support enabling auto ANALYZE statistics only during certain period of the day

    - Support updating the table statistics automatically according to the feedback of the queries

    - Support configuring the number of buckets in the histogram using the `ANALYZE TABLE WITH BUCKETS` statement

    - Optimize the Row Count estimation algorithm using histogram for mixed queries of equality query and range queries

+ Expressions

    + Support following built-in function:

        - `json_contains`

        - `json_contains_path`

        - `encode/decode`

+ Server

    - Support queuing the locally conflicted transactions within tidb-server instance to optimize the performance of conflicted transactions

    - Support Server Side Cursor

    + Add the [HTTP API](https://github.com/pingcap/tidb/blob/release-2.1/docs/tidb_http_api.md)

        - Scatter the distribution of table Regions in the TiKV cluster

        - Control whether to open the `general log`

        - Support modifying the log level online

        - Check the TiDB cluster information

    - [Add the `auto_analyze_ratio` system variables to control the ratio of Analyze](https://docs.pingcap.com/tidb/stable/faq/sql-faq#whats-the-trigger-strategy-for-auto-analyze-in-tidb)

    - [Add the `tidb_retry_limit` system variable to control the automatic retry times of transactions](https://docs.pingcap.com/tidb/stable/system-variables#tidb_retry_limit)

    - [Add the `tidb_disable_txn_auto_retry` system variable to control whether the transaction retries automatically](https://docs.pingcap.com/tidb/stable/system-variables#tidb_disable_txn_auto_retry)

    - [Support using`admin show slow` statement to obtain the slow queries](https://docs.pingcap.com/tidb/stable/identify-slow-queries#admin-show-slow-command)

    - [Add the `tidb_slow_log_threshold` environment variable to set the threshold of slow log automatically](https://docs.pingcap.com/tidb/stable/system-variables#tidb_slow_log_threshold)

    - [Add the `tidb_query_log_max_len` environment variable to set the length of the SQL statement to be truncated in the log dynamically](https://docs.pingcap.com/tidb/stable/system-variables#tidb_query_log_max_len)

+ DDL

    - Support the parallel execution of the Add index statement and other statements to avoid the time consuming Add index operation blocking other operations

    - Optimize the execution speed of `ADD INDEX` and improve it greatly in some scenarios

    - Support the `select tidb_is_ddl_owner()` statement to facilitate deciding whether TiDB is `DDL Owner`

    - Support the `ALTER TABLE FORCE` syntax

    - Support the `ALTER TABLE RENAME KEY TO` syntax

    - Add the table name and database name in the output information of `admin show ddl jobs`

    - [Support using the `ddl/owner/resign` HTTP interface to release the DDL owner and start electing a new DDL owner](https://github.com/pingcap/tidb/blob/release-2.1/docs/tidb_http_api.md)

+ Compatibility

    - Support more MySQL syntaxes

    - Make the `BIT` aggregate function support the `ALL` parameter

    - Support the `SHOW PRIVILEGES` statement

    - Support the `CHARACTER SET` syntax in the `LOAD DATA` statement

    - Support the `IDENTIFIED WITH` syntax in the `CREATE USER` statement

    - Support the `LOAD DATA IGNORE LINES` statement

    - The `Show ProcessList` statement returns more accurate information
