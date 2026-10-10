# Non-prepared plan cache benefits, diagnostics, and monitoring

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-non-prepared-plan-cache.md`
- Source Title: `SQL Non-Prepared Execution Plan Cache`
- Source Heading Path: `SQL Non-Prepared Execution Plan Cache > Performance benefits | SQL Non-Prepared Execution Plan Cache > Diagnostics | SQL Non-Prepared Execution Plan Cache > Monitoring`
- Source Line Ranges: `96-188`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `performance-benefits`, `grafana`, `metrics`, `warnings`, `explain`, `plan-cache`, `statements-summary`, `slow-query-log`, `memory-usage`, `hit-rate`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0077_1055492a5b`
- Source ID: `tidb-docs-8.1:sql-non-prepared-plan-cache.md#performance-benefits`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `985bafebece17677a9651e7bea8238d0dfb12880d1f32992f1a007e21d568e40`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache#performance-benefits
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-non-prepared-plan-cache.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about observed benefits, how to diagnose why a non-prepared query cannot hit the plan cache, or which metrics and tables show non-prepared plan cache usage and hit rate.
- Retrieval Keywords: Performance benefits, Queries Using Plan Cache OPS, Plan Cache Miss OPS, non-prepared, non-prepared-unsupported, Grafana, EXPLAIN FORMAT='plan_cache', SHOW warnings, skip non-prepared plan-cache, statements_summary, INFORMATION_SCHEMA.STATEMENTS_SUMMARY, digest_text, query_sample_text, exec_count, plan_in_cache, plan_cache_hits, slow query log, memory usage, number of plans in the cache, cache hit rate
- Follow-up Guidance: It also shows that EXPLAIN must use FORMAT='plan_cache' to check cache eligibility and that SHOW warnings returns the reason when a query cannot hit the cache.
- Classification Note: This is classified as observability because the content focuses on measuring performance impact, diagnosing cache eligibility with EXPLAIN and warnings, and monitoring memory usage and hit rate through Grafana, statements_summary, and the slow query log.

## Official Source Content

## Performance benefits

In internal tests, enabling the non-prepared plan cache feature can achieve significant performance benefits in most TP scenarios. For example, a performance improvement of about 4% in TPC-C tests, over 10% in some banking workloads, and 15% in Sysbench RangeScan.

However, this feature also introduces some additional memory and CPU overhead, including determining whether the query is supported, parameterizing the query, and searching for a plan in the cache. If the cache cannot hit the majority of queries in your workload, enabling it might actually adversely affect performance.

In this case, you need to observe the `non-prepared` metric in the **Queries Using Plan Cache OPS** panel and the `non-prepared-unsupported` metric in the **Plan Cache Miss OPS** panel on Grafana. If most queries are not supported and only a few can hit the plan cache, you can disable this feature.

![non-prepared-unsupported](/media/non-prepapred-plan-cache-unsupprot.png)
## Diagnostics

After enabling the non-prepared plan cache, you can execute the `EXPLAIN FORMAT='plan_cache' SELECT ...` statement to verify whether the query can hit the cache. For queries that cannot hit the cache, the system returns the reason in a warning.

Note that if you do not add `FORMAT='plan_cache'`, the `EXPLAIN` statement will never hit the cache.

To verify whether the query hits the cache, execute the following `EXPLAIN FORMAT='plan_cache'` statement:

```sql
EXPLAIN FORMAT='plan_cache' SELECT * FROM (SELECT a+1 FROM t) t;
```

The output is as follows:

```sql
3 rows in set, 1 warning (0.00 sec)
```

To view the queries that cannot hit the cache, execute `SHOW warnings;`:

```sql
SHOW warnings;
```

The output is as follows:

```sql
+---------+------+-------------------------------------------------------------------------------+
| Level   | Code | Message                                                                       |
+---------+------+-------------------------------------------------------------------------------+
| Warning | 1105 | skip non-prepared plan-cache: queries that have sub-queries are not supported |
+---------+------+-------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

In the preceding example, the query cannot hit the cache because the non-prepared plan cache does not support the `+` operation.
## Monitoring

After enabling the non-prepared plan cache, you can monitor the memory usage, number of plans in the cache, and cache hit rate in the following panes:

![non-prepare-plan-cache](/media/tidb-non-prepared-plan-cache-metrics.png)

You can also monitor the cache hit rate in the `statements_summary` table and slow query log. The following shows how to view the cache hit rate in the `statements_summary` table:

1. Create a table `t`:

    ```sql
    CREATE TABLE t (a int);
    ```

2. Enable the non-prepared plan cache:

    ```sql
    SET @@tidb_enable_non_prepared_plan_cache=ON;
    ```

3. Execute the following three queries:

    ```sql
    SELECT * FROM t WHERE a<1;
    SELECT * FROM t WHERE a<2;
    SELECT * FROM t WHERE a<3;
    ```

4. Query the `statements_summary` table to view the cache hit rate:

    ```sql
    SELECT digest_text, query_sample_text, exec_count, plan_in_cache, plan_cache_hits FROM INFORMATION_SCHEMA.STATEMENTS_SUMMARY WHERE query_sample_text LIKE '%SELECT * FROM %';
    ```

    The output is as follows:

    ```sql
    +---------------------------------+------------------------------------------+------------+---------------+-----------------+
    | digest_text                     | query_sample_text                        | exec_count | plan_in_cache | plan_cache_hits |
    +---------------------------------+------------------------------------------+------------+---------------+-----------------+
    | SELECT * FROM `t` WHERE `a` < ? | SELECT * FROM t WHERE a<1                |          3 |             1 |               2 |
    +---------------------------------+------------------------------------------+------------+---------------+-----------------+
    1 row in set (0.01 sec)
    ```

    From the output, you can see that the query was executed three times and hit the cache twice.
