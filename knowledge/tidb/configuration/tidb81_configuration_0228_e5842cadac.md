# Configure S3 external storage access for TiDB Cloud Dedicated

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/dedicated-external-storage.md`
- Source Title: `Configure External Storage Access for TiDB Cloud Dedicated`
- Source Heading Path: `Configure External Storage Access for TiDB Cloud Dedicated | Configure External Storage Access for TiDB Cloud Dedicated > Configure Amazon S3 access | Configure External Storage Access for TiDB Cloud Dedicated > Configure Amazon S3 access > Configure Amazon S3 access using a Role ARN | Configure External Storage Access for TiDB Cloud Dedicated > Configure Amazon S3 access > Configure Amazon S3 access using an AWS access key`
- Source Line Ranges: `6-149`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `external-storage`, `amazon-s3`, `role-arn`, `aws-access-key`, `iam`, `bucket-policy`, `kms`, `data-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0228_e5842cadac`
- Source ID: `tidb-docs-8.1:tidb-cloud/dedicated-external-storage.md#configure-external-storage-access-for-tidb-cloud-dedicated`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7cc999d01bf6b2205eb523801fbd7be367042f8012efcce2d30f53ca605e6909`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-external-storage-access-for-tidb-cloud-dedicated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/dedicated-external-storage.md

## Retrieval Guidance

- Use When: Use this chunk when configuring cross-account Amazon S3 access for importing or migrating source data into a TiDB Cloud Dedicated cluster with either a Role ARN or an AWS access key.
- Retrieval Keywords: TiDB Cloud Dedicated external storage, Configure Amazon S3 access, Role ARN, AWS access key, TiDB Cloud Account ID, TiDB Cloud External ID, Import Data from Amazon S3, Create Role ARN manually, s3:GetObject, s3:GetObjectVersion, s3:ListBucket, SSE-KMS, kms:Decrypt, AmazonS3ReadOnlyAccess, CreateOwnAccessKeys, ManageOwnAccessKeys, confused deputy problem
- Follow-up Guidance: The content also points to the TiDB Cloud console path **Data** > **Import** > **Import data from Cloud Storage** > **Amazon S3** and notes that Serverless clusters use a separate external storage document.
- Classification Note: This is classified as configuration because the official content describes how to set up Amazon S3 bucket access, IAM policy permissions, Role ARN trust settings, and AWS access keys for TiDB Cloud Dedicated.

## Official Source Content

# Configure External Storage Access for TiDB Cloud Dedicated

If your source data is stored in Amazon S3 buckets, Azure Blob Storage containers, or Google Cloud Storage (GCS) buckets, before importing or migrating the data to TiDB Cloud, you need to configure cross-account access to the buckets. This document describes how to do this for TiDB Cloud Dedicated clusters.

If you need to configure these external storages for TiDB Cloud Serverless clusters, see [Configure External Storage Access for TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage).
## Configure Amazon S3 access

To allow a TiDB Cloud Dedicated cluster to access the source data in your Amazon S3 bucket, configure the bucket access for the cluster using either of the following methods:

