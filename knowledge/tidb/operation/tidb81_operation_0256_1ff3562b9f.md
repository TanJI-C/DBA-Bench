# Pause, resume, remove, update, and inspect TiCDC changefeeds

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-manage-changefeed.md`
- Source Title: `Manage Changefeeds`
- Source Heading Path: `Manage Changefeeds > Pause a replication task | Manage Changefeeds > Resume a replication task | Manage Changefeeds > Remove a replication task | Manage Changefeeds > Update task configuration | Manage Changefeeds > Manage processing units of replication sub-tasks (`processor`) | Manage Changefeeds > Replicate tables with the new framework for collations enabled`
- Source Line Ranges: `151-260`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `pause`, `resume`, `remove`, `update`, `processor`, `checkpoint-ts`, `overwrite-checkpoint-ts`, `data-loss`, `duplication`, `collation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0256_1ff3562b9f`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-manage-changefeed.md#pause-a-replication-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `98803edf3e54ffb37de14659a3d1740a338c9a127b1f377413f01d16b66da2b8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed#pause-a-replication-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-manage-changefeed.md

## Retrieval Guidance

- Use When: Use this when you need TiCDC commands for pausing, resuming, removing, updating, or inspecting changefeeds and `processor` sub-tasks.
- Retrieval Keywords: cdc cli changefeed pause, cdc cli changefeed resume, cdc cli changefeed remove, cdc cli changefeed update, cdc cli processor list, cdc cli processor query, --overwrite-checkpoint-ts, --no-confirm, checkpoint-ts, data loss, data duplication, processor, changefeed configuration
- Follow-up Guidance: Use `changefeed query` to obtain the current checkpoint TSO before resuming with `--overwrite-checkpoint-ts`.
- Classification Note: This chunk covers changefeed lifecycle operations, processor inspection, configuration updates, and the note about resuming from an overwritten checkpoint TSO.

## Official Source Content

## Pause a replication task

Run the following command to pause a replication task:

```shell
cdc cli changefeed pause --server=http://10.0.10.25:8300 --changefeed-id simple-replication-task
```

In the preceding command:

- `--changefeed-id=uuid` represents the ID of the changefeed that corresponds to the replication task you want to pause.
## Resume a replication task

Run the following command to resume a paused replication task:

```shell
cdc cli changefeed resume --server=http://10.0.10.25:8300 --changefeed-id simple-replication-task
```

- `--changefeed-id=uuid` represents the ID of the changefeed that corresponds to the replication task you want to resume.
- `--overwrite-checkpoint-ts`: starting from v6.2.0, you can specify the starting TSO of resuming the replication task. TiCDC starts pulling data from the specified TSO. The argument accepts `now` or a specific TSO (such as 434873584621453313). The specified TSO must be in the range of (GC safe point, CurrentTSO]. If this argument is not specified, TiCDC replicates data from the current `checkpoint-ts` by default. You can use the `cdc cli changefeed list` command to check the current value of `checkpoint-ts`.
- `--no-confirm`: when the replication is resumed, you do not need to confirm the related information. Defaults to `false`.

> **Note:**
>
> - If the TSO specified in `--overwrite-checkpoint-ts` (`t2`) is larger than the current checkpoint TSO in the changefeed (`t1`), data between `t1` and `t2` will not be replicated to the downstream. This causes data loss. You can obtain `t1` by running `cdc cli changefeed query`.
> - If the TSO specified in `--overwrite-checkpoint-ts` (`t2`) is smaller than the current checkpoint TSO in the changefeed (`t1`), TiCDC pulls data from an old time point (`t2`), which might cause data duplication (for example, if the downstream is MQ sink).
## Remove a replication task

Run the following command to remove a replication task:

```shell
cdc cli changefeed remove --server=http://10.0.10.25:8300 --changefeed-id simple-replication-task
```

In the preceding command:

- `--changefeed-id=uuid` represents the ID of the changefeed that corresponds to the replication task you want to remove.
## Update task configuration

TiCDC supports modifying the configuration of the replication task (not dynamically). To modify the changefeed configuration, pause the task, modify the configuration, and then resume the task.

```shell
cdc cli changefeed pause -c test-cf --server=http://10.0.10.25:8300
cdc cli changefeed update -c test-cf --server=http://10.0.10.25:8300 --sink-uri="mysql://127.0.0.1:3306/?max-txn-row=20&worker-count=8" --config=changefeed.toml
cdc cli changefeed resume -c test-cf --server=http://10.0.10.25:8300
```

Currently, you can modify the following configuration items:

- `sink-uri` of the changefeed.
- The changefeed configuration file and all configuration items in the file.
- The `target-ts` of the changefeed.
## Manage processing units of replication sub-tasks (`processor`)

- Query the `processor` list:

    ```shell
    cdc cli processor list --server=http://10.0.10.25:8300
    ```

    ```shell
    [
            {
                    "id": "9f84ff74-abf9-407f-a6e2-56aa35b33888",
                    "capture-id": "b293999a-4168-4988-a4f4-35d9589b226b",
                    "changefeed-id": "simple-replication-task"
            }
    ]
    ```

- Query a specific changefeed which corresponds to the status of a specific replication task:

    ```shell
    cdc cli processor query --server=http://10.0.10.25:8300 --changefeed-id=simple-replication-task --capture-id=b293999a-4168-4988-a4f4-35d9589b226b
    ```

    ```shell
    {
      "status": {
        "tables": {
          "56": {    # 56 ID of the replication table, corresponding to tidb_table_id of a table in TiDB
            "start-ts": 417474117955485702
          }
        },
        "operation": null,
        "admin-job-type": 0
      },
      "position": {
        "checkpoint-ts": 417474143881789441,
        "resolved-ts": 417474143881789441,
        "count": 0
      }
    }
    ```

    In the preceding command:

    - `status.tables`: Each key number represents the ID of the replication table, corresponding to `tidb_table_id` of a table in TiDB.
    - `resolved-ts`: The largest TSO among the sorted data in the current processor.
    - `checkpoint-ts`: The largest TSO that has been successfully written to the downstream in the current processor.
## Replicate tables with the new framework for collations enabled

Starting from v4.0.15, v5.0.4, v5.1.1 and v5.2.0, TiCDC supports tables that have enabled [new framework for collations](https://docs.pingcap.com/tidb/stable/character-set-and-collation#new-framework-for-collations).
