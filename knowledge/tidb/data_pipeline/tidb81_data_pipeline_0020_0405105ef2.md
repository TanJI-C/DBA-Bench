# Export Dumpling output to Amazon S3

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dumpling-overview.md`
- Source Title: `Dumpling Overview`
- Source Heading Path: `Use Dumpling to Export Data > Export data from TiDB or MySQL > Export data to Amazon S3 cloud storage`
- Source Line Ranges: `224-244`
- Source Scope: `shared`
- Primary Component: `dumpling`
- Related Components: `cloud`
- Topic Tags: `s3`, `cloud-storage`, `credentials`, `output-path`, `export`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0020_0405105ef2`
- Source ID: `tidb-docs-8.1:dumpling-overview.md#export-data-to-amazon-s3-cloud-storage`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c1f1bcdc17b3a0cd5bd0b9f9e448a202eaf88c58eb5b3affcc6d5cff08f602b1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dumpling-overview#export-data-to-amazon-s3-cloud-storage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dumpling-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the official Dumpling syntax and credential methods for exporting dump output to Amazon S3 cloud storage.
- Retrieval Keywords: Amazon S3, S3 bucket, -o "s3://${Bucket}/${Folder}", AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ~/.aws/credentials, Export data to Amazon S3 cloud storage, URI Formats of External Storage Services, tiup dumpling
- Follow-up Guidance: The source also points to URI parameter descriptions in URI Formats of External Storage Services and shows that Dumpling supports reading credentials from ~/.aws/credentials.
- Classification Note: This is classified as a data_pipeline chunk because the content describes directing Dumpling export output to cloud storage using an S3 path and credentials.

## Official Source Content

### Export data to Amazon S3 cloud storage

Starting from v4.0.8, Dumpling supports exporting data to cloud storages. If you need to back up data to Amazon S3, you need to specify the Amazon S3 storage path in the `-o` parameter.

You need to create an Amazon S3 bucket in the specified region (see the [Amazon documentation - How do I create an S3 Bucket](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-bucket.html)). If you also need to create a folder in the bucket, see the [Amazon documentation - Creating a folder](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-folder.html).

Pass `SecretKey` and `AccessKey` of the account with the permission to access the Amazon S3 backend storage to the Dumpling node as environment variables.

```shell
export AWS_ACCESS_KEY_ID=${AccessKey}
export AWS_SECRET_ACCESS_KEY=${SecretKey}
```

Dumpling also supports reading credential files from `~/.aws/credentials`. For more information about URI parameter descriptions, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

```shell
tiup dumpling -u root -P 4000 -h 127.0.0.1 -r 200000 -o "s3://${Bucket}/${Folder}"
```
