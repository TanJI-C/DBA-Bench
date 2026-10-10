# ADMIN SHOW DDL JOBS output fields and example results

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-show-ddl.md`
- Source Title: `ADMIN SHOW DDL [JOBS|JOB QUERIES] | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN SHOW DDL [JOBS|JOB QUERIES] > Examples > `ADMIN SHOW DDL JOBS``
- Source Line Ranges: `99-162`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `ddl`, `jobs`, `schema-state`, `job-state`, `output-columns`, `filtering`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0512_bce22af70a`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-show-ddl.md#admin-show-ddl-jobs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1354ff8bc9cd87431e256904b1a10de2537bf09ea6ccec2aca946bf7afa28ef7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl#admin-show-ddl-jobs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-show-ddl.md

## Retrieval Guidance

- Use When: Use this chunk when you need to interpret `ADMIN SHOW DDL JOBS` output columns, schema states, job states, example results, or row limiting and `WHERE` filtering syntax.
- Retrieval Keywords: ADMIN SHOW DDL JOBS, JOB_ID, DB_NAME, TABLE_NAME, JOB_TYPE, SCHEMA_STATE, SCHEMA_ID, TABLE_ID, ROW_COUNT, CREATE_TIME, START_TIME, END_TIME, STATE, write reorganization, public, none, queueing, running, synced, rollback done, rollingback, cancelling, paused, ADMIN SHOW DDL JOBS [NUM] [WHERE where_condition], ADD INDEX, ADD COLUMN, CREATE TABLE, DROP TABLE, DROP INDEX
- Follow-up Guidance: The source also shows that `STATE` values such as `cancelling` and `paused` are tied to `ADMIN CANCEL DDL JOBS`, `ADMIN PAUSED DDL JOBS`, and `ADMIN RESUME DDL JOBS`.
- Classification Note: This is reference content because it defines each `ADMIN SHOW DDL JOBS` output field, explains state meanings, and provides the exact statement form and example result set.

## Official Source Content

