# PREPARE statement syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-prepare.md`
- Source Title: `PREPARE | TiDB SQL Statement Reference`
- Source Heading Path: `PREPARE | PREPARE > Synopsis | PREPARE > Examples | PREPARE > MySQL compatibility | PREPARE > See also`
- Source Line Ranges: `5-55`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `prepare`, `prepared-statements`, `sql-syntax`, `placeholders`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0620_ac38590f33`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-prepare.md#prepare`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4123edc0dd0f13d32f0917c062f0cd538fe6780fafc8f93bf7b7eb59421da3c7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-prepare#prepare
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-prepare.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about the SQL syntax, placeholder limit, example usage, or MySQL compatibility of the PREPARE statement in TiDB.
- Retrieval Keywords: PREPARE, PreparedStmt ::= 'PREPARE' Identifier 'FROM' PrepareSQL, PrepareSQL, stringLit, UserVariable, server-side prepared statements, maximum number of placeholders is 65535, max_prepared_stmt_count, PREPARE mystmt FROM 'SELECT ? as num FROM DUAL', EXECUTE mystmt USING @number, DEALLOCATE PREPARE mystmt, MySQL compatibility
- Follow-up Guidance: The source also points to the related SQL statements EXECUTE and DEALLOCATE.
- Classification Note: This is reference content because it defines PREPARE statement syntax, limits, examples, and compatibility details for SQL prepared statements.

## Official Source Content

# PREPARE

The `PREPARE` statement provides an SQL interface to server-side prepared statements.
## Synopsis

```ebnf+diagram
PreparedStmt ::=
    'PREPARE' Identifier 'FROM' PrepareSQL

PrepareSQL ::=
    stringLit
|   UserVariable
```

> **Note:**
>
> For each `PREPARE` statement, the maximum number of placeholders is 65535.

To limit the number of `PREPARE` statements in the current TiDB instance, you can use the [`max_prepared_stmt_count`](https://docs.pingcap.com/tidb/stable/system-variables#max_prepared_stmt_count) system variable.
## Examples

```sql
mysql> PREPARE mystmt FROM 'SELECT ? as num FROM DUAL';
Query OK, 0 rows affected (0.00 sec)

mysql> SET @number = 5;
Query OK, 0 rows affected (0.00 sec)

mysql> EXECUTE mystmt USING @number;
+------+
| num  |
+------+
| 5    |
+------+
1 row in set (0.00 sec)

mysql> DEALLOCATE PREPARE mystmt;
Query OK, 0 rows affected (0.00 sec)
```
## MySQL compatibility

The `PREPARE` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [EXECUTE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-execute)
* [DEALLOCATE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-deallocate)
