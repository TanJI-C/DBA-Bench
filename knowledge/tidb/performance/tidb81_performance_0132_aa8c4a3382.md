# Partition pruning applicability and limitations

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Partition pruning > Some cases for partition pruning to take effect`
- Source Line Ranges: `1247-1346`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `partition-pruning`, `query-optimization`, `predicate-pushdown`, `range-partitioning`, `hash-partitioning`, `key-partitioning`, `monotonic-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0132_aa8c4a3382`
- Source ID: `tidb-docs-8.1:partitioned-table.md#some-cases-for-partition-pruning-to-take-effect`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66e67ddfc78db283bd6b6af33eb9d3514f50d0de40f21d255f8ae7cac1154b47`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#some-cases-for-partition-pruning-to-take-effect
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing why partition pruning does or does not take effect for a partitioned table query under specific query shapes, pushdown behavior, or partition types.
- Retrieval Keywords: partition pruning, cannot be pushed down, planner's optimization rules, left join converted to inner join, t1.x > 5, execution phase, subquery, Selection node, TiKV coprocessor, predicate push-down, Hash partition, Key partition, equal condition, Range partition, fn(col), monotonous functions, UNIX_TIMESTAMP(), TO_DAYS(), floor(unix_timestamp())
- Follow-up Guidance: The source also lists the supported partition expression forms and examples for `col`, `fn(col)`, `TO_DAYS()`, and `floor(unix_timestamp())` in Range partition pruning.
- Classification Note: This is classified as performance content because it explains optimizer conditions and implementation limits that determine whether partition pruning can reduce scanned partitions.

## Official Source Content

### Some cases for partition pruning to take effect

1. Partition pruning uses the query conditions on the partitioned table, so if the query conditions cannot be pushed down to the partitioned table according to the planner's optimization rules, partition pruning does not apply for this query.

    For example:

    ```sql
    create table t1 (x int) partition by range (x) (
            partition p0 values less than (5),
            partition p1 values less than (10));
    create table t2 (x int);
    ```

    ```sql
    explain select * from t1 left join t2 on t1.x = t2.x where t2.x > 5;
    ```

    In this query, the left out join is converted to the inner join, and then `t1.x > 5` is derived from `t1.x = t2.x` and `t2.x > 5`, so it could be used in partition pruning and only the partition `p1` remains.

    ```sql
    explain select * from t1 left join t2 on t1.x = t2.x and t2.x > 5;
    ```

    In this query, `t2.x > 5` cannot be pushed down to the `t1` partitioned table, so partition pruning would not take effect for this query.

2. Since partition pruning is done during the plan optimizing phase, it does not apply for those cases that filter conditions are unknown until the execution phase.

    For example:

    ```sql
    create table t1 (x int) partition by range (x) (
            partition p0 values less than (5),
            partition p1 values less than (10));
    ```

    ```sql
    explain select * from t2 where x < (select * from t1 where t2.x < t1.x and t2.x < 2);
    ```

    This query reads a row from `t2` and uses the result for the subquery on `t1`. Theoretically, partition pruning could benefit from `t1.x > val` expression in the subquery, but it does not take effect there as that happens in the execution phase.

3. As a result of a limitation from current implementation, if a query condition cannot be pushed down to TiKV, it cannot be used by the partition pruning.

    Take the `fn(col)` expression as an example. If the TiKV coprocessor supports this `fn` function, `fn(col)` may be pushed down to the leaf node (that is, partitioned table) according to the predicate push-down rule during the plan optimizing phase, and partition pruning can use it.

    If the TiKV coprocessor does not support this `fn` function, `fn(col)` would not be pushed down to the leaf node. Instead, it becomes a `Selection` node above the leaf node. The current partition pruning implementation does not support this kind of plan tree.

4. For Hash and Key partition types, the only query supported by partition pruning is the equal condition.

5. For Range partition, for partition pruning to take effect, the partition expression must be in those forms: `col` or `fn(col)`, and the query condition must be one of `>`, `<`, `=`, `>=`, and `<=`. If the partition expression is in the form of `fn(col)`, the `fn` function must be monotonous.

    If the `fn` function is monotonous, for any `x` and `y`, if `x > y`, then `fn(x) > fn(y)`. Then this `fn` function can be called strictly monotonous. For any `x` and `y`, if `x > y`, then `fn(x) >= fn(y)`. In this case, `fn` could also be called "monotonous". In theory, all monotonous functions are supported by partition pruning.

    Currently, partition pruning in TiDB only support those monotonous functions:

    * [`UNIX_TIMESTAMP()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/date-and-time-functions)
    * [`TO_DAYS()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/date-and-time-functions)

    For example, the partition expression is a simple column:

    ```sql
    create table t (id int) partition by range (id) (
            partition p0 values less than (5),
            partition p1 values less than (10));
    select * from t where id > 6;
    ```

    Or the partition expression is in the form of `fn(col)` where `fn` is `to_days`:

    ```sql
    create table t (dt datetime) partition by range (to_days(id)) (
            partition p0 values less than (to_days('2020-04-01')),
            partition p1 values less than (to_days('2020-05-01')));
    select * from t where dt > '2020-04-18';
    ```

    An exception is `floor(unix_timestamp())` as the partition expression. TiDB does some optimization for that case by case, so it is supported by partition pruning.

    ```sql
    create table t (ts timestamp(3) not null default current_timestamp(3))
    partition by range (floor(unix_timestamp(ts))) (
            partition p0 values less than (unix_timestamp('2020-04-01 00:00:00')),
            partition p1 values less than (unix_timestamp('2020-05-01 00:00:00')));
    select * from t where ts > '2020-04-18 02:00:42.123';
    ```
