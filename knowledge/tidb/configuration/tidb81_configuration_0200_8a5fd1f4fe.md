# Drainer and downstream syncer configuration items

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-configuration-file.md`
- Source Title: `TiDB Binlog Configuration File`
- Source Heading Path: `TiDB Binlog Configuration File > Drainer | TiDB Binlog Configuration File > Drainer > addr | TiDB Binlog Configuration File > Drainer > advertise-addr | TiDB Binlog Configuration File > Drainer > log-file | TiDB Binlog Configuration File > Drainer > log-level | TiDB Binlog Configuration File > Drainer > node-id | TiDB Binlog Configuration File > Drainer > data-dir | TiDB Binlog Configuration File > Drainer > detect-interval | TiDB Binlog Configuration File > Drainer > pd-urls | TiDB Binlog Configuration File > Drainer > initial-commit-ts | TiDB Binlog Configuration File > Drainer > synced-check-time | TiDB Binlog Configuration File > Drainer > compressor | TiDB Binlog Configuration File > Drainer > security | TiDB Binlog Configuration File > Drainer > security > ssl-ca | TiDB Binlog Configuration File > Drainer > security > ssl-cert | TiDB Binlog Configuration File > Drainer > security > ssl-key | TiDB Binlog Configuration File > Drainer > syncer | TiDB Binlog Configuration File > Drainer > syncer > db-type | TiDB Binlog Configuration File > Drainer > syncer > sql-mode | TiDB Binlog Configuration File > Drainer > syncer > ignore-txn-commit-ts | TiDB Binlog Configuration File > Drainer > syncer > ignore-schemas | TiDB Binlog Configuration File > Drainer > syncer > ignore-table | TiDB Binlog Configuration File > Drainer > syncer > replicate-do-db | TiDB Binlog Configuration File > Drainer > syncer > replicate-do-table | TiDB Binlog Configuration File > Drainer > syncer > txn-batch | TiDB Binlog Configuration File > Drainer > syncer > worker-count | TiDB Binlog Configuration File > Drainer > syncer > disable-dispatch | TiDB Binlog Configuration File > Drainer > syncer > safe-mode`
- Source Line Ranges: `129-307`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `br`, `dumpling`
- Topic Tags: `binlog`, `drainer`, `downstream`, `replication`, `checkpoint`, `initial-commit-ts`, `filtering`, `kafka`, `mysql`, `tidb`, `tls`, `safe-mode`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0200_8a5fd1f4fe`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-configuration-file.md#drainer`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2c7d3003fed52969af823274204e403451e507ed3a4162b5d8e19bf56c24c1e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-configuration-file#drainer
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking up Drainer configuration items, including replication start position, `/status` synced checks, compression, TLS, downstream `syncer` settings, filtering rules, batching, concurrency, and safe mode.
- Retrieval Keywords: Drainer, addr, advertise-addr, log-file, log-level, node-id, data-dir, detect-interval, pd-urls, initial-commit-ts, synced-check-time, /status, compressor, gzip, security, ssl-ca, ssl-cert, ssl-key, syncer, db-type, mysql, tidb, kafka, file, sql-mode, ignore-txn-commit-ts, ignore-schemas, ignore-table, replicate-do-db, replicate-do-table, txn-batch, worker-count, disable-dispatch, safe-mode, Replace Into, Delete plus Replace Into, checkpoint, commit ts, backupmeta, metadata, tso
- Follow-up Guidance: The source explains that `initial-commit-ts` can be obtained from BR backup metadata, Dumpling metadata, or the output of the PD Control `tso` command.
- Classification Note: The official content is configuration documentation because it lists Drainer and downstream syncer configuration parameters, supported values, behaviors, and default values.

## Official Source Content

## Drainer

