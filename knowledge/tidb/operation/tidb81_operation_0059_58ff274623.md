# Connect to TiDB with Navicat

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-gui-navicat.md`
- Source Title: `Connect to TiDB with Navicat`
- Source Heading Path: `Connect to TiDB with Navicat | Connect to TiDB with Navicat > Prerequisites | Connect to TiDB with Navicat > Connect to TiDB | Connect to TiDB with Navicat > Next steps | Connect to TiDB with Navicat > Need help?`
- Source Line Ranges: `5-165`
- Source Scope: `all`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `tiup`
- Topic Tags: `navicat`, `gui`, `connection`, `prerequisites`, `ssl`, `password`, `ip-access-list`, `developer-guide`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0059_58ff274623`
- Source ID: `tidb-docs-8.1:develop/dev-guide-gui-navicat.md#connect-to-tidb-with-navicat`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `28b5ed876dad200e09be4a7d4368a64699ed75677adddfcbf5ea6aea03d1e27c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-navicat#connect-to-tidb-with-navicat
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-gui-navicat.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the official prerequisites and connection steps for connecting a TiDB cluster to Navicat Premium, including TiDB Cloud Starter or Essential, TiDB Cloud Dedicated, or TiDB Self-Managed.
- Retrieval Keywords: Connect to TiDB with Navicat, Navicat Premium 17.1.6 or later, New Connection (TiDB), Vendor Filter PingCAP, Test Connection, Connection Successful, TiDB Cloud connection dialog, Generate Password, Reset Password, Connection Type Public, Branch main, Connect With Navicat, CA cert, CA Certificate, Use SSL, Use authentication, Verify server certificate against CA, Configure IP Access List, HOST, PORT, USERNAME, TiDB Self-Managed
- Follow-up Guidance: The source also points to the Developer guide, TiDB developer courses and certifications, and community or support channels such as Discord, Slack, and support tickets.
- Classification Note: This is classified as an operation chunk because the official content is a step-by-step procedure for establishing a GUI connection from Navicat to different TiDB deployment options.

## Official Source Content

# Connect to TiDB with Navicat

TiDB is a MySQL-compatible database, and [Navicat](https://www.navicat.com) is a GUI tool set for database users. This tutorial uses the [Navicat Premium](https://www.navicat.com/en/products/navicat-premium) tool to connect to TiDB.

In this tutorial, you can learn how to connect to your TiDB cluster using Navicat.

> **Note:**
>
> This tutorial is compatible with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.
## Prerequisites

To complete this tutorial, you need:

- [Navicat Premium](https://www.navicat.com) **17.1.6** or later versions.
- A paid account for Navicat Premium.
- A TiDB cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.
## Connect to TiDB

Connect to your TiDB cluster depending on the TiDB deployment option you have selected.

<div label="{{{ .starter }}} or Essential">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`.
    - **Branch** is set to `main`.
    - **Connect With** is set to `Navicat`.
    - **Operating System** matches your environment.

4. Click **Generate Password** to create a random password.

    > **Tip:**
    >
    > If you have created a password before, you can either use the original password or click **Reset Password** to generate a new one.

5. Launch Navicat Premium, click **Connection** in the upper-left corner, select **PingCAP** from the **Vendor Filter** list, and double-click **TiDB** in the right panel.

    ![Navicat: add new connection](/media/develop/navicat-premium-add-new-connection.png)

6. In the **New Connection (TiDB)** dialog, configure the following connection parameters:

    - **Connection Name**: give this connection a meaningful name.
    - **Host**: enter the `HOST` parameter from the TiDB Cloud connection dialog.
    - **Port**: enter the `PORT` parameter from the TiDB Cloud connection dialog.
    - **User Name**: enter the `USERNAME` parameter from the TiDB Cloud connection dialog.
    - **Password**: enter the password of the {{{ .starter }}} cluster.

    ![Navicat: configure connection general panel for {{{ .starter }}}](/media/develop/navicat-premium-connection-config-serverless-general.png)

