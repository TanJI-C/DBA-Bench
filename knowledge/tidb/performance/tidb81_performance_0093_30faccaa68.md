# Specify query engine with read_from_storage hint

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-hybrid-oltp-and-olap-queries.md`
- Source Title: `HTAP Queries`
- Source Heading Path: `HTAP Queries > Hybrid workload > Specify a query engine`
- Source Line Ranges: `210-246`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`, `tikv`
- Topic Tags: `htap`, `optimizer-hints`, `cost-based-optimizer`, `read-from-storage`, `execution-plan`, `explain`, `tiflash-replicas`, `query-engine`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0093_30faccaa68`
- Source ID: `tidb-docs-8.1:develop/dev-guide-hybrid-oltp-and-olap-queries.md#specify-a-query-engine`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `30db0c252f2ea934cef07fa31e63354aa60d3ef934cdc1f025b6f559a9337da0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-hybrid-oltp-and-olap-queries#specify-a-query-engine
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-hybrid-oltp-and-olap-queries.md

## Retrieval Guidance

- Use When: Use this chunk when you need to specify TiKV or TiFlash for a query with the `read_from_storage` optimizer hint and verify the plan with `EXPLAIN`.
- Retrieval Keywords: read_from_storage(engine_name[table_name]), Optimizer Hints, TiDB uses the Cost Based Optimizer (CBO), TiFlash replicas, EXPLAIN, cop[tiflash], cop[tikv], table alias, common table expression, CTE
- Follow-up Guidance: Check the `EXPLAIN` output to see whether `cop[tiflash]` and `cop[tikv]` both appear in the task column.
- Classification Note: This chunk explains how TiDB chooses between TiFlash replicas and TiKV and shows the `read_from_storage` hint syntax with an example SQL statement.

## Official Source Content

### Specify a query engine

TiDB uses the Cost Based Optimizer (CBO) to automatically choose whether to use TiFlash replicas based on cost estimates. However, if you are sure whether your query is transactional or analytical, you can specify the query engine to be used with [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints).

To specify which engine to be used in a query, you can use the `/*+ read_from_storage(engine_name[table_name]) */` hint as in the following statement.

> **Note:**
>
> - If a table has an alias, use the alias instead of the table name in the hint, otherwise, the hint does not work.
> - The `read_from_storage` hint does not work for [common table expression](https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-common-table-expression).

```sql
WITH orders_group_by_month AS (
    SELECT
        /*+ read_from_storage(tikv[o]) */
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
    FROM orders_group_by_month mo
    ORDER BY book_type, month ASC
)
SELECT * FROM acc;
```

You can use the `EXPLAIN` statement to check the execution plan of the above SQL statement. If `cop[tiflash]` and `cop[tikv]` appear in the task column at the same time, it means that TiFlash and TiKV are both scheduled to complete this query. Note that TiFlash and TiKV storage engines usually use different TiDB nodes, so the two query types are not affected by each other.

For more information about how TiDB chooses to use TiFlash, see [Use TiDB to read TiFlash replicas](https://docs.pingcap.com/tidb/stable/tiflash/use-tidb-to-read-tiflash)
