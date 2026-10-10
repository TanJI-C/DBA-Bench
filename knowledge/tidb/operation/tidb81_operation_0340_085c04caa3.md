# Create AWS DMS replication instance and source endpoint

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-mysql-using-aws-dms.md`
- Source Title: `Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS`
- Source Heading Path: `Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS > Step 1. Create an AWS DMS replication instance | Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS > Step 2. Create the source database endpoint`
- Source Line Ranges: `34-93`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `aws dms`, `replication instance`, `source endpoint`, `amazon rds`, `security group`, `connectivity`, `vpc`, `instance class`, `endpoint test`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0340_085c04caa3`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-mysql-using-aws-dms.md#step-1-create-an-aws-dms-replication-instance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5bb1a0d644fa2c7345cd1cb3a94d5ccb117af4b984d35490c7341d4a22264f07`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-aws-dms#step-1-create-an-aws-dms-replication-instance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-mysql-using-aws-dms.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the documented AWS DMS console setup for creating a replication instance and configuring a source MySQL or Amazon RDS endpoint for migration to TiDB Cloud.
- Retrieval Keywords: Create replication instance, Replication instances, AWS DMS console, us-west-2, dms.t3.large, Engine version, Single-AZ, Multi-AZ, Allocated storage (GiB), Network type - new, IPv4, Virtual private cloud (VPC) for IPv4, Replication subnet group, Public accessible, Create endpoint, source database endpoint, Select RDS DB instance, Source engine MySQL, Provide access information manually, Server name, Port, Username, Password, Secure Socket Layer (SSL) mode, Test endpoint connection, Run test, successful, security group rules, public and private network IP addresses
- Follow-up Guidance: The source says to copy the AWS DMS replication instance public and private network IP addresses, add them to the Amazon RDS security group, and verify the endpoint connection test status is `successful`.
- Classification Note: This chunk is classified as operation because it contains the procedural console steps and configuration fields for creating an AWS DMS replication instance and source endpoint.

## Official Source Content

## Step 1. Create an AWS DMS replication instance

1. Go to the [Replication instances](https://console.aws.amazon.com/dms/v2/home#replicationInstances) page in the AWS DMS console, and switch to the corresponding region. It is recommended to use the same region for AWS DMS as TiDB Cloud. In this document, the upstream and downstream databases and the DMS instance are all in the **us-west-2** region.

2. Click **Create replication instance**.

    ![Create replication instance](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-create-instance.png)

3. Fill in an instance name, ARN, and description.

4. Fill in the instance configuration:
    - **Instance class**: select an appropriate instance class. It is recommended to use `dms.t3.large` or a higher instance class to get better performance.
    - **Engine version**: use the default configuration.
    - **Multi-AZ**: select **Single-AZ** or **Multi-AZ** based on your business needs.

5. Configure the storage in the **Allocated storage (GiB)** field. Use the default configuration.

6. Configure connectivity and security.
    - **Network type - new**: select **IPv4**.
    - **Virtual private cloud (VPC) for IPv4**: select the VPC that you need. It is recommended to use the same VPC as the upstream database to simplify the network configuration.
    - **Replication subnet group**: choose a subnet group for your replication instance.
    - **Public accessible**: use the default configuration.

7. Configure the **Advanced settings**, **Maintenance**, and **Tags** if needed. Click **Create replication instance** to finish the instance creation.
## Step 2. Create the source database endpoint

1. In the [AWS DMS console](https://console.aws.amazon.com/dms/v2/home), click the replication instance that you just created. Copy the public and private network IP addresses as shown in the following screenshot.

    ![Copy the public and private network IP addresses](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-copy-ip.png)

2. Configure the security group rules for Amazon RDS. In this example, add the public and private IP addresses of the AWS DMS instance to the security group.

    ![Configure the security group rules](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-rules.png)

3. Click **Create endpoint** to create the source database endpoint.

    ![Click Create endpoint](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-endpoint.png)

4. In this example, click **Select RDS DB instance** and then select the source RDS instance. If the source database is a self-hosted MySQL, you can skip this step and fill in the information in the following steps.

    ![Select RDS DB instance](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-select-rds.png)

5. Configure the following information:
   - **Endpoint identifier**: create a label for the source endpoint to help you identify it in the subsequent task configuration.
   - **Descriptive Amazon Resource Name (ARN) - optional**: create a friendly name for the default DMS ARN.
   - **Source engine**: select **MySQL**.
   - **Access to endpoint database**: select **Provide access information manually**.
   - **Server name**: fill in the name of the data server for the data provider. You can copy it from the database console. If the upstream is Amazon RDS or Amazon Aurora, the name will be automatically filled in. If it is a self-hosted MySQL without a domain name, you can fill in the IP address.
   - Fill in the source database **Port**, **Username**, and **Password**.
   - **Secure Socket Layer (SSL) mode**: you can enable SSL mode as needed.

    ![Fill in the endpoint configurations](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-endpoint-config.png)

6. Use default values for **Endpoint settings**, **KMS key**, and **Tags**. In the **Test endpoint connection (optional)** section, it is recommended to select the same VPC as the source database to simplify the network configuration. Select the corresponding replication instance, and then click **Run test**. The status needs to be **successful**.

7. Click **Create endpoint**.

    ![Click Create endpoint](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-to-tidb-cloud-connection.png)
