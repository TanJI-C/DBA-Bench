# Expose Kafka via Azure Private Link and connect TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in Azure`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in Azure > Step 2. Expose the Kafka cluster as Private Link Service | Set Up Self-Hosted Kafka Private Link Service in Azure > Step 2. Expose the Kafka cluster as Private Link Service > 1. Set up the load balancer | Set Up Self-Hosted Kafka Private Link Service in Azure > Step 2. Expose the Kafka cluster as Private Link Service > 2. Set up Private Link Service | Set Up Self-Hosted Kafka Private Link Service in Azure > Step 3. Connect from TiDB Cloud | Set Up Self-Hosted Kafka Private Link Service in Azure > FAQ | Set Up Self-Hosted Kafka Private Link Service in Azure > FAQ > How to connect to the same Kafka Private Link service from two different TiDB Cloud projects?`
- Source Line Ranges: `420-545`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `ticdc`, `shared`
- Topic Tags: `kafka`, `azure`, `private-link`, `load-balancer`, `frontend-ip`, `backend-pool`, `health-probe`, `changefeed`, `bootstrap-ports`, `faq`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0285_616db16d4a`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md#step-2-expose-the-kafka-cluster-as-private-link-service`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d7a2bfc2a443b382ac10208460f2383b29a1e73e5eded3ade0cde37d4311e32c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service#step-2-expose-the-kafka-cluster-as-private-link-service
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Azure load balancer, Private Link service, and TiDB Cloud changefeed connectivity fields required to expose a self-hosted Kafka cluster through Azure Private Link Service.
- Retrieval Keywords: Set up the load balancer, Set up Private Link Service, Connect from TiDB Cloud, kafka-lb, kafka-lb-ip, kafka-pls, pool1, pool2, pool3, rule1, rule2, rule3, 9093, 9094, 9095, 39092, kafka-lb-hp, Private link services, Alias of the Private Link Service, Bootstrap Ports: 9093,9094,9095, Kafka Advertised Listener Pattern, Connectivity Method > Private Link, How to connect to the same Kafka Private Link service from two different TiDB Cloud projects, EXTERNAL2
- Follow-up Guidance: The chunk also includes the FAQ flow for connecting a second TiDB Cloud project by creating another listener group such as EXTERNAL2, then creating a new load balancer and a new Private Link service.
- Classification Note: The official content is classified as configuration because it enumerates Azure resource settings, port mappings, Private Link access fields, and TiDB Cloud connection parameters.

## Official Source Content

## Step 2. Expose the Kafka cluster as Private Link Service
### 1. Set up the load balancer

