# Open Data Migration and configure connections

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md`
- Source Title: `Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 1: Go to the Data Migration page | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 2: Configure the source and target connection`
- Source Line Ranges: `123-167`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`
- Topic Tags: `console`, `migration-job`, `source-connection`, `target-connection`, `public-ip`, `vpc-peering`, `private-link`, `tls`, `validation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0345_0dc097d14a`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md#step-1-go-to-the-data-migration-page`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2e2a63dc17e7ad4be93278010abfadef2ec57cf431d51f370c2742a9348aa216`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration#step-1-go-to-the-data-migration-page
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud console steps to open Data Migration and fill in source and target connection settings for an incremental migration job.
- Retrieval Keywords: TiDB Cloud console, Clusters page, Data > Migration, Create Migration Job, source connection profile, target connection profile, Data source, Region, Connectivity method, Public IP, VPC Peering, Private Link, Hostname or IP address, Service Name, SSL/TLS, Validate Connection and Next, IP Access List, AWS VPC console, Endpoint services
- Follow-up Guidance: After validation, the source notes that Public IP or VPC Peering requires adding Data Migration service IP addresses to the source database IP Access List and firewall, and AWS Private Link requires accepting the endpoint request in the AWS VPC console.
- Classification Note: This is operation content because it gives step-by-step console workflow and connection field setup for creating a migration job.

## Official Source Content

## Step 1: Go to the Data Migration page

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Migration** in the left navigation pane.

3. On the **Data Migration** page, click **Create Migration Job** in the upper-right corner. The **Create Migration Job** page is displayed.
## Step 2: Configure the source and target connection

On the **Create Migration Job** page, configure the source and target connection.

1. Enter a job name, which must start with a letter and must be less than 60 characters. Letters (A-Z, a-z), numbers (0-9), underscores (_), and hyphens (-) are acceptable.

2. Fill in the source connection profile.

   - **Data source**: the data source type.
   - **Region**: the region of the data source, which is required for cloud databases only.
   - **Connectivity method**: the connection method for the data source. Currently, you can choose public IP, VPC Peering, or Private Link according to your connection method.
   - **Hostname or IP address** (for public IP and VPC Peering): the hostname or IP address of the data source.
   - **Service Name** (for Private Link): the endpoint service name.
   - **Port**: the port of the data source.
   - **Username**: the username of the data source.
   - **Password**: the password of the username.
   - **SSL/TLS**: if you enable SSL/TLS, you need to upload the certificates of the data source, including any of the following:
        - only the CA certificate
        - the client certificate and client key
        - the CA certificate, client certificate and client key

3. Fill in the target connection profile.

   - **Username**: enter the username of the target cluster in TiDB Cloud.
   - **Password**: enter the password of the TiDB Cloud username.

4. Click **Validate Connection and Next** to validate the information you have entered.

5. Take action according to the message you see:

    - If you use Public IP or VPC Peering, you need to add the Data Migration service's IP addresses to the IP Access List of your source database and firewall (if any).
    - If you use AWS Private Link, you are prompted to accept the endpoint request. Go to the [AWS VPC console](https://us-west-2.console.aws.amazon.com/vpc/home), and click **Endpoint services** to accept the endpoint request.
