# Terminate background ANALYZE tasks

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Manage `ANALYZE` tasks and concurrency > Terminate background `ANALYZE` tasks`
- Source Line Ranges: `725-753`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `analyze`, `background-tasks`, `kill`, `show-analyze-status`, `resource-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0236_6e0dde1651`
- Source ID: `tidb-docs-8.1:statistics.md#terminate-background-analyze-tasks`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bca07508e08488b0c91f29c3d2bcfbe719031aab79400e9f3c3b25a11b07e9dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#terminate-background-analyze-tasks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented procedure for terminating a background `ANALYZE` task by finding its `instance` and `process_id` and issuing a `KILL TIDB` statement.
- Retrieval Keywords: Terminate background ANALYZE tasks, SHOW ANALYZE STATUS, instance column, process_id column, KILL TIDB ${id};, enable-global-kill, background `ANALYZE` task, KILL statement
- Follow-up Guidance: The source also points to the `KILL` statement documentation for more information.
- Classification Note: This is classified as an operation because the content gives a step-by-step SQL procedure to identify and terminate a running background `ANALYZE` task.

## Official Source Content

### Terminate background `ANALYZE` tasks

Since TiDB v6.0, TiDB supports using the `KILL` statement to terminate an `ANALYZE` task running in the background. If you find that an `ANALYZE` task running in the background consumes a lot of resources and affects your application, you can terminate the `ANALYZE` task by taking the following steps:

1. Execute the following SQL statement:

    ```sql
    SHOW ANALYZE STATUS
    ```

    By checking the `instance` column and the `process_id` column in the result, you can get the TiDB instance address and the task `ID` of the background `ANALYZE` task.

2. Terminate the `ANALYZE` task that is running in the background.

    - If [`enable-global-kill`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-global-kill-new-in-v610) is `true` (`true` by default), you can execute the `KILL TIDB ${id};` statement directly, where `${id}` is the `ID` of the background `ANALYZE` task obtained from the previous step.
    - If `enable-global-kill` is `false`, you need to use a client to connect to the TiDB instance that is executing the backend `ANALYZE` task, and then execute the `KILL TIDB ${id};` statement. If you use a client to connect to another TiDB instance, or if there is a proxy between the client and the TiDB cluster, the `KILL` statement cannot terminate the background `ANALYZE` task.

    To terminate the `ANALYZE` task, you can execute the `KILL TIDB ${id};` statement, where `${id}` is the `ID` of the background `ANALYZE` task obtained from the previous step.

For more information on the `KILL` statement, see [`KILL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill).
