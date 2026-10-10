# Overview and prerequisites for AWS self-hosted Kafka Private Link

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in AWS`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in AWS | Set Up Self-Hosted Kafka Private Link Service in AWS > Prerequisites`
- Source Line Ranges: `6-61`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `ecosystem`
- Topic Tags: `aws`, `private-link`, `kafka`, `prerequisites`, `az-mapping`, `listener-pattern`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0272_f515d6dd2a`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md#set-up-self-hosted-kafka-private-link-service-in-aws`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `aff41184358c90854b1c2a27ae3335a868969d6e6e807467e6188304f00d07dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service#set-up-self-hosted-kafka-private-link-service-in-aws
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the prerequisites, AWS authorization requirements, TiDB Cloud console information, AZ ID mapping, or Kafka Advertised Listener Pattern needed to set up an AWS self-hosted Kafka Private Link service with TiDB Cloud.
- Retrieval Keywords: Private Link service for self-hosted Kafka in AWS, TiDB Cloud VPC connects to the Kafka VPC through private endpoints, Kafka clients need to communicate directly to all Kafka brokers, each Kafka broker is mapped to a unique port of endpoints, Create Changefeed, Destination Kafka, Connectivity Method Private Link, Reminders before proceeding, Principal of TiDB Cloud AWS Account, Number of AZs, AZ IDs, Availability Zone IDs for your AWS resources, Kafka Advertised Listener Pattern, Check usage and generate, advertised listener pattern, usw2-az1, usw2-az2, usw2-az3, us-west-2, arn:aws:iam::<account_id>:root
- Follow-up Guidance: The documented follow-up is to note down all deployment information and use it later to configure the Kafka Private Link service.
- Classification Note: This is classified as configuration because it defines the required setup information, permissions, region and AZ alignment, and listener pattern inputs used before configuring the Kafka Private Link service.

## Official Source Content

# Set Up Self-Hosted Kafka Private Link Service in AWS

This document describes how to set up Private Link service for self-hosted Kafka in AWS, and how to make it work with TiDB Cloud.

The mechanism works as follows:

1. The TiDB Cloud VPC connects to the Kafka VPC through private endpoints.
2. Kafka clients need to communicate directly to all Kafka brokers.
3. Each Kafka broker is mapped to a unique port of endpoints within the TiDB Cloud VPC.
4. Leverage the Kafka bootstrap mechanism and AWS resources to achieve the mapping.

The following diagram shows the mechanism. 

![Connect to AWS Self-Hosted Kafka Private Link Service](/media/tidb-cloud/changefeed/connect-to-aws-self-hosted-kafka-privatelink-service.jpeg)

The document provides an example of connecting to a Kafka Private Link service deployed across three availability zones (AZ) in AWS. While other configurations are possible based on similar port-mapping principles, this document covers the fundamental setup process of the Kafka Private Link service. For production environments, a more resilient Kafka Private Link service with enhanced operational maintainability and observability is recommended.
## Prerequisites

1. Ensure that you have the following authorization to set up a Kafka Private Link service in your own AWS account. 

    - Manage EC2 nodes
    - Manage VPC
    - Manage subnets
    - Manage security groups
    - Manage load balancer
    - Manage endpoint services
    - Connect to EC2 nodes to configure Kafka nodes

2. [Create a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster) if you do not have one.

3. Get the Kafka deployment information from your TiDB Cloud Dedicated cluster.

    1. In the [TiDB Cloud console](https://tidbcloud.com), navigate to the cluster overview page of the TiDB cluster, and then click **Data** > **Changefeed** in the left navigation pane.
    2. On the overview page, find the region of the TiDB cluster. Ensure that your Kafka cluster will be deployed to the same region.
    3. Click **Create Changefeed**.
        1. In **Destination**, select **Kafka**.
        2. In **Connectivity Method**, select **Private Link**.
    4. Note down the information of the TiDB Cloud AWS account in **Reminders before proceeding**. You will use it to authorize TiDB Cloud to create an endpoint for the Kafka Private Link service.
    5. Select **Number of AZs**. In this example, select **3 AZs**. Note down the IDs of the AZs in which you want to deploy your Kafka cluster. If you want to know the relationship between your AZ names and AZ IDs, see [Availability Zone IDs for your AWS resources](https://docs.aws.amazon.com/ram/latest/userguide/working-with-az-ids.html) to find it.
    6. Enter a unique **Kafka Advertised Listener Pattern** for your Kafka Private Link service.
        1. Input a unique random string. It can only include numbers or lowercase letters. You will use it to generate **Kafka Advertised Listener Pattern** later.
        2. Click **Check usage and generate** to check if the random string is unique and generate **Kafka Advertised Listener Pattern** that will be used to assemble the EXTERNAL advertised listener for Kafka brokers. 

Note down all the deployment information. You need to use it to configure your Kafka Private Link service later.

The following table shows an example of the deployment information.

| Information     | Value    | Note    | 
|--------|-----------------|---------------------------|
| Region    | Oregon (`us-west-2`)    |  N/A |
| Principal of TiDB Cloud AWS Account | `arn:aws:iam::<account_id>:root`     |    N/A  |
| AZ IDs                              | <ul><li>`usw2-az1` </li><li>`usw2-az2` </li><li> `usw2-az3`</li></ul>  | Align AZ IDs to AZ names in your AWS account.<br/>Example: <ul><li> `usw2-az1` => `us-west-2a` </li><li> `usw2-az2` => `us-west-2c` </li><li>`usw2-az3` => `us-west-2b`</li></ul>  |
| Kafka Advertised Listener Pattern   | The unique random string: `abc` <br/>Generated pattern for AZs: <ul><li> `usw2-az1` => &lt;broker_id&gt;.usw2-az1.abc.us-west-2.aws.3199015.tidbcloud.com:&lt;port&gt; </li><li> `usw2-az2` => &lt;broker_id&gt;.usw2-az2.abc.us-west-2.aws.3199015.tidbcloud.com:&lt;port&gt; </li><li> `usw2-az3` => &lt;broker_id&gt;.usw2-az3.abc.us-west-2.aws.3199015.tidbcloud.com:&lt;port&gt; </li></ul>    | Map AZ names to AZ-specified patterns. Make sure that you configure the right pattern to the broker in a specific AZ later. <ul><li> `us-west-2a` => &lt;broker_id&gt;.usw2-az1.abc.us-west-2.aws.3199015.tidbcloud.com:&lt;port&gt; </li><li> `us-west-2c` => &lt;broker_id&gt;.usw2-az2.abc.us-west-2.aws.3199015.tidbcloud.com:&lt;port&gt; </li><li> `us-west-2b` => &lt;broker_id&gt;.usw2-az3.abc.us-west-2.aws.3199015.tidbcloud.com:&lt;port&gt; </li></ul>|
