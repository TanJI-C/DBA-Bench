# Enable DM safe mode automatically or manually

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-safe-mode.md`
- Source Title: `DM Safe Mode`
- Source Heading Path: `DM Safe Mode > Enable safe mode | DM Safe Mode > Enable safe mode > Automatically enable | DM Safe Mode > Enable safe mode > Manually enable`
- Source Line Ranges: `51-93`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `safe-mode`, `task-configuration`, `syncer`, `checkpoint`, `resume`, `safemode-exit-point`, `checkpoint-flush-interval`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0080_5a7d1dff25`
- Source ID: `tidb-docs-8.1:dm/dm-safe-mode.md#enable-safe-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `86a506b319d065fd49a8b14e39621e50acfcfbe69449c096f3992216f4bab10b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-safe-mode#enable-safe-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-safe-mode.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving when DM automatically enables safe mode after resuming from a checkpoint and how to enable it manually in task configuration.
- Retrieval Keywords: Enable safe mode, Automatically enable, Manually enable, safemode_exit_point, checkpoint, begin position, checkpoint-flush-interval, safe-mode, syncer configuration, syncers.global.safe-mode, 60 seconds, two checkpoint intervals
- Follow-up Guidance: The source provides a task configuration example with `syncers.global.safe-mode: true` and explains that automatic safe mode is disabled after the binlog position exceeds `safemode_exit_point` unless it is enabled manually.
- Classification Note: This is classified as configuration because the content describes automatic enablement conditions and the `safe-mode` and `checkpoint-flush-interval` configuration items.

## Official Source Content

## Enable safe mode

You can enable safe mode either automatically or manually. This section describes the detailed steps.
### Automatically enable

When DM resumes an incremental replication task from a checkpoint (For example, DM worker restart or network reconnection), DM automatically enables safe mode for a period (60 seconds by default).

Whether to enable safe mode is related to `safemode_exit_point` in the checkpoint. When an incremental replication task is paused abnormally, DM tries to replicate all DML statements in the memory to the downstream and records the latest binlog position among the DML statements as `safemode_exit_point`, which is saved to the last checkpoint.

The detailed logic is as follows:

- If the checkpoint contains `safemode_exit_point`, the incremental replication task is paused abnormally. When DM resumes the task, the binlog position of the checkpoint to be resumed (**begin position**) is earlier than `safemode_exit_point`, which represents the binlog events between the begin position and the `safemode_exit_point` might have been processed in the downstream. So, during the resume process, some binlog events might be executed repeatedly. Therefore, enabling safe mode can make these binlog positions **safe**. After the binlog position exceeds the `safemode_exit_point`, DM automatically disables safe mode unless safe mode is enabled manually.

- If the checkpoint does not contain `safemode_exit_point`, there are two cases:

    1. This is a new task, or this task is paused as expected.
    2. This task is paused abnormally but DM fails to record `safemode_exit_point`, or the DM process exits abnormally.

    In the second case, DM does not know which binlog events after the checkpoint are executed in the downstream. To ensure that repeatedly executed binlog events do not cause any problems, DM automatically enables safe mode during the first two checkpoint intervals. The default interval between two checkpoints is 30 seconds, which means when a normal incremental replication task starts, safe mode is enforced for the first 60 seconds (2 * 30 seconds).

    Usually, it is not recommended to change the checkpoint interval to adjust the safe mode period at the beginning of the incremental replication task. However, if you do need a change, you can [manually enable safe mode](#manually-enable) (recommended) or change the `checkpoint-flush-interval` item in syncer configuration.
### Manually enable

You can set the `safe-mode` item in the syncer configuration to enable safe mode during the entire replication process. `safe-mode` is a bool type parameter and is `false` by default. If it is set to `true`, DM enables safe mode for the whole incremental replication process. 

The following is a task configuration example with safe mode enabled:

```
syncers:                              # The running configurations of the sync processing unit.
  global:                            # Configuration name.
    # Other configuration items are not provided in this example.
    safe-mode: true                  # Enables safe mode for the whole incremental replication process.
    # Other configuration items are not provided in this example.
# ----------- Instance configuration -----------
mysql-instances:
  -
    source-id: "mysql-replica-01"
    # Other configuration items are not provided in this example.
    syncer-config-name: "global"            # Name of the syncers configuration.
```
