# VPC peering overview and regional CIDR prerequisite

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-vpc-peering-connections.md`
- Source Title: `Connect to TiDB Cloud Dedicated via VPC Peering`
- Source Heading Path: `Connect to TiDB Cloud Dedicated via VPC Peering | Connect to TiDB Cloud Dedicated via VPC Peering > Prerequisite: Set a CIDR for a region`
- Source Line Ranges: `5-55`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `vpc peering`, `network access`, `cidr`, `project settings`, `dedicated cluster`, `aws`, `google cloud`, `prerequisites`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0268_abb3654a13`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-vpc-peering-connections.md#connect-to-tidb-cloud-dedicated-via-vpc-peering`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d43021d0b71452238e2c074c3bd41e23ad497bb6062a8782275123a92d882123`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#connect-to-tidb-cloud-dedicated-via-vpc-peering
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-vpc-peering-connections.md

## Retrieval Guidance

- Use When: Use this chunk when you need the prerequisites and regional CIDR setup details before creating a VPC peering connection for a TiDB Cloud Dedicated cluster.
- Retrieval Keywords: Connect to TiDB Cloud Dedicated via VPC Peering, Prerequisite: Set a CIDR for a region, Project Settings > Network Access, Project CIDR, Create CIDR, Create AWS CIDR, Create Google Cloud CIDR, TiDB Cloud Dedicated, VPC peering, AWS, Google Cloud, CIDR is inactive by default, create an initial TiDB Cloud Dedicated cluster, region CIDR is active
- Follow-up Guidance: After the region CIDR becomes active by creating a cluster in the target region, you can create VPC Peering for the region.
- Classification Note: This is classified as configuration because the content describes project-level network access setup and CIDR configuration required for VPC peering in TiDB Cloud.

## Official Source Content

# Connect to TiDB Cloud Dedicated via VPC Peering

> **Note:**
>
> VPC peering connection is only available for TiDB Cloud Dedicated clusters hosted on AWS and Google Cloud. You cannot use VPC peering to connect to [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted on Azure and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

To connect your application to TiDB Cloud via VPC peering, you need to set up [VPC peering](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#vpc-peering) with TiDB Cloud. This document walks you through setting up VPC peering connections [on AWS](#set-up-vpc-peering-on-aws) and [on Google Cloud](#set-up-vpc-peering-on-google-cloud) and connecting to TiDB Cloud via a VPC peering.

VPC peering connection is a networking connection between two VPCs that enables you to route traffic between them using private IP addresses. Instances in either VPC can communicate with each other as if they are within the same network.

Currently, TiDB clusters of the same project in the same region are created in the same VPC. Therefore, once VPC peering is set up in a region of a project, all the TiDB clusters created in the same region of this project can be connected in your VPC. VPC peering setup differs among cloud providers.

> **Tip:**
>
> To connect your application to TiDB Cloud, you can also set up [private endpoint connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections) with TiDB Cloud, which is secure and private, and does not expose your data to the public internet. It is recommended to use private endpoints over VPC peering connections.
## Prerequisite: Set a CIDR for a region

CIDR (Classless Inter-Domain Routing) is the CIDR block used for creating VPC for TiDB Cloud Dedicated clusters.

Before adding VPC Peering requests to a region, you must set a CIDR for that region and create an initial TiDB Cloud Dedicated cluster in that region. Once the first Dedicated cluster is created, TiDB Cloud will create the VPC of the cluster, allowing you to establish a peering link to your application's VPC.

You can set the CIDR when creating the first TiDB Cloud Dedicated cluster. If you want to set the CIDR before creating the cluster, perform the following operations:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Network Access**.
3. On the **Network Access** page, click the **Project CIDR** tab, and then select **AWS** or **Google Cloud** according to your cloud provider.
4. In the upper-right corner, click **Create CIDR**. Specify the region and CIDR value in the **Create AWS CIDR** or **Create Google Cloud CIDR** dialog, and then click **Confirm**.

    ![Project-CIDR4](/media/tidb-cloud/Project-CIDR4.png)

    > **Note:**
    >
    > - To avoid any conflicts with the CIDR of the VPC where your application is located, you need to set a different project CIDR in this field.
    > - For AWS Region, it is recommended to configure an IP range size between `/16` and `/23`. Supported network addresses include:
    >     - 10.250.0.0 - 10.251.255.255
    >     - 172.16.0.0 - 172.31.255.255
    >     - 192.168.0.0 - 192.168.255.255
    > - For Google Cloud Region, it is recommended to configure an IP range size between `/19` and `/20`. If you want to configure an IP range size between `/16` and `/18`, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support). Supported network addresses include:
    >     - 10.250.0.0 - 10.251.255.255
    >     - 172.16.0.0 - 172.17.255.255
    >     - 172.30.0.0 - 172.31.255.255
    > - TiDB Cloud limits the number of TiDB Cloud nodes in a region of a project based on the CIDR block size of the region.

5. View the CIDR of the cloud provider and the specific region.

    The CIDR is inactive by default. To activate the CIDR, you need to create a cluster in the target region. When the region CIDR is active, you can create VPC Peering for the region.

    ![Project-CIDR2](/media/tidb-cloud/Project-CIDR2.png)
