# SQL features: foreign keys and multi-valued indexes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Feature details > SQL`
- Source Line Ranges: `177-192`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `sql`, `foreign-keys`, `mysql-compatibility`, `experimental`, `multi-valued-indexes`, `json`, `indexing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0416_e83cf4a171`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#sql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d002cbf68bd16f492fdb53da65e3c1cf88a189c10d447d3c0e8f297f78fa68ed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.6.0 SQL features that add MySQL-compatible foreign key constraints or experimental multi-valued indexes for JSON arrays.
- Retrieval Keywords: TiDB 6.6.0 SQL, MySQL-compatible foreign key constraints, foreign key constraints experimental, referencing within a table, between tables, constraints validation, cascade operations, MySQL-compatible multi-valued indexes, multi-valued indexes experimental, JSON column, MEMBER OF(), JSON_CONTAINS(), JSON_OVERLAPS(), CREATE INDEX multi-valued indexes, MySQL 8.0 compatibility
- Follow-up Guidance: The content links to the foreign key documentation and the CREATE INDEX documentation section for multi-valued indexes.
- Classification Note: This is classified under SQL because the official content introduces SQL-level compatibility features for foreign keys and indexing JSON array values.

## Official Source Content

### SQL

* Support MySQL-compatible foreign key constraints (experimental) [#18209](https://github.com/pingcap/tidb/issues/18209) @[crazycs520](https://github.com/crazycs520)

    TiDB v6.6.0 introduces the foreign key constraints feature, which is compatible with MySQL. This feature supports referencing within a table or between tables, constraints validation, and cascade operations. This feature helps to migrate applications to TiDB, maintain data consistency, improve data quality, and facilitate data modeling.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/foreign-key).

* Support MySQL-compatible multi-valued indexes (experimental) [#39592](https://github.com/pingcap/tidb/issues/39592) @[xiongjiwei](https://github.com/xiongjiwei) @[qw4990](https://github.com/qw4990)

    TiDB introduces MySQL-compatible multi-valued indexes in v6.6.0. Filtering the values of an array in a JSON column is a common operation, but normal indexes cannot help speed up such an operation. Creating a multi-valued index on an array can greatly improve filtering performance. If an array in the JSON column has a multi-valued index, you can use the multi-valued index to filter the retrieval conditions with `MEMBER OF()`, `JSON_CONTAINS()`, `JSON_OVERLAPS()` functions, thereby reducing much I/O consumption and improving operation speed.

    Introducing multi-valued indexes further enhances TiDB's support for the JSON data type and also improves TiDB's compatibility with MySQL 8.0.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#multi-valued-indexes).
