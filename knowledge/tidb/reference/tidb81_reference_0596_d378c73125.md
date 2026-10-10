# FLUSH STATUS syntax, behavior, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-flush-status.md`
- Source Title: `FLUSH STATUS | TiDB SQL Statement Reference`
- Source Heading Path: `FLUSH STATUS | FLUSH STATUS > Synopsis | FLUSH STATUS > Examples | FLUSH STATUS > MySQL compatibility | FLUSH STATUS > See also`
- Source Line Ranges: `5-81`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `flush status`, `sql syntax`, `mysql compatibility`, `show status`, `metrics collection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0596_d378c73125`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-flush-status.md#flush-status`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8fb843ef67a336905dccdb51ab6f5cc287c9858088594a0fe20de351b939eb24`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flush-status#flush-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-flush-status.md

## Retrieval Guidance

- Use When: Use this when someone asks what FLUSH STATUS does in TiDB, whether it resets SHOW STATUS output, or how its syntax and MySQL compatibility are documented.
- Retrieval Keywords: FLUSH STATUS, flush status, SHOW STATUS, SHOW GLOBAL STATUS, MySQL compatibility, NoWriteToBinLogAliasOpt, NO_WRITE_TO_BINLOG, LOCAL, FlushOption, Prometheus, Grafana, centralized metrics collection, it has no effect on TiDB
- Follow-up Guidance: The source also points to SHOW [GLOBAL|SESSION] STATUS and Server Status Variables.
- Classification Note: This is reference content because it defines the FLUSH STATUS syntax, shows example SQL output, and states that the statement is included for MySQL compatibility but has no effect on TiDB.

## Official Source Content

# FLUSH STATUS

This statement is included for compatibility with MySQL. It has no effect on TiDB, which uses Prometheus and Grafana for centralized metrics collection instead of `SHOW STATUS`.
## Synopsis

```ebnf+diagram
FlushStmt ::=
    'FLUSH' NoWriteToBinLogAliasOpt FlushOption

NoWriteToBinLogAliasOpt ::=
    ( 'NO_WRITE_TO_BINLOG' | 'LOCAL' )?

FlushOption ::=
    'PRIVILEGES'
|   'STATUS'
|    'TIDB' 'PLUGINS' PluginNameList
|    'HOSTS'
|   LogTypeOpt 'LOGS'
|   TableOrTables TableNameListOpt WithReadLockOpt
```
## Examples

```sql
mysql> show status;
+--------------------+--------------------------------------+
| Variable_name      | Value                                |
+--------------------+--------------------------------------+
| Ssl_cipher_list    |                                      |
| server_id          | 93e2e07d-6bb4-4a1b-90b7-e035fae154fe |
| ddl_schema_version | 141                                  |
| Ssl_verify_mode    | 0                                    |
| Ssl_version        |                                      |
| Ssl_cipher         |                                      |
+--------------------+--------------------------------------+
6 rows in set (0.01 sec)

mysql> show global status;
+--------------------+--------------------------------------+
| Variable_name      | Value                                |
+--------------------+--------------------------------------+
| Ssl_cipher         |                                      |
| Ssl_cipher_list    |                                      |
| Ssl_verify_mode    | 0                                    |
| Ssl_version        |                                      |
| server_id          | 93e2e07d-6bb4-4a1b-90b7-e035fae154fe |
| ddl_schema_version | 141                                  |
+--------------------+--------------------------------------+
6 rows in set (0.00 sec)

mysql> flush status;
Query OK, 0 rows affected (0.00 sec)

mysql> show status;
+--------------------+--------------------------------------+
| Variable_name      | Value                                |
+--------------------+--------------------------------------+
| Ssl_cipher         |                                      |
| Ssl_cipher_list    |                                      |
| Ssl_verify_mode    | 0                                    |
| Ssl_version        |                                      |
| ddl_schema_version | 141                                  |
| server_id          | 93e2e07d-6bb4-4a1b-90b7-e035fae154fe |
+--------------------+--------------------------------------+
6 rows in set (0.00 sec)
```
## MySQL compatibility

* This statement is compatible with MySQL.
## See also

* [SHOW \[GLOBAL|SESSION\] STATUS](/sql-statements/sql-statement-show-status.md)
* [Server Status Variables](https://docs.pingcap.com/tidb/stable/status-variables)
