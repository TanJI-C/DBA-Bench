# TiFlash performance comparison and query routing for multi-tenant filtering workloads

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > When to use TiFlash > SaaS arbitrary filtering workloads > Performance comparison | A Practical Guide for SQL Tuning > SQL tuning guide > When to use TiFlash > SaaS arbitrary filtering workloads > Query routing between TiKV and TiFlash`
- Source Line Ranges: `915-993`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `sql`
- Topic Tags: `performance-comparison`, `query-routing`, `mpp`, `range-scan`, `multi-tenant`, `filtering`, `execution-plan`, `topology-aware-optimization`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0183_6b8722f995`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#performance-comparison`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6f08d15511ab0b9c98500047846b5ce64484748202435349459dd0d89b30ab51`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#performance-comparison
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiKV and TiFlash execution plans for multi-tenant filtering queries and understanding how TiDB routes queries between TiKV and TiFlash based on row count.
- Retrieval Keywords: TiFlash performance comparison, query routing between TiKV and TiFlash, multi-tenant filtering workloads, TiFlash MPP engine, TableRangeScan, 5,121 cop tasks, 2 MPP tasks, COUNT SORT LIMIT push down, columnar storage, small tenants, large tenants, tenantId objectTypeId, usertable, WITH results limited_results, dynamic filtering conditions
- Follow-up Guidance: The source also states that after enabling TiFlash replicas for tables with large amounts of multi-tenant data, the optimizer routes small-tenant queries to TiKV and large-tenant queries to TiFlash based on row count.
- Classification Note: This is classified under performance for the TiFlash component because the content compares TiKV and TiFlash query execution time, task counts, and optimizer routing behavior for filtering workloads.

## Official Source Content

##### Performance comparison

When running the same query on different storage engines, you can observe significant performance differences:

- TiKV plan: The query takes 2 minutes 38.6 seconds on TiKV. `TableRangeScan` sends 5,121 cop tasks because the data is distributed across 5,121 Regions.
- TiFlash plan: The same query takes only 3.44 seconds on TiFlash MPP engine—nearly 46 times faster. TiFlash stores data sorted by primary key, so queries filtered by the primary key's prefix use `TableRangeScan` instead of a full table scan. TiFlash requires only 2 MPP tasks compared to TiKV's 5,121 tasks.

The following is the query statement:

```sql
WITH `results` AS (
  SELECT field1, field2, field3, field4
  FROM usertable
  where tenantId = 1234 and objectTypeId = 6789
),
`limited_results` AS (
  SELECT field1, field2, field3, field4
  FROM `results` LIMIT 100
)
SELECT field1, field2, field3, field4
FROM
  (
    SELECT 100 `__total__`, field1, field2, field3, field4
    FROM `limited_results`
    UNION ALL
    SELECT count(*) `__total__`, field1, field2, field3, field4
    FROM `results`
  ) `result_and_count`;
```

The execution plan on TiKV is as follows:

```
+--------------------------------+-----------+---------+-----------+-----------------------+-----------------------------------------------------+
| id                             | estRows   | actRows | task      | access object         | execution info                                      |
+--------------------------------+-----------+---------+-----------+-----------------------+-----------------------------------------------------+
| Union_18                       | 101.00    | 101     | root      |                       | time:2m38.6s, loops:3, RU:8662189.451027            |
| ├─Limit_20                     | 100.00    | 100     | root      |                       | time:23ms, loops:2                                  |
| │ └─TableReader_25             | 100.00    | 100     | root      |                       | time:23ms, loops:1, cop_task: {num: 1, max: 22.8...}|
| │   └─Limit_24                 | 100.00    | 100     | cop[tikv] |                       | tikv_task:{time:21ms, loops:3}, scan_detail: {...}  |
| │     └─TableRangeScan_22      | 100.00    | 100     | cop[tikv] | table:usertable       | tikv_task:{time:21ms, loops:3}                      |
| └─Projection_26                | 1.00      | 1       | root      |                       | time:2m38.6s, loops:2, Concurrency:OFF              |
|   └─HashAgg_34                 | 1.00      | 1       | root      |                       | time:2m38.6s, loops:2, partial_worker:{...}, fin.. .|
|     └─TableReader_35           | 1.00      | 5121    | root      |                       | time:2m38.6s, loops:7, cop_task: {num: 5121, max:...|
|       └─HashAgg_27             | 1.00      | 5121    | cop[tikv] |                       | tikv_task:{proc max:0s, min:0s, avg: 462.8ms, p...} |
|         └─TableRangeScan_32    | 10000000  | 10000000| cop[tikv] | table:usertable       | tikv_task:{proc max:0s, min:0s, avg: 460.5ms, p...} |
+--------------------------------+-----------+---------+-----------+-----------------------+-----------------------------------------------------+
```

The execution plan on TiFlash is as follows:

```
+--------------------------------+-----------+---------+--------------+--------------------+-----------------------------------------------------+
| id                             | estRows   | actRows | task         | access object      | execution info                                      |
+--------------------------------+-----------+---------+--------------+--------------------+-----------------------------------------------------+
| Union_18                       | 101.00    | 101     | root         |                    | time:3.44s, loops:3, RU:0.000000                    |
| ├─Limit_22                     | 100.00    | 100     | root         |                    | time:146.7ms, loops:2                               |
| │ └─TableReader_30             | 100.00    | 100     | root         |                    | time:146.7ms, loops:1, cop_task: {num: 1, max: 0...}|
| │   └─ExchangeSender_29        | 100.00    | 0       | mpp[tiflash] |                    |                                                     |
| │     └─Limit_28               | 100.00    | 0       | mpp[tiflash] |                    |                                                     |
| │       └─TableRangeScan_27    | 100.00    | 0       | mpp[tiflash] | table:usertable    |                                                     |
| └─Projection_31                | 1.00      | 1       | root         |                    | time:3.42s, loops:2, Concurrency:OFF                |
|   └─HashAgg_49                 | 1.00      | 1       | root         |                    | time:3.42s, loops:2, partial_worker:{...}, fin...   |
|     └─TableReader_51           | 1.00      | 2       | root         |                    | time:3.42s, loops:2, cop_task: {num: 4, max: 0...}  |
|       └─ExchangeSender_50      | 1.00      | 2       | mpp[tiflash] |                    | tiflash_task:{proc max:3.4s, min:3.15s, avg: 3...}  |
|         └─HashAgg_36           | 1.00      | 2       | mpp[tiflash] |                    | tiflash_task:{proc max:3.4s, min:3.15s, avg: 3...}  |
|           └─TableRangeScan_48 | 10000000   | 10000000| mpp[tiflash] | table:usertable    | tiflash_task:{proc max:3.4s, min:3.15s, avg: 3...}  |
+--------------------------------+-----------+---------+--------------+--------------------+-----------------------------------------------------+
```
##### Query routing between TiKV and TiFlash

After enabling TiFlash replicas for tables with large amounts of multi-tenant data, the optimizer routes queries to either TiKV or TiFlash based on the row count:

- Small tenants: TiKV is more suitable for tenants with small data size, as it provides high concurrency for small queries with table range scans.
- Large tenants: For tenants with large datasets (such as 10 million rows in this case), TiFlash is more efficient for the following advantages:
    - TiFlash handles dynamic filtering conditions without requiring specific indexes.
    - TiDB can push down `COUNT`, `SORT`, and `LIMIT` operations to TiFlash.
    - TiFlash scans only the required columns using columnar storage.
