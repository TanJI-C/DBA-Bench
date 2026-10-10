# Import MySQL SQL files into TiDB with TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-sql-files-to-tidb.md`
- Source Title: `Migrate Data from SQL Files to TiDB`
- Source Heading Path: `Migrate Data from SQL Files to TiDB | Migrate Data from SQL Files to TiDB > Prerequisites | Migrate Data from SQL Files to TiDB > Step 1. Prepare SQL files | Migrate Data from SQL Files to TiDB > Step 2. Define the target table schema | Migrate Data from SQL Files to TiDB > Step 3. Create the configuration file | Migrate Data from SQL Files to TiDB > Step 4. Import the data`
- Source Line Ranges: `5-97`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `dumpling`, `tidb`, `pd`, `tiup`, `shared`
- Topic Tags: `sql-file-import`, `migration`, `prerequisites`, `schema-creation`, `configuration`, `s3`, `local-backend`, `tidb-backend`, `credentials`, `progress-monitoring`, `verification`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0036_dc3cd6c419`
- Source ID: `tidb-docs-8.1:migrate-from-sql-files-to-tidb.md#migrate-data-from-sql-files-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d996507b17556c1ab94d28edcff1f6d8fbe4194346c44e2fff0468387e84357`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-sql-files-to-tidb#migrate-data-from-sql-files-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-sql-files-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when looking for official steps and configuration details to import MySQL SQL files into TiDB with TiDB Lightning, including schema preparation, local or S3 data sources, backend settings, credentials, progress checks, and completion verification.
- Retrieval Keywords: Migrate Data from SQL Files to TiDB, Import MySQL SQL files into TiDB with TiDB Lightning, TiDB Lightning, Dumpling, SQL files, .sql files, /data/my_datasource/, s3://my-bucket/sql-backup, ${db_name}-schema-create.sql, ${db_name}.${table_name}-schema.sql, CREATE DATABASE, CREATE TABLE, tidb-lightning.toml, [tikv-importer], backend = "local", backend = "tidb", sorted-kv-dir, [mydumper], data-source-dir, [tidb], status-port, pd-addr, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ~/.aws/credentials, nohup tiup tidb-lightning -config tidb-lightning.toml, SIGHUP, progress, Grafana dashboard, TiDB Lightning Web Interface, tidb-lightning.log, the whole procedure completed, tidb lightning exit, TiDB Lightning FAQ
- Follow-up Guidance: The source points to TiDB Lightning Configuration, TiDB Lightning Monitoring, TiDB Lightning Web Interface, TiDB Lightning FAQ, and Export to SQL files using Dumpling for more details.
- Classification Note: This is classified as a self-managed data pipeline document because the content describes using TiDB Lightning and related configuration to migrate SQL-file data into a TiDB cluster, including PD, TiDB status port, S3 credentials, and import monitoring.

## Official Source Content

# Migrate Data from SQL Files to TiDB

This document describes how to migrate data from MySQL SQL files to TiDB using TiDB Lightning. For how to generate MySQL SQL files, refer to [Export to SQL files using Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#export-to-sql-files).
## Prerequisites

- [Install TiDB Lightning using TiUP](https://docs.pingcap.com/tidb/stable/migration-tools)
- [Grant the required privileges to the target database for TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq#what-are-the-privilege-requirements-for-the-target-database)
## Step 1. Prepare SQL files

Put all the SQL files in the same directory, like `/data/my_datasource/` or `s3://my-bucket/sql-backup`. TiDB Lightning recursively searches for all `.sql` files in this directory and its subdirectories.
## Step 2. Define the target table schema

To import data to TiDB, you need to create the table schema for the target database.

If you use Dumpling to export data, the table schema file is automatically exported. For the data exported in other ways, you can create the table schema in one of the following methods:

+ **Method 1**: Create the target table schema using TiDB Lightning.

    Create SQL files that contain the required DDL statements:

    - Add `CREATE DATABASE` statements in the `${db_name}-schema-create.sql` files.
    - Add `CREATE TABLE` statements in the `${db_name}.${table_name}-schema.sql` files.

+ **Method 2**: Create the target table schema manually.
## Step 3. Create the configuration file

Create a `tidb-lightning.toml` file with the following content:

```toml
[lightning]
# Log
level = "info"
file = "tidb-lightning.log"

[tikv-importer]
# "local": Default. The local backend is used to import large volumes of data (around or more than 1 TiB). During the import, the target TiDB cluster cannot provide any service.
# "tidb": The "tidb" backend can also be used to import small volumes of data (less than 1 TiB). During the import, the target TiDB cluster can provide service normally. For the information about backend mode, refer to https://docs.pingcap.com/tidb/stable/tidb-lightning-backends.

backend = "local"
# Sets the temporary storage directory for the sorted key-value files. The directory must be empty, and the storage space must be greater than the size of the dataset to be imported. For better import performance, it is recommended to use a directory different from `data-source-dir` and use flash storage and exclusive I/O for the directory.
sorted-kv-dir = "${sorted-kv-dir}"

[mydumper]
# Directory of the data source
data-source-dir = "${data-path}" # Local or S3 path, such as 's3://my-bucket/sql-backup'

[tidb]
# The information of target cluster
host = ${host}                # For example, 172.16.32.1
port = ${port}                # For example, 4000
user = "${user_name}"         # For example, "root"
password = "${password}"      # For example, "rootroot"
status-port = ${status-port}  # During the import process, TiDB Lightning needs to obtain table schema information from the "Status Port" of TiDB, such as 10080.
pd-addr = "${ip}:${port}"     # The address of the cluster's PD. TiDB Lightning obtains some information through PD, such as 172.16.31.3:2379. When backend = "local", you must correctly specify status-port and pd-addr. Otherwise, the import will encounter errors.
```

For more information about the configuration file, refer to [TiDB Lightning Configuration](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).
## Step 4. Import the data

To start the import, run `tidb-lightning`. If you launch the program in the command line, the program might exit because of the `SIGHUP` signal. In this case, it is recommended to run the program with a `nohup` or `screen` tool.

If you import the data from S3, you need to pass in `SecretKey` and `AccessKey` of the account as environment variables. The account has the permission to access the S3 backend storage.

```shell
export AWS_ACCESS_KEY_ID=${access_key}
export AWS_SECRET_ACCESS_KEY=${secret_key}
nohup tiup tidb-lightning -config tidb-lightning.toml > nohup.out 2>&1 &
```

TiDB Lightning also supports reading credential files from `~/.aws/credentials`.

After the import is started, you can check the progress in one of the following ways:

- Search the `progress` keyword in the `grep` log, which is updated every 5 minutes by default.
- Use the Grafana dashboard. For details, see [TiDB Lightning Monitoring](https://docs.pingcap.com/tidb/stable/tidb-lightning/monitor-tidb-lightning).
- Use web interface. For details, see [TiDB Lightning Web Interface](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-web-interface).

After the import is completed, TiDB Lightning automatically exits. Check whether `tidb-lightning.log` contains `the whole procedure completed` in the last lines. If yes, the import is successful. If no, the import encounters an error. Address the error as instructed in the error message.

> **Note:**
>
> No matter whether the import is successful or not, the last line displays `tidb lightning exit`. It only means that TiDB Lightning has exited normally, not the completion of the task.
If you encounter problems during the import process, refer to [TiDB Lightning FAQ](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq) for troubleshooting.
