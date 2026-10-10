# Target privileges and migration job connection setup

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-mysql-using-data-migration.md`
- Source Title: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > Grant required privileges for migration > Grant required privileges in the target TiDB Cloud cluster | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 1: Go to the Data Migration page | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Step 2: Configure the source and target connections`
- Source Line Ranges: `314-412`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`, `tidb`
- Topic Tags: `privileges`, `target-user`, `migration-job`, `console`, `source-connection`, `target-connection`, `tls`, `public-ip`, `private-link`, `vpc-peering`, `endpoint-approval`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0246_3defd17c26`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-mysql-using-data-migration.md#grant-required-privileges-in-the-target-tidb-cloud-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1476def2942ab0a10c775386908517127349d66f0d2bccdbb058b16505cecf7a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#grant-required-privileges-in-the-target-tidb-cloud-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when you need the required target TiDB Cloud privileges, the Data Migration console path, or the exact source and target connection fields and connectivity methods for creating a migration job.
- Retrieval Keywords: GRANT CREATE, SELECT, INSERT, UPDATE, DELETE, ALTER, DROP, INDEX ON *.* TO 'dm_target_user'@'%';, target TiDB Cloud cluster privileges, Create Migration Job, Data > Migration, source connection profile, target connection profile, Public IP, Private Link, VPC Peering, Endpoint Service Name, com.amazonaws.vpce-svc-xxxxxxxxxxxxxxxxx, Private Endpoint Resource ID, /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.DBforMySQL/flexibleServers/<server>, SSL/TLS, CA Certificate, Client Certificate, Client private key, require_secure_transport = ON, REQUIRE SUBJECT, REQUIRE ISSUER, REQUIRE X509, REQUIRE SSL, Validate Connection and Next, IP Access List, accept the endpoint request, AWS VPC console, Azure portal
- Follow-up Guidance: The chunk also states what to do after connection validation for Public IP, VPC Peering, and Private Link, including adding Data Migration service IP addresses or approving the endpoint request in AWS or Azure.
- Classification Note: This is classified as configuration because the content defines target user privileges and the exact migration job connection settings, including connectivity and TLS options, in TiDB Cloud.

## Official Source Content

#### Grant required privileges in the target TiDB Cloud cluster

For testing purposes, you can use the `root` account of your TiDB Cloud cluster.

For production workloads, it is recommended to have a dedicated user for replication in the target TiDB Cloud cluster and grant only the necessary privileges:

| Privilege | Scope | Purpose |
|:----------|:------|:--------|
| `CREATE` | Databases, Tables | Creates schema objects in the target |
| `SELECT` | Tables | Verifies data during migration |
| `INSERT` | Tables | Writes migrated data |
| `UPDATE` | Tables | Modifies existing rows during incremental replication |
| `DELETE` | Tables | Removes rows during replication or updates |
| `ALTER`  | Tables | Modifies table definitions when schema changes |
| `DROP`   | Databases, Tables | Removes objects during schema sync |
| `INDEX`  | Tables | Creates and modifies indexes |
| `CREATE VIEW`  | View | Create views used by migration |

For example, you can execute the following `GRANT` statement in your target TiDB Cloud cluster to grant corresponding privileges:

```sql
GRANT CREATE, SELECT, INSERT, UPDATE, DELETE, ALTER, DROP, INDEX ON *.* TO 'dm_target_user'@'%';
```
## Step 1: Go to the Data Migration page

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Migration** in the left navigation pane.

3. On the **Data Migration** page, click **Create Migration Job** in the upper-right corner. The **Create Migration Job** page is displayed.
## Step 2: Configure the source and target connections

On the **Create Migration Job** page, configure the source and target connections.

1. Enter a job name, which must start with a letter and must be less than 60 characters. Letters (A-Z, a-z), numbers (0-9), underscores (_), and hyphens (-) are acceptable.

