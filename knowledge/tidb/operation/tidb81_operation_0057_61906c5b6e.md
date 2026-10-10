# Connect TiDB from DBeaver

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-gui-dbeaver.md`
- Source Title: `Connect to TiDB with DBeaver`
- Source Heading Path: `Connect to TiDB with DBeaver > Connect to TiDB`
- Source Line Ranges: `40-160`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `cloud`
- Topic Tags: `dbeaver`, `connection`, `public endpoint`, `credentials`, `ssl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0057_61906c5b6e`
- Source ID: `tidb-docs-8.1:develop/dev-guide-gui-dbeaver.md#connect-to-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f93382f9a3d7f39c66b0759035efaf3d981b4c5241c034953165a018c157cfc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-dbeaver#connect-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-gui-dbeaver.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the exact DBeaver connection steps for TiDB Cloud Starter or Essential, TiDB Cloud Dedicated, or TiDB Self-Managed.
- Retrieval Keywords: New Database Connection, Connect to a database, select TiDB, Test Connection, Download driver files, Connection test, Connection Type Public, Branch main, Connect With DBeaver, Generate Password, Reset Password, URL for Connect by, CA cert, Configure IP Access List, Private Endpoint, VPC Peering, Server Host, Port, Username, Password
- Follow-up Guidance: The content distinguishes connection steps by deployment option and includes TiDB Cloud connection dialog settings, DBeaver field mappings, and connection validation steps.
- Classification Note: This is classified as an operation chunk because it provides the procedural connection workflow and required connection fields in DBeaver.

## Official Source Content

## Connect to TiDB

Connect to your TiDB cluster depending on the TiDB deployment option you've selected.

<div label="{{{ .starter }}} or Essential">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`
    - **Branch** is set to `main`
    - **Connect With** is set to `DBeaver`
    - **Operating System** matches your environment.

4. Click **Generate Password** to create a random password.

    > **Tip:**
    >
    > If you have created a password before, you can either use the original password or click **Reset Password** to generate a new one.

5. Launch DBeaver and click **New Database Connection** in the upper-left corner. In the **Connect to a database** dialog, select **TiDB** from the list, and then click **Next**.

    ![Select TiDB as the database in DBeaver](/media/develop/dbeaver-select-database.jpg)

6. Copy the connection string from the TiDB Cloud connection dialog. In DBeaver, select **URL** for **Connect by** and paste the connection string into the **URL** field.

7. In the **Authentication (Database Native)** section, enter your **Username** and **Password**. An example is as follows:

    ![Configure connection settings for {{{ .starter }}}](/media/develop/dbeaver-connection-settings-serverless.jpg)

8. Click **Test Connection** to validate the connection to the {{{ .starter }}} cluster.

    If the **Download driver files** dialog is displayed, click **Download** to get the driver files.

    ![Download driver files](/media/develop/dbeaver-download-driver.jpg)

    If the connection test is successful, the **Connection test** dialog is displayed as follows. Click **OK** to close it.

    ![Connection test result](/media/develop/dbeaver-connection-test.jpg)

9. Click **Finish** to save the connection configuration.

</div>
<div label="TiDB Cloud Dedicated">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the connection dialog, select **Public** from the **Connection Type** drop-down list, and then click **CA cert** to download the CA certificate.

    If you have not configured the IP access list, click **Configure IP Access List** or follow the steps in [Configure an IP Access List](https://docs.pingcap.com/tidbcloud/configure-ip-access-list) to configure it before your first connection.

    In addition to the **Public** connection type, TiDB Cloud Dedicated supports **Private Endpoint** and **VPC Peering** connection types. For more information, see [Connect to Your TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidbcloud/connect-to-tidb-cluster).

4. Launch DBeaver and click **New Database Connection** in the upper-left corner. In the **Connect to a database** dialog, select **TiDB** from the list, and then click **Next**.

    ![Select TiDB as the database in DBeaver](/media/develop/dbeaver-select-database.jpg)

5. Copy and paste the appropriate connection string into the DBeaver connection panel. The mappings between DBeaver fields and TiDB Cloud Dedicated connection string are as follows:

    | DBeaver field | TiDB Cloud Dedicated connection string |
    |---------------| ------------------------------- |
    | Server Host   | `{host}`                        |
    | Port          | `{port}`                        |
    | Username      | `{user}`                        |
    | Password      | `{password}`                    |

    An example is as follows:

    ![Configure connection settings for TiDB Cloud Dedicated](/media/develop/dbeaver-connection-settings-dedicated.jpg)

6. Click **Test Connection** to validate the connection to the TiDB Cloud Dedicated cluster.

    If the **Download driver files** dialog is displayed, click **Download** to get the driver files.

    ![Download driver files](/media/develop/dbeaver-download-driver.jpg)

    If the connection test is successful, the **Connection test** dialog is displayed as follows. Click **OK** to close it.

    ![Connection test result](/media/develop/dbeaver-connection-test.jpg)

7. Click **Finish** to save the connection configuration.

</div>
<div label="TiDB Self-Managed">

1. Launch DBeaver and click **New Database Connection** in the upper-left corner. In the **Connect to a database** dialog, select **TiDB** from the list, and then click **Next**.

    ![Select TiDB as the database in DBeaver](/media/develop/dbeaver-select-database.jpg)

2. Configure the following connection parameters:

    - **Server Host**: The IP address or domain name of your TiDB Self-Managed cluster.
    - **Port**: The port number of your TiDB Self-Managed cluster.
    - **Username**: The username to use to connect to your TiDB Self-Managed cluster.
    - **Password**: The password of the username.

    An example is as follows:

    ![Configure connection settings for TiDB Self-Managed](/media/develop/dbeaver-connection-settings-self-hosted.jpg)

3. Click **Test Connection** to validate the connection to the TiDB Self-Managed cluster.

    If the **Download driver files** dialog is displayed, click **Download** to get the driver files.

    ![Download driver files](/media/develop/dbeaver-download-driver.jpg)

    If the connection test is successful, the **Connection test** dialog is displayed as follows. Click **OK** to close it.

    ![Connection test result](/media/develop/dbeaver-connection-test.jpg)

4. Click **Finish** to save the connection configuration.

</div>
