# Dumpling overview, privileges, and SQL/CSV export basics

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dumpling-overview.md`
- Source Title: `Dumpling Overview`
- Source Heading Path: `Use Dumpling to Export Data | Use Dumpling to Export Data > Export data from TiDB or MySQL | Use Dumpling to Export Data > Export data from TiDB or MySQL > Required privileges | Use Dumpling to Export Data > Export data from TiDB or MySQL > Export to SQL files | Use Dumpling to Export Data > Export data from TiDB or MySQL > Export to SQL files > URI formats of the storage services | Use Dumpling to Export Data > Export data from TiDB or MySQL > Export to CSV files`
- Source Line Ranges: `5-151`
- Source Scope: `shared`
- Primary Component: `dumpling`
- Related Components: `tiup`, `tidb`, `lightning`, `pd`, `ticdc`, `br`
- Topic Tags: `overview`, `installation`, `export`, `sql`, `csv`, `privileges`, `storage-uri`, `s3`, `filtering`, `gc`, `consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0019_44faa266f4`
- Source ID: `tidb-docs-8.1:dumpling-overview.md#use-dumpling-to-export-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8ee544f260363531f340a0b830c474ba80fa53feeb01ec2f02fc311a4d842cea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dumpling-overview#use-dumpling-to-export-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dumpling-overview.md

## Retrieval Guidance

- Use When: Use this chunk when looking for Dumpling export basics such as installation, required privileges, SQL or CSV export commands, storage URI output, filtering with --sql, and TiDB-specific consistency or GC safe point notes.
- Retrieval Keywords: Dumpling overview, tiup install dumpling, tiup dumpling, Required privileges, PROCESS, SELECT, RELOAD, LOCK TABLES, REPLICATION CLIENT, --filetype sql, --filetype csv, --output, external storage URI, Amazon S3, -t, -r, -F, --sql, --output-filename-template, --csv-separator, --csv-delimiter, tidb_snapshot, INFORMATION_SCHEMA.CLUSTER_INFO, GC safe point, _tidb_rowid, consistency flush, consistency lock
- Follow-up Guidance: The source also points to the Dumpling option list, external storage URI formats, manual TiDB GC time adjustment, and TiDB Lightning for importing exported data.
- Classification Note: This is classified as data_pipeline because the content describes how Dumpling exports TiDB or MySQL data as SQL or CSV files, including permissions, output destinations, and export options.

## Official Source Content

# Use Dumpling to Export Data

