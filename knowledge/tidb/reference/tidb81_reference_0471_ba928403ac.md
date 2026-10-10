# Partitioned table restrictions and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Restrictions and limitations on partitions`
- Source Line Ranges: `1466-1475`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `limitations`, `alter-table`, `cache`, `temporary-tables`, `foreign-keys`, `optimizer-hints`, `partitioned-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0471_ba928403ac`
- Source ID: `tidb-docs-8.1:partitioned-table.md#restrictions-and-limitations-on-partitions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `868ad656363aa45b094b71c475edc4c75861c3104de5e8f5b5ebd708e21bcc53`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#restrictions-and-limitations-on-partitions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when checking feature restrictions and unsupported statements or compatibility for partitioned tables in TiDB.
- Retrieval Keywords: Restrictions and limitations on partitions, ALTER TABLE ... CHANGE COLUMN, change column types of partitioned tables is not supported, ALTER TABLE ... CACHE, cached tables, Temporary tables, NOT compatible with partitioned tables, foreign key, Creating a foreign key on a partitioned table is not supported, ORDER_INDEX, indexes on partitioned tables cannot be read in order
- Follow-up Guidance: The source specifically names unsupported operations involving `ALTER TABLE ... CHANGE COLUMN`, `ALTER TABLE ... CACHE`, temporary tables, foreign keys, and the `ORDER_INDEX` optimizer hint.
- Classification Note: This is classified as reference content because it enumerates documented restrictions and limitations for partitioned tables.

## Official Source Content

## Restrictions and limitations on partitions

This section introduces some restrictions and limitations on partitioned tables in TiDB.

- Using the [`ALTER TABLE ... CHANGE COLUMN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-column) statement to change column types of partitioned tables is not supported.
- Using the [`ALTER TABLE ... CACHE`](https://docs.pingcap.com/tidb/stable/cached-tables) statement to set partitioned tables to cached tables is not supported.
- [Temporary tables](https://docs.pingcap.com/tidb/stable/temporary-tables) in TiDB are **NOT** compatible with partitioned tables.
- Creating a [foreign key](https://docs.pingcap.com/tidb/stable/foreign-key) on a partitioned table is not supported.
- The [`ORDER_INDEX(t1_name, idx1_name [, idx2_name ...])`](/optimizer-hints.md#order_indext1_name-idx1_name--idx2_name-) hint does not work for partitioned tables and their related indexes, because indexes on partitioned tables cannot be read in order.
