# Composite index tuning for filtering and sorting

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > Index strategy in TiDB > SQL tuning with composite indexes for efficient filtering and sorting`
- Source Line Ranges: `754-832`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `composite-indexes`, `execution-plans`, `filtering`, `sorting`, `limit-pushdown`, `index-range-scan`, `analyze-table`, `query-performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0181_befc2a24e6`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#sql-tuning-with-composite-indexes-for-efficient-filtering-and-sorting`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f50855a2e0d459088ebd501b3c7d516f725e46d24db47de7eb21fba1d4b4a0eb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#sql-tuning-with-composite-indexes-for-efficient-filtering-and-sorting
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing a slow TiDB query that filters on multiple predicates and sorts with ORDER BY ... LIMIT, and you need an example of how a composite index changes the execution plan and runtime.
- Retrieval Keywords: CREATE INDEX idx_composite ON orders(user_id, mode, id, created_at, label_id), ANALYZE TABLE orders index idx_composite, IndexRangeScan_28, index_orders_on_created_at, keep order:true, limit embedded(offset:0, count:101), ORDER BY orders.id DESC LIMIT 101, IndexLookUp_39, TableRowIDScan_36, composite index filtering and sorting, limit push-down, index-only sort
- Follow-up Guidance: The content also provides the before-and-after execution plans showing the shift from scanning index_orders_on_created_at and millions of rows to using idx_composite with keep order:true and limit embedded.
- Classification Note: This chunk is classified as performance for the SQL component because it explains SQL tuning through composite index design, execution plan changes, reduced row scans, and faster query execution in TiDB and TiKV.

## Official Source Content

#### SQL tuning with composite indexes for efficient filtering and sorting

The following query takes 11 minutes and 9 seconds to execute, which is excessively long for a query that returns only 101 rows. The slow performance is caused by several factors:

- Inefficient index usage: The optimizer selects the index on `created_at`, resulting in a scan of 25,147,450 rows.
- Large intermediate result set: After applying the date range filter, 12,082,311 rows still require processing.
- Late filtering: The most selective predicates `(mode, user_id, and label_id)` are applied after accessing the table, resulting in 16,604 rows.
- Sorting overhead: The final sort operation on 16,604 rows adds additional processing time.

The following is the query statement:

```sql
SELECT `orders`.*
FROM `orders`
WHERE 
    `orders`.`mode` = 'production'
    AND `orders`.`user_id` = 11111
    AND orders.label_id IS NOT NULL
    AND orders.created_at >= '2024-04-07 18:07:52'
    AND orders.created_at <= '2024-05-11 18:07:52'
    AND orders.id >= 1000000000
    AND orders.id < 1500000000
ORDER BY orders.id DESC 
LIMIT 101;
```

The following are the existing indexes on `orders`:

```sql
PRIMARY KEY (`id`),
UNIQUE KEY `index_orders_on_adjustment_id` (`adjustment_id`),
KEY `index_orders_on_user_id` (`user_id`),
KEY `index_orders_on_label_id` (`label_id`),
KEY `index_orders_on_created_at` (`created_at`)
```

The original execution plan is as follows:

