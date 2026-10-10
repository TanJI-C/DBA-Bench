# Range partition pruning applicable scenarios

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partition-pruning.md`
- Source Title: `Partition Pruning`
- Source Heading Path: `Partition Pruning > Usage scenarios of partition pruning > Use partition pruning in Range partitioned tables > Applicable scenarios in Range partitioned tables > Scenario one | Partition Pruning > Usage scenarios of partition pruning > Use partition pruning in Range partitioned tables > Applicable scenarios in Range partitioned tables > Scenario two | Partition Pruning > Usage scenarios of partition pruning > Use partition pruning in Range partitioned tables > Applicable scenarios in Range partitioned tables > Scenario three`
- Source Line Ranges: `152-264`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `partition-pruning`, `range-partitioning`, `query-optimization`, `equality-predicates`, `in-predicates`, `interval-comparison`, `monotonic-functions`, `explain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0129_2bbbbf1274`
- Source ID: `tidb-docs-8.1:partition-pruning.md#scenario-one`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5de3038f34037844554e1f6ee67ddefe334472058eb0c4537a760535a5a25bd1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partition-pruning#scenario-one
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partition-pruning.md

## Retrieval Guidance

- Use When: Use this chunk when identifying whether partition pruning applies to Range partitioned tables for equality, IN, interval comparison, or simple monotonic function partition expressions and verifying the pruned partitions with EXPLAIN.
- Retrieval Keywords: partition pruning, Range partitioned tables, equality comparison, x = 3, in query condition, x in(1,13), interval comparison, between, >, <, =, >=, <=, partition expression fn(col), monotonous function, UNIX_TIMESTAMP(), TO_DAYS(), to_days(id), explain select * from t where x between 7 and 14, table:t, partition:p0, table:t, partition:p1, table:t, partition:p2, cop[tikv], TableFullScan
- Follow-up Guidance: The EXPLAIN examples show which partitions are accessed, such as only p0 for x = 3, p0 and p2 for x in(1,13), p1 and p2 for x between 7 and 14, and only p1 for the to_days(id) example.
- Classification Note: This is classified as performance for TiDB because the content explains query optimization through partition pruning in SQL plans and shows reduced partition access in EXPLAIN output.

## Official Source Content

##### Scenario one

Partition pruning applies to the query condition of equality comparison in Range partitioned tables. For example:

```sql
create table t (x int) partition by range (x) (
    partition p0 values less than (5),
    partition p1 values less than (10),
    partition p2 values less than (15)
    );
explain select * from t where x = 3;
```

```sql
+-------------------------+----------+-----------+-----------------------+--------------------------------+
| id                      | estRows  | task      | access object         | operator info                  |
+-------------------------+----------+-----------+-----------------------+--------------------------------+
| TableReader_8           | 10.00    | root      |                       | data:Selection_7               |
| └─Selection_7           | 10.00    | cop[tikv] |                       | eq(test.t.x, 3)                |
|   └─TableFullScan_6     | 10000.00 | cop[tikv] | table:t, partition:p0 | keep order:false, stats:pseudo |
+-------------------------+----------+-----------+-----------------------+--------------------------------+
```

Partition pruning also applies to the equality comparison that uses the `in` query condition. For example:

```sql
create table t (x int) partition by range (x) (
    partition p0 values less than (5),
    partition p1 values less than (10),
    partition p2 values less than (15)
    );
explain select * from t where x in(1,13);
```

```sql
+-----------------------------+----------+-----------+-----------------------+--------------------------------+
| id                          | estRows  | task      | access object         | operator info                  |
+-----------------------------+----------+-----------+-----------------------+--------------------------------+
| Union_8                     | 40.00    | root      |                       |                                |
| ├─TableReader_11            | 20.00    | root      |                       | data:Selection_10              |
| │ └─Selection_10            | 20.00    | cop[tikv] |                       | in(test.t.x, 1, 13)            |
| │   └─TableFullScan_9       | 10000.00 | cop[tikv] | table:t, partition:p0 | keep order:false, stats:pseudo |
| └─TableReader_14            | 20.00    | root      |                       | data:Selection_13              |
|   └─Selection_13            | 20.00    | cop[tikv] |                       | in(test.t.x, 1, 13)            |
|     └─TableFullScan_12      | 10000.00 | cop[tikv] | table:t, partition:p2 | keep order:false, stats:pseudo |
+-----------------------------+----------+-----------+-----------------------+--------------------------------+
```

