# DM quick start: deploy cluster, prepare source and target, run migration task

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/quick-start-with-dm.md`
- Source Title: `TiDB Data Migration Quick Start`
- Source Heading Path: `Quick Start Guide for TiDB Data Migration | Quick Start Guide for TiDB Data Migration > Step 1: Deploy a DM cluster | Quick Start Guide for TiDB Data Migration > Step 2: Prepare the data source | Quick Start Guide for TiDB Data Migration > Step 3: Prepare a downstream database | Quick Start Guide for TiDB Data Migration > Step 4: Prepare test data | Quick Start Guide for TiDB Data Migration > Step 5: Create a data migration task | Quick Start Guide for TiDB Data Migration > Step 6: Check the status of the task`
- Source Line Ranges: `5-181`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `tidb`, `shared`
- Topic Tags: `quickstart`, `deployment`, `data-source`, `mysql`, `docker`, `downstream`, `task-configuration`, `migration-task`, `status-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0126_459e4a24fb`
- Source ID: `tidb-docs-8.1:dm/quick-start-with-dm.md#quick-start-guide-for-tidb-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `30ec678d0b71c48da0ec10bfe0f16d65db927ad34af252dce14f143a3a5b5c77`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/quick-start-with-dm#quick-start-guide-for-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/quick-start-with-dm.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the end-to-end quick start steps to deploy a DM cluster, register a MySQL source, prepare TiDB as the downstream, create a migration task, and check task status.
- Retrieval Keywords: TiDB Data Migration quick start, DM cluster deployment, tiup dm deploy dm-test 8.1.2 topology.yaml -p, tiup install dm dmctl, tiup dm template, operate-source create mysql-01.yaml, tiup dmctl --master-addr=127.0.0.1:8261 operate-source create mysql-01.yaml, tiup playground, testdm-task.yaml, start-task testdm-task.yaml, tiup dmctl --master-addr 127.0.0.1:8261 start-task testdm-task.yaml, query-status testdm, tiup dmctl --master-addr 127.0.0.1:8261 query-status testdm, source-id mysql-01, task-mode all, block-allow-list ba-rule1, do-dbs testdm, MySQL to TiDB migration, SELinux disabled
- Follow-up Guidance: The chunk also includes example MySQL Docker setup, sample SQL for the `testdm` database and tables `t1` and `t2`, and the `dmctl` commands to create the source and query task status.
- Classification Note: This is classified as an operation chunk because the official content is a procedural quick start covering deployment, source registration, task creation, and status checking for DM.

## Official Source Content

# Quick Start Guide for TiDB Data Migration

This document describes how to migrate data from MySQL to TiDB using [TiDB Data Migration (DM)](https://docs.pingcap.com/tidb/stable/dm/dm-overview). This guide is a quick demo of DM features and is not recommended for any production environment.

> **Note:**
>
> If your target machine's operating system supports SELinux, ensure that SELinux is **disabled**.
## Step 1: Deploy a DM cluster

1. Install TiUP, and install [`dmctl`](https://docs.pingcap.com/tidb/stable/dm/dmctl-introduction) using TiUP:

    ```shell
    curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
    tiup install dm dmctl
    ```

2. Generate the minimal deployment topology file of a DM cluster:

    ```
    tiup dm template
    ```

3. Copy the configuration information in the output, and save it as the `topology.yaml` file with the modified IP address. Deploy the DM cluster with the `topology.yaml` file using TiUP:

    ```shell
    tiup dm deploy dm-test 8.1.2 topology.yaml -p
    ```
## Step 2: Prepare the data source

You can use one or multiple MySQL instances as an upstream data source.

1. Create a configuration file for each data source as follows:

    ```yaml
    source-id: "mysql-01"
    from:
      host: "127.0.0.1"
      user: "root"
      password: "fCxfQ9XKCezSzuCD0Wf5dUD+LsKegSg="
      port: 3306
    ```

2. Add the source to the DM cluster by running the following command. `mysql-01.yaml` is the configuration file created in the previous step.

    ```bash
    tiup dmctl --master-addr=127.0.0.1:8261 operate-source create mysql-01.yaml # use one of master_servers as the argument of --master-addr
    ```

If you do not have a MySQL instance for testing, you can create a MySQL instance in Docker by taking the following steps:

1. Create a MySQL configuration file:

    ```shell
    mkdir -p /tmp/mysqltest && cd /tmp/mysqltest

    cat > my.cnf <<EOF
    [mysqld]
    bind-address     = 0.0.0.0
    character-set-server=utf8
    collation-server=utf8_bin
    default-storage-engine=INNODB
    transaction-isolation=READ-COMMITTED
    server-id        = 100
    binlog_format    = row
    log_bin          = /var/lib/mysql/mysql-bin.log
    show_compatibility_56 = ON
    EOF
    ```

2. Start the MySQL instance using Docker:

    ```shell
    docker run --name mysql-01 -v /tmp/mysqltest:/etc/mysql/conf.d -e MYSQL_ROOT_PASSWORD=my-secret-pw -d -p 3306:3306 mysql:5.7
    ```

3. After the MySQL instance is started, access the instance:

    > **Note:**
    >
    > This command is only suitable for trying out data migration, and cannot be used in production environments or stress tests.

    ```shell
    mysql -uroot -p -h 127.0.0.1 -P 3306
    ```
## Step 3: Prepare a downstream database

You can choose an existing TiDB cluster as a target for data migration.

If you do not have a TiDB cluster for testing, you can quickly build a demonstration environment by running the following command:

```shell
tiup playground
```
## Step 4: Prepare test data

Create a test table and data in one or multiple data sources. If you use an existing MySQL database, and the database contains available data, you can skip this step.

```sql
drop database if exists `testdm`;
create database `testdm`;
use `testdm`;
create table t1 (id bigint, uid int, name varchar(80), info varchar(100), primary key (`id`), unique key(`uid`)) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
create table t2 (id bigint, uid int, name varchar(80), info varchar(100), primary key (`id`), unique key(`uid`)) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
insert into t1 (id, uid, name) values (1, 10001, 'Gabriel García Márquez'), (2, 10002, 'Cien años de soledad');
insert into t2 (id, uid, name) values (3, 20001, 'José Arcadio Buendía'), (4, 20002, 'Úrsula Iguarán'), (5, 20003, 'José Arcadio');
```
## Step 5: Create a data migration task

1. Create a task configuration file `testdm-task.yaml`:

    ```yaml
    name: testdm
    task-mode: all

    target-database:
      host: "127.0.0.1"
      port: 4000
      user: "root"
      password: "" # If the password is not empty, it is recommended to use a password encrypted with dmctl.

    # Configure the information of one or multiple data sources
    mysql-instances:
      - source-id: "mysql-01"
        block-allow-list:  "ba-rule1"

    block-allow-list:
      ba-rule1:
        do-dbs: ["testdm"]
    ```

2. Create the task using dmctl:

    ```bash
    tiup dmctl --master-addr 127.0.0.1:8261 start-task testdm-task.yaml
    ```

You have successfully created a task that migrates data from a `mysql-01` database to TiDB.
## Step 6: Check the status of the task

After the task is created, you can use the `dmctl query-status` command to check the status of the task:

```bash
tiup dmctl --master-addr 127.0.0.1:8261 query-status testdm
```
