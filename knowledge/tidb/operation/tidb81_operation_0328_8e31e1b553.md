# Import CSV files from Azure Blob Storage or Alibaba Cloud OSS

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-csv-files-serverless.md`
- Source Title: `Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless`
- Source Heading Path: `Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Step 4. Import CSV files to TiDB Cloud Serverless`
- Source Line Ranges: `204-306`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `sql`
- Topic Tags: `csv`, `import`, `cloud-storage`, `azure-blob-storage`, `alibaba-cloud-oss`, `destination-mapping`, `file-naming-conventions`, `wildcards`, `validation`, `retry`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0328_8e31e1b553`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-csv-files-serverless.md#step-4-import-csv-files-to-tidb-cloud-serverless`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b03d34d8320a4d083ba608491dc3c8604f129bb9526fb9e9d9b07471c5fc72bd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files-serverless#step-4-import-csv-files-to-tidb-cloud-serverless
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-csv-files-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Cloud Serverless steps and URI formats for importing CSV files from Azure Blob Storage or Alibaba Cloud OSS, including destination mapping behavior for single files, directories, and wildcard patterns.
- Retrieval Keywords: Import data from Cloud Storage, Azure Blob Storage, Alibaba Cloud OSS, Source Files URI, [azure|https]://[bucket_name]/[data_source_folder]/[file_name].csv, [azure|https]://[bucket_name]/[data_source_folder]/, oss://[bucket_name]/[data_source_folder]/[file_name].csv, oss://[bucket_name]/[data_source_folder]/, Credential, shared access signature (SAS) token, AccessKey pair, Destination Mapping, Use File naming conventions for automatic mapping, Source, Target Database, Target Table, CSV, * and ? wildcards, TableName.01.csv, my-data?.csv, my-data*.csv, Start Import, Completed, unsupported or invalid conversions, importing error, Drop the partially imported table, table schema file
- Follow-up Guidance: If TiDB Cloud Serverless reports an importing error because unsupported or invalid conversions are detected, the content says to drop the partially imported table, check and correct the table schema file if needed, check the data types in the CSV files, and try the import task again.
- Classification Note: This is classified as an operation chunk because the content provides the import procedure, source URI formats, mapping options, scan and start steps, and the documented retry guidance after import errors.

## Official Source Content

2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Click **Import data from Cloud Storage**.

3. On the **Import Data from Cloud Storage** page, provide the following information:

    - **Storage Provider**: select **Azure Blob Storage**.
    - **Source Files URI**:
        - When importing one file, enter the source file URI and name in the following format `[azure|https]://[bucket_name]/[data_source_folder]/[file_name].csv`. For example, `[azure|https]://sampledata/ingest/TableName.01.csv`.
        - When importing multiple files, enter the source file URI and name in the following format `[azure|https]://[bucket_name]/[data_source_folder]/`. For example, `[azure|https]://sampledata/ingest/`.
    - **Credential**: you can use a shared access signature (SAS) token to access your bucket. For more information, see [Configure Azure Blob Storage access](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-azure-blob-storage-access)

4. Click **Next**.

5. In the **Destination Mapping** section, specify how source files are mapped to target tables.

    When a directory is specified in **Source Files URI**, the **Use [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) for automatic mapping** option is selected by default.

    > **Note:**
    >
    > When a single file is specified in **Source Files URI**, the **Use [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) for automatic mapping** option is not displayed, and TiDB Cloud automatically populates the **Source** field with the file name. In this case, you only need to select the target database and table for data import.

    - To let TiDB Cloud automatically map all source files that follow the [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) to their corresponding tables, keep this option selected and select **CSV** as the data format.

    - To manually configure the mapping rules to associate your source CSV files with the target database and table, unselect this option, and then fill in the following fields:

        - **Source**: enter the file name pattern in the `[file_name].csv` format. For example: `TableName.01.csv`. You can also use wildcards to match multiple files. Only `*` and `?` wildcards are supported.

            - `my-data?.csv`: matches all CSV files that start with `my-data` followed by a single character, such as `my-data1.csv` and `my-data2.csv`.
            - `my-data*.csv`: matches all CSV files that start with `my-data`, such as `my-data-2023.csv` and `my-data-final.csv`.

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
        - When importing one file, enter the source file URI and name in the following format `oss://[bucket_name]/[data_source_folder]/[file_name].csv`. For example, `oss://sampledata/ingest/TableName.01.csv`.
        - When importing multiple files, enter the source file URI and name in the following format `oss://[bucket_name]/[data_source_folder]/`. For example, `oss://sampledata/ingest/`.
    - **Credential**: you can use an AccessKey pair to access your bucket. For more information, see [Configure Alibaba Cloud Object Storage Service (OSS) access](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-alibaba-cloud-object-storage-service-oss-access).

4. Click **Next**.

5. In the **Destination Mapping** section, specify how source files are mapped to target tables.

    When a directory is specified in **Source Files URI**, the **Use [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) for automatic mapping** option is selected by default.

    > **Note:**
    >
    > When a single file is specified in **Source Files URI**, the **Use [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) for automatic mapping** option is not displayed, and TiDB Cloud automatically populates the **Source** field with the file name. In this case, you only need to select the target database and table for data import.

    - To let TiDB Cloud automatically map all source files that follow the [File naming conventions](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import) to their corresponding tables, keep this option selected and select **CSV** as the data format.

    - To manually configure the mapping rules to associate your source CSV files with the target database and table, unselect this option, and then fill in the following fields:

        - **Source**: enter the file name pattern in the `[file_name].csv` format. For example: `TableName.01.csv`. You can also use wildcards to match multiple files. Only `*` and `?` wildcards are supported.

            - `my-data?.csv`: matches all CSV files that start with `my-data` followed by a single character, such as `my-data1.csv` and `my-data2.csv`.
            - `my-data*.csv`: matches all CSV files that start with `my-data`, such as `my-data-2023.csv` and `my-data-final.csv`.

        - **Target Database** and **Target Table**: select the target database and table to import the data to.

6. Click **Next**. TiDB Cloud scans the source files accordingly.

7. Review the scan results, check the data files found and corresponding target tables, and then click **Start Import**.

8. When the import progress shows **Completed**, check the imported tables.

</div>

When you run an import task, if any unsupported or invalid conversions are detected, TiDB Cloud Serverless terminates the import job automatically and reports an importing error.

If you get an importing error, do the following:

1. Drop the partially imported table.
2. Check the table schema file. If there are any errors, correct the table schema file.
3. Check the data types in the CSV files.
4. Try the import task again.
