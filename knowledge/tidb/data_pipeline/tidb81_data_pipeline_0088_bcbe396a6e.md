# Import sample data into TiDB Cloud Dedicated from cloud storage and verify with SQL queries

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-sample-data.md`
- Source Title: `Import Sample Data into TiDB Cloud Dedicated`
- Source Heading Path: `Import Sample Data into TiDB Cloud Dedicated`
- Source Line Ranges: `5-134`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `sample-data`, `import`, `cloud-storage`, `amazon-s3`, `gcs`, `azure-blob-storage`, `ui`, `verification`, `sql-queries`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0088_bcbe396a6e`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-sample-data.md#import-sample-data-into-tidb-cloud-dedicated`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6b340d0ed28ec05e64669a063acd32e1619fd09b88ed8ca2c7ef54ea55fc5cee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-sample-data#import-sample-data-into-tidb-cloud-dedicated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-sample-data.md

## Retrieval Guidance

- Use When: Use this when the user needs the TiDB Cloud Dedicated UI steps to import the Capital Bikeshare sample SQL data from Amazon S3, GCS, or Azure Blob Storage and verify the import with example SQL queries.
- Retrieval Keywords: Import Sample Data into TiDB Cloud Dedicated, Import data from Cloud Storage, Import Data from Amazon S3, Import Data from GCS, Import Data from Azure Blob Storage, Included Schema Files, Data Format SQL, s3://tidbcloud-sample-data/data-ingestion/, arn:aws:iam::801626783489:role/import-sample-access, gs://tidbcloud-samples-us-west1/, https://tcidmsampledata.blob.core.windows.net/sql/, SAS Token, Connect > Start Import, Completed, use bikeshare;, select * from `trips` where start_station_name='12th & U St NW' limit 10;, select * from `trips` where rideable_type="electric_bike" limit 10;
- Follow-up Guidance: After the import progress shows Completed, the content provides verification queries using the bikeshare database and the trips table.
- Classification Note: This is classified as data_pipeline for the cloud component because the content describes importing sample data into a TiDB Cloud Dedicated cluster from cloud storage through the UI and validating it with SQL.

## Official Source Content

# Import Sample Data into TiDB Cloud Dedicated

This document describes how to import the sample data into TiDB Cloud Dedicated via the UI. The sample data used is the system data from Capital Bikeshare, released under the Capital Bikeshare Data License Agreement. Before importing the sample data, you need to have one TiDB cluster.

<div label="Amazon S3">

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Select **Import data from Cloud Storage**.

3. On the **Import Data from Amazon S3** page, configure the following source data information:

    - **Included Schema Files**: for the sample data, select **Yes**.
    - **Data Format**: select **SQL**. 
    - **Folder URI** or **File URI**: enter the sample data URI `s3://tidbcloud-sample-data/data-ingestion/`.
    - **Bucket Access**: for the sample data, you can only use a Role ARN to access its bucket. For your own data, you can use either an AWS access key or a Role ARN to access your bucket.
        - **AWS Role ARN**: enter `arn:aws:iam::801626783489:role/import-sample-access`.
        - **AWS Access Key**: skip this option for the sample data.

4. Click **Connect** > **Start Import**.

</div>
<div label="Google Cloud">

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Select **Import data from Cloud Storage**.

3. On the **Import Data from GCS** page, configure the following source data information:

    - **Included Schema Files**: for the sample data, select **Yes**.
    - **Data Format**: select **SQL**.
    - **Folder URI** or **File URI**: enter the sample data URI `gs://tidbcloud-samples-us-west1/`.
    - **Bucket Access**: you can use a GCS IAM Role to access your bucket. For more information, see [Configure GCS access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-gcs-access).

    If the region of the bucket is different from your cluster, confirm the compliance of cross region.

4. Click **Connect** > **Start Import**.

</div>

<div label="Azure Blob Storage">

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Select **Import data from Cloud Storage**.

3. On the **Import Data from Azure Blob Storage** page, configure the following source data information:

    - **Included Schema Files**: for the sample data, select **Yes**.
    - **Data Format**: select **SQL**.
    - **Folder URI**: enter the sample data URI `https://tcidmsampledata.blob.core.windows.net/sql/`.
    - **SAS Token**: 
        - For the sample data, use the following **SAS Token**: `sv=2015-04-05&ss=b&srt=co&sp=rl&se=2099-03-01T00%3A00%3A01.0000000Z&sig=cQHvaofmVsUJEbgyf4JFkAwTJGsFOmbQHx03GvVMrNc%3D`.
        - For your own data, you can use a SAS token to access your Azure Blob Storage. For more information, see [Configure Azure Blob Storage access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-azure-blob-storage-access).

    If the region of the storage account is different from your cluster, confirm the compliance of cross region.

