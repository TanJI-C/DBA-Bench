# HTAP query basics and window function examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-hybrid-oltp-and-olap-queries.md`
- Source Title: `HTAP Queries`
- Source Heading Path: `HTAP Queries | HTAP Queries > Data preparation | HTAP Queries > Window functions | HTAP Queries > Window functions > `ORDER BY` clause | HTAP Queries > Window functions > `PARTITION BY` clause | HTAP Queries > Window functions > Non-aggregate window functions`
- Source Line Ranges: `5-142`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`, `tikv`, `tiup`, `cloud`
- Topic Tags: `htap`, `oltp`, `olap`, `window-functions`, `order-by`, `partition-by`, `row-number`, `sample-data`, `analytics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0104_1853d87a8e`
- Source ID: `tidb-docs-8.1:develop/dev-guide-hybrid-oltp-and-olap-queries.md#htap-queries`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d240b768c959be64b586d577961d4940c60a3072d0e96e5fcc20d248a06cc69b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-hybrid-oltp-and-olap-queries#htap-queries
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-hybrid-oltp-and-olap-queries.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB HTAP query basics, sample data preparation, or SQL examples of window functions with OVER, ORDER BY, PARTITION BY, SUM(), and row_number().
- Retrieval Keywords: HTAP Queries, Hybrid Transactional and Analytical Processing, TiKV row-based storage engine, TiFlash columnar storage engine, tiup demo bookshop prepare, TiDB Cloud Import, window functions, OVER ([partition_clause] [order_clause] [frame_clause]), ORDER BY clause, PARTITION BY clause, SUM() OVER, DATE_FORMAT(ordered_at, '%Y-%c'), orders_group_by_month, row_number(), Pagination Query
- Follow-up Guidance: The chunk points to enabling HTAP capability in Create a table and to the window-functions and Pagination Query documents for more syntax and row_number() usage.
- Classification Note: This is classified as reference because the content explains HTAP concepts and provides example SQL syntax and results for analytical window function queries.

## Official Source Content

# HTAP Queries

HTAP stands for Hybrid Transactional and Analytical Processing. Traditionally, databases are often designed for transactional or analytical scenarios, so the data platform often needs to be split into Transactional Processing and Analytical Processing, and the data needs to be replicated from the transactional database to the analytical database for quick response to analytical queries. TiDB databases can perform both transactional and analytical tasks, which greatly simplifies the construction of data platforms and allows users to use fresher data for analysis.

TiDB uses TiKV, a row-based storage engine, for Online Transactional Processing (OLTP), and TiFlash, a columnar storage engine, for Online Analytical Processing (OLAP). The row-based storage engine and the columnar storage engine co-exist for HTAP. Both storage engines can replicate data automatically and keep strong consistency. The row-based storage engine optimizes OLTP performance, and the columnar storage engine optimizes OLAP performance.

