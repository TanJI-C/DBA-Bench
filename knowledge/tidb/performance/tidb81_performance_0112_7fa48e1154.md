# Identify query optimizations by adding an index

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-walkthrough.md`
- Source Title: `EXPLAIN Walkthrough`
- Source Heading Path: ``EXPLAIN` Walkthrough > Identify optimizations`
- Source Line Ranges: `121-199`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `indexing`, `predicate-pushdown`, `index-range-scan`, `ddl`, `show-create-table`, `admin-show-ddl-jobs`, `execution-plan`, `explain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0112_7fa48e1154`
- Source ID: `tidb-docs-8.1:explain-walkthrough.md#identify-optimizations`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c54124b35c3c70932a0e98d274a3b31d6f006de8d07035c17d505851c51a4e6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-walkthrough#identify-optimizations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-walkthrough.md

## Retrieval Guidance

- Use When: Use this chunk when identifying a query optimization opportunity where a predicate is applied after a TableFullScan and you need to confirm that adding an index changes the execution plan.
- Retrieval Keywords: SHOW CREATE TABLE trips, ALTER TABLE trips ADD INDEX (start_date), ADMIN SHOW DDL JOBS, tidb_ddl_reorg_batch_size, tidb_ddl_reorg_worker_cnt, EXPLAIN, EXPLAIN ANALYZE, TableFullScan, Selection, IndexReader, IndexRangeScan, start_date BETWEEN, predicate push into an index reader operator
- Follow-up Guidance: After adding the index, the source shows repeating EXPLAIN and EXPLAIN ANALYZE to verify that TableFullScan and Selection are eliminated and the new plan uses IndexReader and IndexRangeScan.
- Classification Note: This is classified as performance because the content focuses on improving execution efficiency by adding an index so the predicate can be applied through an index range scan instead of a full table scan.

## Official Source Content

## Identify optimizations

The current execution plan is efficient in the following aspects:

* Most of the work is handled inside the TiKV coprocessor. Only 56 rows need to be sent across the network back to TiDB for processing. Each of these rows is short and contains only the count that matches the selection.

* Aggregating the count of rows both in TiDB (`StreamAgg_20`) and in TiKV (`└─StreamAgg_9`) uses the stream aggregation, which is very efficient in its memory usage.

The biggest issue with the current execution plan is that the predicate `start_date BETWEEN '2017-07-01 00:00:00' AND '2017-07-01 23:59:59'` does not apply immediately. All rows are read first with a `TableFullScan` operator, and then a selection is applied afterwards. You can find out the cause from the output of `SHOW CREATE TABLE trips`:

```sql
SHOW CREATE TABLE trips\G
```

```sql
*************************** 1. row ***************************
       Table: trips
Create Table: CREATE TABLE `trips` (
  `trip_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `duration` int(11) NOT NULL,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `start_station_number` int(11) DEFAULT NULL,
  `start_station` varchar(255) DEFAULT NULL,
  `end_station_number` int(11) DEFAULT NULL,
  `end_station` varchar(255) DEFAULT NULL,
  `bike_number` varchar(255) DEFAULT NULL,
  `member_type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`trip_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin AUTO_INCREMENT=20477318
1 row in set (0.00 sec)
```

There is **NO** index on `start_date`. You would need an index in order to push this predicate into an index reader operator. Add an index as follows:

```sql
ALTER TABLE trips ADD INDEX (start_date);
```

```sql
Query OK, 0 rows affected (2 min 10.23 sec)
```

> **Note:**
>
> You can monitor the progress of DDL jobs using the [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl) command. The defaults in TiDB are carefully chosen so that adding an index does not impact production workloads too much. For testing environments, consider increasing the [`tidb_ddl_reorg_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_batch_size) and [`tidb_ddl_reorg_worker_cnt`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_worker_cnt) values. On a reference system, a batch size of `10240` and worker count of `32` can achieve a 10x performance improvement over the defaults.

After adding an index, you can then repeat the query in `EXPLAIN`. In the following output, you can see that a new execution plan is chosen, and the `TableFullScan` and `Selection` operators have been eliminated:

```sql
EXPLAIN SELECT count(*) FROM trips WHERE start_date BETWEEN '2017-07-01 00:00:00' AND '2017-07-01 23:59:59';
```

```sql
+-----------------------------+---------+-----------+-------------------------------------------+-------------------------------------------------------------------+
| id                          | estRows | task      | access object                             | operator info                                                     |
+-----------------------------+---------+-----------+-------------------------------------------+-------------------------------------------------------------------+
| StreamAgg_17                | 1.00    | root      |                                           | funcs:count(Column#13)->Column#11                                 |
| └─IndexReader_18            | 1.00    | root      |                                           | index:StreamAgg_9                                                 |
|   └─StreamAgg_9             | 1.00    | cop[tikv] |                                           | funcs:count(1)->Column#13                                         |
|     └─IndexRangeScan_16     | 8471.88 | cop[tikv] | table:trips, index:start_date(start_date) | range:[2017-07-01 00:00:00,2017-07-01 23:59:59], keep order:false |
+-----------------------------+---------+-----------+-------------------------------------------+-------------------------------------------------------------------+
4 rows in set (0.00 sec)
```

To compare the actual execution time, you can again use [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze):

```sql
EXPLAIN ANALYZE SELECT count(*) FROM trips WHERE start_date BETWEEN '2017-07-01 00:00:00' AND '2017-07-01 23:59:59';
```
