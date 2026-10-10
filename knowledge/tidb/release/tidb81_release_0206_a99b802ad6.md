# Diagnostics improvements and deployment section start

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0.md`
- Source Title: `What's New in TiDB 5.0`
- Source Heading Path: `What's New in TiDB 5.0 > Diagnostics | What's New in TiDB 5.0 > Deployment and maintenance`
- Source Line Ranges: `401-415`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `sql`, `tiup`
- Topic Tags: `diagnostics`, `explain-analyze`, `explain-for-connection`, `slow-log`, `deployment`, `maintenance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0206_a99b802ad6`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0.md#diagnostics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `47a178376069425928d0307116d0384dfe4da4650e285aad38f558daf9a894a9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0#diagnostics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.0 diagnostics enhancements involving EXPLAIN ANALYZE, EXPLAIN FOR CONNECTION, or detailed execution information in the slow log.
- Retrieval Keywords: Diagnostics, EXPLAIN ANALYZE, EXPLAIN FOR CONNECTION, DML statements, actual performance plans, execution information of each operator, execution duration of each operator, processed rows, RPC requests, resolving lock conflicts, network latency, scanned volume of deleted data in RocksDB, hit rate of RocksDB caches, slow log
- Follow-up Guidance: The content links to the SQL statement EXPLAIN user document.
- Classification Note: This is classified as a release chunk because it summarizes TiDB 5.0 diagnostics improvements and marks the transition to the Deployment and maintenance section.

## Official Source Content

## Diagnostics

[User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain#explain)

During the troubleshooting of SQL performance issues, detailed diagnostic information is needed to determine the causes of performance issues. Before TiDB 5.0, the information collected by the `EXPLAIN` statements was not detailed enough. The root causes of the issues can only be determined based on log information, monitoring information, or even on guess, which might be inefficient.

In TiDB v5.0, the following improvements are made to help you troubleshoot performance issues more efficiently:

+ Support using the `EXPLAIN ANALYZE` statement to analyze all DML statements to show the actual performance plans and the execution information of each operator. [#18056](https://github.com/pingcap/tidb/issues/18056)
+ Support using the `EXPLAIN FOR CONNECTION` statement to check the real-time status of all the SQL statements being executed. For example, you can use the statement to check the execution duration of each operator and the number of processed rows. [#18233](https://github.com/pingcap/tidb/issues/18233)
+ Provide more details about the operator execution in the output of the `EXPLAIN ANALYZE` statement, including the number of RPC requests sent by operators, the duration of resolving lock conflicts, network latency, the scanned volume of deleted data in RocksDB, and the hit rate of RocksDB caches. [#18663](https://github.com/pingcap/tidb/issues/18663)
+ Support automatically recording the detailed execution information of SQL statements in the slow log. The execution information in the slow log is consistent with the output information of the `EXPLAIN ANALYZE` statement, which includes the time consumed by each operator, the number of processed rows, and the number of sent RPC requests. [#15009](https://github.com/pingcap/tidb/issues/15009)
## Deployment and maintenance
