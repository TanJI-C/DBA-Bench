# Connect to TiDB from VS Code for cloud and self-managed deployments

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-gui-vscode-sqltools.md`
- Source Title: `Connect to TiDB with Visual Studio Code`
- Source Heading Path: `Connect to TiDB with Visual Studio Code > Connect to TiDB`
- Source Line Ranges: `45-188`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `sql`
- Topic Tags: `connection-setup`, `sqltools`, `tidb-cloud`, `self-managed`, `ssl`, `ip-access-list`, `passwords`, `connection-testing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0045_0ac4f4809c`
- Source ID: `tidb-docs-8.1:develop/dev-guide-gui-vscode-sqltools.md#connect-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `aa264bfacc829eba27b7a85c16f955a7c70c2049c774e19fb22ff2416f868e23`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-vscode-sqltools#connect-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-gui-vscode-sqltools.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the exact SQLTools connection settings and test flow for connecting VS Code to TiDB Cloud or TiDB Self-Managed.
- Retrieval Keywords: Connect to TiDB, SQLTools, Add New Connection, TiDB driver, Connect using Server and Port, TEST CONNECTION, Successfully connected!, SAVE CONNECTION, TiDB Cloud Dedicated, TiDB Self-Managed, Connection Type Public, Branch main, Connect With VS Code, Generate Password, Reset Password, Server Address HOST, Port PORT, Username USERNAME, host, port, user, Password mode SQLTools Driver Credentials, Use empty password, Authentication Protocol default, SSL Enabled, SSL Disabled, Certificate Authority (CA) Certificate File, CA cert, Configure IP Access List, Private Endpoint, VPC Peering
- Follow-up Guidance: The content also includes deployment-specific follow-up details such as selecting the remote operating system, downloading the CA cert, configuring the IP access list, and entering credentials during TEST CONNECTION.
- Classification Note: The chunk is classified as configuration because it provides deployment-specific connection parameters, SSL choices, password handling, and validation steps in VS Code SQLTools.

## Official Source Content

## Connect to TiDB

Connect to your TiDB cluster depending on the TiDB deployment option you have selected.

