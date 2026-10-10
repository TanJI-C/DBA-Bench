# Drainer usage options and example configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/deploy-tidb-binlog.md`
- Source Title: `TiDB Binlog Cluster Deployment`
- Source Heading Path: `TiDB Binlog Cluster Deployment > Deploy TiDB Binlog using a binary package > The usage example`
- Source Line Ranges: `153-281`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `shared`
- Topic Tags: `drainer`, `binlog`, `binary-package`, `configuration-file`, `command-options`, `replication`, `downstream`, `safe-mode`, `pd-urls`, `syncer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0198_f9892291d5`
- Source ID: `tidb-docs-8.1:tidb-binlog/deploy-tidb-binlog.md#the-usage-example`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2171d04ccdad218477ef29cd8b0132aa35f8ddf8091907f15d2f6f5fc37aa6a3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/deploy-tidb-binlog#the-usage-example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/deploy-tidb-binlog.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented Drainer command-line options or the example drainer configuration file for TiDB Binlog deployment with settings such as pd-urls, safe-mode, disable-dispatch, db-type, worker-count, or txn-batch.
- Retrieval Keywords: Usage of Drainer, Drainer configuration, -pd-urls, -safe-mode, -disable-dispatch, -dest-db-type, -txn-batch, -metrics-addr, -initial-commit-ts, addr = "192.168.0.13:8249", advertise-addr, [syncer], worker-count = 16, txn-batch = 20, db-type = "mysql", ignore-schemas, ignore-txn-commit-ts, replicate-do-db
- Follow-up Guidance: The source also provides an example TOML configuration for a Drainer node on 192.168.0.13, including security comments and syncer settings.
- Classification Note: This is classified as configuration because the content lists Drainer startup parameters and a concrete configuration file with replication, logging, PD connection, syncer, and downstream settings.

## Official Source Content

