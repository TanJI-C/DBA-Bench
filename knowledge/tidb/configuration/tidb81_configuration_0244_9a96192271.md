# Network connectivity options for MySQL source migration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-mysql-using-data-migration.md`
- Source Title: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > Ensure network connectivity > End-to-end encryption over TLS/SSL | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > Ensure network connectivity > Public endpoints or IP addresses | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > Ensure network connectivity > Private link or private endpoint | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > Ensure network connectivity > VPC peering`
- Source Line Ranges: `169-290`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`
- Topic Tags: `network-connectivity`, `tls`, `public-endpoints`, `private-endpoint`, `privatelink`, `vpc-peering`, `firewall-rules`, `dns`, `source-database`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0244_9a96192271`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-mysql-using-data-migration.md#end-to-end-encryption-over-tls-ssl`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6ecd4fd2215ac8f5c5c509d7b79eca0c91c95d2f1fe379f805c21bfcdaafad1d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#end-to-end-encryption-over-tls-ssl
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Cloud Data Migration network connectivity prerequisites for a MySQL source, including TLS/SSL, public endpoints, PrivateLink or private endpoint setup, or VPC peering requirements.
- Retrieval Keywords: Data Migration network connectivity, TLS/SSL end-to-end encryption, public endpoints or IP addresses, egress IP addresses, mysql -h <public-host> -P <port> -u <user> -p --ssl-ca=<path-to-provider-ca.pem> -e "SELECT version();", PrivateLink, private endpoint, AWS PrivateLink, Network Load Balancer, endpoint service, com.amazonaws.vpce-svc-xxxxxxxxxxxxxxxxx, Azure PrivateLink, Customer Visible FQDNs, resource ID, /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.DBforMySQL/flexibleServers/<server>, VPC peering, Accepter DNS resolution, Google Cloud VPC network peering, Cloud SQL Auth proxy, firewall rules, security group rules, CIDR of the region where your TiDB Cloud cluster is located
- Follow-up Guidance: The content also states that during DM job setup TiDB Cloud provides egress IP ranges for public access and that pending PrivateLink connection requests from TiDB Cloud must later be approved in AWS or Azure.
- Classification Note: This is classified as configuration because the content defines how to configure source-database network access paths, encryption, DNS, firewall or security-group rules, private endpoint identifiers, and peering prerequisites for TiDB Cloud DM.

## Official Source Content

#### End-to-end encryption over TLS/SSL

Regardless of the connection method, it is strongly recommended to use TLS/SSL for end-to-end encryption. While private endpoints and VPC peering secure the network path, TLS/SSL secures the data itself and helps meet compliance requirements.

<details>
<summary> Download and store the cloud provider's certificates for TLS/SSL encrypted connections </summary>