```
+--------------------------------+-----------+---------+-----------+--------------------------------------------------------------------------------+-----------------------------------------------------+----------------------------------------------------------------------------------------+----------+------+
| id                             | estRows   | actRows | task      | access object                                                                  | execution info                                      | operator info                                                                          | memory   | disk |
+--------------------------------+-----------+---------+-----------+--------------------------------------------------------------------------------+-----------------------------------------------------+----------------------------------------------------------------------------------------+----------+------+
| TopN_10                        | 101.00    | 101     | root      |                                                                                | time:11m9.8s, loops:2                               | orders.id:desc, offset:0, count:101                                                    | 271 KB   | N/A  |
| └─IndexLookUp_39               | 173.83    | 16604   | root      |                                                                                | time:11m9.8s, loops:19, index_task: {total_time:...}|                                                                                        | 20.4 MB  | N/A  |
|   ├─Selection_37(Build)        | 8296.70   | 12082311| cop[tikv] |                                                                                | time:26.4ms, loops:11834, cop_task: {num: 294, m...}| ge(orders.id, 1000000000), lt(orders.id, 1500000000)                                   | N/A      | N/A  |
|   │ └─IndexRangeScan_35        | 6934161.90| 25147450| cop[tikv] | table:orders, index:index_orders_on_created_at(created_at)                     | tikv_task:{proc max:2.15s, min:0s, avg: 58.9ms, ...}| range:[2024-04-07 18:07:52,2024-05-11 18:07:52), keep order:false                      | N/A      | N/A  |
|   └─Selection_38(Probe)        | 173.83    | 16604   | cop[tikv] |                                                                                | time:54m46.2s, loops:651, cop_task: {num: 1076, ...}| eq(orders.mode, "production"), eq(orders.user_id, 11111), not(isnull(orders.label_id)) | N/A      | N/A  |
|     └─TableRowIDScan_36        | 8296.70   | 12082311| cop[tikv] | table:orders                                                                   | tikv_task:{proc max:44.8s, min:0s, avg: 3.33s, p...}| keep order:false                                                                       | N/A      | N/A  |
+--------------------------------+-----------+---------+-----------+--------------------------------------------------------------------------------+-----------------------------------------------------+----------------------------------------------------------------------------------------+----------+------+
```

After creating a composite index `idx_composite` on `orders(user_id, mode, id, created_at, label_id)`, the query performance improves significantly. The execution time drops from 11 minutes and 9 seconds to just 5.3 milliseconds, making the query over 126,000 times faster. This massive improvement results from:

- Efficient index usage: the new index enables an index range scan on `user_id`, `mode`, and `id`, which are the most selective predicates. This reduces the number of scanned rows from millions to just 224.
- Index-only sort: the `keep order:true` in the execution plan indicates that sorting is performed using the index structure, eliminating the need for a separate sort operation.
- Early filtering: the most selective predicates are applied first, reducing the result set to 224 rows before further filtering.
- Limit push-down: the `LIMIT` clause is pushed down to the index scan, allowing early termination of the scan once 101 rows are found.

This case demonstrates the significant impact of a well-designed index on query performance. By aligning the index structure with the query's predicates, sort order, and required columns, the query achieves a performance improvement of over five orders of magnitude.

```sql
CREATE INDEX idx_composite ON orders(user_id, mode, id, created_at, label_id);
ANALYZE TABLE orders index idx_composite;
```

The new execution plan is as follows:
```
+--------------------------------+-----------+---------+-----------+--------------------------------------------------------------------------------+-----------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+----------+------+
| id                             | estRows   | actRows | task      | access object                                                                  | execution info                                      | operator info                                                                                                        | memory   | disk |
+--------------------------------+-----------+---------+-----------+--------------------------------------------------------------------------------+-----------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+----------+------+
| IndexLookUp_32                 | 101.00    | 101     | root      |                                                                                | time:5.3ms, loops:2, RU:3.435006, index_task: {t...}| limit embedded(offset:0, count:101)                                                                                  | 128.5 KB | N/A  |
| ├─Limit_31(Build)              | 101.00    | 101     | cop[tikv] |                                                                                | time:1.35ms, loops:1, cop_task: {num: 1, max: 1....}| offset:0, count:101                                                                                                  | N/A      | N/A  |
| │ └─Selection_30               | 535.77    | 224     | cop[tikv] |                                                                                | tikv_task:{time:0s, loops:3}                        | ge(orders.created_at, 2024-04-07 18:07:52), le(orders.created_at, 2024-05-11 18:07:52), not(isnull(orders.label_id)) | N/A      | N/A  |
| │   └─IndexRangeScan_28        | 503893.42 | 224     | cop[tikv] | table:orders, index:idx_composite(user_id, mode, id, created_at, label_id)     | tikv_task:{time:0s, loops:3}                        | range:[11111 "production" 1000000000,11111 "production" 1500000000), keep order:true, desc                           | N/A      | N/A  |
| └─TableRowIDScan_29(Probe)     | 101.00    | 101     | cop[tikv] | table:orders                                                                   | time:2.9ms, loops:2, cop_task: {num: 3, max: 2.7...}| keep order:false                                                                                                     | N/A      | N/A  |
+--------------------------------+-----------+---------+-----------+--------------------------------------------------------------------------------+-----------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+----------+------+
```
