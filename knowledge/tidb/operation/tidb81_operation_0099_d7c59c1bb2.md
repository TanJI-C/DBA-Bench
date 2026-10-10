# Pause DM migration task command usage and results

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-pause-task.md`
- Source Title: `Pause a Data Migration Task`
- Source Heading Path: `Pause a Data Migration Task | Pause a Data Migration Task > Usage example | Pause a Data Migration Task > Flags description | Pause a Data Migration Task > Returned results`
- Source Line Ranges: `5-70`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `pause-task`, `dmctl`, `task-management`, `troubleshooting`, `flags`, `command-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0099_d7c59c1bb2`
- Source ID: `tidb-docs-8.1:dm/dm-pause-task.md#pause-a-data-migration-task`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f214a6299cd81621f11a577b3c39fb061e8d43b6f96ecf3d00447da32cc03d1d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-pause-task#pause-a-data-migration-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-pause-task.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how to pause a running DM migration task with dmctl, what flags it accepts, how it differs from stop-task, and what result output looks like.
- Retrieval Keywords: pause-task, dmctl pause-task, pause a specified running task, pause-task [-s source ...] <task-name | task-file>, -s --source strings, MySQL Source ID, query-status, stop-task, relay log, dm_meta, checkpoint, pause-task test, op Pause, mysql-replica-01, worker1
- Follow-up Guidance: The content also points to query-status for checking status information retained in memory after pause-task.
- Classification Note: This is classified as an operation chunk because the content provides the pause-task command usage, flag meanings, behavioral differences from stop-task, and returned command results for DM task management.

## Official Source Content

# Pause a Data Migration Task

You can use the `pause-task` command to pause a data migration task.

`pause-task` differs from `stop-task` in that:

- `pause-task` only pauses a migration task. You can query the status information (retained in the memory) of the task using `query-status`. `stop-task` terminates a migration task and removes all information related to this task from the memory. This means you cannot use `query-status` to query the status information. `dm_meta` like "checkpoint" and data that have been migrated to the downstream are not removed.
- If `pause-task` is executed to pause the migration task, you cannot start a new task with the same name, neither can you get the relay log of the paused task removed, since this task does exist. If `stop-task` is executed to stop a task, you can start a new task with the same name, and you can get the relay log of the stopped task removed, since this task no longer exists.
- `pause-task` is usually used to pause a task for troubleshooting, while `stop-task` is to permanently remove a migration task, or to co-work with `start-task` to update the configuration information.

```bash
help pause-task
```

```
pause a specified running task

Usage:
 dmctl pause-task [-s source ...] <task-name | task-file> [flags]

Flags:
 -h, --help   help for pause-task

Global Flags:
 -s, --source strings   MySQL Source ID
```
## Usage example

```bash
pause-task [-s "mysql-replica-01"] task-name
```
## Flags description

- `-s`: (Optional) Specifies the MySQL source where you want to pause the subtasks of the migration task. If it is set, this command pauses only the subtasks on the specified MySQL source.
- `task-name| task-file`: (Required) Specifies the task name or task file path.
## Returned results

```bash
pause-task test
```

```
{
    "op": "Pause",
    "result": true,
    "msg": "",
    "sources": [
        {
            "result": true,
            "msg": "",
            "source": "mysql-replica-01",
            "worker": "worker1"
        }
    ]
}
```
