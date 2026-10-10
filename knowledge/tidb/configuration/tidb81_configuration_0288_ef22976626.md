# Deploy new Kafka cluster for PSC port mapping

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md`
- Source Title: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > Set up self-hosted Kafka Private Service Connect service by PSC port mapping > Step 1. Set up the Kafka cluster > Deploy a new Kafka cluster`
- Source Line Ranges: `74-204`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `kafka`, `private-service-connect`, `google-cloud`, `vpc`, `vm-provisioning`, `broker-configuration`, `kraft`, `advertised-listeners`, `port-mapping`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0288_ef22976626`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-self-hosted-kafka-private-service-connect.md#deploy-a-new-kafka-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4a57e1da82c35238c2bbbdb7764ad0ec457f54d14d27cb5f6576f0cfdbed1d1f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect#deploy-a-new-kafka-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md

## Retrieval Guidance

- Use When: Use this chunk when setting up a self-hosted Kafka cluster in Google Cloud for Private Service Connect port mapping, including VPC, VM provisioning, Kafka binary distribution, and broker listener configuration.
- Retrieval Keywords: Private Service Connect port mapping, self-hosted Kafka, Google Cloud, kafka-vpc, bastion-subnet, brokers-subnet, bastion-node, broker-node1, broker-node2, broker-node3, Debian GNU/Linux 12, gcloud compute scp, gcloud compute ssh, Kafka 3.7.1, OpenJDK 22.0.2, KRaft Kafka cluster, process.roles=broker,controller, controller.quorum.voters, listeners=INTERNAL://0.0.0.0:9092,CONTROLLER://0.0.0.0:29092,EXTERNAL://0.0.0.0:39092, advertised.listeners, Kafka Advertised Listener Pattern, b1.abc.us-west1.gcp.3199745.tidbcloud.com:9093, controller.listener.names=CONTROLLER, inter.broker.listener.name=INTERNAL, listener.security.protocol.map, EXTERNAL advertised listener ports range 9093~9095
- Follow-up Guidance: The chunk continues with per-broker `~/config/server.properties` creation using actual broker IP addresses and EXTERNAL advertised listeners based on the Kafka Advertised Listener Pattern from TiDB Cloud.
- Classification Note: The classification is configuration because the content defines concrete Google Cloud network and VM attributes, binary transfer commands, and Kafka `server.properties` settings for brokers and controllers.

## Official Source Content

#### Deploy a new Kafka cluster

**1. Set up the Kafka VPC**

You need to create two subnets for Kafka VPC, one for Kafka brokers, and the other for the bastion node to make it easy to configure the Kafka cluster.

Go to the [Google Cloud console](https://cloud.google.com/cloud-console), and navigate to the [VPC networks](https://console.cloud.google.com/networking/networks/list) page to create the Kafka VPC with the following attributes:

- **Name**: `kafka-vpc`
- Subnets
    - **Name**: `bastion-subnet`; **Region**: `us-west1`; **IPv4 range**: `10.0.0.0/18`
    - **Name**: `brokers-subnet`; **Region**: `us-west1`; **IPv4 range**: `10.64.0.0/18`
- Firewall rules
    - `kafka-vpc-allow-custom`
    - `kafka-vpc-allow-ssh`

**2. Provisioning VMs**

Go to the [VM instances](https://console.cloud.google.com/compute/instances) page to provision VMs:

1. Bastion node

    - **Name**: `bastion-node`
    - **Region**: `us-west1`
    - **Zone**: `Any`
    - **Machine Type**: `e2-medium`
    - **Image**: `Debian GNU/Linux 12`
    - **Network**: `kafka-vpc`
    - **Subnetwork**: `bastion-subnet`
    - **External IPv4 address**: `Ephemeral`

2. Broker node 1

    - **Name**: `broker-node1`
    - **Region**: `us-west1`
    - **Zone**: `us-west1-a`
    - **Machine Type**: `e2-medium`
    - **Image**: `Debian GNU/Linux 12`
    - **Network**: `kafka-vpc`
    - **Subnetwork**: `brokers-subnet`
    - **External IPv4 address**: `None`

3. Broker node 2

    - **Name**: `broker-node2`
    - **Region**: `us-west1`
    - **Zone**: `us-west1-b`
    - **Machine Type**: `e2-medium`
    - **Image**: `Debian GNU/Linux 12`
    - **Network**: `kafka-vpc`
    - **Subnetwork**: `brokers-subnet`
    - **External IPv4 address**: `None`

4. Broker node 3

    - **Name**: `broker-node3`
    - **Region**: `us-west1`
    - **Zone**: `us-west1-c`
    - **Machine Type**: `e2-medium`
    - **Image**: `Debian GNU/Linux 12`
    - **Network**: `kafka-vpc`
    - **Subnetwork**: `brokers-subnet`
    - **External IPv4 address**: `None`

**3. Prepare Kafka runtime binaries**

1. Go to the detail page of the bastion node. Click **SSH** to log in to the bastion node. Download binaries.

    ```shell
    # Download Kafka and OpenJDK, and then extract the files. You can choose the binary version based on your preference.
    wget https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz
    tar -zxf kafka_2.13-3.7.1.tgz
    wget https://download.java.net/java/GA/jdk22.0.2/c9ecb94cd31b495da20a27d4581645e8/9/GPL/openjdk-22.0.2_linux-x64_bin.tar.gz
    tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz
    ```

2. Copy binaries to each broker node.

    ```shell
    # Run this command to authorize gcloud to access the Cloud Platform with Google user credentials
    # Follow the instruction in output to finish the login
    gcloud auth login

    # Copy binaries to broker nodes
    gcloud compute scp kafka_2.13-3.7.1.tgz openjdk-22.0.2_linux-x64_bin.tar.gz broker-node1:~ --zone=us-west1-a
    gcloud compute ssh broker-node1 --zone=us-west1-a --command="tar -zxf kafka_2.13-3.7.1.tgz && tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz"
    gcloud compute scp kafka_2.13-3.7.1.tgz openjdk-22.0.2_linux-x64_bin.tar.gz broker-node2:~ --zone=us-west1-b
    gcloud compute ssh broker-node2 --zone=us-west1-b --command="tar -zxf kafka_2.13-3.7.1.tgz && tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz"
    gcloud compute scp kafka_2.13-3.7.1.tgz openjdk-22.0.2_linux-x64_bin.tar.gz broker-node3:~ --zone=us-west1-c
    gcloud compute ssh broker-node3 --zone=us-west1-c --command="tar -zxf kafka_2.13-3.7.1.tgz && tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz"
    ```

**4. Configure Kafka brokers**

1. Set up a KRaft Kafka cluster with three nodes. Each node acts as a broker and controller roles. For every broker:

    1. For `listeners`, all three brokers are the same and act as brokers and controller roles:
        1. Configure the same CONTROLLER listener for all **controller** role nodes. If you only want to add the **broker** role nodes, you do not need the CONTROLLER listener in `server.properties`.
        2. Configure two **broker** listeners. INTERNAL for internal access; EXTERNAL for external access from TiDB Cloud.
    
    2. For `advertised.listeners`, do the following:
        1. Configure an INTERNAL advertised listener for each broker using the internal IP address of the broker node, which allows internal Kafka clients to connect to the broker via the advertised address.
        2. Configure an EXTERNAL advertised listener based on **Kafka Advertised Listener Pattern** you get from TiDB Cloud for every broker node to help TiDB Cloud differentiate between different brokers. Different EXTERNAL advertised listeners help Kafka clients from TiDB Cloud side route requests to the right broker.
            - `<port>` differentiates brokers from Kafka Private Service Connect access points. Plan a port range for EXTERNAL advertised listeners of all brokers. These ports do not have to be actual ports listened to by brokers. They are ports listened to by the load balancer for Private Service Connect that will forward requests to different brokers.
            - It is recommended to configure different broker IDs for different brokers to make it easy for troubleshooting.
    
    3. The planning values:
        - CONTROLLER port: `29092`
        - INTERNAL port: `9092`
        - EXTERNAL: `39092`
        - EXTERNAL advertised listener ports range: `9093~9095`

2. Use SSH to log in to every broker node. Create a configuration file `~/config/server.properties` with the following content for each broker node respectively.

    ```properties
    # broker-node1 ~/config/server.properties
    # 1. Replace {broker-node1-ip}, {broker-node2-ip}, {broker-node3-ip} with the actual IP addresses.
    # 2. Configure EXTERNAL in "advertised.listeners" based on the "Kafka Advertised Listener Pattern" in the "Prerequisites" section.
    # 2.1 The pattern is "<broker_id>.abc.us-west1.gcp.3199745.tidbcloud.com:<port>".
    # 2.2 So the EXTERNAL can be "b1.abc.us-west1.gcp.3199745.tidbcloud.com:9093". Replace <broker_id> with "b" prefix plus "node.id" properties, and replace <port> with a unique port (9093) in the port range of the EXTERNAL advertised listener.
    process.roles=broker,controller
    node.id=1
    controller.quorum.voters=1@{broker-node1-ip}:29092,2@{broker-node2-ip}:29092,3@{broker-node3-ip}:29092
    listeners=INTERNAL://0.0.0.0:9092,CONTROLLER://0.0.0.0:29092,EXTERNAL://0.0.0.0:39092
    inter.broker.listener.name=INTERNAL
    advertised.listeners=INTERNAL://{broker-node1-ip}:9092,EXTERNAL://b1.abc.us-west1.gcp.3199745.tidbcloud.com:9093
    controller.listener.names=CONTROLLER
    listener.security.protocol.map=INTERNAL:PLAINTEXT,CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT,SSL:SSL,SASL_PLAINTEXT:SASL_PLAINTEXT,SASL_SSL:SASL_SSL
    log.dirs=./data
    ```
