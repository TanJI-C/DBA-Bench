# Azure Kafka broker node creation and initial KRaft listener configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in Azure`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in Azure > Step 1. Set up a Kafka cluster > Deploy a new Kafka cluster > 2. Set up Kafka brokers`
- Source Line Ranges: `83-177`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `azure`, `kafka`, `private-link`, `broker`, `virtual-machine`, `kraft`, `listeners`, `advertised-listeners`, `networking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0282_3c3e76cc6b`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md#2-set-up-kafka-brokers`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `564b409245e6eaf2e8a356f7d8d6cc4ed0573d22cb9ff7bb8cb95feb838cd93b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service#2-set-up-kafka-brokers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving Azure setup details for Kafka broker virtual machines and the initial KRaft `server.properties` listener and `advertised.listeners` configuration for a self-hosted Kafka Private Link service.
- Retrieval Keywords: Azure virtual machine, broker-node, broker-node-1, broker-node-2, broker-node-3, Ubuntu Server 24.04 LTS - x64 Gen2, Standard_D2s_v3, azureuser, kafka_broker_key, kafka-pls-vnet, brokers-subnet, Bastion, wget https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz, openjdk-22.0.2_linux-x64_bin.tar.gz, KRaft Kafka cluster, process.roles=broker,controller, node.id=1, controller.quorum.voters, listeners=INTERNAL://0.0.0.0:9092,CONTROLLER://0.0.0.0:29092,EXTERNAL://0.0.0.0:39092, inter.broker.listener.name=INTERNAL, advertised.listeners, Kafka Advertised Listener Pattern, b1.abc.eastus.azure.3199745.tidbcloud.com:9093, controller.listener.names=CONTROLLER, listener.security.protocol.map, CONTROLLER port 29092, INTERNAL port 9092, EXTERNAL port 39092, EXTERNAL advertised listener ports 9093~9095
- Follow-up Guidance: The source continues with per-broker `~/config/server.properties` content where `{broker-node-1-ip}`, `{broker-node-2-ip}`, and `{broker-node-3-ip}` are replaced with actual IP addresses and the EXTERNAL advertised listener is derived from the TiDB Cloud Kafka Advertised Listener Pattern.
- Classification Note: The official content is classified as configuration because it specifies Azure VM creation parameters, Kafka runtime binary preparation, and exact KRaft broker listener properties in `server.properties`.

## Official Source Content

#### 2. Set up Kafka brokers

**2.1. Create broker nodes**

1. Log in to the [Azure portal](https://portal.azure.com/), go to the [Virtual machines](https://portal.azure.com/#view/Microsoft_Azure_ComputeHub/ComputeHubMenuBlade/~/virtualMachinesBrowse) page, click **+ Create**, and then select **Azure virtual machine**.
2. In the **Basic** tab, select your **Subscription**, **Resource group**, and **Region**, fill in the following information, and then click **Next : Disks**.
    - **Virtual machine name**: `broker-node`
    - **Availability options**: `Availability zone`
    - **Zone options**: `Self-selected zone`
    - **Availability zone**: `Zone 1`, `Zone 2`, `Zone 3`
    - **Image**: `Ubuntu Server 24.04 LTS - x64 Gen2`
    - **VM architecture:** `x64`
    - **Size**: `Standard_D2s_v3`
    - **Authentication type**: `SSH public key`
    - **Username**: `azureuser`
    - **SSH public key source:** `Generate new key pair`
    - **Key pair name**: `kafka_broker_key`
    - **Public inbound ports**: `Allow selected ports`
    - **Select inbound ports**: `SSH (22)`
3. Click **Next : Networking**, and then fill in the following information in the **Networking** tab:
    - **Virtual network**: `kafka-pls-vnet`
    - **Subnet**: `brokers-subnet`
    - **Public IP**: `None`
    - **NIC network security group**: `Basic`
    - **Public inbound ports**: `Allow selected ports`
    - Select inbound ports: `SSH (22)`
    - **Load balancing options**: `None`
4. Click **Review + create** to verify the information.
5. Click **Create**. A **Generate new key pair** message is displayed.
6. Click **Download private key and create resource** to download the private key to your local machine. You can see the progress of virtual machine creation.

**2.2. Prepare Kafka runtime binaries**

After the deployment of your virtual machine is completed, take the following steps:

1. In the [Azure portal](https://portal.azure.com/), go to the [**Resource groups**](https://portal.azure.com/#view/HubsExtension/BrowseResourceGroups.ReactView) page, click your resource group name, and then navigate to the page of each broker node (`broker-node-1`, `broker-node-2`, and `broker-node-3`).

2. On each page of the broker node, click **Connect > Bastion** in the left navigation pane, and then fill in the following information:

    - **Authentication Type**: `SSH Private Key from Local File`
    - **Username**: `azureuser`
    - **Local File**: select the private key file that you downloaded before
    - Select the **Open in new browser tab** option

3. On each page of the broker node, click **Connect** to open a new browser tab with a Linux terminal. For the three broker nodes, you need to open three browser tabs with Linux terminals.

4. In each Linux terminal, run the following commands to download binaries in each broker node.

    ```shell
    # Download Kafka and OpenJDK, and then extract the files. You can choose the binary version based on your preference.
    wget https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz
    tar -zxf kafka_2.13-3.7.1.tgz
    wget https://download.java.net/java/GA/jdk22.0.2/c9ecb94cd31b495da20a27d4581645e8/9/GPL/openjdk-22.0.2_linux-x64_bin.tar.gz
    tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz
    ```

**2.3. Set up Kafka nodes on each broker node**

1. Set up a KRaft Kafka cluster with three nodes. Each node serves both as a broker and a controller. For each broker node:

    1. Configure `listeners`. All three brokers are the same and act as brokers and controller roles.
        1. Configure the same CONTROLLER listener for all **controller** role nodes. If you only want to add the broker role nodes, you can omit the CONTROLLER listener in `server.properties`.
        2. Configure two broker listeners: **INTERNAL** for internal Kafka client access and **EXTERNAL** for access from TiDB Cloud.

    2. For `advertised.listeners`, do the following:
        1. Configure an INTERNAL advertised listener for each broker using the internal IP address of the broker node, which allows internal Kafka clients to connect to the broker via the advertised address.
        2. Configure an EXTERNAL advertised listener based on **Kafka Advertised Listener Pattern** you get from TiDB Cloud for each broker node to help TiDB Cloud distinguish between different brokers. Different EXTERNAL advertised listeners help Kafka clients from the TiDB Cloud side route requests to the right broker.
            - Use different `<port>` values to differentiate brokers in Kafka Private Link service access. Plan a port range for the EXTERNAL advertised listeners of all brokers. These ports do not have to be actual ports listened to by brokers. They are ports listened to by the load balancer in the Private Link service that will forward requests to different brokers.
            - It is recommended to configure different broker IDs for different brokers to make it easy for troubleshooting.

    3. The planning values:
        - CONTROLLER port: `29092`
        - INTERNAL port: `9092`
        - EXTERNAL port: `39092`
        - Range of the EXTERNAL advertised listener ports: `9093~9095`

2. Use SSH to log in to each broker node. Create a configuration file `~/config/server.properties` with the following content for each broker node respectively.

    ```properties
    # broker-node-1 ~/config/server.properties
    # 1. Replace {broker-node-1-ip}, {broker-node-2-ip}, {broker-node-3-ip} with the actual IP addresses.
    # 2. Configure EXTERNAL in "advertised.listeners" based on the "Kafka Advertised Listener Pattern" in the "Prerequisites" section.
    # 2.1 The pattern is "<broker_id>.abc.eastus.azure.3199745.tidbcloud.com:<port>".
    # 2.2 So the EXTERNAL can be "b1.abc.eastus.azure.3199745.tidbcloud.com:9093". Replace <broker_id> with "b" prefix plus "node.id" properties, and replace <port> with a unique port (9093) in the port range of the EXTERNAL advertised listener.
    process.roles=broker,controller
    node.id=1
    controller.quorum.voters=1@{broker-node-1-ip}:29092,2@{broker-node-2-ip}:29092,3@{broker-node-3-ip}:29092
    listeners=INTERNAL://0.0.0.0:9092,CONTROLLER://0.0.0.0:29092,EXTERNAL://0.0.0.0:39092
    inter.broker.listener.name=INTERNAL
    advertised.listeners=INTERNAL://{broker-node-1-ip}:9092,EXTERNAL://b1.abc.eastus.azure.3199745.tidbcloud.com:9093
    controller.listener.names=CONTROLLER
    listener.security.protocol.map=INTERNAL:PLAINTEXT,CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT,SSL:SSL,SASL_PLAINTEXT:SASL_PLAINTEXT,SASL_SSL:SASL_SSL
    log.dirs=./data
    ```
