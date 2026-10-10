# DM instance metrics for relay log and task status

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/monitor-a-dm-cluster.md`
- Source Title: `Data Migration Monitoring Metrics`
- Source Heading Path: `Data Migration Monitoring Metrics > Instance > Relay log | Data Migration Monitoring Metrics > Instance > Task`
- Source Line Ranges: `132-156`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `monitoring`, `metrics`, `alerts`, `relay-log`, `task-state`, `binlog-replication`, `storage`, `load-progress`, `sharding-ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0043_a69e94f431`
- Source ID: `tidb-docs-8.1:dm/monitor-a-dm-cluster.md#relay-log`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `481eb52a1dd39945c08d9d915c4e4f78b7acf8c55b57dddb37b4cc172366f042`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/monitor-a-dm-cluster#relay-log
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/monitor-a-dm-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when looking for DM monitoring metrics and alert conditions related to relay log disk usage, relay log read or write errors, relay log corruption, upstream binlog lag, or subtask status and load progress.
- Retrieval Keywords: DM instance metrics, Relay log, Task, storage capacity, storage remain, process exits with error, relay log data corruption, fail to read binlog from master, fail to write relay log, binlog file index, binlog file gap between master and relay, binlog pos, read binlog duration, write relay log duration, binlog size, task state, load progress, binlog file gap between master and syncer, shard lock resolving, subtask has been paused for more than 10 minutes, waiting for sharding DDL migration
- Follow-up Guidance: The content also provides the alert thresholds and severity levels for storage remain, process exits with error, relay log data corruption, fail to read binlog from master, fail to write relay log, binlog file gap between master and relay, and task state.
- Classification Note: This is classified as observability for DM because it lists monitoring metric names, descriptions, and alert or severity information for relay log and task status in a self-managed DM cluster.

## Official Source Content

### Relay log

| Metric name | Description | Alert | Severity level |
|:----|:------------|:----|:----|
| storage capacity | The total storage capacity of the disk occupied by the relay log | N/A | N/A |
| storage remain | The remaining storage capacity within the disk occupied by the relay log | An alert occurs once the value is smaller than 10G | critical |
| process exits with error | The relay log encounters an error in DM-worker and exits | Immediate alerts | critical |
| relay log data corruption | The number of corrupted relay logs | Immediate alerts | emergency |
| fail to read binlog from master | The number of errors encountered when relay log reads the binlog from the upstream MySQL | Immediate alerts | critical |
| fail to write relay log | The number of errors encountered when the relay log writes the binlog to disks | Immediate alerts | critical |
| binlog file index | The largest index number of relay log files. For example, "value = 1" indicates "relay-log.000001" | N/A | N/A |
| binlog file gap between master and relay | The number of binlog files by which the `relay` processing unit is behind the upstream master | An alert occurs when the number of binlog files by which the `relay` processing unit is behind the upstream master exceeds one (>1) and the condition lasts over 10 minutes | critical |
| binlog pos | The write offset of the latest relay log file | N/A | N/A |
| read binlog duration | The duration that the relay log reads the binlog from the upstream MySQL (in seconds) | N/A | N/A |
| write relay log duration | The duration that the relay log writes the binlog into the disk each time (in seconds) | N/A | N/A |
| binlog size | The size of a single binlog event that the relay log writes into the disks | N/A | N/A |
### Task

| Metric name | Description | Alert | Severity level |
|:----|:------------|:----|:----|
| task state | The state of subtasks for migration | An alert occurs when the subtask has been paused for more than 10 minutes | critical |
| load progress | The percentage of the completed loading process of the load unit. The value range is 0%~100% | N/A | N/A |
| binlog file gap between master and syncer | The number of binlog files by which the binlog replication unit is behind the upstream master | N/A | N/A |
| shard lock resolving | Whether the current subtask is waiting for sharding DDL migration. A value greater than 0 means that the current subtask is waiting for sharding DDL migration | N/A | N/A |
