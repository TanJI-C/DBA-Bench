# Import Parquet files from cloud storage into TiDB Cloud Serverless

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-parquet-files-serverless.md`
- Source Title: `Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless`
- Source Heading Path: `Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Step 4. Import Parquet files to TiDB Cloud Serverless`
- Source Line Ranges: `93-207`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `import`, `parquet`, `cloud-storage`, `s3`, `gcs`, `azure-blob`, `destination-mapping`, `file-naming-conventions`, `credentials`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0329_fd31181880`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-parquet-files-serverless.md#step-4-import-parquet-files-to-tidb-cloud-serverless`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b42eddf6687de957eb142d5e3e6fe965eb4585b3f1e4b336c6cd99f050e60632`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files-serverless#step-4-import-parquet-files-to-tidb-cloud-serverless
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-parquet-files-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud Serverless console steps to import Parquet files from cloud storage, including source URI formats, credentials, destination mapping, and scan review.
- Retrieval Keywords: Import data from Cloud Storage, Import Data from Cloud Storage, Import Data from Google Cloud Storage, TiDB Cloud Serverless, Parquet, Amazon S3, Google Cloud Storage, Source Files URI, s3://[bucket_name]/[data_source_folder]/[file_name].parquet, [gcs|gs]://[bucket_name]/[data_source_folder]/[file_name].parquet, AWS Role ARN, AWS Access Key, GCS IAM Role Service Account key, Destination Mapping, Use File naming conventions for automatic mapping, Source, Target Database, Target Table, * wildcard, ? wildcard, Start Import, Completed
- Follow-up Guidance: After clicking Next, TiDB Cloud scans the source files, then you review the scan results, check the data files found and corresponding target tables, and click Start Import.
- Classification Note: This is an operation chunk because it provides step-by-step UI procedures for importing Parquet files into TiDB Cloud Serverless from cloud storage providers.

## Official Source Content

## Step 4. Import Parquet files to TiDB Cloud Serverless

To import the Parquet files to TiDB Cloud Serverless, take the following steps:

<div label="Amazon S3">

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Click **Import data from Cloud Storage**.

3. On the **Import Data from Cloud Storage** page, provide the following information:

    - **Storage Provider**: select **Amazon S3**.
    - **Source Files URI**:
        - When importing one file, enter the source file URI and name in the following format `s3://[bucket_name]/[data_source_folder]/[file_name].parquet`. For example, `s3://sampledata/ingest/TableName.01.parquet`.
        - When importing multiple files, enter the source file URI and name in the following format `s3://[bucket_name]/[data_source_folder]/`. For example, `s3://sampledata/ingest/`.
    - **Credential**: you can use either an AWS Role ARN or an AWS access key to access your bucket. For more information, see [Configure Amazon S3 access](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-amazon-s3-access).
        - **AWS Role ARN**: enter the AWS Role ARN value.
        - **AWS Access Key**: enter the AWS access key ID and AWS secret access key.

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

<div label="Google Cloud">

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Click **Import data from Cloud Storage**.

3. On the **Import Data from Google Cloud Storage** page, provide the following information:

    - **Storage Provider**: select **Google Cloud Storage**.
    - **Source Files URI**:
        - When importing one file, enter the source file URI and name in the following format `[gcs|gs]://[bucket_name]/[data_source_folder]/[file_name].parquet`. For example, `[gcs|gs]://sampledata/ingest/TableName.01.parquet`.
        - When importing multiple files, enter the source file URI and name in the following format `[gcs|gs]://[bucket_name]/[data_source_folder]/`. For example, `[gcs|gs]://sampledata/ingest/`.
    - **Credential**: you can use a GCS IAM Role Service Account key to access your bucket. For more information, see [Configure GCS access](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-gcs-access).

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

<div label="Azure Blob Storage">

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.
