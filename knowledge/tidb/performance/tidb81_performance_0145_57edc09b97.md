# HTAP query, TiFlash replication, and performance verification

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/quick-start-with-htap.md`
- Source Title: `Quick start with HTAP`
- Source Heading Path: `Quick Start Guide for TiDB HTAP > Steps > Step 3. Query data with the row-based storage engine | Quick Start Guide for TiDB HTAP > Steps > Step 4. Replicate the test data to the columnar storage engine | Quick Start Guide for TiDB HTAP > Steps > Step 5. Analyze data faster using HTAP | Quick Start Guide for TiDB HTAP > What's next`
- Source Line Ranges: `104-215`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `sql`, `shared`
- Topic Tags: `row-store`, `columnar-replica`, `replication`, `tiflash-replica`, `mpp`, `explain-analyze`, `query-performance`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0145_57edc09b97`
- Source ID: `tidb-docs-8.1:quick-start-with-htap.md#step-3-query-data-with-the-row-based-storage-engine`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2434a980f54d100933a1b762eee7befd26f193f8dd7bfdd087bbed9730b47c48`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/quick-start-with-htap#step-3-query-data-with-the-row-based-storage-engine
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/quick-start-with-htap.md

## Retrieval Guidance

- Use When: Use this chunk when the request is about running the sample row-store query, creating TiFlash replicas for test.customer, test.orders, and test.lineitem, checking replication status, or verifying whether TiFlash MPP was selected with EXPLAIN ANALYZE.
- Retrieval Keywords: shipping priority query, USE test, SELECT l_orderkey, c_mktsegment = 'BUILDING', o_orderdate < DATE '1996-01-01', l_shipdate > DATE '1996-02-01', ALTER TABLE test.customer SET TIFLASH REPLICA 1, ALTER TABLE test.orders SET TIFLASH REPLICA 1, ALTER TABLE test.lineitem SET TIFLASH REPLICA 1, information_schema.tiflash_replica, AVAILABLE, PROGRESS, EXPLAIN ANALYZE, desc, ExchangeSender, ExchangeReceiver, MPP mode, Use TiDB to read TiFlash replicas
- Follow-up Guidance: The source notes that after comparing the two query methods, you can continue with Architecture of TiDB HTAP, Explore HTAP, and Use TiFlash.
- Classification Note: This chunk is classified as performance because the official content focuses on comparing query execution before and after TiFlash replication and checking optimizer and MPP usage with EXPLAIN ANALYZE.

## Official Source Content

### Step 3. Query data with the row-based storage engine

To know the performance of TiDB with only the row-based storage engine, execute the following SQL statements:

```sql
USE test;
SELECT
    l_orderkey,
    SUM(
        l_extendedprice * (1 - l_discount)
    ) AS revenue,
    o_orderdate,
    o_shippriority
FROM
    customer,
    orders,
    lineitem
WHERE
    c_mktsegment = 'BUILDING'
AND c_custkey = o_custkey
AND l_orderkey = o_orderkey
AND o_orderdate < DATE '1996-01-01'
AND l_shipdate > DATE '1996-02-01'
GROUP BY
    l_orderkey,
    o_orderdate,
    o_shippriority
ORDER BY
    revenue DESC,
    o_orderdate
limit 10;
```

This is a shipping priority query, which provides the priority and potential revenue of the highest-revenue order that has not been shipped before a specified date. The potential revenue is defined as the sum of `l_extendedprice * (1-l_discount)`. The orders are listed in the descending order of revenue. In this example, this query lists the unshipped orders with potential query revenue in the top 10.
### Step 4. Replicate the test data to the columnar storage engine

After TiFlash is deployed, TiKV does not replicate data to TiFlash immediately. You need to execute the following DDL statements in a MySQL client of TiDB to specify which tables need to be replicated. After that, TiDB will create the specified replicas in TiFlash accordingly.

```sql
ALTER TABLE test.customer SET TIFLASH REPLICA 1;
ALTER TABLE test.orders SET TIFLASH REPLICA 1;
ALTER TABLE test.lineitem SET TIFLASH REPLICA 1;
```

To check the replication status of the specific tables, execute the following statements:

```sql
SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = 'test' and TABLE_NAME = 'customer';
SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = 'test' and TABLE_NAME = 'orders';
SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = 'test' and TABLE_NAME = 'lineitem';
```

In the result of the above statements:

- `AVAILABLE` indicates whether the TiFlash replica of a specific table is available or not. `1` means available and `0` means unavailable. Once the `AVAILABLE` field becomes `1`, this status does not change anymore.
- `PROGRESS` means the progress of the replication. The value is between 0.0 and 1.0. 1 means that the replication progress of the TiFlash replica is complete.
### Step 5. Analyze data faster using HTAP

Execute the SQL statements in [Step 3](#step-3-query-data-with-the-row-based-storage-engine) again, and you can see the performance of TiDB HTAP.

For tables with TiFlash replicas, the TiDB optimizer automatically determines whether to use TiFlash replicas based on the cost estimation. To check whether or not a TiFlash replica is selected, you can use the `desc` or `explain analyze` statement. For example:

```sql
USE test;
EXPLAIN ANALYZE SELECT
    l_orderkey,
    SUM(
        l_extendedprice * (1 - l_discount)
    ) AS revenue,
    o_orderdate,
    o_shippriority
FROM
    customer,
    orders,
    lineitem
WHERE
    c_mktsegment = 'BUILDING'
AND c_custkey = o_custkey
AND l_orderkey = o_orderkey
AND o_orderdate < DATE '1996-01-01'
AND l_shipdate > DATE '1996-02-01'
GROUP BY
    l_orderkey,
    o_orderdate,
    o_shippriority
ORDER BY
    revenue DESC,
    o_orderdate
limit 10;
```

If the result of the `EXPLAIN` statement shows `ExchangeSender` and `ExchangeReceiver` operators, it indicates that the MPP mode has taken effect.

In addition, you can specify that each part of the entire query is computed using only the TiFlash engine. For detailed information, see [Use TiDB to read TiFlash replicas](https://docs.pingcap.com/tidb/stable/tiflash/use-tidb-to-read-tiflash).

You can compare query results and query performance of these two methods.
## What's next

- [Architecture of TiDB HTAP](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#architecture)
- [Explore HTAP](https://docs.pingcap.com/tidb/stable/explore-htap)
- [Use TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#use-tiflash)
