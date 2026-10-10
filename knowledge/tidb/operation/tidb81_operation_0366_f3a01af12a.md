# Create, accept, and use a Google Cloud private endpoint for a TiDB cluster

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud.md`
- Source Title: `Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect`
- Source Heading Path: `Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Set up a private endpoint with Google Cloud Private Service Connect > Step 1. Select a TiDB cluster | Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Set up a private endpoint with Google Cloud Private Service Connect > Step 2. Create a Google Cloud private endpoint | Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Set up a private endpoint with Google Cloud Private Service Connect > Step 3. Accept endpoint access | Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Set up a private endpoint with Google Cloud Private Service Connect > Step 4. Connect to your TiDB cluster | Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Set up a private endpoint with Google Cloud Private Service Connect > Private endpoint status reference`
- Source Line Ranges: `74-131`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `private-endpoint`, `endpoint-creation`, `cluster-selection`, `acceptance`, `connection-string`, `endpoint-status`, `google-cloud-shell`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0366_f3a01af12a`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-private-endpoint-connections-on-google-cloud.md#step-1-select-a-tidb-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0435190efe00001255aa175dc0ec666a48588314878a58d80e9924674438d49e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud#step-1-select-a-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the procedural steps and status meanings for creating, accepting, and using a Google Cloud private endpoint connection to a TiDB cluster.
- Retrieval Keywords: Select a TiDB cluster, Connect, Connection Type, Private Endpoint, Create Private Endpoint Connection, Google Cloud Project ID, Google Cloud VPC Name, Google Cloud Subnet Name, Private Service Connect Endpoint Name, Generate Command, Google Cloud Shell, Accept Endpoint Access, not received connection request from endpoint, System Checking, Active, Connect With, connection string, Pending, Deleting, Failed, Creating, Private endpoint status reference
- Follow-up Guidance: This content also includes the private endpoint and private endpoint service status reference, including Pending, Active, Deleting, Failed, and Creating.
- Classification Note: This is classified as operation because the content provides the step-by-step workflow in the TiDB Cloud console and Google Cloud Shell to create and use the private endpoint connection.

## Official Source Content

### Step 1. Select a TiDB cluster

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target TiDB cluster to go to its overview page. You can select a cluster with any of the following statuses:

    - **Available**
    - **Restoring**
    - **Modifying**
    - **Importing**

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the **Connection Type** drop-down list, select **Private Endpoint**, and then click **Create Private Endpoint Connection**.

    > **Note:**
    >
    > If you have already created a private endpoint connection, the active endpoint will appear in the connection dialog. To create additional private endpoint connections, navigate to the **Networking** page by clicking **Settings** > **Networking** in the left navigation pane.
### Step 2. Create a Google Cloud private endpoint

1. Provide the following information to generate the command for private endpoint creation:
    - **Google Cloud Project ID**: the Project ID associated with your Google Cloud account. You can find the ID on the [Google Cloud **Dashboard** page](https://console.cloud.google.com/home/dashboard).
    - **Google Cloud VPC Name**: the name of the VPC in your specified project. You can find it on the [Google Cloud **VPC networks** page](https://console.cloud.google.com/networking/networks/list).
    - **Google Cloud Subnet Name**: the name of the subnet in the specified VPC. You can find it on the **VPC network details** page.
    - **Private Service Connect Endpoint Name**: enter a unique name for the private endpoint that will be created.
2. After entering the information, click **Generate Command**.
3. Copy the generated command.
4. Open [Google Cloud Shell](https://console.cloud.google.com/home/dashboard) and execute the command to create the private endpoint.
### Step 3. Accept endpoint access

After executing the command in Google Cloud Shell successfully, go back to the TiDB Cloud console and then click **Accept Endpoint Access**.

If you see an error `not received connection request from endpoint`, make sure that you have copied the command correctly and successfully executed it in your Google Cloud Shell.
### Step 4. Connect to your TiDB cluster

After you have accepted the private endpoint connection, you are redirected back to the connection dialog.

1. Wait for the private endpoint connection status to change from **System Checking** to **Active** (approximately 5 minutes).
2. In the **Connect With** drop-down list, select your preferred connection method. The corresponding connection string is displayed at the bottom of the dialog.
3. Connect to your cluster with the connection string.
### Private endpoint status reference

When you use private endpoint connections, the statuses of private endpoints or private endpoint services are displayed on the [**Private Endpoint** page](#prerequisites).

The possible statuses of a private endpoint are explained as follows:

- **Pending**: waiting for processing.
- **Active**: your private endpoint is ready to use. You cannot edit the private endpoint of this status.
- **Deleting**: the private endpoint is being deleted.
- **Failed**: the private endpoint creation fails. You can click **Edit** of that row to retry the creation.

The possible statuses of a private endpoint service are explained as follows:

- **Creating**: the endpoint service is being created, which takes 3 to 5 minutes.
- **Active**: the endpoint service is created, no matter whether the private endpoint is created or not.