- `JOB_ID`: each DDL operation corresponds to a DDL job. `JOB_ID` is globally unique.
- `DB_NAME`: the name of the database where the DDL operation is performed.
- `TABLE_NAME`: the name of the table where the DDL operation is performed.
- `JOB_TYPE`: the type of DDL operation.
- `SCHEMA_STATE`: the current state of the schema object that the DDL operates on. If `JOB_TYPE` is `ADD INDEX`, it is the state of the index; if `JOB_TYPE` is `ADD COLUMN`, it is the state of the column; if `JOB_TYPE` is `CREATE TABLE`, it is the state of the table. Common states include the following:
    - `none`: indicates that it does not exist. Generally, after the `DROP` operation or after the `CREATE` operation fails and rolls back, it will become the `none` state.
    - `delete only`, `write only`, `delete reorganization`, `write reorganization`: these four states are intermediate states. For their specific meanings, see [How the Online DDL Asynchronous Change Works in TiDB](https://docs.pingcap.com/tidb/stable/ddl-introduction#how-the-online-ddl-asynchronous-change-works-in-tidb). As the intermediate state conversion is fast, these states are generally not visible during operation. Only when performing `ADD INDEX` operation can the `write reorganization` state be seen, indicating that index data is being added.
    - `public`: indicates that it exists and is available to users. Generally, after `CREATE TABLE` and `ADD INDEX` (or `ADD COLUMN`) operations are completed, it will become the `public` state, indicating that the newly created table, column, and index can be read and written normally.
- `SCHEMA_ID`: the ID of the database where the DDL operation is performed.
- `TABLE_ID`: the ID of the table where the DDL operation is performed.
- `ROW_COUNT`: when performing the `ADD INDEX` operation, it is the number of data rows that have been added.
- `START_TIME`: the start time of the DDL operation.
- `STATE`: the state of the DDL operation. Common states include the following:
    - `queueing`: indicates that the operation job has entered the DDL job queue but has not been executed because it is still waiting for an earlier DDL job to complete. Another reason might be that after executing the `DROP` operation, it will become the `none` state, but it will soon be updated to the `synced` state, indicating that all TiDB instances have been synchronized to that state.
    - `running`: indicates that the operation is being executed.
    - `synced`: indicates that the operation has been executed successfully and all TiDB instances have been synchronized to this state.
    - `rollback done`: indicates that the operation has failed and the rollback has been completed.
    - `rollingback`: indicates that the operation has failed and is rolling back.
    - `cancelling`: indicates that the operation is being canceled. This state only appears when you use the [`ADMIN CANCEL DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl) command to cancel the DDL job.
    - `paused`: indicates that the operation has been paused. This state only appears when you use the [`ADMIN PAUSED DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-pause-ddl) command to pause the DDL job. You can use the [`ADMIN RESUME DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-resume-ddl) command to resume the DDL job.

The following example shows the results of `ADMIN SHOW DDL JOBS`:

```sql
ADMIN SHOW DDL JOBS;
```

```sql
mysql> ADMIN SHOW DDL JOBS;
+--------+---------+--------------------+--------------+----------------------+-----------+----------+-----------+-----------------------------------------------------------------+---------+
| JOB_ID | DB_NAME | TABLE_NAME         | JOB_TYPE     | SCHEMA_STATE         | SCHEMA_ID | TABLE_ID | ROW_COUNT | CREATE_TIME         | START_TIME          | END_TIME            | STATE   |
+--------+---------+--------------------+--------------+----------------------+-----------+----------+-----------+---------------------+-------------------------------------------+---------+
|     59 | test    | t1                 | add index    | write reorganization |         1 |       55 |     88576 | 2020-08-17 07:51:58 | 2020-08-17 07:51:58 | NULL                | running |
|     60 | test    | t2                 | add index    | none                 |         1 |       57 |         0 | 2020-08-17 07:51:59 | 2020-08-17 07:51:59 | NULL                | none    |
|     58 | test    | t2                 | create table | public               |         1 |       57 |         0 | 2020-08-17 07:41:28 | 2020-08-17 07:41:28 | 2020-08-17 07:41:28 | synced  |
|     56 | test    | t1                 | create table | public               |         1 |       55 |         0 | 2020-08-17 07:41:02 | 2020-08-17 07:41:02 | 2020-08-17 07:41:02 | synced  |
|     54 | test    | t1                 | drop table   | none                 |         1 |       50 |         0 | 2020-08-17 07:41:02 | 2020-08-17 07:41:02 | 2020-08-17 07:41:02 | synced  |
|     53 | test    | t1                 | drop index   | none                 |         1 |       50 |         0 | 2020-08-17 07:35:44 | 2020-08-17 07:35:44 | 2020-08-17 07:35:44 | synced  |
|     52 | test    | t1                 | add index    | public               |         1 |       50 |    451010 | 2020-08-17 07:34:43 | 2020-08-17 07:34:43 | 2020-08-17 07:35:16 | synced  |
|     51 | test    | t1                 | create table | public               |         1 |       50 |         0 | 2020-08-17 07:34:02 | 2020-08-17 07:34:02 | 2020-08-17 07:34:02 | synced  |
|     49 | test    | t1                 | drop table   | none                 |         1 |       47 |         0 | 2020-08-17 07:34:02 | 2020-08-17 07:34:02 | 2020-08-17 07:34:02 | synced  |
|     48 | test    | t1                 | create table | public               |         1 |       47 |         0 | 2020-08-17 07:33:37 | 2020-08-17 07:33:37 | 2020-08-17 07:33:37 | synced  |
|     46 | mysql   | stats_extended     | create table | public               |         3 |       45 |         0 | 2020-08-17 06:42:38 | 2020-08-17 06:42:38 | 2020-08-17 06:42:38 | synced  |
|     44 | mysql   | opt_rule_blacklist | create table | public               |         3 |       43 |         0 | 2020-08-17 06:42:38 | 2020-08-17 06:42:38 | 2020-08-17 06:42:38 | synced  |
+--------+---------+--------------------+--------------+----------------------+-----------+----------+-----------+---------------------+---------------------+-------------------------------+
12 rows in set (0.00 sec)
```

From the output above:

- Job 59 is currently in progress (`STATE` of `running`). The schema state is currently in `write reorganization`, but will switch to `public` once the task is completed to note that the change can be observed publicly by user sessions. The `end_time` column is also `NULL` indicating that the completion time for the job is currently not known.

- Job 60 is an `add index` job, which is currently queued waiting for job 59 to complete. When job 59 completes, the `STATE` of job 60 will switch to `running`.

- For destructive changes such as dropping an index or dropping a table, the `SCHEMA_STATE` will change to `none` when the job is complete. For additive changes, the `SCHEMA_STATE` will change to `public`.

To limit the number of rows shown, specify a number and a where condition:

```sql
ADMIN SHOW DDL JOBS [NUM] [WHERE where_condition];
```
