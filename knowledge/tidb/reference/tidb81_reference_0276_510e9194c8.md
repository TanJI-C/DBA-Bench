# External storage URI formats for S3, GCS, and Azure Blob Storage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/external-storage-uri.md`
- Source Title: `URI Formats of External Storage Services`
- Source Heading Path: `URI Formats of External Storage Services | Amazon S3 URI format | GCS URI format | Azure Blob Storage URI format`
- Source Line Ranges: `5-132`
- Source Scope: `all`
- Primary Component: `shared`
- Related Components: `br`, `lightning`, `ticdc`, `sql`, `cloud`
- Topic Tags: `external-storage`, `uri-format`, `s3`, `gcs`, `azure-blob`, `credentials`, `query-parameters`, `backup`, `restore`, `import`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0276_510e9194c8`
- Source ID: `tidb-docs-8.1:external-storage-uri.md#uri-formats-of-external-storage-services`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `68fdb6d92a71db138c73145fc16cad6312f91a874a11c941f0d1d0175504fe61`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/external-storage-uri#uri-formats-of-external-storage-services
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/external-storage-uri.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the external storage URI format and supported query parameters for Amazon S3, GCS, or Azure Blob Storage in TiDB tools and SQL features.
- Retrieval Keywords: [scheme]://[host]/[path]?[parameters], Amazon S3 URI format, GCS URI format, Azure Blob Storage URI format, s3://external/testfolder?access-key=${access-key}&secret-access-key=${secret-access-key}, gcs://external/testfolder?credentials-file=${credentials-file-path}, gcs://external/test.csv?credentials-file=${credentials-file-path}, azure://external/testfolder?account-name=${account-name}&account-key=${account-key}, sink-uri, BACKUP, RESTORE, IMPORT INTO, access-key, secret-access-key, session-token, use-accelerate-endpoint, endpoint, force-path-style, storage-class, sse, sse-kms-key-id, acl, role-arn, external-id, credentials-file, predefined-acl, account-name, account-key, sas-token, access-tier, encryption-scope, encryption-key
- Follow-up Guidance: The chunk includes concrete URI examples for TiDB Lightning, BR, TiCDC sink-uri, BACKUP, RESTORE, and IMPORT INTO using S3, GCS, and Azure Blob Storage.
- Classification Note: This is reference content because it enumerates URI schemes, hosts, parameters, and example URIs for external storage services.

## Official Source Content

## URI Formats of External Storage Services

This document describes the URI formats of external storage services, including Amazon S3, GCS, and Azure Blob Storage.

The basic format of the URI is as follows:

```shell
[scheme]://[host]/[path]?[parameters]
```
## Amazon S3 URI format

- `scheme`: `s3`
- `host`: `bucket name`
- `parameters`:

    - `access-key`: Specifies the access key.
    - `secret-access-key`: Specifies the secret access key.
    - `session-token`: Specifies the temporary session token. BR supports this parameter starting from v7.6.0.
    - `use-accelerate-endpoint`: Specifies whether to use the accelerate endpoint on Amazon S3 (defaults to `false`).
    - `endpoint`: Specifies the URL of custom endpoint for S3-compatible services (for example, `<https://s3.example.com/>`).
    - `force-path-style`: Use path style access rather than virtual hosted style access (defaults to `true`).
    - `storage-class`: Specifies the storage class of the uploaded objects (for example, `STANDARD` or `STANDARD_IA`).
    - `sse`: Specifies the server-side encryption algorithm used to encrypt the uploaded objects (value options: empty, `AES256`, or `aws:kms`).
    - `sse-kms-key-id`: Specifies the KMS ID if `sse` is set to `aws:kms`.
    - `acl`: Specifies the canned ACL of the uploaded objects (for example, `private` or `authenticated-read`).
    - `role-arn`: When you need to access Amazon S3 data from a third party using a specified [IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html), you can specify the corresponding [Amazon Resource Name (ARN)](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html) of the IAM role with the `role-arn` URL query parameter, such as `arn:aws:iam::888888888888:role/my-role`. For more information about using an IAM role to access Amazon S3 data from a third party, see [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_third-party.html). BR supports this parameter starting from v7.6.0.
    - `external-id`: When you access Amazon S3 data from a third party, you might need to specify a correct [external ID](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html) to assume [the IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html). In this case, you can use this `external-id` URL query parameter to specify the external ID and make sure that you can assume the IAM role. An external ID is an arbitrary string provided by the third party together with the IAM role ARN to access the Amazon S3 data. Providing an external ID is optional when assuming an IAM role, which means if the third party does not require an external ID for the IAM role, you can assume the IAM role and access the corresponding Amazon S3 data without providing this parameter.

The following is an example of an Amazon S3 URI for TiDB Lightning and BR. In this example, you need to specify a specific file path `testfolder`.

```shell
s3://external/testfolder?access-key=${access-key}&secret-access-key=${secret-access-key}
```

The following is an example of an Amazon S3 URI for TiCDC `sink-uri`.

```shell
tiup cdc:v7.5.0 cli changefeed create \
    --server=http://172.16.201.18:8300 \
    --sink-uri="s3://cdc?endpoint=http://10.240.0.38:9000&access-key=${access-key}&secret-access-key=${secret-access-key}" \
    --changefeed-id="cdcTest" \
    --config=cdc_csv.toml
```