7. Click the **SSL** tab and select **Use SSL**, **Use authentication**, and **Verify server certificate against CA** checkboxes. Then, select the `CA` file from the TiDB Cloud connection dialog into the **CA Certificate** field.

    ![Navicat: configure connection SSL panel for {{{ .starter }}}](/media/develop/navicat-premium-connection-config-serverless-ssl.png)

8. Click **Test Connection** to validate the connection to the {{{ .starter }}} cluster.

9. If the connection test is successful, you can see the **Connection Successful** message. Click **OK** to finish the connection configuration.

</div>
<div label="TiDB Cloud Dedicated">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the connection dialog, select **Public** from the **Connection Type** drop-down list.

    If you have not configured the IP access list, click **Configure IP Access List** or follow the steps in [Configure an IP Access List](https://docs.pingcap.com/tidbcloud/configure-ip-access-list) to configure it before your first connection.

    In addition to the **Public** connection type, TiDB Cloud Dedicated supports **Private Endpoint** and **VPC Peering** connection types. For more information, see [Connect to Your TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidbcloud/connect-to-tidb-cluster).

4. Click **CA cert** to download the CA certificate.

5. Launch Navicat Premium, click **Connection** in the upper-left corner, select **PingCAP** from the **Vendor Filter** list, and double-click **TiDB** in the right panel.

    ![Navicat: add new connection](/media/develop/navicat-premium-add-new-connection.png)

6. In the **New Connection (TiDB)** dialog, configure the following connection parameters:

    - **Connection Name**: give this connection a meaningful name.
    - **Host**: enter the `HOST` parameter from the TiDB Cloud connection dialog.
    - **Port**: enter the `PORT` parameter from the TiDB Cloud connection dialog.
    - **User Name**: enter the `USERNAME` parameter from the TiDB Cloud connection dialog.
    - **Password**: enter the password of the TiDB Cloud Dedicated cluster.

    ![Navicat: configure connection general panel for TiDB Cloud Dedicated](/media/develop/navicat-premium-connection-config-dedicated-general.png)

7. Click the **SSL** tab and select **Use SSL**, **Use authentication**, and **Verify server certificate against CA** checkboxes. Then, select the CA file downloaded in step 4 into the **CA Certificate** field.

    ![Navicat: configure connection SSL panel for TiDB Cloud Dedicated](/media/develop/navicat-premium-connection-config-dedicated-ssl.png)

8. **Test Connection** to validate the connection to the TiDB Cloud Dedicated cluster.

9. If the connection test is successful, you can see the **Connection Successful** message. Click **OK** to finish the connection configuration.

</div>
<div label="TiDB Self-Managed">

1. Launch Navicat Premium, click **Connection** in the upper-left corner, select **PingCAP** from the **Vendor Filter** list, and double-click **TiDB** in the right panel.

    ![Navicat: add new connection](/media/develop/navicat-premium-add-new-connection.png)

2. In the **New Connection (TiDB)** dialog, configure the following connection parameters:

    - **Connection Name**: give this connection a meaningful name.
    - **Host**: enter the IP address or domain name of your TiDB Self-Managed cluster.
    - **Port**: enter the port number of your TiDB Self-Managed cluster.
    - **User Name**: enter the username to use to connect to your TiDB.
    - **Password**: enter the password to use to connect to your TiDB.

    ![Navicat: configure connection general panel for self-hosted TiDB](/media/develop/navicat-premium-connection-config-self-hosted-general.png)

3. Click **Test Connection** to validate the connection to the TiDB Self-Managed cluster.

4. If the connection test is successful, you can see the **Connection Successful** message. Click **OK** to finish the connection configuration.

</div>
## Next steps

- Learn the best practices for TiDB application development with the chapters in the [Developer guide](https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview), such as [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data), [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data), [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data), [Single table reading](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table), [Transactions](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview), and [SQL performance optimization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview).
- Learn through the professional [TiDB developer courses](https://www.pingcap.com/education/) and earn [TiDB certifications](https://www.pingcap.com/education/certification/) after passing the exam.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
