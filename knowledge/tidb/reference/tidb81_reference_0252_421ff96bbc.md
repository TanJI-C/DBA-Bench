# Point_Get and Batch_Point_Get access paths

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-indexes.md`
- Source Title: `Explain Statements That Use Indexes`
- Source Heading Path: `Explain Statements That Use Indexes > Point_Get and Batch_Point_Get`
- Source Line Ranges: `174-228`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `point_get`, `batch_point_get`, `primary key`, `unique key`, `handle`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0252_421ff96bbc`
- Source ID: `tidb-docs-8.1:explain-indexes.md#point-get-and-batch-point-get`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ad1f71f94bd6c19769f89628f14427b9e0adada462c87e2351651d6f1adf2405`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-indexes#point-get-and-batch-point-get
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting EXPLAIN plans that show Point_Get or Batch_Point_Get for lookups by primary key or unique key.
- Retrieval Keywords: Point_Get, Batch_Point_Get, primary key, unique key, handle, Batch_Point_Get_1, Point_Get_1, EXPLAIN SELECT * FROM t1 WHERE id = 1234, EXPLAIN SELECT * FROM t1 WHERE id IN (1234,123), EXPLAIN SELECT * FROM t1 WHERE unique_key = 1234, EXPLAIN SELECT * FROM t1 WHERE unique_key IN (1234, 123), index:unique_key(unique_key)
- Follow-up Guidance: The content states that Point_Get and Batch_Point_Get are more efficient than IndexLookup when retrieving data directly from a primary key or unique key.
- Classification Note: This is reference content because it defines the EXPLAIN access paths Point_Get and Batch_Point_Get and shows their output for primary key and unique key queries.

## Official Source Content

## Point_Get and Batch_Point_Get

TiDB uses the `Point_Get` or `Batch_Point_Get` operator when retrieving data directly from a primary key or unique key. These operators are more efficient than `IndexLookup`. For example:

```sql
EXPLAIN SELECT * FROM t1 WHERE id = 1234;
EXPLAIN SELECT * FROM t1 WHERE id IN (1234,123);

ALTER TABLE t1 ADD unique_key INT;
UPDATE t1 SET unique_key = id;
ALTER TABLE t1 ADD UNIQUE KEY (unique_key);

EXPLAIN SELECT * FROM t1 WHERE unique_key = 1234;
EXPLAIN SELECT * FROM t1 WHERE unique_key IN (1234, 123);
```

```sql
+-------------+---------+------+---------------+---------------+
| id          | estRows | task | access object | operator info |
+-------------+---------+------+---------------+---------------+
| Point_Get_1 | 1.00    | root | table:t1      | handle:1234   |
+-------------+---------+------+---------------+---------------+
1 row in set (0.00 sec)

+-------------------+---------+------+---------------+-------------------------------------------------+
| id                | estRows | task | access object | operator info                                   |
+-------------------+---------+------+---------------+-------------------------------------------------+
| Batch_Point_Get_1 | 2.00    | root | table:t1      | handle:[1234 123], keep order:false, desc:false |
+-------------------+---------+------+---------------+-------------------------------------------------+
1 row in set (0.00 sec)

Query OK, 0 rows affected (0.27 sec)

Query OK, 1010 rows affected (0.06 sec)
Rows matched: 1010  Changed: 1010  Warnings: 0

Query OK, 0 rows affected (0.37 sec)

+-------------+---------+------+----------------------------------------+---------------+
| id          | estRows | task | access object                          | operator info |
+-------------+---------+------+----------------------------------------+---------------+
| Point_Get_1 | 1.00    | root | table:t1, index:unique_key(unique_key) |               |
+-------------+---------+------+----------------------------------------+---------------+
1 row in set (0.00 sec)

+-------------------+---------+------+----------------------------------------+------------------------------+
| id                | estRows | task | access object                          | operator info                |
+-------------------+---------+------+----------------------------------------+------------------------------+
| Batch_Point_Get_1 | 2.00    | root | table:t1, index:unique_key(unique_key) | keep order:false, desc:false |
+-------------------+---------+------+----------------------------------------+------------------------------+
1 row in set (0.00 sec)
```
