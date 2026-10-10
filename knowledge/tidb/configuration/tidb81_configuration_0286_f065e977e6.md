# Overview and prerequisites for Kafka Private Service Connect setup

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md`
- Source Title: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud | Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > Prerequisites`
- Source Line Ranges: `5-61`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `shared`
- Topic Tags: `private-service-connect`, `kafka`, `google-cloud`, `prerequisites`, `changefeed`, `deployment-planning`, `networking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0286_f065e977e6`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-self-hosted-kafka-private-service-connect.md#set-up-self-hosted-kafka-private-service-connect-in-google-cloud`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0fa5f5ffc5efd51567e099becc3f23a3a69d944de21eed8790d8d165c63e6883`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect#set-up-self-hosted-kafka-private-service-connect-in-google-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about prerequisites, planning details, or the overall setup mechanism for connecting TiDB Cloud to self-hosted Kafka through Google Cloud Private Service Connect.
- Retrieval Keywords: Private Service Connect, self-hosted Kafka, Google Cloud, TiDB Cloud VPC, private endpoints, Kafka bootstrap mechanism, PSC port mapping, Kafka-proxy, Prerequisites, Manage VM nodes, Manage VPC, Manage subnets, Manage load balancer, Manage Private Service Connect, Create Changefeed, Destination Kafka, Connectivity Method Private Service Connect, Reminders before proceeding, Google Cloud project of TiDB Cloud, Zones of TiDB Cluster, Kafka Advertised Listener Pattern, Check usage and generate
- Follow-up Guidance: The source also points to two setup paths: PSC port mapping and Kafka-proxy, and says the noted deployment information is needed later to configure the Kafka Private Service Connect service.
- Classification Note: This is classified as configuration because the content defines the setup options, required permissions, and exact TiDB Cloud deployment information needed before configuring Kafka Private Service Connect.

## Official Source Content

# Set Up Self-Hosted Kafka Private Service Connect in Google Cloud

This document explains how to set up Private Service Connect for self-hosted Kafka in Google Cloud, and how to make it work with TiDB Cloud.

The mechanism works as follows:

1. The TiDB Cloud VPC connects to the Kafka VPC through private endpoints.
2. Kafka clients need to communicate directly to all Kafka brokers.
3. Each Kafka broker is mapped to a unique port within the TiDB Cloud VPC.
4. Leverage the Kafka bootstrap mechanism and Google Cloud resources to achieve the mapping.

There are two ways to set up Private Service Connect for self-hosted Kafka in Google Cloud:

- Use the Private Service Connect (PSC) port mapping mechanism. This method requires static port-broker mapping configuration. You need to reconfigure the existing Kafka cluster to add a group of EXTERNAL listeners and advertised listeners. See [Set up self-hosted Kafka Private Service Connect service by PSC port mapping](#set-up-self-hosted-kafka-private-service-connect-service-by-psc-port-mapping).

- Use [Kafka-proxy](https://github.com/grepplabs/kafka-proxy). This method introduces an extra running process as the proxy between Kafka clients and Kafka brokers. The proxy dynamically configures the port-broker mapping and forwards requests. You do not need to reconfigure the existing Kafka cluster. See [Set up self-hosted Kafka Private Service Connect by Kafka-proxy](#set-up-self-hosted-kafka-private-service-connect-by-kafka-proxy).

The document provides an example of connecting to a Kafka Private Service Connect service deployed across three availability zones (AZ) in Google Cloud. While other configurations are possible based on similar port-mapping principles, this document covers the fundamental setup process of the Kafka Private Service Connect service. For production environments, a more resilient Kafka Private Service Connect service with enhanced operational maintainability and observability is recommended.
## Prerequisites

1. Ensure that you have the following authorization to set up Kafka Private Service Connect in your own Google Cloud account. 

    - Manage VM nodes
    - Manage VPC
    - Manage subnets
    - Manage load balancer
    - Manage Private Service Connect
    - Connect to VM nodes to configure Kafka nodes

2. [Create a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster) if you do not have one.

3. Get the Kafka deployment information from your TiDB Cloud Dedicated cluster.

    1. In the [TiDB Cloud console](https://tidbcloud.com), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.
    2. On the overview page, find the region of the TiDB cluster. Ensure that your Kafka cluster will be deployed to the same region.
    3. Click **Data** > **Changefeed** in the left navigation pane, click **Create Changefeed** in the upper-right corner, and then provide the following information:
        1. In **Destination**, select **Kafka**.
        2. In **Connectivity Method**, select **Private Service Connect**.
    4. Note down the Google Cloud project in **Reminders before proceeding**. You will use it to authorize the auto-accept endpoint creation request from TiDB Cloud.
    5. Note down the **Zones of TiDB Cluster**. You will deploy your TiDB cluster in these zones. It is recommended that you deploy Kafka in these zones to reduce cross-zone traffic.
    6. Pick a unique **Kafka Advertised Listener Pattern** for your Kafka Private Service Connect service.
        1. Input a unique random string. It can only include numbers or lowercase letters. You will use it to generate **Kafka Advertised Listener Pattern** later.
        2. Click **Check usage and generate** to check if the random string is unique and generate **Kafka Advertised Listener Pattern** that will be used to assemble the EXTERNAL advertised listener for Kafka brokers, or configure Kafka-proxy. 

Note down all the deployment information. You need to use it to configure your Kafka Private Service Connect service later.

The following table shows an example of the deployment information.

| Information                        | Value                           |
|------------------------------------|---------------------------------|
| Region                             | Oregon (`us-west1`)               |
| Google Cloud project of TiDB Cloud | `tidbcloud-prod-000`              |
| Zones                              | <ul><li> `us-west1-a` </li><li> `us-west1-b` </li><li> `us-west1-c` </li></ul>   |
| Kafka Advertised Listener Pattern  | The unique random string: `abc` <br/> Generated pattern: &lt;broker_id&gt;.abc.us-west1.gcp.3199745.tidbcloud.com:&lt;port&gt; |
