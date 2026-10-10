# Query slow logs with SLOW_QUERY and CLUSTER_SLOW_QUERY

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/identify-slow-queries.md`
- Source Title: `Identify Slow Queries`
- Source Heading Path: `Identify Slow Queries > Memory mapping in slow log | Identify Slow Queries > `SLOW_QUERY` / `CLUSTER_SLOW_QUERY` usage examples | Identify Slow Queries > `SLOW_QUERY` / `CLUSTER_SLOW_QUERY` usage examples > Top-N slow queries | Identify Slow Queries > `SLOW_QUERY` / `CLUSTER_SLOW_QUERY` usage examples > Query the Top-N slow queries of the `test` user | Identify Slow Queries > `SLOW_QUERY` / `CLUSTER_SLOW_QUERY` usage examples > Query similar slow queries with the same SQL fingerprints | Identify Slow Queries > Query slow queries with pseudo `stats``
- Source Line Ranges: `202-383`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`, `sql`
- Topic Tags: `slow-query-log`, `information-schema`, `slow_query`, `cluster_slow_query`, `sql-fingerprints`, `top-n`, `pseudo-stats`, `time-range`, `rotated-logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0047_c1279c9f32`
- Source ID: `tidb-docs-8.1:identify-slow-queries.md#memory-mapping-in-slow-log`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cb14982ed249eeb15d473bc931c6402cb55bc867769c7f8d7b1313baf90a24cb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/identify-slow-queries#memory-mapping-in-slow-log
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/identify-slow-queries.md

## Retrieval Guidance

- Use When: Use this chunk when you need SQL examples for querying slow query logs from INFORMATION_SCHEMA.SLOW_QUERY or CLUSTER_SLOW_QUERY, including time-range filtering, Top-N slow queries, SQL fingerprint lookup by digest, or rows whose stats contain pseudo.
- Retrieval Keywords: INFORMATION_SCHEMA.SLOW_QUERY, CLUSTER_SLOW_QUERY, slow_query, cluster_slow_query, TIME range, rotated slow log file, where time > '2020-03-10 00:00:00' and time < '2020-03-11 00:00:00', INSTANCE column, is_internal = false, Top-N slow queries, user = "test", digest, SQL fingerprints, stats like '%pseudo%', select query_time, query from information_schema.slow_query, select query, query_time from information_schema.slow_query where digest
- Follow-up Guidance: The content notes that querying SLOW_QUERY reads and parses the current slow query log each time, and that if the slow log files for the specified time range are removed or there is no slow query, the query returns NULL.
- Classification Note: This is classified as diagnosis content because it shows how to inspect slow query information through the SLOW_QUERY and CLUSTER_SLOW_QUERY system tables and related SQL filters.

## Official Source Content

## Memory mapping in slow log

You can query the content of the slow query log by querying the `INFORMATION_SCHEMA.SLOW_QUERY` table. Each column name in the table corresponds to one field name in the slow log. For table structure, see the introduction to the `SLOW_QUERY` table in [Information Schema](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-slow-query).

> **Note:**
>
> Every time you query the `SLOW_QUERY` table, TiDB reads and parses the current slow query log.

For TiDB 4.0, `SLOW_QUERY` supports querying the slow log of any period of time, including the rotated slow log file. You need to specify the `TIME` range to locate the slow log files that need to be parsed. If you don't specify the `TIME` range, TiDB only parses the current slow log file. For example:

* If you don't specify the time range, TiDB only parses the slow query data that TiDB is writing to the slow log file:

    ```sql
    select count(*),
          min(time),
          max(time)
    from slow_query;
    ```

    ```
    +----------+----------------------------+----------------------------+
    | count(*) | min(time)                  | max(time)                  |
    +----------+----------------------------+----------------------------+
    | 122492   | 2020-03-11 23:35:20.908574 | 2020-03-25 19:16:38.229035 |
    +----------+----------------------------+----------------------------+
    ```

* If you specify the time range, for example, from `2020-03-10 00:00:00` to `2020-03-11 00:00:00`, TiDB first locates the slow log files of the specified time range, and then parses the slow query information:

    ```sql
    select count(*),
          min(time),
          max(time)
    from slow_query
    where time > '2020-03-10 00:00:00'
      and time < '2020-03-11 00:00:00';
    ```

    ```
    +----------+----------------------------+----------------------------+
    | count(*) | min(time)                  | max(time)                  |
    +----------+----------------------------+----------------------------+
    | 2618049  | 2020-03-10 00:00:00.427138 | 2020-03-10 23:00:22.716728 |
    +----------+----------------------------+----------------------------+
    ```

