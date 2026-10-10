# ADMIN CANCEL DDL syntax, usage, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-cancel-ddl.md`
- Source Title: `ADMIN CANCEL DDL | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN CANCEL DDL | ADMIN CANCEL DDL > Synopsis | ADMIN CANCEL DDL > Examples | ADMIN CANCEL DDL > MySQL compatibility | ADMIN CANCEL DDL > See also`
- Source Line Ranges: `6-45`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `ddl`, `job-cancellation`, `syntax`, `examples`, `mysql-compatibility`, `admin-show-ddl`, `kill`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0506_7c86f06ff7`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-cancel-ddl.md#admin-cancel-ddl`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8c3e1d2bb0381e502206fc0035163163b0e410349aee545154f9e56a0227e2a5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl#admin-cancel-ddl
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-cancel-ddl.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, behavior, examples, or compatibility of cancelling running or committed-but-not-yet-completed DDL jobs with SQL in TiDB.
- Retrieval Keywords: ADMIN CANCEL DDL, ADMIN CANCEL DDL JOBS, ADMIN SHOW DDL JOBS, job_id, Cancelled DDL job, ERROR 8214 (HY000): Cancelled DDL job, DDL Job:90 not found, RESULT column, KILL, TiDB extension to MySQL syntax, AdminCancelDDLStmt, NumList
- Follow-up Guidance: Use ADMIN SHOW DDL JOBS to find the job_id values referenced by ADMIN CANCEL DDL JOBS, and see KILL for cancelling ongoing DDL jobs by killing them starting from v6.2.0.
- Classification Note: This is reference content because it defines the ADMIN CANCEL DDL statement syntax, explains execution results and errors, provides example usage, and states MySQL compatibility.

## Official Source Content

# ADMIN CANCEL DDL

The `ADMIN CANCEL DDL` statement allows you to cancel a running DDL job. The `job_id` can be found by running [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl).

The `ADMIN CANCEL DDL` statement also allows you to cancel a DDL job that is committed but not yet completed executing. After the cancellation, the SQL statement that executes the DDL job returns the `ERROR 8214 (HY000): Cancelled DDL job` error. If you cancel a DDL job that has already been completed, you will see the `DDL Job:90 not found` error in the `RESULT` column, which indicates that the job has been removed from the DDL waiting queue.
## Synopsis

```ebnf+diagram
AdminCancelDDLStmt ::=
    'ADMIN' 'CANCEL' 'DDL' 'JOBS' NumList 

NumList ::=
    Int64Num ( ',' Int64Num )*
```
## Examples

To cancel the currently running DDL jobs and return whether the corresponding jobs are successfully cancelled, use `ADMIN CANCEL DDL JOBS`:

```sql
ADMIN CANCEL DDL JOBS job_id [, job_id] ...;
```

If the operation fails to cancel the jobs, specific reasons are displayed.

> **Note:**
>
> - Before v6.2.0, only this operation can cancel DDL jobs, and all other operations and environment changes (such as machine restart and cluster restart) cannot cancel these jobs. Starting from v6.2.0, [`KILL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill) statements can also be used to cancel ongoing DDL jobs by killing them. 
> - This operation can cancel multiple DDL jobs at the same time. You can get the ID of DDL jobs using the [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl) statement.
> - If the jobs you want to cancel are finished, the cancellation operation fails.
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [`ADMIN SHOW DDL [JOBS|JOB QUERIES]`](/sql-statements/sql-statement-admin-show-ddl.md)