This document introduces the data export tool - [Dumpling](https://github.com/pingcap/tidb/tree/release-8.1/dumpling). Dumpling exports data stored in TiDB/MySQL as SQL or CSV data files and can be used to make a logical full backup or export. Dumpling also supports exporting data to Amazon S3.

You can get Dumpling using [TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-overview) by running `tiup install dumpling`. Afterwards, you can use `tiup dumpling ...` to run Dumpling.

The Dumpling installation package is included in the TiDB Toolkit. To download the TiDB Toolkit, see [Download TiDB Tools](https://docs.pingcap.com/tidb/stable/download-ecosystem-tools).

You can install Dumpling using the following commands:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
source ~/.bash_profile
tiup install dumpling
```

In the above commands, you need to modify `~/.bash_profile` to the path of your profile file.

For detailed usage of Dumpling, use the `--help` option or refer to [Option list of Dumpling](#option-list-of-dumpling).

When using Dumpling, you need to execute the export command on a running cluster.

TiDB also provides other tools that you can choose to use as needed.

- For backups of SST files (key-value pairs) or backups of incremental data that are not sensitive to latency, refer to [BR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview).
- For real-time backups of incremental data, refer to [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview).
- All exported data can be imported back to TiDB using [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview).

> **Note:**
>
> PingCAP previously maintained a fork of the [mydumper project](https://github.com/maxbube/mydumper) with enhancements specific to TiDB. Starting from v7.5.0, [Mydumper](https://docs.pingcap.com/tidb/v4.0/mydumper-overview) is deprecated and most of its features have been replaced by [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview). It is strongly recommended that you use Dumpling instead of mydumper.

Dumpling has the following advantages:

- Support exporting data in multiple formats, including SQL and CSV.
- Support the [table-filter](https://github.com/pingcap/tidb-tools/blob/master/pkg/table-filter/README.md) feature, which makes it easier to filter data.
- Support exporting data to Amazon S3 cloud storage.
- More optimizations are made for TiDB:
    - Support configuring the memory limit of a single TiDB SQL statement.
    - If Dumpling can access the PD address and the [`INFORMATION_SCHEMA.CLUSTER_INFO`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-info) table of the TiDB cluster, Dumpling supports automatically adjusting the [GC](https://docs.pingcap.com/tidb/stable/garbage-collection-overview) safe point time to block GC for TiDB v4.0.0 and later versions.
    - Use TiDB's hidden column `_tidb_rowid` to optimize the performance of concurrent data export from a single table.
    - For TiDB, you can set the value of [`tidb_snapshot`](https://docs.pingcap.com/tidb/stable/read-historical-data#how-tidb-reads-data-from-history-versions) to specify the time point of the data backup. This ensures the consistency of the backup, instead of using `FLUSH TABLES WITH READ LOCK` to ensure the consistency.

> **Note:**
>
> Dumpling cannot connect to PD in the following scenarios:
>
> - The TiDB cluster is running on Kubernetes (unless Dumpling itself is run inside the Kubernetes environment).
> - The TiDB cluster is running on TiDB Cloud.
>
> In such cases, you need to manually [adjust the TiDB GC time](#manually-set-the-tidb-gc-time) to avoid export failure.
## Export data from TiDB or MySQL
### Required privileges

- PROCESS: Required to query the cluster information to obtain the PD address and then control GC via the PD.
- SELECT: Required when exporting tables.
- RELOAD: Required when using `consistency flush`. Note that only TiDB supports this privilege. When the upstream is an RDS database or a managed service, you can ignore this privilege.
- LOCK TABLES: Required when using `consistency lock`. This privilege must be granted for all the databases and tables to be exported.
- REPLICATION CLIENT: Required when exporting metadata to record data snapshot. This privilege is optional and you can ignore it if you do not need to export metadata.
### Export to SQL files

This document assumes that there is a TiDB instance on the 127.0.0.1:4000 host and that this TiDB instance has a root user without a password.

Dumpling exports data to SQL files by default. You can also export data to SQL files by adding the `--filetype sql` flag:

```shell
tiup dumpling -u root -P 4000 -h 127.0.0.1 --filetype sql -t 8 -o /tmp/test -r 200000 -F 256MiB
```

In the command above:

+ The `-h`, `-P`, and `-u` option respectively mean the address, the port, and the user. If a password is required for authentication, you can use `-p $YOUR_SECRET_PASSWORD` to pass the password to Dumpling.
+ The `-o` (or `--output`) option specifies the export directory of the storage, which supports an absolute local file path or an [external storage URI](https://docs.pingcap.com/tidb/stable/external-storage-uri).
+ The `-t` option specifies the number of threads for the export. Increasing the number of threads improves the concurrency of Dumpling and the export speed, and also increases the database's memory consumption. Therefore, it is not recommended to set the number too large. Usually, it's less than 64.
+ The `-r` option enables in-table concurrency to speed up the export. It is disabled by default (value `0`). When enabled with a value greater than `0`, the behavior depends on the source database. 

    - For TiDB, Dumpling uses region information for splitting, which also reduces memory usage. The specified `-r` value does not affect the split algorithm. 
    - For MySQL, this option is supported when the primary key (or the first column of a composite primary key) is of an `INT` or `STRING` type.

+ The `-F` option is used to specify the maximum size of a single file (the unit here is `MiB`; inputs like `5GiB` or `8KB` are also acceptable). It is recommended to keep its value to 256 MiB or less if you plan to use TiDB Lightning to load this file into a TiDB instance.

> **Note:**
>
> If the size of a single exported table exceeds 10 GB, it is **strongly recommended to use** the `-r` and `-F` options.
#### URI formats of the storage services

This section describes the URI formats of the storage services, including Amazon S3, GCS, and Azure Blob Storage. The URI format is as follows:

```shell
[scheme]://[host]/[path]?[parameters]
```

For more information, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).
### Export to CSV files

You can export data to CSV files by adding the `--filetype csv` argument.

When you export data to CSV files, you can use `--sql <SQL>` to filter the records with the SQL statements. For example, you can export all records that match `id < 100` in `test.sbtest1` using the following command:

```shell
tiup dumpling -u root -P 4000 -h 127.0.0.1 -o /tmp/test --filetype csv --sql 'select * from `test`.`sbtest1` where id < 100' -F 100MiB --output-filename-template 'test.sbtest1.{{.Index}}'
```

In the command above:

- The `--sql` option can be used only for exporting to CSV files. The command above executes the `SELECT * FROM <table-name> WHERE id <100` statement on all tables to be exported. If a table does not have the specified field, the export fails.

- When you use the `--sql` option, Dumpling cannot obtain the exported table and schema information. You can specify the file name format of the CSV files using the `--output-filename-template` option, which facilitates the subsequent use of [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) to import the data file. For example, `--output-filename-template='test.sbtest1.{{.Index}}'` specifies that the exported CSV files are named as `test.sbtest1.000000000` or `test.sbtest1.000000001`.

- When you use the `--sql` option, Dumpling cannot obtain the exported table and schema information. You can specify the file name format of the CSV files using the `--output-filename-template` option. For example, `--output-filename-template='test.sbtest1.{{.Index}}'` specifies that the exported CSV files are named as `test.sbtest1.000000000` or `test.sbtest1.000000001`.

- You can use options like `--csv-separator` and `--csv-delimiter` to configure the CSV file format. For details, refer to the [Dumpling option list](#option-list-of-dumpling).

> **Note:**
>
> *Strings* and *keywords* are not distinguished by Dumpling. If the imported data is the Boolean type, the value of `true` is converted to `1` and the value of `false` is converted to `0`.
