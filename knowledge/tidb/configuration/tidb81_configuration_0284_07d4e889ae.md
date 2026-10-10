# Reconfigure running Kafka cluster for EXTERNAL listeners

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in Azure`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in Azure > Step 1. Set up a Kafka cluster > Reconfigure a running Kafka cluster`
- Source Line Ranges: `359-419`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `ticdc`, `shared`
- Topic Tags: `kafka`, `azure`, `private-link`, `listener`, `advertised-listener`, `broker`, `kraft`, `bootstrap`, `verification`, `networking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0284_07d4e889ae`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md#reconfigure-a-running-kafka-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b625fc5dc29b9efc0783d27fcf90715b258d6f59d7a2531dcfe7d63a6f12b228`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service#reconfigure-a-running-kafka-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented EXTERNAL listener and advertised.listeners pattern for a running Kafka KRaft cluster in Azure before connecting TiDB Cloud through Private Link Service.
- Retrieval Keywords: Reconfigure a running Kafka cluster, EXTERNAL listener, advertised.listeners, listener.security.protocol.map, Kafka Advertised Listener Pattern, listeners=INTERNAL:...,EXTERNAL://0.0.0.0:39092, advertised.listeners=...,EXTERNAL://b1.abc.eastus.azure.3199745.tidbcloud.com:9093, EXTERNAL:PLAINTEXT, kafka-broker-api-versions.sh --bootstrap-server {one_of_broker_ip}:39092, DisconnectException, same region as the TiDB cluster, restart your Kafka brokers one by one
- Follow-up Guidance: The chunk also shows how to verify the EXTERNAL bootstrap from the internal network with kafka-broker-api-versions.sh and the expected DisconnectException output for advertised listener addresses.
- Classification Note: The official content is classified as configuration because it provides broker listener properties, advertised listener examples, protocol mapping, and bootstrap verification steps for Kafka networking.

## Official Source Content

### Reconfigure a running Kafka cluster

Ensure that your Kafka cluster is deployed in the same region as the TiDB cluster.

**1. Configure the EXTERNAL listener for brokers**

The following configuration applies to a Kafka KRaft cluster. The ZK mode configuration is similar.

1. Plan configuration changes.

    1. Configure an EXTERNAL **listener** for every broker for external access from TiDB Cloud. Select a unique port as the EXTERNAL port, for example, `39092`.
    2. Configure an EXTERNAL **advertised listener** based on **Kafka Advertised Listener Pattern** you get from TiDB Cloud for every broker node to help TiDB Cloud differentiate between different brokers. Different EXTERNAL advertised listeners help Kafka clients from TiDB Cloud side route requests to the right broker.
       - `<port>` differentiates brokers from Kafka Private Link service access points. Plan a port range for EXTERNAL advertised listeners of all brokers, for example, `range from 9093`. These ports do not have to be actual ports listened to by brokers. They are ports listened to by the load balancer for Private Link service that will forward requests to different brokers.
        - It is recommended to configure different broker IDs for different brokers to make it easy for troubleshooting.

2. Use SSH to log in to each broker node. Modify the configuration file of each broker with the following content:

     ```properties
     # Add EXTERNAL listener
     listeners=INTERNAL:...,EXTERNAL://0.0.0.0:39092

     # Add EXTERNAL advertised listeners based on the "Kafka Advertised Listener Pattern" in the "Prerequisites" section
     # 1. The pattern is "<broker_id>.abc.eastus.azure.3199745.tidbcloud.com:<port>".
     # 2. So the EXTERNAL can be "bx.abc.eastus.azure.3199745.tidbcloud.com:xxxx". Replace <broker_id> with "b" prefix plus "node.id" properties, and replace <port> with a unique port in the port range of the EXTERNAL advertised listener.
     # For example
     advertised.listeners=...,EXTERNAL://b1.abc.eastus.azure.3199745.tidbcloud.com:9093

     # Configure the EXTERNAL map
    listener.security.protocol.map=...,EXTERNAL:PLAINTEXT
     ```

3. After you reconfigure all the brokers, restart your Kafka brokers one by one.

**2. Test EXTERNAL listener settings in your internal network**

You can download Kafka and OpenJDK in your Kafka client node.

```shell
# Download Kafka and OpenJDK, and then extract the files. You can choose the binary version based on your preference.
wget https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz
tar -zxf kafka_2.13-3.7.1.tgz
wget https://download.java.net/java/GA/jdk22.0.2/c9ecb94cd31b495da20a27d4581645e8/9/GPL/openjdk-22.0.2_linux-x64_bin.tar.gz
tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz
```

Execute the following script to test if the bootstrap works as expected.

```shell
export JAVA_HOME=~/jdk-22.0.2

# Bootstrap from the EXTERNAL listener
./kafka_2.13-3.7.1/bin/kafka-broker-api-versions.sh --bootstrap-server {one_of_broker_ip}:39092

# Expected output for the last 3 lines (the actual order might be different)
# There will be some exceptions or errors because advertised listeners cannot be resolved in your Kafka network.
# TiDB Cloud will make these addresses resolvable and route requests to the correct broker when you create a changefeed connected to this Kafka cluster via Private Link Service.
b1.abc.eastus.azure.3199745.tidbcloud.com:9093 (id: 1 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
b2.abc.eastus.azure.3199745.tidbcloud.com:9094 (id: 2 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
b3.abc.eastus.azure.3199745.tidbcloud.com:9095 (id: 3 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
```
