# Azure self-hosted Kafka Private Link overview and prerequisites

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in Azure`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in Azure | Set Up Self-Hosted Kafka Private Link Service in Azure > Prerequisites`
- Source Line Ranges: `5-56`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `ticdc`
- Topic Tags: `azure`, `private-link`, `kafka`, `prerequisites`, `authorization`, `changefeed`, `advertised-listener`, `networking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0280_7008ac32bf`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md#set-up-self-hosted-kafka-private-link-service-in-azure`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b8893c1c755e05cccbea52fc723389a9323400762e602578fba11b3240b6d7b9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service#set-up-self-hosted-kafka-private-link-service-in-azure
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the Azure self-hosted Kafka Private Link prerequisites, the TiDB Cloud Changefeed information to note down, or the generated Kafka Advertised Listener Pattern used for Kafka broker EXTERNAL advertised listeners.
- Retrieval Keywords: Set Up Self-Hosted Kafka Private Link Service in Azure, Prerequisites, TiDB Cloud Dedicated cluster, Data > Changefeed, Create Changefeed, Destination Kafka, Connectivity Method Private Link, Reminders before proceeding, Subscription of TiDB Cloud Azure account, Kafka Advertised Listener Pattern, Check usage and generate, EXTERNAL advertised listener, private endpoints, Kafka bootstrap mechanism, Manage virtual machines, Manage virtual networks, Manage load balancers, Manage private link services
- Follow-up Guidance: The source continues with Step 1 to set up a Kafka cluster, including deploying a new Kafka cluster or reconfiguring a running Kafka cluster.
- Classification Note: This chunk is classified as configuration because the official content lists required Azure authorizations, TiDB Cloud Changefeed inputs, and the deployment information needed later to configure the Kafka Private Link service.

## Official Source Content

# Set Up Self-Hosted Kafka Private Link Service in Azure

This document describes how to set up Private Link service for self-hosted Kafka in Azure, and how to make it work with TiDB Cloud.

The mechanism works as follows:

1. The TiDB Cloud virtual network connects to the Kafka virtual network through private endpoints.
2. Kafka clients need to communicate directly to all Kafka brokers.
3. Each Kafka broker is mapped to a unique port of endpoints within the TiDB Cloud virtual network.
4. Leverage the Kafka bootstrap mechanism and Azure resources to achieve the mapping.

The following diagram shows the mechanism.

![Connect to Azure Self-Hosted Kafka Private Link Service](/media/tidb-cloud/changefeed/connect-to-azure-self-hosted-kafka-privatelink-service.png)

The document provides an example of connecting to a Kafka Private Link service in Azure. While other configurations are possible based on similar port-mapping principles, this document covers the fundamental setup process of the Kafka Private Link service. For production environments, a more resilient Kafka Private Link service with enhanced operational maintainability and observability is recommended.
## Prerequisites

1. Ensure that you have the following authorization to set up a Kafka Private Link service in your own Azure account.

    - Manage virtual machines
    - Manage virtual networks
    - Manage load balancers
    - Manage private link services
    - Connect to virtual machines to configure Kafka nodes

2. [Create a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster) on Azure if you do not have one.

3. Get the Kafka deployment information from your [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster.

    1. In the [TiDB Cloud console](https://tidbcloud.com), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.
    2. In the left navigation pane, click **Data** > **Changefeed**.
    3. On the **Changefeed** page, click **Create Changefeed** in the upper-right corner, and then provide the following information:
        1. In **Destination**, select **Kafka**.
        2. In **Connectivity Method**, select **Private Link**.
    4. Note down the region information and the subscription of the TiDB Cloud Azure account in **Reminders before proceeding**. You will use it to authorize TiDB Cloud to access the Kafka Private Link service.
    5. Generate the **Kafka Advertised Listener Pattern** for your Kafka Private Link service by providing a unique random string.
        1. Input a unique random string. It can only include numbers or lowercase letters. You will use it to generate **Kafka Advertised Listener Pattern** later.
        2. Click **Check usage and generate** to check if the random string is unique and generate **Kafka Advertised Listener Pattern** that will be used to assemble the EXTERNAL advertised listener for Kafka brokers.

Note down all the deployment information. You need to use it to configure your Kafka Private Link service later.

The following table shows an example of the deployment information.

| Information     | Value    | Note    |
|--------|-----------------|---------------------------|
| Region | Virginia (`eastus`) | N/A |
| Subscription of TiDB Cloud Azure account | `99549169-6cee-4263-8491-924a3011ee31` | N/A |
| Kafka Advertised Listener Pattern | The unique random string: `abc` | Generated pattern: `<broker_id>.abc.eastus.azure.3199745.tidbcloud.com:<port>`; |
