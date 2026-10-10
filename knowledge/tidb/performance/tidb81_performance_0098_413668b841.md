# SQL performance tuning overview and full table scan diagnosis

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-optimize-sql.md`
- Source Title: `SQL Performance Tuning`
- Source Heading Path: `SQL Performance Tuning | SQL Performance Tuning > Before you begin | SQL Performance Tuning > Issue: Full table scan`
- Source Line Ranges: `5-63`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `tiup`, `cloud`
- Topic Tags: `sql-performance`, `full-table-scan`, `explain`, `execution-plan`, `index-selection`, `sample-data`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0098_413668b841`
- Source ID: `tidb-docs-8.1:develop/dev-guide-optimize-sql.md#sql-performance-tuning`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `75ce5a95f0f710c8d74638eb023c6b99195215cd37470abcf90e5cd8ce1b8f3d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql#sql-performance-tuning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-optimize-sql.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing a slow SELECT on a large table where EXPLAIN shows a full table scan instead of indexed access.
- Retrieval Keywords: SQL Performance Tuning, Issue: Full table scan, SELECT * FROM books WHERE title = 'Marian Yost', EXPLAIN SELECT * FROM books WHERE title = 'Marian Yost', TableFullScan_5, table:books, eq(bookshop.books.title, "Marian Yost"), estRows 1000000.00, full table scan, incorrect indexes, EXPLAIN Walkthrough
- Follow-up Guidance: The source points to the solution of adding a secondary index and also references `EXPLAIN` Walkthrough for more information about using `EXPLAIN`.
- Classification Note: This is classified as performance for SQL because the official content explains slow query diagnosis through an execution plan showing `TableFullScan_5` on the `books` table.

## Official Source Content

# SQL Performance Tuning

This document introduces some common reasons for slow SQL statements and techniques for tuning SQL performance.
## Before you begin

You can use [`tiup demo` import](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#method-1-via-tiup-demo) to prepare data:

```shell
tiup demo bookshop prepare --host 127.0.0.1 --port 4000 --books 1000000
```

Or [using the Import feature of TiDB Cloud](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#method-2-via-tidb-cloud-import) to import the pre-prepared sample data.
## Issue: Full table scan

The most common reason for slow SQL queries is that the `SELECT` statements perform full table scan or use incorrect indexes.

When TiDB retrieves a small number of rows from a large table based on a column that is not the primary key or in the secondary index, the performance is usually poor:

```sql
SELECT * FROM books WHERE title = 'Marian Yost';
```

```sql
+------------+-------------+-----------------------+---------------------+-------+--------+
| id         | title       | type                  | published_at        | stock | price  |
+------------+-------------+-----------------------+---------------------+-------+--------+
| 65670536   | Marian Yost | Arts                  | 1950-04-09 06:28:58 | 542   | 435.01 |
| 1164070689 | Marian Yost | Education & Reference | 1916-05-27 12:15:35 | 216   | 328.18 |
| 1414277591 | Marian Yost | Arts                  | 1932-06-15 09:18:14 | 303   | 496.52 |
| 2305318593 | Marian Yost | Arts                  | 2000-08-15 19:40:58 | 398   | 402.90 |
| 2638226326 | Marian Yost | Sports                | 1952-04-02 12:40:37 | 191   | 174.64 |
+------------+-------------+-----------------------+---------------------+-------+--------+
5 rows in set
Time: 0.582s
```

To understand why this query is slow, you can use `EXPLAIN` to see the execution plan:

```sql
EXPLAIN SELECT * FROM books WHERE title = 'Marian Yost';
```

```sql
+---------------------+------------+-----------+---------------+-----------------------------------------+
| id                  | estRows    | task      | access object | operator info                           |
+---------------------+------------+-----------+---------------+-----------------------------------------+
| TableReader_7       | 1.27       | root      |               | data:Selection_6                        |
| └─Selection_6       | 1.27       | cop[tikv] |               | eq(bookshop.books.title, "Marian Yost") |
|   └─TableFullScan_5 | 1000000.00 | cop[tikv] | table:books   | keep order:false                        |
+---------------------+------------+-----------+---------------+-----------------------------------------+
```

As can be seen from `TableFullScan_5` in the execution plan, TiDB performs a full table scan on the `books` table and checks whether `title` satisfies the condition for each row. The `estRows` value of `TableFullScan_5` is `1000000.00`, which means the optimizer estimates that this full table scan takes `1000000.00` rows of data.

For more information about the usage of `EXPLAIN`, see [`EXPLAIN` Walkthrough](https://docs.pingcap.com/tidb/stable/explain-walkthrough).
