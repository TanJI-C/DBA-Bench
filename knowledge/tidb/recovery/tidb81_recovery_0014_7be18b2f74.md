# DM connection interruption retries and task restart handling

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-error-handling.md`
- Source Title: `Handle Errors in TiDB Data Migration`
- Source Heading Path: `Handle Errors in TiDB Data Migration > Handle common errors > What can I do when a migration task is interrupted with the `invalid connection` error returned? > Solutions | Handle Errors in TiDB Data Migration > Handle common errors > A migration task is interrupted with the `driver: bad connection` error returned | Handle Errors in TiDB Data Migration > Handle common errors > A migration task is interrupted with the `driver: bad connection` error returned > Reason | Handle Errors in TiDB Data Migration > Handle common errors > A migration task is interrupted with the `driver: bad connection` error returned > Solution`
- Source Line Ranges: `116-132`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `invalid-connection`, `bad-connection`, `automatic-retry`, `stop-task`, `start-task`, `query-status`, `incremental-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0014_7be18b2f74`
- Source ID: `tidb-docs-8.1:dm/dm-error-handling.md#solutions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4529a4e5def9ae4e2f6b95227d46aaa49aff6ad269cceecfdfdd81f7552774c0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#solutions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-error-handling.md

## Retrieval Guidance

- Use When: Use this chunk when a DM migration task is interrupted with `invalid connection` or `driver: bad connection` and you need the documented retry and restart handling.
- Retrieval Keywords: invalid connection, driver: bad connection, query-status, stop-task, start-task, incremental replication, DM automatically retries, connection between DM and the upstream TiDB database, network failure, TiDB restart
- Follow-up Guidance: You can check the task errors by using `query-status`, and if DM does not or fails to retry automatically, use `stop-task` and then `start-task`.
- Classification Note: This is classified as recovery because the content explains automatic retry behavior and task restart handling after DM task interruption errors.

## Official Source Content

#### Solutions

Because DM has the feature of concurrently migrating data to the downstream in migration tasks, several errors might occur when a task is interrupted. You can check these errors by using `query-status`.

- If only the `invalid connection` error occurs during the incremental replication process, DM retries the task automatically.
- If DM does not or fails to retry automatically because of version problems, use `stop-task` to stop the task and then use `start-task` to restart the task.
### A migration task is interrupted with the `driver: bad connection` error returned
#### Reason

The `driver: bad connection` error indicates that anomalies have occurred in the connection between DM and the upstream TiDB database (such as network failure and TiDB restart) and that the data of the current request has not yet been sent to TiDB at that moment.
#### Solution

The current version of DM automatically retries on error. If you use the previous version which does not support automatically retry, you can execute the `stop-task` command to stop the task. Then execute `start-task` to restart the task.