- Amazon Aurora MySQL or Amazon RDS MySQL: [Using SSL/TLS to encrypt a connection to a DB instance or cluster](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.SSL.html)
- Azure Database for MySQL - Flexible Server: [Connect with encrypted connections](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/how-to-connect-tls-ssl)
- Google Cloud SQL for MySQL: [Manage SSL/TLS certificates](https://cloud.google.com/sql/docs/mysql/manage-ssl-instance)

</details>
#### Public endpoints or IP addresses

When using public endpoints, you can verify network connectivity and access both now and later during the DM job creation process. TiDB Cloud will provide specific egress IP addresses and prompt instructions at that time.

1. Identify and record the source MySQL instance's endpoint hostname (FQDN) or public IP address.
2. Ensure you have the required permissions to modify the firewall or security group rules for your database. Refer to your cloud provider's documentation for guidance as follows:

    - Amazon Aurora MySQL or Amazon RDS MySQL: [Controlling access with security groups](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Overview.RDSSecurityGroups.html).
    - Azure Database for MySQL - Flexible Server: [Public Network Access](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/concepts-networking-public)
    - Google Cloud SQL for MySQL: [Authorized Networks](https://cloud.google.com/sql/docs/mysql/configure-ip#authorized-networks).

3. Optional: Verify connectivity to your source database from a machine with public internet access using the appropriate certificate for in-transit encryption:

    ```shell
    mysql -h <public-host> -P <port> -u <user> -p --ssl-ca=<path-to-provider-ca.pem> -e "SELECT version();"
    ```

4. Later, during the Data Migration job setup, TiDB Cloud will provide an egress IP range. At that time, you need to add this IP range to your database's firewall or security‑group rules following the same procedure above.
#### Private link or private endpoint

If you use a provider-native private link or private endpoint, create a private endpoint for your source MySQL instance (RDS, Aurora, or Azure Database for MySQL).

<details>
<summary> Set up AWS PrivateLink and Private Endpoint for the MySQL source database </summary>

AWS does not support direct PrivateLink access to RDS or Aurora. Therefore, you need to create a Network Load Balancer (NLB) and publish it as an endpoint service associated with your source MySQL instance.

1. In the [Amazon EC2 console](https://console.aws.amazon.com/ec2/), create an NLB in the same subnet(s) as your RDS or Aurora writer. Configure the NLB with a TCP listener on port `3306` that forwards traffic to the database endpoint.

    For detailed instructions, see [Create a Network Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-network-load-balancer.html) in AWS documentation.

2. In the [Amazon VPC console](https://console.aws.amazon.com/vpc/), click **Endpoint Services** in the left navigation pane, and then create an endpoint service. During the setup, select the NLB created in the previous step as the backing load balancer, and enable the **Require acceptance for endpoint** option. After the endpoint service is created, copy the service name (in the `com.amazonaws.vpce-svc-xxxxxxxxxxxxxxxxx` format) for later use.

    For detailed instructions, see [Create an endpoint service](https://docs.aws.amazon.com/vpc/latest/privatelink/create-endpoint-service.html) in AWS documentation.

3. Optional: Test connectivity from a bastion or client inside the same VPC or VNet before starting the migration:

    ```shell
    mysql -h <private‑host> -P 3306 -u <user> -p --ssl-ca=<path-to-provider-ca.pem> -e "SELECT version();"
    ```

4. Later, when configuring TiDB Cloud DM to connect via PrivateLink, you will need to return to the AWS console and approve the pending connection request from TiDB Cloud to this private endpoint.

</details>

<details>
<summary> Set up Azure PrivateLink and private endpoint for the MySQL source database </summary>

Azure Database for MySQL - Flexible Server supports native private endpoints. You can either enable private access (VNet Integration) during MySQL instance creation or add a private endpoint later.

To add a new private endpoint, take the following steps:

1. In the [Azure portal](https://portal.azure.com/), search for and select **Azure Database for MySQL servers**, click your instance name, and then click **Setting** > **Networking** in the left navigation pane.
2. On the **Networking** page, scroll down to the **Private endpoints** section, click **+ Create private endpoint**, and then follow the on-screen instructions to set up the private endpoint.

    During the setup, select the virtual network and subnet that TiDB Cloud can access in the **Virtual Network** tab, and keep **Private DNS integration** enabled in the **DNS** tab. After the private endpoint is created and deployed, click **Go to resource**, click **Settings** > **DNS configuration** in the left navigation pane, and find the hostname to be used to connect with the instance in the **Customer Visible FQDNs** section. Typically, the hostname is in the `<your-instance-name>.mysql.database.azure.com` format.

    For detailed instructions, see [Create a private endpoint via Private Link Center](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/how-to-networking-private-link-portal#create-a-private-endpoint-via-private-link-center) in Azure documentation.

3. Optional: Test connectivity from a bastion or client inside the same VPC or VNet before starting the migration:

    ```shell
    mysql -h <private‑host> -P 3306 -u <user> -p --ssl-ca=<path-to-provider-ca.pem> -e "SELECT version();"
    ```

4. In the [Azure portal](https://portal.azure.com/), return to the overview page of your MySQL Flexible Server instance (not the private endpoint object), click **JSON View** for the **Essentials** section, and then copy the resource ID for later use. The resource ID is in the `/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.DBforMySQL/flexibleServers/<server>` format. You will use this resource ID (not the private endpoint ID) to configure TiDB Cloud DM.

5. Later, when configuring TiDB Cloud DM to connect via PrivateLink, you will need to return to the Azure portal and approve the pending connection request from TiDB Cloud to this private endpoint.

</details>
#### VPC peering

If you use AWS VPC peering or Google Cloud VPC network peering, see the following instructions to configure the network.

<details>
<summary> Set up AWS VPC peering</summary>

If your MySQL service is in an AWS VPC, take the following steps:

1. [Set up a VPC peering connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) between the VPC of the MySQL service and your TiDB cluster.

2. Modify the inbound rules of the security group that the MySQL service is associated with.

    You must add [the CIDR of the region where your TiDB Cloud cluster is located](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#prerequisite-set-a-cidr-for-a-region) to the inbound rules. Doing so allows the traffic to flow from your TiDB cluster to the MySQL instance.

3. If the MySQL URL contains a DNS hostname, you need to allow TiDB Cloud to be able to resolve the hostname of the MySQL service.

    1. Follow the steps in [Enable DNS resolution for a VPC peering connection](https://docs.aws.amazon.com/vpc/latest/peering/modify-peering-connections.html#vpc-peering-dns).
    2. Enable the **Accepter DNS resolution** option.

</details>

<details>
<summary> Set up Google Cloud VPC network peering </summary>

If your MySQL service is in a Google Cloud VPC, take the following steps:

1. If it is a self-hosted MySQL, you can skip this step and proceed to the next step. If your MySQL service is Google Cloud SQL, you must expose a MySQL endpoint in the associated VPC of the Google Cloud SQL instance. You might need to use the [Cloud SQL Auth proxy](https://cloud.google.com/sql/docs/mysql/sql-proxy) developed by Google.

2. [Set up a VPC peering connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) between the VPC of your MySQL service and your TiDB cluster.

3. Modify the ingress firewall rules of the VPC where MySQL is located.

    You must add [the CIDR of the region where your TiDB Cloud cluster is located](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#prerequisite-set-a-cidr-for-a-region) to the ingress firewall rules. This allows the traffic to flow from your TiDB cluster to the MySQL endpoint.

</details>
