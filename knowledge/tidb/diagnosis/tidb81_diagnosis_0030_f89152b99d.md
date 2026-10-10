# DM FAQ: adding tables, import and checkpoint errors, monitoring, and version issues

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-faq.md`
- Source Title: `TiDB Data Migration FAQs`
- Source Heading Path: `TiDB Data Migration FAQs > How to add tables to the existing data migration tasks? | TiDB Data Migration FAQs > How to add tables to the existing data migration tasks? > In the `Dump` stage | TiDB Data Migration FAQs > How to add tables to the existing data migration tasks? > In the `Load` stage | TiDB Data Migration FAQs > How to add tables to the existing data migration tasks? > In the `Sync` stage | TiDB Data Migration FAQs > How to handle the error `packet for query is too large. Try adjusting the 'max_allowed_packet' variable` that occurs during the full import? | TiDB Data Migration FAQs > How to handle the error `Error 1054: Unknown column 'binlog_gtid' in 'field list'` that occurs when existing DM migration tasks of an DM 1.0 cluster are running on a DM 2.0 or newer cluster? | TiDB Data Migration FAQs > Why does TiUP fail to deploy some versions of DM (for example, v2.0.0-hotfix)? | TiDB Data Migration FAQs > How to handle the error `parse mydumper metadata error: EOF` that occurs when DM is replicating data? | TiDB Data Migration FAQs > Why does DM report no fatal error when replicating sharded schemas and tables, but downstream data is lost? | TiDB Data Migration FAQs > Why does the `replicate lag` monitor metric show no data when DM is not replicating from upstream? | TiDB Data Migration FAQs > How to handle the error `fail to initial unit Sync of subtask` when DM is starting a task, with the `RawCause` in the error message showing `context deadline exceeded`?`
- Source Line Ranges: `81-158`
- Source Scope: `shared`
- Primary Component: `dm`
- Related Components: `tidb`, `tiup`
- Topic Tags: `add-tables`, `dump`, `load`, `sync`, `checkpoint`, `safe-mode`, `max-allowed-packet`, `upgrade`, `deployment`, `metadata`, `sharding`, `monitoring`, `heartbeat`, `version-specific`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0030_f89152b99d`
- Source ID: `tidb-docs-8.1:dm/dm-faq.md#how-to-add-tables-to-the-existing-data-migration-tasks`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e0d58fcaa9894768ace285549b8f5a2570d5daaa862439a0db13e7ce21ef993`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-faq#how-to-add-tables-to-the-existing-data-migration-tasks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-faq.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing DM issues related to adding tables by task stage, full import packet size errors, checkpoint migration errors, TiUP deployment versions, mydumper metadata parsing, sharded table configuration mismatches, missing replicate lag metrics, or Sync initialization timeouts.
- Retrieval Keywords: add tables to the existing data migration tasks, Dump stage, Load stage, Sync stage, global checkpoint, is_global=1, checkpoint-T, checkpoint-S, {task-name}_syncer_checkpoint, {dm_meta}, binlog_name, binlog_pos, safe-mode: true, query-status, syncerBinlog, packet for query is too large, max_allowed_packet, target-database.max-allowed-packet, Error 1054: Unknown column 'binlog_gtid' in 'field list', manually importing DM migration tasks of a DM 1.0 cluster to a DM 2.0 cluster, tiup list dm-master, parse mydumper metadata error: EOF, block-allow-list, table-route, wildcard characters instead of regular expressions, replicate lag, enable-heartbeat, fail to initial unit Sync of subtask, RawCause, context deadline exceeded, DM 2.0.0, v2.0.0-hotfix
- Follow-up Guidance: The content includes exact checkpoint table fields to modify for adding tables in the `Sync` stage and notes version-specific behavior for `replicate lag` and the `context deadline exceeded` issue.
- Classification Note: This chunk is classified as diagnosis because it focuses on error messages, stage-specific limitations, monitoring behavior, configuration mismatches, and version-related causes and handling guidance.

## Official Source Content

## How to add tables to the existing data migration tasks?

If you need to add tables to a data migration task that is running, you can address it in the following ways according to the stage of the task.

> **Note:**
>
> Because adding tables to an existing data migration task is complex, it is recommended that you perform this operation only when necessary.
### In the `Dump` stage

Since MySQL cannot specify a snapshot for export, it does not support updating data migration tasks during the export and then restarting to resume the export through the checkpoint. Therefore, you cannot dynamically add tables that need to be migrated at the `Dump` stage.

If you really need to add tables for migration, it is recommended to restart the task directly using the new configuration file.
### In the `Load` stage

During the export, multiple data migration tasks usually have different binlog positions. If you merge the tasks in the `Load` stage, they might not be able to reach consensus on binlog positions. Therefore, it is not recommended to add tables to a data migration task in the `Load` stage.
### In the `Sync` stage

When the data migration task is in the `Sync` stage, if you add additional tables to the configuration file and restart the task, DM does not re-execute full export and import for the newly added tables. Instead, DM continues incremental replication from the previous checkpoint.

Therefore, if the full data of the newly added table has not been imported to the downstream, you need to use a separate data migration task to export and import the full data to the downstream.

Record the position information in the global checkpoint (`is_global=1`) corresponding to the existing migration task as `checkpoint-T`, such as `(mysql-bin.000100, 1234)`. Record the position information of the full export `metedata` (or the checkpoint of another data migration task in the `Sync` stage) of the table to be added to the migration task as `checkpoint-S`, such as `(mysql-bin.000099, 5678)`. You can add the table to the migration task by the following steps:

1. Use `stop-task` to stop an existing migration task. If the table to be added belongs to another running migration task, stop that task as well.

2. Use a MySQL client to connect the downstream TiDB database and manually update the information in the checkpoint table corresponding to the existing migration task to the smaller value between `checkpoint-T` and `checkpoint-S`. In this example, it is `(mysql- bin.000099, 5678)`.

    - The checkpoint table to be updated is `{task-name}_syncer_checkpoint` in the `{dm_meta}` schema.

    - The checkpoint rows to be updated match `id=(source-id)` and `is_global=1`.

    - The checkpoint columns to be updated are `binlog_name` and `binlog_pos`.

3. Set `safe-mode: true` for the `syncers` in the task to ensure reentrant execution.

4. Start the task using `start-task`.

5. Observe the task status through `query-status`. When `syncerBinlog` exceeds the larger value of `checkpoint-T` and `checkpoint-S`, restore `safe-mode` to the original value and restart the task. In this example, it is `(mysql-bin.000100, 1234)`.
## How to handle the error `packet for query is too large. Try adjusting the 'max_allowed_packet' variable` that occurs during the full import?

Set the parameters below to a value larger than the default 67108864 (64M).

- The global variable of the TiDB server: `max_allowed_packet`.
- The configuration item in the task configuration file: `target-database.max-allowed-packet`. For details, refer to [DM Advanced Task Configuration File](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full).
## How to handle the error `Error 1054: Unknown column 'binlog_gtid' in 'field list'` that occurs when existing DM migration tasks of an DM 1.0 cluster are running on a DM 2.0 or newer cluster?

Since DM v2.0, if you directly run the `start-task` command with the task configuration file of the DM 1.0 cluster to continue the incremental data replication, the error `Error 1054: Unknown column 'binlog_gtid' in 'field list'` occurs.

This error can be handled by [manually importing DM migration tasks of a DM 1.0 cluster to a DM 2.0 cluster](https://docs.pingcap.com/tidb/stable/dm/manually-upgrade-dm-1.0-to-2.0).
## Why does TiUP fail to deploy some versions of DM (for example, v2.0.0-hotfix)?

You can use the `tiup list dm-master` command to view the DM versions that TiUP supports to deploy. TiUP does not manage DM versions which are not shown by this command.
## How to handle the error `parse mydumper metadata error: EOF` that occurs when DM is replicating data?

You need to check the error message and log files to further analyze this error. The cause might be that the dump unit does not produce the correct metadata file due to a lack of permissions.
## Why does DM report no fatal error when replicating sharded schemas and tables, but downstream data is lost?

Check the configuration items `block-allow-list` and `table-route`:

- You need to configure the names of upstream databases and tables under `block-allow-list`. You can add "~" before `do-tables` to use regular expressions to match names.
- `table-route` uses wildcard characters instead of regular expressions to match table names. For example, `table_parttern_[0-63]` only matches 7 tables, from `table_parttern_0` to `table_pattern_6`.
## Why does the `replicate lag` monitor metric show no data when DM is not replicating from upstream?

In DM 1.0, you need to enable `enable-heartbeat` to generate the monitor data. In DM 2.0 and later versions, it is expected to have no data in the monitor metric `replicate lag` because this feature is not supported.
## How to handle the error `fail to initial unit Sync of subtask` when DM is starting a task, with the `RawCause` in the error message showing `context deadline exceeded`?

This is a known issue in DM 2.0.0 version and will be fixed in DM 2.0.1 version. It is likely to be triggered when a replication task has a lot of tables to process. If you use TiUP to deploy DM, you can upgrade DM to the nightly version to fix this issue. Or you can download the 2.0.0-hotfix version from [the release page of DM](https://github.com/pingcap/tiflow/releases) on GitHub and manually replace the executable files.
