# ADMIN examples for next row ID and DDL job inspection

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin.md`
- Source Title: `ADMIN | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN > Examples | ADMIN > MySQL compatibility`
- Source Line Ranges: `253-302`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `admin`, `ddl-jobs`, `schema-state`, `job-state`, `next-row-id`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0520_68c761ce7f`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin.md#examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1ecaab54c5a90169b71022e68c83ec59e63757900af33a55360968c91470aed2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin.md

## Retrieval Guidance

- Use When: Use this chunk when looking for ADMIN statement examples that show next row ID output or how to inspect uncompleted DDL jobs and interpret DDL job schema and state fields.
- Retrieval Keywords: ADMIN SHOW DDL JOBS 5 WHERE state != 'synced' AND db_name = 'test', NEXT_GLOBAL_ROW_ID, ID_TYPE, _tidb_rowid, AUTO_INCREMENT, JOB_ID, DB_NAME, TABLE_NAME, JOB_TYPE, SCHEMA_STATE, STATE, write reorganization, rollback done, running, synced, ADMIN examples, TiDB extension to MySQL syntax
- Follow-up Guidance: The source also lists the meanings of DDL job columns and common SCHEMA_STATE and STATE values, including none, write reorganization, public, running, synced, rollback done, rollingback, cancelling, and paused.
- Classification Note: This is reference content because it provides concrete ADMIN command examples, result-set fields, and state definitions, and it explicitly notes that the statement is a TiDB extension to MySQL syntax.

## Official Source Content

```sql
+---------+------------+-------------+--------------------+----------------+
| DB_NAME | TABLE_NAME | COLUMN_NAME | NEXT_GLOBAL_ROW_ID | ID_TYPE        |
+---------+------------+-------------+--------------------+----------------+
| test    | t          | _tidb_rowid |                101 | _TIDB_ROWID    |
| test    | t          | _tidb_rowid |                  1 | AUTO_INCREMENT |
+---------+------------+-------------+--------------------+----------------+
2 rows in set (0.01 sec)
```

Run the following command to view the uncompleted DDL jobs in the test database. The results include the DDL jobs that are running and the last 5 DDL jobs that are completed but failed.

```sql
ADMIN SHOW DDL JOBS 5 WHERE state != 'synced' AND db_name = 'test';
```

```
+--------+---------+------------+---------------------+----------------+-----------+----------+-----------+-----------------------------------+-----------------------------------+---------------+
| JOB_ID | DB_NAME | TABLE_NAME | JOB_TYPE            | SCHEMA_STATE   | SCHEMA_ID | TABLE_ID | ROW_COUNT | START_TIME                        | END_TIME                          | STATE         |
+--------+---------+------------+---------------------+----------------+-----------+----------+-----------+-----------------------------------+-----------------------------------+---------------+
| 45     | test    | t1         | add index     | write reorganization | 32        | 37       | 0         | 2019-01-10 12:38:36.501 +0800 CST |                                   | running       |
| 44     | test    | t1         | add index     | none                 | 32        | 37       | 0         | 2019-01-10 12:36:55.18 +0800 CST  | 2019-01-10 12:36:55.852 +0800 CST | rollback done |
+--------+---------+------------+---------------------+----------------+-----------+----------+-----------+-----------------------------------+-----------------------------------+---------------+
```

* `JOB_ID`: each DDL operation corresponds to one DDL job. `JOB_ID` is globally unique.
* `DB_NAME`: the name of the database on which the DDL operations are performed.
* `TABLE_NAME`: the name of the table on which the DDL operations are performed.
* `JOB_TYPE`: the type of the DDL operations.
* `SCHEMA_STATE`: the current state of the schema. If the `JOB_TYPE` is `add index`, it is the state of the index; if the `JOB_TYPE` is `add column`, it is the state of the column; if the `JOB_TYPE` is `create table`, it is the state of the table. The common states include:
    * `none`: it indicates not existing. When the `drop` or `create` operation fails and rolls back, it usually becomes the `none` state.
    * `delete only`, `write only`, `delete reorganization`, `write reorganization`: these four states are intermediate states. These states are not visible in common operations, because the conversion from the intermediate states is so quick. You can see the `write reorganization` state only in `add index` operations, which means that the index data is being added.
    * `public`: it indicates existing and usable. When operations like `create table` and `add index/column` are finished, it usually becomes the `public` state, which means that the created table/column/index can be normally read and written now.
* `SCHEMA_ID`: the ID of the database on which the DDL operations are performed.
* `TABLE_ID`: the ID of the table on which the DDL operations are performed.
* `ROW_COUNT`: the number of the data rows that have been added when running the `add index` operation.
* `START_TIME`: the start time of the DDL operations.
* `END_TIME`: the end time of the DDL operations.
* `STATE`: the state of the DDL operations. The common states include:
    * `none`: it indicates that the operation task has been put in the DDL job queue but has not been performed yet, because it is waiting for the previous tasks to complete. Another reason might be that it becomes the `none` state after running the drop operation, but it will soon be updated to the `synced` state, which means that all TiDB instances have been synced to this state.
    * `running`: it indicates that the operation is being performed.
    * `synced`: it indicates that the operation has been performed successfully and all TiDB instances have been synced to this state.
    * `rollback done`: it indicates that the operation has failed and has finished rolling back.
    * `rollingback`: it indicates that the operation has failed and is rolling back.
    * `cancelling`: it indicates that the operation is being cancelled. This state only occurs when you cancel DDL jobs using the [`ADMIN CANCEL DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl) command.
    * `paused`: it indicates that the operation has been paused. This state only appears when you use the [`ADMIN PAUSED DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-pause-ddl) command to pause the DDL job. You can use the [`ADMIN RESUME DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-resume-ddl) command to resume the DDL job.
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
