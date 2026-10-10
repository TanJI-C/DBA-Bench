# BR command-line structure, options, backup, log backup, and restore commands

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/use-br-command-line-tool.md`
- Source Title: `br Command-line Manual`
- Source Heading Path: `br Command-line Manual | br Command-line Manual > `br` command-line description | br Command-line Manual > `br` command-line description > Commands and sub-commands | br Command-line Manual > `br` command-line description > Common options | br Command-line Manual > Commands of full backup | br Command-line Manual > Commands of log backup | br Command-line Manual > Commands of restoring backup data`
- Source Line Ranges: `5-94`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tiup`, `cloud`
- Topic Tags: `command-line`, `subcommands`, `options`, `snapshot-backup`, `log-backup`, `pitr`, `restore`, `external-storage`, `compression`, `tls`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0034_f283ce482c`
- Source ID: `tidb-docs-8.1:br/use-br-command-line-tool.md#br-command-line-manual`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9d89df0da9dc679491df1acc5753513a447c8d361f3ac6faaca0ea57255f33e0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/use-br-command-line-tool#br-command-line-manual
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/use-br-command-line-tool.md

## Retrieval Guidance

- Use When: Use this chunk when you need the overall `tiup br` command structure, the available `backup`, `log`, `restore`, and `debug` sub-commands, or the common BR options for snapshot backup, log backup, PITR, and restore.
- Retrieval Keywords: tiup br, br command-line manual, tiup br backup, tiup br log, tiup br restore, tiup br debug, backup full, restore full, restore db, restore table, log backup, point-in-time recovery, PITR, --pd, --storage, -s, --ca, --cert, --key, --status-addr, --concurrency, --compression, --compression-level, s3://backup-data/snapshot-202209081330/, PD service address, external storage, Amazon S3, Google Cloud Storage, GCS, Azure Blob Storage, NFS, debug checksum, ADMIN CHECKSUM TABLE, backupmeta, decode, encode, search-log-backup
- Follow-up Guidance: The source points to detailed sections for back up cluster snapshots, start a log backup task, query the backup status, point-in-time recovery, and restore cluster snapshots.
- Classification Note: This chunk is reference content because it defines the `br` command-line syntax, lists sub-commands and options, and maps backup, log backup, and restore operations to their exact command names.

## Official Source Content

# br Command-line Manual

This document describes the definition, components, and common options of `br` commands, and how to perform snapshot backup and restore, and log backup and point-in-time recovery (PITR) using `br` commands.
## `br` command-line description

A `br` command consists of sub-commands, options, and parameters. A sub-command is the characters without `-` or `--`. An option is the characters that start with `-` or `--`. A parameter is the characters that immediately follow behind and are passed to the sub-command or the option.

The following is a complete `br` command:

```shell
tiup br backup full --pd "${PD_IP}:2379" \
--storage "s3://backup-data/snapshot-202209081330/"
```

Explanations for the preceding command are as follows:

* `backup`: the sub-command of `tiup br`.
* `full`: the sub-command of `tiup br backup`.
* `-s` (or `--storage`): the option that specifies the path where the backup files are stored. `"s3://backup-data/snapshot-202209081330/"` is the parameter of `-s`.
* `--pd`: the option that specifies the PD service address. `"${PD_IP}:2379"` is the parameter of `--pd`.
### Commands and sub-commands

A `tiup br` command consists of multiple layers of sub-commands. Currently, br command-line tool has the following sub-commands:

* `tiup br backup`: used to back up the data of the TiDB cluster.
* `tiup br log`: used to start and manage log backup tasks.
* `tiup br restore`: used to restore backup data of the TiDB cluster.
* `tiup br debug`: used to parse backup metadata, check backup data, and so on.

`tiup br backup` and `tiup br restore` include the following sub-commands:

* `full`: used to back up or restore all the cluster data.
* `db`: used to back up or restore a specified database of the cluster.
* `table`: used to back up or restore a single table in the specified database of the cluster.

`tiup br debug` includes the following sub-commands:

