# CSV import prerequisites, limitations, schema preparation, and storage access

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-csv-files.md`
- Source Title: `Import CSV Files from Cloud Storage into TiDB Cloud Dedicated`
- Source Heading Path: `Import CSV Files from Cloud Storage into TiDB Cloud Dedicated | Import CSV Files from Cloud Storage into TiDB Cloud Dedicated > Limitations | Import CSV Files from Cloud Storage into TiDB Cloud Dedicated > Step 1. Prepare the CSV files | Import CSV Files from Cloud Storage into TiDB Cloud Dedicated > Step 2. Create the target table schemas | Import CSV Files from Cloud Storage into TiDB Cloud Dedicated > Step 3. Configure cross-account access`
- Source Line Ranges: `6-90`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `csv`, `import`, `cloud-storage`, `s3`, `gcs`, `azure-blob`, `schema-files`, `table-creation`, `naming-rules`, `compression`, `cross-account-access`, `limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0082_e6f8b8f01b`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-csv-files.md#import-csv-files-from-cloud-storage-into-tidb-cloud-dedicated`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `90de338ae8daba2061148749bd07a307099c3f13be8f95e4e7ef696e05f8c04d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files#import-csv-files-from-cloud-storage-into-tidb-cloud-dedicated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-csv-files.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud Dedicated CSV import prerequisites, file naming rules, schema file formats, storage access setup, or documented import limitations for Amazon S3, GCS, or Azure Blob Storage.
- Retrieval Keywords: Import CSV Files from Cloud Storage into TiDB Cloud Dedicated, TiDB Cloud Dedicated, empty tables only, INSERT SELECT, Import Data button will be disabled, changefeed, Point-in-time Restore, physical import mode, CSV files around 256 MB, ${db_name}.${table_name}.csv, ${db_name}.${table_name}.000001.csv, ${db_name}.${table_name}.${suffix}.csv.${compress}, .gzip, .gz, .zstd, .zst, .snappy, official Snappy format, Mapping Settings, ${db_name}-schema-create.sql, CREATE DATABASE, ${db_name}.${table_name}-schema.sql, CREATE TABLE, single DDL statement, cross-account access, AWS access key, Role ARN, configure Amazon S3 access, configure GCS access, configure Azure Blob Storage access
- Follow-up Guidance: The next step referenced by this content is Step 4, where the import uses the saved access credentials or Role ARN and can use Mapping Settings for some uncompressed files with unchanged names.
- Classification Note: This is classified as data_pipeline for the TiDB Cloud component because the content covers importing CSV data into TiDB Cloud Dedicated, including source file preparation, target schema creation, and cloud storage access configuration.

## Official Source Content

# Import CSV Files from Cloud Storage into TiDB Cloud Dedicated

This document describes how to import CSV files from Amazon Simple Storage Service (Amazon S3), Google Cloud Storage (GCS), or Azure Blob Storage into TiDB Cloud Dedicated.
## Limitations

- To ensure data consistency, TiDB Cloud allows to import CSV files into empty tables only. To import data into an existing table that already contains data, you can use TiDB Cloud to import the data into a temporary empty table by following this document, and then use the `INSERT SELECT` statement to copy the data to the target existing table.

- If a TiDB Cloud Dedicated cluster has a [changefeed](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview) or has [Point-in-time Restore](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-point-in-time-restore) enabled, you cannot import data to the cluster (the **Import Data** button will be disabled) because the current data import feature uses the [physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning-physical-import-mode). In this mode, the imported data does not generate change logs, so the changefeed and Point-in-time Restore cannot detect the imported data.
## Step 1. Prepare the CSV files

1. If a CSV file is larger than 256 MB, consider splitting it into smaller files, each with a size of around 256 MB.

    TiDB Cloud supports importing very large CSV files but performs best with multiple input files around 256 MB in size. This is because TiDB Cloud can process multiple files in parallel, which can greatly improve the import speed.

2. Name the CSV files as follows:

    - If a CSV file contains all data of an entire table, name the file in the `${db_name}.${table_name}.csv` format, which maps to the `${db_name}.${table_name}` table when you import the data.
    - If the data of one table is separated into multiple CSV files, append a numeric suffix to these CSV files. For example, `${db_name}.${table_name}.000001.csv` and `${db_name}.${table_name}.000002.csv`. The numeric suffixes can be inconsecutive but must be in ascending order. You also need to add extra zeros before the number to ensure all the suffixes are of the same length.
    - TiDB Cloud supports importing compressed files in the following formats: `.gzip`, `.gz`, `.zstd`, `.zst`, and `.snappy`. If you want to import compressed CSV files, name the files in the `${db_name}.${table_name}.${suffix}.csv.${compress}` format, in which `${suffix}` is optional and can be any integer such as '000001'. For example, if you want to import the `trips.000001.csv.gz` file to the `bikeshare.trips` table, you need to rename the file as `bikeshare.trips.000001.csv.gz`.

    > **Note:**
    >
    > - You only need to compress the data files, not the database or table schema files.
    > - To achieve better performance, it is recommended to limit the size of each compressed file to 100 MiB.
    > - The Snappy compressed file must be in the [official Snappy format](https://github.com/google/snappy). Other variants of Snappy compression are not supported.
    > - For uncompressed files, if you cannot update the CSV filenames according to the preceding rules in some cases (for example, the CSV file links are also used by your other programs), you can keep the filenames unchanged and use the **Mapping Settings** in [Step 4](#step-4-import-csv-files-to-tidb-cloud) to import your source data to a single target table.
## Step 2. Create the target table schemas

Because CSV files do not contain schema information, before importing data from CSV files into TiDB Cloud, you need to create the table schemas using either of the following methods:

- Method 1: In TiDB Cloud, create the target databases and tables for your source data.

- Method 2: In the Amazon S3, GCS, or Azure Blob Storage directory where the CSV files are located, create the target table schema files for your source data as follows:

    1. Create database schema files for your source data.

        If your CSV files follow the naming rules in [Step 1](#step-1-prepare-the-csv-files), the database schema files are optional for the data import. Otherwise, the database schema files are mandatory.

        Each database schema file must be in the `${db_name}-schema-create.sql` format and contain a `CREATE DATABASE` DDL statement. With this file, TiDB Cloud will create the `${db_name}` database to store your data when you import the data.

        For example, if you create a `mydb-scehma-create.sql` file that contains the following statement, TiDB Cloud will create the `mydb` database when you import the data.

        ```sql
        CREATE DATABASE mydb;
        ```

    2. Create table schema files for your source data.

        If you do not include the table schema files in the Amazon S3, GCS, or Azure Blob Storage directory where the CSV files are located, TiDB Cloud will not create the corresponding tables for you when you import the data.

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

To allow TiDB Cloud to access the CSV files in the Amazon S3 bucket, GCS bucket, or Azure Blob Storage container, do one of the following:

- If your CSV files are located in Amazon S3, [configure Amazon S3 access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-amazon-s3-access).

    You can use either an AWS access key or a Role ARN to access your bucket. Once finished, make a note of the access key (including the access key ID and secret access key) or the Role ARN value as you will need it in [Step 4](#step-4-import-csv-files-to-tidb-cloud).

- If your CSV files are located in GCS, [configure GCS access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-gcs-access).

- If your CSV files are located in Azure Blob Storage, [configure Azure Blob Storage access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-azure-blob-storage-access).
