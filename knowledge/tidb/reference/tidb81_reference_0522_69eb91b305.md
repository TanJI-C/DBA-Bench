# ALTER INDEX visibility syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-index.md`
- Source Title: `ALTER INDEX`
- Source Heading Path: `ALTER INDEX | ALTER INDEX > Synopsis | ALTER INDEX > Examples | ALTER INDEX > MySQL compatibility | ALTER INDEX > See also`
- Source Line Ranges: `5-128`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `alter index`, `invisible indexes`, `visible indexes`, `optimizer`, `syntax`, `examples`, `mysql compatibility`, `sql hints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0522_69eb91b305`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-index.md#alter-index`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e7b7973fda6bc446d3f24a52b16a6352ef42b62e0256d498d8dc692074a72cf6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-index#alter-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-index.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax and behavior of ALTER TABLE ... ALTER INDEX to switch an index between VISIBLE and INVISIBLE, including optimizer behavior and MySQL compatibility notes.
- Retrieval Keywords: ALTER INDEX, ALTER TABLE ... ALTER INDEX ... VISIBLE, ALTER TABLE ... ALTER INDEX ... INVISIBLE, invisible indexes, visible indexes, tidb_opt_use_invisible_indexes, USE INDEX, ERROR 1176 (42000): Key 'c1' doesn't exist in table 't1', SHOW CREATE TABLE, EXPLAIN, PRIMARY KEY invisible, MySQL 8.0 compatibility
- Follow-up Guidance: The page also points to related statements CREATE TABLE, CREATE INDEX, ADD INDEX, DROP INDEX, and RENAME INDEX.
- Classification Note: This is a SQL reference chunk because it defines ALTER INDEX syntax, shows examples with EXPLAIN and SHOW CREATE TABLE, and states compatibility behavior for invisible indexes.

## Official Source Content

# ALTER INDEX

The `ALTER INDEX` statement is used to modify the visibility of the index to `Visible` or `Invisible`. Invisible indexes are maintained by DML statements, but will not be used by the query optimizer. This is useful in scenarios where you want to double-check before removing an index permanently. Starting from TiDB v8.0.0, you can make the optimizer select invisible indexes by modifying the system variable [`tidb_opt_use_invisible_indexes`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_use_invisible_indexes-new-in-v800).
## Synopsis

```ebnf+diagram
AlterTableStmt
         ::= 'ALTER' 'IGNORE'? 'TABLE' TableName AlterIndexSpec ( ',' AlterIndexSpec )*

AlterIndexSpec
         ::= 'ALTER' 'INDEX' Identifier ( 'VISIBLE' | 'INVISIBLE' )
```
## Examples

You can modify the visibility of an index using the `ALTER TABLE ... ALTER INDEX ...` statement.

```sql
CREATE TABLE t1 (c1 INT, UNIQUE(c1));
ALTER TABLE t1 ALTER INDEX c1 INVISIBLE;
```

```sql
Query OK, 0 rows affected (0.02 sec)
```

```sql
SHOW CREATE TABLE t1;
```

```sql
+-------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Table | Create Table
                                    |
+-------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t1    | CREATE TABLE `t1` (
  `c1` int(11) DEFAULT NULL,
  UNIQUE KEY `c1` (`c1`) /*!80000 INVISIBLE */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin |
+-------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

The optimizer cannot use the **invisible index** of `c1`.

```sql
EXPLAIN SELECT c1 FROM t1 ORDER BY c1;
```

```sql
+-------------------------+----------+-----------+---------------+--------------------------------+
| id                      | estRows  | task      | access object | operator info                  |
+-------------------------+----------+-----------+---------------+--------------------------------+
| Sort_4                  | 10000.00 | root      |               | test.t1.c1:asc                 |
| └─TableReader_8         | 10000.00 | root      |               | data:TableFullScan_7           |
|   └─TableFullScan_7     | 10000.00 | cop[tikv] | table:t1      | keep order:false, stats:pseudo |
+-------------------------+----------+-----------+---------------+--------------------------------+
3 rows in set (0.00 sec)
```

By comparison, `c2` is a **visible index** and can be used by the optimizer.

```sql
EXPLAIN SELECT c2 FROM t1 ORDER BY c2;
```

```sql
+------------------------+----------+-----------+------------------------+-------------------------------+
| id                     | estRows  | task      | access object          | operator info                 |
+------------------------+----------+-----------+------------------------+-------------------------------+
| IndexReader_13         | 10000.00 | root      |                        | index:IndexFullScan_12        |
| └─IndexFullScan_12     | 10000.00 | cop[tikv] | table:t1, index:c2(c2) | keep order:true, stats:pseudo |
+------------------------+----------+-----------+------------------------+-------------------------------+
2 rows in set (0.00 sec)
```

Even if you use the `USE INDEX` SQL hint to forcibly use indexes, the optimizer still cannot use invisible indexes; otherwise, an error is returned.

```sql
SELECT * FROM t1 USE INDEX(c1);
```

```sql
ERROR 1176 (42000): Key 'c1' doesn't exist in table 't1'
```

> **Note:**
>
> "Invisible" here means invisible only to the optimizer. You can still modify or delete invisible indexes.

```sql
ALTER TABLE t1 DROP INDEX c1;
```

```sql
Query OK, 0 rows affected (0.02 sec)
```
## MySQL compatibility

* Invisible indexes in TiDB are modeled on the equivalent feature from MySQL 8.0.
* Similar to MySQL, TiDB does not permit `PRIMARY KEY` indexes to be made invisible.
## See also

* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [CREATE INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index)
* [ADD INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index)
* [DROP INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-index)
* [RENAME INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rename-index)
