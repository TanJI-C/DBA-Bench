# Binary package usage example: Drainer configuration, startup, and TiDB binlog enablement

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/deploy-tidb-binlog.md`
- Source Title: `TiDB Binlog Cluster Deployment`
- Source Heading Path: `TiDB Binlog Cluster Deployment > Deploy TiDB Binlog using a binary package > The usage example`
- Source Line Ranges: `282-386`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `shared`
- Topic Tags: `drainer`, `pump`, `binlog`, `configuration`, `startup`, `initial-commit-ts`, `backup`, `restore`, `replication`, `downstream`, `sql_mode`, `ddl`, `kafka`, `checkpoint`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0270_f28cdc6ef3`
- Source ID: `tidb-docs-8.1:tidb-binlog/deploy-tidb-binlog.md#the-usage-example`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b402664b1524beaf5e890df66d73a5d74b7a9b9f5c1942568a9f59fd13eac681`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/deploy-tidb-binlog#the-usage-example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/deploy-tidb-binlog.md

## Retrieval Guidance

- Use When: Use this chunk when you need the binary-package example for configuring and starting Drainer, setting initial-commit-ts, or enabling TiDB Binlog on TiDB server with Pump registration behavior from PD.
- Retrieval Keywords: drainer.toml, ./drainer -config drainer.toml -initial-commit-ts {initial-commit-ts}, initial-commit-ts, [binlog] enable=true, -enable-binlog, Pump, Drainer, PD, registered Pumps, TiDB server will refuse to start, syncer.to, encrypted_password, ./binlogctl -cmd encrypt -text string, syncer.to.checkpoint, checkpoint type mysql tidb file kafka, topic-name, kafka-addrs, zookeeper-addrs, syncer.relay, relay log, run_ddl=false, sql_mode, select @@sql_mode;, rename DDL operation, ignore schemas, CREATE TABLE t1(a INT) ROW_FORMAT=FIXED;
- Follow-up Guidance: The source also notes backup and restore before the initial start of Drainer for MySQL or TiDB downstream, requires at least one Pump running normally, and describes sql_mode consistency and DDL incompatibility considerations for replication.
- Classification Note: This is classified as an operation chunk because the official content gives deployment-time configuration and startup details for Drainer and TiDB Binlog, including command-line parameters, configuration sections, and runtime prerequisites.

## Official Source Content

# [syncer.relay]
        # It saves the directory of the relay log. The relay log is not enabled if the value is empty.
        # The configuration only comes to effect if the downstream is TiDB or MySQL.
        # log-dir = ""
        # the maximum size of each file
        # max-file-size = 10485760

        # [[syncer.replicate-do-table]]
        # db-name ="test"
        # tbl-name = "log"

        # [[syncer.replicate-do-table]]
        # db-name ="test"
        # tbl-name = "~^a.*"

        # Ignore the replication of some tables
        # [[syncer.ignore-table]]
        # db-name = "test"
        # tbl-name = "log"

        # the server parameters of the downstream database when `db-type` is set to "mysql"
        [syncer.to]
        host = "192.168.0.13"
        user = "root"
        # If you do not want to set a cleartext `password` in the configuration file, you can create `encrypted_password` using `./binlogctl -cmd encrypt -text string`.
        # When you have created an `encrypted_password` that is not empty, the `password` above will be ignored, because `encrypted_password` and `password` cannot take effect at the same time.
        password = ""
        encrypted_password = ""
        port = 3306

        [syncer.to.checkpoint]
        # When the checkpoint type is "mysql" or "tidb", this option can be
        # enabled to change the database that saves the checkpoint
        # schema = "tidb_binlog"
        # Currently only the "mysql" and "tidb" checkpoint types are supported
        # You can remove the comment tag to control where to save the checkpoint
        # The default method of saving the checkpoint for the downstream db-type:
        # mysql/tidb -> in the downstream MySQL or TiDB database
        # file/kafka -> file in `data-dir`
        # type = "mysql"
        # host = "127.0.0.1"
        # user = "root"
        # password = ""
        # `encrypted_password` is encrypted using `./binlogctl -cmd encrypt -text string`.
        # When `encrypted_password` is not empty, the `password` above will be ignored.
        # encrypted_password = ""
        # port = 3306

        # the directory where the binlog file is stored when `db-type` is set to `file`
        # [syncer.to]
        # dir = "data.drainer"

        # the Kafka configuration when `db-type` is set to "kafka"
        # [syncer.to]
        # only one of kafka-addrs and zookeeper-addrs is needed. If both are present, the program gives priority
        # to the kafka address in zookeeper
        # zookeeper-addrs = "127.0.0.1:2181"
        # kafka-addrs = "127.0.0.1:9092"
        # kafka-version = "0.8.2.0"
        # The maximum number of messages (number of binlogs) in a broker request. If it is left blank or a value smaller than 0 is configured, the default value 1024 is used.
        # kafka-max-messages = 1024
        # The maximum size of a broker request (unit: byte). The default value is 1 GiB and the maximum value is 2 GiB.
        # kafka-max-message-size = 1073741824

        # the topic name of the Kafka cluster that saves the binlog data. The default value is <cluster-id>_obinlog.
        # To run multiple Drainers to replicate data to the same Kafka cluster, you need to set different `topic-name`s for each Drainer.
        # topic-name = ""
        ```

    - Starting Drainer:

        > **Note:**
        >
        > If the downstream is MySQL/TiDB, to guarantee the data integrity, you need to obtain the `initial-commit-ts` value and make a full backup of the data and restore the data before the initial start of Drainer.

        When Drainer is started for the first time, use the `initial-commit-ts` parameter.

        ```bash
        ./drainer -config drainer.toml -initial-commit-ts {initial-commit-ts}
        ```

        If the command line parameter and the configuration file parameter are the same, the parameter value in the command line is used.

