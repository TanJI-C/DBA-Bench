# Analyze slow TiDB execution with concurrency and disk spill

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/analyze-slow-queries.md`
- Source Title: `Analyze Slow Queries`
- Source Heading Path: `Analyze Slow Queries > Analyze system issues > TiDB is slow in execution | Analyze Slow Queries > Analyze system issues > TiDB is slow in execution > Low concurrency | Analyze Slow Queries > Analyze system issues > TiDB is slow in execution > Data is spilled to disk`
- Source Line Ranges: `162-213`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `slow-query-analysis`, `execution-plan`, `explain-analyze`, `concurrency`, `hash-join`, `system-variables`, `disk-spill`, `memory-limit`, `slow-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0005_7add016788`
- Source ID: `tidb-docs-8.1:analyze-slow-queries.md#tidb-is-slow-in-execution`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cf63766c7b8847455507f9d3ce67f6c40b0d29b7083ec792bdd50e699a4697c8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/analyze-slow-queries#tidb-is-slow-in-execution
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/analyze-slow-queries.md

## Retrieval Guidance

- Use When: Use this when `EXPLAIN ANALYZE` shows slow TiDB execution caused by low concurrency or by disk spill during execution.
- Retrieval Keywords: TiDB is slow in execution, Low concurrency, Data is spilled to disk, EXPLAIN ANALYZE, tidb_hash_join_concurrency, HashJoin_14, Projection_24, disk spill, memory limit, slow log
- Follow-up Guidance: The content points to increasing concurrency for operators such as `HashJoin_14` by adjusting `tidb_hash_join_concurrency`, and it also shows disk spill in both the execution plan and slow log.
- Classification Note: This chunk classifies a TiDB execution diagnosis that covers low-concurrency operators and execution-time disk spill.

## Official Source Content

### TiDB is slow in execution

Assume that the execution plan in TiDB is correct but the execution is slow. To solve this type of issue, you can adjust parameters or use the hint according to the result of `EXPLAIN ANALYZE` for the SQL statement.

If the execution plan is incorrect, see the [Analyze optimizer issues](#analyze-optimizer-issues) section.
#### Low concurrency

If the bottleneck is in the operator with concurrency, speed up the execution by adjusting the concurrency. For example:

```sql
mysql> explain analyze select sum(t1.a) from t t1, t t2 where t1.a=t2.a;
+----------------------------------+--------------+-----------+-----------+---------------+-------------------------------------------------------------------------------------+------------------------------------------------+------------------+---------+
| id                               | estRows      | actRows   | task      | access object | execution info                                                                      | operator info                                  | memory           | disk    |
+----------------------------------+--------------+-----------+-----------+---------------+-------------------------------------------------------------------------------------+------------------------------------------------+------------------+---------+
| HashAgg_11                       | 1.00         | 1         | root      |               | time:9.666832189s, loops:2, PartialConcurrency:4, FinalConcurrency:4                | funcs:sum(Column#6)->Column#5                  | 322.125 KB       | N/A     |
| └─Projection_24                  | 268435456.00 | 268435456 | root      |               | time:9.098644711s, loops:262145, Concurrency:4                                      | cast(test.t.a, decimal(65,0) BINARY)->Column#6 | 199 KB           | N/A     |
|   └─HashJoin_14                  | 268435456.00 | 268435456 | root      |               | time:6.616773501s, loops:262145, Concurrency:5, probe collision:0, build:881.404µs  | inner join, equal:[eq(test.t.a, test.t.a)]     | 131.75 KB        | 0 Bytes |
|     ├─TableReader_21(Build)      | 16384.00     | 16384     | root      |               | time:6.553717ms, loops:17                                                           | data:Selection_20                              | 33.6318359375 KB | N/A     |
|     │ └─Selection_20             | 16384.00     |           | cop[tikv] |               | time:0ns, loops:0                                                                   | not(isnull(test.t.a))                          | N/A              | N/A     |
|     │   └─TableFullScan_19       | 16384.00     | -1        | cop[tikv] | table:t2      | time:0s, loops:0                                                                    | keep order:false                               | N/A              | N/A     |
|     └─TableReader_18(Probe)      | 16384.00     | 16384     | root      |               | time:6.880923ms, loops:17                                                           | data:Selection_17                              | 33.6318359375 KB | N/A     |
|       └─Selection_17             | 16384.00     |           | cop[tikv] |               | time:0ns, loops:0                                                                   | not(isnull(test.t.a))                          | N/A              | N/A     |
|         └─TableFullScan_16       | 16384.00     | -1        | cop[tikv] | table:t1      | time:0s, loops:0                                                                    | keep order:false                               | N/A              | N/A     |
+----------------------------------+--------------+-----------+-----------+---------------+-------------------------------------------------------------------------------------+------------------------------------------------+------------------+---------+
9 rows in set (9.67 sec)
```

As shown above, `HashJoin_14` and `Projection_24` consume much of the execution time. Consider increasing their concurrency using SQL variables to speed up execution.

All system variables are documented in [system-variables](https://docs.pingcap.com/tidb/stable/system-variables). To increase the concurrency of `HashJoin_14`, you can modify the `tidb_hash_join_concurrency` system variable.
#### Data is spilled to disk

Another cause of slow execution is disk spill that occurs during execution if the memory limit is reached. You can find out this cause in the execution plan and the slow log:

```sql
+-------------------------+-----------+---------+-----------+---------------+------------------------------+----------------------+-----------------------+----------------+
| id                      | estRows   | actRows | task      | access object | execution info               | operator info        | memory                | disk           |
+-------------------------+-----------+---------+-----------+---------------+------------------------------+----------------------+-----------------------+----------------+
| Sort_4                  | 462144.00 | 462144  | root      |               | time:2.02848898s, loops:453  | test.t.a             | 149.68795776367188 MB | 219.3203125 MB |
| └─TableReader_8         | 462144.00 | 462144  | root      |               | time:616.211272ms, loops:453 | data:TableFullScan_7 | 197.49601364135742 MB | N/A            |
|   └─TableFullScan_7     | 462144.00 | -1      | cop[tikv] | table:t       | time:0s, loops:0             | keep order:false     | N/A                   | N/A            |
+-------------------------+-----------+---------+-----------+---------------+------------------------------+----------------------+-----------------------+----------------+
```

```
...
# Disk_max: 229974016
...
```
