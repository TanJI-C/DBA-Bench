# TiDB Cloud audit logging setup for Google Cloud and Azure prerequisites

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-auditing.md`
- Source Title: `TiDB Cloud Dedicated Database Audit Logging`
- Source Heading Path: `TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for Google Cloud | TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for Google Cloud > Step 1. Create a GCS bucket | TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for Google Cloud > Step 2. Configure GCS access | TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for Google Cloud > Step 3. Enable audit logging | TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for Azure | TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for Azure > Step 1. Create an Azure storage account`
- Source Line Ranges: `113-186`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `audit-logging`, `google-cloud`, `gcs`, `iam`, `bucket-access`, `connection-testing`, `azure`, `storage-account`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0297_91d84fd756`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-auditing.md#enable-audit-logging-for-google-cloud`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `618867ca0798d6d024d9667f6eab1303d503d3bd8b20d9da909649193fababab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-auditing#enable-audit-logging-for-google-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-auditing.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Google Cloud or Azure storage prerequisites for TiDB Cloud Dedicated audit logging, especially GCS bucket access and connection testing details.
- Retrieval Keywords: Enable audit logging for Google Cloud, Google Cloud Storage, GCS bucket, Google Cloud Service Account ID, Google Cloud Server Account ID, Service Account ID, IAM & Admin, Roles, storage.objects.create, storage.objects.delete, ADD PRINCIPAL, Bucket URI, Bucket Region, Test Connection, The connection is successfully, Enable audit logging for Azure, Azure storage account
- Follow-up Guidance: The chunk also notes that after changing the GCS bucket URI or location, you must click Test Connection again and then click Enable to apply the changes.
- Classification Note: This chunk is classified as configuration because it describes the required cloud storage and IAM setup steps for Google Cloud and the Azure storage account prerequisite for audit logging.

## Official Source Content

### Enable audit logging for Google Cloud

To enable audit logging for Google Cloud, take the following steps:
#### Step 1. Create a GCS bucket

Specify a Google Cloud Storage (GCS) bucket in your corporate-owned Google Cloud account as a destination to which TiDB Cloud writes audit logs.

For more information, see [Creating storage buckets](https://cloud.google.com/storage/docs/creating-buckets) in the Google Cloud Storage documentation.
#### Step 2. Configure GCS access

1. Get the Google Cloud Service Account ID of the TiDB cluster that you want to enable audit logging.

    1. In the TiDB Cloud console, navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Settings** > **DB Audit Logging** in the left navigation pane.
    3. On the **DB Audit Logging** page, click **Enable** in the upper-right corner.
    4. In the **Enable Database Audit Logging** dialog, locate the **Google Cloud Server Account ID** section, and record **Service Account ID** for later use.

2. In the Google Cloud console, go to **IAM & Admin** > **Roles**, and then check whether a role with the following write-only permissions of the storage container exists.

    - storage.objects.create
    - storage.objects.delete

    If yes, record the matched role for the TiDB cluster for later use. If not, go to **IAM & Admin** > **Roles** > **CREATE ROLE** to define a role for the TiDB cluster.

3. Go to **Cloud Storage** > **Browser**, select the GCS bucket you want TiDB Cloud to access, and then click **SHOW INFO PANEL**.

    The panel is displayed.

4. In the panel, click **ADD PRINCIPAL**.

    The dialog box for adding principals is displayed.

5. In the dialog box, take the following steps:

    1. In the **New Principals** field, paste the Google Cloud Service Account ID of the TiDB cluster.
    2. In the **Role** drop-down list, choose the role of the target TiDB cluster.
    3. Click **SAVE**.
#### Step 3. Enable audit logging

In the TiDB Cloud console, go back to the **Enable Database Audit Logging** dialog box where you got the TiDB Cloud account ID, and then take the following steps:

1. In the **Bucket URI** field, enter your full GCS bucket name.
2. In the **Bucket Region** field, select the GCS region where the bucket locates.
3. Click **Test Connection** to verify whether TiDB Cloud can access and write to the bucket.

    If it is successful, **The connection is successfully** is displayed. Otherwise, check your access configuration.

4. Click **Enable** to enable audit logging for the cluster.

    TiDB Cloud is ready to write audit logs for the specified cluster to your GCS bucket.

> **Note:**
>
> - After enabling audit logging, if you make any new changes to the bucket URI or location, you must click **Test Connection** again to verify that TiDB Cloud can connect to the bucket. Then, click **Enable** to apply the changes.
> - To remove TiDB Cloud's access to your GCS bucket, delete the trust policy granted to this cluster in the Google Cloud console.
### Enable audit logging for Azure

To enable audit logging for Azure, take the following steps:
#### Step 1. Create an Azure storage account

Create an Azure storage account in your organization's Azure subscription as the destination to which TiDB Cloud writes the database audit logs.

For more information, see [Create an Azure storage account](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal) in Azure documentation.
