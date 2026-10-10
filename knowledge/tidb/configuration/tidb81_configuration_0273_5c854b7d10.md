# Set up a new Kafka cluster VPC for Private Link

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in AWS`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in AWS > Step 1. Set up a Kafka cluster | Set Up Self-Hosted Kafka Private Link Service in AWS > Step 1. Set up a Kafka cluster > Deploy a new Kafka cluster | Set Up Self-Hosted Kafka Private Link Service in AWS > Step 1. Set up a Kafka cluster > Deploy a new Kafka cluster > 1. Set up the Kafka VPC`
- Source Line Ranges: `62-149`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `ticdc`
- Topic Tags: `aws`, `kafka`, `vpc`, `subnets`, `bastion`, `internet-gateway`, `route-table`, `az-mapping`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0273_5c854b7d10`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md#step-1-set-up-a-kafka-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `68e1ce5e409dbcdbcd0afb858d2eb59c8c0b6098c053beace7295436e3c1e4a8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service#step-1-set-up-a-kafka-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the AWS VPC and subnet layout for deploying a new Kafka cluster for Private Link, including broker subnets, a bastion subnet, and AZ ID to AZ name mapping.
- Retrieval Keywords: Set up the Kafka VPC, Deploy a new Kafka cluster, Kafka VPC, three private subnets for brokers, one public subnet, bastion node, AZ IDs and AZ names mapping, usw2-az1 => us-west-2a, usw2-az2 => us-west-2c, usw2-az3 => us-west-2b, Create VPC, VPC only, IPv4 CIDR manual input, 10.0.0.0/16, Create private subnets, broker-usw2-az1, broker-usw2-az2, broker-usw2-az3, 10.0.0.0/18, 10.0.64.0/18, 10.0.128.0/18, advertised.listener configuration, Create public subnet, bastion, 10.0.192.0/18, Internet Gateway, kafka-vpc-igw, route table, kafka-vpc-igw-route-table, 0.0.0.0/0, Subnet associations
- Follow-up Guidance: The documented follow-up is to continue setting up the Kafka cluster after creating the Kafka VPC, private broker subnets, and the public bastion subnet with Internet Gateway routing.
- Classification Note: This is classified as configuration because it provides the concrete AWS network topology and resource settings required to deploy a new Kafka cluster for Private Link.

## Official Source Content

## Step 1. Set up a Kafka cluster

If you need to deploy a new cluster, follow the instructions in [Deploy a new Kafka cluster](#deploy-a-new-kafka-cluster).

If you need to expose an existing cluster, follow the instructions in [Reconfigure a running Kafka cluster](#reconfigure-a-running-kafka-cluster). 
### Deploy a new Kafka cluster
#### 1. Set up the Kafka VPC

The Kafka VPC requires the following:

- Three private subnets for brokers, one for each AZ. 
- One public subnet in any AZ with a bastion node that can connect to the internet and three private subnets, which makes it easy to set up the Kafka cluster. In a production environment, you might have your own bastion node that can connect to the Kafka VPC.

Before creating subnets, create subnets in AZs based on the mappings of AZ IDs and AZ names. Take the following mapping as an example.

- `usw2-az1` => `us-west-2a`
- `usw2-az2` => `us-west-2c`
- `usw2-az3` => `us-west-2b`

Create private subnets in the following AZs: 

- `us-west-2a`
- `us-west-2c`
- `us-west-2b`

Take the following steps to create the Kafka VPC.

**1.1. Create the Kafka VPC**

1. Go to [AWS Console > VPC dashboard](https://console.aws.amazon.com/vpcconsole/home?#vpcs:), and switch to the region in which you want to deploy Kafka.

2. Click **Create VPC**. Fill in the information on the **VPC settings** page as follows.

    1. Select **VPC only**.
    2. Enter a tag in **Name tag**, for example, `Kafka VPC`.
    3. Select **IPv4 CIDR manual input**, and enter the IPv4 CIDR, for example, `10.0.0.0/16`.
    4. Use the default values for other options. Click **Create VPC**.
    5. On the VPC detail page, take note of the VPC ID, for example, `vpc-01f50b790fa01dffa`.

**1.2. Create private subnets in the Kafka VPC**

1. Go to the [Subnets Listing page](https://console.aws.amazon.com/vpcconsole/home?#subnets:).
2. Click **Create subnet**.
3. Select **VPC ID** (`vpc-01f50b790fa01dffa` in this example) that you noted down before.
4. Add three subnets with the following information. It is recommended that you put the AZ IDs in the subnet names to make it easy to configure the brokers later, because TiDB Cloud requires encoding the AZ IDs in the broker's `advertised.listener` configuration.

    - Subnet1 in `us-west-2a`
        - **Subnet name**: `broker-usw2-az1`
        - **Availability Zone**: `us-west-2a`
        - **IPv4 subnet CIDR block**: `10.0.0.0/18`

    - Subnet2 in `us-west-2c`
        - **Subnet name**: `broker-usw2-az2`
        - **Availability Zone**: `us-west-2c`
        - **IPv4 subnet CIDR block**: `10.0.64.0/18`

    - Subnet3 in `us-west-2b`
        - **Subnet name**: `broker-usw2-az3`
        - **Availability Zone**: `us-west-2b`
        - **IPv4 subnet CIDR block**: `10.0.128.0/18`

5. Click **Create subnet**. The **Subnets Listing** page is displayed.

**1.3. Create the public subnet in the Kafka VPC**

1. Click **Create subnet**.
2. Select **VPC ID** (`vpc-01f50b790fa01dffa` in this example) that you noted down before.
3. Add the public subnet in any AZ with the following information:

   - **Subnet name**: `bastion`
   - **IPv4 subnet CIDR block**: `10.0.192.0/18`

4. Configure the bastion subnet to the Public subnet.

    1. Go to [VPC dashboard > Internet gateways](https://console.aws.amazon.com/vpcconsole/home#igws:). Create an Internet Gateway with the name `kafka-vpc-igw`.
    2. On the **Internet gateways Detail** page, in **Actions**, click **Attach to VPC** to attach the Internet Gateway to the Kafka VPC.
    3. Go to [VPC dashboard > Route tables](https://console.aws.amazon.com/vpcconsole/home#CreateRouteTable:). Create a route table to the Internet Gateway in Kafka VPC and add a new route with the following information:

       - **Name**: `kafka-vpc-igw-route-table`
       - **VPC**: `Kafka VPC`
       - **Route**: 
           - **Destination**: `0.0.0.0/0`
           - **Target**: `Internet Gateway`, `kafka-vpc-igw`

    4. Attach the route table to the bastion subnet. On the **Detail** page of the route table, click **Subnet associations > Edit subnet associations** to add the bastion subnet and save changes.
