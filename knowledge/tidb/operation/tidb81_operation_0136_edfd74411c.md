# BR server-side encryption for S3 and Azure Blob backups

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/encryption-at-rest.md`
- Source Title: `Encryption at Rest`
- Source Heading Path: `Encryption at Rest > BR S3 server-side encryption | Encryption at Rest > BR Azure Blob Storage server-side encryption | Encryption at Rest > BR Azure Blob Storage server-side encryption > Method 1: use an encryption scope`
- Source Line Ranges: `399-446`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `tiup`, `shared`
- Topic Tags: `backup`, `restore`, `s3`, `azure-blob`, `server-side-encryption`, `kms`, `encryption-scope`, `iam`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0136_edfd74411c`
- Source ID: `tidb-docs-8.1:encryption-at-rest.md#br-s3-server-side-encryption`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3fb2e2831a551632637cc30599dba7c738070aee847baf99da812923a85fb7e0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/encryption-at-rest#br-s3-server-side-encryption
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/encryption-at-rest.md

## Retrieval Guidance

- Use When: Use this chunk when the request is about BR server-side encryption settings for backups to S3 or Azure Blob Storage, including `--s3.sse`, `--s3.sse-kms-key-id`, or Azure `encryption-scope` options and restore behavior.
- Retrieval Keywords: BR S3 server-side encryption, tiup br backup full, tiup br restore full, --s3.sse, aws:kms, --s3.sse-kms-key-id, custom AWS KMS CMK, same AWS region as the S3 bucket, AWS IAM, restore will fail, BR Azure Blob Storage server-side encryption, --azblob.encryption-scope, encryption-scope=scope1, Azure Blob Storage automatically decrypts the data
- Follow-up Guidance: The source also states that restore commands should not use `--s3.sse` or `--s3.sse-kms-key-id` for S3 backups, and that Azure Blob Storage restores do not need the encryption scope specified.
- Classification Note: This is classified as operation for the BR component because the content focuses on backup and restore command options for S3 and Azure Blob Storage server-side encryption.

## Official Source Content

## BR S3 server-side encryption

To enable S3 server-side encryption when backup to S3 using BR, pass `--s3.sse` argument and set value to "aws:kms". S3 will use its own KMS key for encryption. Example:

```
tiup br backup full --pd <pd-address> --storage "s3://<bucket>/<prefix>" --s3.sse aws:kms
```

To use a custom AWS KMS CMK that you created and owned, pass `--s3.sse-kms-key-id` in addition. In this case, both the BR process and all the TiKV nodes in the cluster would need access to the KMS CMK (for example, via AWS IAM), and the KMS CMK needs to be in the same AWS region as the S3 bucket used to store the backup. It is advised to grant access to the KMS CMK to BR process and TiKV nodes via AWS IAM. Refer to AWS documentation for usage of [IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html). For example:

```
tiup br backup full --pd <pd-address> --storage "s3://<bucket>/<prefix>" --s3.sse aws:kms --s3.sse-kms-key-id 0987dcba-09fe-87dc-65ba-ab0987654321
```

When restoring the backup, both `--s3.sse` and `--s3.sse-kms-key-id` should NOT be used. S3 will figure out encryption settings by itself. The BR process and TiKV nodes in the cluster to restore the backup to would also need access to the KMS CMK, or the restore will fail. Example:

```
tiup br restore full --pd <pd-address> --storage "s3://<bucket>/<prefix>"
```
## BR Azure Blob Storage server-side encryption

When backing up data to Azure Blob Storage using BR, you can specify either an encryption scope or an encryption key for server-side encryption.
### Method 1: use an encryption scope

To specify an encryption scope for the backup data, you can use one of the following two ways:

- Include the `--azblob.encryption-scope` option in the `backup` command and set it to the scope name:

    ```shell
    tiup br backup full --pd <pd-address> --storage "azure://<bucket>/<prefix>" --azblob.encryption-scope scope1
    ```

- Include `encryption-scope` in the URI and set it to the scope name:

    ```shell
    tiup br backup full --pd <pd-address> --storage "azure://<bucket>/<prefix>?encryption-scope=scope1"
    ```

For more information, see the Azure documentation: [Upload a blob with an encryption scope](https://learn.microsoft.com/en-us/azure/storage/blobs/encryption-scope-manage?tabs=powershell#upload-a-blob-with-an-encryption-scope).

When restoring the backup, you do not need to specify the encryption scope. Azure Blob Storage automatically decrypts the data. For example:

```shell
tiup br restore full --pd <pd-address> --storage "azure://<bucket>/<prefix>"
```
