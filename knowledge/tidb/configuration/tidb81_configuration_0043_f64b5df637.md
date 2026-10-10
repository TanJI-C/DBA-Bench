# Connect TiDB with MySQL Workbench

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-gui-mysql-workbench.md`
- Source Title: `Connect to TiDB with MySQL Workbench`
- Source Heading Path: `Connect to TiDB with MySQL Workbench | Connect to TiDB with MySQL Workbench > Prerequisites | Connect to TiDB with MySQL Workbench > Connect to TiDB`
- Source Line Ranges: `5-153`
- Source Scope: `all`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `sql`
- Topic Tags: `mysql workbench`, `connection`, `prerequisites`, `tls`, `password`, `cloud dedicated`, `self-managed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0043_f64b5df637`
- Source ID: `tidb-docs-8.1:develop/dev-guide-gui-mysql-workbench.md#connect-to-tidb-with-mysql-workbench`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a5ebec30d185ab9b76804826853d02ff7deaa2a7a5cd75266724059108f1ee42`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-mysql-workbench#connect-to-tidb-with-mysql-workbench
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-gui-mysql-workbench.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the prerequisites or connection dialog fields for connecting a TiDB cluster to MySQL Workbench across TiDB Cloud Starter or Essential, TiDB Cloud Dedicated, or TiDB Self-Managed.
- Retrieval Keywords: Connect TiDB with MySQL Workbench, MySQL Workbench 8.0.31 or later, Setup New Connection, MySQL Connections, HOST, PORT, USERNAME, Generate Password, Reset Password, Test Connection, Successfully made the MySQL connection, Connection Type Public, Branch main, Connect With MySQL Workbench, CA cert, Configure IP Access List, TiDB Cloud Dedicated, TiDB Self-Managed
- Follow-up Guidance: The source also notes that MySQL Workbench does not fully support TiDB and points to DataGrip, DBeaver, VS Code SQLTools, and Third-party tools supported by TiDB for GUI tools that fully support TiDB.
- Classification Note: This is classified as configuration because the content is a step-by-step setup guide for MySQL Workbench connection parameters and related connection dialog options.

## Official Source Content

# Connect to TiDB with MySQL Workbench

