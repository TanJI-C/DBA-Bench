# Expose Kafka with Google Cloud PSC and connect from TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md`
- Source Title: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > Set up self-hosted Kafka Private Service Connect service by PSC port mapping > Step 2. Expose the Kafka cluster as Private Service Connect | Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > Set up self-hosted Kafka Private Service Connect service by PSC port mapping > Step 3. Connect from TiDB Cloud | Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > Set up self-hosted Kafka Private Service Connect by Kafka-proxy`
- Source Line Ranges: `469-551`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `ecosystem`
- Topic Tags: `kafka`, `private-service-connect`, `network-endpoint-group`, `load-balancer`, `service-attachment`, `firewall-rules`, `changefeed`, `kafka-proxy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0291_37627b7759`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-self-hosted-kafka-private-service-connect.md#step-2-expose-the-kafka-cluster-as-private-service-connect`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dd19d282f013012543ef7cd47f6bf46c7f6a7f66ffff01b7d9cb1e42abbb1e84`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect#step-2-expose-the-kafka-cluster-as-private-service-connect
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Google Cloud Private Service Connect setup details for exposing self-hosted Kafka with a port mapping NEG and internal passthrough Network Load Balancer, then filling TiDB Cloud changefeed PSC connection fields.
- Retrieval Keywords: Network endpoint group, Port Mapping NEG(Regional), kafka-neg, broker-node1, VM Port 39092, Client Port 9093, Client Port 9094, Client Port 9095, Network Load Balancer, Passthrough, Internal, kafka-lb, Private Service Connect, PUBLISH SERVICE, kafka-psc, Service attachment, allow-psc-traffic, psc-subnet, 10.128.0.0/18, Configure the changefeed target, Connectivity Method, Private Service Connect, Kafka Advertised Listener Pattern, Service Attachment, Bootstrap Ports 9092,9093,9094, Set up self-hosted Kafka Private Service Connect by Kafka-proxy
- Follow-up Guidance: The chunk points to creating a changefeed in the TiDB Cloud console and then proceeding with the Sink to Apache Kafka documentation after entering the Kafka Advertised Listener Pattern, Service Attachment, and Bootstrap Ports.
- Classification Note: This is classified as configuration because the content specifies Google Cloud NEG, load balancer, PSC service publication, firewall rule values, and TiDB Cloud connection field values for the Kafka integration.

## Official Source Content

### Step 2. Expose the Kafka cluster as Private Service Connect

1. Go to the [Network endpoint group](https://console.cloud.google.com/compute/networkendpointgroups/list) page. Create a network endpoint group as follows:

    - **Name**: `kafka-neg`
    - **Network endpoint group type**: `Port Mapping NEG(Regional)`
        - **Region**: `us-west1`
        - **Network**: `kafka-vpc`
        - **Subnet**: `brokers-subnet`

2. Go to the detail page of the network endpoint group, and add the network endpoints to configure the port mapping to broker nodes.

    1. Network endpoint 1
        - **Instance**: `broker-node1`
        - **VM Port**: `39092`
        - **Client Port**: `9093`
    2. Network endpoint 2
        - **Instance**: `broker-node2`
        - **VM Port**: `39092`
        - **Client Port**: `9094`
    3. Network endpoint 3
        - **Instance**: `broker-node3`
        - **VM Port**: `39092`
        - **Client Port**: `9095`

3. Go to the [Load balancing](https://console.cloud.google.com/net-services/loadbalancing/list/loadBalancers) page. Create a load balancer as follows:

    - **Type of load balancer**: `Network Load Balancer`
    - **Proxy or Passthrough**: `Passthrough`
    - **Public facing or internal**: `Internal`
    - **Load Balancer name**: `kafka-lb`
    - **Region**: `us-west1`
    - **Network**: `kafka-vpc`
    - Backend configuration
        - **Backend type**: `Port mapping network endpoint group`
        - **Protocol**: `TCP`
        - **Port mapping network endpoint group**: `kafka-neg`
    - Frontend configuration
        - **Subnetwork**: `brokers-subnet`
        - **Ports**: `All`

4. Go to [**Private Service Connect** > **PUBLISH SERVICE**](https://console.cloud.google.com/net-services/psc/list/producers).

    - **Load Balancer Type**: `Internal passthrough Network Load Balancer`
    - **Internal load balancer**: `kafka-lb`
    - **Service name**: `kafka-psc`
    - **Subnets**: `RESERVE NEW SUBNET`
        - **Name**: `psc-subnet`
        - **VPC Network**: `kafka-vpc`
        - **Region**: `us-west1`
        - **IPv4 range**: `10.128.0.0/18`
    - **Accepted projects**: the Google Cloud project of TiDB Cloud you got in [Prerequisites](#prerequisites), for example, `tidbcloud-prod-000`.

5. Navigate to the detail page of the `kafka-psc`. Note down the **Service attachment**, for example, `projects/tidbcloud-dp-stg-000/regions/us-west1/serviceAttachments/kafka-psc`. You will use it in TiDB Cloud to connect to this PSC.

6. Go to the detail page of the VPC network `kafka-vpc`. Add a firewall rule to allow PSC traffic to all brokers.

    - **Name**: `allow-psc-traffic`
    - **Direction of traffic**: `Ingress`
    - **Action on match**: `Allow`
    - **Targets**: `All instances in the network`
    - **Source filter**: `IPv4 ranges`
    - **Source IPv4 ranges**: `10.128.0.0/18`. The range of psc-subnet.
    - **Protocols and ports**: Allow all
### Step 3. Connect from TiDB Cloud

1. Go back to the [TiDB Cloud console](https://tidbcloud.com) to create a changefeed for the cluster to connect to the Kafka cluster by **Private Service Connect**. For more information, see [Sink to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka).

2. When you proceed to **Configure the changefeed target > Connectivity Method > Private Service Connect**, fill in the following fields with corresponding values and other fields as needed.

    - **Kafka Advertised Listener Pattern**: `abc`. It is the same as the unique random string you use to generate **Kafka Advertised Listener Pattern** in [Prerequisites](#prerequisites).
    - **Service Attachment**: the Kafka service attachment of PSC, for example, `projects/tidbcloud-dp-stg-000/regions/us-west1/serviceAttachments/kafka-psc`.
    - **Bootstrap Ports**: `9092,9093,9094`

3. Proceed with the steps in [Sink to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka).
## Set up self-hosted Kafka Private Service Connect by Kafka-proxy

Expose each Kafka broker to TiDB Cloud VPC with a unique port by using the Kafka-proxy dynamic port mapping mechanism. The following diagram shows how it works.

![Connect to Google Cloud self-hosted Kafka Private Service Connect by Kafka proxy](/media/tidb-cloud/changefeed/connect-to-google-cloud-self-hosted-kafka-private-service-connect-by-kafka-proxy.jpeg)
