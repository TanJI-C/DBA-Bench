# Configure migration objects, precheck, start, and monitor job

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-mysql-using-data-migration.md`
- Source Title: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 4: Choose the objects to be migrated | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 5: Precheck | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 6: Choose a spec and start migration | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 7: View the migration progress`
- Source Line Ranges: `453-492`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`
- Topic Tags: `object-selection`, `precheck`, `job-specification`, `job-start`, `migration-progress`, `pause`, `resume`, `delete`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0342_9ed4f9e22a`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-mysql-using-data-migration.md#step-4-choose-the-objects-to-be-migrated`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d5d4e5a35b31cd0d863b9bc87731b3ab17c89865fa39728a1609f60bc8cd89cf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#step-4-choose-the-objects-to-be-migrated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB Cloud Data Migration lets you choose migration objects, review Precheck results, select a migration spec, start the job, and view or manage migration progress.
- Retrieval Keywords: Choose Objects to Migrate, All, Customize, Existing data migration, Incremental data migration, Precheck, Failed, Warning, Check again, Migration Task Precheck, Choose a Spec and Start Migration, Create Job and Start, Migration Job Details, Stage and Status, pause, resume, delete, Migration errors and solutions, Precheck errors and solutions
- Follow-up Guidance: If precheck or migration issues occur, the source points to Precheck errors and solutions, Migration Task Precheck, and Migration errors and solutions.
- Classification Note: This is classified as an operation chunk because the content describes the TiDB Cloud console workflow for configuring migration objects, validating with precheck, starting a migration job, and monitoring or managing job status.

## Official Source Content

## Step 4: Choose the objects to be migrated

1. On the **Choose Objects to Migrate** page, select the objects to be migrated. You can click **All** to select all objects, or click **Customize** and then click the checkbox next to the object name to select the object.

    - If you click **All**, the migration job will migrate the existing data from the whole source database instance to TiDB Cloud and migrate ongoing changes after the full migration. Note that it happens only if you have selected the **Existing data migration** and **Incremental data migration** checkboxes in the previous step.
    - If you click **Customize** and select some databases, the migration job will migrate the existing data and migrate ongoing changes of the selected databases to TiDB Cloud. Note that it happens only if you have selected the **Existing data migration** and **Incremental data migration** checkboxes in the previous step.
    - If you click **Customize** and select some tables under a dataset name, the migration job will only migrate the existing data and migrate ongoing changes of the selected tables. Tables created afterwards in the same database will not be migrated.

2. Click **Next**.
## Step 5: Precheck

On the **Precheck** page, you can view the precheck results. If the precheck fails, you need to operate according to **Failed** or **Warning** details, and then click **Check again** to recheck.

If there are only warnings on some check items, you can evaluate the risk and consider whether to ignore the warnings. If all warnings are ignored, the migration job will automatically go on to the next step.

For more information about errors and solutions, see [Precheck errors and solutions](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting#precheck-errors-and-solutions).

For more information about precheck items, see [Migration Task Precheck](https://docs.pingcap.com/tidb/stable/dm-precheck).

If all check items show **Pass**, click **Next**.
## Step 6: Choose a spec and start migration

On the **Choose a Spec and Start Migration** page, select an appropriate migration specification according to your performance requirements. For more information about the specifications, see [Specifications for Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing-dm#specifications-for-data-migration).

After selecting the spec, click **Create Job and Start** to start the migration.
## Step 7: View the migration progress

After the migration job is created, you can view the migration progress on the **Migration Job Details** page. The migration progress is displayed in the **Stage and Status** area.

You can pause or delete a migration job when it is running.

If a migration job has failed, you can resume it after solving the problem.

You can delete a migration job in any status.

If you encounter any problems during the migration, see [Migration errors and solutions](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting#migration-errors-and-solutions).
