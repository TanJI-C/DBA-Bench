# Configure IP access list for a TiDB Cloud Dedicated cluster

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/configure-ip-access-list.md`
- Source Title: `Configure an IP Access List`
- Source Heading Path: `Configure an IP Access List`
- Source Line Ranges: `5-30`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `ip access list`, `firewall`, `networking`, `cluster access`, `cidr`, `public access`, `dedicated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0213_265d4a501f`
- Source ID: `tidb-docs-8.1:tidb-cloud/configure-ip-access-list.md#configure-an-ip-access-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `458e380e8930c7785b7942e375c33938ab2eeb73023c1881bb5694f29fa9c21d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-ip-access-list#configure-an-ip-access-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/configure-ip-access-list.md

## Retrieval Guidance

- Use When: Use this content when the question is about configuring an IP access list for a TiDB Cloud Dedicated cluster to control which client or application IP addresses can connect.
- Retrieval Keywords: Configure an IP Access List, TiDB Cloud Dedicated, IP access list, firewall access control list, Settings > Networking, Add IP Address, Allow access from anywhere, Use IP addresses, CIDR addresses, up to 100 IP addresses, cluster access
- Follow-up Guidance: The source also distinguishes TiDB Cloud Dedicated from TiDB Cloud Serverless and points to separate Serverless firewall rule instructions for public endpoints.
- Classification Note: The classification is configuration for the cloud component because the content describes UI steps in TiDB Cloud to set networking access rules for a Dedicated cluster.

## Official Source Content

# Configure an IP Access List

For each TiDB Cloud Dedicated cluster in TiDB Cloud, you can configure an IP access list to filter internet traffic trying to access the cluster, which works similarly to a firewall access control list. After the configuration, only the clients and applications whose IP addresses are in the IP access list can connect to your TiDB Cloud Dedicated cluster.

> **Note:**
>
> This document applies to [**TiDB Cloud Dedicated**](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated). For instructions on configuring an IP access list for **TiDB Cloud Serverless**, see [Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-serverless-firewall-rules-for-public-endpoints).

To configure an IP access list for your TiDB Cloud Dedicated cluster, take the following steps:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. In the left navigation pane, click **Settings** > **Networking**.
3. On the **Networking** page, click **Add IP Address**.
4. In the displayed dialog, choose one of the following options:

    - **Allow access from anywhere**: allows all IP addresses to access TiDB Cloud. This option exposes your cluster to the internet completely and is highly risky.
    - **Use IP addresses** (recommended): you can add a list of IPs and CIDR addresses that are allowed to access TiDB Cloud via a SQL client.

5. If you choose **Use IP addresses**, add IP addresses or CIDR range with an optional description. For each TiDB Cloud Dedicated cluster, you can add up to 100 IP addresses.
6. Click **Confirm** to save your changes.
