# Enable, create, delete, and move extended statistics

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/extended-statistics.md`
- Source Title: `Introduction to Extended Statistics`
- Source Heading Path: `Introduction to Extended Statistics > Common operations | Introduction to Extended Statistics > Common operations > Enable extended statistics | Introduction to Extended Statistics > Common operations > Create extended statistics objects | Introduction to Extended Statistics > Common operations > Delete extended statistics objects | Introduction to Extended Statistics > Common operations > Export and import extended statistics`
- Source Line Ranges: `29-109`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `extended-statistics`, `system-variable`, `ddl`, `analyze`, `mysql.stats_extended`, `cache-reload`, `export`, `import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0138_d3ae6c4ddf`
- Source ID: `tidb-docs-8.1:extended-statistics.md#common-operations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2d95ffed19103b914983ab6094a62a8cc5adceec2938fc8ff1513f09f4ac7dab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/extended-statistics#common-operations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/extended-statistics.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how to enable, create, delete, export, import, or reload extended statistics objects in TiDB.
- Retrieval Keywords: tidb_enable_extended_stats, SET GLOBAL tidb_enable_extended_stats = ON, ALTER TABLE ADD STATS_EXTENDED, ALTER TABLE table_name ADD STATS_EXTENDED IF NOT EXISTS stats_name stats_type(column_name, column_name...), correlation type, ALTER TABLE DROP STATS_EXTENDED, mysql.stats_extended, ADMIN RELOAD STATS_EXTENDED, export and import extended statistics, status column, version column
- Follow-up Guidance: The source explains that TiDB nodes cache data from mysql.stats_extended, warns against directly operating on that system table, and says ADMIN RELOAD STATS_EXTENDED clears the current cache and fully reloads the table on each TiDB node.
- Classification Note: This is operation content because it provides the SQL statements and system variable used to enable, create, delete, reload, and transfer extended statistics objects.

## Official Source Content

## Common operations
### Enable extended statistics

To enable extended statistics, set the system variable `tidb_enable_extended_stats` to `ON`:

```sql
SET GLOBAL tidb_enable_extended_stats = ON;
```

The default value of this variable is `OFF`. The setting of this system variable applies to all extended statistics objects.
### Create extended statistics objects

The creation of extended statistics objects is not a one-time task. You need to repeat the creation for each extended statistics object.

To create an extended statistics object, use the SQL statement `ALTER TABLE ADD STATS_EXTENDED`. The syntax is as follows:

```sql
ALTER TABLE table_name ADD STATS_EXTENDED IF NOT EXISTS stats_name stats_type(column_name, column_name...);
```

In the syntax, you can specify the table name, statistics name, statistics type, and column name of the extended statistics object to be collected.

- `table_name` specifies the name of the table from which the extended statistics are collected.
- `stats_name` specifies the name of the statistics object, which must be unique for each table.
- `stats_type` specifies the type of the statistics. Currently, only the correlation type is supported.
- `column_name` specifies the column group, which might have multiple columns. Currently, you can only specify two column names.

<details>
<summary> How it works</summary>

To improve access performance, each TiDB node maintains a cache in the system table `mysql.stats_extended` for extended statistics. After you create the extended statistics objects, the next time the `ANALYZE` statement is executed, TiDB will collect the extended statistics if the system table `mysql.stats_extended` has the corresponding objects.

Each row in the `mysql.stats_extended` table has a `version` column. Once a row is updated, the value of `version` is increased. In this way, TiDB loads the table into memory incrementally, instead of fully.

TiDB loads `mysql.stats_extended` periodically to ensure that the cache is kept the same as the data in the table.

> **Warning:**
>
> It is **NOT RECOMMENDED** to directly operate on the `mysql.stats_extended` system table. Otherwise, inconsistent caches occur on different TiDB nodes.
>
> If you have mistakenly operated on the table, you can execute the following statement on each TiDB node. Then the current cache will be cleared and the `mysql.stats_extended` table will be fully reloaded:
>
> ```sql
> ADMIN RELOAD STATS_EXTENDED;
> ```

</details>
### Delete extended statistics objects

To delete an extended statistics object, use the following statement:

```sql
ALTER TABLE table_name DROP STATS_EXTENDED stats_name;
```

<details>
<summary>How it works</summary>

After you execute the statement, TiDB marks the value of the corresponding object in `mysql.stats_extended`'s column `status` to `2`, instead of deleting the object directly.

Other TiDB nodes will read this change and delete the object in their memory cache. The background garbage collection will delete the object eventually.

> **Warning:**
>
> It is **NOT RECOMMENDED** to directly operate on the `mysql.stats_extended` system table. Otherwise, inconsistent caches occur on different TiDB nodes.
>
> If you have mistakenly operated on the table, you can use the following statement on each TiDB node. Then the current cache will be cleared and the `mysql.stats_extended` table will be fully reloaded:
>
> ```sql
> ADMIN RELOAD STATS_EXTENDED;
> ```

</details>
### Export and import extended statistics

The way of exporting or importing extended statistics is the same as exporting or importing basic statistics. See [Introduction to Statistics - Import and export statistics](https://docs.pingcap.com/tidb/stable/statistics#export-and-import-statistics) for details.
