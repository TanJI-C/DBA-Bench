# Hash partition pruning inapplicable scenarios

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partition-pruning.md`
- Source Title: `Partition Pruning`
- Source Heading Path: `Partition Pruning > Usage scenarios of partition pruning > Use partition pruning in Hash partitioned tables > Inapplicable scenarios in Hash partitioned tables | Partition Pruning > Usage scenarios of partition pruning > Use partition pruning in Hash partitioned tables > Inapplicable scenarios in Hash partitioned tables > Scenario one | Partition Pruning > Usage scenarios of partition pruning > Use partition pruning in Hash partitioned tables > Inapplicable scenarios in Hash partitioned tables > Scenario two`
- Source Line Ranges: `73-143`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `partition-pruning`, `hash-partitioning`, `query-planning`, `execution-plan`, `predicate-limitations`, `subquery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0127_43deb39c69`
- Source ID: `tidb-docs-8.1:partition-pruning.md#inapplicable-scenarios-in-hash-partitioned-tables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e79245978041a8fff5c7d8a6cb5148509f0c155fda0ebb95904ed9dbaf5b34bc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partition-pruning#inapplicable-scenarios-in-hash-partitioned-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partition-pruning.md

## Retrieval Guidance

- Use When: Use this chunk when checking why partition pruning does not apply to Hash partitioned tables for non-equality predicates or for filter conditions that are only known during query execution.
- Retrieval Keywords: Inapplicable scenarios in Hash partitioned tables, partition pruning inapplicable, x > 2, in, between, >, <, >=, <=, Union_10, table:t, partition:p0, table:t, partition:p1, table:t, partition:p2, table:t, partition:p3, rule optimization, generation phase of the query plan, execution phase, Apply_15, subquery, x = (select * from t1 where t2.x = t1.x and t2.x < 2)
- Follow-up Guidance: The chunk distinguishes two reasons: the Hash partition cannot be confirmed from predicates like x > 2, and partition pruning is done during query plan generation rather than during execution.
- Classification Note: This is classified as performance because the official content describes limitations of the partition pruning optimization in query planning and execution plans.

## Official Source Content

#### Inapplicable scenarios in Hash partitioned tables

This section describes two inapplicable usage scenarios of partition pruning in Hash partitioned tables.
##### Scenario one

If you cannot confirm the condition that the query result falls in only one partition (such as `in`, `between`, `>`, `<`, `>=`, `<=`), you cannot use the partition pruning optimization. For example:

```sql
create table t (x int) partition by hash(x) partitions 4;
explain select * from t where x > 2;
```

```sql
+------------------------------+----------+-----------+-----------------------+--------------------------------+
| id                           | estRows  | task      | access object         | operator info                  |
+------------------------------+----------+-----------+-----------------------+--------------------------------+
| Union_10                     | 13333.33 | root      |                       |                                |
| ├─TableReader_13             | 3333.33  | root      |                       | data:Selection_12              |
| │ └─Selection_12             | 3333.33  | cop[tikv] |                       | gt(test.t.x, 2)                |
| │   └─TableFullScan_11       | 10000.00 | cop[tikv] | table:t, partition:p0 | keep order:false, stats:pseudo |
| ├─TableReader_16             | 3333.33  | root      |                       | data:Selection_15              |
| │ └─Selection_15             | 3333.33  | cop[tikv] |                       | gt(test.t.x, 2)                |
| │   └─TableFullScan_14       | 10000.00 | cop[tikv] | table:t, partition:p1 | keep order:false, stats:pseudo |
| ├─TableReader_19             | 3333.33  | root      |                       | data:Selection_18              |
| │ └─Selection_18             | 3333.33  | cop[tikv] |                       | gt(test.t.x, 2)                |
| │   └─TableFullScan_17       | 10000.00 | cop[tikv] | table:t, partition:p2 | keep order:false, stats:pseudo |
| └─TableReader_22             | 3333.33  | root      |                       | data:Selection_21              |
|   └─Selection_21             | 3333.33  | cop[tikv] |                       | gt(test.t.x, 2)                |
|     └─TableFullScan_20       | 10000.00 | cop[tikv] | table:t, partition:p3 | keep order:false, stats:pseudo |
+------------------------------+----------+-----------+-----------------------+--------------------------------+
```

In this case, partition pruning is inapplicable because the corresponding Hash partition cannot be confirmed by the `x > 2` condition.
##### Scenario two

Because the rule optimization of partition pruning is performed during the generation phase of the query plan, partition pruning is not suitable for scenarios where the filter conditions can be obtained only during the execution phase. For example:

```sql
create table t (x int) partition by hash(x) partitions 4;
explain select * from t2 where x = (select * from t1 where t2.x = t1.x and t2.x < 2);
```

```sql
+--------------------------------------+----------+-----------+------------------------+----------------------------------------------+
| id                                   | estRows  | task      | access object          | operator info                                |
+--------------------------------------+----------+-----------+------------------------+----------------------------------------------+
| Projection_13                        | 9990.00  | root      |                        | test.t2.x                                    |
| └─Apply_15                           | 9990.00  | root      |                        | inner join, equal:[eq(test.t2.x, test.t1.x)] |
|   ├─TableReader_18(Build)            | 9990.00  | root      |                        | data:Selection_17                            |
|   │ └─Selection_17                   | 9990.00  | cop[tikv] |                        | not(isnull(test.t2.x))                       |
|   │   └─TableFullScan_16             | 10000.00 | cop[tikv] | table:t2               | keep order:false, stats:pseudo               |
|   └─Selection_19(Probe)              | 0.80     | root      |                        | not(isnull(test.t1.x))                       |
|     └─MaxOneRow_20                   | 1.00     | root      |                        |                                              |
|       └─Union_21                     | 2.00     | root      |                        |                                              |
|         ├─TableReader_24             | 2.00     | root      |                        | data:Selection_23                            |
|         │ └─Selection_23             | 2.00     | cop[tikv] |                        | eq(test.t2.x, test.t1.x), lt(test.t2.x, 2)   |
|         │   └─TableFullScan_22       | 2500.00  | cop[tikv] | table:t1, partition:p0 | keep order:false, stats:pseudo               |
|         └─TableReader_27             | 2.00     | root      |                        | data:Selection_26                            |
|           └─Selection_26             | 2.00     | cop[tikv] |                        | eq(test.t2.x, test.t1.x), lt(test.t2.x, 2)   |
|             └─TableFullScan_25       | 2500.00  | cop[tikv] | table:t1, partition:p1 | keep order:false, stats:pseudo               |
+--------------------------------------+----------+-----------+------------------------+----------------------------------------------+
```

Each time this query reads a row from `t2`, it will query on the `t1` partitioned table. Theoretically, the filter condition of `t1.x = val` is met at this time, but in fact, partition pruning takes effect only in the generation phase of the query plan, not the execution phase.
