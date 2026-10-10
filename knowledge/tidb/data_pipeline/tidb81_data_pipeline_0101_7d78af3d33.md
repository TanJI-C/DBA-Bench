# End-to-end AWS DMS procedure to migrate Oracle RDS data into TiDB Cloud Serverless

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-oracle-using-aws-dms.md`
- Source Title: `Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS`
- Source Heading Path: `Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Step 1. Create a VPC | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Step 2. Create an Oracle DB instance | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Step 3. Prepare the table data in Oracle | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Step 4. Create a TiDB Cloud Serverless cluster | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Step 5. Create an AWS DMS replication instance | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Step 6. Create DMS endpoints | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Step 7. Migrate the schema | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Step 8. Create a database migration task | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Step 9. Check data in the downstream TiDB cluster | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Summary | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > See also`
- Source Line Ranges: `45-157`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `aws-dms`, `oracle`, `rds`, `vpc`, `endpoint`, `schema-migration`, `full-load`, `verification`, `cloudwatch`, `serverless`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0101_7d78af3d33`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-oracle-using-aws-dms.md#step-1-create-a-vpc`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `73dfe5423216ee7fc2a167363427a63734cd8bb02ad64d886fab489725a02a25`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-oracle-using-aws-dms#step-1-create-a-vpc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-oracle-using-aws-dms.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the end-to-end AWS DMS workflow for migrating data from an Oracle RDS instance into a TiDB Cloud Serverless cluster, including setup, endpoints, schema handling, migration task creation, verification, and troubleshooting references.
- Retrieval Keywords: Create a VPC, Create an Oracle DB instance, Prepare the table data in Oracle, github_events, GH Archive, table_schema_oracle.sql, oracle_data.sql, Create a TiDB Cloud Serverless cluster, Generate Password, AWS DMS replication instance, dms.t3.large, Create DMS endpoints, Oracle source endpoint, TiDB target endpoint, Migrate the schema, AWS Schema Conversion Tool, AWS SCT, Create a database migration task, Selection rules, Data migration tasks, Table statistics, ADMIN, admin.github_event, CloudWatch, Connect AWS DMS to TiDB Cloud clusters
- Follow-up Guidance: If migration issues or failures occur, the source says you can check the log information in CloudWatch to troubleshoot the issues.
- Classification Note: This chunk is classified as a data pipeline because it provides the sequential migration procedure from source preparation through AWS DMS task execution and downstream data verification.

## Official Source Content

## Step 1. Create a VPC

