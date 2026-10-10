# Import full export from Amazon S3 into TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-op-tidb.md`
- Source Title: `Migrate from TiDB Self-Managed to TiDB Cloud`
- Source Heading Path: `Migrate from TiDB Self-Managed to TiDB Cloud > Migrate full data > Migrate data from Amazon S3 to TiDB Cloud`
- Source Line Ranges: `200-273`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dumpling`
- Topic Tags: `full-data-migration`, `amazon-s3`, `iam`, `kms`, `role-arn`, `import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0099_bbad461952`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-op-tidb.md#migrate-data-from-amazon-s3-to-tidb-cloud`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e978c6d5520d755edf4d14b391d5207182155e2c42c83d13d80d296798dbf925`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-op-tidb#migrate-data-from-amazon-s3-to-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-op-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented TiDB Cloud process for importing full exported data from Amazon S3, including AWS IAM policy, Account ID, External ID, and Role-ARN details.
- Retrieval Keywords: Migrate data from Amazon S3 to TiDB Cloud, Account ID, External ID, Role-ARN, AWS Console > IAM > Access Management > Policies, AWS Console > IAM > Access Management > Roles, s3:GetObject, s3:GetObjectVersion, s3:ListBucket, s3:GetBucketLocation, kms:Decrypt, SSE-KMS, Import CSV Files from Cloud Storage into TiDB Cloud Dedicated
- Follow-up Guidance: The chunk points to Import CSV Files from Cloud Storage into TiDB Cloud Dedicated for the actual data import step after obtaining the Role-ARN.
- Classification Note: This is classified as a cloud data pipeline chunk because the content covers full-data migration into TiDB Cloud from Amazon S3 using IAM permissions and import configuration.

## Official Source Content

### Migrate data from Amazon S3 to TiDB Cloud

After you export data from the TiDB Self-Managed cluster to Amazon S3, you need to migrate the data to TiDB Cloud.

1. Get the Account ID and External ID of the cluster in the TiDB Cloud console. For more information, see [Step 2. Configure Amazon S3 access](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-auditing#step-2-configure-amazon-s3-access).

    The following screenshot shows how to get the Account ID and External ID:

    ![Get the Account ID and External ID](/media/tidb-cloud/op-to-cloud-get-role-arn.png)

2. Configure access permissions for Amazon S3. Usually you need the following read-only permissions:

    - s3:GetObject
    - s3:GetObjectVersion
    - s3:ListBucket
    - s3:GetBucketLocation

    If the S3 bucket uses server-side encryption SSE-KMS, you also need to add the KMS permission.

    - kms:Decrypt

3. Configure the access policy. Go to the [AWS Console > IAM > Access Management > Policies](https://console.aws.amazon.com/iamv2/home#/policies) and switch to your region to check if the access policy for TiDB Cloud exists already. If it does not exist, create a policy following this document [Creating policies on the JSON tab](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_create-console.html).

    The following is an example template for the json policy.

    ```json
    ## Create a json policy template
    ##<Your customized directory>: fill in the path to the folder in the S3 bucket where the data files to be imported are located.
    ##<Your S3 bucket ARN>: fill in the ARN of the S3 bucket. You can click the Copy ARN button on the S3 Bucket Overview page to get it.
    ##<Your AWS KMS ARN>: fill in the ARN for the S3 bucket KMS key. You can get it from S3 bucket > Properties > Default encryption > AWS KMS Key ARN. For more information, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/viewing-bucket-key-settings.html

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:GetObjectVersion"
                ],
                "Resource": "arn:aws:s3:::<Your customized directory>"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:GetBucketLocation"
                ],
                "Resource": "<Your S3 bucket ARN>"
            }
            // If you have enabled SSE-KMS for the S3 bucket, you need to add the following permissions.
            {
                "Effect": "Allow",
                "Action": [
                    "kms:Decrypt"
                ],
                "Resource": "<Your AWS KMS ARN>"
            }
            ,
            {
                "Effect": "Allow",
                "Action": "kms:Decrypt",
                "Resource": "<Your AWS KMS ARN>"
            }
        ]
    }
    ```

4. Configure the role. See [Creating an IAM role (console)](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user.html). In the Account ID field, enter the TiDB Cloud Account ID and TiDB Cloud External ID you have noted down in Step 1.

5. Get the Role-ARN. Go to [AWS Console > IAM > Access Management > Roles](https://console.aws.amazon.com/iamv2/home#/roles). Switch to your region. Click the role you have created, and note down the ARN. You will use it when importing data into TiDB Cloud.

6. Import data to TiDB Cloud. See [Import CSV Files from Cloud Storage into TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files).
