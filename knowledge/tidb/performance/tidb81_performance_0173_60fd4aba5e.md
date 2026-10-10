# Optimizer fundamentals and statistics management

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > Understand query processing > Optimizer fundamentals | A Practical Guide for SQL Tuning > SQL tuning guide > Understand query processing > Statistics management`
- Source Line Ranges: `171-267`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `cost-based optimizer`, `statistics`, `analyze`, `stats health`, `stats meta`, `auto analyze`, `manual analyze`, `lock stats`, `query planning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0173_60fd4aba5e`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#optimizer-fundamentals`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f7ee4a5d377ea32b518525d23f1c358eb398ff3fa5a63613ec1b20f267b7550`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#optimizer-fundamentals
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about how TiDB cost-based optimization depends on statistics quality, how to inspect statistics metadata or health, or how automatic, manual, and locked statistics collection works.
- Retrieval Keywords: cost-based optimizer, CBO, statistics management, table statistics, index statistics, column statistics, SHOW STATS_META, SHOW STATS_HEALTHY, stats health, stats meta, ANALYZE TABLE, auto analyze, manual analyze, LOCK STATS, tidb_auto_analyze_ratio, tidb_auto_analyze_start_time, tidb_auto_analyze_end_time, SHOW VARIABLES LIKE 'tidb\_auto\_analyze%', histograms, Count-Min Sketch, Top-N, Modify_count, Row_count, Healthy
- Follow-up Guidance: The source also states that manual ANALYZE settings such as sample rate, Top-N count, or specific columns are inherited by subsequent automatic collection jobs.
- Classification Note: This is classified as performance for TiDB because the official content explains optimizer inputs, statistics accuracy, execution-plan estimation, and statistics collection controls that affect query planning.

## Official Source Content

#### Optimizer fundamentals

TiDB uses a cost-based optimizer (CBO) to determine the most efficient execution plan for a SQL statement. The optimizer evaluates different execution strategies and selects the one with the lowest estimated cost. The cost depends on factors such as:

- The SQL statement
- Schema design
- Statistics, including:
    - Table statistics
    - Index statistics
    - Column statistics

Based on these inputs, the cost model generates an execution plan that details how TiDB will execute the SQL statement, including:

- Access method
- Join method
- Join order

The effectiveness of the optimizer depends on the quality of the information it receives. To achieve optimal performance, ensure that statistics are up to date and indexes are well-designed.
#### Statistics management

Statistics are essential for the TiDB optimizer. TiDB uses statistics as the input of the optimizer to estimate the number of rows processed in each step of a SQL execution plan.

Statistics are divided into two levels:

- **Table-level statistics**: include the total number of rows in the table and the number of rows modified since the last statistics collection.
- **Index/column-level statistics**: include detailed information such as histograms, Count-Min Sketch, Top-N (values or indexes with the highest occurrences), distribution and quantity of different values, and the number of NULL values.

To check the accuracy and health of your statistics, you can use the following SQL statements:

- [`SHOW STATS_META`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-meta): shows metadata about table statistics.

    ```sql
    SHOW STATS_META WHERE table_name='T2'\G;
    ```

    ```
    *************************** 1. row ***************************
              Db_name: test
           Table_name: T2
       Partition_name:
          Update_time: 2023-05-11 02:16:50
         Modify_count: 10000
            Row_count: 20000
    1 row in set (0.03 sec)
    ```

- [`SHOW STATS_HEALTHY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-healthy): shows the health status of table statistics.

    ```sql
    SHOW STATS_HEALTHY WHERE table_name='T2'\G;
    ```

    ```
    *************************** 1. row ***************************
           Db_name: test
        Table_name: T2
    Partition_name:
           Healthy: 50
    1 row in set (0.00 sec)
    ```

TiDB provides two methods for collecting statistics: automatic and manual collection. In most cases, automatic collection is sufficient. TiDB triggers automatic collection when certain conditions are met. Some common triggering conditions include:

- [`tidb_auto_analyze_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_ratio): the healthiness trigger.
- [`tidb_auto_analyze_start_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_start_time) and [`tidb_auto_analyze_end_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_end_time): the time window for automatic statistics collection.

```sql
SHOW VARIABLES LIKE 'tidb\_auto\_analyze%';
```

```
+-----------------------------------------+-------------+
| Variable_name                           | Value       |
+-----------------------------------------+-------------+
| tidb_auto_analyze_ratio                 | 0.5         |
| tidb_auto_analyze_start_time            | 00:00 +0000 |
| tidb_auto_analyze_end_time              | 23:59 +0000 |
+-----------------------------------------+-------------+
```

In some cases, automatic collection might not meet your needs. By default, it occurs between `00:00` and `23:59`, meaning the analyze job can run at any time. To minimize performance impact on your online business, you can set specific start and end times for statistics collection.

You can manually collect statistics using the `ANALYZE TABLE table_name` statement. This lets you adjust settings such as the sample rate, the number of Top-N values, or collect statistics for specific columns only.

Note that after manual collection, subsequent automatic collection jobs inherit the new settings. This means that any customizations made during manual collection will apply to future automatic analyses.

Locking table statistics is useful in the following scenarios:

- The statistics on the table already represent the data well.
- The table is very large, and statistics collection is time-consuming.
- You want to maintain statistics only during specific time windows.

To lock statistics for a table, you can use the [`LOCK STATS table_name`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats) statement.

For more information, see [Statistics](https://docs.pingcap.com/tidb/stable/statistics).
