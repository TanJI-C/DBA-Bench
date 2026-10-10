# Choose migration job type and mode

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-mysql-using-data-migration.md`
- Source Title: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 3: Choose migration job type | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 3: Choose migration job type > Migrate existing data and incremental data | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 3: Choose migration job type > Migrate only existing data | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 3: Choose migration job type > Migrate only incremental data`
- Source Line Ranges: `413-452`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`, `tikv`
- Topic Tags: `job-type`, `existing-data`, `incremental-data`, `logical-mode`, `physical-mode`, `performance`, `pitr`, `changefeed`, `empty-target-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0341_258c470df4`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-mysql-using-data-migration.md#step-3-choose-migration-job-type`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `aa64f8efea0a3dd21592cf4032f6912750381c602a0af16cd31407abf6d6b0cc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#step-3-choose-migration-job-type
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when you need to choose a Data Migration job type or compare logical mode and physical mode for existing data and incremental data migration in TiDB Cloud.
- Retrieval Keywords: Choose migration job type, Existing data migration, Incremental data migration, logical mode, physical mode, target tables to be empty before migration, cannot create a second migration job or import task, PITR, Point-in-time Recovery, changefeed, writing directly to TiKV, 16 RCUs, 2 RCUs, 4 RCUs, 8 RCUs, performance regression of the MySQL source database, Maximum export speed, Migrate only existing data, Migrate only incremental data
- Follow-up Guidance: The chunk also links to detailed instructions for migrating only incremental data from MySQL-compatible databases to TiDB Cloud using Data Migration.
- Classification Note: This is classified as operation because the content describes selecting migration job types and runtime migration modes, along with their constraints and performance characteristics.

## Official Source Content

## Step 3: Choose migration job type

In the **Choose the objects to be migrated** step, you can choose existing data migration, incremental data migration, or both.
### Migrate existing data and incremental data

To migrate data to TiDB Cloud once and for all, choose both **Existing data migration** and **Incremental data migration**, which ensures data consistency between the source and target databases.

You can use **physical mode** or **logical mode** to migrate **existing data** and **incremental data**.

- The default mode is **logical mode**. This mode exports data from MySQL source databases as SQL statements and then executes them on TiDB. In this mode, the target tables before migration can be either empty or non-empty. But the performance is slower than physical mode.

- For large datasets, it is recommended to use **physical mode**. This mode exports data from MySQL source databases and encodes it as KV pairs, writing directly to TiKV to achieve faster performance. This mode requires the target tables to be empty before migration. For the specification of 16 RCUs (Replication Capacity Units), the performance is about 2.5 times faster than logical mode. The performance of other specifications can increase by 20% to 50% compared with logical mode. Note that the performance data is for reference only and might vary in different scenarios.

> **Note:**
>
> - When you use physical mode, you cannot create a second migration job or import task for the TiDB cluster before the existing data migration is completed.
> - When you use physical mode and the migration job has started, do **NOT** enable PITR (Point-in-time Recovery) or have any changefeed on the cluster. Otherwise, the migration job will be stuck. If you need to enable PITR or have any changefeed, use logical mode instead to migrate data.

Physical mode exports the MySQL source data as fast as possible, so [different specifications](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing-dm#specifications-for-data-migration) have different performance impacts on QPS and TPS of the MySQL source database during data export. The following table shows the performance regression of each specification.

| Migration specification |  Maximum export speed | Performance regression of the MySQL source database |
|---------|-------------|--------|
| 2 RCUs   | 80.84 MiB/s  | 15.6% |
| 4 RCUs   | 214.2 MiB/s  | 20.0% |
| 8 RCUs   | 365.5 MiB/s  | 28.9% |
| 16 RCUs | 424.6 MiB/s  | 46.7% |
### Migrate only existing data

To migrate only existing data of the source database to TiDB Cloud, choose **Existing data migration**.

You can only use logical mode to migrate existing data. For more information, see [Migrate existing data and incremental data](#migrate-existing-data-and-incremental-data).
### Migrate only incremental data

To migrate only the incremental data of the source database to TiDB Cloud, choose **Incremental data migration**. In this case, the migration job does not migrate the existing data of the source database to TiDB Cloud, but only migrates the ongoing changes of the source database that are explicitly specified by the migration job.

For detailed instructions about incremental data migration, see [Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration).