The [Create a table](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#use-htap-capabilities) section introduces how to enable the HTAP capability of TiDB. The following describes how to use HTAP to analyze data faster.
## Data preparation

Before starting, you can import more sample data [via the `tiup demo` command](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#method-1-via-tiup-demo). For example:

```shell
tiup demo bookshop prepare --users=200000 --books=500000 --authors=100000 --ratings=1000000 --orders=1000000 --host 127.0.0.1 --port 4000 --drop-tables
```

Or you can [use the Import function of TiDB Cloud](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#method-2-via-tidb-cloud-import) to import the pre-prepared sample data.
## Window functions

When using a database, in addition to storing your data and providing application features (such as ordering and rating books), you might also need to analyze the data in the database to make further operations and decisions.

The [Query data from a single table](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table) document introduces how to use aggregate queries to analyze data as a whole. In more complex scenarios, you might want to aggregate the results of multiple aggregation queries into a single query. If you want to know the historical trend of the order amount of a particular book, you can aggregate `sum` for all order data of each month, and then aggregate the `sum` results together to get the historical trend.

To facilitate such analysis, since TiDB v3.0, TiDB supports window functions. For each row of data, this function provides the ability to access data across multiple rows. Different from a regular aggregation query, the window function aggregates rows without merging results set into a single row.

Similar to aggregate functions, you also need to follow a fixed set of syntax when using the window function:

```sql
SELECT
    window_function() OVER ([partition_clause] [order_clause] [frame_clause]) AS alias
FROM
    table_name
```
### `ORDER BY` clause

With the aggregate window function `sum()`, you can analyze the historical trend of the order amount of a particular book. For example:

```sql
WITH orders_group_by_month AS (
  SELECT DATE_FORMAT(ordered_at, '%Y-%c') AS month, COUNT(*) AS orders
  FROM orders
  WHERE book_id = 3461722937
  GROUP BY 1
)
SELECT
month,
SUM(orders) OVER(ORDER BY month ASC) as acc
FROM orders_group_by_month
ORDER BY month ASC;
```

The `sum()` function accumulates the data in the order specified by the `ORDER BY` statement in the `OVER` clause. The result is as follows:

```
+---------+-------+
| month   | acc   |
+---------+-------+
| 2011-5  |     1 |
| 2011-8  |     2 |
| 2012-1  |     3 |
| 2012-2  |     4 |
| 2013-1  |     5 |
| 2013-3  |     6 |
| 2015-11 |     7 |
| 2015-4  |     8 |
| 2015-8  |     9 |
| 2017-11 |    10 |
| 2017-5  |    11 |
| 2019-5  |    13 |
| 2020-2  |    14 |
+---------+-------+
13 rows in set (0.01 sec)
```

Visualize the above data through a line chart with time as the horizontal axis and cumulative order amount as the vertical axis. You can easily know the historical ordering trend of the book through the change of the slope.
### `PARTITION BY` clause

Suppose that you want to analyze the historical ordering trend of different types of books, and visualize it in the same line chart with multiple series.

You can use the `PARTITION BY` clause to group books by types and count history orders for each type separately.

```sql
WITH orders_group_by_month AS (
    SELECT
        b.type AS book_type,
        DATE_FORMAT(ordered_at, '%Y-%c') AS month,
        COUNT(*) AS orders
    FROM orders o
    LEFT JOIN books b ON o.book_id = b.id
    WHERE b.type IS NOT NULL
    GROUP BY book_type, month
), acc AS (
    SELECT
        book_type,
        month,
        SUM(orders) OVER(PARTITION BY book_type ORDER BY book_type, month ASC) as acc
    FROM orders_group_by_month
    ORDER BY book_type, month ASC
)
SELECT * FROM acc;
```

The result is as follows:

```
+------------------------------+---------+------+
| book_type                    | month   | acc  |
+------------------------------+---------+------+
| Magazine                     | 2011-10 |    1 |
| Magazine                     | 2011-8  |    2 |
| Magazine                     | 2012-5  |    3 |
| Magazine                     | 2013-1  |    4 |
| Magazine                     | 2013-6  |    5 |
...
| Novel                        | 2011-3  |   13 |
| Novel                        | 2011-4  |   14 |
| Novel                        | 2011-6  |   15 |
| Novel                        | 2011-8  |   17 |
| Novel                        | 2012-1  |   18 |
| Novel                        | 2012-2  |   20 |
...
| Sports                       | 2021-4  |   49 |
| Sports                       | 2021-7  |   50 |
| Sports                       | 2022-4  |   51 |
+------------------------------+---------+------+
1500 rows in set (1.70 sec)
```
### Non-aggregate window functions

TiDB also provides some non-aggregated [window functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions) for more analysis statements.

For example, the [Pagination Query](https://docs.pingcap.com/tidb/stable/develop/dev-guide-paginate-results) document introduces how to use the `row_number()` function to achieve efficient pagination batch processing.
