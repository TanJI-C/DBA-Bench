# Generate and display execution plans with EXPLAIN and EXPLAIN ANALYZE

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > Understand execution plans > Generate and display execution plans`
- Source Line Ranges: `324-397`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `tiflash`, `dashboard`
- Topic Tags: `execution-plans`, `explain`, `explain-analyze`, `query-debugging`, `runtime-information`, `operator-metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0175_bd44cff4af`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#generate-and-display-execution-plans`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9142ba60efa37836f7a1302e9723e59ad48bc9f983b80303815bb5b46e3f59f7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#generate-and-display-execution-plans
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to inspect a SQL query execution plan with EXPLAIN or EXPLAIN ANALYZE and interpret estimated rows, runtime information, and execution layers such as TiDB, TiKV, or TiFlash.
- Retrieval Keywords: EXPLAIN, EXPLAIN ANALYZE, execution plan, actRows, estRows, execution info, memory, disk, task root, cop[tikv], mpp[tiflash], access object, operator info, TiDB Dashboard, runtime information, operator metrics
- Follow-up Guidance: The source also notes that execution plan information can be accessed through TiDB Dashboard and links to the EXPLAIN ANALYZE statement documentation for more information.
- Classification Note: This is classified under performance for the SQL component because it explains how to generate and read execution plans and runtime operator details for query debugging and tuning.

## Official Source Content

#### Generate and display execution plans

Besides accessing execution plan information through TiDB Dashboard, you can use the `EXPLAIN` statement to display the execution plan for a SQL query. The `EXPLAIN` output includes the following columns:

- `id`: the operator name and a unique identifier of the step.
- `estRows`: the estimated number of rows from the particular step.
- `task`: indicates the layer where the operator is executed. For example, `root` indicates execution on the TiDB server, `cop[tikv]` indicates execution on TiKV, and `mpp[tiflash]` indicates execution on TiFlash.
- `access object`: the object where row sources are located.
- `operator info`: additional details about the operator in the step.

```sql
EXPLAIN SELECT COUNT(*) FROM trips WHERE start_date BETWEEN '2017-07-01 00:00:00' AND '2017-07-01 23:59:59';
```

```
+--------------------------+-------------+--------------+-------------------+----------------------------------------------------------------------------------------------------+
| id                       | estRows     | task         | access object     | operator info                                                                                      |
+--------------------------+-------------+--------------+-------------------+----------------------------------------------------------------------------------------------------+
| StreamAgg_20             | 1.00        | root         |                   | funcs:count(Column#13)->Column#11                                                                  |
| └─TableReader_21         | 1.00        | root         |                   | data:StreamAgg_9                                                                                   |
|   └─StreamAgg_9          | 1.00        | cop[tikv]    |                   | funcs:count(1)->Column#13                                                                          |
|     └─Selection_19       | 250.00      | cop[tikv]    |                   | ge(trips.start_date, 2017-07-01 00:00:00.000000), le(trips.start_date, 2017-07-01 23:59:59.000000) |
|       └─TableFullScan_18 | 10000.00    | cop[tikv]    | table:trips       | keep order:false, stats:pseudo                                                                     |
+--------------------------+-------------+--------------+-------------------+----------------------------------------------------------------------------------------------------+
5 rows in set (0.00 sec)
```

Different from `EXPLAIN`, `EXPLAIN ANALYZE` executes the corresponding SQL statement, records its runtime information, and returns the runtime information together with the execution plan. This runtime information is crucial for debugging query execution. For more information, see [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze).

The `EXPLAIN ANALYZE` output includes:

- `actRows`: the number of rows output by the operator.
- `execution info`: detailed execution information of the operator. `time` represents the total `wall time`, including the total execution time of all sub-operators. If the operator is called many times by the parent operator, then the time refers to the accumulated time.
- `memory`: the memory used by the operator.
- `disk`: the disk space used by the operator.

The following is an example. Some attributes and table columns are omitted to improve formatting.

```sql
EXPLAIN ANALYZE
SELECT SUM(pm.m_count) / COUNT(*) 
FROM (
    SELECT COUNT(m.name) m_count
    FROM universe.moons m
    RIGHT JOIN (
        SELECT p.id, p.name
        FROM universe.planet_categories c
        JOIN universe.planets p
            ON c.id = p.category_id 
            AND c.name = 'Jovian'
    ) pc ON m.planet_id = pc.id
    GROUP BY pc.name
) pm;
```

```
+-----------------------------------------+.+---------+-----------+---------------------------+----------------------------------------------------------------+.+-----------+---------+
| id                                      |.| actRows | task      | access object             | execution info                                                 |.| memory    | disk    |
+-----------------------------------------+.+---------+-----------+---------------------------+----------------------------------------------------------------+.+-----------+---------+
| Projection_14                           |.| 1       | root      |                           | time:1.39ms, loops:2, RU:1.561975, Concurrency:OFF             |.| 9.64 KB   | N/A     |
| └─StreamAgg_16                          |.| 1       | root      |                           | time:1.39ms, loops:2                                           |.| 1.46 KB   | N/A     |
|   └─Projection_40                       |.| 4       | root      |                           | time:1.38ms, loops:4, Concurrency:OFF                          |.| 8.24 KB   | N/A     |
|     └─HashAgg_17                        |.| 4       | root      |                           | time:1.36ms, loops:4, partial_worker:{...}, final_worker:{...} |.| 82.1 KB   | N/A     |
|       └─HashJoin_19                     |.| 25      | root      |                           | time:1.29ms, loops:2, build_hash_table:{...}, probe:{...}      |.| 2.25 KB   | 0 Bytes |
|         ├─HashJoin_35(Build)            |.| 4       | root      |                           | time:1.08ms, loops:2, build_hash_table:{...}, probe:{...}      |.| 25.7 KB   | 0 Bytes |
|         │ ├─IndexReader_39(Build)       |.| 1       | root      |                           | time:888.5µs, loops:2, cop_task: {...}                         |.| 286 Bytes | N/A     |
|         │ │ └─IndexRangeScan_38         |.| 1       | cop[tikv] | table:c, index:name(name) | tikv_task:{time:0s, loops:1}, scan_detail: {...}               |.| N/A       | N/A     |
|         │ └─TableReader_37(Probe)       |.| 10      | root      |                           | time:543.7µs, loops:2, cop_task: {...}                         |.| 577 Bytes | N/A     |
|         │   └─TableFullScan_36          |.| 10      | cop[tikv] | table:p                   | tikv_task:{time:0s, loops:1}, scan_detail: {...}               |.| N/A       | N/A     |
|         └─TableReader_22(Probe)         |.| 28      | root      |                           | time:671.7µs, loops:2, cop_task: {...}                         |.| 876 Bytes | N/A     |
|           └─TableFullScan_21            |.| 28      | cop[tikv] | table:m                   | tikv_task:{time:0s, loops:1}, scan_detail: {...}               |.| N/A       | N/A     |
+-----------------------------------------+.+---------+-----------+---------------------------+----------------------------------------------------------------+.+-----------+---------+
```
