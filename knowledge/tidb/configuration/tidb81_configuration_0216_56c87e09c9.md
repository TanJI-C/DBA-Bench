# TiDB Cloud Serverless public endpoint firewall rules

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/configure-serverless-firewall-rules-for-public-endpoints.md`
- Source Title: `Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints`
- Source Heading Path: `Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints | Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints > Public endpoints | Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints > Public endpoints > Characteristics of public access | Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints > Public endpoints > Firewall rules | Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints > Public endpoints > Allow AWS access | Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints > Create and manage a firewall rule | Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints > What's next`
- Source Line Ranges: `5-58`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `public-endpoint`, `firewall-rules`, `authorized-networks`, `ip-allowlist`, `aws-access`, `networking`, `access-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0216_56c87e09c9`
- Source ID: `tidb-docs-8.1:tidb-cloud/configure-serverless-firewall-rules-for-public-endpoints.md#configure-tidb-cloud-serverless-firewall-rules-for-public-endpoints`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2657f7707a8baf4e37964aef45f4744106564ab67ad4a75dbdb6b341f7ed34d9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-serverless-firewall-rules-for-public-endpoints#configure-tidb-cloud-serverless-firewall-rules-for-public-endpoints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/configure-serverless-firewall-rules-for-public-endpoints.md

## Retrieval Guidance

- Use When: Use this chunk when asking how public endpoint access control works for a TiDB Cloud Serverless cluster, including authorized networks, firewall rules, default allowed IPs, AWS access representation, and where to manage these settings in the console.
- Retrieval Keywords: TiDB Cloud Serverless public endpoint firewall rules, Authorized Networks, public endpoint, firewall rules, IP firewall rules, 0.0.0.0 - 255.255.255.255, publicly resolvable DNS address, public internet, unapproved IP address error, maximum of 200 IP firewall rules, all AWS IP addresses, 169.254.65.87, Clusters, Settings > Networking, Public Endpoint, Add Current IP, Add rule, Start IP Address, End IP Address
- Follow-up Guidance: The next related step in the source is Connect to TiDB Cloud Serverless via Public Endpoint.
- Classification Note: This is classified as cloud configuration content because the source explains TiDB Cloud Serverless public endpoint behavior and the console workflow for creating and managing firewall rules in Authorized Networks.

## Official Source Content

# Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints

This document describes the public connectivity option for TiDB Cloud Serverless. You will learn key concepts for securely managing a TiDB Cloud Serverless cluster accessible via the internet.

> **Note:**
>
> This document applies to **TiDB Cloud Serverless**. For instructions on configuring an IP access list for **TiDB Cloud Dedicated**, see [Configure an IP Access List for TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-ip-access-list).
## Public endpoints

Configuring public access on your TiDB Cloud Serverless cluster allows the cluster access through a public endpoint. That is, the cluster is accessible through the internet. The public endpoint is a publicly resolvable DNS address. The term "authorized network" refers to a range of IP addresses you choose to permit access to your cluster. These permissions are enforced through **firewall rules**.
### Characteristics of public access

- Only specified IP addresses can access TiDB Cloud Serverless.  
    - By default, all IP addresses (`0.0.0.0 - 255.255.255.255`) are allowed.  
    - You can update allowed IP addresses after cluster creation.  
- Your cluster has a publicly resolvable DNS name.  
- Network traffic to and from your cluster is routed over the **public internet** rather than a private network.
### Firewall rules

Granting access to an IP address is done via **firewall rules**. If a connection attempt originates from an unapproved IP address, the client will receive an error.

You can create a maximum of 200 IP firewall rules.
### Allow AWS access

You can enable access from **all AWS IP addresses** by referring to the official [AWS IP address list](https://docs.aws.amazon.com/vpc/latest/userguide/aws-ip-ranges.html).  

TiDB Cloud regularly updates this list and uses the reserved IP address **169.254.65.87** to represent all AWS IP addresses.
## Create and manage a firewall rule

This section describes how to manage firewall rules for a TiDB Cloud Serverless cluster. With a public endpoint, the connections to the TiDB Cloud Serverless cluster are restricted to the IP addresses specified in the firewall rules.

To add firewall rules to a TiDB Cloud Serverless cluster, take the following steps:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. In the left navigation pane, click **Settings** > **Networking**.

3. On the **Networking** page, enable **Public Endpoint** if it is disabled. In **Authorized Networks**, click **+ Add Current IP**. This automatically creates a firewall rule with the public IP address of your computer, as perceived by TiDB Cloud.

    > **Note:**
    >
    > In some situations, the IP address observed by the TiDB Cloud console differs from the IP address used when accessing the internet. Therefore, you might need to change the start and end IP addresses to make the rule function as expected. You can use a search engine or other online tool to check your own IP address. For example, search for "what is my IP."

4. Click **Add rule** to add more address ranges. In the displayed window, you can specify a single IP address or a range of IP addresses. If you want to limit the rule to a single IP address, type the same IP address in the **Start IP Address** and **End IP Address** fields. Opening the firewall enables administrators, users, and applications to access any database on your TiDB Cloud Serverless cluster to which they have valid credentials. Click **Submit** to add the firewall rule.
## What's next

- [Connect to TiDB Cloud Serverless via Public Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection-serverless)
