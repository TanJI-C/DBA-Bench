# Precheck, start migration, and monitor job progress

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md`
- Source Title: `Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 5: Precheck | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 6: Choose a spec and start migration | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 7: View the migration progress`
- Source Line Ranges: `214-242`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`
- Topic Tags: `precheck`, `warnings`, `migration-spec`, `start-migration`, `job-progress`, `pause`, `resume`, `delete-job`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0347_3fb4b0ff01`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md#step-5-precheck`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2767e593d9648dcbe143607ebbd6a68c82b3a44fb7b70b640a1e0f4c5a27d351`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration#step-5-precheck
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB Cloud Data Migration handles precheck results, starting a migration job after choosing a spec, and viewing or managing job progress on the Migration Job Details page.
- Retrieval Keywords: Precheck page, Failed, Warning, Check again, Pass, Migration Task Precheck, Precheck errors and solutions, Choose a Spec and Start Migration, Specifications for Data Migration, Create Job and Start, Migration Job Details, Stage and Status, pause migration job, resume migration job, delete migration job, Migration errors and solutions, TiDB Cloud Data Migration
- Follow-up Guidance: The source points to Precheck errors and solutions, Migration Task Precheck, Specifications for Data Migration, and Migration errors and solutions for more details.
- Classification Note: This is classified as an operation chunk because the content describes the workflow steps to precheck, start, monitor, pause, resume, and delete a TiDB Cloud migration job.

## Official Source Content

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
