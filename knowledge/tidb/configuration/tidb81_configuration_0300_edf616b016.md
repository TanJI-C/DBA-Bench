# Network setup for AWS DMS connectivity

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-connect-aws-dms.md`
- Source Title: `Connect AWS DMS to TiDB Cloud clusters`
- Source Heading Path: `Connect AWS DMS to TiDB Cloud clusters > Configure network`
- Source Line Ranges: `26-62`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `network configuration`, `public endpoint`, `private endpoint`, `vpc peering`, `nat gateway`, `ip access list`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0300_edf616b016`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-connect-aws-dms.md#configure-network`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `524cdbd3629a15f2b259a70c95767bf13091f160172e8ecd18bb30091fd3c89a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-connect-aws-dms#configure-network
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-connect-aws-dms.md

## Retrieval Guidance

- Use When: Use this chunk when determining how to configure network connectivity between an AWS DMS replication instance and a TiDB Cloud Serverless or TiDB Cloud Dedicated cluster.
- Retrieval Keywords: Configure network, public endpoint, private endpoint, VPC peering, Public accessible, public subnets, private subnets, NAT gateway, replication instance, IP access list, TiDB Cloud Serverless, TiDB Cloud Dedicated
- Follow-up Guidance: The source distinguishes Serverless and Dedicated connectivity options and notes that public endpoint access for TiDB Cloud Dedicated also requires adding the public IP address of the replication instance or NAT gateway to the cluster's IP access list.
- Classification Note: This is classified as configuration because the content describes network topology and endpoint access options required for AWS DMS communication with TiDB Cloud clusters.

## Official Source Content

## Configure network

Before creating DMS resources, you need to configure network properly to ensure DMS can communicate with TiDB Cloud clusters. If you are unfamiliar with AWS, contact AWS Support. The following provides several possible configurations for your reference.

<div label="TiDB Cloud Serverless">

For TiDB Cloud Serverless, your clients can connect to clusters via public endpoint or private endpoint.

- To [connect to a TiDB Cloud Serverless cluster via public endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection-serverless), do one of the following to make sure that the DMS replication instance can access the internet.

    - Deploy the replication instance in public subnets and enable **Public accessible**. For more information, see [Configuration for internet access](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html#vpc-igw-internet-access).

    - Deploy the replication instance in private subnets and route traffic in the private subnets to public subnets. In this case, you need at least three subnets, two private subnets, and one public subnet. The two private subnets form a subnet group where the replication instance lives. Then you need to create a NAT gateway in the public subnet and route traffic of the two private subnets to the NAT gateway. For more information, see [Access the internet from a private subnet](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-scenarios.html#public-nat-internet-access).

- To connect to a TiDB Cloud Serverless cluster via private endpoint, [set up a private endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-serverless) first and deploy the replication instance in private subnets.

</div>

<div label="TiDB Cloud Dedicated">

For TiDB Cloud Dedicated, your clients can connect to clusters via public endpoint, private endpoint, or VPC peering.

- To [connect to a TiDB Cloud Dedicated cluster via public endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection), do one of the following to make sure that the DMS replication instance can access the internet. In addition, you need to add the public IP address of the replication instance or NAT gateway to the cluster's [IP access list](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-ip-access-list).

    - Deploy the replication instance in public subnets and enable **Public accessible**. For more information, see [Configuration for internet access](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html#vpc-igw-internet-access).

    - Deploy the replication instance in private subnets and route traffic in the private subnets to public subnets. In this case, you need at least three subnets, two private subnets, and one public subnet. The two private subnets form a subnet group where the replication instance lives. Then you need to create a NAT gateway in the public subnet and route traffic of the two private subnets to the NAT gateway. For more information, see [Access the internet from a private subnet](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-scenarios.html#public-nat-internet-access).

- To connect to a TiDB Cloud Dedicated cluster via private endpoint, [set up a private endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections) first and deploy the replication instance in private subnets.

- To connect to a TiDB Cloud Dedicated cluster via VPC peering, [set up a VPC peering connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) first and deploy the replication instance in private subnets.

</div>