1. Log in to the [Azure portal](https://portal.azure.com/), go to the [Load balancing](https://portal.azure.com/#view/Microsoft_Azure_Network/LoadBalancingHubMenuBlade/~/loadBalancers) page, and then click **+ Create** to create a load balancer.
2. In the **Basic** tab, select your **Subscription**, **Resource group**, and **Region**, fill in the following instance information, and then click **Next : Frontend IP configuration >**.

    - **Name**: `kafka-lb`
    - **SKU**: `Standard`
    - **Type**: `Internal`
    - **Tier**: `Regional`

3. In the **Frontend IP configuration** tab, click **+ Add a frontend IP configuration**, fill in the following information, click **Save**, and then click **Next : Backend pools >**.

    - **Name**: `kafka-lb-ip`
    - **IP version**: `IPv4`
    - **Virtual network**: `kafka-pls-vnet`
    - **Subnet**: `brokers-subnet`
    - **Assignment**: `Dynamic`
    - **Availability zone**: `Zone-redundant`

4. In the **Backend pools** tab, add three backend pools as follows, and then click **Next : Inbound rules**.

    - Name: `pool1`; Backend Pool Configuration: `NIC`; IP configurations: `broker-node-1`
    - Name: `pool2`; Backend Pool Configuration: `NIC`; IP configurations: `broker-node-2`
    - Name: `pool3`; Backend Pool Configuration: `NIC`; IP configurations: `broker-node-3`

5. In the **Inbound rules** tab, add three load balancing rules as follows:

    1. Rule 1

        - **Name**: `rule1`
        - **IP version**: `IPv4`
        - **Frontend IP address**: `kafka-lb-ip`
        - **Backend pool**: `pool1`
        - **Protocol**: `TCP`
        - **Port**: `9093`
        - **Backend port**: `39092`
        - **Health probe**: click **Create New** and fill in the probe information.
            - **Name**: `kafka-lb-hp`
            - **Protocol**: `TCP`
            - **Port**: `39092`

    2. Rule 2

        - **Name**: `rule2`
        - **IP version**: `IPv4`
        - **Frontend IP address**: `kafka-lb-ip`
        - **Backend pool**: `pool2`
        - **Protocol**: `TCP`
        - **Port**: `9094`
        - **Backend port**: `39092`
        - **Health probe**: click **Create New** and fill in the probe information.
            - **Name**: `kafka-lb-hp`
            - **Protocol**: `TCP`
            - **Port**: `39092`

    3. Rule 3

        - **Name**: `rule3`
        - **IP version**: `IPv4`
        - **Frontend IP address**: `kafka-lb-ip`
        - **Backend pool**: `pool3`
        - **Protocol**: `TCP`
        - **Port**: `9095`
        - **Backend port**: `39092`
        - **Health probe**: click **Create New** and fill in the probe information.
            - **Name**: `kafka-lb-hp`
            - **Protocol**: `TCP`
            - **Port**: `39092`

6. Click **Next : Outbound rule**, click **Next : Tags >**, and then click **Next : Review + create** to verify the information.

7. Click **Create**.
### 2. Set up Private Link Service

1. Log in to the [Azure portal](https://portal.azure.com/), go to the [Private link services](https://portal.azure.com/#view/Microsoft_Azure_Network/PrivateLinkCenterBlade/~/privatelinkservices) page, and then click **+ Create** to create a Private Link service for the Kafka load balancer.

2. In the **Basic** tab, select your **Subscription**, **Resource group**, and **Region**, fill in `kafka-pls` in the **Name** field, and then click **Next : Outbound settings >**.

3. In the **Outbound settings** tab, fill in the parameters as follows, and then click **Next : Access security >**.

    - **Load balancer**: `kafka-lb`
    - **Load balancer frontend IP address**: `kafka-lb-ip`
    - **Source NAT subnet**: `kafka-pls-vnet/brokers-subnet`

4. In the **Access security** tab, do the following:

    - For **Visibility**, select **Restricted by subscription** or **Anyone with your alias**.
    - For **Subscription-level access and auto-approval**, click **Add subscriptions** to add the subscription of TiDB Cloud Azure account you got in [Prerequisites](#prerequisites).

5. Click **Next : Tags >**, and then click **Next : Review + create >** to verify the information.

6. Click **Create**. When the operation is done, note down the alias of the Private Link service for later use.
## Step 3. Connect from TiDB Cloud

1. Return to the [TiDB Cloud console](https://tidbcloud.com) to create a changefeed for the cluster to connect to the Kafka cluster by **Private Link**. For more information, see [Sink to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka).

2. When you proceed to **Configure the changefeed target > Connectivity Method > Private Link**, fill in the following fields with corresponding values and other fields as needed.

    - **Kafka Advertised Listener Pattern**: the unique random string that you use to generate **Kafka Advertised Listener Pattern** in [Prerequisites](#prerequisites).
    - **Alias of the Private Link Service**: the alias of the Private Link service that you got in [2. Set up Private Link Service](#2-set-up-private-link-service).
    - **Bootstrap Ports**: `9093,9094,9095`.

3. Proceed with the steps in [Sink to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka).

Now you have successfully finished the task.
## FAQ
### How to connect to the same Kafka Private Link service from two different TiDB Cloud projects?

If you have already followed this document to successfully set up the connection from the first project, you can connect to the same Kafka Private Link service from the second project as follows:

1. Follow instructions from the beginning of this document.

2. When you proceed to [Step 1. Set up a Kafka cluster](#step-1-set-up-a-kafka-cluster), follow [Reconfigure a running Kafka cluster](#reconfigure-a-running-kafka-cluster) to create another group of EXTERNAL listeners and advertised listeners. You can name it as **EXTERNAL2**. Note that the port range of **EXTERNAL2** can overlap with the **EXTERNAL**.

3. After reconfiguring brokers, create a new load balancer and a new Private Link service.

4. Configure the TiDB Cloud connection with the following information:

    - New Kafka Advertised Listener Group
    - New Private Link service
