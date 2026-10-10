# DM v2.0 inconsecutive Syncer checkpoint GTIDs with relay and GTID enabled

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-faq.md`
- Source Title: `TiDB Data Migration FAQs`
- Source Heading Path: `TiDB Data Migration FAQs > In DM v2.0, why does the query result of the command `query-status` show that the Syncer checkpoint GTIDs are inconsecutive if the task has `enable-relay` and `enable-gtid` enabled at the same time?`
- Source Line Ranges: `250-354`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `sql`
- Topic Tags: `gtid`, `relay-log`, `query-status`, `incremental-task`, `safe-mode`, `binlog`, `metadata`, `data-loss`, `bugfix`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0017_63a8e75a4f`
- Source ID: `tidb-docs-8.1:dm/dm-faq.md#in-dm-v2-0-why-does-the-query-result-of-the-command-query-status-show-that-the-syncer-checkpoint-gtids-are-inconsecutive-if-the-task-has-enable-relay-and-enable-gtid-enabled-at-the-same-time`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `11a0cbac326696920ccb4777e66add0564289c1ff36ef2c86728b7a59de9e429`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-faq#in-dm-v2-0-why-does-the-query-result-of-the-command-query-status-show-that-the-syncer-checkpoint-gtids-are-inconsecutive-if-the-task-has-enable-relay-and-enable-gtid-enabled-at-the-same-time
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-faq.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing DM v2.0 `query-status` output where `subTaskStatus.sync.syncerBinlogGtid` is inconsecutive while `subTaskStatus.sync.masterBinlogGtid` is consecutive with both `enable-relay` and `enable-gtid` enabled.
- Retrieval Keywords: query-status <task>, subTaskStatus.sync.syncerBinlogGtid, subTaskStatus.sync.masterBinlogGtid, enable-relay, enable-gtid, show binlog events in '<newest-binlog>' limit 2, previous_gtids, MySQL secondary database, syncers.safe-mode, mysql-instances.meta, binlog-name, binlog-pos, binlog-gtid, start-task task.yaml --remove-meta, relay log, local relay logs, data loss, DM v2.0.2
- Follow-up Guidance: The content provides handling paths based on whether upstream binlogs are purged, whether local relay logs remain, and whether unaffected sources should use `syncerBinlog` and `syncerBinlogGtid` from `subTaskStatus.sync` in the incremental task metadata.
- Classification Note: This chunk is classified as recovery because it describes a known DM bug that can cause data loss and gives concrete recovery procedures using incremental tasks, metadata, and `safe-mode`.

## Official Source Content

## In DM v2.0, why does the query result of the command `query-status` show that the Syncer checkpoint GTIDs are inconsecutive if the task has `enable-relay` and `enable-gtid` enabled at the same time?

This is a known bug in DM, which is fixed in DM v2.0.2. The bug is triggered when the following two conditions are fully met at the same time:

1. Parameters `enable-relay` and `enable-gtid` are set to `true` in the source configuration file.
2. The upstream database is a **MySQL secondary database**. If you execute the command `show binlog events in '<newest-binlog>' limit 2` to query the `previous_gtids` of the database, the result is inconsecutive, such as the following example:

```
mysql> show binlog events in 'mysql-bin.000005' limit 2;
+------------------+------+----------------+-----------+-------------+--------------------------------------------------------------------+
| Log_name         | Pos  | Event_type     | Server_id | End_log_pos | Info                                                               |
+------------------+------+----------------+-----------+-------------+--------------------------------------------------------------------+
| mysql-bin.000005 |    4 | Format_desc    |    123452 |         123 | Server ver: 5.7.32-35-log, Binlog ver: 4                           |
| mysql-bin.000005 |  123 | Previous_gtids |    123452 |         194 | d3618e68-6052-11eb-a68b-0242ac110002:6-7                           |
+------------------+------+----------------+-----------+-------------+--------------------------------------------------------------------+
```

The bug occurs if you run `query-status <task>` in dmctl to query task information and find that `subTaskStatus.sync.syncerBinlogGtid` is inconsecutive but `subTaskStatus.sync.masterBinlogGtid` is consecutive. See the following example:

