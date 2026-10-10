# DM workflow for migrating small MySQL datasets to TiDB

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-small-mysql-to-tidb.md`
- Source Title: `Migrate Small Datasets from MySQL to TiDB`
- Source Heading Path: `Migrate Small Datasets from MySQL to TiDB | Migrate Small Datasets from MySQL to TiDB > Prerequisites | Migrate Small Datasets from MySQL to TiDB > Step 1. Create the data source | Migrate Small Datasets from MySQL to TiDB > Step 2. Create the migration task | Migrate Small Datasets from MySQL to TiDB > Step 3. Start the migration task | Migrate Small Datasets from MySQL to TiDB > Step 4: Check the migration task status | Migrate Small Datasets from MySQL to TiDB > Step 5. Monitor the task and view logs （optional) | Migrate Small Datasets from MySQL to TiDB > What's next`
- Source Line Ranges: `5-148`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `tidb`, `shared`
- Topic Tags: `mysql-to-tidb`, `full-migration`, `incremental-replication`, `data-source`, `task-configuration`, `dmctl`, `task-validation`, `task-start`, `status-check`, `monitoring`, `logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0050_539e983e24`
- Source ID: `tidb-docs-8.1:migrate-small-mysql-to-tidb.md#migrate-small-datasets-from-mysql-to-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8abc2bbd37ea93633b7d1fd28736dae26df4283d0aaeb758604da9afd62feb04`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-small-mysql-to-tidb#migrate-small-datasets-from-mysql-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-small-mysql-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the end-to-end DM workflow to migrate a small MySQL dataset to TiDB, including data source creation, task configuration, task validation, task start, status checks, monitoring, and log locations.
- Retrieval Keywords: Migrate Small Datasets from MySQL to TiDB, DM, TiDB Data Migration, small datasets less than 1 TiB, full migration mode, incremental replication mode, source1.yaml, task1.yaml, source-id: "mysql-01", enable-gtid: true, operate-source create, tiup dmctl --master-addr ${advertise-addr} operate-source create source1.yaml, task-mode: "all", target-database, mysql-instances, block-allow-list, do-tables, check-task, tiup dmctl --master-addr ${advertise-addr} check-task task.yaml, start-task, tiup dmctl --master-addr ${advertise-addr} start-task task.yaml, query-status, tiup dmctl --master-addr ${advertise-addr} query-status ${task-name}, DM dashboard, Grafana, DM-master log, DM-worker log, /dm-deploy/dm-master-8261/log/, /dm-deploy/dm-worker-8262/log/
- Follow-up Guidance: The source also points to related DM operations including Pause the migration task, Resume the migration task, Stop the migration task, Export and import the cluster data source and task configuration, and Handle failed DDL statements.
- Classification Note: This is classified as a data_pipeline chunk for the dm component because the content describes a self-managed DM migration pipeline from MySQL to TiDB with task configuration, execution, validation, monitoring, and logs.

## Official Source Content

# Migrate Small Datasets from MySQL to TiDB

This document describes how to use TiDB Data Migration (DM) to migrate small datasets from MySQL to TiDB in the full migration mode and incremental replication mode. "Small datasets" in this document mean data size less than 1 TiB.

The migration speed varies from 30 GB/h to 50 GB/h, depending on multiple factors such as the number of indexes in the table schema, hardware, and network environment. <!--The migration process using DM is shown in the figure below.-->

<!--/media/dm/migrate-with-dm.png-->
## Prerequisites

