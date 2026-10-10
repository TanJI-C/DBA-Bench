# Import Parquet files from S3, GCS, or Azure Blob Storage

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-parquet-files.md`
- Source Title: `Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated`
- Source Heading Path: `Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated > Step 4. Import Parquet files to TiDB Cloud`
- Source Line Ranges: `97-200`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `import`, `parquet`, `cloud-storage`, `s3`, `gcs`, `azure-blob`, `console`, `mapping-settings`, `wildcards`, `bucket-access`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0330_c0ff3779e9`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-parquet-files.md#step-4-import-parquet-files-to-tidb-cloud`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e542d542db88fb008013e32db52470215cae495782ddfdc1bc9a6ede94bdfea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files#step-4-import-parquet-files-to-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-parquet-files.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Cloud Dedicated console steps to import Parquet files from Amazon S3 or Google Cloud Storage, including cloud storage connection fields and multi-file mapping settings.
- Retrieval Keywords: Import data from Cloud Storage, Import Data from Amazon S3, Import Data from Google Cloud Storage, Data > Import, Included Schema Files, Data Format, Parquet, Folder URI, s3://[bucket_name]/[data_source_folder]/, gs://[bucket_name]/[data_source_folder]/, Bucket Access, AWS Role ARN, AWS Access Key, Google Cloud Service Account ID, Advanced Settings, Mapping Settings, Source File URIs and Names, wildcards ? *, Start Import, Completed
- Follow-up Guidance: After clicking Connect, the content says to select the target database and table in Destination, optionally configure Advanced Settings > Mapping Settings for individual file URIs or wildcard patterns, click Start Import, and verify the tables when the progress shows Completed.
- Classification Note: The official content is operational because it gives step-by-step console procedures for importing Parquet files from S3 or GCS into TiDB Cloud Dedicated.

## Official Source Content

## Step 4. Import Parquet files to TiDB Cloud

To import the Parquet files to TiDB Cloud, take the following steps:

<div label="Amazon S3">

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Select **Import data from Cloud Storage**.

3. On the **Import Data from Amazon S3** page, provide the following information:

    - **Included Schema Files**: if the source folder contains the target table schema files (such as `${db_name}-schema-create.sql`), select **Yes**. Otherwise, select **No**.
    - **Data Format**: select **Parquet**.
    - **Folder URI**: enter the source folder URI in the `s3://[bucket_name]/[data_source_folder]/` format. The path must end with a `/`. For example, `s3://sampledata/ingest/`.
    - **Bucket Access**: you can use either an AWS IAM role ARN or an AWS access key to access your bucket.
        - **AWS Role ARN** (recommended): enter the AWS IAM role ARN value. If you don't have an IAM role for the bucket yet, you can create it using the provided AWS CloudFormation template by clicking **Click here to create new one with AWS CloudFormation** and following the instructions on the screen. Alternatively, you can manually create an IAM role ARN for the bucket.
        - **AWS Access Key**: enter the AWS access key ID and AWS secret access key.
        - For detailed instructions on both methods, see [Configure Amazon S3 access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-amazon-s3-access).

4. Click **Connect**.

5. In the **Destination** section, select the target database and table.

    When importing multiple files, you can use **Advanced Settings** > **Mapping Settings** to customize the mapping of individual target tables to their corresponding Parquet files. For each target database and table:

    - **Target Database**: select the corresponding database name from the list.
    - **Target Table**: select the corresponding table name from the list.
    - **Source File URIs and Names**: enter the full URI of the source file, including the folder and file name, making sure it is in the `s3://[bucket_name]/[data_source_folder]/[file_name].parquet` format. For example, `s3://sampledata/ingest/TableName.01.parquet`. You can also use wildcards (`?` and `*`) to match multiple files. For example:
        - `s3://[bucket_name]/[data_source_folder]/my-data1.parquet`: a single Parquet file named `my-data1.parquet` in `[data_source_folder]` will be imported into the target table.
        - `s3://[bucket_name]/[data_source_folder]/my-data?.parquet`: all Parquet files starting with `my-data` followed by one character (such as `my-data1.parquet` and `my-data2.parquet`) in `[data_source_folder]` will be imported into the same target table.
        - `s3://[bucket_name]/[data_source_folder]/my-data*.parquet`: all Parquet files starting with `my-data` (such as `my-data10.parquet` and `my-data100.parquet`) in `[data_source_folder]` will be imported into the same target table.

6. Click **Start Import**.

7. When the import progress shows **Completed**, check the imported tables.

</div>

<div label="Google Cloud">

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Select **Import data from Cloud Storage**.

3. On the **Import Data from Google Cloud Storage** page, provide the following information for the source Parquet files:

    - **Included Schema Files**: if the source folder contains the target table schema files (such as `${db_name}-schema-create.sql`), select **Yes**. Otherwise, select **No**.
    - **Data Format**: select **Parquet**.
    - **Folder URI**: enter the source folder URI in the `gs://[bucket_name]/[data_source_folder]/` format. The path must end with a `/`. For example, `gs://sampledata/ingest/`.
    - **Google Cloud Service Account ID**: TiDB Cloud provides a unique Service Account ID on this page (such as `example-service-account@your-project.iam.gserviceaccount.com`). You must grant this Service Account ID the necessary IAM permissions (such as "Storage Object Viewer") on your GCS bucket within your Google Cloud project. For more information, see [Configure GCS access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-gcs-access).

4. Click **Connect**.

5. In the **Destination** section, select the target database and table.

    When importing multiple files, you can use **Advanced Settings** > **Mapping Settings** to customize the mapping of individual target tables to their corresponding Parquet files. For each target database and table:

    - **Target Database**: select the corresponding database name from the list.
    - **Target Table**: select the corresponding table name from the list.
    - **Source File URIs and Names**: enter the full URI of the source file, including the folder and file name, making sure it is in the `gs://[bucket_name]/[data_source_folder]/[file_name].parquet` format. For example, `gs://sampledata/ingest/TableName.01.parquet`. You can also use wildcards (`?` and `*`) to match multiple files. For example:
        - `gs://[bucket_name]/[data_source_folder]/my-data1.parquet`: a single Parquet file named `my-data1.parquet` in `[data_source_folder]` will be imported into the target table.
        - `gs://[bucket_name]/[data_source_folder]/my-data?.parquet`: all Parquet files starting with `my-data` followed by one character (such as `my-data1.parquet` and `my-data2.parquet`) in `[data_source_folder]` will be imported into the same target table.
        - `gs://[bucket_name]/[data_source_folder]/my-data*.parquet`: all Parquet files starting with `my-data` (such as `my-data10.parquet` and `my-data100.parquet`) in `[data_source_folder]` will be imported into the same target table.

6. Click **Start Import**.

7. When the import progress shows **Completed**, check the imported tables.

</div>

<div label="Azure Blob Storage">

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Select **Import data from Cloud Storage**.

3. On the **Import Data from Azure Blob Storage** page, provide the following information:
