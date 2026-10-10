# Kafka-proxy PSC setup and TiDB Cloud connection

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md`
- Source Title: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > Set up self-hosted Kafka Private Service Connect by Kafka-proxy > Step 1. Set up Kafka-proxy | Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > Set up self-hosted Kafka Private Service Connect by Kafka-proxy > Step 2. Expose Kafka-proxy as Private Service Connect Service | Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > Set up self-hosted Kafka Private Service Connect by Kafka-proxy > Step 3. Connect from TiDB Cloud`
- Source Line Ranges: `552-685`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `ecosystem`
- Topic Tags: `private-service-connect`, `kafka`, `kafka-proxy`, `load-balancer`, `service-attachment`, `firewall`, `changefeed`, `bootstrap-ports`, `advertised-listeners`, `google-cloud`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0292_3900e037a5`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-self-hosted-kafka-private-service-connect.md#step-1-set-up-kafka-proxy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9a472d533dc4d788bc61779c7e3dc074b9948dd449ceb4b7d5d02d71455c3d43`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect#step-1-set-up-kafka-proxy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented Google Cloud and TiDB Cloud values for setting up self-hosted Kafka Private Service Connect by Kafka-proxy, including Kafka-proxy flags, internal passthrough Network Load Balancer, Service attachment, firewall rule, and changefeed connectivity fields.
- Retrieval Keywords: kafka-proxy-ig, kafka-proxy-tpl, kafka-proxy server, --bootstrap-server-mapping, --dynamic-sequential-min-port, --dynamic-advertised-listener, b1.abc.us-west1.gcp.3199745.tidbcloud.com:9092, brokers.abc.us-west1.gcp.3199745.tidbcloud.com, kafka-broker-api-versions.sh --bootstrap-server 0.0.0.0:9092, org.apache.kafka.common.errors.DisconnectException, kafka-proxy-lb, Internal passthrough Network Load Balancer, kafka-proxy-hc, kafka-proxy-psc, proxy-psc-subnet, Service attachment, allow-proxy-psc-traffic, Private Service Connect, Kafka Advertised Listener Pattern, Bootstrap Ports 9092,9093,9094, Configure the changefeed target, Connectivity Method
- Follow-up Guidance: The source then says to continue with the guideline in Sink to Apache Kafka after filling Kafka Advertised Listener Pattern, Service Attachment, and Bootstrap Ports in the TiDB Cloud changefeed configuration.
- Classification Note: This is classified as configuration because the content provides concrete setup parameters and named resources for Kafka-proxy, load balancing, Private Service Connect publishing, firewall rules, and TiDB Cloud changefeed connectivity.

## Official Source Content

### Step 1. Set up Kafka-proxy

Assume that you already have a Kafka cluster running in the same region as the TiDB cluster. You can connect to the Kafka cluster from your VPC network. The Kafka cluster can be self-hosted or provided by third-party providers, such as Confluent.

