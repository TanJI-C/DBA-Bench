# sys schema overview and MySQL compatibility tables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sys-schema/sys-schema.md`
- Source Title: `sys Schema`
- Source Heading Path: ``sys` Schema | `sys` Schema > Tables for MySQL compatibility`
- Source Line Ranges: `5-14`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `sys-schema`, `system-tables`, `views`, `information-schema`, `performance-schema`, `mysql-compatibility`, `unused-indexes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0708_45d6630b51`
- Source ID: `tidb-docs-8.1:sys-schema/sys-schema.md#sys-schema`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c65f6e1a98cd2f4d8adbe3d8a39c58f5f67778cb340b5f37ea0256b0ca729baa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sys-schema/sys-schema#sys-schema
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sys-schema/sys-schema.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what the `sys` schema provides in TiDB and which MySQL compatibility table shows indexes unused since the last TiDB start.
- Retrieval Keywords: `sys` schema, sys schema overview, Tables for MySQL compatibility, `schema_unused_indexes`, unused indexes since the last start of TiDB, `INFORMATION_SCHEMA`, `PERFORMANCE SCHEMA`, views in `sys` schema
- Follow-up Guidance: The source points to the `schema_unused_indexes` table for details about indexes that have not been used since the last start of TiDB.
- Classification Note: This is reference content because it defines the purpose of the `sys` schema and lists the MySQL compatibility table `schema_unused_indexes` with its description.

## Official Source Content

# `sys` Schema

Starting from v8.0.0, TiDB provides the `sys` schema. You can use the views in `sys` schema to understand the data in the system tables, [`INFORMATION_SCHEMA`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema), and [`PERFORMANCE SCHEMA`](https://docs.pingcap.com/tidb/stable/performance-schema/performance-schema) of TiDB.
## Tables for MySQL compatibility

| Table name                                                                                       | Description                                               |
|--------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| [`schema_unused_indexes`](https://docs.pingcap.com/tidb/stable/sys-schema/sys-schema-unused-indexes)                                  | Records indexes that have not been used since the last start of TiDB. |
