# DM alert handling reference

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-handle-alerts.md`
- Source Title: `Handle Alerts in TiDB Data Migration`
- Source Heading Path: `Handle Alerts in TiDB Data Migration | Handle Alerts in TiDB Data Migration > Alerts related to high availability | Handle Alerts in TiDB Data Migration > Alerts related to high availability > `DM_master_all_down` | Handle Alerts in TiDB Data Migration > Alerts related to high availability > `DM_worker_offline` | Handle Alerts in TiDB Data Migration > Alerts related to high availability > `DM_DDL_error` | Handle Alerts in TiDB Data Migration > Alerts related to high availability > `DM_pending_DDL` | Handle Alerts in TiDB Data Migration > Alert rules related to task status | Handle Alerts in TiDB Data Migration > Alert rules related to task status > `DM_task_state` | Handle Alerts in TiDB Data Migration > Alert rules related to relay log | Handle Alerts in TiDB Data Migration > Alert rules related to relay log > `DM_relay_process_exits_with_error` | Handle Alerts in TiDB Data Migration > Alert rules related to relay log > `DM_remain_storage_of_relay_log` | Handle Alerts in TiDB Data Migration > Alert rules related to relay log > `DM_relay_log_data_corruption` | Handle Alerts in TiDB Data Migration > Alert rules related to relay log > `DM_fail_to_read_binlog_from_master` | Handle Alerts in TiDB Data Migration > Alert rules related to relay log > `DM_fail_to_write_relay_log` | Handle Alerts in TiDB Data Migration > Alert rules related to relay log > `DM_binlog_file_gap_between_master_relay` | Handle Alerts in TiDB Data Migration > Alert rules related to Dump/Load | Handle Alerts in TiDB Data Migration > Alert rules related to Dump/Load > `DM_dump_process_exists_with_error` | Handle Alerts in TiDB Data Migration > Alert rules related to Dump/Load > `DM_load_process_exists_with_error` | Handle Alerts in TiDB Data Migration > Alert rules related to binlog replication | Handle Alerts in TiDB Data Migration > Alert rules related to binlog replication > `DM_sync_process_exists_with_error` | Handle Alerts in TiDB Data Migration > Alert rules related to binlog replication > `DM_binlog_file_gap_between_master_syncer` | Handle Alerts in TiDB Data Migration > Alert rules related to binlog replication > `DM_binlog_file_gap_between_relay_syncer``
- Source Line Ranges: `5-189`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `alerts`, `high-availability`, `task-status`, `relay-log`, `dump-load`, `binlog-replication`, `troubleshooting`, `disk-space`, `paused-state`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0040_0352da4e59`
- Source ID: `tidb-docs-8.1:dm/dm-handle-alerts.md#handle-alerts-in-tidb-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `423839f45ef7743aa24a39d96ce8c652e769fd73153c37ac7c8949861dcdf54e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-handle-alerts#handle-alerts-in-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-handle-alerts.md

## Retrieval Guidance

- Use When: Use this chunk when looking up what specific DM alert names mean and the documented handling references for DM-master, DM-worker, task state, relay log, dump/load, binlog replication, disk space, and sharding DDL situations.
- Retrieval Keywords: Handle Alerts in TiDB Data Migration, DM_master_all_down, DM_worker_offline, DM_DDL_error, DM_pending_DDL, DM_task_state, Paused, DM_relay_process_exits_with_error, DM_remain_storage_of_relay_log, pause-relay, resume-relay, DM_relay_log_data_corruption, DM_fail_to_read_binlog_from_master, DM_fail_to_write_relay_log, DM_binlog_file_gap_between_master_relay, DM_dump_process_exists_with_error, DM_load_process_exists_with_error, DM_sync_process_exists_with_error, DM_binlog_file_gap_between_master_syncer, DM_binlog_file_gap_between_relay_syncer, Troubleshoot DM, Handle Sharding DDL Locks Manually in DM, Handle Performance Issues, automatic data purge strategy of the relay log, manual-purge, free space of the disk where the relay log is located is less than 10G
- Follow-up Guidance: The content points to Troubleshoot DM for multiple alerts, Handle Sharding DDL Locks Manually in DM for pending sharding DDL, and Handle Performance Issues for the two binlog file gap alerts related to syncer processing.
- Classification Note: The official content is classified as observability for the self-managed DM component because it is a reference for alert descriptions and documented handling steps across DM high availability, task status, relay log, dump/load, and binlog replication.

## Official Source Content

# Handle Alerts in TiDB Data Migration

This document introduces how to deal with the alert information in DM.
## Alerts related to high availability
### `DM_master_all_down`

- Description:

    If all DM-master nodes are offline, this alert is triggered.

- Solution:

    You can take the following steps to handle the alert:

    1. Check the environment of the cluster.
    2. Check the logs of all DM-master nodes for troubleshooting.
### `DM_worker_offline`

- Description:

    If a DM-worker node is offline for more than one hour, this alert is triggered. In a high-availability architecture, this alert might not directly interrupt the task but increases the risk of interruption.

- Solution:

    You can take the following steps to handle the alert:

    1. View the working status of the corresponding DM-worker node.
    2. Check whether the node is connected.
    3. Troubleshoot errors through logs.
