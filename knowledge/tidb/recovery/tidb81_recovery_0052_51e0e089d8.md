# TiDB Cloud backup and restore concepts

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/backup-and-restore-concepts.md`
- Source Title: `Backup & Restore`
- Source Heading Path: `Backup & Restore | Backup & Restore > Automatic backup | Backup & Restore > Manual backup | Backup & Restore > Dual region backup | Backup & Restore > Point-in-time Restore`
- Source Line Ranges: `5-42`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `backup`, `restore`, `automatic-backup`, `manual-backup`, `dual-region`, `cross-region`, `disaster-recovery`, `pitr`, `retention-policy`, `serverless`, `dedicated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0052_51e0e089d8`
- Source ID: `tidb-docs-8.1:tidb-cloud/backup-and-restore-concepts.md#backup-restore`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `395da15adc2fc9d54397801d1d8ce35c2179e1b643df607513d824da77a4876d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore-concepts#backup-restore
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/backup-and-restore-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiDB Cloud Backup & Restore concepts, including automatic backup, manual backup, dual region backup, backup retention policy, and Point-in-time Restore for Serverless or Dedicated clusters.
- Retrieval Keywords: TiDB Cloud Backup & Restore, automatic backup, snapshot backups, backup retention policy, TiDB Cloud Serverless, TiDB Cloud Dedicated, manual backup, dual region backup, cross-region data protection, disaster recovery, Point-in-time Restore, PITR, restore to a new cluster, scalable clusters, free clusters, enable PITR
- Follow-up Guidance: The source points to more detailed pages for automatic backups, performing a manual backup, turning on dual region backup, and enabling Point-in-time Restore.
- Classification Note: This is classified as recovery content because the official content describes backup and restore features used to safeguard data, recover cluster data, and restore to a specific point in time.

## Official Source Content

# Backup & Restore

TiDB Cloud Backup & Restore features are designed to safeguard your data and ensure business continuity by enabling you to back up and recover cluster data.
## Automatic backup

For both TiDB Cloud Serverless and TiDB Cloud Dedicated clusters, snapshot backups are taken automatically by default and stored according to your backup retention policy.

For more information, see the following:

- [Automatic backups for TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore-serverless#automatic-backups)
- [Automatic backups for TiDB Cloud Dedicated clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-auto-backup)
## Manual backup

Manual backup is a feature of TiDB Cloud Dedicated that enables you to back up your data to a known state as needed, and then restore to that state at any time.

For more information, see [Perform a manual backup](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#perform-a-manual-backup).
## Dual region backup

Dual region backup is a feature of TiDB Cloud Dedicated that enables you to replicate backups from your cluster region to another different region. After it is enabled, all backups are automatically replicated to the specified region. This provides cross-region data protection and disaster recovery capabilities. It is estimated that approximately 99% of the data can be replicated to the secondary region within an hour.

For more information, see [Turn on dual region backup](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-dual-region-backup).
## Point-in-time Restore

Point-in-time Restore is a feature that enables you to restore data of any point in time to a new cluster. You can use it to:

- Reduce RPO in disaster recovery.
- Resolve cases of data write errors by restoring point-in-time that is before the error event.
- Audit the historical data of the business.

If you want to perform Point-in-time Restore, note the following:

- For TiDB Cloud Serverless clusters, Point-in-time Restore is available only for scalable clusters and not available for free clusters. For more information, see [Restore mode](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore-serverless#restore-mode).
- For TiDB Cloud Dedicated clusters, you need to [enable PITR](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-point-in-time-restore) in advance.
