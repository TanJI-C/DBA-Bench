# Connect TiDB from DataGrip

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-gui-datagrip.md`
- Source Title: `Connect to TiDB with JetBrains DataGrip`
- Source Heading Path: `Connect to TiDB with JetBrains DataGrip > Connect to TiDB`
- Source Line Ranges: `45-171`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`
- Topic Tags: `connection`, `datagrip`, `ssl`, `tls`, `password`, `driver`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0042_de4afc8859`
- Source ID: `tidb-docs-8.1:develop/dev-guide-gui-datagrip.md#connect-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `28c6a1e1421d928aa13387db34a4ae639021563ba274fab8ca8c6eb9c7e643a4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-datagrip#connect-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-gui-datagrip.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented DataGrip connection steps for a TiDB cluster, including deployment-specific fields, SSL or TLS settings, password generation, or driver download prompts.
- Retrieval Keywords: Connect to TiDB, Clusters page, Connect, Generate Password, Reset Password, Data Source > Other > TiDB, URL field, Download missing driver files, Test Connection, TiDB Cloud Dedicated, CA cert, Configure IP Access List, SSH/SSL, Use SSL, CA file, enabledTLSProtocols, TLSv1.2,TLSv1.3, TiDB Self-Managed, Host, Port, User, Password, Public, Branch main, Connect With DataGrip
- Follow-up Guidance: The source separates the procedure for Starter or Essential, TiDB Cloud Dedicated, and TiDB Self-Managed, with Dedicated additionally covering CA certificate, IP access list, SSL, and enabledTLSProtocols.
- Classification Note: This is classified as configuration because the content provides step-by-step connection setup parameters and UI selections in DataGrip for different TiDB deployment options.

## Official Source Content

## Connect to TiDB

Connect to your TiDB cluster depending on the TiDB deployment option you've selected.

<div label="{{{ .starter }}} or Essential">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`
    - **Branch** is set to `main`
    - **Connect With** is set to `DataGrip`
    - **Operating System** matches your environment.

4. Click **Generate Password** to create a random password.

    > **Tip:**
    >
    > If you have created a password before, you can either use the original password or click **Reset Password** to generate a new one.

5. Launch DataGrip and create a project to manage your connections.

    ![Create a project in DataGrip](/media/develop/datagrip-create-project.jpg)

6. In the newly created project, click **+** in the upper-left corner of the **Database Explorer** panel, and select **Data Source** > **Other** > **TiDB**.

    ![Select a data source in DataGrip](/media/develop/datagrip-data-source-select.jpg)

7. Copy the connection string from the TiDB Cloud connection dialog. Then, paste it into the **URL** field, and the remaining parameters will be auto-populated. An example result is as follows:

    ![Configure the URL field for {{{ .starter }}}](/media/develop/datagrip-url-paste.jpg)

    If a **Download missing driver files** warning displays, click **Download** to acquire the driver files.

8. Click **Test Connection** to validate the connection to the {{{ .starter }}} cluster.

    ![Test the connection to a {{{ .starter }}} cluster](/media/develop/datagrip-test-connection.jpg)

9. Click **OK** to save the connection configuration.

</div>
<div label="TiDB Cloud Dedicated">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the connection dialog, select **Public** from the **Connection Type** drop-down list, and then click **CA cert** to download the CA certificate.

    If you have not configured the IP access list, click **Configure IP Access List** or follow the steps in [Configure an IP Access List](https://docs.pingcap.com/tidbcloud/configure-ip-access-list) to configure it before your first connection.

    In addition to the **Public** connection type, TiDB Cloud Dedicated supports **Private Endpoint** and **VPC Peering** connection types. For more information, see [Connect to Your TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidbcloud/connect-to-tidb-cluster).

4. Launch DataGrip and create a project to manage your connections.

    ![Create a project in DataGrip](/media/develop/datagrip-create-project.jpg)

5. In the newly created project, click **+** in the upper-left corner of the **Database Explorer** panel, and select **Data Source** > **Other** > **TiDB**.

    ![Select a data source in DataGrip](/media/develop/datagrip-data-source-select.jpg)

6. Copy and paste the appropriate connection string into the **Data Source and Drivers** window in DataGrip. The mappings between DataGrip fields and TiDB Cloud Dedicated connection string are as follows:

    | DataGrip field | TiDB Cloud Dedicated connection string |
    | -------------- | ------------------------------- |
    | Host           | `{host}`                        |
    | Port           | `{port}`                        |
    | User           | `{user}`                        |
    | Password       | `{password}`                    |

    An example is as follows:

    ![Configure the connection parameters for TiDB Cloud Dedicated](/media/develop/datagrip-dedicated-connect.jpg)

7. Click the **SSH/SSL** tab, select the **Use SSL** checkbox, and input the CA certificate path into the **CA file** field.

    ![Configure the CA for TiDB Cloud Dedicated](/media/develop/datagrip-dedicated-ssl.jpg)

    If a **Download missing driver files** warning displays, click **Download** to acquire the driver files.

8. Click the **Advanced** tab, scroll to find the **enabledTLSProtocols** parameter, and set its value to `TLSv1.2,TLSv1.3`.

    ![Configure the TLS for TiDB Cloud Dedicated](/media/develop/datagrip-dedicated-advanced.jpg)

9. Click **Test Connection** to validate the connection to the TiDB Cloud Dedicated cluster.

    ![Test the connection to a TiDB Cloud Dedicated cluster](/media/develop/datagrip-dedicated-test-connection.jpg)

10. Click **OK** to save the connection configuration.

</div>
<div label="TiDB Self-Managed">

1. Launch DataGrip and create a project to manage your connections.

    ![Create a project in DataGrip](/media/develop/datagrip-create-project.jpg)

2. In the newly created project, click **+** in the upper-left corner of the **Database Explorer** panel, and select **Data Source** > **Other** > **TiDB**.

    ![Select a data source in DataGrip](/media/develop/datagrip-data-source-select.jpg)

3. Configure the following connection parameters:

    - **Host**: The IP address or domain name of your TiDB Self-Managed cluster.
    - **Port**: The port number of your TiDB Self-Managed cluster.
    - **User**: The username to use to connect to your TiDB Self-Managed cluster.
    - **Password**: The password of the username.

    An example is as follows:

    ![Configure the connection parameters for TiDB Self-Managed](/media/develop/datagrip-self-hosted-connect.jpg)

    If a **Download missing driver files** warning displays, click **Download** to acquire the driver files.

4. Click **Test Connection** to validate the connection to the TiDB Self-Managed cluster.

    ![Test the connection to a TiDB Self-Managed cluster](/media/develop/datagrip-self-hosted-test-connection.jpg)

5. Click **OK** to save the connection configuration.

</div>