```
query-status test
{
    ...
    "sources": [
        {
            ...
            "sourceStatus": {
                "source": "mysql1",
                ...
                "relayStatus": {
                    "masterBinlog": "(mysql-bin.000006, 744)",
                    "masterBinlogGtid": "f8004e25-6067-11eb-9fa3-0242ac110003:1-50",
                    ...
                }
            },
            "subTaskStatus": [
                {
                    ...
                    "sync": {
                        ...
                        "masterBinlog": "(mysql-bin.000006, 744)",
                        "masterBinlogGtid": "f8004e25-6067-11eb-9fa3-0242ac110003:1-50",
                        "syncerBinlog": "(mysql-bin|000001.000006, 738)",
                        "syncerBinlogGtid": "f8004e25-6067-11eb-9fa3-0242ac110003:1-20:40-49",
                        ...
                        "synced": false,
                        "binlogType": "local"
                    }
                }
            ]
        },
        {
            ...
            "sourceStatus": {
                "source": "mysql2",
                ...
                "relayStatus": {
                    "masterBinlog": "(mysql-bin.000007, 1979)",
                    "masterBinlogGtid": "ddb8974e-6064-11eb-8357-0242ac110002:1-25",
                    ...
                }
            },
            "subTaskStatus": [
                {
                    ...
                    "sync": {
                        "masterBinlog": "(mysql-bin.000007, 1979)",
                        "masterBinlogGtid": "ddb8974e-6064-11eb-8357-0242ac110002:1-25",
                        "syncerBinlog": "(mysql-bin|000001.000008, 1979)",
                        "syncerBinlogGtid": "ddb8974e-6064-11eb-8357-0242ac110002:1-25",
                        ...
                        "synced": true,
                        "binlogType": "local"
                    }
                }
            ]
        }
    ]
}
```

In the example, the `syncerBinlogGtid` of the data source `mysql1` is inconsecutive. In this case, you can do one of the following to handle the data loss:

- If upstream binlogs from the current time to the position recorded in the metadata of the full export task have not been purged, you can take these steps:
    1. Stop the current task and delete all data sources with inconsecutive GTIDs.
    2. Set `enable-relay` to `false` in all source configuration files.
    3. For data sources with inconsecutive GTIDs (such as `mysql1` in the above example), change the task to an incremental task and configure related `mysql-instances.meta` with metadata information of each full export task, including the `binlog-name`, `binlog-pos`, and `binlog-gtid` information.
    4. Set `syncers.safe-mode` to `true` in `task.yaml` of the incremental task and restart the task.
    5. After the incremental task replicates all missing data to the downstream, stop the task and change `safe-mode` to `false` in the `task.yaml`.
    6. Restart the task again.
- If upstream binlogs have been purged but local relay logs remain, you can take these steps:
    1. Stop the current task.
    2. For data sources with inconsecutive GTIDs (such as `mysql1` in the above example), change the task to an incremental task and configure related `mysql-instances.meta` with metadata information of each full export task, including the `binlog-name`, `binlog-pos`, and `binlog-gtid` information.
    3. In the `task.yaml` of the incremental task, change the previous value of `binlog-gtid` to the previous value of `previous_gtids`. For the above example, change `1-y` to `6-y`.
    4. Set `syncers.safe-mode` to `true` in the `task.yaml` and restart the task.
    5. After the incremental task replicates all missing data to the downstream, stop the task and change `safe-mode` to `false` in the `task.yaml`.
    6. Restart the task again.
    7. Restart the data source and set either `enable-relay` or `enable-gtid` to `false` in the source configuration file.
- If none of the above conditions is met or if the data volume of the task is small, you can take these steps:
    1. Clean up imported data in the downstream database.
    2. Restart the data source and set either `enable-relay` or `enable-gtid` to `false` in the source configuration file.
    3. Create a new task and run the command `start-task task.yaml --remove-meta` to migrate data from the beginning again.

For data sources that can be replicated normally (such as `mysql2` in the above example) in the first and second solutions above, configure related `mysql-instances.meta` with `syncerBinlog` and `syncerBinlogGtid` information from `subTaskStatus.sync` when setting the incremental task.
