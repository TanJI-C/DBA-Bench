# Extended statistics overview and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/extended-statistics.md`
- Source Title: `Introduction to Extended Statistics`
- Source Heading Path: `Introduction to Extended Statistics | Introduction to Extended Statistics > Limitations`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `extended-statistics`, `optimizer`, `analyze`, `basic-statistics`, `limitations`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0275_f06193cf39`
- Source ID: `tidb-docs-8.1:extended-statistics.md#introduction-to-extended-statistics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cbd03adfeeed206974b5f5d4b707a990f31fb1eb1938c1849476fbde1d74098f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/extended-statistics#introduction-to-extended-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/extended-statistics.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about what extended statistics are, how they differ from basic statistics, or when TiDB does not collect extended statistics during ANALYZE.
- Retrieval Keywords: extended statistics, basic statistics, histograms, Count-Min Sketch, optimizer estimate query cost, ANALYZE, extended statistics disabled by default, limitations, ANALYZE INCREMENTAL, tidb_enable_fast_analyze, statistics collection on indexes only, experimental
- Follow-up Guidance: The source states that TiDB collects only basic statistics by default, and extended statistics are collected only after enabling the feature and creating extended statistics objects before a later ANALYZE.
- Classification Note: This is reference content because it defines extended statistics, contrasts them with basic statistics, and lists documented limitations on collection scenarios.

## Official Source Content

# Introduction to Extended Statistics

TiDB can collect the following two types of statistics. This document describes how to use extended statistics to guide the optimizer. Before reading this document, it is recommended that you read [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics) first.

- Basic statistics: statistics such as histograms and Count-Min Sketch, which primarily focus on individual columns. They are essential for the optimizer to estimate the query cost. See [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics) for details.
- Extended statistics: statistics that focus on data correlations between specified columns, which guide the optimizer to estimate the query cost more precisely when the queried columns are correlated. 

When the `ANALYZE` statement is executed manually or automatically, TiDB by default only collects the basic statistics and does not collect the extended statistics. This is because the extended statistics are only used for optimizer estimates in specific scenarios, and collecting them requires additional overhead.

Extended statistics are disabled by default. To collect extended statistics, you need to first enable extended statistics, and then create your desired extended statistics objects one by one. After the object creation, the next time the `ANALYZE` statement is executed, TiDB collects both the basic statistics and the corresponding extended statistics of the created objects.

> **Warning:**
>
> This feature is experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.
## Limitations

Extended statistics are not collected in the following scenarios:

- Statistics collection on indexes only
- Statistics collection using the `ANALYZE INCREMENTAL` command
- Statistics collection when the value of the system variable `tidb_enable_fast_analyze` is set to `true`
