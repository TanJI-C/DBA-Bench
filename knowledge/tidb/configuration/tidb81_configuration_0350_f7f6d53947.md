# Manage background task types in resource control

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-resource-control.md`
- Source Title: `Use Resource Control to Achieve Resource Isolation`
- Source Heading Path: `Use Resource Control to Achieve Resource Isolation > How to use resource control > Manage background tasks > `BACKGROUND` parameters | Use Resource Control to Achieve Resource Isolation > How to use resource control > Manage background tasks > Examples`
- Source Line Ranges: `409-486`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `br`, `lightning`
- Topic Tags: `resource-control`, `background-tasks`, `resource-groups`, `task-types`, `session-labeling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0350_f7f6d53947`
- Source ID: `tidb-docs-8.1:tidb-resource-control.md#background-parameters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0a5b645f29af8f7158820bde44de072b556c5f35cec73fe83ee7d3a92cde4ade`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-resource-control#background-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-resource-control.md

## Retrieval Guidance

- Use When: Use this content when identifying how to mark and inspect supported background task types for resource control in the `default` resource group, including session labeling with `tidb_request_source_type`.
- Retrieval Keywords: BACKGROUND, TASK_TYPES, ALTER RESOURCE GROUP `default` BACKGROUND=(TASK_TYPES='br,ddl'), ALTER RESOURCE GROUP `default` BACKGROUND=NULL, ALTER RESOURCE GROUP `default` BACKGROUND=(TASK_TYPES=""), SELECT * FROM information_schema.resource_groups WHERE NAME="default", tidb_request_source_type, background, lightning, br, ddl, stats, information_schema.resource_groups
- Follow-up Guidance: The examples show how to modify `default`, reset `BACKGROUND` to `NULL`, set `TASK_TYPES` to empty, query `information_schema.resource_groups`, and set `@@tidb_request_source_type="background"` before executing `LOAD DATA`.
- Classification Note: This is classified as configuration because the content defines the `BACKGROUND` and `TASK_TYPES` settings of a resource group and shows SQL used to configure and view them.

## Official Source Content

#### `BACKGROUND` parameters

`TASK_TYPES`: specifies the task types that need to be managed as background tasks. Use commas (`,`) to separate multiple task types.

TiDB supports the following types of background tasks:

- `lightning`: perform import tasks using [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview). Both physical and logical import modes of TiDB Lightning are supported.
- `br`: perform backup and restore tasks using [BR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview). PITR is not supported.
- `ddl`: control the resource usage during the batch data write back phase of Reorg DDLs.
- `stats`: the [collect statistics](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics) tasks that are manually executed or automatically triggered by TiDB.
- `background`: a reserved task type. You can use the [`tidb_request_source_type`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_request_source_type-new-in-v740) system variable to specify the task type of the current session as `background`.

- `lightning`: perform import tasks using [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning-overview). Both physical and logical import modes of TiDB Lightning are supported.
- `br`: perform backup and restore tasks using [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview). PITR is not supported.
- `ddl`: control the resource usage during the batch data write back phase of Reorg DDLs.
- `stats`: the [collect statistics](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics) tasks that are manually executed or automatically triggered by TiDB.
- `background`: a reserved task type. You can use the [`tidb_request_source_type`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_request_source_type-new-in-v740) system variable to specify the task type of the current session as `background`.

By default, the task types that are marked as background tasks are `""`, and the management of background tasks is disabled. To enable background task management, you need to manually modify the background task type of the `default` resource group. After a background task is identified and matched, Resource Control is automatically performed. This means that when system resources are insufficient, the background tasks are automatically reduced to the lowest priority to ensure the execution of foreground tasks.

> **Note:**
>
> Currently, background tasks for all resource groups are bound to the `default` resource group. You can manage background task types globally through `default`. Binding background tasks to other resource groups is currently not supported.
#### Examples

1. Modify the `default` resource group and mark `br` and `ddl` as background tasks.

    ```sql
    ALTER RESOURCE GROUP `default` BACKGROUND=(TASK_TYPES='br,ddl');
    ```

2. Change the `default` resource group to revert the background task type to its default value.

    ```sql
    ALTER RESOURCE GROUP `default` BACKGROUND=NULL;
    ```

3. Change the `default` resource group to set the background task type to empty. In this case, all tasks of this resource group are not treated as background tasks.

    ```sql
    ALTER RESOURCE GROUP `default` BACKGROUND=(TASK_TYPES="");
    ```

4. View the background task type of the `default` resource group.

    ```sql
    SELECT * FROM information_schema.resource_groups WHERE NAME="default";
    ```

    The output is as follows:

    ```
    +---------+------------+----------+-----------+-------------+---------------------+
    | NAME    | RU_PER_SEC | PRIORITY | BURSTABLE | QUERY_LIMIT | BACKGROUND          |
    +---------+------------+----------+-----------+-------------+---------------------+
    | default | UNLIMITED  | MEDIUM   | YES       | NULL        | TASK_TYPES='br,ddl' |
    +---------+------------+----------+-----------+-------------+---------------------+
    ```

5. To explicitly mark tasks in the current session as the background type, you can use `tidb_request_source_type` to explicitly specify the task type. The following is an example:

    ``` sql
    SET @@tidb_request_source_type="background";
    /* Add background task type */
    ALTER RESOURCE GROUP `default` BACKGROUND=(TASK_TYPES="background");
    /* Execute LOAD DATA in the current session */
    LOAD DATA INFILE "s3://resource-control/Lightning/test.customer.aaaa.csv"
    ```
