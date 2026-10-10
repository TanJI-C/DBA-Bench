# EXECUTE statement syntax, example, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-execute.md`
- Source Title: `EXECUTE | TiDB SQL Statement Reference`
- Source Heading Path: `EXECUTE | EXECUTE > Synopsis | EXECUTE > Examples | EXECUTE > MySQL compatibility | EXECUTE > See also`
- Source Line Ranges: `5-45`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `execute`, `prepared-statements`, `syntax`, `examples`, `mysql-compatibility`, `prepare`, `deallocate`, `user-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0584_a72ba8bdaf`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-execute.md#execute`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7c1dc21e84d838a048a738dceb31db8993314544362df1ead95d0ace5af1b8c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-execute#execute
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-execute.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the SQL syntax, example usage, or MySQL compatibility of the EXECUTE statement for server-side prepared statements.
- Retrieval Keywords: EXECUTE, ExecuteStmt ::= 'EXECUTE' Identifier ( 'USING' UserVariable ( ',' UserVariable )* )?, server-side prepared statements, EXECUTE mystmt USING @number, PREPARE mystmt FROM 'SELECT ? as num FROM DUAL', SET @number = 5, DEALLOCATE PREPARE mystmt, MySQL compatibility, UserVariable
- Follow-up Guidance: The source also points to related statements PREPARE and DEALLOCATE.
- Classification Note: This is reference content because it defines EXECUTE syntax, shows a concrete SQL example with PREPARE and DEALLOCATE, and states MySQL compatibility.

## Official Source Content

# EXECUTE

The `EXECUTE` statement provides an SQL interface to server-side prepared statements.
## Synopsis

```ebnf+diagram
ExecuteStmt ::=
    'EXECUTE' Identifier ( 'USING' UserVariable ( ',' UserVariable )* )?
```
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

The `EXECUTE` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [PREPARE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-prepare)
* [DEALLOCATE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-deallocate)
