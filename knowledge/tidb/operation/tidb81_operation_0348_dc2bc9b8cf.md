# TiDB Cloud import task from Amazon S3

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-sql-shards.md`
- Source Title: `Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud`
- Source Heading Path: `Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform full data migration from MySQL to TiDB Cloud > Step 5. Perform the data import task`
- Source Line Ranges: `174-235`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `data-import`, `s3`, `csv`, `mapping-rules`, `access-validation`, `cross-region`, `wildcards`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0348_dc2bc9b8cf`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-sql-shards.md#step-5-perform-the-data-import-task`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `08d717aa7fa29d45bec0fc67254afa66ff3ca467d45caa3b56140dec36eadb6c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-sql-shards#step-5-perform-the-data-import-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-sql-shards.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the TiDB Cloud console steps and field values to import CSV files from Amazon S3 into a target cluster, including validation behavior and mapping settings for multiple files.
- Retrieval Keywords: TiDB Cloud Import data from Cloud Storage, Amazon S3, Import Data from Amazon S3, Import File Count, Multiple files, Included Schema Files, Data Format CSV, Folder URI, AWS Role ARN, AccessDenied, Troubleshoot Access Denied Errors during Data Import from S3, Advanced Settings, Mapping Settings, Source File URIs and Names, s3://[bucket_name]/[data_source_folder]/[file_name].csv, wildcards ? and *, Edit CSV configuration, Backslash Escape, Separator, Delimiter
- Follow-up Guidance: After the import is completed, the source notes that you can remove TiDB Cloud access to Amazon S3 by deleting the policy that was added.
- Classification Note: This is classified as an operation chunk because it gives step-by-step TiDB Cloud console procedures and import form settings for running a data import task from Amazon S3.

## Official Source Content

### Step 5. Perform the data import task

After configuring the Amazon S3 access, you can perform the data import task in the TiDB Cloud console as follows:

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Select **Import data from Cloud Storage**, and then click **Amazon S3**.

3. On the **Import Data from Amazon S3** page, fill in the following information:

    - **Import File Count**: for TiDB Cloud Serverless, select **Multiple files**. This field is not available in TiDB Cloud Dedicated.
    - **Included Schema Files**: select **No**.
    - **Data Format**: select **CSV**.
    - **Folder URI**: fill in the bucket URI of your source data. You can use the second-level directory corresponding to tables, `s3://dumpling-s3/store/sales/` in this example, so that TiDB Cloud can import and merge the data in all MySQL instances into `store.sales` in one go.
    - **Bucket Access** > **AWS Role ARN**: enter the Role-ARN you obtained.

    If the location of the bucket is different from your cluster, confirm the compliance of cross region.

    TiDB Cloud starts validating whether it can access your data in the specified bucket URI. After validation, TiDB Cloud tries to scan all the files in the data source using the default file naming pattern, and returns a scan summary result on the left side of the next page. If you get the `AccessDenied` error, see [Troubleshoot Access Denied Errors during Data Import from S3](https://docs.pingcap.com/tidb/stable/tidb-cloud/troubleshoot-import-access-denied-error).

4. Click **Connect**.

5. In the **Destination** section, select the target database and table.

    When importing multiple files, you can use **Advanced Settings** > **Mapping Settings** to define a custom mapping rule for each target table and its corresponding CSV file. After that, the data source files will be re-scanned using the provided custom mapping rule.

    When you enter the source file URI and name in **Source File URIs and Names**, make sure it is in the following format `s3://[bucket_name]/[data_source_folder]/[file_name].csv`. For example, `s3://sampledata/ingest/TableName.01.csv`.

    You can also use wildcards to match the source files. For example:

    - `s3://[bucket_name]/[data_source_folder]/my-data?.csv`: all CSV files starting with `my-data` followed by one character (such as `my-data1.csv` and `my-data2.csv`) in that folder will be imported into the same target table.

    - `s3://[bucket_name]/[data_source_folder]/my-data*.csv`: all CSV files in the folder starting with `my-data` will be imported into the same target table.

    Note that only `?` and `*` are supported.

    > **Note:**
    >
    > The URI must contain the data source folder.

6. Edit the CSV configuration if needed.

    You can also click **Edit CSV configuration** to configure Backslash Escape, Separator, and Delimiter for more fine-grained control.

    > **Note:**
    >
    > For the configurations of separator, delimiter, and null, you can use both alphanumeric characters and certain special characters. The supported special characters include `\t`, `\b`, `\n`, `\r`, `\f`, and `\u0001`.

7. Click **Start Import**.

8. When the import progress shows **Completed**, check the imported tables.

After the data is imported, if you want to remove the Amazon S3 access of TiDB Cloud, simply delete the policy that you added.
