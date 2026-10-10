# Hybrid workload with TiFlash replicas

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-hybrid-oltp-and-olap-queries.md`
- Source Title: `HTAP Queries`
- Source Heading Path: `HTAP Queries > Hybrid workload | HTAP Queries > Hybrid workload > Create TiFlash replicas`
- Source Line Ranges: `143-209`
- Source Scope: `developer`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `sql`
- Topic Tags: `hybrid-workload`, `replicas`, `tiflash-replica`, `alter-table`, `information-schema`, `explain`, `coprocessor`, `performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0060_c1ad2be5ff`
- Source ID: `tidb-docs-8.1:develop/dev-guide-hybrid-oltp-and-olap-queries.md#hybrid-workload`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8d288388392bcdad232592e92fa2d21d3a988cf1ccb314754d8e5808f66fe2fb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-hybrid-oltp-and-olap-queries#hybrid-workload
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-hybrid-oltp-and-olap-queries.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB uses TiFlash replicas in a hybrid workload, how to create and verify TiFlash replicas for books and orders, or how to confirm cop[tiflash] in an execution plan.
- Retrieval Keywords: Hybrid workload, Create TiFlash replicas, ALTER TABLE books SET TIFLASH REPLICA 1, ALTER TABLE orders SET TIFLASH REPLICA 1, information_schema.tiflash_replica, TABLE_SCHEMA = 'bookshop', TABLE_NAME = 'books', TABLE_NAME = 'orders', AVAILABLE, PROGRESS, EXPLAIN, cop[tiflash], TiFlash engine, TiKV, full table scan, columnar TiFlash, row-based TiKV
- Follow-up Guidance: After replicas are available, the chunk says to use EXPLAIN on the PARTITION BY window function query and notes that cop[tiflash] indicates the TiFlash engine has started to work.
- Classification Note: This is classified as operation because the content gives concrete SQL steps and verification checks for creating TiFlash replicas and inspecting their usage in query execution.

## Official Source Content

## Hybrid workload

When using TiDB for real-time online analytical processing in hybrid load scenarios, you only need to provide an entry point of TiDB to your data. TiDB automatically selects different processing engines based on the specific business.
### Create TiFlash replicas

TiDB uses the row-based storage engine, TiKV, by default. To use the columnar storage engine, TiFlash, see [Enable HTAP capability](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#use-htap-capabilities). Before querying data through TiFlash, you need to create TiFlash replicas for `books` and `orders` tables using the following statement:

```sql
ALTER TABLE books SET TIFLASH REPLICA 1;
ALTER TABLE orders SET TIFLASH REPLICA 1;
```

You can check the progress of the TiFlash replicas using the following statement:

```sql
SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = 'bookshop' and TABLE_NAME = 'books';
SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = 'bookshop' and TABLE_NAME = 'orders';
```

A `PROGRESS` column of 1 indicates that the progress is 100% complete, and a `AVAILABLE` column of 1 indicates that the replica is currently available.

```
+--------------+------------+----------+---------------+-----------------+-----------+----------+
| TABLE_SCHEMA | TABLE_NAME | TABLE_ID | REPLICA_COUNT | LOCATION_LABELS | AVAILABLE | PROGRESS |
+--------------+------------+----------+---------------+-----------------+-----------+----------+
| bookshop     | books      |      143 |             1 |                 |         1 |        1 |
+--------------+------------+----------+---------------+-----------------+-----------+----------+
1 row in set (0.07 sec)
+--------------+------------+----------+---------------+-----------------+-----------+----------+
| TABLE_SCHEMA | TABLE_NAME | TABLE_ID | REPLICA_COUNT | LOCATION_LABELS | AVAILABLE | PROGRESS |
+--------------+------------+----------+---------------+-----------------+-----------+----------+
| bookshop     | orders     |      147 |             1 |                 |         1 |        1 |
+--------------+------------+----------+---------------+-----------------+-----------+----------+
1 row in set (0.07 sec)
```

After replicas are added, you can use the `EXPLAIN` statement to check the execution plan of the above window function [`PARTITION BY` clause](#partition-by-clause). If `cop[tiflash]` appears in the execution plan, it means that the TiFlash engine has started to work.

Then, execute the sample SQL statement in [`PARTITION BY` clause](#partition-by-clause) again. The result is as follows:

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
1500 rows in set (0.79 sec)
```

By comparing the two execution results, you can find that the query speed is significantly improved with TiFlash (the improvement is more significant with a large volume of data). This is because a window function usually relies on a full table scan for some columns, and columnar TiFlash is more suitable to handle this type of analytical task than row-based TiKV. For TiKV, if you use primary keys or indexes to reduce the number of rows to be queried, the queries can be fast too and consume fewer resources compared with TiFlash.
