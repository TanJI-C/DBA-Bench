# TABLE statement syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-table.md`
- Source Title: `TABLE | TiDB SQL Statement Reference`
- Source Heading Path: `TABLE | TABLE > Synopsis | TABLE > Examples | TABLE > MySQL compatibility | TABLE > See also`
- Source Line Ranges: `5-87`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `table-statement`, `syntax`, `examples`, `order-by`, `limit`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0694_3d1cfce34a`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-table.md#table`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `98f746b5a43dd44cfff27f4a3c2443a30c8b0bc6ccf49b90baa32418e127aad1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-table#table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-table.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about the TiDB `TABLE` statement syntax, examples, ordering, limiting, or how it compares to `SELECT * FROM` and MySQL compatibility.
- Retrieval Keywords: TABLE statement, TABLE t1, TABLE t1 ORDER BY id DESC, TABLE t1 LIMIT 1, SELECT * FROM, TableStmt ::= "TABLE" Table ( "ORDER BY" Column )? ( "LIMIT" NUM )?, MySQL 8.0.19, sql-statement-table
- Follow-up Guidance: The source also points to the related `SELECT` statement and MySQL `TABLE` statement documentation.
- Classification Note: This is reference content because it defines the `TABLE` statement syntax, shows example SQL and result sets, and notes MySQL compatibility.

## Official Source Content

# TABLE

The `TABLE` statement can be used instead of `SELECT * FROM` when no aggregation or complex filtering is needed.
## Synopsis

```ebnf+diagram
TableStmt ::=
    "TABLE" Table ( "ORDER BY" Column )? ( "LIMIT" NUM )?
```
## Examples

Create table `t1`:

```sql
CREATE TABLE t1(id INT PRIMARY KEY);
```

Insert some data into `t1`:

```sql
INSERT INTO t1 VALUES (1),(2),(3);
```

View the data in table `t1`:

```sql
TABLE t1;
```

```sql
+----+
| id |
+----+
|  1 |
|  2 |
|  3 |
+----+
3 rows in set (0.01 sec)
```

Query `t1` and sort the result by the `id` field in descending order:

```sql
TABLE t1 ORDER BY id DESC;
```

```sql
+----+
| id |
+----+
|  3 |
|  2 |
|  1 |
+----+
3 rows in set (0.01 sec)
```

Query the first record in `t1`:

```sql
TABLE t1 LIMIT 1;
```

```sql
+----+
| id |
+----+
|  1 |
+----+
1 row in set (0.01 sec)
```
## MySQL compatibility

The `TABLE` statement was introduced in MySQL 8.0.19.
## See also

- [`SELECT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select)
- [`TABLE` statements in MySQL](https://dev.mysql.com/doc/refman/8.0/en/table.html)
