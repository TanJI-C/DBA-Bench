# Incremental migration overview and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md`
- Source Title: `Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Limitations`
- Source Line Ranges: `5-36`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`
- Topic Tags: `incremental-migration`, `limitations`, `gtid`, `binlog`, `target-table`, `dml`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0816_a0e81d784d`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md#migrate-only-incremental-data-from-mysql-compatible-databases-to-tidb-cloud-using-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e1ef75e5f52d40f43a9a92812504372247d5d515064f1306cc083abe547020a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration#migrate-only-incremental-data-from-mysql-compatible-databases-to-tidb-cloud-using-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented limitations for migrating only incremental data from a MySQL-compatible source to TiDB Cloud using Data Migration, especially around missing target tables, DELETE or UPDATE replication behavior, and GTID-based start position constraints.
- Retrieval Keywords: incremental data migration limitations, target table not yet created, Error 1146: Table doesn't exist, cannot fetch downstream table schema, DELETE and UPDATE DML operations, GTID mode enabled, MySQL 5.6 or later, InnoDB, REPLICATE CREATE TABLE ... SELECT, secondary database in the upstream
- Follow-up Guidance: The source also points readers to the general limitations in Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration.
- Classification Note: This is reference content because it lists documented scope and failure conditions for incremental migration, including exact error text and GTID-related limitations.

## Official Source Content

# Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration

This document describes how to migrate incremental data from a MySQL-compatible database on a cloud provider (Amazon Aurora MySQL, Amazon Relational Database Service (RDS), Google Cloud SQL for MySQL, or Azure Database for MySQL) or self-hosted source database to TiDB Cloud using the Data Migration feature of the TiDB Cloud console.

For instructions about how to migrate existing data or both existing data and incremental data, see [Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration).
## Limitations

> **Note**:
>
> This section only includes limitations about incremental data migration. It is recommended that you also read the general limitations. See [Limitations](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#limitations).

- If the target table is not yet created in the target database, the migration job will report an error as follows and fail. In this case, you need to manually create the target table and then retry the migration job.

    ```sql
    startLocation: [position: (mysql_bin.000016, 5122), gtid-set:
    00000000-0000-0000-0000-00000000000000000], endLocation:
    [position: (mysql_bin.000016, 5162), gtid-set: 0000000-0000-0000
    0000-0000000000000:0]: cannot fetch downstream table schema of
    zm`.'table1' to initialize upstream schema 'zm'.'table1' in sschema
    tracker Raw Cause: Error 1146: Table 'zm.table1' doesn't exist
    ```

- If some rows are deleted or updated in the upstream and there are no corresponding rows in the downstream, the migration job will detect that there are no rows available for deletion or update when replicating the `DELETE` and `UPDATE` DML operations from the upstream.

If you specify GTID as the start position to migrate incremental data, note the following limitations:

- Make sure that the GTID mode is enabled in the source database.
- If the source database is MySQL, the MySQL version must be 5.6 or later, and the storage engine must be InnoDB.
- If the migration job connects to a secondary database in the upstream, the `REPLICATE CREATE TABLE ... SELECT` events cannot be migrated. This is because the statement will be split into two transactions (`CREATE TABLE` and `INSERT`) that are assigned the same GTID. As a result, the `INSERT` statement will be ignored by the secondary database.
