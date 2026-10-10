# Connection methods for TiDB Cloud Dedicated clusters

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/connect-to-tidb-cluster.md`
- Source Title: `Connect to Your TiDB Cloud Dedicated Cluster`
- Source Heading Path: `Connect to Your TiDB Cloud Dedicated Cluster | Connect to Your TiDB Cloud Dedicated Cluster > What's next`
- Source Line Ranges: `5-50`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `connectivity`, `public-connection`, `private-endpoint`, `vpc-peering`, `sql-editor`, `tls`, `aws`, `azure`, `google-cloud`, `chat2query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0291_f5fe3cbd3d`
- Source ID: `tidb-docs-8.1:tidb-cloud/connect-to-tidb-cluster.md#connect-to-your-tidb-cloud-dedicated-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a811933dd54d933390f8ccf96588ed41764e91d11c79678e3051448015a42b46`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster#connect-to-your-tidb-cloud-dedicated-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/connect-to-tidb-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when identifying how to connect to a TiDB Cloud Dedicated cluster, including direct connections, network connection types, and the built-in SQL Editor.
- Retrieval Keywords: TiDB Cloud Dedicated cluster connection methods, direct connections, MySQL native connection system over TCP, MySQL Command-Line Client, SQL Shell, public connection, private endpoint, VPC peering, TLS, AWS PrivateLink, Azure Private Link, Google Cloud Private Service Connect, Built-in SQL Editor, Chat2Query, connect to your TiDB Cloud Dedicated cluster
- Follow-up Guidance: After a successful connection, the source points to exploring SQL statements with TiDB.
- Classification Note: This is classified as an operation topic for the cloud component because the content describes available connection methods and access paths for TiDB Cloud Dedicated clusters.

## Official Source Content

# Connect to Your TiDB Cloud Dedicated Cluster

This document introduces the methods to connect to your TiDB Cloud Dedicated cluster.

> **Tip:**
>
> To learn how to connect to a TiDB Cloud Serverless cluster, see [Connect to Your TiDB Cloud Serverless Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster-serverless).

After your TiDB Cloud Dedicated cluster is created on TiDB Cloud, you can connect to it via one of the following methods:

- Direct connections

    Direct connections use the MySQL native connection system over TCP. You can connect to your TiDB Cloud Dedicated cluster using any tool that supports MySQL connections, such as the [MySQL Command-Line Client](https://dev.mysql.com/doc/refman/8.0/en/mysql.html). TiDB Cloud also provides [SQL Shell](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-sql-shell), which enables you to try TiDB SQL, test out TiDB's compatibility with MySQL quickly, and manage user privileges.

    TiDB Cloud Dedicated provides three network connection types:

    - [Public connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection)

        The public connection exposes a public endpoint with traffic filters, so you can connect to your TiDB cluster via a SQL client from your laptop. You can connect to your TiDB clusters using TLS, which ensures the security of data transmission from your applications to TiDB clusters. For more information, see [Connect to TiDB Cloud Dedicated via Public Connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection).

    - Private endpoint (recommended)

        Private endpoint connection provides a private endpoint to allow SQL clients in your VPC to securely access TiDB Cloud Dedicated clusters. This uses the private link service provided by different cloud providers, which provides highly secure and one-way access to database services with simplified network management.

        - For TiDB Cloud Dedicated clusters hosted on AWS, the private endpoint connection uses AWS PrivateLink. For more information, see [Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections).
        - For TiDB Cloud Dedicated clusters hosted on Azure, the private endpoint connection uses Azure Private Link. For more information, see [Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-azure).
        - For TiDB Cloud Dedicated clusters hosted on Google Cloud, the private endpoint connection uses Google Cloud Private Service Connect. For more information, see [Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud).

    - [VPC peering](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections)

        If you want lower latency and more security, set up VPC peering and connect via a private endpoint using a VM instance on the corresponding cloud provider in your cloud account. For more information, see [Connect to TiDB Cloud Dedicated via VPC Peering](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections).

- [Built-in SQL Editor](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query)

    > **Note:**
    >
    > To use SQL Editor on [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters, contact [TiDB Cloud support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).

    If your cluster is hosted on AWS and the TiDB version of the cluster is v6.5.0 or later, you can use the AI-assisted SQL Editor in the [TiDB Cloud console](https://tidbcloud.com/) to maximize your data value.

    In SQL Editor, you can either write SQL queries manually or simply press <kbd>⌘</kbd> + <kbd>I</kbd> on macOS (or <kbd>Control</kbd> + <kbd>I</kbd> on Windows or Linux) to instruct [Chat2Query (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#chat2query) to generate SQL queries automatically. This enables you to run SQL queries against databases without a local SQL client. You can intuitively view the query results in tables or charts and easily check the query logs.
## What's next

After you have successfully connected to your TiDB cluster, you can [explore SQL statements with TiDB](https://docs.pingcap.com/tidb/stable/basic-sql-operations).
