# Parquet import prerequisites, schema setup, and storage access

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-parquet-files.md`
- Source Title: `Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated`
- Source Heading Path: `Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated | Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated > Limitations | Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated > Step 1. Prepare the Parquet files | Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated > Step 2. Create the target table schemas | Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated > Step 3. Configure cross-account access`
- Source Line Ranges: `5-96`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `parquet`, `cloud-storage`, `import`, `limitations`, `file-naming`, `schema-files`, `create-table`, `cross-account-access`, `s3`, `gcs`, `azure-blob`, `snappy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0086_c4641ecfe2`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-parquet-files.md#import-apache-parquet-files-from-cloud-storage-into-tidb-cloud-dedicated`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cb8caeac462ef7120c427bfc1c4ca4a8a98f33ebd51b489a348869172d7c1f7a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files#import-apache-parquet-files-from-cloud-storage-into-tidb-cloud-dedicated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-parquet-files.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB Cloud Dedicated requirements and limitations for importing Apache Parquet files from Amazon S3, GCS, or Azure Blob Storage, including file naming, schema files, empty-table constraints, and cross-account access setup.
- Retrieval Keywords: Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated, Parquet import limitations, empty tables only, INSERT SELECT, changefeed, Point-in-time Restore, physical import mode, Google Snappy, official Snappy format, other Parquet compression codecs are not supported, LIST, NEST STRUCT, BOOL, ARRAY, MAP, 256 MB, ${db_name}.${table_name}.parquet, ${db_name}.${table_name}.000001.parquet, Mapping Settings, ${db_name}-schema-create.sql, CREATE DATABASE, ${db_name}.${table_name}-schema.sql, CREATE TABLE, single DDL statement, configure Amazon S3 access, AWS access key, Role ARN, configure GCS access, configure Azure Blob Storage access
- Follow-up Guidance: The next step referenced by this content is Step 4, where the import uses Mapping Settings and the saved access credentials such as an AWS access key or Role ARN.
- Classification Note: This is classified as data_pipeline for the cloud component because the content describes TiDB Cloud Dedicated Parquet data import preparation, schema creation, storage access configuration, and import constraints.

## Official Source Content

# Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated

This document describes how to import Apache Parquet files from Amazon Simple Storage Service (Amazon S3), Google Cloud Storage (GCS), or Azure Blob Storage into TiDB Cloud Dedicated. You can import Parquet files that are either uncompressed or compressed with [Google Snappy](https://github.com/google/snappy). Other Parquet compression codecs are not supported.
## Limitations

- To ensure data consistency, TiDB Cloud allows to import Parquet files into empty tables only. To import data into an existing table that already contains data, you can use TiDB Cloud to import the data into a temporary empty table by following this document, and then use the `INSERT SELECT` statement to copy the data to the target existing table.

- If a TiDB Cloud Dedicated cluster has a [changefeed](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview) or has [Point-in-time Restore](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-point-in-time-restore) enabled, you cannot import data to the cluster (the **Import Data** button will be disabled) because the current data import feature uses the [physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning-physical-import-mode). In this mode, the imported data does not generate change logs, so the changefeed and Point-in-time Restore cannot detect the imported data.
## Step 1. Prepare the Parquet files

> **Note:**
>
> Currently, TiDB Cloud does not support importing Parquet files that contain any of the following data types. If Parquet files to be imported contain such data types, you need to first regenerate the Parquet files using the [supported data types](#supported-data-types) (for example, `STRING`). Alternatively, you could use a service such as AWS Glue to transform data types easily.
>
> - `LIST`
> - `NEST STRUCT`
> - `BOOL`
> - `ARRAY`
> - `MAP`

1. If a Parquet file is larger than 256 MB, consider splitting it into smaller files, each with a size around 256 MB.

    TiDB Cloud supports importing very large Parquet files but performs best with multiple input files around 256 MB in size. This is because TiDB Cloud can process multiple files in parallel, which can greatly improve the import speed.

2. Name the Parquet files as follows:

    - If a Parquet file contains all data of an entire table, name the file in the `${db_name}.${table_name}.parquet` format, which maps to the `${db_name}.${table_name}` table when you import the data.
    - If the data of one table is separated into multiple Parquet files, append a numeric suffix to these Parquet files. For example, `${db_name}.${table_name}.000001.parquet` and `${db_name}.${table_name}.000002.parquet`. The numeric suffixes can be inconsecutive but must be in ascending order. You also need to add extra zeros before the number to ensure all the suffixes are in the same length.

    > **Note:**
    >
    > - If you cannot update the Parquet filenames according to the preceding rules in some cases (for example, the Parquet file links are also used by your other programs), you can keep the filenames unchanged and use the **Mapping Settings** in [Step 4](#step-4-import-parquet-files-to-tidb-cloud) to import your source data to a single target table.
    > - The Snappy compressed file must be in the [official Snappy format](https://github.com/google/snappy). Other variants of Snappy compression are not supported.
## Step 2. Create the target table schemas

Because Parquet files do not contain schema information, before importing data from Parquet files into TiDB Cloud, you need to create the table schemas using either of the following methods:

- Method 1: In TiDB Cloud, create the target databases and tables for your source data.

- Method 2: In the Amazon S3, GCS, or Azure Blob Storage directory where the Parquet files are located, create the target table schema files for your source data as follows:

    1. Create database schema files for your source data.

        If your Parquet files follow the naming rules in [Step 1](#step-1-prepare-the-parquet-files), the database schema files are optional for the data import. Otherwise, the database schema files are mandatory.

        Each database schema file must be in the `${db_name}-schema-create.sql` format and contain a `CREATE DATABASE` DDL statement. With this file, TiDB Cloud will create the `${db_name}` database to store your data when you import the data.

        For example, if you create a `mydb-scehma-create.sql` file that contains the following statement, TiDB Cloud will create the `mydb` database when you import the data.

        ```sql
        CREATE DATABASE mydb;
        ```

    2. Create table schema files for your source data.

        If you do not include the table schema files in the Amazon S3, GCS, or Azure Blob Storage directory where the Parquet files are located, TiDB Cloud will not create the corresponding tables for you when you import the data.

        Each table schema file must be in the `${db_name}.${table_name}-schema.sql` format and contain a `CREATE TABLE` DDL statement. With this file, TiDB Cloud will create the `${db_table}` table in the `${db_name}` database when you import the data.

        For example, if you create a `mydb.mytable-schema.sql` file that contains the following statement, TiDB Cloud will create the `mytable` table in the `mydb` database when you import the data.

        ```sql
        CREATE TABLE mytable (
        ID INT,
        REGION VARCHAR(20),
        COUNT INT );
        ```

        > **Note:**
        >
        > Each `${db_name}.${table_name}-schema.sql` file should only contain a single DDL statement. If the file contains multiple DDL statements, only the first one takes effect.
## Step 3. Configure cross-account access

To allow TiDB Cloud to access the Parquet files in the Amazon S3 bucket, GCS bucket, or Azure Blob Storage container, do one of the following:

- If your Parquet files are located in Amazon S3, [configure Amazon S3 access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-amazon-s3-access).

    You can use either an AWS access key or a Role ARN to access your bucket. Once finished, make a note of the access key (including the access key ID and secret access key) or the Role ARN value as you will need it in [Step 4](#step-4-import-parquet-files-to-tidb-cloud).

- If your Parquet files are located in GCS, [configure GCS access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-gcs-access).

- If your Parquet files are located in Azure Blob Storage, [configure Azure Blob Storage access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-azure-blob-storage-access).
