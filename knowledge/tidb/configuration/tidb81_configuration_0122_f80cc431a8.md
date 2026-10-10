# Dynamic pruning mode and GlobalStats behavior

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Restrictions and limitations on partitions > Dynamic pruning mode`
- Source Line Ranges: `1819-1938`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `partitioning`, `dynamic-pruning`, `static-pruning`, `globalstats`, `analyze`, `statistics`, `session-variables`, `global-variables`, `query-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0122_f80cc431a8`
- Source ID: `tidb-docs-8.1:partitioned-table.md#dynamic-pruning-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `583d3fbc043406b2ce7e8c8163ba2befbf78755d79a93eae86f4648ab4d7980a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when you need information about `tidb_partition_prune_mode`, the difference between `dynamic` and `static` access for partitioned tables, and how GlobalStats affects query plans and analyze behavior.
- Retrieval Keywords: tidb_partition_prune_mode, dynamic pruning mode, static mode, GlobalStats, auto-analyze, manual ANALYZE, set @@session.tidb_partition_prune_mode = 'dynamic', set global tidb_partition_prune_mode = dynamic, show stats_meta where table_name like "t", analyze table t partition p1, partition-level statistics, table-level statistics, global stats failed due to missing partition-level column stats, Warning 8244, PartitionUnion, partition:p0,p1, Collect statistics of partitioned tables in dynamic pruning mode
- Follow-up Guidance: If `analyze` shows warning `8244` about missing partition-level column stats, the content says partition statistics are inconsistent and statistics need to be collected again for those partitions or the entire table.
- Classification Note: This is classified as configuration content because it centers on the session-level and global `tidb_partition_prune_mode` setting and explains how that setting changes statistics usage and partitioned-table execution plans.

## Official Source Content

### Dynamic pruning mode

TiDB accesses partitioned tables in either `dynamic` or `static` mode. `dynamic` mode is used by default since v6.3.0. However, dynamic partitioning is effective only after the full table-level statistics, or GlobalStats, are collected. Before GlobalStats are collected, TiDB will use the `static` mode instead. For detailed information about GlobalStats, see [Collect statistics of partitioned tables in dynamic pruning mode](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics-of-partitioned-tables-in-dynamic-pruning-mode).

```sql
set @@session.tidb_partition_prune_mode = 'dynamic'
```

Manual ANALYZE and normal queries use the session-level `tidb_partition_prune_mode` setting. The `auto-analyze` operation in the background uses the global `tidb_partition_prune_mode` setting.

In `static` mode, partitioned tables use partition-level statistics. In `dynamic` mode, partitioned tables use table-level GlobalStats.

When switching from `static` mode to `dynamic` mode, you need to check and collect statistics manually. This is because after the switch to `dynamic` mode, partitioned tables have only partition-level statistics but no table-level statistics. GlobalStats are collected only upon the next `auto-analyze` operation.

```sql
set session tidb_partition_prune_mode = 'dynamic';
show stats_meta where table_name like "t";
```

```
+---------+------------+----------------+---------------------+--------------+-----------+
| Db_name | Table_name | Partition_name | Update_time         | Modify_count | Row_count |
+---------+------------+----------------+---------------------+--------------+-----------+
| test    | t          | p0             | 2022-05-27 20:23:34 |            1 |         2 |
| test    | t          | p1             | 2022-05-27 20:23:34 |            2 |         4 |
| test    | t          | p2             | 2022-05-27 20:23:34 |            2 |         4 |
+---------+------------+----------------+---------------------+--------------+-----------+
3 rows in set (0.01 sec)
```

To make sure that the statistics used by SQL statements are correct after you enable global `dynamic` pruning mode, you need to manually trigger `analyze` on the tables or on a partition of the table to obtain GlobalStats.

```sql
analyze table t partition p1;
show stats_meta where table_name like "t";
```

```
+---------+------------+----------------+---------------------+--------------+-----------+
| Db_name | Table_name | Partition_name | Update_time         | Modify_count | Row_count |
+---------+------------+----------------+---------------------+--------------+-----------+
| test    | t          | global         | 2022-05-27 20:50:53 |            0 |         5 |
| test    | t          | p0             | 2022-05-27 20:23:34 |            1 |         2 |
| test    | t          | p1             | 2022-05-27 20:50:52 |            0 |         2 |
| test    | t          | p2             | 2022-05-27 20:50:08 |            0 |         2 |
+---------+------------+----------------+---------------------+--------------+-----------+
4 rows in set (0.00 sec)
```

If the following warning is displayed during the `analyze` process, partition statistics are inconsistent, and you need to collect statistics of these partitions or the entire table again.

```
| Warning | 8244 | Build table: `t` column: `a` global-level stats failed due to missing partition-level column stats, please run analyze table to refresh columns of all partitions
```

You can also use scripts to update statistics of all partitioned tables. For details, see [Update statistics of partitioned tables in dynamic pruning mode](#update-statistics-of-partitioned-tables-in-dynamic-pruning-mode).

After table-level statistics are ready, you can enable the global dynamic pruning mode, which is effective to all SQL statements and `auto-analyze` operations.

```sql
set global tidb_partition_prune_mode = dynamic
```

In `static` mode, TiDB accesses each partition separately using multiple operators, and then merges the results using `Union`. The following example is a simple read operation where TiDB merges the results of two corresponding partitions using `Union`:

```sql
mysql> create table t1(id int, age int, key(id)) partition by range(id) (
        partition p0 values less than (100),
        partition p1 values less than (200),
        partition p2 values less than (300),
        partition p3 values less than (400));
Query OK, 0 rows affected (0.01 sec)

mysql> explain select * from t1 where id < 150;
```

```
+------------------------------+----------+-----------+------------------------+--------------------------------+
| id                           | estRows  | task      | access object          | operator info                  |
+------------------------------+----------+-----------+------------------------+--------------------------------+
| PartitionUnion_9             | 6646.67  | root      |                        |                                |
| ├─TableReader_12             | 3323.33  | root      |                        | data:Selection_11              |
| │ └─Selection_11             | 3323.33  | cop[tikv] |                        | lt(test.t1.id, 150)            |
| │   └─TableFullScan_10       | 10000.00 | cop[tikv] | table:t1, partition:p0 | keep order:false, stats:pseudo |
| └─TableReader_18             | 3323.33  | root      |                        | data:Selection_17              |
|   └─Selection_17             | 3323.33  | cop[tikv] |                        | lt(test.t1.id, 150)            |
|     └─TableFullScan_16       | 10000.00 | cop[tikv] | table:t1, partition:p1 | keep order:false, stats:pseudo |
+------------------------------+----------+-----------+------------------------+--------------------------------+
7 rows in set (0.00 sec)
```

In `dynamic` mode, each operator supports direct access to multiple partitions, so TiDB no longer uses `Union`.

```sql
mysql> set @@session.tidb_partition_prune_mode = 'dynamic';
Query OK, 0 rows affected (0.00 sec)

mysql> explain select * from t1 where id < 150;
+-------------------------+----------+-----------+-----------------+--------------------------------+
| id                      | estRows  | task      | access object   | operator info                  |
+-------------------------+----------+-----------+-----------------+--------------------------------+
| TableReader_7           | 3323.33  | root      | partition:p0,p1 | data:Selection_6               |
| └─Selection_6           | 3323.33  | cop[tikv] |                 | lt(test.t1.id, 150)            |
|   └─TableFullScan_5     | 10000.00 | cop[tikv] | table:t1        | keep order:false, stats:pseudo |
+-------------------------+----------+-----------+-----------------+--------------------------------+
3 rows in set (0.00 sec)
```
