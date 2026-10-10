# BR Azure Blob Storage server-side encryption with encryption key

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/encryption-at-rest.md`
- Source Title: `Encryption at Rest`
- Source Heading Path: `Encryption at Rest > BR Azure Blob Storage server-side encryption > Method 2: use an encryption key`
- Source Line Ranges: `447-491`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tiup`, `pd`
- Topic Tags: `azure blob storage`, `server-side encryption`, `encryption key`, `backup`, `restore`, `environment variables`, `uri parameters`, `aes256`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0109_1fc85086d7`
- Source ID: `tidb-docs-8.1:encryption-at-rest.md#method-2-use-an-encryption-key`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7693a6b50ae65fe92ca8b270478ae474291d6c40496a40bd609ea27615efd8ba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/encryption-at-rest#method-2-use-an-encryption-key
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/encryption-at-rest.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how BR specifies an Azure Blob Storage server-side encryption key for backup or restore using a command option, URI parameter, or environment variable.
- Retrieval Keywords: BR Azure Blob Storage server-side encryption, Method 2: use an encryption key, --azblob.encryption-key, encryption-key, AZURE_ENCRYPTION_KEY, AES256 encryption key, tiup br backup full, tiup br restore full, azure://<bucket>/<prefix>, Provide an encryption key on a request to Blob storage
- Follow-up Guidance: The same AES256 encryption key must be specified again when restoring the backup, using --azblob.encryption-key, the encryption-key URI parameter, or the AZURE_ENCRYPTION_KEY environment variable.
- Classification Note: This is classified as configuration because the content defines exact BR backup and restore parameters and environment variables for Azure Blob Storage server-side encryption with a customer-provided AES256 key.

## Official Source Content

### Method 2: use an encryption key

To specify an encryption key for the backup data, you can use one of the following three ways:

- Include the `--azblob.encryption-key` option in the `backup` command and set it to an AES256 encryption key:

    ```shell
    tiup br backup full --pd <pd-address> --storage "azure://<bucket>/<prefix>" --azblob.encryption-key <aes256-key>
    ```

- Include `encryption-key` in the URI and set it to an AES256 encryption key. If the key contains URI reserved characters such as `&` and `%`, you need to percent-encode it first:

    ```shell
    tiup br backup full --pd <pd-address> --storage "azure://<bucket>/<prefix>?encryption-key=<aes256-key>"
    ```

- Set the `AZURE_ENCRYPTION_KEY` environment variable to an AES256 encryption key. Before running, make sure that you remember the encryption key in the environment variable to avoid forgetting it.

    ```shell
    export AZURE_ENCRYPTION_KEY=<aes256-key>
    tiup br backup full --pd <pd-address> --storage "azure://<bucket>/<prefix>"
    ```

For more information, see the Azure documentation: [Provide an encryption key on a request to Blob storage](https://learn.microsoft.com/en-us/azure/storage/blobs/encryption-customer-provided-keys).

When restoring the backup, you need to specify the encryption key. For example:

- Include the `--azblob.encryption-key` option in the `restore` command:

    ```shell
    tiup br restore full --pd <pd-address> --storage "azure://<bucket>/<prefix>" --azblob.encryption-key <aes256-key>
    ```

- Include `encryption-key` in the URI:

    ```shell
    tiup br restore full --pd <pd-address> --storage "azure://<bucket>/<prefix>?encryption-key=<aes256-key>"
    ```

- Set the `AZURE_ENCRYPTION_KEY` environment variable:

    ```shell
    export AZURE_ENCRYPTION_KEY=<aes256-key>
    tiup br restore full --pd <pd-address> --storage "azure://<bucket>/<prefix>"
    ```
