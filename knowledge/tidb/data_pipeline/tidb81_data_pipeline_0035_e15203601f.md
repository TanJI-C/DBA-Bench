# Parquet to TiDB migration with TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-parquet-files-to-tidb.md`
- Source Title: `Migrate Data from Parquet Files to TiDB`
- Source Heading Path: `Migrate Data from Parquet Files to TiDB | Migrate Data from Parquet Files to TiDB > Prerequisites | Migrate Data from Parquet Files to TiDB > Step 1. Prepare the parquet files | Migrate Data from Parquet Files to TiDB > Step 2. Create the target table schema | Migrate Data from Parquet Files to TiDB > Step 3. Create the configuration file | Migrate Data from Parquet Files to TiDB > Step 4. Import the data`
- Source Line Ranges: `5-130`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `pd`, `tiup`, `shared`
- Topic Tags: `parquet`, `hive`, `schema-creation`, `configuration`, `import`, `s3`, `hdfs`, `progress-check`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0035_e15203601f`
- Source ID: `tidb-docs-8.1:migrate-from-parquet-files-to-tidb.md#migrate-data-from-parquet-files-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c702261cc2d6cec2f8a0df2fce7cc3804cdc350615f3a885d07f750d2984f32`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-parquet-files-to-tidb#migrate-data-from-parquet-files-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-parquet-files-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented workflow to migrate Parquet files from Hive, local storage, HDFS, or S3 into TiDB with TiDB Lightning, including schema preparation, configuration, import, and progress verification.
- Retrieval Keywords: Migrate Data from Parquet Files to TiDB, TiDB Lightning, Apache Hive, STORED AS PARQUET LOCATION '/path/in/hdfs', CREATE TABLE temp STORED AS PARQUET, hdfs dfs -get, DROP TABLE temp, ${db_name}.${table_name}.parquet, TiDB Lightning Data Sources, customized expressions, ${db_name}-schema-create.sql, ${db_name}.${table_name}-schema.sql, tidb-lightning.toml, [tikv-importer], backend = "local", backend = "tidb", sorted-kv-dir, [mydumper], data-source-dir, [tidb], status-port, pd-addr, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ~/.aws/credentials, nohup tiup tidb-lightning -config tidb-lightning.toml, progress, tidb-lightning.log, the whole procedure completed, tidb lightning exit
- Follow-up Guidance: The source also points to TiDB Lightning configuration, TiDB Lightning Data Sources, the monitoring dashboard, the TiDB Lightning web interface, and the TiDB Lightning FAQ for more details and troubleshooting.
- Classification Note: This is classified as a self-managed data pipeline topic for the lightning component because the content describes configuring and running TiDB Lightning to import Parquet data into TiDB, including HDFS or S3 data sources, schema files, and import progress checks.

## Official Source Content

# Migrate Data from Parquet Files to TiDB

This document describes how to generate parquet files from Apache Hive and how to migrate data from parquet files to TiDB using TiDB Lightning.

