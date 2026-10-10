# Troubleshoot S3 access denied from IAM policies and bucket permissions

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/troubleshoot-import-access-denied-error.md`
- Source Title: `Troubleshoot Access Denied Errors during Data Import from Amazon S3`
- Source Heading Path: `Troubleshoot Access Denied Errors during Data Import from Amazon S3 > Access denied | Troubleshoot Access Denied Errors during Data Import from Amazon S3 > Access denied > Check the policy of the IAM user | Troubleshoot Access Denied Errors during Data Import from Amazon S3 > Access denied > Check the policy of the IAM role | Troubleshoot Access Denied Errors during Data Import from Amazon S3 > Access denied > Check the bucket policy | Troubleshoot Access Denied Errors during Data Import from Amazon S3 > Access denied > Check the Object Ownership`
- Source Line Ranges: `59-199`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `s3`, `iam-user`, `iam-role`, `bucket-policy`, `object-ownership`, `kms`, `accessdenied`, `permissions`, `data-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0095_8b69e73680`
- Source ID: `tidb-docs-8.1:tidb-cloud/troubleshoot-import-access-denied-error.md#access-denied`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b20fd02a2789cfc88e714e54975694fed1021b3d08589190d186e3cc9afb412f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/troubleshoot-import-access-denied-error#access-denied
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/troubleshoot-import-access-denied-error.md

## Retrieval Guidance

- Use When: Use this content when data import from Amazon S3 in TiDB Cloud fails with AccessDenied and you need to check IAM user permissions, IAM role permissions, bucket policy, Object Ownership, or SSE-KMS access.
- Retrieval Keywords: Access denied, AccessDenied, s3:GetObject, s3:ListBucket, s3:GetBucketLocation, s3:GetObjectVersion, kms:Decrypt, Permission policies, Bucket policy, Object Ownership, Bucket owner enforced, Revoke active sessions, SSE-KMS, customer-managed key encryption, Resource fields, /*
- Follow-up Guidance: The content also notes checking denied bucket policies, ensuring Object Ownership is set to Bucket owner enforced, and including the correct KMS key resources when SSE-KMS with customer-managed keys is used.
- Classification Note: This chunk is classified as diagnosis because it details the permission-related causes of AccessDenied during S3 import and the exact IAM, bucket, and KMS settings to inspect.

## Official Source Content

## Access denied

This section describes how to troubleshoot access issues.
### Check the policy of the IAM user

When you use the AWS access key of an IAM user to access the Amazon S3 bucket, you might encounter the following error:

- "Access denied to the source '{bucket_uri}' using the access key ID '{access_key_id}' and the secret access key '{secret_access_key}'"

It indicates that TiDB Cloud failed to access the Amazon S3 bucket due to insufficient permissions. You need the following permissions to access the Amazon S3 bucket:

- `s3:GetObject`
- `s3:ListBucket`
- `s3:GetBucketLocation`

To check the policy of the IAM user, perform the following steps:

1. In the AWS Management Console, go to **IAM** > **Access Management** > **Users**.
2. In the list of users, find and click the user you have used for importing data to TiDB Cloud. The user summary page is displayed.
3. In the **Permission policies** area of the user summary page, a list of policies is displayed. Take the following steps for each policy:
    1. Click the policy to enter the policy summary page.
    2. On the policy summary page, click the **{}JSON** tab to check the permission policy. Make sure that the `Resource` fields in the policy are correctly configured.

The following is a sample policy:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::tidb-cloud-source-data/mydata/*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": "arn:aws:s3:::tidb-cloud-source-data"
        },
}
```

For more information about how to grant a user permissions and test them, see [Controlling access to a bucket with user policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/walkthrough1.html).
### Check the policy of the IAM role

1. In the AWS Management Console, go to **IAM** > **Access Management** > **Roles**. 
2. In the list of roles, find and click the role you have created for the target TiDB cluster. The role summary page is displayed.
3. In the **Permission policies** area of the role summary page, a list of policies is displayed. Take the following steps for each policy:
    1. Click the policy to enter the policy summary page.
    2. On the policy summary page, click the **{}JSON** tab to check the permission policy. Make sure that the `Resource` fields in the policy are correctly configured.

The following is a sample policy.

```
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
            "Resource": "arn:aws:s3:::tidb-cloud-source-data/mydata/*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": "arn:aws:s3:::tidb-cloud-source-data"
        },
        {
            "Sid": "AllowKMSkey",
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": "arn:aws:kms:ap-northeast-1:105880447796:key/c3046e91-fdfc-4f3a-acff-00597dd3801f"
        }
    ]
}
```

In this sample policy, pay attention to the following:

- In `"arn:aws:s3:::tidb-cloud-source-data/mydata/*"`, `"arn:aws:s3:::tidb-cloud-source-data"` is a sample S3 bucket ARN, and `/mydata/*` is a directory that you can customize in your S3 bucket root level for data storage. The directory needs to end with `/*`, for example, `"<Your S3 bucket ARN>/<Directory of your source data>/*"`. If `/*` is not added, the `AccessDenied` error occurs.

- If you have enabled AWS Key Management Service key (SSE-KMS) with customer-managed key encryption, make sure the following configuration is included in the policy. `"arn:aws:kms:ap-northeast-1:105880447796:key/c3046e91-fdfc-4f3a-acff-00597dd3801f"` is a sample KMS key of the bucket.

    ```
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

If your policy is not correctly configured as the preceding example shows, correct the `Resource` fields in your policy and try importing data again.

> **Tip:**
>
> If you have updated the permission policy multiple times and still get the `AccessDenied` error during data import, you can try to revoke active sessions. Go to **IAM** > **Access Management** > **Roles**, click your target role to enter the role summary page. On the role summary page, find **Revoke active sessions** and click the button to revoke active sessions. Then, retry the data import.
>
> Note that this might affect your other applications.
### Check the bucket policy

1. In the AWS Management Console, open the Amazon S3 console, and then go to the **Buckets** page. A list of buckets is displayed.
2. In the list, find and click the target bucket. The bucket information page is displayed.
3. Click the **Permissions** tab, and then scroll down to the **Bucket policy** area. By default, this area has no policy value. If any denied policy is displayed in this area, the `AccessDenied` error might occur during data import.

If you see a denied policy, check whether the policy relates to the current data import. If yes, delete it from the area and retry the data import.
### Check the Object Ownership

1. In the AWS Management Console, open the Amazon S3 console, and then go to the **Buckets** page. A list of buckets is displayed.
2. In the list of buckets, find and click the target bucket. The bucket information page is displayed.
3. On the bucket information page, click the **Permissions** tab, and then scroll down to the **Object Ownership** area. Make sure that the "Object Ownership" configuration is "Bucket owner enforced".

    If the configuration is not "Bucket owner enforced", the `AccessDenied` error occurs, because your account does not have enough permissions for all objects in this bucket.

To handle the error, click **Edit** in the upper-right corner of the Object Ownership area and change the ownership to "Bucket owner enforced". Note that this might affect your other applications that are using this bucket.
