# New SQL features in TiDB 5.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0.md`
- Source Title: `What's New in TiDB 5.0`
- Source Heading Path: `What's New in TiDB 5.0 > New features | What's New in TiDB 5.0 > New features > SQL | What's New in TiDB 5.0 > New features > SQL > List partitioning (**Experimental**) | What's New in TiDB 5.0 > New features > SQL > List COLUMNS partitioning (**Experimental**) | What's New in TiDB 5.0 > New features > SQL > Invisible indexes`
- Source Line Ranges: `75-104`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `new-features`, `sql`, `list-partitioning`, `list-columns-partitioning`, `invisible-indexes`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0201_d0e7eba43d`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0.md#new-features`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `928c20d0ae04b3425e33f97dfc1102f5eb6afc5c53bf513b7720f9804982558c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0#new-features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving new SQL features in TiDB 5.0 such as experimental list partitioning, list COLUMNS partitioning, or invisible indexes and their enabling variables or statements.
- Retrieval Keywords: New features, SQL, List partitioning, Experimental, PARTITION BY LIST(expr), PARTITION part_name VALUES IN (...), 1024 distinct integer values, tidb_enable_list_partition, List COLUMNS partitioning, string, DATE, DATETIME, Invisible indexes, Visible, Invisible, ALTER INDEX, optimizer
- Follow-up Guidance: The chunk states that both list partitioning and List COLUMNS partitioning are enabled by setting the session variable `tidb_enable_list_partition` to `ON`, and that index visibility is modified using the `ALTER INDEX` statement.
- Classification Note: This is a SQL new-features chunk because the content introduces SQL-layer capabilities and syntax-related behavior added in TiDB 5.0.

## Official Source Content

## New features
### SQL
#### List partitioning (**Experimental**)

[User document](https://docs.pingcap.com/tidb/stable/partitioned-table#list-partitioning)

With the list partitioning feature, you can effectively query and maintain tables with a large amount of data.

With this feature enabled, partitions and how data is distributed among partitions are defined according to the `PARTITION BY LIST(expr) PARTITION part_name VALUES IN (...)` expression. The partitioned tables' data set supports at most 1024 distinct integer values. You can define the values using the `PARTITION ... VALUES IN (...)` clause.

To enable list partitioning, set the session variable [`tidb_enable_list_partition`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_list_partition-new-in-v50) to `ON`.
#### List COLUMNS partitioning (**Experimental**)

[User document](https://docs.pingcap.com/tidb/stable/partitioned-table#list-columns-partitioning)

List COLUMNS partitioning is a variant of list partitioning. You can use multiple columns as partition keys. Besides the integer data type, you can also use the columns in the string, `DATE`, and `DATETIME` data types as partition columns.

To enable List COLUMNS partitioning, set the session variable [`tidb_enable_list_partition`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_list_partition-new-in-v50) to `ON`.
#### Invisible indexes

[User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-index), [#9246](https://github.com/pingcap/tidb/issues/9246)

When you tune performance or select optimal indexes, you can set an index to be `Visible` or `Invisible` by using SQL statements. This setting can avoid performing resource-consuming operations, such as `DROP INDEX` and `ADD INDEX`.

To modify the visibility of an index, use the `ALTER INDEX` statement. After the modification, the optimizer decides whether to add this index to the index list based on the index visibility.
