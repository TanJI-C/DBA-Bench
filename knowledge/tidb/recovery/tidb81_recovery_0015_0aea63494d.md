# DM relay and binlog checkpoint recovery for oversized upstream binlogs

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-error-handling.md`
- Source Title: `Handle Errors in TiDB Data Migration`
- Source Heading Path: `Handle Errors in TiDB Data Migration > Handle common errors > The relay unit throws error `event from * in * diff from passed-in event *` or a migration task is interrupted with failing to get or parse binlog errors like `get binlog error ERROR 1236 (HY000)` and `binlog checksum mismatch, data may be corrupted` returned | Handle Errors in TiDB Data Migration > Handle common errors > The relay unit throws error `event from * in * diff from passed-in event *` or a migration task is interrupted with failing to get or parse binlog errors like `get binlog error ERROR 1236 (HY000)` and `binlog checksum mismatch, data may be corrupted` returned > Reason | Handle Errors in TiDB Data Migration > Handle common errors > The relay unit throws error `event from * in * diff from passed-in event *` or a migration task is interrupted with failing to get or parse binlog errors like `get binlog error ERROR 1236 (HY000)` and `binlog checksum mismatch, data may be corrupted` returned > Solutions`
- Source Line Ranges: `133-178`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `sql`
- Topic Tags: `relay-log`, `binlog`, `checkpoint`, `gtid`, `safe-mode`, `dm-worker`, `stop-task`, `start-task`, `query-status`, `manual-recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0015_0aea63494d`
- Source ID: `tidb-docs-8.1:dm/dm-error-handling.md#the-relay-unit-throws-error-event-from-in-diff-from-passed-in-event-or-a-migration-task-is-interrupted-with-failing-to-get-or-parse-binlog-errors-like-get-binlog-error-error-1236-hy000-and-binlog-checksum-mismatch-data-may-be-corrupted-returned`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7b31f870b2103bcc964c9d26ea86329bf605967417469f4b6d63a867bb5d1da4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#the-relay-unit-throws-error-event-from-in-diff-from-passed-in-event-or-a-migration-task-is-interrupted-with-failing-to-get-or-parse-binlog-errors-like-get-binlog-error-error-1236-hy000-and-binlog-checksum-mismatch-data-may-be-corrupted-returned
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-error-handling.md

## Retrieval Guidance

- Use When: Use this chunk when DM relay log pulling or incremental replication hits oversized upstream binlog issues such as `event from * in * diff from passed-in event *`, `get binlog error ERROR 1236 (HY000)`, or `binlog checksum mismatch, data may be corrupted`.
- Retrieval Keywords: event from * in * diff from passed-in event *, get binlog error ERROR 1236 (HY000), binlog checksum mismatch, data may be corrupted, relay unit, incremental replication, upstream binlog file exceeds 4 GB, uint32, relay.meta, enable_gtid, binlog-gtid, dm_meta, dm_test_syncer_checkpoint, binlog_name, binlog_pos, safe-mode: true, query-status, stop-task, start-task, DM-worker
- Follow-up Guidance: The source provides manual recovery steps for both relay units and binlog replication processing units, including updating `relay.meta` or downstream `dm_meta` checkpoints, using `safe-mode: true`, and checking progress with `query-status`.
- Classification Note: This is classified as recovery because the content describes manual migration recovery steps after relay or binlog checkpoint errors caused by binlog files larger than 4 GB.

## Official Source Content

### The relay unit throws error `event from * in * diff from passed-in event *` or a migration task is interrupted with failing to get or parse binlog errors like `get binlog error ERROR 1236 (HY000)` and `binlog checksum mismatch, data may be corrupted` returned
#### Reason

During the DM process of relay log pulling or incremental replication, this two errors might occur if the size of the upstream binlog file exceeds **4 GB**.

**Cause:** When writing relay logs, DM needs to perform event verification based on binlog positions and the size of the binlog file, and store the replicated binlog positions as checkpoints. However, the official MySQL uses `uint32` to store binlog positions. This means the binlog position for a binlog file over 4 GB overflows, and then the errors above occur.
#### Solutions

For relay units, manually recover migration using the following solution:

1. Identify in the upstream that the size of the corresponding binlog file has exceeded 4GB when the error occurs.

2. Stop the DM-worker.

3. Copy the corresponding binlog file in the upstream to the relay log directory as the relay log file.

4. In the relay log directory, update the corresponding `relay.meta` file to pull from the next binlog file. If you have specified `enable_gtid` to `true` for the DM-worker, you need to modify the GTID corresponding to the next binlog file when updating the `relay.meta` file. Otherwise, you don't need to modify the GTID.

    Example: when the error occurs, `binlog-name = "mysql-bin.004451"` and `binlog-pos = 2453`. Update them respectively to `binlog-name = "mysql-bin.004452"` and `binlog-pos = 4`, and update `binlog-gtid` to `f0e914ef-54cf-11e7-813d-6c92bf2fa791:1-138218058`.

5. Restart the DM-worker.

For binlog replication processing units, manually recover migration using the following solution:

1. Identify in the upstream that the size of the corresponding binlog file has exceeded 4GB when the error occurs.

2. Stop the migration task using `stop-task`.

3. Update the `binlog_name` in the global checkpoints and in each table checkpoint of the downstream `dm_meta` database to the name of the binlog file in error; update `binlog_pos` to a valid position value for which migration has completed, for example, 4.

    Example: the name of the task in error is `dm_test`, the corresponding s`source-id` is `replica-1`, and the corresponding binlog file is `mysql-bin|000001.004451`. Execute the following command:

    ```sql
    UPDATE dm_test_syncer_checkpoint SET binlog_name='mysql-bin|000001.004451', binlog_pos = 4 WHERE id='replica-1';
    ```

4. Specify `safe-mode: true` in the `syncers` section of the migration task configuration to ensure re-entrant.

5. Start the migration task using `start-task`.

6. View the status of the migration task using `query-status`. You can restore `safe-mode` to the original value and restart the migration task when migration is done for the original error-triggering relay log files.
