# DM migration and replication error troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-troubleshooting-map.md`
- Source Title: `TiDB Troubleshooting Map`
- Source Heading Path: `TiDB Troubleshooting Map > 6. Ecosystem tools > 6.2 Data Migration`
- Source Line Ranges: `470-517`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `tikv`
- Topic Tags: `migration`, `replication`, `authentication`, `privileges`, `connection-errors`, `relay-log`, `binlog`, `gtid`, `utf8`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0113_e95061992e`
- Source ID: `tidb-docs-8.1:tidb-troubleshooting-map.md#6-2-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2048e8eda4017521acc1fe3063867eedf3ad2f1afc405488b394a8031e1fe96`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-troubleshooting-map#6-2-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-troubleshooting-map.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting DM migration or replication errors such as access denied, bad connection, invalid connection, binlog parsing failures, GTID purge errors, or incorrect utf8 value messages.
- Retrieval Keywords: DM Data Migration, query status, query-status, query-error, Access denied for user 'root'@'172.31.43.27', driver: bad connection, invalid connection, event from * in * diff from passed-in event *, get binlog error ERROR 1236 (HY000), binlog checksum mismatch, relay.meta, CHANGE MASTER TO MASTER_AUTO_POSITION = 1, tidb_skip_utf8_check, stop-task, start-task
- Follow-up Guidance: Check the specific DM error text and the related notes about privileges, relay.meta, binlog size, or UTF-8 handling.
- Classification Note: This chunk is classified as diagnosis for the DM ecosystem tool and collects troubleshooting notes for replication and migration failures.

## Official Source Content

### 6.2 Data Migration

- 6.2.1 TiDB Data Migration (DM) is a migration tool that supports data migration from MySQL/MariaDB into TiDB. For details, see [DM overview](https://docs.pingcap.com/tidb/stable/dm/dm-overview).

- 6.2.2 `Access denied for user 'root'@'172.31.43.27' (using password: YES)` shows when you run `query status` or check the log.

    - The database related passwords in all the DM configuration files should be encrypted by `dmctl`. If a database password is empty, it is unnecessary to encrypt the password. Cleartext passwords can be used since v1.0.6.
    - During DM operation, the user of the upstream and downstream databases must have the corresponding read and write privileges. Data Migration also [prechecks the corresponding privileges](https://docs.pingcap.com/tidb/stable/dm/dm-precheck) automatically while starting the data replication task.
    - To deploy different versions of DM-worker/DM-master/dmctl in a DM cluster, see the [case study on AskTUG](https://pingkai.cn/tidbcommunity/forum/t/topic/1049/5) in Chinese.

- 6.2.3 A replication task is interrupted with the `driver: bad connection` error returned.

    - The `driver: bad connection` error indicates that an anomaly has occurred in the connection between DM and the downstream TiDB database (such as network failure and TiDB restart), and that the data of the current request has not yet been sent to TiDB.

        - For versions earlier than DM 1.0.0 GA, stop the task by running `stop-task` and then restart the task by running `start-task`.
        - For DM 1.0.0 GA or later versions, an automatic retry mechanism for this type of error is added. See [#265](https://github.com/pingcap/dm/pull/265).

- 6.2.4 A replication task is interrupted with the `invalid connection` error.

    - The `invalid connection` error indicates that an anomaly has occurred in the connection between DM and the downstream TiDB database (such as network failure, TiDB restart, and TiKV busy), and that a part of the data for the current request has been sent to TiDB. Because DM has the feature of concurrently replicating data to the downstream in replication tasks, several errors might occur when a task is interrupted. You can check these errors by running `query-status` or `query-error`.

        - If only the `invalid connection` error occurs during the incremental replication process, DM retries the task automatically.
        - If DM does not retry or fails to retry automatically because of version problems (automatic retry is introduced in v1.0.0-rc.1), use `stop-task` to stop the task and then use `start-task` to restart the task.

- 6.2.5 The relay unit reports the error `event from * in * diff from passed-in event *`, or a replication task is interrupted with an error that fails to get or parse binlog, such as `get binlog error ERROR 1236 (HY000) and binlog checksum mismatch, data may be corrupted returned`

    - During the process that DM pulls relay log or the incremental replication, this two errors might occur if the size of the upstream binlog file exceeds 4 GB.

    - Cause: When writing relay logs, DM needs to perform event verification based on binlog positions and the binlog file size, and store the replicated binlog positions as checkpoints. However, the official MySQL uses uint32 to store binlog positions, which means the binlog position for a binlog file over 4 GB overflows, and then the errors above occur.

    - Solution:

        - For relay processing units, [manually recover replication](https://pingcap.com/docs/tidb-data-migration/dev/error-handling/#the-relay-unit-throws-error-event-from--in--diff-from-passed-in-event--or-a-replication-task-is-interrupted-with-failing-to-get-or-parse-binlog-errors-like-get-binlog-error-error-1236-hy000-and-binlog-checksum-mismatch-data-may-be-corrupted-returned).
        - For binlog replication processing units, [manually recover replication](https://pingcap.com/docs/tidb-data-migration/dev/error-handling/#the-relay-unit-throws-error-event-from--in--diff-from-passed-in-event--or-a-replication-task-is-interrupted-with-failing-to-get-or-parse-binlog-errors-like-get-binlog-error-error-1236-hy000-and-binlog-checksum-mismatch-data-may-be-corrupted-returned).

- 6.2.6 The DM replication is interrupted, and the log returns `ERROR 1236 (HY000) The slave is connecting using CHANGE MASTER TO MASTER_AUTO_POSITION = 1, but the master has purged binary logs containing GTIDs that the slave requires.`

    - Check whether the master binlog is purged.
    - Check the position information recorded in `relay.meta`.

        - `relay.meta` has recorded the empty GTID information. DM-worker saves the GTID information in memory to `relay.meta` when it exits or in every 30s. When DM-worker does not obtain the upstream GTID information, it saves the empty GTID information to `relay.meta`. See [case-772](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case772.md) in Chinese.

        - The binlog event recorded in `relay.meta` triggers the incomplete recover process and records the wrong GTID information. This issue is fixed in v1.0.2, and might occur in earlier versions. <!--See [case-764](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case764.md).-->

- 6.2.7 The DM replication process returns an error `Error 1366: incorrect utf8 value eda0bdedb29d(\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd)`.

    - This value cannot be successfully written into MySQL 8.0 or TiDB, but can be written into MySQL 5.7. You can skip the data format check by enabling the `tidb_skip_utf8_check` parameter.
