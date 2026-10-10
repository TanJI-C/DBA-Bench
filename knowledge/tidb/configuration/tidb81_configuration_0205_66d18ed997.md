# Configure Kafka changefeed target by connectivity method

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-apache-kafka.md`
- Source Title: `Sink to Apache Kafka`
- Source Heading Path: `Sink to Apache Kafka > Step 2. Configure the changefeed target`
- Source Line Ranges: `120-202`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `ecosystem`
- Topic Tags: `changefeed`, `kafka`, `connectivity`, `vpc-peering`, `public-ip`, `private-link`, `private-service-connect`, `authentication`, `tls`, `compression`, `endpoint-service`, `bootstrap-ports`, `network-test`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0205_66d18ed997`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-apache-kafka.md#step-2-configure-the-changefeed-target`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d50e64fa11bc92124d962d9572a92c832ec5a7fa12e2c5244cb8d659f0dacabb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka#step-2-configure-the-changefeed-target
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-apache-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when configuring a TiDB Cloud changefeed target for Apache Kafka and the required fields depend on the selected connectivity method such as VPC Peering, Public IP, Private Link, or Private Service Connect.
- Retrieval Keywords: Step 2. Configure the changefeed target, Connectivity Method, VPC Peering, Public IP, Private Link, Private Service Connect, Kafka brokers endpoints, Authentication, Disable, user name, password, Kafka Version, Kafka v2, Compression, TLS Encryption, test the network connection, Endpoint Service Name, Bootstrap Ports, Service Attachment, Alias of Private Link Service, Kafka Advertised Listener Pattern, AWS Principal, Number of AZs, AZ IDs of Kafka Deployment
- Follow-up Guidance: For Private Link and Private Service Connect, after TiDB Cloud creates the endpoint, you must accept the connection request in the cloud provider console and then confirm acceptance in the TiDB Cloud console so TiDB Cloud can test the connection and proceed.
- Classification Note: This chunk is classified as configuration because it lists the changefeed target settings and required inputs for each Kafka connectivity method in TiDB Cloud.

## Official Source Content

## Step 2. Configure the changefeed target

The steps vary depending on the connectivity method you select.

<div label="VPC Peering or Public IP">

1. In **Connectivity Method**, select **VPC Peering** or **Public IP**, fill in your Kafka brokers endpoints. You can use commas `,` to separate multiple endpoints.
2. Select an **Authentication** option according to your Kafka authentication configuration.

    - If your Kafka does not require authentication, keep the default option **Disable**.
    - If your Kafka requires authentication, select the corresponding authentication type, and then fill in the **user name** and **password** of your Kafka account for authentication.

3. Select your **Kafka Version**. If you do not know which one to use, use **Kafka v2**.
4. Select a **Compression** type for the data in this changefeed.
5. Enable the **TLS Encryption** option if your Kafka has enabled TLS encryption and you want to use TLS encryption for the Kafka connection.
6. Click **Next** to test the network connection. If the test succeeds, you will be directed to the next page.

</div>
<div label="Private Link (AWS)">

