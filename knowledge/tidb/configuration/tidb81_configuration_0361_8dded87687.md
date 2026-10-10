# TiDB methods for reading TiFlash replicas

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/use-tidb-to-read-tiflash.md`
- Source Title: `Use TiDB to Read TiFlash Replicas`
- Source Heading Path: `Use TiDB to Read TiFlash Replicas | Use TiDB to Read TiFlash Replicas > Smart selection | Use TiDB to Read TiFlash Replicas > Engine isolation | Use TiDB to Read TiFlash Replicas > Manual hint | Use TiDB to Read TiFlash Replicas > The relationship of smart selection, engine isolation, and manual hint`
- Source Line Ranges: `5-149`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `dashboard`, `sql`
- Topic Tags: `tiflash-replica`, `smart-selection`, `cost-based-optimization`, `engine-isolation`, `session-variable`, `instance-configuration`, `manual-hint`, `read-from-storage`, `query-plans`, `non-read-only-statements`, `version-dependent-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0361_8dded87687`
- Source ID: `tidb-docs-8.1:tiflash/use-tidb-to-read-tiflash.md#use-tidb-to-read-tiflash-replicas`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7a4545e7a54f819fcb05c4d91d903f14b10b7f5736589df84a83b85ef50dbd7f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/use-tidb-to-read-tiflash#use-tidb-to-read-tiflash-replicas
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/use-tidb-to-read-tiflash.md

## Retrieval Guidance

- Use When: Use this content when determining how TiDB reads TiFlash replicas, how to verify `cop[tiflash]` in `desc` or `explain analyze`, or how `tidb_isolation_read_engines` and `READ_FROM_STORAGE` interact.
- Retrieval Keywords: TiDB read TiFlash replicas, smart selection, CBO cost-based optimization, cop[tiflash], desc select count(*) from test.t, explain analyze, analyze table, engine isolation, tidb_isolation_read_engines, [isolation-read] engines, INSTANCE level, SESSION level, set @@session.tidb_isolation_read_engines, set SESSION tidb_isolation_read_engines, read_from_storage(tiflash[table_name]), read_from_storage(tikv[table_name]), READ_FROM_STORAGE, TiDB Dashboard, system tables, tidb engine, non-read-only SQL statement, INSERT INTO ... SELECT, SELECT ... FOR UPDATE, UPDATE, DELETE, tidb_enable_tiflash_read_for_write_stmt, sql_mode, STRICT_TRANS_TABLES, STRICT_ALL_TABLES
- Follow-up Guidance: The content also describes how smart selection, engine isolation, and manual hint relate, including error or warning behavior when the specified engine is unavailable or not in the engine isolation list.
- Classification Note: This chunk is classified as configuration because it defines instance-level and session-level engine settings, the `tidb_isolation_read_engines` variable, and SQL hint usage that control whether queries read TiFlash, TiKV, or TiDB engines.

## Official Source Content

# Use TiDB to Read TiFlash Replicas

This document introduces how to use TiDB to read TiFlash replicas.

TiDB provides three ways to read TiFlash replicas. If you have added a TiFlash replica without any engine configuration, the CBO (cost-based optimization) mode is used by default.
## Smart selection

For tables with TiFlash replicas, the TiDB optimizer automatically determines whether to use TiFlash replicas based on the cost estimation. You can use the `desc` or `explain analyze` statement to check whether or not a TiFlash replica is selected. For example:

```sql
desc select count(*) from test.t;
```

```
+--------------------------+---------+--------------+---------------+--------------------------------+
| id                       | estRows | task         | access object | operator info                  |
+--------------------------+---------+--------------+---------------+--------------------------------+
| StreamAgg_9              | 1.00    | root         |               | funcs:count(1)->Column#4       |
| └─TableReader_17         | 1.00    | root         |               | data:TableFullScan_16          |
|   └─TableFullScan_16     | 1.00    | cop[tiflash] | table:t       | keep order:false, stats:pseudo |
+--------------------------+---------+--------------+---------------+--------------------------------+
3 rows in set (0.00 sec)
```

```sql
explain analyze select count(*) from test.t;
```

```
+--------------------------+---------+---------+--------------+---------------+----------------------------------------------------------------------+--------------------------------+-----------+------+
| id                       | estRows | actRows | task         | access object | execution info                                                       | operator info                  | memory    | disk |
+--------------------------+---------+---------+--------------+---------------+----------------------------------------------------------------------+--------------------------------+-----------+------+
| StreamAgg_9              | 1.00    | 1       | root         |               | time:83.8372ms, loops:2                                              | funcs:count(1)->Column#4       | 372 Bytes | N/A  |
| └─TableReader_17         | 1.00    | 1       | root         |               | time:83.7776ms, loops:2, rpc num: 1, rpc time:83.5701ms, proc keys:0 | data:TableFullScan_16          | 152 Bytes | N/A  |
|   └─TableFullScan_16     | 1.00    | 1       | cop[tiflash] | table:t       | tiflash_task:{time:43ms, loops:1, threads:1}, tiflash_scan:{...}     | keep order:false, stats:pseudo | N/A       | N/A  |
+--------------------------+---------+---------+--------------+---------------+----------------------------------------------------------------------+--------------------------------+-----------+------+
```

