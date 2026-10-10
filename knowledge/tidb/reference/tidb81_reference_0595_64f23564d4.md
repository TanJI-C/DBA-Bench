# FLUSH PRIVILEGES statement reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-flush-privileges.md`
- Source Title: `FLUSH PRIVILEGES | TiDB SQL Statement Reference`
- Source Heading Path: `FLUSH PRIVILEGES | FLUSH PRIVILEGES > Synopsis | FLUSH PRIVILEGES > Examples | FLUSH PRIVILEGES > MySQL compatibility | FLUSH PRIVILEGES > See also`
- Source Line Ranges: `5-47`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `privileges`, `reload`, `grant`, `revoke`, `mysql-compatibility`, `syntax`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0595_64f23564d4`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-flush-privileges.md#flush-privileges`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `876fd1fbfb1eb8efa8f6556cc79a1888c36f2a70c869cb5f01f95275640c3e17`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flush-privileges#flush-privileges
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-flush-privileges.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about the SQL statement that reloads the in-memory copy of privileges from privilege tables after manual edits such as to `mysql.user`.
- Retrieval Keywords: FLUSH PRIVILEGES, reload in-memory copy of privileges, privilege tables, mysql.user, GRANT, REVOKE, RELOAD privilege, MySQL compatibility, SHOW GRANTS, Privilege Management
- Follow-up Guidance: The content notes that `FLUSH PRIVILEGES` is not necessary after using privilege statements like `GRANT` or `REVOKE`, and that executing it requires the `RELOAD` privilege.
- Classification Note: This is a SQL statement reference because it provides the purpose, syntax synopsis, example, privilege requirement, and MySQL compatibility note for `FLUSH PRIVILEGES`.

## Official Source Content

# FLUSH PRIVILEGES

The statement `FLUSH PRIVILEGES` instructs TiDB to reload the in-memory copy of privileges from the privilege tables. You must execute this statement after manually editing tables such as `mysql.user`. However, executing this statement is not necessary after using privilege statements like `GRANT` or `REVOKE`. To execute this statement, the `RELOAD` privilege is required.
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
mysql> FLUSH PRIVILEGES;
Query OK, 0 rows affected (0.01 sec)
```
## MySQL compatibility

The `FLUSH PRIVILEGES` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [SHOW GRANTS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-grants)

* [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management)
