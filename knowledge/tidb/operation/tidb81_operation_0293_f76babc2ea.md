# Connect to a Serverless cluster via public endpoint

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/connect-via-standard-connection-serverless.md`
- Source Title: `Connect to TiDB Cloud Serverless via Public Endpoint`
- Source Heading Path: `Connect to TiDB Cloud Serverless via Public Endpoint | Connect to TiDB Cloud Serverless via Public Endpoint > Connect via a public endpoint`
- Source Line Ranges: `5-39`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `public-endpoint`, `connection`, `sql-client`, `tls`, `branch`, `password`, `username-prefix`, `firewall-rules`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0293_f76babc2ea`
- Source ID: `tidb-docs-8.1:tidb-cloud/connect-via-standard-connection-serverless.md#connect-to-tidb-cloud-serverless-via-public-endpoint`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dbb8206f036ad20e5c29acee99fca2e50462e523786d65a03bf945693d12599a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection-serverless#connect-to-tidb-cloud-serverless-via-public-endpoint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/connect-via-standard-connection-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about connecting to a TiDB Cloud Serverless cluster through a public endpoint, obtaining the connection string, choosing a branch, or understanding required TLS, user name prefix, password generation, and allowed IP rules.
- Retrieval Keywords: TiDB Cloud Serverless public endpoint, Connect via a public endpoint, Connect dialog, Connection Type Public, standard TLS connection, Private Endpoint, Branch drop-down list, main represents the cluster itself, Generate Password, connection string, user name prefix, quotation marks, allowed IP rules, Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints
- Follow-up Guidance: After you have successfully connected to your TiDB cluster, you can explore SQL statements with TiDB.
- Classification Note: The official content is an operation guide for TiDB Cloud Serverless public-endpoint connectivity, including connection dialog choices, branch selection, password generation, TLS connection context, user name prefix, and public-endpoint firewall rule requirements.

## Official Source Content

# Connect to TiDB Cloud Serverless via Public Endpoint

This document describes how to connect to your TiDB Cloud Serverless cluster via a public endpoint, using a SQL client from your computer, as well as how to disable a public endpoint.
## Connect via a public endpoint

> **Tip:**
>
> To learn how to connect to a TiDB Cloud Dedicated cluster via public endpoint, see [Connect to TiDB Cloud Dedicated via Public Connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection).

To connect to a TiDB Cloud Serverless cluster via public endpoint, take the following steps:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the dialog, keep the default setting of the connection type as `Public`, and select your preferred connection method and operating system to get the corresponding connection string.

    > **Note:**
    >
    > - Keeping the connection type as `Public` means the connection is via standard TLS connection. For more information, see [TLS Connection to TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/secure-connections-to-serverless-clusters).
    > - If you choose **Private Endpoint** in the **Connection Type** drop-down list, it means that the connection is via private endpoint. For more information, see [Connect to TiDB Cloud Serverless via Private Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-serverless).

4. TiDB Cloud Serverless lets you create [branches](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-overview) for your cluster. After a branch is created, you can choose to connect to the branch via the **Branch** drop-down list. `main` represents the cluster itself.

5. If you have not set a password yet, click **Generate Password** to generate a random password. The generated password will not show again, so save your password in a secure location.

6. Connect to your cluster with the connection string.

    > **Note:**
    >
    > When you connect to a TiDB Cloud Serverless cluster, you must include the prefix for your cluster in the user name and wrap the name with quotation marks. For more information, see [User name prefix](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#user-name-prefix).
    > Your client IP must be in the allowed IP rules of the public endpoint of your cluster. For more information, see [Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-serverless-firewall-rules-for-public-endpoints).
