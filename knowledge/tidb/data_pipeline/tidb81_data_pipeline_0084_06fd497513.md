# Parquet import preparation, schema creation, and storage access for TiDB Cloud Serverless

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-parquet-files-serverless.md`
- Source Title: `Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless`
- Source Heading Path: `Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless | Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Step 1. Prepare the Parquet files | Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Step 2. Create the target table schemas | Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Step 3. Configure cross-account access`
- Source Line Ranges: `5-92`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `shared`
- Topic Tags: `parquet`, `import`, `s3`, `gcs`, `azure-blob-storage`, `alibaba-cloud-oss`, `schema-files`, `table-creation`, `database-creation`, `cross-account-access`, `file-naming`, `snappy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0084_06fd497513`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-parquet-files-serverless.md#import-apache-parquet-files-from-amazon-s3-gcs-azure-blob-storage-or-alibaba-cloud-oss-into-tidb-cloud-serverless`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `47c49728f3b3976bbd04f95ab9a56dce6e8b076bb55d778dae6a14d0307dd6a0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files-serverless#import-apache-parquet-files-from-amazon-s3-gcs-azure-blob-storage-or-alibaba-cloud-oss-into-tidb-cloud-serverless
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-parquet-files-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented prerequisites for importing Apache Parquet files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless, including file preparation, schema creation, and cross-account access setup.
- Retrieval Keywords: TiDB Cloud Serverless import Parquet files, Amazon S3 GCS Azure Blob Storage Alibaba Cloud OSS, empty tables only, INSERT SELECT temporary empty table, Snappy compressed official Snappy format, unsupported data types LIST NEST STRUCT BOOL ARRAY MAP, 256 MB split files, ${db_name}.${table_name}.parquet, ${db_name}.${table_name}.000001.parquet, Mapping Settings, ${db_name}-schema-create.sql, CREATE DATABASE, ${db_name}.${table_name}-schema.sql, CREATE TABLE, single DDL statement only first one takes effect, configure external storage access for TiDB Cloud Serverless, AWS access key, Role ARN
- Follow-up Guidance: The source notes that you will need the access key, secret access key, or Role ARN in Step 4, and that Mapping Settings in Step 4 can map unchanged filenames to a single target table.
- Classification Note: This is classified as data_pipeline for the cloud component because the content describes Parquet import prerequisites, schema SQL files, storage naming rules, and external storage access for TiDB Cloud Serverless.

## Official Source Content

# Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless

You can import both uncompressed and Snappy compressed [Apache Parquet](https://parquet.apache.org/) format data files to TiDB Cloud Serverless. This document describes how to import Parquet files from Amazon Simple Storage Service (Amazon S3), Google Cloud Storage (GCS), Azure Blob Storage, or Alibaba Cloud Object Storage Service (OSS) into TiDB Cloud Serverless.

> **Note:**
>
> - TiDB Cloud Serverless only supports importing Parquet files into empty tables. To import data into an existing table that already contains data, you can use TiDB Cloud Serverless to import the data into a temporary empty table by following this document, and then use the `INSERT SELECT` statement to copy the data to the target existing table.
> - The Snappy compressed file must be in the [official Snappy format](https://github.com/google/snappy). Other variants of Snappy compression are not supported.
## Step 1. Prepare the Parquet files

> **Note:**
>
> Currently, TiDB Cloud Serverless does not support importing Parquet files that contain any of the following data types. If Parquet files to be imported contain such data types, you need to first regenerate the Parquet files using the [supported data types](#supported-data-types) (for example, `STRING`). Alternatively, you could use a service such as AWS Glue to transform data types easily.
>
> - `LIST`
> - `NEST STRUCT`
> - `BOOL`
> - `ARRAY`
> - `MAP`

1. If a Parquet file is larger than 256 MB, consider splitting it into smaller files, each with a size around 256 MB.

    TiDB Cloud Serverless supports importing very large Parquet files but performs best with multiple input files around 256 MB in size. This is because TiDB Cloud Serverless can process multiple files in parallel, which can greatly improve the import speed.

2. Name the Parquet files as follows:

    - If a Parquet file contains all data of an entire table, name the file in the `${db_name}.${table_name}.parquet` format, which maps to the `${db_name}.${table_name}` table when you import the data.
    - If the data of one table is separated into multiple Parquet files, append a numeric suffix to these Parquet files. For example, `${db_name}.${table_name}.000001.parquet` and `${db_name}.${table_name}.000002.parquet`. The numeric suffixes can be inconsecutive but must be in ascending order. You also need to add extra zeros before the number to ensure all the suffixes are in the same length.

    > **Note:**
    >
    > If you cannot update the Parquet filenames according to the preceding rules in some cases (for example, the Parquet file links are also used by your other programs), you can keep the filenames unchanged and use the **Mapping Settings** in [Step 4](#step-4-import-parquet-files-to-tidb-cloud-serverless) to import your source data to a single target table.
## Step 2. Create the target table schemas

Because Parquet files do not contain schema information, before importing data from Parquet files into TiDB Cloud Serverless, you need to create the table schemas using either of the following methods:

- Method 1: In TiDB Cloud Serverless, create the target databases and tables for your source data.

- Method 2: In the Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud Object Storage Service directory where the Parquet files are located, create the target table schema files for your source data as follows:

    1. Create database schema files for your source data.

        If your Parquet files follow the naming rules in [Step 1](#step-1-prepare-the-parquet-files), the database schema files are optional for the data import. Otherwise, the database schema files are mandatory.

        Each database schema file must be in the `${db_name}-schema-create.sql` format and contain a `CREATE DATABASE` DDL statement. With this file, TiDB Cloud Serverless will create the `${db_name}` database to store your data when you import the data.

        For example, if you create a `mydb-scehma-create.sql` file that contains the following statement, TiDB Cloud Serverless will create the `mydb` database when you import the data.

        ```sql
        CREATE DATABASE mydb;
        ```

    2. Create table schema files for your source data.

        If you do not include the table schema files in the Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud Object Storage Service directory where the Parquet files are located, TiDB Cloud Serverless will not create the corresponding tables for you when you import the data.

        Each table schema file must be in the `${db_name}.${table_name}-schema.sql` format and contain a `CREATE TABLE` DDL statement. With this file, TiDB Cloud Serverless will create the `${db_table}` table in the `${db_name}` database when you import the data.

        For example, if you create a `mydb.mytable-schema.sql` file that contains the following statement, TiDB Cloud Serverless will create the `mytable` table in the `mydb` database when you import the data.

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

To allow TiDB Cloud Serverless to access the Parquet files in the Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud Object Storage Service bucket, do one of the following:

- If your Parquet files are located in Amazon S3, [configure external storage access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-amazon-s3-access).

    You can use either an AWS access key or a Role ARN to access your bucket. Once finished, make a note of the access key (including the access key ID and secret access key) or the Role ARN value as you will need it in [Step 4](#step-4-import-parquet-files-to-tidb-cloud-serverless).

- If your Parquet files are located in GCS, [configure external storage access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-gcs-access).

- If your Parquet files are located in Azure Blob Storage, [configure external storage access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-azure-blob-storage-access).

- If your Parquet files are located in Alibaba Cloud Object Storage Service (OSS), [configure external storage access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-alibaba-cloud-object-storage-service-oss-access).