1. Go to the [Instance groups](https://console.cloud.google.com/compute/instanceGroups/list) page, and create an instance group for Kafka-proxy.

    - **Name**: `kafka-proxy-ig`
    - Instance template:
        - **Name**: `kafka-proxy-tpl`
        - **Location**: `Regional`
        - **Region**: `us-west1`
        - **Machine type**: `e2-medium`. You can choose your own machine type based on your workload.
        - **Network**: your VPC network that can connect to the Kafka cluster.
        - **Subnetwork**: your subnet that can connect to the Kafka cluster.
        - **External IPv4 address**: `Ephemeral`. Enable Internet access to make it easy to configure Kafka-proxy. You can select **None** in your production environment and log in to the node in your way.
    - **Location**: `Single zone`
    - **Region**: `us-west1`
    - **Zone**: choose one of your broker's zones.
    - **Autoscaling mode**: `Off`
    - **Minimum number of instances**: `1`
    - **Maximum number of instances**: `1`. Kafka-proxy does not support the cluster mode, so only one instance can be deployed. Each Kafka-proxy randomly maps local ports to the ports of the broker, resulting in different mappings across proxies. Deploying multiple Kafka-proxies behind a load balancer can cause issues. If a Kafka client connects to one proxy and then accesses a broker through another, the request might be routed to the wrong broker.

2. Go to the detail page of the node in kafka-proxy-ig. Click **SSH** to log in to the node. Download the binaries:

    ```shell
    # You can choose another version 
    wget https://github.com/grepplabs/kafka-proxy/releases/download/v0.3.11/kafka-proxy-v0.3.11-linux-amd64.tar.gz
    tar -zxf kafka-proxy-v0.3.11-linux-amd64.tar.gz
    ```

3. Run Kafka-proxy and connect to Kafka brokers.

    ```shell
    # There are three kinds of parameters that need to feed to the Kafka-proxy
    # 1. --bootstrap-server-mapping defines the bootstrap mapping. Suggest that you configure three mappings, one for each zone for resilience.
    #   a) Kafka broker address; 
    #   b) Local address for the broker in Kafka-proxy; 
    #   c) Advertised listener for the broker if Kafka clients bootstrap from Kafka-proxy
    # 2. --dynamic-sequential-min-port defines the start port of the random mapping for other brokers
    # 3. --dynamic-advertised-listener defines advertised listener address for other brokers based on the pattern obtained from the "Prerequisites" section
    #   a) The pattern: <broker_id>.abc.us-west1.gcp.3199745.tidbcloud.com:<port>
    #   b) Make sure to replace <broker_id> with a fixed lowercase string, for example, "brokers". You can use your own string. This step will help TiDB Cloud route requests properly.
    #   c) Remove ":<port>"
    #   d) The advertised listener address would be: brokers.abc.us-west1.gcp.3199745.tidbcloud.com
    ./kafka-proxy server \
            --bootstrap-server-mapping "{address_of_broker1},0.0.0.0:9092,b1.abc.us-west1.gcp.3199745.tidbcloud.com:9092" \
            --bootstrap-server-mapping "{address_of_broker2},0.0.0.0:9093,b2.abc.us-west1.gcp.3199745.tidbcloud.com:9093" \
            --bootstrap-server-mapping "{address_of_broker3},0.0.0.0:9094,b3.abc.us-west1.gcp.3199745.tidbcloud.com:9094" \
            --dynamic-sequential-min-port=9095 \
            --dynamic-advertised-listener=brokers.abc.us-west1.gcp.3199745.tidbcloud.com > ./kafka_proxy.log 2>&1 &
    ```

4. Test bootstrap in the Kafka-proxy node.

    ```shell
    # Download Kafka and OpenJDK, and then extract the files. You can choose the binary version based on your preference.
    wget https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz
    tar -zxf kafka_2.13-3.7.1.tgz
    wget https://download.java.net/java/GA/jdk22.0.2/c9ecb94cd31b495da20a27d4581645e8/9/GPL/openjdk-22.0.2_linux-x64_bin.tar.gz
    tar -zxf openjdk-22.0.2_linux-x64_bin.tar.gz

    export JAVA_HOME=~/jdk-22.0.2

    ./kafka_2.13-3.7.1/bin/kafka-broker-api-versions.sh --bootstrap-server 0.0.0.0:9092
    # Expected output of the last few lines (the actual order might be different)
    # There might be exceptions or errors because advertised listeners cannot be resolved in your network.
    # We will make them resolvable in TiDB Cloud side and make it route to the right broker when you create a changefeed connect to this Kafka cluster by Private Service Connect. 
    b1.abc.us-west1.gcp.3199745.tidbcloud.com:9092 (id: 1 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
    b2.abc.us-west1.gcp.3199745.tidbcloud.com:9093 (id: 2 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
    b3.abc.us-west1.gcp.3199745.tidbcloud.com:9094 (id: 3 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
    brokers.abc.us-west1.gcp.3199745.tidbcloud.com:9095 (id: 4 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
    brokers.abc.us-west1.gcp.3199745.tidbcloud.com:9096 (id: 5 rack: null) -> ERROR: org.apache.kafka.common.errors.DisconnectException
    ...
    ```
### Step 2. Expose Kafka-proxy as Private Service Connect Service

1. Go to the [Load balancing](https://console.cloud.google.com/net-services/loadbalancing/list/loadBalancers) page, and create a load balancer.

    - **Type of load balancer**: `Network Load Balancer`
    - **Proxy or Passthrough**: `Passthrough`
    - **Public facing or internal**: `Internal`
    - **Load Balancer name**: `kafka-proxy-lb`
    - **Region**: `us-west1`
    - **Network**: your network
    - Backend configuration
        - **Backend type**: `Instance group`
        - **Protocol**: `TCP`
        - **Instance group**: `kafka-proxy-ig`
    - Frontend configuration
        - **Subnetwork**: your subnet
        - **Ports**: `All`
        - Heath check:
            - **Name**: `kafka-proxy-hc`
            - **Scope**: `Regional`
            - **Protocol**: `TCP`
            - **Port**: `9092`. You can select one of the bootstrap ports in Kafka-proxy.

2. Go to [**Private Service Connect** > **PUBLISH SERVICE**](https://console.cloud.google.com/net-services/psc/list/producers).

    - **Load Balancer Type**: `Internal passthrough Network Load Balancer`
    - **Internal load balancer**: `kafka-proxy-lb`
    - **Service name**: `kafka-proxy-psc`
    - **Subnets**: `RESERVE NEW SUBNET`
        - **Name**: `proxy-psc-subnet`
        - **VPC Network**: your network
        - **Region**: `us-west1`
        - **IPv4 range**: set the CIDR based on your network planning
    - **Accepted projects**: the Google Cloud project of TiDB Cloud you get in [Prerequisites](#prerequisites), for example, `tidbcloud-prod-000`.

3. Navigate to the detail page of the **kafka-proxy-psc**. Note down the `Service attachment`, for example, `projects/tidbcloud-dp-stg-000/regions/us-west1/serviceAttachments/kafka-proxy-psc`, which will be used in TiDB Cloud to connect to this PSC.

4. Go to the detail page of your VPC network. Add a firewall rule to allow the PSC traffic for all brokers.

    - **Name**: `allow-proxy-psc-traffic`
    - **Direction of traffic**: `Ingress`
    - **Action on match**: `Allow`
    - **Targets**: All instances in the network
    - **Source filter**: `IPv4 ranges`
    - **Source IPv4 ranges**: the CIDR of proxy-psc-subnet
    - **Protocols and ports**: Allow all
### Step 3. Connect from TiDB Cloud

1. Return to the [TiDB Cloud console](https://tidbcloud.com) and create a changefeed for the cluster to connect to the Kafka cluster by **Private Service Connect**. For more information, see [Sink to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka).

2. After you proceed to the **Configure the changefeed target** > **Connectivity Method** > **Private Service Connect**, fill in the following fields with corresponding values and other fields as needed.

   - **Kafka Advertised Listener Pattern**: `abc`. The same as the unique random string you use to generate **Kafka Advertised Listener Pattern** in [Prerequisites](#prerequisites).
   - **Service Attachment**: the kafka-proxy service attachment of PSC, for example, `projects/tidbcloud-dp-stg-000/regions/us-west1/serviceAttachments/kafka-proxy-psc`.
   - **Bootstrap Ports**: `9092,9093,9094`

3. Continue to follow the guideline in [Sink to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka).
