# Enable audit logging with Azure Blob Storage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-auditing.md`
- Source Title: `TiDB Cloud Dedicated Database Audit Logging`
- Source Heading Path: `TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for Azure > Step 2. Configure Azure Blob Storage access | TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for Azure > Step 3. Enable audit logging`
- Source Line Ranges: `187-248`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `audit-logging`, `azure`, `blob-storage`, `sas-token`, `connection-test`, `cluster-settings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0298_ba6b6a3499`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-auditing.md#step-2-configure-azure-blob-storage-access`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ef4b554941ed031c9e10bfe0b42055b92e4b7b221155d8e683ebe937b0afc32b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-auditing#step-2-configure-azure-blob-storage-access
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-auditing.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the exact TiDB Cloud Dedicated audit logging setup for Azure Blob Storage, including container URL, SAS token, Test Connection, and Enable steps.
- Retrieval Keywords: Azure Blob Storage, Blob URL, SAS Token, Generate SAS, Account key, Read Write Create, HTTPS only, Test Connection, The connection is successfully, DB Audit Logging, Enable Database Audit Logging, Settings > DB Audit Logging
- Follow-up Guidance: If Blob URL or SAS Token is changed after audit logging is enabled, the content says to click Test Connection again and then click Enable to apply the changes.
- Classification Note: This is configuration content because it describes how to configure Azure Blob Storage access and enable DB Audit Logging in the TiDB Cloud console.

## Official Source Content

#### Step 2. Configure Azure Blob Storage access

1. In the [Azure portal](https://portal.azure.com/), create a container used for storing database audit logs.

    1. In the left navigation pane of the Azure portal, click **Storage Accounts**, and then click the storage account for storing database audit logs.

        > **Tip:**
        >
        > If the left navigation pane is hidden, click the menu button in the upper-left corner to toggle its visibility.

    2. In the navigation pane for the selected storage account, click **Data storage > Containers**, and then click **+ Container** to open the **New container** pane.

    3. In the **New container** pane, enter a name for your new container, set the anonymous access level (the recommended level is **Private**, which means no anonymous access), and then click **Create**. The new container will be created and displayed in the container list in a few seconds.

2. Get the URL of the target container.

    1. In the container list, select the target container, click **...** for the container, and then select **Container properties**.
    2. On the displayed properties page, copy the **URL** value for later use, and then return to the container list.

3. Generate a SAS token for the target container.

    1. In the container list, select the target container, click **...** for the container, and then select **Generate SAS**.
    2. In the displayed **Generate SAS** pane, select **Account key** for **Signing method**.
    3. In the **Permissions** drop-down list, select **Read**, **Write**, and **Create** to allow writing audit log files.
    4. In the **Start** and **Expiry** fields, specify a validity period for the SAS token.

        > **Note:**
        >
        > - The audit feature needs to continuously write audit logs to the storage account, so the SAS token must have a sufficiently long validity period. However, longer validity increases the risk of token leakage. For security, it is recommended to replace your SAS token every six to twelve months.
        > - The generated SAS token cannot be revoked, so you need to set its validity period carefully.
        > - Make sure to re-generate and update the SAS token before it expires to ensure continuous availability of audit logs.

    5. For **Allowed protocols**, select **HTTPS only** to ensure secure access.
    6. Click **Generate SAS token and URL**, and then copy the displayed **Blob SAS token** for later use.
#### Step 3. Enable audit logging

1. In the TiDB Cloud console, navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of your target cluster to go to its overview page, and then click **Settings** > **DB Audit Logging** in the left navigation pane.
3. On the **DB Audit Logging** page, click **Enable** in the upper-right corner.
4. In the **Enable Database Audit Logging** dialog, provide the blob URL and SAS token that you obtained from [Step 2. Configure Azure Blob access](#step-2-configure-azure-blob-storage-access):

    - In the **Blob URL** field, enter the URL of the container where audit logs will be stored.
    - In the **SAS Token** field, enter the SAS token for accessing the container.

5. Click **Test Connection** to verify whether TiDB Cloud can access and write to the container.

    If it is successful, **The connection is successfully** is displayed. Otherwise, check your access configuration.

6. Click **Enable** to enable audit logging for the cluster.

    TiDB Cloud is ready to write audit logs for the specified cluster to your Azure blob container.

> **Note:**
>
> After enabling audit logging, if you make new changes to the **Blob URL** or **SAS Token** fields, you must click **Test Connection** again to verify that TiDB Cloud can connect to the container. Then, click **Enable** to apply the changes.
