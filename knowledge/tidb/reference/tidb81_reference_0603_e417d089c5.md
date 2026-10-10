# IMPORT INTO FROM SELECT usage, examples, compatibility, and references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-import-into.md`
- Source Title: `IMPORT INTO`
- Source Heading Path: `IMPORT INTO > `IMPORT INTO ... FROM SELECT` usage | IMPORT INTO > `IMPORT INTO ... FROM SELECT` usage > Import the query result of `SELECT` | IMPORT INTO > `IMPORT INTO ... FROM SELECT` usage > Import historical data at a specified time point | IMPORT INTO > MySQL compatibility | IMPORT INTO > See also`
- Source Line Ranges: `338-367`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `import-into`, `from-select`, `historical-data`, `as-of-timestamp`, `mysql-compatibility`, `import-jobs`, `sql-syntax`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0603_e417d089c5`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-import-into.md#import-into-from-select-usage`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `91a207dffeaacd156383f355bcecbba11864a2d0f6eb7e23ecd9bff6cd938e38`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#import-into-from-select-usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-import-into.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax and examples of `IMPORT INTO ... FROM SELECT`, including importing a `SELECT` or `UNION` result into an empty table and importing historical data with `AS OF TIMESTAMP`.
- Retrieval Keywords: IMPORT INTO ... FROM SELECT, IMPORT INTO t FROM SELECT, UNION SELECT, WITH THREAD = 8, DISABLE_PRECHECK, AS OF TIMESTAMP, import historical data, empty table, MySQL compatibility, SHOW IMPORT JOB, CANCEL IMPORT JOB, ADMIN CHECKSUM TABLE, TiDB Distributed eXecution Framework (DXF)
- Follow-up Guidance: The source also points to `ADMIN CHECKSUM TABLE`, `CANCEL IMPORT JOB`, `SHOW IMPORT JOB(s)`, and TiDB Distributed eXecution Framework (DXF) as related references.
- Classification Note: This is classified as reference content because it defines `IMPORT INTO ... FROM SELECT` usage with exact SQL examples, states its MySQL compatibility, and lists related statements.

## Official Source Content

## `IMPORT INTO ... FROM SELECT` usage

`IMPORT INTO ... FROM SELECT` lets you import the query result of a `SELECT` statement to an empty table in TiDB. You can also use it to import historical data queried with [`AS OF TIMESTAMP`](https://docs.pingcap.com/tidb/stable/as-of-timestamp).
### Import the query result of `SELECT`

To import the `UNION` result to the target table `t`, with the import concurrency specified as `8` and precheck of non-critical items configured as disabled, execute the following SQL statement:

```sql
IMPORT INTO t FROM SELECT * FROM src UNION SELECT * FROM src2 WITH THREAD = 8, DISABLE_PRECHECK;
```
### Import historical data at a specified time point

To import historical data at a specified time point to the target table `t`, execute the following SQL statement:

```sql
IMPORT INTO t FROM SELECT * FROM src AS OF TIMESTAMP '2024-02-27 11:38:00';
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [`ADMIN CHECKSUM TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-checksum-table)
* [`CANCEL IMPORT JOB`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-cancel-import-job)
* [`SHOW IMPORT JOB(s)`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-import-job)
* [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework)