<div label="{{{ .starter }}} or Essential">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`.
    - **Branch** is set to `main`.
    - **Connect With** is set to `VS Code`.
    - **Operating System** matches your environment.

    > **Tip:**
    >
    > If your VS Code is running on a remote development environment, select the remote operating system from the list. For example, if you are using Windows Subsystem for Linux (WSL), switch to the corresponding Linux distribution. This is not necessary if you are using GitHub Codespaces.

4. Click **Generate Password** to create a random password.

    > **Tip:**
    >
    > If you have created a password before, you can either use the original password or click **Reset Password** to generate a new one.

5. Launch VS Code and select the **SQLTools** extension on the navigation pane. Under the **CONNECTIONS** section, click **Add New Connection** and select **TiDB** as the database driver.

    ![VS Code SQLTools: add new connection](/media/develop/vsc-sqltools-add-new-connection.jpg)

6. In the setting pane, configure the following connection parameters:

    - **Connection name**: give this connection a meaningful name.
    - **Connection group**: (optional) give this group of connections a meaningful name. Connections with the same group name will be grouped together.
    - **Connect using**: select **Server and Port**.
    - **Server Address**: enter the `HOST` parameter from the TiDB Cloud connection dialog.
    - **Port**: enter the `PORT` parameter from the TiDB Cloud connection dialog.
    - **Database**: enter the database that you want to connect to.
    - **Username**: enter the `USERNAME` parameter from the TiDB Cloud connection dialog.
    - **Password mode**: select **SQLTools Driver Credentials**.
    - In the **MySQL driver specific options** area, configure the following parameters:

        - **Authentication Protocol**: select **default**.
        - **SSL**: select **Enabled**. {{{ .starter }}} requires a secure connection. In the **SSL Options (node.TLSSocket)** area, configure the **Certificate Authority (CA) Certificate File** field as the `CA` parameter from the TiDB Cloud connection dialog.

            > **Note:**
            >
            > If you are running on Windows or GitHub Codespaces, you can leave **SSL** blank. By default SQLTools trusts well-known CAs curated by Let's Encrypt. For more information, see [{{{ .starter }}} root certificate management](https://docs.pingcap.com/tidbcloud/secure-connections-to-serverless-clusters#root-certificate-management).

    ![VS Code SQLTools: configure connection settings for {{{ .starter }}}](/media/develop/vsc-sqltools-connection-config-serverless.jpg)

7. Click **TEST CONNECTION** to validate the connection to the {{{ .starter }}} cluster.

    1. In the pop-up window, click **Allow**.
    2. In the **SQLTools Driver Credentials** dialog, enter the password you created in step 4.

        ![VS Code SQLTools: enter password to connect to {{{ .starter }}}](/media/develop/vsc-sqltools-password.jpg)

8. If the connection test is successful, you can see the **Successfully connected!** message. Click **SAVE CONNECTION** to save the connection configuration.

</div>
<div label="TiDB Cloud Dedicated">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the connection dialog, select **Public** from the **Connection Type** drop-down list, and then click **CA cert** to download the CA certificate.

    If you have not configured the IP access list, click **Configure IP Access List** or follow the steps in [Configure an IP Access List](https://docs.pingcap.com/tidbcloud/configure-ip-access-list) to configure it before your first connection.

    In addition to the **Public** connection type, TiDB Cloud Dedicated supports **Private Endpoint** and **VPC Peering** connection types. For more information, see [Connect to Your TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidbcloud/connect-to-tidb-cluster).

4. Launch VS Code and select the **SQLTools** extension on the navigation pane. Under the **CONNECTIONS** section, click **Add New Connection** and select **TiDB** as the database driver.

    ![VS Code SQLTools: add new connection](/media/develop/vsc-sqltools-add-new-connection.jpg)

5. In the setting pane, configure the following connection parameters:

    - **Connection name**: give this connection a meaningful name.
    - **Connection group**: (optional) give this group of connections a meaningful name. Connections with the same group name will be grouped together.
    - **Connect using**: select **Server and Port**.
    - **Server Address**: enter the `host` parameter from the TiDB Cloud connection dialog.
    - **Port**: enter the `port` parameter from the TiDB Cloud connection dialog.
    - **Database**: enter the database that you want to connect to.
    - **Username**: enter the `user` parameter from the TiDB Cloud connection dialog.
    - **Password mode**: select **SQLTools Driver Credentials**.
    - In the **MySQL driver specific options** area, configure the following parameters:

        - **Authentication Protocol**: select **default**.
        - **SSL**: select **Disabled**.

    ![VS Code SQLTools: configure connection settings for TiDB Cloud Dedicated](/media/develop/vsc-sqltools-connection-config-dedicated.jpg)

6. Click **TEST CONNECTION** to validate the connection to the TiDB Cloud Dedicated cluster.

    1. In the pop-up window, click **Allow**.
    2. In the **SQLTools Driver Credentials** dialog, enter the password of the TiDB Cloud Dedicated cluster.

    ![VS Code SQLTools: enter password to connect to TiDB Cloud Dedicated](/media/develop/vsc-sqltools-password.jpg)

7. If the connection test is successful, you can see the **Successfully connected!** message. Click **SAVE CONNECTION** to save the connection configuration.

</div>
<div label="TiDB Self-Managed">

1. Launch VS Code and select the **SQLTools** extension on the navigation pane. Under the **CONNECTIONS** section, click **Add New Connection** and select **TiDB** as the database driver.

    ![VS Code SQLTools: add new connection](/media/develop/vsc-sqltools-add-new-connection.jpg)

2. In the setting pane, configure the following connection parameters:
    - **Connection name**: give this connection a meaningful name.
    - **Connection group**: (optional) give this group of connections a meaningful name. Connections with the same group name will be grouped together.
    - **Connect using**: select **Server and Port**.
    - **Server Address**: enter the IP address or domain name of your TiDB Self-Managed cluster.
    - **Port**: enter the port number of your TiDB Self-Managed cluster.
    - **Database**: enter the database that you want to connect to.
    - **Username**: enter the username to use to connect to your TiDB Self-Managed cluster.
    - **Password mode**:

        - If the password is empty, select **Use empty password**.
        - Otherwise, select **SQLTools Driver Credentials**.

    - In the **MySQL driver specific options** area, configure the following parameters:

        - **Authentication Protocol**: select **default**.
        - **SSL**: select **Disabled**.

    ![VS Code SQLTools: configure connection settings for TiDB Self-Managed](/media/develop/vsc-sqltools-connection-config-self-hosted.jpg)

3. Click **TEST CONNECTION** to validate the connection to the TiDB Self-Managed cluster.

    If the password is not empty, click **Allow** in the pop-up window, and then enter the password of the TiDB Self-Managed cluster.

    ![VS Code SQLTools: enter password to connect to TiDB Self-Managed](/media/develop/vsc-sqltools-password.jpg)

4. If the connection test is successful, you can see the **Successfully connected!** message. Click **SAVE CONNECTION** to save the connection configuration.

</div>
