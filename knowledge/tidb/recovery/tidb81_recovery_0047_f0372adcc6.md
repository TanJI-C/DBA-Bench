# TiCDC downstream DDL failure handling and resume options

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/troubleshoot-ticdc.md`
- Source Title: `Troubleshoot TiCDC`
- Source Heading Path: `Troubleshoot TiCDC > How can I find out whether a DDL statement fails to execute in downstream during TiCDC replication? How to resume the replication?`
- Source Line Ranges: `121-147`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `ddl`, `downstream`, `resume`, `checkpoint-ts`, `ignore-txn-start-ts`, `remove`, `create`, `data-loss`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0047_f0372adcc6`
- Source ID: `tidb-docs-8.1:ticdc/troubleshoot-ticdc.md#how-can-i-find-out-whether-a-ddl-statement-fails-to-execute-in-downstream-during-ticdc-replication-how-to-resume-the-replication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7618f7e57ca9978bf396f756875bad17beac06404cae6dbeecbbcd46d886de96`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot-ticdc#how-can-i-find-out-whether-a-ddl-statement-fails-to-execute-in-downstream-during-ticdc-replication-how-to-resume-the-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/troubleshoot-ticdc.md

## Retrieval Guidance

- Use When: Use this chunk when a downstream DDL execution failure stops a TiCDC changefeed and you need the documented resume behavior, checkpoint-ts meaning, or the documented skip options and their risk.
- Retrieval Keywords: DDL statement fails to execute, changefeed automatically stops, checkpoint-ts, finish-ts, cdc cli changefeed resume, ignore-txn-start-ts, apply job, start-ts, cdc cli changefeed remove, cdc cli changefeed create, checkpointTs+1, data loss, strictly prohibited in production environments
- Follow-up Guidance: The content states that `checkpoint-ts` is the DDL statement's `finish-ts`, and it warns that recreating the task with `start-ts` set to `checkpoint-ts + 1` can lose DML data change at `checkpointTs+1`.
- Classification Note: This chunk is classified as recovery because it focuses on how to resume a stopped changefeed after downstream DDL failure and how the documented skip methods affect replication continuity.

## Official Source Content

## How can I find out whether a DDL statement fails to execute in downstream during TiCDC replication? How to resume the replication?

If a DDL statement fails to execute, the replication task (changefeed) automatically stops. The checkpoint-ts is the DDL statement's finish-ts. If you want TiCDC to retry executing this statement in the downstream, use `cdc cli changefeed resume` to resume the replication task. For example:

```shell
cdc cli changefeed resume -c test-cf --server=http://127.0.0.1:8300
```

If you want to skip this DDL statement that goes wrong, set the start-ts of the changefeed to the checkpoint-ts (the timestamp at which the DDL statement goes wrong) plus one, and then run the `cdc cli changefeed create` command to create a new changefeed task. For example, if the checkpoint-ts at which the DDL statement goes wrong is `415241823337054209`, run the following commands to skip this DDL statement:

To skip this DDL statement that goes wrong, you can configure the `ignore-txn-start-ts` parameter to skip the transactions corresponding to the specified `start-ts`. For example:

1. Search the TiCDC log for the `apply job` field, and identify the `start-ts` of the DDLs that are taking a long time.
2. Modify the changefeed configuration. Add the above `start-ts` to the `ignore-txn-start-ts` configuration item.
3. Resume the suspended changefeed.

> **Note:**
>
> Although setting the changefeed `start-ts` to the value of `checkpoint-ts` (at the time of the error) plus one and then recreating the task can skip the DDL statement, it can also cause TiCDC to lose the DML data change at the time of `checkpointTs+1`. Therefore, this operation is strictly prohibited in production environments.

```shell
cdc cli changefeed remove --server=http://127.0.0.1:8300 --changefeed-id simple-replication-task
cdc cli changefeed create --server=http://127.0.0.1:8300 --sink-uri="mysql://root:123456@127.0.0.1:3306/" --changefeed-id="simple-replication-task" --sort-engine="unified" --start-ts 415241823337054210
```
