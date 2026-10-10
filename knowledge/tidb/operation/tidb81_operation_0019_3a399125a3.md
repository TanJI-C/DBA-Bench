# BR log backup command operations

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-pitr-manual.md`
- Source Title: `TiDB Log Backup and PITR Command Manual`
- Source Heading Path: `TiDB Log Backup and PITR Command Manual > Perform log backup | TiDB Log Backup and PITR Command Manual > Perform log backup > Start a backup task | TiDB Log Backup and PITR Command Manual > Perform log backup > Query the backup status | TiDB Log Backup and PITR Command Manual > Perform log backup > Pause and resume a backup task | TiDB Log Backup and PITR Command Manual > Perform log backup > Stop and restart a backup task | TiDB Log Backup and PITR Command Manual > Perform log backup > Stop and restart a backup task > Stop a backup task | TiDB Log Backup and PITR Command Manual > Perform log backup > Stop and restart a backup task > Restart a backup task`
- Source Line Ranges: `15-257`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `shared`
- Topic Tags: `backup task`, `status`, `pause`, `resume`, `stop`, `restart`, `metadata`, `storage`, `gc safepoint`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0019_3a399125a3`
- Source ID: `tidb-docs-8.1:br/br-pitr-manual.md#perform-log-backup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `965b65c7a572f0897bd5c9980d4a32697e0ce12ab091733b400961cd16f022ff`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-pitr-manual#perform-log-backup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-pitr-manual.md

## Retrieval Guidance

- Use When: Use this when you need BR log backup command usage, subcommands, status output fields, pause and resume behavior, or stop and restart notes.
- Retrieval Keywords: tiup br log, br log start, br log status, br log pause, br log resume, br log stop, br log truncate, br log metadata, --task-name, --start-ts, checkpoint[global], ErrBackupGCSafepointExceeded
- Follow-up Guidance: 
- Classification Note: This chunk is an operational command reference for starting, querying, pausing, resuming, stopping, and restarting TiDB log backup tasks with `tiup br log`.

## Official Source Content

## Perform log backup

You can start and manage log backup using the `tiup br log` command.

```shell
tiup br log --help

backup stream log from TiDB/TiKV cluster

Usage:
  br log [command]

Available Commands:
  metadata   get the metadata of log dir
  pause      pause a log backup task
  resume     resume a log backup task
  start      start a log backup task
  status     get status for the log backup task
  stop       stop a log backup task
  truncate   truncate the log data until sometime
```

Each subcommand is described as follows:

- `tiup br log start`: start a log backup task.
- `tiup br log status`: query the status of the log backup task.
- `tiup br log pause`: pause a log backup task.
- `tiup br log resume`: resume a paused log backup task.
- `tiup br log stop`: stop a log backup task and delete the task metadata.
- `tiup br log truncate`: clean up the log backup data from the backup storage.
- `tiup br log metadata`: query the metadata of the log backup data.
### Start a backup task

You can run the `tiup br log start` command to start a log backup task. This task runs in the background of your TiDB cluster and automatically backs up the change log of KV storage to the backup storage.

Run `tiup br log start --help` to see the help information:

```shell
tiup br log start --help
start a log backup task

Usage:
  br log start [flags]

Flags:
  -h, --help               help for start
  --start-ts string        usually equals last full backupTS, used for backup log. Default value is current ts. support TSO or datetime, e.g. '400036290571534337' or '2018-05-11 01:42:23+0800'.
  --task-name string       The task name for the backup log task.

Global Flags:
 --ca string                  CA certificate path for TLS connection
 --cert string                Certificate path for TLS connection
 --key string                 Private key path for TLS connection
 -u, --pd strings             PD address (default [127.0.0.1:2379])
 -s, --storage string         specify the url where backup storage, eg, "s3://bucket/path/prefix"

```

The example output only shows the common parameters. These parameters are described as follows:

- `--start-ts`: specifies the start timestamp for the log backup. If this parameter is not specified, the backup program uses the current time as `start-ts`.
- `task-name`: specifies the task name for the log backup. This name is also used to query, pause, and resume the backup task.
- `--ca`, `--cert`, `--key`: specifies the mTLS encryption method to communicate with TiKV and PD.
- `--pd`: specifies the PD address for the backup cluster. BR needs to access PD to start the log backup task.
- `--storage`: specifies the backup storage address. Currently, BR supports Amazon S3, Google Cloud Storage (GCS), or Azure Blob Storage as the storage for log backup. The preceding command uses Amazon S3 as an example. For details, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

Usage example:

```shell
tiup br log start --task-name=pitr --pd="${PD_IP}:2379" \
--storage='s3://backup-101/logbackup?access-key=${access-key}&secret-access-key=${secret-access-key}"'
```
### Query the backup status

You can run the `tiup br log status` command to query the backup status.

Run `tiup br log status --help` to see the help information:

```shell
tiup br log status --help
get status for the log backup task

Usage:
  br log status [flags]

Flags:
  -h, --help           help for status
  --json               Print JSON as the output.
  --task-name string   The task name for backup stream log. If default, get status of all of tasks (default "*")

