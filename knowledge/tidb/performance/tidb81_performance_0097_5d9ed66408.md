# SQL performance optimization overview and schema design guidance

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-optimize-sql-overview.md`
- Source Title: `Overview of Optimizing SQL Performance`
- Source Heading Path: `Overview of Optimizing SQL Performance | Overview of Optimizing SQL Performance > SQL performance tuning | Overview of Optimizing SQL Performance > Schema design | Overview of Optimizing SQL Performance > Schema design > See also | Overview of Optimizing SQL Performance > Need help?`
- Source Line Ranges: `5-66`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`
- Topic Tags: `sql-tuning`, `schema-design`, `indexing`, `join-types`, `full-table-scan`, `htap`, `transaction-contention`, `hot-spots`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0097_5d9ed66408`
- Source ID: `tidb-docs-8.1:develop/dev-guide-optimize-sql-overview.md#overview-of-optimizing-sql-performance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5e9210efa267b17557295f21a38c18d52416d5f0a44e633990092883260bc33a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview#overview-of-optimizing-sql-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-optimize-sql-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about a high-level overview of optimizing SQL performance in TiDB, including SQL tuning basics, schema design concerns, and when TiFlash is mentioned for HTAP workloads.
- Retrieval Keywords: Overview of Optimizing SQL Performance, SQL performance tuning, Schema design, scan as few rows as possible, full table scan, WHERE clause, use the right index, use the right join type, cost-based optimizer, TiFlash, hybrid OLTP and OLAP workloads, HTAP Query, transaction contention, hot spots, Troubleshoot Lock Conflicts, Troubleshoot Hotspot Issues, SQL Performance Tuning, Need help, Discord, Slack, support ticket
- Follow-up Guidance: The source points to related topics including SQL Performance Tuning, HTAP Query, Troubleshoot Lock Conflicts, and Troubleshoot Hotspot Issues, and it also lists Discord, Slack, and support ticket links for help.
- Classification Note: This chunk is classified under performance for SQL because the official content provides overview guidance on reducing scanned rows, indexing, join type selection, storage engine choice, and schema design issues that affect SQL performance.

## Official Source Content

# Overview of Optimizing SQL Performance

This document introduces how to optimize the performance of SQL statements in TiDB. To get good performance, you can start with the following aspects:

* SQL performance tuning
* Schema design: Based on your application workload patterns, you might need to change the table schema to avoid transaction contention or hot spots.
## SQL performance tuning

To get good SQL statement performance, you can follow these guidelines:

* Scan as few rows as possible. It is recommended to scan only the data you need and avoid scanning excess data.
* Use the right index. Ensure that there is a corresponding index for the column in the `WHERE` clause in SQL. If not, the statement entails a full table scan and thus causes poor performance.
* Use the right join type. It is important to choose the right join type based on the relative size of the tables involved in the query. In general, TiDB's cost-based optimizer picks the best-performing join type. However, in a few cases, you might need to manually specify a better join type.
* Use the right storage engine. For hybrid OLTP and OLAP workloads, the TiFlash engine is recommended. For details, see [HTAP Query](https://docs.pingcap.com/tidb/stable/develop/dev-guide-hybrid-oltp-and-olap-queries).
## Schema design

After [tuning SQL performance](#sql-performance-tuning), if your application still cannot get good performance, you might need to check your schema design and data access patterns to avoid the following issues:

* Transaction contention. For how to diagnose and resolve transaction contention, see [Troubleshoot Lock Conflicts](https://docs.pingcap.com/tidb/stable/troubleshoot-lock-conflicts).
* Hot spots. For how to diagnose and resolve hot spots, see [Troubleshoot Hotspot Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues).

* Transaction contention. For how to diagnose and resolve transaction contention, see [Troubleshoot Lock Conflicts](https://docs.pingcap.com/tidb/stable/troubleshoot-lock-conflicts).
* Hot spots. For how to diagnose and resolve hot spots, see [Troubleshoot Hotspot Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues).
### See also

* [SQL Performance Tuning](https://docs.pingcap.com/tidb/stable/sql-tuning-overview)

* [SQL Performance Tuning](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sql-tuning-overview)
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
