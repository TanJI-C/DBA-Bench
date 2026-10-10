# DM incremental migration task creation, execution, monitoring, and follow-up actions

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-aurora-to-tidb.md`
- Source Title: `Migrate Data from Amazon Aurora to TiDB`
- Source Heading Path: `Migrate Data from Amazon Aurora to TiDB > Replicate incremental data to TiDB (optional) > Step 2: Create the migration task | Migrate Data from Amazon Aurora to TiDB > Replicate incremental data to TiDB (optional) > Step 3. Run the migration task | Migrate Data from Amazon Aurora to TiDB > Replicate incremental data to TiDB (optional) > Step 4. Check the migration task status | Migrate Data from Amazon Aurora to TiDB > Replicate incremental data to TiDB (optional) > Step 5. Monitor the task and view logs | Migrate Data from Amazon Aurora to TiDB > What's next`
- Source Line Ranges: `214-311`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `tidb`, `shared`
- Topic Tags: `incremental-replication`, `migration-task`, `task-configuration`, `dmctl`, `task-startup`, `status-checking`, `monitoring`, `logs`, `safe-mode`, `follow-up-operations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0031_4d2428146f`
- Source ID: `tidb-docs-8.1:migrate-aurora-to-tidb.md#step-2-create-the-migration-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fc7ffcc55046595736115bdf62ccd09e52d8fcdca9a947459e5b08d51c835f24`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-aurora-to-tidb#step-2-create-the-migration-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-aurora-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official DM workflow for creating an incremental migration task from Aurora to TiDB, starting it with dmctl, checking status, viewing monitoring and logs, and seeing the listed follow-up task operations.
- Retrieval Keywords: task1.yaml, task-mode: "incremental", target-database, block-allow-list, mysql-instances, source-id: "mysql-01", meta, binlog-name, binlog-pos, binlog-gtid, safe-mode: true, tiup dmctl --master-addr ${advertise-addr} check-task task.yaml, tiup dmctl --master-addr ${advertise-addr} start-task task.yaml, tiup dmctl --master-addr ${advertise-addr} query-status ${task-name}, DM dashboard, DM-master, DM-worker, dmctl, --log-file, /dm-deploy/dm-master-8261/log/, /dm-deploy/dm-worker-8262/log/, Pause the migration task, Resume the migration task, Stop the migration task, Export and import the cluster data source and task configuration, Handle failed DDL statements
- Follow-up Guidance: The source next points to pause, resume, and stop task operations, export and import of cluster data source and task configuration, and handling failed DDL statements.
- Classification Note: This chunk is classified as data_pipeline for the DM component because the official content covers DM task configuration, incremental replication startup, status querying, monitoring metrics, logs, and subsequent migration task operations.

## Official Source Content

### Step 2: Create the migration task

Create the `task1.yaml` file as follows:

