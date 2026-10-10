# Run PITR restore and clean up outdated backup data

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/backup-and-restore-use-cases.md`
- Source Title: `TiDB Backup and Restore Use Cases`
- Source Heading Path: `TiDB Backup and Restore Use Cases > Run PITR | TiDB Backup and Restore Use Cases > Clean up outdated data | TiDB Backup and Restore Use Cases > See also`
- Source Line Ranges: `135-176`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tikv`, `tiup`, `cloud`
- Topic Tags: `pitr`, `restore`, `point-in-time-recovery`, `snapshot-backup`, `log-backup`, `retention`, `cleanup`, `truncate`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0002_ccdbc60522`
- Source ID: `tidb-docs-8.1:br/backup-and-restore-use-cases.md#run-pitr`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e29500642ccd376dc612707e31eba3977f465d920edebc8281c8b8fb9dd8d7f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/backup-and-restore-use-cases#run-pitr
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/backup-and-restore-use-cases.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the PITR restore command that combines full snapshot backup and log backup to a target timestamp, or for the example commands that clean up old snapshot and log backup data.
- Retrieval Keywords: Run PITR, tiup br restore point, --storage='s3://tidb-pitr-bucket/backup-data/log-backup', --full-backup-storage='s3://tidb-pitr-bucket/backup-data/snapshot-20220514000000', --restored-ts '2022-05-15 18:00:00+0800', Full Restore success summary, restore log success summary, Clean up outdated data, rm s3://tidb-pitr-bucket/backup-data/snapshot-20220514000000, tiup br log truncate, --until='2022-05-14 00:00:00 +0800', point-in-time recovery, query the data at 2022/05/15 18:00:00
- Follow-up Guidance: The source also links to Backup Storages, Snapshot Backup and Restore Command Manual, and Log Backup and PITR Command Manual.
- Classification Note: This is classified as recovery because the main content shows restoring a cluster to a specified time point and includes related retention cleanup commands for backup data.

## Official Source Content

## Run PITR

Assume that you need to query the data at 2022/05/15 18:00:00. You can use PITR to restore a cluster to that time point by restoring a snapshot backup taken at 2022/05/14 and the log backup data between the snapshot and 2022/05/15 18:00:00.

The command is as follows:

```shell
tiup br restore point --pd="${PD_IP}:2379" \
--storage='s3://tidb-pitr-bucket/backup-data/log-backup' \
--full-backup-storage='s3://tidb-pitr-bucket/backup-data/snapshot-20220514000000' \
--restored-ts '2022-05-15 18:00:00+0800'

Full Restore <--------------------------------------------------------------------------------------------------------------------------------------------------------> 100.00%
[2022/05/29 18:15:39.132 +08:00] [INFO] [collector.go:69] ["Full Restore success summary"] [total-ranges=12] [ranges-succeed=xxx] [ranges-failed=0] [split-region=xxx.xxxµs] [restore-ranges=xxx] [total-take=xxx.xxxs] [restore-data-size(after-compressed)=xxx.xxx] [Size=xxxx] [BackupTS={TS}] [total-kv=xxx] [total-kv-size=xxx] [average-speed=xxx]
Restore Meta Files <--------------------------------------------------------------------------------------------------------------------------------------------------> 100.00%
Restore KV Files <----------------------------------------------------------------------------------------------------------------------------------------------------> 100.00%
[2022/05/29 18:15:39.325 +08:00] [INFO] [collector.go:69] ["restore log success summary"] [total-take=xxx.xx] [restore-from={TS}] [restore-to={TS}] [total-kv-count=xxx] [total-size=xxx]
```
## Clean up outdated data

You can clean up outdated data every two days using an automatic tool such as crontab.

For example, you can run the following commands to clean up outdated data:

- Delete snapshot data earlier than 2022/05/14 00:00:00

  ```shell
  rm s3://tidb-pitr-bucket/backup-data/snapshot-20220514000000
  ```

- Delete log backup data earlier than 2022/05/14 00:00:00

  ```shell
  tiup br log truncate --until='2022-05-14 00:00:00 +0800' --storage='s3://tidb-pitr-bucket/backup-data/log-backup'
  ```
## See also

- [Backup Storages](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages)
- [Snapshot Backup and Restore Command Manual](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual)
- [Log Backup and PITR Command Manual](https://docs.pingcap.com/tidb/stable/br/br-pitr-manual)
