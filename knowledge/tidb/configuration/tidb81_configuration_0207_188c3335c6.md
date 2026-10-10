# Pulsar prerequisites, networking, and topics

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-apache-pulsar.md`
- Source Title: `Sink to Apache Pulsar`
- Source Heading Path: `Sink to Apache Pulsar > Prerequisites | Sink to Apache Pulsar > Prerequisites > Network | Sink to Apache Pulsar > Prerequisites > Create topics in Apache Pulsar`
- Source Line Ranges: `23-81`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `shared`
- Topic Tags: `prerequisites`, `vpc peering`, `public ip`, `dns`, `firewall`, `acl`, `topic creation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0207_188c3335c6`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-apache-pulsar.md#prerequisites`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `db3e76d8e6be5e9226739b5006be0c7e3f7f1b04c6c7a16453ae79b529c8ad5b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-pulsar#prerequisites
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-apache-pulsar.md

## Retrieval Guidance

- Use When: Use this chunk when preparing prerequisites for a TiDB Cloud changefeed to Apache Pulsar, especially network connectivity, ACL authorization, and topic creation requirements.
- Retrieval Keywords: Prerequisites, Network, VPC Peering, Public IP, Pulsar ACL authorization, allowAutoTopicCreation, Create topics in Apache Pulsar, Accepter DNS resolution, security group inbound rules, ingress firewall rules, CIDR of the region, Pulsar brokers, <Topic Prefix><DatabaseName><Separator><TableName><Topic Suffix>, <Topic Prefix><DatabaseName><Topic Suffix>, default topic for non-row events
- Follow-up Guidance: The document next explains how to open the TiDB Cloud console Changefeed page and configure the Pulsar destination connection settings.
- Classification Note: This is configuration content because it defines prerequisite setup for networking and topic naming, including VPC peering, public IP access, DNS resolution, firewall or security group rules, ACL authorization, and manual topic creation.

## Official Source Content

## Prerequisites

Before creating a changefeed to stream data to Apache Pulsar, you need to complete the following prerequisites:

- Set up your network connection
- Add permissions for Pulsar ACL authorization
- Create topics in Apache Pulsar manually, or enable [`allowAutoTopicCreation`](https://pulsar.apache.org/reference/#/4.0.x/config/reference-configuration-broker?id=allowautotopiccreation) in the Apache Pulsar broker configuration
### Network

Ensure that your TiDB cluster can connect to the Apache Pulsar service. You can choose one of the following connection methods:

- VPC Peering: requires network planning to avoid potential VPC CIDR conflicts and consideration of security concerns.
- Public IP: suitable for setup when Pulsar advertises a public IP. This method is not recommended for production environments and requires careful consideration of security concerns.

<div label="VPC Peering">

If your Apache Pulsar service is in an AWS VPC that has no internet access, take the following steps:

1. [Set up a VPC peering connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) between the VPC of the Apache Pulsar service and your TiDB cluster.
2. Modify the inbound rules of the security group that the Apache Pulsar service is associated with.

    You must add the CIDR of the region where your TiDB Cloud cluster is located to the inbound rules. The CIDR can be found on the **VPC Peering** page. Doing so allows the traffic to flow from your TiDB cluster to the Pulsar brokers.

3. If the Apache Pulsar URL contains hostnames, you need to allow TiDB Cloud to resolve the DNS hostnames of the Apache Pulsar brokers.

    1. Follow the steps in [Enable DNS resolution for a VPC peering connection](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-dns.html).
    2. Enable the **Accepter DNS resolution** option.

If your Apache Pulsar service is in a Google Cloud VPC that has no internet access, take the following steps:

1. [Set up a VPC peering connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) between the VPC of the Apache Pulsar service and your TiDB cluster.
2. Modify the ingress firewall rules of the VPC where Apache Pulsar is located.

    You must add the CIDR of the region where your TiDB Cloud cluster is located to the ingress firewall rules. The CIDR can be found on the **VPC Peering** page. Doing so allows the traffic to flow from your TiDB cluster to the Pulsar brokers.

</div>
<div label="Public IP">

If you want to provide Public IP access to your Apache Pulsar service, assign public IP addresses to all your Pulsar brokers. 

It is **NOT** recommended to use Public IP in a production environment. 

</div>
### Create topics in Apache Pulsar

Currently, TiCDC does not automatically create Pulsar topics. You need to create the required topics in Pulsar before creating the changefeed. The number and naming of topics depend on your preferred distribution mode:

- To distribute all Pulsar messages to a single topic: create one topic with your preferred name.
- To distribute Pulsar messages of each table to a dedicated topic, create topics in the `<Topic Prefix><DatabaseName><Separator><TableName><Topic Suffix>` format for each table you want to replicate.
- To distribute Pulsar messages of a database to a dedicated topic, create topics in the `<Topic Prefix><DatabaseName><Topic Suffix>` format for each database you want to replicate.

You might also need a default topic for non-row events (such as schema changes) depending on your configuration.

For more information, see [How to create a topic](https://pulsar.apache.org/docs/4.0.x/tutorials-topic/) in Apache Pulsar documentation.