In the SQL statement above, it can be known from the `x in(1,13)` condition that all results fall in a few partitions. After analysis, it is found that all records of `x = 1` are in the `p0` partition, and all records of `x = 13` are in the `p2` partition, so only `p0` and `p2` partitions need to be accessed.
##### Scenario two

Partition pruning applies to the query condition of interval comparison, such as `between`, `>`, `<`, `=`, `>=`, `<=`. For example:

```sql
create table t (x int) partition by range (x) (
    partition p0 values less than (5),
    partition p1 values less than (10),
    partition p2 values less than (15)
    );
explain select * from t where x between 7 and 14;
```

```sql
+-----------------------------+----------+-----------+-----------------------+-----------------------------------+
| id                          | estRows  | task      | access object         | operator info                     |
+-----------------------------+----------+-----------+-----------------------+-----------------------------------+
| Union_8                     | 500.00   | root      |                       |                                   |
| ├─TableReader_11            | 250.00   | root      |                       | data:Selection_10                 |
| │ └─Selection_10            | 250.00   | cop[tikv] |                       | ge(test.t.x, 7), le(test.t.x, 14) |
| │   └─TableFullScan_9       | 10000.00 | cop[tikv] | table:t, partition:p1 | keep order:false, stats:pseudo    |
| └─TableReader_14            | 250.00   | root      |                       | data:Selection_13                 |
|   └─Selection_13            | 250.00   | cop[tikv] |                       | ge(test.t.x, 7), le(test.t.x, 14) |
|     └─TableFullScan_12      | 10000.00 | cop[tikv] | table:t, partition:p2 | keep order:false, stats:pseudo    |
+-----------------------------+----------+-----------+-----------------------+-----------------------------------+
```
##### Scenario three

Partition pruning applies to the scenario where the partition expression is in the simple form of `fn(col)`, the query condition is one of `>`, `<`, `=`, `>=`, and `<=`, and the `fn` function is monotonous.

If the `fn` function is monotonous, for any `x` and `y`, if `x > y`, then `fn(x) > fn(y)`. Then this `fn` function can be called strictly monotonous. For any `x` and `y`, if `x > y`, then `fn(x) >= fn(y)`. In this case, `fn` could also be called "monotonous". Theoretically, all monotonous functions, strictly or not, are supported by partition pruning. Currently, TiDB only supports the following monotonous functions:

* [`UNIX_TIMESTAMP()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/date-and-time-functions)
* [`TO_DAYS()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/date-and-time-functions)

For example, partition pruning takes effect when the partition expression is in the form of `fn(col)`, where the `fn` is monotonous function `to_days`:

```sql
create table t (id datetime) partition by range (to_days(id)) (
    partition p0 values less than (to_days('2020-04-01')),
    partition p1 values less than (to_days('2020-05-01')));
explain select * from t where id > '2020-04-18';
```

```sql
+-------------------------+----------+-----------+-----------------------+-------------------------------------------+
| id                      | estRows  | task      | access object         | operator info                             |
+-------------------------+----------+-----------+-----------------------+-------------------------------------------+
| TableReader_8           | 3333.33  | root      |                       | data:Selection_7                          |
| └─Selection_7           | 3333.33  | cop[tikv] |                       | gt(test.t.id, 2020-04-18 00:00:00.000000) |
|   └─TableFullScan_6     | 10000.00 | cop[tikv] | table:t, partition:p1 | keep order:false, stats:pseudo            |
+-------------------------+----------+-----------+-----------------------+-------------------------------------------+
```
