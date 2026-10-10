# Data Migration overview and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-mysql-using-data-migration.md`
- Source Title: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Limitations | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Limitations > Availability | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Limitations > Maximum number of migration jobs | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Limitations > Filtered out and deleted databases | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Limitations > Limitations of existing data migration | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Limitations > Limitations of incremental data migration`
- Source Line Ranges: `6-51`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`, `shared`
- Topic Tags: `migration`, `limitations`, `availability`, `job-limits`, `binlog`, `incremental-replication`, `safe-mode`, `duplicate-keys`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0815_2c0b9a2d0b`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-mysql-using-data-migration.md#migrate-mysql-compatible-databases-to-tidb-cloud-using-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ed40a1418f3b806e21a1e8591e6ec218c1a8f7939d10d64c7d37ce9fbd44b937`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#migrate-mysql-compatible-databases-to-tidb-cloud-using-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB Cloud Data Migration limitations, availability constraints, migration job limits, filtered system databases, or duplicate-key and safe-mode behavior during existing or incremental migration.
- Retrieval Keywords: TiDB Cloud Dedicated, Data Migration availability, maximum number of migration jobs, up to 200 migration jobs for each organization, mysql information_schema performance_schema sys, Amazon Aurora MySQL writer instances, Amazon Aurora MySQL reader instances, existing data migration duplicate keys replaced, incremental data migration duplicate keys error, Restart button, safe mode for 60 seconds, INSERT as REPLACE, UPDATE as DELETE and REPLACE, do not purge binary logs, latency is not 0ms
- Follow-up Guidance: If you only want to replicate ongoing binlog changes, the content points to Migrate Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration.
- Classification Note: This is reference content because it states official limitations, availability, supported migration behaviors, and operational constraints for TiDB Cloud Data Migration.

## Official Source Content

# Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration

This document guides you through migrating your MySQL databases from Amazon Aurora MySQL, Amazon RDS, Azure Database for MySQL - Flexible Server, Google Cloud SQL for MySQL, or self-managed MySQL instances to TiDB Cloud using the Data Migration feature in the [TiDB Cloud console](https://tidbcloud.com/).

This feature enables you to migrate your existing MySQL data and continuously replicate ongoing changes (binlog) from your MySQL-compatible source databases directly to TiDB Cloud, maintaining data consistency whether in the same region or across different regions. The streamlined process eliminates the need for separate dump and load operations, reducing downtime and simplifying your migration from MySQL to a more scalable platform.

If you only want to replicate ongoing binlog changes from your MySQL-compatible database to TiDB Cloud, see [Migrate Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration).
## Limitations
### Availability

- The Data Migration feature is available only for **TiDB Cloud Dedicated** clusters.

- If you don't see the [Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#step-1-go-to-the-data-migration-page) entry for your TiDB Cloud Dedicated cluster in the [TiDB Cloud console](https://tidbcloud.com/), the feature might not be available in your region. To request support for your region, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).

- Amazon Aurora MySQL writer instances support both existing data and incremental data migration. Amazon Aurora MySQL reader instances only support existing data migration and do not support incremental data migration.
### Maximum number of migration jobs

You can create up to 200 migration jobs for each organization. To create more migration jobs, you need to [file a support ticket](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
### Filtered out and deleted databases

- The system databases will be filtered out and not migrated to TiDB Cloud even if you select all of the databases to migrate. That is, `mysql`, `information_schema`, `performance_schema`, and `sys` will not be migrated using this feature.

- When you delete a cluster in TiDB Cloud, all migration jobs in that cluster are automatically deleted and not recoverable.
### Limitations of existing data migration

- During existing data migration, if the target database already contains the table to be migrated and there are duplicate keys, the rows with duplicate keys will be replaced.

- If your dataset size is smaller than 1 TiB, it is recommended that you use logical mode (the default mode). If your dataset size is larger than 1 TiB, or you want to migrate existing data faster, you can use physical mode. For more information, see [Migrate existing data and incremental data](#migrate-existing-data-and-incremental-data).
### Limitations of incremental data migration

- During incremental data migration, if the table to be migrated already exists in the target database with duplicate keys, an error is reported and the migration is interrupted. In this situation, you need to make sure whether the MySQL source data is accurate. If yes, click the "Restart" button of the migration job, and the migration job will replace the target TiDB Cloud cluster's conflicting records with the MySQL source records.

- During incremental replication (migrating ongoing changes to your cluster), if the migration job recovers from an abrupt error, it might open the safe mode for 60 seconds. During the safe mode, `INSERT` statements are migrated as `REPLACE`, `UPDATE` statements as `DELETE` and `REPLACE`, and then these transactions are migrated to the target TiDB Cloud cluster to make sure that all the data during the abrupt error has been migrated smoothly to the target TiDB Cloud cluster. In this scenario, for MySQL source tables without primary keys or non-null unique indexes, some data might be duplicated in the target TiDB Cloud cluster because the data might be inserted repeatedly into the target TiDB Cloud cluster.

- In the following scenarios, if the migration job takes longer than 24 hours, do not purge binary logs in the source database to ensure that Data Migration can get consecutive binary logs for incremental replication:

    - During the existing data migration.
    - After the existing data migration is completed and when incremental data migration is started for the first time, the latency is not 0ms.