3. Starting TiDB server:

    - After starting Pump and Drainer, start TiDB server with binlog enabled by adding this section to your config file for TiDB server:

        ```
        [binlog]
        enable=true
        ```

    - TiDB server will obtain the addresses of registered Pumps from PD and will stream data to all of them. If there are no registered Pump instances, TiDB server will refuse to start or will block starting until a Pump instance comes online.

> **Note:**
>
> - When TiDB is running, you need to guarantee that at least one Pump is running normally.
> - To enable the TiDB Binlog service in TiDB server, use the `-enable-binlog` startup parameter in TiDB, or add enable=true to the [binlog] section of the TiDB server configuration file.
> - Make sure that the TiDB Binlog service is enabled in all TiDB instances in a same cluster, otherwise upstream and downstream data inconsistency might occur during data replication. If you want to temporarily run a TiDB instance where the TiDB Binlog service is not enabled, set `run_ddl=false` in the TiDB configuration file.
> - Drainer does not support the `rename` DDL operation on the table of `ignore schemas` (the schemas in the filter list).
> - If you want to start Drainer in an existing TiDB cluster, generally you need to make a full backup of the cluster data, obtain **snapshot timestamp**, import the data to the target database, and then start Drainer to replicate the incremental data from the corresponding **snapshot timestamp**.
> - When the downstream database is TiDB or MySQL, ensure that the `sql_mode` in the upstream and downstream databases are consistent. In other words, the `sql_mode` should be the same when each SQL statement is executed in the upstream and replicated to the downstream. You can execute the `select @@sql_mode;` statement in the upstream and downstream respectively to compare `sql_mode`.
> - When a DDL statement is supported in the upstream but incompatible with the downstream, Drainer fails to replicate data. An example is to replicate the `CREATE TABLE t1(a INT) ROW_FORMAT=FIXED;` statement when the downstream database MySQL uses the InnoDB engine. In this case, you can configure [skipping transactions](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-faq#what-can-i-do-when-some-ddl-statements-supported-by-the-upstream-database-cause-error-when-executed-in-the-downstream-database) in Drainer, and manually execute compatible statements in the downstream database.
