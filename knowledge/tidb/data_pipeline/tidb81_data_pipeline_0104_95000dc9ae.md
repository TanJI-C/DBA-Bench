# Serverless export overview and destination requirements

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-export.md`
- Source Title: `Export Data from TiDB Cloud Serverless`
- Source Heading Path: `Export Data from TiDB Cloud Serverless | Export Data from TiDB Cloud Serverless > Export locations | Export Data from TiDB Cloud Serverless > Export locations > A local file | Export Data from TiDB Cloud Serverless > Export locations > Amazon S3 | Export Data from TiDB Cloud Serverless > Export locations > Google Cloud Storage | Export Data from TiDB Cloud Serverless > Export locations > Azure Blob Storage | Export Data from TiDB Cloud Serverless > Export locations > Alibaba Cloud OSS`
- Source Line Ranges: `5-83`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dumpling`, `shared`
- Topic Tags: `export`, `serverless`, `storage-destination`, `local-file`, `s3`, `gcs`, `azure-blob`, `alibaba-oss`, `credentials`, `permissions`, `limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0104_95000dc9ae`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-export.md#export-data-from-tidb-cloud-serverless`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `018ebe9b229f6cbf09ad189096ed293fb2f951c49b4b628c85a1c7bac104130d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-export#export-data-from-tidb-cloud-serverless
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-export.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Cloud Serverless Export destinations, export size and location limits, or the required URI and credentials for local file, Amazon S3, Google Cloud Storage, Azure Blob Storage, or Alibaba Cloud OSS.
- Retrieval Keywords: TiDB Cloud Serverless Export (Beta), maximum export size 1 TiB, export more than 100 GiB external storage, local file, stashing area, expire after two days, Downloading exported data using the TiDB Cloud console is not supported, Amazon S3, s3://<bucket-name>/<folder-path>/, s3:PutObject, s3:ListBucket, role ARN, only clusters hosted on AWS support the role ARN, Google Cloud Storage, gs://<bucket-name>/<folder-path>/, base64 encoded service account key, storage.objects.create, Azure Blob Storage, azure://<account-name>.blob.core.windows.net/<container-name>/<folder-path>/, https://<account-name>.blob.core.windows.net/<container-name>/<folder-path>/, shared access signature (SAS) token, Read and Write permissions, Container and Object resources, Alibaba Cloud OSS, oss://<bucket-name>/<folder-path>/, AccessKey pair, oss:PutObject, oss:ListBuckets, oss:GetBucketInfo
- Follow-up Guidance: The source also points to the TiDB Cloud console or TiDB Cloud CLI path for local-file export and to the external storage access configuration pages for Amazon S3, GCS, Azure Blob Storage, and Alibaba Cloud OSS.
- Classification Note: This is classified as data_pipeline for the cloud component because the content describes exporting data from TiDB Cloud Serverless to local or external storage destinations with destination-specific access requirements and limitations.

## Official Source Content

# Export Data from TiDB Cloud Serverless

TiDB Cloud Serverless Export (Beta) is a service that enables you to export data from a TiDB Cloud Serverless cluster to a local file or an external storage service. You can use the exported data for backup, migration, data analysis, or other purposes.

While you can also export data using tools such as [mysqldump](https://dev.mysql.com/doc/refman/8.0/en/mysqldump.html) and TiDB [Dumpling](https://docs.pingcap.com/tidb/dev/dumpling-overview), TiDB Cloud Serverless Export offers a more convenient and efficient way to export data from a TiDB Cloud Serverless cluster. It brings the following benefits:

- Convenience: the export service provides a simple and easy-to-use way to export data from a TiDB Cloud Serverless cluster, eliminating the need for additional tools or resources.
- Isolation: the export service uses separate computing resources, ensuring isolation from the resources used by your online services.
- Consistency: the export service ensures the consistency of the exported data without causing locks, which does not affect your online services.

> **Note:**
>
> The maximum export size is currently 1 TiB. To export more data or request a higher export speed, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
## Export locations

You can export data to the following locations:

- A local file
- An external storage, including:

    - [Amazon S3](https://aws.amazon.com/s3/)
    - [Google Cloud Storage](https://cloud.google.com/storage)
    - [Azure Blob Storage](https://azure.microsoft.com/en-us/services/storage/blobs/)
    - [Alibaba Cloud Object Storage Service (OSS)](https://www.alibabacloud.com/product/oss)

> **Note:**
>
> If the size of the data to be exported is large (more than 100 GiB), it is recommended that you export it to an external storage.
### A local file

To export data from a TiDB Cloud Serverless cluster to a local file, you need to export data [using the TiDB Cloud console](#export-data-to-a-local-file) or [using the TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-export-create), and then download the exported data using the TiDB Cloud CLI.

Exporting data to a local file has the following limitations:

- Downloading exported data using the TiDB Cloud console is not supported.
- Exported data is saved in the stashing area of TiDB Cloud and will expire after two days. You need to download the exported data in time.
- If the storage space of stashing area is full, you will not be able to export data to the local file.
### Amazon S3

To export data to Amazon S3, you need to provide the following information:

- URI: `s3://<bucket-name>/<folder-path>/`
- One of the following access credentials:
    - [An access key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html): make sure the access key has the `s3:PutObject` and `s3:ListBucket` permissions.
    - [A role ARN](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns.html): make sure the role ARN (Amazon Resource Name) has the `s3:PutObject` and `s3:ListBucket` permissions. Note that only clusters hosted on AWS support the role ARN.

For more information, see [Configure Amazon S3 access](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-amazon-s3-access).
### Google Cloud Storage

To export data to Google Cloud Storage, you need to provide the following information:

- URI: `gs://<bucket-name>/<folder-path>/`
- Access credential: a **base64 encoded** [service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) for your bucket. Make sure the service account key has the `storage.objects.create` permission.

For more information, see [Configure GCS access](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-gcs-access).
### Azure Blob Storage

To export data to Azure Blob Storage, you need to provide the following information:

- URI: `azure://<account-name>.blob.core.windows.net/<container-name>/<folder-path>/` or `https://<account-name>.blob.core.windows.net/<container-name>/<folder-path>/`
- Access credential: a [shared access signature (SAS) token](https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview) for your Azure Blob Storage container. Make sure the SAS token has the `Read` and `Write` permissions on the `Container` and `Object` resources.

For more information, see [Configure Azure Blob Storage access](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-azure-blob-storage-access).
### Alibaba Cloud OSS

To export data to Alibaba Cloud OSS, you need to provide the following information:

- URI: `oss://<bucket-name>/<folder-path>/`
- Access credential: An [AccessKey pair](https://www.alibabacloud.com/help/en/ram/user-guide/create-an-accesskey-pair) for your Alibaba Cloud account. Make sure the AccessKey pair has the `oss:PutObject`, `oss:ListBuckets` and `oss:GetBucketInfo` permissions to allow data export to the OSS bucket.

For more information, see [Configure Alibaba Cloud Object Storage Service (OSS) access](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-external-storage#configure-alibaba-cloud-object-storage-service-oss-access).
