# SHOW PROCESSLIST syntax, example, permissions, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-processlist.md`
- Source Title: `SHOW [FULL] PROCESSLIST | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW [FULL] PROCESSLIST | SHOW [FULL] PROCESSLIST > Synopsis | SHOW [FULL] PROCESSLIST > Examples | SHOW [FULL] PROCESSLIST > Permissions | SHOW [FULL] PROCESSLIST > MySQL compatibility | SHOW [FULL] PROCESSLIST > See also`
- Source Line Ranges: `5-40`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show processlist`, `sessions`, `query text`, `full output`, `permissions`, `process privilege`, `mysql compatibility`, `cluster processlist`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0670_1e054eefa0`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-processlist.md#show-full-processlist`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8a1584204172a55eb3cd35cc3a9a38a969e1603699667fd3e5fa54e4ed4ea598`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-processlist#show-full-processlist
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-processlist.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about the syntax, output behavior, permissions, or TiDB compatibility notes of `SHOW [FULL] PROCESSLIST`.
- Retrieval Keywords: SHOW PROCESSLIST, SHOW FULL PROCESSLIST, ShowProcesslistStmt, PROCESS privilege, Info column, query text truncated, same TiDB server, INFORMATION_SCHEMA.CLUSTER_PROCESSLIST, INFORMATION_SCHEMA.PROCESSLIST, State column in TiDB is non-descriptive, KILL [TIDB]
- Follow-up Guidance: For process information across the entire cluster, the source points to `INFORMATION_SCHEMA.CLUSTER_PROCESSLIST`.
- Classification Note: This is a SQL reference chunk because it defines the statement syntax, shows an example result set, states the `PROCESS` privilege behavior, and notes TiDB-specific MySQL compatibility for the `State` column.

## Official Source Content

# SHOW [FULL] PROCESSLIST

This statement lists the current sessions connected to the same TiDB server. The `Info` column contains the query text, which will be truncated unless the optional keyword `FULL` is specified. To view the processlist across the entire cluster, use the [`INFORMATION_SCHEMA.CLUSTER_PROCESSLIST`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-processlist#cluster_processlist) table.
## Synopsis

```ebnf+diagram
ShowProcesslistStmt ::=
    "SHOW" "FULL"? "PROCESSLIST"
```
## Examples

```sql
mysql> SHOW PROCESSLIST;
+------+------+-----------------+------+---------+------+------------+------------------+
| Id   | User | Host            | db   | Command | Time | State      | Info             |
+------+------+-----------------+------+---------+------+------------+------------------+
|    5 | root | 127.0.0.1:45970 | test | Query   |    0 | autocommit | SHOW PROCESSLIST |
+------+------+-----------------+------+---------+------+------------+------------------+
1 rows in set (0.00 sec)
```
## Permissions

If the current user does not have the `PROCESS` privilege, `SHOW PROCESSLIST` only shows the requests from the user’s own sessions.
## MySQL compatibility

* The `State` column in TiDB is non-descriptive. Representing state as a single value is more complex in TiDB, since queries are executed in parallel and each goroutine will have a different state at any one time.
## See also

* [KILL \[TIDB\]](/sql-statements/sql-statement-kill.md)
* [`INFORMATION_SCHEMA.PROCESSLIST`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-processlist)
