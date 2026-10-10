# ADMIN SHOW DDL jobs and queries

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-show-ddl.md`
- Source Title: `ADMIN SHOW DDL [JOBS|JOB QUERIES] | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN SHOW DDL [JOBS|JOB QUERIES] | ADMIN SHOW DDL [JOBS|JOB QUERIES] > Synopsis | ADMIN SHOW DDL [JOBS|JOB QUERIES] > Examples | ADMIN SHOW DDL [JOBS|JOB QUERIES] > Examples > `ADMIN SHOW DDL` | ADMIN SHOW DDL [JOBS|JOB QUERIES] > Examples > `ADMIN SHOW DDL JOBS``
- Source Line Ranges: `5-98`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `ddl`, `jobs`, `queries`, `schema version`, `job queue`, `job state`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0511_8a4b121b85`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-show-ddl.md#admin-show-ddl-jobs-job-queries`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9c484b633faa512c3a8a028193829bc3adb02a8248e4cb33b1c7bf654ac57446`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl#admin-show-ddl-jobs-job-queries
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-show-ddl.md

## Retrieval Guidance

- Use When: Use this content when you need the syntax and output meanings of `ADMIN SHOW DDL`, `ADMIN SHOW DDL JOBS`, or `ADMIN SHOW DDL JOB QUERIES` to inspect running, queued, or recently completed DDL jobs.
- Retrieval Keywords: ADMIN SHOW DDL, ADMIN SHOW DDL JOBS, ADMIN SHOW DDL JOB QUERIES, SCHEMA_VER, OWNER_ID, OWNER_ADDRESS, RUNNING_JOBS, SELF_ID, QUERY, JOB_ID, DB_NAME, TABLE_NAME, JOB_TYPE, SCHEMA_STATE, SCHEMA_ID, TABLE_ID, ROW_COUNT, CREATE_TIME, START_TIME, END_TIME, STATE, queueing, running, synced, rollback done, rollingback, cancelling, cancelled, pausing, paused, done, write reorganization, DDL job queue
- Follow-up Guidance: The source also notes related commands and function names including `TIDB_IS_DDL_OWNER()`, `ADMIN CANCEL DDL JOBS`, `ADMIN PAUSED DDL JOBS`, and `ADMIN RESUME DDL JOBS`.
- Classification Note: This is reference content because it defines the statement syntax and explains the returned fields and states for DDL job inspection queries in TiDB SQL.

## Official Source Content

# ADMIN SHOW DDL [JOBS|JOB QUERIES]

The `ADMIN SHOW DDL [JOBS|JOB QUERIES]` statement shows information about running and recently completed DDL jobs.
## Synopsis

```ebnf+diagram
AdminShowDDLStmt ::=
    'ADMIN' 'SHOW' 'DDL'
    ( 
        'JOBS' Int64Num? WhereClauseOptional 
    |   'JOB' 'QUERIES' NumList 
    |   'JOB' 'QUERIES' 'LIMIT' m ( ('OFFSET' | ',') n )?
    )?

NumList ::=
    Int64Num ( ',' Int64Num )*

WhereClauseOptional ::=
    WhereClause?
```
## Examples
### `ADMIN SHOW DDL`

To view the status of the currently running DDL jobs, use `ADMIN SHOW DDL`. The output includes the current schema version, the DDL ID and address of the owner, the running DDL jobs and SQL statements, and the DDL ID of the current TiDB instance. The returned result fields are described as follows:

