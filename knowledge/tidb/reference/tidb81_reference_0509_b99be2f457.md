# ADMIN PAUSE DDL JOBS syntax, behavior, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-pause-ddl.md`
- Source Title: `ADMIN PAUSE DDL JOBS`
- Source Heading Path: `ADMIN PAUSE DDL JOBS | ADMIN PAUSE DDL JOBS > Synopsis | ADMIN PAUSE DDL JOBS > Examples | ADMIN PAUSE DDL JOBS > MySQL compatibility | ADMIN PAUSE DDL JOBS > See also`
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `ddl`, `pause`, `job-management`, `syntax`, `mysql-compatibility`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0509_b99be2f457`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-pause-ddl.md#admin-pause-ddl-jobs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8a48f5b5b8964ddacd1cf5efade7cc2eff4c71928fd611229a9d3a949fcd1905`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-pause-ddl#admin-pause-ddl-jobs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-pause-ddl.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the syntax and behavior of pausing one or more running DDL jobs with SQL, including how paused jobs relate to ADMIN SHOW DDL JOBS and ADMIN RESUME DDL JOBS.
- Retrieval Keywords: ADMIN PAUSE DDL JOBS, ADMIN PAUSE DDL, AdminPauseDDLStmt, NumList, job_id, ADMIN SHOW DDL JOBS, ADMIN RESUME DDL JOBS, DDL Job:90 not found, RESULT column, TiDB extension to MySQL syntax, pause multiple DDL jobs, cluster upgrade paused DDL jobs
- Follow-up Guidance: Related statements listed here are ADMIN SHOW DDL [JOBS|QUERIES], ADMIN CANCEL DDL, and ADMIN RESUME DDL.
- Classification Note: This is classified as a SQL reference chunk because the content defines statement syntax, execution behavior, examples, MySQL compatibility, and related SQL statements for DDL job management.

## Official Source Content

# ADMIN PAUSE DDL JOBS

`ADMIN PAUSE DDL` allows you to pause a running DDL job. The `job_id` can be found by running [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl).

You can use this statement to pause a DDL job that is issued but not yet completed executing. After the pause, the SQL statement that executes the DDL job does not return immediately, but looks like it is still running. If you try to pause a DDL job that has already been completed, you will see the `DDL Job:90 not found` error in the `RESULT` column, which indicates that the job has been removed from the DDL waiting queue.
## Synopsis

```ebnf+diagram
AdminPauseDDLStmt ::=
    'ADMIN' 'PAUSE' 'DDL' 'JOBS' NumList 

NumList ::=
    Int64Num ( ',' Int64Num )*
```
## Examples

`ADMIN PAUSE DDL JOBS` pauses the currently running DDL job and returns whether the job is paused successfully. The job can be resumed by `ADMIN RESUME DDL JOBS`.

```sql
ADMIN PAUSE DDL JOBS job_id [, job_id] ...;
```

If the pause fails, the specific reason for the failure is displayed.

> **Note:**
>
> + This statement can pause a DDL job, but other operations and environment changes (such as machine restarts and cluster restarts) do not pause DDL jobs except for cluster upgrades.
> + During the cluster upgrade, the ongoing DDL jobs are paused, and the DDL jobs initiated during the upgrade are also paused. After the upgrade, all paused DDL jobs will resume. The pause and resume operations during the upgrade are taken automatically. For details, see [TiDB Smooth Upgrade](https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb).
> + This statement can pause multiple DDL jobs. You can use the [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl) statement to obtain the `job_id` of a DDL job.

> **Note:**
>
> + This statement can pause a DDL job, but other operations and environment changes (such as machine restarts and cluster restarts) do not pause DDL jobs except for cluster upgrades.
> + During the cluster upgrade, the ongoing DDL jobs are paused, and the DDL jobs initiated during the upgrade are also paused. After the upgrade, all paused DDL jobs will resume. The pause and resume operations during the upgrade are taken automatically. For details, see [TiDB Smooth Upgrade](https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb).
> + This statement can pause multiple DDL jobs. You can use the [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl) statement to obtain the `job_id` of a DDL job.
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [`ADMIN SHOW DDL [JOBS|QUERIES]`](/sql-statements/sql-statement-admin-show-ddl.md)
* [`ADMIN CANCEL DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl)
* [`ADMIN RESUME DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-resume-ddl)
