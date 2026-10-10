# TiDB Cloud migration and import overview

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-migration-overview.md`
- Source Title: `Migration and Import Overview`
- Source Heading Path: `Migration and Import Overview | Migration and Import Overview > Migrate data from MySQL-Compatible databases | Migration and Import Overview > Import data from files to TiDB Cloud | Migration and Import Overview > Reference | Migration and Import Overview > Reference > Configure cloud storage access | Migration and Import Overview > Reference > Naming conventions for data import | Migration and Import Overview > Reference > Troubleshoot access denied errors during data import from Amazon S3`
- Source Line Ranges: `6-66`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`, `dumpling`, `ticdc`, `ecosystem`
- Topic Tags: `migration`, `import`, `mysql-compatible`, `aws-dms`, `sharding`, `cloud-storage`, `csv`, `parquet`, `sql-files`, `aurora-snapshot`, `naming-conventions`, `s3-troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0107_ef6803c9fa`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-migration-overview.md#migration-and-import-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `299356d5f273963df83c156d267a46bedda5bb35fc53898564add69f138995ce`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-migration-overview#migration-and-import-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-migration-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants an overview of TiDB Cloud migration or import paths, including MySQL-compatible database migration, AWS DMS for heterogeneous databases, shard merge, TiDB Self-Managed migration, or file import from local files and cloud storage.
- Retrieval Keywords: TiDB Cloud migration and import overview, Data Migration, MySQL-compatible databases, AWS DMS, AWS Database Migration Service, PostgreSQL, Oracle, SQL Server, Migrate and merge MySQL shards, TiDB Self-Managed, Dumpling, TiCDC, Import local CSV file to TiDB Cloud, Import sample data, SQL file, CSV, Parquet, Aurora Snapshot, Amazon S3, Google Cloud Storage, GCS, Azure Blob Storage, Configure cloud storage access, Naming conventions for data import, Troubleshoot access denied errors during data import from Amazon S3
- Follow-up Guidance: The document points to related references for configuring external storage access, naming conventions for data import, and troubleshooting Amazon S3 access denied errors.
- Classification Note: This chunk is classified as data_pipeline for the TiDB Cloud component because it summarizes migration and import scenarios, supported source types, and related data movement methods in TiDB Cloud.

## Official Source Content

# Migration and Import Overview

You can migrate data from a wide variety of data sources to TiDB Cloud. This document gives an overview of the data migration scenarios.
## Migrate data from MySQL-Compatible databases

When you migrate data from a MySQL-compatible database, you can perform full data migration and incremental data migration. The migration scenarios and methods are as follows:

- Migrate MySQL-compatible databases using Data Migration

    TiDB is highly compatible with MySQL. You can use Data Migration in the TiDB Cloud console to migrate data from any MySQL-compatible databases to TiDB Cloud smoothly. For more information, see [Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration).

- Migrate using AWS DMS

    If you want to migrate heterogeneous databases, such as PostgreSQL, Oracle, and SQL Server to TiDB Cloud, it is recommended to use AWS Database Migration Service (AWS DMS).

    - [Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-aws-dms)
    - [Migrate from Amazon RDS for Oracle Using AWS DMS](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-oracle-using-aws-dms)

- Migrate and merge MySQL shards

    If your application uses MySQL shards for data storage, you can migrate these shards into TiDB Cloud as one table. For more information, see [Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-sql-shards).

- Migrate from TiDB Self-Managed

    You can migrate data from your TiDB Self-Managed clusters to TiDB Cloud (AWS) through Dumpling and TiCDC. For more information, see [Migrate from TiDB Self-Managed to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-op-tidb).
## Import data from files to TiDB Cloud

If you have data files in SQL, CSV, Parquet, or Aurora Snapshot formats, you can import these files to TiDB Cloud in one go. The import scenarios and methods are as follows:

- Import a local CSV file to TiDB Cloud

    You can import a local CSV file to TiDB Cloud. For more information, see [Import Local Files to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-import-local-files).

- Import sample data (SQL file) to TiDB Cloud

    You can import sample data (SQL file) to TiDB Cloud to quickly get familiar with the TiDB Cloud interface and the import process. For more information, see [Import Sample Data to TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-sample-data-serverless) and [Import Sample Data to TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-sample-data).

- Import CSV files from Amazon S3, Google Cloud Storage (GCS), or Azure Blob Storage into TiDB Cloud

    You can import CSV files from Amazon S3, Google Cloud Storage (GCS), or Azure Blob Storage into TiDB Cloud. For more information, see [Import CSV Files from Cloud Storage into TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files-serverless) and [Import CSV Files from Cloud Storage into TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files).

- Import Apache Parquet files from Amazon S3, Google Cloud Storage (GCS), or Azure Blob Storage into TiDB Cloud

    You can import Parquet files from Amazon S3, Google Cloud Storage (GCS), or Azure Blob Storage into TiDB Cloud. For more information, see [Import Apache Parquet Files from Cloud Storage into TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files-serverless) and [Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files).
## Reference
### Configure cloud storage access

If your source data is stored in Amazon S3, Google Cloud Storage (GCS) buckets, or Azure Blob Storage containers, before importing or migrating the data to TiDB Cloud, you need to configure access to the storage. For more information, see [Configure External Storage Access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage) and [Configure External Storage Access for TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage).
### Naming conventions for data import

To make sure that your data can be imported successfully, you need to prepare schema files and data files that conform to the naming conventions. For more information, see [Naming Conventions for Data Import](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import).
### Troubleshoot access denied errors during data import from Amazon S3

You can troubleshoot access denied errors that might occur when you import data from Amazon S3 into TiDB Cloud. For more information, see [Troubleshoot Access Denied Errors during Data Import from Amazon S3](https://docs.pingcap.com/tidb/stable/tidb-cloud/troubleshoot-import-access-denied-error).
