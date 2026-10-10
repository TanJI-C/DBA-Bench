# Selective statistics collection and sampling performance options

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Selective statistics collection > Collect statistics on some columns | Introduction to Statistics > Selective statistics collection > Collect statistics on partitions | Introduction to Statistics > Selective statistics collection > Collect statistics on partitions > Collect statistics of partitioned tables in dynamic pruning mode | Introduction to Statistics > Improve collection performance | Introduction to Statistics > Improve collection performance > Statistics sampling`
- Source Line Ranges: `127-252`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `analyze`, `statistics`, `predicate-columns`, `partitions`, `globalstats`, `dynamic-pruning`, `sampling`, `performance`, `column-tracking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0229_d1cff0fbba`
- Source ID: `tidb-docs-8.1:statistics.md#collect-statistics-on-some-columns`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `37da1f7a21fe9e620520213070ad8451cb0f7ea5b051047fe59ca98f1d374901`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#collect-statistics-on-some-columns
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when looking for exact ANALYZE syntax and behavior for collecting statistics on selected columns, PREDICATE COLUMNS, partitions, GlobalStats in dynamic pruning mode, or sampling options to improve statistics collection performance.
- Retrieval Keywords: ANALYZE TABLE TableName COLUMNS ColumnNameList, ANALYZE TABLE TableName PREDICATE COLUMNS, ANALYZE TABLE TableName ALL COLUMNS, ANALYZE TABLE TableName PARTITION PartitionNameList, ANALYZE TABLE TableName PARTITION PartitionNameList INDEX, ANALYZE TABLE TableName PARTITION PartitionNameList COLUMNS ColumnNameList, PREDICATE COLUMNS, tidb_enable_column_tracking, mysql.column_stats_usage, tidb_analyze_version = 2, tidb_analyze_skip_column_types, dynamic pruning mode, GlobalStats, tidb_skip_missing_partition_stats, WITH NUM SAMPLES, WITH FLOATNUM SAMPLERATE, reservoir sampling, Bernoulli sampling, SHOW STATS_META, SHOW TABLE REGIONS, APPROXIMATE_KEYS
- Follow-up Guidance: The source also states that in dynamic pruning mode the ANALYZE configurations of partitions and tables should be the same, and TiDB ignores partition-level COLUMNS or WITH options and returns a warning.
- Classification Note: This is classified as an operation chunk because the content gives operational SQL syntax, system variables, warnings, and behavior for collecting and sampling table statistics.

## Official Source Content

### Collect statistics on some columns

In most cases, the optimizer only uses statistics on columns in the `WHERE`, `JOIN`, `ORDER BY`, and `GROUP BY` statements. These columns can be referred to as `PREDICATE COLUMNS`.