```yaml
# Task name. Multiple tasks that are running at the same time must each have a unique name.
name: "test"
# Task mode. Options are:
# - full: only performs full data migration.
# - incremental: only performs binlog real-time replication.
# - all: full data migration + binlog real-time replication.
task-mode: "incremental"
# The configuration of the target TiDB database.
target-database:
  host: "${host}"                   # e.g.: 172.16.10.83
  port: 4000
  user: "root"
  password: "${password}"           # Supported but not recommended to use a plaintext password. It is recommended to use `dmctl encrypt` to encrypt the plaintext password before using it.

# Global configuration for block and allow lists. Each instance can reference the configuration by name.
block-allow-list:                     # If the DM version is earlier than v2.0.0-beta.2, use black-white-list.
  listA:                              # Name.
    do-tables:                        # Allow list for the upstream tables to be migrated.
    - db-name: "test_db"              # Name of databases to be migrated.
      tbl-name: "test_table"          # Name of tables to be migrated.

# Configures the data source.
mysql-instances:
  - source-id: "mysql-01"               # Data source ID, i.e., source-id in source1.yaml
    block-allow-list: "listA"           # References the block-allow-list configuration above.
#       syncer-config-name: "global"    # Name of the syncer configuration.
    meta:                               # The position where the binlog replication starts when `task-mode` is `incremental` and the downstream database checkpoint does not exist. If the checkpoint exists, the checkpoint is used. If neither the `meta` configuration item nor the downstream database checkpoint exists, the migration starts from the latest binlog position of the upstream.
      binlog-name: "mysql-bin.000004"   # The binlog position recorded in "Step 1. Export an Amazon Aurora snapshot to Amazon S3". When the upstream database has source-replica switching, GTID mode is required.
      binlog-pos: 109227
      # binlog-gtid: "09bec856-ba95-11ea-850a-58f2b4af5188:1-9"

# (Optional) If you need to incrementally replicate data that has already been migrated in the full data migration, you need to enable the safe mode to avoid the incremental data replication error.
   # This scenario is common in the following case: the full migration data does not belong to the data source's consistency snapshot, and after that, DM starts to replicate incremental data from a position earlier than the full migration.
   # syncers:            # The running configurations of the sync processing unit.
   #   global:            # Configuration name.
   #     safe-mode: true  # If this field is set to true, DM changes INSERT of the data source to REPLACE for the target database, and changes UPDATE of the data source to DELETE and REPLACE for the target database. This is to ensure that when the table schema contains a primary key or unique index, DML statements can be imported repeatedly. In the first minute of starting or resuming an incremental replication task, DM automatically enables the safe mode.
```

The YAML file above is the minimum configuration required for the migration task. For more configuration items, refer to [DM Advanced Task Configuration File](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full).
### Step 3. Run the migration task

Before you start the migration task, to reduce the probability of errors, it is recommended to confirm that the configuration meets the requirements of DM by running the `check-task` command:

```shell
tiup dmctl --master-addr ${advertise-addr} check-task task.yaml
```

After that, start the migration task by running `tiup dmctl`:

```shell
tiup dmctl --master-addr ${advertise-addr} start-task task.yaml
```

The parameters used in the command above are described as follows:

|Parameter              |Description    |
|-                      |-              |
|`--master-addr`        |The `{advertise-addr}` of any DM-master in the cluster where `dmctl` is to be connected, e.g.: 172.16.10.71:8261|
|`start-task`           |Starts the migration task.|

If the task fails to start, check the prompt message and fix the configuration. After that, you can re-run the command above to start the task.

If you encounter any problem, refer to [DM error handling](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling) and [DM FAQ](https://docs.pingcap.com/tidb/stable/dm/dm-faq).
### Step 4. Check the migration task status

To learn whether the DM cluster has an ongoing migration task and the task status, run the `query-status` command using `tiup dmctl`:

```shell
tiup dmctl --master-addr ${advertise-addr} query-status ${task-name}
```

For a detailed interpretation of the results, refer to [Query Status](https://docs.pingcap.com/tidb/stable/dm/dm-query-status).
### Step 5. Monitor the task and view logs

To view the history status of the migration task and other internal metrics, take the following steps.

If you have deployed Prometheus, Alertmanager, and Grafana when you deployed DM using TiUP, you can access Grafana using the IP address and port specified during the deployment. You can then select DM dashboard to view DM-related monitoring metrics.

When DM is running, DM-worker, DM-master, and dmctl print the related information in logs. The log directories of these components are as follows:

- DM-master: specified by the DM-master process parameter `--log-file`. If you deploy DM using TiUP, the log directory is `/dm-deploy/dm-master-8261/log/` by default.
- DM-worker: specified by the DM-worker process parameter `--log-file`. If you deploy DM using TiUP, the log directory is `/dm-deploy/dm-worker-8262/log/` by default.
## What's next

- [Pause the migration task](https://docs.pingcap.com/tidb/stable/dm/dm-pause-task).
- [Resume the migration task](https://docs.pingcap.com/tidb/stable/dm/dm-resume-task).
- [Stop the migration task](https://docs.pingcap.com/tidb/stable/dm/dm-stop-task).
- [Export and import the cluster data source and task configuration](https://docs.pingcap.com/tidb/stable/dm/dm-export-import-config).
- [Handle failed DDL statements](https://docs.pingcap.com/tidb/stable/dm/handle-failed-ddl-statements).
