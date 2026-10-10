# Snapshot backup overview and full-cluster backup command

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-snapshot-manual.md`
- Source Title: `TiDB Snapshot Backup and Restore Command Manual`
- Source Heading Path: `TiDB Snapshot Backup and Restore Command Manual | TiDB Snapshot Backup and Restore Command Manual > Back up cluster snapshots`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tikv`, `tiup`
- Topic Tags: `snapshot-backup`, `full-backup`, `backup-command`, `backupts`, `gc-safepoint`, `ratelimit`, `logging`, `progress`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0022_a9bbdfe79c`
- Source ID: `tidb-docs-8.1:br/br-snapshot-manual.md#tidb-snapshot-backup-and-restore-command-manual`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b8296b8775df1309749d35fee4102f15c324d7daca2a6ed8f50ddd2f5daa6a43`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#tidb-snapshot-backup-and-restore-command-manual
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-snapshot-manual.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the BR command and parameters to back up a full TiDB cluster snapshot, including a specified backup timestamp, rate limit, log file, GC safepoint behavior, and progress display.
- Retrieval Keywords: tiup br backup full, --backupts, TSO, 2024-06-28 13:30:00 +08:00, --pd, --storage, --ratelimit, --log-file, GC Safe Point, safePoint, backupTS, progress bar, Full Backup
- Follow-up Guidance: It also states that if `--backupts` is unspecified, `br` picks the snapshot corresponding to the backup start time, and if the snapshot data has been garbage collected, `tiup br backup` returns an error and `br` exits.
- Classification Note: This is classified as an operation chunk because the content gives the executable `tiup br backup full` procedure and explains its runtime parameters and behavior.

## Official Source Content

# TiDB Snapshot Backup and Restore Command Manual

This document describes the commands of TiDB snapshot backup and restore according to the application scenarios, including:

- [Back up cluster snapshots](#back-up-cluster-snapshots)
- [Back up a database or a table](#back-up-a-database-or-a-table)
    - [Back up a database](#back-up-a-database)
    - [Back up a table](#back-up-a-table)
    - [Back up multiple tables with table filter](#back-up-multiple-tables-with-table-filter)
- [Back up statistics](#back-up-statistics)
- [Encrypt the backup data](#encrypt-the-backup-data)
- [Restore cluster snapshots](#restore-cluster-snapshots)
- [Restore a database or a table](#restore-a-database-or-a-table)
    - [Restore a database](#restore-a-database)
    - [Restore a table](#restore-a-table)
    - [Restore multiple tables with table filter](#restore-multiple-tables-with-table-filter)
    - [Restore execution plan bindings from the `mysql` schema](#restore-execution-plan-bindings-from-the-mysql-schema)
- [Restore encrypted snapshots](#restore-encrypted-snapshots)

For more information about snapshot backup and restore, refer to:

- [Snapshot Backup and Restore Guide](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide)
- [Backup and Restore Use Cases](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-use-cases)
## Back up cluster snapshots

You can back up the latest or specified snapshot of the TiDB cluster using the `tiup br backup full` command. For more information about the command, run the `tiup br backup full --help` command.

```shell
tiup br backup full \
    --pd "${PD_IP}:2379" \
    --backupts '2024-06-28 13:30:00 +08:00' \
    --storage "s3://${backup_collection_addr}/snapshot-${date}?access-key=${access-key}&secret-access-key=${secret-access-key}" \
    --ratelimit 128 \
    --log-file backupfull.log
```

In the preceding command:

- `--backupts`: The time point of the snapshot. The format can be [TSO](https://docs.pingcap.com/tidb/stable/glossary#tso) or timestamp, such as `400036290571534337` or `2024-06-28 13:30:00 +08:00`. If the data of this snapshot is garbage collected, the `tiup br backup` command returns an error and 'br' exits. If you leave this parameter unspecified, `br` picks the snapshot corresponding to the backup start time.
- `--ratelimit`: The maximum speed **per TiKV** performing backup tasks. The unit is in MiB/s.
- `--log-file`: The target file where `br` log is written.

> **Note:**
>
> The BR tool already supports self-adapting to GC. It automatically registers `backupTS` (the latest PD timestamp by default) to PD's `safePoint` to ensure that TiDB's GC Safe Point does not move forward during the backup, thus avoiding manually setting GC configurations.

During backup, a progress bar is displayed in the terminal, as shown below. When the progress bar advances to 100%, the backup is complete.

```shell
Full Backup <---------/................................................> 17.12%.
```