If a table has many columns, collecting statistics on all the columns can cause a large overhead. To reduce the overhead, you can collect statistics on only specific columns (that you choose) or `PREDICATE COLUMNS` to be used by the optimizer. To persist the column list of any subset of columns for reuse in future, see [Persist column configurations](#persist-column-configurations).

> **Note:**
>
> - Collecting statistics on predicate columns is only applicable for [`tidb_analyze_version = 2`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_version-new-in-v510).
> - Starting from TiDB v7.2.0, TiDB also introduces the [`tidb_analyze_skip_column_types`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_skip_column_types-new-in-v720) system variable, indicating which types of columns are skipped for statistics collection when executing the `ANALYZE` command to collect statistics. The system variable is only applicable for `tidb_analyze_version = 2`.

- To collect statistics on specific columns, use the following syntax:

    ```sql
    ANALYZE TABLE TableName COLUMNS ColumnNameList [WITH NUM BUCKETS|TOPN|CMSKETCH DEPTH|CMSKETCH WIDTH]|[WITH NUM SAMPLES|WITH FLOATNUM SAMPLERATE];
    ```

    In the syntax, `ColumnNameList` specifies the name list of the target columns. If you need to specify more than one column, use comma `,` to separate the column names. For example, `ANALYZE table t columns a, b`. Besides collecting statistics on the specific columns in a specific table, this syntax collects statistics on the indexed columns and all indexes in that table at the same time.

- To collect statistics on `PREDICATE COLUMNS`, do the following:

    > **Warning:**
    >
    > Currently, collecting statistics on `PREDICATE COLUMNS` is an experimental feature. It is not recommended that you use it in production environments.

    1. Set the value of the [`tidb_enable_column_tracking`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_column_tracking-new-in-v540) system variable to `ON` to enable TiDB to collect `PREDICATE COLUMNS`.

        After the setting, TiDB writes the `PREDICATE COLUMNS` information to the [`mysql.column_stats_usage`](https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema#statistics-system-tables) system table every 100 * [`stats-lease`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#stats-lease).

        After the setting, TiDB writes the `PREDICATE COLUMNS` information to the [`mysql.column_stats_usage`](https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema#statistics-system-tables) system table every 300 seconds.

    2. After the query pattern of your business is relatively stable, collect statistics on `PREDICATE COLUMNS` by using the following syntax:

        ```sql
        ANALYZE TABLE TableName PREDICATE COLUMNS [WITH NUM BUCKETS|TOPN|CMSKETCH DEPTH|CMSKETCH WIDTH]|[WITH NUM SAMPLES|WITH FLOATNUM SAMPLERATE];
        ```

        Besides collecting statistics on `PREDICATE COLUMNS` in a specific table, this syntax collects statistics on indexed columns and all indexes in that table at the same time.

        > **Note:**
        >
        > - If the [`mysql.column_stats_usage`](https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema#statistics-system-tables) system table does not contain any `PREDICATE COLUMNS` recorded for that table, the preceding syntax collects statistics on all columns and all indexes in that table.
        > - Any columns excluded from collection (either by manually listing columns or using `PREDICATE COLUMNS`) will not have their statistics overwritten. When executing a new type of SQL query, the optimizer will use the old statistics for such columns if it exists or pseudo column statistics if columns never had statistics collected. The next ANALYZE using `PREDICATE COLUMNS` will collect the statistics on those columns.

- To collect statistics on all columns and indexes, use the following syntax:

    ```sql
    ANALYZE TABLE TableName ALL COLUMNS [WITH NUM BUCKETS|TOPN|CMSKETCH DEPTH|CMSKETCH WIDTH]|[WITH NUM SAMPLES|WITH FLOATNUM SAMPLERATE];
    ```
### Collect statistics on partitions

- To collect statistics on all partitions in `PartitionNameList` in `TableName`, use the following syntax:

    ```sql
    ANALYZE TABLE TableName PARTITION PartitionNameList [WITH NUM BUCKETS|TOPN|CMSKETCH DEPTH|CMSKETCH WIDTH]|[WITH NUM SAMPLES|WITH FLOATNUM SAMPLERATE];
    ```

- To collect index statistics on all partitions in `PartitionNameList` in `TableName`, use the following syntax:

    ```sql
    ANALYZE TABLE TableName PARTITION PartitionNameList INDEX [IndexNameList] [WITH NUM BUCKETS|TOPN|CMSKETCH DEPTH|CMSKETCH WIDTH]|[WITH NUM SAMPLES|WITH FLOATNUM SAMPLERATE];
    ```

- If you only need to [collect statistics on some columns](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics-on-some-columns) of some partitions in a table, use the following syntax:

    > **Warning:**
    >
    > Currently, collecting statistics on `PREDICATE COLUMNS` is an experimental feature. It is not recommended that you use it in production environments.

    ```sql
    ANALYZE TABLE TableName PARTITION PartitionNameList [COLUMNS ColumnNameList|PREDICATE COLUMNS|ALL COLUMNS] [WITH NUM BUCKETS|TOPN|CMSKETCH DEPTH|CMSKETCH WIDTH]|[WITH NUM SAMPLES|WITH FLOATNUM SAMPLERATE];
    ```
#### Collect statistics of partitioned tables in dynamic pruning mode

When accessing partitioned tables in [dynamic pruning mode](https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode) (which is the default since v6.3.0), TiDB collects table-level statistics, which is called GlobalStats. Currently, GlobalStats is aggregated from statistics of all partitions. In dynamic pruning mode, a statistics update in any partition of a table can trigger the GlobalStats of that table to be updated.

If statistics of some partitions are empty, or statistics of some columns are missing in some partitions, then the collection behavior is controlled by the [`tidb_skip_missing_partition_stats`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_skip_missing_partition_stats-new-in-v730) variable:

- When GlobalStats update is triggered and [`tidb_skip_missing_partition_stats`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_skip_missing_partition_stats-new-in-v730) is `OFF`:

    - If some partitions have no statistics (such as a new partition that has never been analyzed), GlobalStats generation is interrupted and a warning message is displayed saying that no statistics are available on partitions.

    - If statistics of some columns are absent in specific partitions (different columns are specified for analyzing in these partitions), GlobalStats generation is interrupted when statistics of these columns are aggregated, and a warning message is displayed saying that statistics of some columns are absent in specific partitions.

- When GlobalStats update is triggered and [`tidb_skip_missing_partition_stats`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_skip_missing_partition_stats-new-in-v730) is `ON`:

    - If statistics of all or some columns are missing for some partitions, TiDB skips these missing partition statistics when generating GlobalStats so the generation of GlobalStats is not affected.

In dynamic pruning mode, the `ANALYZE` configurations of partitions and tables should be the same. Therefore, if you specify the `COLUMNS` configuration following the `ANALYZE TABLE TableName PARTITION PartitionNameList` statement or the `OPTIONS` configuration following `WITH`, TiDB will ignore them and return a warning.
## Improve collection performance

> **Note:**
>
> - The execution time of `ANALYZE TABLE` in TiDB might be longer than that in MySQL or InnoDB. In InnoDB, only a small number of pages are sampled, while by default in TiDB a comprehensive set of statistics are completely rebuilt.

TiDB provides two options to improve the performance of statistics collection:

- Collecting statistics on a subset of the columns. See [Collecting statistics on some columns](#collect-statistics-on-some-columns).
- Sampling.
### Statistics sampling

Sampling is available via two separate options of the `ANALYZE` statement - with each corresponding to a different collection algorithm:

- `WITH NUM SAMPLES` specifies the size of the sampling set, which is implemented in the reservoir sampling method in TiDB. When a table is large, it is not recommended to use this method to collect statistics. Because the intermediate result set of the reservoir sampling contains redundant results, it causes additional pressure on resources such as memory.
- `WITH FLOAT_NUM SAMPLERATE` is a sampling method introduced in v5.3.0. With the value range `(0, 1]`, this parameter specifies the sampling rate. It is implemented in the way of Bernoulli sampling in TiDB, which is more suitable for sampling larger tables and performs better in collection efficiency and resource usage.

Before v5.3.0, TiDB uses the reservoir sampling method to collect statistics. Since v5.3.0, the TiDB Version 2 statistics uses the Bernoulli sampling method to collect statistics by default. To re-use the reservoir sampling method, you can use the `WITH NUM SAMPLES` statement.

The current sampling rate is calculated based on an adaptive algorithm. When you can observe the number of rows in a table using [`SHOW STATS_META`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-meta), you can use this number of rows to calculate the sampling rate corresponding to 100,000 rows. If you cannot observe this number, you can use the sum of all the values in the `APPROXIMATE_KEYS` column in the results of [`SHOW TABLE REGIONS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-regions) of the table as another reference to calculate the sampling rate.

> **Note:**
>
> Normally, `STATS_META` is more credible than `APPROXIMATE_KEYS`. However, when the result of `STATS_META` is much smaller than the result of `APPROXIMATE_KEYS`, it is recommended that you use `APPROXIMATE_KEYS` to calculate the sampling rate.
