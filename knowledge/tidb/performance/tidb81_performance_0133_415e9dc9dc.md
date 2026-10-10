# Database-time tuning approach and bottleneck identification

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-methods.md`
- Source Title: `Performance Analysis and Tuning`
- Source Heading Path: `Performance Analysis and Tuning | Performance Analysis and Tuning > Performance tuning based on database time | Performance Analysis and Tuning > Performance tuning based on database time > Is TiDB the bottleneck? | Performance Analysis and Tuning > Performance tuning based on database time > If the bottleneck is in TiDB, how to identify it?`
- Source Line Ranges: `5-46`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `shared`
- Topic Tags: `database time`, `bottleneck analysis`, `sql latency`, `connection idle time`, `sql phases`, `tso wait`, `kv requests`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0133_415e9dc9dc`
- Source ID: `tidb-docs-8.1:performance-tuning-methods.md#performance-analysis-and-tuning`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1b92341bff42422bb3f26af63dadda00aa657f6add18faa67b818e0d269fdf89`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-methods#performance-analysis-and-tuning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-methods.md

## Retrieval Guidance

- Use When: Use this chunk when you need to judge whether transaction latency is caused by TiDB and to map database time into SQL type, SQL phase, TiDB executor time, KV request time, PD TSO wait time, and retried execution time.
- Retrieval Keywords: database time, Is TiDB the bottleneck, average SQL processing latency, idle time of a TiDB connection in a transaction, Database Time = Select Time + Insert Time + Update Time + Delete Time + Commit Time, Get Token Time, Parse Time, Compile Time, Execute Time, TiDB Executor Time, KV Request Time, PD TSO Wait Time, Retried execution time, Performance Overview dashboard
- Follow-up Guidance: If the average idle time of TiDB connections in transactions is higher than the average SQL processing latency, check external components such as application server hardware resources and network latency from the application to the database.
- Classification Note: This chunk is classified as performance for TiDB because it explains a database-time method to identify whether TiDB is the bottleneck and which internal SQL processing stage or request path consumes time.

## Official Source Content

# Performance Analysis and Tuning

This document describes a tuning approach by database time, and illustrates how to use the TiDB [Performance Overview dashboard](https://docs.pingcap.com/tidb/stable/grafana-performance-overview-dashboard) for performance analysis and tuning.

With the methods described in this document, you can analyze user response time and database time from a global and top-down perspective, to confirm whether the bottleneck in user response time is caused by database issues. If the bottleneck is in the database, you can use the database time overview and SQL latency breakdowns to identify the bottleneck and tune performance.
## Performance tuning based on database time

TiDB is constantly measuring and collecting SQL processing paths and database time. Therefore, it is easy to identify database performance bottlenecks in TiDB. Based on database time metrics, you can achieve the following two goals even without data on user response time:

- Determine whether the bottleneck is in TiDB by comparing the average SQL processing latency with the idle time of a TiDB connection in a transaction.
- If the bottleneck is in TiDB, further identify the exact module in the distributed system based on database time overview, color-based performance data, key metrics, resource utilization, and top-down latency breakdowns.
### Is TiDB the bottleneck?

- If the average idle time of TiDB connections in transactions is higher than the average SQL processing latency, the database is not to blame for the transaction latency of applications. The database time takes only a small part of the user response time, indicating that the bottleneck is outside the database.

    In this case, check the external components of the database. For example, determine whether there are sufficient hardware resources in the application server, and whether the network latency from the application to the database is excessively high.

- If the average SQL processing latency is higher than the average idle time of TiDB connections in transactions, the bottleneck in transactions is in TiDB, and the database time takes a large percentage of the user response time.
### If the bottleneck is in TiDB, how to identify it?

The following figure shows a typical SQL process. You can see that most SQL processing paths are covered in TiDB performance metrics. The database time is broken down into different dimensions, which are colored accordingly. You can quickly understand the workload characteristics and catch the bottlenecks inside the database if any.

![database time decomposition chart](/media/performance/dashboard-diagnostics-time-relation.png)

Database time is the sum of all SQL processing time. A breakdown of the database time into the following three dimensions helps you quickly identify bottlenecks in TiDB:

- By SQL processing type: Determine which type of SQL statements consumes the most database time. The formula is:

    `DB Time = Select Time + Insert Time + Update Time + Delete Time + Commit Time + ...`

- By the 4 steps of SQL processing (get_token/parse/compile/execute): Determine which step consumes the most time. The formula is:

    `DB Time = Get Token Time + Parse Time + Compile Time + Execute Time`

- By executor time, TSO wait time, KV request time, and execution retry time: Determine which execution step constitutes the bottleneck. The formula is:

    `Execute Time ~= TiDB Executor Time + KV Request Time + PD TSO Wait Time + Retried execution time`
