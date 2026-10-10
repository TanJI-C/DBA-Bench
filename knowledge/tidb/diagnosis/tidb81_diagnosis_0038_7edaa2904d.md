# EXPLAIN and EXPLAIN ANALYZE walkthrough for query plan assessment

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-walkthrough.md`
- Source Title: `EXPLAIN Walkthrough`
- Source Heading Path: ``EXPLAIN` Walkthrough | `EXPLAIN` Walkthrough > Assess the current performance`
- Source Line Ranges: `5-86`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `explain analyze`, `execution plan`, `query performance`, `statistics`, `analyze table`, `tablefullscan`, `stream aggregation`, `coprocessor`, `estrows`, `actrows`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0038_7edaa2904d`
- Source ID: `tidb-docs-8.1:explain-walkthrough.md#explain-walkthrough`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3205ccccbcab220bfa9757f14d9c5db902695bb19be23859d455323ff33416c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-walkthrough#explain-walkthrough
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-walkthrough.md

## Retrieval Guidance

- Use When: Use this chunk when assessing a query execution plan with EXPLAIN or EXPLAIN ANALYZE and interpreting estRows, actRows, TableFullScan, StreamAgg, Selection, and stats:pseudo for a count query on the trips table.
- Retrieval Keywords: EXPLAIN walkthrough, EXPLAIN ANALYZE, execution plan assessment, estRows, actRows, TableFullScan_18, Selection_19, StreamAgg_9, StreamAgg_20, TableReader_21, stats:pseudo, ANALYZE TABLE trips, SHOW TABLE REGIONS, cop[tikv], root, count(*) FROM trips WHERE start_date BETWEEN
- Follow-up Guidance: The content notes that after running ANALYZE TABLE trips, you can run EXPLAIN ANALYZE again to see estimates that are much closer, and SHOW TABLE REGIONS provides a general view of the Regions for the table.
- Classification Note: This is classified as diagnosis for the SQL component because the content explains how to inspect and interpret query execution plans and actual execution metrics to assess current query performance.

## Official Source Content

# `EXPLAIN` Walkthrough

