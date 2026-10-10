# Google Cloud Private Service Connect overview, restrictions, and prerequisites

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud.md`
- Source Title: `Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect`
- Source Heading Path: `Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect | Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Restrictions | Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Set up a private endpoint with Google Cloud Private Service Connect | Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Set up a private endpoint with Google Cloud Private Service Connect > Prerequisites`
- Source Line Ranges: `5-73`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`
- Topic Tags: `private-service-connect`, `private-endpoint`, `restrictions`, `prerequisites`, `iam`, `api-enablement`, `firewall`, `region`, `vpc-peering`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0264_557484ae8c`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-private-endpoint-connections-on-google-cloud.md#connect-to-a-tidb-cloud-dedicated-cluster-via-google-cloud-private-service-connect`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3077b9a07c64ca62d2786ae232ab2fb025ac56801ef34a7f159d2cd321624ce9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud#connect-to-a-tidb-cloud-dedicated-cluster-via-google-cloud-private-service-connect
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the overview, restrictions, prerequisites, or role and API requirements for connecting a TiDB Cloud Dedicated cluster through Google Cloud Private Service Connect.
- Retrieval Keywords: Google Cloud Private Service Connect, private endpoint, TiDB Cloud Dedicated cluster, Restrictions, Prerequisites, Organization Owner, Project Owner, 10 endpoints, same region, egress firewall rules, Compute Engine API, Service Directory API, Cloud DNS API, Compute Network Admin, roles/compute.networkAdmin, Service Directory Editor, roles/servicedirectory.editor, VPC peering, TiCDC, cross-region connection
- Follow-up Guidance: This content also points to the setup flow steps for selecting a TiDB cluster, creating a Google Cloud private endpoint, accepting endpoint access, and connecting to the cluster.
- Classification Note: This is classified as configuration because the content defines eligibility, limits, region and firewall constraints, enabled APIs, and IAM roles required before creating a Google Cloud private endpoint.

## Official Source Content

# Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect

This document describes how to connect to your TiDB Cloud Dedicated cluster via [Private Service Connect](https://cloud.google.com/vpc/docs/private-service-connect). Google Cloud Private Service Connect is a private endpoint service provided by Google Cloud.

> **Tip:**
>
> - To learn how to connect to a TiDB Cloud Dedicated cluster via private endpoint with AWS, see [Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections).
> - To learn how to connect to a TiDB Cloud Dedicated cluster via private endpoint with Azure, see [Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-azure).
> - To learn how to connect to a TiDB Cloud Serverless cluster via private endpoint, see [Connect to TiDB Cloud Serverless via Private Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-serverless).

TiDB Cloud supports highly secure and one-way access to the TiDB Cloud service hosted in a Google Cloud VPC via [Private Service Connect](https://cloud.google.com/vpc/docs/private-service-connect). You can create an endpoint and use it to connect to the TiDB Cloud service .

Powered by Google Cloud Private Service Connect, the endpoint connection is secure and private, and does not expose your data to the public internet. In addition, the endpoint connection supports CIDR overlap and is easier for network management.

The architecture of Google Cloud Private Service Connect is as follows: [^1]

![Private Service Connect architecture](/media/tidb-cloud/google-cloud-psc-endpoint-overview.png)

For more detailed definitions of the private endpoint and endpoint service, see the following Google Cloud documents:

- [Private Service Connect](https://cloud.google.com/vpc/docs/private-service-connect)
- [Access published services through endpoints](https://cloud.google.com/vpc/docs/configure-private-service-connect-services)
## Restrictions

- This feature is applicable to TiDB Cloud Dedicated clusters created after April 13, 2023. For older clusters, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for assistance.
- Only the `Organization Owner` and `Project Owner` roles can create Google Cloud Private Service Connect endpoints.
- Each TiDB cluster can handle connections from up to 10 endpoints.
- Each Google Cloud project can have up to 10 endpoints connecting to a TiDB Cluster.
- You can create up to 8 TiDB Cloud Dedicated clusters hosted on Google Cloud in a project with the endpoint service configured.
- The private endpoint and the TiDB cluster to be connected must be located in the same region.
- Egress firewall rules must permit traffic to the internal IP address of the endpoint. The [implied allow egress firewall rule](https://cloud.google.com/firewall/docs/firewalls#default_firewall_rules) permits egress to any destination IP address.
- If you have created egress deny firewall rules in your VPC network, or if you have created hierarchical firewall policies that modify the implied allowed egress behavior, access to the endpoint might be affected. In this case, you need to create a specific egress allow firewall rule or policy to permit traffic to the internal destination IP address of the endpoint.

In most scenarios, it is recommended that you use private endpoint connection over VPC peering. However, in the following scenarios, you should use VPC peering instead of private endpoint connection:

- You are using a [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview) cluster to replicate data from a source TiDB cluster to a target TiDB cluster across regions, to get high availability. Currently, private endpoint does not support cross-region connection.
- You are using a TiCDC cluster to replicate data to a downstream cluster (such as Amazon Aurora, MySQL, and Kafka) but you cannot maintain the endpoint service of the downstream on your own.
## Set up a private endpoint with Google Cloud Private Service Connect

To connect to your TiDB Cloud Dedicated cluster via a private endpoint, complete the [prerequisites](#prerequisites) and follow these steps:

1. [Select a TiDB cluster](#step-1-select-a-tidb-cluster)
2. [Create a Google Cloud private endpoint](#step-2-create-a-google-cloud-private-endpoint)
3. [Accept endpoint access](#step-3-accept-endpoint-access)
4. [Connect to your TiDB cluster](#step-4-connect-to-your-tidb-cluster)

If you have multiple clusters, you need to repeat these steps for each cluster that you want to connect to using Google Cloud Private Service Connect.
### Prerequisites

Before you begin to create an endpoint:

- [Enable](https://console.cloud.google.com/apis/library/compute.googleapis.com) the following APIs in your Google Cloud project:
    - [Compute Engine API](https://cloud.google.com/compute/docs/reference/rest/v1)
    - [Service Directory API](https://cloud.google.com/service-directory/docs/reference/rest)
    - [Cloud DNS API](https://cloud.google.com/dns/docs/reference/v1)

- Prepare the following [IAM roles](https://cloud.google.com/iam/docs/understanding-roles) with the permissions needed to create an endpoint.

    - Tasks:
        - Create an endpoint
        - Automatically or manually configure [DNS entries](https://cloud.google.com/vpc/docs/configure-private-service-connect-services#dns-endpoint) for an endpoint
    - Required IAM roles:
        - [Compute Network Admin](https://cloud.google.com/iam/docs/understanding-roles#compute.networkAdmin) (roles/compute.networkAdmin)
        - [Service Directory Editor](https://cloud.google.com/iam/docs/understanding-roles#servicedirectory.editor) (roles/servicedirectory.editor)
