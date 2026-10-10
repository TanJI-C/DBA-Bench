# Start Kafka cluster setup and create the Azure virtual network

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in Azure`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in Azure > Step 1. Set up a Kafka cluster | Set Up Self-Hosted Kafka Private Link Service in Azure > Step 1. Set up a Kafka cluster > Deploy a new Kafka cluster | Set Up Self-Hosted Kafka Private Link Service in Azure > Step 1. Set up a Kafka cluster > Deploy a new Kafka cluster > 1. Set up the Kafka virtual network`
- Source Line Ranges: `57-82`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`
- Topic Tags: `kafka`, `azure`, `virtual-network`, `subnet`, `bastion`, `cluster-setup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0281_2d51a0b22c`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md#step-1-set-up-a-kafka-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `461314bda871a317141a915084cdc5eddb0c3137c8c57d386da6647aea240f0c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service#step-1-set-up-a-kafka-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-azure-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the initial Azure setup steps for a new Kafka cluster virtual network, including virtual network creation, Azure Bastion, and the brokers-subnet address settings.
- Retrieval Keywords: Step 1. Set up a Kafka cluster, Deploy a new Kafka cluster, Set up the Kafka virtual network, Azure portal, Virtual networks, kafka-pls-vnet, Enable Azure Bastion, IP addresses tab, Add a subnet, brokers-subnet, 10.0.0.0/16, 10.0.0.0/24, AzureBastionSubnet, Review + create
- Follow-up Guidance: The source continues within the Kafka cluster setup procedure after the virtual network is created.
- Classification Note: This chunk is classified as configuration because the official content provides explicit Azure portal fields and network values for creating the Kafka virtual network and subnet.

## Official Source Content

## Step 1. Set up a Kafka cluster

If you need to deploy a new cluster, follow the instructions in [Deploy a new Kafka cluster](#deploy-a-new-kafka-cluster).

If you need to expose an existing cluster, follow the instructions in [Reconfigure a running Kafka cluster](#reconfigure-a-running-kafka-cluster).
### Deploy a new Kafka cluster
#### 1. Set up the Kafka virtual network

1. Log in to the [Azure portal](https://portal.azure.com/), go to the [Virtual networks](https://portal.azure.com/#browse/Microsoft.Network%2FvirtualNetworks) page, and then click **+ Create** to create a virtual network.
2. In the **Basic** tab, select your **Subscription**, **Resource group**, and **Region**, enter a name (for example, `kafka-pls-vnet`) in the **Virtual network name** field, and then click **Next**.
3. In the **Security** tab, enable Azure Bastion, and then click **Next**.
4. In the **IP addresses** tab, do the following:

    1. Set the address space of your virtual network, for example, `10.0.0.0/16`.
    2. Click **Add a subnet** to create a subnet for brokers, fill in the following information, and then click **Add**.
        - **Name**: `brokers-subnet`
        - **IP address range**: `10.0.0.0/24`
        - **Size**: `/24 (256 addresses)`

        An `AzureBastionSubnet` will be created by default.

5. Click **Review + create** to verify the information.
6. Click **Create**.
