# Complete Azure import flow and handle import errors

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-parquet-files.md`
- Source Title: `Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated`
- Source Heading Path: `Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated > Step 4. Import Parquet files to TiDB Cloud`
- Source Line Ranges: `201-238`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `import`, `parquet`, `azure-blob`, `sas-token`, `mapping-settings`, `wildcards`, `import-errors`, `unsupported-types`, `schema-validation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0331_6064d561ac`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-parquet-files.md#step-4-import-parquet-files-to-tidb-cloud`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `55af7dff92084db8720c70867d1d7d216152591268a7d41a3432f37001f7b069`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files#step-4-import-parquet-files-to-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-parquet-files.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Azure Blob Storage import fields and mapping options for Parquet files in TiDB Cloud Dedicated, or when handling import errors caused by invalid conversions or unsupported Parquet data types.
- Retrieval Keywords: Import Data from Azure Blob Storage, Azure Blob Storage, SAS Token, Folder URI, https://[account_name].blob.core.windows.net/[container_name]/[data_source_folder]/, Advanced Settings, Mapping Settings, Source File URIs and Names, wildcards ? *, Status field, importing error, unsupported or invalid conversions, unsupported data types, NEST STRUCT, ARRAY, MAP, supported data types, drop the partially imported table, Start Import, Completed
- Follow-up Guidance: If an importing error occurs, the content says to drop the partially imported table, check and correct the table schema file, check Parquet data types, regenerate files that contain unsupported types such as NEST STRUCT, ARRAY, or MAP using supported data types, and then try the import task again.
- Classification Note: The official content is classified as an operation because it covers both the Azure import procedure in the TiDB Cloud console and the documented remediation flow for import job errors.

## Official Source Content

- **Included Schema Files**: if the source folder contains the target table schema files (such as `${db_name}-schema-create.sql`), select **Yes**. Otherwise, select **No**.
    - **Data Format**: select **Parquet**.
    - **Folder URI**: enter the Azure Blob Storage URI where your source files are located using the format `https://[account_name].blob.core.windows.net/[container_name]/[data_source_folder]/`. The path must end with a `/`. For example, `https://myaccount.blob.core.windows.net/mycontainer/data-ingestion/`.
    - **SAS Token**: enter an account SAS token to allow TiDB Cloud to access the source files in your Azure Blob Storage container. If you don't have one yet, you can create it using the provided Azure ARM template by clicking **Click here to create a new one with Azure ARM template** and following the instructions on the screen. Alternatively, you can manually create an account SAS token. For more information, see [Configure Azure Blob Storage access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-azure-blob-storage-access).

4. Click **Connect**.

5. In the **Destination** section, select the target database and table.

    When importing multiple files, you can use **Advanced Settings** > **Mapping Settings** to customize the mapping of individual target tables to their corresponding Parquet files. For each target database and table:

    - **Target Database**: select the corresponding database name from the list.
    - **Target Table**: select the corresponding table name from the list.
    - **Source File URIs and Names**: enter the full URI of the source file, including the folder and file name, making sure it is in the `https://[account_name].blob.core.windows.net/[container_name]/[data_source_folder]/[file_name].parquet` format. For example, `https://myaccount.blob.core.windows.net/mycontainer/data-ingestion/TableName.01.parquet`. You can also use wildcards (`?` and `*`) to match multiple files. For example:
        - `https://[account_name].blob.core.windows.net/[container_name]/[data_source_folder]/my-data1.parquet`: a single Parquet file named `my-data1.parquet` in `[data_source_folder]` will be imported into the target table.
        - `https://[account_name].blob.core.windows.net/[container_name]/[data_source_folder]/my-data?.parquet`: all Parquet files starting with `my-data` followed by one character (such as `my-data1.parquet` and `my-data2.parquet`) in `[data_source_folder]` will be imported into the same target table.
        - `https://[account_name].blob.core.windows.net/[container_name]/[data_source_folder]/my-data*.parquet`: all Parquet files starting with `my-data` (such as `my-data10.parquet` and `my-data100.parquet`) in `[data_source_folder]` will be imported into the same target table.

6. Click **Start Import**.

7. When the import progress shows **Completed**, check the imported tables.

</div>

When you run an import task, if any unsupported or invalid conversions are detected, TiDB Cloud terminates the import job automatically and reports an importing error. You can view details in the **Status** field.

If you get an importing error, do the following:

1. Drop the partially imported table.
2. Check the table schema file. If there are any errors, correct the table schema file.
3. Check the data types in the Parquet files.

    If the Parquet files contain any unsupported data types (for example, `NEST STRUCT`, `ARRAY`, or `MAP`), you need to regenerate the Parquet files using [supported data types](#supported-data-types) (for example, `STRING`).

4. Try the import task again.
