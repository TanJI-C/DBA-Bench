# Multi-valued index hints and plan cache behavior

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/choose-index.md`
- Source Title: `Index Selection`
- Source Heading Path: `Index Selection > Use multi-valued indexes > Supported scenarios | Index Selection > Use multi-valued indexes > Multi-valued indexes and plan cache`
- Source Line Ranges: `599-687`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `multi-valued-indexes`, `optimizer-hints`, `index-merge`, `plan-cache`, `member-of`, `json-contains`, `json-overlaps`, `explain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0081_f8f9fc5c1c`
- Source ID: `tidb-docs-8.1:choose-index.md#supported-scenarios`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `08a46cb2ca2dbccb524e4c8c0f3ee7c6b9b6a84d132fb22da4e084fa18ee2a7a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/choose-index#supported-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/choose-index.md

## Retrieval Guidance

- Use When: Use this chunk when asking about multi-valued index optimizer hints, the `Can't find a proper physical plan for this query` error with `use_index`, or whether plan cache works for `member of`, `JSON_CONTAINS()`, and `JSON_OVERLAPS()` with multi-valued indexes.
- Retrieval Keywords: multi-valued indexes, use_index, use_index_merge, Can't find a proper physical plan for this query, ERROR 1815 (HY000), member of, JSON_CONTAINS(), JSON_OVERLAPS(), plan cache, @@last_plan_from_cache, skip prepared plan-cache: json_contains function with immutable parameters can affect index selection, EXPLAIN SELECT /*+ use_index(t3, idx) */, EXPLAIN SELECT /*+ use_index_merge(t3, idx) */
- Follow-up Guidance: The content also shows prepared statement examples with `PREPARE`, `EXECUTE`, `SHOW WARNINGS`, and `@@last_plan_from_cache` to illustrate when a plan using multi-valued indexes is cached or skipped.
- Classification Note: This is classified under performance for SQL because it explains optimizer hint behavior and plan cache eligibility when choosing multi-valued indexes.

## Official Source Content

Limited by the current implementation of multi-valued indexes, using [`use_index`](https://docs.pingcap.com/tidb/stable/optimizer-hints#use_indext1_name-idx1_name--idx2_name-) might return the `Can't find a proper physical plan for this query` error while using [`use_index_merge`](https://docs.pingcap.com/tidb/stable/optimizer-hints#use_index_merget1_name-idx1_name--idx2_name-) will not return such an error. Therefore, it is recommended to use `use_index_merge` if you want to use multi-valued indexes.

```sql
mysql> EXPLAIN SELECT /*+ use_index(t3, idx) */ * FROM t3 WHERE ((1 member of (j)) AND (2 member of (j))) OR ((3 member of (j)) AND (4 member of (j)));
ERROR 1815 (HY000): Internal : Cant find a proper physical plan for this query

mysql> EXPLAIN SELECT /*+ use_index_merge(t3, idx) */ * FROM t3 WHERE ((1 member of (j)) AND (2 member of (j))) OR ((3 member of (j)) AND (4 member of (j)));
+-------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| id                      | estRows  | task      | access object | operator info                                                                                                                                                                                                |
+-------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Selection_5             | 8000.00  | root      |               | or(and(json_memberof(cast(1, json BINARY), test.t3.j), json_memberof(cast(2, json BINARY), test.t3.j)), and(json_memberof(cast(3, json BINARY), test.t3.j), json_memberof(cast(4, json BINARY), test.t3.j))) |
| └─TableReader_7         | 10000.00 | root      |               | data:TableFullScan_6                                                                                                                                                                                         |
|   └─TableFullScan_6     | 10000.00 | cop[tikv] | table:t3      | keep order:false, stats:pseudo                                                                                                                                                                               |
+-------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
3 rows in set, 2 warnings (0.00 sec)
```
### Multi-valued indexes and plan cache

A query plan that uses `member of` to choose multi-valued indexes can be cached. A query plan that uses the `JSON_CONTAINS()` or `JSON_OVERLAPS()` function to choose multi-valued indexes cannot be cached.

The following are some examples that query plans can be cached:

```sql
mysql> CREATE TABLE t5 (j1 JSON, j2 JSON, INDEX idx1((CAST(j1 AS SIGNED ARRAY))));
Query OK, 0 rows affected (0.04 sec)

mysql> PREPARE st FROM 'SELECT /*+ use_index(t5, idx1) */ * FROM t5 WHERE (? member of (j1))';
Query OK, 0 rows affected (0.00 sec)

mysql> SET @a=1;
Query OK, 0 rows affected (0.00 sec)

mysql> EXECUTE st USING @a;
Empty set (0.01 sec)

mysql> EXECUTE st USING @a;
Empty set (0.00 sec)

mysql> SELECT @@last_plan_from_cache;
+------------------------+
| @@last_plan_from_cache |
+------------------------+
|                      1 |
+------------------------+
1 row in set (0.00 sec)

mysql> PREPARE st FROM 'SELECT /*+ use_index(t5, idx1) */ * FROM t5 WHERE (? member of (j1)) AND JSON_CONTAINS(j2, ?)';
Query OK, 0 rows affected (0.00 sec)

mysql> SET @a=1, @b='[1,2]';
Query OK, 0 rows affected (0.00 sec)

mysql> EXECUTE st USING @a, @b;
Empty set (0.00 sec)

mysql> EXECUTE st USING @a, @b;
Empty set (0.00 sec)

mysql> SELECT @@LAST_PLAN_FROM_CACHE; -- can hit plan cache if the JSON_CONTAINS doesn't impact index selection
+------------------------+
| @@LAST_PLAN_FROM_CACHE |
+------------------------+
|                      1 |
+------------------------+
1 row in set (0.00 sec)
```

The following are some examples that query plans cannot be cached:

```sql
mysql> PREPARE st2 FROM 'SELECT /*+ use_index(t5, idx1) */ * FROM t5 WHERE JSON_CONTAINS(j1, ?)';
Query OK, 0 rows affected (0.00 sec)

mysql> SET @a='[1,2]';
Query OK, 0 rows affected (0.01 sec)

mysql> EXECUTE st2 USING @a;
Empty set, 1 warning (0.00 sec)

mysql> SHOW WARNINGS;  -- cannot hit plan cache since the JSON_CONTAINS predicate might affect index selection
+---------+------+-------------------------------------------------------------------------------------------------------+
| Level   | Code | Message                                                                                               |
+---------+------+-------------------------------------------------------------------------------------------------------+
| Warning | 1105 | skip prepared plan-cache: json_contains function with immutable parameters can affect index selection |
+---------+------+-------------------------------------------------------------------------------------------------------+
1 row in set (0.01 sec)
```
