# AWS VPC peering request creation in TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-vpc-peering-connections.md`
- Source Title: `Connect to TiDB Cloud Dedicated via VPC Peering`
- Source Heading Path: `Connect to TiDB Cloud Dedicated via VPC Peering > Set up VPC peering on AWS | Connect to TiDB Cloud Dedicated via VPC Peering > Set up VPC peering on AWS > Step 1. Add VPC peering requests`
- Source Line Ranges: `56-120`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `aws`, `vpc peering`, `networking`, `network access`, `console workflow`, `project-level setup`, `cluster-level setup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0269_a7562118a9`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-vpc-peering-connections.md#set-up-vpc-peering-on-aws`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9c81cdcd1e3688f3b8c3ec9588a481e8afcbcd4500b0baccfb4b81c901d07720`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#set-up-vpc-peering-on-aws
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-vpc-peering-connections.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Cloud console workflow and required AWS VPC fields to create an AWS VPC peering request.
- Retrieval Keywords: Set up VPC peering on AWS, Step 1. Add VPC peering requests, Network Access, VPC Peering, AWS sub-tab, Create VPC Peering, Settings > Networking, Your VPC Region, AWS Account ID, VPC ID, VPC CIDR, System Checking, VPC Peering Details, AWS VPC Peering Details
- Follow-up Guidance: After clicking Create, the newly created VPC peering appears with status System Checking, and you can open its details from the Action column.
- Classification Note: This is classified as configuration because the content provides the console procedures and input fields for creating AWS VPC peering requests at the project level or cluster level.

## Official Source Content

## Set up VPC peering on AWS

This section describes how to set up VPC peering connections on AWS. For Google Cloud, see [Set up VPC peering on Google Cloud](#set-up-vpc-peering-on-google-cloud).
### Step 1. Add VPC peering requests

You can add VPC peering requests on either the project-level **Network Access** page or the cluster-level **Networking** page in the TiDB Cloud console.

<div label="VPC peering setting on the project-level Network Access page">

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Network Access**.
3. On the **Network Access** page, click the **VPC Peering**tab, and then click the **AWS** sub-tab.

    The **VPC Peering** configuration is displayed by default.

4. In the upper-right corner, click **Create VPC Peering**, select the **TiDB Cloud VPC Region**, and then fill in the required information of your existing AWS VPC:

    - Your VPC Region
    - AWS Account ID
    - VPC ID
    - VPC CIDR

    You can get such information from your VPC details page of the [AWS Management Console](https://console.aws.amazon.com/). TiDB Cloud supports creating VPC peerings between VPCs in the same region or from two different regions.

    ![VPC peering](/media/tidb-cloud/vpc-peering/vpc-peering-creating-infos.png)

5. Click **Create** to send the VPC peering request, and then view the VPC peering information on the **VPC Peering** > **AWS** tab. The status of the newly created VPC peering is **System Checking**.

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

3. On the **Networking** page, click **Create VPC Peering**, and then fill in the required information of your existing AWS VPC:

    - Your VPC Region
    - AWS Account ID
    - VPC ID
    - VPC CIDR

    You can get such information from your VPC details page of the [AWS Management Console](https://console.aws.amazon.com/). TiDB Cloud supports creating VPC peerings between VPCs in the same region or from two different regions.

    ![VPC peering](/media/tidb-cloud/vpc-peering/vpc-peering-creating-infos.png)

4. Click **Create** to send the VPC peering request, and then view the VPC peering information on the **Networking** > **AWS VPC Peering** section. The status of the newly created VPC peering is **System Checking**.

5. To view detailed information about your newly created VPC peering, click **...** > **View** in the **Action** column. The **AWS VPC Peering Details** page is displayed.

</div>
