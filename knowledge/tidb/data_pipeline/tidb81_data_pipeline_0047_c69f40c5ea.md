# Configure and run DM incremental replication task

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-large-mysql-to-tidb.md`
- Source Title: `Migrate Large Datasets from MySQL to TiDB`
- Source Heading Path: `Migrate Large Datasets from MySQL to TiDB > Step 3. Replicate incremental data to TiDB > Add the data source | Migrate Large Datasets from MySQL to TiDB > Step 3. Replicate incremental data to TiDB > Add a replication task | Migrate Large Datasets from MySQL to TiDB > Step 3. Replicate incremental data to TiDB > Check the migration task status | Migrate Large Datasets from MySQL to TiDB > Step 3. Replicate incremental data to TiDB > Monitor the task and view logs | Migrate Large Datasets from MySQL to TiDB > What's next`
- Source Line Ranges: `172-304`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `tidb`, `shared`
- Topic Tags: `incremental-replication`, `data-source`, `task-configuration`, `binlog`, `gtid`, `safe-mode`, `task-status`, `monitoring`, `logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0047_c69f40c5ea`
- Source ID: `tidb-docs-8.1:migrate-large-mysql-to-tidb.md#add-the-data-source`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cbc5ae8fd39134ed81d58bbbb84d2a52422306c8f03b731c35f4f89da77f5f19`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-large-mysql-to-tidb#add-the-data-source
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-large-mysql-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official DM steps and configuration for adding a MySQL data source, creating an incremental replication task to TiDB, checking task status, and viewing monitoring or log locations.
- Retrieval Keywords: source1.yaml, source-id, mysql-01, enable-gtid, operate-source create, tiup dmctl --master-addr ${advertise-addr} operate-source create source1.yaml, task.yaml, task-mode: incremental, target-database, block-allow-list, mysql-instances, meta, binlog-gtid, binlog-name, binlog-pos, safe-mode, syncers, check-task, tiup dmctl --master-addr ${advertise-addr} check-task task.yaml, start-task, tiup dmctl --master-addr ${advertise-addr} start-task task.yaml, query-status, tiup dmctl --master-addr ${advertise-addr} query-status ${task-name}, DM-worker, DM-master, dmctl, Grafana, DM dashboard, --log-file, /dm-deploy/dm-master-8261/log/, /dm-deploy/dm-worker-8262/log/, incremental replication task, DM error handling, DM FAQ
- Follow-up Guidance: The source also points to related DM operations including Pause a Data Migration Task, Resume a Data Migration Task, Stop a Data Migration Task, Export and Import Data Sources and Task Configuration of Clusters, and Handle Failed DDL Statements.
- Classification Note: This is classified as a self-managed DM data pipeline chunk because the content covers TiUP and dmctl commands, DM source and task YAML configuration, incremental binlog replication settings, task status checks, and DM monitoring and log paths.

## Official Source Content

### Add the data source

1. Create a `source1.yaml` file as follows:

    ```yaml
    # Must be unique.
    source-id: "mysql-01"

    # Configures whether DM-worker uses the global transaction identifier (GTID) to pull binlogs. To enable this mode, the upstream MySQL must also enable GTID. If the upstream MySQL service is configured to switch master between different nodes automatically, GTID mode is required.
    enable-gtid: true

    from:
      host: "${host}"           # e.g.: 172.16.10.81
      user: "root"
      password: "${password}"   # Supported but not recommended to use a plaintext password. It is recommended to use `dmctl encrypt` to encrypt the plaintext password before using it.
      port: 3306
    ```

2. Load the data source configuration to the DM cluster using `tiup dmctl` by running the following command:

    ```shell
    tiup dmctl --master-addr ${advertise-addr} operate-source create source1.yaml
    ```

    The parameters used in the command above are described as follows:

    |Parameter              |Description    |
    |-                      |-              |
    |`--master-addr`        |The `{advertise-addr}` of any DM-master in the cluster where `dmctl` is to be connected, e.g.: 172.16.10.71:8261|
    |`operate-source create`|Loads the data source to the DM cluster.|
### Add a replication task

1. Edit the `task.yaml` file. Configure the incremental replication mode and the starting point of each data source:

    ```yaml
    name: task-test                      # Task name. Must be globally unique.
    task-mode: incremental               # Task mode. The "incremental" mode only performs incremental data replication.

    # Configures the target TiDB database.
    target-database:                     # The target database instance.
      host: "${host}"                    # e.g.: 127.0.0.1
      port: 4000
      user: "root"
      password: "${password}"            # It is recommended to use `dmctl encrypt` to encrypt the plaintext password before using it.

    # Use block and allow lists to specify the tables to be replicated.
    block-allow-list:                    # The collection of filtering rules that matches the tables in the source database instance. If the DM version is earlier than v2.0.0-beta.2, use black-white-list.
      bw-rule-1:                         # The block-allow-list configuration item ID.
        do-dbs: ["${db-name}"]           # Name of databases to be replicated.

    # Configures the data source.
    mysql-instances:
      - source-id: "mysql-01"            # Data source ID, i.e., source-id in source1.yaml
        block-allow-list: "bw-rule-1"    # You can use the block-allow-list configuration above.
        # syncer-config-name: "global"    # You can use the syncers incremental data configuration below.
        meta:                            # The position where the binlog replication starts when `task-mode` is `incremental` and the downstream database checkpoint does not exist. If the checkpoint exists, the checkpoint is used. If neither the `meta` configuration item nor the downstream database checkpoint exists, the migration starts from the latest binlog position of the upstream.
          # binlog-name: "mysql-bin.000004"  # The binlog position recorded in "Step 1. Export all data from MySQL". If the upstream database service is configured to switch master between different nodes automatically, GTID mode is required.
          # binlog-pos: 109227
          binlog-gtid: "09bec856-ba95-11ea-850a-58f2b4af5188:1-9"

    # (Optional) If you need to incrementally replicate data that has already been migrated in the full data migration, you need to enable the safe mode to avoid the incremental data replication error.
    # This scenario is common in the following case: the full migration data does not belong to the data source's consistency snapshot, and after that, DM starts to replicate incremental data from a position earlier than the full migration.
    # syncers:            # The running configurations of the sync processing unit.
    #   global:           # Configuration name.
    #     safe-mode: true # If this field is set to true, DM changes INSERT of the data source to REPLACE for the target database, and changes UPDATE of the data source to DELETE and REPLACE for the target database. This is to ensure that when the table schema contains a primary key or unique index, DML statements can be imported repeatedly. In the first minute of starting or resuming an incremental replication task, DM automatically enables the safe mode.
    ```

    The YAML above is the minimum configuration required for the migration task. For more configuration items, refer to [DM Advanced Task Configuration File](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full).

    Before you start the migration task, to reduce the probability of errors, it is recommended to confirm that the configuration meets the requirements of DM by running the `check-task` command:

    ```shell
    tiup dmctl --master-addr ${advertise-addr} check-task task.yaml
    ```

2. Start the migration task by running the following command:

    ```shell
    tiup dmctl --master-addr ${advertise-addr} start-task task.yaml
    ```

    The parameters used in the command above are described as follows:

    |Parameter              |Description    |
    |-                      |-              |
    |`--master-addr`        |The {advertise-addr} of any DM-master in the cluster where `dmctl` is to be connected, e.g.: 172.16.10.71:8261|
    |`start-task`           |Starts the migration task.|

    If the task fails to start, check the prompt message and fix the configuration. After that, you can re-run the command above to start the task.

    If you encounter any problem, refer to [DM error handling](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling) and [DM FAQ](https://docs.pingcap.com/tidb/stable/dm/dm-faq).
### Check the migration task status

To learn whether the DM cluster has an ongoing migration task and view the task status, run the `query-status` command using `tiup dmctl`:

```shell
tiup dmctl --master-addr ${advertise-addr} query-status ${task-name}
```

For a detailed interpretation of the results, refer to [Query Status](https://docs.pingcap.com/tidb/stable/dm/dm-query-status).
### Monitor the task and view logs

To view the history status of the migration task and other internal metrics, take the following steps.

If you have deployed Prometheus, Alertmanager, and Grafana when you deployed DM using TiUP, you can access Grafana using the IP address and port specified during the deployment. You can then select DM dashboard to view DM-related monitoring metrics.

When DM is running, DM-worker, DM-master, and dmctl print the related information in logs. The log directories of these components are as follows:

- DM-master: specified by the DM-master process parameter `--log-file`. If you deploy DM using TiUP, the log directory is `/dm-deploy/dm-master-8261/log/` by default.
- DM-worker: specified by the DM-worker process parameter `--log-file`. If you deploy DM using TiUP, the log directory is `/dm-deploy/dm-worker-8262/log/` by default.
## What's next

- [Pause a Data Migration Task](https://docs.pingcap.com/tidb/stable/dm/dm-pause-task)
- [Resume a Data Migration Task](https://docs.pingcap.com/tidb/stable/dm/dm-resume-task)
- [Stop a Data Migration Task](https://docs.pingcap.com/tidb/stable/dm/dm-stop-task)
- [Export and Import Data Sources and Task Configuration of Clusters](https://docs.pingcap.com/tidb/stable/dm/dm-export-import-config)
- [Handle Failed DDL Statements](https://docs.pingcap.com/tidb/stable/dm/handle-failed-ddl-statements)
