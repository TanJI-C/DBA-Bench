# Selective statistics collection on indexes

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Selective statistics collection | Introduction to Statistics > Selective statistics collection > Collect statistics on indexes`
- Source Line Ranges: `109-126`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `statistics`, `analyze-table`, `indexes`, `selective-collection`, `analyze-version`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0228_0bbcbb7e0f`
- Source ID: `tidb-docs-8.1:statistics.md#selective-statistics-collection`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9df66ecbe332e4f7d3371d020d8aa423cace6e2f751a672d6e21371733e0e3b3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#selective-statistics-collection
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when you need the SQL syntax for collecting statistics on selected indexes and the note about `tidb_analyze_version = 2` behavior.
- Retrieval Keywords: Selective statistics collection, Collect statistics on indexes, ANALYZE TABLE TableName INDEX [IndexNameList], IndexNameList, tidb_analyze_version, collects statistics on the entire table, all columns and indexes
- Follow-up Guidance: If `IndexNameList` is empty, the syntax collects statistics on all indexes in `TableName`.
- Classification Note: This content describes selective `ANALYZE TABLE ... INDEX` usage and the version-specific note for `tidb_analyze_version` 2.

## Official Source Content

## Selective statistics collection

This section describes how to collect statistics selectively.
### Collect statistics on indexes

To collect statistics on all indexes in `IndexNameList` in `TableName`, use the following syntax:

```sql
ANALYZE TABLE TableName INDEX [IndexNameList] [WITH NUM BUCKETS|TOPN|CMSKETCH DEPTH|CMSKETCH WIDTH]|[WITH NUM SAMPLES|WITH FLOATNUM SAMPLERATE];
```

When `IndexNameList` is empty, this syntax collects statistics on all indexes in `TableName`.

> **Note:**
>
> To ensure that the statistical information before and after the collection is consistent, when `tidb_analyze_version` is `2`, this syntax collects statistics on the entire table (including all columns and indexes), instead of only on indexes.
