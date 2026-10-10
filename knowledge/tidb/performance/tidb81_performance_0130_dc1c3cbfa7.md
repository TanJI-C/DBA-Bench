# Range partition pruning inapplicable when filters are only known at execution time

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partition-pruning.md`
- Source Title: `Partition Pruning`
- Source Heading Path: `Partition Pruning > Usage scenarios of partition pruning > Use partition pruning in Range partitioned tables > Inapplicable scenario in Range partitioned tables`
- Source Line Ranges: `265-301`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `partition-pruning`, `range-partitioning`, `query-planning`, `execution-phase`, `subquery`, `explain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0130_dc1c3cbfa7`
- Source ID: `tidb-docs-8.1:partition-pruning.md#inapplicable-scenario-in-range-partitioned-tables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66023d95576c9481a4397f79352f862c3cd43ef405797189f9861cd6b8f95449`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partition-pruning#inapplicable-scenario-in-range-partitioned-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partition-pruning.md

## Retrieval Guidance

- Use When: Use this chunk when explaining why range partition pruning does not apply to a query whose partition filter can be determined only during execution, such as a correlated subquery shown by EXPLAIN scanning multiple partitions.
- Retrieval Keywords: partition pruning, Range partitioned tables, Inapplicable scenario in Range partitioned tables, rule optimization, generation phase of the query plan, execution phase, correlated subquery, explain select * from t2 where x < (select * from t1 where t2.x < t1.x and t2.x < 2), Apply_15, Union_21, table:t1, partition:p0, table:t1, partition:p1, TableFullScan_22, TableFullScan_25
- Follow-up Guidance: The EXPLAIN output shows scans on both `table:t1, partition:p0` and `table:t1, partition:p1` because partition pruning takes effect only in the generation phase of the query plan, not the execution phase.
- Classification Note: This is classified as performance because the official content describes when partition pruning cannot reduce scanned partitions during query planning in TiDB.

## Official Source Content

#### Inapplicable scenario in Range partitioned tables

Because the rule optimization of partition pruning is performed during the generation phase of the query plan, partition pruning is not suitable for scenarios where the filter conditions can be obtained only during the execution phase. For example:

```sql
create table t1 (x int) partition by range (x) (
    partition p0 values less than (5),
    partition p1 values less than (10));
create table t2 (x int);
explain select * from t2 where x < (select * from t1 where t2.x < t1.x and t2.x < 2);
```

```sql
+--------------------------------------+----------+-----------+------------------------+-----------------------------------------------------------+
| id                                   | estRows  | task      | access object          | operator info                                             |
+--------------------------------------+----------+-----------+------------------------+-----------------------------------------------------------+
| Projection_13                        | 9990.00  | root      |                        | test.t2.x                                                 |
| └─Apply_15                           | 9990.00  | root      |                        | CARTESIAN inner join, other cond:lt(test.t2.x, test.t1.x) |
|   ├─TableReader_18(Build)            | 9990.00  | root      |                        | data:Selection_17                                         |
|   │ └─Selection_17                   | 9990.00  | cop[tikv] |                        | not(isnull(test.t2.x))                                    |
|   │   └─TableFullScan_16             | 10000.00 | cop[tikv] | table:t2               | keep order:false, stats:pseudo                            |
|   └─Selection_19(Probe)              | 0.80     | root      |                        | not(isnull(test.t1.x))                                    |
|     └─MaxOneRow_20                   | 1.00     | root      |                        |                                                           |
|       └─Union_21                     | 2.00     | root      |                        |                                                           |
|         ├─TableReader_24             | 2.00     | root      |                        | data:Selection_23                                         |
|         │ └─Selection_23             | 2.00     | cop[tikv] |                        | lt(test.t2.x, 2), lt(test.t2.x, test.t1.x)                |
|         │   └─TableFullScan_22       | 2.50     | cop[tikv] | table:t1, partition:p0 | keep order:false, stats:pseudo                            |
|         └─TableReader_27             | 2.00     | root      |                        | data:Selection_26                                         |
|           └─Selection_26             | 2.00     | cop[tikv] |                        | lt(test.t2.x, 2), lt(test.t2.x, test.t1.x)                |
|             └─TableFullScan_25       | 2.50     | cop[tikv] | table:t1, partition:p1 | keep order:false, stats:pseudo                            |
+--------------------------------------+----------+-----------+------------------------+-----------------------------------------------------------+
14 rows in set (0.00 sec)
```

Each time this query reads a row from `t2`, it will query on the `t1` partitioned table. Theoretically, the `t1.x> val` filter condition is met at this time, but in fact, partition pruning takes effect only in the generation phase of the query plan, not the execution phase.
