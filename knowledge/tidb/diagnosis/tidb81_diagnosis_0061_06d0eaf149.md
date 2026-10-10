# EXPLAIN diagnostic enhancements for SQL troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0-rc.md`
- Source Title: `TiDB 5.0 RC Release Notes`
- Source Heading Path: `TiDB 5.0 RC Release Notes > Diagnostics | TiDB 5.0 RC Release Notes > Diagnostics > Optimized `EXPLAIN` features with more collected information help users troubleshoot performance issues`
- Source Line Ranges: `171-183`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `explain-analyze`, `explain-for-connection`, `slow-log`, `diagnostics`, `troubleshooting`, `rpc`, `locks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0061_06d0eaf149`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0-rc.md#diagnostics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0ce51b845302b771242e2b5a6733d1b2be40866222726486f71106a2c6cb2ea7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0-rc#diagnostics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0-rc.md

## Retrieval Guidance

- Use When: Use this chunk when searching for SQL troubleshooting improvements in `EXPLAIN`, `EXPLAIN ANALYZE`, `EXPLAIN FOR CONNECTION`, slow log execution details, RPC request counts, lock conflict duration, or RocksDB diagnostic fields.
- Retrieval Keywords: Diagnostics, EXPLAIN, EXPLAIN ANALYZE, EXPLAIN FOR CONNECTION, all DML statements, actual performance plans, execution information of each operator, execution duration of each operator, number of processed rows, number of RPC requests, resolving lock conflicts, network latency, scanned volume of deleted data in RocksDB, hit rate of RocksDB caches, slow log, detailed execution information
- Follow-up Guidance: The source states that slow log execution details are consistent with the output information of `EXPLAIN ANALYZE`.
- Classification Note: This is classified as diagnosis because the content focuses on diagnostic information collected for troubleshooting SQL performance issues.

## Official Source Content

## Diagnostics
### Optimized `EXPLAIN` features with more collected information help users troubleshoot performance issues

When users troubleshoot SQL performance issues, they need detailed diagnostic information to determine the causes of performance issues. In previous TiDB versions, the information collected by the `EXPLAIN` statements was not detailed enough. DBAs performed troubleshooting only based on log information, monitoring information, or even on guess, which might be inefficient. The following improvements are made in TiDB v5.0 to help users troubleshoot performance issues more efficiently:

+ `EXPLAIN ANALYZE` supports analyzing all DML statements and shows the actual performance plans and the execution information of each operator. [#18056](https://github.com/pingcap/tidb/issues/18056)
+ Users can use `EXPLAIN FOR CONNECTION` to analyze the status information of the SQL statements that are being executed. This information includes the execution duration of each operator and the number of processed rows. [#18233](https://github.com/pingcap/tidb/issues/18233)
+ More information is available in the output of `EXPLAIN ANALYZE`, including the number of RPC requests sent by operators, the duration of resolving lock conflicts, network latency, the scanned volume of deleted data in RocksDB, and the hit rate of RocksDB caches. [#18663](https://github.com/pingcap/tidb/issues/18663)
+ The detailed execution information of SQL statements is recorded in the slow log, which is consistent with the output information of `EXPLAIN ANALYZE`. This information includes the time consumed by each operator, the number of processed rows, and the number of sent RPC requests. [#15009](https://github.com/pingcap/tidb/issues/15009)

[User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain)