Global Flags:
 --ca string                  CA certificate path for TLS connection
 --cert string                Certificate path for TLS connection
 --key string                 Private key path for TLS connection
 -u, --pd strings             PD address (default [127.0.0.1:2379])

```

In the example output, `task-name` is used to specify the name of the backup task. The default value is `*`, which means querying the status of all tasks.

Usage example:

```shell
tiup br log status --task-name=pitr --pd="${PD_IP}:2379"
```

Expected output:

```shell
● Total 1 Tasks.
> #1 <
              name: pitr
            status: ● NORMAL
             start: 2022-07-14 20:08:03.268 +0800
               end: 2090-11-18 22:07:45.624 +0800
           storage: s3://backup-101/logbackup
       speed(est.): 0.82 ops/s
checkpoint[global]: 2022-07-25 22:52:15.518 +0800; gap=2m52s
```

The output fields are described as follows:

- `status`: the status of the backup task, which can be `NORMAL`, `ERROR`, or `PAUSE`.
- `start`: the start time of the backup task. It is the `start-ts` value specified when the backup task is started.
- `storage`: the backup storage address.
- `speed`: the total QPS of the backup task. QPS means the number of logs backed per second.
- `checkpoint [global]`: all data before this checkpoint is backed up to the backup storage. This is the latest timestamp available for restoring the backup data.
- `error [store]`: the error the log backup program encounters on the storage node.
### Pause and resume a backup task

You can run the `tiup br log pause` command to pause a running backup task.

Run `tiup br log pause --help` to see the help information:

```shell
tiup br log pause --help
pause a log backup task

Usage:
  br log pause [flags]

Flags:
  --gc-ttl int         the TTL (in seconds) that PD holds for BR's GC safepoint (default 86400)
  -h, --help           help for status
  --task-name string   The task name for backup stream log.

Global Flags:
 --ca string                  CA certificate path for TLS connection
 --cert string                Certificate path for TLS connection
 --key string                 Private key path for TLS connection
 -u, --pd strings             PD address (default [127.0.0.1:2379])
```

> **Note:**
>
> - After the log backup task is paused, to prevent the MVCC data that generates the change log from being deleted, the backup program automatically sets the current backup checkpoint as the service safepoint, which retains MVCC data within the latest 24 hours. If the backup task is paused for more than 24 hours, the corresponding data is garbage collected and is not backed up.
> - Retaining too much MVCC data has a negative impact on the storage capacity and performance of the TiDB cluster. Therefore, it is recommended to resume the backup task in time.

Usage example:

```shell
tiup br log pause --task-name=pitr --pd="${PD_IP}:2379"
```

You can run the `tiup br log resume` command to resume a paused backup task.

Run `tiup br log resume --help` to see the help information:

```shell
tiup br log resume --help
resume a log backup task

Usage:
  br log resume [flags]

Flags:
  -h, --help           help for status
  --task-name string   The task name for backup stream log.

Global Flags:
 --ca string                  CA certificate path for TLS connection
 --cert string                Certificate path for TLS connection
 --key string                 Private key path for TLS connection
 -u, --pd strings             PD address (default [127.0.0.1:2379])
```

After the backup task is paused for more than 24 hours, running `tiup br log resume` reports an error, and BR prompts that backup data is lost. To handle this error, refer to [Backup & Restore FAQs](https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq#what-should-i-do-if-the-error-message-errbackupgcsafepointexceeded-is-returned-when-using-the-br-log-resume-command-to-resume-a-suspended-task).

Usage example:

```shell
tiup br log resume --task-name=pitr --pd="${PD_IP}:2379"
```
### Stop and restart a backup task

You can stop a log backup task by running the `tiup br log stop` command and restart a backup task that is stopped by using the original `--storage` directory.
#### Stop a backup task

You can run the `tiup br log stop` command to stop a log backup task. This command cleans up the task metadata in the backup cluster.

Run `tiup br log stop --help` to see the help information:

```shell
tiup br log stop --help
stop a log backup task

Usage:
  br log stop [flags]

Flags:
  -h, --help           help for status
  --task-name string   The task name for the backup log task.

Global Flags:
 --ca string                  CA certificate path for TLS connection
 --cert string                Certificate path for TLS connection
 --key string                 Private key path for TLS connection
 -u, --pd strings             PD address (default [127.0.0.1:2379])
```

> **Note:**
>
> Use this command with caution. If you need to pause a log backup task, use `tiup br log pause` and `tiup br log resume` instead.

Usage example:

```shell
tiup br log stop --task-name=pitr --pd="${PD_IP}:2379"
```
#### Restart a backup task

After running the `tiup br log stop` command to stop a log backup task, you can create a new log backup task in another `--storage` directory or restart the log backup task in the original `--storage` directory by running the `tiup br log start` command. If you restart the task in the original `--storage` directory, pay attention to the following points:

- Parameters of the `--storage` directory for restarting a task must be the same as the task that is stopped.
- The `--start-ts` does not need to be specified. BR automatically starts the backup from the last backup checkpoint.
- If the task is stopped for a long time and multiple versions of the data have been garbage collected, the error `BR:Backup:ErrBackupGCSafepointExceeded` is reported when you attempt to restart the task. In this case, you have to create a new log backup task in another `--storage` directory.
