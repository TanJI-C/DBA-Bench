# Configure Azure Blob SAS access for TiDB Cloud Dedicated imports

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/dedicated-external-storage.md`
- Source Title: `Configure External Storage Access for TiDB Cloud Dedicated`
- Source Heading Path: `Configure External Storage Access for TiDB Cloud Dedicated > Configure Azure Blob Storage access`
- Source Line Ranges: `216-242`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `azure-blob`, `sas-token`, `storage-account`, `container-access`, `permissions`, `data-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0230_dd1aad1bcb`
- Source ID: `tidb-docs-8.1:tidb-cloud/dedicated-external-storage.md#configure-azure-blob-storage-access`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ddffd883917b1c455b6207bde3a75f93999e77f986620947ffb5485deecf5c4b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-azure-blob-storage-access
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/dedicated-external-storage.md

## Retrieval Guidance

- Use When: Use this chunk when configuring Azure Blob Storage container access with an account SAS token for TiDB Cloud Dedicated data import.
- Retrieval Keywords: Configure Azure Blob Storage access, TiDB Cloud Dedicated, Azure Blob container, account SAS token, Shared access signature, Allowed services Blob, Allowed resource types Container, Allowed resource types Object, Allowed permissions Read, Allowed permissions List, Generate SAS and connection string, SAS Token
- Follow-up Guidance: The content notes that before starting data import, you can test the connection and permissions to ensure TiDB Cloud Dedicated can access the specified Azure Blob container and files.
- Classification Note: This is classified as configuration because the content explains how to create and use an Azure Blob account SAS token with the required services, resource types, and permissions for data import.

## Official Source Content

## Configure Azure Blob Storage access

To allow TiDB Cloud Dedicated to access your Azure Blob container, you need to configure the Azure Blob access for the container. You can use an account SAS token to configure the container access:

1. On the [Azure Storage account](https://portal.azure.com/#browse/Microsoft.Storage%2FStorageAccounts) page, click your storage account to which the container belongs.

2. In the navigation pane for your storage account, click **Security + networking** > **Shared access signature**.

    ![sas-position](/media/tidb-cloud/dedicated-external-storage/azure-sas-position.png)

3. On the **Shared access signature** page, create an [account SAS token](https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview) with the necessary permissions as follows:

    1. Under **Allowed services**, select **Blob**.
    2. Under **Allowed resource types**, select **Container** and **Object**.
    3. Under **Allowed permissions**, select the required permissions. For example, importing data to TiDB Cloud Dedicated requires **Read** and **List**.
    4. Adjust **Start and expiry date/time** as needed. For security reasons, it is recommended to set an expiration date that aligns with your data import timeline.
    5. Keep the default values for other settings.

    ![sas-create](/media/tidb-cloud/dedicated-external-storage/azure-sas-create.png)

4. Click **Generate SAS and connection string** to generate the SAS token.

5. Copy the generated **SAS Token**. You will need this token string when configuring the data import in TiDB Cloud.

> **Note:**
>
> Before starting data import, test the connection and permissions to ensure TiDB Cloud Dedicated can access the specified Azure Blob container and files.
