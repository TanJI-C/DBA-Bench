# Kafka changefeed overview, restrictions, prerequisites, and access setup

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-apache-kafka.md`
- Source Title: `Sink to Apache Kafka`
- Source Heading Path: `Sink to Apache Kafka | Sink to Apache Kafka > Restrictions | Sink to Apache Kafka > Prerequisites | Sink to Apache Kafka > Prerequisites > Network | Sink to Apache Kafka > Prerequisites > Kafka ACL authorization | Sink to Apache Kafka > Step 1. Open the Changefeed page for Apache Kafka`
- Source Line Ranges: `5-119`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `ecosystem`
- Topic Tags: `changefeed`, `kafka`, `restrictions`, `prerequisites`, `network`, `private-connect`, `vpc-peering`, `public-ip`, `acl`, `permissions`, `console`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0204_056f5155e2`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-apache-kafka.md#sink-to-apache-kafka`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ad8beade9060c4b8086eee6bd2f11cdd803f5ad6dea705abb3cd95623afd7f50`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka#sink-to-apache-kafka
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-apache-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the overview, restrictions, prerequisites, network connectivity options, Kafka ACL permissions, or console entry path for creating a TiDB Cloud changefeed to Apache Kafka.
- Retrieval Keywords: Sink to Apache Kafka, TiDB Cloud changefeed to Apache Kafka, Restrictions, Prerequisites, Network, Private Connect, Private Link, Private Service Connect, VPC Peering, Public IP, Kafka ACL authorization, Create permission, Write permission, DescribeConfigs permission, TiCDC restrictions, self-signed TLS certificates, up to 100 changefeeds, Debezium, Kafka partition distribution, primary key or non-null unique index, TiDB Cloud Dedicated cluster version v6.1.3 or later, TiDB Cloud Serverless changefeed unavailable, Data > Changefeed, Create Changefeed, Destination Kafka
- Follow-up Guidance: The source also lists the required console-provided fields for Private Connect on AWS, Google Cloud, and Azure, and the navigation steps in the TiDB Cloud console to open the Kafka changefeed page.
- Classification Note: This is classified as configuration because the content defines supported conditions, version and connectivity restrictions, required Kafka ACL permissions, and the console setup path for creating a Kafka changefeed in TiDB Cloud.

## Official Source Content

# Sink to Apache Kafka

This document describes how to create a changefeed to stream data from TiDB Cloud to Apache Kafka.

> **Note:**
>
> - To use the changefeed feature, make sure that your TiDB Cloud Dedicated cluster version is v6.1.3 or later.
> - For [TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless), the changefeed feature is unavailable.
## Restrictions

