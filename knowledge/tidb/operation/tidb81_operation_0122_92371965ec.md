# Deploy v2.0+ cluster, stop v1.0.x, and start upgraded task

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/manually-upgrade-dm-1.0-to-2.0.md`
- Source Title: `Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+`
- Source Heading Path: `Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+ > Step 2: Deploy the v2.0+ cluster | Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+ > Step 3: Stop the v1.0.x cluster | Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+ > Step 4: Upgrade data migration task`
- Source Line Ranges: `103-165`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `tiup`
- Topic Tags: `manual-upgrade`, `cluster-deployment`, `cluster-stop`, `checkpoint-query`, `incremental-replication`, `start-task`, `query-status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0122_92371965ec`
- Source ID: `tidb-docs-8.1:dm/manually-upgrade-dm-1.0-to-2.0.md#step-2-deploy-the-v2-0-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b43f5f8b02f5638e88428c5cb09ed1e914ad59d57fdfcbad36652a2ecc5a050`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/manually-upgrade-dm-1.0-to-2.0#step-2-deploy-the-v2-0-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/manually-upgrade-dm-1.0-to-2.0.md

## Retrieval Guidance

- Use When: Use this chunk when manually upgrading a DM v1.0.x task to v2.0+ by deploying a new cluster if needed, stopping the old cluster, extracting global checkpoint data from downstream TiDB, and starting an incremental task in v2.0+.
- Retrieval Keywords: Step 2 Deploy the v2.0+ cluster, Use TiUP to deploy a new v2.0+ cluster, Step 3 Stop the v1.0.x cluster, DM-Ansible stop the v1.0.x cluster, stop the DM-worker and DM-master processes directly, Step 4 Upgrade data migration task, operate-source, start-task, query-status, global checkpoint information, incremental checkpoint table, dm_meta, task_v1_syncer_checkpoint, SELECT `id`, `binlog_name`, `binlog_pos` FROM `dm_meta`.`task_v1_syncer_checkpoint` WHERE `is_global`=1;, is_global=1, task_v1.yaml, task_v2.yaml, task-mode incremental, mysql-instances, meta, binlog-name, binlog-pos, binlog-gtid, mysql-replica-01, mysql-replica-02
- Follow-up Guidance: After loading source configuration and updating the task file with a new name, task-mode incremental, and checkpoint-based meta, the content says to use start-task and then query-status to confirm the task is running normally.
- Classification Note: This chunk is classified as operation because it describes the procedural upgrade flow: deploy or reuse a v2.0+ cluster, stop the v1.0.x cluster, query checkpoint data from downstream TiDB, and start the upgraded task.

## Official Source Content

## Step 2: Deploy the v2.0+ cluster

> **Note:**
>
> Skip this step if you have other v2.0+ clusters available.

[Use TiUP](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup) to deploy a new v2.0+ cluster according to the required number of nodes.
## Step 3: Stop the v1.0.x cluster

If the original v1.0.x cluster is deployed by DM-Ansible, you need to use [DM-Ansible to stop the v1.0.x cluster](https://docs.pingcap.com/tidb-data-migration/v1.0/cluster-operations#stop-a-cluster).

If the original v1.0.x cluster is deployed by binary, you can stop the DM-worker and DM-master processes directly.
## Step 4: Upgrade data migration task

1. Use the [`operate-source`](https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#operate-data-source) command to load the upstream database source configuration from [step 1](#step-1-prepare-v20-configuration-file) into the v2.0+ cluster.

2. In the downstream TiDB cluster, obtain the corresponding global checkpoint information from the incremental checkpoint table of the v1.0.x data migration task.

    - Assume that the v1.0.x data migration configuration does not specify `meta-schema` (or specify its value as the default `dm_meta`), and the corresponding task name is `task_v1`, the corresponding checkpoint information is in the ``` `dm_meta`.`task_v1_syncer_checkpoint` ``` table of the downstream TiDB.
    - Use the following SQL statements to obtain the global checkpoint information of all upstream database sources corresponding to the data migration task.

        ```sql
        > SELECT `id`, `binlog_name`, `binlog_pos` FROM `dm_meta`.`task_v1_syncer_checkpoint` WHERE `is_global`=1;
        +------------------+-------------------------+------------+
        | id               | binlog_name             | binlog_pos |
        +------------------+-------------------------+------------+
        | mysql-replica-01 | mysql-bin|000001.000123 | 15847      |
        | mysql-replica-02 | mysql-bin|000001.000456 | 10485      |
        +------------------+-------------------------+------------+
        ```

3. Update the v1.0.x data migration task configuration file to start a new v2.0+ data migration task.

    - If the data migration task configuration file of v1.0.x is `task_v1.yaml`, copy it and rename it to `task_v2.yaml`.
    - Make the following changes to `task_v2.yaml`:
        - Modify `name` to a new name, such as `task_v2`.
        - Change `task-mode` to `incremental`.
        - Set the starting point of incremental replication for each source according to the global checkpoint information obtained in step 2. For example:

            ```yaml
            mysql-instances:
              - source-id: "mysql-replica-01"        # Corresponds to the `id` of the checkpoint information.
                meta:
                  binlog-name: "mysql-bin.000123"    # Corresponds to the `binlog_name` in the checkpoint information, excluding the part of `|000001`.
                  binlog-pos: 15847                  # Corresponds to `binlog_pos` in the checkpoint information.

              - source-id: "mysql-replica-02"
                meta:
                  binlog-name: "mysql-bin.000456"
                  binlog-pos: 10485
            ```

            > **Note:**
            >
            > If `enable-gtid` is enabled in the source configuration, currently you need to parse the binlog or relay log file to obtain the GTID sets corresponding to the binlog position, and set it to `binlog-gtid` in the `meta`.

4. Use the [`start-task`](https://docs.pingcap.com/tidb/stable/dm/dm-create-task) command to start the upgraded data migration task through the v2.0+ data migration task configuration file.

5. Use the [`query-status`](https://docs.pingcap.com/tidb/stable/dm/dm-query-status) command to confirm whether the data migration task is running normally.

If the data migration task runs normally, it indicates that the DM upgrade to v2.0+ is successful.
