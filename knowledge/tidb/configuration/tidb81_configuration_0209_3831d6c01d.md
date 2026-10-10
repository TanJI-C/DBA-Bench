# Changefeed cloud storage overview, restrictions, and destination setup

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-cloud-storage.md`
- Source Title: `Sink to Cloud Storage`
- Source Heading Path: `Sink to Cloud Storage | Sink to Cloud Storage > Restrictions | Sink to Cloud Storage > Step 1. Configure destination`
- Source Line Ranges: `5-94`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`
- Topic Tags: `changefeed`, `cloud-storage`, `amazon-s3`, `gcs`, `restrictions`, `destination-configuration`, `iam`, `connectivity`, `service-account`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0209_3831d6c01d`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-cloud-storage.md#sink-to-cloud-storage`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9888a029d4016a65133a7f1ac4b6f1d8fe1a297ecb1f544b8b44b225185a4519`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-cloud-storage#sink-to-cloud-storage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-cloud-storage.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud Dedicated changefeed sink-to-cloud-storage overview, restrictions, supported destinations, or destination connection setup for Amazon S3 or GCS.
- Retrieval Keywords: Sink to Cloud Storage, TiDB Cloud Dedicated, changefeed, cloud storage, Amazon S3, GCS, v7.1.1 or later, TiDB Cloud Serverless, changefeed feature is unavailable, up to 100 changefeeds, TiCDC restrictions, unsupported scenarios, primary key, non-null unique index, duplicated data inserted downstream, Create Changefeed, S3 URI, Access Key ID, Secret Access Key, same region, Service Account ID, IAM role, storage.buckets.get, storage.objects.create, storage.objects.delete, storage.objects.get, storage.objects.list, storage.objects.update, Grant access, bucket gsutil URI, gs://, connectivity error
- Follow-up Guidance: After the destination is configured, TiDB Cloud automatically tests the connection and either proceeds to the next step or displays a connectivity error for retry after it is resolved.
- Classification Note: Classified as configuration because the content defines changefeed prerequisites, restrictions, and the exact destination setup fields, permissions, and connection verification steps for Amazon S3 and GCS.

## Official Source Content

# Sink to Cloud Storage

This document describes how to create a changefeed to stream data from TiDB Cloud to cloud storage. Currently, Amazon S3 and GCS are supported.

> **Note:**
>
> - To stream data to cloud storage, make sure that your TiDB cluster version is v7.1.1 or later. To upgrade your TiDB Cloud Dedicated cluster to v7.1.1 or later, [contact TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
> - For [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters, the changefeed feature is unavailable.
## Restrictions

- For each TiDB Cloud cluster, you can create up to 100 changefeeds.
- Because TiDB Cloud uses TiCDC to establish changefeeds, it has the same [restrictions as TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview#unsupported-scenarios).
- If the table to be replicated does not have a primary key or a non-null unique index, the absence of a unique constraint during replication could result in duplicated data being inserted downstream in some retry scenarios.
## Step 1. Configure destination

Navigate to the cluster overview page of the target TiDB cluster. Click **Data** > **Changefeed** in the left navigation pane, click **Create Changefeed**, and select **Amazon S3** or **GCS** as the destination. The configuration process varies depend on the destination you choose.

<div label="Amazon S3">

For **Amazon S3**, fill the **S3 Endpoint** area: `S3 URI`, `Access Key ID`, and `Secret Access Key`. Make the S3 bucket in the same region with your TiDB cluster.

![s3_endpoint](/media/tidb-cloud/changefeed/sink-to-cloud-storage-s3-endpoint.jpg)

</div>
<div label="GCS">

For **GCS**, before filling **GCS Endpoint**, you need to first grant the GCS bucket access. Take the following steps:

1. In the TiDB Cloud console, record the **Service Account ID**, which will be used to grant TiDB Cloud access to your GCS bucket.

    ![gcs_endpoint](/media/tidb-cloud/changefeed/sink-to-cloud-storage-gcs-endpoint.png)

2. In the Google Cloud console, create an IAM role for your GCS bucket.

    1. Sign in to the [Google Cloud console](https://console.cloud.google.com/).
    2. Go to the [Roles](https://console.cloud.google.com/iam-admin/roles) page, and then click **Create role**.

        ![Create a role](/media/tidb-cloud/changefeed/sink-to-cloud-storage-gcs-create-role.png)

    3. Enter a name, description, ID, and role launch stage for the role. The role name cannot be changed after the role is created.
    4. Click **Add permissions**. Add the following permissions to the role, and then click **Add**.

        - storage.buckets.get
        - storage.objects.create
        - storage.objects.delete
        - storage.objects.get
        - storage.objects.list
        - storage.objects.update

    ![Add permissions](/media/tidb-cloud/changefeed/sink-to-cloud-storage-gcs-assign-permission.png)

3. Go to the [Bucket](https://console.cloud.google.com/storage/browser) page, and choose a GCS bucket you want TiDB Cloud to access. Note that the GCS bucket must be in the same region as your TiDB cluster.

4. On the **Bucket details** page, click the **Permissions** tab, and then click **Grant access**.

    ![Grant Access to the bucket ](/media/tidb-cloud/changefeed/sink-to-cloud-storage-gcs-grant-access-1.png)

5. Fill in the following information to grant access to your bucket, and then click **Save**.

    - In the **New Principals** field, paste the **Service Account ID** of the target TiDB cluster you recorded before.
    - In the **Select a role** drop-down list, type the name of the IAM role you just created, and then choose the name from the filter result.

    > **Note:**
    >
    > To remove the access to TiDB Cloud, simply remove the access that you have granted.

6. On the **Bucket details** page, click the **Objects** tab.

    - To get a bucket's gsutil URI, click the copy button and add `gs://` as a prefix. For example, if the bucket name is `test-sink-gcs`, the URI would be `gs://test-sink-gcs/`.

        ![Get bucket URI](/media/tidb-cloud/changefeed/sink-to-cloud-storage-gcs-uri01.png)

    - To get a folder's gsutil URI, open the folder, click the copy button, and add `gs://` as a prefix. For example, if the bucket name is `test-sink-gcs` and the folder name is `changefeed-xxx`, the URI would be `gs://test-sink-gcs/changefeed-xxx/`.

        ![Get bucket URI](/media/tidb-cloud/changefeed/sink-to-cloud-storage-gcs-uri02.png)

7. In the TiDB Cloud console, go to the Changefeed's **Configure Destination** page, and fill in the **bucket gsutil URI** field.

</div>

Click **Next** to establish the connection from the TiDB Cloud Dedicated cluster to Amazon S3 or GCS. TiDB Cloud will automatically test and verify if the connection is successful.

- If yes, you are directed to the next step of configuration.
- If not, a connectivity error is displayed, and you need to handle the error. After the error is resolved, click **Next** to retry the connection.
