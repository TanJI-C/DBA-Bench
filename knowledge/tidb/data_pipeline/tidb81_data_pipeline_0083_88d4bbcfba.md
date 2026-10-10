# Import CSV files from cloud storage and handle import errors

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-csv-files.md`
- Source Title: `Import CSV Files from Cloud Storage into TiDB Cloud Dedicated`
- Source Heading Path: `Import CSV Files from Cloud Storage into TiDB Cloud Dedicated > Step 4. Import CSV files to TiDB Cloud | Import CSV Files from Cloud Storage into TiDB Cloud Dedicated > Troubleshooting`
- Source Line Ranges: `91-234`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `sql`
- Topic Tags: `csv`, `import`, `cloud-storage`, `s3`, `gcs`, `azure-blob`, `table-mapping`, `wildcards`, `schema-files`, `access-credentials`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0083_88d4bbcfba`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-csv-files.md#step-4-import-csv-files-to-tidb-cloud`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd783d5bbe8ca2962bf23cde0366a29226002c632291858b2e78279b70cbfb8c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files#step-4-import-csv-files-to-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-csv-files.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to import CSV files from Amazon S3, Google Cloud Storage, or Azure Blob Storage into TiDB Cloud Dedicated, including file mapping, CSV options, access credentials, and import error handling.
- Retrieval Keywords: Import data from Cloud Storage, Import Data from Amazon S3, Import Data from Google Cloud Storage, Import Data from Azure Blob Storage, Included Schema Files, Data Format CSV, Edit CSV Configuration, Folder URI, s3://[bucket_name]/[data_source_folder]/, gs://[bucket_name]/[data_source_folder]/, https://[account_name].blob.core.windows.net/[container_name]/[data_source_folder]/, AWS Role ARN, AWS Access Key, Google Cloud Service Account ID, SAS Token, Advanced Settings, Mapping Settings, Source File URIs and Names, wildcards ? and *, Start Import, Completed, Status field, unsupported or invalid conversions, Drop the partially imported table, check the table schema file, check the data types in the CSV files
- Follow-up Guidance: If an importing error is reported because unsupported or invalid conversions are detected, the content says to drop the partially imported table, check and correct the table schema file if needed, check the data types in the CSV files, and try the import task again.
- Classification Note: The official content is classified as a cloud data pipeline topic because it describes TiDB Cloud Dedicated CSV import from cloud storage providers and includes mapping settings and troubleshooting for import jobs.

## Official Source Content

## Step 4. Import CSV files to TiDB Cloud

To import the CSV files to TiDB Cloud, take the following steps:

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
    - **Data Format**: select **CSV**.
    - **Edit CSV Configuration**: if necessary, configure the options according to your CSV files. You can set the separator and delimiter characters, specify whether to use backslashes for escaped characters, and specify whether your files contain a header row.
    - **Folder URI**: enter the source folder URI in the `s3://[bucket_name]/[data_source_folder]/` format. The path must end with a `/`. For example, `s3://mybucket/myfolder/`.
    - **Bucket Access**: you can use either an AWS IAM role ARN or an AWS access key to access your bucket.
        - **AWS Role ARN** (recommended): enter the AWS IAM role ARN value. If you don't have an IAM role for the bucket yet, you can create it using the provided AWS CloudFormation template by clicking **Click here to create new one with AWS CloudFormation** and following the instructions on the screen. Alternatively, you can manually create an IAM role ARN for the bucket.
        - **AWS Access Key**: enter the AWS access key ID and AWS secret access key.
        - For detailed instructions on both methods, see [Configure Amazon S3 access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-amazon-s3-access).

4. Click **Connect**.

5. In the **Destination** section, select the target database and table.

    When importing multiple files, you can use **Advanced Settings** > **Mapping Settings** to customize the mapping of individual target tables to their corresponding CSV files. For each target database and table:

    - **Target Database**: select the corresponding database name from the list.
    - **Target Table**: select the corresponding table name from the list.
    - **Source File URIs and Names**: enter the full URI of the source file, including the folder and file name, making sure it is in the `s3://[bucket_name]/[data_source_folder]/[file_name].csv` format. You can also use wildcards (`?` and `*`) to match multiple files. For example:
        - `s3://mybucket/myfolder/my-data1.csv`: a single CSV file named `my-data1.csv` in `myfolder` will be imported into the target table.
        - `s3://mybucket/myfolder/my-data?.csv`: all CSV files starting with `my-data` followed by one character (such as `my-data1.csv` and `my-data2.csv`) in `myfolder` will be imported into the same target table.
        - `s3://mybucket/myfolder/my-data*.csv`: all CSV files starting with `my-data` (such as `my-data10.csv` and `my-data100.csv`) in `myfolder` will be imported into the same target table.

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

