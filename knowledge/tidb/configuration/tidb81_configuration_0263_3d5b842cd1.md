# Azure Private Link setup for TiDB Cloud Dedicated clusters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-private-endpoint-connections-on-azure.md`
- Source Title: `Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link`
- Source Heading Path: `Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link | Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link > Restrictions | Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link > Set up a private endpoint with Azure Private Link | Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link > Set up a private endpoint with Azure Private Link > Step 1. Select a TiDB cluster | Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link > Set up a private endpoint with Azure Private Link > Step 2. Create an Azure private endpoint | Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link > Set up a private endpoint with Azure Private Link > Step 3. Accept the endpoint | Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link > Set up a private endpoint with Azure Private Link > Step 4. Connect to your TiDB cluster | Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link > Set up a private endpoint with Azure Private Link > Private endpoint status reference`
- Source Line Ranges: `5-112`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `azure private link`, `private endpoint`, `networking`, `dedicated cluster`, `endpoint verification`, `connection status`, `region restriction`, `resource id`, `dns ip`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0263_3d5b842cd1`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-private-endpoint-connections-on-azure.md#connect-to-a-tidb-cloud-dedicated-cluster-via-azure-private-link`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3fd6635329ff21bf96355b3ae864505295e63c088ab0c5da6c2db5e9ddbc4619`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-azure#connect-to-a-tidb-cloud-dedicated-cluster-via-azure-private-link
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-private-endpoint-connections-on-azure.md

## Retrieval Guidance

- Use When: Use this when the user needs the setup flow, restrictions, required identifiers, or status meanings for connecting a TiDB Cloud Dedicated cluster via Azure Private Link.
- Retrieval Keywords: Azure Private Link, private endpoint, TiDB Cloud Dedicated cluster, Create Azure Private Endpoint Connection, TiDB Cloud resource ID, Resource ID, DNS configuration, IP address, Verify Endpoint, Accept Endpoint, Settings > Networking, private endpoint status reference, Discovered, Pending, Active, Deleting, Failed, endpoint service status, Creating, same region, Organization Owner, Project Owner
- Follow-up Guidance: The source also provides a private endpoint status reference and endpoint service status meanings on the Networking page.
- Classification Note: This is classified as configuration because the content describes restrictions and the step-by-step procedure to create, verify, accept, and use an Azure private endpoint connection.

## Official Source Content

# Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link

This document describes how to connect to your TiDB Cloud Dedicated cluster via [Azure Private Link](https://learn.microsoft.com/en-us/azure/private-link/private-link-overview).

> **Tip:**
>
> - To learn how to connect to a TiDB Cloud Dedicated cluster via private endpoint with AWS, see [Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections).
> - To learn how to connect to a TiDB Cloud Dedicated cluster via private endpoint with Google Cloud, see [Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud)
> - To learn how to connect to a TiDB Cloud Serverless cluster via private endpoint, see [Connect to TiDB Cloud Serverless via Private Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-serverless).

TiDB Cloud supports highly secure and one-way access to the TiDB Cloud service hosted in an Azure virtual network via [Azure Private Link](https://learn.microsoft.com/en-us/azure/private-link/private-link-overview), as if the service were in your own virtual network. You can create a private endpoint in your virtual network, and then connect to the TiDB Cloud service via the endpoint with permission.

Powered by Azure Private Link, the endpoint connection is secure and private, and does not expose your data to the public internet. In addition, the endpoint connection supports CIDR overlap and is easier for network management.

The architecture of Azure Private Link is as follows: [^1]

![Azure Private Link architecture](/media/tidb-cloud/azure-private-endpoint-arch.png)

For more detailed definitions of the private endpoint and endpoint service, see the following Azure documents:

- [What is Azure Private Link](https://learn.microsoft.com/en-us/azure/private-link/private-link-overview)
- [What is a private endpoint](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview)
- [Create a private endpoint](https://learn.microsoft.com/en-us/azure/private-link/create-private-endpoint-portal?tabs=dynamic-ip)
## Restrictions

- Only the `Organization Owner` and `Project Owner` roles can create private endpoints.
- The private endpoint and the TiDB cluster to be connected must be located in the same region.
## Set up a private endpoint with Azure Private Link

To connect to your TiDB Cloud Dedicated cluster via a private endpoint, complete the following steps:

1. [Select a TiDB cluster](#step-1-select-a-tidb-cluster)
2. [Create an Azure private endpoint](#step-2-create-an-azure-private-endpoint)
3. [Accept the endpoint](#step-3-accept-the-endpoint)
4. [Connect to your TiDB cluster](#step-4-connect-to-your-tidb-cluster)

If you have multiple clusters, you need to repeat these steps for each cluster that you want to connect to using Azure Private Link.
### Step 1. Select a TiDB cluster

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target TiDB cluster to go to its overview page.
2. Click **Connect** in the upper-right corner. A connection dialog is displayed.
3. In the **Connection Type** drop-down list, select **Private Endpoint**, and then click **Create Private Endpoint Connection** to open the **Create Azure Private Endpoint Connection** dialog.

> **Note:**
>
> If you have already created a private endpoint connection, the active endpoint will appear in the connection dialog. To create additional private endpoint connections, navigate to the **Networking** page by clicking **Settings** > **Networking** in the left navigation pane.
### Step 2. Create an Azure private endpoint

1. In the **Create Azure Private Endpoint Connection** dialog, copy the TiDB Cloud resource ID of the private link service and leave the dialog open for later use.

    > **Note:**
    >
    > For each TiDB Cloud Dedicated cluster, the corresponding endpoint service is automatically created 3 to 4 minutes after the cluster creation.

2. Log in to the [Azure portal](https://portal.azure.com/), and then create a private endpoint for your cluster using the copied TiDB Cloud resource ID as follows:

    1. In the Azure portal, search for **Private endpoints**, and then select **Private endpoints** in the result.
    2. On the **Private endpoint** page, click **+ Create**.
    3. In the **Basics** tab, fill in the project and instance information, and then click **Next: Resource**.
    4. In the **Resource** tab, choose **Connect to an Azure resource by resource ID or alias** as the **connection method**, and paste the TiDB Cloud resource ID to the **Resource ID or alias** field.
    5. Continue clicking **Next** to go through the remaining configuration tabs and complete the required settings. Then, click **Create** to create and deploy the private endpoint. It might take a few seconds for Azure to complete the deployment. For more information, see [Create a private endpoint](https://learn.microsoft.com/en-us/azure/private-link/create-private-endpoint-portal?tabs=dynamic-ip#create-a-private-endpoint) in Azure documentation.

3. After the private endpoint is created and deployed, click **Go to resource**, and then do the following:

     - Click **Settings** > **Properties** in the left navigation pane, and copy its **Resource ID** for later use.

         ![Azure private endpoint resource ID](/media/tidb-cloud/azure-private-endpoint-resource-id.png)

     - Click **Settings** > **DNS configuration** in the left navigation pane, and then copy its **IP address** for later use.

         ![Azure private endpoint DNS IP](/media/tidb-cloud/azure-private-endpoint-dns-ip.png)
### Step 3. Accept the endpoint

1. Return to the **Create Azure Private Endpoint Connection** dialog in the TiDB Cloud console, and then paste the copied **Resource ID** and **IP address** into the corresponding fields.
2. Click **Verify Endpoint** to validate the private endpoint access. If you encounter any error, follow the error message for troubleshooting, and then try again.
3. Once verification is successful, click **Accept Endpoint** to approve the connection from your private endpoint.
### Step 4. Connect to your TiDB cluster

After you have accepted the endpoint connection, you are redirected back to the connection dialog.

1. Wait for the private endpoint connection status to become **Active** (approximately 5 minutes). To check the status, navigate to the **Networking** page by clicking **Settings** > **Networking** in the left navigation pane.
2. In the **Connect With** drop-down list, select your preferred connection method. The corresponding connection string is displayed at the bottom of the dialog.
3. Connect to your cluster with the connection string.
### Private endpoint status reference

To view the statuses of private endpoints or private endpoint services, navigate to the **Networking** page by clicking **Settings** > **Networking** in the left navigation pane.

The possible statuses of a private endpoint are explained as follows:

- **Discovered**: TiDB Cloud can automatically detect your private endpoint associated with the endpoint service before accepting the request to prevent the need for creating another one.
- **Pending**: waiting for processing.
- **Active**: your private endpoint is ready to use. You cannot edit the private endpoint of this status.
- **Deleting**: the private endpoint is being deleted.
- **Failed**: the private endpoint creation fails. You can click **Edit** of that row to retry the creation.

The possible statuses of a private endpoint service are explained as follows:

- **Creating**: the endpoint service is being created, which takes 3 to 5 minutes.
- **Active**: the endpoint service is created, no matter whether the private endpoint is created or not.
