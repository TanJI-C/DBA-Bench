# DM resume-task command usage and results

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-resume-task.md`
- Source Title: `Resume a Data Migration Task`
- Source Heading Path: `Resume a Data Migration Task | Resume a Data Migration Task > Usage example | Resume a Data Migration Task > Flags description | Resume a Data Migration Task > Returned results`
- Source Line Ranges: `5-64`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `task-resume`, `paused-task`, `dmctl`, `mysql-source`, `subtask`, `command-flags`, `returned-results`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0103_a9380ea442`
- Source ID: `tidb-docs-8.1:dm/dm-resume-task.md#resume-a-data-migration-task`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1a88b696dc7f260747cfb45c4622e4e38e3d7349d5fb520fded3164627edc6cc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-resume-task#resume-a-data-migration-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-resume-task.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to run dmctl to resume a data migration task that is in the Paused state, including optional source filtering and the returned JSON result format.
- Retrieval Keywords: resume-task, dmctl resume-task, resume a specified paused task, Paused state, MySQL Source ID, -s source, --source strings, resume-task [-s source ...] <task-name | task-file>, resume-task [-s "mysql-replica-01"] task-name, subtask, mysql-replica-01, returned results, "op": "Resume", "result": true, worker1
- Follow-up Guidance: If the -s option is set, the command resumes only the subtasks on the specified MySQL source.
- Classification Note: This is classified as an operation chunk because the official content gives the dmctl command usage, flags, example invocation, and returned results for resuming a paused migration task.

## Official Source Content

# Resume a Data Migration Task

You can use the `resume-task` command to resume a data migration task in the `Paused` state. This is generally used in scenarios where you want to manually resume a data migration task after handling the error that get the task paused.

```bash
help resume-task
```

```
resume a specified paused task

Usage:
 dmctl resume-task [-s source ...] <task-name | task-file> [flags]

Flags:
 -h, --help   help for resume-task

Global Flags:
 -s, --source strings   MySQL Source ID
```
## Usage example

```bash
resume-task [-s "mysql-replica-01"] task-name
```
## Flags description

- `-s`: (Optional) Specifies the MySQL source where you want to resume the subtask of the migration task. If it is set, the command resumes only the subtasks on the specified MySQL source.
- `task-name | task-file`: (Required) Specifies the task name or task file path.
## Returned results

```bash
resume-task test
```

```
{
    "op": "Resume",
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
