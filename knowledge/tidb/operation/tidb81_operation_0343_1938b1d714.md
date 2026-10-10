# Scale migration job specification

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-mysql-using-data-migration.md`
- Source Title: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Scale a migration job specification | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Scale a migration job specification > Limitations | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Scale a migration job specification > Scaling procedure`
- Source Line Ranges: `493-519`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`
- Topic Tags: `scaling`, `job-specification`, `limitations`, `performance`, `cost`, `restart`, `binlog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0343_1938b1d714`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-mysql-using-data-migration.md#scale-a-migration-job-specification`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3ab588a914318353778ac2d96df688e0cbb81270f1c1e6d930f6a7f25bd6211e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#scale-a-migration-job-specification
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud Data Migration job specification scaling behavior, limitations, and the console steps for Scale Up/Down.
- Retrieval Keywords: Scale a migration job specification, scaling up or down, RCU, existing data migration, incremental migration, Running, Paused, existing data export stage, Scale Up/Down, restart the job, primary key, duplicate data, binary log, expire_logs_days, continuous binary log position, Data > Migration, Action, Submit
- Follow-up Guidance: The source states that scaling takes about 5 to 10 minutes, keeps the old specification if scaling fails, and can be initiated from the Data Migration page through Action > Scale Up/Down.
- Classification Note: This is classified as an operation chunk because the content explains how to change a migration job specification in TiDB Cloud and lists the status restrictions and restart-related limitations of that operation.

## Official Source Content

## Scale a migration job specification

TiDB Cloud supports scaling up or down a migration job specification to meet your performance and cost requirements in different scenarios.

Different migration specifications have different performances. Your performance requirements might vary at different stages as well. For example, during the existing data migration, you want the performance to be as fast as possible, so you choose a migration job with a large specification, such as 8 RCU. Once the existing data migration is completed, the incremental migration does not require such a high performance, so you can scale down the job specification, for example, from 8 RCU to 2 RCU, to save cost.

When scaling a migration job specification, note the following:

- It takes about 5 to 10 minutes to scale a migration job specification.
- If the scaling fails, the job specification remains the same as it was before the scaling.
### Limitations

- You can only scale a migration job specification when the job is in the **Running** or **Paused** status.
- TiDB Cloud does not support scaling a migration job specification during the existing data export stage.
- Scaling a migration job specification will restart the job. If a source table of the job does not have a primary key, duplicate data might be inserted.
- During scaling, do not purge the binary log of the source database or increase `expire_logs_days` of the MySQL source database temporarily. Otherwise, the job might fail because it cannot get the continuous binary log position.
### Scaling procedure

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Migration** in the left navigation pane.

3. On the **Data Migration** page, locate the migration job you want to scale. In the **Action** column, click **...** > **Scale Up/Down**.

4. In the **Scale Up/Down** window, select the new specification you want to use, and then click **Submit**. You can view the new price of the specification at the bottom of the window.