2. Fill in the source connection profile.

    - **Data source**: the data source type.
    - **Connectivity method**: select a connection method for your data source based on your security requirements and cloud provider:
        - **Public IP**: available for all cloud providers (recommended for testing and proof-of-concept migrations).
        - **Private Link**: available for AWS and Azure only (recommended for production workloads requiring private connectivity).
        - **VPC Peering**: available for AWS and Google Cloud only (recommended for production workloads needing low-latency, intra-region connections with non-overlapping VPC/VNet CIDRs).
    - Based on the selected **Connectivity method**, do the following:
        - If **Public IP** or **VPC Peering** is selected, fill in the **Hostname or IP address** field with the hostname or IP address of the data source.
        - If **Private Link** is selected, fill in the following information:
            - **Endpoint Service Name** (available if **Data source** is from AWS): enter the VPC endpoint service name (format: `com.amazonaws.vpce-svc-xxxxxxxxxxxxxxxxx`) that you created for your RDS or Aurora instance.
            - **Private Endpoint Resource ID** (available if **Data source** is from Azure): enter the resource ID of your MySQL Flexible Server instance (format: `/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.DBforMySQL/flexibleServers/<server>`).
    - **Port**: the port of the data source.
    - **User Name**: the username of the data source.
    - **Password**: the password of the username.
    - **SSL/TLS**: enable SSL/TLS for end-to-end data encryption (highly recommended for all migration jobs). Upload the appropriate certificates based on your MySQL server's SSL configuration.

        SSL/TLS configuration options:

        - Option 1: Server authentication only

            - If your MySQL server is configured for server authentication only, upload only the **CA Certificate**.
            - In this option, the MySQL server presents its certificate to prove its identity, and TiDB Cloud verifies the server certificate against the CA.
            - The CA certificate protects against man-in-the-middle attacks and is required if the MySQL server is started with `require_secure_transport = ON`.

        - Option 2: Client certificate authentication

            - If your MySQL server is configured for client certificate authentication, upload **Client Certificate** and  **Client private key**.
            - In this option, TiDB Cloud presents its certificate to the MySQL server for authentication, but TiDB Cloud does not verify the MySQL server's certificate.
            - This option is typically used when the MySQL server is configured with options such as `REQUIRE SUBJECT '...'` or `REQUIRE ISSUER '...'` without `REQUIRE X509`, allowing it to check specific attributes of the client certificate without full CA validation of that client certificate.
            - This option is often used when the MySQL server accepts client certificates in self-signed or custom PKI environments. Note that this configuration is vulnerable to man-in-the-middle attacks and is not recommended for production environments unless other network-level controls guarantee server authenticity.

        - Option 3: Mutual TLS (mTLS) - highest security

            - If your MySQL server is configured for mutual TLS (mTLS) authentication, upload **CA Certificate**, **Client Certificate**, and **Client private key**.
            - In this option, the MySQL server verifies TiDB Cloud's identity using the client certificate, and TiDB Cloud verifies MySQL server's identity using the CA certificate.
            - This option is required when the MySQL server has `REQUIRE X509` or `REQUIRE SSL` configured for the migration user.
            - This option is used when the MySQL server requires client certificates for authentication.
            - You can get the certificates from the following sources:
                - Download from your cloud provider (see [TLS certificate links](#end-to-end-encryption-over-tlsssl)).
                - Use your organization's internal CA certificates.
                - Self-signed certificates (for development/testing only).

3. Fill in the target connection profile.

    - **User Name**: enter the username of the target cluster in TiDB Cloud.
    - **Password**: enter the password of the TiDB Cloud username.

4. Click **Validate Connection and Next** to validate the information you have entered.

5. Take action according to the message you see:

    - If you use **Public IP** or **VPC Peering** as the connectivity method, you need to add the Data Migration service's IP addresses to the IP Access List of your source database and firewall (if any).
    - If you use **Private Link** as the connectivity method, you are prompted to accept the endpoint request:
        - For AWS: go to the [AWS VPC console](https://us-west-2.console.aws.amazon.com/vpc/home), click **Endpoint services**, and accept the endpoint request from TiDB Cloud.
        - For Azure: go to the [Azure portal](https://portal.azure.com), search for your MySQL Flexible Server by name, click **Setting** > **Networking** in the left navigation pane, locate the **Private endpoint** section on the right side, and then approve the pending connection request from TiDB Cloud.
