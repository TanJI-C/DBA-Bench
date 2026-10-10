# ANALYZE statement syntax, usage, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-analyze-table.md`
- Source Title: `ANALYZE | TiDB SQL Statement Reference`
- Source Heading Path: `ANALYZE | ANALYZE > Synopsis | ANALYZE > Examples | ANALYZE > MySQL compatibility | ANALYZE > See also`
- Source Line Ranges: `5-105`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `analyze table`, `statistics`, `query plans`, `syntax`, `examples`, `mysql compatibility`, `explain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0536_05b8c7d15b`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-analyze-table.md#analyze`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0c9f2d64187fbcecd80d380baccf2814e4f4babe77091acc282438882c2ce3a6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table#analyze
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-analyze-table.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about `ANALYZE TABLE` syntax, examples of updating table and index statistics, or why `EXPLAIN` shows `stats:pseudo` and inaccurate `estRows` before statistics are collected.
- Retrieval Keywords: ANALYZE TABLE, AnalyzeTableStmt, ALL COLUMNS, PREDICATE COLUMNS, COLUMNS ColumnNameList, INDEX IndexNameList, PARTITION PartitionNameList, WITH NUM BUCKETS, NUM TOPN, CMSKETCH DEPTH, CMSKETCH WIDTH, NUM SAMPLES, SAMPLERATE, statistics, stats:pseudo, EXPLAIN, EXPLAIN ANALYZE, estRows, query execution plans, Introduction to statistics, MySQL compatibility, #16570, sleep(1)
- Follow-up Guidance: The source also points to `EXPLAIN`, `EXPLAIN ANALYZE`, and `Introduction to statistics`, and notes that after a batch update of rows you might need to `sleep(1)` before executing `ANALYZE TABLE` for the statistics update to reflect very recently committed changes.
- Classification Note: This is classified as reference content because it provides the `ANALYZE` statement grammar, behavior description, worked SQL examples, and MySQL compatibility notes from the official documentation.

## Official Source Content

# ANALYZE

This statement updates the statistics that TiDB builds on tables and indexes. It is recommended to run `ANALYZE` after performing a large batch update or import of records, or when you notice that query execution plans are sub-optimal.

TiDB will also automatically update its statistics over time as it discovers that they are inconsistent with its own estimates.

Currently, TiDB collects statistical information as a full collection by using the `ANALYZE TABLE` statement. For more information, see [Introduction to statistics](https://docs.pingcap.com/tidb/stable/statistics).
## Synopsis

```ebnf+diagram
AnalyzeTableStmt ::=
    'ANALYZE' ( 'TABLE' ( TableNameList ( 'ALL COLUMNS' | 'PREDICATE COLUMNS' ) | TableName ( 'INDEX' IndexNameList? | AnalyzeColumnOption | 'PARTITION' PartitionNameList ( 'INDEX' IndexNameList? | AnalyzeColumnOption )? )? ) ) AnalyzeOptionListOpt

AnalyzeOptionListOpt ::=
( WITH AnalyzeOptionList )?

AnalyzeOptionList ::=
AnalyzeOption ( ',' AnalyzeOption )*

AnalyzeOption ::=
( NUM ( 'BUCKETS' | 'TOPN' | ( 'CMSKETCH' ( 'DEPTH' | 'WIDTH' ) ) | 'SAMPLES' ) ) | ( FLOATNUM 'SAMPLERATE' )

AnalyzeColumnOption ::=
( 'ALL COLUMNS' | 'PREDICATE COLUMNS' | 'COLUMNS' ColumnNameList )

TableNameList ::=
    TableName (',' TableName)*

TableName ::=
    Identifier ( '.' Identifier )?

ColumnNameList ::=
    Identifier ( ',' Identifier )*

IndexNameList ::=
    Identifier ( ',' Identifier )*

PartitionNameList ::=
    Identifier ( ',' Identifier )*
```
## Examples

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, c1 INT NOT NULL);
Query OK, 0 rows affected (0.11 sec)
```

```sql
mysql> INSERT INTO t1 (c1) VALUES (1),(2),(3),(4),(5);
Query OK, 5 rows affected (0.03 sec)
Records: 5  Duplicates: 0  Warnings: 0
```

```sql
mysql> ALTER TABLE t1 ADD INDEX (c1);
Query OK, 0 rows affected (0.30 sec)
```

```sql
mysql> EXPLAIN SELECT * FROM t1 WHERE c1 = 3;
+------------------------+---------+-----------+------------------------+---------------------------------------------+
| id                     | estRows | task      | access object          | operator info                               |
+------------------------+---------+-----------+------------------------+---------------------------------------------+
| IndexReader_6          | 10.00   | root      |                        | index:IndexRangeScan_5                      |
| └─IndexRangeScan_5     | 10.00   | cop[tikv] | table:t1, index:c1(c1) | range:[3,3], keep order:false, stats:pseudo |
+------------------------+---------+-----------+------------------------+---------------------------------------------+
2 rows in set (0.00 sec)
```

The status of the current statistics is `pseudo`, which means the statistics is inaccurate.

```sql
mysql> ANALYZE TABLE t1;
Query OK, 0 rows affected (0.13 sec)

mysql> EXPLAIN SELECT * FROM t1 WHERE c1 = 3;
+------------------------+---------+-----------+------------------------+-------------------------------+
| id                     | estRows | task      | access object          | operator info                 |
+------------------------+---------+-----------+------------------------+-------------------------------+
| IndexReader_6          | 1.00    | root      |                        | index:IndexRangeScan_5        |
| └─IndexRangeScan_5     | 1.00    | cop[tikv] | table:t1, index:c1(c1) | range:[3,3], keep order:false |
+------------------------+---------+-----------+------------------------+-------------------------------+
2 rows in set (0.00 sec)
```

The statistics is now correctly updated and loaded.
## MySQL compatibility

TiDB differs from MySQL in **both** the statistics it collects and how it makes use of statistics during query execution. While this statement is syntactically similar to MySQL, the following differences apply:

+ TiDB might not include very recently committed changes when running `ANALYZE TABLE`. After a batch update of rows, you might need to `sleep(1)` before executing `ANALYZE TABLE` in order for the statistics update to reflect these changes. See [#16570](https://github.com/pingcap/tidb/issues/16570).
+ `ANALYZE TABLE` takes significantly longer to execute in TiDB than MySQL.
## See also

* [EXPLAIN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain)
* [EXPLAIN ANALYZE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze)