Because SQL is a declarative language, you cannot automatically tell whether a query is executed efficiently. You must first use the [`EXPLAIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain) statement to learn the current execution plan.

The following statement from the [bikeshare example database](https://docs.pingcap.com/tidb/stable/import-example-data) counts how many trips were taken on July 1, 2017:

The following statement from the [bikeshare example database](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-sample-data) counts how many trips were taken on July 1, 2017:

```sql
EXPLAIN SELECT count(*) FROM trips WHERE start_date BETWEEN '2017-07-01 00:00:00' AND '2017-07-01 23:59:59';
```

```sql
+------------------------------+----------+-----------+---------------+------------------------------------------------------------------------------------------------------------------------+
| id                           | estRows  | task      | access object | operator info                                                                                                          |
+------------------------------+----------+-----------+---------------+------------------------------------------------------------------------------------------------------------------------+
| StreamAgg_20                 | 1.00     | root      |               | funcs:count(Column#13)->Column#11                                                                                      |
| └─TableReader_21             | 1.00     | root      |               | data:StreamAgg_9                                                                                                       |
|   └─StreamAgg_9              | 1.00     | cop[tikv] |               | funcs:count(1)->Column#13                                                                                              |
|     └─Selection_19           | 250.00   | cop[tikv] |               | ge(bikeshare.trips.start_date, 2017-07-01 00:00:00.000000), le(bikeshare.trips.start_date, 2017-07-01 23:59:59.000000) |
|       └─TableFullScan_18     | 10000.00 | cop[tikv] | table:trips   | keep order:false, stats:pseudo                                                                                         |
+------------------------------+----------+-----------+---------------+------------------------------------------------------------------------------------------------------------------------+
5 rows in set (0.00 sec)
```

From the child operator `└─TableFullScan_18` back, you can see its execution process as follows, which is currently suboptimal:

1. The coprocessor (TiKV) reads the entire `trips` table as a `TableFullScan` operation. It then passes the rows that it reads to the `Selection_19` operator, which is still within TiKV.
2. The `WHERE start_date BETWEEN ..` predicate is then filtered in the `Selection_19` operator. Approximately `250` rows are estimated to meet this selection. Note that this number is estimated according to the statistics and the operator's logic. The `└─TableFullScan_18` operator shows `stats:pseudo`, which means that the table does not have the actual statistical information. After running `ANALYZE TABLE trips` to collect statistical information, the statistics are expected to be more accurate.
3. The rows that meet the selection criteria then have a `count` function applied to them. This is also completed inside the `StreamAgg_9` operator, which is still inside TiKV (`cop[tikv]`). The TiKV coprocessor can execute a number of MySQL built-in functions, `count` being one of them.
4. The results from `StreamAgg_9` are then sent to the `TableReader_21` operator which is now inside the TiDB server (the task of `root`). The `estRows` column value for this operator is `1`, which means that the operator will receive one row from each of the TiKV Regions to be accessed. For more information about these requests, see [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze).
5. The `StreamAgg_20` operator then applies a `count` function to each of the rows from the `└─TableReader_21` operator, which you can see from [`SHOW TABLE REGIONS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-regions) and will be about 56 rows. Because this is the root operator, it then returns results to the client.

> **Note:**
>
> For a general view of the Regions that a table contains, execute [`SHOW TABLE REGIONS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-regions).
## Assess the current performance

`EXPLAIN` only returns the query execution plan but does not execute the query. To get the actual execution time, you can either execute the query or use `EXPLAIN ANALYZE`:

```sql
EXPLAIN ANALYZE SELECT count(*) FROM trips WHERE start_date BETWEEN '2017-07-01 00:00:00' AND '2017-07-01 23:59:59';
```

```sql
+------------------------------+----------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------+-----------+------+
| id                           | estRows  | actRows  | task      | access object | execution info                                                                                                                                                                                                                                    | operator info                                                                                                          | memory    | disk |
+------------------------------+----------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------+-----------+------+
| StreamAgg_20                 | 1.00     | 1        | root      |               | time:1.031417203s, loops:2                                                                                                                                                                                                                        | funcs:count(Column#13)->Column#11                                                                                      | 632 Bytes | N/A  |
| └─TableReader_21             | 1.00     | 56       | root      |               | time:1.031408123s, loops:2, cop_task: {num: 56, max: 782.147269ms, min: 5.759953ms, avg: 252.005927ms, p95: 609.294603ms, max_proc_keys: 910371, p95_proc_keys: 704775, tot_proc: 11.524s, tot_wait: 580ms, rpc_num: 56, rpc_time: 14.111932641s} | data:StreamAgg_9                                                                                                       | 328 Bytes | N/A  |
|   └─StreamAgg_9              | 1.00     | 56       | cop[tikv] |               | proc max:640ms, min:8ms, p80:276ms, p95:480ms, iters:18695, tasks:56                                                                                                                                                                              | funcs:count(1)->Column#13                                                                                              | N/A       | N/A  |
|     └─Selection_19           | 250.00   | 11409    | cop[tikv] |               | proc max:640ms, min:8ms, p80:276ms, p95:476ms, iters:18695, tasks:56                                                                                                                                                                              | ge(bikeshare.trips.start_date, 2017-07-01 00:00:00.000000), le(bikeshare.trips.start_date, 2017-07-01 23:59:59.000000) | N/A       | N/A  |
|       └─TableFullScan_18     | 10000.00 | 19117643 | cop[tikv] | table:trips   | proc max:612ms, min:8ms, p80:248ms, p95:460ms, iters:18695, tasks:56                                                                                                                                                                              | keep order:false, stats:pseudo                                                                                         | N/A       | N/A  |
+------------------------------+----------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------+-----------+------+
5 rows in set (1.03 sec)
```

The example query above takes `1.03` seconds to execute, which is not ideal performance.

From the result of `EXPLAIN ANALYZE` above, `actRows` indicates that some of the estimates (`estRows`) are inaccurate (expecting 10 thousand rows but finding 19 million rows), which is already indicated in the `operator info` (`stats:pseudo`) of `└─TableFullScan_18`. If you run [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) first and then `EXPLAIN ANALYZE` again, you can see that the estimates are much closer:

```sql
ANALYZE TABLE trips;
EXPLAIN ANALYZE SELECT count(*) FROM trips WHERE start_date BETWEEN '2017-07-01 00:00:00' AND '2017-07-01 23:59:59';
```
