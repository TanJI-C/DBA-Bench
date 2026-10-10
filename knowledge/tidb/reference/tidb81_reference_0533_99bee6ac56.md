# ALTER TABLE examples and algorithm assertions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-table.md`
- Source Title: `ALTER TABLE | TiDB SQL Statement Reference`
- Source Heading Path: `ALTER TABLE > Examples`
- Source Line Ranges: `64-165`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `ddl`, `alter-table`, `examples`, `add-index`, `explain`, `algorithm`, `instant`, `inplace`, `copy`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0533_99bee6ac56`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-table.md#examples`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6cf6f0298aebbd10dfd6a3761a5a126ddb8ed697537842bdf93fdf87e6fba5f6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-table.md

## Retrieval Guidance

- Use When: Use this chunk when you need ALTER TABLE examples showing ADD INDEX effects in EXPLAIN output or how ALGORITHM assertions produce errors or warnings.
- Retrieval Keywords: ALTER TABLE examples, EXPLAIN SELECT * FROM t1 WHERE c1 = 3, ALTER TABLE t1 ADD INDEX (c1), IndexRangeScan, TableFullScan, ALGORITHM=INSTANT, ALGORITHM=INPLACE, ALGORITHM=COPY, ERROR 1846 (0A000), SHOW WARNINGS, Cannot alter table by INSTANT, Cannot alter table by COPY
- Follow-up Guidance: The source shows that ALGORITHM=INSTANT on ADD INDEX returns ERROR 1846 and that ALGORITHM=COPY on an INPLACE operation can be inspected with SHOW WARNINGS.
- Classification Note: This is reference content because it demonstrates concrete SQL examples and the exact returned plans, warnings, and errors for ALTER TABLE behavior.

## Official Source Content

## Examples

Create a table with some initial data:

```sql
CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, c1 INT NOT NULL);
INSERT INTO t1 (c1) VALUES (1),(2),(3),(4),(5);
```

```sql
Query OK, 0 rows affected (0.11 sec)

Query OK, 5 rows affected (0.03 sec)
Records: 5  Duplicates: 0  Warnings: 0
```

The following query requires a full table scan because the column c1 is not indexed:

```sql
EXPLAIN SELECT * FROM t1 WHERE c1 = 3;
```

```sql
+-------------------------+----------+-----------+---------------+--------------------------------+
| id                      | estRows  | task      | access object | operator info                  |
+-------------------------+----------+-----------+---------------+--------------------------------+
| TableReader_7           | 10.00    | root      |               | data:Selection_6               |
| └─Selection_6           | 10.00    | cop[tikv] |               | eq(test.t1.c1, 3)              |
|   └─TableFullScan_5     | 10000.00 | cop[tikv] | table:t1      | keep order:false, stats:pseudo |
+-------------------------+----------+-----------+---------------+--------------------------------+
3 rows in set (0.00 sec)
```

The statement [`ALTER TABLE .. ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) can be used to add an index on the table t1. `EXPLAIN` confirms that the original query now uses an index range scan, which is more efficient:

```sql
ALTER TABLE t1 ADD INDEX (c1);
EXPLAIN SELECT * FROM t1 WHERE c1 = 3;
```

```sql
Query OK, 0 rows affected (0.30 sec)

+------------------------+---------+-----------+------------------------+---------------------------------------------+
| id                     | estRows | task      | access object          | operator info                               |
+------------------------+---------+-----------+------------------------+---------------------------------------------+
| IndexReader_6          | 10.00   | root      |                        | index:IndexRangeScan_5                      |
| └─IndexRangeScan_5     | 10.00   | cop[tikv] | table:t1, index:c1(c1) | range:[3,3], keep order:false, stats:pseudo |
+------------------------+---------+-----------+------------------------+---------------------------------------------+
2 rows in set (0.00 sec)
```

TiDB supports the ability to assert that DDL changes use a particular `ALTER` algorithm. Note that this is only an assertion, and does not change the actual algorithm used to modify the table:

```sql
ALTER TABLE t1 DROP INDEX c1, ALGORITHM=INSTANT;
```

```sql
Query OK, 0 rows affected (0.24 sec)
```

Using the `ALGORITHM=INSTANT` assertion on an operation that requires the `INPLACE` algorithm results in a statement error:

```sql
ALTER TABLE t1 ADD INDEX (c1), ALGORITHM=INSTANT;
```

```sql
ERROR 1846 (0A000): ALGORITHM=INSTANT is not supported. Reason: Cannot alter table by INSTANT. Try ALGORITHM=INPLACE.
```

However, using the `ALGORITHM=COPY` assertion for an `INPLACE` operation generates a warning instead of an error. This is because TiDB interprets the assertion as _this algorithm or better_. This behavior difference is useful for MySQL compatibility because the algorithm TiDB uses might differ from MySQL:

```sql
ALTER TABLE t1 ADD INDEX (c1), ALGORITHM=COPY;
SHOW WARNINGS;
```

```sql
Query OK, 0 rows affected, 1 warning (0.25 sec)

+-------+------+---------------------------------------------------------------------------------------------+
| Level | Code | Message                                                                                     |
+-------+------+---------------------------------------------------------------------------------------------+
| Error | 1846 | ALGORITHM=COPY is not supported. Reason: Cannot alter table by COPY. Try ALGORITHM=INPLACE. |
+-------+------+---------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