This section introduces the configuration items of Drainer. For the example of a complete Drainer configuration file, see [Drainer Configuration](https://github.com/pingcap/tidb-binlog/blob/release-8.1/cmd/drainer/drainer.toml)
### addr

* Specifies the listening address of HTTP API in the format of `host:port`.
* Default value: `127.0.0.1:8249`
### advertise-addr

* Specifies the externally accessible HTTP API address. This address is registered in PD in the format of `host:port`.
* Default value: `127.0.0.1:8249`
### log-file

* Specifies the path where log files are stored. If the parameter is set to an empty value, log files are not stored.
* Default value: ""
### log-level

* Specifies the log level.
* Default value: `info`
### node-id

* Specifies the Drainer node ID. With this ID, this Drainer process can be identified in the cluster.
* Default value: `hostname:port number`. For example, `node-1:8249`.
### data-dir

* Specifies the directory used to store files that need to be saved during Drainer operation.
* Default value: `data.drainer`
### detect-interval

* Specifies the interval (in seconds) at which PD updates the Pump information.
* Default value: `5`
### pd-urls

* The comma-separated list of PD URLs. If multiple addresses are specified, the PD client will automatically attempt to connect to another address if an error occurs when connecting to one address.
* Default value: `http://127.0.0.1:2379`
### initial-commit-ts

* Specifies from which commit timestamp of the transaction the replication process starts. This configuration is applicable only to the Drainer node that is in the replication process for the first time. If a checkpoint already exists in the downstream, the replication will be performed according to the time recorded in the checkpoint.
* commit ts (commit timestamp) is a specific point in time for [transaction](https://docs.pingcap.com/tidb/stable/transaction-overview#transactions) commits in TiDB. It is a globally unique and increasing timestamp from PD as the unique ID of the current transaction. You can get the `initial-commit-ts` configuration in the following typical ways:
    - If BR is used, you can get `initial-commit-ts` from the backup TS recorded in the metadata backed up by BR (backupmeta).
    - If Dumpling is used, you can get `initial-commit-ts` from the Pos recorded in the metadata backed up by Dumpling (metadata),
    - If PD Control is used, `initial-commit-ts` is in the output of the `tso` command.
* Default value: `-1`. Drainer will get a new timestamp from PD as the starting time, which means that the replication process starts from the current time.
### synced-check-time

* You can access the `/status` path through the HTTP API to query the status of Drainer replication. `synced-check-time` specifies how many minutes from the last successful replication is considered as `synced`, that is, the replication is complete.
* Default value: `5`
### compressor

* Specifies the compression algorithm used for data transfer between Pump and Drainer. Currently only the `gzip` algorithm is supported.
* Default value: "", which means no compression.
### security

This section introduces configuration items related to security.
#### ssl-ca

* Specifies the file path of the trusted SSL certificate list or CA list. For example, `/path/to/ca.pem`.
* Default value: ""
#### ssl-cert

* Specifies the path of the X509 certificate file encoded in the PEM format. For example, `/path/to/drainer.pem`.
* Default value: ""
#### ssl-key

* Specifies the path of the X509 key file encoded in the PEM format. For example, `/path/to/pump-key.pem`.
* Default value: ""
### syncer

The `syncer` section includes configuration items related to the downstream.
#### db-type

Currently, the following downstream types are supported:

* `mysql`
* `tidb`
* `kafka`
* `file`

Default value: `mysql`
#### sql-mode

* Specifies the SQL mode when the downstream is the `mysql` or `tidb` type. If there is more than one mode, use commas to separate them.
* Default value: ""
#### ignore-txn-commit-ts

* Specifies the commit timestamp at which the binlog is ignored, such as `[416815754209656834, 421349811963822081]`.
* Default value: `[]`
#### ignore-schemas

* Specifies the database to be ignored during replication. If there is more than one database to be ignored, use commas to separate them. If all changes in a binlog file are filtered, the whole binlog file is ignored.
* Default value: `INFORMATION_SCHEMA,PERFORMANCE_SCHEMA,mysql`
#### ignore-table

Ignores the specified table changes during replication. You can specify multiple tables to be ignored in the `toml` file. For example:

```toml
[[syncer.ignore-table]]
db-name = "test"
tbl-name = "log"

[[syncer.ignore-table]]
db-name = "test"
tbl-name = "audit"
```

If all changes in a binlog file are filtered, the whole binlog file is ignored.

Default value: `[]`
#### replicate-do-db

* Specifies the database to be replicated. For example, `[db1, db2]`.
* Default value: `[]`
#### replicate-do-table

Specifies the table to be replicated. For example:

```toml
[[syncer.replicate-do-table]]
db-name ="test"
tbl-name = "log"

[[syncer.replicate-do-table]]
db-name ="test"
tbl-name = "~^a.*"
```

Default value: `[]`
#### txn-batch

* When the downstream is the `mysql` or `tidb` type, DML operations are executed in different batches. This parameter specifies how many DML operations can be included in each transaction.
* Default value: `20`
#### worker-count

* When the downstream is the `mysql` or `tidb` type, DML operations are executed concurrently. This parameter specifies the concurrency numbers of DML operations.
* Default value: `16`
#### disable-dispatch

* Disables the concurrency and forcibly set `worker-count` to `1`.
* Default value: `false`
#### safe-mode

If the safe mode is enabled, Drainer modifies the replication updates in the following way:

* `Insert` is modified to `Replace Into`
* `Update` is modified to `Delete` plus `Replace Into`

Default value: `false`
