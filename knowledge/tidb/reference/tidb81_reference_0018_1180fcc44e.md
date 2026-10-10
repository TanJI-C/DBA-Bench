# DDL administration commands

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/ddl-introduction.md`
- Source Title: `Execution Principles and Best Practices of DDL Statements`
- Source Heading Path: `Execution Principles and Best Practices of DDL Statements > DDL-related commands`
- Source Line Ranges: `169-188`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `ddl`, `admin-commands`, `show-ddl`, `show-ddl-jobs`, `cancel-ddl`, `pause-ddl`, `resume-ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0018_1180fcc44e`
- Source ID: `tidb-docs-8.1:best-practices/ddl-introduction.md#ddl-related-commands`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `181fc00acbaa22d5ad59210c99bccdce26992aac0d1b01ce87b22dc8c7cff578`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction#ddl-related-commands
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/ddl-introduction.md

## Retrieval Guidance

- Use When: Use this chunk when a user needs SQL commands to inspect, query, cancel, pause, or resume TiDB DDL jobs and understand the related status fields or error messages.
- Retrieval Keywords: ADMIN SHOW DDL, ADMIN SHOW DDL JOBS, ADMIN SHOW DDL JOB QUERIES, ADMIN CANCEL DDL JOBS, ADMIN PAUSE DDL JOBS, ADMIN RESUME DDL JOBS, current schema version number, DDL Owner, job_id, ERROR 8214 (HY000): Cancelled DDL job, DDL Job:90 not found, Job 3 can't be paused now, Job 3 can't be resumed
- Follow-up Guidance: The chunk includes the specific errors returned when canceling a completed task or when pausing or resuming a job that is not in the required state.
- Classification Note: Classified as reference because the content is a catalog of DDL administration SQL statements, their purposes, and the exact related errors and status information.

## Official Source Content

## DDL-related commands

- `ADMIN SHOW DDL`: Used to view the status of TiDB DDL operations, including the current schema version number, the DDL ID and address of the DDL Owner, the DDL task and SQL being executed, and the DDL ID of the current TiDB instance. For details, see [`ADMIN SHOW DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl#admin-show-ddl).

- `ADMIN SHOW DDL JOBS`: Used to view the detailed status of DDL tasks running in the cluster environment. For details, see [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl#admin-show-ddl-jobs).

- `ADMIN SHOW DDL JOB QUERIES job_id [, job_id]`: Used to view the original SQL statement of the DDL task corresponding to the `job_id`. For details, see [`ADMIN SHOW DDL JOB QUERIES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl#admin-show-ddl-job-queries).

- `ADMIN CANCEL DDL JOBS job_id, [, job_id]`: Used to cancel DDL tasks that have been submitted but not completed. After the cancellation is completed, the SQL statement that executes the DDL task returns the `ERROR 8214 (HY000): Cancelled DDL job` error.

    If a completed DDL task is canceled, you can see the `DDL Job:90 not found` error in the `RESULT` column, which means that the task has been removed from the DDL waiting queue.

- `ADMIN PAUSE DDL JOBS job_id [, job_id]`: Used to pause the DDL jobs that are being executed. After the command is executed, the SQL statement that executes the DDL job is displayed as being executed, while the background job has been paused. For details, refer to [`ADMIN PAUSE DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-pause-ddl).

    You can only pause DDL tasks that are in progress or still in the queue. Otherwise, the `Job 3 can't be paused now` error is shown in the `RESULT` column.

- `ADMIN RESUME DDL JOBS job_id [, job_id]`: Used to resume the DDL tasks that have been paused. After the command is executed, the SQL statement that executes the DDL task is displayed as being executed, and the background task is resumed. For details, refer to [`ADMIN RESUME DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-resume-ddl).

    You can only resume a paused DDL task. Otherwise, the `Job 3 can't be resumed` error is shown in the `RESULT` column.
