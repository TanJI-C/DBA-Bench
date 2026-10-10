# Import Parquet files from Azure Blob Storage or Alibaba Cloud OSS into TiDB Cloud Serverless

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-parquet-files-serverless.md`
- Source Title: `Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless`
- Source Heading Path: `Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Step 4. Import Parquet files to TiDB Cloud Serverless`
- Source Line Ranges: `208-317`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `parquet`, `cloud-storage`, `azure-blob-storage`, `alibaba-cloud-oss`, `destination-mapping`, `file-naming-conventions`, `wildcards`, `import-errors`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0085_43744ac39e`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-parquet-files-serverless.md#step-4-import-parquet-files-to-tidb-cloud-serverless`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2c58233d94d627d2de3d4d71122025e193908ba13c58e4e157ff453fc90032e1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files-serverless#step-4-import-parquet-files-to-tidb-cloud-serverless
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-parquet-files-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to import Parquet files from Azure Blob Storage or Alibaba Cloud OSS into TiDB Cloud Serverless, including Source Files URI formats, Destination Mapping behavior, wildcard patterns, and import error handling.
- Retrieval Keywords: TiDB Cloud Serverless, Import data from Cloud Storage, Azure Blob Storage, Alibaba Cloud OSS, Source Files URI, [azure|https]://[bucket_name]/[data_source_folder]/[file_name].parquet, oss://[bucket_name]/[data_source_folder]/[file_name].parquet, Destination Mapping, Use File naming conventions for automatic mapping, Parquet, Source, Target Database, Target Table, * wildcard, ? wildcard, TableName.01.parquet, my-data?.parquet, my-data*.parquet, Start Import, Completed, unsupported or invalid conversions, Drop the partially imported table, NEST STRUCT, ARRAY, MAP
- Follow-up Guidance: If unsupported or invalid conversions are reported, the content says to drop the partially imported table, check and correct the table schema file, check Parquet data types, regenerate files using supported data types if needed, and then try the import task again.
- Classification Note: The official content is classified as data_pipeline because it describes the cloud import workflow, storage credentials, file-to-table mapping, scanning, and import-task error handling for Parquet data.

## Official Source Content

> **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Click **Import data from Cloud Storage**.

3. On the **Import Data from Cloud Storage** page, provide the following information:

    - **Storage Provider**: select **Azure Blob Storage**.
    - **Source Files URI**:
        - When importing one file, enter the source file URI and name in the following format `[azure|https]://[bucket_name]/[data_source_folder]/[file_name].parquet`. For example, `[azure|https]://sampledata/ingest/TableName.01.parquet`.
        - When importing multiple files, enter the source file URI and name in the following format `[azure|https]://[bucket_name]/[data_source_folder]/`. For example, `[azure|https]://sampledata/ingest/`.
    - **Credential**: you can use a shared access signature (SAS) token to access your bucket. For more information, see [Configure Azure Blob Storage access](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-azure-blob-storage-access)

4. Click **Next**.

5. In the **Destination Mapping** section, specify how source files are mapped to target tables.

    When a directory is specified in **Source Files URI**, the **Use [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) for automatic mapping** option is selected by default.

    > **Note:**
    >
    > When a single file is specified in **Source Files URI**, the **Use [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) for automatic mapping** option is not displayed, and TiDB Cloud automatically populates the **Source** field with the file name. In this case, you only need to select the target database and table for data import.

    - To let TiDB Cloud automatically map all source files that follow the [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) to their corresponding tables, keep this option selected and select **Parquet** as the data format.

    - To manually configure the mapping rules to associate your source Parquet files with the target database and table, unselect this option, and then fill in the following fields:

        - **Source**: enter the file name pattern in the `[file_name].parquet` format. For example: `TableName.01.parquet`. You can also use wildcards to match multiple files. Only `*` and `?` wildcards are supported.

            - `my-data?.parquet`: matches all Parquet files that start with `my-data` followed by a single character, such as `my-data1.parquet` and `my-data2.parquet`.
            - `my-data*.parquet`: matches all Parquet files that start with `my-data`, such as `my-data-2023.parquet` and `my-data-final.parquet`.

        - **Target Database** and **Target Table**: select the target database and table to import the data to.

6. Click **Next**. TiDB Cloud scans the source files accordingly.

7. Review the scan results, check the data files found and corresponding target tables, and then click **Start Import**.

8. When the import progress shows **Completed**, check the imported tables.

</div>

<div label="Alibaba Cloud Object Storage Service (OSS)">

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Click **Import data from Cloud Storage**.

3. On the **Import Data from Cloud Storage** page, provide the following information:

    - **Storage Provider**: select **Alibaba Cloud OSS**.
    - **Source Files URI**:
        - When importing one file, enter the source file URI and name in the following format `oss://[bucket_name]/[data_source_folder]/[file_name].parquet`. For example, `oss://sampledata/ingest/TableName.01.parquet`.
        - When importing multiple files, enter the source file URI and name in the following format `oss://[bucket_name]/[data_source_folder]/`. For example, `oss://sampledata/ingest/`.
    - **Credential**: you can use an AccessKey pair to access your bucket. For more information, see [Configure Alibaba Cloud Object Storage Service (OSS) access](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-alibaba-cloud-object-storage-service-oss-access).

4. Click **Next**.

5. In the **Destination Mapping** section, specify how source files are mapped to target tables.

    When a directory is specified in **Source Files URI**, the **Use [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) for automatic mapping** option is selected by default.

    > **Note:**
    >
    > When a single file is specified in **Source Files URI**, the **Use [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) for automatic mapping** option is not displayed, and TiDB Cloud automatically populates the **Source** field with the file name. In this case, you only need to select the target database and table for data import.

    - To let TiDB Cloud automatically map all source files that follow the [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) to their corresponding tables, keep this option selected and select **Parquet** as the data format.

    - To manually configure the mapping rules to associate your source Parquet files with the target database and table, unselect this option, and then fill in the following fields:

        - **Source**: enter the file name pattern in the `[file_name].parquet` format. For example: `TableName.01.parquet`. You can also use wildcards to match multiple files. Only `*` and `?` wildcards are supported.

            - `my-data?.parquet`: matches all Parquet files that start with `my-data` followed by a single character, such as `my-data1.parquet` and `my-data2.parquet`.
            - `my-data*.parquet`: matches all Parquet files that start with `my-data`, such as `my-data-2023.parquet` and `my-data-final.parquet`.

        - **Target Database** and **Target Table**: select the target database and table to import the data to.

6. Click **Next**. TiDB Cloud scans the source files accordingly.

7. Review the scan results, check the data files found and corresponding target tables, and then click **Start Import**.

8. When the import progress shows **Completed**, check the imported tables.

</div>

When you run an import task, if any unsupported or invalid conversions are detected, TiDB Cloud Serverless terminates the import job automatically and reports an importing error.

If you get an importing error, do the following:

1. Drop the partially imported table.
2. Check the table schema file. If there are any errors, correct the table schema file.
3. Check the data types in the Parquet files.

    If the Parquet files contain any unsupported data types (for example, `NEST STRUCT`, `ARRAY`, or `MAP`), you need to regenerate the Parquet files using [supported data types](#supported-data-types) (for example, `STRING`).

4. Try the import task again.