4. Click **Connect** > **Start Import**.

</div>

When the data import progress shows **Completed**, you have successfully imported the sample data and the database schema to your database in TiDB Cloud.

After connecting to the cluster, you can run some queries in your terminal to check the result, for example:

1. Get the trip records starting at "12th & U St NW":

    ```sql
    use bikeshare;
    ```

    ```sql
    select * from `trips` where start_station_name='12th & U St NW' limit 10;
    ```
    ```sql
    +-----------------+---------------+---------------------+---------------------+--------------------+------------------+-------------------------------------------+----------------+-----------+------------+-----------+------------+---------------+
    | ride_id         | rideable_type | started_at          | ended_at            | start_station_name | start_station_id | end_station_name                          | end_station_id | start_lat | start_lng  | end_lat   | end_lng    | member_casual |
    +-----------------+---------------+---------------------+---------------------+--------------------+------------------+-------------------------------------------+----------------+-----------+------------+-----------+------------+---------------+
    | E291FF5018      | classic_bike  | 2021-01-02 11:12:38 | 2021-01-02 11:23:47 | 12th & U St NW     |            31268 | 7th & F St NW / National Portrait Gallery |          31232 | 38.916786 |  -77.02814 |  38.89728 | -77.022194 | member        |
    | E76F3605D0      | docked_bike   | 2020-09-13 00:44:11 | 2020-09-13 00:59:38 | 12th & U St NW     |            31268 | 17th St & Massachusetts Ave NW            |          31267 | 38.916786 |  -77.02814 | 38.908142 |  -77.03836 | casual        |
    | FFF0B75414      | docked_bike   | 2020-09-28 16:47:53 | 2020-09-28 16:57:30 | 12th & U St NW     |            31268 | 17th St & Massachusetts Ave NW            |          31267 | 38.916786 |  -77.02814 | 38.908142 |  -77.03836 | casual        |
    | C3F2C16949      | docked_bike   | 2020-09-13 00:42:03 | 2020-09-13 00:59:43 | 12th & U St NW     |            31268 | 17th St & Massachusetts Ave NW            |          31267 | 38.916786 |  -77.02814 | 38.908142 |  -77.03836 | casual        |
    | 1C7EC91629      | docked_bike   | 2020-09-28 16:47:49 | 2020-09-28 16:57:26 | 12th & U St NW     |            31268 | 17th St & Massachusetts Ave NW            |          31267 | 38.916786 |  -77.02814 | 38.908142 |  -77.03836 | member        |
    | A3A38BCACA      | classic_bike  | 2021-01-14 09:52:53 | 2021-01-14 10:00:51 | 12th & U St NW     |            31268 | 10th & E St NW                            |          31256 | 38.916786 |  -77.02814 | 38.895912 |  -77.02606 | member        |
    | EC4943257E      | electric_bike | 2021-01-28 10:06:52 | 2021-01-28 10:16:28 | 12th & U St NW     |            31268 | 10th & E St NW                            |          31256 | 38.916843 | -77.028206 |  38.89607 |  -77.02608 | member        |
    | D4070FBFA7      | classic_bike  | 2021-01-12 09:50:51 | 2021-01-12 09:59:41 | 12th & U St NW     |            31268 | 10th & E St NW                            |          31256 | 38.916786 |  -77.02814 | 38.895912 |  -77.02606 | member        |
    | 6EABEF3CAB      | classic_bike  | 2021-01-09 15:00:43 | 2021-01-09 15:18:30 | 12th & U St NW     |            31268 | 1st & M St NE                             |          31603 | 38.916786 |  -77.02814 | 38.905697 | -77.005486 | member        |
    | 2F5CC89018      | electric_bike | 2021-01-02 01:47:07 | 2021-01-02 01:58:29 | 12th & U St NW     |            31268 | 3rd & H St NE                             |          31616 | 38.916836 |  -77.02815 |  38.90074 |  -77.00219 | member        |
    +-----------------+---------------+---------------------+---------------------+--------------------+------------------+-------------------------------------------+----------------+-----------+------------+-----------+------------+---------------+
    ```

2. Get the trip records with electric bikes:

    ```sql
    use bikeshare;
    ```

    ```sql
    select * from `trips` where rideable_type="electric_bike" limit 10;
    ```