3. On the **Import Data from Google Cloud Storage** page, provide the following information for the source CSV files:

    - **Included Schema Files**: if the source folder contains the target table schema files (such as `${db_name}-schema-create.sql`), select **Yes**. Otherwise, select **No**.
    - **Data Format**: select **CSV**.
    - **Edit CSV Configuration**: if necessary, configure the options according to your CSV files. You can set the separator and delimiter characters, specify whether to use backslashes for escaped characters, and specify whether your files contain a header row.
    - **Folder URI**: enter the source folder URI in the `gs://[bucket_name]/[data_source_folder]/` format. The path must end with a `/`. For example, `gs://sampledata/ingest/`.
    - **Google Cloud Service Account ID**: TiDB Cloud provides a unique Service Account ID on this page (such as `example-service-account@your-project.iam.gserviceaccount.com`). You must grant this Service Account ID the necessary IAM permissions (such as "Storage Object Viewer") on your GCS bucket within your Google Cloud project. For more information, see [Configure GCS access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-gcs-access).

4. Click **Connect**.

5. In the **Destination** section, select the target database and table.

    When importing multiple files, you can use **Advanced Settings** > **Mapping Settings** to customize the mapping of individual target tables to their corresponding CSV files. For each target database and table:

    - **Target Database**: select the corresponding database name from the list.
    - **Target Table**: select the corresponding table name from the list.
    - **Source File URIs and Names**: enter the full URI of the source file, including the folder and file name, making sure it is in the `gs://[bucket_name]/[data_source_folder]/[file_name].csv` format. You can also use wildcards (`?` and `*`) to match multiple files. For example:
        - `gs://mybucket/myfolder/my-data1.csv`: a single CSV file named `my-data1.csv` in `myfolder` will be imported into the target table.
        - `gs://mybucket/myfolder/my-data?.csv`: all CSV files starting with `my-data` followed by one character (such as `my-data1.csv` and `my-data2.csv`) in `myfolder` will be imported into the same target table.
        - `gs://mybucket/myfolder/my-data*.csv`: all CSV files starting with `my-data` (such as `my-data10.csv` and `my-data100.csv`) in `myfolder` will be imported into the same target table.

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
    - **Included Schema Files**: if the source folder contains the target table schema files (such as `${db_name}-schema-create.sql`), select **Yes**. Otherwise, select **No**.
    - **Data Format**: select **CSV**.
    - **Edit CSV Configuration**: if necessary, configure the options according to your CSV files. You can set the separator and delimiter characters, specify whether to use backslashes for escaped characters, and specify whether your files contain a header row.
    - **Folder URI**: enter the Azure Blob Storage URI where your source files are located using the format `https://[account_name].blob.core.windows.net/[container_name]/[data_source_folder]/`. The path must end with a `/`. For example, `https://myaccount.blob.core.windows.net/mycontainer/myfolder/`.
    - **SAS Token**: enter an account SAS token to allow TiDB Cloud to access the source files in your Azure Blob Storage container. If you don't have one yet, you can create it using the provided Azure ARM template by clicking **Click here to create a new one with Azure ARM template** and following the instructions on the screen. Alternatively, you can manually create an account SAS token. For more information, see [Configure Azure Blob Storage access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-azure-blob-storage-access).

4. Click **Connect**.

5. In the **Destination** section, select the target database and table.

    When importing multiple files, you can use **Advanced Settings** > **Mapping Settings** to customize the mapping of individual target tables to their corresponding CSV files. For each target database and table:

    - **Target Database**: select the corresponding database name from the list.
    - **Target Table**: select the corresponding table name from the list.
    - **Source File URIs and Names**: enter the full URI of the source file, including the folder and file name, making sure it is in the `https://[account_name].blob.core.windows.net/[container_name]/[data_source_folder]/[file_name].csv` format. You can also use wildcards (`?` and `*`) to match multiple files. For example:
        - `https://myaccount.blob.core.windows.net/mycontainer/myfolder/my-data1.csv`: a single CSV file named `my-data1.csv` in `myfolder` will be imported into the target table.
        - `https://myaccount.blob.core.windows.net/mycontainer/myfolder/my-data?.csv`: all CSV files starting with `my-data` followed by one character (such as `my-data1.csv` and `my-data2.csv`) in `myfolder` will be imported into the same target table.
        - `https://myaccount.blob.core.windows.net/mycontainer/myfolder/my-data*.csv`: all CSV files starting with `my-data` (such as `my-data10.csv` and `my-data100.csv`) in `myfolder` will be imported into the same target table.

6. Click **Start Import**.

7. When the import progress shows **Completed**, check the imported tables.

</div>

When you run an import task, if any unsupported or invalid conversions are detected, TiDB Cloud terminates the import job automatically and reports an importing error. You can view details in the **Status** field.

If you get an importing error, do the following:

1. Drop the partially imported table.
2. Check the table schema file. If there are any errors, correct the table schema file.
3. Check the data types in the CSV files.
4. Try the import task again.
## Troubleshooting
