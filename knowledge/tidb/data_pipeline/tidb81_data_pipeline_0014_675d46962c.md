# Deploy DM and prepare migration sources and task config

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/migrate-data-using-dm.md`
- Source Title: `Migrate Data Using Data Migration`
- Source Heading Path: `Migrate Data Using Data Migration | Migrate Data Using Data Migration > Step 1: Deploy the DM cluster | Migrate Data Using Data Migration > Step 2: Check the cluster information | Migrate Data Using Data Migration > Step 3: Create data source | Migrate Data Using Data Migration > Step 4: Configure the data migration task`
- Source Line Ranges: `5-118`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `tidb`
- Topic Tags: `deployment`, `cluster-information`, `source-configuration`, `task-configuration`, `full-migration`, `incremental-migration`, `preparation`, `privileges`, `gtid`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0014_675d46962c`
- Source ID: `tidb-docs-8.1:dm/migrate-data-using-dm.md#migrate-data-using-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `52321baa234621be293b9860cd86c70272ac0c29c1b09229533a8dd12ac9872b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/migrate-data-using-dm#migrate-data-using-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/migrate-data-using-dm.md

## Retrieval Guidance

- Use When: Use this chunk when preparing a DM migration by deploying a DM cluster, checking cluster information, creating source configurations, or writing a task.yaml for full plus incremental migration from MySQL to TiDB.
- Retrieval Keywords: deploy the DM cluster using TiUP, deploy the DM cluster using binary, dmctl, Encrypt the database password using dmctl, operate-source create conf/source1.yaml, source-id, enable-gtid, task.yaml, task-mode: "all", target-database, mysql-instances, block-allow-list, black-white-list, mydumper-config-name, mydumpers, do-tables, test_db, test_table, precheck, upstream and downstream databases privileges
- Follow-up Guidance: The next related steps in the source are to start the migration task with `tiup dmctl --master-addr 172.16.10.71:8261 start-task ./task.yaml` and use precheck or `check-task` to validate configuration.
- Classification Note: This is classified as a data_pipeline chunk because the content covers DM deployment, source configuration, and task configuration for full and incremental data migration.

## Official Source Content

# Migrate Data Using Data Migration

This guide shows how to migrate data using the Data Migration (DM) tool.
## Step 1: Deploy the DM cluster

It is recommended to [deploy the DM cluster using TiUP](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup). You can also [deploy the DM cluster using binary](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-binary) for trial or test.

> **Note:**
>
> - For database passwords in all the DM configuration files, it is recommended to use the passwords encrypted by `dmctl`. If a database password is empty, it is unnecessary to encrypt it. See [Encrypt the database password using dmctl](https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#encrypt-the-database-password).
> - The user of the upstream and downstream databases must have the corresponding read and write privileges.
## Step 2: Check the cluster information

After the DM cluster is deployed using TiUP, the configuration information is like what is listed below.

- The configuration information of related components in the DM cluster:

    | Component | Host | Port |
    |------| ---- | ---- |
    | dm_worker1 | 172.16.10.72 | 8262 |
    | dm_worker2 | 172.16.10.73 | 8262 |
    | dm_master | 172.16.10.71 | 8261 |

- The information of upstream and downstream database instances:

    | Database instance | Host | Port | Username | Encrypted password |
    | -------- | --- | --- | --- | --- |
    | Upstream MySQL-1 | 172.16.10.81 | 3306 | root | VjX8cEeTX+qcvZ3bPaO4h0C80pe/1aU= |
    | Upstream MySQL-2 | 172.16.10.82 | 3306 | root | VjX8cEeTX+qcvZ3bPaO4h0C80pe/1aU= |
    | Downstream TiDB | 172.16.10.83 | 4000 | root | |

The list of privileges needed on the MySQL host can be found in the [precheck](https://docs.pingcap.com/tidb/stable/dm/dm-precheck) documentation.
## Step 3: Create data source

1. Write MySQL-1 related information to `conf/source1.yaml`:

    ```yaml
    # MySQL1 Configuration.

    source-id: "mysql-replica-01"
    # This indicates that whether DM-worker uses Global Transaction Identifier (GTID) to pull binlog. Before you use this configuration item, make sure that the GTID mode is enabled in the upstream MySQL.
    enable-gtid: false

    from:
      host: "172.16.10.81"
      user: "root"
      password: "VjX8cEeTX+qcvZ3bPaO4h0C80pe/1aU="
      port: 3306
    ```

2. Execute the following command in the terminal, and use `tiup dmctl` to load the MySQL-1 data source configuration to the DM cluster:

    ```bash
    tiup dmctl --master-addr 172.16.10.71:8261 operate-source create conf/source1.yaml
    ```

3. For MySQL-2, modify the relevant information in the configuration file and execute the same `dmctl` command.
## Step 4: Configure the data migration task

The following example assumes that you need to migrate all the `test_table` table data in the `test_db` database of both the upstream MySQL-1 and MySQL-2 instances, to the downstream `test_table` table in the `test_db` database of TiDB, in the full data plus incremental data mode.

Edit the `task.yaml` task configuration file as below:

```yaml
# The task name. You need to use a different name for each of the multiple tasks that
# run simultaneously.
name: "test"
# The full data plus incremental data (all) migration mode.
task-mode: "all"
# The downstream TiDB configuration information.
target-database:
  host: "172.16.10.83"
  port: 4000
  user: "root"
  password: ""

# Configuration of all the upstream MySQL instances required by the current data migration task.
mysql-instances:
-
  # The ID of upstream instances or the migration group. You can refer to the configuration of `source_id` in the "inventory.ini" file or in the "dm-master.toml" file.
  source-id: "mysql-replica-01"
  # The configuration item name of the block and allow lists of the name of the
  # database/table to be migrated, used to quote the global block and allow
  # lists configuration that is set in the global block-allow-list below.
  block-allow-list: "global"  # Use black-white-list if the DM version is earlier than or equal to v2.0.0-beta.2.
  # The configuration item name of the dump processing unit, used to quote the global configuration of the dump unit.
  mydumper-config-name: "global"

-
  source-id: "mysql-replica-02"
  block-allow-list: "global"  # Use black-white-list if the DM version is earlier than or equal to v2.0.0-beta.2.
  mydumper-config-name: "global"

# The global configuration of block and allow lists. Each instance can quote it by the
# configuration item name.
block-allow-list:                     # Use black-white-list if the DM version is earlier than or equal to v2.0.0-beta.2.
  global:
    do-tables:                        # The allow list of upstream tables to be migrated.
    - db-name: "test_db"              # The database name of the table to be migrated.
      tbl-name: "test_table"          # The name of the table to be migrated.

# The global configuration of the dump unit. Each instance can quote it by the configuration item name.
mydumpers:
  global:
    extra-args: ""
```
