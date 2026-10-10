# Log in to TiDB and run simple verification SQL

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/post-installation-check.md`
- Source Title: `Check Cluster Status`
- Source Heading Path: `Check Cluster Status > Log in to the database and perform simple operations | Check Cluster Status > Log in to the database and perform simple operations > Database operations`
- Source Line Ranges: `44-214`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `login`, `mysql client`, `sql verification`, `database operations`, `version check`, `table creation`, `data insert`, `tikv store status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0194_bf996fdae3`
- Source ID: `tidb-docs-8.1:post-installation-check.md#log-in-to-the-database-and-perform-simple-operations`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b021dfbf8829abdce601808c4cb4d808de702d151fba82b49966d226d2f2605`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/post-installation-check#log-in-to-the-database-and-perform-simple-operations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/post-installation-check.md

## Retrieval Guidance

- Use When: Use this chunk when logging in to TiDB with the MySQL client and verifying the deployment by running simple SQL statements and checking TiKV store status.
- Retrieval Keywords: mysql -u root -h ${tidb_server_host_IP_address} -P 4000, select tidb_version()\G, create database pingcap;, use pingcap;, CREATE TABLE `tab_tidb`, insert into `tab_tidb` values (1,'TiDB',5,'TiDB-v5.0.0');, select * from tab_tidb;, INFORMATION_SCHEMA.TIKV_STORE_STATUS, select STORE_ID,ADDRESS,STORE_STATE,STORE_STATE_NAME,CAPACITY,AVAILABLE,UPTIME from INFORMATION_SCHEMA.TIKV_STORE_STATUS;, exit, MySQL client, STORE_STATE_NAME, Up
- Follow-up Guidance: It notes that you need to install the MySQL client before logging in to the database.
- Classification Note: The classification is operation for the tidb component because the content covers database login, basic SQL verification, and querying TiKV store information from TiDB.

## Official Source Content

## Log in to the database and perform simple operations

> **Note:**
>
> Install the MySQL client before you log in to the database.

Log in to the database by running the following command:

```shell
mysql -u root -h ${tidb_server_host_IP_address} -P 4000
```

`${tidb_server_host_IP_address}` is one of the IP addresses set for `tidb_servers` when you [initialize the cluster topology file](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#step-3-initialize-cluster-topology-file), such as `10.0.1.7`.

The following information indicates successful login:

```sql
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 3
Server version: 8.0.11-TiDB-v8.1.2 TiDB Server (Apache License 2.0) Community Edition, MySQL 8.0 compatible
Copyright (c) 2000, 2023, Oracle and/or its affiliates. All rights reserved.
Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
```
### Database operations

- Check the version of TiDB:

    ```sql
    select tidb_version()\G
    ```

    Expected output:

    ```sql
    *************************** 1. row ***************************
    tidb_version(): Release Version: v5.0.0
    Edition: Community
    Git Commit Hash: 689a6b6439ae7835947fcaccf329a3fc303986cb
    Git Branch: HEAD
    UTC Build Time: 2020-05-28 11:09:45
    GoVersion: go1.13.4
    Race Enabled: false
    TiKV Min Version: v3.0.0-60965b006877ca7234adaced7890d7b029ed1306
    Check Table Before Drop: false
    1 row in set (0.00 sec)
    ```

- Create a database named `pingcap`:

    ```sql
    create database pingcap;
    ```

    Expected output:

    ```sql
    Query OK, 0 rows affected (0.10 sec)
    ```

    Switch to the `pingcap` database:

    ```sql
    use pingcap;
    ```

    Expected output:

    ```sql
    Database changed
    ```

- Create a table named `tab_tidb`:

    ```sql
    CREATE TABLE `tab_tidb` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(20) NOT NULL DEFAULT '',
    `age` int(11) NOT NULL DEFAULT 0,
    `version` varchar(20) NOT NULL DEFAULT '',
    PRIMARY KEY (`id`),
    KEY `idx_age` (`age`));
    ```

    Expected output:

    ```sql
    Query OK, 0 rows affected (0.11 sec)
    ```

- Insert data:

    ```sql
    insert into `tab_tidb` values (1,'TiDB',5,'TiDB-v5.0.0');
    ```

    Expected output:

    ```sql
    Query OK, 1 row affected (0.03 sec)
    ```

- View the entries in `tab_tidb`:

    ```sql
    select * from tab_tidb;
    ```

    Expected output:

    ```sql
    +----+------+-----+-------------+
    | id | name | age | version     |
    +----+------+-----+-------------+
    |  1 | TiDB |   5 | TiDB-v5.0.0 |
    +----+------+-----+-------------+
    1 row in set (0.00 sec)
    ```

- View the store state, `store_id`, capacity, and uptime of TiKV:

    ```sql
    select STORE_ID,ADDRESS,STORE_STATE,STORE_STATE_NAME,CAPACITY,AVAILABLE,UPTIME from INFORMATION_SCHEMA.TIKV_STORE_STATUS;
    ```

    Expected output:

    ```sql
    +----------+--------------------+-------------+------------------+----------+-----------+--------------------+
    | STORE_ID | ADDRESS            | STORE_STATE | STORE_STATE_NAME | CAPACITY | AVAILABLE | UPTIME             |
    +----------+--------------------+-------------+------------------+----------+-----------+--------------------+
    |        1 | 10.0.1.1:20160 |           0 | Up               | 49.98GiB | 46.3GiB   | 5h21m52.474864026s |
    |        4 | 10.0.1.2:20160 |           0 | Up               | 49.98GiB | 46.32GiB  | 5h21m52.522669177s |
    |        5 | 10.0.1.3:20160 |           0 | Up               | 49.98GiB | 45.44GiB  | 5h21m52.713660541s |
    +----------+--------------------+-------------+------------------+----------+-----------+--------------------+
    3 rows in set (0.00 sec)
    ```

- Exit TiDB:

    ```sql
    exit
    ```

    Expected output:

    ```sql
    Bye
    ```
