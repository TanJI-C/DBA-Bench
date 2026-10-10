# TiDB Cloud Serverless local CSV import overview, limits, and procedure

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-import-local-files.md`
- Source Title: `Import Local Files to TiDB Cloud Serverless`
- Source Heading Path: `Import Local Files to TiDB Cloud Serverless | Import Local Files to TiDB Cloud Serverless > Limitations | Import Local Files to TiDB Cloud Serverless > Import local files`
- Source Line Ranges: `5-83`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `csv`, `import`, `serverless`, `local-files`, `limitations`, `table-definition`, `column-mapping`, `primary-key`, `csv-configuration`, `task-monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0106_2b5cb29c86`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-import-local-files.md#import-local-files-to-tidb-cloud-serverless`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `86a93fe6bc6a499e3f8556f65b5d8543476bc4cdf09d6cf4b8fc145d4a4ef1ad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-import-local-files#import-local-files-to-tidb-cloud-serverless
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-import-local-files.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud Serverless local CSV import workflow, limits, table definition behavior, CSV configuration options, or import task monitoring details.
- Retrieval Keywords: Import Local Files to TiDB Cloud Serverless, TiDB Cloud Serverless, local CSV file, one CSV file for one task, 250 MiB, existing empty table, new table, Define Table, Table Definition, Use first row as column name, primary key, composite primary key, clustered index, Edit CSV configuration, Backslash Escape, Separator, Delimiter, Start Import, Import Task Detail, Explore your data by SQL Editor
- Follow-up Guidance: The source also points to the FAQ for importing files larger than 250 MiB and to CSV configuration and SQL Editor documentation.
- Classification Note: This chunk is classified as data_pipeline because the official content describes the end-to-end process and constraints for importing local CSV data into a TiDB Cloud Serverless cluster.

## Official Source Content

# Import Local Files to TiDB Cloud Serverless

You can import local files to TiDB Cloud Serverless directly. It only takes a few clicks to complete the task configuration, and then your local CSV data will be quickly imported to your TiDB cluster. Using this method, you do not need to provide the cloud storage and credentials. The whole importing process is quick and smooth.

Currently, this method supports importing one CSV file for one task into either an existing empty table or a new table.
## Limitations

- Currently, TiDB Cloud only supports importing a local file in CSV format within 250 MiB for one task.
- Importing local files is supported only for TiDB Cloud Serverless clusters, not for TiDB Cloud Dedicated clusters.
- You cannot run more than one import task at the same time.
## Import local files

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. On the **Import** page, you can directly drag and drop your local file to the upload area, or click **Upload a local file** to select and upload the target local file. Note that you can upload only one CSV file of less than 250 MiB for one task. If your local file is larger than 250 MiB, see [How to import a local file larger than 250 MiB?](#how-to-import-a-local-file-larger-than-250-mib).

3. In the **Destination** section, select the target database and the target table, or enter a name directly to create a new database or a new table. The name must only contain characters in Unicode BMP (Basic Multilingual Plane), excluding the null character `\u0000` and whitespace characters, and can be up to 64 characters in length. Click **Define Table**, the **Table Definition** section is displayed.

4. Check the table.

    You can see a list of configurable table columns. Each line shows the table column name inferred by TiDB Cloud, the table column type inferred, and the previewed data from the CSV file.

    - If you import data into an existing table in TiDB Cloud, the column list is extracted from the table definition, and the previewed data is mapped to the corresponding columns by column names.

    - If you want to create a new table, the column list is extracted from the CSV file, and the column type is inferred by TiDB Cloud. For example, if the previewed data is all integers, the inferred column type will be integer.

5. Configure the column names and data types.

    If the first row in the CSV file records the column names, make sure that **Use first row as column name** is selected, which is selected by default.

    If the CSV file does not have a row for the column names, do not select **Use first row as column name**. In this case:

    - If the target table already exists, the columns in the CSV file will be imported into the target table in order. Extra columns will be truncated and missing columns will be filled with default values.

    - If you need TiDB Cloud to create the target table, input the name for each column. The column name must meet the following requirements:

        * The name must be composed of characters in Unicode BMP, excluding the null character `\u0000` and whitespace characters.
        * The length of the name must be less than 65 characters.

        You can also change the data type if needed.

    > **Note:**
    >
    > When you import a CSV file into an existing table in TiDB Cloud and the target table has more columns than the source file, the extra columns are handled differently depending on the situation:
    > - If the extra columns are not the primary keys or the unique keys, no error will be reported. Instead, these extra columns will be populated with their [default values](https://docs.pingcap.com/tidb/stable/data-type-default-values).
    > - If the extra columns are the primary keys or the unique keys and do not have the `auto_increment` or `auto_random` attribute, an error will be reported. In that case, it is recommended that you choose one of the following strategies:
    >   - Provide a source file that includes these primary key or unique key columns.
    >   - Modify the target table's primary key and unique key columns to match the existing columns in the source file.
    >   - Set the attributes of the primary key or the unique key columns to `auto_increment` or `auto_random`.

6. For a new target table, you can set the primary key. You can select a column as the primary key, or select multiple columns to create a composite primary key. The composite primary key will be formed in the order in which you select the column names.

    > **Note:**
    >
    > The primary key of the table is a clustered index and cannot be dropped after creation.

7. Edit the CSV configuration if needed.

   You can also click **Edit CSV configuration** to configure Backslash Escape, Separator, and Delimiter for more fine-grained control. For more information about the CSV configuration, see [CSV Configurations for Importing Data](https://docs.pingcap.com/tidb/stable/tidb-cloud/csv-config-for-import-data).

8. Click **Start Import**.

    You can view the import progress on the **Import Task Detail** page. If there are warnings or failed tasks, you can check to view the details and solve them.

9. After the import task is completed, you can click **Explore your data by SQL Editor** to query your imported data. For more information about how to use SQL Editor, see [Explore your data with AI-assisted SQL Editor](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query).

10. On the **Import** page, you can click **...** > **View** in the **Action** column to check the import task detail.
