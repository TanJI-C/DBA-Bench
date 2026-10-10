# Configure GCS, Azure Blob, and Alibaba OSS access for TiDB Cloud Serverless

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-external-storage.md`
- Source Title: `Configure TiDB Cloud Serverless External Storage Access`
- Source Heading Path: `Configure External Storage Access for TiDB Cloud Serverless > Configure GCS access | Configure External Storage Access for TiDB Cloud Serverless > Configure Azure Blob Storage access | Configure External Storage Access for TiDB Cloud Serverless > Configure Alibaba Cloud Object Storage Service (OSS) access`
- Source Line Ranges: `181-294`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `external-storage`, `gcs`, `azure-blob`, `oss`, `service-account`, `sas-token`, `accesskey`, `import`, `export`, `permissions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0262_4e1d8fb7fb`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-external-storage.md#configure-gcs-access`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ec65a12b3b1c33acadc5fc86e31e4d4358ef6be4649b71951bcb4f88e976605b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-gcs-access
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-external-storage.md

## Retrieval Guidance

- Use When: Use this chunk when configuring external storage access for a TiDB Cloud Serverless cluster with GCS, Azure Blob Storage, or Alibaba Cloud OSS for data import or export.
- Retrieval Keywords: TiDB Cloud Serverless external storage access, Configure GCS access, service account key, storage.objects.create, storage.buckets.get, storage.objects.get, storage.objects.list, Configure Azure Blob Storage access, service SAS token, Azure ARM template, Generate New SAS Token via ARM Template Deployment, Allowed services Blob, Allowed Resource types Container Object, Read and Write permissions, Read and List permissions, Generate SAS and connection string, Configure Alibaba Cloud Object Storage Service (OSS) access, AccessKey pair, RAM user, Using permanent AccessKey to access, oss:GetObject, oss:GetBucketInfo, oss:ListObjects, oss:PutObject, oss:ListBuckets
- Follow-up Guidance: The source also provides the exact permission sets needed for import and export for GCS, Azure Blob Storage, and Alibaba Cloud OSS, along with where to create the corresponding credentials or tokens.
- Classification Note: This is classified as configuration because the content explains how to set up cloud storage credentials, tokens, and permissions for TiDB Cloud Serverless external storage access.

## Official Source Content

## Configure GCS access

To allow a TiDB Cloud Serverless cluster to access your GCS bucket, you need to configure the GCS access for the bucket. You can use a service account key to configure the bucket access:

Take the following steps to configure a service account key:

