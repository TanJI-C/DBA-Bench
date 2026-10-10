# Log backup and full backup setup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-pitr-guide.md`
- Source Title: `TiDB Log Backup and PITR Guide`
- Source Heading Path: `TiDB Log Backup and PITR Guide | TiDB Log Backup and PITR Guide > Back up TiDB cluster | TiDB Log Backup and PITR Guide > Back up TiDB cluster > Start log backup | TiDB Log Backup and PITR Guide > Back up TiDB cluster > Run full backup regularly`
- Source Line Ranges: `5-56`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `log backup`, `full backup`, `pitr`, `storage`, `status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0018_c41f9b85d8`
- Source ID: `tidb-docs-8.1:br/br-pitr-guide.md#tidb-log-backup-and-pitr-guide`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `994230d1a74e3645cf82357400efacfb173cd95a35d55d29144694d91758edcd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-pitr-guide#tidb-log-backup-and-pitr-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-pitr-guide.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the BR commands and status output for starting TiDB log backup and scheduling regular full snapshot backups for PITR.
- Retrieval Keywords: tiup br log start, tiup br log status, tiup br backup full, --task-name=pitr, checkpoint[global], status: NORMAL, Start log backup, Run full backup regularly, snapshot backup, log backup, PITR, --send-credentials-to-tikv
- Follow-up Guidance: It also shows that a cluster can only run one log backup task each time and that the log backup task runs in the background until stopped manually.
- Classification Note: The content is classified as operation because it describes how to start log backup, check its status, and run full backup commands.

## Official Source Content

# TiDB Log Backup and PITR Guide

A full backup (snapshot backup) contains the full cluster data at a certain point, while TiDB log backup can back up data written by applications to a specified storage in a timely manner. If you want to choose the restore point as required, that is, to perform point-in-time recovery (PITR), you can [start log backup](#start-log-backup) and [run full backup regularly](#run-full-backup-regularly).

Before you back up or restore data using the br command-line tool (hereinafter referred to as `br`), you need to [install `br`](https://docs.pingcap.com/tidb/stable/br/br-use-overview#deploy-and-use-br) first.
## Back up TiDB cluster
### Start log backup

> **Note:**
>
> - The following examples assume that Amazon S3 access keys and secret keys are used to authorize permissions. If IAM roles are used to authorize permissions, you need to set `--send-credentials-to-tikv` to `false`.
> - If other storage systems or authorization methods are used to authorize permissions, adjust the parameter settings according to [Backup Storages](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages).

To start a log backup, run `tiup br log start`. A cluster can only run one log backup task each time.

```shell
tiup br log start --task-name=pitr --pd "${PD_IP}:2379" \
--storage 's3://backup-101/logbackup?access-key=${access-key}&secret-access-key=${secret-access-key}'
```

After the log backup task starts, it runs in the background of the TiDB cluster until you stop it manually. During this process, the TiDB change logs are regularly backed up to the specified storage in small batches. To query the status of the log backup task, run the following command:

```shell
tiup br log status --task-name=pitr --pd "${PD_IP}:2379"
```

Expected output:

```
● Total 1 Tasks.
> #1 <
    name: pitr
    status: ● NORMAL
    start: 2022-05-13 11:09:40.7 +0800
      end: 2035-01-01 00:00:00 +0800
    storage: s3://backup-101/log-backup
    speed(est.): 0.00 ops/s
checkpoint[global]: 2022-05-13 11:31:47.2 +0800; gap=4m53s
```
### Run full backup regularly

The snapshot backup can be used as a method of full backup. You can run `tiup br backup full` to back up the cluster snapshot to the backup storage according to a fixed schedule (for example, every 2 days).

```shell
tiup br backup full --pd "${PD_IP}:2379" \
--storage 's3://backup-101/snapshot-${date}?access-key=${access-key}&secret-access-key=${secret-access-key}'
```
