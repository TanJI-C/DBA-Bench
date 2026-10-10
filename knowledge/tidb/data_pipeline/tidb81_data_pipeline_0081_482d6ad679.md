# Serverless CSV import prerequisites, schema preparation, and storage access

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-csv-files-serverless.md`
- Source Title: `Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless`
- Source Heading Path: `Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless | Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Limitations | Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Step 1. Prepare the CSV files | Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Step 2. Create the target table schemas | Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Step 3. Configure cross-account access`
- Source Line Ranges: `5-84`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `csv import`, `serverless`, `s3`, `gcs`, `azure blob storage`, `alibaba cloud oss`, `file naming`, `compression`, `schema files`, `create table`, `cross-account access`, `empty tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0081_482d6ad679`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-csv-files-serverless.md#import-csv-files-from-amazon-s3-gcs-azure-blob-storage-or-alibaba-cloud-oss-into-tidb-cloud-serverless`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5ed0aa37b25379f653fc892ad52f0248e29d0401d09500d2a48d6074f6269d1f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files-serverless#import-csv-files-from-amazon-s3-gcs-azure-blob-storage-or-alibaba-cloud-oss-into-tidb-cloud-serverless
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-csv-files-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when you need the prerequisites and preparation rules for importing CSV files into TiDB Cloud Serverless, including empty-table limitation, CSV naming, schema SQL files, compression formats, and cross-account storage access.
- Retrieval Keywords: TiDB Cloud Serverless import CSV empty tables only, INSERT SELECT temporary empty table, ${db_name}.${table_name}.csv, ${db_name}.${table_name}.000001.csv, ${db_name}.${table_name}.${suffix}.csv.${compress}, compressed CSV .gzip .gz .zstd .zst .snappy, official Snappy format, Mapping Settings, ${db_name}-schema-create.sql, CREATE DATABASE, ${db_name}.${table_name}-schema.sql, CREATE TABLE, single DDL statement only the first one takes effect, configure external storage access for TiDB Cloud Serverless, AWS access key, Role ARN, Amazon S3, GCS, Azure Blob Storage, Alibaba Cloud Object Storage Service OSS
- Follow-up Guidance: The source notes that Step 4 uses Mapping Settings for unchanged uncompressed filenames and requires the recorded AWS access key or Role ARN value when importing from Amazon S3.
- Classification Note: This is classified under data_pipeline for the cloud component because the content describes TiDB Cloud Serverless CSV import preparation, target schema creation, and external object storage access configuration.

## Official Source Content

# Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless

This document describes how to import CSV files from Amazon Simple Storage Service (Amazon S3), Google Cloud Storage (GCS), Azure Blob Storage, or Alibaba Cloud Object Storage Service (OSS) into TiDB Cloud Serverless.
## Limitations

- To ensure data consistency, TiDB Cloud Serverless allows to import CSV files into empty tables only. To import data into an existing table that already contains data, you can use TiDB Cloud Serverless to import the data into a temporary empty table by following this document, and then use the `INSERT SELECT` statement to copy the data to the target existing table.
## Step 1. Prepare the CSV files

1. If a CSV file is larger than 256 MB, consider splitting it into smaller files, each with a size around 256 MB.

    TiDB Cloud Serverless supports importing very large CSV files but performs best with multiple input files around 256 MB in size. This is because TiDB Cloud Serverless can process multiple files in parallel, which can greatly improve the import speed.

2. Name the CSV files as follows:

    - If a CSV file contains all data of an entire table, name the file in the `${db_name}.${table_name}.csv` format, which maps to the `${db_name}.${table_name}` table when you import the data.
    - If the data of one table is separated into multiple CSV files, append a numeric suffix to these CSV files. For example, `${db_name}.${table_name}.000001.csv` and `${db_name}.${table_name}.000002.csv`. The numeric suffixes can be inconsecutive but must be in ascending order. You also need to add extra zeros before the number to ensure all the suffixes are in the same length.
    - TiDB Cloud Serverless supports importing compressed files in the following formats: `.gzip`, `.gz`, `.zstd`, `.zst` and `.snappy`. If you want to import compressed CSV files, name the files in the `${db_name}.${table_name}.${suffix}.csv.${compress}` format, in which `${suffix}` is optional and can be any integer such as '000001'. For example, if you want to import the `trips.000001.csv.gz` file to the `bikeshare.trips` table, you need to rename the file as `bikeshare.trips.000001.csv.gz`.

    > **Note:**
    >
    > - To achieve better performance, it is recommended to limit the size of each compressed file to 100 MiB.
    > - The Snappy compressed file must be in the [official Snappy format](https://github.com/google/snappy). Other variants of Snappy compression are not supported.
    > - For uncompressed files, if you cannot update the CSV filenames according to the preceding rules in some cases (for example, the CSV file links are also used by your other programs), you can keep the filenames unchanged and use the **Mapping Settings** in [Step 4](#step-4-import-csv-files-to-tidb-cloud-serverless) to import your source data to a single target table.
## Step 2. Create the target table schemas

Because CSV files do not contain schema information, before importing data from CSV files into TiDB Cloud Serverless, you need to create the table schemas using either of the following methods:

- Method 1: In TiDB Cloud Serverless, create the target databases and tables for your source data.

- Method 2: In the Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud Object Storage Service directory where the CSV files are located, create the target table schema files for your source data as follows:

    1. Create database schema files for your source data.

        If your CSV files follow the naming rules in [Step 1](#step-1-prepare-the-csv-files), the database schema files are optional for the data import. Otherwise, the database schema files are mandatory.

        Each database schema file must be in the `${db_name}-schema-create.sql` format and contain a `CREATE DATABASE` DDL statement. With this file, TiDB Cloud Serverless will create the `${db_name}` database to store your data when you import the data.

        For example, if you create a `mydb-scehma-create.sql` file that contains the following statement, TiDB Cloud Serverless will create the `mydb` database when you import the data.

        ```sql
        CREATE DATABASE mydb;
        ```

    2. Create table schema files for your source data.

        If you do not include the table schema files in the Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud Object Storage Service directory where the CSV files are located, TiDB Cloud Serverless will not create the corresponding tables for you when you import the data.

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

To allow TiDB Cloud Serverless to access the CSV files in the Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud Object Storage Service bucket, do one of the following:

- If your CSV files are located in Amazon S3, [configure external storage access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-amazon-s3-access).

    You can use either an AWS access key or a Role ARN to access your bucket. Once finished, make a note of the access key (including the access key ID and secret access key) or the Role ARN value as you will need it in [Step 4](#step-4-import-csv-files-to-tidb-cloud-serverless).

- If your CSV files are located in GCS, [configure external storage access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-gcs-access).

- If your CSV files are located in Azure Blob Storage, [configure external storage access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-azure-blob-storage-access).

- If your CSV files are located in Alibaba Cloud Object Storage Service (OSS), [configure external storage access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-alibaba-cloud-object-storage-service-oss-access).
