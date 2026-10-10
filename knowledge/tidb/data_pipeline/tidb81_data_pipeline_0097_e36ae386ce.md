# Configure AWS DMS target endpoint and migration task for TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-mysql-using-aws-dms.md`
- Source Title: `Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS`
- Source Heading Path: `Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS > Step 3. Create the target database endpoint | Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS > Step 4. Create a database migration task | Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS > See also`
- Source Line Ranges: `94-188`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `aws dms`, `target endpoint`, `traffic filter`, `ca certificate`, `vpc peering`, `ssl`, `migration task`, `cdc`, `table mappings`, `cloudwatch`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0097_e36ae386ce`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-mysql-using-aws-dms.md#step-3-create-the-target-database-endpoint`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6c223a43358e84aac304d5dae3f03c46999667923bb2d72f971a4288925a4375`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-aws-dms#step-3-create-the-target-database-endpoint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-mysql-using-aws-dms.md

## Retrieval Guidance

- Use When: Use this chunk when configuring AWS DMS to migrate from a MySQL-compatible source to TiDB Cloud and you need the exact target endpoint, SSL, VPC peering, traffic filter, migration task, table mappings, and CloudWatch troubleshooting details.
- Retrieval Keywords: AWS DMS target endpoint, TiDB Cloud traffic filter, public and private network IP addresses, Download CA cert, VPC Peering, Target engine MySQL, Server name -h, Port -P, User name -u, SSL mode Verify-ca, Add new CA certificate, Test endpoint connection successful, Create endpoint, Data migration tasks, Migration type Migrate existing data and replicate ongoing changes, Editing mode Wizard, Target table preparation mode Do nothing, Limited LOB mode, Maximum LOB size 32, Turn on CloudWatch logs, Table mappings, Source name %, system databases mysql sys, task failure, CloudWatch troubleshooting
- Follow-up Guidance: The source also points to related documents for connecting AWS DMS to TiDB Cloud clusters, using Data Migration on TiDB Cloud for MySQL-compatible databases, and migrating from Amazon RDS for Oracle to TiDB Cloud Serverless using AWS DMS.
- Classification Note: This is classified as data_pipeline for cloud because the content describes AWS DMS endpoint and migration task setup between a source database and a TiDB Cloud cluster, including networking, SSL, CDC-style migration selection, table mappings, and task logging.

## Official Source Content

## Step 3. Create the target database endpoint

1. In the [AWS DMS console](https://console.aws.amazon.com/dms/v2/home), click the replication instance that you just created. Copy the public and private network IP addresses as shown in the following screenshot.

    ![Copy the public and private network IP addresses](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-copy-ip.png)

2. In the TiDB Cloud console, go to the [**Clusters**](https://tidbcloud.com/project/clusters) page, click the name of your target cluster, and then click **Connect** in the upper-right corner to get the TiDB Cloud database connection information.

3. Under **Step 1: Create traffic filter** in the dialog, click **Edit**, enter the public and private network IP addresses that you copied from the AWS DMS console, and then click **Update Filter**. It is recommended to add the public IP address and private IP address of the AWS DMS replication instance to the TiDB cluster traffic filter at the same time. Otherwise, AWS DMS might not be able to connect to the TiDB cluster in some scenarios.

4. Click **Download CA cert** to download the CA certificate. Under **Step 3: Connect with a SQL client** in the dialog, take a note of the `-u`, `-h`, and `-P` information in the connection string for later use.

5. Click the **VPC Peering** tab in the dialog, and then click **Add** under **Step 1: Set up VPC** to create a VPC Peering connection for the TiDB cluster and AWS DMS.

6. Configure the corresponding information. See [Set Up VPC Peering Connections](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections).

7. Configure the target endpoint for the TiDB cluster.
    - **Endpoint type**: select **Target endpoint**.
    - **Endpoint identifier**: fill in a name for the endpoint.
    - **Descriptive Amazon Resource Name (ARN) - optional**: create a friendly name for the default DMS ARN.
    - **Target engine**: select **MySQL**.

    ![Configure the target endpoint](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-target-endpoint.png)

8. In the [AWS DMS console](https://console.aws.amazon.com/dms/v2/home), click **Create endpoint** to create the target database endpoint, and then configure the following information:
    - **Server name**: fill in the hostname of your TiDB cluster, which is the `-h` information you have recorded.
    - **Port**: enter the port of your TiDB cluster, which is the `-P` information you have recorded. The default port of a TiDB cluster is 4000.
    - **User name**: enter the user name of your TiDB cluster, which is the `-u` information you have recorded.
    - **Password**: enter the password of your TiDB cluster.
    - **Secure Socket Layer (SSL) mode**: select **Verify-ca**.
    - Click **Add new CA certificate** to import the CA file downloaded from the TiDB Cloud console in the previous steps.

    ![Fill in the target endpoint information](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-target-endpoint2.png)

9. Import the CA file.

    ![Upload CA](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-upload-ca.png)

10. Use the default values for **Endpoint settings**, **KMS key**, and **Tags**. In the **Test endpoint connection (optional)** section, select the same VPC as the source database. Select the corresponding replication instance, and then click **Run test**. The status needs to be **successful**.

11. Click **Create endpoint**.

    ![Click Create endpoint](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-target-endpoint3.png)
## Step 4. Create a database migration task

1. In the AWS DMS console, go to the [Data migration tasks](https://console.aws.amazon.com/dms/v2/home#tasks) page. Switch to your region. Then click **Create task** in the upper-right corner of the window.

    ![Create task](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-create-task.png)

2. Configure the following information:
    - **Task identifier**: fill in a name for the task. It is recommended to use a name that is easy to remember.
    - **Descriptive Amazon Resource Name (ARN) - optional**: create a friendly name for the default DMS ARN.
    - **Replication instance**: select the AWS DMS instance that you just created.
    - **Source database endpoint**: select the source database endpoint that you just created.
    - **Target database endpoint**: select the target database endpoint that you just created.
    - **Migration type**: select a migration type as needed. In this example, select **Migrate existing data and replicate ongoing changes**.

    ![Task configurations](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-task-config.png)

3. Configure the following information:
    - **Editing mode**: select **Wizard**.
    - **Custom CDC stop mode for source transactions**: use the default setting.
    - **Target table preparation mode**: select **Do nothing** or other options as needed. In this example, select **Do nothing**.
    - **Stop task after full load completes**: use the default setting.
    - **Include LOB columns in replication**: select **Limited LOB mode**.
    - **Maximum LOB size in (KB)**: use the default value **32**.
    - **Turn on validation**: select it according to your needs.
    - **Task logs**: select **Turn on CloudWatch logs** for troubleshooting in future. Use the default settings for the related configurations.

    ![Task settings](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-task-settings.png)

4. In the **Table mappings** section, specify the database to be migrated.

    The schema name is the database name in the Amazon RDS instance. The default value of the **Source name** is "%", which means that all databases in the Amazon RDS will be migrated to TiDB. It will cause the system databases such as `mysql` and `sys` in Amazon RDS to be migrated to the TiDB cluster, and result in task failure. Therefore, it is recommended to fill in the specific database name, or filter out all system databases. For example, according to the settings in the following screenshot, only the database named `franktest` and all the tables in that database will be migrated.

    ![Table mappings](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-table-mappings.png)

5. Click **Create task** in the lower-right corner.

6. Go back to the [Data migration tasks](https://console.aws.amazon.com/dms/v2/home#tasks) page. Switch to your region. You can see the status and progress of the task.

    ![Tasks status](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-task-status.png)

If you encounter any issues or failures during the migration, you can check the log information in [CloudWatch](https://console.aws.amazon.com/cloudwatch/home) to troubleshoot the issues.

![Troubleshooting](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-troubleshooting.png)
## See also

- If you want to learn more about how to connect AWS DMS to TiDB Cloud Serverless or TiDB Cloud Dedicated, see [Connect AWS DMS to TiDB Cloud clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-connect-aws-dms).

- If you want to migrate from MySQL-compatible databases, such as Aurora MySQL and Amazon Relational Database Service (RDS), to TiDB Cloud, it is recommended to use [Data Migration on TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration).

- If you want to migrate from Amazon RDS for Oracle to TiDB Cloud Serverless Using AWS DMS, see [Migrate from Amazon RDS for Oracle to TiDB Cloud Serverless Using AWS DMS](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-oracle-using-aws-dms).
