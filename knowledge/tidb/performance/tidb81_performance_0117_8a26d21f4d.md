# SQL priority, auto analyze, and optimizer overrides

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/sql-faq.md`
- Source Title: `SQL FAQs`
- Source Heading Path: `SQL FAQs > How to control or change the execution priority of SQL commits? | SQL FAQs > What's the trigger strategy for `auto analyze` in TiDB? | SQL FAQs > Can I use optimizer hints to override the optimizer behavior?`
- Source Line Ranges: `202-247`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `statement-priority`, `resource-control`, `auto-analyze`, `statistics`, `optimizer-hints`, `sql-plan-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0117_8a26d21f4d`
- Source ID: `tidb-docs-8.1:faq/sql-faq.md#how-to-control-or-change-the-execution-priority-of-sql-commits`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3bde2bd3b5412acae8f792a02f6c246410bf788e888a0c46de307293e02f47e5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/sql-faq#how-to-control-or-change-the-execution-priority-of-sql-commits
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/sql-faq.md

## Retrieval Guidance

- Use When: Use this chunk when discussing SQL statement priority settings, `auto analyze` trigger conditions, or ways to override optimizer behavior with hints or SQL Plan Management.
- Retrieval Keywords: tidb_force_priority, HIGH_PRIORITY, LOW_PRIORITY, DELAYED, NO_PRIORITY, Resource Control, resource groups, ANALYZE has a low priority by default, full table scan low priority, auto analyze, tidb_auto_analyze_ratio, tidb_enable_auto_analyze, pseudo-estimate-ratio, tidb_enable_pseudo_for_outdated_stats, optimizer hints, SQL Plan Management, USE INDEX
- Follow-up Guidance: The source states that `auto analyze` is triggered when a table or partition reaches 1000 rows and its modified-row ratio exceeds `tidb_auto_analyze_ratio`, and that TiDB supports optimizer overrides through hints and SQL Plan Management.
- Classification Note: This is classified as performance content because it covers execution priority, automatic statistics collection thresholds, and optimizer override mechanisms that affect query execution behavior.

## Official Source Content

## How to control or change the execution priority of SQL commits?

TiDB supports changing the priority on a [global](https://docs.pingcap.com/tidb/stable/system-variables#tidb_force_priority) or individual statement basis. Priority has the following meaning:

- `HIGH_PRIORITY`: this statement has a high priority, that is, TiDB gives priority to this statement and executes it first.

- `LOW_PRIORITY`: this statement has a low priority, that is, TiDB reduces the priority of this statement during the execution period.

- `DELAYED`: this statement has normal priority and is the same as the `NO_PRIORITY` setting for `tidb_force_priority`.

> **Note:**
>
> Starting from v6.6.0, TiDB supports [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control). You can use this feature to execute SQL statements with different priorities in different resource groups. By configuring proper quotas and priorities for these resource groups, you can gain better scheduling control for SQL statements with different priorities. When resource control is enabled, statement priority will no longer take effect. It is recommended that you use [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) to manage resource usage for different SQL statements.

You can combine the above two parameters with the DML of TiDB to use them. For example:

1. Adjust the priority by writing SQL statements in the database:

    ```sql
    SELECT HIGH_PRIORITY | LOW_PRIORITY | DELAYED COUNT(*) FROM table_name;
    INSERT HIGH_PRIORITY | LOW_PRIORITY | DELAYED INTO table_name insert_values;
    DELETE HIGH_PRIORITY | LOW_PRIORITY | DELAYED FROM table_name;
    UPDATE HIGH_PRIORITY | LOW_PRIORITY | DELAYED table_reference SET assignment_list WHERE where_condition;
    REPLACE HIGH_PRIORITY | LOW_PRIORITY | DELAYED INTO table_name;
    ```

2. The full table scan statement automatically adjusts itself to a low priority. [`ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) has a low priority by default.
## What's the trigger strategy for `auto analyze` in TiDB?

When the number of rows in a table or a single partition of a partitioned table reaches 1000, and the ratio (the number of modified rows / the current total number of rows) of the table or partition is larger than [`tidb_auto_analyze_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_ratio), the [`ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) statement is automatically triggered.

The default value of the `tidb_auto_analyze_ratio` system variable is `0.5`, indicating that this feature is enabled by default. It is not recommended to set the value of `tidb_auto_analyze_ratio` to be larger than or equal to [`pseudo-estimate-ratio`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#pseudo-estimate-ratio) (the default value is `0.8`), otherwise the optimizer might use pseudo statistics. TiDB v5.3.0 introduces the [`tidb_enable_pseudo_for_outdated_stats`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_pseudo_for_outdated_stats-new-in-v530) variable, and when you set it to `OFF`, pseudo statistics are not used even if the statistics are outdated.

To disable `auto analyze`, use the system variable [`tidb_enable_auto_analyze`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_auto_analyze-new-in-v610).
## Can I use optimizer hints to override the optimizer behavior?

TiDB supports multiple ways to override the default query optimizer behavior, including [hints](https://docs.pingcap.com/tidb/stable/optimizer-hints) and [SQL Plan Management](https://docs.pingcap.com/tidb/stable/sql-plan-management). The basic usage is similar to MySQL, with several TiDB specific extensions:

```sql
SELECT column_name FROM table_name USE INDEX（index_name）WHERE where_condition;
```
