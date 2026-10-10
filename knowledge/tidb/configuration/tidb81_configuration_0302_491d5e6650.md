# TiDB Cloud cluster security and connection basics

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-faq.md`
- Source Title: `TiDB Cloud FAQs`
- Source Heading Path: `TiDB Cloud FAQs > Security FAQs > Is my TiDB cluster secure? | TiDB Cloud FAQs > Security FAQs > How do I connect to my database in a TiDB cluster?`
- Source Line Ranges: `154-198`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `sql`, `tidb`
- Topic Tags: `security`, `tls`, `network-access`, `ip-allowlist`, `database-users`, `connection-string`, `dedicated`, `serverless`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0302_491d5e6650`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-faq.md#is-my-tidb-cluster-secure`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f73c821d434295618a15699773843e3cf717f13e68ac98a41c384b54614aeed5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-faq#is-my-tidb-cluster-secure
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-faq.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiDB Cloud Dedicated or Serverless cluster security measures, TLS, IP access rules, or the basic steps to connect with a SQL client and connection string.
- Retrieval Keywords: TiDB Cloud Dedicated cluster security, TiDB Cloud Serverless cluster security, independent sub-accounts, VPCs, firewall rules, server-side TLS certificates, component-level TLS certificates, cluster server TLS certificates, IP access rules, allowed source IP addresses, authorize your network, database users and login credentials, download and configure TLS, SQL client, auto-generated connection string, Connect to Your TiDB Cloud Dedicated Cluster, Connect to Your TiDB Cloud Serverless Cluster
- Follow-up Guidance: The source points to Connect to Your TiDB Cloud Dedicated Cluster and Connect to Your TiDB Cloud Serverless Cluster for more information.
- Classification Note: This is classified as configuration because the content describes connection prerequisites and security-related setup items such as IP access rules, database users, TLS, and connection strings in TiDB Cloud.

## Official Source Content

### Is my TiDB cluster secure?

In TiDB Cloud, you can use either a TiDB Cloud Dedicated cluster or a TiDB Cloud Serverless cluster according to your needs.

For TiDB Cloud Dedicated clusters, TiDB Cloud ensures cluster security with the following measures:

- Creates independent sub-accounts and VPCs for each cluster.
- Sets up firewall rules to isolate external connections.
- Creates server-side TLS certificates and component-level TLS certificates for each cluster to encrypt cluster data in transit.
- Provide IP access rules for each cluster to ensure that only allowed source IP addresses can access your cluster.

For TiDB Cloud Serverless clusters, TiDB Cloud ensures cluster security with the following measures:

- Creates independent sub-accounts for each cluster.
- Sets up firewall rules to isolate external connections.
- Provides cluster server TLS certificates to encrypt cluster data in transit.
### How do I connect to my database in a TiDB cluster?

<div label="TiDB Cloud Dedicated">

For a TiDB Cloud Dedicated cluster, the steps to connect to your cluster are simplified as follows:

1. Authorize your network.
2. Set up your database users and login credentials.
3. Download and configure TLS for your cluster server.
4. Choose a SQL client, get an auto-generated connection string displayed on the TiDB Cloud UI, and then connect to your cluster through the SQL client using the string.

For more information, see [Connect to Your TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster).

</div>

<div label="TiDB Cloud Serverless">

For a TiDB Cloud Serverless cluster, the steps to connect to your cluster are simplified as follows:

1. Set a database user and login credential.
2. Choose a SQL client, get an auto-generated connection string displayed on the TiDB Cloud UI, and then connect to your cluster through the SQL client using the string.

For more information, see [Connect to Your TiDB Cloud Serverless Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster-serverless).

</div>
