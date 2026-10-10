# Reconfigure Kafka brokers with EXTERNAL listeners and validate internally

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in AWS`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in AWS > Step 1. Set up a Kafka cluster > Reconfigure a running Kafka cluster > 1. Configure the EXTERNAL listener for brokers | Set Up Self-Hosted Kafka Private Link Service in AWS > Step 1. Set up a Kafka cluster > Reconfigure a running Kafka cluster > 2. Test EXTERNAL listener settings in your internal network`
- Source Line Ranges: `528-618`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `ticdc`
- Topic Tags: `kafka`, `private-link`, `aws`, `external-listener`, `advertised-listener`, `broker`, `kraft`, `bootstrap`, `connectivity-test`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0277_93a48a050d`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md#1-configure-the-external-listener-for-brokers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c8d987c5fa438380826f9d53906312d87d916a3b581c90462977451666c53206`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service#1-configure-the-external-listener-for-brokers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact Kafka broker EXTERNAL listener and advertised.listeners configuration pattern for AWS Private Link access from TiDB Cloud and the expected internal bootstrap validation output.
- Retrieval Keywords: EXTERNAL listener, advertised.listeners, listener.security.protocol.map, Kafka Advertised Listener Pattern, KRaft cluster, listeners=INTERNAL:...,EXTERNAL://0.0.0.0:39092, advertised.listeners=...,EXTERNAL://b1.usw2-az1.abc.us-west-2.aws.3199015.tidbcloud.com:9093, EXTERNAL:PLAINTEXT, kafka-broker-api-versions.sh --bootstrap-server {one_of_broker_ip}:39092, org.apache.kafka.common.errors.DisconnectException, node.id, b1.usw2-az1, b2.usw2-az2, b3.usw2-az3
- Follow-up Guidance: After reconfiguring all brokers, restart the Kafka brokers one by one, then run kafka-broker-api-versions.sh against one broker IP on port 39092 and compare the last lines with the expected DisconnectException output.
- Classification Note: This is classified as configuration because the content defines broker properties, EXTERNAL listener and advertised listener mappings, and an internal connectivity test for the configured bootstrap endpoint.

## Official Source Content

#### 1. Configure the EXTERNAL listener for brokers

The following configuration applies to a Kafka KRaft cluster. The ZK mode configuration is similar.

1. Plan configuration changes.

    1. Configure an EXTERNAL **listener** for every broker for external access from TiDB Cloud. Select a unique port as the EXTERNAL port, for example, `39092`.
    2. Configure an EXTERNAL **advertised listener** based on **Kafka Advertised Listener Pattern** you get from TiDB Cloud for every broker node to help TiDB Cloud differentiate between different brokers. Different EXTERNAL advertised listeners help Kafka clients from TiDB Cloud route requests to the right broker.

        - `<port>` differentiates brokers from Kafka Private Link Service access points. Plan a port range for EXTERNAL advertised listeners of all brokers, for example, `range from 9093`. These ports do not have to be actual ports listened to by brokers. They are ports listened to by the load balancer for Private Link Service that will forward requests to different brokers.
        - `AZ ID` in **Kafka Advertised Listener Pattern** indicates where the broker is deployed. TiDB Cloud will route requests to different endpoint DNS names based on the AZ ID.
      
      It is recommended to configure different broker IDs for different brokers to make it easy for troubleshooting.

