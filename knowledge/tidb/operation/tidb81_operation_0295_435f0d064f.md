# Connect to TiDB Cloud Dedicated via public connection

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/connect-via-standard-connection.md`
- Source Title: `Connect to TiDB Cloud Dedicated via Public Connection`
- Source Heading Path: `Connect to TiDB Cloud Dedicated via Public Connection | Connect to TiDB Cloud Dedicated via Public Connection > Prerequisite: Configure IP access list | Connect to TiDB Cloud Dedicated via Public Connection > Connect to the cluster | Connect to TiDB Cloud Dedicated via Public Connection > What's next`
- Source Line Ranges: `5-44`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `public-connection`, `ip-access-list`, `cluster-connection`, `tls`, `ca-cert`, `sql-client`, `connection-string`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0295_435f0d064f`
- Source ID: `tidb-docs-8.1:tidb-cloud/connect-via-standard-connection.md#connect-to-tidb-cloud-dedicated-via-public-connection`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2f2e034b0953cd9d55e7248de2cc45fe445ca2b0acfec41470fea6b9ab464189`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection#connect-to-tidb-cloud-dedicated-via-public-connection
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/connect-via-standard-connection.md

## Retrieval Guidance

- Use When: Use this when someone needs the TiDB Cloud Dedicated public connection steps, including IP access list requirements, the Connect dialog flow, and TLS CA certificate download information.
- Retrieval Keywords: Connect to TiDB Cloud Dedicated via Public Connection, TiDB Cloud Dedicated, public connection, public endpoint, traffic filters, IP access list, Configure an IP Access List, Clusters page, Connect, Connection Type, Public, Configure IP Access List, CA cert, TLS 1.2, connection string, sample code, SQL client
- Follow-up Guidance: After connecting successfully, the source points to exploring SQL statements with TiDB.
- Classification Note: This is classified as an operation because the content provides the procedure and prerequisites for connecting to a TiDB Cloud Dedicated cluster through a public connection.

## Official Source Content

# Connect to TiDB Cloud Dedicated via Public Connection

This document describes how to connect to your TiDB Cloud Dedicated cluster via public connection. The public connection exposes a public endpoint with traffic filters, so you can connect to your TiDB Cloud Dedicated cluster via a SQL client from your laptop.

> **Tip:**
>
> To learn how to connect to a TiDB Cloud Serverless cluster via public connection, see [Connect to TiDB Cloud Serverless via Public Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection-serverless).
## Prerequisite: Configure IP access list

For public connections, TiDB Cloud Dedicated only allows client connections from addresses in the IP access list. If you have not configured the IP access list, follow the steps in [Configure an IP Access List](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-ip-access-list) to configure it before your first connection.
## Connect to the cluster

To connect to a TiDB Cloud Dedicated cluster via public connection, take the following steps:

1. Open the overview page of the target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the connection dialog, select **Public** from the **Connection Type** drop-down list.

    If you have not configured the IP access list, click **Configure IP Access List** or follow the steps in [Configure an IP Access List](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-ip-access-list) to configure it before your first connection.

4. Click **CA cert** to download CA cert for TLS connection to TiDB clusters. The CA cert supports TLS 1.2 version by default.

5. Choose your preferred connection method, and then refer to the connection string and sample code on the tab to connect to your cluster.
## What's next

After you have successfully connected to your TiDB cluster, you can [explore SQL statements with TiDB](https://docs.pingcap.com/tidb/stable/basic-sql-operations).
