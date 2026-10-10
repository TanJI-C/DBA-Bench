# SQL and DB operations features: partition management, rollup, grouping, and MySQL 8.0 collations

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.4.0.md`
- Source Title: `TiDB 7.4.0 Release Notes`
- Source Heading Path: `TiDB 7.4.0 Release Notes > Feature details > SQL | TiDB 7.4.0 Release Notes > Feature details > DB operations`
- Source Line Ranges: `210-233`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `sql`, `partitioning`, `alter-table`, `rollup`, `grouping`, `collation`, `mysql-compatibility`, `migration`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0508_b76cf8ccdb`
- Source ID: `tidb-docs-8.1:releases/release-7.4.0.md#sql`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1daa3e9f350255bc57f719c317d5299f50cec2caa955e02fb75c932ea4d2d4ac`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.4.0#sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.4.0 SQL and DB operation changes involving partition management, GROUP BY rollups, or MySQL 8.0 collations.
- Retrieval Keywords: ALTER TABLE t PARTITION BY ..., partition type management, partitioned tables to non-partitioned tables, non-partitioned tables to partitioned tables, changing partition types, WITH ROLLUP, GROUPING function, GROUP BY clause, SELECT ... FROM ... GROUP BY ... WITH ROLLUP, utf8mb4_0900_ai_ci, utf8mb4_0900_bin, default_collation_for_utf8mb4, MySQL 8.0, migration, data replication from MySQL 5.7 or earlier versions
- Follow-up Guidance: The source points to documentation for converting partitioned tables, using the GROUP BY modifier, and supported character sets and collations.
- Classification Note: This is a release-note chunk for SQL and DB operations because it covers syntax and compatibility additions in v7.4.0, including partition conversion, rollup and grouping support, and new utf8mb4 collations.

## Official Source Content

### SQL

* TiDB supports partition type management [#42728](https://github.com/pingcap/tidb/issues/42728) @[mjonss](https://github.com/mjonss)

    Before v7.4.0, partition types of partitioned tables in TiDB cannot be modified. Starting from v7.4.0, TiDB supports modifying partitioned tables to non-partitioned tables or non-partitioned tables to partitioned tables, and supports changing partition types. Hence, now you can flexibly adjust the partition type and number for a partitioned table. For example, you can use the `ALTER TABLE t PARTITION BY ...` statement to modify the partition type.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/partitioned-table#convert-a-partitioned-table-to-a-non-partitioned-table).

* TiDB supports using the `ROLLUP` modifier and the `GROUPING` function [#44487](https://github.com/pingcap/tidb/issues/44487) @[AilinKid](https://github.com/AilinKid)

    The `WITH ROLLUP` modifier and `GROUPING` function are commonly used in data analysis for multi-dimensional data summarization. Starting from v7.4.0, you can use the `WITH ROLLUP` modifier and `GROUPING` function in the `GROUP BY` clause. For example, you can use the `WITH ROLLUP` modifier in the `SELECT ... FROM ... GROUP BY ... WITH ROLLUP` syntax.

   For more information, see [documentation](https://docs.pingcap.com/tidb/stable/functions-and-operators/group-by-modifier).
### DB operations

* Support collation `utf8mb4_0900_ai_ci` and `utf8mb4_0900_bin` [#37566](https://github.com/pingcap/tidb/issues/37566) @[YangKeao](https://github.com/YangKeao) @[zimulala](https://github.com/zimulala) @[bb7133](https://github.com/bb7133)

    TiDB v7.4.0 enhances the support for migrating data from MySQL 8.0 and adds two collations: `utf8mb4_0900_ai_ci` and `utf8mb4_0900_bin`. `utf8mb4_0900_ai_ci` is the default collation in MySQL 8.0.

    TiDB v7.4.0 also introduces the system variable `default_collation_for_utf8mb4` which is compatible with MySQL 8.0. This enables you to specify the default collation for the utf8mb4 character set and provides compatibility with migration or data replication from MySQL 5.7 or earlier versions.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/character-set-and-collation#character-sets-and-collations-supported-by-tidb).
