# Stream aggregation execution plans and ordered input

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-aggregation.md`
- Source Title: `Explain Statements That Use Aggregation`
- Source Heading Path: `Explain Statements Using Aggregation > Stream Aggregation`
- Source Line Ranges: `118-173`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `aggregation`, `stream-aggregation`, `group-by`, `execution-plan`, `sort`, `index-scan`, `ordered-input`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0245_38f11ebe70`
- Source ID: `tidb-docs-8.1:explain-aggregation.md#stream-aggregation`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f141e51fea71794ff798e294ad67becab9c2423e435c5232e7dd99b6a7c87f11`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-aggregation#stream-aggregation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-aggregation.md

## Retrieval Guidance

- Use When: Use this chunk when explaining why a Stream Aggregation plan includes a Sort operator and how ordered input from an index scan changes the EXPLAIN output.
- Retrieval Keywords: Stream Aggregation, STREAM_AGG(), EXPLAIN SELECT /*+ STREAM_AGG() */ col1, count(*) FROM t2 GROUP BY col1, Sort_13, IndexFullScan_13, keep order:true, keep order:false, TableFullScan_11, IndexReader_15, StreamAgg_8, group by:test.t2.col1, ALTER TABLE t2 ADD INDEX (col1), ordered input
- Follow-up Guidance: The content also shows that after `ALTER TABLE t2 ADD INDEX (col1)`, the EXPLAIN plan changes from `TableFullScan` plus `Sort` to an ordered `IndexFullScan` and removes `Sort_13`.
- Classification Note: This is reference content because it compares EXPLAIN plans for stream aggregation and identifies plan operators and ordered-input conditions such as `Sort`, `IndexFullScan`, and `keep order:true`.

## Official Source Content

## Stream Aggregation

The Stream Aggregation algorithm usually consumes less memory than Hash Aggregation. However, this operator requires that data is sent ordered so that it can _stream_ and apply the aggregation on values as they arrive.

Consider the following example:

```sql
CREATE TABLE t2 (id INT NOT NULL PRIMARY KEY, col1 INT NOT NULL);
INSERT INTO t2 VALUES (1, 9),(2, 3),(3,1),(4,8),(6,3);
EXPLAIN SELECT /*+ STREAM_AGG() */ col1, count(*) FROM t2 GROUP BY col1;
```

```sql
Query OK, 0 rows affected (0.11 sec)

Query OK, 5 rows affected (0.01 sec)
Records: 5  Duplicates: 0  Warnings: 0

+------------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------+
| id                           | estRows  | task      | access object | operator info                                                                               |
+------------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------+
| Projection_4                 | 8000.00  | root      |               | test.t2.col1, Column#3                                                                      |
| └─StreamAgg_8                | 8000.00  | root      |               | group by:test.t2.col1, funcs:count(1)->Column#3, funcs:firstrow(test.t2.col1)->test.t2.col1 |
|   └─Sort_13                  | 10000.00 | root      |               | test.t2.col1                                                                                |
|     └─TableReader_12         | 10000.00 | root      |               | data:TableFullScan_11                                                                       |
|       └─TableFullScan_11     | 10000.00 | cop[tikv] | table:t2      | keep order:false, stats:pseudo                                                              |
+------------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------+
5 rows in set (0.00 sec)
```

In this example, the `└─Sort_13` operator can be eliminated by adding an index on `col1`. Once the index is added, the data can be read in order and the `└─Sort_13` operator is eliminated:

```sql
ALTER TABLE t2 ADD INDEX (col1);
EXPLAIN SELECT /*+ STREAM_AGG() */ col1, count(*) FROM t2 GROUP BY col1;
```

```sql
Query OK, 0 rows affected (0.28 sec)

+------------------------------+---------+-----------+----------------------------+----------------------------------------------------------------------------------------------------+
| id                           | estRows | task      | access object              | operator info                                                                                      |
+------------------------------+---------+-----------+----------------------------+----------------------------------------------------------------------------------------------------+
| Projection_4                 | 4.00    | root      |                            | test.t2.col1, Column#3                                                                             |
| └─StreamAgg_14               | 4.00    | root      |                            | group by:test.t2.col1, funcs:count(Column#4)->Column#3, funcs:firstrow(test.t2.col1)->test.t2.col1 |
|   └─IndexReader_15           | 4.00    | root      |                            | index:StreamAgg_8                                                                                  |
|     └─StreamAgg_8            | 4.00    | cop[tikv] |                            | group by:test.t2.col1, funcs:count(1)->Column#4                                                    |
|       └─IndexFullScan_13     | 5.00    | cop[tikv] | table:t2, index:col1(col1) | keep order:true, stats:pseudo                                                                      |
+------------------------------+---------+-----------+----------------------------+----------------------------------------------------------------------------------------------------+
5 rows in set (0.00 sec)
```
