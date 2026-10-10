# TiDB Binlog fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.3.md`
- Source Title: `TiDB 2.1.3 Release Notes`
- Source Heading Path: `TiDB 2.1.3 Release Notes > Tools`
- Source Line Ranges: `52-57`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`
- Topic Tags: `binlog`, `pump`, `client-log`, `data-inconsistency`, `unique-key`, `null-value`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0075_fa6949a454`
- Source ID: `tidb-docs-8.1:releases/release-2.1.3.md#tools`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `85d1829477dd81b984b955e96d7728e561b3cb16b63a0d440052d5388e84da95`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.3#tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.3.md

## Retrieval Guidance

- Use When: Use this chunk when searching the TiDB Binlog changes in 2.1.3, including the no available pump issue, Pump client log output, and a data inconsistency fix involving unique keys with NULL values.
- Retrieval Keywords: TiDB Binlog, no available pump, TiDB started or restarted, Pump client log, data inconsistency, unique key containing the NULL value, table only has the unique key and does not have the primary key
- Follow-up Guidance: The source lists fixes for the no available pump issue during TiDB start or restart, enabling Pump client log output, and a data inconsistency issue involving a unique key with NULL values and no primary key.
- Classification Note: This is classified under Tools because the content specifically covers TiDB Binlog changes in the Tools section of the release notes.

## Official Source Content

## Tools

+ TiDB Binlog
    - Fix the `no available pump` issue while TiDB is started or restarted [#157](https://github.com/pingcap/tidb-tools/pull/158)
    - Enable outputting the Pump client log [#165](https://github.com/pingcap/tidb-tools/pull/165)
    - Fix the data inconsistency issue caused by the unique key containing the NULL value when the table only has the unique key and does not have the primary key
