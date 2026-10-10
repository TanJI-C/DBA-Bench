# Information functions reference and support matrix

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/information-functions.md`
- Source Title: `Information Functions`
- Source Heading Path: `Information Functions | Information Functions > TiDB supported MySQL functions | Information Functions > TiDB supported MySQL functions > BENCHMARK() | Information Functions > TiDB supported MySQL functions > CONNECTION_ID() | Information Functions > TiDB supported MySQL functions > CURRENT_ROLE() | Information Functions > TiDB supported MySQL functions > CURRENT_USER() | Information Functions > TiDB supported MySQL functions > DATABASE() | Information Functions > TiDB supported MySQL functions > FOUND_ROWS() | Information Functions > TiDB supported MySQL functions > LAST_INSERT_ID() | Information Functions > TiDB supported MySQL functions > ROW_COUNT() | Information Functions > TiDB supported MySQL functions > SCHEMA() | Information Functions > TiDB supported MySQL functions > SESSION_USER() | Information Functions > TiDB supported MySQL functions > SYSTEM_USER() | Information Functions > TiDB supported MySQL functions > USER() | Information Functions > TiDB supported MySQL functions > VERSION() | Information Functions > TiDB specific functions | Information Functions > Unsupported functions`
- Source Line Ranges: `5-322`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `information-functions`, `mysql-compatibility`, `function-reference`, `connection-id`, `session-identity`, `database-schema`, `found-rows`, `last-insert-id`, `row-count`, `version`, `resource-groups`, `unsupported-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0312_79ce7362ba`
- Source ID: `tidb-docs-8.1:functions-and-operators/information-functions.md#information-functions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d42a85288bcfd7e088f91cc6315a2921ce4469d09fc0a997a661d69c8e973b2b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/information-functions#information-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/information-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB information functions, their MySQL compatibility, exact semantics of functions such as CONNECTION_ID(), CURRENT_USER(), DATABASE(), FOUND_ROWS(), LAST_INSERT_ID(), ROW_COUNT(), USER(), VERSION(), or the list of unsupported information functions.
- Retrieval Keywords: information functions, BENCHMARK(), CONNECTION_ID(), CURRENT_ROLE(), CURRENT_USER(), DATABASE(), FOUND_ROWS(), LAST_INSERT_ID(), ROW_COUNT(), SCHEMA(), SESSION_USER(), SYSTEM_USER(), USER(), VERSION(), CURRENT_RESOURCE_GROUP(), unsupported functions, SQL_CALC_FOUND_ROWS, tidb_enable_noop_functions, enable-32bits-connection-id, enable-global-kill, server-version, TIDB_VERSION(), AUTO_INCREMENT, AUTO_RANDOM, AUTO_ID_CACHE
- Follow-up Guidance: The content also points to TIDB_VERSION() for more detailed version output and names configuration items such as enable-32bits-connection-id, enable-global-kill, tidb_enable_noop_functions, and server-version that affect related behavior.
- Classification Note: This is a reference chunk because it provides a support matrix, syntax, examples, synonyms, notes, and unsupported-function lists for SQL information functions in TiDB.

## Official Source Content

# Information Functions

