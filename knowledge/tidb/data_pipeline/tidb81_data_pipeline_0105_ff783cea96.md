# Export examples to Azure Blob Storage and Alibaba Cloud OSS

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-export.md`
- Source Title: `Export Data from TiDB Cloud Serverless`
- Source Heading Path: `Export Data from TiDB Cloud Serverless > Examples > Export data to Azure Blob Storage | Export Data from TiDB Cloud Serverless > Examples > Export data to Alibaba Cloud OSS`
- Source Line Ranges: `306-384`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `export`, `external-storage`, `azure-blob`, `alibaba-oss`, `console`, `cli`, `task-creation`, `credentials`, `uri`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0105_ff783cea96`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-export.md#export-data-to-azure-blob-storage`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7e35834b4c84035ff6dd8db8539a36055a4ab72884b302f66e8b79d2f6ee0131`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-export#export-data-to-azure-blob-storage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-export.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the exact TiDB Cloud Serverless export options or CLI flags for exporting data to Azure Blob Storage or Alibaba Cloud OSS.
- Retrieval Keywords: Export data to Azure Blob Storage, Export data to Alibaba Cloud OSS, Azure Blob Storage, Alibaba Cloud OSS, ticloud serverless export create, --target-type AZURE_BLOB, --azblob.uri, --azblob.sas-token, azure://<account-name>.blob.core.windows.net/<container-name>/<folder-path>/, (azure|https)://<account-name>.blob.core.windows.net/<container-name>/<folder-path>/, SAS Token, --target-type OSS, --oss.uri, --oss.access-key-id, --oss.access-key-secret, oss://<bucket-name>/<folder-path>/, Task Name, SNAPSHOT_{snapshot_time}, Data Format, SQL, CSV, Parquet, Compression, Gzip, Snappy, Zstd, Folder URI, Export Data to
- Follow-up Guidance: The source also points to Configure External Storage Access for TiDB Cloud Serverless for Azure Blob Storage access details.
- Classification Note: This chunk is classified as data_pipeline because it describes export task creation, destination storage URIs, credentials, and related console and CLI parameters for external storage targets.

## Official Source Content

### Export data to Azure Blob Storage

<div label="Console">

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

   > **Tip:**
   >
   > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

3. On the **Import** page, click **Export Data to** in the upper-right corner, and then choose **Azure Blob Storage** from the drop-down list. Fill in the following parameters:

    - **Task Name**: enter a name for the export task. The default value is `SNAPSHOT_{snapshot_time}`.
    - **Exported Data**: choose the databases and tables you want to export.
    - **Data Format**: choose **SQL**, **CSV**, or **Parquet**.
    - **Compression**: choose **Gzip**, **Snappy**, **Zstd**, or **None**.
    - **Folder URI**: enter the URI of Azure Blob Storage with the `azure://<account-name>.blob.core.windows.net/<container-name>/<folder-path>/` format.
    - **SAS Token**: enter the SAS token that has the permission to access the container. It is recommended to create a SAS token with the [Azure ARM template](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/). For more information, see [Configure External Storage Access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-azure-blob-storage-access).

4. Click **Export**.

</div>

<div label="CLI">

```shell
ticloud serverless export create -c <cluster-id> --target-type AZURE_BLOB --azblob.uri <uri> --azblob.sas-token <sas-token> --filter "database.table"
```

- `azblob.uri`: the URI of the Azure Blob Storage in the `(azure|https)://<account-name>.blob.core.windows.net/<container-name>/<folder-path>/` format.
- `azblob.sas-token`: the account SAS token of the Azure Blob Storage.

</div>
### Export data to Alibaba Cloud OSS

<div label="Console">

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

   > **Tip:**
   >
   > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

3. On the **Import** page, click **Export Data to** in the upper-right corner, and then choose **Alibaba Cloud OSS** from the drop-down list. 

4. Fill in the following parameters:

    - **Task Name**: enter a name for the export task. The default value is `SNAPSHOT_{snapshot_time}`.
    - **Exported Data**: choose the databases and tables you want to export.
    - **Data Format**: choose **SQL**, **CSV**, or **Parquet**.
    - **Compression**: choose **Gzip**, **Snappy**, **Zstd**, or **None**.
    - **Folder URI**: enter the Alibaba Cloud OSS URI where you want to export the data, in the `oss://<bucket-name>/<folder-path>/` format.
    - **AccessKey ID** and **AccessKey Secret**: enter the AccessKey ID and AccessKey Secret that have the permission to access the bucket.

5. Click **Export**.

</div>

<div label="CLI">

```shell
ticloud serverless export create -c <cluster-id> --target-type OSS --oss.uri <uri> --oss.access-key-id <access-key-id> --oss.access-key-secret <access-key-secret> --filter "database.table"
```

- `oss.uri`: the Alibaba Cloud OSS URI where you want to export the data, in the `oss://<bucket-name>/<folder-path>/` format.
- `oss.access-key-id`: the AccessKey ID of the user who has the permission to access the bucket.
- `oss.access-key-secret`: the AccessKey secret of the user who has the permission to access the bucket.

</div>
