# SHOW ERRORS syntax, behavior, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-errors.md`
- Source Title: `SHOW ERRORS | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW ERRORS | SHOW ERRORS > Synopsis | SHOW ERRORS > Examples | SHOW ERRORS > MySQL compatibility | SHOW ERRORS > See also`
- Source Line Ranges: `5-59`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `show errors`, `sql syntax`, `error buffer`, `sql_mode`, `mysql compatibility`, `examples`, `show warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0659_4ba689a527`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-errors.md#show-errors`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1368d98932b937bf808ebc80b9b9e9af7b82eedb142d53aeb3a046541b2fd614`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-errors#show-errors
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-errors.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how `SHOW ERRORS` works in TiDB, including syntax, how the error buffer is cleared, filtering with `LIKE` or `WHERE`, example output, or MySQL compatibility.
- Retrieval Keywords: SHOW ERRORS, ShowErrorsStmt, SHOW ERRORS LIKE, SHOW ERRORS WHERE, error buffer is cleared as soon as a statement executes successfully, sql_mode, Unknown column 'invalid' in 'field list', ERROR 1054 (42S22), ERROR 1064 (42000), Empty set, SHOW WARNINGS, MySQL compatibility
- Follow-up Guidance: The source also points to `SHOW WARNINGS` as a related statement.
- Classification Note: This is reference content because it defines the `SHOW ERRORS` syntax, explains its behavior, gives SQL examples and output, and states MySQL compatibility.

## Official Source Content

# SHOW ERRORS

This statement shows errors from previously executed statements. The error buffer is cleared as soon as a statement executes successfully. In which case, `SHOW ERRORS` will return an empty set.

The behavior of which statements generate errors vs. warnings is highly influenced by the current `sql_mode`.
## Synopsis

```ebnf+diagram
ShowErrorsStmt ::=
    "SHOW" "ERRORS" ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

```sql
mysql> select invalid;
ERROR 1054 (42S22): Unknown column 'invalid' in 'field list'
mysql> create invalid;
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your TiDB version for the right syntax to use line 1 column 14 near "invalid"
mysql> SHOW ERRORS;
+-------+------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
| Level | Code | Message                                                                                                                                                   |
+-------+------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
| Error | 1054 | Unknown column 'invalid' in 'field list'                                                                                                                  |
| Error | 1064 | You have an error in your SQL syntax; check the manual that corresponds to your TiDB version for the right syntax to use line 1 column 14 near "invalid"  |
+-------+------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
2 rows in set (0.00 sec)

mysql> CREATE invalid2;
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your TiDB version for the right syntax to use line 1 column 15 near "invalid2"
mysql> SELECT 1;
+------+
| 1    |
+------+
|    1 |
+------+
1 row in set (0.00 sec)

mysql> SHOW ERRORS;
Empty set (0.00 sec)
```
## MySQL compatibility

The `SHOW ERRORS` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [SHOW WARNINGS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-warnings)
