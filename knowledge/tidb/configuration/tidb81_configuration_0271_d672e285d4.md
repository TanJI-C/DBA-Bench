# Google Cloud VPC peering setup and cluster connection

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-vpc-peering-connections.md`
- Source Title: `Connect to TiDB Cloud Dedicated via VPC Peering`
- Source Heading Path: `Connect to TiDB Cloud Dedicated via VPC Peering > Set up VPC peering on Google Cloud | Connect to TiDB Cloud Dedicated via VPC Peering > Set up VPC peering on Google Cloud > Step 1. Add VPC peering requests | Connect to TiDB Cloud Dedicated via VPC Peering > Set up VPC peering on Google Cloud > Step 2. Approve the VPC peering | Connect to TiDB Cloud Dedicated via VPC Peering > Connect to the TiDB cluster`
- Source Line Ranges: `248-333`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `vpc-peering`, `google-cloud`, `gcloud`, `network-access`, `networking`, `cluster-connection`, `connection-string`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0271_d672e285d4`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-vpc-peering-connections.md#set-up-vpc-peering-on-google-cloud`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7c100e5e092bd60812fe0dd299e09f426c1a27f029e8a8cbf3120c02e1a53d38`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#set-up-vpc-peering-on-google-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-vpc-peering-connections.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Google Cloud procedure to create and approve TiDB Cloud VPC peering and then obtain the VPC Peering connection string to connect to the cluster.
- Retrieval Keywords: Google Cloud VPC peering, Network Access, Networking, Create VPC Peering, Google Cloud Project ID, VPC Network Name, VPC CIDR, System Checking, Google Cloud VPC Peering Details, gcloud beta compute networks peerings create, --peer-project <tidb-project-id>, --peer-network <tidb-vpc-network-name>, Connect to the TiDB cluster, Connection Type, VPC Peering, Connect With, connection string, active
- Follow-up Guidance: After the VPC peering is set up, the source says to wait for the status to change from system checking to active, then select VPC Peering in the Connect dialog and use the displayed connection string.
- Classification Note: This chunk is classified as configuration because it provides the TiDB Cloud console fields and the gcloud command used to create and approve Google Cloud VPC peering, plus the connection dialog steps.

## Official Source Content

## Set up VPC peering on Google Cloud
### Step 1. Add VPC peering requests

You can add VPC peering requests on either the project-level **Network Access** page or the cluster-level **Networking** page in the TiDB Cloud console.

<div label="VPC peering setting on the project-level Network Access page">

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Network Access**.
3. On the **Network Access** page, click the **VPC Peering** tab, and then click the **Google Cloud** sub-tab.

    The **VPC Peering** configuration is displayed by default.

4. In the upper-right corner, click **Create VPC Peering**, select the **TiDB Cloud VPC Region**, and then fill in the required information of your existing Google Cloud VPC:

    > **Tip:**
    >
    > You can follow instructions next to the **Google Cloud Project ID** and **VPC Network Name** fields to find the project ID and VPC network name.

    - Google Cloud Project ID
    - VPC Network Name
    - VPC CIDR

5. Click **Create** to send the VPC peering request, and then view the VPC peering information on the **VPC Peering** > **Google Cloud** tab. The status of the newly created VPC peering is **System Checking**.

6. To view detailed information about your newly created VPC peering, click **...** > **View** in the **Action** column. The **VPC Peering Details** page is displayed.

</div>
<div label="VPC peering setting on the cluster-level Networking page">

1. Open the overview page of the target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page.

2. In the left navigation pane, click **Settings** > **Networking**.

3. On the **Networking** page, click **Create VPC Peering**, and then fill in the required information of your existing Google Cloud VPC:

    > **Tip:**
    >
    > You can follow instructions next to the **Google Cloud Project ID** and **VPC Network Name** fields to find the project ID and VPC network name.

    - Google Cloud Project ID
    - VPC Network Name
    - VPC CIDR

4. Click **Create** to send the VPC peering request, and then view the VPC peering information on the **Networking** > **Google Cloud VPC Peering** section. The status of the newly created VPC peering is **System Checking**.

5. To view detailed information about your newly created VPC peering, click **...** > **View** in the **Action** column. The **Google Cloud VPC Peering Details** page is displayed.

</div>
### Step 2. Approve the VPC peering

Execute the following command to finish the setup of VPC peering:

```bash
gcloud beta compute networks peerings create <your-peer-name> --project <your-project-id> --network <your-vpc-network-name> --peer-project <tidb-project-id> --peer-network <tidb-vpc-network-name>
```

> **Note:**
>
> You can name `<your-peer-name>` as you like.

Now you have successfully set up the VPC peering connection. Next, [connect to the TiDB cluster via VPC peering](#connect-to-the-tidb-cluster).
## Connect to the TiDB cluster

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner, and select **VPC Peering** from the **Connection Type** drop-down list.

    Wait for the VPC peering connection status to change from **system checking** to **active** (approximately 5 minutes).

3. In the **Connect With** drop-down list, select your preferred connection method. The corresponding connection string is displayed at the bottom of the dialog.

4. Connect to your cluster with the connection string.
