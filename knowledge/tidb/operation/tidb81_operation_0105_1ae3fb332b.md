# DM stop-task command usage, flags, and results

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-stop-task.md`
- Source Title: `Stop a Data Migration Task`
- Source Heading Path: `Stop a Data Migration Task | Stop a Data Migration Task > Usage example | Stop a Data Migration Task > Flags description | Stop a Data Migration Task > Returned results`
- Source Line Ranges: `5-71`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `task-stop`, `dmctl`, `migration-task`, `source-selection`, `returned-results`, `checkpoint-retention`, `metadata-removal`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0105_1ae3fb332b`
- Source ID: `tidb-docs-8.1:dm/dm-stop-task.md#stop-a-data-migration-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2a99732a4c422e91b50e1925ae0225050e275323b2dd83eda4829d5f2258f856`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-stop-task#stop-a-data-migration-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-stop-task.md

## Retrieval Guidance

- Use When: Use this when looking for how to run the DM `stop-task` command, its `-s` source selection flag, and what result output and retained metadata are described after stopping a migration task.
- Retrieval Keywords: stop-task, dmctl stop-task, dmctl stop-task [-s source ...] <task-name | task-file>, MySQL Source ID, -s, --source strings, stop a specified task, migration task, subtasks, query-status, dm_meta, checkpoint, --remove-meta, start-task, returned results, op: Stop, result: true
- Follow-up Guidance: The content notes that after `stop-task`, `query-status` no longer displays the task, while checkpoint and other related information remain in the `dm_meta` database, and it mentions `start-task --remove-meta` and manual deletion of four task-prefixed tables in `dm_meta` for complete removal.
- Classification Note: This is classified as an operation document because it explains the `dmctl stop-task` command usage, flags, example invocation, returned results, and the documented effects on task visibility and retained metadata.

## Official Source Content

# Stop a Data Migration Task

You can use the `stop-task` command to stop a data migration task. For differences between `stop-task` and `pause-task`, refer to [Pause a Data Migration Task](https://docs.pingcap.com/tidb/stable/dm/dm-pause-task).

```bash
help stop-task
```

```
stop a specified task

Usage:
 dmctl stop-task [-s source ...] <task-name | task-file> [flags]

Flags:
 -h, --help   help for stop-task

Global Flags:
 -s, --source strings   MySQL Source ID
```
## Usage example

```bash
stop-task [-s "mysql-replica-01"]  task-name
```
## Flags description

- `-s`: (Optional) Specifies the MySQL source where the subtasks of the migration task (that you want to stop) run. If it is set, only subtasks on the specified MySQL source are stopped.
- `task-name | task-file`: (Required) Specifies the task name or task file path.
## Returned results

```bash
stop-task test
```

```
{
    "op": "Stop",
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

> **Note:**
>
> After you stop a migration task with the `stop-task` command, running [`query-status`](https://docs.pingcap.com/tidb/stable/dm/dm-query-status) will no longer display the task. However, the checkpoint and other related information for this task is still retained in the `dm_meta` database.
>
> + To start over the migration task, add the `--remove-meta` option when running the [`start-task`](https://docs.pingcap.com/tidb/stable/dm/dm-create-task) command.
> + To completely remove the migration task, manually delete the four tables that use the task name as a prefix from the `dm_meta` database.
