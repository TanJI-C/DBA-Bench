# DM query status fields and subtask state model

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-query-status.md`
- Source Title: `Query Task Status in TiDB Data Migration`
- Source Heading Path: `Query Task Status in TiDB Data Migration > Detailed query result | Query Task Status in TiDB Data Migration > Subtask status | Query Task Status in TiDB Data Migration > Subtask status > Status description | Query Task Status in TiDB Data Migration > Subtask status > Status switch diagram`
- Source Line Ranges: `222-311`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `task-status`, `query-result`, `subtask-status`, `status-fields`, `replication-progress`, `binlog-position`, `ddl-locks`, `state-transitions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0229_cc1c6e21dc`
- Source ID: `tidb-docs-8.1:dm/dm-query-status.md#detailed-query-result`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `74563a8b284ed9e2519b3887a49dc50a91d4b8ab2f25101f607559d7e71681c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-query-status#detailed-query-result
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-query-status.md

## Retrieval Guidance

- Use When: Use this chunk when you need the DM query status response fields or the subtask state model for a task, source, or processing unit.
- Retrieval Keywords: result, msg, sources, sourceStatus, subTaskStatus, stage, unit, unresolvedDDLLockID, sync, masterBinlog, masterBinlogGtid, syncerBinlog, syncerBinlogGtid, blockingDDLs, unresolvedGroups, synced, totalRows, totalRps, recentRps, load, finishedBytes, totalBytes, progress, bps, dump, totalTables, completedTables, finishedRows, estimateTotalRows, New, Running, Paused, Stopped, Finished, pause-task, resume-task, stop-task
- Follow-up Guidance: See the subtask status section for the state descriptions and the status switch diagram.
- Classification Note: This chunk is a reference description of DM query status fields and subtask status transitions, including detailed metrics for Sync, Load, and Dump.

## Official Source Content

- `result`: Whether the query is successful.
- `msg`: The error message returned when the query fails.
- `sources`: The list of upstream MySQL instances. Each source contains the following fields:
    - `result`
    - `msg`
    - `sourceStatus`: The information of the upstream MySQL databases.
    - `subTaskStatus`: The information of all subtasks of upstream MySQL databases. Each subtask might contain the following fields:
        - `name`: The name of the subtask.
        - `stage`: The status of the subtask. For the status description and status switch relationship of "stage" of "subTaskStatus" of "sources", see the [subtask status](#subtask-status).
        - `unit`: The processing unit of DM, including "Check", "Dump", "Load", and "Sync".
        - `result`: Displays the error information if a subtask fails.
        - `unresolvedDDLLockID`: The sharding DDL lock ID, used for manually handling the sharding DDL lock in the abnormal condition. For operation details of "unresolvedDDLLockID" of "subTaskStatus" of "sources", see [Handle Sharding DDL Locks Manually](https://docs.pingcap.com/tidb/stable/dm/manually-handling-sharding-ddl-locks).
        - `sync`: The replication information of the `Sync` processing unit. This information is about the same component with the current processing unit.
            - `masterBinlog`: The binlog position in the upstream database.
            - `masterBinlogGtid`: The GTID information in the upstream database.
            - `syncerBinlog`:  The position of the binlog that has been replicated in the `Sync` processing unit.
            - `syncerBinlogGtid`: The binlog position replicated using GTID.
            - `blockingDDLs`: The DDL list that is blocked currently. It is not empty only when all the upstream tables of this DM-worker are in the "synced" status. In this case, it indicates the sharding DDL statements to be executed or that are skipped.
            - `unresolvedGroups`: The sharding group that is not resolved. Each group contains the following fields:
                - `target`: The downstream database table to be replicated.
                - `DDLs`: A list of DDL statements.
                - `firstPos`: The starting position of the sharding DDL statement.
                - `synced`: The upstream sharded table whose executed sharding DDL statement has been read by the `Sync` unit.
                - `unsynced`: The upstream table that has not executed this sharding DDL statement. If any upstream tables have not finished replication, `blockingDDLs` is empty.
            - `synced`: Whether the incremental replication catches up with the upstream and has the same binlog position as that in the upstream. The save point is not refreshed in real time in the `Sync` background, so `false` of `synced` does not always mean a replication delay exits.
            - `totalRows`: The total number of rows that are replicated in this subtask.
            - `totalRps`: The number of rows that are replicated in this subtask per second.
            - `recentRps`: The number of rows that are replicated in this subtask in the last second.
        - `load`:  The replication information of the `Load` processing unit.
            - `finishedBytes`: The number of bytes that have been loaded.
            - `totalBytes`: The total number of bytes that need to be loaded.
            - `progress`: The progress of the loading process.
            - `bps`: The speed of the full loading.
        - `dump`: The replication information of the `Dump` processing unit.
            - `totalTables`: The number of tables to be dumped.
            - `completedTables`:  The number of tables that have been dumped.
            - `finishedBytes`: The number of bytes that have been dumped.
            - `finishedRows`: The number of rows that have been dumped.
            - `estimateTotalRows`: The estimated number of rows to be dumped.
            - `progress`: The progress of the dumping process.
            - `bps`: The dumping speed in bytes/second.
## Subtask status
### Status description

- `New`:

    - The initial status.
    - If the subtask does not encounter an error, it is switched to `Running`; otherwise it is switched to `Paused`.

- `Running`: The normal running status.

- `Paused`:

    - The paused status.
    - If the subtask encounters an error, it is switched to `Paused`.
    - If you run `pause-task` when the subtask is in the `Running` status, the task is switched to `Paused`.
    - When the subtask is in this status, you can run the `resume-task` command to resume the task.

- `Stopped`:

    - The stopped status.
    - If you run `stop-task` when the subtask is in the `Running` or `Paused` status, the task is switched to `Stopped`.
    - When the subtask is in this status, you cannot use `resume-task` to resume the task.

- `Finished`:

    - The finished subtask status.
    - Only when the full replication subtask is finished normally, the task is switched to this status.
### Status switch diagram

```
                                         error occurs
                            New --------------------------------|
                             |                                  |
                             |           resume-task            |
                             |  |----------------------------|  |
                             |  |                            |  |
                             |  |                            |  |
                             v  v        error occurs        |  v
  Finished <-------------- Running -----------------------> Paused
                             ^  |        or pause-task       |
                             |  |                            |
                  start task |  | stop task                  |
                             |  |                            |
                             |  v        stop task           |
                           Stopped <-------------------------|
```