- For each TiDB Cloud cluster, you can create up to 100 changefeeds.
- Currently, TiDB Cloud does not support uploading self-signed TLS certificates to connect to Kafka brokers.
- Because TiDB Cloud uses TiCDC to establish changefeeds, it has the same [restrictions as TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview#unsupported-scenarios).
- If the table to be replicated does not have a primary key or a non-null unique index, the absence of a unique constraint during replication could result in duplicated data being inserted downstream in some retry scenarios.
- If you choose Private Link or Private Service Connect as the network connectivity method, ensure that your TiDB cluster version meets the following requirements:

    - For v6.5.x: version v6.5.9 or later
    - For v7.1.x: version v7.1.4 or later
    - For v7.5.x: version v7.5.1 or later
    - For v8.1.x: all versions of v8.1.x and later are supported
- If you want to use Debezium as your data format, make sure the version of your TiDB cluster is v8.1.0 or later.
- For the partition distribution of Kafka messages, note the following:

    - If you want to distribute changelogs by primary key or index value to Kafka partition with a specified index name, make sure the version of your TiDB cluster is v7.5.0 or later.
    - If you want to distribute changelogs by column value to Kafka partition, make sure the version of your TiDB cluster is v7.5.0 or later.
## Prerequisites

Before creating a changefeed to stream data to Apache Kafka, you need to complete the following prerequisites:

- Set up your network connection
- Add permissions for Kafka ACL authorization
### Network

Ensure that your TiDB cluster can connect to the Apache Kafka service. You can choose one of the following connection methods:

- Private Connect: ideal for avoiding VPC CIDR conflicts and meeting security compliance, but incurs additional [Private Data Link Cost](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing-ticdc-rcu#private-data-link-cost).
- VPC Peering: suitable as a cost-effective option, but requires managing potential VPC CIDR conflicts and security considerations.
- Public IP: suitable for a quick setup.

<div label="Private Connect">

Private Connect leverages **Private Link** or **Private Service Connect** technologies from cloud providers to enable resources in your VPC to connect to services in other VPCs using private IP addresses, as if those services were hosted directly within your VPC.

TiDB Cloud currently supports Private Connect only for self-hosted Kafka. It does not support direct integration with MSK, Confluent Kafka, or other Kafka SaaS services. To connect to these Kafka SaaS services via Private Connect, you can deploy a [kafka-proxy](https://github.com/grepplabs/kafka-proxy) as an intermediary, effectively exposing the Kafka service as self-hosted Kafka. For a detailed example, see [Set Up Self-Hosted Kafka Private Service Connect by Kafka-proxy in Google Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect#set-up-self-hosted-kafka-private-service-connect-by-kafka-proxy). This setup is similar across all Kafka SaaS services.

- If your Apache Kafka service is hosted in AWS, follow [Set Up Self-Hosted Kafka Private Link Service in AWS](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service) to ensure that the network connection is properly configured. After setup, provide the following information in the TiDB Cloud console to create the changefeed:

    - The ID in Kafka Advertised Listener Pattern
    - The Endpoint Service Name
    - The Bootstrap Ports

- If your Apache Kafka service is hosted in Google Cloud, follow [Set Up Self-Hosted Kafka Private Service Connect in Google Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect) to ensure that the network connection is properly configured. After setup, provide the following information in the TiDB Cloud console to create the changefeed:

    - The ID in Kafka Advertised Listener Pattern
    - The Service Attachment
    - The Bootstrap Ports

- If your Apache Kafka service is hosted in Azure, follow [Set Up Self-Hosted Kafka Private Link Service in Azure](https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service) to ensure that the network connection is properly configured. After setup, provide the following information in the TiDB Cloud console to create the changefeed:

    - The ID in Kafka Advertised Listener Pattern
    - The Alias of Private Link Service
    - The Bootstrap Ports

</div>
<div label="VPC Peering">

If your Apache Kafka service is in an AWS VPC that has no internet access, take the following steps:

1. [Set up a VPC peering connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) between the VPC of the Apache Kafka service and your TiDB cluster.
2. Modify the inbound rules of the security group that the Apache Kafka service is associated with.

    You must add the CIDR of the region where your TiDB Cloud cluster is located to the inbound rules. The CIDR can be found on the **VPC Peering** page. Doing so allows the traffic to flow from your TiDB cluster to the Kafka brokers.

3. If the Apache Kafka URL contains hostnames, you need to allow TiDB Cloud to be able to resolve the DNS hostnames of the Apache Kafka brokers.

    1. Follow the steps in [Enable DNS resolution for a VPC peering connection](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-dns.html).
    2. Enable the **Accepter DNS resolution** option.

If your Apache Kafka service is in a Google Cloud VPC that has no internet access, take the following steps:

1. [Set up a VPC peering connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) between the VPC of the Apache Kafka service and your TiDB cluster.
2. Modify the ingress firewall rules of the VPC where Apache Kafka is located.

    You must add the CIDR of the region where your TiDB Cloud cluster is located to the ingress firewall rules. The CIDR can be found on the **VPC Peering** page. Doing so allows the traffic to flow from your TiDB cluster to the Kafka brokers.

</div>
<div label="Public IP">

If you want to provide Public IP access to your Apache Kafka service, assign Public IP addresses to all your Kafka brokers. 

It is **NOT** recommended to use Public IP in a production environment. 

</div>
### Kafka ACL authorization

To allow TiDB Cloud changefeeds to stream data to Apache Kafka and create Kafka topics automatically, ensure that the following permissions are added in Kafka:

- The `Create` and `Write` permissions are added for the topic resource type in Kafka.
- The `DescribeConfigs` permission is added for the cluster resource type in Kafka.

For example, if your Kafka cluster is in Confluent Cloud, you can see [Resources](https://docs.confluent.io/platform/current/kafka/authorization.html#resources) and [Adding ACLs](https://docs.confluent.io/platform/current/kafka/authorization.html#adding-acls) in Confluent documentation for more information.
## Step 1. Open the Changefeed page for Apache Kafka

1. Log in to the [TiDB Cloud console](https://tidbcloud.com).
2. Navigate to the cluster overview page of the target TiDB cluster, and then click **Data** > **Changefeed** in the left navigation pane.
3. Click **Create Changefeed**, and select **Kafka** as **Destination**.
