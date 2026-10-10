# PITR log backup alert rules and samples

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-monitoring-and-alert.md`
- Source Title: `Monitoring and Alert for Backup and Restore`
- Source Heading Path: `Monitoring and Alert for Backup and Restore > Log backup monitoring > Log backup alerts | Monitoring and Alert for Backup and Restore > Log backup monitoring > Log backup alerts > Alert configuration | Monitoring and Alert for Backup and Restore > Log backup monitoring > Log backup alerts > LogBackupRunningRPOMoreThan10m | Monitoring and Alert for Backup and Restore > Log backup monitoring > Log backup alerts > LogBackupRunningRPOMoreThan30m | Monitoring and Alert for Backup and Restore > Log backup monitoring > Log backup alerts > LogBackupPausingMoreThan2h | Monitoring and Alert for Backup and Restore > Log backup monitoring > Log backup alerts > LogBackupPausingMoreThan12h`
- Source Line Ranges: `55-107`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `shared`
- Topic Tags: `alerts`, `prometheus`, `pitr`, `log-backup`, `rpo`, `checkpoint`, `paused-task`, `rule-files`, `reload`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0015_58fb018362`
- Source ID: `tidb-docs-8.1:br/br-monitoring-and-alert.md#log-backup-alerts`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `89c60a8aa9f279513b9e5164c56f9d887a04c1028a49cf385c9c985ee71fb392`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-monitoring-and-alert#log-backup-alerts
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-monitoring-and-alert.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to configure Prometheus alert rules for PITR log backup RPO or paused-task conditions, including exact rule expressions and reload methods.
- Retrieval Keywords: Log backup alerts, PITR does not have built-in alert items, pitr.rules.yml, rule_files, SIGHUP, kill -HUP pid, http://prometheus-addr/-/reload, --web.enable-lifecycle, LogBackupRunningRPOMoreThan10m, LogBackupRunningRPOMoreThan30m, LogBackupPausingMoreThan2h, LogBackupPausingMoreThan12h, tidb_log_backup_last_checkpoint, tikv_log_backup_task_status, severity: warning, severity: critical, br log resume, RPO of log backup is high
- Follow-up Guidance: The source says that a 30-minute running RPO alert often indicates anomalies and you can check the TiKV logs to find the cause, while paused-task alerts expect `br log resume` as soon as possible.
- Classification Note: This is observability content because it defines official Prometheus alert configuration steps, recommended PITR alert items, exact alert expressions, severities, and related operational signals.

## Official Source Content

### Log backup alerts
#### Alert configuration

Currently, PITR does not have built-in alert items. This section introduces how to configure alert items in PITR and recommends some items.

To configure alert items in PITR, follow these steps:

1. Create a configuration file (for example, `pitr.rules.yml`) for the alert rules on the node where Prometheus is located. In the file, fill in the alert rules according to the [Prometheus documentation](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/), the following recommended alert items, and the configuration sample.
2. In the `rule_files` field of the Prometheus configuration file, add the path of the alert rule file.
3. Send `SIGHUP` signal to the Prometheus process (`kill -HUP pid`) or send an HTTP `POST` request to `http://prometheus-addr/-/reload` (before you send the HTTP request, add the `--web.enable-lifecycle` parameter when starting Prometheus).

The recommended alert items are as follows:
#### LogBackupRunningRPOMoreThan10m

- Alert item: `max(time() - tidb_log_backup_last_checkpoint / 262144000) by (task) / 60 > 10 and max(tidb_log_backup_last_checkpoint) by (task) > 0 and max(tikv_log_backup_task_status) by (task) == 0`
- Alert level: warning
- Description: The log data is not persisted to the storage for more than 10 minutes. This alert item is a reminder. In most cases, it does not affect log backup.

A configuration sample of this alert item is as follows:

```yaml
groups:
- name: PiTR
  rules:
  - alert: LogBackupRunningRPOMoreThan10m
    expr: max(time() - tidb_log_backup_last_checkpoint / 262144000) by (task) / 60 > 10 and max(tidb_log_backup_last_checkpoint) by (task) > 0 and max(tikv_log_backup_task_status) by (task) == 0
    labels:
      severity: warning
    annotations:
      summary: RPO of log backup is high
      message: RPO of the log backup task {{ $labels.task }} is more than 10m
```
#### LogBackupRunningRPOMoreThan30m

- Alert item: `max(time() - tidb_log_backup_last_checkpoint / 262144000) by (task) / 60 > 30 and max(tidb_log_backup_last_checkpoint) by (task) > 0 and max(tikv_log_backup_task_status) by (task) == 0`
- Alert level: critical
- Description: The log data is not persisted to the storage for more than 30 minutes. This alert often indicates anomalies. You can check the TiKV logs to find the cause.
#### LogBackupPausingMoreThan2h

- Alert item: `max(time() - tidb_log_backup_last_checkpoint / 262144000) by (task) / 3600 > 2 and max(tidb_log_backup_last_checkpoint) by (task) > 0 and max(tikv_log_backup_task_status) by (task) == 1`
- Alert level: warning
- Description: The log backup task is paused for more than 2 hours. This alert item is a reminder and you are expected to run `br log resume` as soon as possible.
#### LogBackupPausingMoreThan12h

- Alert item: `max(time() - tidb_log_backup_last_checkpoint / 262144000) by (task) / 3600 > 12 and max(tidb_log_backup_last_checkpoint) by (task) > 0 and max(tikv_log_backup_task_status) by (task) == 1`
- Alert level: critical
- Description: The log backup task is paused for more than 12 hours. You are expected to run `br log resume` as soon as possible to resume the task. Log tasks paused for too long have the risk of data loss.
