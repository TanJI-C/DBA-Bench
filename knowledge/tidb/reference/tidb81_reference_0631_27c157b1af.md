# SELECT and SELECT INTO OUTFILE examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-select.md`
- Source Title: `SELECT | TiDB SQL Statement Reference`
- Source Heading Path: `SELECT > Examples | SELECT > Examples > SELECT | SELECT > Examples > SELECT ... INTO OUTFILE`
- Source Line Ranges: `82-199`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `cloud`, `tiup`
- Topic Tags: `select`, `examples`, `tablesample`, `outfile`, `csv`, `tsv`, `fields-terminated-by`, `fields-enclosed-by`, `lines-terminated-by`, `file-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0631_27c157b1af`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-select.md#examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84051335d2b7e3bf49fe9d8efa09ef9448a7ca1d2f896d3cc12be69ba7dd5946`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-select.md

## Retrieval Guidance

- Use When: Use this chunk when you need SELECT examples, TABLESAMPLE REGIONS query examples, or SELECT ... INTO OUTFILE file format examples and scope notes.
- Retrieval Keywords: SELECT examples, TABLESAMPLE REGIONS example, SELECT AVG(s_quantity), COUNT(s_quantity) FROM stock TABLESAMPLE REGIONS(), SELECT INTO OUTFILE, INTO OUTFILE '/tmp/tmp_file1', FIELDS TERMINATED BY, FIELDS ENCLOSED BY, LINES TERMINATED BY, CSV output, TSV output, /tmp/tmp_file2, /tmp/tmp_file3, TiDB Self-Managed, not available on TiDB Cloud, external storages, Amazon S3, GCS, tiup bench tpcc prepare
- Follow-up Guidance: The chunk states that SELECT ... INTO OUTFILE is only applicable to TiDB Self-Managed, not available on TiDB Cloud, and does not support writing query results to external storages such as Amazon S3 or GCS.
- Classification Note: This is a SQL reference examples chunk because it demonstrates SELECT usage, TABLESAMPLE behavior, and SELECT ... INTO OUTFILE output formatting with concrete SQL examples.

## Official Source Content

## Examples
### SELECT

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, c1 INT NOT NULL);
Query OK, 0 rows affected (0.11 sec)

mysql> INSERT INTO t1 (c1) VALUES (1),(2),(3),(4),(5);
Query OK, 5 rows affected (0.03 sec)
Records: 5  Duplicates: 0  Warnings: 0

mysql> SELECT * FROM t1;
+----+----+
| id | c1 |
+----+----+
|  1 |  1 |
|  2 |  2 |
|  3 |  3 |
|  4 |  4 |
|  5 |  5 |
+----+----+
5 rows in set (0.00 sec)
```

```sql
mysql> SELECT AVG(s_quantity), COUNT(s_quantity) FROM stock TABLESAMPLE REGIONS();
+-----------------+-------------------+
| AVG(s_quantity) | COUNT(s_quantity) |
+-----------------+-------------------+
|         59.5000 |                 4 |
+-----------------+-------------------+
1 row in set (0.00 sec)

mysql> SELECT AVG(s_quantity), COUNT(s_quantity) FROM stock;
+-----------------+-------------------+
| AVG(s_quantity) | COUNT(s_quantity) |
+-----------------+-------------------+
|         54.9729 |           1000000 |
+-----------------+-------------------+
1 row in set (0.52 sec)
```

The above example uses data generated with `tiup bench tpcc prepare`. The first query shows the use of `TABLESAMPLE`.
### SELECT ... INTO OUTFILE

The `SELECT ... INTO OUTFILE` statement is used to write the result of a query to a file.

> **Note:**
>
> - This statement is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).
> - This statement does not support writing query results to any [external storages](https://docs.pingcap.com/tidb/stable/backup-and-restore-storages) such as Amazon S3 or GCS.

In the statement, you can specify the format of the output file by using the following clauses:

- `FIELDS TERMINATED BY`: specifies the field delimiter in the file. For example, you can specify it as `','` to output comma-separated values (CSV) or `'\t'` to output tab-separated values (TSV).
- `FIELDS ENCLOSED BY`: specifies the enclosing character that wraps around each field in the file.
- `LINES TERMINATED BY`: specifies the line terminator in the file, if you want to end a line with a certain character.

Assume that there is a table `t` with three columns as follows:

```sql
mysql> CREATE TABLE t (a INT, b VARCHAR(10), c DECIMAL(10,2));
Query OK, 0 rows affected (0.02 sec)

mysql> INSERT INTO t VALUES (1, 'a', 1.1), (2, 'b', 2.2), (3, 'c', 3.3);
Query OK, 3 rows affected (0.01 sec)
```

The following examples show how to use the `SELECT ... INTO OUTFILE` statement to write the query result to a file.

**Example 1:**

```sql
mysql> SELECT * FROM t INTO OUTFILE '/tmp/tmp_file1';
Query OK, 3 rows affected (0.00 sec)
```

In this example, you can find the query result in `/tmp/tmp_file1` as follows:

```
1       a       1.10
2       b       2.20
3       c       3.30
```

**Example 2:**

```sql
mysql> SELECT * FROM t INTO OUTFILE '/tmp/tmp_file2' FIELDS TERMINATED BY ',' ENCLOSED BY '"';
Query OK, 3 rows affected (0.00 sec)
```

In this example, you can find the query result in `/tmp/tmp_file2` as follows:

```
"1","a","1.10"
"2","b","2.20"
"3","c","3.30"
```

**Example 3:**

```sql
mysql> SELECT * FROM t INTO OUTFILE '/tmp/tmp_file3'
    -> FIELDS TERMINATED BY ',' ENCLOSED BY '\'' LINES TERMINATED BY '<<<\n';
Query OK, 3 rows affected (0.00 sec)
```

In this example, you can find the query result in `/tmp/tmp_file3` as follows:

```
'1','a','1.10'<<<
'2','b','2.20'<<<
'3','c','3.30'<<<
```
