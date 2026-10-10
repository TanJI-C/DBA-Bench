# TiFlash window function pushdown examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-supported-pushdown-calculations.md`
- Source Title: `Push-down calculations Supported by TiFlash`
- Source Heading Path: `Push-down Calculations Supported by TiFlash > Examples > Example 4: Window functions`
- Source Line Ranges: `159-206`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `sql`, `tidb`, `tikv`
- Topic Tags: `pushdown`, `window-functions`, `mpp`, `explain`, `row-number`, `max`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0955_ab67b4ea5e`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-supported-pushdown-calculations.md#example-4-window-functions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5d05861ac40d9b073693a5708a650aec21317881acc440e6f2acfeef01212a88`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations#example-4-window-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-supported-pushdown-calculations.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether TiFlash can push down window functions in MPP by reading EXPLAIN output for ROW_NUMBER() or MAX() OVER (PARTITION BY id > 10).
- Retrieval Keywords: TiFlash window function pushdown, EXPLAIN ROW_NUMBER() OVER (PARTITION BY id > 10), EXPLAIN MAX(id) OVER (PARTITION BY id > 10), Window mpp[tiflash], Window root task column, MppVersion: 1, ExchangeSender, ExchangeReceiver, HashPartition, ROW_NUMBER push down to TiFlash, MAX window function cannot be pushed down, MAX() only supported for push-down as an aggregate function, ALTER TABLE t SET TIFLASH REPLICA 1
- Follow-up Guidance: The examples distinguish pushdown by the EXPLAIN task column: `Window` shows `mpp[tiflash]` for `ROW_NUMBER() OVER (PARTITION BY id > 10)` and `root` for `MAX(id) OVER (PARTITION BY id > 10)`.
- Classification Note: This is reference content because it provides concrete EXPLAIN examples that show supported and unsupported TiFlash pushdown behavior for window functions.

## Official Source Content

### Example 4: Window functions

```sql
CREATE TABLE t(id INT PRIMARY KEY, c1 VARCHAR(100));
ALTER TABLE t SET TIFLASH REPLICA 1;
INSERT INTO t VALUES(1,"foo"),(2,"bar"),(3,"bar foo"),(10,"foo"),(20,"bar"),(30,"bar foo");

EXPLAIN SELECT id, ROW_NUMBER() OVER (PARTITION BY id > 10) FROM t;
+----------------------------------+----------+--------------+---------------+---------------------------------------------------------------------------------------------------------------+
| id                               | estRows  | task         | access object | operator info                                                                                                 |
+----------------------------------+----------+--------------+---------------+---------------------------------------------------------------------------------------------------------------+
| TableReader_30                   | 10000.00 | root         |               | MppVersion: 1, data:ExchangeSender_29                                                                         |
| └─ExchangeSender_29              | 10000.00 | mpp[tiflash] |               | ExchangeType: PassThrough                                                                                     |
|   └─Projection_7                 | 10000.00 | mpp[tiflash] |               | test.t.id, Column#5, stream_count: 4                                                                          |
|     └─Window_28                  | 10000.00 | mpp[tiflash] |               | row_number()->Column#5 over(partition by Column#4 rows between current row and current row), stream_count: 4  |
|       └─Sort_14                  | 10000.00 | mpp[tiflash] |               | Column#4, stream_count: 4                                                                                     |
|         └─ExchangeReceiver_13    | 10000.00 | mpp[tiflash] |               | stream_count: 4                                                                                               |
|           └─ExchangeSender_12    | 10000.00 | mpp[tiflash] |               | ExchangeType: HashPartition, Compression: FAST, Hash Cols: [name: Column#4, collate: binary], stream_count: 4 |
|             └─Projection_10      | 10000.00 | mpp[tiflash] |               | test.t.id, gt(test.t.id, 10)->Column#4                                                                        |
|               └─TableFullScan_11 | 10000.00 | mpp[tiflash] | table:t       | keep order:false, stats:pseudo                                                                                |
+----------------------------------+----------+--------------+---------------+---------------------------------------------------------------------------------------------------------------+
9 rows in set (0.0073 sec)

```

In this output, you can see that the `Window` operation has a value of `mpp[tiflash]` in the `task` column, indicating that the `ROW_NUMBER() OVER (PARTITION BY id > 10)` operation can be pushed down to TiFlash.

```sql
CREATE TABLE t(id INT PRIMARY KEY, c1 VARCHAR(100));
ALTER TABLE t SET TIFLASH REPLICA 1;
INSERT INTO t VALUES(1,"foo"),(2,"bar"),(3,"bar foo"),(10,"foo"),(20,"bar"),(30,"bar foo");

EXPLAIN SELECT id, MAX(id) OVER (PARTITION BY id > 10) FROM t;
+-----------------------------+----------+-----------+---------------+------------------------------------------------------------+
| id                          | estRows  | task      | access object | operator info                                              |
+-----------------------------+----------+-----------+---------------+------------------------------------------------------------+
| Projection_6                | 10000.00 | root      |               | test.t1.id, Column#5                                       |
| └─Shuffle_14                | 10000.00 | root      |               | execution info: concurrency:5, data sources:[Projection_8] |
|   └─Window_7                | 10000.00 | root      |               | max(test.t1.id)->Column#5 over(partition by Column#4)      |
|     └─Sort_13               | 10000.00 | root      |               | Column#4                                                   |
|       └─Projection_8        | 10000.00 | root      |               | test.t1.id, gt(test.t1.id, 10)->Column#4                   |
|         └─TableReader_10    | 10000.00 | root      |               | data:TableFullScan_9                                       |
|           └─TableFullScan_9 | 10000.00 | cop[tikv] | table:t1      | keep order:false, stats:pseudo                             |
+-----------------------------+----------+-----------+---------------+------------------------------------------------------------+
7 rows in set (0.0010 sec)
```

In this output, you can see that the `Window` operation has a value of `root` in the `task` column, indicating that the `MAX(id) OVER (PARTITION BY id > 10)` operation cannot be pushed down to TiFlash. This is because `MAX()` is only supported for push-down as an aggregate function and not as a window function.
