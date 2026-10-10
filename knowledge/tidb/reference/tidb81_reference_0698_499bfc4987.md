# UPDATE statement syntax, examples, compatibility, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-update.md`
- Source Title: `UPDATE | TiDB SQL Statement Reference`
- Source Heading Path: `UPDATE | UPDATE > Synopsis | UPDATE > Examples | UPDATE > MySQL compatibility | UPDATE > See also`
- Source Line Ranges: `5-87`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `update`, `sql-syntax`, `resource-control`, `examples`, `mysql-compatibility`, `expression-evaluation`, `dml`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0698_499bfc4987`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-update.md#update`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ab0f9dc3eb14eaf726c752988e41acda9a56e97ead9fa7ae473acf3176b5d24`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update#update
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-update.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB UPDATE statement syntax, examples of modifying rows, or TiDB-specific behavior for expression evaluation and statement priority options.
- Retrieval Keywords: UPDATE, UpdateStmt, UpdateOption, TableRef, TableRefs, SET Assignment, WhereClause, OrderBy, Limit, LOW_PRIORITY, HIGH_PRIORITY, DELAYED, IGNORE, Resource Control, statement priority, MySQL compatibility, TiDB always uses the original value of a column when evaluating expressions, UPDATE t SET a = a+1,b=a, Rows matched, Changed, Warnings
- Follow-up Guidance: The related statements listed are INSERT, SELECT, DELETE, and REPLACE.
- Classification Note: This is reference content because it defines the UPDATE syntax, shows example SQL and results, and documents TiDB compatibility behavior compared with MySQL.

## Official Source Content

# UPDATE

The `UPDATE` statement is used to modify data in a specified table.
## Synopsis

```ebnf+diagram
UpdateStmt ::=
    "UPDATE" UpdateOption
(   TableRef "SET" Assignment ("," Assignment)* WhereClause? OrderBy? Limit?
|   TableRefs "SET" Assignment ("," Assignment)* WhereClause?
)

UpdateOption ::=
    OptimizerHints? ("LOW_PRIORITY" | "HIGH_PRIORITY" | "DELAYED")? "IGNORE"?

TableRef ::=
    ( TableFactor | JoinTable )

TableRefs ::=
    EscapedTableRef ("," EscapedTableRef)*
```

> **Note:**
>
> Starting from v6.6.0, TiDB supports [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control). You can use this feature to execute SQL statements with different priorities in different resource groups. By configuring proper quotas and priorities for these resource groups, you can gain better scheduling control for SQL statements with different priorities. When resource control is enabled, statement priority (`LOW_PRIORITY` and `HIGH_PRIORITY`) will no longer take effect. It is recommended that you use [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) to manage resource usage for different SQL statements.
## Examples

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, c1 INT NOT NULL);
Query OK, 0 rows affected (0.11 sec)

mysql> INSERT INTO t1 (c1) VALUES (1), (2), (3);
Query OK, 3 rows affected (0.02 sec)
Records: 3  Duplicates: 0  Warnings: 0

mysql> SELECT * FROM t1;
+----+----+
| id | c1 |
+----+----+
|  1 |  1 |
|  2 |  2 |
|  3 |  3 |
+----+----+
3 rows in set (0.00 sec)

mysql> UPDATE t1 SET c1=5 WHERE c1=3;
Query OK, 1 row affected (0.01 sec)
Rows matched: 1  Changed: 1  Warnings: 0

mysql> SELECT * FROM t1;
+----+----+
| id | c1 |
+----+----+
|  1 |  1 |
|  2 |  2 |
|  3 |  5 |
+----+----+
3 rows in set (0.00 sec)
```
## MySQL compatibility

TiDB always uses the original value of a column when evaluating expressions. For example:

```sql
CREATE TABLE t (a int, b int);
INSERT INTO t VALUES (1,2);
UPDATE t SET a = a+1,b=a;
```

In MySQL, the column `b` is updated to 2 because it is set to the value of `a`, and the value of `a` (which is 1) is updated to `a+1` (which is 2) in the same statement. 

TiDB follows the more standard SQL behavior, and updates `b` to 1.
## See also

* [INSERT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert)
* [SELECT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select)
* [DELETE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete)
* [REPLACE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-replace)