1. On the Google Cloud [service account page](https://console.cloud.google.com/iam-admin/serviceaccounts), click **CREATE SERVICE ACCOUNT** to create a service account. For more information, see [Creating a service account](https://cloud.google.com/iam/docs/creating-managing-service-accounts).

    1. Enter a service account name.
    2. Optional: Enter a description of the service account.
    3. Click **CREATE AND CONTINUE** to create the service account.
    4. In the `Grant this service account access to project`, choose the [IAM roles](https://cloud.google.com/iam/docs/understanding-roles) with the needed permission.

        - Exporting data from a TiDB Cloud Serverless cluster needs a role with `storage.objects.create` permission.
        - Importing data into a TiDB Cloud Serverless cluster needs a role with `storage.buckets.get`, `storage.objects.get`, and `storage.objects.list` permissions.

    5. Click **Continue** to go to the next step.
    6. Optional: In the `Grant users access to this service account`, choose members that need to [attach the service account to other resources](https://cloud.google.com/iam/docs/attach-service-accounts).
    7. Click **Done** to finish creating the service account.

   ![service-account](/media/tidb-cloud/serverless-external-storage/gcs-service-account.png)

2. Click the service account, and then click **ADD KEY** on the `KEYS` page to create a service account key.

   ![service-account-key](/media/tidb-cloud/serverless-external-storage/gcs-service-account-key.png)

3. Choose the default `JSON` key type, and then click **CREATE** to download the Google Cloud credentials file. The file contains the service account key that you need to use when configuring the GCS access for the TiDB Cloud Serverless cluster.
## Configure Azure Blob Storage access

To allow TiDB Cloud Serverless to access your Azure Blob container, you need to create a service SAS token for the container.

You can create a SAS token either using an [Azure ARM template](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/overview) (recommended) or manual configuration. 

To create a SAS token using an Azure ARM template, take the following steps:

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

2. Open the **Generate New SAS Token via ARM Template Deployment** dialog.
        
    1. Click **Export data to...**  > **Azure Blob Storage**. If your cluster has neither imported nor exported any data before, click **Click here to export data to...** > **Azure Blob Storage** at the bottom of the page.
   
    2. Scroll down to the **Azure Blob Storage Settings** area, and then click **Click here to create a new one with Azure ARM template** under the SAS Token field. 
   
3. Create a SAS token with the Azure ARM template.

    1. In the **Generate New SAS Token via ARM Template Deployment** dialog, click **Click to open the Azure Portal with the pre-configured ARM template**.
   
    2. After logging in to Azure, you will be redirected to the Azure **Custom deployment** page.

    3. Fill in the **Resource group** and **Storage Account Name** in the **Custom deployment** page. You can get all the information from the storage account overview page where the container is located.

        ![azure-storage-account-overview](/media/tidb-cloud/serverless-external-storage/azure-storage-account-overview.png)

    4. Click **Review + create** or **Next** to review the deployment. Click **Create** to start the deployment.
   
    5. After it completes, you will be redirected to the deployment overview page. Navigate to the **Outputs** section to get the SAS token.

If you have any trouble creating a SAS token with the Azure ARM template, take the following steps to create one manually:

<details>
<summary>Click here to see details</summary>

1. On the [Azure Storage account](https://portal.azure.com/#browse/Microsoft.Storage%2FStorageAccounts) page, click your storage account to which the container belongs.
   
2. On your **Storage account** page, click the **Security+network**, and then click **Shared access signature**.

   ![sas-position](/media/tidb-cloud/serverless-external-storage/azure-sas-position.png)

3. On the **Shared access signature** page, create a service SAS token with needed permissions as follows. For more information, see [Create a service SAS token](https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview).

    1. In the **Allowed services** section, choose the **Blob** service.
    2. In the **Allowed Resource types** section, choose **Container** and **Object**.
    3. In the **Allowed permissions** section, choose the permission as needed.

        - Exporting data from a TiDB Cloud Serverless cluster needs the **Read** and **Write** permissions.
        - Importing data into a TiDB Cloud Serverless cluster needs the **Read** and **List** permissions.

    4. Adjust **Start and expiry date/time** as needed.
    5. You can keep the default values for other settings.

   ![sas-create](/media/tidb-cloud/serverless-external-storage/azure-sas-create.png)

4. Click **Generate SAS and connection string** to generate the SAS token.

</details>
## Configure Alibaba Cloud Object Storage Service (OSS) access

To allow TiDB Cloud Serverless to access your Alibaba Cloud OSS bucket, you need to create an AccessKey pair for the bucket.

Take the following steps to configure an AccessKey pair:

1. Create a RAM user and get the AccessKey pair. For more information, see [Create a RAM user](https://www.alibabacloud.com/help/en/ram/user-guide/create-a-ram-user).
    
    In the **Access Mode** section, select **Using permanent AccessKey to access**.

2. Create a custom policy with the required permissions. For more information, see [Create custom policies](https://www.alibabacloud.com/help/en/ram/user-guide/create-a-custom-policy).
    
    - In the **Effect** section, select **Allow**.
    - In the **Service** section, select **Object Storage Service**.
    - In the **Action** section, select the permissions as needed.
   
        To import data into a TiDB Cloud Serverless cluster, grant **oss:GetObject**, **oss:GetBucketInfo**, and **oss:ListObjects** permissions.

        To export data from a TiDB Cloud Serverless cluster, grant **oss:PutObject**, **oss:GetBucketInfo**, and **oss:ListBuckets** permissions.
        
    - In the **Resource** section, select the bucket and the objects in the bucket.

3. Attach the custom policies to the RAM user. For more information, see [Grant permissions to a RAM user](https://www.alibabacloud.com/help/en/ram/user-guide/grant-permissions-to-the-ram-user).