```bash
        Usage of Drainer:
        -L string
            the output information level of logs: debug, info, warn, error, fatal ("info" by default)
        -V
            the print version information
        -addr string
            the address through which Drainer provides the service (-addr="192.168.0.13:8249")
        -c int
            the number of the concurrency of the downstream for replication. The bigger the value, the better throughput performance of the concurrency ("1" by default).
        -cache-binlog-count int
            the limit on the number of binlog items in the cache ("8" by default)
            If a large single binlog item in the upstream causes OOM in Drainer, try to lower the value of this parameter to reduce memory usage.
        -config string
            the directory of the configuration file. Drainer reads the configuration file first.
            If the corresponding configuration exists in the command line parameters, Drainer uses the configuration of the command line parameters to cover that of the configuration file.
        -data-dir string
            the directory where the Drainer data is stored ("data.drainer" by default)
        -dest-db-type string
            the downstream service type of Drainer
            The value can be "mysql", "tidb", "kafka", and "file". ("mysql" by default)
        -detect-interval int
            the interval of checking the online Pump in PD ("10" by default, in seconds)
        -disable-detect
            whether to disable the conflict monitoring
        -disable-dispatch
            whether to disable the SQL feature of splitting a single binlog file. If it is set to "true", each binlog file is restored to a single transaction for replication based on the order of binlogs.
            It is set to "False", when the downstream is MySQL.
        -ignore-schemas string
            the db filter list ("INFORMATION_SCHEMA,PERFORMANCE_SCHEMA,mysql,test" by default)
            It does not support the Rename DDL operation on tables of `ignore schemas`.
        -initial-commit-ts
            If Drainer does not have the related breakpoint information, you can configure the related breakpoint information using this parameter. ("-1" by default)
            If the value of this parameter is `-1`, Drainer automatically obtains the latest timestamp from PD.
        -log-file string
            the path of the log file
        -log-rotate string
            the switch frequency of log files, hour/day
        -metrics-addr string
            the Prometheus Pushgateway address
            It it is not set, the monitoring metrics are not reported.
        -metrics-interval int
            the report frequency of the monitoring metrics ("15" by default, in seconds)
        -node-id string
            the unique ID of a Drainer node. If you do not specify this ID, the system automatically generates an ID based on the host name and listening port.
        -pd-urls string
            the address of the PD cluster nodes (-pd-urls="http://192.168.0.16:2379,http://192.168.0.15:2379,http://192.168.0.14:2379")
        -safe-mode
            Whether to enable safe mode so that data can be written into the downstream MySQL/TiDB repeatedly.
            This mode replaces the `INSERT` statement with the `REPLACE` statement and splits the `UPDATE` statement into `DELETE` plus `REPLACE`.
        -txn-batch int
            the number of SQL statements of a transaction which are output to the downstream database ("1" by default)
        ```

    - Taking deploying Drainer on "192.168.0.13" as an example, the Drainer configuration file is as follows:

        ```toml
        # Drainer Configuration.

        # the address through which Drainer provides the service ("192.168.0.13:8249")
        addr = "192.168.0.13:8249"

        # the address through which Drainer provides the external service
        advertise-addr = "192.168.0.13:8249"

        # the interval of checking the online Pump in PD ("10" by default, in seconds)
        detect-interval = 10

        # the directory where the Drainer data is stored "data.drainer" by default)
        data-dir = "data.drainer"

        # the address of the PD cluster nodes (each separated by a comma with no whitespace)
        pd-urls = "http://192.168.0.16:2379,http://192.168.0.15:2379,http://192.168.0.14:2379"

        # the directory of the log file
        log-file = "drainer.log"

        # Drainer compresses the data when it gets the binlog from Pump. The value can be "gzip". If it is not configured, it will not be compressed
        # compressor = "gzip"

        # [security]
        # This section is generally commented out if no special security settings are required.
        # The file path containing a list of trusted SSL CAs connected to the cluster.
        # ssl-ca = "/path/to/ca.pem"
        # The path to the X509 certificate in PEM format that is connected to the cluster.
        # ssl-cert = "/path/to/pump.pem"
        # The path to the X509 key in PEM format that is connected to the cluster.
        # ssl-key = "/path/to/pump-key.pem"

        # Syncer Configuration
        [syncer]
        # If the item is set, the sql-mode will be used to parse the DDL statement.
        # If the downstream database is MySQL or TiDB, then the downstream sql-mode
        # is also set to this value.
        # sql-mode = "STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION"

        # the number of SQL statements of a transaction that are output to the downstream database ("20" by default)
        txn-batch = 20

        # the number of the concurrency of the downstream for replication. The bigger the value,
        # the better throughput performance of the concurrency ("16" by default)
        worker-count = 16

        # whether to disable the SQL feature of splitting a single binlog file. If it is set to "true",
        # each binlog file is restored to a single transaction for replication based on the order of binlogs.
        # If the downstream service is MySQL, set it to "False".
        disable-dispatch = false

        # In safe mode, data can be written into the downstream MySQL/TiDB repeatedly.
        # This mode replaces the `INSERT` statement with the `REPLACE` statement and replaces the `UPDATE` statement with `DELETE` plus `REPLACE` statements.
        safe-mode = false

        # the downstream service type of Drainer ("mysql" by default)
        # Valid value: "mysql", "tidb", "file", and "kafka".
        db-type = "mysql"

        # If `commit ts` of the transaction is in the list, the transaction is filtered and not replicated to the downstream.
        ignore-txn-commit-ts = []

        # the db filter list ("INFORMATION_SCHEMA,PERFORMANCE_SCHEMA,mysql,test" by default)
        # Does not support the Rename DDL operation on tables of `ignore schemas`.
        ignore-schemas = "INFORMATION_SCHEMA,PERFORMANCE_SCHEMA,mysql"

        # `replicate-do-db` has priority over `replicate-do-table`. When they have the same `db` name,
        # regular expressions are supported for configuration.
        # The regular expression should start with "~".

        # replicate-do-db = ["~^b.*","s1"]
