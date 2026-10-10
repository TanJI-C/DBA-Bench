# EXPLAIN MySQL compatibility and EXPLAIN FOR CONNECTION

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-explain.md`
- Source Title: `EXPLAIN | TiDB SQL Statement Reference`
- Source Heading Path: ``EXPLAIN` > MySQL compatibility | `EXPLAIN` > MySQL compatibility > `EXPLAIN FOR CONNECTION` | `EXPLAIN` > See also`
- Source Line Ranges: `340-359`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `explain`, `mysql-compatibility`, `explain-for-connection`, `privileges`, `output-format`, `query-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0592_d16c106984`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-explain.md#mysql-compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cf660bbda53d90f586d4769dd27081f9ce52f297c727da5dfe6d1a5d8932132e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-explain.md

## Retrieval Guidance

- Use When: Use this when the user asks about TiDB `EXPLAIN` compatibility with MySQL, supported `FORMAT` options, or the behavior and privilege requirements of `EXPLAIN FOR CONNECTION`.
- Retrieval Keywords: MySQL compatibility, EXPLAIN FOR CONNECTION, FORMAT=JSON, FORMAT=TREE, FORMAT=tidb_json, execution plan of the currently executed SQL query, last executed SQL query, sleeping connection, current session, SUPER privilege, PROCESS privilege
- Follow-up Guidance: The source also links to `Understanding the Query Execution Plan`, `EXPLAIN ANALYZE`, `ANALYZE TABLE`, and `TRACE`.
- Classification Note: This is reference content because it compares TiDB and MySQL behavior for `EXPLAIN` and documents `EXPLAIN FOR CONNECTION` output and privilege differences.

## Official Source Content

## MySQL compatibility

* Both the format of `EXPLAIN` and the potential execution plans in TiDB differ substantially from MySQL.
* TiDB does not support the `FORMAT=JSON` or `FORMAT=TREE` options.
* `FORMAT=tidb_json` in TiDB is the JSON format output of the default `EXPLAIN` result. The format and fields are different from the `FORMAT=JSON` output in MySQL.
### `EXPLAIN FOR CONNECTION`

`EXPLAIN FOR CONNECTION` is used to get the execution plan of the currently executed SQL query or the last executed SQL query in a connection. The output format is the same as that of `EXPLAIN`. However, the implementation of `EXPLAIN FOR CONNECTION` in TiDB is different from that in MySQL. Their differences (apart from the output format) are listed as follows:

- If the connection is sleeping, MySQL returns an empty result, while TiDB returns the last executed query plan.
- If you try to get the execution plan of the current session, MySQL returns an error, while TiDB returns the result normally.
- MySQL requires the login user to be the same as the connection being queried, or the login user has the **`PROCESS`** privilege; while TiDB requires the login user to be the same as the connection being queried, or the login user has the **`SUPER`** privilege.
## See also

* [Understanding the Query Execution Plan](https://docs.pingcap.com/tidb/stable/explain-overview)
* [EXPLAIN ANALYZE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze)
* [ANALYZE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table)
* [TRACE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-trace)
