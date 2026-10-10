# Slow query analysis workflow and bottleneck identification

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/analyze-slow-queries.md`
- Source Title: `Analyze Slow Queries`
- Source Heading Path: `Analyze Slow Queries | Analyze Slow Queries > Identify the performance bottleneck of the query | Analyze Slow Queries > Analyze system issues`
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `tidb`, `tikv`
- Topic Tags: `slow-queries`, `bottleneck-analysis`, `slow-log`, `explain-analyze`, `statement-summary`, `system-issues`, `optimizer-issues`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0001_fe2c8bdb54`
- Source ID: `tidb-docs-8.1:analyze-slow-queries.md#analyze-slow-queries`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `32d504d27ebe2e58153dc451a9d6856c543107f033b16607dc010499b85b918d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/analyze-slow-queries#analyze-slow-queries
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/analyze-slow-queries.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official workflow for analyzing slow queries, identifying which queries are slow with slow query log or statement summary table, and locating the performance bottleneck with slow log or EXPLAIN ANALYZE.
- Retrieval Keywords: Analyze Slow Queries, Identify the performance bottleneck of the query, Analyze system issues, slow query log, statement summary table, TiDB Dashboard, EXPLAIN ANALYZE, slow log, Plan field in the slow log, optimizer issues, system issues, TiDB performance map
- Follow-up Guidance: After identifying the time-consuming part of the query, the content says to analyze possible system issues according to the query bottleneck and monitoring or log information, and then analyze whether there is a better execution plan.
- Classification Note: This is classified as diagnosis because the content describes how to determine why a query is slow by separating bottleneck identification, system issue analysis, and optimizer issue analysis.

## Official Source Content

# Analyze Slow Queries

To address the issue of slow queries, you need to take the following two steps:

1. Among many queries, identify which type of queries are slow.
2. Analyze why this type of queries are slow.

You can easily perform step 1 using the [slow query log](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-slow-query) and the [statement summary table](https://docs.pingcap.com/tidb/stable/statement-summary-tables) features. It is recommended to use [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro), which integrates the two features and directly displays the slow queries in your browser. 

This document focuses on how to perform step 2 - analyze why this type of queries are slow.

Generally, slow queries have the following major causes:

- Optimizer issues, such as wrong index selected, wrong join type or sequence selected.
- System issues. All issues not caused by the optimizer are system issues. For example, a busy TiKV instance processes requests slowly; outdated Region information causes slow queries.

In actual situations, optimizer issues might cause system issues. For example, for a certain type of queries, the optimizer uses a full table scan instead of the index. As a result, the SQL queries consume many resources, which causes the CPU usage of some TiKV instances to soar. This seems like a system issue, but in essence, it is an optimizer issue.

To identify system issues is relatively simple. To analyze optimizer issues, you need to determine whether the execution plan is reasonable or not. Therefore, it is recommended to analyze slow queries by following these procedures:

1. Identify the performance bottleneck of the query, that is, the time-consuming part of the query process.
2. Analyze the system issues: analyze the possible causes according to the query bottleneck and the monitoring/log information of that time.
3. Analyze the optimizer issues: analyze whether there is a better execution plan.

The procedures above are explained in the following sections.
## Identify the performance bottleneck of the query

First, you need to have a general understanding of the query process. The key stages of the query execution process in TiDB are illustrated in [TiDB performance map](/media/performance-map.png).

You can get the duration information using the following methods:

- [Slow log](https://docs.pingcap.com/tidb/stable/identify-slow-queries). It is recommended to view the slow log in [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-overview).
- [`EXPLAIN ANALYZE` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze).

The methods above are different in the following aspects:

- The slow log records the duration of almost all stages of a SQL execution, from parsing to returning results, and is relatively comprehensive (you can query and analyze the slow log in TiDB Dashboard in an intuitive way).
- By executing `EXPLAIN ANALYZE`, you can learn the time consumption of each operator in an actual SQL execution. The results have more detailed statistics of the execution duration.

In summary, the slow log and `EXPLAIN ANALYZE` statements help you determine the SQL query is slow in which component (TiDB or TiKV) at which stage of the execution. Therefore, you can accurately identify the performance bottleneck of the query.

In addition, since v4.0.3, the `Plan` field in the slow log also includes the SQL execution information, which is the result of `EXPLAIN ANALYZE`. So you can find all information of SQL duration in the slow log.
## Analyze system issues

System issues can be divided into the following types according to different execution stages of a SQL statement:

1. TiKV is slow in data processing. For example, the TiKV coprocessor processes data slowly.
2. TiDB is slow in execution. For example, a `Join` operator processes data slowly.
3. Other key stages are slow. For example, getting the timestamp takes a long time.

For each slow query, first determine to which type the query belongs, and then analyze it in detail.
