# AWS PrivateLink overview, restrictions, prerequisites, and cluster selection

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-private-endpoint-connections.md`
- Source Title: `Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink`
- Source Heading Path: `Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink | Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink > Restrictions | Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink > Prerequisites | Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink > Set up a private endpoint connection and connect to your cluster | Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink > Set up a private endpoint connection and connect to your cluster > Step 1. Select a TiDB cluster`
- Source Line Ranges: `5-65`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `pd`, `tikv`
- Topic Tags: `aws`, `privatelink`, `private-endpoint`, `restrictions`, `prerequisites`, `dns`, `vpc`, `cluster-selection`, `networking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0266_2b0a40b038`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-private-endpoint-connections.md#connect-to-a-tidb-cloud-dedicated-cluster-via-aws-privatelink`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bf32ffe842b73815816210c81fdddfeb4fa6c11c570e0938df827cbb8f41e86f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections#connect-to-a-tidb-cloud-dedicated-cluster-via-aws-privatelink
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-private-endpoint-connections.md

## Retrieval Guidance

- Use When: Use this chunk when you need the AWS PrivateLink overview for TiDB Cloud Dedicated, including restrictions, prerequisites, and how to start by selecting a cluster for a private endpoint connection.
- Retrieval Keywords: AWS PrivateLink, private endpoint, TiDB Cloud Dedicated cluster, Restrictions, Prerequisites, DNS hostnames, DNS resolution, same region, Organization Owner, Project Owner, TiCDC, cross-region connection, VPC peering, PD, TiKV, Connection Type, Create Private Endpoint Connection, Settings > Networking
- Follow-up Guidance: It points to the next setup steps after cluster selection: create an AWS interface endpoint, create a private endpoint connection, enable private DNS, and connect to your TiDB cluster.
- Classification Note: This is classified as configuration because the content defines required roles, regional and networking prerequisites, unsupported scenarios, and the console path to initiate a private endpoint connection.

## Official Source Content

# Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink

This document describes how to connect to your TiDB Cloud Dedicated cluster via [AWS PrivateLink](https://aws.amazon.com/privatelink).

> **Tip:**
>
> - To learn how to connect to a TiDB Cloud Serverless cluster via private endpoint, see [Connect to TiDB Cloud Serverless via Private Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-serverless).
> - To learn how to connect to a TiDB Cloud Dedicated cluster via private endpoint with Azure, see [Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-azure).
> - To learn how to connect to a TiDB Cloud Dedicated cluster via private endpoint with Google Cloud, see [Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud).

TiDB Cloud supports highly secure and one-way access to the TiDB Cloud service hosted in an AWS VPC via [AWS PrivateLink](https://aws.amazon.com/privatelink), as if the service were in your own VPC. A private endpoint is exposed in your VPC and you can create a connection to the TiDB Cloud service via the endpoint with permission.

Powered by AWS PrivateLink, the endpoint connection is secure and private, and does not expose your data to the public internet. In addition, the endpoint connection supports CIDR overlap and is easier for network management.

The architecture of the private endpoint is as follows:

![Private endpoint architecture](/media/tidb-cloud/aws-private-endpoint-arch.png)

For more detailed definitions of the private endpoint and endpoint service, see the following AWS documents:

- [What is AWS PrivateLink?](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html)
- [AWS PrivateLink concepts](https://docs.aws.amazon.com/vpc/latest/privatelink/concepts.html)
## Restrictions

- Only the `Organization Owner` and the `Project Owner` roles can create private endpoints.
- The private endpoint and the TiDB cluster to be connected must be located in the same region.

In most scenarios, you are recommended to use private endpoint connection over VPC peering. However, in the following scenarios, you should use VPC peering instead of private endpoint connection:

- You are using a [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview) cluster to replicate data from a source TiDB cluster to a target TiDB cluster across regions, to get high availability. Currently, private endpoint does not support cross-region connection.
- You are using a TiCDC cluster to replicate data to a downstream cluster (such as Amazon Aurora, MySQL, and Kafka) but you cannot maintain the endpoint service on your own.
- You are connecting to PD or TiKV nodes directly.
## Prerequisites

Make sure that DNS hostnames and DNS resolution are both enabled in your AWS VPC settings. They are disabled by default when you create a VPC in the [AWS Management Console](https://console.aws.amazon.com/).
## Set up a private endpoint connection and connect to your cluster

To connect to your TiDB Cloud Dedicated cluster via a private endpoint, complete the follow these steps:

1. [Select a TiDB cluster](#step-1-select-a-tidb-cluster)
2. [Create an AWS interface endpoint](#step-2-create-an-aws-interface-endpoint)
3. [Create a private endpoint connection](#step-3-create-a-private-endpoint-connection)
4. [Enable private DNS](#step-4-enable-private-dns)
5. [Connect to your TiDB cluster](#step-5-connect-to-your-tidb-cluster)

If you have multiple clusters, you need to repeat these steps for each cluster that you want to connect to using AWS PrivateLink.
### Step 1. Select a TiDB cluster

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target TiDB cluster to go to its overview page.
2. Click **Connect** in the upper-right corner. A connection dialog is displayed.
3. In the **Connection Type** drop-down list, select **Private Endpoint**, and then click **Create Private Endpoint Connection**.

> **Note:**
>
> If you have already created a private endpoint connection, the active endpoint will appear in the connection dialog. To create additional private endpoint connections, navigate to the **Networking** page by clicking **Settings** > **Networking** in the left navigation pane.
