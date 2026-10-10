# Feature details reliability: runaway query management GA

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.0.md`
- Source Title: `TiDB 8.1.0 Release Notes`
- Source Heading Path: `TiDB 8.1.0 Release Notes > Feature details | TiDB 8.1.0 Release Notes > Feature details > Reliability`
- Source Line Ranges: `92-107`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `feature-details`, `reliability`, `resource-control`, `runaway-queries`, `query-watch`, `execution-time`, `query-cancellation`, `priority-downgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0592_3e3db8fa6a`
- Source ID: `tidb-docs-8.1:releases/release-8.1.0.md#feature-details`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2bdd4bfb298250d7fd5f8c35a83a48e790489dbd77d17778993a5f9d9b38896`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.0#feature-details
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how TiDB 8.1.0 manages runaway queries or queries that consume more resources than expected using resource groups or QUERY WATCH.
- Retrieval Keywords: Support managing queries that consume more resources than expected, GA, v8.1.0, resource group, maximum execution time, priority is automatically reduced, query is canceled, immediately matching identified queries, text or execution plans, manual marking of queries, QUERY WATCH, SQL text, SQL Digest, execution plan, SQL blocklist, runaway queries, tidb-resource-control
- Follow-up Guidance: For more information, the content refers to the documentation for managing queries that consume more resources than expected and the QUERY WATCH SQL statement.
- Classification Note: This is a feature-details reliability chunk because it explains the GA capability in TiDB 8.1.0 for runaway query management, including execution-time limits, automatic mitigation, and manual query marking.

## Official Source Content

## Feature details
### Reliability

* Support managing queries that consume more resources than expected (GA) [#43691](https://github.com/pingcap/tidb/issues/43691) @[nolouch](https://github.com/nolouch)

    Sudden SQL query performance problems can cause a decline in overall database performance, which is the most common challenge to database stability. The reasons for these problems are diverse, such as untested new SQL statements, drastic changes in data volume, and sudden changes in execution plans. These problems are difficult to avoid completely at the source. TiDB v7.2.0 has introduced the capability to manage queries that consume more resources than expected to quickly reduce the impact of sudden query performance problems. This feature becomes generally available in v8.1.0.

    You can set the maximum execution time for a query in a resource group. When the execution time of a query exceeds the set value, the priority of the query is automatically reduced or the query is canceled. You can also set immediately matching identified queries through text or execution plans within a period of time, to avoid excessive resource consumption during the identification phase when the concurrency of problematic queries is too high.

    TiDB also supports the manual marking of queries. By using the [`QUERY WATCH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-query-watch) command, you can mark queries based on the SQL text, SQL Digest, or execution plan. The queries that match the mark can be downgraded or canceled, achieving the purpose of adding a SQL blocklist.

    The automatic management capability of queries that consume more resources than expected provides users with an effective means to quickly mitigate the impact of query problems on overall performance before the root cause is identified, thereby improving the stability of the database.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries).
