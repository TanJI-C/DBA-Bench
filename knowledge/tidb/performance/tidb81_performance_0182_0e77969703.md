# When to use TiFlash for analytical and SaaS filtering workloads

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > When to use TiFlash | A Practical Guide for SQL Tuning > SQL tuning guide > When to use TiFlash > Analytical query | A Practical Guide for SQL Tuning > SQL tuning guide > When to use TiFlash > SaaS arbitrary filtering workloads | A Practical Guide for SQL Tuning > SQL tuning guide > When to use TiFlash > SaaS arbitrary filtering workloads > Case study: multi-tenant data access`
- Source Line Ranges: `833-914`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `sql`
- Topic Tags: `analytical-queries`, `mpp`, `columnar-storage`, `query-performance`, `execution-plans`, `olap`, `mixed-workloads`, `saas`, `multi-tenant`, `filtering`, `composite-primary-key`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0182_0e77969703`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#when-to-use-tiflash`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `36ce654ad0aec1c42ab59b290c06ced8fff48758a8879f49b15df5e15c0aa256`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#when-to-use-tiflash
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when identifying whether TiFlash fits analytical queries, mixed OLTP and OLAP workloads, or SaaS multi-tenant filtering queries with many filter columns and composite primary keys.
- Retrieval Keywords: When to use TiFlash, TiFlash, MPP mode, columnar storage, analytical query, large-scale data analysis, complex scans, aggregations, and joins, mixed workloads, OLTP, OLAP, SaaS arbitrary filtering workloads, late materialization, composite primary key, tenantId, objectTypeId, objectId, multi-tenant data access, TPC-H Query 14, order_line, item, HashJoin_21, HashAgg_9, Projection_38, TableFullScan_22, TableFullScan_25, HashJoin_50, HashAgg_52, ExchangeSender_53, mpp[tiflash], cop[tikv], table range scans
- Follow-up Guidance: The source follows with an analytical example comparing TPC-H Query 14 on TiKV and TiFlash, including execution plans and timings, and a SaaS case study with the composite primary key `(tenantId, objectTypeId, objectId)`.
- Classification Note: This chunk is classified under performance for the TiFlash component because the content explains workload patterns and execution plans where TiFlash improves query performance through columnar storage and MPP execution.

## Official Source Content

### When to use TiFlash

This section explains when to use TiFlash in TiDB. TiFlash is optimized for analytical queries that involve complex calculations, aggregations, and large dataset scans. Its columnar storage format and MPP mode significantly improve performance in these scenarios.

Use TiFlash in the following scenarios:

- Large-scale data analysis: TiFlash delivers faster performance for OLAP workloads that require extensive data scans. Its columnar storage and MPP execution mode optimize query efficiency compared to TiKV.
- Complex scans, aggregations, and joins: TiFlash processes queries with heavy aggregations and joins more efficiently by reading only the necessary columns.
- Mixed workloads: in hybrid environments where both transactional (OLTP) and analytical (OLAP) workloads run simultaneously, TiFlash handles analytical queries without affecting TiKV's performance for transactional queries.
- SaaS applications with arbitrary filtering requirements: queries often involve filtering across many columns. Indexing all columns is impractical, especially when queries include a tenant ID as part of the primary key. TiFlash sorts and clusters data by primary key, making it well suited for these workloads. With the [late materialization](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-late-materialization) feature, TiFlash enables efficient table range scans, improving query performance without the overhead of maintaining multiple indexes.

Using TiFlash strategically enhances query performance and optimizes resource usage in TiDB for data-intensive analytical queries. The following sections provide examples of TiFlash use cases.
#### Analytical query

This section compares the execution performance of TPC-H Query 14 on TiKV and TiFlash storage engines.

TPC-H Query 14 involves joining the `order_line` and `item` tables. The query takes **21.1 seconds** on TiKV but only **1.41 seconds** using TiFlash MPP mode, making it 15 times faster.

- TiKV plan: TiDB fetches 3,864,397 rows from the `lineitem` table and 10 million rows from the `part` table. The hash join operation (`HashJoin_21`), along with the subsequent projection (`Projection_38`) and aggregation (`HashAgg_9`) operations, are performed in TiDB.
- TiFlash plan: The optimizer detects TiFlash replicas for both `order_line` and `item` tables. Based on cost estimation, TiDB automatically selects the MPP mode, executing the entire query within the TiFlash columnar storage engine. This includes table scans, hash joins, column projections, and aggregations, significantly improving performance compared to the TiKV plan.

The following is the query:

```sql
select 100.00 * sum(case when i_data like 'PR%' then ol_amount else 0 end) / (1+sum(ol_amount)) as promo_revenue
from order_line, item
where ol_i_id = i_id and ol_delivery_d >= '2007-01-02 00:00:00.000000' and ol_delivery_d < '2030-01-02 00:00:00.000000';
```

