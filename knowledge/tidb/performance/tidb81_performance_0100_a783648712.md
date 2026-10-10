# Index-based full table scan optimizations

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-optimize-sql.md`
- Source Title: `SQL Performance Tuning`
- Source Heading Path: `SQL Performance Tuning > Issue: Full table scan > Solution: Use covering index | SQL Performance Tuning > Issue: Full table scan > Solution: Use primary index`
- Source Line Ranges: `114-238`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `full-table-scan`, `covering-index`, `secondary-index`, `primary-key`, `explain`, `index-lookup`, `point-get`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0100_a783648712`
- Source ID: `tidb-docs-8.1:develop/dev-guide-optimize-sql.md#solution-use-covering-index`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd0caedda58710725963b00e11e2f1951d9297975c3907e4a0f3479e0521ec24`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql#solution-use-covering-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-optimize-sql.md

## Retrieval Guidance

- Use When: Use this content when looking for ways to avoid a full table scan by using a covering index or by filtering with the primary key and checking the EXPLAIN plan.
- Retrieval Keywords: full table scan, covering index, secondary index, primary index, EXPLAIN, IndexLookUp_10, IndexReader_6, IndexRangeScan_5, TableRowIDScan_9, Point_Get_1, title_idx, title_price_idx, ALTER TABLE books DROP INDEX title_idx, CREATE INDEX title_price_idx ON books (title, price), SELECT title, price FROM books WHERE title = 'Marian Yost', SELECT * FROM books WHERE id = 896, books, id, title, price
- Follow-up Guidance: The content shows EXPLAIN output before and after changing from `title_idx` to `title_price_idx`, and also shows that querying `books` by primary key `id` uses the `Point_Get` plan.
- Classification Note: This is classified as performance content because it explains SQL execution plan changes that make queries faster by scanning a covering index or using the primary key.

## Official Source Content

### Solution: Use covering index

If the index is a covering index, which contains all the columns queried by the SQL statements, scanning the index data is sufficient for the query.

For example, in the following query, you only need to query the corresponding `price` based on `title`:

```sql
SELECT title, price FROM books WHERE title = 'Marian Yost';
```

```sql
+-------------+--------+
| title       | price  |
+-------------+--------+
| Marian Yost | 435.01 |
| Marian Yost | 328.18 |
| Marian Yost | 496.52 |
| Marian Yost | 402.90 |
| Marian Yost | 174.64 |
+-------------+--------+
5 rows in set
Time: 0.007s
```

Because the `title_idx` index only contains data in the `title` column, TiDB still needs to first scan the index data and then query the `price` column from the table.

```sql
EXPLAIN SELECT title, price FROM books WHERE title = 'Marian Yost';
```

```sql
+---------------------------+---------+-----------+-------------------------------------+-------------------------------------------------------+
| id                        | estRows | task      | access object                       | operator info                                         |
+---------------------------+---------+-----------+-------------------------------------+-------------------------------------------------------+
| IndexLookUp_10            | 1.27    | root      |                                     |                                                       |
| ├─IndexRangeScan_8(Build) | 1.27    | cop[tikv] | table:books, index:title_idx(title) | range:["Marian Yost","Marian Yost"], keep order:false |
| └─TableRowIDScan_9(Probe) | 1.27    | cop[tikv] | table:books                         | keep order:false                                      |
+---------------------------+---------+-----------+-------------------------------------+-------------------------------------------------------+
```

To optimize the performance, drop the `title_idx` index and create a new covering index `title_price_idx`:

```sql
ALTER TABLE books DROP INDEX title_idx;
```

```sql
CREATE INDEX title_price_idx ON books (title, price);
```

Because the `price` data is stored in the `title_price_idx` index, the following query only needs to scan the index data:

```sql
EXPLAIN SELECT title, price FROM books WHERE title = 'Marian Yost';
```

```sql
--------------------+---------+-----------+--------------------------------------------------+-------------------------------------------------------+
| id                 | estRows | task      | access object                                    | operator info                                         |
+--------------------+---------+-----------+--------------------------------------------------+-------------------------------------------------------+
| IndexReader_6      | 1.27    | root      |                                                  | index:IndexRangeScan_5                                |
| └─IndexRangeScan_5 | 1.27    | cop[tikv] | table:books, index:title_price_idx(title, price) | range:["Marian Yost","Marian Yost"], keep order:false |
+--------------------+---------+-----------+--------------------------------------------------+-------------------------------------------------------+
```

Now this query runs faster:

```sql
SELECT title, price FROM books WHERE title = 'Marian Yost';
```

```sql
+-------------+--------+
| title       | price  |
+-------------+--------+
| Marian Yost | 174.64 |
| Marian Yost | 328.18 |
| Marian Yost | 402.90 |
| Marian Yost | 435.01 |
| Marian Yost | 496.52 |
+-------------+--------+
5 rows in set
Time: 0.004s
```

Since the `books` table will be used in later examples, drop the `title_price_idx` index:

```sql
ALTER TABLE books DROP INDEX title_price_idx;
```
### Solution: Use primary index

If a query uses the primary key to filter data, the query runs fast. For example, the primary key of the `books` table is the `id` column, so you can use the `id` column to query data:

```sql
SELECT * FROM books WHERE id = 896;
```

```sql
+-----+----------------+----------------------+---------------------+-------+--------+
| id  | title          | type                 | published_at        | stock | price  |
+-----+----------------+----------------------+---------------------+-------+--------+
| 896 | Kathryne Doyle | Science & Technology | 1969-03-18 01:34:15 | 468   | 281.32 |
+-----+----------------+----------------------+---------------------+-------+--------+
1 row in set
Time: 0.004s
```

Use `EXPLAIN` to see the execution plan:

```sql
EXPLAIN SELECT * FROM books WHERE id = 896;
```

```sql
+-------------+---------+------+---------------+---------------+
| id          | estRows | task | access object | operator info |
+-------------+---------+------+---------------+---------------+
| Point_Get_1 | 1.00    | root | table:books   | handle:896    |
+-------------+---------+------+---------------+---------------+
```

`Point_Get` is a very fast execute plan.
