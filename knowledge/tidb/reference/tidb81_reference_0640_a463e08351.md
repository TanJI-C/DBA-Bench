# SHOW ANALYZE STATUS syntax and result columns

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-analyze-status.md`
- Source Title: `SHOW ANALYZE STATUS`
- Source Heading Path: `SHOW ANALYZE STATUS | SHOW ANALYZE STATUS > Synopsis`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show-analyze-status`, `statistics`, `analyze-jobs`, `syntax`, `result-columns`, `history-tasks`, `cluster-level-tasks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0640_a463e08351`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-analyze-status.md#show-analyze-status`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9a55574ecb1ce3a4d116e650d93eb1d84f10cbc0af5c8383be46a050efa96cbe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-analyze-status#show-analyze-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-analyze-status.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax of `SHOW ANALYZE STATUS`, what task records it shows, or the meaning of its result columns and task states.
- Retrieval Keywords: SHOW ANALYZE STATUS, ShowAnalyzeStatusStmt, SHOW ANALYZE STATUS syntax, SHOW ANALYZE STATUS columns, Table_schema, Table_name, Partition_name, Job_info, Processed_rows, Start_time, State, Fail_reason, Instance, Process_id, pending, running, finished, failed, mysql.analyze_jobs, history tasks within the last 7 days, cluster-level tasks, instance-level tasks, SHOW ANALYZE STATUS LIKE, SHOW ANALYZE STATUS WHERE
- Follow-up Guidance: The source also states that `mysql.analyze_jobs` can be used to view history tasks within the last 7 days and, starting from TiDB v7.3.0, the progress of the current `ANALYZE` task.
- Classification Note: This is reference content because it defines the statement purpose, gives the formal synopsis, and enumerates the returned columns and their meanings.

## Official Source Content

# SHOW ANALYZE STATUS

The `SHOW ANALYZE STATUS` statement shows the statistics collection tasks being executed by TiDB and a limited number of historical task records.

Starting from TiDB v6.1.0, the `SHOW ANALYZE STATUS` statement supports showing cluster-level tasks. Even after a TiDB restart, you can still view task records before the restart using this statement. Before TiDB v6.1.0, the `SHOW ANALYZE STATUS` statement can only show instance-level tasks, and task records are cleared after a TiDB restart.

Starting from TiDB v6.1.0, you can view the history tasks within the last 7 days through the system table `mysql.analyze_jobs`.

Starting from TiDB v7.3.0, you can view the progress of the current `ANALYZE` task through the system table `mysql.analyze_jobs` or `SHOW ANALYZE STATUS`.

Currently, the `SHOW ANALYZE STATUS` statement returns the following columns:

| Column name      | Description |
| :--------------- | :------------- |
| `Table_schema`   | The database name |
| `Table_name`     | The table name |
| `Partition_name` | The partition name |
| `Job_info`       | The task information. If an index is analyzed, this information will include the index name. When `tidb_analyze_version =2`, this information will include configuration items such as sample rate. |
| `Processed_rows` | The number of rows that have been analyzed |
| `Start_time`     | The time at which the task starts |
| `State`          | The state of a task, including `pending`, `running`, `finished`, and `failed` |
| `Fail_reason`    | The reason why the task fails. If the execution is successful, the value is `NULL`. |
| `Instance`       | The TiDB instance that executes the task |
| `Process_id`     | The process ID that executes the task |
## Synopsis

```ebnf+diagram
ShowAnalyzeStatusStmt ::= 'SHOW' 'ANALYZE' 'STATUS' ShowLikeOrWhereOpt

ShowLikeOrWhereOpt ::= 'LIKE' SimpleExpr | 'WHERE' Expression
```
