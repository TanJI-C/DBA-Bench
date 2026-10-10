# EXPLAIN IndexLookup examples and plan output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-indexes.md`
- Source Title: `Explain Statements That Use Indexes`
- Source Heading Path: `Explain Statements That Use Indexes | Explain Statements That Use Indexes > IndexLookup`
- Source Line Ranges: `5-95`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `indexes`, `indexlookup`, `execution-plan`, `index-range-scan`, `table-rowid-scan`, `sample-data`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0249_4f10cef302`
- Source ID: `tidb-docs-8.1:explain-indexes.md#explain-statements-that-use-indexes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5eeb0b86da010689f96177d5455f21e19013e44dfb8e8a895675759c34ef43dd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-indexes#explain-statements-that-use-indexes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when identifying why EXPLAIN shows an IndexLookUp plan for queries that retrieve data through the secondary index intkey on table t1.
- Retrieval Keywords: IndexLookup, IndexLookUp_10, IndexRangeScan_8(Build), TableRowIDScan_9(Probe), EXPLAIN SELECT * FROM t1 WHERE intkey = 123, EXPLAIN SELECT * FROM t1 WHERE intkey < 10, EXPLAIN SELECT * FROM t1 WHERE intkey BETWEEN 300 AND 310, EXPLAIN SELECT * FROM t1 WHERE intkey IN (123,29,98), EXPLAIN SELECT * FROM t1 WHERE intkey >= 99 AND intkey <= 103, table:t1, index:intkey(intkey), range:[123,123], range:[-inf,10), range:[300,310], range:[29,29], [98,98], [123,123], range:[99,103], cop[tikv], keep order:false
- Follow-up Guidance: The source continues by stating that the IndexLookup operator has two child nodes.
- Classification Note: This chunk is reference content because it provides concrete EXPLAIN examples and the corresponding IndexLookup, IndexRangeScan, and TableRowIDScan plan output for indexed queries.

## Official Source Content

# Explain Statements That Use Indexes

TiDB supports several operators which make use of indexes to speed up query execution:

+ [`IndexLookup`](#indexlookup)
+ [`IndexReader`](#indexreader)
+ [`Point_Get` and `Batch_Point_Get`](#point_get-and-batch_point_get)
+ [`IndexFullScan`](#indexfullscan)

The examples in this document are based on the following sample data:

```sql
CREATE TABLE t1 (
 id INT NOT NULL PRIMARY KEY auto_increment,
 intkey INT NOT NULL,
 pad1 VARBINARY(1024),
 INDEX (intkey)
);

INSERT INTO t1 SELECT NULL, FLOOR(RAND()*1024), RANDOM_BYTES(1024) FROM dual;
INSERT INTO t1 SELECT NULL, FLOOR(RAND()*1024), RANDOM_BYTES(1024) FROM t1 a JOIN t1 b JOIN t1 c LIMIT 10000;
INSERT INTO t1 SELECT NULL, FLOOR(RAND()*1024), RANDOM_BYTES(1024) FROM t1 a JOIN t1 b JOIN t1 c LIMIT 10000;
INSERT INTO t1 SELECT NULL, FLOOR(RAND()*1024), RANDOM_BYTES(1024) FROM t1 a JOIN t1 b JOIN t1 c LIMIT 10000;
```
## IndexLookup

TiDB uses the `IndexLookup` operator when retrieving data from a secondary index. In this case, the following queries will all use the `IndexLookup` operator on the `intkey` index:

```sql
EXPLAIN SELECT * FROM t1 WHERE intkey = 123;
EXPLAIN SELECT * FROM t1 WHERE intkey < 10;
EXPLAIN SELECT * FROM t1 WHERE intkey BETWEEN 300 AND 310;
EXPLAIN SELECT * FROM t1 WHERE intkey IN (123,29,98);
EXPLAIN SELECT * FROM t1 WHERE intkey >= 99 AND intkey <= 103;
```
```sql
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
| id                            | estRows | task      | access object                  | operator info                     |
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
| IndexLookUp_10                | 1.00    | root      |                                |                                   |
| ├─IndexRangeScan_8(Build)     | 1.00    | cop[tikv] | table:t1, index:intkey(intkey) | range:[123,123], keep order:false |
| └─TableRowIDScan_9(Probe)     | 1.00    | cop[tikv] | table:t1                       | keep order:false                  |
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
3 rows in set (0.00 sec)

+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
| id                            | estRows | task      | access object                  | operator info                     |
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
| IndexLookUp_10                | 3.60    | root      |                                |                                   |
| ├─IndexRangeScan_8(Build)     | 3.60    | cop[tikv] | table:t1, index:intkey(intkey) | range:[-inf,10), keep order:false |
| └─TableRowIDScan_9(Probe)     | 3.60    | cop[tikv] | table:t1                       | keep order:false                  |
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
3 rows in set (0.00 sec)

+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
| id                            | estRows | task      | access object                  | operator info                     |
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
| IndexLookUp_10                | 5.67    | root      |                                |                                   |
| ├─IndexRangeScan_8(Build)     | 5.67    | cop[tikv] | table:t1, index:intkey(intkey) | range:[300,310], keep order:false |
| └─TableRowIDScan_9(Probe)     | 5.67    | cop[tikv] | table:t1                       | keep order:false                  |
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
3 rows in set (0.00 sec)

+-------------------------------+---------+-----------+--------------------------------+-----------------------------------------------------+
| id                            | estRows | task      | access object                  | operator info                                       |
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------------------------+
| IndexLookUp_10                | 4.00    | root      |                                |                                                     |
| ├─IndexRangeScan_8(Build)     | 4.00    | cop[tikv] | table:t1, index:intkey(intkey) | range:[29,29], [98,98], [123,123], keep order:false |
| └─TableRowIDScan_9(Probe)     | 4.00    | cop[tikv] | table:t1                       | keep order:false                                    |
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------------------------+
3 rows in set (0.00 sec)

+-------------------------------+---------+-----------+--------------------------------+----------------------------------+
| id                            | estRows | task      | access object                  | operator info                    |
+-------------------------------+---------+-----------+--------------------------------+----------------------------------+
| IndexLookUp_10                | 6.00    | root      |                                |                                  |
| ├─IndexRangeScan_8(Build)     | 6.00    | cop[tikv] | table:t1, index:intkey(intkey) | range:[99,103], keep order:false |
| └─TableRowIDScan_9(Probe)     | 6.00    | cop[tikv] | table:t1                       | keep order:false                 |
+-------------------------------+---------+-----------+--------------------------------+----------------------------------+
3 rows in set (0.00 sec)
```

The `IndexLookup` operator has two child nodes:
