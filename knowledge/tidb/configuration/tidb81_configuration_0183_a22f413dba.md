# Configure TiCDC sink URIs for cloud storage and NFS

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-cloud-storage.md`
- Source Title: `Replicate Data to Storage Services`
- Source Heading Path: `Replicate Data to Storage Services > Configure sink URI | Replicate Data to Storage Services > Configure sink URI > Configure sink URI for external storage | Replicate Data to Storage Services > Configure sink URI > Configure sink URI for NFS`
- Source Line Ranges: `37-150`
- Source Scope: `cloud`
- Primary Component: `ticdc`
- Related Components: `cloud`
- Topic Tags: `sink-uri`, `s3`, `gcs`, `azure-blob`, `nfs`, `authentication`, `permissions`, `protocol`, `flush-interval`, `file-size`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0183_a22f413dba`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-cloud-storage.md#configure-sink-uri`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `75ccca8218452951045b41aacfe0581fb13cac1080ae607f4bdc5218b621a389`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-cloud-storage#configure-sink-uri
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-cloud-storage.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Sink URI format, supported query parameters, authentication methods, or example URIs for Amazon S3, GCS, Azure Blob Storage, or NFS in TiCDC.
- Retrieval Keywords: Configure sink URI, [scheme]://[host]/[path]?[query_parameters], worker-count, flush-interval, file-size, protocol, enable-tidb-extension, CDC:ErrSinkUnknownProtocol, s3://bucket/prefix?protocol=canal-json, gcs://bucket/prefix?protocol=canal-json, azure://bucket/prefix?protocol=canal-json, file:///my-directory/prefix?protocol=canal-json, s3:ListBucket, s3:PutObject, s3:GetObject, s3:AbortMultipartUpload, s3:ListMultipartUploadParts, s3:ListBucketMultipartUploads, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_SHARED_CREDENTIALS_FILE, GOOGLE_APPLICATION_CREDENTIALS, AZURE_STORAGE_KEY, AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, credentials-file, account-name, sas-token, account-key
- Follow-up Guidance: This chunk refers to URI Formats of External Storage Services for more information about URI parameters of Amazon S3, GCS, and Azure Blob Storage in TiCDC.
- Classification Note: The classification is configuration because the content defines Sink URI syntax, query parameters, provider-specific authentication settings, and example URI values.

## Official Source Content

## Configure sink URI

This section describes how to configure Sink URI for storage services, including Amazon S3, GCS, Azure Blob Storage, and NFS. Sink URI is used to specify the connection information of the TiCDC target system. The format is as follows:

```shell
[scheme]://[host]/[path]?[query_parameters]
```

For `[query_parameters]` in the URI, the following parameters can be configured:

