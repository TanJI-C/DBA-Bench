# Authentication for S3, GCS, and Azure Blob Storage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/backup-and-restore-storages.md`
- Source Title: `Backup Storages`
- Source Heading Path: `Backup Storages > Authentication`
- Source Line Ranges: `100-203`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `cloud`, `tiup`
- Topic Tags: `authentication`, `s3`, `gcs`, `azure`, `iam-role`, `access-key`, `credentials-file`, `sas-token`, `azure-ad`, `environment-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0010_bc54e4531e`
- Source ID: `tidb-docs-8.1:br/backup-and-restore-storages.md#authentication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `af6ece745dc7e129588d849c786814b0c0b054517a540e84186e550fcd1c13bc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages#authentication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/backup-and-restore-storages.md

## Retrieval Guidance

- Use When: Use this chunk when you need authentication methods, credential sources, or required S3 permissions for BR backup data stored in Amazon S3, GCS, or Azure Blob Storage.
- Retrieval Keywords: Authentication, Amazon S3, GCS, Azure Blob Storage, s3:ListBucket, s3:GetObject, s3:DeleteObject, s3:PutObject, s3:AbortMultipartUpload, ./checkpoints, ./pitr_id_maps, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_SHARED_CREDENTIALS_FILE, ~/.aws/credentials, IAM role, credentials-file, GOOGLE_APPLICATION_CREDENTIALS, ~/.config/gcloud/application_default_credentials.json, metadata server, GCE, GAE, sas-token, account-name, account-key, AZURE_STORAGE_KEY, AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, systemctl edit tikv-24000, systemctl daemon-reload, systemctl restart tikv-24000
- Follow-up Guidance: The source includes BR command examples for IAM role access to S3 and Azure AD-based backup to Azure Blob Storage.
- Classification Note: This is classified as configuration because it enumerates supported authentication parameters, environment variables, and account configuration methods for cloud storage access.

## Official Source Content

## Authentication

When storing backup data in a cloud storage system, you need to configure authentication parameters depending on the specific cloud service provider. This section describes the authentication methods used by Amazon S3, GCS, and Azure Blob Storage, and how to configure the accounts used to access the corresponding storage service.

<div label="Amazon S3" value="amazon">

Before backup, configure the following privileges to access the backup directory on S3.

- Minimum privileges for TiKV and Backup & Restore (BR) to access the backup directories during backup: `s3:ListBucket`, `s3:GetObject`, `s3:DeleteObject`, `s3:PutObject`, and `s3:AbortMultipartUpload`
- Minimum privileges for TiKV and BR to access the backup directories during restore: `s3:ListBucket`, `s3:GetObject`, `s3:DeleteObject`, and `s3:PutObject`. BR writes checkpoint information to the `./checkpoints` subdirectory under the backup directory. When restoring log backup data, BR writes the table ID mapping relationship of the restored cluster to the `./pitr_id_maps` subdirectory under the backup directory.

If you have not yet created a backup directory, refer to [Create a bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) to create an S3 bucket in the specified region. If necessary, you can also create a folder in the bucket by referring to [Create a folder](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-folders.html).

It is recommended that you configure access to S3 using either of the following ways:

- Method 1: Specify the access key

    If you specify an access key and a secret access key in the URI, authentication is performed using the specified access key and secret access key. Besides specifying the key in the URI, the following methods are also supported:

    - BR reads the environment variables `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY`.
    - BR reads the environment variables `$AWS_ACCESS_KEY` and `$AWS_SECRET_KEY`.
    - BR reads the shared credentials file in the path specified by the environment variable `$AWS_SHARED_CREDENTIALS_FILE`.
    - BR reads the shared credentials file in the `~/.aws/credentials` path.

- Method 2: Access based on the IAM role

    Associate an IAM role that can access S3 with EC2 instances where the TiKV and BR nodes run. After the association, BR can directly access the backup directories in S3 without additional settings.

    ```shell
    tiup br backup full --pd "${PD_IP}:2379" \
    --storage "s3://${host}/${path}"
    ```

</div>
<div label="GCS" value="gcs">

You can configure the account used to access GCS by specifying the access key. If you specify the `credentials-file` parameter, the authentication is performed using the specified `credentials-file`. Besides specifying the key in the URI, the following methods are also supported:

- BR reads the file in the path specified by the environment variable `$GOOGLE_APPLICATION_CREDENTIALS`
- BR reads the file `~/.config/gcloud/application_default_credentials.json`.
- BR obtains the credentials from the metadata server when the cluster is running in GCE or GAE.

</div>
<div label="Azure Blob Storage" value="azure">

- Method 1: Specify the shared access signature

    If you specify `account-name` and `sas-token` in the URI, the authentication is performed using the specified account name and shared access signature (SAS) token. Note that the SAS token contains the `&` character. You need to encode it as `%26` before appending it to the URI. You can also directly encode the entire `sas-token` using percent-encoding.

- Method 2: Specify the access key

    If you specify `account-name` and `account-key` in the URI, the authentication is performed using the specified account name and account key. Besides the method of specifying the key in the URI, BR can also read the key from the environment variable `$AZURE_STORAGE_KEY`.

- Method 3: Use Azure AD for backup and restore

    Configure the environment variables `$AZURE_CLIENT_ID`, `$AZURE_TENANT_ID`, and `$AZURE_CLIENT_SECRET` on the node where BR is running.

    - When the cluster is started using TiUP, TiKV uses the systemd service. The following example shows how to configure the preceding three environment variables for TiKV:

        > **Note:**
        >
        > If this method is used, you need to restart TiKV in step 3. If your cluster cannot be restarted, use **Method 1: Specify the access key** for backup and restore.

        1. Suppose that the TiKV port on this node is `24000`, that is, the name of the systemd service is `tikv-24000`:

            ```shell
            systemctl edit tikv-24000
            ```

        2. Edit the TiKV configuration file to configure the three environment variables:

            ```
            [Service]
            Environment="AZURE_CLIENT_ID=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            Environment="AZURE_TENANT_ID=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            Environment="AZURE_CLIENT_SECRET=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            ```

        3. Reload the configuration and restart TiKV:

            ```shell
            systemctl daemon-reload
            systemctl restart tikv-24000
            ```

    - To configure the Azure AD information for TiKV and BR started with command lines, you only need to check whether the environment variables `$AZURE_CLIENT_ID`, `$AZURE_TENANT_ID`, and `$AZURE_CLIENT_SECRET` are configured in the operating environment by running the following commands:

        ```shell
        echo $AZURE_CLIENT_ID
        echo $AZURE_TENANT_ID
        echo $AZURE_CLIENT_SECRET
        ```

    - Use BR to back up data to Azure Blob Storage:

        ```shell
        tiup br backup full -u "${PD_IP}:2379" \
        --storage "azure://external/backup-20220915?account-name=${account-name}"
        ```

</div>
