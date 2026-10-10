# Use a secondary index to avoid full table scans

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-optimize-sql.md`
- Source Title: `SQL Performance Tuning`
- Source Heading Path: `SQL Performance Tuning > Issue: Full table scan > Solution: Use secondary index`
- Source Line Ranges: `64-113`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `secondary-index`, `full-table-scan`, `explain`, `execution-plan`, `index-lookup`, `query-tuning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0099_5d992083ec`
- Source ID: `tidb-docs-8.1:develop/dev-guide-optimize-sql.md#solution-use-secondary-index`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f284b5f5374ba3b258a242c3394c8868734076e84750ec3ac5fc7069372e766`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql#solution-use-secondary-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-optimize-sql.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an example of improving a slow query by adding a secondary index and verifying the new EXPLAIN plan.
- Retrieval Keywords: Solution: Use secondary index, CREATE INDEX title_idx ON books (title), title_idx, EXPLAIN SELECT * FROM books WHERE title = 'Marian Yost', IndexLookUp_10, IndexRangeScan_8, TableRowIDScan_9, table:books, index:title_idx(title), range:["Marian Yost","Marian Yost"], estRows 1.27, TiDB Query Execution Plan Overview
- Follow-up Guidance: The source also refers to TiDB Query Execution Plan Overview for more information on the execution plan.
- Classification Note: This is classified as performance for SQL because the official content shows that adding the `title_idx` secondary index changes the plan from a full scan to `IndexLookUp_10` with fewer estimated scanned rows.

## Official Source Content

### Solution: Use secondary index

To speed up this query above, add a secondary index on the `books.title` column:

```sql
CREATE INDEX title_idx ON books (title);
```

The query execution is much faster:

```sql
SELECT * FROM books WHERE title = 'Marian Yost';
```

```sql
+------------+-------------+-----------------------+---------------------+-------+--------+
| id         | title       | type                  | published_at        | stock | price  |
+------------+-------------+-----------------------+---------------------+-------+--------+
| 1164070689 | Marian Yost | Education & Reference | 1916-05-27 12:15:35 | 216   | 328.18 |
| 1414277591 | Marian Yost | Arts                  | 1932-06-15 09:18:14 | 303   | 496.52 |
| 2305318593 | Marian Yost | Arts                  | 2000-08-15 19:40:58 | 398   | 402.90 |
| 2638226326 | Marian Yost | Sports                | 1952-04-02 12:40:37 | 191   | 174.64 |
| 65670536   | Marian Yost | Arts                  | 1950-04-09 06:28:58 | 542   | 435.01 |
+------------+-------------+-----------------------+---------------------+-------+--------+
5 rows in set
Time: 0.007s
```

To understand why the performance is improved, use `EXPLAIN` to see the new execution plan:

```sql
EXPLAIN SELECT * FROM books WHERE title = 'Marian Yost';
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

As can be seen from `IndexLookup_10` in the execution plan, TiDB queries the data by the `title_idx` index. Its `estRows` value is `1.27`, which means that the optimizer estimates that only `1.27` rows are scanned. The estimated rows scanned are much fewer than the `1000000.00` rows of data in the full table scan.

The `IndexLookup_10` execution plan is to first use the `IndexRangeScan_8` operator to read the index data that meets the condition through the `title_idx` index, and then use the `TableLookup_9` operator to query the corresponding rows according to the Row ID stored in the index data.

For more information on the TiDB execution plan, see [TiDB Query Execution Plan Overview](https://docs.pingcap.com/tidb/stable/explain-overview).