Log in to the [AWS console](https://console.aws.amazon.com/vpc/home#vpcs:) and create an AWS VPC. You need to create Oracle RDS and DMS instances in this VPC later.

For instructions about how to create a VPC, see [Creating a VPC](https://docs.aws.amazon.com/vpc/latest/userguide/working-with-vpcs.html#Create-VPC).

![Create VPC](/media/tidb-cloud/aws-dms-from-oracle-to-tidb-1.png)
## Step 2. Create an Oracle DB instance

Create an Oracle DB instance in the VPC you just created, and remember the password and grant it public access. You must enable public access to use the AWS Schema Conversion Tool. Note that granting public access in the production environment is not recommended.

For instructions about how to create an Oracle DB instance, see [Creating an Oracle DB instance and connecting to a database on an Oracle DB instance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.CreatingConnecting.Oracle.html).

![Create Oracle RDS](/media/tidb-cloud/aws-dms-from-oracle-to-tidb-2.png)
## Step 3. Prepare the table data in Oracle

Using the following scripts to create and populate 10000 rows of data in the github_events table. You can use the github event dataset and download it from [GH Archive](https://gharchive.org/). It contains 10000 rows of data. Use the following SQL script to execute it in Oracle.

- [table_schema_oracle.sql](https://github.com/pingcap-inc/tidb-integration-script/blob/main/aws-dms/oracle_table_schema.sql)
- [oracle_data.sql](https://github.com/pingcap-inc/tidb-integration-script/blob/main/aws-dms/oracle_data.sql)

After you finish executing the SQL script, check the data in Oracle. The following example uses [DBeaver](https://dbeaver.io/) to query the data:

![Oracle RDS Data](/media/tidb-cloud/aws-dms-from-oracle-to-tidb-3.png)
## Step 4. Create a TiDB Cloud Serverless cluster

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/project/clusters).

2. [Create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-quickstart).

3. In the [**Clusters**](https://tidbcloud.com/project/clusters) page, click the target cluster name to go to its overview page.

4. In the upper-right corner, click **Connect**.

5. Click **Generate Password** to generate a password and copy the generated password.
## Step 5. Create an AWS DMS replication instance

1. Go to the [Replication instances](https://console.aws.amazon.com/dms/v2/home#replicationInstances) page in the AWS DMS console, and switch to the corresponding region.

2. Create an AWS DMS replication instance with `dms.t3.large` in the VPC.

    ![Create AWS DMS Instance](/media/tidb-cloud/aws-dms-from-oracle-to-tidb-8.png)

> **Note:**
>
> For detailed steps on creating an AWS DMS replication instance to work with TiDB Cloud Serverless, see [Connect AWS DMS to TiDB Cloud clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-connect-aws-dms).
## Step 6. Create DMS endpoints

1. In the [AWS DMS console](https://console.aws.amazon.com/dms/v2/home), click the `Endpoints` menu item on the left pane.

2. Create the Oracle source endpoint and the TiDB target endpoint.

    The following screenshot shows the configurations of the source endpoint.

    ![Create AWS DMS Source endpoint](/media/tidb-cloud/aws-dms-from-oracle-to-tidb-9.png)

    The following screenshot shows the configurations of the target endpoint.

    ![Create AWS DMS Target endpoint](/media/tidb-cloud/aws-dms-from-oracle-to-tidb-10.png)

> **Note:**
>
> For detailed steps on creating a TiDB Cloud Serverless DMS endpoint, see [Connect AWS DMS to TiDB Cloud clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-connect-aws-dms).
## Step 7. Migrate the schema

In this example, AWS DMS automatically handles the schema, since the schema definition is simple.

If you decide to migrate schema using the AWS Schema Conversion Tool, see [Installing AWS SCT](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Installing.html#CHAP_Installing.Procedure).

For more information, see [Migrating your source schema to your target database using AWS SCT](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_GettingStarted.SCT.html).
## Step 8. Create a database migration task

1. In the AWS DMS console, go to the [Data migration tasks](https://console.aws.amazon.com/dms/v2/home#tasks) page. Switch to your region. Then click **Create task** in the upper right corner of the window.

    ![Create task](/media/tidb-cloud/aws-dms-to-tidb-cloud-create-task.png)

2. Create a database migration task and specify the **Selection rules**:

    ![Create AWS DMS migration task](/media/tidb-cloud/aws-dms-from-oracle-to-tidb-11.png)

    ![AWS DMS migration task selection rules](/media/tidb-cloud/aws-dms-from-oracle-to-tidb-12.png)

3. Create the task, start it, and then wait for the task to finish.

4. Click the **Table statistics** to check the table. The schema name is `ADMIN`.

    ![Check AWS DMS migration task](/media/tidb-cloud/aws-dms-from-oracle-to-tidb-13.png)
## Step 9. Check data in the downstream TiDB cluster

Connect to the [TiDB Cloud Serverless cluster](https://tidbcloud.com/clusters/create-cluster) and check the `admin.github_event` table data. As shown in the following screenshot, DMS successfully migrated table `github_events` and 10000 rows of data.

![Check Data In TiDB](/media/tidb-cloud/aws-dms-from-oracle-to-tidb-14.png)
## Summary

With AWS DMS, you can successfully migrate data from any upstream AWS RDS database following the example in this document.

If you encounter any issues or failures during the migration, you can check the log information in [CloudWatch](https://console.aws.amazon.com/cloudwatch/home) to troubleshoot the issues.

![Troubleshooting](/media/tidb-cloud/aws-dms-to-tidb-cloud-troubleshooting.png)
## See also

- [Migrate from MySQL-Compatible Databases Using AWS DMS](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-aws-dms)
- [Connect AWS DMS to TiDB Cloud clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-connect-aws-dms)
