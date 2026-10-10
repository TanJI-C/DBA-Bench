# Choose incremental start position and migration objects

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md`
- Source Title: `Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 3: Choose migration job type | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 3: Choose migration job type > The time when the incremental migration job starts | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 3: Choose migration job type > Specify GTID | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 3: Choose migration job type > Specify binlog file name and position | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 4: Choose the objects to be migrated`
- Source Line Ranges: `168-213`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`
- Topic Tags: `incremental-migration`, `start-position`, `gtid`, `binlog-position`, `show-master-status`, `object-selection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0346_fd2dfce817`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md#step-3-choose-migration-job-type`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4da0ccd529f5b55187375d236b963f2b78fa313a13214b31ed498e6a5c545a9f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration#step-3-choose-migration-job-type
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented choices for an incremental migration job start position and how to select migration objects in TiDB Cloud Data Migration.
- Retrieval Keywords: Incremental data migration, Existing data migration, Start Position, The time when the incremental migration job starts, GTID, Binlog file name and position, SHOW MASTER STATUS, binlog.000001, 1307, 3E11FA47-71CA-11E1-9E33-C80AA9429562:1-23, Choose Objects to Migrate, All, Customize
- Follow-up Guidance: The source states that once a migration job starts, you cannot change the start position, and it notes possible conflicts if existing target data does not match the specified binlog position.
- Classification Note: This is operation content because it explains how to choose the migration job type, specify the incremental start position, and select objects to migrate in the workflow.

## Official Source Content

## Step 3: Choose migration job type

To migrate only the incremental data of the source database to TiDB Cloud, select **Incremental data migration** and do not select **Existing data migration**. In this way, the migration job only migrates ongoing changes of the source database to TiDB Cloud.

In the **Start Position** area, you can specify one of the following types of start positions for incremental data migration:

- The time when the incremental migration job starts
- GTID
- Binlog file name and position

Once a migration job starts, you cannot change the start position.
### The time when the incremental migration job starts

If you select this option, the migration job will only migrate the incremental data that is generated in the source database after the migration job starts.
### Specify GTID

Select this option to specify the GTID of the source database, for example, `3E11FA47-71CA-11E1-9E33-C80AA9429562:1-23`. The migration job will replicate the transactions excluding the specified GTID set to migrate ongoing changes of the source database to TiDB Cloud.

You can run the following command to check the GTID of the source database:

```sql
SHOW MASTER STATUS;
```

For information about how to enable GTID, see [Prerequisites](#prerequisites).
### Specify binlog file name and position

Select this option to specify the binlog file name (for example, `binlog.000001`) and binlog position (for example, `1307`) of the source database. The migration job will start from the specified binlog file name and position to migrate ongoing changes of the source database to TiDB Cloud.

You can run the following command to check the binlog file name and position of the source database:

```sql
SHOW MASTER STATUS;
```

If there is data in the target database, make sure the binlog position is correct. Otherwise, there might be conflicts between the existing data and the incremental data. If conflicts occur, the migration job will fail. If you want to replace the conflicted records with data from the source database, you can resume the migration job.
## Step 4: Choose the objects to be migrated

1. On the **Choose Objects to Migrate** page, select the objects to be migrated. You can click **All** to select all objects, or click **Customize** and then click the checkbox next to the object name to select the object.

2. Click **Next**.