| Parameter | Description | Default value | Value range |
| :---------| :---------- | :------------ | :---------- |
| `worker-count` | Concurrency for saving data changes to cloud storage in the downstream.  | `16` | `[1, 512]` |
| `flush-interval` | Interval for saving data changes to cloud storage in the downstream.   | `5s` | `[2s, 10m]` |
| `file-size` | A data change file is stored to cloud storage if the number of bytes exceeds the value of this parameter. | `67108864` | `[1048576, 536870912]` |
| `protocol` | The protocol format of the messages sent to the downstream.  | N/A |  `canal-json` and `csv` |
| `enable-tidb-extension` | When `protocol` is set to `canal-json` and `enable-tidb-extension` is set to `true`, TiCDC sends [WATERMARK events](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-canal-json#watermark-event) and adds the [TiDB extension field](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-canal-json#tidb-extension-field) to Canal-JSON messages. | `false` | `false` and `true` |

> **Note:**
>
> Data change files are saved to the downstream when either `flush-interval` or `file-size` meets the requirements.
> The `protocol` parameter is mandatory. If TiCDC does not receive this parameter when creating a changefeed, the `CDC:ErrSinkUnknownProtocol` error is returned.
### Configure sink URI for external storage

When storing data in a cloud storage system, you need to set different authentication parameters depending on the cloud service provider. This section describes the authentication methods when using Amazon S3, Google Cloud Storage (GCS), and Azure Blob Storage, and how to configure accounts to access the corresponding storage services.

<div label="Amazon S3" value="amazon">

The following is an example configuration for Amazon S3:

```shell
--sink-uri="s3://bucket/prefix?protocol=canal-json"
```

Before replicating data, you need to set appropriate access permissions for the directory in Amazon S3:

- Minimum permissions required by TiCDC: `s3:ListBucket`, `s3:PutObject`, and `s3:GetObject`.
- If the changefeed configuration item `sink.cloud-storage-config.flush-concurrency` is greater than 1, which means parallel uploading of single files is enabled, you need to additionally add permissions related to [ListParts](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListParts.html):
    - `s3:AbortMultipartUpload`
    - `s3:ListMultipartUploadParts`
    - `s3:ListBucketMultipartUploads`

If you have not created a replication data storage directory, refer to [Create a bucket](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-bucket.html) to create an S3 bucket in the specified region. If necessary, you can also create a folder in the bucket by referring to [Organize objects in the Amazon S3 console by using folders](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-folder.html).

You can configure an account to access Amazon S3 in the following ways:

- Method 1: Specify the access key

    If you specify an access key and a secret access key, authentication is performed according to them. In addition to specifying the key in the URI, the following methods are supported:

    - TiCDC reads the `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY` environment variables.
    - TiCDC reads the `$AWS_ACCESS_KEY` and `$AWS_SECRET_KEY` environment variables.
    - TiCDC reads the shared credentials file in the path specified by the `$AWS_SHARED_CREDENTIALS_FILE` environment variable.
    - TiCDC reads the shared credentials file in the `~/.aws/credentials` path.

- Method 2: Access based on an IAM role

    Associate an [IAM role with configured permissions to access Amazon S3](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2.html) to the EC2 instance running the TiCDC server. After successful setup, TiCDC can directly access the corresponding directories in Amazon S3 without additional settings.

</div>
<div label="GCS" value="gcs">

The following is an example configuration for GCS:

```shell
--sink-uri="gcs://bucket/prefix?protocol=canal-json"
```

You can configure the account used to access GCS by specifying an access key. Authentication is performed according to the specified `credentials-file`. In addition to specifying the key in the URI, the following methods are supported:

- TiCDC reads the file in the path specified by the `$GOOGLE_APPLICATION_CREDENTIALS` environment variable.
- TiCDC reads the file `~/.config/gcloud/application_default_credentials.json`.
- TiCDC obtains credentials from the metadata server when the cluster is running in GCE or GAE.

</div>
<div label="Azure Blob Storage" value="azure">

The following is an example configuration for Azure Blob Storage:

```shell
--sink-uri="azure://bucket/prefix?protocol=canal-json"
```

You can configure an account to access Azure Blob Storage in the following ways:

- Method 1: Specify a shared access signature

    If you configure `account-name` and `sas-token` in the URI, the storage account name and shared access signature token specified by this parameter are used. Because the shared access signature token has the `&` character, you need to encode it as `%26` before adding it to the URI. You can also directly encode the entire `sas-token` using percent-encoding.

- Method 2: Specify the access key

    If you configure `account-name` and `account-key` in the URI, the storage account name and key specified by this parameter are used. In addition to specifying the key file in the URI, TiCDC can also read the key from the environment variable `$AZURE_STORAGE_KEY`.

- Method 3: Use Azure AD to restore the backup

    Configure the environment variables `$AZURE_CLIENT_ID`, `$AZURE_TENANT_ID`, and `$AZURE_CLIENT_SECRET`.

</div>

> **Tip:**
>
> For more information about the URI parameters of Amazon S3, GCS, and Azure Blob Storage in TiCDC, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).
### Configure sink URI for NFS

The following is an example configuration for NFS:

```shell
--sink-uri="file:///my-directory/prefix?protocol=canal-json"
```