The execution plan on TiKV is as follows:

```
+-------------------------------+--------------+-----------+-----------+----------------+----------------------------------------------+
| ID                            | ESTROWS      | ACTROWS   | TASK      | ACCESS OBJECT  | EXECUTION INFO                               |
+-------------------------------+--------------+-----------+-----------+----------------+----------------------------------------------+
| Projection_8                  | 1.00         | 1         | root      |                | time:21.1s, loops:2, RU:1023225.707561, ...  |
| └─HashAgg_9                   | 1.00         | 1         | root      |                | time:21.1s, loops:2, partial_worker:{ ...    |
|   └─Projection_38             | 3839984.46   | 3864397   | root      |                | time:21.1s, loops:3776, Concurrency:5        |
|     └─HashJoin_21             | 3839984.46   | 3864397   | root      |                | time:21.1s, loops:3776, build_hash_table:... |
|       ├─TableReader_24(Build) | 3826762.62   | 3864397   | root      |                | time:18.4s, loops:3764, cop_task: ...        |
|       │ └─Selection_23        | 3826762.62   | 3864397   | cop[tikv] |                | tikv_task:{proc max:717ms, min:265ms, ...    |
|       │   └─TableFullScan_22  | 300005811.00 | 300005811 | cop[tikv] | table:lineitem | tikv_task:{proc max:685ms, min:252ms, ...    |
|       └─TableReader_26(Probe) | 10000000.00  | 10000000  | root      |                | time:1.29s, loops:9780, cop_task: ...        |
|         └─TableFullScan_25    | 10000000.00  | 10000000  | cop[tikv] | table:part     | tikv_task:{proc max:922ms, min:468ms, ...    |
+-------------------------------+--------------+-----------+-----------+----------------+----------------------------------------------+
```

The execution plan on TiFlash is as follows:

```
+--------------------------------------------+-------------+----------+--------------+----------------+--------------------------------------+
| ID                                         | ESTROWS     | ACTROWS  | TASK         | ACCESS OBJECT  | EXECUTION INFO                       |
+--------------------------------------------+-------------+----------+--------------+----------------+--------------------------------------+
| Projection_8                               | 1.00        | 1        | root         |                | time:1.41s, loops:2, RU:45879.127909 |
| └─HashAgg_52                               | 1.00        | 1        | root         |                | time:1.41s, loops:2, ...             |
|   └─TableReader_54                         | 1.00        | 1        | root         |                | time:1.41s, loops:2, ...             |
|     └─ExchangeSender_53                    | 1.00        | 1        | mpp[tiflash] |                | tiflash_task:{time:1.41s, ...        |
|       └─HashAgg_13                         | 1.00        | 1        | mpp[tiflash] |                | tiflash_task:{time:1.41s, ...        |
|         └─Projection_74                    | 3813443.11  | 3864397  | mpp[tiflash] |                | tiflash_task:{time:1.4s, ...         |
|           └─Projection_51                  | 3813443.11  | 3864397  | mpp[tiflash] |                | tiflash_task:{time:1.39s, ...        |
|             └─HashJoin_50                  | 3813443.11  | 3864397  | mpp[tiflash] |                | tiflash_task:{time:1.39s, ...        |
|               ├─ExchangeReceiver_31(Build) | 3800312.67  | 3864397  | mpp[tiflash] |                | tiflash_task:{time:1.05s, ...        |
|               │ └─ExchangeSender_30        | 3800312.67  | 3864397  | mpp[tiflash] |                | tiflash_task:{time:1.2s, ...         |
|               │   └─TableFullScan_28       | 3800312.67  | 3864397  | mpp[tiflash] | table:lineitem | tiflash_task:{time:1.15s, ...        |
|               └─ExchangeReceiver_34(Probe) | 10000000.00 | 10000000 | mpp[tiflash] |                | tiflash_task:{time:1.24s, ...        |
|                 └─ExchangeSender_33        | 10000000.00 | 10000000 | mpp[tiflash] |                | tiflash_task:{time:1.4s, ...         |
|                   └─TableFullScan_32       | 10000000.00 | 10000000 | mpp[tiflash] | table:part     | tiflash_task:{time:59.2ms, ...       |
+--------------------------------------------+-------------+----------+--------------+----------------+--------------------------------------+
```
#### SaaS arbitrary filtering workloads

In SaaS applications, tables often use composite primary keys that include tenant identification. The following example demonstrates how TiFlash can significantly improve query performance in these scenarios.
##### Case study: multi-tenant data access

Consider a table with a composite primary key: `(tenantId, objectTypeId, objectId)`. A typical query pattern for this table involves:

- Retrieving the first N records for a specific tenant and object type while applying random filters across hundreds or thousands of columns. This makes creating indexes for all possible filter combinations impractical. The query might also include a sort operation after filtering.
- Calculating the total count of records that match the filter criteria.
