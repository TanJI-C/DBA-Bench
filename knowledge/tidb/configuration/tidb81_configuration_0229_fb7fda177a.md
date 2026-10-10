# Configure GCS bucket access for TiDB Cloud Dedicated imports

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/dedicated-external-storage.md`
- Source Title: `Configure External Storage Access for TiDB Cloud Dedicated`
- Source Heading Path: `Configure External Storage Access for TiDB Cloud Dedicated > Configure GCS access`
- Source Line Ranges: `150-215`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `gcs`, `iam`, `service-account`, `bucket-permissions`, `data-import`, `uri`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0229_fb7fda177a`
- Source ID: `tidb-docs-8.1:tidb-cloud/dedicated-external-storage.md#configure-gcs-access`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `71672749c31f2193732ec0577afa7cd89e8d23ba53703622d017ea10f5a5f001`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-gcs-access
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/dedicated-external-storage.md

## Retrieval Guidance

- Use When: Use this chunk when configuring Google Cloud Storage bucket access and a gsutil URI for TiDB Cloud Dedicated data import.
- Retrieval Keywords: Configure GCS access, TiDB Cloud Dedicated, Google Cloud Service Account ID, Import data from Cloud Storage, Google Cloud Storage, IAM role, storage.buckets.get, storage.objects.get, storage.objects.list, GRANT ACCESS, Bucket gsutil URI, gs://tidb-cloud-source-data/, Copy gsutil URI
- Follow-up Guidance: After granting bucket access, the content shows how to copy a file gsutil URI or build a folder URI such as gs://tidb-cloud-source-data/ and paste it into the Bucket gsutil URI field on the Data Import page.
- Classification Note: This is classified as configuration because the content describes setting up GCS IAM permissions, bucket access, and the import URI for TiDB Cloud Dedicated.

## Official Source Content

## Configure GCS access

To allow TiDB Cloud to access the source data in your GCS bucket, you need to configure the GCS access for the bucket. Once the configuration is done for one TiDB cluster in a project, all TiDB clusters in that project can access the GCS bucket.

1. In the TiDB Cloud console, get the Google Cloud Service Account ID of the target TiDB cluster.

    1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

    3. Select **Import data from Cloud Storage**, and then click **Google Cloud Storage**.

    4. Click **Show Google Cloud Server Account ID**, and then copy the Service Account ID for later use.

2. In the Google Cloud console, create an IAM role for your GCS bucket.

    1. Sign in to the [Google Cloud console](https://console.cloud.google.com/).
    2. Go to the [Roles](https://console.cloud.google.com/iam-admin/roles) page, and then click **CREATE ROLE**.

        ![Create a role](/media/tidb-cloud/gcp-create-role.png)

    3. Enter a name, description, ID, and role launch stage for the role. The role name cannot be changed after the role is created.
    4. Click **ADD PERMISSIONS**.
    5. Add the following read-only permissions to the role, and then click **Add**.

        - storage.buckets.get
        - storage.objects.get
        - storage.objects.list

        You can copy a permission name to the **Enter property name or value** field as a filter query, and choose the name in the filter result. To add the three permissions, you can use **OR** between the permission names.

        ![Add permissions](/media/tidb-cloud/gcp-add-permissions.png)

3. Go to the [Bucket](https://console.cloud.google.com/storage/browser) page, and click the name of the GCS bucket you want TiDB Cloud to access.

4. On the **Bucket details** page, click the **PERMISSIONS** tab, and then click **GRANT ACCESS**.

    ![Grant Access to the bucket ](/media/tidb-cloud/gcp-bucket-permissions.png)

5. Fill in the following information to grant access to your bucket, and then click **SAVE**.

    - In the **New Principals** field, paste the Google Cloud Service Account ID of the target TiDB cluster.
    - In the **Select a role** drop-down list, type the name of the IAM role you just created, and then choose the name from the filter result.

    > **Note:**
    >
    > To remove the access to TiDB Cloud, you can simply remove the access that you have granted.

6. On the **Bucket details** page, click the **OBJECTS** tab.

    If you want to copy a file's gsutil URI, select the file, click **Open object overflow menu**, and then click **Copy gsutil URI**.

    ![Get bucket URI](/media/tidb-cloud/gcp-bucket-uri01.png)

    If you want to use a folder's gsutil URI, open the folder, and then click the copy button following the folder name to copy the folder name. After that, you need to add `gs://` to the beginning and `/` to the end of the name to get the correct URI for the folder.

    For example, if the folder name is `tidb-cloud-source-data`, you need to use `gs://tidb-cloud-source-data/` as the URI.

    ![Get bucket URI](/media/tidb-cloud/gcp-bucket-uri02.png)

7. In the TiDB Cloud console, go to the **Data Import** page where you get the Google Cloud Service Account ID, and then paste the GCS bucket gsutil URI to the **Bucket gsutil URI** field. For example, paste `gs://tidb-cloud-source-data/`.