- [Use a Role ARN](#configure-amazon-s3-access-using-a-role-arn) (recommended): use a Role ARN to access your Amazon S3 bucket.
- [Use an AWS access key](#configure-amazon-s3-access-using-an-aws-access-key): use the access key of an IAM user to access your Amazon S3 bucket.
### Configure Amazon S3 access using a Role ARN

Configure the bucket access for TiDB Cloud and get the Role ARN as follows:

1. In the [TiDB Cloud console](https://tidbcloud.com/), get the corresponding TiDB Cloud account ID and external ID of the target TiDB cluster.

    1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

    3. Select **Import data from Cloud Storage**, and then click **Amazon S3**.

    4. On the **Import Data from Amazon S3** page, click the link under **Role ARN**. The **Add New Role ARN** dialog is displayed.

    5. Expand **Create Role ARN manually** to get the TiDB Cloud Account ID and TiDB Cloud External ID. Take a note of these IDs for later use.

2. In the AWS Management Console, create a managed policy for your Amazon S3 bucket.

    1. Sign in to the AWS Management Console and open the Amazon S3 console at [https://console.aws.amazon.com/s3/](https://console.aws.amazon.com/s3/).
    2. In the **Buckets** list, choose the name of your bucket with the source data, and then click **Copy ARN** to get your S3 bucket ARN (for example, `arn:aws:s3:::tidb-cloud-source-data`). Take a note of the bucket ARN for later use.

        ![Copy bucket ARN](/media/tidb-cloud/copy-bucket-arn.png)

    3. Open the IAM console at [https://console.aws.amazon.com/iam/](https://console.aws.amazon.com/iam/), click **Policies** in the navigation pane on the left, and then click **Create Policy**.

        ![Create a policy](/media/tidb-cloud/aws-create-policy.png)

    4. On the **Create policy** page, click the **JSON** tab.
    5. Copy the following access policy template and paste it into the policy text field.

        ````json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:GetObjectVersion"
                    ],
                    "Resource": "<Your S3 bucket ARN>/<Directory of your source data>/*"
                },
                {
                    "Sid": "VisualEditor1",
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListBucket"
                    ],
                    "Resource": "<Your S3 bucket ARN>"
                }
            ]
        }
        ```

        In the policy text field, update the following configurations to your own values.

        - `"Resource": "<Your S3 bucket ARN>/<Directory of the source data>/*"`

            For example, if your source data is stored in the root directory of the `tidb-cloud-source-data` bucket, use `"Resource": "arn:aws:s3:::tidb-cloud-source-data/*"`. If your source data is stored in the `mydata` directory of the bucket, use `"Resource": "arn:aws:s3:::tidb-cloud-source-data/mydata/*"`. Make sure that `/*` is added to the end of the directory so TiDB Cloud can access all files in this directory.

        - `"Resource": "<Your S3 bucket ARN>"`

            For example, `"Resource": "arn:aws:s3:::tidb-cloud-source-data"`.

        - If you have enabled AWS Key Management Service key (SSE-KMS) with customer-managed key encryption, make sure the following configuration is included in the policy. `"arn:aws:kms:ap-northeast-1:105880447796:key/c3046e91-fdfc-4f3a-acff-00597dd3801f"` is a sample KMS key of the bucket.

            ```json
            {
                "Sid": "AllowKMSkey",
                "Effect": "Allow",
                "Action": [
                    "kms:Decrypt"
                ],
                "Resource": "arn:aws:kms:ap-northeast-1:105880447796:key/c3046e91-fdfc-4f3a-acff-00597dd3801f"
            }
            ```

            If the objects in your bucket have been copied from another encrypted bucket, the KMS key value needs to include the keys of both buckets. For example, `"Resource": ["arn:aws:kms:ap-northeast-1:105880447796:key/c3046e91-fdfc-4f3a-acff-00597dd3801f","arn:aws:kms:ap-northeast-1:495580073302:key/0d7926a7-6ecc-4bf7-a9c1-a38f0faec0cd"]`.

    6. Click **Next**.
    7. Set a policy name, add a tag of the policy (optional), and then click **Create policy**.

3. In the AWS Management Console, create an access role for TiDB Cloud and get the role ARN.

    1. In the IAM console at [https://console.aws.amazon.com/iam/](https://console.aws.amazon.com/iam/), click **Roles** in the navigation pane on the left, and then click **Create role**.

        ![Create a role](/media/tidb-cloud/aws-create-role.png)

    2. To create a role, fill in the following information:

        - Under **Trusted entity type**, select **AWS account**.
        - Under **An AWS account**, select **Another AWS account**, and then paste the TiDB Cloud account ID to the **Account ID** field.
        - Under **Options**, click **Require external ID** to avoid the [confused deputy problem](https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html), and then paste the TiDB Cloud External ID to the **External ID** field. If the role is created without "Require external ID", anyone with your S3 bucket URI and IAM role ARN might be able to access your Amazon S3 bucket. If the role is created with both the account ID and external ID, only TiDB clusters running in the same project and the same region can access the bucket.

    3. Click **Next** to open the policy list, choose the policy you just created, and then click **Next**.
    4. Under **Role details**, set a name for the role, and then click **Create role** in the lower-right corner. After the role is created, the list of roles is displayed.
    5. In the list of roles, click the name of the role that you just created to go to its summary page, and then copy the role ARN.

        ![Copy AWS role ARN](/media/tidb-cloud/aws-role-arn.png)

4. In the TiDB Cloud console, go to the **Data Import** page where you get the TiDB Cloud account ID and external ID, and then paste the role ARN to the **Role ARN** field.
### Configure Amazon S3 access using an AWS access key

It is recommended that you use an IAM user (instead of the AWS account root user) to create an access key.

Take the following steps to configure an access key:

1. Create an IAM user with the following policies:

   - `AmazonS3ReadOnlyAccess`
   - [`CreateOwnAccessKeys` (required) and `ManageOwnAccessKeys` (optional)](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#access-keys_required-permissions)

   It is recommended that these policies only work for your bucket that stores the source data.

   For more information, see [Creating an IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console).

2. Use your AWS account ID or account alias, and your IAM user name and password to sign in to [the IAM console](https://console.aws.amazon.com/iam).

3. Create an access key. For more details, see [Creating an access key for an IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey).

> **Note:**
>
> TiDB Cloud does not store your access keys. It is recommended that you [delete the access key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey) after the import is complete.
