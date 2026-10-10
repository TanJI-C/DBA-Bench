# Configure Amazon S3 access for TiDB Cloud Serverless using an AWS access key

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-external-storage.md`
- Source Title: `Configure TiDB Cloud Serverless External Storage Access`
- Source Heading Path: `Configure External Storage Access for TiDB Cloud Serverless > Configure Amazon S3 access > Configure Amazon S3 access using an AWS access key`
- Source Line Ranges: `165-180`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `s3`, `aws-access-key`, `iam-user`, `credentials`, `import`, `export`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0261_25475ecdec`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-external-storage.md#configure-amazon-s3-access-using-an-aws-access-key`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `20033a4c7b3875f97e3b5df2f2b1348ba5d4c84bf2c2721212e51bb4d60be329`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-amazon-s3-access-using-an-aws-access-key
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-external-storage.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how to configure Amazon S3 access for TiDB Cloud Serverless using an AWS access key or asks about IAM user access keys for import and export.
- Retrieval Keywords: Configure Amazon S3 access using an AWS access key, AWS access key, IAM user, IAM console, creating an IAM user, creating an access key for an IAM user, TiDB Cloud does not store your access keys, delete the access key after the import or export is complete
- Follow-up Guidance: The source states that TiDB Cloud does not store access keys and notes that deleting the access key after the import or export is complete is recommended.
- Classification Note: This is configuration content because it describes the access-key-based setup path for Amazon S3 using an IAM user and the related credential handling note.

## Official Source Content

### Configure Amazon S3 access using an AWS access key

It is recommended that you use an IAM user (instead of the AWS account root user) to create an access key.

Take the following steps to configure an access key:

1. Create an IAM user. For more information, see [creating an IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console).

2. Use your AWS account ID or account alias, and your IAM user name and password to sign in to [the IAM console](https://console.aws.amazon.com/iam).

3. Create an access key. For more information, see [creating an access key for an IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey).

> **Note:**
>
> TiDB Cloud does not store your access keys. It is recommended that you [delete the access key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey) after the import or export is complete.
