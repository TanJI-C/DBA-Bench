# SHOW BACKUPS and SHOW RESTORES syntax, examples, and filtering

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-backups.md`
- Source Title: `SHOW [BACKUPS|RESTORES] | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW [BACKUPS|RESTORES] | SHOW [BACKUPS|RESTORES] > Synopsis | SHOW [BACKUPS|RESTORES] > Examples | SHOW [BACKUPS|RESTORES] > Examples > Filtering | SHOW [BACKUPS|RESTORES] > MySQL compatibility | SHOW [BACKUPS|RESTORES] > See also`
- Source Line Ranges: `5-116`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `br`, `tidb`
- Topic Tags: `show-backups`, `show-restores`, `backup-tasks`, `restore-tasks`, `syntax`, `examples`, `filtering`, `privileges`, `mysql-compatibility`, `kill-query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0642_c53777f2ac`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-backups.md#show-backups-restores`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `19021ca40fc08bb7aecfc08d32c578a5e67a8b3ff0757fe0b4cc3b65783ccfae`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-backups#show-backups-restores
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-backups.md

## Retrieval Guidance

- Use When: Use this content when you need the syntax, examples, result columns, task states, filtering options, privilege requirement, or MySQL compatibility details for `SHOW BACKUPS` or `SHOW RESTORES` in TiDB.
- Retrieval Keywords: SHOW BACKUPS, SHOW RESTORES, ShowBRIEStmt, SHOW BACKUPS LIKE, SHOW BACKUPS WHERE `Progress` < 25.0, SHOW BACKUPS;, BACKUP DATABASE `test` TO 's3://example-bucket/backup-01';, Destination, State, Progress, Queue_time, Execution_time, Finish_time, Connection, Message, Backup, Wait, Checksum, SUPER privilege, KILL TIDB QUERY, br commandline tool are not shown, TiDB extension to MySQL syntax
- Follow-up Guidance: The source also notes that the `Connection` ID from `SHOW BACKUPS` or `SHOW RESTORES` can be used with `KILL TIDB QUERY` to cancel a backup or restore task.
- Classification Note: This is reference content because it defines the `SHOW BACKUPS` and `SHOW RESTORES` statements with synopsis, examples, filtering clauses, output columns, states, privilege requirements, and compatibility notes.

## Official Source Content

# SHOW [BACKUPS|RESTORES]

These statements show a list of all queued, running and recently finished [`BACKUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-backup) and [`RESTORE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-restore) tasks that were executed on a TiDB instance.

Both statements require `SUPER` privilege to run.

Use `SHOW BACKUPS` to query `BACKUP` tasks and use `SHOW RESTORES` to query `RESTORE` tasks.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

Backups and restores that were started with the `br` commandline tool are not shown.
## Synopsis

```ebnf+diagram
ShowBRIEStmt ::=
    "SHOW" ("BACKUPS" | "RESTORES") ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

In one connection, execute the following statement:

```sql
BACKUP DATABASE `test` TO 's3://example-bucket/backup-01';
```

Before the backup completes, run `SHOW BACKUPS` in a new connection:

```sql
SHOW BACKUPS;
```

```sql
+--------------------------------+---------+----------+---------------------+---------------------+-------------+------------+---------+
| Destination                    | State   | Progress | Queue_time          | Execution_time      | Finish_time | Connection | Message |
+--------------------------------+---------+----------+---------------------+---------------------+-------------+------------+---------+
| s3://example-bucket/backup-01/ | Backup  | 98.38    | 2020-04-12 23:09:03 | 2020-04-12 23:09:25 |        NULL |          4 | NULL    |
+--------------------------------+---------+----------+---------------------+---------------------+-------------+------------+---------+
1 row in set (0.00 sec)
```

The first row of the result above is described as follows:

| Column | Description |
| :-------- | :--------- |
| `Destination` | The destination URL (with all parameters stripped to avoid leaking secret keys) |
| `State` | State of the task |
| `Progress` | Estimated progress in the current state as a percentage |
| `Queue_time` | When the task was queued |
| `Execution_time` | When the task was started; the value is `0000-00-00 00:00:00` for queueing tasks |
| `Finish_time` | The timestamp when the task finished; the value is `0000-00-00 00:00:00` for queueing and running tasks |
| `Connection` | Connection ID running this task |
| `Message` | Message with details |

The possible states are:

| State | Description |
| :-----|:------------|
| Backup | Making a backup |
| Wait | Waiting for execution |
| Checksum | Running a checksum operation |

The connection ID can be used to cancel a backup/restore task via the [`KILL TIDB QUERY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill) statement.

```sql
KILL TIDB QUERY 4;
```

```sql
Query OK, 0 rows affected (0.00 sec)
```
### Filtering

Use the `LIKE` clause to filter out tasks by matching the destination URL against a wildcard expression.

```sql
SHOW BACKUPS LIKE 's3://%';
```

Use the `WHERE` clause to filter by columns.

```sql
SHOW BACKUPS WHERE `Progress` < 25.0;
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [BACKUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-backup)
* [RESTORE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-restore)