1. In **Connectivity Method**, select **Private Link**.
2. Authorize the [AWS Principal](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html#principal-accounts) of TiDB Cloud to create an endpoint for your endpoint service. The AWS Principal is provided in the tip on the web page.
3. Make sure you select the same **Number of AZs** and **AZ IDs of Kafka Deployment**, and fill the same unique ID in **Kafka Advertised Listener Pattern** when you [Set Up Self-Hosted Kafka Private Link Service in AWS](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service) in the **Network** section.
4. Fill in the **Endpoint Service Name** which is configured in [Set Up Self-Hosted Kafka Private Link Service in AWS](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service).
5. Fill in the **Bootstrap Ports**. It is recommended that you set at least one port for one AZ. You can use commas `,` to separate multiple ports.
6. Select an **Authentication** option according to your Kafka authentication configuration.

    - If your Kafka does not require authentication, keep the default option **Disable**.
    - If your Kafka requires authentication, select the corresponding authentication type, and then fill in the **user name** and **password** of your Kafka account for authentication.

7. Select your **Kafka Version**. If you do not know which one to use, use **Kafka v2**.
8. Select a **Compression** type for the data in this changefeed.
9. Enable the **TLS Encryption** option if your Kafka has enabled TLS encryption and you want to use TLS encryption for the Kafka connection.
10. Click **Next** to test the network connection. If the test succeeds, you will be directed to the next page.
11. TiDB Cloud creates the endpoint for **Private Link**, which might take several minutes.
12. Once the endpoint is created, log in to your cloud provider console and accept the connection request.
13. Return to the [TiDB Cloud console](https://tidbcloud.com) to confirm that you have accepted the connection request. TiDB Cloud will test the connection and proceed to the next page if the test succeeds.

</div>
<div label="Private Service Connect (Google Cloud)">

1. In **Connectivity Method**, select **Private Service Connect**.    
2. Ensure that you fill in the same unique ID in **Kafka Advertised Listener Pattern** when you [Set Up Self-Hosted Kafka Private Service Connect in Google Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect) in the **Network** section.
3. Fill in the **Service Attachment** that you have configured in [Setup Self Hosted Kafka Private Service Connect in Google Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect)
4. Fill in the **Bootstrap Ports**. It is recommended that you provide more than one port. You can use commas `,` to separate multiple ports. 
5. Select an **Authentication** option according to your Kafka authentication configuration.

    - If your Kafka does not require authentication, keep the default option **Disable**.
    - If your Kafka requires authentication, select the corresponding authentication type, and then fill in the **user name** and **password** of your Kafka account for authentication.

6. Select your **Kafka Version**. If you do not know which one to use, use **Kafka v2**.
7. Select a **Compression** type for the data in this changefeed.
8. Enable the **TLS Encryption** option if your Kafka has enabled TLS encryption and you want to use TLS encryption for the Kafka connection.
9. Click **Next** to test the network connection. If the test succeeds, you will be directed to the next page.
10. TiDB Cloud creates the endpoint for **Private Service Connect**, which might take several minutes.
11. Once the endpoint is created, log in to your cloud provider console and accept the connection request.
12. Return to the [TiDB Cloud console](https://tidbcloud.com) to confirm that you have accepted the connection request. TiDB Cloud will test the connection and proceed to the next page if the test succeeds.

</div>
<div label="Private Link (Azure)">

1. In **Connectivity Method**, select **Private Link**.
2. Authorize the Azure subscription of TiDB Cloud or allow anyone with your alias to access your Private Link service before creating the changefeed. The Azure subscription is provided in the **Reminders before proceeding** tip on the web page. For more information about the visibility of Private Link service, see [Control service exposure](https://learn.microsoft.com/en-us/azure/private-link/private-link-service-overview#control-service-exposure) in Azure documentation.
3. Make sure you fill in the same unique ID in **Kafka Advertised Listener Pattern** when you [Set Up Self-Hosted Kafka Private Link Service in Azure](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service) in the **Network** section.
4. Fill in the **Alias of Private Link Service** which is configured in [Set Up Self-Hosted Kafka Private Link Service in Azure](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service).
5. Fill in the **Bootstrap Ports**. It is recommended that you set at least one port for one AZ. You can use commas `,` to separate multiple ports.
6. Select an **Authentication** option according to your Kafka authentication configuration.

    - If your Kafka does not require authentication, keep the default option **Disable**.
    - If your Kafka requires authentication, select the corresponding authentication type, and then fill in the **user name** and **password** of your Kafka account for authentication.
7. Select your **Kafka Version**. If you do not know which one to use, use **Kafka v2**.
8. Select a **Compression** type for the data in this changefeed.
9. Enable the **TLS Encryption** option if your Kafka has enabled TLS encryption and you want to use TLS encryption for the Kafka connection.
10. Click **Next** to test the network connection. If the test succeeds, you will be directed to the next page.
11. TiDB Cloud creates the endpoint for **Private Link**, which might take several minutes.
12. Once the endpoint is created, log in to the [Azure portal](https://portal.azure.com/) and accept the connection request.
13. Return to the [TiDB Cloud console](https://tidbcloud.com) to confirm that you have accepted the connection request. TiDB Cloud will test the connection and proceed to the next page if the test succeeds.

</div>
