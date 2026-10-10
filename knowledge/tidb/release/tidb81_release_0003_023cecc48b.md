# TiDB 1.0 release highlights across TiDB, PD, and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-1.0-ga.md`
- Source Title: `TiDB 1.0 release notes`
- Source Heading Path: `TiDB 1.0 Release Notes | TiDB 1.0 Release Notes > TiDB | TiDB 1.0 Release Notes > PD | TiDB 1.0 Release Notes > TiKV`
- Source Line Ranges: `5-37`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `release-notes`, `mysql-compatibility`, `sql-optimization`, `performance`, `stability`, `query-optimizer`, `pushdown`, `store-weight`, `read-balancing`, `coprocessor`, `debug-api`, `tispark`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0003_023cecc48b`
- Source ID: `tidb-docs-8.1:releases/release-1.0-ga.md#tidb-1-0-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `261c6e9770665b7300bbb243b8744842806efc3b5305bacb60a41eb18e14ebca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-1.0-ga#tidb-1-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-1.0-ga.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 1.0 release highlights for MySQL compatibility, SQL optimization, stability, performance, and the specific changes across TiDB, PD, and TiKV.
- Retrieval Keywords: TiDB 1.0 Release Notes, October 16, 2017, MySQL compatibility, SQL optimization, stability, performance, SQL query optimizer, adjust the cost model, analyze pushdown, function signature pushdown, optimize the internal data format, NO_SQL_CACHE, Hash Aggregator, Stream Aggregator, PD, read flow based balancing, Store weight, weight based balancing, TiKV, Coprocessor, pushdown functions, sampling operation, manually triggering data compact, Debug API, TiSpark Beta Release, configuration framework, ThriftSever/JDBC, Spark SQL
- Follow-up Guidance: The source also lists PD features such as read flow based balancing and Store weight, and TiKV features such as more coprocessor pushdown functions, sampling pushdown, manual data compact, Debug API, and TiSpark Beta Release items.
- Classification Note: This is a release-notes summary chunk because the official content enumerates TiDB 1.0 feature highlights by component under TiDB, PD, and TiKV.

## Official Source Content

# TiDB 1.0 Release Notes

On October 16, 2017, TiDB 1.0 is now released! This release is focused on MySQL compatibility, SQL optimization, stability, and performance.
## TiDB

- The SQL query optimizer:
    - Adjust the cost model
    - Analyze pushdown
    - Function signature pushdown
- Optimize the internal data format to reduce the interim data size
- Enhance the MySQL compatibility
- Support the `NO_SQL_CACHE` syntax and limit the cache usage in the storage engine
- Refactor the Hash Aggregator operator to reduce the memory usage
- Support the Stream Aggregator operator
## PD

- Support read flow based balancing
- Support setting the Store weight and weight based balancing
## TiKV

- Coprocessor now supports more pushdown functions
- Support pushing down the sampling operation
- Support manually triggering data compact to collect space quickly
- Improve the performance and stability
- Add a Debug API for debugging
- TiSpark Beta Release:
- Support configuration framework
- Support ThriftSever/JDBC and Spark SQL