If you export parquet files from Amazon Aurora, refer to [Migrate data from Amazon Aurora to TiDB](https://docs.pingcap.com/tidb/stable/migrate-aurora-to-tidb).
## Prerequisites

- [Install TiDB Lightning using TiUP](https://docs.pingcap.com/tidb/stable/migration-tools).
- [Get the target database privileges required for TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq#what-are-the-privilege-requirements-for-the-target-database).
## Step 1. Prepare the parquet files

This section describes how to export parquet files from Hive that can be read by TiDB Lightning.

Each table in Hive can be exported to parquet files by annotating `STORED AS PARQUET LOCATION '/path/in/hdfs'`. Therefore, if you need to export a table named `test`, perform the following steps:

1. Run the following SQL statement in Hive:

    ```sql
    CREATE TABLE temp STORED AS PARQUET LOCATION '/path/in/hdfs'
    AS SELECT * FROM test;
    ```

    After executing the preceding statement, the table data is successfully exported to the HDFS system.

2. Export the parquet files to the local file system using the `hdfs dfs -get` command:

    ```shell
    hdfs dfs -get /path/in/hdfs /path/in/local
    ```

    After the export is complete, if you need to delete the exported parquet files in HDFS, you can directly delete the temporary table (`temp`):

    ```sql
    DROP TABLE temp;
    ```

3. The parquet files exported from Hive might not have the `.parquet` suffix and cannot be correctly identified by TiDB Lightning. Therefore, before importing the files, you need to rename the exported files and add the `.parquet` suffix to change the full filename to a format that TiDB Lightning recognizes, for example, `${db_name}. ${table_name}.parquet`. For more information about file types and patterns, see [TiDB Lightning Data Sources](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-data-source). You can also match data files by setting correct [customized expressions](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-data-source#match-customized-files).

4. Put all the parquet files in a unified directory, for example, `/data/my_datasource/` or `s3://my-bucket/sql-backup`. TiDB Lightning will recursively search for all `.parquet` files in this directory and its subdirectories.
## Step 2. Create the target table schema

Before importing data from parquet files into TiDB, you need to create the target table schema. You can create the target table schema by either of the following two methods:

* **Method 1**: create the target table schema using TiDB Lightning.

    Create SQL files that contain the required DDL statements:

    - Add `CREATE DATABASE` statements in the `${db_name}-schema-create.sql` files.
    - Add `CREATE TABLE` statements in the `${db_name}.${table_name}-schema.sql` files.

* **Method 2**: create the target table schema manually.
## Step 3. Create the configuration file

Create a `tidb-lightning.toml` file with the following content:

```toml
[lightning]
# Log
level = "info"
file = "tidb-lightning.log"

[tikv-importer]
# "local": Default backend. The local backend is recommended to import large volumes of data (1 TiB or more). During the import, the target TiDB cluster cannot provide any service.
backend = "local"
# "tidb": The "tidb" backend is recommended to import data less than 1 TiB. During the import, the target TiDB cluster can provide service normally.
# For more information on import mode, refer to <https://docs.pingcap.com/tidb/stable/tidb-lightning-overview#tidb-lightning-architecture>
# Set the temporary storage directory for the sorted Key-Value files. The directory must be empty, and the storage space must be greater than the size of the dataset to be imported. For better import performance, it is recommended to use a directory different from `data-source-dir` and use flash storage, which can use I/O exclusively.
sorted-kv-dir = "${sorted-kv-dir}"

[mydumper]
# Directory of the data source.
data-source-dir = "${data-path}" # A local path or S3 path. For example, 's3://my-bucket/sql-backup'.

[tidb]
# The target cluster.
host = ${host}            # e.g.: 172.16.32.1
port = ${port}            # e.g.: 4000
user = "${user_name}"     # e.g.: "root"
password = "${password}"  # e.g.: "rootroot"
status-port = ${status-port} # During the import, TiDB Lightning needs to obtain the table schema information from the TiDB status port. e.g.: 10080
pd-addr = "${ip}:${port}" # The address of the PD cluster, e.g.: 172.16.31.3:2379. TiDB Lightning obtains some information from PD. When backend = "local", you must specify status-port and pd-addr correctly. Otherwise, the import will be abnormal.
```

For more information on the configuration file, refer to [TiDB Lightning configuration](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).
## Step 4. Import the data

1. Run `tidb-lightning`.

    - If you import data from Amazon S3, you need to set the SecretKey and AccessKey of the account that has permission to access the S3 backend storage as environment variables before running TiDB Lightning.

        ```shell
        export AWS_ACCESS_KEY_ID=${access_key}
        export AWS_SECRET_ACCESS_KEY=${secret_key}
        ```

        In addition to the preceding method, TiDB Lightning also supports reading the credential file from `~/.aws/credentials`.

    - If you launch the program in the command line, the process might exit unexpectedly after receiving a `SIGHUP` signal. In this case, it is recommended to run the program using a `nohup` or `screen` tool. For example:

        ```shell
        nohup tiup tidb-lightning -config tidb-lightning.toml > nohup.out 2>&1 &
        ```

2. After the import starts, you can check the progress of the import by either of the following methods:

    - Search for the keyword `progress` in the log using `grep`. The progress is updated every 5 minutes by default.
    - Check progress in the [monitoring dashboard](https://docs.pingcap.com/tidb/stable/tidb-lightning/monitor-tidb-lightning).
    - Check progress in [TiDB Lightning web interface](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-web-interface).

    After TiDB Lightning completes the import, it exits automatically.

3. Check if the import is successful.

    Check whether `tidb-lightning.log` contains `the whole procedure completed` in the last lines. If yes, the import is successful. If no, the import encounters an error. Address the error as instructed in the error message.

    > **Note:**
    >
    > Whether the import is successful or not, the last line of the log shows `tidb lightning exit`. It means that TiDB Lightning exits normally, but does not necessarily mean that the import is successful.

If the import fails, refer to [TiDB Lightning FAQ](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq) for troubleshooting.