* `checksum`: (hidden parameter) used to offline check the integrity of backup data to ensure that all backup files match the CRC64 checksum results calculated by [`ADMIN CHECKSUM TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-checksum-table).
* `backupmeta`: used to check whether an intersection exists among backup data files. In normal cases, backup data files do not intersect.
* `decode`: used to parse the `backupmeta` metadata file of a full backup into JSON format. In addition, you can parse specific fields using the `--field` parameter.
* `encode`: used to encode the `backupmeta.json` metadata file of a full backup into the protobuf format that is used during data restore.
* `reset-pd-config-as-default`: (deprecated) used to restore the PD configurations that were changed during the data recovery process to default configurations.
* `search-log-backup`: used to search for specific key information in log backup data.
### Common options

* `--pd`: specifies the PD service address. For example, `"${PD_IP}:2379"`.
* `-s` (or `--storage`): specifies the path where the backup files are stored. Amazon S3, Google Cloud Storage (GCS), Azure Blob Storage, and NFS are supported to store backup data. For more details, refer to [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).
* `--ca`: specifies the path to the trusted CA certificate in the PEM format.
* `--cert`: specifies the path to the SSL certificate in the PEM format.
* `--key`: specifies the path to the SSL certificate key in the PEM format.
* `--status-addr`: specifies the listening address through which `br` provides statistics to Prometheus.
* `--concurrency`: the number of concurrent tasks during the backup or restore.
* `--compression`: determines the compression algorithm used for generating backup files. It supports `lz4`, `snappy`, and `zstd`, with the default being `zstd` (usually no need to modify). For guidance on choosing different compression algorithms, refer to [this document](https://github.com/EighteenZi/rocksdb_wiki/blob/master/Compression.md).
* `--compression-level`: sets the compression level corresponding to the chosen compression algorithm for backup. The default compression level for `zstd` is 3. In most cases there is no need to set this option.
## Commands of full backup

To back up cluster data, run the `tiup br backup` command. You can add the `full` or `table` sub-command to specify the scope of your backup operation: the whole cluster (`full`) or a single table (`table`).

- [Back up TiDB cluster snapshots](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-cluster-snapshots)
- [Back up a database](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-a-database)
- [Back up a table](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-a-table)
- [Back up multiple tables with table filter](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-multiple-tables-with-table-filter)
- [Encrypt snapshots](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages#server-side-encryption)
## Commands of log backup

To start log backup and manage log backup tasks, run the `tiup br log` command.

- [Start a log backup task](https://docs.pingcap.com/tidb/stable/br/br-pitr-manual#start-a-backup-task)
- [Query the backup status](https://docs.pingcap.com/tidb/stable/br/br-pitr-manual#query-the-backup-status)
- [Pause and resume a log backup task](https://docs.pingcap.com/tidb/stable/br/br-pitr-manual#pause-and-resume-a-backup-task)
- [Stop and restart a log backup task](https://docs.pingcap.com/tidb/stable/br/br-pitr-manual#stop-and-restart-a-backup-task)
- [Clean up the backup data](https://docs.pingcap.com/tidb/stable/br/br-pitr-manual#clean-up-backup-data)
- [View the backup metadata](https://docs.pingcap.com/tidb/stable/br/br-pitr-manual#view-the-backup-metadata)
## Commands of restoring backup data

To restore cluster data, run the `tiup br restore` command. You can add the `full`, `db`, or `table` sub-command to specify the scope of your restore: the whole cluster (`full`), a single database (`db`), or a single table (`table`).

- [Point-in-time recovery](https://docs.pingcap.com/tidb/stable/br/br-pitr-manual#restore-to-a-specified-point-in-time-pitr)
- [Restore cluster snapshots](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#restore-cluster-snapshots)
- [Restore a database](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#restore-a-database)
- [Restore a table](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#restore-a-table)
- [Restore multiple tables with table filter](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#restore-multiple-tables-with-table-filter)
- [Restore encrypted snapshots](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#restore-encrypted-snapshots)
