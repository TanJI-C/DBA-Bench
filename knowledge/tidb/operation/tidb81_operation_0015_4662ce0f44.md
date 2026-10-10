# Run log backup and scheduled snapshot backups

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/backup-and-restore-use-cases.md`
- Source Title: `TiDB Backup and Restore Use Cases`
- Source Heading Path: `TiDB Backup and Restore Use Cases > Run log backup | TiDB Backup and Restore Use Cases > Run snapshot backup`
- Source Line Ranges: `88-134`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tikv`, `tiup`
- Topic Tags: `log-backup`, `snapshot-backup`, `commands`, `status-check`, `s3`, `scheduling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0015_4662ce0f44`
- Source ID: `tidb-docs-8.1:br/backup-and-restore-use-cases.md#run-log-backup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2a7c8f2e5919b257b4edb777c574a11b43fdd73c3f441cb4ac20e66097aa0af9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/backup-and-restore-use-cases#run-log-backup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/backup-and-restore-use-cases.md

## Retrieval Guidance

- Use When: Use this chunk when searching for the exact BR commands to start and check a log backup task or to run full snapshot backups to S3 on a schedule.
- Retrieval Keywords: tiup br log start, --task-name=pitr, --pd="${PD_IP}:2379", --storage='s3://tidb-pitr-bucket/backup-data/log-backup', tiup br log status, status: ● NORMAL, checkpoint[global], Run log backup, Run snapshot backup, crontab, tiup br backup full, --storage='s3://tidb-pitr-bucket/backup-data/snapshot-20220514000000', --storage='s3://tidb-pitr-bucket/backup-data/snapshot-20220516000000', --backupts='2022/05/14 00:00:00 +08:00', --backupts='2022/05/16 00:00:00 +08:00'
- Follow-up Guidance: The source next shows how to run PITR with a snapshot backup plus log backup data and how to clean up outdated backup data.
- Classification Note: This is classified as operation because the content provides execution and status-check commands for log backup and scheduled snapshot backup tasks.

## Official Source Content

## Run log backup

After the log backup task is started, the log backup process runs in the TiKV cluster to continuously send the data change in the database to the S3 storage. To start a log backup task, run the following command:

```shell
tiup br log start --task-name=pitr --pd="${PD_IP}:2379" \
--storage='s3://tidb-pitr-bucket/backup-data/log-backup'
```

When the log backup task is running, you can query the backup status:

```shell
tiup br log status --task-name=pitr --pd="${PD_IP}:2379"

● Total 1 Tasks.
> #1 <
    name: pitr
    status: ● NORMAL
    start: 2022-05-13 11:09:40.7 +0800
      end: 2035-01-01 00:00:00 +0800
    storage: s3://tidb-pitr-bucket/backup-data/log-backup
    speed(est.): 0.00 ops/s
checkpoint[global]: 2022-05-13 11:31:47.2 +0800; gap=4m53s
```
## Run snapshot backup

You can run snapshot backup tasks on a regular basis using an automatic tool such as crontab. For example, run a snapshot backup at 00:00 every two days.

The following are two snapshot backup examples:

- Run a snapshot backup at 2022/05/14 00:00:00

    ```shell
    tiup br backup full --pd="${PD_IP}:2379" \
    --storage='s3://tidb-pitr-bucket/backup-data/snapshot-20220514000000' \
    --backupts='2022/05/14 00:00:00 +08:00'
    ```

- Run a snapshot backup at 2022/05/16 00:00:00

    ```shell
    tiup br backup full --pd="${PD_IP}:2379" \
    --storage='s3://tidb-pitr-bucket/backup-data/snapshot-20220516000000' \
    --backupts='2022/05/16 00:00:00 +08:00'
    ```
