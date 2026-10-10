# SHOW GLOBAL or SESSION STATUS syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-status.md`
- Source Title: `SHOW [GLOBAL|SESSION] STATUS | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW [GLOBAL|SESSION] STATUS | SHOW [GLOBAL|SESSION] STATUS > Synopsis | SHOW [GLOBAL|SESSION] STATUS > Examples | SHOW [GLOBAL|SESSION] STATUS > MySQL compatibility | SHOW [GLOBAL|SESSION] STATUS > See also`
- Source Line Ranges: `5-73`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `show status`, `mysql compatibility`, `syntax`, `examples`, `status variables`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0680_63a04bfcfd`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-status.md#show-global-session-status`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd9d43eb2f3079bb2cb5f6fb886609ee14d030bc4cf27bc45662e15cc9eec5a3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-status#show-global-session-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-status.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about the syntax, examples, or MySQL compatibility of `SHOW GLOBAL STATUS` or `SHOW SESSION STATUS` in TiDB.
- Retrieval Keywords: SHOW GLOBAL STATUS, SHOW SESSION STATUS, SHOW STATUS, ShowStatusStmt, SHOW Scope STATUS, LIKE SimpleExpr, WHERE Expression, MySQL compatibility, status variables, Prometheus and Grafana, FLUSH STATUS, Server Status Variables, Uptime, ddl_schema_version, server_id
- Follow-up Guidance: The source also points to `FLUSH STATUS` and `Server Status Variables` for related information.
- Classification Note: This is a SQL reference chunk because the official content defines the statement syntax, gives example output, and notes compatibility and related references.

## Official Source Content

# SHOW [GLOBAL|SESSION] STATUS

This statement is included for compatibility with MySQL. TiDB uses Prometheus and Grafana for centralized metrics collection instead of `SHOW STATUS` for most metrics.

A full description of the variables can be found here: [status variables](https://docs.pingcap.com/tidb/stable/status-variables)
## Synopsis

```ebnf+diagram
ShowStatusStmt ::=
    'SHOW' Scope? 'STATUS' ShowLikeOrWhere?

Scope ::=
    ( 'GLOBAL' | 'SESSION' )

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

```sql
mysql> SHOW SESSION STATUS;
+-------------------------------+--------------------------------------+
| Variable_name                 | Value                                |
+-------------------------------+--------------------------------------+
| Compression                   | OFF                                  |
| Compression_algorithm         |                                      |
| Compression_level             | 0                                    |
| Ssl_cipher                    |                                      |
| Ssl_cipher_list               |                                      |
| Ssl_server_not_after          |                                      |
| Ssl_server_not_before         |                                      |
| Ssl_verify_mode               | 0                                    |
| Ssl_version                   |                                      |
| Uptime                        | 1409                                 |
| ddl_schema_version            | 116                                  |
| last_plan_binding_update_time | 0000-00-00 00:00:00                  |
| server_id                     | 61160e73-ab80-40ff-8f33-27d55d475fd1 |
+-------------------------------+--------------------------------------+
13 rows in set (0.00 sec)

mysql> SHOW GLOBAL STATUS;
+-----------------------+--------------------------------------+
| Variable_name         | Value                                |
+-----------------------+--------------------------------------+
| Ssl_cipher            |                                      |
| Ssl_cipher_list       |                                      |
| Ssl_server_not_after  |                                      |
| Ssl_server_not_before |                                      |
| Ssl_verify_mode       | 0                                    |
| Ssl_version           |                                      |
| Uptime                | 1413                                 |
| ddl_schema_version    | 116                                  |
| server_id             | 61160e73-ab80-40ff-8f33-27d55d475fd1 |
+-----------------------+--------------------------------------+
9 rows in set (0.00 sec)
```
## MySQL compatibility

* This statement is compatible with MySQL.
## See also

* [FLUSH STATUS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flush-status)
* [Server Status Variables](https://docs.pingcap.com/tidb/stable/status-variables)
