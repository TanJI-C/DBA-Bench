# MySQL compatibility and JSON GA features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.3.0.md`
- Source Title: `TiDB 6.3.0 Release Notes`
- Source Heading Path: `TiDB 6.3.0 Release Notes > New features > MySQL compatibility`
- Source Line Ranges: `158-175`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `mysql-compatibility`, `regular-expressions`, `account-lock`, `json`, `expression-indexes`, `generated-columns`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0338_5c05ce4713`
- Source ID: `tidb-docs-8.1:releases/release-6.3.0.md#mysql-compatibility`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9892fb64de87b9eb1c2535c5e8714046e9ab771e43e6bbae319c6c3faf714ff3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.3.0#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.3.0 MySQL compatibility additions such as new regular expression functions, ACCOUNT LOCK/UNLOCK support, or the GA status of JSON data type and JSON functions.
- Retrieval Keywords: TiDB 6.3.0 MySQL compatibility, REGEXP_INSTR(), REGEXP_LIKE(), REGEXP_REPLACE(), REGEXP_SUBSTR(), Regular expression compatibility with MySQL, CREATE USER ACCOUNT LOCK/UNLOCK, ALTER USER ACCOUNT LOCK/UNLOCK, locked user cannot log in, JSON data type GA, JSON functions GA, expression indexes, generated-columns
- Follow-up Guidance: The content points to details for regular expression compatibility with MySQL and notes that JSON functions can be used in expression indexes and generated-columns.
- Classification Note: This is a release-note chunk for TiDB new features in MySQL compatibility, covering SQL function support, user account lock options, and JSON GA capabilities.

## Official Source Content

### MySQL compatibility

* Improve MySQL 8.0 compatibility by adding support for four regular expression functions: `REGEXP_INSTR()`, `REGEXP_LIKE()`, `REGEXP_REPLACE()`, and `REGEXP_SUBSTR()` [#23881](https://github.com/pingcap/tidb/issues/23881) @[windtalker](https://github.com/windtalker)

    For more details about the compatibility with MySQL, see [Regular expression compatibility with MySQL](https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#regular-expression-compatibility-with-mysql).

* The `CREATE USER` and `ALTER USER` statements support the `ACCOUNT LOCK/UNLOCK` option [#37051](https://github.com/pingcap/tidb/issues/37051) @[CbcWestwolf](https://github.com/CbcWestwolf)

    When you create a user using the [`CREATE USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user) statement, you can specify whether the created user is locked using the `ACCOUNT LOCK/UNLOCK` option. A locked user cannot log in to the database.

    You can modify the lock state of an existing user using the `ACCOUNT LOCK/UNLOCK` option in the [`ALTER USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user) statement.

* JSON data type and JSON functions become GA [#36993](https://github.com/pingcap/tidb/issues/36993) @[xiongjiwei](https://github.com/xiongjiwei)

    JSON is a popular data format adopted by a large number of programs. TiDB has introduced the [JSON support](https://docs.pingcap.com/tidb/stable/data-type-json) as an experimental feature since an earlier version, compatible with MySQL's JSON data type and some JSON functions.

    In TiDB v6.3.0, the JSON data type and functions become GA, which enriches TiDB's data types, supports using JSON functions in [expression indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#expression-index) and [generated-columns](https://docs.pingcap.com/tidb/stable/generated-columns), and further improves TiDB's compatibility with MySQL.