### `DM_DDL_error`

- Description:

    This error occurs when DM is processing the sharding DDL operations.

- Solution:

    Refer to [Troubleshoot DM](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#troubleshooting).
### `DM_pending_DDL`

- Description:

    If a sharding DDL operation is pending for more than one hour, this alert is triggered.

- Solution:

    In some scenarios, the pending sharding DDL operation might be what users expect. Otherwise, refer to [Handle Sharding DDL Locks Manually in DM](https://docs.pingcap.com/tidb/stable/dm/manually-handling-sharding-ddl-locks) for solution.
## Alert rules related to task status
### `DM_task_state`

- Description:

    When a sub-task of DM-worker is in the `Paused` state for over 20 minutes, an alert is triggered.

- Solution:

    Refer to [Troubleshoot DM](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#troubleshooting).
## Alert rules related to relay log
### `DM_relay_process_exits_with_error`

- Description:

    When the relay log processing unit encounters a non-autorecoverable error (for example, binlog files not found), or when it encounters multiple recoverable errors (for example, network problems) in a short period of time (for example, more than 3 times in 2 minutes), this alert is triggered.

- Solution:

    Refer to [Troubleshoot DM](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#troubleshooting).
### `DM_remain_storage_of_relay_log`

- Description:

    When the free space of the disk where the relay log is located is less than 10G, an alert is triggered.

- Solutions:

    You can take the following methods to handle the alert:

    - Delete unwanted data manually to increase free disk space.
    - Reconfigure the [automatic data purge strategy of the relay log](https://docs.pingcap.com/tidb/stable/dm/relay-log#automatic-purge) or [purge data manually](https://docs.pingcap.com/tidb/stable/dm/relay-log#manual-purge).
    - Execute the command `pause-relay` to pause the relay log pulling process. After there is enough free disk space, resume the process by running the command `resume-relay`. Note that you must not purge upstream binlog files that have not been pulled after the relay log pulling process is paused.
### `DM_relay_log_data_corruption`

- Description:

    When the relay log processing unit validates the binlog event read from the upstream and detects abnormal checksum information, this unit moves to the `Paused` state, and an alert is triggered.

- Solution:

    Refer to [Troubleshoot DM](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#troubleshooting).
### `DM_fail_to_read_binlog_from_master`

- Description:

    If an error occurs when the relay log processing unit tries to read the binlog event from the upstream, this unit moves to the `Paused` state, and an alert is triggered.

- Solution:

    Refer to [Troubleshoot DM](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#troubleshooting).
### `DM_fail_to_write_relay_log`

- Description:

    If an error occurs when the relay log processing unit tries to write the binlog event into the relay log file, this unit moves to the `Paused` state, and an alert is triggered.

- Solution:

    Refer to [Troubleshoot DM](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#troubleshooting).
### `DM_binlog_file_gap_between_master_relay`

- Description:

    When the number of the binlog files in the current upstream MySQL/MariaDB exceeds that of the latest binlog files pulled by the relay log processing unit by **more than** 1 for 10 minutes, and an alert is triggered.

- Solution:

    Refer to [Troubleshoot DM](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#troubleshooting).
## Alert rules related to Dump/Load
### `DM_dump_process_exists_with_error`

- Description:

    When the Dump processing unit encounters a non-autorecoverable error (for example, binlog files not found), or when it encounters multiple recoverable errors (for example, network problems) in a short period of time (for example, more than 3 times in 2 minutes), this alert is triggered.

- Solution:

    Refer to [Troubleshoot DM](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#troubleshooting).
### `DM_load_process_exists_with_error`

- Description:

    When the Load processing unit encounters a non-autorecoverable error (for example, binlog files not found), or when it encounters multiple recoverable errors (for example, network problems) in a short period of time (for example, more than 3 times in 2 minutes), this alert is triggered.

- Solution:

    Refer to [Troubleshoot DM](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#troubleshooting).
## Alert rules related to binlog replication
### `DM_sync_process_exists_with_error`

- Description:

    When the binlog replication processing unit encounters a non-autorecoverable error (for example, binlog files not found), or when it encounters multiple recoverable errors (for example, network problems) in a short period of time (for example, more than 3 times in 2 minutes), this alert is triggered.

- Solution:

    Refer to [Troubleshoot DM](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#troubleshooting).
### `DM_binlog_file_gap_between_master_syncer`

- Description:

    When the number of the binlog files in the current upstream MySQL/MariaDB exceeds that of the latest binlog files processed by the relay log processing unit by **more than** 1 for 10 minutes, an alert is triggered.

- Solution:

    Refer to [Handle Performance Issues](https://docs.pingcap.com/tidb/stable/dm/dm-handle-performance-issues).
### `DM_binlog_file_gap_between_relay_syncer`

- Description:

    When the number of the binlog files in the current relay log processing unit exceeds that of the latest binlog files processed by the binlog replication processing unit by **more than** 1 for 10 minutes, an alert is triggered.

- Solution:

    Refer to [Handle Performance Issues](https://docs.pingcap.com/tidb/stable/dm/dm-handle-performance-issues).
