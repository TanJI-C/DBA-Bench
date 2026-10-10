# CREATE BINDING examples, limits, permissions, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-binding.md`
- Source Title: `CREATE [GLOBAL|SESSION] BINDING`
- Source Heading Path: `CREATE [GLOBAL|SESSION] BINDING > Examples | CREATE [GLOBAL|SESSION] BINDING > SQL statement truncation | CREATE [GLOBAL|SESSION] BINDING > Permissions | CREATE [GLOBAL|SESSION] BINDING > MySQL compatibility | CREATE [GLOBAL|SESSION] BINDING > See also`
- Source Line Ranges: `137-189`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `create-binding`, `sql-plan-management`, `plan-digest`, `statement-summary`, `sql-truncation`, `privileges`, `mysql-compatibility`, `optimizer-hints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0550_b2ecc66bbf`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-binding.md#examples`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `caad0b782b8995b2bece380d42cff12056d2b0ae5982e25bb4fad37bef112da6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-binding#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-binding.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about creating a binding from a historical execution plan, checking plan_digest from statement summary, SQL truncation limits for CREATE BINDING FROM HISTORY USING PLAN DIGEST, required privileges, or MySQL compatibility.
- Retrieval Keywords: CREATE BINDING FROM HISTORY USING PLAN DIGEST, plan_digest, INFORMATION_SCHEMA.STATEMENTS_SUMMARY, QUERY_SAMPLE_TEXT, @@LAST_PLAN_FROM_BINDING, tidb_stmt_summary_max_sql_length, statement summary tables, SUPER privilege, TiDB extension to MySQL syntax, IGNORE_INDEX(t, a), SHOW BINDINGS, DROP BINDING, SQL Plan Management, Optimizer Hints
- Follow-up Guidance: The see also section points to DROP [GLOBAL|SESSION] BINDING, SHOW [GLOBAL|SESSION] BINDINGS, ANALYZE TABLE, Optimizer Hints, and SQL Plan Management.
- Classification Note: This is reference content because it provides example SQL, a documented failure limit tied to tidb_stmt_summary_max_sql_length, the required SUPER privilege, and a MySQL compatibility note for CREATE BINDING.

## Official Source Content

The following example shows how to create a binding according to a historical execution plan.

```sql
mysql> CREATE TABLE t(id INT PRIMARY KEY , a INT, KEY(a));
Query OK, 0 rows affected (0.06 sec)

mysql> SELECT /*+ IGNORE_INDEX(t, a) */ * FROM t WHERE a = 1;
Empty set (0.01 sec)

mysql> SELECT plan_digest FROM INFORMATION_SCHEMA.STATEMENTS_SUMMARY WHERE QUERY_SAMPLE_TEXT = 'SELECT /*+ IGNORE_INDEX(t, a) */ * FROM t WHERE a = 1';
+------------------------------------------------------------------+
| plan_digest                                                      |
+------------------------------------------------------------------+
| 4e3159169cc63c14b139a4e7d72eae1759875c9a9581f94bb2079aae961189cb |
+------------------------------------------------------------------+
1 row in set (0.01 sec)

mysql> CREATE BINDING FROM HISTORY USING PLAN DIGEST '4e3159169cc63c14b139a4e7d72eae1759875c9a9581f94bb2079aae961189cb';
Query OK, 0 rows affected (0.02 sec)

mysql> SELECT * FROM t WHERE a = 1;
Empty set (0.01 sec)

mysql> SELECT @@LAST_PLAN_FROM_BINDING;
+--------------------------+
| @@LAST_PLAN_FROM_BINDING |
+--------------------------+
|                        1 |
+--------------------------+
1 row in set (0.01 sec)

```
## SQL statement truncation

When you use `CREATE BINDING ... FROM HISTORY USING PLAN DIGEST`, the binding can fail if the SQL statement stored in [statement summary tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables) for that digest is truncated because it is longer than [`tidb_stmt_summary_max_sql_length`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_stmt_summary_max_sql_length-new-in-v40). In this case, you need to increase `tidb_stmt_summary_max_sql_length`.
## Permissions

The `CREATE BINDING` statement requires the `SUPER` privilege.
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [DROP [GLOBAL|SESSION] BINDING](/sql-statements/sql-statement-drop-binding.md)
* [SHOW [GLOBAL|SESSION] BINDINGS](/sql-statements/sql-statement-show-bindings.md)
* [ANALYZE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table)
* [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints)
* [SQL Plan Management](https://docs.pingcap.com/tidb/stable/sql-plan-management)
