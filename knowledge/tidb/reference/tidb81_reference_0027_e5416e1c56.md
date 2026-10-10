# Amazon S3 Object Lock support and warning

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/backup-and-restore-storages.md`
- Source Title: `Backup Storages`
- Source Heading Path: `Backup Storages > Other features supported by the storage service`
- Source Line Ranges: `214-222`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `cloud`
- Topic Tags: `s3`, `object-lock`, `snapshot-backup`, `pitr`, `retention`, `warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0027_e5416e1c56`
- Source ID: `tidb-docs-8.1:br/backup-and-restore-storages.md#other-features-supported-by-the-storage-service`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e31bd99419f83accb3e807361e8b534bbb6a9f5ba41f6551a38eb4ac85ec9e5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages#other-features-supported-by-the-storage-service
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/backup-and-restore-storages.md

## Retrieval Guidance

- Use When: Use this chunk when asking about BR or PITR support for Amazon S3 Object Lock, automatic detection behavior, or the warning about backup failures when Object Lock is enabled during backup.
- Retrieval Keywords: Amazon S3 Object Lock, BR supports Amazon S3 Object Lock, PITR supports Amazon S3 Object Lock, snapshot backups, full backups, log data backups, PITR log backup, automatically detect whether the Amazon S3 Object Lock feature is enabled or disabled, backup might fail, restart the snapshot backup or PITR log backup task, retention period
- Follow-up Guidance: If the Object Lock feature is enabled during the snapshot backup or PITR log backup process, the snapshot backup or log backup might fail, and you need to restart the snapshot backup or PITR log backup task to continue the backup.
- Classification Note: This is reference content because it states support scope, automatic detection behavior, and a warning for Amazon S3 Object Lock in BR and PITR.

## Official Source Content

## Other features supported by the storage service

Amazon [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) can help prevent backup data from accidental or intentional deletion during a specified retention period, enhancing the security and integrity of data. Starting from v6.3.0, BR supports Amazon S3 Object Lock for snapshot backups, adding an additional layer of security for full backups. Starting from v8.0.0, PITR also supports Amazon S3 Object Lock. Whether for full backups or log data backups, the Object Lock feature ensures more reliable data protection, further strengthening the security of data backup and recovery and meeting regulatory requirements.

BR and PITR automatically detect whether the Amazon S3 Object Lock feature is enabled or disabled. You do not need to perform any additional operations.

> **Warning:**
>
> If the Object Lock feature is enabled during the snapshot backup or PITR log backup process, the snapshot backup or log backup might fail. You need to restart the snapshot backup or PITR log backup task to continue the backup.