TiDB supports most of the [information functions](https://dev.mysql.com/doc/refman/8.0/en/information-functions.html) available in MySQL 8.0.
## TiDB supported MySQL functions

| Name | Description |
|:-----|:------------|
| [`BENCHMARK()`](#benchmark) | Execute an expression in a loop |
| [`CONNECTION_ID()`](#connection_id) | Return the connection ID (thread ID) for the connection  |
| [`CURRENT_ROLE()`](#current_role) | Return the role that is in use by the connection |
| [`CURRENT_USER()`, `CURRENT_USER`](#current_user) | Return the authenticated user name and host name |
| [`DATABASE()`](#database) | Return the default (current) database name  |
| [`FOUND_ROWS()`](#found_rows) | For a `SELECT` with a `LIMIT` clause, the number of the rows that are returned if there is no `LIMIT` clause |
| [`LAST_INSERT_ID()`](#last_insert_id) | Return the value of the `AUTOINCREMENT` column for the last `INSERT`   |
| [`ROW_COUNT()`](#row_count) | The number of rows affected |
| [`SCHEMA()`](#schema) | Synonym for `DATABASE()`  |
| [`SESSION_USER()`](#session_user) | Synonym for `USER()`    |
| [`SYSTEM_USER()`](#system_user) | Synonym for `USER()`   |
| [`USER()`](#user) | Return the user name and host name provided by the client    |
| [`VERSION()`](#version) | Return a string that indicates the MySQL server version   |
### BENCHMARK()

The `BENCHMARK()` function executes the given expression a specified number of times.

Syntax:

```sql
BENCHMARK(count, expression)
```

- `count`: the number of times the expression to be executed.
- `expression`: the expression to be executed repeatedly.

Example:

```sql
SELECT BENCHMARK(5, SLEEP(2));
```

```
+------------------------+
| BENCHMARK(5, SLEEP(2)) |
+------------------------+
|                      0 |
+------------------------+
1 row in set (10.00 sec)
```
### CONNECTION_ID()

The `CONNECTION_ID()` function returns the ID of the connection. Based on the value of the [`enable-32bits-connection-id`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-32bits-connection-id-new-in-v730) configuration item for TiDB, this function returns a 32-bit or 64-bit connection ID.

If [`enable-global-kill`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-global-kill-new-in-v610) is enabled, the connection ID can be used to kill queries across multiple TiDB instances of the same cluster.

The `CONNECTION_ID()` function returns the ID of the connection. Based on the value of the [`enable-32bits-connection-id`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-32bits-connection-id-new-in-v730) configuration item for TiDB, this function returns a 32-bit or 64-bit connection ID.

If [`enable-global-kill`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-global-kill-new-in-v610) is enabled, the connection ID can be used to kill queries across multiple TiDB instances of the same cluster.

```sql
SELECT CONNECTION_ID();
```

```
+-----------------+
| CONNECTION_ID() |
+-----------------+
|       322961414 |
+-----------------+
1 row in set (0.00 sec)
```
### CURRENT_ROLE()

The `CURRENT_ROLE()` function returns the current [role](https://docs.pingcap.com/tidb/stable/role-based-access-control) for the current session.

The `CURRENT_ROLE()` function returns the current [role](https://docs.pingcap.com/tidb/stable/role-based-access-control) for the current session.

```sql
SELECT CURRENT_ROLE();
```

```
+----------------+
| CURRENT_ROLE() |
+----------------+
| NONE           |
+----------------+
1 row in set (0.00 sec)
```
### CURRENT_USER()

The `CURRENT_USER()` function returns the account that is used in the current session.

```sql
SELECT CURRENT_USER();
```

```
+----------------+
| CURRENT_USER() |
+----------------+
| root@%         |
+----------------+
1 row in set (0.00 sec)
```
### DATABASE()

The `DATABASE()` function returns the database schema that the current session is using.

```sql
SELECT DATABASE();
```

```
+------------+
| DATABASE() |
+------------+
| test       |
+------------+
1 row in set (0.00 sec)
```
### FOUND_ROWS()

The `FOUND_ROWS()` function returns the number of rows in the result set of the last executed `SELECT` statement.

```sql
SELECT 1 UNION ALL SELECT 2;
```

```
+------+
| 1    |
+------+
|    2 |
|    1 |
+------+
2 rows in set (0.01 sec)
```

```sql
SELECT FOUND_ROWS();
```

```
+--------------+
| FOUND_ROWS() |
+--------------+
|            2 |
+--------------+
1 row in set (0.00 sec)
```

> **Note:**
>
> The `SQL_CALC_FOUND_ROWS` query modifier, which calculates the total number of rows in a result set without considering the `LIMIT` clause, is only accepted if [`tidb_enable_noop_functions`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_noop_functions-new-in-v40) is enabled. This query modifier is deprecated starting from MySQL 8.0.17. It is recommended to use `COUNT(*)` instead.
### LAST_INSERT_ID()

The `LAST_INSERT_ID()` function returns the ID of the last inserted row in a table that contains an [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment) or [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/auto-random) column.

```sql
CREATE TABLE t1(id SERIAL);
Query OK, 0 rows affected (0.17 sec)

INSERT INTO t1() VALUES();
Query OK, 1 row affected (0.03 sec)

INSERT INTO t1() VALUES();
Query OK, 1 row affected (0.00 sec)

SELECT LAST_INSERT_ID();
+------------------+
| LAST_INSERT_ID() |
+------------------+
|                3 |
+------------------+
1 row in set (0.00 sec)

TABLE t1;
+----+
| id |
+----+
|  1 |
|  3 |
+----+
2 rows in set (0.00 sec)
```

> **Note**
>
> - In TiDB, [`AUTO_ID_CACHE`](https://docs.pingcap.com/tidb/stable/auto-increment#auto_id_cache) might lead to results that differ from those returned by MySQL. This discrepancy arises because TiDB caches IDs on each node, potentially leading to IDs that are out of order or have gaps. If maintaining strict ID ordering is essential for your application, you can enable [MySQL compatible mode](https://docs.pingcap.com/tidb/stable/auto-increment#mysql-compatibility-mode).
>
> - In the preceding example, IDs increase by 2 while MySQL would generate IDs incrementing by 1 in the same scenario. For more compatibility information, see [Auto-increment ID](https://docs.pingcap.com/tidb/stable/mysql-compatibility#auto-increment-id).
### ROW_COUNT()

The `ROW_COUNT()` function returns the number of affected rows.

```sql
CREATE TABLE t1(id BIGINT UNSIGNED PRIMARY KEY AUTO_RANDOM);
Query OK, 0 rows affected, 1 warning (0.16 sec)

INSERT INTO t1() VALUES (),(),();
Query OK, 3 rows affected (0.02 sec)
Records: 3  Duplicates: 0  Warnings: 0

SELECT ROW_COUNT();
+-------------+
| ROW_COUNT() |
+-------------+
|           3 |
+-------------+
1 row in set (0.00 sec)
```
### SCHEMA()

The `SCHEMA()` function is a synonym for [`DATABASE()`](#database).
### SESSION_USER()

The `SESSION_USER()` function is a synonym for [`USER()`](#user).
### SYSTEM_USER()

The `SYSTEM_USER()` function is a synonym for [`USER()`](#user).
### USER()

The `USER()` function returns the user of the current connection. This might differ slightly from the output of `CURRENT_USER()`, as `USER()` displays the actual IP address instead of a wildcard.

```sql
SELECT USER(), CURRENT_USER();
```

```
+----------------+----------------+
| USER()         | CURRENT_USER() |
+----------------+----------------+
| root@127.0.0.1 | root@%         |
+----------------+----------------+
1 row in set (0.00 sec)
```
### VERSION()

The `VERSION()` function returns the TiDB version in a format that is compatible with MySQL. To get a more detailed result, you can use the [`TIDB_VERSION()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb_version) function.

```sql
SELECT VERSION();
+--------------------+
| VERSION()          |
+--------------------+
| 8.0.11-TiDB-v7.5.1 |
+--------------------+
1 row in set (0.00 sec)
```

```sql
SELECT TIDB_VERSION()\G
*************************** 1. row ***************************
TIDB_VERSION(): Release Version: v7.5.1
Edition: Community
Git Commit Hash: 7d16cc79e81bbf573124df3fd9351c26963f3e70
Git Branch: heads/refs/tags/v7.5.1
UTC Build Time: 2024-02-27 14:28:32
GoVersion: go1.21.6
Race Enabled: false
Check Table Before Drop: false
Store: tikv
1 row in set (0.00 sec)
```

The preceding example is from TiDB v7.5.1, which identifies itself as MySQL 8.0.11.

If you want to change the returned version, you can modify the [`server-version`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#server-version) configuration item.
## TiDB specific functions

The following function is only supported by TiDB, and there is no equivalent function in MySQL.

| Name | Description |
|:-----|:------------|
| [`CURRENT_RESOURCE_GROUP()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#current_resource_group)  | Return the name of the resource group that the current session is bound to |
## Unsupported functions

* `CHARSET()`
* `COERCIBILITY()`
* `COLLATION()`
* `ICU_VERSION()`
* `ROLES_GRAPHML()`
