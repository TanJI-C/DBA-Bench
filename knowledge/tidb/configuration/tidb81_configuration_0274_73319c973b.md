# Deploy Kafka brokers and prepare KRaft configuration on AWS

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in AWS`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in AWS > Step 1. Set up a Kafka cluster > Deploy a new Kafka cluster > 2. Set up Kafka brokers`
- Source Line Ranges: `150-292`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `ecosystem`
- Topic Tags: `aws`, `kafka`, `private-link`, `ec2`, `bastion`, `broker`, `kraft`, `listeners`, `advertised-listeners`, `networking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0274_73319c973b`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md#2-set-up-kafka-brokers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2065e5b466ef0aea234ecc478bcd9df55c44ce15f07fe14eab6536f2c6cdbf7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service#2-set-up-kafka-brokers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the AWS EC2 setup details and KRaft listener planning for a self-hosted Kafka cluster behind a Private Link Service for TiDB Cloud.
- Retrieval Keywords: bastion-node, broker-node1, broker-node2, broker-node3, Kafka VPC, bastion subnet, broker-usw2-az1, broker-usw2-az2, broker-usw2-az3, kafka-vpc-key-pair.pem, Amazon linux, t2.small, t2.large, allow all TCP from Kafka VPC, 10.0.0.0/16, kafka_2.13-3.7.1.tgz, openjdk-22.0.2_linux-x64_bin.tar.gz, KRaft Kafka cluster with three nodes, listeners, advertised.listeners, CONTROLLER, INTERNAL, EXTERNAL, Kafka Advertised Listener Pattern, CONTROLLER port 29092, INTERNAL port 9092, EXTERNAL 39092, EXTERNAL advertised listener ports range 9093~9095, server.properties
- Follow-up Guidance: The next step in the source is to SSH to every broker node and create the configuration file `~/config/server.properties`.
- Classification Note: This chunk is classified as configuration because it provides concrete AWS instance settings, network parameters, binary preparation commands, and Kafka KRaft listener and advertised listener planning values.

## Official Source Content

#### 2. Set up Kafka brokers

**2.1. Create a bastion node**