2. Use SSH to log in to each broker node. Modify the configuration file of each broker with the following content:

    ```properties
    # brokers in usw2-az1

    # Add EXTERNAL listener
    listeners=INTERNAL:...,EXTERNAL://0.0.0.0:39092

    # Add EXTERNAL advertised listeners based on the "Kafka Advertised Listener Pattern" in "Prerequisites" section
    # 1. The pattern for AZ(ID: usw2-az1) is "<broker_id>.usw2-az1.abc.us-west-2.aws.3199015.tidbcloud.com:<port>"
    # 2. So the EXTERNAL can be "b1.usw2-az1.abc.us-west-2.aws.3199015.tidbcloud.com:9093", replace <broker_id> with "b" prefix plus "node.id" properties, replace <port> with a unique port(9093) in EXTERNAL advertised listener ports range 
    advertised.listeners=...,EXTERNAL://b1.usw2-az1.abc.us-west-2.aws.3199015.tidbcloud.com:9093

    # Configure EXTERNAL map
    listener.security.protocol.map=...,EXTERNAL:PLAINTEXT
    ```
 
    ```properties
    # brokers in usw2-az2

    # Add EXTERNAL listener
    listeners=INTERNAL:...,EXTERNAL://0.0.0.0:39092

    # Add EXTERNAL advertised listeners based on the "Kafka Advertised Listener Pattern" in "Prerequisites" section
    # 1. The pattern for AZ(ID: usw2-az2) is "<broker_id>.usw2-az2.abc.us-west-2.aws.3199015.tidbcloud.com:<port>"
    # 2. So the EXTERNAL can be "b2.usw2-az2.abc.us-west-2.aws.3199015.tidbcloud.com:9094". Replace <broker_id> with "b" prefix plus "node.id" properties, and replace <port> with a unique port(9094) in EXTERNAL advertised listener ports range.
    advertised.listeners=...,EXTERNAL://b2.usw2-az2.abc.us-west-2.aws.3199015.tidbcloud.com:9094

    # Configure EXTERNAL map
    listener.security.protocol.map=...,EXTERNAL:PLAINTEXT
    ```

    ```properties
    # brokers in usw2-az3

    # Add EXTERNAL listener
    listeners=INTERNAL:...,EXTERNAL://0.0.0.0:39092

    # Add EXTERNAL advertised listeners based on the "Kafka Advertised Listener Pattern" in "Prerequisites" section
    # 1. The pattern for AZ(ID: usw2-az3) is "<broker_id>.usw2-az3.abc.us-west-2.aws.3199015.tidbcloud.com:<port>"
    # 2. So the EXTERNAL can be "b2.usw2-az3.abc.us-west-2.aws.3199015.tidbcloud.com:9095". Replace <broker_id> with "b" prefix plus "node.id" properties, and replace <port> with a unique port(9095) in EXTERNAL advertised listener ports range.
    advertised.listeners=...,EXTERNAL://b3.usw2-az3.abc.us-west-2.aws.3199015.tidbcloud.com:9095

    # Configure EXTERNAL map
    listener.security.protocol.map=...,EXTERNAL:PLAINTEXT
    ```

3. After you reconfigure all the brokers, restart your Kafka brokers one by one.
#### 2. Test EXTERNAL listener settings in your internal network

You can download the Kafka and OpenJDK in you Kafka client node.

```shell
# Download Kafka and OpenJDK, and then extract the files. You can choose the binary version based on your preference.
wget https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz
tar -zxf kafka_2.13-3.7.1.tgz
wget https://download.java.net/java/GA/jdk22.0.2/c9ecb94cd31b495da20a27d4581645e8/9/GPL/openjdk-22.0.2_linux-x64_bin.tar.gz
tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz
```

Execute the following script to test if the bootstrap works as expected.

```shell
export JAVA_HOME=/home/ec2-user/jdk-22.0.2

# Bootstrap from the EXTERNAL listener
./kafka_2.13-3.7.1/bin/kafka-broker-api-versions.sh --bootstrap-server {one_of_broker_ip}:39092

# Expected output for the last 3 lines (the actual order might be different)
# There will be some exceptions or errors because advertised listeners cannot be resolved in your Kafka network. 
# We will make them resolvable in TiDB Cloud side and make it route to the right broker when you create a changefeed connect to this Kafka cluster by Private Link. 
b1.usw2-az1.abc.us-west-2.aws.3199015.tidbcloud.com:9093 (id: 1 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
b2.usw2-az2.abc.us-west-2.aws.3199015.tidbcloud.com:9094 (id: 2 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
b3.usw2-az3.abc.us-west-2.aws.3199015.tidbcloud.com:9095 (id: 3 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
```
