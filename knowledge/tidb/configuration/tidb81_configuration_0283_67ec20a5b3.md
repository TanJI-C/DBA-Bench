# Kafka broker startup and cluster connectivity test scripts

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in Azure`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in Azure > Step 1. Set up a Kafka cluster > Deploy a new Kafka cluster > 2. Set up Kafka brokers`
- Source Line Ranges: `178-358`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `shared`
- Topic Tags: `kafka`, `azure`, `private-link`, `broker-configuration`, `startup-script`, `bootstrap-test`, `producer`, `consumer`, `connectivity-validation`, `message-flow`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0283_67ec20a5b3`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md#2-set-up-kafka-brokers`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0421dd9e13b70ab2e7eeee6e3e389966ded36ee2fd5c3376ab1c63b5236d6968`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service#2-set-up-kafka-brokers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when looking for Azure self-hosted Kafka broker server.properties examples, broker startup script content, or bootstrap, producer, and consumer connectivity validation commands for a Kafka cluster used with Private Link Service.
- Retrieval Keywords: server.properties, advertised.listeners, Kafka Advertised Listener Pattern, <broker_id>.abc.eastus.azure.3199745.tidbcloud.com:<port>, b2.abc.eastus.azure.3199745.tidbcloud.com:9094, b3.abc.eastus.azure.3199745.tidbcloud.com:9095, process.roles=broker,controller, node.id=2, node.id=3, controller.quorum.voters, listeners=INTERNAL://0.0.0.0:9092,CONTROLLER://0.0.0.0:29092,EXTERNAL://0.0.0.0:39092, inter.broker.listener.name=INTERNAL, controller.listener.names=CONTROLLER, listener.security.protocol.map, log.dirs=./data, kafka-storage.sh format, kafka-server-start.sh, kafka-broker-api-versions.sh --bootstrap-server, bootstrap from INTERNAL listener, bootstrap from EXTERNAL listener, org.apache.kafka.common.errors.DisconnectException, produce.sh, consume.sh, kafka-topics.sh --create --if-not-exists --partitions 3 --replication-factor 3, kafka-console-producer.sh --broker-list, kafka-console-consumer.sh --bootstrap-server, test-topic, test-group, TimeoutException, Processed a total of 10 messages
- Follow-up Guidance: The chunk also includes expected output for INTERNAL and EXTERNAL bootstrap tests and for running produce.sh and consume.sh against {one_of_broker_ip}:9092.
- Classification Note: This is classified as configuration because the content provides Kafka broker property settings, startup script variables and commands, and validation scripts for cluster connectivity and message flow.

## Official Source Content

```properties
    # broker-node-2 ~/config/server.properties
    # 1. Replace {broker-node-1-ip}, {broker-node-2-ip}, {broker-node-3-ip} with the actual IP addresses.
    # 2. Configure EXTERNAL in "advertised.listeners" based on the "Kafka Advertised Listener Pattern" in the "Prerequisites" section.
    # 2.1 The pattern is "<broker_id>.abc.eastus.azure.3199745.tidbcloud.com:<port>".
    # 2.2 So the EXTERNAL can be "b2.abc.eastus.azure.3199745.tidbcloud.com:9094". Replace <broker_id> with "b" prefix plus "node.id" properties, and replace <port> with a unique port (9094) in the port range of the EXTERNAL advertised listener.
    process.roles=broker,controller
    node.id=2
    controller.quorum.voters=1@{broker-node-1-ip}:29092,2@{broker-node-2-ip}:29092,3@{broker-node-3-ip}:29092
    listeners=INTERNAL://0.0.0.0:9092,CONTROLLER://0.0.0.0:29092,EXTERNAL://0.0.0.0:39092
    inter.broker.listener.name=INTERNAL
    advertised.listeners=INTERNAL://{broker-node-2-ip}:9092,EXTERNAL://b2.abc.eastus.azure.3199745.tidbcloud.com:9094
    controller.listener.names=CONTROLLER
    listener.security.protocol.map=INTERNAL:PLAINTEXT,CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT,SSL:SSL,SASL_PLAINTEXT:SASL_PLAINTEXT,SASL_SSL:SASL_SSL
    log.dirs=./data
    ```

    ```properties
    # broker-node-3 ~/config/server.properties
    # 1. Replace {broker-node-1-ip}, {broker-node-2-ip}, {broker-node-3-ip} with the actual IP addresses.
    # 2. Configure EXTERNAL in "advertised.listeners" based on the "Kafka Advertised Listener Pattern" in the "Prerequisites" section.
    # 2.1 The pattern is "<broker_id>.abc.eastus.azure.3199745.tidbcloud.com:<port>".
    # 2.2 So the EXTERNAL can be "b3.abc.eastus.azure.3199745.tidbcloud.com:9095". Replace <broker_id> with "b" prefix plus "node.id" properties, and replace <port> with a unique port (9095) in the port range of the EXTERNAL advertised listener.
    process.roles=broker,controller
    node.id=3
    controller.quorum.voters=1@{broker-node-1-ip}:29092,2@{broker-node-2-ip}:29092,3@{broker-node-3-ip}:29092
    listeners=INTERNAL://0.0.0.0:9092,CONTROLLER://0.0.0.0:29092,EXTERNAL://0.0.0.0:39092
    inter.broker.listener.name=INTERNAL
    advertised.listeners=INTERNAL://{broker-node-3-ip}:9092,EXTERNAL://b3.abc.eastus.azure.3199745.tidbcloud.com:9095
    controller.listener.names=CONTROLLER
    listener.security.protocol.map=INTERNAL:PLAINTEXT,CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT,SSL:SSL,SASL_PLAINTEXT:SASL_PLAINTEXT,SASL_SSL:SASL_SSL
    log.dirs=./data
    ```

3. Create a script, and then execute it to start the Kafka broker in each broker node.

    ```shell
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    export JAVA_HOME="$SCRIPT_DIR/jdk-22.0.2"
    KAFKA_DIR="$SCRIPT_DIR/kafka_2.13-3.7.1/bin"
    KAFKA_STORAGE_CMD=$KAFKA_DIR/kafka-storage.sh
    KAFKA_START_CMD=$KAFKA_DIR/kafka-server-start.sh
    KAFKA_DATA_DIR=$SCRIPT_DIR/data
    KAFKA_LOG_DIR=$SCRIPT_DIR/log
    KAFKA_CONFIG_DIR=$SCRIPT_DIR/config

    KAFKA_PIDS=$(ps aux | grep 'kafka.Kafka' | grep -v grep | awk '{print $2}')
    if [ -z "$KAFKA_PIDS" ]; then
    echo "No Kafka processes are running."
    else
    echo "Killing Kafka processes with PIDs: $KAFKA_PIDS"
    for PID in $KAFKA_PIDS; do
        kill -9 $PID
        echo "Killed Kafka process with PID: $PID"
    done
    echo "All Kafka processes have been killed."
    fi

    rm -rf $KAFKA_DATA_DIR
    mkdir -p $KAFKA_DATA_DIR
    rm -rf $KAFKA_LOG_DIR
    mkdir -p $KAFKA_LOG_DIR

    $KAFKA_STORAGE_CMD format -t "BRl69zcmTFmiPaoaANybiw" -c "$KAFKA_CONFIG_DIR/server.properties" > $KAFKA_LOG_DIR/server_format.log
    LOG_DIR=$KAFKA_LOG_DIR nohup $KAFKA_START_CMD "$KAFKA_CONFIG_DIR/server.properties" &
    ```

**2.4. Test the cluster setting**

1. Test the Kafka bootstrap.

    ```shell
    export JAVA_HOME=/home/azureuser/jdk-22.0.2

    # Bootstrap from INTERNAL listener
    ./kafka_2.13-3.7.1/bin/kafka-broker-api-versions.sh --bootstrap-server {one_of_broker_ip}:9092 | grep 9092
    # Expected output (the actual order might be different)
    {broker-node-1-ip}:9092 (id: 1 rack: null) -> (
    {broker-node-2-ip}:9092 (id: 2 rack: null) -> (
    {broker-node-3-ip}:9092 (id: 3 rack: null) -> (

    # Bootstrap from EXTERNAL listener
    ./kafka_2.13-3.7.1/bin/kafka-broker-api-versions.sh --bootstrap-server {one_of_broker_ip}:39092
    # Expected output for the last 3 lines (the actual order might be different)
    # The difference in the output from "bootstrap from INTERNAL listener" is that exceptions or errors might occur because advertised listeners cannot be resolved in kafka-pls-vnet.
    # TiDB Cloud will make these addresses resolvable and route requests to the correct broker when you create a changefeed connected to this Kafka cluster via Private Link Service.
    b1.abc.eastus.azure.3199745.tidbcloud.com:9093 (id: 1 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
    b2.abc.eastus.azure.3199745.tidbcloud.com:9094 (id: 2 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
    b3.abc.eastus.azure.3199745.tidbcloud.com:9095 (id: 3 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
    ```

2. Create a producer script `produce.sh` in the bastion node.

    ```shell
    BROKER_LIST=$1

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    export JAVA_HOME="$SCRIPT_DIR/jdk-22.0.2"
    KAFKA_DIR="$SCRIPT_DIR/kafka_2.13-3.7.1/bin"
    TOPIC="test-topic"

    create_topic() {
        echo "Creating topic if it does not exist..."
        $KAFKA_DIR/kafka-topics.sh --create --topic $TOPIC --bootstrap-server $BROKER_LIST --if-not-exists --partitions 3 --replication-factor 3
    }

    produce_messages() {
        echo "Producing messages to the topic..."
        for ((chrono=1; chrono <= 10; chrono++)); do
            message="Test message "$chrono
            echo "Create "$message
            echo $message | $KAFKA_DIR/kafka-console-producer.sh --broker-list $BROKER_LIST --topic $TOPIC
        done
    }
    create_topic
    produce_messages
    ```

3. Create a consumer script `consume.sh` in the bastion node.

    ```shell
    BROKER_LIST=$1
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    export JAVA_HOME="$SCRIPT_DIR/jdk-22.0.2"
    KAFKA_DIR="$SCRIPT_DIR/kafka_2.13-3.7.1/bin"
    TOPIC="test-topic"
    CONSUMER_GROUP="test-group"
    consume_messages() {
        echo "Consuming messages from the topic..."
        $KAFKA_DIR/kafka-console-consumer.sh --bootstrap-server $BROKER_LIST --topic $TOPIC --from-beginning --timeout-ms 5000 --consumer-property group.id=$CONSUMER_GROUP
    }
    consume_messages
    ```

4. Run the `produce.sh` and `consume.sh` scripts. These scripts automatically test connectivity and message flow to verify that the Kafka cluster is functioning correctly. The `produce.sh` script creates a topic with `--partitions 3 --replication-factor 3`, sends test messages, and connects to all three brokers using the `--broker-list` parameter. The `consume.sh` script reads messages from the topic to confirm successful message delivery.

    ```shell
    # Test write message.
    ./produce.sh {one_of_broker_ip}:9092
    ```
    ```shell
    # Expected output
    Creating topic if it does not exist...

    Producing messages to the topic...
    Create Test message 1
    >>Create Test message 2
    >>Create Test message 3
    >>Create Test message 4
    >>Create Test message 5
    >>Create Test message 6
    >>Create Test message 7
    >>Create Test message 8
    >>Create Test message 9
    >>Create Test message 10
    ```

    ```shell
    # Test read message
    ./consume.sh {one_of_broker_ip}:9092
    ```

    ```shell
    # Expected example output (the actual message order might be different)
    Consuming messages from the topic...
    Test message 3
    Test message 4
    Test message 5
    Test message 9
    Test message 10
    Test message 6
    Test message 8
    Test message 1
    Test message 2
    Test message 7
    [2024-11-01 08:54:27,547] ERROR Error processing message, terminating consumer process:  (kafka.tools.ConsoleConsumer$)
    org.apache.kafka.common.errors.TimeoutException
    Processed a total of 10 messages
    ```
