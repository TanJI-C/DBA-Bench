# Log backup alert items

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-monitoring-and-alert.md`
- Source Title: `Monitoring and Alert for Backup and Restore`
- Source Heading Path: `Monitoring and Alert for Backup and Restore > Log backup monitoring > Log backup alerts > LogBackupFailed | Monitoring and Alert for Backup and Restore > Log backup monitoring > Log backup alerts > LogBackupGCSafePointExceedsCheckpoint`
- Source Line Ranges: `108-118`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `tidb`
- Topic Tags: `log backup`, `alert`, `critical`, `checkpoint`, `gc safe point`, `failure`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0016_32d96e2f33`
- Source ID: `tidb-docs-8.1:br/br-monitoring-and-alert.md#logbackupfailed`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `21b66e036f3f43af34350b1bcd4a244c37d6566952da9593f37fd82b2030ffca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-monitoring-and-alert#logbackupfailed
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-monitoring-and-alert.md

## Retrieval Guidance

- Use When: Use this chunk when someone asks about critical log backup alerts, their alert expressions, or what LogBackupFailed and LogBackupGCSafePointExceedsCheckpoint mean in BR monitoring.
- Retrieval Keywords: LogBackupFailed, LogBackupGCSafePointExceedsCheckpoint, max(tikv_log_backup_task_status) by (task) == 2 and max(tidb_log_backup_last_checkpoint) by (task) > 0, min(tidb_log_backup_last_checkpoint) by (instance) - max(tikv_gcworker_autogc_safe_point) by (instance) < 0, tikv_log_backup_task_status, tidb_log_backup_last_checkpoint, tikv_gcworker_autogc_safe_point, br log status, log backup task fails, gc safe point exceeds checkpoint, some data has been garbage-collected before the backup
- Follow-up Guidance: For LogBackupFailed, the content says to run `br log status` to see the failure reason and, if necessary, further check the TiKV logs.
- Classification Note: The classification is observability for the BR component because the content defines log backup alert items, alert levels, Prometheus-style alert expressions, and alert descriptions for backup monitoring.

## Official Source Content

#### LogBackupFailed

- Alert item: `max(tikv_log_backup_task_status) by (task) == 2 and max(tidb_log_backup_last_checkpoint) by (task) > 0`
- Alert level: critical
- Description: The log backup task fails. You need to run `br log status` to see the failure reason. If necessary, you need to further check the TiKV logs.
#### LogBackupGCSafePointExceedsCheckpoint

- Alert item: `min(tidb_log_backup_last_checkpoint) by (instance) - max(tikv_gcworker_autogc_safe_point) by (instance) < 0`
- Alert level: critical
- Description: Some data has been garbage-collected before the backup. This means that some data has been lost and is very likely to affect your services.
