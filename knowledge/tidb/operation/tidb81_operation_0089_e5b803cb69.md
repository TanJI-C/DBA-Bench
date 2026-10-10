# dmctl start-task usage, flags, and returned results

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-create-task.md`
- Source Title: `Create a Data Migration Task`
- Source Heading Path: `Create a Data Migration Task | Create a Data Migration Task > Usage example | Create a Data Migration Task > Flags description | Create a Data Migration Task > Returned results`
- Source Line Ranges: `5-81`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `task-creation`, `dmctl`, `start-task`, `precheck`, `flags`, `binlog-replication`, `checkpoint`, `safe-mode`, `metadata`, `returned-results`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0089_e5b803cb69`
- Source ID: `tidb-docs-8.1:dm/dm-create-task.md#create-a-data-migration-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a016ca0acb088006d3c4ab71f9922709bfe1d93c6f59e023f188cdc66a7c775f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-create-task#create-a-data-migration-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-create-task.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to run `dmctl start-task`, what `-s`, `--remove-meta`, and `--start-time` mean, what precheck happens at task start, and what result JSON is returned.
- Retrieval Keywords: dmctl start-task, help start-task, Starts a task as defined in the configuration file, dmctl start-task [-s source ...] [--remove-meta] <config-file>, --remove-meta, --start-time, MySQL Source ID, config-file, task.yaml, prechecks privileges and configurations, binlog replication start time, 2021-10-21 00:01:00, 2021-10-21T00:01:00, checkpoint, safe mode, start-time {input-time} is too late, no binlog location matches it, returned results, result true, sources, worker1
- Follow-up Guidance: The content notes that DM prechecks privileges and configurations when the data migration task is started, and for `--start-time` it explains precedence over task configuration and downstream checkpoint plus the safe mode behavior when a checkpoint already exists.
- Classification Note: This is classified as an operation chunk because it documents the `start-task` command usage, flags, execution scope by source, and the returned command result for creating a DM data migration task.

## Official Source Content

# Create a Data Migration Task

You can use the `start-task` command to create a data migration task. When the data migration task is started, DM [prechecks privileges and configurations](https://docs.pingcap.com/tidb/stable/dm/dm-precheck).

```bash
help start-task
```

```
Starts a task as defined in the configuration file

Usage:
  dmctl start-task [-s source ...] [--remove-meta] <config-file> [flags]

Flags:
  -h, --help                help for start-task
      --remove-meta         whether to remove task's meta data
      --start-time string   specify the start time of binlog replication, e.g. '2021-10-21 00:01:00' or 2021-10-21T00:01:00

Global Flags:
      --config string        Path to config file.
      --master-addr string   Master API server address, this parameter is required when interacting with the dm-master
      --rpc-timeout string   RPC timeout, default is 10m. (default "10m")
  -s, --source strings       MySQL Source ID.
      --ssl-ca string        Path of file that contains list of trusted SSL CAs for connection.
      --ssl-cert string      Path of file that contains X509 certificate in PEM format for connection.
      --ssl-key string       Path of file that contains X509 key in PEM format for connection.
  -V, --version              Prints version and exit.
```
## Usage example

```bash
start-task [ -s "mysql-replica-01"] ./task.yaml
```
## Flags description

- `-s`: (Optional) Specifies the MySQL source to execute `task.yaml`. If it is set, the command only starts the subtasks of the specified task on the MySQL source.
- `config-file`: (Required) Specifies the file path of `task.yaml`.
- `remove-meta`: (Optional) Specifies whether to remove the task's previous metadata when starting the task.
- `start-time`: (Optional) Specifies the start time of binlog replication.
    - Format: `'2021-10-21 00:01:00'` or `2021-10-21T00:01:00`.
    - For incremental tasks, you can specify a rough starting point for the task using this flag. This flag takes precedence over the binlog position in the task configuration file and the binlog position in the downstream checkpoint.
    - When the task already has a checkpoint, if you start the task using this flag, DM automatically enables safe mode until the replication passes the checkpoint. This is to avoid the data duplication error caused by resetting the task to an earlier position.
        - When you reset the task to an earlier position, if the table schema at that time point is different from the downstream at the current time point, the task might report an error.
        - When you reset the task to a later position, note that the skipped binlog might have dirty data left in the downstream.
    - When you specify an earlier start time, DM starts migration from the earliest binlog position available.
    - When you specify a later start time, DM reports an error: `start-time {input-time} is too late, no binlog location matches it`.
## Returned results

```bash
start-task task.yaml
```

```
{
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
