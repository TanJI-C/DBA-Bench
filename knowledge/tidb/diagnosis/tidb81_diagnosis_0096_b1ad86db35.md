# S3 access denied checks for bucket encryption and AWS guidance

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/troubleshoot-import-access-denied-error.md`
- Source Title: `Troubleshoot Access Denied Errors during Data Import from Amazon S3`
- Source Heading Path: `Troubleshoot Access Denied Errors during Data Import from Amazon S3 > Access denied > Check your bucket encryption type | Troubleshoot Access Denied Errors during Data Import from Amazon S3 > Access denied > Check the AWS article for instruction`
- Source Line Ranges: `200-236`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `s3-import`, `accessdenied`, `iam-role`, `bucket-encryption`, `sse-s3`, `sse-kms`, `kms-key`, `cross-account`, `bucket-objects`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0096_b1ad86db35`
- Source ID: `tidb-docs-8.1:tidb-cloud/troubleshoot-import-access-denied-error.md#check-your-bucket-encryption-type`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1f0f0a3858c7be21b422c275f991ce6f80fdc1f55dc53f5e4ee52d7cd57bca78`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/troubleshoot-import-access-denied-error#check-your-bucket-encryption-type
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/troubleshoot-import-access-denied-error.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting an Amazon S3 `AccessDenied` or 403 error during TiDB Cloud data import and you need bucket encryption checks involving SSE-S3, SSE-KMS, KMS key ARN type, or cross-account access guidance.
- Retrieval Keywords: AccessDenied, 403 Access Denied, Amazon S3, TiDB Cloud import, bucket encryption type, Default encryption, server-side encryption, SSE-S3, SSE-KMS, AWS KMS key ARN, aws/s3, AWS-managed key, customer-managed key, cross-account access denied, Key users, bucket objects copied from encrypted bucket, Using default encryption with replication, How do I troubleshoot 403 Access Denied errors from Amazon S3
- Follow-up Guidance: If all listed checks still do not resolve the `AccessDenied` error, the source points to the AWS article "How do I troubleshoot 403 Access Denied errors from Amazon S3" for more instruction.
- Classification Note: The content is classified as diagnosis because it explains how to inspect S3 bucket encryption and KMS key type to determine causes of `AccessDenied` errors during data import.

## Official Source Content

### Check your bucket encryption type

There are more than one way to encrypt an S3 bucket. When you try to access the objects in a bucket, the role you have created must have the permission to access the encryption key for data decryption. Otherwise, the `AccessDenied` error occurs.

To check the encryption type of your bucket, take the following steps:

1. In the AWS Management Console, open the Amazon S3 console, and then go to the **Buckets** page. A list of buckets is displayed.
2. In the list of buckets, find and click the target bucket. The bucket information page is displayed.
3. On the bucket information page, click the **Properties** tab, scroll down to the **Default encryption** area, and then check the configurations in this area.

There are two types of server-side encryption: Amazon S3-managed key (SSE-S3) and AWS Key Management Service (SSE-KMS). For SSE-S3, further check is not needed because this encryption type does not cause access denied errors. For SSE-KMS, you need to check the following:

- If the AWS KMS key ARN in the area is displayed in black without an underline, the AWS KMS key is an AWS-managed key (aws/s3).
- If the AWS KMS key ARN in the area is displayed in blue with a link, click the key ARN to open the key information page. Check the left navigation bar to see the specific encryption type. It might be an AWS managed key (aws/s3) or a customer managed key.

<details>
<summary>For the AWS managed key (aws/s3) in SSE-KMS</summary>

In this situation, if the `AccessDenied` error occurs, the reason might be that the key is read-only and cross-account permission grants are not allowed. See the AWS article [Why are cross-account users getting Access Denied errors when they try to access S3 objects encrypted by a custom AWS KMS key](https://aws.amazon.com/premiumsupport/knowledge-center/cross-account-access-denied-error-s3/) for details.

To solve the access denied error, click **Edit** in the upper-right corner of the **Default encryption** area, and change the AWS KMS key to "Choose from your AWS KMS keys" or "Enter AWS KMS key ARN", or change the server-side encryption type to "AWS S3 Managed Key (SSE-S3). In addition to this method, you can also create a new bucket and use the custom-managed key or the SSE-S3 encryption method.
</details>

<details>
<summary>For the customer-managed key in SSE-KMS</summary>

To solve the `AccessDenied` error in this situation, click the key ARN or manually find the key in KMS. A **Key users** page is displayed. Click **Add** in the upper-right corner of the area to add the role you have used to import data to TiDB Cloud. Then, try importing data again.

</details>

> **Note:**
>
> If the objects in your bucket have been copied from an existing encrypted bucket, you also need to include the key of the source bucket in the AWS KMS key ARN. This is because the objects in your bucket use the same encryption method as the source object encryption. For more information, see the AWS document [Using default encryption with replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html).
### Check the AWS article for instruction

If you have performed all the checks above and still get the `AccessDenied` error, you can check the AWS article [How do I troubleshoot 403 Access Denied errors from Amazon S3](https://aws.amazon.com/premiumsupport/knowledge-center/s3-troubleshoot-403/) for more instruction.