> **Note:**
>
> If the slow log files of the specified time range are removed, or there is no slow query, the query returns NULL.

TiDB 4.0 adds the [`CLUSTER_SLOW_QUERY`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-slow-query#cluster_slow_query-table) system table to query the slow query information of all TiDB nodes. The table schema of the `CLUSTER_SLOW_QUERY` table differs from that of the `SLOW_QUERY` table in that an `INSTANCE` column is added to `CLUSTER_SLOW_QUERY`. The `INSTANCE` column represents the TiDB node address of the row information on the slow query. You can use `CLUSTER_SLOW_QUERY` the way you do with [`SLOW_QUERY`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-slow-query).

When you query the `CLUSTER_SLOW_QUERY` table, TiDB pushes the computation and the judgment down to other nodes, instead of retrieving all slow query information from other nodes and executing the operations on one TiDB node.
## `SLOW_QUERY` / `CLUSTER_SLOW_QUERY` usage examples
### Top-N slow queries

Query the Top 2 slow queries of users. `Is_internal=false` means excluding slow queries inside TiDB and only querying slow queries of users.

```sql
select query_time, query
from information_schema.slow_query
where is_internal = false
order by query_time desc
limit 2;
```

Output example:

```
+--------------+------------------------------------------------------------------+
| query_time   | query                                                            |
+--------------+------------------------------------------------------------------+
| 12.77583857  | select * from t_slim, t_wide where t_slim.c0=t_wide.c0;          |
|  0.734982725 | select t0.c0, t1.c1 from t_slim t0, t_wide t1 where t0.c0=t1.c0; |
+--------------+------------------------------------------------------------------+
```
### Query the Top-N slow queries of the `test` user

In the following example, the slow queries executed by the `test` user are queried, and the first two results are displayed in reverse order of execution time.

```sql
select query_time, query, user
from information_schema.slow_query
where is_internal = false
  and user = "test"
order by query_time desc
limit 2;
```

Output example:

```
+-------------+------------------------------------------------------------------+----------------+
| Query_time  | query                                                            | user           |
+-------------+------------------------------------------------------------------+----------------+
| 0.676408014 | select t0.c0, t1.c1 from t_slim t0, t_wide t1 where t0.c0=t1.c1; | test           |
+-------------+------------------------------------------------------------------+----------------+
```
### Query similar slow queries with the same SQL fingerprints

After querying the Top-N SQL statements, continue to query similar slow queries using the same fingerprints.

1. Acquire Top-N slow queries and the corresponding SQL fingerprints.

    ```sql
    select query_time, query, digest
    from information_schema.slow_query
    where is_internal = false
    order by query_time desc
    limit 1;
    ```

    Output example:

    ```
    +-------------+-----------------------------+------------------------------------------------------------------+
    | query_time  | query                       | digest                                                           |
    +-------------+-----------------------------+------------------------------------------------------------------+
    | 0.302558006 | select * from t1 where a=1; | 4751cb6008fda383e22dacb601fde85425dc8f8cf669338d55d944bafb46a6fa |
    +-------------+-----------------------------+------------------------------------------------------------------+
    ```

2. Query similar slow queries with the fingerprints.

    ```sql
    select query, query_time
    from information_schema.slow_query
    where digest = "4751cb6008fda383e22dacb601fde85425dc8f8cf669338d55d944bafb46a6fa";
    ```

    Output example:

    ```
    +-----------------------------+-------------+
    | query                       | query_time  |
    +-----------------------------+-------------+
    | select * from t1 where a=1; | 0.302558006 |
    | select * from t1 where a=2; | 0.401313532 |
    +-----------------------------+-------------+
    ```
## Query slow queries with pseudo `stats`

```sql
select query, query_time, stats
from information_schema.slow_query
where is_internal = false
  and stats like '%pseudo%';
```

Output example:

```
+-----------------------------+-------------+---------------------------------+
| query                       | query_time  | stats                           |
+-----------------------------+-------------+---------------------------------+
| select * from t1 where a=1; | 0.302558006 | t1:pseudo                       |
| select * from t1 where a=2; | 0.401313532 | t1:pseudo                       |
| select * from t1 where a>2; | 0.602011247 | t1:pseudo                       |
| select * from t1 where a>3; | 0.50077719  | t1:pseudo                       |
| select * from t1 join t2;   | 0.931260518 | t1:407872303825682445,t2:pseudo |
+-----------------------------+-------------+---------------------------------+
```
