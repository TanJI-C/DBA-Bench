# ADMIN RESUME DDL JOBS syntax and usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-resume-ddl.md`
- Source Title: `ADMIN RESUME DDL JOBS`
- Source Heading Path: `ADMIN RESUME DDL JOBS | ADMIN RESUME DDL JOBS > Synopsis | ADMIN RESUME DDL JOBS > Examples | ADMIN RESUME DDL JOBS > MySQL compatibility | ADMIN RESUME DDL JOBS > See also`
- Source Line Ranges: `5-61`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `ddl`, `resume`, `job-id`, `syntax`, `examples`, `mysql-compatibility`, `upgrade`, `paused-jobs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0510_e00c9321a8`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-resume-ddl.md#admin-resume-ddl-jobs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bef845e63754f8d29ec4d9235c989034ede27fd05b980545dd0a5513ddaf6703`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-resume-ddl#admin-resume-ddl-jobs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-resume-ddl.md

## Retrieval Guidance

- Use When: Use this when looking up the syntax, behavior, and errors for resuming paused DDL jobs with the ADMIN RESUME DDL JOBS statement.
- Retrieval Keywords: ADMIN RESUME DDL JOBS, ADMIN RESUME DDL, AdminResumeDDLStmt, ADMIN SHOW DDL JOBS, job_id, paused DDL job, NumList, DDL Job:90 not found, RESULT column, Error Number: 8261, TiDB extension to MySQL syntax, resume multiple DDL jobs
- Follow-up Guidance: The content points to ADMIN SHOW DDL JOBS to obtain the job_id and also references ADMIN CANCEL DDL and ADMIN PAUSE DDL.
- Classification Note: This is a SQL reference entry because the content defines the ADMIN RESUME DDL JOBS syntax, usage notes, examples, compatibility, and related statements.

## Official Source Content

# ADMIN RESUME DDL JOBS

`ADMIN RESUME DDL` allows you to resume a paused DDL job. You can find the `job_id` by running [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl).

You can use this statement to resume a paused DDL job. After the resume is completed, the SQL statement that executes the DDL job continues to show as being executed. If you try to resume a DDL job that has already been completed, you will see the `DDL Job:90 not found` error in the `RESULT` column, which indicates that the job has been removed from the DDL waiting queue.
## Synopsis

```ebnf+diagram
AdminResumeDDLStmt ::=
    'ADMIN' 'RESUME' 'DDL' 'JOBS' NumList 

NumList ::=
    Int64Num ( ',' Int64Num )*
```
## Examples

`ADMIN RESUME DDL JOBS` resumes the currently paused DDL job and returns whether the job is resumed successfully.

```sql
ADMIN RESUME DDL JOBS job_id [, job_id] ...;
```

If the resume fails, the specific reason for the failure is displayed.

> **Note:**
>
> + During the cluster upgrade, the ongoing DDL jobs are paused, and the DDL jobs initiated during the upgrade are also paused. After the upgrade, all paused DDL jobs will resume. The pause and resume operations during the upgrade are taken automatically. For details, see [TiDB Smooth Upgrade](https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb).
> + This statement can resume multiple DDL jobs. You can use the [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl) statement to obtain the `job_id` of a DDL job.
> + A DDL job in other status (other than `paused`) cannot be resumed and the resume operation will fail.
> + If you try to resume a job more than once, TiDB reports an error `Error Number: 8261`.

> **Note:**
>
> + During the cluster upgrade, the ongoing DDL jobs are paused, and the DDL jobs initiated during the upgrade are also paused. After the upgrade, all paused DDL jobs will resume. The pause and resume operations during the upgrade are taken automatically. For details, see [TiDB Smooth Upgrade](https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb).
> + This statement can resume multiple DDL jobs. You can use the [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl) statement to obtain the `job_id` of a DDL job.
> + A DDL job in other status (other than `paused`) cannot be resumed and the resume operation will fail.
> + If you try to resume a job more than once, TiDB reports an error `Error Number: 8261`.
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [`ADMIN SHOW DDL [JOBS|QUERIES]`](/sql-statements/sql-statement-admin-show-ddl.md)
* [`ADMIN CANCEL DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl)
* [`ADMIN PAUSE DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-pause-ddl)
