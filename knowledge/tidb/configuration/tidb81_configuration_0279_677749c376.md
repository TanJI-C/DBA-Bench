# Create Kafka Private Link service and connect TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in AWS`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in AWS > Step 2. Expose the Kafka cluster as Private Link Service > 2. Set up Private Link Service | Set Up Self-Hosted Kafka Private Link Service in AWS > Step 3. Connect from TiDB Cloud | Set Up Self-Hosted Kafka Private Link Service in AWS > FAQ | Set Up Self-Hosted Kafka Private Link Service in AWS > FAQ > How to connect to the same Kafka Private Link service from two different TiDB Cloud projects?`
- Source Line Ranges: `715-761`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `ticdc`
- Topic Tags: `aws`, `private-link`, `kafka`, `endpoint-service`, `load-balancer`, `changefeed`, `connectivity`, `multi-project`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0279_677749c376`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md#2-set-up-private-link-service`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e1b94a46c1d642a376fb2dd0bfaab14ce35180bc98c5a9f5f89d1b0aaabd2d6e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service#2-set-up-private-link-service
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the AWS Endpoint service settings and TiDB Cloud changefeed fields needed to connect a self-hosted Kafka cluster through Private Link, including reuse from two different TiDB Cloud projects.
- Retrieval Keywords: Create endpoint service, Endpoint service, Private Link service, kafka-pl-service, Network, kafka-lb, Included Availability Zones, usw2-az1, usw2-az2, usw2-az3, Acceptance required, Enable private DNS name, Service name, com.amazonaws.vpce.us-west-2.vpce-svc-0f49e37e1f022cd45, Allow principals, arn:aws:iam::<account_id>:root, Configure the changefeed target, Connectivity Method, Private Link, Kafka Type, 3 AZs, Kafka Advertised Listener Pattern, Endpoint Service Name, Bootstrap Ports, 9092, same Kafka Private Link service from two different TiDB Cloud projects, EXTERNAL2, New Bootstrap port, New Kafka Advertised Listener Group, The same Endpoint Service
- Follow-up Guidance: The source also states that after entering these fields you proceed with the steps in Sink to Apache Kafka, and for a second TiDB Cloud project you create another group of EXTERNAL listeners and add another target group in the load balancer.
- Classification Note: This is classified as configuration because the content provides concrete AWS Private Link service parameters, TiDB Cloud changefeed connectivity fields, and multi-project connection settings.

## Official Source Content

### 2. Set up Private Link Service

1. Go to [Endpoint service](https://console.aws.amazon.com/vpcconsole/home#EndpointServices:). Click **Create endpoint service** to create a Private Link service for the Kafka load balancer.

    - **Name**: `kafka-pl-service`
    - **Load balancer type**: `Network`
    - **Load balancers**: `kafka-lb`
    - **Included Availability Zones**: `usw2-az1`,`usw2-az2`, `usw2-az3`
    - **Require acceptance for endpoint**: `Acceptance required`
    - **Enable private DNS name**: `No`

2. Note down the **Service name**. You need to provide it to TiDB Cloud, for example `com.amazonaws.vpce.us-west-2.vpce-svc-0f49e37e1f022cd45`.

3. On the detail page of the kafka-pl-service, click the **Allow principals** tab, and allow the AWS account of TiDB Cloud to create the endpoint. You can get the AWS account of TiDB Cloud in [Prerequisites](#prerequisites), for example, `arn:aws:iam::<account_id>:root`.
## Step 3. Connect from TiDB Cloud

1. Return to the [TiDB Cloud console](https://tidbcloud.com) to create a changefeed for the cluster to connect to the Kafka cluster by **Private Link**. For more information, see [Sink to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka).

2. When you proceed to **Configure the changefeed target > Connectivity Method > Private Link**, fill in the following fields with corresponding values and other fields as needed.

    - **Kafka Type**: `3 AZs`. Ensure that your Kafka cluster is deployed in the same three AZs.
    - **Kafka Advertised Listener Pattern**: `abc`. It is the same as the unique random string you use to generate **Kafka Advertised Listener Pattern** in [Prerequisites](#prerequisites).
    - **Endpoint Service Name**: the Kafka service name.
    - **Bootstrap Ports**: `9092`. A single port is sufficient because you configure a dedicated bootstrap target group behind it.

3. Proceed with the steps in [Sink to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka).

Now you have successfully finished the task.
## FAQ
### How to connect to the same Kafka Private Link service from two different TiDB Cloud projects?

If you have already followed this document to successfully set up the connection from the first project, you can connect to the same Kafka Private Link service from the second project as follows:

1. Follow instructions from the beginning of this document. 

2. When you proceed to [Step 1. Set up a Kafka cluster](#step-1-set-up-a-kafka-cluster), follow [Reconfigure a running Kafka cluster](#reconfigure-a-running-kafka-cluster) to create another group of EXTERNAL listeners and advertised listeners. You can name it as **EXTERNAL2**. Note that the port range of **EXTERNAL2** cannot overlap with the **EXTERNAL**.

3. After reconfiguring brokers, add another target group in the load balancer, including the bootstrap and broker target groups.

4. Configure the TiDB Cloud connection with the following information:

    - New Bootstrap port
    - New Kafka Advertised Listener Group
    - The same Endpoint Service
