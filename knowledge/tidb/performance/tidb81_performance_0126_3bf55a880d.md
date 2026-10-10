# Partition pruning overview and hash applicable equality case

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partition-pruning.md`
- Source Title: `Partition Pruning`
- Source Heading Path: `Partition Pruning | Partition Pruning > Usage scenarios of partition pruning | Partition Pruning > Usage scenarios of partition pruning > Use partition pruning in Hash partitioned tables | Partition Pruning > Usage scenarios of partition pruning > Use partition pruning in Hash partitioned tables > Applicable scenario in Hash partitioned tables`
- Source Line Ranges: `5-72`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `partition-pruning`, `partitioned-tables`, `hash-partitioning`, `range-partitioning`, `query-optimization`, `explain`, `equality-predicate`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0126_3bf55a880d`
- Source ID: `tidb-docs-8.1:partition-pruning.md#partition-pruning`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `20ea233e85405c5083ed94bc4a6adcf62134cc11ec31439cc61162c0c53b75b9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partition-pruning#partition-pruning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partition-pruning.md

## Retrieval Guidance

- Use When: Use this chunk when identifying how partition pruning works in partitioned tables and when checking the applicable equality-comparison case for Hash partitioned tables with EXPLAIN output.
- Retrieval Keywords: Partition Pruning, partition pruning, Hash partitioned tables, Range partitioned tables, equality comparison, x = 1, partition by hash(x) partitions 4, EXPLAIN SELECT * FROM t WHERE x = 1, TableFullScan, table:t, partition:p1, access object, PartitionUnion, TableRangeScan, id BETWEEN 80 AND 120
- Follow-up Guidance: It also shows that pruning can be confirmed from the execution plan when only one TableFullScan appears and the partition such as p1 is specified in access object.
- Classification Note: This is classified as performance because the official content explains partition pruning as a query optimization that reduces accessed data and can significantly improve query execution times.

## Official Source Content

# Partition Pruning

Partition pruning is a performance optimization that applies to partitioned tables. It analyzes the filter conditions in query statements, and eliminates (_prunes_) partitions from consideration when they do not contain any data that will be required. By eliminating the non-required partitions, TiDB is able to reduce the amount of data that needs to be accessed and potentially significantly improving query execution times.

The following is an example:

```sql
CREATE TABLE t1 (
 id INT NOT NULL PRIMARY KEY,
 pad VARCHAR(100)
)
PARTITION BY RANGE COLUMNS(id) (
 PARTITION p0 VALUES LESS THAN (100),
 PARTITION p1 VALUES LESS THAN (200),
 PARTITION p2 VALUES LESS THAN (MAXVALUE)
);

INSERT INTO t1 VALUES (1, 'test1'),(101, 'test2'), (201, 'test3');
EXPLAIN SELECT * FROM t1 WHERE id BETWEEN 80 AND 120;
```

```sql
+----------------------------+---------+-----------+------------------------+------------------------------------------------+
| id                         | estRows | task      | access object          | operator info                                  |
+----------------------------+---------+-----------+------------------------+------------------------------------------------+
| PartitionUnion_8           | 80.00   | root      |                        |                                                |
| ├─TableReader_10           | 40.00   | root      |                        | data:TableRangeScan_9                          |
| │ └─TableRangeScan_9       | 40.00   | cop[tikv] | table:t1, partition:p0 | range:[80,120], keep order:false, stats:pseudo |
| └─TableReader_12           | 40.00   | root      |                        | data:TableRangeScan_11                         |
|   └─TableRangeScan_11      | 40.00   | cop[tikv] | table:t1, partition:p1 | range:[80,120], keep order:false, stats:pseudo |
+----------------------------+---------+-----------+------------------------+------------------------------------------------+
5 rows in set (0.00 sec)
```
## Usage scenarios of partition pruning

The usage scenarios of partition pruning are different for the two types of partitioned tables: Range partitioned tables and Hash partitioned tables.
### Use partition pruning in Hash partitioned tables

This section describes the applicable and inapplicable usage scenarios of partition pruning in Hash partitioned tables.
#### Applicable scenario in Hash partitioned tables

Partition pruning applies only to the query condition of equality comparison in Hash partitioned tables.

```sql
create table t (x int) partition by hash(x) partitions 4;
explain select * from t where x = 1;
```

```sql
+-------------------------+----------+-----------+-----------------------+--------------------------------+
| id                      | estRows  | task      | access object         | operator info                  |
+-------------------------+----------+-----------+-----------------------+--------------------------------+
| TableReader_8           | 10.00    | root      |                       | data:Selection_7               |
| └─Selection_7           | 10.00    | cop[tikv] |                       | eq(test.t.x, 1)                |
|   └─TableFullScan_6     | 10000.00 | cop[tikv] | table:t, partition:p1 | keep order:false, stats:pseudo |
+-------------------------+----------+-----------+-----------------------+--------------------------------+
```

In the SQL statement above, it can be known from the condition `x = 1` that all results fall in one partition. The value `1` can be confirmed to be in the `p1` partition after passing through the Hash partition. Therefore, only the `p1` partition needs to be scanned, and there is no need to access the `p2`, `p3`, and `p4` partitions that will not have matching results. From the execution plan, only one `TableFullScan` operator appears and the `p1` partition is specified in `access object`, so it can be confirmed that `partition pruning` takes effect.