Go to the [EC2 Listing page](https://console.aws.amazon.com/ec2/home#Instances:). Create the bastion node in the bastion subnet.

- **Name**: `bastion-node`
- **Amazon Machine Image**: `Amazon linux`
- **Instance Type**: `t2.small`
- **Key pair**: `kafka-vpc-key-pair`. Create a new key pair named `kafka-vpc-key-pair`. Download **kafka-vpc-key-pair.pem** to your local for later configuration.
- Network settings

    - **VPC**: `Kafka VPC`
    - **Subnet**: `bastion`
    - **Auto-assign public IP**: `Enable`
    - **Security Group**: create a new security group allow SSH login from anywhere. You can narrow the rule for safety in the production environment.

**2.2. Create broker nodes**

Go to the [EC2 Listing page](https://console.aws.amazon.com/ec2/home#Instances:). Create three broker nodes in broker subnets, one for each AZ.

- Broker 1 in subnet `broker-usw2-az1`

    - **Name**: `broker-node1`
    - **Amazon Machine Image**: `Amazon linux`
    - **Instance Type**: `t2.large`
    - **Key pair**: reuse `kafka-vpc-key-pair`
    - Network settings

        - **VPC**: `Kafka VPC`
        - **Subnet**: `broker-usw2-az1`
        - **Auto-assign public IP**: `Disable`
        - **Security Group**: create a new security group to allow all TCP from Kafka VPC. You can narrow the rule for safety in the production environment.
            - **Protocol**: `TCP`
            - **Port range**: `0 - 65535`
            - **Source**: `10.0.0.0/16`

- Broker 2 in subnet `broker-usw2-az2`

    - **Name**: `broker-node2`
    - **Amazon Machine Image**: `Amazon linux`
    - **Instance Type**: `t2.large`
    - **Key pair**: reuse `kafka-vpc-key-pair`
    - Network settings

        - **VPC**: `Kafka VPC`
        - **Subnet**: `broker-usw2-az2`
        - **Auto-assign public IP**: `Disable`
        - **Security Group**: create a new security group to allow all TCP from Kafka VPC. You can narrow the rule for safety in the production environment.
            - **Protocol**: `TCP`
            - **Port range**: `0 - 65535`
            - **Source**: `10.0.0.0/16`

- Broker 3 in subnet `broker-usw2-az3`

    - **Name**: `broker-node3`
    - **Amazon Machine Image**: `Amazon linux`
    - **Instance Type**: `t2.large`
    - **Key pair**: reuse `kafka-vpc-key-pair`
    - Network settings

        - **VPC**: `Kafka VPC`
        - **Subnet**: `broker-usw2-az3`
        - **Auto-assign public IP**: `Disable`
        - **Security Group**: create a new security group to allow all TCP from Kafka VPC. You can narrow the rule for safety in the production environment.
            - **Protocol**: `TCP`
            - **Port range**: `0 - 65535`
            - **Source**: `10.0.0.0/16`

**2.3. Prepare Kafka runtime binaries**

1. Go to the detail page of the bastion node. Get the **Public IPv4 address**. Use SSH to log in to the node with the previously downloaded `kafka-vpc-key-pair.pem`.

    ```shell
    chmod 400 kafka-vpc-key-pair.pem
    ssh -i "kafka-vpc-key-pair.pem" ec2-user@{bastion_public_ip} # replace {bastion_public_ip} with the IP address of your bastion node, for example, 54.186.149.187
    scp -i "kafka-vpc-key-pair.pem" kafka-vpc-key-pair.pem ec2-user@{bastion_public_ip}:~/
    ```

2. Download binaries.

    ```shell
    # Download Kafka and OpenJDK, and then extract the files. You can choose the binary version based on your preference.
    wget https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz
    tar -zxf kafka_2.13-3.7.1.tgz
    wget https://download.java.net/java/GA/jdk22.0.2/c9ecb94cd31b495da20a27d4581645e8/9/GPL/openjdk-22.0.2_linux-x64_bin.tar.gz
    tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz
    ```

3. Copy binaries to each broker node.

    ```shell
    # Replace {broker-node1-ip} with your broker-node1 IP address
    scp -i "kafka-vpc-key-pair.pem" kafka_2.13-3.7.1.tgz ec2-user@{broker-node1-ip}:~/
    ssh -i "kafka-vpc-key-pair.pem" ec2-user@{broker-node1-ip} "tar -zxf kafka_2.13-3.7.1.tgz"
    scp -i "kafka-vpc-key-pair.pem" openjdk-22.0.2_linux-x64_bin.tar.gz ec2-user@{broker-node1-ip}:~/
    ssh -i "kafka-vpc-key-pair.pem" ec2-user@{broker-node1-ip} "tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz"

    # Replace {broker-node2-ip} with your broker-node2 IP address
    scp -i "kafka-vpc-key-pair.pem" kafka_2.13-3.7.1.tgz ec2-user@{broker-node2-ip}:~/
    ssh -i "kafka-vpc-key-pair.pem" ec2-user@{broker-node2-ip} "tar -zxf kafka_2.13-3.7.1.tgz"
    scp -i "kafka-vpc-key-pair.pem" openjdk-22.0.2_linux-x64_bin.tar.gz ec2-user@{broker-node2-ip}:~/
    ssh -i "kafka-vpc-key-pair.pem" ec2-user@{broker-node2-ip} "tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz"

    # Replace {broker-node3-ip} with your broker-node3 IP address
    scp -i "kafka-vpc-key-pair.pem" kafka_2.13-3.7.1.tgz ec2-user@{broker-node3-ip}:~/
    ssh -i "kafka-vpc-key-pair.pem" ec2-user@{broker-node3-ip} "tar -zxf kafka_2.13-3.7.1.tgz"
    scp -i "kafka-vpc-key-pair.pem" openjdk-22.0.2_linux-x64_bin.tar.gz ec2-user@{broker-node3-ip}:~/
    ssh -i "kafka-vpc-key-pair.pem" ec2-user@{broker-node3-ip} "tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz"
    ```

**2.4. Set up Kafka nodes on each broker node**

**2.4.1 Set up a KRaft Kafka cluster with three nodes**

Each node will act as a broker and controller role. Do the following for each broker:

1. For the `listeners` item, all three brokers are the same and act as broker and controller roles: 

    1. Configure the same CONTROLLER listener for all **controller** role nodes. If you only want to add the **broker** role nodes, you do not need the CONTROLLER listener in `server.properties`.
    2. Configure two **broker** listeners, `INTERNAL` for internal access and `EXTERNAL` for external access from TiDB Cloud.

2. For the `advertised.listeners` item, do the following:

    1. Configure an INTERNAL advertised listener for every broker with the internal IP of the broker node. Advertised internal Kafka clients use this address to visit the broker.
    2. Configure an EXTERNAL advertised listener based on **Kafka Advertised Listener Pattern** you get from TiDB Cloud for each broker node to help TiDB Cloud differentiate between different brokers. Different EXTERNAL advertised listeners help the Kafka client from TiDB Cloud route requests to the right broker.

        - `<port>` differentiates brokers from Kafka Private Link Service access points. Plan a port range for EXTERNAL advertised listeners of all brokers. These ports do not have to be actual ports listened to by brokers. They are ports listened to by the load balancer for Private Link Service that will forward requests to different brokers.
        - `AZ ID` in **Kafka Advertised Listener Pattern** indicates where the broker is deployed. TiDB Cloud will route requests to different endpoint DNS names based on the AZ ID.
     
      It is recommended to configure different broker IDs for different brokers to make it easy for troubleshooting.

3. The planning values are as follows:

    - **CONTROLLER port**: `29092`
    - **INTERNAL port**: `9092`
    - **EXTERNAL**: `39092`
    - **EXTERNAL advertised listener ports range**: `9093~9095`

**2.4.2. Create a configuration file**

Use SSH to log in to every broker node. Create a configuration file `~/config/server.properties` with the following content.
