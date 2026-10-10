# Reconfigure running Kafka brokers for PSC port mapping

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md`
- Source Title: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > Set up self-hosted Kafka Private Service Connect service by PSC port mapping > Step 1. Set up the Kafka cluster > Reconfigure a running Kafka cluster`
- Source Line Ranges: `408-468`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `ecosystem`
- Topic Tags: `kafka`, `private-service-connect`, `broker-listeners`, `advertised-listeners`, `port-mapping`, `broker-restart`, `connectivity-test`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0290_578e00b6cd`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-self-hosted-kafka-private-service-connect.md#reconfigure-a-running-kafka-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b23437f248f7b08d670cc1fd02f928bbcad7125511539b1f3bb315e5b1aba3ee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect#reconfigure-a-running-kafka-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact Kafka broker EXTERNAL listener and advertised.listeners configuration for Private Service Connect port mapping, plus the expected kafka-broker-api-versions.sh connectivity test output.
- Retrieval Keywords: Reconfigure a running Kafka cluster, EXTERNAL listener, advertised.listeners, listener.security.protocol.map, Kafka Advertised Listener Pattern, listeners=INTERNAL:...,EXTERNAL://0.0.0.0:39092, advertised.listeners=...,EXTERNAL://b1.abc.us-west1.gcp.3199745.tidbcloud.com:9093, EXTERNAL:PLAINTEXT, restart your Kafka brokers one by one, kafka-broker-api-versions.sh --bootstrap-server {one_of_broker_ip}:39092, org.apache.kafka.common.errors.DisconnectException
- Follow-up Guidance: The chunk continues with downloading Kafka and OpenJDK and running kafka-broker-api-versions.sh to verify the EXTERNAL listener bootstrap behavior in the internal network.
- Classification Note: This is classified as configuration because the content provides broker listener, advertised listener, protocol map, restart, and connectivity test settings for a running Kafka cluster.

## Official Source Content

#### Reconfigure a running Kafka cluster

Ensure that your Kafka cluster is deployed in the same region as the TiDB cluster. It is recommended that the zones are also in the same region to reduce cross-zone traffic.

**1. Configure the EXTERNAL listener for brokers**

The following configuration applies to a Kafka KRaft cluster. The ZK mode configuration is similar.

1. Plan configuration changes.

    1. Configure an EXTERNAL **listener** for every broker for external access from TiDB Cloud. Select a unique port as the EXTERNAL port, for example, `39092`.
    2. Configure an EXTERNAL **advertised listener** based on **Kafka Advertised Listener Pattern** you get from TiDB Cloud for every broker node to help TiDB Cloud differentiate between different brokers. Different EXTERNAL advertised listeners help Kafka clients from TiDB Cloud side route requests to the right broker.
       - `<port>` differentiates brokers from Kafka Private Service Connect access points. Plan a port range for EXTERNAL advertised listeners of all brokers, for example, `range from 9093`. These ports do not have to be actual ports listened to by brokers. They are ports listened to by the load balancer for Private Service Connect that will forward requests to different brokers.
        - It is recommended to configure different broker IDs for different brokers to make it easy for troubleshooting.

2. Use SSH to log in to each broker node. Modify the configuration file of each broker with the following content:

     ```properties
     # Add EXTERNAL listener
     listeners=INTERNAL:...,EXTERNAL://0.0.0.0:39092

     # Add EXTERNAL advertised listeners based on the "Kafka Advertised Listener Pattern" in the "Prerequisites" section
     # 1. The pattern is "<broker_id>.abc.us-west1.gcp.3199745.tidbcloud.com:<port>".
     # 2. So the EXTERNAL can be "bx.abc.us-west1.gcp.3199745.tidbcloud.com:xxxx". Replace <broker_id> with "b" prefix plus "node.id" properties, and replace <port> with a unique port in the port range of the EXTERNAL advertised listener.
     # For example
     advertised.listeners=...,EXTERNAL://b1.abc.us-west1.gcp.3199745.tidbcloud.com:9093

     # Configure EXTERNAL map
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
# We will make them resolvable in TiDB Cloud side and make it route to the right broker when you create a changefeed connect to this Kafka cluster by Private Service Connect. 
b1.abc.us-west1.gcp.3199745.tidbcloud.com:9093 (id: 1 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
b2.abc.us-west1.gcp.3199745.tidbcloud.com:9094 (id: 2 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
b3.abc.us-west1.gcp.3199745.tidbcloud.com:9095 (id: 3 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
```