TiDB is a MySQL-compatible database, and [MySQL Workbench](https://www.mysql.com/products/workbench/) is a GUI tool set for MySQL database users.

> **Warning:**
>
> - Although you can use MySQL Workbench to connect to TiDB due to its MySQL compatibility, MySQL Workbench does not fully support TiDB. You might encounter some issues during usage as it treats TiDB as MySQL.
> - It is recommended to use other GUI tools that officially support TiDB, such as [DataGrip](https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-datagrip), [DBeaver](https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-dbeaver), and [VS Code SQLTools](https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-vscode-sqltools). For a complete list of GUI tools that fully supported by TiDB, see [Third-party tools supported by TiDB](https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-support#gui).

In this tutorial, you can learn how to connect to your TiDB cluster using MySQL Workbench.

> **Note:**
>
> This tutorial is compatible with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.
## Prerequisites

To complete this tutorial, you need:

- [MySQL Workbench](https://dev.mysql.com/downloads/workbench/) **8.0.31** or later versions.
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
    - **Connect With** is set to `MySQL Workbench`.
    - **Operating System** matches your environment.

4. Click **Generate Password** to create a random password.

    > **Tip:**
    >
    > If you have created a password before, you can either use the original password or click **Reset Password** to generate a new one.

5. Launch MySQL Workbench and click **+** near the **MySQL Connections** title.

    ![MySQL Workbench: add new connection](/media/develop/mysql-workbench-add-new-connection.png)

6. In the **Setup New Connection** dialog, configure the following connection parameters:

    - **Connection Name**: give this connection a meaningful name.
    - **Hostname**: enter the `HOST` parameter from the TiDB Cloud connection dialog.
    - **Port**: enter the `PORT` parameter from the TiDB Cloud connection dialog.
    - **Username**: enter the `USERNAME` parameter from the TiDB Cloud connection dialog.
    - **Password**: click **Store in Keychain ...** or **Store in Vault**, enter the password of the {{{ .starter }}} cluster, and then click **OK** to store the password.

        ![MySQL Workbench: store the password of {{{ .starter }}} in keychain](/media/develop/mysql-workbench-store-password-in-keychain.png)

    The following figure shows an example of the connection parameters:

    ![MySQL Workbench: configure connection settings for {{{ .starter }}}](/media/develop/mysql-workbench-connection-config-serverless-parameters.png)

7. Click **Test Connection** to validate the connection to the {{{ .starter }}} cluster.

8. If the connection test is successful, you can see the **Successfully made the MySQL connection** message. Click **OK** to save the connection configuration.

</div>
<div label="TiDB Cloud Dedicated">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the connection dialog, select **Public** from the **Connection Type** drop-down list, and then click **CA cert** to download the CA certificate.

    If you have not configured the IP access list, click **Configure IP Access List** or follow the steps in [Configure an IP Access List](https://docs.pingcap.com/tidbcloud/configure-ip-access-list) to configure it before your first connection.

    In addition to the **Public** connection type, TiDB Cloud Dedicated supports **Private Endpoint** and **VPC Peering** connection types. For more information, see [Connect to Your TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidbcloud/connect-to-tidb-cluster).

4. Launch MySQL Workbench and click **+** near the **MySQL Connections** title.

    ![MySQL Workbench: add new connection](/media/develop/mysql-workbench-add-new-connection.png)

5. In the **Setup New Connection** dialog, configure the following connection parameters:

    - **Connection Name**: give this connection a meaningful name.
    - **Hostname**: enter the `HOST` parameter from the TiDB Cloud connection dialog.
    - **Port**: enter the `PORT` parameter from the TiDB Cloud connection dialog.
    - **Username**: enter the `USERNAME` parameter from the TiDB Cloud connection dialog.
    - **Password**: click **Store in Keychain ...**, enter the password of the TiDB Cloud Dedicated cluster, and then click **OK** to store the password.

        ![MySQL Workbench: store the password of TiDB Cloud Dedicated in keychain](/media/develop/mysql-workbench-store-dedicated-password-in-keychain.png)

    The following figure shows an example of the connection parameters:

    ![MySQL Workbench: configure connection settings for TiDB Cloud Dedicated](/media/develop/mysql-workbench-connection-config-dedicated-parameters.png)

6. Click **Test Connection** to validate the connection to the TiDB Cloud Dedicated cluster.

7. If the connection test is successful, you can see the **Successfully made the MySQL connection** message. Click **OK** to save the connection configuration.

</div>
<div label="TiDB Self-Managed">

1. Launch MySQL Workbench and click **+** near the **MySQL Connections** title.

    ![MySQL Workbench: add new connection](/media/develop/mysql-workbench-add-new-connection.png)

2. In the **Setup New Connection** dialog, configure the following connection parameters:

    - **Connection Name**: give this connection a meaningful name.
    - **Hostname**: enter the IP address or domain name of your TiDB Self-Managed cluster.
    - **Port**: enter the port number of your TiDB Self-Managed cluster.
    - **Username**: enter the username to use to connect to your TiDB.
    - **Password**: click **Store in Keychain ...**, enter the password to use to connect to your TiDB cluster, and then click **OK** to store the password.

        ![MySQL Workbench: store the password of TiDB Self-Managed in keychain](/media/develop/mysql-workbench-store-self-hosted-password-in-keychain.png)

    The following figure shows an example of the connection parameters:

    ![MySQL Workbench: configure connection settings for TiDB Self-Managed](/media/develop/mysql-workbench-connection-config-self-hosted-parameters.png)

3. Click **Test Connection** to validate the connection to the TiDB Self-Managed cluster.

4. If the connection test is successful, you can see the **Successfully made the MySQL connection** message. Click **OK** to save the connection configuration.

</div>
