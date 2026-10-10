# Serverless export examples for local file, Amazon S3, and Google Cloud Storage

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-export.md`
- Source Title: `Export Data from TiDB Cloud Serverless`
- Source Heading Path: `Export Data from TiDB Cloud Serverless > Examples | Export Data from TiDB Cloud Serverless > Examples > Export data to a local file | Export Data from TiDB Cloud Serverless > Examples > Export data to Amazon S3 | Export Data from TiDB Cloud Serverless > Examples > Export data to Google Cloud Storage`
- Source Line Ranges: `171-305`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `export`, `console`, `cli`, `local-file`, `s3`, `gcs`, `credentials`, `download`, `task-creation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0364_52b12441c1`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-export.md#examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `26de8d6be830a365e0ce101c22b9b78870632b57e3136afb9cfaf24b1409232a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-export#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-export.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official examples for exporting TiDB Cloud Serverless data to a local file, Amazon S3, or Google Cloud Storage by console or CLI.
- Retrieval Keywords: Export data to a local file, Export data to Amazon S3, Export data to Google Cloud Storage, ticloud serverless export create -c <cluster-id>, ticloud serverless export download -c <cluster-id> -e <export-id>, --target-type S3, --s3.uri, --s3.access-key-id, --s3.secret-access-key, --s3.role-arn, --target-type GCS, --gcs.uri, --gcs.service-account-key, SNAPSHOT_{snapshot_time}, Data Format SQL CSV Parquet, Compression Gzip Snappy Zstd None, s3://<bucket-name>/<folder-path>/, gs://<bucket-name>/<folder-path>/, --filter "database.table"
- Follow-up Guidance: For local file export, after the export task is successful, the content says you can copy the download command from the export task detail or use `ticloud serverless export download -c <cluster-id> -e <export-id>` in the TiDB Cloud CLI.
- Classification Note: This is operation content because it provides step-by-step console and CLI procedures and command examples for creating export tasks and downloading exported data.

## Official Source Content

## Examples
### Export data to a local file

<div label="Console">

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

   > **Tip:**
   >
   > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

3. On the **Import** page, click **Export Data to** in the upper-right corner, then choose **Local File** from the drop-down list. Fill in the following parameters:

    - **Task Name**: enter a name for the export task. The default value is `SNAPSHOT_{snapshot_time}`.
    - **Exported Data**: choose the databases and tables you want to export.
    - **Data Format**: choose **SQL**, **CSV**, or **Parquet**.
    - **Compression**: choose **Gzip**, **Snappy**, **Zstd**, or **None**.

   > **Tip:**
   >
   > If your cluster has neither imported nor exported any data before, you need to click **Click here to export data to...** at the bottom of the page to export data.

4. Click **Export**.

5. After the export task is successful, you can copy the download command displayed in the export task detail, and then download the exported data by running the command in the [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference).

</div>

<div label="CLI">

1. Create an export task:

    ```shell
    ticloud serverless export create -c <cluster-id>
    ```

    You will get an export ID from the output.

2. After the export task is successful, download the exported data to your local file:

    ```shell
    ticloud serverless export download -c <cluster-id> -e <export-id>
    ```

    For more information about the download command, see [ticloud serverless export download](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-export-download).
 
</div>
### Export data to Amazon S3

<div label="Console">

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

   > **Tip:**
   >
   > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

3. On the **Import** page, click **Export Data to** in the upper-right corner, then choose **Amazon S3** from the drop-down list. Fill in the following parameters:

    - **Task Name**: enter a name for the export task. The default value is `SNAPSHOT_{snapshot_time}`.
    - **Exported Data**: choose the databases and tables you want to export.
    - **Data Format**: choose **SQL**, **CSV**, or **Parquet**.
    - **Compression**: choose **Gzip**, **Snappy**, **Zstd**, or **None**.
    - **Folder URI**: enter the URI of the Amazon S3 with the `s3://<bucket-name>/<folder-path>/` format.
    - **Bucket Access**: choose one of the following access credentials and then fill in the credential information:
        - **AWS Role ARN**: enter the role ARN that has the permission to access the bucket. It is recommended to create the role ARN with AWS CloudFormation. For more information, see [Configure External Storage Access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-amazon-s3-access).
        - **AWS Access Key**: enter the access key ID and access key secret that have the permission to access the bucket.

4. Click **Export**.

</div>

<div label="CLI">

```shell
ticloud serverless export create -c <cluster-id> --target-type S3 --s3.uri <uri> --s3.access-key-id <access-key-id> --s3.secret-access-key <secret-access-key> --filter "database.table"

ticloud serverless export create -c <cluster-id> --target-type S3 --s3.uri <uri> --s3.role-arn <role-arn> --filter "database.table"
```

- `s3.uri`: the Amazon S3 URI with the `s3://<bucket-name>/<folder-path>/` format.
- `s3.access-key-id`: the access key ID of the user who has the permission to access the bucket.
- `s3.secret-access-key`: the access key secret of the user who has the permission to access the bucket.
- `s3.role-arn`: the role ARN that has the permission to access the bucket.

</div>
### Export data to Google Cloud Storage

<div label="Console">

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

   > **Tip:**
   >
   > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

3. On the **Import** page, click **Export Data to** in the upper-right corner, and then choose **Google Cloud Storage** from the drop-down list. Fill in the following parameters:

    - **Task Name**: enter a name for the export task. The default value is `SNAPSHOT_{snapshot_time}`.
    - **Exported Data**: choose the databases and tables you want to export.
    - **Data Format**: choose **SQL**, **CSV**, or **Parquet**.
    - **Compression**: choose **Gzip**, **Snappy**, **Zstd**, or **None**.
    - **Folder URI**: enter the URI of the Google Cloud Storage with the `gs://<bucket-name>/<folder-path>/` format.
    - **Bucket Access**: upload the Google Cloud credentials file that has permission to access the bucket.

4. Click **Export**.

</div>

<div label="CLI">

```shell
ticloud serverless export create -c <cluster-id> --target-type GCS --gcs.uri <uri> --gcs.service-account-key <service-account-key> --filter "database.table"
```

- `gcs.uri`: the URI of the Google Cloud Storage bucket in the `gs://<bucket-name>/<folder-path>/` format.
- `gcs.service-account-key`: the base64 encoded service account key.

</div>
