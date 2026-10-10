# Export Aurora snapshot to S3 and import full data with Lightning

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-aurora-to-tidb.md`
- Source Title: `Migrate Data from Amazon Aurora to TiDB`
- Source Heading Path: `Migrate Data from Amazon Aurora to TiDB > Import full data to TiDB > Step 2. Export and import an Amazon Aurora snapshot to Amazon S3 | Migrate Data from Amazon Aurora to TiDB > Import full data to TiDB > Step 2. Export and import an Amazon Aurora snapshot to Amazon S3 > 2.1 Export an Amazon Aurora snapshot to Amazon S3 | Migrate Data from Amazon Aurora to TiDB > Import full data to TiDB > Step 2. Export and import an Amazon Aurora snapshot to Amazon S3 > 2.2 Create the TiDB Lightning configuration file for the data file | Migrate Data from Amazon Aurora to TiDB > Import full data to TiDB > Step 2. Export and import an Amazon Aurora snapshot to Amazon S3 > 2.3 Import full data to TiDB`
- Source Line Ranges: `87-176`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `pd`, `tikv`, `tiup`, `shared`
- Topic Tags: `snapshot-export`, `s3`, `full-load`, `binlog-position`, `lightning-config`, `parquet`, `monitoring`, `verification`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0029_f90ca5cfa7`
- Source ID: `tidb-docs-8.1:migrate-aurora-to-tidb.md#step-2-export-and-import-an-amazon-aurora-snapshot-to-amazon-s3`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `82bc04f9970746c1737838ffd129562d284866e7a85233b9af308092626aeaa7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-aurora-to-tidb#step-2-export-and-import-an-amazon-aurora-snapshot-to-amazon-s3
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-aurora-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact procedure for recording Aurora binlog position, exporting an Aurora snapshot to S3, configuring TiDB Lightning for parquet snapshot files, and checking full data import progress and completion.
- Retrieval Keywords: Export and import an Amazon Aurora snapshot to Amazon S3, SHOW MASTER STATUS, mysql-bin-changelog.018128, binlog position, within 5 minutes, tidb-lightning-data.toml, data-source-dir = "${s3_path}", s3://my-bucket/sql-backup, [[mydumper.files]], pattern = '(?i)^(?:[^/]*/)*([a-z0-9_]+)\.([a-z0-9_]+)/(?:[^/]*/)*(?:[a-z0-9\-_.]+\.(parquet))$', schema = '$1', table = '$2', type = '$3', backend = "local", nohup tiup tidb-lightning -config tidb-lightning-data.toml, grep progress, monitoring dashboard, TiDB Lightning web interface, tidb-lightning.log, the whole procedure completed, tidb lightning exit, TiDB Lightning FAQ
- Follow-up Guidance: If problems occur during import, the content directs readers to TiDB Lightning FAQ for troubleshooting.
- Classification Note: This is classified under data_pipeline with primary component lightning because it focuses on snapshot-based full data import into TiDB using TiDB Lightning and related monitoring and log verification details.

## Official Source Content

### Step 2. Export and import an Amazon Aurora snapshot to Amazon S3

This section describes how to export an Amazon Aurora snapshot to Amazon S3 and import it into TiDB by TiDB Lightning.
#### 2.1 Export an Amazon Aurora snapshot to Amazon S3

1. Get the name and location of the Amazon Aurora binlog for subsequent incremental migration. In Amazon Aurora, run the `SHOW MASTER STATUS` command and record the current binlog position:

    ```sql
    SHOW MASTER STATUS;
    ```

    The output is similar to the following. Record the binlog name and position for later use.

    ```
    +----------------------------+----------+--------------+------------------+-------------------+
    | File                       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
    +----------------------------+----------+--------------+------------------+-------------------+
    | mysql-bin-changelog.018128 |    52806 |              |                  |                   |
    +----------------------------+----------+--------------+------------------+-------------------+
    1 row in set (0.012 sec)
    ```

2. Export the Amazon Aurora snapshot. For detailed steps, refer to [Exporting DB snapshot data to Amazon S3](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_ExportSnapshot.html). After you obtain the binlog position, export the snapshot within 5 minutes. Otherwise, the recorded binlog position might be outdated and thus cause data conflict during the incremental replication.
#### 2.2 Create the TiDB Lightning configuration file for the data file

Create a new `tidb-lightning-data.toml` configuration file, copy the following content into the file, and replace the corresponding content.

```toml
[tidb]

# The target TiDB cluster information.
host = ${host}
port = ${port}
user = "${user_name}"
password = "${password}"
status-port = ${status-port}  # The TiDB status port. Usually the port is 10080.
pd-addr = "${ip}:${port}"     # The cluster PD address. Usually the port is 2379.

[tikv-importer]
# "local": Use the default Physical Import Mode (the "local" backend).
# During the import, the target TiDB cluster cannot provide any service.
# For more information about import modes, see https://docs.pingcap.com/tidb/stable/tidb-lightning-overview
backend = "local"

# Set the temporary storage directory for the sorted Key-Value files.
# The directory must be empty, and the storage space must be greater than the size of the dataset to be imported.
# For better import performance, it is recommended to use a directory different from `data-source-dir` and use flash storage,
# which can use I/O exclusively.
sorted-kv-dir = "${path}"

[mydumper]
# Set the directory of the snapshot file exported from Amazon Aurora
data-source-dir = "${s3_path}"  # eg: s3://my-bucket/sql-backup

[[mydumper.files]]
# The expression that parses the parquet file.
pattern = '(?i)^(?:[^/]*/)*([a-z0-9_]+)\.([a-z0-9_]+)/(?:[^/]*/)*(?:[a-z0-9\-_.]+\.(parquet))$'
schema = '$1'
table = '$2'
type = '$3'
```

If you need to enable TLS in the TiDB cluster, refer to [TiDB Lightning Configuration](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).
#### 2.3 Import full data to TiDB

1. Use TiDB Lightning to import data from an Amazon Aurora snapshot to TiDB.

    ```shell
    export AWS_ACCESS_KEY_ID=${access_key}
    export AWS_SECRET_ACCESS_KEY=${secret_key}
    nohup tiup tidb-lightning -config tidb-lightning-data.toml > nohup.out 2>&1 &
    ```

2. After the import starts, you can check the progress of the import by either of the following methods:

    - `grep` the keyword `progress` in the log. The progress is updated every 5 minutes by default.
    - Check progress in [the monitoring dashboard](https://docs.pingcap.com/tidb/stable/tidb-lightning/monitor-tidb-lightning).
    - Check progress in [the TiDB Lightning web interface](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-web-interface).

3. After TiDB Lightning completes the import, it exits automatically. Check whether `tidb-lightning.log` contains `the whole procedure completed` in the last lines. If yes, the import is successful. If no, the import encounters an error. Address the error as instructed in the error message.

> **Note:**
>
> Whether the import is successful or not, the last line of the log shows `tidb lightning exit`. It means that TiDB Lightning exits normally, but does not necessarily mean that the import is successful.

If you encounter any problem during the import, refer to [TiDB Lightning FAQ](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq) for troubleshooting.
