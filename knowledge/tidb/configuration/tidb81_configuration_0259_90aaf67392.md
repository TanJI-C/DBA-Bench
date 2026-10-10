# TiDB Cloud Serverless external storage overview and S3 access methods

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-external-storage.md`
- Source Title: `Configure TiDB Cloud Serverless External Storage Access`
- Source Heading Path: `Configure External Storage Access for TiDB Cloud Serverless | Configure External Storage Access for TiDB Cloud Serverless > Configure Amazon S3 access`
- Source Line Ranges: `5-18`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `external-storage`, `cross-account-access`, `s3`, `import`, `export`, `serverless`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0259_90aaf67392`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-external-storage.md#configure-external-storage-access-for-tidb-cloud-serverless`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2767009f20a7b0b0901eaa8897b6d957dc90e9beb054a347c771ca7480cad064`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-external-storage-access-for-tidb-cloud-serverless
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-external-storage.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how TiDB Cloud Serverless accesses external storage for import or export, especially Amazon S3 cross-account access methods.
- Retrieval Keywords: Configure External Storage Access for TiDB Cloud Serverless, Configure Amazon S3 access, cross-account access, import data from external storage, export data to external storage, TiDB Cloud Serverless, Use a Role ARN, Use an AWS access key
- Follow-up Guidance: For Amazon S3 access, the source points to either configuring access using a Role ARN or using an AWS access key.
- Classification Note: This is configuration content because it introduces the required cross-account access setup and the two supported Amazon S3 access methods for TiDB Cloud Serverless.

## Official Source Content

# Configure External Storage Access for TiDB Cloud Serverless

If you want to import data from or export data to an external storage in a TiDB Cloud Serverless cluster, you need to configure cross-account access. This document describes how to configure access to an external storage for TiDB Cloud Serverless clusters.

If you need to configure these external storages for a TiDB Cloud Dedicated cluster, see [Configure External Storage Access for TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage).
## Configure Amazon S3 access

To allow a TiDB Cloud Serverless cluster to access the source data in your Amazon S3 bucket, configure the bucket access for the cluster using either of the following methods:

- [Use a Role ARN](#configure-amazon-s3-access-using-a-role-arn): use a Role ARN to access your Amazon S3 bucket.
- [Use an AWS access key](#configure-amazon-s3-access-using-an-aws-access-key): use the access key of an IAM user to access your Amazon S3 bucket.
