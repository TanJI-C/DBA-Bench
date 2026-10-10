# General third-party incompatibilities in TiDB

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-third-party-tools-compatibility.md`
- Source Title: `Known Incompatibility Issues with Third-Party Tools`
- Source Heading Path: `Known Incompatibility Issues with Third-Party Tools | Known Incompatibility Issues with Third-Party Tools > General incompatibility | Known Incompatibility Issues with Third-Party Tools > General incompatibility > `SELECT CONNECTION_ID()` returns a 64-bit integer in TiDB | Known Incompatibility Issues with Third-Party Tools > General incompatibility > TiDB does not maintain `Com_*` counters | Known Incompatibility Issues with Third-Party Tools > General incompatibility > TiDB distinguishes between `TIMESTAMP` and `DATETIME` in error messages | Known Incompatibility Issues with Third-Party Tools > General incompatibility > TiDB does not support the `CHECK TABLE` statement`
- Source Line Ranges: `5-84`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `cloud`, `sql`
- Topic Tags: `compatibility`, `mysql`, `connection-id`, `status-variables`, `monitoring`, `error-codes`, `check-table`, `admin-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0187_852b50fcba`
- Source ID: `tidb-docs-8.1:develop/dev-guide-third-party-tools-compatibility.md#known-incompatibility-issues-with-third-party-tools`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7df3f33a48b9e03842fe00ecb82889dce224ef31a52b8dfa5362e00de7e51afb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-tools-compatibility#known-incompatibility-issues-with-third-party-tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-third-party-tools-compatibility.md

## Retrieval Guidance

- Use When: Use this chunk when checking documented TiDB incompatibilities with third-party tools around SELECT CONNECTION_ID(), Com_* status variables, TIMESTAMP versus DATETIME error messages, or the unsupported CHECK TABLE statement.
- Retrieval Keywords: SELECT CONNECTION_ID(), 64-bit integer, Com_* counters, SHOW GLOBAL STATUS LIKE 'Com_%', TIMESTAMP, DATETIME, Error Codes, CHECK TABLE, ADMIN CHECK TABLE, ADMIN CHECK INDEX, Known Incompatibility Issues with Third-Party Tools
- Follow-up Guidance: The content points to Error Codes for troubleshooting and to ADMIN CHECK [TABLE|INDEX] for checking data and index consistency instead of CHECK TABLE.
- Classification Note: This is reference content because it enumerates specific TiDB and MySQL behavior differences and the exact related SQL statements, variables, and error-handling concepts.

## Official Source Content

# Known Incompatibility Issues with Third-Party Tools

> **Note:**
>
> The [Unsupported features](https://docs.pingcap.com/tidb/stable/mysql-compatibility#unsupported-features) section lists the unsupported features in TiDB, including:
>
> - Stored procedures and functions
> - Triggers
> - Events
> - User-defined functions
> - `SPATIAL` functions, data types and indexes
> - `XA` syntax
>
> The preceding unsupported features are expected behavior and are not listed in this document. For more details, see [MySQL Compatibility](https://docs.pingcap.com/tidb/stable/mysql-compatibility).

The incompatibility issues listed in this document are found in some [third-party tools supported by TiDB](https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-tools-compatibility).
## General incompatibility
### `SELECT CONNECTION_ID()` returns a 64-bit integer in TiDB

**Description**

The `SELECT CONNECTION_ID()` function returns a 64-bit integer in TiDB, such as `2199023260887`, while it returns a 32-bit integer in MySQL, such as `391650`.

**Way to avoid**

In a TiDB application, to avoid data overflow, you should use a 64-bit integer or string type to store the result of `SELECT CONNECTION_ID()`. For example, you can use `Long` or `String` in Java and use `string` in JavaScript or TypeScript.
### TiDB does not maintain `Com_*` counters

**Description**

MySQL maintains a series of [server status variables starting with `Com_`](https://dev.mysql.com/doc/refman/8.0/en/server-status-variables.html#statvar_Com_xxx) to keep track of the total number of operations you have performed on the database. For example, `Com_select` records the total number of `SELECT` statements initiated by MySQL since it was last started (even if the statements were not queried successfully). TiDB does not maintain these variables. You can use the statement [<code>SHOW GLOBAL STATUS LIKE 'Com_%'</code>](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-status) to see the difference between TiDB and MySQL.

**Way to avoid**

Do not use these variables. One common scenario is monitoring. TiDB is well observable and does not require querying from server status variables. For custom monitoring tools, refer to [TiDB Monitoring Framework Overview](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework).

Do not use these variables. One common scenario is monitoring. TiDB Cloud is well observable and does not require querying from server status variables. For more information about TiDB Cloud monitoring services, refer to [Monitor a TiDB Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-tidb-cluster).
### TiDB distinguishes between `TIMESTAMP` and `DATETIME` in error messages

**Description**

TiDB error messages distinguish between `TIMESTAMP` and `DATETIME`, while MySQL does not, and returns them all as `DATETIME`. That is, MySQL incorrectly converts `TIMESTAMP` type error messages to `DATETIME` type.

**Way to avoid**

Do not use the error messages for string matching. Instead, use [Error Codes](https://docs.pingcap.com/tidb/stable/error-codes) for troubleshooting.

Do not use the error messages for string matching. Instead, use [Error Codes](https://docs.pingcap.com/tidb/stable/error-codes) for troubleshooting.
### TiDB does not support the `CHECK TABLE` statement

**Description**

The `CHECK TABLE` statement is not supported in TiDB.

**Way to avoid**

To check the consistency of data and corresponding indexes, you can use the [`ADMIN CHECK [TABLE|INDEX]`](/sql-statements/sql-statement-admin-check-table-index.md) statement in TiDB.
