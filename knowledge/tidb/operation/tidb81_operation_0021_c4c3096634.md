# Snapshot backup overview, full backup command, and backup timestamp lookup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-snapshot-guide.md`
- Source Title: `Snapshot Backup and Restore Guide`
- Source Heading Path: `Snapshot Backup and Restore Guide | Snapshot Backup and Restore Guide > Back up cluster snapshots | Snapshot Backup and Restore Guide > Get the backup time point of a snapshot backup`
- Source Line Ranges: `5-61`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tikv`, `shared`
- Topic Tags: `snapshot-backup`, `backup-time-point`, `mvcc`, `external-storage`, `s3`, `credentials`, `ratelimit`, `backup-validation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0021_c4c3096634`
- Source ID: `tidb-docs-8.1:br/br-snapshot-guide.md#snapshot-backup-and-restore-guide`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `116fcfc00d7f43e06025c2c1fe5bdf5df8cb97dc773182c43ae231426487bea0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#snapshot-backup-and-restore-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-snapshot-guide.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to run a BR snapshot full backup, specify a backup time point, understand `--storage` and `--ratelimit`, or decode the backup timestamp from snapshot metadata.
- Retrieval Keywords: tiup br backup full, --backupts, TSO, timestamp, MVCC, --storage, s3://backup-101/snapshot-202209081330, --ratelimit, MiB/s per TiKV, --send-credentials-to-tikv, tiup br validate decode --field="end-version", end-version, BackupTS, snapshot backup time point, physical time of a snapshot backup
- Follow-up Guidance: The source also shows using `tiup br validate decode --field="end-version" --storage ... | tail -n1` to get the physical time corresponding to a snapshot backup.
- Classification Note: This is classified as an operation chunk because the content provides BR snapshot backup commands, parameter meanings, runtime output, and backup time-point lookup steps.

## Official Source Content

# Snapshot Backup and Restore Guide

This document describes how to back up and restore TiDB snapshots using the br command-line tool (hereinafter referred to as `br`). Before backing up and restoring data, you need to [install the br command-line tool](https://docs.pingcap.com/tidb/stable/br/br-use-overview#deploy-and-use-br) first.

Snapshot backup is an implementation to back up the entire cluster. It is based on [multi-version concurrency control (MVCC)](https://docs.pingcap.com/tidb/stable/tidb-storage#mvcc) and backs up all data in the specified snapshot to a target storage. The size of the backup data is approximately the size of the compressed single replica in the cluster. After the backup is completed, you can restore the backup data to an empty cluster or a cluster that does not contain conflict data (with the same schema or same tables), restore the cluster to the time point of the snapshot backup, and restore multiple replicas according to the cluster replica settings.

Besides basic backup and restore, snapshot backup and restore also provides the following features:

* [Backup data of a specified time point](#back-up-cluster-snapshots)
* [Restore data of a specified database or table](#restore-a-database-or-a-table)
## Back up cluster snapshots

> **Note:**
>
> - The following examples assume that Amazon S3 access keys and secret keys are used to authorize permissions. If IAM roles are used to authorize permissions, you need to set `--send-credentials-to-tikv` to `false`.
> - If other storage systems or authorization methods are used to authorize permissions, adjust the parameter settings according to [Backup Storages](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages).

You can back up a TiDB cluster snapshot by running the `tiup br backup full` command. Run `tiup br backup full --help` to see the help information:

```shell
tiup br backup full --pd "${PD_IP}:2379" \
    --backupts '2022-09-08 13:30:00 +08:00' \
    --storage "s3://backup-101/snapshot-202209081330?access-key=${access-key}&secret-access-key=${secret-access-key}" \
    --ratelimit 128 \
```

In the preceding command:

- `--backupts`: The time point of the snapshot. The format can be [TSO](https://docs.pingcap.com/tidb/stable/glossary#tso) or timestamp, such as `400036290571534337` or `2018-05-11 01:42:23 +08:00`. If the data of this snapshot is garbage collected, the `tiup br backup` command returns an error and `br` exits. When backing up using a timestamp, it is recommended to specify the time zone as well. Otherwise, `br` uses the local time zone to construct the timestamp by default, which might lead to an incorrect backup time point. If you leave this parameter unspecified, `br` picks the snapshot corresponding to the backup start time.
- `--storage`: The storage address of the backup data. Snapshot backup supports Amazon S3, Google Cloud Storage, and Azure Blob Storage as backup storage. The preceding command uses Amazon S3 as an example. For more details, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).
- `--ratelimit`: The maximum speed **per TiKV** performing backup tasks. The unit is in MiB/s.

During backup, a progress bar is displayed in the terminal as shown below. When the progress bar advances to 100%, the backup task is completed and statistics such as total backup time, average backup speed, and backup data size are displayed.

```shell
Full Backup <-------------------------------------------------------------------------------> 100.00%
Checksum <----------------------------------------------------------------------------------> 100.00%
*** ["Full Backup success summary"] *** [backup-checksum=3.597416ms] [backup-fast-checksum=2.36975ms] *** [total-take=4.715509333s] [BackupTS=435844546560000000] [total-kv=1131] [total-kv-size=250kB] [average-speed=53.02kB/s] [backup-data-size(after-compressed)=71.33kB] [Size=71330]
```
## Get the backup time point of a snapshot backup

To manage a lot of backups, if you need to get the physical time of a snapshot backup, you can run the following command:

```shell
tiup br validate decode --field="end-version" \
--storage "s3://backup-101/snapshot-202209081330?access-key=${access-key}&secret-access-key=${secret-access-key}" | tail -n1
```

The output is as follows, corresponding to the physical time `2022-09-08 13:30:00 +0800 CST`:

```
435844546560000000
```