- [Deploy a DM Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup)
- [Grant the required privileges for the source database and the target database of DM](https://docs.pingcap.com/tidb/stable/dm/dm-worker-intro)
## Step 1. Create the data source

First, create the `source1.yaml` file as follows:

```yaml
# The ID must be unique.
source-id: "mysql-01"

# Configures whether DM-worker uses the global transaction identifier (GTID) to pull binlogs. To enable GTID, the upstream MySQL must have enabled GTID. If the upstream MySQL has automatic source-replica switching, the GTID mode is required.
enable-gtid: true

from:
  host: "${host}"         # For example: 172.16.10.81
  user: "root"
  password: "${password}" # Plaintext password is supported but not recommended. It is recommended to use dmctl encrypt to encrypt the plaintext password before using the password.
  port: 3306
```

Then, load the data source configuration to the DM cluster using `tiup dmctl` by running the following command:

```shell
tiup dmctl --master-addr ${advertise-addr} operate-source create source1.yaml
```

The parameters used in the command above are described as follows:

|Parameter      |Description|
|  :-        |    :-           |
|`--master-addr`  |`{advertise-addr}` of any DM-master node in the cluster where `dmctl` is to connect. For example, 172.16.10.71:8261.
|`operate-source create`|Load the data source to the DM cluster.|
## Step 2. Create the migration task

Create the `task1.yaml` file as follows:

```yaml
# Task name. Each of the multiple tasks running at the same time must have a unique name.
name: "test"
# Task mode. Options are:
# full: only performs full data migration.
# incremental: only performs binlog real-time replication.
# all: full data migration + binlog real-time replication.
task-mode: "all"
# The configuration of the target TiDB database.
target-database:
  host: "${host}"                   # For example: 172.16.10.83
  port: 4000
  user: "root"
  password: "${password}"           # Plaintext password is supported but not recommended. It is recommended to use dmctl encrypt to encrypt the plaintext password before using the password.

# The configuration of all MySQL instances of source database required for the current migration task.
mysql-instances:
-
  # The ID of an upstream instance or a replication group
  source-id: "mysql-01"
  # The names of the block list and allow list configuration of the schema name or table name that is to be migrated. These names are used to reference the global configuration of the block and allowlist. For the global configuration, refer to the `block-allow-list` configuration below.
  block-allow-list: "listA"

# The global configuration of blocklist and allowlist. Each instance is referenced by a configuration item name.
block-allow-list:
  listA:                              # name
    do-tables:                        # The allowlist of upstream tables that need to be migrated.
    - db-name: "test_db"              # The schema name of the table to be migrated.
      tbl-name: "test_table"          # The name of the table to be migrated.

```

The above is the minimum task configuration to perform the migration. For more configuration items regarding the task, refer to [DM task complete configuration file introduction](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full).
## Step 3. Start the migration task

To avoid errors, before starting the migration task, it is recommended to use the `check-task` command to check whether the configuration meets the requirements of DM configuration.

```shell
tiup dmctl --master-addr ${advertise-addr} check-task task.yaml
```

Start the migration task by running the following command with `tiup dmctl`.

```shell
tiup dmctl --master-addr ${advertise-addr} start-task task.yaml
```

The parameters used in the command above are described as follows:

|Parameter|Description|
|     -    |     -     |
|`--master-addr`| `{advertise-addr}` of any DM-master node in the cluster where `dmctl` is to connect. For example: 172.16.10.71:8261. |
|`start-task`| Start the migration task |

If the task fails to start, after changing the configuration according to the returned result, you can run the `start-task task.yaml` command to restart the task. If you encounter problems, refer to [Handle Errors](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling) and [FAQ](https://docs.pingcap.com/tidb/stable/dm/dm-faq).
## Step 4: Check the migration task status

To learn whether the DM cluster has an ongoing migration task, the task status and some other information, run the `query-status` command using `tiup dmctl`:

```shell
tiup dmctl --master-addr ${advertise-addr} query-status ${task-name}
```

For a detailed interpretation of the results, refer to [Query Status](https://docs.pingcap.com/tidb/stable/dm/dm-query-status).
## Step 5. Monitor the task and view logs （optional)

To view the historical status of the migration task and other internal metrics, take the following steps.

If you have deployed Prometheus, Alertmanager, and Grafana when deploying DM using TiUP, you can access Grafana using the IP address and port specified during the deployment. You can then select the DM dashboard to view DM-related monitoring metrics.

- The log directory of DM-master: specified by the DM-master process parameter `--log-file`. If you have deployed DM using TiUP, the log directory is `/dm-deploy/dm-master-8261/log/` by default.
- The log directory of DM-worker: specified by the DM-worker process parameter `--log-file`. If you have deployed DM using TiUP, the log directory is `/dm-deploy/dm-worker-8262/log/` by default.
## What's next

- [Pause the migration task](https://docs.pingcap.com/tidb/stable/dm/dm-pause-task)
- [Resume the migration task](https://docs.pingcap.com/tidb/stable/dm/dm-resume-task)
- [Stop the migration task](https://docs.pingcap.com/tidb/stable/dm/dm-stop-task)
- [Export and import the cluster data source and task configuration](https://docs.pingcap.com/tidb/stable/dm/dm-export-import-config)
- [Handle failed DDL statements](https://docs.pingcap.com/tidb/stable/dm/handle-failed-ddl-statements)
