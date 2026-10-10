# Statement summary parameter configuration and sizing

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statement-summary-tables.md`
- Source Title: `Statement Summary Tables`
- Source Heading Path: `Statement Summary Tables > Parameter configuration | Statement Summary Tables > Parameter configuration > Set a proper size for statement summary`
- Source Line Ranges: `129-209`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `statement-summary`, `system-variables`, `refresh-interval`, `history-size`, `eviction`, `memory-usage`, `sql-digest`, `sizing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0150_7436916bea`
- Source ID: `tidb-docs-8.1:statement-summary-tables.md#parameter-configuration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c0ec6bcfaf8e0e003381231c9899277abd80f28bebe9757be1787bd242f3bbdd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statement-summary-tables#parameter-configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statement-summary-tables.md

## Retrieval Guidance

- Use When: Use this content when you need the statement summary system variables, refresh and history behavior, eviction semantics, memory sizing formula, or SQL examples for checking whether `information_schema.statements_summary` is full and whether `information_schema.statements_summary_evicted` has records.
- Retrieval Keywords: tidb_enable_stmt_summary, tidb_stmt_summary_refresh_interval, tidb_stmt_summary_history_size, tidb_stmt_summary_max_stmt_count, tidb_stmt_summary_max_sql_length, tidb_stmt_summary_internal_query, information_schema.statements_summary, information_schema.statements_summary_history, information_schema.statements_summary_evicted, SQL digest eviction, least recently used SQL digests, statement summary memory usage formula, select @@global.tidb_stmt_summary_max_stmt_count, select count(*) from information_schema.statements_summary, select * from information_schema.statements_summary_evicted
- Follow-up Guidance: The source includes example `set global` statements and SQL queries to compare `@@global.tidb_stmt_summary_max_stmt_count` with `count(*)` from `information_schema.statements_summary` and to inspect `EVICTED_COUNT` in `information_schema.statements_summary_evicted`.
- Classification Note: This is classified as configuration because it defines statement summary system variables, their defaults and effects, and how their sizes affect refresh behavior, history retention, eviction, and memory usage.

## Official Source Content

## Parameter configuration

The following system variables are used to control the statement summary:

- `tidb_enable_stmt_summary`: Determines whether to enable the statement summary feature. `1` represents `enable`, and `0` means `disable`. The feature is enabled by default. The statistics in the system table are cleared if this feature is disabled. The statistics are re-calculated next time this feature is enabled. Tests have shown that enabling this feature has little impact on performance.
- `tidb_stmt_summary_refresh_interval`: The interval at which the `statements_summary` table is refreshed. The time unit is second (s). The default value is `1800`.
- `tidb_stmt_summary_history_size`: The size of each SQL statement category stored in the `statements_summary_history` table, which is also the maximum number of records in the `statements_summary_evicted` table. The default value is `24`.
- `tidb_stmt_summary_max_stmt_count`: Limits the number of SQL digests that the `statements_summary` and `statements_summary_history` tables can store in memory totally. The default value is `3000`.

    Once this limit is exceeded, TiDB evicts the least recently used SQL digests from both `statements_summary` and `statements_summary_history` tables. These evicted digests are then counted in the [`statements_summary_evicted`](#statements_summary_evicted) table.

    > **Note:**
    >
    > - When a SQL digest is evicted, its related summary data of all time ranges is removed from both the `statements_summary` and `statements_summary_history` tables. As a result, even if the number of SQL digests within a specific time range does not exceed the limit, the number of SQL digests in the `statements_summary_history` table might be less than the actual number of SQL digests. If this situation occurs and affects performance, you are recommended to increase the value of `tidb_stmt_summary_max_stmt_count`.
    > - For TiDB Self-Managed, when [`tidb_stmt_summary_enable_persistent`](#persist-statements-summary) is enabled, data in the `statements_summary_history` table is persisted to the disk. In this case, `tidb_stmt_summary_max_stmt_count` only limits the number of SQL digests that the `statements_summary` table can store in memory, and TiDB evicts the least recently used SQL digests only from the `statements_summary` table when `tidb_stmt_summary_max_stmt_count` is exceeded.

- `tidb_stmt_summary_max_sql_length`: Specifies the longest display length of `DIGEST_TEXT` and `QUERY_SAMPLE_TEXT`. The default value is `4096`.
- `tidb_stmt_summary_internal_query`: Determines whether to count the TiDB SQL statements. `1` means to count, and `0` means not to count. The default value is `0`.

An example of the statement summary configuration is shown as follows:

```sql
set global tidb_stmt_summary_max_stmt_count = 3000;
set global tidb_enable_stmt_summary = true;
set global tidb_stmt_summary_refresh_interval = 1800;
set global tidb_stmt_summary_history_size = 24;
```

After the preceding configuration takes effect, the `statements_summary` table is cleared every 30 minutes and the `statements_summary_history` table stores up to 3000 types of SQL statements. For each type, the `statements_summary_history` table stores data for the recent 24 periods. The `statements_summary_evicted` table records the recent 24 periods during which SQL statements are evicted from the statement summary. The `statements_summary_evicted` table is updated every 30 minutes.

> **Note:**
>
> - If a SQL type appears every minute, the `statements_summary_history` stores data for the most recent 12 hours. If a SQL type only appears from 00:00 to 00:30 every day, the `statements_summary_history` stores data for the most recent 24 periods, with each period being 1 day. Therefore, the `statements_summary_history` stores the most recent 24 days of data for this SQL type.
> - The `tidb_stmt_summary_history_size`, `tidb_stmt_summary_max_stmt_count`, and `tidb_stmt_summary_max_sql_length` configuration items affect memory usage. It is recommended that you adjust these configurations based on your needs, the SQL size, SQL count, and machine configuration. It is not recommended to set them too large values. You can calculate the memory usage using `tidb_stmt_summary_history_size` \* `tidb_stmt_summary_max_stmt_count` \* `tidb_stmt_summary_max_sql_length` \* `3`.
### Set a proper size for statement summary

After the system has run for a period of time (depending on the system load), you can check the `statement_summary` table to see whether SQL eviction has occurred. For example:

```sql
select @@global.tidb_stmt_summary_max_stmt_count;
select count(*) from information_schema.statements_summary;
```

```sql
+-------------------------------------------+
| @@global.tidb_stmt_summary_max_stmt_count |
+-------------------------------------------+
| 3000                                      |
+-------------------------------------------+
1 row in set (0.001 sec)

+----------+
| count(*) |
+----------+
|     3001 |
+----------+
1 row in set (0.001 sec)
```

You can see that the `statements_summary` table is full of records. Then check the evicted data from the `statements_summary_evicted` table:

```sql
select * from information_schema.statements_summary_evicted;
```

```sql
+---------------------+---------------------+---------------+
| BEGIN_TIME          | END_TIME            | EVICTED_COUNT |
+---------------------+---------------------+---------------+
| 2020-01-02 16:30:00 | 2020-01-02 17:00:00 |            59 |
+---------------------+---------------------+---------------+
| 2020-01-02 16:00:00 | 2020-01-02 16:30:00 |            45 |
+---------------------+---------------------+---------------+
2 row in set (0.001 sec)
```

From the preceding result, you can see that a maximum of 59 SQL categories are evicted. In this case, it is recommended that you increase the size of the `statement_summary` table by at least 59 records, which means increasing the size to at least 3059 records.