`cop[tiflash]` means that the task will be sent to TiFlash for processing. If you have not selected a TiFlash replica, you can try to update the statistics using the `analyze table` statement, and then check the result using the `explain analyze` statement.

Note that if a table has only a single TiFlash replica and the related node cannot provide service, queries in the CBO mode will repeatedly retry. In this situation, you need to specify the engine or use the manual hint to read data from the TiKV replica.
## Engine isolation

Engine isolation is to specify that all queries use a replica of the specified engine by configuring the corresponding variable. The optional engines are "tikv", "tidb" (indicates the internal memory table area of TiDB, which stores some TiDB system tables and cannot be actively used by users), and "tiflash".

You can specify the engines at the following two configuration levels:

* TiDB instance-level, namely, INSTANCE level. Add the following configuration item in the TiDB configuration file:

    ```
    [isolation-read]
    engines = ["tikv", "tidb", "tiflash"]
    ```

    **The INSTANCE-level default configuration is `["tikv", "tidb", "tiflash"]`.**

* SESSION level. Use the following statement to configure:

    ```sql
    set @@session.tidb_isolation_read_engines = "engine list separated by commas";
    ```

    or

    ```sql
    set SESSION tidb_isolation_read_engines = "engine list separated by commas";
    ```

    The default configuration of the SESSION level inherits from the configuration of the TiDB INSTANCE level.

The final engine configuration is the session-level configuration, that is, the session-level configuration overrides the instance-level configuration. For example, if you have configured "tikv" in the INSTANCE level and "tiflash" in the SESSION level, then the TiFlash replicas are read. If the final engine configuration is "tikv" and "tiflash", then the TiKV and TiFlash replicas are both read, and the optimizer automatically selects a better engine to execute.

> **Note:**
>
> Because [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) and other components need to read some system tables stored in the TiDB memory table area, it is recommended to always add the "tidb" engine to the instance-level engine configuration.

You can specify the engines using the following statement:

```sql
set @@session.tidb_isolation_read_engines = "engine list separated by commas";
```

or

```sql
set SESSION tidb_isolation_read_engines = "engine list separated by commas";
```

If the queried table does not have a replica of the specified engine (for example, the engine is configured as "tiflash" but the table does not have a TiFlash replica), the query returns an error.
## Manual hint

Manual hint can force TiDB to use specified replicas for specific table(s) on the premise of satisfying engine isolation. Here is an example of using the manual hint:

```sql
select /*+ read_from_storage(tiflash[table_name]) */ ... from table_name;
```

If you set an alias to a table in a query statement, you must use the alias in the statement that includes a hint for the hint to take effect. For example:

```sql
select /*+ read_from_storage(tiflash[alias_a,alias_b]) */ ... from table_name_1 as alias_a, table_name_2 as alias_b where alias_a.column_1 = alias_b.column_2;
```

In the above statements, `tiflash[]` prompts the optimizer to read the TiFlash replicas. You can also use `tikv[]` to prompt the optimizer to read the TiKV replicas as needed. For hint syntax details, refer to [READ_FROM_STORAGE](https://docs.pingcap.com/tidb/stable/optimizer-hints#read_from_storagetiflasht1_name--tl_name--tikvt2_name--tl_name-).

If the table specified by a hint does not have a replica of the specified engine, the hint is ignored and a warning is reported. In addition, a hint only takes effect on the premise of engine isolation. If the engine specified in a hint is not in the engine isolation list, the hint is also ignored and a warning is reported.

> **Note:**
>
> The MySQL client of 5.7.7 or earlier versions clears optimizer hints by default. To use the hint syntax in these early versions, start the client with the `--comments` option, for example, `mysql -h 127.0.0.1 -P 4000 -uroot --comments`.
## The relationship of smart selection, engine isolation, and manual hint

In the above three ways of reading TiFlash replicas, engine isolation specifies the overall range of available replicas of engines; within this range, manual hint provides statement-level and table-level engine selection that is more fine-grained; finally, CBO makes the decision and selects a replica of an engine based on cost estimation within the specified engine list.

> **Note:**
>
> - Before v4.0.3, the behavior of reading from TiFlash replica in a non-read-only SQL statement (for example, `INSERT INTO ... SELECT`, `SELECT ... FOR UPDATE`, `UPDATE ...`, `DELETE ...`) is undefined.
> - For versions from v4.0.3 to v6.2.0, internally TiDB ignores the TiFlash replica for a non-read-only SQL statement to guarantee the data correctness. That is, for [smart selection](#smart-selection), TiDB automatically selects the non-TiFlash replica; for [engine isolation](#engine-isolation) that specifies TiFlash replica **only**, TiDB reports an error; and for [manual hint](#manual-hint), TiDB ignores the hint.
> - For versions from v6.3.0 to v7.0.0, if the TiFlash replica is enabled, you can use the [`tidb_enable_tiflash_read_for_write_stmt`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tiflash_read_for_write_stmt-new-in-v630) variable to control whether TiDB uses the TiFlash replica for a non-read-only SQL statement.
> - Starting from v7.1.0, if the TiFlash replica is enabled and the [SQL Mode](https://docs.pingcap.com/tidb/stable/sql-mode) of the current session is not strict (which means the `sql_mode` value does not contain `STRICT_TRANS_TABLES` or `STRICT_ALL_TABLES`), TiDB automatically decides whether to use the TiFlash replica for a non-read-only SQL statement based on cost estimation.