- `SCHEMA_VER`: a number indicating the version of the schema.
- `OWNER_ID`: the UUID of the DDL owner. See also [`TIDB_IS_DDL_OWNER()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions).
- `OWNER_ADDRESS`: the IP address of the DDL owner.
- `RUNNING_JOBS`: details about the running DDL job.
- `SELF_ID`: the UUID of the TiDB node to which you are currently connected. If `SELF_ID` is the same as the `OWNER_ID`, it means that you are connected to the DDL owner.
- `QUERY`: the statements of the queries.

```sql
ADMIN SHOW DDL\G;
```

```sql
*************************** 1. row ***************************
   SCHEMA_VER: 26
     OWNER_ID: 2d1982af-fa63-43ad-a3d5-73710683cc63
OWNER_ADDRESS: 0.0.0.0:4000
 RUNNING_JOBS: 
      SELF_ID: 2d1982af-fa63-43ad-a3d5-73710683cc63
        QUERY: 
1 row in set (0.00 sec)
```
### `ADMIN SHOW DDL JOBS`

The `ADMIN SHOW DDL JOBS` statement is used to view all the results in the current DDL job queue, including running and queuing tasks, as well as the latest ten results in the completed DDL job queue. The returned result fields are described as follows:

- `JOB_ID`: each DDL operation corresponds to a DDL job. `JOB_ID` is globally unique.
- `DB_NAME`: the name of the database where the DDL operation is performed.
- `TABLE_NAME`: the name of the table where the DDL operation is performed.
- `JOB_TYPE`: the type of DDL operation. Common job types include the following:
    - `create schema`: for [`CREATE SCHEMA`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-database) operations.
    - `create table`: for [`CREATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table) operations.
    - `create view`: for [`CREATE VIEW`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-view) operations.
    - `ingest`: ingestion with accelerated index backfilling as configured by [`tidb_ddl_enable_fast_reorg`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630).
    - `txn`: basic transactional backfilling.
    - `add index /* txn-merge */`: transactional backfilling with a temporary index that gets merged with the original index when the backfilling is finished.
- `SCHEMA_STATE`: the current state of the schema object that the DDL operates on. If `JOB_TYPE` is `ADD INDEX`, it is the state of the index; if `JOB_TYPE` is `ADD COLUMN`, it is the state of the column; if `JOB_TYPE` is `CREATE TABLE`, it is the state of the table. Common states include the following:
    - `none`: indicates that it does not exist. Generally, after the `DROP` operation or after the `CREATE` operation fails and rolls back, it will become the `none` state.
    - `delete only`, `write only`, `delete reorganization`, `write reorganization`: these four states are intermediate states. For their specific meanings, see [How the Online DDL Asynchronous Change Works in TiDB](https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction#how-the-online-ddl-asynchronous-change-works-in-tidb). As the intermediate state conversion is fast, these states are generally not visible during operation. Only when performing `ADD INDEX` operation can the `write reorganization` state be seen, indicating that index data is being added.
    - `public`: indicates that it exists and is available to users. Generally, after `CREATE TABLE` and `ADD INDEX` (or `ADD COLUMN`) operations are completed, it will become the `public` state, indicating that the newly created table, column, and index can be read and written normally.
- `SCHEMA_ID`: the ID of the database where the DDL operation is performed.
- `TABLE_ID`: the ID of the table where the DDL operation is performed.
- `ROW_COUNT`: when performing the `ADD INDEX` operation, it is the number of data rows that have been added.
- `CREATE_TIME`: the creation time of the DDL operation.
- `START_TIME`: the start time of the DDL operation.
- `END_TIME`: the end time of the DDL operation.
- `STATE`: the state of the DDL operation. Common states include the following:
    - `none`: indicates that the operation has not started yet.
    - `queueing`: indicates that the operation job has entered the DDL job queue but has not been executed because it is still waiting for an earlier DDL job to complete. Another reason might be that after executing the `DROP` operation, the `queueing` state will become the `done` state, but it will soon be updated to the `synced` state, indicating that all TiDB instances have been synchronized to that state.
    - `running`: indicates that the operation is being executed.
    - `synced`: indicates that the operation has been executed successfully and all TiDB instances have been synchronized to this state.
    - `rollback done`: indicates that the operation has failed and the rollback has been completed.
    - `rollingback`: indicates that the operation has failed and is rolling back.
    - `cancelling`: indicates that the operation is being canceled. This state only appears when you use the [`ADMIN CANCEL DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl) command to cancel the DDL job.
    - `cancelled`: indicates that the operation has been canceled.
    - `pausing`: indicates that the operation is being paused.
    - `paused`: indicates that the operation has been paused. This state only appears when you use the [`ADMIN PAUSED DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-pause-ddl) command to pause the DDL job. You can use the [`ADMIN RESUME DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-resume-ddl) command to resume the DDL job.
    - `done`: indicates that the operation has been successfully executed on the TiDB owner node, but other TiDB nodes have not yet synchronized the changes performed by this DDL job.
