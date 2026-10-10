# Expose Kafka through AWS Private Link with an NLB

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in AWS`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in AWS > Step 2. Expose the Kafka cluster as Private Link Service | Set Up Self-Hosted Kafka Private Link Service in AWS > Step 2. Expose the Kafka cluster as Private Link Service > 1. Set up the load balancer`
- Source Line Ranges: `619-714`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `ticdc`
- Topic Tags: `kafka`, `private-link`, `aws`, `network-load-balancer`, `target-group`, `security-group`, `bootstrap`, `broker-mapping`, `vpc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0278_9a326c920c`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md#step-2-expose-the-kafka-cluster-as-private-link-service`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d38001201f87cd087bc9d56ebc2506e49b1cd56affc9320750aca97d27ff2256`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service#step-2-expose-the-kafka-cluster-as-private-link-service
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact AWS Network Load Balancer and target group port mappings that expose a self-hosted Kafka cluster as a Private Link Service for TiDB Cloud.
- Retrieval Keywords: network load balancer, Private Link Service, bootstrap-target-group, broker-target-group-1, broker-target-group-2, broker-target-group-3, 9092 => broker-node1:39092,broker-node2:39092,broker-node3:39092, 9093 => broker-node1:39092, 9094 => broker-node2:39092, 9095 => broker-node3:39092, kafka-lb, Security groups, Project Settings > Network Access, Project CIDR > AWS, kafka-broker-api-versions.sh --bootstrap-server {lb_dns_name}:9092, cross-zone load balancing, org.apache.kafka.common.errors.DisconnectException
- Follow-up Guidance: After creating the target groups and the network load balancer, test bootstrap from the bastion node with the kafka-lb DNS name on port 9092 and compare the last lines with the expected DisconnectException output.
- Classification Note: This is classified as configuration because the content specifies the target groups, listener routing, security group rules, availability zone settings, and bootstrap test details for exposing Kafka through AWS Private Link.

## Official Source Content

## Step 2. Expose the Kafka cluster as Private Link Service
### 1. Set up the load balancer

Create a network load balancer with four target groups with different ports. One target group is for bootstrap, and the others will map to different brokers.

1. bootstrap target group => 9092 => broker-node1:39092,broker-node2:39092,broker-node3:39092
2. broker target group 1  => 9093 => broker-node1:39092
3. broker target group 2  => 9094 => broker-node2:39092
4. broker target group 3  => 9095 => broker-node3:39092

If you have more broker role nodes, you need to add more mappings. Ensure that you have at least one node in the bootstrap target group. It is recommended to add three nodes, one for each AZ for resilience.

Do the following to set up the load balancer:

1. Go to [Target groups](https://console.aws.amazon.com/ec2/home#CreateTargetGroup:) to create four target groups.

    - Bootstrap target group 

        - **Target type**: `Instances`
        - **Target group name**: `bootstrap-target-group`
        - **Protocol**: `TCP`
        - **Port**: `9092`
        - **IP address type**: `IPv4`
        - **VPC**: `Kafka VPC`
        - **Health check protocol**: `TCP`
        - **Register targets**: `broker-node1:39092`, `broker-node2:39092`, `broker-node3:39092`

    - Broker target group 1

        - **Target type**: `Instances`
        - **Target group name**: `broker-target-group-1`
        - **Protocol**: `TCP`
        - **Port**: `9093`
        - **IP address type**: `IPv4`
        - **VPC**: `Kafka VPC`
        - **Health check protocol**: `TCP`
        - **Register targets**: `broker-node1:39092`

    - Broker target group 2

        - **Target type**: `Instances`
        - **Target group name**: `broker-target-group-2`
        - **Protocol**: `TCP`
        - **Port**: `9094`
        - **IP address type**: `IPv4`
        - **VPC**: `Kafka VPC`
        - **Health check protocol**: `TCP`
        - **Register targets**: `broker-node2:39092`

    - Broker target group 3

        - **Target type**: `Instances`
        - **Target group name**: `broker-target-group-3`
        - **Protocol**: `TCP`
        - **Port**: `9095`
        - **IP address type**: `IPv4`
        - **VPC**: `Kafka VPC`
        - **Health check protocol**: `TCP`
        - **Register targets**: `broker-node3:39092`

2. Go to [Load balancers](https://console.aws.amazon.com/ec2/home#LoadBalancers:) to create a network load balancer.

    - **Load balancer name**: `kafka-lb`
    - **Schema**: `Internal`
    - **Load balancer IP address type**: `IPv4`
    - **VPC**: `Kafka VPC`
    - **Availability Zones**: 
        - `usw2-az1` with `broker-usw2-az1 subnet`
        - `usw2-az2` with `broker-usw2-az2 subnet`
        - `usw2-az3` with `broker-usw2-az3 subnet`
    - **Security groups**: create a new security group with the following rules.
        - Inbound rule allows all TCP from Kafka VPC: Type - `{ports of target groups}`, for example, `9092-9095`; Source - `{CIDR of TiDB Cloud}`. To get the CIDR of TiDB Cloud in the region, switch to your target project using the combo box in the upper-left corner of the [TiDB Cloud console](https://tidbcloud.com), click **Project Settings** > **Network Access** in the left navigation pane, and then click **Project CIDR** > **AWS**.
        - Outbound rule allows all TCP to Kafka VPC: Type - `All TCP`; Destination - `Anywhere-IPv4`
    - Listeners and routing:
        - Protocol: `TCP`; Port: `9092`; Forward to: `bootstrap-target-group`
        - Protocol: `TCP`; Port: `9093`; Forward to: `broker-target-group-1`
        - Protocol: `TCP`; Port: `9094`; Forward to: `broker-target-group-2`
        - Protocol: `TCP`; Port: `9095`; Forward to: `broker-target-group-3`

3. Test the load balancer in the bastion node. This example only tests the Kafka bootstrap. Because the load balancer is listening on the Kafka EXTERNAL listener, the addresses of EXTERNAL advertised listeners can not be resolved in the bastion node. Note down the `kafka-lb` DNS name from the load balancer detail page, for example `kafka-lb-77405fa57191adcb.elb.us-west-2.amazonaws.com`. Execute the script in the bastion node.

    ```shell
    # Replace {lb_dns_name} to your actual value
    export JAVA_HOME=/home/ec2-user/jdk-22.0.2
    ./kafka_2.13-3.7.1/bin/kafka-broker-api-versions.sh --bootstrap-server {lb_dns_name}:9092

    # Expected output for the last 3 lines (the actual order might be different)
    b1.usw2-az1.abc.us-west-2.aws.3199015.tidbcloud.com:9093 (id: 1 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
    b2.usw2-az2.abc.us-west-2.aws.3199015.tidbcloud.com:9094 (id: 2 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
    b3.usw2-az3.abc.us-west-2.aws.3199015.tidbcloud.com:9095 (id: 3 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException

    # You can also try bootstrap in other ports 9093/9094/9095. It will succeed probabilistically because NLB in AWS resolves LB DNS to the IP address of any availability zone and disables cross-zone load balancing by default. 
    # If you enable cross-zone load balancing in LB, it will succeed. However, it is unnecessary and might cause additional cross-AZ traffic.
    ```
