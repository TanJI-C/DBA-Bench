# Aurora migration overview, prerequisites, and schema import with Lightning

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-aurora-to-tidb.md`
- Source Title: `Migrate Data from Amazon Aurora to TiDB`
- Source Heading Path: `Migrate Data from Amazon Aurora to TiDB | Migrate Data from Amazon Aurora to TiDB > Prerequisites | Migrate Data from Amazon Aurora to TiDB > Import full data to TiDB | Migrate Data from Amazon Aurora to TiDB > Import full data to TiDB > Step 1. Export and import the schema file | Migrate Data from Amazon Aurora to TiDB > Import full data to TiDB > Step 1. Export and import the schema file > 1.1 Export the schema file from Amazon Aurora | Migrate Data from Amazon Aurora to TiDB > Import full data to TiDB > Step 1. Export and import the schema file > 1.2 Create the TiDB Lightning configuration file for the schema file | Migrate Data from Amazon Aurora to TiDB > Import full data to TiDB > Step 1. Export and import the schema file > 1.3 Import the schema file to TiDB`
- Source Line Ranges: `5-86`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `dumpling`, `tidb`, `pd`, `tikv`, `tiup`, `shared`
- Topic Tags: `migration`, `full-load`, `schema-export`, `schema-import`, `s3`, `credentials`, `lightning-config`, `dumpling`, `tls`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0028_e3256b022c`
- Source ID: `tidb-docs-8.1:migrate-aurora-to-tidb.md#migrate-data-from-amazon-aurora-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d5cddd28afa1d6d17d380e08a7244a6235cb72195f7769e0e566463a82b3f6cb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-aurora-to-tidb#migrate-data-from-amazon-aurora-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-aurora-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Aurora-to-TiDB full-load prerequisites and the exact Dumpling and TiDB Lightning steps for exporting Aurora schema to S3 and importing that schema into TiDB.
- Retrieval Keywords: Migrate Data from Amazon Aurora to TiDB, Import full data to TiDB, Export and import the schema file, Dumpling, TiDB Lightning, tiup dumpling, --filter, --consistency none, --no-data, s3://my-bucket/schema-backup, tidb-lightning-schema.toml, data-source-dir, sorted-kv-dir, backend = "local", AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ~/.aws/credentials, nohup tiup tidb-lightning -config tidb-lightning-schema.toml
- Follow-up Guidance: If TLS needs to be enabled in the TiDB cluster, the content points to TiDB Lightning Configuration.
- Classification Note: This is classified under data_pipeline with primary component lightning because the content covers schema export with Dumpling and schema import into TiDB using TiDB Lightning configuration and commands.

## Official Source Content

# Migrate Data from Amazon Aurora to TiDB

This document describes how to migrate data from Amazon Aurora to TiDB. The migration process uses [DB snapshot](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Managing.Backups.html), which saves a lot of space and time.

The whole migration has two processes:

- Import full data to TiDB using TiDB Lightning
- Replicate incremental data to TiDB using DM (optional)
## Prerequisites

- [Install Dumpling and TiDB Lightning](https://docs.pingcap.com/tidb/stable/migration-tools). If you want to create the corresponding tables manually on the target side, do not install Dumpling.
- [Get the upstream database privileges required by Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#required-privileges).
- [Get the target database privileges required for TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq#what-are-the-privilege-requirements-for-the-target-database).
## Import full data to TiDB
### Step 1. Export and import the schema file

This section describes how to export the schema file from Amazon Aurora and import it to TiDB. If you have manually created the table in the target database, you can skip this step.
#### 1.1 Export the schema file from Amazon Aurora

Because the snapshot file from Amazon Aurora does not contain the DDL statements, you need to export the schema using Dumpling and create the schema in the target database using TiDB Lightning.

Export the schema using Dumpling by running the following command. The command includes the `--filter` parameter to only export the desired table schema. For more information about the parameters, see the [Option list of Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#option-list-of-dumpling).

```shell
export AWS_ACCESS_KEY_ID=${access_key}
export AWS_SECRET_ACCESS_KEY=${secret_key}
tiup dumpling --host ${host} --port 3306 --user root --password ${password} --filter 'my_db1.table[12],mydb.*' --consistency none --no-data --output 's3://my-bucket/schema-backup'
```

Record the URI of the schema exported in the above command, such as 's3://my-bucket/schema-backup', which will be used when importing the schema file later.

To get access to Amazon S3, you can pass the secret access key and access key of the account that has access to this Amazon S3 storage path into the Dumpling or TiDB Lightning node as environment variables. Dumpling and TiDB Lightning also support reading credential files from `~/.aws/credentials`. This method eliminates the need to provide the secret access key and access key again for all tasks on that Dumpling or TiDB Lightning node.
#### 1.2 Create the TiDB Lightning configuration file for the schema file

Create a new `tidb-lightning-schema.toml` file, copy the following content into the file, and replace the corresponding content.

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
# Set the directory of the schema file exported from Amazon Aurora
data-source-dir = "s3://my-bucket/schema-backup"
```

If you need to enable TLS in the TiDB cluster, refer to [TiDB Lightning Configuration](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).
#### 1.3 Import the schema file to TiDB

Use TiDB Lightning to import the schema file to the downstream TiDB.

```shell
export AWS_ACCESS_KEY_ID=${access_key}
export AWS_SECRET_ACCESS_KEY=${secret_key}
nohup tiup tidb-lightning -config tidb-lightning-schema.toml > nohup.out 2>&1 &
```
