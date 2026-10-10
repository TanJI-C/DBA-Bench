# Operational notes and repair SQL cautions

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sync-diff-inspector/sync-diff-inspector-overview.md`
- Source Title: `sync-diff-inspector User Guide`
- Source Heading Path: `sync-diff-inspector User Guide > Note`
- Source Line Ranges: `292-299`
- Source Scope: `shared`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`, `shared`
- Topic Tags: `resource-usage`, `collation`, `character-set`, `index-fields`, `check-data-only`, `statistics`, `analyze-table`, `table-rules`, `sharding`, `repair-sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0241_f0fe762588`
- Source ID: `tidb-docs-8.1:sync-diff-inspector/sync-diff-inspector-overview.md#note`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `44160906875480ea8324cc68f4bd3da6a20879c16b9cd6b63e35636a66f00de7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview#note
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sync-diff-inspector/sync-diff-inspector-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need official operational cautions for sync-diff-inspector about resource usage, collation and character set effects, index-fields, check-data-only, statistics, table-rules, sharding, and the repair SQL reference note.
- Retrieval Keywords: sync-diff-inspector Note, peak business hours, collation, character set, index-fields, check-data-only, analyze table {table_name}, TiDB statistics, table-rules, schema-pattern, table-pattern, target-schema, target-table, sharding is enabled by default, composite primary key, varchar, repair SQL, generated SQL file is only used as a reference
- Follow-up Guidance: The source also notes that when sharded MySQL tables are merged into TiDB with a composite primary key, configure the original primary key with `index-fields` and set `check-data-only` to `true`.
- Classification Note: This is classified as operation content because it provides usage notes and cautions that affect how sync-diff-inspector compares data and how generated repair SQL should be treated.

## Official Source Content

## Note

- sync-diff-inspector consumes a certain amount of server resources when checking data. Avoid using sync-diff-inspector to check data during peak business hours.
- Before comparing the data in MySQL with that in TiDB, check the character set and `collation` configuration of the tables. This is especially important when the primary key or unique key of a table is the `varchar` type. If collation rules differ between upstream and downstream databases, sorting issues might occur, leading to inaccurate verification results. For example, MySQL's default collation is case-insensitive, while TiDB's default collation is case-sensitive. This inconsistency might cause identical delete and insert records in the repair SQL. To avoid this issue, use the `index-fields` configuration to specify index columns that are not affected by case sensitivity. If you configure `collation` in the sync-diff-inspector configuration file and explicitly use the same collation for both upstream and downstream during chunk-based comparison, note that the order of index fields depends on the table's collation configuration. If the collations differ, one side might be unable to use the index. Additionally, if the character sets differ between upstream and downstream (for example, MySQL uses UTF-8 while TiDB uses UTF-8MB4), it is not possible to unify the collation configuration.
- If the primary key differs between upstream and downstream tables, sync-diff-inspector does not use the original primary key column to divide chunks. For example, when sharded tables in MySQL are merged into TiDB using a composite primary key that includes the original primary key and a shard key. In this case, configure the original primary key column using `index-fields` and set `check-data-only` to `true`.
- sync-diff-inspector divides data into chunks first according to TiDB statistics and you need to guarantee the accuracy of the statistics. You can manually run the `analyze table {table_name}` command when the TiDB server's *workload is light*.
- Pay special attention to `table-rules`. If you configure `schema-pattern="test1"`, `table-pattern = "t_1"`, `target-schema="test2"` and `target-table = "t_2"`, the `test1`.`t_1` schema in the source database and the `test2`.`t_2` schema in the target database are compared. Sharding is enabled by default in sync-diff-inspector, so if the source database has a `test2`.`t_2` table, the `test1`.`t_1` table and `test2`.`t_2` table in the source database serving as sharding are compared with the `test2`.`t_2` table in the target database.
- The generated SQL file is only used as a reference for repairing data, and you need to confirm it before executing these SQL statements to repair data.
