# PITR restore and cleanup

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-pitr-guide.md`
- Source Title: `TiDB Log Backup and PITR Guide`
- Source Heading Path: `TiDB Log Backup and PITR Guide > Run PITR | TiDB Log Backup and PITR Guide > Clean up outdated data`
- Source Line Ranges: `57-104`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `pd`, `tidb`
- Topic Tags: `point-in-time recovery`, `restore`, `truncate`, `retention`, `snapshot`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0007_92bfb25311`
- Source ID: `tidb-docs-8.1:br/br-pitr-guide.md#run-pitr`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e89e432448f74de94c207caeb537000efe4f2644ef3bb779a57c212c7cfdfa26`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-pitr-guide#run-pitr
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-pitr-guide.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to run point-in-time recovery with BR or how to clean up outdated log and snapshot backup data within the retention period workflow.
- Retrieval Keywords: tiup br restore point, --restored-ts, --full-backup-storage, full restore, log restore, Restore Meta Files, Restore KV Files, tiup br log truncate, tiup br validate decode --field="end-version", FULL_BACKUP_TS, Clean up outdated data, backup retention period
- Follow-up Guidance: It includes the restore phases and the cleanup sequence of finding the last full backup outside the retention period, decoding its end-version timestamp, truncating earlier log backup data, and deleting earlier snapshot data.
- Classification Note: The content is classified as recovery because it explains restoring to a specified time point and handling backup data needed for PITR retention cleanup.

## Official Source Content

## Run PITR

To restore the cluster to any point in time within the backup retention period, you can use `tiup br restore point`. When you run this command, you need to specify the **time point you want to restore**, **the latest snapshot backup data before the time point**, and the **log backup data**. BR will automatically determine and read data needed for the restore, and then restore these data to the specified cluster in order.

```shell
tiup br restore point --pd "${PD_IP}:2379" \
--storage='s3://backup-101/logbackup?access-key=${access-key}&secret-access-key=${secret-access-key}' \
--full-backup-storage='s3://backup-101/snapshot-${date}?access-key=${access-key}&secret-access-key=${secret-access-key}' \
--restored-ts '2022-05-15 18:00:00+0800'
```

During data restore, you can view the progress through the progress bar in the terminal. The restore is divided into two phases, full restore and log restore (restore meta files and restore KV files). After each phase is completed, `br` outputs information such as restore time and data size.

```shell
Full Restore <--------------------------------------------------------------------------------------------------------------------------------------------------------> 100.00%
*** ["Full Restore success summary"] ****** [total-take=xxx.xxxs] [restore-data-size(after-compressed)=xxx.xxx] [Size=xxxx] [BackupTS={TS}] [total-kv=xxx] [total-kv-size=xxx] [average-speed=xxx]
Restore Meta Files <--------------------------------------------------------------------------------------------------------------------------------------------------> 100.00%
Restore KV Files <----------------------------------------------------------------------------------------------------------------------------------------------------> 100.00%
*** ["restore log success summary"] [total-take=xxx.xx] [restore-from={TS}] [restore-to={TS}] [total-kv-count=xxx] [total-size=xxx]
```
## Clean up outdated data

As described in the [Usage Overview of TiDB Backup and Restore](https://docs.pingcap.com/tidb/stable/br/br-use-overview):

To perform PITR, you need to restore the full backup before the restore point, and the log backup between the full backup point and the restore point. Therefore, for log backups that exceed the backup retention period, you can use `tiup br log truncate` to delete the backup before the specified time point. **It is recommended to only delete the log backup before the full snapshot**.

The following steps describe how to clean up backup data that exceeds the backup retention period:

1. Get the **last full backup** outside the backup retention period.
2. Use the `validate` command to get the time point corresponding to the backup. Assume that the backup data before 2022/09/01 needs to be cleaned, you should look for the last full backup before this time point and ensure that it will not be cleaned.

    ```shell
    FULL_BACKUP_TS=`tiup br validate decode --field="end-version" --storage "s3://backup-101/snapshot-${date}?access-key=${access-key}&secret-access-key=${secret-access-key}"| tail -n1`
    ```

3. Delete log backup data earlier than the snapshot backup `FULL_BACKUP_TS`:

    ```shell
    tiup br log truncate --until=${FULL_BACKUP_TS} --storage='s3://backup-101/logbackup?access-key=${access-key}&secret-access-key=${secret-access-key}'
    ```

4. Delete snapshot data earlier than the snapshot backup `FULL_BACKUP_TS`:

    ```shell
    aws s3 rm --recursive s3://backup-101/snapshot-${date}
    ```