- `scheme`: `s3`
- `host`: `bucket name`
- `parameters`:

    - `access-key`: Specifies the access key.
    - `secret-access-key`: Specifies the secret access key.
    - `session-token`: Specifies the temporary session token.
    - `use-accelerate-endpoint`: Specifies whether to use the accelerate endpoint on Amazon S3 (defaults to `false`).
    - `endpoint`: Specifies the URL of custom endpoint for S3-compatible services (for example, `<https://s3.example.com/>`).
    - `force-path-style`: Use path style access rather than virtual hosted style access (defaults to `true`).
    - `storage-class`: Specifies the storage class of the uploaded objects (for example, `STANDARD` or `STANDARD_IA`).
    - `sse`: Specifies the server-side encryption algorithm used to encrypt the uploaded objects (value options: empty, `AES256`, or `aws:kms`).
    - `sse-kms-key-id`: Specifies the KMS ID if `sse` is set to `aws:kms`.
    - `acl`: Specifies the canned ACL of the uploaded objects (for example, `private` or `authenticated-read`).
    - `role-arn`: To allow TiDB Cloud to access Amazon S3 data using a specific [IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html), provide the role's [Amazon Resource Name (ARN)](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html) in the `role-arn` URL query parameter. For example: `arn:aws:iam::888888888888:role/my-role`. 

        > **Note:**
        >
        > - To automatically create an IAM role, navigate to the **Import Data from Amazon S3** page of your cluster in the [TiDB Cloud console](https://tidbcloud.com/), fill in the **Folder URI** field, click **Click here to create new one with AWS CloudFormation** under the **Role ARN** field, and then follow the on-screen instructions in the **Add New Role ARN** dialog.
        > - If you have any trouble creating the IAM role using AWS CloudFormation, click **click Having trouble? Create Role ARN manually** in the **Add New Role ARN** dialog to get the TiDB Cloud Account ID and TiDB Cloud External ID, and then follow the steps in [Configure Amazon S3 access using a Role ARN](https://docs.pingcap.com/tidbcloud/dedicated-external-storage#configure-amazon-s3-access-using-a-role-arn) to create the role manually. When configuring the IAM role, make sure to enter the TiDB Cloud account ID in the **Account ID** field and select **Require external ID** to protect against [confused deputy attacks](https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html).
        > - To enhance security, you can reduce the valid duration of the IAM role by configuring a shorter **Max session duration**. For more information, see [Update the maximum session duration for a role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_update-role-settings.html#id_roles_update-session-duration) in AWS documentation.

    - `external-id`: Specifies the TiDB Cloud External ID, which is required for TiDB Cloud to access Amazon S3 data. You can obtain this ID from the **Add New Role ARN** dialog in the [TiDB Cloud console](https://tidbcloud.com/). For more information, see [Configure Amazon S3 access using a Role ARN](https://docs.pingcap.com/tidbcloud/dedicated-external-storage#configure-amazon-s3-access-using-a-role-arn).

The following is an example of an Amazon S3 URI for [`BACKUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-backup) and [`RESTORE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-restore). This example uses the file path `testfolder`.

```shell
s3://external/testfolder?access-key=${access-key}&secret-access-key=${secret-access-key}
```
## GCS URI format

- `scheme`: `gcs` or `gs`
- `host`: `bucket name`
- `parameters`:

    - `credentials-file`: Specifies the path to the credentials JSON file on the migration tool node.
    - `storage-class`: Specifies the storage class of the uploaded objects (for example, `STANDARD` or `COLDLINE`)
    - `predefined-acl`: Specifies the predefined ACL of the uploaded objects (for example, `private` or `project-private`)

The following is an example of a GCS URI for TiDB Lightning and BR. In this example, you need to specify a specific file path `testfolder`.

```shell
gcs://external/testfolder?credentials-file=${credentials-file-path}
```

The following is an example of a GCS URI for [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into). In this example, you need to specify a specific filename `test.csv`.

```shell
gcs://external/test.csv?credentials-file=${credentials-file-path}
```
## Azure Blob Storage URI format

- `scheme`: `azure` or `azblob`
- `host`: `container name`
- `parameters`:

    - `account-name`: Specifies the account name of the storage.
    - `account-key`: Specifies the access key.
    - `sas-token`: Specifies the shared access signature (SAS) token.
    - `access-tier`: Specifies the access tier of the uploaded objects, for example, `Hot`, `Cool`, or `Archive`. The default value is the default access tier of the storage account.
    - `encryption-scope`: Specifies the [encryption scope](https://learn.microsoft.com/en-us/azure/storage/blobs/encryption-scope-manage?tabs=powershell#upload-a-blob-with-an-encryption-scope) for server-side encryption.
    - `encryption-key`: Specifies the [encryption key](https://learn.microsoft.com/en-us/azure/storage/blobs/encryption-customer-provided-keys) for server-side encryption, which uses the AES256 encryption algorithm.

The following is an example of an Azure Blob Storage URI for BR. In this example, you need to specify a specific file path `testfolder`.

```shell
azure://external/testfolder?account-name=${account-name}&account-key=${account-key}
```
